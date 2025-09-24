#!/usr/bin/env python3
"""
Modern Railway Database Setup Script
===================================

A clean, efficient database setup for the RailServe railway booking system.
Initializes database with comprehensive, realistic Indian railway data.

Features:
- Clean database initialization
- Realistic Indian railway stations
- Modern train fleet with proper classifications  
- Dynamic route generation
- Sample user accounts
- Production-ready configuration

Author: RailServe Team
Version: 4.0 - Modern Rewrite
Date: September 2025
"""

import os
import sys
import logging
from datetime import datetime, time
from decimal import Decimal

# Add src directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

try:
    from src.app import app
    from src.database import db
    from src.models import (
        User, Station, Train, TrainRoute, Booking, Passenger, 
        Payment, ComplaintManagement, GroupBooking, RefundRequest
    )
    from werkzeug.security import generate_password_hash
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RailwayDatabaseSetup:
    """Modern, efficient railway database setup"""
    
    def __init__(self):
        self.app = app
        self.db = db
        logger.info("🚅 Initializing Modern Railway Database Setup")
    
    def setup_database(self):
        """Complete database setup process"""
        try:
            with self.app.app_context():
                logger.info("📋 Creating database tables...")
                self.db.create_all()
                logger.info("✅ Database tables created")
                
                # Setup data in logical order
                self.create_stations()
                self.create_trains()
                self.create_routes()
                self.create_users()
                
                logger.info("🎉 Database setup completed successfully!")
                
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            raise
    
    def create_stations(self):
        """Create major Indian railway stations"""
        logger.info("🚉 Setting up railway stations...")
        
        stations = [
            # Metro Cities
            ("New Delhi", "NDLS", "Delhi", "Delhi"),
            ("Mumbai Central", "MMCT", "Mumbai", "Maharashtra"), 
            ("Chennai Central", "MAS", "Chennai", "Tamil Nadu"),
            ("Howrah", "HWH", "Kolkata", "West Bengal"),
            ("Bangalore City", "SBC", "Bangalore", "Karnataka"),
            ("Hyderabad Deccan", "HYB", "Hyderabad", "Telangana"),
            ("Pune Junction", "PUNE", "Pune", "Maharashtra"),
            ("Ahmedabad", "ADI", "Ahmedabad", "Gujarat"),
            
            # Major Cities
            ("Jaipur", "JP", "Jaipur", "Rajasthan"),
            ("Lucknow", "LJN", "Lucknow", "Uttar Pradesh"),
            ("Kanpur Central", "CNB", "Kanpur", "Uttar Pradesh"),
            ("Patna Junction", "PNBE", "Patna", "Bihar"),
            ("Bhopal", "BPL", "Bhopal", "Madhya Pradesh"),
            ("Indore", "INDB", "Indore", "Madhya Pradesh"),
            ("Nagpur", "NGP", "Nagpur", "Maharashtra"),
            ("Coimbatore", "CBE", "Coimbatore", "Tamil Nadu"),
            ("Kochi", "ERS", "Kochi", "Kerala"),
            ("Thiruvananthapuram", "TVC", "Thiruvananthapuram", "Kerala"),
            ("Visakhapatnam", "VSKP", "Visakhapatnam", "Andhra Pradesh"),
            
            # Important Junctions
            ("Allahabad", "ALD", "Allahabad", "Uttar Pradesh"),
            ("Varanasi", "BSB", "Varanasi", "Uttar Pradesh"),
            ("Agra Cantt", "AGC", "Agra", "Uttar Pradesh"),
            ("Guwahati", "GHY", "Guwahati", "Assam"),
            ("Bhubaneswar", "BBS", "Bhubaneswar", "Odisha"),
            ("Chandigarh", "CDG", "Chandigarh", "Punjab"),
            ("Amritsar", "ASR", "Amritsar", "Punjab"),
            ("Jodhpur", "JU", "Jodhpur", "Rajasthan"),
            ("Udaipur", "UDZ", "Udaipur", "Rajasthan"),
            ("Ranchi", "RNC", "Ranchi", "Jharkhand")
        ]
        
        count = 0
        for name, code, city, state in stations:
            if not Station.query.filter_by(code=code).first():
                station = Station(
                    name=name,
                    code=code, 
                    city=city,
                    state=state,
                    active=True
                )
                self.db.session.add(station)
                count += 1
        
        self.db.session.commit()
        logger.info(f"✅ Created {count} railway stations")
    
    def create_trains(self):
        """Create modern train fleet"""
        logger.info("🚂 Setting up modern train fleet...")
        
        trains = [
            # Premium Trains
            ("12301", "Rajdhani Express", 400, 2.5, 40),
            ("12951", "Mumbai Rajdhani", 420, 2.6, 42),
            ("20001", "Vande Bharat Express", 400, 3.0, 40),
            ("12001", "Shatabdi Express", 350, 1.8, 35),
            ("12259", "Duronto Express", 380, 2.2, 38),
            
            # Express Trains
            ("12431", "Trivandrum Express", 520, 1.4, 52),
            ("12345", "Saraighat Express", 600, 1.2, 60),
            ("11301", "Udyan Express", 720, 0.9, 72),
            ("16501", "Ahmedabad Express", 450, 0.8, 45),
            ("19015", "Saurashtra Express", 650, 0.9, 65),
            
            # Popular Trains  
            ("12002", "Chennai Shatabdi", 360, 1.9, 36),
            ("12432", "Chennai Express", 540, 1.5, 54),
            ("11302", "Tamil Nadu Express", 700, 1.0, 70),
            ("16502", "Jodhpur Express", 480, 0.75, 48),
            ("52902", "Jan Shatabdi", 400, 0.6, 40)
        ]
        
        count = 0
        for number, name, seats, fare, tatkal in trains:
            if not Train.query.filter_by(number=number).first():
                train = Train(
                    number=number,
                    name=name,
                    total_seats=seats,
                    available_seats=seats,
                    fare_per_km=fare,
                    tatkal_seats=tatkal,
                    tatkal_fare_per_km=fare * 1.5,
                    active=True
                )
                self.db.session.add(train)
                count += 1
        
        self.db.session.commit()
        logger.info(f"✅ Created {count} trains")
    
    def create_routes(self):
        """Create realistic train routes"""
        logger.info("🗺️ Setting up train routes...")
        
        # Get all trains and stations
        trains = Train.query.all()
        stations = Station.query.all()
        
        # Create simple route patterns
        major_routes = [
            ["NDLS", "AGC", "JP", "ADI"],  # Delhi-Ahmedabad
            ["MMCT", "PUNE", "SBC", "MAS"],  # Mumbai-Chennai  
            ["HWH", "PNBE", "CNB", "NDLS"],  # Kolkata-Delhi
            ["MAS", "CBE", "ERS", "TVC"],  # Chennai-Kerala
            ["NDLS", "LJN", "ALD", "BSB"]  # Delhi-Varanasi
        ]
        
        station_map = {s.code: s for s in stations}
        count = 0
        
        for i, train in enumerate(trains):
            # Select a route pattern
            route_codes = major_routes[i % len(major_routes)]
            
            # Create route with timing
            base_hour = 6  # Start at 6 AM
            
            for seq, code in enumerate(route_codes, 1):
                if code in station_map:
                    station = station_map[code]
                    
                    # Calculate timing
                    arrival_hour = (base_hour + seq * 2) % 24
                    departure_hour = (arrival_hour + 0.25) % 24  # 15 min stop
                    
                    arrival_time = time(int(arrival_hour), int((arrival_hour % 1) * 60))
                    departure_time = time(int(departure_hour), int((departure_hour % 1) * 60))
                    
                    route = TrainRoute(
                        train_id=train.id,
                        station_id=station.id,
                        sequence=seq,
                        arrival_time=arrival_time,
                        departure_time=departure_time,
                        distance_from_start=seq * 150  # 150km between stations
                    )
                    self.db.session.add(route)
                    count += 1
        
        self.db.session.commit()
        logger.info(f"✅ Created {count} route entries")
    
    def create_users(self):
        """Create user accounts"""
        logger.info("👥 Setting up user accounts...")
        
        users = [
            ("admin", "admin@railserve.com", "admin123", "admin"),
            ("testuser", "test@railserve.com", "test123", "user"),
            ("rajesh", "rajesh@email.com", "password123", "user"),
            ("priya", "priya@email.com", "password123", "user"),
            ("amit", "amit@email.com", "password123", "user")
        ]
        
        count = 0
        for username, email, password, role in users:
            if not User.query.filter_by(username=username).first():
                user = User(
                    username=username,
                    email=email,
                    password_hash=generate_password_hash(password),
                    role=role,
                    active=True
                )
                self.db.session.add(user)
                count += 1
        
        self.db.session.commit()
        logger.info(f"✅ Created {count} user accounts")

def main():
    """Main setup function"""
    print("🚅 RailServe Database Setup")
    print("=" * 40)
    
    setup = RailwayDatabaseSetup()
    setup.setup_database()
    
    print("\n✅ Setup completed successfully!")
    print("\nDefault accounts:")
    print("- Admin: admin / admin123")
    print("- Test User: testuser / test123")
    print("\n🌐 Start the application with: python main.py")

if __name__ == "__main__":
    main()