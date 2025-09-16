from .models import Train, Station, Booking, TrainRoute
from .app import db
from datetime import datetime, date
from sqlalchemy import and_, or_

def get_running_trains():
    """Get list of active trains"""
    return Train.query.filter_by(active=True).all()

def search_trains(from_station_id, to_station_id, journey_date):
    """Search trains between stations"""
    # Find trains that have both stations in their route
    train_ids = db.session.query(TrainRoute.train_id).filter(
        TrainRoute.station_id == from_station_id
    ).intersect(
        db.session.query(TrainRoute.train_id).filter(
            TrainRoute.station_id == to_station_id
        )
    ).all()
    
    train_ids = [tid[0] for tid in train_ids]
    
    if not train_ids:
        return []
    
    # Get trains and verify route order
    valid_trains = []
    for train_id in train_ids:
        from_route = TrainRoute.query.filter_by(
            train_id=train_id, station_id=from_station_id
        ).first()
        to_route = TrainRoute.query.filter_by(
            train_id=train_id, station_id=to_station_id
        ).first()
        
        # Check if from station comes before to station
        if from_route and to_route and from_route.sequence < to_route.sequence:
            train = Train.query.get(train_id)
            if train and train.active:
                valid_trains.append(train)
    
    return valid_trains

def calculate_fare(train_id, from_station_id, to_station_id, passengers, booking_type='general'):
    """Calculate fare for the journey with Tatkal premium"""
    from_route = TrainRoute.query.filter_by(
        train_id=train_id, station_id=from_station_id
    ).first()
    to_route = TrainRoute.query.filter_by(
        train_id=train_id, station_id=to_station_id
    ).first()
    
    if not from_route or not to_route:
        return 0
    
    distance = abs(to_route.distance_from_start - from_route.distance_from_start)
    train = Train.query.get(train_id)
    
    if not train:
        return 0
    
    # Calculate base fare based on booking type
    if booking_type == 'tatkal' and train.tatkal_fare_per_km:
        base_fare = distance * train.tatkal_fare_per_km * passengers
        # Tatkal surcharge (additional 30% + fixed charge)
        tatkal_surcharge = min(base_fare * 0.3, 500)  # Cap at ₹500
        base_fare += tatkal_surcharge
    else:
        base_fare = distance * train.fare_per_km * passengers
    
    # Add service charges (10%)
    total_fare = base_fare * 1.1
    
    return round(total_fare, 2)

def check_seat_availability(train_id, journey_date):
    """Check available seats for a train on given date (only confirmed bookings)"""
    train = Train.query.get(train_id)
    if not train:
        return 0
    
    # Count only confirmed bookings for the date (not waitlisted)
    booked_passengers = db.session.query(
        db.func.sum(Booking.passengers)
    ).filter(
        Booking.train_id == train_id,
        Booking.journey_date == journey_date,
        Booking.status == 'confirmed'  # Only count confirmed bookings
    ).scalar() or 0
    
    return max(0, train.total_seats - booked_passengers)

def generate_booking_report(start_date, end_date):
    """Generate booking report for date range"""
    bookings = Booking.query.filter(
        and_(
            Booking.booking_date >= start_date,
            Booking.booking_date <= end_date
        )
    ).all()
    
    return bookings

def get_popular_routes():
    """Get most popular routes"""
    popular_routes = db.session.query(
        Station.name.label('from_station'),
        Station.name.label('to_station'),
        db.func.count(Booking.id).label('booking_count')
    ).select_from(Booking).join(
        Station, Booking.from_station_id == Station.id
    ).join(
        Station, Booking.to_station_id == Station.id
    ).group_by(
        Booking.from_station_id, Booking.to_station_id
    ).order_by(
        db.func.count(Booking.id).desc()
    ).limit(10).all()
    
    return popular_routes

def get_station_by_name(name):
    """Get station by name"""
    return Station.query.filter_by(name=name).first()

def get_train_by_number(number):
    """Get train by number"""
    return Train.query.filter_by(number=number).first()

def validate_journey_date(date_string):
    """Validate journey date"""
    try:
        journey_date = datetime.strptime(date_string, '%Y-%m-%d').date()
        return journey_date >= date.today()
    except ValueError:
        return False

def format_currency(amount):
    """Format currency"""
    return f"₹{amount:,.2f}"

def check_tatkal_availability(journey_date):
    """Check if Tatkal booking is available for the date"""
    from datetime import timedelta
    
    # Tatkal booking opens 1 day before travel (for AC) or same day (for non-AC)
    today = date.today()
    tatkal_open_date = journey_date - timedelta(days=1)
    
    return today >= tatkal_open_date

def get_booking_statistics():
    """Get booking statistics with Tatkal breakdown"""
    total_bookings = Booking.query.count()
    confirmed_bookings = Booking.query.filter_by(status='confirmed').count()
    waitlisted_bookings = Booking.query.filter_by(status='waitlisted').count()
    cancelled_bookings = Booking.query.filter_by(status='cancelled').count()
    tatkal_bookings = Booking.query.filter_by(booking_type='tatkal').count()
    
    return {
        'total': total_bookings,
        'confirmed': confirmed_bookings,
        'waitlisted': waitlisted_bookings,
        'cancelled': cancelled_bookings,
        'tatkal': tatkal_bookings
    }
