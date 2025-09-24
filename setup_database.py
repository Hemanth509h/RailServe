#!/usr/bin/env python3
"""
Comprehensive Railway Database Setup Script
==========================================

This script initializes the RailServe railway reservation system database
with comprehensive data including stations, trains, routes, and sample bookings.

Features:
- Creates all database tables
- Populates stations across India
- Adds diverse train types and routes
- Sets up coach configurations and fare structures
- Creates sample users and bookings
- Implements data validation and error handling

Author: RailServe Team
Version: 2.0
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

from app import app, db
from models import (
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

class DatabaseSetup:
    """Comprehensive database setup and data population"""
    
    def __init__(self):
        self.app = app
        self.db = db
        logger.info("Starting Comprehensive Railway Database Setup")
    
    def create_tables(self):
        """Create all database tables"""
        logger.info("Creating database tables...")
        try:
            with self.app.app_context():
                self.db.create_all()
                logger.info("✓ All tables created successfully")
        except Exception as e:
            logger.error(f"✗ Failed to create tables: {e}")
            raise
    
    def create_stations(self):
        """Create comprehensive station data across India"""
        logger.info("Creating stations...")
        
        stations_data = [
            # Metro Cities - Tier 1
            {"name": "New Delhi", "code": "NDLS", "city": "Delhi", "state": "Delhi"},
            {"name": "Mumbai Central", "code": "MMCT", "city": "Mumbai", "state": "Maharashtra"},
            {"name": "Bangalore City", "code": "BNC", "city": "Bangalore", "state": "Karnataka"},
            {"name": "Chennai Central", "code": "MAS", "city": "Chennai", "state": "Tamil Nadu"},
            {"name": "Kolkata Howrah", "code": "HWH", "city": "Kolkata", "state": "West Bengal"},
            {"name": "Hyderabad Deccan", "code": "HYB", "city": "Hyderabad", "state": "Telangana"},
            {"name": "Pune Junction", "code": "PUNE", "city": "Pune", "state": "Maharashtra"},
            {"name": "Ahmedabad", "code": "ADI", "city": "Ahmedabad", "state": "Gujarat"},
            
            # Major Cities - Tier 2
            {"name": "Jaipur", "code": "JP", "city": "Jaipur", "state": "Rajasthan"},
            {"name": "Lucknow", "code": "LJN", "city": "Lucknow", "state": "Uttar Pradesh"},
            {"name": "Kanpur Central", "code": "CNB", "city": "Kanpur", "state": "Uttar Pradesh"},
            {"name": "Nagpur", "code": "NGP", "city": "Nagpur", "state": "Maharashtra"},
            {"name": "Indore", "code": "INDB", "city": "Indore", "state": "Madhya Pradesh"},
            {"name": "Bhopal", "code": "BPL", "city": "Bhopal", "state": "Madhya Pradesh"},
            {"name": "Chandigarh", "code": "CDG", "city": "Chandigarh", "state": "Punjab"},
            {"name": "Coimbatore", "code": "CBE", "city": "Coimbatore", "state": "Tamil Nadu"},
            {"name": "Kochi", "code": "ERS", "city": "Kochi", "state": "Kerala"},
            {"name": "Trivandrum Central", "code": "TVC", "city": "Trivandrum", "state": "Kerala"},
            {"name": "Visakhapatnam", "code": "VSKP", "city": "Visakhapatnam", "state": "Andhra Pradesh"},
            {"name": "Bhubaneswar", "code": "BBS", "city": "Bhubaneswar", "state": "Odisha"},
            
            # Important Junction Stations
            {"name": "Allahabad Junction", "code": "ALD", "city": "Allahabad", "state": "Uttar Pradesh"},
            {"name": "Gwalior", "code": "GWL", "city": "Gwalior", "state": "Madhya Pradesh"},
            {"name": "Agra Cantt", "code": "AGC", "city": "Agra", "state": "Uttar Pradesh"},
            {"name": "Varanasi", "code": "BSB", "city": "Varanasi", "state": "Uttar Pradesh"},
            {"name": "Patna", "code": "PNBE", "city": "Patna", "state": "Bihar"},
            {"name": "Guwahati", "code": "GHY", "city": "Guwahati", "state": "Assam"},
            {"name": "Ranchi", "code": "RNC", "city": "Ranchi", "state": "Jharkhand"},
            {"name": "Raipur", "code": "R", "city": "Raipur", "state": "Chhattisgarh"},
            {"name": "Jodhpur", "code": "JU", "city": "Jodhpur", "state": "Rajasthan"},
            {"name": "Udaipur City", "code": "UDZ", "city": "Udaipur", "state": "Rajasthan"},
            {"name": "Amritsar", "code": "ASR", "city": "Amritsar", "state": "Punjab"},
            
            # Tourist & Religious Centers
            {"name": "Haridwar", "code": "HW", "city": "Haridwar", "state": "Uttarakhand"},
            {"name": "Rishikesh", "code": "RKSH", "city": "Rishikesh", "state": "Uttarakhand"},
            {"name": "Mathura", "code": "MTJ", "city": "Mathura", "state": "Uttar Pradesh"},
            {"name": "Vrindavan", "code": "VRB", "city": "Vrindavan", "state": "Uttar Pradesh"},
            {"name": "Tirupati", "code": "TPTY", "city": "Tirupati", "state": "Andhra Pradesh"},
            {"name": "Madurai", "code": "MDU", "city": "Madurai", "state": "Tamil Nadu"},
            {"name": "Thanjavur", "code": "TJ", "city": "Thanjavur", "state": "Tamil Nadu"},
            {"name": "Mysore", "code": "MYS", "city": "Mysore", "state": "Karnataka"},
            {"name": "Hampi", "code": "HPT", "city": "Hampi", "state": "Karnataka"},
            {"name": "Ajmer", "code": "AII", "city": "Ajmer", "state": "Rajasthan"}
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
                logger.info(f"✓ Created {station_count} stations across India")
                
        except Exception as e:
            logger.error(f"✗ Failed to create stations: {e}")
            self.db.session.rollback()
            raise
    
    def create_trains(self):
        """Create diverse train data with different categories"""
        logger.info("Creating trains...")
        
        trains_data = [
            # Rajdhani Express (Premium AC trains)
            {"number": "12301", "name": "Rajdhani Express", "type": "Rajdhani", "total_seats": 400, "tatkal_seats": 40},
            {"number": "12302", "name": "New Delhi Rajdhani", "type": "Rajdhani", "total_seats": 450, "tatkal_seats": 45},
            {"number": "12951", "name": "Mumbai Rajdhani", "type": "Rajdhani", "total_seats": 420, "tatkal_seats": 42},
            
            # Shatabdi Express (Day trains)
            {"number": "12001", "name": "Bhopal Shatabdi", "type": "Shatabdi", "total_seats": 350, "tatkal_seats": 35},
            {"number": "12002", "name": "Chennai Shatabdi", "type": "Shatabdi", "total_seats": 360, "tatkal_seats": 36},
            {"number": "12003", "name": "Bangalore Shatabdi", "type": "Shatabdi", "total_seats": 340, "tatkal_seats": 34},
            
            # Duronto Express (Non-stop)
            {"number": "12259", "name": "Mumbai Duronto", "type": "Duronto", "total_seats": 380, "tatkal_seats": 38},
            {"number": "12260", "name": "Chennai Duronto", "type": "Duronto", "total_seats": 390, "tatkal_seats": 39},
            
            # Premium Express
            {"number": "12431", "name": "Trivandrum Express", "type": "Express", "total_seats": 520, "tatkal_seats": 52},
            {"number": "12432", "name": "Chennai Express", "type": "Express", "total_seats": 540, "tatkal_seats": 54},
            {"number": "12433", "name": "Bangalore Express", "type": "Express", "total_seats": 500, "tatkal_seats": 50},
            
            # Superfast Trains
            {"number": "12345", "name": "Saraighat Express", "type": "Superfast", "total_seats": 600, "tatkal_seats": 60},
            {"number": "12346", "name": "Ganga Kaveri Express", "type": "Superfast", "total_seats": 580, "tatkal_seats": 58},
            {"number": "12347", "name": "Howrah Express", "type": "Superfast", "total_seats": 620, "tatkal_seats": 62},
            
            # Mail Express
            {"number": "11301", "name": "Udyan Express", "type": "Mail", "total_seats": 720, "tatkal_seats": 72},
            {"number": "11302", "name": "Tamil Nadu Express", "type": "Mail", "total_seats": 700, "tatkal_seats": 70},
            {"number": "11303", "name": "Maharashtra Express", "type": "Mail", "total_seats": 680, "tatkal_seats": 68},
            
            # Regional Trains
            {"number": "16501", "name": "Ahmedabad Express", "type": "Express", "total_seats": 450, "tatkal_seats": 45},
            {"number": "16502", "name": "Jodhpur Express", "type": "Express", "total_seats": 480, "tatkal_seats": 48},
            {"number": "16503", "name": "Ranthambore Express", "type": "Express", "total_seats": 420, "tatkal_seats": 42},
            
            # Long Distance
            {"number": "19015", "name": "Saurashtra Express", "type": "Express", "total_seats": 650, "tatkal_seats": 65},
            {"number": "19016", "name": "Dehradun Express", "type": "Express", "total_seats": 600, "tatkal_seats": 60},
            {"number": "19017", "name": "Goa Express", "type": "Express", "total_seats": 580, "tatkal_seats": 58}
        ]
        
        try:
            with self.app.app_context():
                train_count = 0
                for train_data in trains_data:
                    existing = Train.query.filter_by(number=train_data['number']).first()
                    if not existing:
                        train = Train(
                            number=train_data['number'],
                            name=train_data['name'],
                            train_type=train_data['type'],
                            total_seats=train_data['total_seats'],
                            available_seats=train_data['total_seats'],
                            tatkal_seats=train_data['tatkal_seats'],
                            active=True
                        )
                        self.db.session.add(train)
                        train_count += 1
                
                self.db.session.commit()
                logger.info(f"✓ Created {train_count} trains with diverse categories")
                
        except Exception as e:
            logger.error(f"✗ Failed to create trains: {e}")
            self.db.session.rollback()
            raise
    
    def create_train_routes(self):
        """Create comprehensive train routes connecting major stations"""
        logger.info("Creating train routes...")
        
        try:
            with self.app.app_context():
                trains = Train.query.all()
                stations = Station.query.all()
                route_count = 0
                
                # Create routes for each train with realistic station sequences
                for train in trains:
                    if "Rajdhani" in train.name:
                        # Rajdhani routes: Major metros with fewer stops
                        route_stations = random.sample([s for s in stations if s.city in 
                            ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata']], 3)
                    elif "Shatabdi" in train.name:
                        # Shatabdi: Day trains with 2-4 stops
                        route_stations = random.sample(stations, random.randint(2, 4))
                    elif "Duronto" in train.name:
                        # Duronto: Source to destination with minimal stops
                        route_stations = random.sample(stations, 2)
                    else:
                        # Regular trains: More comprehensive stops
                        route_stations = random.sample(stations, random.randint(4, 8))
                    
                    # Sort by city name for consistent routing
                    route_stations.sort(key=lambda x: x.name)
                    
                    for sequence, station in enumerate(route_stations, 1):
                        # Check if route already exists
                        existing = TrainRoute.query.filter_by(
                            train_id=train.id, 
                            station_id=station.id
                        ).first()
                        
                        if not existing:
                            # Calculate arrival and departure times
                            base_time = datetime.strptime("06:00", "%H:%M").time()
                            arrival_hours = 6 + (sequence - 1) * 2
                            departure_hours = arrival_hours + 0.25  # 15 min stop
                            
                            arrival_time = datetime.strptime(f"{arrival_hours:02d}:00", "%H:%M").time()
                            departure_time = datetime.strptime(f"{int(departure_hours):02d}:{int((departure_hours % 1) * 60):02d}", "%H:%M").time()
                            
                            route = TrainRoute(
                                train_id=train.id,
                                station_id=station.id,
                                sequence=sequence,
                                arrival_time=arrival_time,
                                departure_time=departure_time,
                                distance_from_source=sequence * 150,  # Approximate 150km between major stations
                                platform_number=random.randint(1, 8)
                            )
                            self.db.session.add(route)
                            route_count += 1
                
                self.db.session.commit()
                logger.info(f"✓ Created {route_count} train route entries")
                
        except Exception as e:
            logger.error(f"✗ Failed to create train routes: {e}")
            self.db.session.rollback()
            raise
    
    def create_sample_users(self):
        """Create sample users for testing"""
        logger.info("Creating sample users...")
        
        users_data = [
            {"username": "admin", "email": "admin@railserve.com", "password": "admin123", "is_admin": True},
            {"username": "john_doe", "email": "john@example.com", "password": "password123"},
            {"username": "jane_smith", "email": "jane@example.com", "password": "password123"},
            {"username": "rajesh_kumar", "email": "rajesh@example.com", "password": "password123"},
            {"username": "priya_sharma", "email": "priya@example.com", "password": "password123"},
            {"username": "amit_patel", "email": "amit@example.com", "password": "password123"},
            {"username": "sneha_reddy", "email": "sneha@example.com", "password": "password123"},
            {"username": "test_user", "email": "test@railserve.com", "password": "test123"}
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
                            password_hash=generate_password_hash(user_data['password'])
                        )
                        self.db.session.add(user)
                        user_count += 1
                
                self.db.session.commit()
                logger.info(f"✓ Created {user_count} sample users")
                
        except Exception as e:
            logger.error(f"✗ Failed to create users: {e}")
            self.db.session.rollback()
            raise
    
    def create_sample_bookings(self):
        """Create realistic sample bookings for testing"""
        logger.info("Creating sample bookings...")
        
        try:
            with self.app.app_context():
                users = User.query.filter(User.username != 'admin').all()
                trains = Train.query.all()[:10]  # Use first 10 trains
                stations = Station.query.all()
                
                booking_count = 0
                passenger_count = 0
                
                for _ in range(25):  # Create 25 sample bookings
                    user = random.choice(users)
                    train = random.choice(trains)
                    
                    # Get train's route stations
                    train_stations = [tr.station for tr in train.routes]
                    if len(train_stations) < 2:
                        continue
                    
                    from_station = random.choice(train_stations[:-1])
                    to_station = random.choice(train_stations[train_stations.index(from_station)+1:])
                    
                    # Create booking
                    journey_date = date.today() + timedelta(days=random.randint(1, 30))
                    passengers = random.randint(1, 4)
                    coach_class = random.choice(['AC1', 'AC2', 'AC3', 'SL', '2S', 'CC'])
                    booking_type = random.choice(['general', 'tatkal'])
                    quota = random.choice(['general', 'ladies', 'senior', 'tatkal'])
                    status = random.choice(['confirmed', 'waitlisted', 'cancelled'])
                    
                    # Calculate fare based on distance and class
                    base_fare = 100 + random.randint(50, 500)
                    class_multiplier = {'AC1': 5.0, 'AC2': 3.0, 'AC3': 2.0, 'SL': 1.0, '2S': 0.6, 'CC': 1.2}
                    total_amount = base_fare * class_multiplier[coach_class] * passengers
                    
                    booking = Booking(
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
                        booking_date=datetime.now() - timedelta(days=random.randint(0, 10))
                    )
                    
                    self.db.session.add(booking)
                    self.db.session.flush()  # Get booking ID
                    
                    # Create passengers for this booking
                    indian_names = [
                        "Rajesh Kumar", "Priya Sharma", "Amit Patel", "Sneha Reddy",
                        "Vikram Singh", "Pooja Gupta", "Ravi Verma", "Anjali Joshi",
                        "Suresh Yadav", "Kavitha Nair", "Manoj Agarwal", "Deepika Iyer"
                    ]
                    
                    for i in range(passengers):
                        passenger = Passenger(
                            booking_id=booking.id,
                            name=random.choice(indian_names),
                            age=random.randint(18, 70),
                            gender=random.choice(['male', 'female']),
                            seat_preference=random.choice(['Lower', 'Middle', 'Upper', 'Window', 'Aisle', None])
                        )
                        self.db.session.add(passenger)
                        passenger_count += 1
                    
                    booking_count += 1
                
                self.db.session.commit()
                logger.info(f"✓ Created {booking_count} sample bookings with {passenger_count} passengers")
                
        except Exception as e:
            logger.error(f"✗ Failed to create sample bookings: {e}")
            self.db.session.rollback()
            raise
    
    def create_sample_payments(self):
        """Create payment records for confirmed bookings"""
        logger.info("Creating sample payments...")
        
        try:
            with self.app.app_context():
                confirmed_bookings = Booking.query.filter_by(status='confirmed').all()
                payment_count = 0
                
                for booking in confirmed_bookings:
                    # Only create payment if it doesn't exist
                    existing_payment = Payment.query.filter_by(booking_id=booking.id).first()
                    if not existing_payment:
                        payment = Payment(
                            booking_id=booking.id,
                            user_id=booking.user_id,
                            amount=booking.total_amount,
                            payment_method=random.choice(['credit_card', 'debit_card', 'upi', 'net_banking']),
                            transaction_id=f"TXN{random.randint(100000, 999999)}",
                            status='success',
                            completed_at=booking.booking_date + timedelta(minutes=random.randint(1, 30))
                        )
                        self.db.session.add(payment)
                        payment_count += 1
                
                self.db.session.commit()
                logger.info(f"✓ Created {payment_count} payment records")
                
        except Exception as e:
            logger.error(f"✗ Failed to create payments: {e}")
            self.db.session.rollback()
            raise
    
    def setup_database(self):
        """Main method to set up the complete database"""
        logger.info("=" * 60)
        logger.info("STARTING COMPREHENSIVE RAILWAY DATABASE SETUP")
        logger.info("=" * 60)
        
        try:
            self.create_tables()
            self.create_stations()
            self.create_trains()
            self.create_train_routes()
            self.create_sample_users()
            self.create_sample_bookings()
            self.create_sample_payments()
            
            logger.info("=" * 60)
            logger.info("✓ DATABASE SETUP COMPLETED SUCCESSFULLY!")
            logger.info("=" * 60)
            logger.info("Database ready for RailServe Railway Reservation System")
            logger.info("Admin credentials: admin / admin123")
            logger.info("Test user credentials: test_user / test123")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"✗ DATABASE SETUP FAILED: {e}")
            raise

def main():
    """Main function to run database setup"""
    try:
        setup = DatabaseSetup()
        setup.setup_database()
        return True
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)