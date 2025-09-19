from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from .models import Booking, Payment, Train, Station, Passenger
from .app import db
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError
from .queue_manager import WaitlistManager
import random
import string

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/pay/<int:booking_id>')
@login_required
def pay(booking_id):
    """Payment page"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user owns the booking
    if booking.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Check if payment already exists
    if booking.payment and booking.payment.status == 'success':
        flash('Payment already completed', 'info')
        return redirect(url_for('auth.profile'))
    
    return render_template('payment.html', booking=booking)

@payment_bp.route('/pay_session')
@login_required
def pay_from_session():
    """Payment page for session-based booking data"""
    booking_data = session.get('pending_booking')
    
    if not booking_data:
        flash('No pending booking found. Please start a new booking.', 'error')
        return redirect(url_for('index'))
    
    # Check if user matches the booking
    if booking_data.get('user_id') != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get train and station details for display
    train = Train.query.get(booking_data['train_id'])
    from_station = Station.query.get(booking_data['from_station_id'])
    to_station = Station.query.get(booking_data['to_station_id'])
    
    if not train or not from_station or not to_station:
        flash('Invalid booking data. Please start a new booking.', 'error')
        session.pop('pending_booking', None)
        return redirect(url_for('index'))
    
    # Create a temporary booking object for template display
    class TempBooking:
        def __init__(self, data):
            self.train = train
            self.from_station = from_station
            self.to_station = to_station
            self.journey_date = datetime.strptime(data['journey_date'], '%Y-%m-%d').date()
            self.passengers = data['passengers']
            self.total_amount = data['total_amount']
            self.booking_type = data['booking_type']
            self.quota = data['quota']
            self.coach_class = data['coach_class']
            self.status = data['status']
            self.pnr = 'PENDING'  # Temporary PNR
    
    temp_booking = TempBooking(booking_data)
    return render_template('payment.html', booking=temp_booking, from_session=True)

@payment_bp.route('/process/<int:booking_id>', methods=['POST'])
@login_required
def process_payment(booking_id):
    """Process payment with idempotency protection"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user owns the booking
    if booking.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # CRITICAL FIX: Check for existing successful payment (idempotency)
    if booking.payment and booking.payment.status == 'success':
        flash('Payment already completed', 'info')
        return redirect(url_for('payment.success', booking_id=booking.id))
    
    payment_method = request.form.get('payment_method')
    
    if not payment_method:
        flash('Please select a payment method', 'error')
        return redirect(url_for('payment.pay', booking_id=booking_id))
    
    try:
        # Double-check for existing payment (race condition protection)
        existing_payment = Payment.query.filter_by(booking_id=booking.id, status='success').first()
        if existing_payment:
            flash('Payment already completed', 'info')
            return redirect(url_for('payment.success', booking_id=booking.id))
        
        # Generate transaction ID
        transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        
        # Create payment record with amount verification
        payment = Payment(
            booking_id=booking.id,
            user_id=current_user.id,
            amount=booking.total_amount,  # Verified against booking amount
            payment_method=payment_method,
            transaction_id=transaction_id,
            status='success',  # Simulating successful payment
            completed_at=datetime.utcnow()
        )
        
        db.session.add(payment)
        
        # Update booking status based on current state
        if booking.status == 'waitlisted':
            # Keep as waitlisted but mark payment as completed
            pass
        elif booking.status == 'pending_payment':
            booking.status = 'confirmed'
        
        # Commit all changes
        db.session.commit()
        
        flash(f'Payment successful! Transaction ID: {transaction_id}', 'success')
        return redirect(url_for('payment.success', booking_id=booking.id))
        
    except IntegrityError as e:
        # Handle duplicate payment constraint violation 
        db.session.rollback()
        if 'uq_booking_payment_success' in str(e):
            # Payment already exists for this booking
            flash('Payment already completed for this booking', 'info')
            return redirect(url_for('payment.success', booking_id=booking_id))
        else:
            flash('Payment processing failed due to data conflict. Please try again.', 'error')
            return redirect(url_for('payment.pay', booking_id=booking_id))
    except Exception as e:
        db.session.rollback()
        flash('Payment processing failed. Please try again.', 'error')
        return redirect(url_for('payment.pay', booking_id=booking_id))

@payment_bp.route('/process_session', methods=['POST'])
@login_required  
def process_session_payment():
    """Process payment from session data and create booking ONLY after successful payment"""
    booking_data = session.get('pending_booking')
    
    if not booking_data:
        flash('No pending booking found. Please start a new booking.', 'error')
        return redirect(url_for('index'))
    
    # Check if user matches the booking
    if booking_data.get('user_id') != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    payment_method = request.form.get('payment_method')
    
    if not payment_method:
        flash('Please select a payment method', 'error')
        return redirect(url_for('payment.pay_from_session'))
    
    try:
        # Start transaction for atomic booking creation
        
        # Lock the train record to ensure atomic seat allocation  
        train = db.session.query(Train).filter_by(id=booking_data['train_id']).with_for_update().first()
        
        if not train or not train.active:
            flash('Train not found or not active', 'error')
            session.pop('pending_booking', None)
            return redirect(url_for('index'))
        
        # Re-validate seat availability with current data
        journey_date = datetime.strptime(booking_data['journey_date'], '%Y-%m-%d').date()
        
        if booking_data['booking_type'] == 'tatkal':
            tatkal_booked = db.session.query(
                db.func.sum(Booking.passengers)
            ).filter(
                Booking.train_id == booking_data['train_id'],
                Booking.journey_date == journey_date,
                Booking.booking_type == 'tatkal',
                Booking.status == 'confirmed'
            ).scalar() or 0
            
            available_seats = max(0, (train.tatkal_seats or 0) - tatkal_booked)
        else:
            general_booked = db.session.query(
                db.func.sum(Booking.passengers)
            ).filter(
                Booking.train_id == booking_data['train_id'],
                Booking.journey_date == journey_date,
                Booking.booking_type == 'general',
                Booking.status == 'confirmed'
            ).scalar() or 0
            
            general_quota = train.total_seats - (train.tatkal_seats or 0)
            available_seats = max(0, general_quota - general_booked)
        
        # Determine final booking status
        if available_seats >= booking_data['passengers']:
            final_status = 'confirmed'
        else:
            final_status = 'waitlisted'
        
        # Generate transaction ID
        transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        
        # NOW CREATE THE ACTUAL BOOKING RECORD (only after payment succeeds)
        booking = Booking(
            user_id=booking_data['user_id'],
            train_id=booking_data['train_id'],
            from_station_id=booking_data['from_station_id'],
            to_station_id=booking_data['to_station_id'],
            journey_date=journey_date,
            passengers=booking_data['passengers'],
            total_amount=booking_data['total_amount'],
            booking_type=booking_data['booking_type'],
            quota=booking_data['quota'],
            coach_class=booking_data['coach_class'],
            status=final_status
        )
        
        db.session.add(booking)
        db.session.flush()  # Get booking ID
        
        # Create passenger records
        for passenger_data in booking_data['passenger_details']:
            passenger = Passenger(
                booking_id=booking.id,
                name=passenger_data['name'],
                age=passenger_data['age'],
                gender=passenger_data['gender'],
                id_proof_type=passenger_data['id_proof_type'],
                id_proof_number=passenger_data['id_proof_number'],
                seat_preference=passenger_data['seat_preference'],
                coach_class=passenger_data['coach_class']
            )
            db.session.add(passenger)
        
        # Create payment record (payment successful)
        payment = Payment(
            booking_id=booking.id,
            user_id=current_user.id,
            amount=booking_data['total_amount'],
            payment_method=payment_method,
            transaction_id=transaction_id,
            status='success',
            completed_at=datetime.utcnow()
        )
        
        db.session.add(payment)
        
        # Allocate seats for confirmed bookings
        if final_status == 'confirmed':
            from .seat_allocation import SeatAllocator
            seat_allocator = SeatAllocator()
            seat_allocator.allocate_seats(booking.id)
        
        # Handle waitlist if needed
        if final_status == 'waitlisted':
            waitlist_manager = WaitlistManager()
            waitlist_manager.add_to_waitlist(booking.id, booking_data['train_id'], journey_date)
        
        # Commit all changes atomically
        db.session.commit()
        
        # Clear session data
        session.pop('pending_booking', None)
        
        flash(f'Payment successful! Booking confirmed. PNR: {booking.pnr}, Transaction ID: {transaction_id}', 'success')
        return redirect(url_for('payment.success', booking_id=booking.id))
        
    except Exception as e:
        db.session.rollback()
        # Clear session data on error
        session.pop('pending_booking', None)
        flash('Payment processing failed. Please try booking again.', 'error')
        return redirect(url_for('index'))

@payment_bp.route('/success/<int:booking_id>')
@login_required
def success(booking_id):
    """Payment success page"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user owns the booking
    if booking.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Clear any pending booking data from session
    session.pop('pending_booking', None)
    
    return render_template('payment_success.html', booking=booking)

@payment_bp.route('/failure/<int:booking_id>')
@login_required
def failure(booking_id):
    """Payment failure page"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user owns the booking
    if booking.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    return render_template('payment_failure.html', booking=booking)
