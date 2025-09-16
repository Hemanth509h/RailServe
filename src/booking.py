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
    
    # Backend validation (frontend should handle most of this)
    if not all([from_station_id, to_station_id, journey_date, passengers]):
        flash('Please fill all fields', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    try:
        journey_date = datetime.strptime(journey_date or '', '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    # Start atomic transaction for concurrent booking
    try:
        # Use row-level locking to prevent concurrent booking conflicts
        with db.session.begin():
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
            
            # Calculate fare with booking type
            total_amount = calculate_fare(train_id, from_station_id, to_station_id, passengers, booking_type)
            
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
                        seat_preference=passenger_seat_pref
                    )
                    passenger_details.append(passenger)
                    db.session.add(passenger)
            
            # Atomic seat allocation or waitlist assignment with concurrent protection
            if available_seats >= (passengers or 0):
                booking.status = 'confirmed'
                # Update available seats on the locked train record
                if train:
                    train.available_seats = max(0, train.available_seats - (passengers or 0))
            else:
                booking.status = 'waitlisted'
                # Add to waitlist queue
                waitlist_manager = WaitlistManager()
                waitlist_manager.add_to_waitlist(booking.id, train_id, journey_date)
            
            # Transaction automatically commits here with all changes
            
        if booking.status == 'confirmed':
            flash(f'Ticket booked successfully! PNR: {booking.pnr}', 'success')
            return redirect(url_for('payment.payment_page', booking_id=booking.id))
        else:
            flash(f'No seats available. Added to waitlist! PNR: {booking.pnr}', 'warning')
            return redirect(url_for('booking.booking_history'))
        
    except Exception as e:
        db.session.rollback()
        flash('Booking failed due to high demand. Please try again.', 'error')
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
        # Use atomic transaction for cancellation
        with db.session.begin():
            # Lock the train record for seat release
            train = db.session.query(Train).filter_by(id=booking.train_id).with_for_update().first()
            
            # Store original status before changing
            original_status = booking.status
            
            # Cancel booking
            booking.status = 'cancelled'
            
            # If it was a confirmed booking, release seats and process waitlist
            if original_status == 'confirmed' and train:
                train.available_seats += booking.passengers
                
                # Process waitlist after seat release
                waitlist_manager = WaitlistManager()
                waitlist_manager.process_waitlist(booking.train_id, booking.journey_date)
            
            # Transaction automatically commits here
            
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
