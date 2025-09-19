#!/usr/bin/env python3
"""
RailServe Railway Reservation System - Complete Database Setup
==============================================================

This script sets up the complete RailServe database with all tables and relationships.
It uses the Replit environment variables and creates all necessary schema.

Features:
- Creates all database tables using SQLAlchemy models
- Populates basic reference data (stations, trains, tatkal slots)
- Creates admin user account
- Configures for Replit environment

Usage:
    python setup_database.py

Environment Variables (configured automatically for Replit):
    DATABASE_URL - PostgreSQL connection string from Replit
    SESSION_SECRET - Flask session secret
"""

import os
import sys
import random
import logging
from datetime import datetime, time, date, timedelta
from typing import List, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the src directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

try:
    # Import required packages
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from werkzeug.security import generate_password_hash
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except ImportError as e:
    print(f"❌ Required dependencies not found: {e}")
    print("Please install: pip install sqlalchemy psycopg2-binary werkzeug flask flask-sqlalchemy flask-login")
    sys.exit(1)

class RailServeSetup:
    """Complete RailServe database setup for Replit environment"""
    
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        if not self.database_url:
            logger.error("❌ DATABASE_URL environment variable not found")
            logger.info("Please create a Replit database and ensure DATABASE_URL is set")
            sys.exit(1)
        
        # Ensure database_url is a string
        if self.database_url is None:
            raise ValueError("DATABASE_URL cannot be None")
        
        self.engine = None
        self.Session = None
        
        # Set session secret if not already set
        if not os.environ.get('SESSION_SECRET'):
            os.environ['SESSION_SECRET'] = 'railserve-production-secret-key-2025'
    
    def connect_database(self) -> bool:
        """Connect to the Replit PostgreSQL database"""
        try:
            logger.info("🔌 Connecting to Replit PostgreSQL database...")
            self.engine = create_engine(self.database_url)
            self.Session = sessionmaker(bind=self.engine)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("✅ Database connection successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            logger.info("Please ensure your Replit database is running and DATABASE_URL is correct")
            return False
    
    def create_tables(self) -> bool:
        """Create all database tables using SQLAlchemy models"""
        try:
            logger.info("🏗️  Creating database tables...")
            
            # Import Flask app to trigger table creation
            from src.app import app, db
            
            with app.app_context():
                # Drop all tables first (clean slate)
                logger.info("🗑️  Dropping existing tables...")
                db.drop_all()
                
                # Create all tables
                logger.info("📋 Creating all tables...")
                db.create_all()
                
                # Verify tables were created
                with db.engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT table_name FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                        ORDER BY table_name
                    """))
                    tables = [row[0] for row in result.fetchall()]
                    logger.info(f"✅ Created {len(tables)} tables: {', '.join(tables)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Table creation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def populate_basic_data(self) -> bool:
        """Populate basic reference data"""
        try:
            logger.info("📊 Populating basic reference data...")
            
            from src.app import app, db
            from src.models import User, Station, Train, TatkalTimeSlot
            
            with app.app_context():
                # Create admin user
                admin_user = User.query.filter_by(username='admin').first()
                if not admin_user:
                    admin_user = User(
                        username='admin',
                        email='admin@railserve.com',
                        password_hash=generate_password_hash('admin123'),
                        role='super_admin',
                        active=True
                    )
                    db.session.add(admin_user)
                    logger.info("👤 Created admin user (username: admin, password: admin123)")
                
                # Create sample stations
                if Station.query.count() == 0:
                    stations = [
                        {'code': 'NDLS', 'name': 'New Delhi', 'city': 'Delhi', 'state': 'Delhi'},
                        {'code': 'CST', 'name': 'Chhatrapati Shivaji Terminus', 'city': 'Mumbai', 'state': 'Maharashtra'},
                        {'code': 'HWH', 'name': 'Howrah Junction', 'city': 'Kolkata', 'state': 'West Bengal'},
                        {'code': 'MAS', 'name': 'Chennai Central', 'city': 'Chennai', 'state': 'Tamil Nadu'},
                        {'code': 'SBC', 'name': 'Bangalore City', 'city': 'Bangalore', 'state': 'Karnataka'},
                        {'code': 'PUNE', 'name': 'Pune Junction', 'city': 'Pune', 'state': 'Maharashtra'},
                        {'code': 'AMD', 'name': 'Ahmedabad Junction', 'city': 'Ahmedabad', 'state': 'Gujarat'},
                        {'code': 'JP', 'name': 'Jaipur Junction', 'city': 'Jaipur', 'state': 'Rajasthan'},
                        {'code': 'AGC', 'name': 'Agra Cantt', 'city': 'Agra', 'state': 'Uttar Pradesh'},
                        {'code': 'LKO', 'name': 'Lucknow', 'city': 'Lucknow', 'state': 'Uttar Pradesh'}
                    ]
                    
                    for station_data in stations:
                        station = Station(**station_data)
                        db.session.add(station)
                    
                    logger.info(f"🚉 Created {len(stations)} stations")
                
                # Create sample trains
                if Train.query.count() == 0:
                    trains = [
                        {'number': '12951', 'name': 'Mumbai Rajdhani Express', 'total_seats': 350, 'available_seats': 350, 'fare_per_km': 2.5, 'tatkal_seats': 35, 'tatkal_fare_per_km': 3.5},
                        {'number': '12301', 'name': 'Howrah Rajdhani Express', 'total_seats': 400, 'available_seats': 400, 'fare_per_km': 2.8, 'tatkal_seats': 40, 'tatkal_fare_per_km': 3.8},
                        {'number': '12009', 'name': 'Shatabdi Express', 'total_seats': 280, 'available_seats': 280, 'fare_per_km': 2.2, 'tatkal_seats': 28, 'tatkal_fare_per_km': 3.2},
                        {'number': '22691', 'name': 'Rajdhani Express', 'total_seats': 320, 'available_seats': 320, 'fare_per_km': 2.6, 'tatkal_seats': 32, 'tatkal_fare_per_km': 3.6},
                        {'number': '12423', 'name': 'Dibrugarh Rajdhani Express', 'total_seats': 380, 'available_seats': 380, 'fare_per_km': 2.7, 'tatkal_seats': 38, 'tatkal_fare_per_km': 3.7}
                    ]
                    
                    for train_data in trains:
                        train = Train(**train_data)
                        db.session.add(train)
                    
                    logger.info(f"🚂 Created {len(trains)} trains")
                
                # Create Tatkal time slots
                if TatkalTimeSlot.query.count() == 0:
                    tatkal_slots = [
                        {
                            'name': 'AC Classes Tatkal',
                            'coach_classes': 'AC1,AC2,AC3,CC',
                            'open_time': time(10, 0),  # 10:00 AM
                            'days_before_journey': 1,
                            'active': True,
                            'created_by': admin_user.id
                        },
                        {
                            'name': 'Non-AC Classes Tatkal',
                            'coach_classes': 'SL,2S',
                            'open_time': time(11, 0),  # 11:00 AM
                            'days_before_journey': 1,
                            'active': True,
                            'created_by': admin_user.id
                        }
                    ]
                    
                    for slot_data in tatkal_slots:
                        slot = TatkalTimeSlot(**slot_data)
                        db.session.add(slot)
                    
                    logger.info(f"⏰ Created {len(tatkal_slots)} Tatkal time slots")
                
                # Commit all changes
                db.session.commit()
                logger.info("✅ Basic reference data populated successfully")
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Data population failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify_setup(self) -> bool:
        """Verify the database setup is complete"""
        try:
            logger.info("🔍 Verifying database setup...")
            
            from src.app import app, db
            from src.models import User, Station, Train, TatkalTimeSlot
            
            with app.app_context():
                # Check tables exist and have data
                user_count = User.query.count()
                station_count = Station.query.count()
                train_count = Train.query.count()
                tatkal_count = TatkalTimeSlot.query.count()
                
                logger.info(f"📊 Database verification:")
                logger.info(f"   Users: {user_count}")
                logger.info(f"   Stations: {station_count}")
                logger.info(f"   Trains: {train_count}")
                logger.info(f"   Tatkal Slots: {tatkal_count}")
                
                # Check admin user exists
                admin_user = User.query.filter_by(username='admin').first()
                if admin_user and admin_user.role == 'super_admin':
                    logger.info("✅ Admin user verified")
                else:
                    logger.warning("⚠️  Admin user not found or incorrect role")
                
                return user_count > 0 and station_count > 0 and train_count > 0
                
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return False
    
    def run_setup(self) -> bool:
        """Run the complete database setup"""
        logger.info("🚀 Starting RailServe database setup...")
        
        # Step 1: Connect to database
        if not self.connect_database():
            return False
        
        # Step 2: Create tables
        if not self.create_tables():
            return False
        
        # Step 3: Populate basic data
        if not self.populate_basic_data():
            return False
        
        # Step 4: Verify setup
        if not self.verify_setup():
            return False
        
        logger.info("🎉 RailServe database setup completed successfully!")
        logger.info("📝 Next steps:")
        logger.info("   1. Start your Flask application: python init_app.py")
        logger.info("   2. Login as admin (username: admin, password: admin123)")
        logger.info("   3. Configure additional settings in the admin panel")
        
        return True

def main():
    """Main function to run the setup"""
    setup = RailServeSetup()
    
    try:
        success = setup.run_setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Setup failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()