"""
Railway Functions Library
=========================
This file contains utility functions for various railway operations like booking tickets,
tatkal booking, PNR status checking, and more.

Usage:
    from railway_functions import *
    
    # Book a ticket
    result = book_ticket(user_id=1, train_id=101, from_station="DEL", to_station="MUM", 
                        journey_date="2025-01-15", passengers=2, coach_class="SL")
    
    # Check PNR status
    status = check_pnr_status("PNR123456")
"""

from datetime import datetime, date, timedelta
import random
import string
from werkzeug.security import generate_password_hash

# Import Flask app components (these will be available when imported in Flask context)
try:
    from app import db
    from models import Booking, Train, Station, User, TrainStatus
except ImportError:
    # When running standalone, these won't be available
    print("Note: This file should be imported within a Flask application context")
    db = None


def generate_pnr():
    """Generate a unique PNR number"""
    return ''.join(random.choices(string.digits, k=10))


def book_ticket(user_id, train_id, from_station_id, to_station_id, journey_date, 
                passengers=1, coach_class="SL", quota="GENERAL", booking_type="general"):
    """
    Book a railway ticket
    
    Args:
        user_id (int): ID of the user booking the ticket
        train_id (int): ID of the train
        from_station_id (int): ID of departure station
        to_station_id (int): ID of destination station
        journey_date (str or date): Date of journey
        passengers (int): Number of passengers
        coach_class (str): Class of coach (SL, AC1, AC2, AC3)
        quota (str): Booking quota (GENERAL, TATKAL, PREMIUM)
        booking_type (str): Type of booking (general, tatkal, premium)
    
    Returns:
        dict: Booking result with PNR and status
    """
    try:
        # Convert string date to date object if needed
        if isinstance(journey_date, str):
            journey_date = datetime.strptime(journey_date, '%Y-%m-%d').date()
        
        # Generate PNR
        pnr = generate_pnr()
        
        # Calculate total amount (base calculation)
        base_fare = 500 * passengers  # Base fare per passenger
        if coach_class == "AC1":
            base_fare *= 4
        elif coach_class == "AC2":
            base_fare *= 3
        elif coach_class == "AC3":
            base_fare *= 2.5
        elif coach_class == "SL":
            base_fare *= 1
        
        # Add tatkal charges if applicable
        if booking_type == "tatkal":
            base_fare += 100 * passengers
        
        # Create booking
        booking = Booking(
            pnr=pnr,
            user_id=user_id,
            train_id=train_id,
            from_station_id=from_station_id,
            to_station_id=to_station_id,
            journey_date=journey_date,
            passengers=passengers,
            total_amount=base_fare,
            booking_type=booking_type,
            quota=quota,
            coach_class=coach_class,
            status='confirmed',
            booking_date=datetime.utcnow()
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return {
            'success': True,
            'pnr': pnr,
            'status': 'confirmed',
            'amount': base_fare,
            'message': f'Ticket booked successfully! PNR: {pnr}'
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'Booking failed: {str(e)}'
        }


def tatkal_booking(user_id, train_id, from_station_id, to_station_id, journey_date, 
                   passengers=1, coach_class="SL"):
    """
    Book a tatkal ticket (premium booking with higher charges)
    
    Args:
        user_id (int): ID of the user
        train_id (int): ID of the train
        from_station_id (int): ID of departure station
        to_station_id (int): ID of destination station
        journey_date (str or date): Date of journey
        passengers (int): Number of passengers
        coach_class (str): Class of coach
    
    Returns:
        dict: Booking result
    """
    # Check if tatkal booking time is allowed (typically 10 AM to 2 PM)
    current_time = datetime.now().time()
    tatkal_start = datetime.strptime("10:00", "%H:%M").time()
    tatkal_end = datetime.strptime("14:00", "%H:%M").time()
    
    if not (tatkal_start <= current_time <= tatkal_end):
        return {
            'success': False,
            'message': 'Tatkal booking is only allowed between 10:00 AM and 2:00 PM'
        }
    
    return book_ticket(
        user_id=user_id,
        train_id=train_id,
        from_station_id=from_station_id,
        to_station_id=to_station_id,
        journey_date=journey_date,
        passengers=passengers,
        coach_class=coach_class,
        quota="TATKAL",
        booking_type="tatkal"
    )


def check_pnr_status(pnr):
    """
    Check the status of a PNR
    
    Args:
        pnr (str): PNR number
    
    Returns:
        dict: PNR status information
    """
    try:
        booking = Booking.query.filter_by(pnr=pnr).first()
        
        if not booking:
            return {
                'success': False,
                'message': 'PNR not found'
            }
        
        # Get related information
        train = Train.query.get(booking.train_id)
        from_station = Station.query.get(booking.from_station_id)
        to_station = Station.query.get(booking.to_station_id)
        user = User.query.get(booking.user_id)
        
        return {
            'success': True,
            'pnr': pnr,
            'status': booking.status,
            'train_number': train.number if train else 'N/A',
            'train_name': train.name if train else 'N/A',
            'from_station': from_station.name if from_station else 'N/A',
            'to_station': to_station.name if to_station else 'N/A',
            'journey_date': booking.journey_date.strftime('%Y-%m-%d'),
            'passengers': booking.passengers,
            'coach_class': booking.coach_class,
            'total_amount': booking.total_amount,
            'booking_date': booking.booking_date.strftime('%Y-%m-%d %H:%M'),
            'passenger_name': user.username if user else 'N/A'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error checking PNR: {str(e)}'
        }


def cancel_ticket(pnr, user_id):
    """
    Cancel a booked ticket
    
    Args:
        pnr (str): PNR number
        user_id (int): User ID for verification
    
    Returns:
        dict: Cancellation result
    """
    try:
        booking = Booking.query.filter_by(pnr=pnr, user_id=user_id).first()
        
        if not booking:
            return {
                'success': False,
                'message': 'Booking not found or unauthorized'
            }
        
        if booking.status == 'cancelled':
            return {
                'success': False,
                'message': 'Ticket is already cancelled'
            }
        
        # Calculate cancellation charges
        cancellation_charges = booking.total_amount * 0.1  # 10% cancellation fee
        refund_amount = booking.total_amount - cancellation_charges
        
        # Update booking status
        booking.status = 'cancelled'
        booking.cancellation_charges = cancellation_charges
        
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Ticket cancelled successfully',
            'refund_amount': refund_amount,
            'cancellation_charges': cancellation_charges
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'Cancellation failed: {str(e)}'
        }


def check_seat_availability(train_id, from_station_id, to_station_id, journey_date, coach_class="SL"):
    """
    Check seat availability for a train
    
    Args:
        train_id (int): ID of the train
        from_station_id (int): ID of departure station
        to_station_id (int): ID of destination station
        journey_date (str or date): Date of journey
        coach_class (str): Class of coach
    
    Returns:
        dict: Availability information
    """
    try:
        if isinstance(journey_date, str):
            journey_date = datetime.strptime(journey_date, '%Y-%m-%d').date()
        
        train = Train.query.get(train_id)
        if not train:
            return {
                'success': False,
                'message': 'Train not found'
            }
        
        # Count booked seats for this route and date
        booked_seats = db.session.query(db.func.sum(Booking.passengers)).filter(
            Booking.train_id == train_id,
            Booking.journey_date == journey_date,
            Booking.coach_class == coach_class,
            Booking.status.in_(['confirmed', 'waitlisted'])
        ).scalar() or 0
        
        # Calculate available seats (assuming 72 seats per coach)
        total_seats = 72
        available_seats = max(0, total_seats - booked_seats)
        waitlist_count = max(0, booked_seats - total_seats)
        
        return {
            'success': True,
            'train_number': train.number,
            'train_name': train.name,
            'available_seats': available_seats,
            'waitlist_count': waitlist_count,
            'status': 'AVAILABLE' if available_seats > 0 else 'WAITLIST'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error checking availability: {str(e)}'
        }


def search_trains(from_station_id, to_station_id, journey_date):
    """
    Search for trains between stations
    
    Args:
        from_station_id (int): ID of departure station
        to_station_id (int): ID of destination station
        journey_date (str or date): Date of journey
    
    Returns:
        dict: List of available trains
    """
    try:
        # Get all trains (in real system, this would check routes)
        trains = Train.query.filter_by(active=True).all()
        
        train_list = []
        for train in trains:
            availability = check_seat_availability(
                train.id, from_station_id, to_station_id, journey_date
            )
            
            train_list.append({
                'train_id': train.id,
                'train_number': train.number,
                'train_name': train.name,
                'departure_time': train.departure_time,
                'arrival_time': train.arrival_time,
                'available_seats': availability.get('available_seats', 0),
                'status': availability.get('status', 'UNKNOWN')
            })
        
        return {
            'success': True,
            'trains': train_list,
            'count': len(train_list)
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error searching trains: {str(e)}'
        }


def add_to_waitlist(user_id, train_id, from_station_id, to_station_id, journey_date, 
                    passengers=1, coach_class="SL"):
    """
    Add booking to waitlist when seats are not available
    
    Args:
        user_id (int): ID of the user
        train_id (int): ID of the train
        from_station_id (int): ID of departure station
        to_station_id (int): ID of destination station
        journey_date (str or date): Date of journey
        passengers (int): Number of passengers
        coach_class (str): Class of coach
    
    Returns:
        dict: Waitlist result
    """
    try:
        if isinstance(journey_date, str):
            journey_date = datetime.strptime(journey_date, '%Y-%m-%d').date()
        
        pnr = generate_pnr()
        
        # Calculate amount
        base_fare = 500 * passengers
        if coach_class == "AC1":
            base_fare *= 4
        elif coach_class == "AC2":
            base_fare *= 3
        elif coach_class == "AC3":
            base_fare *= 2.5
        
        booking = Booking(
            pnr=pnr,
            user_id=user_id,
            train_id=train_id,
            from_station_id=from_station_id,
            to_station_id=to_station_id,
            journey_date=journey_date,
            passengers=passengers,
            total_amount=base_fare,
            booking_type="general",
            quota="GENERAL",
            coach_class=coach_class,
            status='waitlisted',
            booking_date=datetime.utcnow()
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Calculate waitlist position
        waitlist_position = Booking.query.filter(
            Booking.train_id == train_id,
            Booking.journey_date == journey_date,
            Booking.coach_class == coach_class,
            Booking.status == 'waitlisted',
            Booking.booking_date < booking.booking_date
        ).count() + 1
        
        return {
            'success': True,
            'pnr': pnr,
            'status': 'waitlisted',
            'waitlist_position': waitlist_position,
            'message': f'Added to waitlist. PNR: {pnr}, Position: {waitlist_position}'
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'Waitlist booking failed: {str(e)}'
        }


def check_train_status(train_number, station_code=None):
    """
    Check current status of a train
    
    Args:
        train_number (str): Train number
        station_code (str): Station code to check status at
    
    Returns:
        dict: Train status information
    """
    try:
        train = Train.query.filter_by(number=train_number).first()
        
        if not train:
            return {
                'success': False,
                'message': 'Train not found'
            }
        
        # Get train status (this would connect to real-time data in production)
        train_status = TrainStatus.query.filter_by(train_id=train.id).first()
        
        if train_status:
            return {
                'success': True,
                'train_number': train.number,
                'train_name': train.name,
                'current_station': train_status.current_station,
                'status': train_status.status,
                'delay_minutes': train_status.delay_minutes,
                'last_updated': train_status.last_updated.strftime('%Y-%m-%d %H:%M')
            }
        else:
            return {
                'success': True,
                'train_number': train.number,
                'train_name': train.name,
                'status': 'On Time',
                'message': 'No delay information available'
            }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error checking train status: {str(e)}'
        }


def create_user(username, email, password):
    """
    Create a new user account
    
    Args:
        username (str): Username
        email (str): Email address
        password (str): Password
    
    Returns:
        dict: User creation result
    """
    try:
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            return {
                'success': False,
                'message': 'Username or email already exists'
            }
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(user)
        db.session.commit()
        
        return {
            'success': True,
            'user_id': user.id,
            'message': 'User created successfully'
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'User creation failed: {str(e)}'
        }


def get_user_bookings(user_id, limit=10):
    """
    Get booking history for a user
    
    Args:
        user_id (int): User ID
        limit (int): Number of bookings to return
    
    Returns:
        dict: List of user bookings
    """
    try:
        bookings = Booking.query.filter_by(user_id=user_id)\
                                .order_by(Booking.booking_date.desc())\
                                .limit(limit).all()
        
        booking_list = []
        for booking in bookings:
            train = Train.query.get(booking.train_id)
            from_station = Station.query.get(booking.from_station_id)
            to_station = Station.query.get(booking.to_station_id)
            
            booking_list.append({
                'pnr': booking.pnr,
                'train_number': train.number if train else 'N/A',
                'train_name': train.name if train else 'N/A',
                'from_station': from_station.name if from_station else 'N/A',
                'to_station': to_station.name if to_station else 'N/A',
                'journey_date': booking.journey_date.strftime('%Y-%m-%d'),
                'status': booking.status,
                'passengers': booking.passengers,
                'total_amount': booking.total_amount,
                'booking_date': booking.booking_date.strftime('%Y-%m-%d %H:%M')
            })
        
        return {
            'success': True,
            'bookings': booking_list,
            'count': len(booking_list)
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error fetching bookings: {str(e)}'
        }


# Example usage and testing functions
def demo_functions():
    """
    Demonstration of how to use the railway functions
    """
    print("=== Railway Functions Demo ===\n")
    
    # Example: Create a user
    print("1. Creating a user...")
    user_result = create_user("testuser", "test@example.com", "password123")
    print(f"Result: {user_result}\n")
    
    # Example: Search trains
    print("2. Searching trains...")
    search_result = search_trains(1, 2, "2025-01-15")
    print(f"Result: {search_result}\n")
    
    # Example: Check seat availability
    print("3. Checking seat availability...")
    availability = check_seat_availability(1, 1, 2, "2025-01-15", "SL")
    print(f"Result: {availability}\n")
    
    # Example: Book a ticket
    print("4. Booking a ticket...")
    booking_result = book_ticket(1, 1, 1, 2, "2025-01-15", 2, "SL")
    print(f"Result: {booking_result}\n")
    
    # Example: Check PNR status
    if booking_result.get('success'):
        print("5. Checking PNR status...")
        pnr_status = check_pnr_status(booking_result['pnr'])
        print(f"Result: {pnr_status}\n")


if __name__ == "__main__":
    # Run demo when file is executed directly
    demo_functions()