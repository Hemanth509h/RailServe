#!/usr/bin/env python3
"""
Railway Database Setup Script - Clean & Efficient
Creates essential database schema with realistic Indian railway data for development and testing.

Features:
- 100 major Indian railway stations (all regions covered)
- 200 trains with realistic routes and configurations
- Admin and test user accounts
- Essential system configurations
- Modular, maintainable code structure

Usage:
    python setup_database.py

Environment Variables:
    DATABASE_URL: Database connection string (optional - defaults to configured database)
    ADMIN_PASSWORD: Admin password (defaults to 'admin123')
"""

import os
import sys
import logging
import random
from datetime import datetime, date, time, timedelta
from werkzeug.security import generate_password_hash

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_database():
    """Initialize database with essential Indian railway data"""
    
    # Safety check - don't run in production
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        logger.error("Database setup should not be run in production!")
        sys.exit(1)
    
    logger.info("🚂 Starting Railway Database Setup")
    logger.info("Creating essential data: stations, trains, users, and configurations")
    logger.info("=" * 60)
    
    # Import Flask app and models
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from src.app import app, db
        
        with app.app_context():
            # Import essential models
            from src.models import (
                User, Station, Train, TrainRoute, Booking, Passenger, 
                Payment, GroupBooking, TatkalTimeSlot
            )
            
            logger.info("Recreating database tables...")
            db.drop_all()
            db.create_all()
            
            # Create essential data
            create_users(db)
            create_stations(db)
            create_trains(db)
            create_routes(db)
            create_system_config(db)
            
            logger.info("🎉 Database setup completed successfully!")
            logger.info("Railway system is ready with essential data for development")
            
    except Exception as e:
        logger.error(f"❌ Database setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def create_users(db):
    """Create admin and test user accounts"""
    logger.info("Creating user accounts...")
    
    from src.models import User
    
    # Admin user
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    admin = User(
        username='admin',
        email='admin@railway.gov.in',
        password_hash=generate_password_hash(admin_password),
        role='super_admin',
        active=True
    )
    
    # Regular test user
    user = User(
        username='testuser',
        email='user@example.com',
        password_hash=generate_password_hash('user123'),
        role='user',
        active=True
    )
    
    db.session.add_all([admin, user])
    db.session.commit()
    logger.info("✅ Created admin (admin/admin123) and testuser (testuser/user123) accounts")

def create_stations(db):
    """Create 100 major Indian railway stations covering all regions"""
    logger.info("Creating 100 major railway stations...")
    
    from src.models import Station
    
    # Major stations across India - covering all regions
    stations_data = [
        # South India - Major stations
        ('MAS', 'Chennai Central', 'Chennai', 'Tamil Nadu'),
        ('SBC', 'Bangalore City', 'Bangalore', 'Karnataka'),
        ('MYS', 'Mysore Junction', 'Mysore', 'Karnataka'),
        ('CBE', 'Coimbatore Junction', 'Coimbatore', 'Tamil Nadu'),
        ('MDU', 'Madurai Junction', 'Madurai', 'Tamil Nadu'),
        ('TPJ', 'Tiruchirapalli Junction', 'Tiruchirappalli', 'Tamil Nadu'),
        ('ERS', 'Ernakulam Junction', 'Kochi', 'Kerala'),
        ('TVC', 'Thiruvananthapuram Central', 'Thiruvananthapuram', 'Kerala'),
        ('CLT', 'Kozhikode', 'Kozhikode', 'Kerala'),
        ('TCR', 'Thrissur', 'Thrissur', 'Kerala'),
        ('SC', 'Secunderabad Junction', 'Hyderabad', 'Telangana'),
        ('BZA', 'Vijayawada Junction', 'Vijayawada', 'Andhra Pradesh'),
        ('VSKP', 'Visakhapatnam', 'Visakhapatnam', 'Andhra Pradesh'),
        ('TPTY', 'Tirupati', 'Tirupati', 'Andhra Pradesh'),
        ('GTL', 'Guntakal Junction', 'Guntakal', 'Andhra Pradesh'),
        
        # North India - Major stations  
        ('NDLS', 'New Delhi', 'New Delhi', 'Delhi'),
        ('LKO', 'Lucknow Junction', 'Lucknow', 'Uttar Pradesh'),
        ('CNB', 'Kanpur Central', 'Kanpur', 'Uttar Pradesh'),
        ('PRYJ', 'Prayagraj Junction', 'Prayagraj', 'Uttar Pradesh'),
        ('BSB', 'Varanasi Junction', 'Varanasi', 'Uttar Pradesh'),
        ('GKP', 'Gorakhpur Junction', 'Gorakhpur', 'Uttar Pradesh'),
        ('AGC', 'Agra Cantt', 'Agra', 'Uttar Pradesh'),
        ('MTJ', 'Mathura Junction', 'Mathura', 'Uttar Pradesh'),
        ('JP', 'Jaipur Junction', 'Jaipur', 'Rajasthan'),
        ('KOTA', 'Kota Junction', 'Kota', 'Rajasthan'),
        ('JU', 'Jodhpur Junction', 'Jodhpur', 'Rajasthan'),
        ('UDZ', 'Udaipur City', 'Udaipur', 'Rajasthan'),
        ('ASR', 'Amritsar Junction', 'Amritsar', 'Punjab'),
        ('LDH', 'Ludhiana Junction', 'Ludhiana', 'Punjab'),
        ('CDG', 'Chandigarh', 'Chandigarh', 'Chandigarh'),
        ('JAT', 'Jammu Tawi', 'Jammu', 'Jammu & Kashmir'),
        
        # West India - Major stations
        ('CSMT', 'Mumbai CST', 'Mumbai', 'Maharashtra'),
        ('LTT', 'Lokmanya Tilak Terminus', 'Mumbai', 'Maharashtra'),
        ('PUNE', 'Pune Junction', 'Pune', 'Maharashtra'),
        ('NGP', 'Nagpur', 'Nagpur', 'Maharashtra'),
        ('BSL', 'Bhusaval Junction', 'Bhusaval', 'Maharashtra'),
        ('MMR', 'Manmad Junction', 'Manmad', 'Maharashtra'),
        ('ADI', 'Ahmedabad Junction', 'Ahmedabad', 'Gujarat'),
        ('BRC', 'Vadodara Junction', 'Vadodara', 'Gujarat'),
        ('ST', 'Surat', 'Surat', 'Gujarat'),
        ('RJT', 'Rajkot Junction', 'Rajkot', 'Gujarat'),
        ('BPL', 'Bhopal Junction', 'Bhopal', 'Madhya Pradesh'),
        ('JBP', 'Jabalpur', 'Jabalpur', 'Madhya Pradesh'),
        ('INDB', 'Indore Junction', 'Indore', 'Madhya Pradesh'),
        ('GWL', 'Gwalior', 'Gwalior', 'Madhya Pradesh'),
        ('JHS', 'Jhansi Junction', 'Jhansi', 'Uttar Pradesh'),
        
        # East India - Major stations
        ('HWH', 'Howrah Junction', 'Kolkata', 'West Bengal'),
        ('SDAH', 'Sealdah', 'Kolkata', 'West Bengal'),
        ('KGP', 'Kharagpur Junction', 'Kharagpur', 'West Bengal'),
        ('ASN', 'Asansol Junction', 'Asansol', 'West Bengal'),
        ('BWN', 'Barddhaman Junction', 'Bardhaman', 'West Bengal'),
        ('PNBE', 'Patna Junction', 'Patna', 'Bihar'),
        ('DNR', 'Danapur', 'Patna', 'Bihar'),
        ('KIUL', 'Kiul Junction', 'Kiul', 'Bihar'),
        ('JAJ', 'Jhajha', 'Jhajha', 'Bihar'),
        ('DHN', 'Dhanbad Junction', 'Dhanbad', 'Jharkhand'),
        ('RNC', 'Ranchi', 'Ranchi', 'Jharkhand'),
        ('TATA', 'Tatanagar Junction', 'Jamshedpur', 'Jharkhand'),
        ('BBS', 'Bhubaneswar', 'Bhubaneswar', 'Odisha'),
        ('CTC', 'Cuttack', 'Cuttack', 'Odisha'),
        ('PURI', 'Puri', 'Puri', 'Odisha'),
        
        # Central India  
        ('R', 'Raipur Junction', 'Raipur', 'Chhattisgarh'),
        ('BIA', 'Bilaspur Junction', 'Bilaspur', 'Chhattisgarh'),
        ('JSG', 'Jharsuguda Junction', 'Jharsuguda', 'Odisha'),
        ('ROU', 'Rourkela', 'Rourkela', 'Odisha'),
        ('G', 'Gondia Junction', 'Gondia', 'Maharashtra'),
        
        # Northeast India
        ('GHY', 'Guwahati', 'Guwahati', 'Assam'),
        ('KYQ', 'Kamakhya', 'Guwahati', 'Assam'),
        ('DLG', 'Dimapur', 'Dimapur', 'Nagaland'),
        ('FKG', 'Furkating Junction', 'Furkating', 'Assam'),
        ('NTSK', 'New Tinsukia', 'Tinsukia', 'Assam'),
        
        # Additional important stations
        ('UBL', 'Hubli Junction', 'Hubli', 'Karnataka'),
        ('BGM', 'Belagavi', 'Belagavi', 'Karnataka'),
        ('ED', 'Erode Junction', 'Erode', 'Tamil Nadu'),
        ('SA', 'Salem Junction', 'Salem', 'Tamil Nadu'),
        ('KPD', 'Katpadi Junction', 'Vellore', 'Tamil Nadu'),
        ('JTJ', 'Jolarpettai Junction', 'Jolarpettai', 'Tamil Nadu'),
        ('TEN', 'Tirunelveli Junction', 'Tirunelveli', 'Tamil Nadu'),
        ('CAPE', 'Kanyakumari', 'Kanyakumari', 'Tamil Nadu'),
        ('PGT', 'Palakkad Town', 'Palakkad', 'Kerala'),
        ('SRR', 'Shoranur Junction', 'Shoranur', 'Kerala'),
        ('MAQ', 'Mangalore Junction', 'Mangalore', 'Karnataka'),
        ('MAJN', 'Mangalore Central', 'Mangalore', 'Karnataka'),
        ('RU', 'Renigunta Junction', 'Tirupati', 'Andhra Pradesh'),
        ('GDR', 'Gudur Junction', 'Gudur', 'Andhra Pradesh'),
        ('NLR', 'Nellore', 'Nellore', 'Andhra Pradesh'),
        ('OGL', 'Ongole', 'Ongole', 'Andhra Pradesh'),
        ('TEL', 'Tenali Junction', 'Tenali', 'Andhra Pradesh'),
        ('WL', 'Warangal', 'Warangal', 'Telangana'),
        ('KZJ', 'Kazipet Junction', 'Warangal', 'Telangana'),
        ('BWT', 'Bangarapet', 'Bangarapet', 'Karnataka'),
        ('KJG', 'Karajgi', 'Karajgi', 'Karnataka'),
        ('DVG', 'Davangere', 'Davangere', 'Karnataka'),
        ('ASK', 'Arsikere Junction', 'Arsikere', 'Karnataka'),
        ('RRB', 'Birur Junction', 'Birur', 'Karnataka'),
        ('TK', 'Tumkur', 'Tumkur', 'Karnataka'),
        ('YPR', 'Yesvantpur Junction', 'Bangalore', 'Karnataka'),
        ('KJM', 'Krishnarajapuram', 'Bangalore', 'Karnataka'),
        ('BNC', 'Bangalore Cantonment', 'Bangalore', 'Karnataka'),
        ('BAND', 'Banaswadi', 'Bangalore', 'Karnataka'),
    ]
    
    stations = []
    for code, name, city, state in stations_data:
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
    logger.info(f"✅ Created {len(stations)} major railway stations across India")

def create_trains(db):
    """Create 200 trains with realistic configurations"""
    logger.info("Creating 200 trains with realistic configurations...")
    
    from src.models import Train
    
    # Train types with realistic parameters (seats, fare_per_km, tatkal_seats, tatkal_fare)
    train_types = [
        ('Rajdhani Express', 400, 3.5, 40, 5.0),
        ('Shatabdi Express', 350, 3.0, 35, 4.5),
        ('Vande Bharat Express', 500, 4.0, 50, 6.0),
        ('Duronto Express', 450, 2.8, 45, 4.0),
        ('Superfast Express', 400, 2.0, 40, 3.0),
        ('Mail/Express', 380, 1.5, 38, 2.5),
        ('Intercity Express', 300, 1.8, 30, 2.8),
        ('Jan Shatabdi Express', 320, 2.2, 32, 3.2),
        ('Garib Rath', 350, 1.2, 35, 2.0),
        ('Humsafar Express', 380, 2.5, 38, 3.8),
        ('Tejas Express', 400, 3.2, 40, 4.8),
        ('AC Express', 350, 2.5, 35, 3.5),
        ('Passenger Express', 250, 0.8, 25, 1.2),
        ('MEMU', 200, 0.6, 20, 1.0),
    ]
    
    # Famous Indian train names
    train_names = [
        'Tamil Nadu Express', 'Kerala Express', 'Karnataka Express', 'Andhra Pradesh Express',
        'Chennai Express', 'Mumbai Express', 'Bangalore Express', 'Mysore Express',
        'Coromandel Express', 'Island Express', 'Konkan Kanya Express', 'Mangalore Express',
        'Brindavan Express', 'Lalbagh Express', 'Chamundi Express', 'Tippu Express',
        'Udyan Express', 'Janmabhoomi Express', 'Godavari Express', 'Krishna Express',
        'Rayalaseema Express', 'Hamsa Express', 'Kaveri Express', 'Ganga Kaveri Express',
        'Trivandrum Express', 'Kanyakumari Express', 'Grand Trunk Express', 'Deccan Queen',
        'Golden Temple Mail', 'Punjab Mail', 'Howrah Express', 'Kalka Mail',
        'Himalayan Queen', 'Nilgiri Express', 'Western Express', 'Central Express',
        'Gomti Express', 'Saryu Yamuna Express', 'Mahananda Express', 'Kanchanjunga Express',
        'Assam Express', 'Brahmaputra Mail', 'Northeast Express', 'Capital Express',
        'Rajdhani Express', 'Shatabdi Express', 'Duronto Express', 'Sampark Kranti Express',
        'Humsafar Express', 'Antyodaya Express', 'Tejas Express', 'Vande Bharat Express'
    ]
    
    trains = []
    train_number = 12001
    
    for i in range(200):
        # Select train type and configuration
        train_type, base_seats, base_fare, base_tatkal_seats, base_tatkal_fare = random.choice(train_types)
        
        # Select train name
        if i < len(train_names):
            train_name = train_names[i]
        else:
            # Generate additional names
            prefixes = ['Express', 'Superfast', 'Intercity', 'Jan', 'Special', 'Premium']
            regions = ['South', 'North', 'East', 'West', 'Central']
            train_name = f"{random.choice(regions)} {random.choice(prefixes)} {i-len(train_names)+1}"
        
        # Add variation to base parameters
        total_seats = base_seats + random.randint(-50, 80)
        fare_per_km = base_fare + random.uniform(-0.3, 0.5)
        tatkal_seats = base_tatkal_seats + random.randint(-5, 10)
        tatkal_fare_per_km = base_tatkal_fare + random.uniform(-0.5, 1.0)
        
        # Ensure reasonable bounds
        total_seats = max(150, min(550, total_seats))
        fare_per_km = max(0.5, min(4.5, fare_per_km))
        tatkal_seats = max(10, min(total_seats // 8, tatkal_seats))
        tatkal_fare_per_km = max(1.0, min(6.0, tatkal_fare_per_km))
        
        train = Train(
            number=str(train_number),
            name=train_name,
            total_seats=total_seats,
            available_seats=random.randint(total_seats - 80, total_seats),
            fare_per_km=fare_per_km,
            tatkal_seats=tatkal_seats,
            tatkal_fare_per_km=tatkal_fare_per_km,
            active=True
        )
        trains.append(train)
        train_number += 1
    
    db.session.add_all(trains)
    db.session.commit()
    logger.info(f"✅ Created {len(trains)} trains with realistic configurations")

def create_routes(db):
    """Create train routes connecting stations"""
    logger.info("Creating train routes...")
    
    from src.models import Train, Station, TrainRoute
    
    trains = Train.query.all()
    stations = Station.query.all()
    
    # Group stations by region for logical routing
    regions = {
        'South': [s for s in stations if s.state in ['Tamil Nadu', 'Karnataka', 'Kerala', 'Andhra Pradesh', 'Telangana']],
        'North': [s for s in stations if s.state in ['Delhi', 'Uttar Pradesh', 'Punjab', 'Haryana', 'Rajasthan', 'Jammu & Kashmir', 'Chandigarh']],
        'West': [s for s in stations if s.state in ['Maharashtra', 'Gujarat', 'Madhya Pradesh']],
        'East': [s for s in stations if s.state in ['West Bengal', 'Bihar', 'Jharkhand', 'Odisha']],
        'Central': [s for s in stations if s.state in ['Chhattisgarh']],
        'Northeast': [s for s in stations if s.state in ['Assam', 'Nagaland']]
    }
    
    routes = []
    
    for train in trains:
        try:
            # Determine route characteristics based on train type
            if 'Rajdhani' in train.name or 'Duronto' in train.name:
                route_length = random.randint(6, 12)  # Long distance
            elif 'Express' in train.name:
                route_length = random.randint(4, 8)   # Medium distance
            else:
                route_length = random.randint(3, 5)   # Short distance
            
            # Select starting and ending regions
            start_region = random.choice(list(regions.keys()))
            possible_end_regions = [r for r in regions.keys() if r != start_region and regions[r]]
            
            if not possible_end_regions or not regions[start_region]:
                continue
                
            end_region = random.choice(possible_end_regions)
            
            # Build route
            route_stations = []
            
            # Start station
            start_station = random.choice(regions[start_region])
            route_stations.append(start_station)
            
            # Intermediate stations (mix of regions)
            current_region = start_region
            for i in range(route_length - 2):
                if random.random() < 0.6 and len(regions[current_region]) > 1:
                    # Stay in same region
                    available = [s for s in regions[current_region] if s not in route_stations]
                    if available:
                        route_stations.append(random.choice(available))
                else:
                    # Move towards destination region
                    intermediate_regions = [r for r in regions.keys() if r not in [start_region, end_region] and regions[r]]
                    if intermediate_regions:
                        current_region = random.choice(intermediate_regions)
                        available = [s for s in regions[current_region] if s not in route_stations]
                        if available:
                            route_stations.append(random.choice(available))
            
            # End station
            end_candidates = [s for s in regions[end_region] if s not in route_stations]
            if end_candidates:
                route_stations.append(random.choice(end_candidates))
            
            # Create route entries with realistic timings
            if len(route_stations) < 2:
                continue
                
            total_distance = 0
            current_time = time(random.randint(6, 22), random.randint(0, 59))  # Realistic start times
            
            for sequence, station in enumerate(route_stations):
                if sequence == 0:
                    # First station - departure only
                    route = TrainRoute(
                        train_id=train.id,
                        station_id=station.id,
                        sequence=sequence + 1,
                        departure_time=current_time,
                        distance_from_start=0
                    )
                elif sequence == len(route_stations) - 1:
                    # Last station - arrival only
                    segment_distance = random.randint(100, 350)
                    total_distance += segment_distance
                    travel_hours = segment_distance / random.randint(45, 75)  # 45-75 km/h average
                    current_time = add_hours_to_time(current_time, travel_hours)
                    
                    route = TrainRoute(
                        train_id=train.id,
                        station_id=station.id,
                        sequence=sequence + 1,
                        arrival_time=current_time,
                        distance_from_start=total_distance
                    )
                else:
                    # Intermediate station - arrival and departure
                    segment_distance = random.randint(100, 350)
                    total_distance += segment_distance
                    travel_hours = segment_distance / random.randint(45, 75)
                    current_time = add_hours_to_time(current_time, travel_hours)
                    
                    # Stop duration: 2-10 minutes for most stations
                    stop_minutes = random.randint(2, 10)
                    departure_time = add_minutes_to_time(current_time, stop_minutes)
                    
                    route = TrainRoute(
                        train_id=train.id,
                        station_id=station.id,
                        sequence=sequence + 1,
                        arrival_time=current_time,
                        departure_time=departure_time,
                        distance_from_start=total_distance
                    )
                    current_time = departure_time
                
                routes.append(route)
                
        except Exception as e:
            logger.warning(f"Skipping route for train {train.name}: {e}")
            continue
    
    # Add routes in batches
    if routes:
        batch_size = 100
        for i in range(0, len(routes), batch_size):
            batch = routes[i:i + batch_size]
            db.session.add_all(batch)
            db.session.commit()
    
    logger.info(f"✅ Created routes for trains connecting stations logically")

def create_system_config(db):
    """Create essential system configurations"""
    logger.info("Creating system configurations...")
    
    from src.models import TatkalTimeSlot
    
    # Create Tatkal booking time slots
    tatkal_slots = [
        TatkalTimeSlot(
            name="AC Classes Tatkal",
            open_time=time(10, 0),   # 10:00 AM
            close_time=time(11, 0),  # 11:00 AM
            coach_classes="AC1,AC2,AC3,CC",
            days_before_journey=1,
            active=True
        ),
        TatkalTimeSlot(
            name="Non-AC Classes Tatkal", 
            open_time=time(11, 0),   # 11:00 AM
            close_time=time(12, 0),  # 12:00 PM
            coach_classes="SL,2S",
            days_before_journey=1,
            active=True
        )
    ]
    
    db.session.add_all(tatkal_slots)
    db.session.commit()
    
    logger.info("✅ Created essential system configurations")

def add_hours_to_time(time_obj, hours):
    """Add hours to a time object, handling day overflow"""
    dt = datetime.combine(date.today(), time_obj)
    dt += timedelta(hours=hours)
    return dt.time()

def add_minutes_to_time(time_obj, minutes):
    """Add minutes to a time object, handling day overflow"""
    dt = datetime.combine(date.today(), time_obj)
    dt += timedelta(minutes=minutes)
    return dt.time()

if __name__ == '__main__':
    setup_database()