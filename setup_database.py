#!/usr/bin/env python3
"""
Railway Database Setup Script - Simplified & Optimized
Creates core database schema and populates with essential railway data
Focuses on core functionality: 50 stations, 100 trains, sample bookings

Usage:
    python setup_database.py

Environment Variables:
    DATABASE_URL: PostgreSQL connection string
    CREATE_ADMIN: Set to '1' to create admin user
    ADMIN_PASSWORD: Admin password (required if CREATE_ADMIN=1)
"""

import os
import sys
from datetime import datetime, date, time, timedelta
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_database():
    """Initialize database with essential railway data"""
    
    # Safety check
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        logger.error("Database setup script should not be run in production!")
        sys.exit(1)
    
    logger.info("Starting Railway Database Setup (Simplified)...")
    logger.info("Target: 50 stations, 100 trains, 500 sample bookings")
    logger.info("=" * 60)
    
    # Import Flask app and models
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from src.app import app, db
        from src import models  # Import all models
        
        with app.app_context():
            logger.info("Creating database schema...")
            
            # Only drop tables in development
            logger.warning("DROPPING ALL TABLES - This will delete all data!")
            db.drop_all()
            
            # Create essential tables only
            create_essential_tables(db)
            logger.info("Database schema created successfully")
            
            # Populate with essential railway data
            logger.info("Populating database with essential railway data...")
            populate_essential_data(db)
            
            logger.info("Database setup completed successfully!")
            logger.info("Created 50 stations, 100 trains, and sample bookings")
            
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def create_essential_tables(db):
    """Create only essential tables for core functionality"""
    
    # Import essential models only
    from src.models import (
        User, Station, Train, TrainRoute, Booking, Passenger, 
        Payment, Waitlist, ChartPreparation
    )
    
    # Create tables
    db.create_all()
    logger.info("Essential tables created: User, Station, Train, TrainRoute, Booking, Passenger, Payment, Waitlist, ChartPreparation")

def populate_essential_data(db):
    """Populate database with essential railway data"""
    
    from src.models import User, Station, Train, TrainRoute, Booking, Passenger, Payment, Waitlist, ChartPreparation
    
    # Create admin user if requested
    create_admin_user(db, User)
    
    # Create sample user for testing
    create_sample_user(db, User)
    
    # Create 50 major Indian railway stations
    logger.info("Creating 50 major railway stations...")
    create_major_stations(db, Station)
    
    # Create 100 trains
    logger.info("Creating 100 trains...")
    create_essential_trains(db, Train)
    
    # Create train routes
    logger.info("Creating train routes...")
    create_essential_routes(db, Train, Station, TrainRoute)
    
    # Create sample bookings and related data
    logger.info("Creating sample bookings...")
    create_sample_bookings(db, User, Train, Station, Booking, Passenger, Payment)
    
    # Create sample chart preparation records
    logger.info("Creating chart preparation samples...")
    create_sample_chart_preparation(db, Train, ChartPreparation)

def create_admin_user(db, User):
    """Create admin user only if explicitly requested"""
    
    admin_password = os.environ.get('ADMIN_PASSWORD')
    create_admin = os.environ.get('CREATE_ADMIN', '').lower() in ['1', 'true', 'yes']
    
    if create_admin:
        if not admin_password:
            logger.error("CREATE_ADMIN=1 requires ADMIN_PASSWORD environment variable")
            sys.exit(1)
        
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash(admin_password)
        
        admin = User(
            username='admin',
            email='admin@railserve.com',
            password_hash=password_hash,
            role='super_admin',
            active=True
        )
        
        db.session.add(admin)
        db.session.commit()
        logger.info("Created admin user with provided password")
    else:
        logger.info("Skipping admin user creation (set CREATE_ADMIN=1 and ADMIN_PASSWORD to create)")

def create_sample_user(db, User):
    """Create a sample regular user for testing purposes"""
    
    # Check if sample user already exists
    existing_user = User.query.filter_by(email='user@example.com').first()
    if existing_user:
        logger.info("Sample user already exists, skipping creation")
        return
    
    from werkzeug.security import generate_password_hash
    password_hash = generate_password_hash('password123')
    
    sample_user = User(
        username='sampleuser',
        email='user@example.com',
        password_hash=password_hash,
        role='user',
        active=True
    )
    
    db.session.add(sample_user)
    db.session.commit()
    logger.info("Created sample user: username='sampleuser', email='user@example.com', password='password123'")

def create_major_stations(db, Station):
    """Create 50 major Indian railway stations"""
    
    # Major Indian railway stations
    major_stations = [
        # North India
        ('NDLS', 'New Delhi', 'New Delhi', 'DL'),
        ('DEL', 'Delhi Junction', 'Delhi', 'DL'),
        ('AGC', 'Agra Cantt', 'Agra', 'UP'),
        ('LKO', 'Lucknow Junction', 'Lucknow', 'UP'),
        ('CNB', 'Kanpur Central', 'Kanpur', 'UP'),
        ('PRYJ', 'Prayagraj Junction', 'Prayagraj', 'UP'),
        ('BSB', 'Varanasi Junction', 'Varanasi', 'UP'),
        ('GKP', 'Gorakhpur Junction', 'Gorakhpur', 'UP'),
        ('LJN', 'Lucknow NE Railway', 'Lucknow', 'UP'),
        ('ALD', 'Allahabad Junction', 'Allahabad', 'UP'),
        
        # West India
        ('CSMT', 'Mumbai CST', 'Mumbai', 'MH'),
        ('LTT', 'Lokmanya Tilak Terminus', 'Mumbai', 'MH'),
        ('PUNE', 'Pune Junction', 'Pune', 'MH'),
        ('NGP', 'Nagpur', 'Nagpur', 'MH'),
        ('SUR', 'Solapur', 'Solapur', 'MH'),
        ('ADI', 'Ahmedabad Junction', 'Ahmedabad', 'GJ'),
        ('BRC', 'Vadodara Junction', 'Vadodara', 'GJ'),
        ('ST', 'Surat', 'Surat', 'GJ'),
        ('UDZ', 'Udaipur City', 'Udaipur', 'RJ'),
        ('JP', 'Jaipur Junction', 'Jaipur', 'RJ'),
        
        # South India
        ('MAS', 'Chennai Central', 'Chennai', 'TN'),
        ('SBC', 'Bangalore City', 'Bangalore', 'KA'),
        ('MYS', 'Mysore Junction', 'Mysore', 'KA'),
        ('UBL', 'Hubli Junction', 'Hubli', 'KA'),
        ('CBE', 'Coimbatore Junction', 'Coimbatore', 'TN'),
        ('MDU', 'Madurai Junction', 'Madurai', 'TN'),
        ('TPJ', 'Tiruchirapalli Junction', 'Tiruchirappalli', 'TN'),
        ('TVC', 'Thiruvananthapuram Central', 'Thiruvananthapuram', 'KL'),
        ('ERS', 'Ernakulam Junction', 'Kochi', 'KL'),
        ('CLT', 'Kozhikode', 'Kozhikode', 'KL'),
        
        # East India
        ('HWH', 'Howrah Junction', 'Kolkata', 'WB'),
        ('SDAH', 'Sealdah', 'Kolkata', 'WB'),
        ('BWN', 'Barddhaman Junction', 'Bardhaman', 'WB'),
        ('ASN', 'Asansol Junction', 'Asansol', 'WB'),
        ('PNBE', 'Patna Junction', 'Patna', 'BR'),
        ('DNR', 'Danapur', 'Patna', 'BR'),
        ('RJPB', 'Rajendranagar', 'Patna', 'BR'),
        ('JAT', 'Jammu Tawi', 'Jammu', 'JK'),
        ('UMB', 'Ambala Cantt', 'Ambala', 'HR'),
        ('CDG', 'Chandigarh', 'Chandigarh', 'CH'),
        
        # Central India
        ('BPL', 'Bhopal Junction', 'Bhopal', 'MP'),
        ('JBP', 'Jabalpur', 'Jabalpur', 'MP'),
        ('INDB', 'Indore Junction', 'Indore', 'MP'),
        ('GWL', 'Gwalior', 'Gwalior', 'MP'),
        ('BZA', 'Vijayawada Junction', 'Vijayawada', 'AP'),
        ('SC', 'Secunderabad Junction', 'Hyderabad', 'TS'),
        ('HYB', 'Hyderabad Deccan', 'Hyderabad', 'TS'),
        ('VSKP', 'Visakhapatnam', 'Visakhapatnam', 'AP'),
        ('BBS', 'Bhubaneswar', 'Bhubaneswar', 'OR'),
        ('CTC', 'Cuttack', 'Cuttack', 'OR')
    ]
    
    stations = []
    for code, name, city, state in major_stations:
        station = Station(
            name=name,
            code=code,
            city=city,
            state=state,
            active=True
        )
        stations.append(station)
    
    db.session.add_all(stations)
    db.session.commit()
    logger.info(f"Created {len(stations)} major railway stations")

def create_essential_trains(db, Train):
    """Create 100 essential trains with realistic configurations"""
    
    # Train types and their characteristics
    train_types = [
        ('Rajdhani', 400, 2.5, 40, 3.5),  # name, seats, fare_per_km, tatkal_seats, tatkal_fare
        ('Shatabdi', 350, 2.0, 35, 3.0),
        ('Duronto', 450, 1.8, 45, 2.8),
        ('Superfast', 400, 1.2, 40, 2.0),
        ('Mail/Express', 350, 0.8, 35, 1.5),
        ('Passenger', 200, 0.4, 20, 0.8),
        ('Intercity', 300, 1.0, 30, 1.8),
        ('Jan Shatabdi', 320, 1.5, 32, 2.2)
    ]
    
    famous_train_names = [
        'Rajdhani Express', 'Shatabdi Express', 'Duronto Express', 'Garib Rath',
        'Punjab Mail', 'Golden Temple Mail', 'Deccan Queen', 'Island Express',
        'Konkan Kanya Express', 'Kerala Express', 'Tamil Nadu Express', 'Coromandel Express',
        'Howrah Express', 'Kalka Mail', 'Himalayan Queen', 'Nilgiri Express',
        'Brindavan Express', 'Mysore Express', 'Bangalore Express', 'Chennai Express',
        'Mumbai Express', 'Delhi Express', 'Kolkata Express', 'Hyderabad Express',
        'Lucknow Express', 'Varanasi Express', 'Amritsar Express', 'Ahmedabad Express',
        'Pune Express', 'Nagpur Express', 'Bhopal Express', 'Indore Express'
    ]
    
    trains = []
    train_number = 12001
    
    for i in range(100):
        # Select train type
        train_type, base_seats, base_fare, base_tatkal_seats, base_tatkal_fare = random.choice(train_types)
        
        # Select train name
        if i < len(famous_train_names):
            train_name = famous_train_names[i]
        else:
            train_name = f"{random.choice(['Super', 'Express', 'Fast', 'Premium'])} {random.choice(['Express', 'Mail', 'Passenger'])}"
        
        # Add some variation to the base values
        total_seats = base_seats + random.randint(-50, 50)
        fare_per_km = base_fare + random.uniform(-0.2, 0.2)
        tatkal_seats = base_tatkal_seats + random.randint(-5, 5)
        tatkal_fare_per_km = base_tatkal_fare + random.uniform(-0.3, 0.3)
        
        # Ensure reasonable bounds
        total_seats = max(150, min(500, total_seats))
        fare_per_km = max(0.3, min(3.0, fare_per_km))
        tatkal_seats = max(10, min(total_seats // 10, tatkal_seats))
        tatkal_fare_per_km = max(0.5, min(4.0, tatkal_fare_per_km))
        
        train = Train(
            number=str(train_number),
            name=train_name,
            total_seats=total_seats,
            available_seats=total_seats,  # Initially all seats available
            fare_per_km=fare_per_km,
            tatkal_seats=tatkal_seats,
            tatkal_fare_per_km=tatkal_fare_per_km,
            active=True
        )
        trains.append(train)
        train_number += 1
    
    db.session.add_all(trains)
    db.session.commit()
    logger.info(f"Created {len(trains)} trains with realistic configurations")

def create_essential_routes(db, Train, Station, TrainRoute):
    """Create essential train routes connecting major stations"""
    
    trains = Train.query.all()
    stations = Station.query.all()
    
    # Create a mapping of stations by state for logical routing
    station_by_state = {}
    for station in stations:
        if station.state not in station_by_state:
            station_by_state[station.state] = []
        station_by_state[station.state].append(station)
    
    routes = []
    
    for train in trains:
        # Create routes with 3-8 stations per train
        route_length = random.randint(3, 8)
        
        # Pick a starting state and create a logical route
        start_state = random.choice(list(station_by_state.keys()))
        route_stations = []
        
        # Add starting station
        start_station = random.choice(station_by_state[start_state])
        route_stations.append(start_station)
        
        # Add intermediate stations (mix of same state and neighboring states)
        for i in range(1, route_length - 1):
            # 70% chance to pick from same state, 30% from different state
            if random.random() < 0.7 and len(station_by_state[start_state]) > 1:
                available_stations = [s for s in station_by_state[start_state] if s not in route_stations]
                if available_stations:
                    route_stations.append(random.choice(available_stations))
                else:
                    # Pick from any state if no more stations in current state
                    available_stations = [s for s in stations if s not in route_stations]
                    route_stations.append(random.choice(available_stations))
            else:
                available_stations = [s for s in stations if s not in route_stations]
                route_stations.append(random.choice(available_stations))
        
        # Add end station (preferably from a different state)
        end_candidates = [s for s in stations if s not in route_stations and s.state != start_state]
        if end_candidates:
            route_stations.append(random.choice(end_candidates))
        else:
            available_stations = [s for s in stations if s not in route_stations]
            route_stations.append(random.choice(available_stations))
        
        # Create route entries with realistic timings and distances
        total_distance = 0
        current_time = time(6, 0)  # Start at 6:00 AM
        
        for sequence, station in enumerate(route_stations):
            if sequence == 0:
                # First station - only departure
                departure_time = current_time
                arrival_time = None
                distance = 0
            elif sequence == len(route_stations) - 1:
                # Last station - only arrival
                segment_distance = random.randint(50, 200)
                total_distance += segment_distance
                
                # Add travel time (roughly 1 hour per 100km)
                travel_minutes = int(segment_distance * 0.6) + random.randint(10, 30)
                current_time = add_minutes_to_time(current_time, travel_minutes)
                
                arrival_time = current_time
                departure_time = None
                distance = total_distance
            else:
                # Intermediate station - both arrival and departure
                segment_distance = random.randint(50, 200)
                total_distance += segment_distance
                
                # Add travel time
                travel_minutes = int(segment_distance * 0.6) + random.randint(10, 30)
                current_time = add_minutes_to_time(current_time, travel_minutes)
                
                arrival_time = current_time
                
                # Add halt time (5-15 minutes)
                halt_minutes = random.randint(5, 15)
                current_time = add_minutes_to_time(current_time, halt_minutes)
                departure_time = current_time
                distance = total_distance
            
            route = TrainRoute(
                train_id=train.id,
                station_id=station.id,
                sequence=sequence + 1,
                arrival_time=arrival_time,
                departure_time=departure_time,
                distance_from_start=distance
            )
            routes.append(route)
    
    db.session.add_all(routes)
    db.session.commit()
    logger.info(f"Created routes for {len(trains)} trains with realistic schedules")

def add_minutes_to_time(time_obj, minutes):
    """Add minutes to a time object, handling day overflow"""
    dt = datetime.combine(date.today(), time_obj)
    dt += timedelta(minutes=minutes)
    return dt.time()

def create_sample_bookings(db, User, Train, Station, Booking, Passenger, Payment):
    """Create sample bookings for testing"""
    
    users = User.query.all()
    trains = Train.query.all()
    stations = Station.query.all()
    
    if not users or not trains or not stations:
        logger.warning("Missing data for creating bookings")
        return
    
    bookings = []
    passengers = []
    payments = []
    
    # Create 500 sample bookings
    for i in range(500):
        user = random.choice(users)
        train = random.choice(trains)
        
        # Get route stations for this train
        route_stations = [route.station for route in train.routes]
        if len(route_stations) < 2:
            continue
        
        # Pick from and to stations from the route
        from_station = random.choice(route_stations[:-1])
        remaining_stations = route_stations[route_stations.index(from_station) + 1:]
        to_station = random.choice(remaining_stations)
        
        # Generate booking details
        journey_date = date.today() + timedelta(days=random.randint(1, 30))
        passenger_count = random.randint(1, 4)
        
        # Calculate distance and amount
        from_route = next((r for r in train.routes if r.station_id == from_station.id), None)
        to_route = next((r for r in train.routes if r.station_id == to_station.id), None)
        
        if not from_route or not to_route:
            continue
        
        distance = to_route.distance_from_start - from_route.distance_from_start
        base_amount = distance * train.fare_per_km * passenger_count
        total_amount = base_amount + random.uniform(0, 50)  # Add some fees/taxes
        
        # Generate PNR
        pnr = f"PNR{1000000 + i}"
        
        # Random booking type and status
        booking_type = 'tatkal' if random.random() < 0.2 else 'general'
        status_choices = ['confirmed', 'waitlisted', 'cancelled', 'pending_payment']
        status = random.choices(status_choices, weights=[60, 20, 10, 10])[0]
        
        booking = Booking(
            pnr=pnr,
            user_id=user.id,
            train_id=train.id,
            from_station_id=from_station.id,
            to_station_id=to_station.id,
            journey_date=journey_date,
            passengers=passenger_count,
            total_amount=total_amount,
            booking_type=booking_type,
            quota='general',
            coach_class=random.choice(['SL', 'AC3', 'AC2', 'AC1', '2S']),
            status=status,
            booking_date=datetime.utcnow() - timedelta(days=random.randint(0, 30))
        )
        bookings.append(booking)
        
        # Update train available seats if booking is confirmed
        if status == 'confirmed':
            train.available_seats = max(0, train.available_seats - passenger_count)
    
    db.session.add_all(bookings)
    db.session.commit()
    
    # Create passenger details for bookings
    for booking in bookings:
        for p_num in range(booking.passengers):
            passenger = Passenger(
                booking_id=booking.id,
                name=f"Passenger {p_num + 1}",
                age=random.randint(18, 70),
                gender=random.choice(['Male', 'Female']),
                id_proof_type='Aadhar',
                id_proof_number=f"XXXX-XXXX-{random.randint(1000, 9999)}"
            )
            passengers.append(passenger)
    
    db.session.add_all(passengers)
    
    # Create payment records for confirmed bookings
    for booking in bookings:
        if booking.status in ['confirmed', 'cancelled']:
            payment = Payment(
                booking_id=booking.id,
                user_id=booking.user_id,
                amount=booking.total_amount,
                payment_method=random.choice(['card', 'upi', 'netbanking']),
                status='success' if booking.status == 'confirmed' else 'failed',
                transaction_id=f"TXN{random.randint(10000000, 99999999)}",
                payment_date=booking.booking_date + timedelta(minutes=random.randint(1, 30))
            )
            payments.append(payment)
    
    db.session.add_all(payments)
    db.session.commit()
    
    logger.info(f"Created {len(bookings)} sample bookings with passengers and payments")

def create_sample_chart_preparation(db, Train, ChartPreparation):
    """Create sample chart preparation records"""
    
    trains = Train.query.all()
    chart_records = []
    
    # Create chart preparation for some trains
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    for train in trains[:20]:  # Only for first 20 trains
        # Chart for today (some prepared, some final)
        status = random.choice(['prepared', 'final', 'pending'])
        if status != 'pending':
            chart_today = ChartPreparation(
                train_id=train.id,
                journey_date=today,
                status=status,
                chart_prepared_at=datetime.utcnow() - timedelta(hours=random.randint(1, 12)),
                confirmed_from_waitlist=random.randint(0, 10),
                cancelled_waitlist=random.randint(0, 5)
            )
            
            if status == 'final':
                chart_today.final_chart_at = chart_today.chart_prepared_at + timedelta(minutes=random.randint(30, 120))
            
            chart_records.append(chart_today)
        
        # Chart for tomorrow (mostly pending or prepared)
        status = random.choice(['pending', 'prepared'])
        if status == 'prepared':
            chart_tomorrow = ChartPreparation(
                train_id=train.id,
                journey_date=tomorrow,
                status=status,
                chart_prepared_at=datetime.utcnow() - timedelta(hours=random.randint(1, 6)),
                confirmed_from_waitlist=random.randint(0, 8),
                cancelled_waitlist=random.randint(0, 3)
            )
            chart_records.append(chart_tomorrow)
    
    db.session.add_all(chart_records)
    db.session.commit()
    
    logger.info(f"Created {len(chart_records)} chart preparation records")

if __name__ == '__main__':
    setup_database()