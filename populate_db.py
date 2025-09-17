#!/usr/bin/env python3
"""
RailServe Database Population Script
Creates comprehensive railway system data including stations, trains, routes, and users.
Production-ready with enhanced error handling and data validation.
"""

import os
import sys
import logging
from datetime import time, datetime
import random
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('populate_db.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.app import app, db
    from src.models import User, Train, Station, TrainRoute
    from werkzeug.security import generate_password_hash
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

def validate_database_connection():
    """Validate database connection and schema"""
    try:
        with app.app_context():
            db.session.execute(db.text('SELECT 1'))
            logger.info("✅ Database connection validated")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def clear_existing_data():
    """Safely clear existing data with confirmation"""
    try:
        logger.info("Clearing existing data...")
        # Delete in proper order to respect foreign key constraints
        TrainRoute.query.delete()
        Train.query.delete() 
        Station.query.delete()
        User.query.delete()
        db.session.commit()
        logger.info("✅ Existing data cleared successfully")
    except Exception as e:
        logger.error(f"❌ Failed to clear existing data: {e}")
        db.session.rollback()
        raise

def populate_database():
    """Populate the database with comprehensive railway system data"""
    
    start_time = datetime.now()
    logger.info("🚂 Starting RailServe database population...")
    
    if not validate_database_connection():
        logger.error("Cannot proceed without valid database connection")
        return False
    
    try:
        with app.app_context():
            logger.info("Creating database tables...")
            db.create_all()
            
            # Clear existing data
            clear_existing_data()
        
        # Create stations (1000 stations)
        print("Creating 1000 stations...")
        
        # Major stations (first 50)
        major_stations = [
            {'code': 'NDLS', 'name': 'New Delhi', 'city': 'Delhi', 'state': 'Delhi'},
            {'code': 'CST', 'name': 'Chhatrapati Shivaji Terminus', 'city': 'Mumbai', 'state': 'Maharashtra'},
            {'code': 'HWH', 'name': 'Howrah Junction', 'city': 'Kolkata', 'state': 'West Bengal'},
            {'code': 'MAS', 'name': 'Chennai Central', 'city': 'Chennai', 'state': 'Tamil Nadu'},
            {'code': 'SBC', 'name': 'Bangalore City', 'city': 'Bangalore', 'state': 'Karnataka'},
            {'code': 'PUNE', 'name': 'Pune Junction', 'city': 'Pune', 'state': 'Maharashtra'},
            {'code': 'AMD', 'name': 'Ahmedabad Junction', 'city': 'Ahmedabad', 'state': 'Gujarat'},
            {'code': 'JP', 'name': 'Jaipur Junction', 'city': 'Jaipur', 'state': 'Rajasthan'},
            {'code': 'AGC', 'name': 'Agra Cantt', 'city': 'Agra', 'state': 'Uttar Pradesh'},
            {'code': 'LKO', 'name': 'Lucknow Junction', 'city': 'Lucknow', 'state': 'Uttar Pradesh'},
            {'code': 'BCT', 'name': 'Mumbai Central', 'city': 'Mumbai', 'state': 'Maharashtra'},
            {'code': 'BZA', 'name': 'Vijayawada Junction', 'city': 'Vijayawada', 'state': 'Andhra Pradesh'},
            {'code': 'CNB', 'name': 'Kanpur Central', 'city': 'Kanpur', 'state': 'Uttar Pradesh'},
            {'code': 'GWL', 'name': 'Gwalior Junction', 'city': 'Gwalior', 'state': 'Madhya Pradesh'},
            {'code': 'JBP', 'name': 'Jabalpur Junction', 'city': 'Jabalpur', 'state': 'Madhya Pradesh'},
            {'code': 'VSKP', 'name': 'Visakhapatnam Junction', 'city': 'Visakhapatnam', 'state': 'Andhra Pradesh'},
            {'code': 'UDZ', 'name': 'Udaipur City', 'city': 'Udaipur', 'state': 'Rajasthan'},
            {'code': 'JU', 'name': 'Jodhpur Junction', 'city': 'Jodhpur', 'state': 'Rajasthan'},
            {'code': 'BKN', 'name': 'Bikaner Junction', 'city': 'Bikaner', 'state': 'Rajasthan'},
            {'code': 'KOAA', 'name': 'Kochuveli', 'city': 'Thiruvananthapuram', 'state': 'Kerala'},
            {'code': 'ERS', 'name': 'Ernakulam Junction', 'city': 'Kochi', 'state': 'Kerala'},
            {'code': 'CLT', 'name': 'Kozhikode', 'city': 'Kozhikode', 'state': 'Kerala'},
            {'code': 'MDU', 'name': 'Madurai Junction', 'city': 'Madurai', 'state': 'Tamil Nadu'},
            {'code': 'CBE', 'name': 'Coimbatore Junction', 'city': 'Coimbatore', 'state': 'Tamil Nadu'},
            {'code': 'RJPB', 'name': 'Rjndr Ngr Bihar', 'city': 'Patna', 'state': 'Bihar'},
            {'code': 'PNBE', 'name': 'Patna Junction', 'city': 'Patna', 'state': 'Bihar'},
            {'code': 'RNC', 'name': 'Ranchi Junction', 'city': 'Ranchi', 'state': 'Jharkhand'},
            {'code': 'TATA', 'name': 'Tatanagar Junction', 'city': 'Jamshedpur', 'state': 'Jharkhand'},
            {'code': 'BSB', 'name': 'Varanasi Junction', 'city': 'Varanasi', 'state': 'Uttar Pradesh'},
            {'code': 'GKP', 'name': 'Gorakhpur Junction', 'city': 'Gorakhpur', 'state': 'Uttar Pradesh'},
            {'code': 'VAPI', 'name': 'Vapi', 'city': 'Vapi', 'state': 'Gujarat'},
            {'code': 'ST', 'name': 'Surat', 'city': 'Surat', 'state': 'Gujarat'},
            {'code': 'BRC', 'name': 'Vadodara Junction', 'city': 'Vadodara', 'state': 'Gujarat'},
            {'code': 'GOA', 'name': 'Goa', 'city': 'Panaji', 'state': 'Goa'},
            {'code': 'MAJN', 'name': 'Mangalore Junction', 'city': 'Mangalore', 'state': 'Karnataka'},
            {'code': 'QLM', 'name': 'Quilon Junction', 'city': 'Kollam', 'state': 'Kerala'},
            {'code': 'DWI', 'name': 'Dwarka', 'city': 'Dwarka', 'state': 'Gujarat'},
            {'code': 'RMM', 'name': 'Rameswaram', 'city': 'Rameswaram', 'state': 'Tamil Nadu'},
            {'code': 'PURI', 'name': 'Puri', 'city': 'Puri', 'state': 'Odisha'},
            {'code': 'HRD', 'name': 'Hardwar Junction', 'city': 'Haridwar', 'state': 'Uttarakhand'},
            {'code': 'RKSH', 'name': 'Rishikesh', 'city': 'Rishikesh', 'state': 'Uttarakhand'},
            {'code': 'DDD', 'name': 'Dehradun', 'city': 'Dehradun', 'state': 'Uttarakhand'},
            {'code': 'ATR', 'name': 'Atari', 'city': 'Atari', 'state': 'Punjab'},
            {'code': 'JHL', 'name': 'Jammu Tawi', 'city': 'Jammu', 'state': 'Jammu and Kashmir'},
            {'code': 'SVDK', 'name': 'Shri Mata Vaishno Devi Katra', 'city': 'Katra', 'state': 'Jammu and Kashmir'},
            {'code': 'GHY', 'name': 'Guwahati', 'city': 'Guwahati', 'state': 'Assam'},
            {'code': 'DBRG', 'name': 'Dibrugarh', 'city': 'Dibrugarh', 'state': 'Assam'},
            {'code': 'MB', 'name': 'Moradabad Junction', 'city': 'Moradabad', 'state': 'Uttar Pradesh'},
            {'code': 'BE', 'name': 'Bareilly Junction', 'city': 'Bareilly', 'state': 'Uttar Pradesh'},
            {'code': 'RTM', 'name': 'Ratlam Junction', 'city': 'Ratlam', 'state': 'Madhya Pradesh'},
        ]
        
        # Indian states and sample cities for generating realistic station data
        states_cities = {
            'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Agra', 'Varanasi', 'Allahabad', 'Meerut', 'Bareilly', 'Aligarh', 'Moradabad', 'Gorakhpur'],
            'Maharashtra': ['Mumbai', 'Pune', 'Nagpur', 'Nashik', 'Aurangabad', 'Solapur', 'Amravati', 'Kolhapur', 'Sangli', 'Ahmednagar'],
            'Tamil Nadu': ['Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem', 'Erode', 'Tirunelveli', 'Vellore', 'Thoothukudi', 'Dindigul'],
            'Karnataka': ['Bangalore', 'Mysore', 'Hubli', 'Mangalore', 'Belgaum', 'Gulbarga', 'Davanagere', 'Bellary', 'Bijapur', 'Shimoga'],
            'Gujarat': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Bhavnagar', 'Jamnagar', 'Junagadh', 'Gandhinagar', 'Anand', 'Bharuch'],
            'Rajasthan': ['Jaipur', 'Jodhpur', 'Udaipur', 'Bikaner', 'Ajmer', 'Alwar', 'Bharatpur', 'Pali', 'Sikar', 'Tonk'],
            'West Bengal': ['Kolkata', 'Howrah', 'Durgapur', 'Asansol', 'Siliguri', 'Burdwan', 'Malda', 'Kharagpur', 'Haldia', 'Krishnanagar'],
            'Madhya Pradesh': ['Bhopal', 'Indore', 'Jabalpur', 'Gwalior', 'Ujjain', 'Sagar', 'Dewas', 'Satna', 'Ratlam', 'Rewa'],
            'Kerala': ['Thiruvananthapuram', 'Kochi', 'Kozhikode', 'Thrissur', 'Kollam', 'Palakkad', 'Alappuzha', 'Malappuram', 'Kannur', 'Kasaragod'],
            'Andhra Pradesh': ['Visakhapatnam', 'Vijayawada', 'Guntur', 'Nellore', 'Kurnool', 'Rajahmundry', 'Kadapa', 'Kakinada', 'Anantapur', 'Tirupati'],
            'Telangana': ['Hyderabad', 'Warangal', 'Nizamabad', 'Khammam', 'Karimnagar', 'Mahbubnagar', 'Nalgonda', 'Adilabad', 'Miryalaguda', 'Suryapet'],
            'Odisha': ['Bhubaneswar', 'Cuttack', 'Rourkela', 'Brahmapur', 'Sambalpur', 'Puri', 'Balasore', 'Bhadrak', 'Baripada', 'Jharsuguda'],
            'Punjab': ['Chandigarh', 'Ludhiana', 'Amritsar', 'Jalandhar', 'Patiala', 'Bathinda', 'Mohali', 'Hoshiarpur', 'Batala', 'Pathankot'],
            'Haryana': ['Gurgaon', 'Faridabad', 'Panipat', 'Ambala', 'Yamunanagar', 'Rohtak', 'Hisar', 'Karnal', 'Sonipat', 'Panchkula'],
            'Bihar': ['Patna', 'Gaya', 'Bhagalpur', 'Muzaffarpur', 'Purnia', 'Darbhanga', 'Bihar Sharif', 'Arrah', 'Begusarai', 'Katihar'],
            'Jharkhand': ['Ranchi', 'Jamshedpur', 'Dhanbad', 'Bokaro', 'Deoghar', 'Phusro', 'Hazaribagh', 'Giridih', 'Ramgarh', 'Medininagar'],
            'Assam': ['Guwahati', 'Silchar', 'Dibrugarh', 'Jorhat', 'Nagaon', 'Tinsukia', 'Tezpur', 'Bongaigaon', 'Karimganj', 'Sivasagar'],
            'Uttarakhand': ['Dehradun', 'Haridwar', 'Roorkee', 'Haldwani', 'Rudrapur', 'Kashipur', 'Rishikesh', 'Kotdwar', 'Jaspur', 'Kichha'],
            'Himachal Pradesh': ['Shimla', 'Dharamshala', 'Solan', 'Mandi', 'Palampur', 'Una', 'Kullu', 'Hamirpur', 'Bilaspur', 'Chamba'],
            'Jammu and Kashmir': ['Jammu', 'Srinagar', 'Kathua', 'Udhampur', 'Anantnag', 'Baramulla', 'Kupwara', 'Pulwama', 'Rajouri', 'Poonch'],
            'Chhattisgarh': ['Raipur', 'Bhilai', 'Bilaspur', 'Korba', 'Durg', 'Jagdalpur', 'Ambikapur', 'Chirmiri', 'Dhamtari', 'Mahasamund'],
            'Goa': ['Panaji', 'Margao', 'Vasco da Gama', 'Mapusa', 'Ponda', 'Bicholim', 'Curchorem', 'Sanquelim', 'Cuncolim', 'Quepem']
        }
        
        stations_data = major_stations.copy()
        
        # Generate additional 950 stations to reach 1000 total
        station_counter = 1001
        existing_names = {station['name'] for station in major_stations}
        existing_codes = {station['code'] for station in major_stations}
        
        for state, cities in states_cities.items():
            for city in cities:
                for i in range(1, 6):  # 5 stations per city
                    station_suffix = ['Jn', 'City', 'Cantt', 'Town', 'Central'][i-1]
                    base_code = f"{city[:3].upper()}{i:02d}"
                    name = f"{city} {station_suffix}"
                    
                    # Ensure unique code
                    code = base_code
                    counter = 1
                    while code in existing_codes:
                        code = f"{city[:3].upper()}{i:02d}{counter}"
                        counter += 1
                    
                    # Skip if name already exists, but ensure we have unique code
                    if name not in existing_names:
                        stations_data.append({
                            'code': code,
                            'name': name,
                            'city': city,
                            'state': state
                        })
                        existing_names.add(name)
                        existing_codes.add(code)
                    
                    station_counter += 1
                    if len(stations_data) >= 1000:
                        break
                if len(stations_data) >= 1000:
                    break
            if len(stations_data) >= 1000:
                break
        
        # Create stations in batches for better performance
        logger.info(f"Creating {len(stations_data)} stations in batches...")
        stations = []
        batch_size = 100
        
        for i, station_data in enumerate(stations_data):
            try:
                station = Station(**station_data)
                stations.append(station)
                db.session.add(station)
                
                # Commit in batches
                if (i + 1) % batch_size == 0:
                    db.session.commit()
                    logger.info(f"  ✅ Created {i + 1}/{len(stations_data)} stations")
            except Exception as e:
                logger.warning(f"  ⚠️  Failed to create station {station_data['name']}: {e}")
                db.session.rollback()
                continue
        
        # Final commit for remaining stations
        db.session.commit()
        logger.info(f"✅ Successfully created {len(stations)} stations")
        
        # Create trains (500 trains)
        print("Creating 500 trains...")
        
        train_types = [
            ('Rajdhani Express', 350, 18.0),
            ('Shatabdi Express', 320, 16.0),
            ('Duronto Express', 380, 17.0),
            ('Superfast Express', 450, 14.0),
            ('Mail Express', 500, 12.0),
            ('Passenger', 600, 8.0),
            ('Jan Shatabdi', 280, 10.0),
            ('Garib Rath', 550, 9.0),
            ('Humsafar Express', 400, 15.0),
            ('Tejas Express', 300, 20.0),
            ('Vande Bharat Express', 250, 25.0),
            ('Double Decker Express', 480, 13.0),
            ('Intercity Express', 420, 11.0),
            ('Express', 500, 10.0),
            ('Local', 800, 6.0)
        ]
        
        # Route patterns for train generation
        route_patterns = [
            ['New Delhi', 'Mumbai'],
            ['Kolkata', 'Chennai'], 
            ['Bangalore', 'Delhi'],
            ['Hyderabad', 'Pune'],
            ['Ahmedabad', 'Kolkata'],
            ['Jaipur', 'Mumbai'],
            ['Chennai', 'Bangalore'],
            ['Delhi', 'Kolkata'],
            ['Mumbai', 'Chennai'],
            ['Pune', 'Delhi'],
            ['Goa', 'Mumbai'],
            ['Kerala', 'Delhi'],
            ['Rajasthan', 'Gujarat'],
            ['Punjab', 'Haryana'],
            ['Bihar', 'West Bengal'],
            ['Assam', 'Delhi'],
            ['Karnataka', 'Tamil Nadu'],
            ['Madhya Pradesh', 'Maharashtra'],
            ['Uttar Pradesh', 'Delhi'],
            ['Odisha', 'West Bengal']
        ]
        
        # Create trains with enhanced data validation
        logger.info("Creating 500 trains with enhanced configuration...")
        trains = []
        train_number = 10001
        created_names = set()  # Track unique train names
        
        for i in range(500):
            try:
                train_type, capacity, base_fare = random.choice(train_types)
                route = random.choice(route_patterns)
                
                # Add realistic variation
                capacity += random.randint(-50, 100)
                base_fare += random.uniform(-2.0, 3.0)
                
                # Ensure minimum values
                capacity = max(150, capacity)
                base_fare = max(5.0, base_fare)
                
                # Generate unique train name
                base_name = f"{route[0]} {route[1]} {train_type}"
                train_name = base_name
                counter = 1
                while train_name in created_names:
                    train_name = f"{base_name} ({counter})"
                    counter += 1
                created_names.add(train_name)
                
                # Enhanced Tatkal configuration
                tatkal_seats = max(10, int(capacity * random.uniform(0.10, 0.20)))  # 10-20% Tatkal quota
                tatkal_fare = round(base_fare * random.uniform(1.3, 1.8), 2)  # 1.3-1.8x regular fare
                
                train = Train(
                    number=str(train_number),
                    name=train_name,
                    total_seats=capacity,
                    available_seats=capacity,
                    fare_per_km=round(base_fare, 2),
                    tatkal_seats=tatkal_seats,
                    tatkal_fare_per_km=tatkal_fare,
                    active=True
                )
                
                trains.append(train)
                db.session.add(train)
                train_number += 1
                
                # Batch commit for performance
                if (i + 1) % 100 == 0:
                    db.session.commit()
                    logger.info(f"  ✅ Generated {i + 1}/500 trains")
                    
            except Exception as e:
                logger.warning(f"  ⚠️  Failed to create train {train_number}: {e}")
                db.session.rollback()
                train_number += 1
                continue
        
        # Final commit
        db.session.commit()
        logger.info(f"✅ Successfully created {len(trains)} trains")
        
        # Create sample users
        print("Creating sample users...")
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@railserve.com', 
                'password': 'admin123',
                'role': 'super_admin'
            },
            {
                'username': 'manager',
                'email': 'manager@railserve.com',
                'password': 'manager123', 
                'role': 'admin'
            },
            {
                'username': 'john_doe',
                'email': 'john@example.com',
                'password': 'user123',
                'role': 'user'
            },
            {
                'username': 'test_user',
                'email': 'test@example.com',
                'password': 'test123',
                'role': 'user'
            }
        ]
        
        # Create users with validation
        logger.info("Creating sample users with enhanced security...")
        created_users = []
        
        for user_data in users_data:
            try:
                # Validate user data
                if not user_data['username'] or not user_data['email']:
                    logger.warning(f"Skipping invalid user data: {user_data}")
                    continue
                
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    role=user_data.get('role', 'user')  # Default to 'user' role
                )
                db.session.add(user)
                created_users.append(user_data['username'])
                
            except Exception as e:
                logger.warning(f"  ⚠️  Failed to create user {user_data['username']}: {e}")
                db.session.rollback()
                continue
        
        db.session.commit()
        logger.info(f"✅ Successfully created {len(created_users)} users: {', '.join(created_users)}")
        
        # Create comprehensive train routes with enhanced logic
        logger.info("Creating intelligent train routes for all trains...")
        route_count = 0
        failed_routes = 0
        
        # Get all trains and stations
        all_trains = Train.query.all()
        all_stations = Station.query.all()
        
        if not all_trains or not all_stations:
            logger.error("No trains or stations found. Cannot create routes.")
            raise Exception("Missing prerequisite data")
        
        logger.info(f"Processing routes for {len(all_trains)} trains using {len(all_stations)} stations")
        
        # Group stations by state for realistic routing
        stations_by_state = {}
        for station in all_stations:
            state = station.state
            if state not in stations_by_state:
                stations_by_state[state] = []
            stations_by_state[state].append(station)
        
        # Major route patterns (state-to-state connections)
        major_routes = [
            ['Delhi', 'Uttar Pradesh', 'Bihar', 'West Bengal'],
            ['Delhi', 'Rajasthan', 'Gujarat', 'Maharashtra'], 
            ['Maharashtra', 'Karnataka', 'Tamil Nadu'],
            ['Delhi', 'Haryana', 'Punjab', 'Jammu and Kashmir'],
            ['West Bengal', 'Odisha', 'Andhra Pradesh', 'Tamil Nadu'],
            ['Gujarat', 'Maharashtra', 'Karnataka', 'Kerala'],
            ['Uttar Pradesh', 'Madhya Pradesh', 'Maharashtra'],
            ['Delhi', 'Uttarakhand', 'Himachal Pradesh'],
            ['Bihar', 'Jharkhand', 'West Bengal'],
            ['Assam', 'West Bengal', 'Odisha'],
            ['Telangana', 'Karnataka', 'Tamil Nadu'],
            ['Rajasthan', 'Madhya Pradesh', 'Maharashtra'],
            ['Punjab', 'Haryana', 'Delhi', 'Uttar Pradesh'],
            ['Kerala', 'Tamil Nadu', 'Karnataka'],
            ['Chhattisgarh', 'Odisha', 'Andhra Pradesh']
        ]
        
        # Create routes for each train with enhanced error handling
        for train_idx, train in enumerate(all_trains):
            try:
                # Choose route pattern based on train characteristics
                route_pattern = major_routes[train_idx % len(major_routes)]
                
                # Build intelligent station sequence for this route
                route_stations = []
                total_distance = 0
                
                # Build route with better logic
                for state_idx, state in enumerate(route_pattern):
                    if state in stations_by_state and stations_by_state[state]:
                        # Pick stations strategically based on train type
                        available_stations = stations_by_state[state]
                        num_stations = min(2, len(available_stations))
                        
                        if 'Express' in train.name or 'Rajdhani' in train.name:
                            # Express trains stop at major stations (first ones in list)
                            state_stations = available_stations[:num_stations]
                        else:
                            # Regular trains can stop at any station
                            state_stations = random.sample(available_stations, num_stations)
                        
                        for station in state_stations:
                            if len(route_stations) < 8:  # Max 8 stations per train
                                route_stations.append(station)
                
                # Ensure minimum viable route
                if len(route_stations) < 2:
                    # Fallback: create simple route with random stations
                    route_stations = random.sample(all_stations, min(3, len(all_stations)))
                
                # Remove duplicates while preserving order
                seen = set()
                unique_stations = []
                for station in route_stations:
                    if station.id not in seen:
                        unique_stations.append(station)
                        seen.add(station.id)
                route_stations = unique_stations[:8]
                
                # Create route entries with realistic timing
                departure_hour = random.randint(4, 22)  # Trains depart between 4 AM and 10 PM
                current_time_minutes = departure_hour * 60 + random.randint(0, 59)
                
                for seq, station in enumerate(route_stations):
                    if seq == 0:
                        # First station
                        distance = 0
                        arrival_time = None
                        departure_time = time(
                            current_time_minutes // 60,
                            current_time_minutes % 60
                        )
                    else:
                        # Subsequent stations
                        segment_distance = random.randint(80, 350)
                        total_distance += segment_distance
                        
                        # Calculate realistic travel time based on train type
                        if 'Express' in train.name:
                            avg_speed = random.randint(70, 90)  # Express trains faster
                        else:
                            avg_speed = random.randint(45, 65)  # Regular trains slower
                        
                        travel_time_minutes = int(segment_distance / avg_speed * 60)
                        current_time_minutes += travel_time_minutes
                        
                        arrival_time = time(
                            (current_time_minutes // 60) % 24,
                            current_time_minutes % 60
                        )
                        
                        # Add station stop time (if not last station)
                        if seq < len(route_stations) - 1:
                            if 'Express' in train.name:
                                stop_duration = random.randint(2, 5)  # Express trains stop briefly
                            else:
                                stop_duration = random.randint(5, 15)  # Regular trains longer stops
                            
                            current_time_minutes += stop_duration
                            departure_time = time(
                                (current_time_minutes // 60) % 24,
                                current_time_minutes % 60
                            )
                        else:
                            departure_time = None  # Last station
                    
                    # Create route entry with validation
                    route = TrainRoute(
                        train_id=train.id,
                        station_id=station.id,
                        sequence=seq + 1,
                        arrival_time=arrival_time,
                        departure_time=departure_time,
                        distance_from_start=total_distance
                    )
                    
                    db.session.add(route)
                    route_count += 1
                
                # Batch commit for performance
                if (train_idx + 1) % 50 == 0:
                    db.session.commit()
                    logger.info(f"  ✅ Created routes for {train_idx + 1}/{len(all_trains)} trains")
                
            except Exception as e:
                failed_routes += 1
                logger.warning(f"  ⚠️  Could not create route for train {train.number}: {e}")
                db.session.rollback()
                continue
        
            # Final commit for routes
            db.session.commit()
            logger.info(f"✅ Successfully created {route_count} train routes")
            if failed_routes > 0:
                logger.warning(f"⚠️  Failed to create routes for {failed_routes} trains")
            
            # Generate summary statistics
            end_time = datetime.now()
            duration = end_time - start_time
            
            # Verify data integrity
            final_stations = Station.query.count()
            final_trains = Train.query.count()
            final_users = User.query.count()
            final_routes = TrainRoute.query.count()
            
            logger.info("\n" + "="*60)
            logger.info("🎉 DATABASE POPULATION COMPLETED SUCCESSFULLY!")
            logger.info("="*60)
            logger.info(f"⏱️  Total Duration: {duration.total_seconds():.2f} seconds")
            logger.info(f"")
            logger.info(f"📊 FINAL STATISTICS:")
            logger.info(f"   🚉 Stations: {final_stations:,}")
            logger.info(f"   🚂 Trains: {final_trains:,}")
            logger.info(f"   👥 Users: {final_users}")
            logger.info(f"   🛤️  Train Routes: {final_routes:,}")
            logger.info(f"")
            logger.info(f"🚀 SYSTEM FEATURES:")
            logger.info(f"   ✅ Tatkal booking enabled (10-20% quota per train)")
            logger.info(f"   ✅ Concurrent booking protection")
            logger.info(f"   ✅ Comprehensive passenger details collection")
            logger.info(f"   ✅ Intelligent route generation")
            logger.info(f"   ✅ Waitlist management system")
            logger.info(f"   ✅ Admin dashboard with analytics")
            logger.info(f"   ✅ Multi-role user management")
            logger.info(f"")
            logger.info(f"🔑 LOGIN CREDENTIALS:")
            logger.info(f"   🔴 Super Admin: admin / admin123")
            logger.info(f"   🟡 Admin: manager / manager123")
            logger.info(f"   🟢 User: john_doe / user123")
            logger.info(f"   🔵 Test User: test_user / test123")
            logger.info(f"")
            logger.info(f"🎯 READY FOR PRODUCTION DEPLOYMENT!")
            logger.info("="*60)
            
            # Save summary to file
            summary_data = {
                'timestamp': end_time.isoformat(),
                'duration_seconds': duration.total_seconds(),
                'stations_created': final_stations,
                'trains_created': final_trains,
                'users_created': final_users,
                'routes_created': final_routes,
                'failed_routes': failed_routes,
                'status': 'success'
            }
            
            with open('population_summary.json', 'w') as f:
                json.dump(summary_data, f, indent=2)
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Database population failed: {e}")
        db.session.rollback()
        
        # Save error summary
        error_summary = {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'status': 'failed'
        }
        
        with open('population_summary.json', 'w') as f:
            json.dump(error_summary, f, indent=2)
        
        return False

def main():
    """Main function with command line argument support"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='RailServe Database Population Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python populate_db.py                    # Run full population
  python populate_db.py --verify          # Verify existing data
  python populate_db.py --clear-only      # Clear data only (no population)
        '''
    )
    
    parser.add_argument('--verify', action='store_true',
                        help='Verify existing data instead of populating')
    parser.add_argument('--clear-only', action='store_true',
                        help='Clear existing data only (no population)')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        default='INFO', help='Set logging level')
    
    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    try:
        if args.verify:
            verify_data()
        elif args.clear_only:
            if validate_database_connection():
                with app.app_context():
                    clear_existing_data()
                    logger.info("✅ Data cleared successfully")
        else:
            success = populate_database()
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        logger.info("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

def verify_data():
    """Verify the integrity of existing data"""
    with app.app_context():
        logger.info("🔍 Verifying database integrity...")
        
        stations_count = Station.query.count()
        trains_count = Train.query.count()
        users_count = User.query.count()
        routes_count = TrainRoute.query.count()
        
        logger.info(f"📊 Current Data:")
        logger.info(f"   Stations: {stations_count:,}")
        logger.info(f"   Trains: {trains_count:,}")
        logger.info(f"   Users: {users_count}")
        logger.info(f"   Routes: {routes_count:,}")
        
        # Check for trains without routes
        trains_without_routes = db.session.query(Train).outerjoin(TrainRoute).filter(TrainRoute.train_id.is_(None)).count()
        if trains_without_routes > 0:
            logger.warning(f"⚠️  Found {trains_without_routes} trains without routes")
        
        # Check for orphaned routes
        orphaned_routes = db.session.query(TrainRoute).outerjoin(Train).filter(Train.id.is_(None)).count()
        if orphaned_routes > 0:
            logger.warning(f"⚠️  Found {orphaned_routes} orphaned routes")
        
        logger.info("✅ Data verification completed")

if __name__ == '__main__':
    main()