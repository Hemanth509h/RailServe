from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Train, Station, Booking, TrainRoute, Passenger
from .app import db
from datetime import datetime, date
from .utils import calculate_fare, check_seat_availability, is_booking_open, check_tatkal_availability
from .queue_manager import WaitlistManager
from .route_graph import get_route_graph
import random

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/book/<int:train_id>')
@login_required
def book_ticket(train_id):
    """Book ticket form"""
    train = Train.query.get_or_404(train_id)
    stations = Station.query.filter_by(active=True).all()
    
    # Get train route stations
    train_stations = db.session.query(Station).join(TrainRoute).filter(
        TrainRoute.train_id == train_id
    ).order_by(TrainRoute.sequence).all()
    
    return render_template('book_ticket.html', 
                         train=train, 
                         stations=stations,
                         train_stations=train_stations)

@booking_bp.route('/book/<int:train_id>', methods=['POST'])
@login_required
def book_ticket_post(train_id):
    """Process ticket booking with proper concurrency control"""
    from_station_id = request.form.get('from_station', type=int)
    to_station_id = request.form.get('to_station', type=int)
    journey_date = request.form.get('journey_date')
    passengers = request.form.get('passengers', type=int)
    booking_type = request.form.get('booking_type', 'general')  # general or tatkal
    quota = request.form.get('quota', 'general')  # general, ladies, senior, disability, tatkal
    coach_class = request.form.get('coach_class', 'SL')  # AC1, AC2, AC3, SL, 2S, CC
    
    # Synchronize quota and booking_type - if quota is tatkal, force booking_type to tatkal
    if quota == 'tatkal':
        booking_type = 'tatkal'
    elif booking_type == 'tatkal':
        # If booking_type is tatkal but quota is not, force quota to tatkal
        quota = 'tatkal'
    
    # Backend validation (frontend should handle most of this)
    if not all([from_station_id, to_station_id, journey_date, passengers, coach_class]):
        flash('Please fill all fields including coach class', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    # Validate coach class
    valid_classes = ['AC1', 'AC2', 'AC3', 'SL', '2S', 'CC']
    if coach_class not in valid_classes:
        flash('Invalid coach class selected', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    # Validate passenger count
    if not passengers or passengers < 1 or passengers > 6:
        flash('Passenger count must be between 1 and 6', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    # Validate passenger details are provided
    missing_details = []
    for i in range(passengers):
        passenger_name = request.form.get(f'passenger_{i}_name', '').strip()
        passenger_age = request.form.get(f'passenger_{i}_age', type=int)
        passenger_gender = request.form.get(f'passenger_{i}_gender', '').strip()
        
        if not passenger_name:
            missing_details.append(f'Passenger {i+1} name')
        if not passenger_age or passenger_age < 1 or passenger_age > 120:
            missing_details.append(f'Passenger {i+1} valid age (1-120)')
        if not passenger_gender:
            missing_details.append(f'Passenger {i+1} gender')
    
    if missing_details:
        flash(f'Missing required details: {", ".join(missing_details)}', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    try:
        journey_date = datetime.strptime(journey_date or '', '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    # Process booking with proper transaction handling
    try:
        # Lock the train record to ensure atomic seat allocation
        train = db.session.query(Train).filter_by(id=train_id).with_for_update().first()
        
        if not train or not train.active:
            flash('Train not found or not active', 'error')
            return redirect(url_for('index'))
        
        # Validate route exists
        route_graph = get_route_graph()
        if not route_graph.has_route(train_id, from_station_id, to_station_id):
            flash('No route available between selected stations for this train', 'error')
            return redirect(url_for('booking.book_ticket', train_id=train_id))
        
        # Validate booking window
        if not is_booking_open(journey_date):
            flash('Booking is not available for this date', 'error')
            return redirect(url_for('booking.book_ticket', train_id=train_id))
        
        # Validate Tatkal booking window
        if booking_type == 'tatkal' and not check_tatkal_availability(journey_date):
            flash('Tatkal booking is not yet open for this date', 'error')
            return redirect(url_for('booking.book_ticket', train_id=train_id))
        
        # Calculate fare with booking type and coach class
        total_amount = calculate_fare(train_id, from_station_id, to_station_id, passengers, booking_type, coach_class)
        
        # Check availability based on booking type with concurrent safety
        if booking_type == 'tatkal':
            # Check Tatkal quota availability with row-level locking
            tatkal_booked = db.session.query(
                db.func.sum(Booking.passengers)
            ).filter(
                Booking.train_id == train_id,
                Booking.journey_date == journey_date,
                Booking.booking_type == 'tatkal',
                Booking.status == 'confirmed'
            ).scalar() or 0
            
            available_seats = max(0, (train.tatkal_seats or 0) - tatkal_booked)
        else:
            # Check general quota availability
            general_booked = db.session.query(
                db.func.sum(Booking.passengers)
            ).filter(
                Booking.train_id == train_id,
                Booking.journey_date == journey_date,
                Booking.booking_type == 'general',
                Booking.status == 'confirmed'
            ).scalar() or 0
            
            general_quota = train.total_seats - (train.tatkal_seats or 0)
            available_seats = max(0, general_quota - general_booked)
        
        # Create booking record
        booking = Booking(
            user_id=current_user.id,
            train_id=train_id,
            from_station_id=from_station_id,
            to_station_id=to_station_id,
            journey_date=journey_date,
            passengers=passengers,
            total_amount=total_amount,
            booking_type=booking_type,
            quota=quota,
            coach_class=coach_class,
            status='pending_payment'
        )
        
        db.session.add(booking)
        db.session.flush()  # Get booking ID without committing
        
        # Parse and create passenger details with concurrent safety
        passenger_details = []
        for i in range(passengers or 0):
            passenger_name = request.form.get(f'passenger_{i}_name', '')
            passenger_age = request.form.get(f'passenger_{i}_age', type=int)
            passenger_gender = request.form.get(f'passenger_{i}_gender', '')
            passenger_id_type = request.form.get(f'passenger_{i}_id_type', '')
            passenger_id_number = request.form.get(f'passenger_{i}_id_number', '')
            passenger_seat_pref = request.form.get(f'passenger_{i}_seat_preference', 'No Preference')
            
            if passenger_name and passenger_age and passenger_gender:
                passenger = Passenger(
                    booking_id=booking.id,
                    name=passenger_name,
                    age=passenger_age,
                    gender=passenger_gender,
                    id_proof_type=passenger_id_type or 'Aadhar',
                    id_proof_number=passenger_id_number or f'ID{random.randint(100000, 999999)}',
                    seat_preference=passenger_seat_pref,
                    coach_class=coach_class
                )
                passenger_details.append(passenger)
                db.session.add(passenger)
        
        # Atomic seat allocation or waitlist assignment with concurrent protection
        if available_seats >= (passengers or 0):
            booking.status = 'confirmed'
            # Note: Do not modify train.available_seats as it's global - availability is calculated per-date
        else:
            booking.status = 'waitlisted'
            # Add to waitlist queue
            waitlist_manager = WaitlistManager()
            waitlist_manager.add_to_waitlist(booking.id, train_id, journey_date)
        
        # Commit all changes
        db.session.commit()
            
        if booking.status == 'confirmed':
            flash(f'Ticket booked successfully! PNR: {booking.pnr}', 'success')
            return redirect(url_for('payment.pay', booking_id=booking.id))
        else:
            flash(f'No seats available. Added to waitlist! PNR: {booking.pnr}', 'warning')
            return redirect(url_for('booking.booking_history'))
        
    except Exception as e:
        db.session.rollback()
        # Provide more specific error messages for debugging
        import traceback
        error_details = str(e)
        print(f"Booking error: {error_details}")
        print(f"Full traceback: {traceback.format_exc()}")
        
        # Specific error handling
        if "constraint" in error_details.lower():
            flash('Booking failed: Data constraint violation. Please check your details and try again.', 'error')
        elif "connection" in error_details.lower():
            flash('Booking failed: Database connection issue. Please try again in a moment.', 'error')
        elif "integrity" in error_details.lower():
            flash('Booking failed: Data integrity error. Please verify all details and try again.', 'error')
        else:
            flash(f'Booking failed: {error_details}. Please check your details and try again.', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))

@booking_bp.route('/cancel/<int:booking_id>')
@login_required
def cancel_booking(booking_id):
    """Cancel booking with proper seat release"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user owns the booking
    if booking.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('auth.profile'))
    
    # Check if booking can be cancelled
    if booking.status in ['cancelled', 'completed']:
        flash('Booking cannot be cancelled', 'error')
        return redirect(url_for('auth.profile'))
    
    try:
        # Lock the train record for seat release
        train = db.session.query(Train).filter_by(id=booking.train_id).with_for_update().first()
        
        # Store original status before changing
        original_status = booking.status
        
        # Cancel booking
        booking.status = 'cancelled'
        
        # If it was a confirmed booking, process waitlist (no need to modify global seats)
        if original_status == 'confirmed':
            # Process waitlist after cancellation - availability will be calculated dynamically
            waitlist_manager = WaitlistManager()
            waitlist_manager.process_waitlist(booking.train_id, booking.journey_date)
        
        # Commit all changes
        db.session.commit()
            
        flash('Booking cancelled successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Cancellation failed. Please try again.', 'error')
    
    return redirect(url_for('auth.profile'))

@booking_bp.route('/history')
@login_required
def booking_history():
    """User booking history"""
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(
        Booking.booking_date.desc()
    ).all()
    return render_template('booking_history.html', bookings=bookings)

@booking_bp.route('/tatkal/<int:train_id>', methods=['GET', 'POST'])
@login_required
def tatkal_booking(train_id):
    """Dedicated Tatkal booking page with enhanced features"""
    train = Train.query.get_or_404(train_id)
    
    if request.method == 'GET':
        # Show Tatkal booking page
        stations = Station.query.filter_by(active=True).all()
        train_stations = db.session.query(Station).join(TrainRoute).filter(
            TrainRoute.train_id == train_id
        ).order_by(TrainRoute.sequence).all()
        
        return render_template('tatkal_booking.html', 
                             train=train, 
                             stations=stations,
                             train_stations=train_stations)
    
    # Handle POST - process Tatkal booking with all data from previous form
    # All form validation and processing logic is the same as regular booking
    # but with enhanced Tatkal-specific checks and UI
    return book_ticket_post(train_id)  # Reuse existing logic
