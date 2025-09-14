from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Train, Station, Booking, TrainRoute
from .app import db
from datetime import datetime, date
from .utils import calculate_fare, check_seat_availability
from .queue_manager import WaitlistManager
from .route_graph import get_route_graph

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
    """Process ticket booking"""
    train = Train.query.get_or_404(train_id)
    
    from_station_id = request.form.get('from_station', type=int)
    to_station_id = request.form.get('to_station', type=int)
    journey_date = request.form.get('journey_date')
    passengers = request.form.get('passengers', type=int)
    
    # Validation
    if not all([from_station_id, to_station_id, journey_date, passengers]):
        flash('Please fill all fields', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    if from_station_id == to_station_id:
        flash('Source and destination cannot be same', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    if not passengers or passengers <= 0 or passengers > 6:
        flash('Number of passengers must be between 1 and 6', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    journey_date = datetime.strptime(journey_date or '', '%Y-%m-%d').date()
    
    if journey_date < date.today():
        flash('Journey date cannot be in the past', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    # Check if route exists
    route_graph = get_route_graph()
    if not route_graph.has_route(train_id, from_station_id, to_station_id):
        flash('No route available between selected stations for this train', 'error')
        return redirect(url_for('booking.book_ticket', train_id=train_id))
    
    # Calculate fare
    total_amount = calculate_fare(train_id, from_station_id, to_station_id, passengers)
    
    # Check seat availability
    available_seats = check_seat_availability(train_id, journey_date)
    
    # Create booking
    booking = Booking(
        user_id=current_user.id,
        train_id=train_id,
        from_station_id=from_station_id,
        to_station_id=to_station_id,
        journey_date=journey_date,
        passengers=passengers,
        total_amount=total_amount,
        status='pending_payment'
    )
    
    db.session.add(booking)
    db.session.commit()
    
    # If seats available, mark as confirmed, otherwise add to waitlist
    if available_seats >= (passengers or 0):
        booking.status = 'confirmed'
        train.available_seats -= passengers
    else:
        booking.status = 'waitlisted'
        # Add to waitlist queue
        waitlist_manager = WaitlistManager()
        waitlist_manager.add_to_waitlist(booking.id, train_id, journey_date)
    
    db.session.commit()
    
    # Redirect to payment
    return redirect(url_for('payment.pay', booking_id=booking.id))

@booking_bp.route('/cancel/<int:booking_id>')
@login_required
def cancel_booking(booking_id):
    """Cancel booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user owns the booking
    if booking.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('auth.profile'))
    
    # Check if booking can be cancelled
    if booking.status in ['cancelled', 'completed']:
        flash('Booking cannot be cancelled', 'error')
        return redirect(url_for('auth.profile'))
    
    # Cancel booking
    booking.status = 'cancelled'
    
    # If confirmed booking, release seats and process waitlist
    if booking.status == 'confirmed':
        train = booking.train
        train.available_seats += booking.passengers
        
        # Process waitlist
        waitlist_manager = WaitlistManager()
        waitlist_manager.process_waitlist(booking.train_id, booking.journey_date)
    
    db.session.commit()
    
    flash('Booking cancelled successfully', 'success')
    return redirect(url_for('auth.profile'))

@booking_bp.route('/history')
@login_required
def booking_history():
    """User booking history"""
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(
        Booking.booking_date.desc()
    ).all()
    return render_template('booking_history.html', bookings=bookings)
