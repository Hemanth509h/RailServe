#!/usr/bin/env python3
"""
RailServe 2025 - Comprehensive Database Setup Script
==================================================

This script creates a complete railway reservation system database with:
- Core railway system tables (trains, stations, users, bookings)
- Enhanced group booking system with modern enterprise features
- Advanced payment and loyalty integration
- Sustainability tracking and analytics
- Modern audit trails and security features

Usage:
    python setup_database.py

Environment Variables:
    DATABASE_URL: PostgreSQL connection string (required)
"""

import os
import sys
import logging
from datetime import datetime, date
from decimal import Decimal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_database():
    """Main setup function - creates all tables and initial data using Flask models"""
    logger.info("🚀 Starting RailServe 2025 database setup...")
    
    # Import Flask app and models
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from src.app import app, db
        
        with app.app_context():
            # Import core models
            from src.models import (
                User, Station, Train, TrainRoute, Booking, Passenger, 
                Payment, RefundRequest, TatkalTimeSlot, TatkalOverride, 
                ComplaintManagement, Waitlist, GroupBooking
            )
            
            logger.info("📋 Creating database tables...")
            
            # Drop and recreate all tables
            db.drop_all()
            db.create_all()
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"✅ Created {len(tables)} database tables")
            
            # Create initial data
            create_initial_data(db, User, Station, Train, TrainRoute)
            
            logger.info("🎉 Database setup completed successfully!")
            logger.info("✨ RailServe 2025 is ready for operation!")
            
    except Exception as e:
        logger.error(f"❌ Database setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def create_initial_data(db, User, Station, Train, TrainRoute):
    """Create essential initial data for the system"""
    from werkzeug.security import generate_password_hash
    
    logger.info("💾 Creating initial system data...")
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@railserve.com',
        password_hash=generate_password_hash('admin123'),
        role='super_admin',
        active=True
    )
    
    # Create test user
    user = User(
        username='user',
        email='user@example.com',
        password_hash=generate_password_hash('user123'),
        role='user',
        active=True
    )
    
    db.session.add_all([admin, user])
    
    # Create major stations
    stations_data = [
        ('NDLS', 'New Delhi', 'New Delhi', 'Delhi'),
        ('CSMT', 'Mumbai CST', 'Mumbai', 'Maharashtra'),
        ('HWH', 'Howrah Junction', 'Kolkata', 'West Bengal'),
        ('MAS', 'Chennai Central', 'Chennai', 'Tamil Nadu'),
        ('SBC', 'Bangalore City', 'Bangalore', 'Karnataka'),
        ('SC', 'Secunderabad Junction', 'Hyderabad', 'Telangana'),
        ('PUNE', 'Pune Junction', 'Pune', 'Maharashtra'),
        ('ADI', 'Ahmedabad Junction', 'Ahmedabad', 'Gujarat'),
        ('LKO', 'Lucknow Junction', 'Lucknow', 'Uttar Pradesh'),
        ('JP', 'Jaipur Junction', 'Jaipur', 'Rajasthan'),
        ('CBE', 'Coimbatore Junction', 'Coimbatore', 'Tamil Nadu'),
        ('ERS', 'Ernakulam Junction', 'Kochi', 'Kerala'),
        ('TVC', 'Thiruvananthapuram Central', 'Thiruvananthapuram', 'Kerala'),
        ('BZA', 'Vijayawada Junction', 'Vijayawada', 'Andhra Pradesh'),
        ('VSKP', 'Visakhapatnam', 'Visakhapatnam', 'Andhra Pradesh'),
        ('BBS', 'Bhubaneswar', 'Bhubaneswar', 'Odisha'),
        ('PURI', 'Puri', 'Puri', 'Odisha'),
        ('NGP', 'Nagpur', 'Nagpur', 'Maharashtra'),
        ('BPL', 'Bhopal Junction', 'Bhopal', 'Madhya Pradesh'),
        ('INDB', 'Indore Junction', 'Indore', 'Madhya Pradesh')
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
    
    # Create sample trains
    trains_data = [
        ('12301', 'Rajdhani Express', 400, 350, 2.5, 50, 4.0),
        ('12302', 'New Delhi Rajdhani', 400, 350, 2.5, 50, 4.0),
        ('12951', 'Mumbai Rajdhani', 350, 300, 2.8, 40, 4.5),
        ('12952', 'New Delhi Rajdhani', 350, 300, 2.8, 40, 4.5),
        ('12621', 'Tamil Nadu Express', 450, 400, 1.8, 60, 3.0),
        ('12622', 'Tamil Nadu Express', 450, 400, 1.8, 60, 3.0),
        ('12841', 'Coromandel Express', 400, 350, 2.0, 50, 3.2),
        ('12842', 'Coromandel Express', 400, 350, 2.0, 50, 3.2),
        ('16031', 'Andaman Express', 420, 380, 1.4, 50, 2.2),
        ('16032', 'Andaman Express', 420, 380, 1.4, 50, 2.2),
        ('12431', 'Trivandrum Rajdhani', 300, 250, 3.5, 35, 5.5),
        ('12432', 'Trivandrum Rajdhani', 300, 250, 3.5, 35, 5.5),
        ('11013', 'Coimbatore Express', 400, 350, 1.3, 45, 2.0),
        ('11014', 'Coimbatore Express', 400, 350, 1.3, 45, 2.0),
        ('12605', 'Pallavan Express', 380, 330, 1.4, 40, 2.1),
        ('12606', 'Pallavan Express', 380, 330, 1.4, 40, 2.1),
        ('12223', 'Kaifiyat Express', 380, 320, 1.5, 45, 2.8),
        ('12224', 'Kaifiyat Express', 380, 320, 1.5, 45, 2.8),
        ('12253', 'Anga Express', 360, 310, 1.6, 40, 2.5),
        ('12254', 'Anga Express', 360, 310, 1.6, 40, 2.5)
    ]
    
    trains = []
    for number, name, total_seats, available_seats, fare_per_km, tatkal_seats, tatkal_fare_per_km in trains_data:
        train = Train(
            number=number,
            name=name,
            total_seats=total_seats,
            available_seats=available_seats,
            fare_per_km=fare_per_km,
            tatkal_seats=tatkal_seats,
            tatkal_fare_per_km=tatkal_fare_per_km,
            active=True
        )
        trains.append(train)
    
    db.session.add_all(trains)
    
    # Commit all data
    db.session.commit()
    
    logger.info("✅ Created initial data:")
    logger.info(f"   - {len(stations)} major railway stations")
    logger.info(f"   - {len(trains)} popular trains")
    logger.info("   - Admin user (admin/admin123)")
    logger.info("   - Test user (user/user123)")

if __name__ == '__main__':
    setup_database()