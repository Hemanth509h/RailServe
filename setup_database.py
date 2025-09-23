#!/usr/bin/env python3
"""
Railway Database Setup Script - Essential Tables Only
Creates clean database schema with core railway booking functionality

This script creates only the essential tables needed for:
- User authentication
- Station and train management  
- Booking and passenger management
- Payment processing
- Waitlist management
- Chart preparation

Usage:
    python setup_database.py

Environment Variables:
    DATABASE_URL: PostgreSQL connection string (optional - defaults to SQLite)
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
    """Initialize database with essential railway data only"""
    
    # Safety check - don't run in production
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        logger.error("Database setup script should not be run in production!")
        sys.exit(1)
    
    logger.info("Starting Railway Database Setup - Essential Tables Only")
    logger.info("Creating: Users, Stations, Trains, Routes, Bookings, Payments, Waitlist")
    logger.info("=" * 70)
    
    # Import Flask app and models
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from src.app import app, db
        
        with app.app_context():
            # Import only essential models
            from src.models import (
                User, Station, Train, TrainRoute, 
                Booking, Passenger, Payment, Waitlist, ChartPreparation
            )
            
            logger.info("Dropping existing tables...")
            db.drop_all()
            
            logger.info("Creating essential database schema...")
            db.create_all()
            
            # Verify essential tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            essential_tables = ['user', 'station', 'train', 'train_route', 'booking', 
                              'passenger', 'payment', 'waitlist', 'chart_preparation']
            
            created_tables = [t for t in essential_tables if t in tables]
            logger.info(f"Created {len(created_tables)} essential tables: {', '.join(created_tables)}")
            
            # Create admin user if requested
            create_admin_user(User)
            
            # Create sample data for testing
            logger.info("Creating sample railway data...")
            create_sample_data(Station, Train, TrainRoute, User, Booking, Passenger, 
                             Payment, Waitlist, ChartPreparation)
            
            logger.info("✅ Database setup completed successfully!")
            logger.info("Essential railway booking system is ready")
            
    except Exception as e:
        logger.error(f"❌ Database setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def create_admin_user(User):
    """Create admin user only if explicitly requested"""
    
    admin_password = os.environ.get('ADMIN_PASSWORD')
    create_admin = os.environ.get('CREATE_ADMIN', '').lower() in ['1', 'true', 'yes']
    
    if create_admin:
        if not admin_password:
            logger.error("CREATE_ADMIN=1 requires ADMIN_PASSWORD environment variable")
            sys.exit(1)
        
        # Check if admin already exists
        existing_admin = User.query.filter_by(username='admin').first()
        if existing_admin:
            logger.info("Admin user already exists, skipping creation")
            return
        
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash(admin_password)
        
        admin = User(
            username='admin',
            email='admin@railserve.com',
            password_hash=password_hash,
            role='super_admin',
            active=True
        )
        
        from src.app import db
        db.session.add(admin)
        db.session.commit()
        logger.info("✅ Created admin user with provided password")
    else:
        logger.info("⏭️  Skipping admin user creation (set CREATE_ADMIN=1 and ADMIN_PASSWORD to create)")

def create_sample_data(Station, Train, TrainRoute, User, Booking, Passenger, Payment, Waitlist, ChartPreparation):
    """Create essential sample data for testing"""
    from src.app import db
    
    # Create sample user for testing
    create_sample_user(User)
    
    # Create 20 major stations
    logger.info("Creating 20 major railway stations...")
    create_major_stations(Station)
    
    # Create 30 trains
    logger.info("Creating 30 trains...")
    create_essential_trains(Train)
    
    # Create routes
    logger.info("Creating train routes...")
    create_train_routes(Train, Station, TrainRoute)
    
    # Create sample bookings
    logger.info("Creating sample bookings...")
    create_sample_bookings(User, Train, Station, Booking, Passenger, Payment, Waitlist)
    
    # Create chart preparation records
    logger.info("Creating chart preparation samples...")
    create_chart_preparation_records(Train, ChartPreparation)

def create_sample_user(User):
    """Create a sample regular user for testing"""
    from src.app import db
    from werkzeug.security import generate_password_hash
    
    # Check if sample user already exists
    existing_user = User.query.filter_by(email='user@example.com').first()
    if existing_user:
        logger.info("Sample user already exists")
        return
    
    sample_user = User(
        username='testuser',
        email='user@example.com',
        password_hash=generate_password_hash('password123'),
        role='user',
        active=True
    )
    
    db.session.add(sample_user)
    db.session.commit()
    logger.info("✅ Created sample user: username='testuser', email='user@example.com', password='password123'")

def create_major_stations(Station):
    """Create 20 major Indian railway stations"""
    from src.app import db
    
    major_stations = [
        ('NDLS', 'New Delhi', 'New Delhi', 'Delhi'),
        ('CSMT', 'Mumbai CST', 'Mumbai', 'Maharashtra'),
        ('HWH', 'Howrah Junction', 'Kolkata', 'West Bengal'),
        ('MAS', 'Chennai Central', 'Chennai', 'Tamil Nadu'),
        ('SBC', 'Bangalore City', 'Bangalore', 'Karnataka'),
        ('PUNE', 'Pune Junction', 'Pune', 'Maharashtra'),
        ('ADI', 'Ahmedabad Junction', 'Ahmedabad', 'Gujarat'),
        ('JP', 'Jaipur Junction', 'Jaipur', 'Rajasthan'),
        ('LKO', 'Lucknow Junction', 'Lucknow', 'Uttar Pradesh'),
        ('PNBE', 'Patna Junction', 'Patna', 'Bihar'),
        ('BPL', 'Bhopal Junction', 'Bhopal', 'Madhya Pradesh'),
        ('SC', 'Secunderabad Junction', 'Hyderabad', 'Telangana'),
        ('ERS', 'Ernakulam Junction', 'Kochi', 'Kerala'),
        ('BZA', 'Vijayawada Junction', 'Vijayawada', 'Andhra Pradesh'),
        ('BBS', 'Bhubaneswar', 'Bhubaneswar', 'Odisha'),
        ('CDG', 'Chandigarh', 'Chandigarh', 'Chandigarh'),
        ('JAT', 'Jammu Tawi', 'Jammu', 'J&K'),
        ('CBE', 'Coimbatore Junction', 'Coimbatore', 'Tamil Nadu'),
        ('NGP', 'Nagpur', 'Nagpur', 'Maharashtra'),
        ('ASN', 'Asansol Junction', 'Asansol', 'West Bengal')
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
    logger.info(f"✅ Created {len(stations)} major railway stations")

def create_essential_trains(Train):
    """Create 30 essential trains with realistic configurations"""
    from src.app import db
    
    train_data = [
        ('12001', 'Rajdhani Express', 400, 2.5, 40, 3.5),
        ('12002', 'Shatabdi Express', 350, 2.0, 35, 3.0),
        ('12003', 'Duronto Express', 450, 1.8, 45, 2.8),
        ('12004', 'Superfast Express', 400, 1.2, 40, 2.0),
        ('12005', 'Tamil Nadu Express', 350, 0.8, 35, 1.5),
        ('12006', 'Howrah Express', 380, 1.0, 38, 1.8),
        ('12007', 'Kerala Express', 360, 0.9, 36, 1.6),
        ('12008', 'Deccan Queen', 320, 1.5, 32, 2.2),
        ('12009', 'Konkan Kanya Express', 340, 1.1, 34, 1.9),
        ('12010', 'Punjab Mail', 380, 1.0, 38, 1.8),
        ('22001', 'Garib Rath', 300, 0.7, 30, 1.2),
        ('22002', 'Golden Temple Mail', 350, 0.9, 35, 1.6),
        ('22003', 'Island Express', 320, 0.8, 32, 1.4),
        ('22004', 'Coromandel Express', 360, 1.0, 36, 1.8),
        ('22005', 'Brindavan Express', 280, 1.2, 28, 2.0),
        ('22006', 'Mysore Express', 300, 1.0, 30, 1.8),
        ('22007', 'Chennai Express', 380, 1.1, 38, 1.9),
        ('22008', 'Mumbai Express', 400, 1.2, 40, 2.0),
        ('22009', 'Delhi Express', 420, 1.3, 42, 2.1),
        ('22010', 'Kolkata Express', 360, 1.0, 36, 1.8),
        ('11001', 'Intercity Express', 250, 0.8, 25, 1.4),
        ('11002', 'Jan Shatabdi', 280, 1.0, 28, 1.8),
        ('11003', 'Passenger Express', 200, 0.5, 20, 0.9),
        ('11004', 'Mail Express', 300, 0.7, 30, 1.2),
        ('11005', 'Fast Passenger', 220, 0.6, 22, 1.0),
        ('11006', 'City Express', 250, 0.8, 25, 1.4),
        ('11007', 'Local Express', 180, 0.4, 18, 0.8),
        ('11008', 'Regional Express', 240, 0.7, 24, 1.2),
        ('11009', 'Valley Express', 200, 0.6, 20, 1.0),
        ('11010', 'Hills Express', 220, 0.8, 22, 1.4)
    ]
    
    trains = []
    for number, name, total_seats, fare_per_km, tatkal_seats, tatkal_fare_per_km in train_data:
        train = Train(
            number=number,
            name=name,
            total_seats=total_seats,
            available_seats=total_seats,
            fare_per_km=fare_per_km,
            tatkal_seats=tatkal_seats,
            tatkal_fare_per_km=tatkal_fare_per_km,
            active=True
        )
        trains.append(train)
    
    db.session.add_all(trains)
    db.session.commit()
    logger.info(f"✅ Created {len(trains)} trains with realistic configurations")

def create_train_routes(Train, Station, TrainRoute):
    """Create realistic train routes"""
    from src.app import db
    
    trains = Train.query.all()
    stations = Station.query.all()
    
    routes = []
    for train in trains:
        # Create route with 3-6 stations per train
        route_length = random.randint(3, 6)
        selected_stations = random.sample(stations, route_length)
        
        total_distance = 0
        current_time = time(6, 0)  # Start at 6:00 AM
        
        for sequence, station in enumerate(selected_stations):
            if sequence == 0:
                # First station
                departure_time = current_time
                arrival_time = None
                distance = 0
            elif sequence == len(selected_stations) - 1:
                # Last station
                segment_distance = random.randint(80, 250)
                total_distance += segment_distance
                
                # Add travel time
                travel_minutes = int(segment_distance * 0.8) + random.randint(10, 30)
                current_time = add_minutes_to_time(current_time, travel_minutes)
                
                arrival_time = current_time
                departure_time = None
                distance = total_distance
            else:
                # Intermediate station
                segment_distance = random.randint(80, 250)
                total_distance += segment_distance
                
                # Add travel time
                travel_minutes = int(segment_distance * 0.8) + random.randint(10, 30)
                current_time = add_minutes_to_time(current_time, travel_minutes)
                
                arrival_time = current_time
                
                # Add halt time
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
    logger.info(f"✅ Created realistic routes for {len(trains)} trains")

def add_minutes_to_time(time_obj, minutes):
    """Add minutes to a time object"""
    dt = datetime.combine(date.today(), time_obj)
    dt += timedelta(minutes=minutes)
    return dt.time()

def create_sample_bookings(User, Train, Station, Booking, Passenger, Payment, Waitlist):
    """Create 100 sample bookings for testing"""
    from src.app import db
    
    users = User.query.all()
    trains = Train.query.all()
    
    if not users or not trains:
        logger.warning("⚠️  Missing users or trains for creating bookings")
        return
    
    bookings = []
    passengers = []
    payments = []
    waitlists = []
    
    for i in range(100):
        user = random.choice(users)
        train = random.choice(trains)
        
        # Get route stations
        route_stations = [route.station for route in train.routes]
        if len(route_stations) < 2:
            continue
        
        from_station = random.choice(route_stations[:-1])
        remaining_stations = route_stations[route_stations.index(from_station) + 1:]
        to_station = random.choice(remaining_stations)
        
        # Generate booking details
        journey_date = date.today() + timedelta(days=random.randint(1, 30))
        passenger_count = random.randint(1, 4)
        
        # Calculate amount
        from_route = next((r for r in train.routes if r.station_id == from_station.id), None)
        to_route = next((r for r in train.routes if r.station_id == to_station.id), None)
        
        if not from_route or not to_route:
            continue
        
        distance = to_route.distance_from_start - from_route.distance_from_start
        total_amount = distance * train.fare_per_km * passenger_count + random.uniform(10, 50)
        
        # Generate PNR
        pnr = f"PNR{1000000 + i}"
        
        # Status distribution
        status_choices = ['confirmed', 'waitlisted', 'cancelled']
        status = random.choices(status_choices, weights=[70, 20, 10])[0]
        
        booking = Booking(
            pnr=pnr,
            user_id=user.id,
            train_id=train.id,
            from_station_id=from_station.id,
            to_station_id=to_station.id,
            journey_date=journey_date,
            passengers=passenger_count,
            total_amount=total_amount,
            booking_type=random.choice(['general', 'tatkal']),
            quota='general',
            coach_class=random.choice(['SL', 'AC3', 'AC2', '2S']),
            status=status
        )
        bookings.append(booking)
        
        # Update train seats
        if status == 'confirmed':
            train.available_seats = max(0, train.available_seats - passenger_count)
    
    db.session.add_all(bookings)
    db.session.commit()
    
    # Create passengers and payments
    for booking in bookings:
        # Passengers
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
        
        # Payment
        if booking.status in ['confirmed', 'cancelled']:
            payment = Payment(
                booking_id=booking.id,
                user_id=booking.user_id,
                amount=booking.total_amount,
                payment_method=random.choice(['card', 'upi', 'netbanking']),
                status='success' if booking.status == 'confirmed' else 'failed',
                transaction_id=f"TXN{random.randint(10000000, 99999999)}"
            )
            payments.append(payment)
        
        # Waitlist entry
        if booking.status == 'waitlisted':
            waitlist = Waitlist(
                booking_id=booking.id,
                train_id=train.id,
                journey_date=journey_date,
                position=random.randint(1, 50),
                waitlist_type='GNWL'
            )
            waitlists.append(waitlist)
    
    db.session.add_all(passengers + payments + waitlists)
    db.session.commit()
    
    logger.info(f"✅ Created {len(bookings)} sample bookings with passengers and payments")

def create_chart_preparation_records(Train, ChartPreparation):
    """Create chart preparation records for today and tomorrow"""
    from src.app import db
    
    trains = Train.query.limit(10).all()  # Only for first 10 trains
    chart_records = []
    
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    for train in trains:
        # Chart for today
        if random.random() < 0.7:  # 70% chance to have chart
            chart_today = ChartPreparation(
                train_id=train.id,
                journey_date=today,
                status=random.choice(['prepared', 'final']),
                chart_prepared_at=datetime.utcnow() - timedelta(hours=random.randint(1, 12)),
                confirmed_from_waitlist=random.randint(0, 10),
                cancelled_waitlist=random.randint(0, 5)
            )
            
            if chart_today.status == 'final':
                chart_today.final_chart_at = chart_today.chart_prepared_at + timedelta(minutes=random.randint(30, 120))
            
            chart_records.append(chart_today)
        
        # Chart for tomorrow
        if random.random() < 0.5:  # 50% chance to have chart
            chart_tomorrow = ChartPreparation(
                train_id=train.id,
                journey_date=tomorrow,
                status=random.choice(['pending', 'prepared']),
                chart_prepared_at=datetime.utcnow() - timedelta(hours=random.randint(1, 6)) if random.random() < 0.7 else None,
                confirmed_from_waitlist=random.randint(0, 8),
                cancelled_waitlist=random.randint(0, 3)
            )
            chart_records.append(chart_tomorrow)
    
    db.session.add_all(chart_records)
    db.session.commit()
    
    logger.info(f"✅ Created {len(chart_records)} chart preparation records")

if __name__ == '__main__':
    setup_database()