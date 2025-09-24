#!/usr/bin/env python3
"""
Modern Railway Database Setup Script
===================================

This script initializes the RailServe railway reservation system database
with comprehensive, realistic data including stations, trains, routes, and sample bookings.

Features:
- Creates all database tables
- Populates major railway stations across India
- Adds diverse train types with proper classifications
- Sets up realistic routes with proper timing
- Creates sample users and bookings
- Implements proper seat allocation system
- Sets up payment records

Author: RailServe Team
Version: 3.0 - Modern Rewrite
Date: September 2025
"""

import os
import sys
import logging
import random
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import app
from src.database import db
from src.models import (
    User, Station, Train, TrainRoute, Booking, Passenger, 
    Payment, ComplaintManagement, GroupBooking, RefundRequest
)
from werkzeug.security import generate_password_hash

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModernRailwayDatabaseSetup:
    """Modern comprehensive database setup with realistic Indian Railway data"""
    
    def __init__(self):
        self.app = app
        self.db = db
        logger.info("🚅 Starting Modern Railway Database Setup")
    
    def create_tables(self):
        """Create all database tables"""
        logger.info("📋 Creating database tables...")
        try:
            with self.app.app_context():
                self.db.create_all()
                logger.info("✅ All tables created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            raise
    
    def create_major_stations(self):
        """Create comprehensive station data with major Indian railway stations"""
        logger.info("🚉 Creating major railway stations...")
        
        # Major stations with realistic codes and locations
        stations_data = [
            # Delhi Region
            {"name": "New Delhi", "code": "NDLS", "city": "Delhi", "state": "Delhi"},
            {"name": "Old Delhi", "code": "DLI", "city": "Delhi", "state": "Delhi"},
            {"name": "Hazrat Nizamuddin", "code": "NZM", "city": "Delhi", "state": "Delhi"},
            {"name": "Anand Vihar Terminal", "code": "ANVT", "city": "Delhi", "state": "Delhi"},
            
            # Mumbai Region
            {"name": "Mumbai Central", "code": "MMCT", "city": "Mumbai", "state": "Maharashtra"},
            {"name": "Chhatrapati Shivaji Terminus", "code": "CSMT", "city": "Mumbai", "state": "Maharashtra"},
            {"name": "Lokmanya Tilak Terminus", "code": "LTT", "city": "Mumbai", "state": "Maharashtra"},
            {"name": "Bandra Terminus", "code": "BDTS", "city": "Mumbai", "state": "Maharashtra"},
            
            # Southern India
            {"name": "Chennai Central", "code": "MAS", "city": "Chennai", "state": "Tamil Nadu"},
            {"name": "Chennai Egmore", "code": "MS", "city": "Chennai", "state": "Tamil Nadu"},
            {"name": "Bangalore City", "code": "SBC", "city": "Bangalore", "state": "Karnataka"},
            {"name": "Bangalore Cantonment", "code": "BNC", "city": "Bangalore", "state": "Karnataka"},
            {"name": "Hyderabad Deccan", "code": "HYB", "city": "Hyderabad", "state": "Telangana"},
            {"name": "Secunderabad", "code": "SC", "city": "Hyderabad", "state": "Telangana"},
            
            # Eastern India
            {"name": "Howrah", "code": "HWH", "city": "Kolkata", "state": "West Bengal"},
            {"name": "Sealdah", "code": "SDAH", "city": "Kolkata", "state": "West Bengal"},
            {"name": "Kolkata", "code": "KOAA", "city": "Kolkata", "state": "West Bengal"},
            
            # Western India
            {"name": "Ahmedabad", "code": "ADI", "city": "Ahmedabad", "state": "Gujarat"},
            {"name": "Pune Junction", "code": "PUNE", "city": "Pune", "state": "Maharashtra"},
            {"name": "Surat", "code": "ST", "city": "Surat", "state": "Gujarat"},
            
            # Northern India
            {"name": "Chandigarh", "code": "CDG", "city": "Chandigarh", "state": "Punjab"},
            {"name": "Amritsar", "code": "ASR", "city": "Amritsar", "state": "Punjab"},
            {"name": "Ludhiana", "code": "LDH", "city": "Ludhiana", "state": "Punjab"},
            {"name": "Jammu Tawi", "code": "JAT", "city": "Jammu", "state": "Jammu & Kashmir"},
            
            # Central India
            {"name": "Bhopal", "code": "BPL", "city": "Bhopal", "state": "Madhya Pradesh"},
            {"name": "Indore", "code": "INDB", "city": "Indore", "state": "Madhya Pradesh"},
            {"name": "Nagpur", "code": "NGP", "city": "Nagpur", "state": "Maharashtra"},
            {"name": "Jabalpur", "code": "JBP", "city": "Jabalpur", "state": "Madhya Pradesh"},
            
            # Uttar Pradesh
            {"name": "Lucknow", "code": "LJN", "city": "Lucknow", "state": "Uttar Pradesh"},
            {"name": "Kanpur Central", "code": "CNB", "city": "Kanpur", "state": "Uttar Pradesh"},
            {"name": "Allahabad Junction", "code": "ALD", "city": "Allahabad", "state": "Uttar Pradesh"},
            {"name": "Varanasi", "code": "BSB", "city": "Varanasi", "state": "Uttar Pradesh"},
            {"name": "Agra Cantt", "code": "AGC", "city": "Agra", "state": "Uttar Pradesh"},
            
            # Rajasthan
            {"name": "Jaipur", "code": "JP", "city": "Jaipur", "state": "Rajasthan"},
            {"name": "Jodhpur", "code": "JU", "city": "Jodhpur", "state": "Rajasthan"},
            {"name": "Ajmer", "code": "AII", "city": "Ajmer", "state": "Rajasthan"},
            {"name": "Udaipur City", "code": "UDZ", "city": "Udaipur", "state": "Rajasthan"},
            
            # Eastern States
            {"name": "Patna", "code": "PNBE", "city": "Patna", "state": "Bihar"},
            {"name": "Guwahati", "code": "GHY", "city": "Guwahati", "state": "Assam"},
            {"name": "Bhubaneswar", "code": "BBS", "city": "Bhubaneswar", "state": "Odisha"},
            {"name": "Visakhapatnam", "code": "VSKP", "city": "Visakhapatnam", "state": "Andhra Pradesh"},
            
            # Kerala
            {"name": "Thiruvananthapuram Central", "code": "TVC", "city": "Thiruvananthapuram", "state": "Kerala"},
            {"name": "Ernakulam Junction", "code": "ERS", "city": "Kochi", "state": "Kerala"},
            {"name": "Kozhikode", "code": "CLT", "city": "Kozhikode", "state": "Kerala"},
            
            # Other Important Stations
            {"name": "Coimbatore", "code": "CBE", "city": "Coimbatore", "state": "Tamil Nadu"},
            {"name": "Madurai", "code": "MDU", "city": "Madurai", "state": "Tamil Nadu"},
            {"name": "Mysore", "code": "MYS", "city": "Mysore", "state": "Karnataka"},
            {"name": "Mangalore Central", "code": "MAQ", "city": "Mangalore", "state": "Karnataka"},
            {"name": "Goa", "code": "KRMI", "city": "Goa", "state": "Goa"},
            {"name": "Ranchi", "code": "RNC", "city": "Ranchi", "state": "Jharkhand"},
            {"name": "Raipur", "code": "R", "city": "Raipur", "state": "Chhattisgarh"}
        ]
        
        try:
            with self.app.app_context():
                station_count = 0
                for station_data in stations_data:
                    existing = Station.query.filter_by(code=station_data['code']).first()
                    if not existing:
                        station = Station(
                            name=station_data['name'],
                            code=station_data['code'],
                            city=station_data['city'],
                            state=station_data['state'],
                            active=True
                        )
                        self.db.session.add(station)
                        station_count += 1
                
                self.db.session.commit()
                logger.info(f"✅ Created {station_count} major railway stations")
                
        except Exception as e:
            logger.error(f"❌ Failed to create stations: {e}")
            self.db.session.rollback()
            raise
    
    def create_modern_trains(self):
        """Create modern trains with proper classifications and realistic data"""
        logger.info("🚂 Creating modern train fleet...")
        
        trains_data = [
            # Rajdhani Express (Premium AC trains)
            {"number": "12301", "name": "Rajdhani Express", "total_seats": 400, "fare_per_km": 2.5, "tatkal_seats": 40},
            {"number": "12302", "name": "New Delhi Rajdhani", "total_seats": 450, "fare_per_km": 2.8, "tatkal_seats": 45},
            {"number": "12951", "name": "Mumbai Rajdhani", "total_seats": 420, "fare_per_km": 2.6, "tatkal_seats": 42},
            {"number": "12953", "name": "August Kranti Rajdhani", "total_seats": 380, "fare_per_km": 2.7, "tatkal_seats": 38},
            
            # Shatabdi Express (Premium Day trains)
            {"number": "12001", "name": "Bhopal Shatabdi", "total_seats": 350, "fare_per_km": 1.8, "tatkal_seats": 35},
            {"number": "12002", "name": "Chennai Shatabdi", "total_seats": 360, "fare_per_km": 1.9, "tatkal_seats": 36},
            {"number": "12003", "name": "Bangalore Shatabdi", "total_seats": 340, "fare_per_km": 1.7, "tatkal_seats": 34},
            {"number": "12005", "name": "Kalka Shatabdi", "total_seats": 320, "fare_per_km": 1.6, "tatkal_seats": 32},
            
            # Duronto Express (Non-stop premium)
            {"number": "12259", "name": "Mumbai Duronto", "total_seats": 380, "fare_per_km": 2.2, "tatkal_seats": 38},
            {"number": "12260", "name": "Chennai Duronto", "total_seats": 390, "fare_per_km": 2.3, "tatkal_seats": 39},
            {"number": "12261", "name": "Bangalore Duronto", "total_seats": 370, "fare_per_km": 2.1, "tatkal_seats": 37},
            
            # Vande Bharat Express (Modern trains)
            {"number": "20001", "name": "Vande Bharat Express", "total_seats": 400, "fare_per_km": 3.0, "tatkal_seats": 40},
            {"number": "20002", "name": "Shatabdi Vande Bharat", "total_seats": 380, "fare_per_km": 2.9, "tatkal_seats": 38},
            
            # Premium Express
            {"number": "12431", "name": "Trivandrum Express", "total_seats": 520, "fare_per_km": 1.4, "tatkal_seats": 52},
            {"number": "12432", "name": "Chennai Express", "total_seats": 540, "fare_per_km": 1.5, "tatkal_seats": 54},
            {"number": "12433", "name": "Bangalore Express", "total_seats": 500, "fare_per_km": 1.3, "tatkal_seats": 50},
            {"number": "12434", "name": "Mumbai Express", "total_seats": 560, "fare_per_km": 1.6, "tatkal_seats": 56},
            
            # Superfast Express
            {"number": "12345", "name": "Saraighat Express", "total_seats": 600, "fare_per_km": 1.2, "tatkal_seats": 60},
            {"number": "12346", "name": "Ganga Kaveri Express", "total_seats": 580, "fare_per_km": 1.3, "tatkal_seats": 58},
            {"number": "12347", "name": "Howrah Express", "total_seats": 620, "fare_per_km": 1.1, "tatkal_seats": 62},
            {"number": "12348", "name": "Golden Temple Mail", "total_seats": 550, "fare_per_km": 1.25, "tatkal_seats": 55},
            
            # Premium Mail Express
            {"number": "11301", "name": "Udyan Express", "total_seats": 720, "fare_per_km": 0.9, "tatkal_seats": 72},
            {"number": "11302", "name": "Tamil Nadu Express", "total_seats": 700, "fare_per_km": 1.0, "tatkal_seats": 70},
            {"number": "11303", "name": "Maharashtra Express", "total_seats": 680, "fare_per_km": 0.95, "tatkal_seats": 68},
            {"number": "11304", "name": "Karnataka Express", "total_seats": 650, "fare_per_km": 0.85, "tatkal_seats": 65},
            
            # Regional Express
            {"number": "16501", "name": "Ahmedabad Express", "total_seats": 450, "fare_per_km": 0.8, "tatkal_seats": 45},
            {"number": "16502", "name": "Jodhpur Express", "total_seats": 480, "fare_per_km": 0.75, "tatkal_seats": 48},
            {"number": "16503", "name": "Ranthambore Express", "total_seats": 420, "fare_per_km": 0.7, "tatkal_seats": 42},
            {"number": "16504", "name": "Jaipur Express", "total_seats": 460, "fare_per_km": 0.8, "tatkal_seats": 46},
            
            # Long Distance Express
            {"number": "19015", "name": "Saurashtra Express", "total_seats": 650, "fare_per_km": 0.9, "tatkal_seats": 65},
            {"number": "19016", "name": "Dehradun Express", "total_seats": 600, "fare_per_km": 0.85, "tatkal_seats": 60},
            {"number": "19017", "name": "Goa Express", "total_seats": 580, "fare_per_km": 0.8, "tatkal_seats": 58},
            {"number": "19018", "name": "Mandovi Express", "total_seats": 520, "fare_per_km": 0.75, "tatkal_seats": 52},
            
            # Popular Passenger Trains
            {"number": "52901", "name": "Passenger Local", "total_seats": 800, "fare_per_km": 0.4, "tatkal_seats": 20},
            {"number": "52902", "name": "Jan Shatabdi", "total_seats": 400, "fare_per_km": 0.6, "tatkal_seats": 40},
            {"number": "52903", "name": "Intercity Express", "total_seats": 500, "fare_per_km": 0.5, "tatkal_seats": 50}
        ]
        
        try:
            with self.app.app_context():
                train_count = 0
                for train_data in trains_data:
                    existing = Train.query.filter_by(number=train_data['number']).first()
                    if not existing:
                        # Calculate tatkal fare (1.5x regular fare)
                        tatkal_fare = train_data['fare_per_km'] * 1.5
                        
                        train = Train(
                            number=train_data['number'],
                            name=train_data['name'],
                            total_seats=train_data['total_seats'],
                            available_seats=train_data['total_seats'],
                            fare_per_km=train_data['fare_per_km'],
                            tatkal_seats=train_data['tatkal_seats'],
                            tatkal_fare_per_km=tatkal_fare,
                            active=True
                        )
                        self.db.session.add(train)
                        train_count += 1
                
                self.db.session.commit()
                logger.info(f"✅ Created {train_count} modern trains")
                
        except Exception as e:
            logger.error(f"❌ Failed to create trains: {e}")
            self.db.session.rollback()
            raise
    
    def create_realistic_routes(self):
        """Create realistic train routes connecting major stations with proper timing"""
        logger.info("🗺️ Creating realistic train routes...")
        
        try:
            with self.app.app_context():
                trains = Train.query.all()
                stations = Station.query.all()
                route_count = 0
                
                # Define route patterns for different train types
                route_patterns = {
                    'Rajdhani': ['NDLS', 'MMCT', 'MAS', 'HWH', 'SC'],  # Major metro connections
                    'Shatabdi': ['NDLS', 'JP', 'ADI', 'PUNE', 'BPL'],  # Day train routes
                    'Duronto': ['MMCT', 'MAS', 'SBC', 'HYB'],  # Non-stop routes
                    'Vande Bharat': ['NDLS', 'MMCT', 'MAS', 'SBC'],  # Modern train routes
                    'Express': ['NDLS', 'CNB', 'ALD', 'BSB', 'PNBE', 'HWH'],  # Long routes
                    'Mail': ['MMCT', 'ST', 'ADI', 'JP', 'NDLS'],  # Mail train routes
                    'Passenger': ['NDLS', 'AGC', 'JP'],  # Shorter routes
                    'Local': ['MMCT', 'PUNE']  # Very short routes
                }
                
                # Create station mapping
                station_map = {station.code: station for station in stations}
                
                for train in trains:
                    # Determine route pattern based on train type
                    train_type = 'Express'  # Default
                    if 'Rajdhani' in train.name:
                        train_type = 'Rajdhani'
                    elif 'Shatabdi' in train.name:
                        train_type = 'Shatabdi'
                    elif 'Duronto' in train.name:
                        train_type = 'Duronto'
                    elif 'Vande Bharat' in train.name:
                        train_type = 'Vande Bharat'
                    elif 'Mail' in train.name:
                        train_type = 'Mail'
                    elif 'Passenger' in train.name or 'Local' in train.name:
                        train_type = 'Passenger'
                    
                    # Get route pattern or create random route
                    if train_type in route_patterns:
                        station_codes = route_patterns[train_type]
                    else:
                        # Create random route for other trains
                        station_codes = random.sample([s.code for s in stations], min(6, len(stations)))
                    
                    # Ensure stations exist
                    route_stations = []
                    for code in station_codes:
                        if code in station_map:
                            route_stations.append(station_map[code])
                    
                    if len(route_stations) < 2:
                        # Fallback to random stations
                        route_stations = random.sample(stations, min(4, len(stations)))
                    
                    # Create route with realistic timing
                    base_time = 6  # Start at 6 AM
                    for sequence, station in enumerate(route_stations, 1):
                        # Check if route already exists
                        existing = TrainRoute.query.filter_by(
                            train_id=train.id, 
                            station_id=station.id
                        ).first()
                        
                        if not existing:
                            # Calculate timing based on train type
                            if train_type in ['Rajdhani', 'Shatabdi', 'Vande Bharat']:
                                stop_duration = 0.08  # 5 minutes
                                travel_time = 1.5  # 1.5 hours between stations
                            elif train_type == 'Duronto':
                                stop_duration = 0.05  # 3 minutes
                                travel_time = 1.0  # 1 hour between stations
                            else:
                                stop_duration = 0.17  # 10 minutes
                                travel_time = 2.0  # 2 hours between stations
                            
                            arrival_hours = base_time + (sequence - 1) * travel_time
                            departure_hours = arrival_hours + stop_duration
                            
                            # Handle 24-hour wraparound
                            arrival_hours = arrival_hours % 24
                            departure_hours = departure_hours % 24
                            
                            arrival_time = datetime.strptime(f"{int(arrival_hours):02d}:{int((arrival_hours % 1) * 60):02d}", "%H:%M").time()
                            departure_time = datetime.strptime(f"{int(departure_hours):02d}:{int((departure_hours % 1) * 60):02d}", "%H:%M").time()
                            
                            route = TrainRoute(
                                train_id=train.id,
                                station_id=station.id,
                                sequence=sequence,
                                arrival_time=arrival_time,
                                departure_time=departure_time,
                                distance_from_start=sequence * 200,  # Realistic 200km between major stations
                            )
                            self.db.session.add(route)
                            route_count += 1
                
                self.db.session.commit()
                logger.info(f"✅ Created {route_count} realistic train routes")
                
        except Exception as e:
            logger.error(f"❌ Failed to create routes: {e}")
            self.db.session.rollback()
            raise
    
    def create_modern_users(self):
        """Create modern user accounts with different roles"""
        logger.info("👥 Creating modern user accounts...")
        
        users_data = [
            # Admin users
            {"username": "admin", "email": "admin@railserve.com", "password": "admin123", "role": "admin"},
            {"username": "superadmin", "email": "superadmin@railserve.com", "password": "super123", "role": "super_admin"},
            
            # Regular users with Indian names
            {"username": "rajesh_kumar", "email": "rajesh.kumar@email.com", "password": "password123", "role": "user"},
            {"username": "priya_sharma", "email": "priya.sharma@email.com", "password": "password123", "role": "user"},
            {"username": "amit_patel", "email": "amit.patel@email.com", "password": "password123", "role": "user"},
            {"username": "sneha_reddy", "email": "sneha.reddy@email.com", "password": "password123", "role": "user"},
            {"username": "vikram_singh", "email": "vikram.singh@email.com", "password": "password123", "role": "user"},
            {"username": "kavitha_nair", "email": "kavitha.nair@email.com", "password": "password123", "role": "user"},
            {"username": "ravi_verma", "email": "ravi.verma@email.com", "password": "password123", "role": "user"},
            {"username": "anjali_joshi", "email": "anjali.joshi@email.com", "password": "password123", "role": "user"},
            {"username": "suresh_yadav", "email": "suresh.yadav@email.com", "password": "password123", "role": "user"},
            {"username": "deepika_iyer", "email": "deepika.iyer@email.com", "password": "password123", "role": "user"},
            
            # Test user
            {"username": "testuser", "email": "test@railserve.com", "password": "test123", "role": "user"}
        ]
        
        try:
            with self.app.app_context():
                user_count = 0
                for user_data in users_data:
                    existing = User.query.filter_by(username=user_data['username']).first()
                    if not existing:
                        user = User(
                            username=user_data['username'],
                            email=user_data['email'],
                            password_hash=generate_password_hash(user_data['password']),
                            role=user_data['role'],
                            active=True
                        )
                        self.db.session.add(user)
                        user_count += 1
                
                self.db.session.commit()
                logger.info(f"✅ Created {user_count} user accounts")
                
        except Exception as e:
            logger.error(f"❌ Failed to create users: {e}")
            self.db.session.rollback()
            raise
    
    def create_realistic_bookings(self):
        """Create realistic sample bookings with proper seat allocation"""
        logger.info("🎫 Creating realistic sample bookings...")
        
        try:
            with self.app.app_context():
                users = User.query.filter(User.role == 'user').all()
                trains = Train.query.limit(15).all()  # Use first 15 trains
                stations = Station.query.all()
                
                booking_count = 0
                passenger_count = 0
                
                # Indian names for passengers
                indian_names = [
                    "Rajesh Kumar", "Priya Sharma", "Amit Patel", "Sneha Reddy",
                    "Vikram Singh", "Pooja Gupta", "Ravi Verma", "Anjali Joshi",
                    "Suresh Yadav", "Kavitha Nair", "Manoj Agarwal", "Deepika Iyer",
                    "Arjun Mehta", "Divya Aggarwal", "Kiran Desai", "Rohit Bansal",
                    "Neha Kapoor", "Sanjay Malhotra", "Sunita Agrawal", "Ashok Jain"
                ]
                
                # Create 50 realistic bookings
                for _ in range(50):
                    user = random.choice(users)
                    train = random.choice(trains)
                    
                    # Get train's route stations
                    train_stations = [tr.station for tr in train.routes]
                    if len(train_stations) < 2:
                        continue
                    
                    from_station = random.choice(train_stations[:-1])
                    to_station = random.choice(train_stations[train_stations.index(from_station)+1:])
                    
                    # Create realistic booking details
                    journey_date = date.today() + timedelta(days=random.randint(1, 60))
                    passengers = random.randint(1, 4)
                    coach_class = random.choice(['AC1', 'AC2', 'AC3', 'SL', '2S', 'CC'])
                    booking_type = random.choice(['general'] * 8 + ['tatkal'] * 2)  # 80% general, 20% tatkal
                    quota = random.choice(['general'] * 6 + ['ladies', 'senior', 'tatkal'])
                    status = random.choice(['confirmed'] * 6 + ['waitlisted'] * 3 + ['cancelled'] * 1)
                    
                    # Calculate realistic fare
                    distance = abs(train_stations.index(to_station) - train_stations.index(from_station)) * 200
                    base_fare = distance * train.fare_per_km
                    
                    # Class-based multipliers
                    class_multiplier = {
                        'AC1': 5.0, 'AC2': 3.0, 'AC3': 2.0, 
                        'SL': 1.0, '2S': 0.6, 'CC': 1.2
                    }
                    
                    total_amount = base_fare * class_multiplier[coach_class] * passengers
                    
                    # Add tatkal surcharge if applicable
                    if booking_type == 'tatkal':
                        total_amount *= 1.3
                    
                    # Generate unique PNR
                    pnr = ''.join([str(random.randint(0, 9)) for _ in range(10)])
                    
                    booking = Booking(
                        pnr=pnr,
                        user_id=user.id,
                        train_id=train.id,
                        from_station_id=from_station.id,
                        to_station_id=to_station.id,
                        journey_date=journey_date,
                        passengers=passengers,
                        total_amount=round(total_amount, 2),
                        booking_type=booking_type,
                        quota=quota,
                        coach_class=coach_class,
                        status=status,
                        booking_date=datetime.now() - timedelta(days=random.randint(0, 15))
                    )
                    
                    self.db.session.add(booking)
                    self.db.session.flush()  # Get booking ID
                    
                    # Create passengers for this booking
                    for i in range(passengers):
                        passenger_name = random.choice(indian_names)
                        age = random.randint(18, 75)
                        gender = random.choice(['Male', 'Female'])
                        id_proof_type = random.choice(['Aadhar', 'PAN', 'Passport', 'Voter ID'])
                        id_proof_number = ''.join([str(random.randint(0, 9)) for _ in range(12)])
                        seat_preference = random.choice(['Lower', 'Middle', 'Upper', 'Window', 'Aisle', 'No Preference'])
                        
                        # Assign seat if confirmed
                        seat_number = None
                        berth_type = None
                        if status == 'confirmed':
                            coach_prefix = {'AC1': 'H', 'AC2': 'A', 'AC3': 'B', 'SL': 'S', '2S': 'D', 'CC': 'C'}
                            coach_num = random.randint(1, 8)
                            seat_num = random.randint(1, 72)
                            seat_number = f"{coach_prefix[coach_class]}{coach_num}-{seat_num}"
                            berth_type = random.choice(['Lower', 'Middle', 'Upper', 'Side Lower', 'Side Upper'])
                        
                        passenger = Passenger(
                            booking_id=booking.id,
                            name=passenger_name,
                            age=age,
                            gender=gender,
                            id_proof_type=id_proof_type,
                            id_proof_number=id_proof_number,
                            seat_preference=seat_preference,
                            coach_class=coach_class,
                            seat_number=seat_number,
                            berth_type=berth_type
                        )
                        self.db.session.add(passenger)
                        passenger_count += 1
                    
                    booking_count += 1
                
                self.db.session.commit()
                logger.info(f"✅ Created {booking_count} realistic bookings with {passenger_count} passengers")
                
        except Exception as e:
            logger.error(f"❌ Failed to create bookings: {e}")
            self.db.session.rollback()
            raise
    
    def create_payment_records(self):
        """Create payment records for confirmed bookings"""
        logger.info("💳 Creating payment records...")
        
        try:
            with self.app.app_context():
                confirmed_bookings = Booking.query.filter_by(status='confirmed').all()
                payment_count = 0
                
                for booking in confirmed_bookings:
                    # Only create payment if it doesn't exist
                    existing_payment = Payment.query.filter_by(booking_id=booking.id).first()
                    if not existing_payment:
                        payment_method = random.choice([
                            'credit_card', 'debit_card', 'upi', 'net_banking', 'wallet'
                        ])
                        
                        payment = Payment(
                            booking_id=booking.id,
                            user_id=booking.user_id,
                            amount=booking.total_amount,
                            payment_method=payment_method,
                            transaction_id=f"TXN{random.randint(100000000, 999999999)}",
                            status='success',
                            completed_at=booking.booking_date + timedelta(minutes=random.randint(1, 45))
                        )
                        self.db.session.add(payment)
                        payment_count += 1
                
                self.db.session.commit()
                logger.info(f"✅ Created {payment_count} payment records")
                
        except Exception as e:
            logger.error(f"❌ Failed to create payments: {e}")
            self.db.session.rollback()
            raise
    
    def setup_modern_database(self):
        """Main method to set up the complete modern database"""
        logger.info("🚀" + "="*70)
        logger.info("🚀 STARTING MODERN RAILWAY DATABASE SETUP")
        logger.info("🚀" + "="*70)
        
        try:
            with self.app.app_context():
                self.create_tables()
                self.create_major_stations()
                self.create_modern_trains()
                self.create_realistic_routes()
                self.create_modern_users()
                self.create_realistic_bookings()
                self.create_payment_records()
                
                logger.info("🚀" + "="*70)
                logger.info("✅ MODERN DATABASE SETUP COMPLETED SUCCESSFULLY!")
                logger.info("🚀" + "="*70)
                logger.info("🎯 Database ready for RailServe Railway Reservation System")
                logger.info("👤 Admin credentials: admin / admin123")
                logger.info("👤 Super Admin credentials: superadmin / super123")
                logger.info("👤 Test user credentials: testuser / test123")
                logger.info("🚉 Major railway stations configured")
                logger.info("🚂 Modern train fleet with realistic routes")
                logger.info("🎫 Sample bookings with seat allocation")
                logger.info("💳 Payment records for confirmed bookings")
                logger.info("🚀" + "="*70)
                
        except Exception as e:
            logger.error(f"❌ MODERN DATABASE SETUP FAILED: {e}")
            raise

def main():
    """Main function to run modern database setup"""
    try:
        setup = ModernRailwayDatabaseSetup()
        setup.setup_modern_database()
        return True
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)