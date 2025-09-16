#!/usr/bin/env python3
"""
Standalone Database Population Script for RailServe
This script can be run outside of Replit to populate the database with initial data.

Usage:
    python scripts/populate_db.py --help
    python scripts/populate_db.py --reset --stations --trains 100 --create-admin
    
Environment Variables Required:
    DATABASE_URL - PostgreSQL connection string
    SESSION_SECRET - Secret key for sessions (for app validation)
"""

import os
import sys
import argparse
import random
import csv
import logging
from datetime import datetime, time, date
from typing import List, Dict, Any

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Import SQLAlchemy directly
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker, Session
    from sqlalchemy.exc import IntegrityError
    from werkzeug.security import generate_password_hash
except ImportError as e:
    print(f"Required dependencies not found: {e}")
    print("Please install: pip install sqlalchemy psycopg2-binary werkzeug")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabasePopulator:
    """Standalone database population tool"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def verify_connection(self) -> bool:
        """Verify database connection"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def reset_data(self) -> bool:
        """Clear existing data (destructive operation)"""
        try:
            with self.Session() as session:
                # Delete in correct order to respect foreign key constraints
                logger.info("🗑️  Clearing existing data...")
                session.execute(text("DELETE FROM waitlist"))
                session.execute(text("DELETE FROM payment"))
                session.execute(text("DELETE FROM booking"))
                session.execute(text("DELETE FROM train_route"))
                session.execute(text("DELETE FROM train"))
                session.execute(text("DELETE FROM station"))
                session.execute(text("DELETE FROM \"user\" WHERE role != 'super_admin'"))  # Keep super admins
                session.commit()
                logger.info("✅ Data cleared successfully")
                return True
        except Exception as e:
            logger.error(f"❌ Data clearing failed: {e}")
            return False
    
    def populate_stations(self) -> bool:
        """Populate stations with comprehensive Indian railway network"""
        stations_data = [
            # Major Metropolitan Cities
            {'code': 'NDLS', 'name': 'New Delhi', 'city': 'Delhi', 'state': 'Delhi'},
            {'code': 'CST', 'name': 'Chhatrapati Shivaji Terminus', 'city': 'Mumbai', 'state': 'Maharashtra'},
            {'code': 'HWH', 'name': 'Howrah Junction', 'city': 'Kolkata', 'state': 'West Bengal'},
            {'code': 'MAS', 'name': 'Chennai Central', 'city': 'Chennai', 'state': 'Tamil Nadu'},
            {'code': 'SBC', 'name': 'Bangalore City', 'city': 'Bangalore', 'state': 'Karnataka'},
            {'code': 'PUNE', 'name': 'Pune Junction', 'city': 'Pune', 'state': 'Maharashtra'},
            {'code': 'AMD', 'name': 'Ahmedabad Junction', 'city': 'Ahmedabad', 'state': 'Gujarat'},
            {'code': 'JP', 'name': 'Jaipur Junction', 'city': 'Jaipur', 'state': 'Rajasthan'},
            
            # Major Junction Cities
            {'code': 'AGC', 'name': 'Agra Cantt', 'city': 'Agra', 'state': 'Uttar Pradesh'},
            {'code': 'ALLP', 'name': 'Allahabad Junction', 'city': 'Allahabad', 'state': 'Uttar Pradesh'},
            {'code': 'BCT', 'name': 'Mumbai Central', 'city': 'Mumbai', 'state': 'Maharashtra'},
            {'code': 'BZA', 'name': 'Vijayawada Junction', 'city': 'Vijayawada', 'state': 'Andhra Pradesh'},
            {'code': 'CNB', 'name': 'Kanpur Central', 'city': 'Kanpur', 'state': 'Uttar Pradesh'},
            {'code': 'GWL', 'name': 'Gwalior Junction', 'city': 'Gwalior', 'state': 'Madhya Pradesh'},
            {'code': 'JBP', 'name': 'Jabalpur Junction', 'city': 'Jabalpur', 'state': 'Madhya Pradesh'},
            {'code': 'VSKP', 'name': 'Visakhapatnam Junction', 'city': 'Visakhapatnam', 'state': 'Andhra Pradesh'},
            
            # Tourist and Heritage Cities
            {'code': 'UDZ', 'name': 'Udaipur City', 'city': 'Udaipur', 'state': 'Rajasthan'},
            {'code': 'JU', 'name': 'Jodhpur Junction', 'city': 'Jodhpur', 'state': 'Rajasthan'},
            {'code': 'BKN', 'name': 'Bikaner Junction', 'city': 'Bikaner', 'state': 'Rajasthan'},
            {'code': 'KOAA', 'name': 'Kochuveli', 'city': 'Thiruvananthapuram', 'state': 'Kerala'},
            {'code': 'ERS', 'name': 'Ernakulam Junction', 'city': 'Kochi', 'state': 'Kerala'},
            {'code': 'CLT', 'name': 'Kozhikode', 'city': 'Kozhikode', 'state': 'Kerala'},
            {'code': 'MDU', 'name': 'Madurai Junction', 'city': 'Madurai', 'state': 'Tamil Nadu'},
            {'code': 'CBE', 'name': 'Coimbatore Junction', 'city': 'Coimbatore', 'state': 'Tamil Nadu'},
            
            # Industrial Cities
            {'code': 'RJPB', 'name': 'Rjndr Ngr Bihar', 'city': 'Patna', 'state': 'Bihar'},
            {'code': 'PNBE', 'name': 'Patna Junction', 'city': 'Patna', 'state': 'Bihar'},
            {'code': 'RNC', 'name': 'Ranchi Junction', 'city': 'Ranchi', 'state': 'Jharkhand'},
            {'code': 'TATA', 'name': 'Tatanagar Junction', 'city': 'Jamshedpur', 'state': 'Jharkhand'},
            {'code': 'BSB', 'name': 'Varanasi Junction', 'city': 'Varanasi', 'state': 'Uttar Pradesh'},
            {'code': 'GKP', 'name': 'Gorakhpur Junction', 'city': 'Gorakhpur', 'state': 'Uttar Pradesh'},
            
            # Additional Important Stations
            {'code': 'LKO', 'name': 'Lucknow Junction', 'city': 'Lucknow', 'state': 'Uttar Pradesh'},
            {'code': 'MB', 'name': 'Moradabad Junction', 'city': 'Moradabad', 'state': 'Uttar Pradesh'},
            {'code': 'BE', 'name': 'Bareilly Junction', 'city': 'Bareilly', 'state': 'Uttar Pradesh'},
            {'code': 'RTM', 'name': 'Ratlam Junction', 'city': 'Ratlam', 'state': 'Madhya Pradesh'},
            {'code': 'INDB', 'name': 'Indore Junction', 'city': 'Indore', 'state': 'Madhya Pradesh'},
            {'code': 'BPL', 'name': 'Bhopal Junction', 'city': 'Bhopal', 'state': 'Madhya Pradesh'},
            {'code': 'NGP', 'name': 'Nagpur Junction', 'city': 'Nagpur', 'state': 'Maharashtra'},
        ]
        
        try:
            with self.Session() as session:
                logger.info("🚉 Populating stations...")
                created_count = 0
                
                for station_data in stations_data:
                    # Use upsert logic to handle duplicates
                    result = session.execute(text("""
                        INSERT INTO station (code, name, city, state, active) 
                        VALUES (:code, :name, :city, :state, true)
                        ON CONFLICT (code) DO UPDATE SET 
                            name = EXCLUDED.name,
                            city = EXCLUDED.city,
                            state = EXCLUDED.state,
                            active = true
                        RETURNING id
                    """), station_data)
                    
                    if result.rowcount > 0:
                        created_count += 1
                
                session.commit()
                logger.info(f"✅ Stations populated successfully: {created_count} stations")
                return True
                
        except Exception as e:
            logger.error(f"❌ Station population failed: {e}")
            return False
    
    def populate_trains(self, count: int = 50) -> bool:
        """Populate trains with realistic details"""
        train_types = [
            ('Rajdhani Express', 'RAJ', 18.00, 100, 15.00, 20),
            ('Shatabdi Express', 'SHTB', 16.00, 80, 14.00, 15),
            ('Duronto Express', 'DRN', 17.00, 90, 15.50, 18),
            ('Superfast Express', 'SF', 12.00, 120, 10.50, 25),
            ('Mail Express', 'MAIL', 10.00, 150, 8.50, 30),
            ('Passenger', 'PASS', 6.00, 200, 5.00, 40),
            ('Jan Shatabdi', 'JSHT', 8.00, 100, 7.00, 20),
            ('Garib Rath', 'GR', 9.00, 180, 8.00, 35),
            ('Humsafar Express', 'HMS', 13.00, 110, 11.50, 22),
            ('Tejas Express', 'TEJ', 15.00, 85, 13.50, 17),
            ('Vande Bharat Express', 'VB', 20.00, 70, 18.00, 14),
        ]
        
        try:
            with self.Session() as session:
                logger.info(f"🚄 Populating {count} trains...")
                created_count = 0
                train_number = 12001
                
                for i in range(count):
                    train_type, type_code, fare_per_km, total_seats, tatkal_fare, tatkal_seats = random.choice(train_types)
                    
                    # Generate train name with route info
                    train_name = f"{train_type} {train_number}"
                    
                    try:
                        result = session.execute(text("""
                            INSERT INTO train (number, name, total_seats, available_seats, fare_per_km, 
                                             tatkal_seats, tatkal_fare_per_km, active) 
                            VALUES (:number, :name, :total_seats, :available_seats, :fare_per_km,
                                   :tatkal_seats, :tatkal_fare_per_km, true)
                            ON CONFLICT (number) DO NOTHING
                            RETURNING id
                        """), {
                            'number': str(train_number),
                            'name': train_name,
                            'total_seats': total_seats,
                            'available_seats': total_seats,
                            'fare_per_km': fare_per_km,
                            'tatkal_seats': tatkal_seats,
                            'tatkal_fare_per_km': tatkal_fare
                        })
                        
                        if result.rowcount > 0:
                            created_count += 1
                            
                    except IntegrityError:
                        # Skip duplicate train numbers
                        session.rollback()
                        session.begin()
                    
                    train_number += 1
                    if train_number > 99999:
                        train_number = 10001  # Reset to avoid very large numbers
                
                session.commit()
                logger.info(f"✅ Trains populated successfully: {created_count} trains")
                return True
                
        except Exception as e:
            logger.error(f"❌ Train population failed: {e}")
            return False
    
    def create_admin_user(self, username: str = "admin", password: str = "admin123") -> bool:
        """Create admin user for system access"""
        try:
            with self.Session() as session:
                logger.info(f"👤 Creating admin user: {username}")
                
                # Check if user already exists
                result = session.execute(text("SELECT id FROM \"user\" WHERE username = :username"), 
                                       {'username': username})
                
                if result.fetchone():
                    logger.info(f"ℹ️  Admin user '{username}' already exists")
                    return True
                
                password_hash = generate_password_hash(password)
                
                session.execute(text("""
                    INSERT INTO \"user\" (username, email, password_hash, role, active) 
                    VALUES (:username, :email, :password_hash, 'super_admin', true)
                """), {
                    'username': username,
                    'email': f"{username}@railserve.com",
                    'password_hash': password_hash
                })
                
                session.commit()
                logger.info(f"✅ Admin user created successfully: {username}")
                logger.info(f"🔐 Login credentials: {username} / {password}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Admin user creation failed: {e}")
            return False
    
    def create_test_users(self, count: int = 5) -> bool:
        """Create test users for development"""
        try:
            with self.Session() as session:
                logger.info(f"👥 Creating {count} test users...")
                created_count = 0
                
                for i in range(count):
                    username = f"user{i+1}"
                    email = f"user{i+1}@example.com"
                    password_hash = generate_password_hash("test123")
                    
                    try:
                        session.execute(text("""
                            INSERT INTO \"user\" (username, email, password_hash, role, active) 
                            VALUES (:username, :email, :password_hash, 'user', true)
                            ON CONFLICT (username) DO NOTHING
                        """), {
                            'username': username,
                            'email': email,
                            'password_hash': password_hash
                        })
                        created_count += 1
                    except IntegrityError:
                        # Skip duplicates
                        session.rollback()
                        session.begin()
                
                session.commit()
                logger.info(f"✅ Test users created: {created_count} users (Password: test123)")
                return True
                
        except Exception as e:
            logger.error(f"❌ Test user creation failed: {e}")
            return False

def validate_environment() -> str:
    """Validate required environment variables"""
    database_url = os.environ.get('DATABASE_URL')
    session_secret = os.environ.get('SESSION_SECRET')
    
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable is required")
        logger.info("Example: export DATABASE_URL='postgresql://user:pass@localhost/dbname'")
        sys.exit(1)
    
    if not session_secret:
        logger.error("❌ SESSION_SECRET environment variable is required")
        logger.info("Example: export SESSION_SECRET='your-secret-key-here'")
        sys.exit(1)
    
    return database_url

def main():
    """Main function with CLI argument parsing"""
    parser = argparse.ArgumentParser(description='RailServe Database Population Tool')
    parser.add_argument('--reset', action='store_true', 
                       help='Clear existing data (DESTRUCTIVE)')
    parser.add_argument('--stations', action='store_true', 
                       help='Populate stations')
    parser.add_argument('--trains', type=int, metavar='COUNT', 
                       help='Populate trains (specify count, default: 50)')
    parser.add_argument('--create-admin', action='store_true', 
                       help='Create admin user (admin/admin123)')
    parser.add_argument('--test-users', type=int, metavar='COUNT', 
                       help='Create test users (specify count, default: 5)')
    parser.add_argument('--all', action='store_true', 
                       help='Populate all data (equivalent to --stations --trains 100 --create-admin --test-users 5)')
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # Handle --all flag
    if args.all:
        args.stations = True
        args.trains = args.trains or 100
        args.create_admin = True
        args.test_users = args.test_users or 5
    
    # Validate environment
    database_url = validate_environment()
    
    # Initialize populator
    populator = DatabasePopulator(database_url)
    
    if not populator.verify_connection():
        sys.exit(1)
    
    logger.info("🚀 Starting database population...")
    success = True
    
    # Reset data if requested
    if args.reset:
        if not populator.reset_data():
            success = False
    
    # Populate stations
    if args.stations:
        if not populator.populate_stations():
            success = False
    
    # Populate trains
    if args.trains:
        train_count = args.trains if isinstance(args.trains, int) else 50
        if not populator.populate_trains(train_count):
            success = False
    
    # Create admin user
    if args.create_admin:
        if not populator.create_admin_user():
            success = False
    
    # Create test users
    if args.test_users:
        user_count = args.test_users if isinstance(args.test_users, int) else 5
        if not populator.create_test_users(user_count):
            success = False
    
    if success:
        logger.info("🎉 Database population completed successfully!")
    else:
        logger.error("💥 Database population completed with errors!")
        sys.exit(1)

if __name__ == '__main__':
    main()