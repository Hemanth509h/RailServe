#!/usr/bin/env python3
"""
RailServe 2025 - Database Setup Script
=======================================

This script performs a complete database reset and setup:
1. Drops all existing tables (clean slate)
2. Creates all required tables from models
3. Populates initial data (stations, trains, users)
4. Verifies all tables and relationships

Usage:
    python setup_database.py

Environment Variables:
    DATABASE_URL: Database connection string (PostgreSQL or SQLite)
"""

import os
import sys
import logging
from datetime import datetime, time, timedelta, date
from decimal import Decimal
import random
import string

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def drop_all_tables(db, engine):
    """Drop all existing tables using reflection"""
    logger.info("🗑️  Dropping all existing tables...")
    
    try:
        from sqlalchemy import MetaData, inspect
        
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if existing_tables:
            logger.info(f"   Found {len(existing_tables)} existing tables: {', '.join(existing_tables)}")
            
            metadata = MetaData()
            metadata.reflect(bind=engine)
            metadata.drop_all(bind=engine)
            
            logger.info("✅ Successfully dropped all existing tables")
        else:
            logger.info("   No existing tables found - fresh database")
            
    except Exception as e:
        logger.warning(f"   Note: {str(e)}")
        logger.info("   Continuing with db.drop_all()...")
        db.drop_all()

def create_all_tables(db):
    """Create all tables defined in models"""
    logger.info("📋 Creating all database tables from models...")
    
    db.create_all()
    
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    logger.info(f"✅ Created {len(tables)} tables:")
    
    for i, table in enumerate(sorted(tables), 1):
        logger.info(f"   {i:2d}. {table}")
    
    return tables

def create_initial_stations(db, Station):
    """Create major railway stations across India"""
    logger.info("🚉 Creating railway stations...")
    
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
        ('INDB', 'Indore Junction', 'Indore', 'Madhya Pradesh'),
        ('GHY', 'Guwahati', 'Guwahati', 'Assam'),
        ('PAT', 'Patna Junction', 'Patna', 'Bihar'),
        ('ALD', 'Allahabad Junction', 'Prayagraj', 'Uttar Pradesh'),
        ('AGC', 'Agra Cantt', 'Agra', 'Uttar Pradesh'),
        ('JAT', 'Jammu Tawi', 'Jammu', 'Jammu & Kashmir')
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
    
    logger.info(f"✅ Created {len(stations)} railway stations")
    return stations

def create_initial_trains(db, Train):
    """Create sample trains with realistic data"""
    logger.info("🚂 Creating trains...")
    
    trains_data = [
        ('12301', 'Rajdhani Express', 400, 400, 2.5, 50, 4.0),
        ('12302', 'New Delhi Rajdhani', 400, 400, 2.5, 50, 4.0),
        ('12951', 'Mumbai Rajdhani', 350, 350, 2.8, 40, 4.5),
        ('12952', 'New Delhi Rajdhani', 350, 350, 2.8, 40, 4.5),
        ('12621', 'Tamil Nadu Express', 450, 450, 1.8, 60, 3.0),
        ('12622', 'Tamil Nadu Express', 450, 450, 1.8, 60, 3.0),
        ('12841', 'Coromandel Express', 400, 400, 2.0, 50, 3.2),
        ('12842', 'Coromandel Express', 400, 400, 2.0, 50, 3.2),
        ('16031', 'Andaman Express', 420, 420, 1.4, 50, 2.2),
        ('16032', 'Andaman Express', 420, 420, 1.4, 50, 2.2),
        ('12431', 'Trivandrum Rajdhani', 300, 300, 3.5, 35, 5.5),
        ('12432', 'Trivandrum Rajdhani', 300, 300, 3.5, 35, 5.5),
        ('11013', 'Coimbatore Express', 400, 400, 1.3, 45, 2.0),
        ('11014', 'Coimbatore Express', 400, 400, 1.3, 45, 2.0),
        ('12605', 'Pallavan Express', 380, 380, 1.4, 40, 2.1),
        ('12606', 'Pallavan Express', 380, 380, 1.4, 40, 2.1),
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
    db.session.commit()
    
    logger.info(f"✅ Created {len(trains)} trains")
    return trains

def create_train_routes(db, TrainRoute, Train, trains, stations):
    """Create realistic train routes"""
    logger.info("🛤️  Creating train routes...")
    
    station_map = {s.code: s for s in stations}
    train_map = {t.number: t for t in trains}
    
    routes_data = [
        {
            'train_number': '12301',
            'route': [
                ('NDLS', 0, None, time(16, 50), 0),
                ('AGC', 1, time(19, 30), time(19, 35), 195),
                ('BPL', 2, time(23, 55), time(0, 5), 705),
                ('NGP', 3, time(6, 15), time(6, 25), 1089),
                ('BZA', 4, time(16, 40), time(16, 50), 1589),
                ('MAS', 5, time(20, 45), None, 1759)
            ]
        },
        {
            'train_number': '12302',
            'route': [
                ('MAS', 0, None, time(23, 0), 0),
                ('BZA', 1, time(4, 15), time(4, 25), 170),
                ('NGP', 2, time(14, 40), time(14, 50), 670),
                ('BPL', 3, time(21, 0), time(21, 10), 1054),
                ('AGC', 4, time(1, 30), time(1, 35), 1564),
                ('NDLS', 5, time(4, 15), None, 1759)
            ]
        },
        {
            'train_number': '12621',
            'route': [
                ('NDLS', 0, None, time(22, 30), 0),
                ('AGC', 1, time(1, 15), time(1, 20), 195),
                ('BPL', 2, time(6, 0), time(6, 10), 705),
                ('NGP', 3, time(11, 40), time(11, 50), 1089),
                ('BZA', 4, time(20, 50), time(21, 0), 1589),
                ('MAS', 5, time(1, 15), None, 1759)
            ]
        },
    ]
    
    routes_created = 0
    for route_data in routes_data:
        train = train_map.get(route_data['train_number'])
        if train:
            for station_code, seq, arr, dep, dist in route_data['route']:
                if station_code in station_map:
                    route = TrainRoute(
                        train_id=train.id,
                        station_id=station_map[station_code].id,
                        sequence=seq,
                        arrival_time=arr,
                        departure_time=dep,
                        distance_from_start=dist
                    )
                    db.session.add(route)
                    routes_created += 1
    
    db.session.commit()
    logger.info(f"✅ Created {routes_created} train route entries")

def create_admin_users(db, User):
    """Create admin and test users"""
    from werkzeug.security import generate_password_hash
    
    logger.info("👥 Creating admin users...")
    
    users = []
    
    admin = User(
        username='admin',
        email='admin@railserve.com',
        password_hash=generate_password_hash('admin123'),
        role='super_admin',
        active=True
    )
    users.append(admin)
    
    test_user = User(
        username='testuser',
        email='user@example.com',
        password_hash=generate_password_hash('user123'),
        role='user',
        active=True
    )
    users.append(test_user)
    
    db.session.add_all(users)
    db.session.commit()
    
    logger.info(f"✅ Created {len(users)} users")
    logger.info("   - Admin: admin / admin123")
    logger.info("   - Test User: testuser / user123")
    
    return users

def verify_database_setup(db):
    """Verify the database setup is correct"""
    logger.info("🔍 Verifying database setup...")
    
    from src.models import User, Station, Train, TrainRoute
    
    checks = [
        ("Users", User.query.count(), 2),
        ("Stations", Station.query.count(), 25),
        ("Trains", Train.query.count(), 16),
        ("Train Routes", TrainRoute.query.count(), 0),  # At least some routes
    ]
    
    all_passed = True
    for name, count, min_expected in checks:
        passed = count >= min_expected
        status = "✅" if passed else "❌"
        logger.info(f"   {status} {name}: {count}")
        all_passed = all_passed and passed
    
    return all_passed

def setup_database():
    """Main database setup function"""
    logger.info("=" * 80)
    logger.info("RailServe 2025 - Modern Railway Database Setup")
    logger.info("=" * 80)
    logger.info("")
    
    try:
        # Import models and database
        from src.database import db
        from src.app import app
        from src.models import User, Station, Train, TrainRoute
        
        with app.app_context():
            # Step 1: Drop all tables
            drop_all_tables(db, db.engine)
            logger.info("")
            
            # Step 2: Create all tables
            tables = create_all_tables(db)
            logger.info("")
            
            # Step 3: Create initial data
            stations = create_initial_stations(db, Station)
            trains = create_initial_trains(db, Train)
            create_train_routes(db, TrainRoute, Train, trains, stations)
            users = create_admin_users(db, User)
            logger.info("")
            
            # Step 4: Verify setup
            if verify_database_setup(db):
                logger.info("")
                logger.info("=" * 80)
                logger.info("✅ DATABASE SETUP COMPLETED SUCCESSFULLY")
                logger.info("=" * 80)
                logger.info("")
                logger.info("🎉 RailServe is ready to use!")
                logger.info("")
                logger.info("📝 Access Details:")
                logger.info("   - Admin Login: admin / admin123")
                logger.info("   - Test User: testuser / user123")
                logger.info("")
                logger.info("🌐 Start the application:")
                logger.info("   python main.py")
                logger.info("")
                return True
            else:
                logger.error("")
                logger.error("=" * 80)
                logger.error("❌ DATABASE SETUP VERIFICATION FAILED")
                logger.error("=" * 80)
                return False
                
    except Exception as e:
        logger.error(f"❌ Fatal error during database setup: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == '__main__':
    success = setup_database()
    sys.exit(0 if success else 1)
