from .models import Train, Station, Booking, TrainRoute, SeatAvailability
from .database import db
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

def get_all_class_availability(train_id, from_station_id, to_station_id, journey_date):
    """Get seat availability for all coach classes for a train"""
    coach_classes = ['AC1', 'AC2', 'AC3', 'SL', '2S', 'CC']
    availability = {}
    
    try:
        journey_date_obj = datetime.strptime(str(journey_date), '%Y-%m-%d').date() if isinstance(journey_date, str) else journey_date
    except:
        journey_date_obj = date.today()
    
    for coach_class in coach_classes:
        avail_data = check_seat_availability_detailed(
            train_id, from_station_id, to_station_id, 
            journey_date_obj, coach_class, 'general'
        )
        availability[coach_class] = avail_data
    
    return availability

def calculate_fare(train_id, from_station_id, to_station_id, passengers, booking_type='general', coach_class='SL', passenger_details=None):
    """Calculate fare for the journey with coach class multipliers and age-based concessions"""
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
    
    # Coach class multipliers for fare calculation
    coach_multipliers = {
        'AC1': 5.0,  # AC First Class
        'AC2': 3.0,  # AC 2 Tier
        'AC3': 2.0,  # AC 3 Tier
        'SL': 1.0,   # Sleeper Class
        '2S': 0.6,   # Second Sitting
        'CC': 1.2    # Chair Car
    }
    
    coach_multiplier = coach_multipliers.get(coach_class, 1.0)
    
    # LOGIC FIX: Calculate base fare correctly with proper Tatkal surcharge
    # Base fare per passenger without any surcharges
    base_fare_per_passenger = distance * train.fare_per_km
    
    if booking_type == 'tatkal' and train.tatkal_fare_per_km:
        # Use Tatkal fare rate if available
        base_fare_per_passenger = distance * train.tatkal_fare_per_km
    
    # Apply coach class multiplier to base fare
    base_fare_per_passenger *= coach_multiplier
    
    # Apply Tatkal surcharge correctly (before passenger count multiplication)
    if booking_type == 'tatkal':
        ac_classes = ['AC1', 'AC2', 'AC3', 'CC']
        max_surcharge_per_passenger = 400 if coach_class in ac_classes else 200
        tatkal_surcharge_per_passenger = min(base_fare_per_passenger * 0.3, max_surcharge_per_passenger)
        base_fare_per_passenger += tatkal_surcharge_per_passenger
    
    # LOGIC FIX: Apply age-based concessions correctly per passenger
    total_fare = 0
    if passenger_details and len(passenger_details) == passengers:
        for passenger in passenger_details:
            age = passenger.get('age', 0)
            gender = passenger.get('gender', 'Male')
            passenger_fare = base_fare_per_passenger
            
            # Senior citizen concession (apply per passenger)
            if (gender == 'Male' and age >= 60) or (gender == 'Female' and age >= 58):
                # 40% discount for male 60+, 50% discount for female 58+
                discount = 0.5 if gender == 'Female' else 0.4
                passenger_fare = passenger_fare * (1 - discount)
            
            # Child fare rules (apply per passenger)
            elif age < 5:
                # Free for children under 5
                passenger_fare = 0
            elif age >= 5 and age <= 12:
                # 50% discount for children 5-12 years
                passenger_fare = passenger_fare * 0.5
            
            total_fare += passenger_fare
    else:
        # No passenger details provided, use standard fare for all passengers
        total_fare = base_fare_per_passenger * passengers
    
    # LOGIC FIX: Add GST and service charges (18%) on final fare after all discounts
    final_fare_with_gst = total_fare * 1.18
    
    return round(final_fare_with_gst, 2)

def calculate_cancellation_charges(booking, cancellation_time=None):
    """Calculate cancellation charges based on time before departure"""
    from datetime import datetime, timedelta
    
    if cancellation_time is None:
        cancellation_time = datetime.utcnow()
    
    # Convert journey_date to datetime for comparison
    journey_datetime = datetime.combine(booking.journey_date, datetime.min.time())
    time_diff = journey_datetime - cancellation_time
    hours_before = time_diff.total_seconds() / 3600
    
    if booking.booking_type == 'tatkal' and booking.status == 'confirmed':
        # No refund for confirmed Tatkal tickets
        return booking.total_amount
    
    if booking.status in ['waitlisted', 'rac']:
        # Flat cancellation charge for waitlist/RAC
        return 60.0
    
    # Time-based cancellation charges for confirmed tickets
    if hours_before >= 48:
        # 48+ hours before departure
        ac_classes = ['AC1', 'AC2', 'AC3', 'CC']
        min_charge = 120 if booking.coach_class in ac_classes else 60
        return min_charge
    elif hours_before >= 12:
        # 12-48 hours before departure
        calculated_charge = booking.total_amount * 0.25
        ac_classes = ['AC1', 'AC2', 'AC3', 'CC']
        min_charge = 120 if booking.coach_class in ac_classes else 60
        return max(calculated_charge, min_charge)
    elif hours_before >= 4:
        # 4-12 hours before departure
        calculated_charge = booking.total_amount * 0.50
        ac_classes = ['AC1', 'AC2', 'AC3', 'CC']
        min_charge = 120 if booking.coach_class in ac_classes else 60
        return max(calculated_charge, min_charge)
    else:
        # Less than 4 hours - no refund
        return booking.total_amount

def get_waitlist_type(from_station_id, to_station_id, train_id):
    """Determine waitlist type based on journey stations"""
    from .models import TrainRoute
    
    # Get train route to determine waitlist type
    from_route = TrainRoute.query.filter_by(
        train_id=train_id, station_id=from_station_id
    ).first()
    to_route = TrainRoute.query.filter_by(
        train_id=train_id, station_id=to_station_id
    ).first()
    
    if not from_route or not to_route:
        return 'GNWL'  # Default to General Waiting List
    
    # Get all routes for this train
    all_routes = TrainRoute.query.filter_by(train_id=train_id).order_by(TrainRoute.sequence).all()
    
    if len(all_routes) == 0:
        return 'GNWL'
    
    start_station = all_routes[0]
    end_station = all_routes[-1]
    
    # PQWL - Pooled Quota Waiting List (intermediate stations)
    if from_route.sequence != start_station.sequence or to_route.sequence != end_station.sequence:
        # Check if it's a popular intermediate section
        total_distance = end_station.distance_from_start - start_station.distance_from_start
        journey_distance = to_route.distance_from_start - from_route.distance_from_start
        
        if journey_distance < (total_distance * 0.3):  # Short distance journey
            return 'PQWL'
    
    # RLWL - Remote Location Waiting List (for remote stations)
    if from_route.sequence > len(all_routes) * 0.7 or to_route.sequence > len(all_routes) * 0.7:
        return 'RLWL'
    
    # Default to GNWL for most cases
    return 'GNWL'

def check_seat_availability_detailed(train_id, from_station_id, to_station_id, journey_date, coach_class='SL', quota='general'):
    """Detailed seat availability checking with different quotas"""
    from .models import SeatAvailability
    
    # Check if we have cached availability data
    availability = SeatAvailability.query.filter_by(
        train_id=train_id,
        from_station_id=from_station_id,
        to_station_id=to_station_id,
        journey_date=journey_date,
        coach_class=coach_class,
        quota=quota
    ).first()
    
    if availability and (datetime.utcnow() - availability.last_updated).total_seconds() < 300:  # 5 minutes cache
        return {
            'available': availability.available_seats,
            'waiting': availability.waiting_list,
            'rac': availability.rac_seats,
            'status': 'Available' if availability.available_seats > 0 else ('RAC' if availability.rac_seats > 0 else 'WL')
        }
    
    # Calculate real-time availability
    train = Train.query.get(train_id)
    if not train:
        return {'available': 0, 'waiting': 0, 'rac': 0, 'status': 'Not Available'}
    
    # Calculate based on quota
    if quota == 'tatkal':
        total_quota_seats = train.tatkal_seats or 0
    else:
        total_quota_seats = train.total_seats - (train.tatkal_seats or 0)
    
    # Count confirmed bookings for this quota
    confirmed_passengers = db.session.query(
        db.func.sum(Booking.passengers)
    ).filter(
        Booking.train_id == train_id,
        Booking.journey_date == journey_date,
        Booking.status == 'confirmed',
        Booking.quota == quota,
        Booking.coach_class == coach_class
    ).scalar() or 0
    
    # Count RAC passengers
    rac_passengers = db.session.query(
        db.func.sum(Booking.passengers)
    ).filter(
        Booking.train_id == train_id,
        Booking.journey_date == journey_date,
        Booking.status == 'rac',
        Booking.quota == quota,
        Booking.coach_class == coach_class
    ).scalar() or 0
    
    # Count waitlisted passengers
    waitlist_passengers = db.session.query(
        db.func.sum(Booking.passengers)
    ).filter(
        Booking.train_id == train_id,
        Booking.journey_date == journey_date,
        Booking.status == 'waitlisted',
        Booking.quota == quota,
        Booking.coach_class == coach_class
    ).scalar() or 0
    
    # LOGIC FIX: Calculate availability correctly
    available_seats = max(0, total_quota_seats - confirmed_passengers)
    # RAC seats should be calculated independently, not dependent on confirmed seats
    max_rac_for_quota = min(10, total_quota_seats // 10)  # 10% of quota or max 10
    rac_seats = max(0, max_rac_for_quota - rac_passengers)
    
    result = {
        'available': available_seats,
        'waiting': waitlist_passengers,
        'rac': rac_seats,
        'status': 'Available' if available_seats > 0 else ('RAC' if rac_seats > 0 else f'WL{waitlist_passengers + 1}')
    }
    
    # Update or create availability cache
    if availability:
        availability.available_seats = available_seats
        availability.waiting_list = waitlist_passengers
        availability.rac_seats = rac_seats
        availability.last_updated = datetime.utcnow()
    else:
        availability = SeatAvailability(
            train_id=train_id,
            from_station_id=from_station_id,
            to_station_id=to_station_id,
            journey_date=journey_date,
            coach_class=coach_class,
            quota=quota,
            available_seats=available_seats,
            waiting_list=waitlist_passengers,
            rac_seats=rac_seats
        )
        db.session.add(availability)
    
    try:
        db.session.commit()
    except:
        db.session.rollback()
    
    return result

def prepare_chart(train_id, journey_date):
    """Prepare chart 4 hours before departure - confirm waitlist and cancel remaining"""
    from .models import ChartPreparation, Waitlist, Booking
    from .queue_manager import WaitlistManager
    from datetime import datetime, timedelta
    
    # Check if chart already prepared
    chart = ChartPreparation.query.filter_by(
        train_id=train_id,
        journey_date=journey_date
    ).first()
    
    if chart and chart.status in ['prepared', 'final']:
        return chart
    
    train = Train.query.get(train_id)
    if not train:
        return None
    
    # Process waitlist one final time
    waitlist_manager = WaitlistManager()
    waitlist_manager.process_waitlist(train_id, journey_date)
    
    # Count confirmed and cancelled from waitlist
    confirmed_from_waitlist = db.session.query(db.func.count(Booking.id)).filter(
        Booking.train_id == train_id,
        Booking.journey_date == journey_date,
        Booking.status == 'confirmed',
        Booking.booking_date >= datetime.utcnow() - timedelta(hours=1)  # Recently confirmed
    ).scalar() or 0
    
    # Cancel remaining waitlisted tickets
    remaining_waitlist = Booking.query.filter(
        Booking.train_id == train_id,
        Booking.journey_date == journey_date,
        Booking.status == 'waitlisted'
    ).all()
    
    cancelled_waitlist = 0
    for booking in remaining_waitlist:
        booking.status = 'cancelled'
        cancelled_waitlist += 1
    
    # Mark all bookings as chart prepared
    Booking.query.filter(
        Booking.train_id == train_id,
        Booking.journey_date == journey_date
    ).update({'chart_prepared': True})
    
    # Create or update chart preparation record
    if not chart:
        chart = ChartPreparation(
            train_id=train_id,
            journey_date=journey_date,
            chart_prepared_at=datetime.utcnow(),
            status='prepared',
            confirmed_from_waitlist=confirmed_from_waitlist,
            cancelled_waitlist=cancelled_waitlist
        )
        db.session.add(chart)
    else:
        chart.chart_prepared_at = datetime.utcnow()
        chart.status = 'prepared'
        chart.confirmed_from_waitlist = confirmed_from_waitlist
        chart.cancelled_waitlist = cancelled_waitlist
    
    # Delete waitlist entries for cancelled bookings
    Waitlist.query.filter(
        Waitlist.train_id == train_id,
        Waitlist.journey_date == journey_date
    ).delete()
    
    db.session.commit()
    return chart

def prepare_final_chart(train_id, journey_date):
    """Prepare final chart 30 minutes before departure and allocate seats"""
    from .models import ChartPreparation, Booking, Passenger
    from .seat_allocation import SeatAllocator
    
    chart = ChartPreparation.query.filter_by(
        train_id=train_id,
        journey_date=journey_date
    ).first()
    
    if chart:
        chart.final_chart_at = datetime.utcnow()
        chart.status = 'final'
        
        # Allocate seats for all confirmed bookings that don't have seats yet
        confirmed_bookings = Booking.query.filter(
            Booking.train_id == train_id,
            Booking.journey_date == journey_date,
            Booking.status == 'confirmed'
        ).all()
        
        seat_allocator = SeatAllocator()
        allocated_count = 0
        
        for booking in confirmed_bookings:
            # Check if any passenger in this booking doesn't have a seat
            passengers_without_seats = Passenger.query.filter(
                Passenger.booking_id == booking.id,
                db.or_(Passenger.seat_number.is_(None), Passenger.seat_number == '')
            ).count()
            
            if passengers_without_seats > 0:
                try:
                    if seat_allocator.allocate_seats(booking.id):
                        allocated_count += 1
                except Exception as e:
                    # Log error but continue with other bookings
                    import logging
                    logging.error(f"Failed to allocate seats for booking {booking.id}: {str(e)}")
        
        db.session.commit()
        
        # Log the allocation results
        import logging
        logging.info(f"Chart finalized for train {train_id} on {journey_date}. Allocated seats for {allocated_count} bookings.")
    
    return chart

def get_live_train_status(train_id, journey_date):
    """Get live train status (simulated)"""
    from .models import TrainStatus, TrainRoute
    import random
    
    # Check existing status
    status = TrainStatus.query.filter_by(
        train_id=train_id,
        journey_date=journey_date
    ).first()
    
    if status and (datetime.utcnow() - status.last_updated).total_seconds() < 600:  # 10 minutes cache
        return status
    
    # Simulate live status
    train_routes = TrainRoute.query.filter_by(train_id=train_id).order_by(TrainRoute.sequence).all()
    
    if not train_routes:
        return None
    
    # Simulate current position
    current_route = random.choice(train_routes)
    delay_minutes = random.choice([0, 0, 0, 5, 10, 15, 30, 45])  # Mostly on time
    
    status_text = 'On Time' if delay_minutes == 0 else 'Delayed'
    
    if not status:
        status = TrainStatus(
            train_id=train_id,
            journey_date=journey_date,
            current_station_id=current_route.station_id,
            status=status_text,
            delay_minutes=delay_minutes,
            last_updated=datetime.utcnow()
        )
        db.session.add(status)
    else:
        status.current_station_id = current_route.station_id
        status.status = status_text
        status.delay_minutes = delay_minutes
        status.last_updated = datetime.utcnow()
    
    try:
        db.session.commit()
    except:
        db.session.rollback()
    
    return status

def check_current_reservation_available(train_id, journey_date):
    """Check if current reservation (post-chart) is available"""
    from .models import ChartPreparation
    from datetime import datetime, timedelta
    
    # Check if chart is prepared
    chart = ChartPreparation.query.filter_by(
        train_id=train_id,
        journey_date=journey_date,
        status='prepared'
    ).first()
    
    if not chart:
        return False
    
    # Current reservation opens after chart preparation
    # and closes 30 minutes before departure
    journey_datetime = datetime.combine(journey_date, datetime.min.time())
    now = datetime.utcnow()
    
    # Closes 30 minutes before departure
    if (journey_datetime - now).total_seconds() < 1800:  # 30 minutes
        return False
    
    return True

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

def check_tatkal_availability(journey_date, coach_class='SL', train_id=None):
    """Check if Tatkal booking is available for the date and coach class using admin-configured time slots or override"""
    from .models import TatkalTimeSlot, TatkalOverride
    from datetime import datetime, timedelta, time
    
    # First check for admin override - if active, allow Tatkal booking anytime
    active_override = TatkalOverride.get_active_override()
    if active_override and active_override.is_valid():
        # Check if override applies to this coach class
        override_classes = active_override.get_coach_classes_list()
        coach_class_valid = not override_classes or coach_class in override_classes
        
        # Check if override applies to this specific train
        train_valid = True
        if train_id:
            train_valid = active_override.applies_to_train(train_id)
        
        if coach_class_valid and train_valid:
            return True
    
    # Get active time slots for the given coach class
    time_slots = TatkalTimeSlot.query.filter_by(active=True).all()
    
    # Real tatkal booking logic - booking opens 1 day before journey at specific times
    today = date.today()
    tatkal_open_date = journey_date - timedelta(days=1)
    
    # If journey date is not tomorrow, tatkal is not available (unless overridden)
    if today != tatkal_open_date:
        return False
    
    if not time_slots:
        # Fallback to real Indian Railways timing
        now = datetime.now().time()
        ac_classes = ['AC1', 'AC2', 'AC3', 'CC']
        
        if coach_class in ac_classes:
            # AC classes: 10:00 AM to 12:00 PM
            return time(10, 0) <= now <= time(12, 0)
        else:
            # Non-AC classes: 11:00 AM to 12:00 PM  
            return time(11, 0) <= now <= time(12, 0)
    
    # Check if any time slot allows booking for this coach class and journey date
    for time_slot in time_slots:
        coach_classes = time_slot.get_coach_classes_list()
        
        # If time slot applies to this coach class (or all classes if none specified)
        if not coach_classes or coach_class in coach_classes:
            if time_slot.is_currently_open(journey_date):
                return True
    
    return False

def is_booking_open(journey_date):
    """Check if booking is open for the journey date"""
    from datetime import timedelta
    
    # Booking is available up to 120 days in advance
    today = date.today()
    max_advance_date = today + timedelta(days=120)
    
    return today <= journey_date <= max_advance_date

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
