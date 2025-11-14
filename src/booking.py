from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from .models import Train, Station, Booking, TrainRoute, Passenger, RefundRequest
from .database import db
from datetime import datetime, date
from .utils import calculate_fare, check_seat_availability, is_booking_open, check_tatkal_availability, calculate_cancellation_charges, check_seat_availability_detailed, get_live_train_status, check_current_reservation_available, get_waitlist_type, get_all_class_availability
from .seat_allocation import SeatAllocator
from .queue_manager import WaitlistManager
from .route_graph import get_route_graph
import random
import json

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
    
    # Get seat availability for all classes if station and date are provided
    from_station_id = request.args.get('from_station', type=int)
    to_station_id = request.args.get('to_station', type=int)
    journey_date = request.args.get('journey_date')
    
    seat_availability = None
    if from_station_id and to_station_id and journey_date:
        seat_availability = get_all_class_availability(
            train_id, from_station_id, to_station_id, journey_date
        )
    
    return render_template('book_ticket.html', 
                         train=train, 
                         stations=stations,
                         train_stations=train_stations,
                         seat_availability=seat_availability,
                         from_station_id=from_station_id,
                         to_station_id=to_station_id,
                         journey_date=journey_date)

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
    
    # COMPREHENSIVE BACKEND VALIDATION FOR ALL FIELDS
    
    # 1. Validate required fields are present
    if not all([from_station_id, to_station_id, journey_date, passengers, coach_class, booking_type, quota]):
        flash('All fields are required. Please fill in all booking details.', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    # 2. Validate from and to stations are different
    if from_station_id == to_station_id:
        flash('Departure and destination stations cannot be the same', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    # 3. Validate stations exist and are active
    from_station = Station.query.filter_by(id=from_station_id, active=True).first()
    to_station = Station.query.filter_by(id=to_station_id, active=True).first()
    
    if not from_station or not to_station:
        flash('Invalid station selection. Please select valid stations.', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    # 4. Validate journey date format and range
    try:
        journey_date = datetime.strptime(journey_date or '', '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format. Please select a valid journey date.', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    # Validate date is not in the past
    if journey_date < date.today():
        flash('Journey date cannot be in the past. Please select a future date.', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    # Validate date is within booking window (120 days advance)
    max_advance_days = 120
    if (journey_date - date.today()).days > max_advance_days:
        flash(f'Journey date cannot be more than {max_advance_days} days in advance', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    # 5. Validate passenger count
    if not passengers or passengers < 1 or passengers > 6:
        flash('Passenger count must be between 1 and 6', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    # 6. Validate coach class
    valid_classes = ['AC1', 'AC2', 'AC3', 'SL', '2S', 'CC']
    if coach_class not in valid_classes:
        flash('Invalid coach class selected', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    # 7. Validate booking type
    valid_booking_types = ['general', 'tatkal']
    if booking_type not in valid_booking_types:
        flash('Invalid booking type selected', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    # 8. Validate quota
    valid_quotas = ['general', 'ladies', 'senior', 'disability', 'tatkal', 'premium_tatkal', 'lower_berth', 'defence']
    if quota not in valid_quotas:
        flash('Invalid quota selected', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    # 9. Validate passenger details if provided
    for i in range(passengers):
        passenger_name = request.form.get(f'passenger_{i}_name', '').strip()
        passenger_age = request.form.get(f'passenger_{i}_age', type=int)
        passenger_gender = request.form.get(f'passenger_{i}_gender', '')
        passenger_id_type = request.form.get(f'passenger_{i}_id_type', '')
        passenger_id_number = request.form.get(f'passenger_{i}_id_number', '').strip()
        
        # Validate name if provided
        if passenger_name:
            if len(passenger_name) < 2:
                flash(f'Passenger {i+1}: Name must be at least 2 characters long', 'error')
                return redirect(url_for('booking.book_ticket', train_id=train_id))
            if len(passenger_name) > 100:
                flash(f'Passenger {i+1}: Name cannot exceed 100 characters', 'error')
                return redirect(url_for('booking.book_ticket', train_id=train_id))
            # Check for valid name characters (letters, spaces, dots, hyphens)
            if not all(c.isalpha() or c.isspace() or c in '.-' for c in passenger_name):
                flash(f'Passenger {i+1}: Name contains invalid characters. Only letters, spaces, dots and hyphens allowed', 'error')
                return redirect(url_for('booking.book_ticket', train_id=train_id))
        
        # Validate age if provided
        if passenger_age is not None:
            if passenger_age < 1 or passenger_age > 120:
                flash(f'Passenger {i+1}: Age must be between 1 and 120 years', 'error')
                return redirect(url_for('booking.book_ticket', train_id=train_id))
        
        # Validate gender if provided
        if passenger_gender:
            valid_genders = ['Male', 'Female', 'Other']
            if passenger_gender not in valid_genders:
                flash(f'Passenger {i+1}: Invalid gender selection', 'error')
                return redirect(url_for('booking.book_ticket', train_id=train_id))
        
        # Validate ID proof type if provided
        if passenger_id_type:
            valid_id_types = ['Aadhar', 'PAN', 'Passport', 'Voter ID', 'Driving License']
            if passenger_id_type not in valid_id_types:
                flash(f'Passenger {i+1}: Invalid ID proof type', 'error')
                return redirect(url_for('booking.book_ticket', train_id=train_id))
        
        # Validate ID number format if provided
        if passenger_id_number:
            if len(passenger_id_number) < 5:
                flash(f'Passenger {i+1}: ID proof number must be at least 5 characters', 'error')
                return redirect(url_for('booking.book_ticket', train_id=train_id))
            if len(passenger_id_number) > 20:
                flash(f'Passenger {i+1}: ID proof number cannot exceed 20 characters', 'error')
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
        
        # CRITICAL FIX: Check if chart preparation is completed - no new bookings allowed
        from .models import ChartPreparation
        chart = ChartPreparation.query.filter_by(
            train_id=train_id,
            journey_date=journey_date
        ).first()
        
        if chart and chart.status in ['prepared', 'final']:
            flash('Booking is closed - chart preparation has been completed for this train', 'error')
            return redirect(url_for('booking.book_ticket', train_id=train_id))
        
        # Validate Tatkal booking window with coach class and train_id for override check
        if booking_type == 'tatkal' and not check_tatkal_availability(journey_date, coach_class, train_id):
            flash('Tatkal booking is not yet open for this date and coach class', 'error')
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
        
        # Store booking data in session instead of creating database record
        # This ensures booking is only created AFTER successful payment
        passenger_details = []
        for i in range(passengers or 0):
            passenger_name = request.form.get(f'passenger_{i}_name', '').strip()
            passenger_age = request.form.get(f'passenger_{i}_age', type=int)
            passenger_gender = request.form.get(f'passenger_{i}_gender', '')
            passenger_id_type = request.form.get(f'passenger_{i}_id_type', '')
            passenger_id_number = request.form.get(f'passenger_{i}_id_number', '')
            passenger_seat_pref = request.form.get(f'passenger_{i}_seat_preference', 'No Preference')
            
            # Allow booking even with incomplete passenger details
            passenger_data = {
                'name': passenger_name or f'Passenger {i+1}',
                'age': passenger_age or 25,  # Default age if not provided
                'gender': passenger_gender or 'Male',  # Default gender if not provided
                'id_proof_type': passenger_id_type or 'Aadhar',
                'id_proof_number': passenger_id_number or f'ID{random.randint(100000, 999999)}',
                'seat_preference': passenger_seat_pref,
                'coach_class': coach_class
            }
            passenger_details.append(passenger_data)
        
        # Determine seat availability status
        if available_seats >= (passengers or 0):
            booking_status = 'confirmed'
        else:
            booking_status = 'waitlisted'
        
        # Store all booking data in session for payment processing
        booking_data = {
            'user_id': current_user.id,
            'train_id': train_id,
            'from_station_id': from_station_id,
            'to_station_id': to_station_id,
            'journey_date': journey_date.isoformat(),  # Convert to string for JSON
            'passengers': passengers,
            'total_amount': total_amount,
            'booking_type': booking_type,
            'quota': quota,
            'coach_class': coach_class,
            'status': booking_status,
            'passenger_details': passenger_details,
            'available_seats': available_seats
        }
        
        session['pending_booking'] = booking_data
        session.permanent = True  # Make session data persistent
        
        # Rollback any database changes since we're not saving yet
        db.session.rollback()
        
        # Redirect to payment with session data
        flash(f'Booking details confirmed. Proceed to payment to complete booking.', 'info')
        return redirect(url_for('payment.pay_from_session'))
        
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
        
        # If it was a confirmed booking, restore seats and process waitlist
        if original_status == 'confirmed':
            # CRITICAL FIX: Restore available seats when confirmed booking is cancelled
            if train:
                train.available_seats = train.available_seats + booking.passengers
            
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
    """User booking history with search functionality"""
    search = request.args.get('search', '').strip()
    
    if search:
        # Search within user's bookings by PNR, train number, or train name
        bookings = Booking.query.filter_by(user_id=current_user.id).join(Train).filter(
            db.or_(
                db.func.lower(Booking.pnr).contains(search.lower()),
                db.func.lower(Train.number).contains(search.lower()),
                db.func.lower(Train.name).contains(search.lower())
            )
        ).order_by(
            Booking.booking_date.desc()
        ).all()
    else:
        bookings = Booking.query.filter_by(user_id=current_user.id).order_by(
            Booking.booking_date.desc()
        ).all()
    
    # Get user's payment history
    from .models import Payment
    payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.created_at.desc()).all()
    
    return render_template('booking_history.html', bookings=bookings, payments=payments, search=search)

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
        
        # Get pre-filled form data from URL parameters (from booking page navigation)
        selected_from_station = request.args.get('from_station', type=int)
        selected_to_station = request.args.get('to_station', type=int)
        selected_journey_date = request.args.get('journey_date')
        selected_passengers = request.args.get('passengers', type=int)
        selected_coach_class = request.args.get('coach_class')
        
        # Aadhaar verification requirement removed for simplified booking process
        
        # Get current tatkal booking status
        from datetime import datetime, time
        now = datetime.now().time()
        is_ac_open = now >= time(10, 0) and now <= time(10, 30)  # AC classes: 10:00-10:30 AM
        is_non_ac_open = now >= time(11, 0) and now <= time(11, 30)  # Non-AC: 11:00-11:30 AM
        
        return render_template('tatkal_booking.html', 
                             train=train, 
                             stations=stations,
                             train_stations=train_stations,
                             is_ac_open=is_ac_open,
                             is_non_ac_open=is_non_ac_open,
                             current_time=now.strftime('%H:%M'),
                             # Pre-fill form data from previous page
                             selected_from_station=selected_from_station,
                             selected_to_station=selected_to_station,
                             selected_journey_date=selected_journey_date,
                             selected_passengers=selected_passengers,
                             selected_coach_class=selected_coach_class)
    
    # Handle POST - process Tatkal booking with all data from previous form
    # All form validation and processing logic is the same as regular booking
    # but with enhanced Tatkal-specific checks and UI
    return book_ticket_post(train_id)  # Reuse existing logic

@booking_bp.route('/seat-availability')
def seat_availability():
    """Check seat availability before booking"""
    train_id = request.args.get('train_id', type=int)
    from_station_id = request.args.get('from_station_id', type=int)
    to_station_id = request.args.get('to_station_id', type=int)
    journey_date = request.args.get('journey_date')
    coach_class = request.args.get('coach_class', 'SL')
    quota = request.args.get('quota', 'general')
    
    if not all([train_id, from_station_id, to_station_id, journey_date]):
        return {'error': 'Missing required parameters'}, 400
    
    try:
        if not journey_date:
            return {'error': 'Journey date is required'}, 400
        journey_date = datetime.strptime(journey_date, '%Y-%m-%d').date()
    except ValueError:
        return {'error': 'Invalid date format'}, 400
    
    availability = check_seat_availability_detailed(
        train_id, from_station_id, to_station_id, journey_date, coach_class, quota
    )
    
    return availability

@booking_bp.route('/train-status/<int:train_id>')
def live_train_status(train_id):
    """Get live train status"""
    journey_date = request.args.get('journey_date')
    
    if not journey_date:
        journey_date = date.today()
    else:
        try:
            if journey_date:
                journey_date = datetime.strptime(journey_date, '%Y-%m-%d').date()
            else:
                journey_date = date.today()
        except ValueError:
            return {'error': 'Invalid date format'}, 400
    
    status = get_live_train_status(train_id, journey_date)
    
    if not status:
        return {'error': 'Train status not found'}, 404
    
    return {
        'train_id': train_id,
        'journey_date': journey_date.isoformat(),
        'current_station': status.current_station_id,
        'status': status.status,
        'delay_minutes': status.delay_minutes,
        'last_updated': status.last_updated.isoformat()
    }

@booking_bp.route('/current-reservation/<int:train_id>')
@login_required
def current_reservation(train_id):
    """Current reservation booking (post-chart)"""
    journey_date = request.args.get('journey_date')
    
    if not journey_date:
        flash('Journey date is required', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    try:
        journey_date = datetime.strptime(journey_date, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    if not check_current_reservation_available(train_id, journey_date):
        flash('Current reservation is not available for this train/date', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    train = Train.query.get_or_404(train_id)
    stations = Station.query.filter_by(active=True).all()
    train_stations = db.session.query(Station).join(TrainRoute).filter(
        TrainRoute.train_id == train_id
    ).order_by(TrainRoute.sequence).all()
    
    return render_template('current_reservation.html', 
                         train=train, 
                         stations=stations,
                         train_stations=train_stations,
                         journey_date=journey_date)

@booking_bp.route('/cancel-with-refund/<int:booking_id>', methods=['POST'])
@login_required
def cancel_with_refund(booking_id):
    """Cancel booking with proper refund calculation"""
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
        # Calculate cancellation charges
        cancellation_charges = calculate_cancellation_charges(booking)
        refund_amount = max(0, booking.total_amount - cancellation_charges)
        
        # Store charges before cancelling
        booking.cancellation_charges = cancellation_charges
        
        # Cancel booking (this will process waitlist)
        original_status = booking.status
        booking.status = 'cancelled'
        
        # Process waitlist if it was a confirmed booking
        if original_status == 'confirmed':
            from .queue_manager import WaitlistManager
            waitlist_manager = WaitlistManager()
            waitlist_manager.process_waitlist(booking.train_id, booking.journey_date)
        
        db.session.commit()
        
        # Show refund details
        flash(f'Booking cancelled. Refund amount: ₹{refund_amount:.2f} (Cancellation charges: ₹{cancellation_charges:.2f})', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Cancellation failed. Please try again.', 'error')
    
    return redirect(url_for('auth.profile'))

@booking_bp.route('/file-tdr/<int:booking_id>')
@login_required
def file_tdr(booking_id):
    """File TDR (Ticket Deposit Receipt) for refund"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user owns the booking
    if booking.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('auth.profile'))
    
    return render_template('file_tdr.html', booking=booking)

@booking_bp.route('/file-tdr/<int:booking_id>', methods=['POST'])
@login_required
def file_tdr_post(booking_id):
    """Process TDR filing"""
    from .models import RefundRequest
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user owns the booking
    if booking.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('auth.profile'))
    
    reason = request.form.get('reason')
    description = request.form.get('description', '')
    
    if not reason:
        flash('Please select a reason for refund', 'error')
        return render_template('file_tdr.html', booking=booking)
    
    # Check if TDR already filed
    existing_tdr = RefundRequest.query.filter_by(booking_id=booking_id).first()
    if existing_tdr:
        flash('TDR already filed for this booking', 'error')
        return redirect(url_for('auth.profile'))
    
    try:
        # Calculate refund amount based on reason
        if reason in ['train_cancelled', 'ac_failure', 'coach_not_attached']:
            # Full refund for valid reasons
            refund_amount = booking.total_amount
            cancellation_charges = 0.0
        elif reason == 'delay_more_than_3_hours':
            # Full refund for delay > 3 hours
            refund_amount = booking.total_amount
            cancellation_charges = 0.0
        else:
            # Normal cancellation charges
            cancellation_charges = calculate_cancellation_charges(booking)
            refund_amount = max(0, booking.total_amount - cancellation_charges)
        
        # Create TDR request
        tdr = RefundRequest(
            booking_id=booking_id,
            user_id=current_user.id,
            reason=f"{reason}: {description}" if description else reason,
            amount_paid=booking.total_amount,
            refund_amount=refund_amount,
            cancellation_charges=cancellation_charges
        )
        
        db.session.add(tdr)
        db.session.commit()
        
        flash(f'TDR filed successfully. TDR Number: {tdr.tdr_number}. Expected refund: ₹{refund_amount:.2f}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Failed to file TDR. Please try again.', 'error')
    
    return redirect(url_for('auth.profile'))
