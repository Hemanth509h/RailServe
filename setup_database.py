#!/usr/bin/env python3
"""
Railway Database Setup Script - Clean and Efficient
Creates essential database schema with focused railway data

Features:
- All essential tables from models.py
- 50 major railway stations across India  
- 20 popular trains with realistic routes
- 2 users (regular user and admin)
- Essential system configurations

Usage:
    python setup_database.py

Environment Variables:
    DATABASE_URL: PostgreSQL connection string (optional - defaults to SQLite)
    ADMIN_PASSWORD: Admin password (defaults to 'admin123')
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
    """Initialize database with essential Indian railway data"""
    
    # Safety check - don't run in production
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        logger.error("Database setup script should not be run in production!")
        sys.exit(1)
    
    logger.info("🚂 Starting Railway Database Setup")
    logger.info("Creating: Essential tables, 50 stations, 20 trains, 2 users")
    logger.info("=" * 80)
    
    # Import Flask app and models
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from src.app import app, db
        
        with app.app_context():
            # Import all models to ensure tables are created
            from src.models import (
                User, Station, Train, TrainRoute, 
                Booking, Passenger, Payment, RefundRequest,
                ChartPreparation, TrainStatus, SeatAvailability,
                TatkalTimeSlot, Waitlist, GroupBooking, GroupMessage,
                GroupMemberPayment, GroupMemberInvitation,
                LoyaltyProgram, NotificationPreferences, TatkalOverride,
                PlatformManagement, TrainPlatformAssignment, ComplaintManagement,
                PerformanceMetrics, DynamicPricing, PNRStatusTracking
            )
            
            logger.info("Dropping existing tables...")
            db.drop_all()
            
            logger.info("Creating database schema...")
            db.create_all()
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"✅ Created {len(tables)} tables")
            
            # Create users
            logger.info("Creating user accounts...")
            create_users(User, db)
            
            # Create essential stations
            logger.info("Creating 50 major railway stations...")
            create_stations(Station, db)
            
            # Create trains
            logger.info("Creating 20 popular trains...")
            create_trains(Train, db)
            
            # Create train routes
            logger.info("Creating train routes...")
            create_routes(Train, Station, TrainRoute, db)
            
            # Create system configurations
            logger.info("Creating system configurations...")
            create_configurations(TatkalTimeSlot, PlatformManagement, Station, db)
            
            logger.info("🎉 Database setup completed successfully!")
            logger.info("Railway System with 50 stations, 20 trains ready for development and testing")
            
    except Exception as e:
        logger.error(f"❌ Database setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def create_users(User, db):
    """Create admin and regular user accounts"""
    from werkzeug.security import generate_password_hash
    
    # Admin user
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    admin = User(
        username='admin',
        email='admin@railway.gov.in',
        password_hash=generate_password_hash(admin_password),
        role='super_admin',
        active=True
    )
    
    # Regular user
    user = User(
        username='user',
        email='user@example.com',
        password_hash=generate_password_hash('user123'),
        role='user',
        active=True
    )
    
    db.session.add_all([admin, user])
    db.session.commit()
    logger.info("✅ Created admin (admin/admin123) and user (user/user123) accounts")

def create_stations(Station, db):
    """Create 50 major railway stations across India"""
    
    stations_data = [
        # Major Metro Cities
        ('NDLS', 'New Delhi', 'New Delhi', 'Delhi'),
        ('CSMT', 'Mumbai CST', 'Mumbai', 'Maharashtra'),
        ('HWH', 'Howrah Junction', 'Kolkata', 'West Bengal'),
        ('MAS', 'Chennai Central', 'Chennai', 'Tamil Nadu'),
        ('SBC', 'Bangalore City', 'Bangalore', 'Karnataka'),
        ('SC', 'Secunderabad Junction', 'Hyderabad', 'Telangana'),
        ('PUNE', 'Pune Junction', 'Pune', 'Maharashtra'),
        ('ADI', 'Ahmedabad Junction', 'Ahmedabad', 'Gujarat'),
        
        # North India
        ('LKO', 'Lucknow Junction', 'Lucknow', 'Uttar Pradesh'),
        ('CNB', 'Kanpur Central', 'Kanpur', 'Uttar Pradesh'),
        ('PNBE', 'Patna Junction', 'Patna', 'Bihar'),
        ('JP', 'Jaipur Junction', 'Jaipur', 'Rajasthan'),
        ('JU', 'Jodhpur Junction', 'Jodhpur', 'Rajasthan'),
        ('ASR', 'Amritsar Junction', 'Amritsar', 'Punjab'),
        ('CDG', 'Chandigarh', 'Chandigarh', 'Chandigarh'),
        
        # South India
        ('TPJ', 'Tiruchirapalli Junction', 'Tiruchirappalli', 'Tamil Nadu'),
        ('MDU', 'Madurai Junction', 'Madurai', 'Tamil Nadu'),
        ('CBE', 'Coimbatore Junction', 'Coimbatore', 'Tamil Nadu'),
        ('ERS', 'Ernakulam Junction', 'Kochi', 'Kerala'),
        ('TVC', 'Thiruvananthapuram Central', 'Thiruvananthapuram', 'Kerala'),
        ('CLT', 'Kozhikode', 'Kozhikode', 'Kerala'),
        ('MYS', 'Mysore Junction', 'Mysore', 'Karnataka'),
        ('UBL', 'Hubli Junction', 'Hubli', 'Karnataka'),
        ('BZA', 'Vijayawada Junction', 'Vijayawada', 'Andhra Pradesh'),
        ('VSKP', 'Visakhapatnam', 'Visakhapatnam', 'Andhra Pradesh'),
        
        # East India
        ('BBS', 'Bhubaneswar', 'Bhubaneswar', 'Odisha'),
        ('PURI', 'Puri', 'Puri', 'Odisha'),
        ('ASN', 'Asansol Junction', 'Asansol', 'West Bengal'),
        ('TATA', 'Tatanagar Junction', 'Jamshedpur', 'Jharkhand'),
        ('GHY', 'Guwahati', 'Guwahati', 'Assam'),
        
        # West India
        ('ST', 'Surat', 'Surat', 'Gujarat'),
        ('BRC', 'Vadodara Junction', 'Vadodara', 'Gujarat'),
        ('NGP', 'Nagpur', 'Nagpur', 'Maharashtra'),
        ('BSL', 'Bhusaval Junction', 'Bhusaval', 'Maharashtra'),
        ('KOP', 'Kolhapur CSMT', 'Kolhapur', 'Maharashtra'),
        
        # Central India
        ('BPL', 'Bhopal Junction', 'Bhopal', 'Madhya Pradesh'),
        ('JBP', 'Jabalpur', 'Jabalpur', 'Madhya Pradesh'),
        ('INDB', 'Indore Junction', 'Indore', 'Madhya Pradesh'),
        ('GWL', 'Gwalior', 'Gwalior', 'Madhya Pradesh'),
        ('JHS', 'Jhansi Junction', 'Jhansi', 'Uttar Pradesh'),
        
        # Hill Stations & Tourist Places
        ('DLI', 'Delhi', 'Delhi', 'Delhi'),
        ('AGC', 'Agra Cantt', 'Agra', 'Uttar Pradesh'),
        ('AF', 'Ajmer Junction', 'Ajmer', 'Rajasthan'),
        ('UDZ', 'Udaipur City', 'Udaipur', 'Rajasthan'),
        ('JAT', 'Jammu Tawi', 'Jammu', 'Jammu & Kashmir'),
        ('CAPE', 'Kanyakumari', 'Kanyakumari', 'Tamil Nadu'),
        ('RMM', 'Rameswaram', 'Rameswaram', 'Tamil Nadu'),
        
        # Important Junctions
        ('GTL', 'Guntakal Junction', 'Guntakal', 'Andhra Pradesh'),
        ('KPD', 'Katpadi Junction', 'Vellore', 'Tamil Nadu'),
        ('JTJ', 'Jolarpettai Junction', 'Jolarpettai', 'Tamil Nadu'),
        ('KUR', 'Khurda Road Junction', 'Khurda', 'Odisha'),
        ('RTM', 'Ratlam Junction', 'Ratlam', 'Madhya Pradesh')
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

def create_trains(Train, db):
    """Create 20 popular trains"""
    
    trains_data = [
        # Express Trains
        ('12301', 'Rajdhani Express', 400, 350, 2.5, 50, 4.0),
        ('12302', 'New Delhi Rajdhani', 400, 350, 2.5, 50, 4.0),
        ('12951', 'Mumbai Rajdhani', 350, 300, 2.8, 40, 4.5),
        ('12952', 'New Delhi Rajdhani', 350, 300, 2.8, 40, 4.5),
        ('12621', 'Tamil Nadu Express', 450, 400, 1.8, 60, 3.0),
        ('12622', 'Tamil Nadu Express', 450, 400, 1.8, 60, 3.0),
        ('12841', 'Coromandel Express', 400, 350, 2.0, 50, 3.2),
        ('12842', 'Coromandel Express', 400, 350, 2.0, 50, 3.2),
        
        # Superfast Trains
        ('12223', 'Kaifiyat Express', 380, 320, 1.5, 45, 2.8),
        ('12224', 'Kaifiyat Express', 380, 320, 1.5, 45, 2.8),
        ('12253', 'Anga Express', 360, 310, 1.6, 40, 2.5),
        ('12254', 'Anga Express', 360, 310, 1.6, 40, 2.5),
        ('16031', 'Andaman Express', 420, 380, 1.4, 50, 2.2),
        ('16032', 'Andaman Express', 420, 380, 1.4, 50, 2.2),
        
        # Mail Express
        ('11013', 'Coimbatore Express', 400, 350, 1.3, 45, 2.0),
        ('11014', 'Coimbatore Express', 400, 350, 1.3, 45, 2.0),
        ('12605', 'Pallavan Express', 380, 330, 1.4, 40, 2.1),
        ('12606', 'Pallavan Express', 380, 330, 1.4, 40, 2.1),
        
        # Premium Trains
        ('12431', 'Trivandrum Rajdhani', 300, 250, 3.5, 35, 5.5),
        ('12432', 'Trivandrum Rajdhani', 300, 250, 3.5, 35, 5.5)
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

def create_routes(Train, Station, TrainRoute, db):
    """Create comprehensive train routes for all trains"""
    
    # Define comprehensive route templates
    routes = [
        # Express Trains - Long Distance
        ('12301', [('NDLS', 0, time(16, 55), time(17, 0), 0), ('BPL', 1, time(23, 45), time(23, 50), 707), ('NGP', 2, time(3, 20), time(3, 25), 1071), ('HYB', 3, time(9, 45), None, 1578)]),
        ('12302', [('HYB', 0, time(17, 40), time(17, 45), 0), ('NGP', 1, time(0, 15), time(0, 20), 507), ('BPL', 2, time(4, 45), time(4, 50), 871), ('NDLS', 3, time(11, 55), None, 1578)]),
        
        ('12951', [('CSMT', 0, time(16, 55), time(17, 0), 0), ('BRC', 1, time(21, 8), time(21, 13), 391), ('RTM', 2, time(1, 50), time(1, 55), 679), ('JP', 3, time(9, 15), time(9, 20), 1238), ('NDLS', 4, time(14, 30), None, 1384)]),
        ('12952', [('NDLS', 0, time(16, 0), time(16, 5), 0), ('JP', 1, time(21, 10), time(21, 15), 146), ('RTM', 2, time(3, 45), time(3, 50), 705), ('BRC', 3, time(8, 42), time(8, 47), 993), ('CSMT', 4, time(12, 55), None, 1384)]),
        
        ('12621', [('NDLS', 0, time(20, 30), time(20, 35), 0), ('GWL', 1, time(0, 45), time(0, 50), 319), ('JHS', 2, time(2, 20), time(2, 25), 415), ('BPL', 3, time(6, 0), time(6, 10), 707), ('NGP', 4, time(11, 35), time(11, 45), 1071), ('BZA', 5, time(21, 15), time(21, 25), 1445), ('MAS', 6, time(6, 45), None, 1768)]),
        ('12622', [('MAS', 0, time(21, 40), time(21, 45), 0), ('BZA', 1, time(8, 30), time(8, 40), 323), ('NGP', 2, time(18, 10), time(18, 20), 697), ('BPL', 3, time(23, 35), time(23, 45), 1061), ('JHS', 4, time(3, 25), time(3, 30), 1353), ('GWL', 5, time(5, 5), time(5, 10), 1449), ('NDLS', 6, time(10, 15), None, 1768)]),
        
        ('12841', [('HWH', 0, time(14, 20), time(14, 25), 0), ('BBS', 1, time(20, 0), time(20, 10), 441), ('VSKP', 2, time(1, 55), time(2, 5), 736), ('BZA', 3, time(7, 50), time(8, 0), 1048), ('MAS', 4, time(14, 30), None, 1662)]),
        ('12842', [('MAS', 0, time(8, 30), time(8, 35), 0), ('BZA', 1, time(15, 5), time(15, 15), 614), ('VSKP', 2, time(21, 0), time(21, 10), 926), ('BBS', 3, time(2, 40), time(2, 50), 1221), ('HWH', 4, time(8, 30), None, 1662)]),
        
        # Superfast Trains
        ('12223', [('NDLS', 0, time(19, 50), time(19, 55), 0), ('CNB', 1, time(0, 8), time(0, 13), 441), ('PNBE', 2, time(8, 45), time(8, 55), 998), ('ASN', 3, time(13, 30), None, 1233)]),
        ('12224', [('ASN', 0, time(22, 15), time(22, 20), 0), ('PNBE', 1, time(2, 45), time(2, 55), 235), ('CNB', 2, time(11, 32), time(11, 37), 792), ('NDLS', 3, time(15, 45), None, 1233)]),
        
        ('12253', [('BBS', 0, time(6, 30), time(6, 35), 0), ('KUR', 1, time(7, 15), time(7, 20), 44), ('VSKP', 2, time(10, 20), time(10, 30), 295), ('HWH', 3, time(20, 45), None, 736)]),
        ('12254', [('HWH', 0, time(23, 55), time(0, 0), 0), ('VSKP', 1, time(10, 25), time(10, 35), 441), ('KUR', 2, time(13, 35), time(13, 40), 691), ('BBS', 3, time(14, 25), None, 736)]),
        
        ('16031', [('MAS', 0, time(6, 0), time(6, 5), 0), ('KPD', 1, time(8, 23), time(8, 28), 135), ('JTJ', 2, time(10, 45), time(10, 50), 230), ('SBC', 3, time(13, 15), None, 362)]),
        ('16032', [('SBC', 0, time(14, 0), time(14, 5), 0), ('JTJ', 1, time(16, 25), time(16, 30), 132), ('KPD', 2, time(18, 47), time(18, 52), 227), ('MAS', 3, time(21, 15), None, 362)]),
        
        # Mail Express
        ('11013', [('LTT', 0, time(11, 25), time(11, 30), 0), ('PUNE', 1, time(14, 55), time(15, 5), 192), ('SBC', 2, time(4, 30), time(4, 40), 844), ('CBE', 3, time(10, 15), None, 1134)]),
        ('11014', [('CBE', 0, time(20, 15), time(20, 20), 0), ('SBC', 1, time(1, 55), time(2, 5), 290), ('PUNE', 2, time(16, 25), time(16, 35), 942), ('LTT', 3, time(19, 55), None, 1134)]),
        
        ('12605', [('MAS', 0, time(13, 40), time(13, 45), 0), ('KPD', 1, time(15, 58), time(16, 3), 135), ('JTJ', 2, time(18, 20), time(18, 25), 230), ('NDLS', 3, time(7, 35), None, 2180)]),
        ('12606', [('NDLS', 0, time(15, 50), time(15, 55), 0), ('JTJ', 1, time(4, 45), time(4, 50), 1950), ('KPD', 2, time(7, 7), time(7, 12), 2045), ('MAS', 3, time(9, 30), None, 2180)]),
        
        # Premium Trains
        ('12431', [('TVC', 0, time(11, 0), time(11, 5), 0), ('ERS', 1, time(15, 25), time(15, 35), 220), ('CBE', 2, time(21, 15), time(21, 25), 441), ('BZA', 3, time(7, 20), time(7, 30), 1074), ('NDLS', 4, time(4, 35), None, 3149)]),
        ('12432', [('NDLS', 0, time(10, 30), time(10, 35), 0), ('BZA', 1, time(7, 45), time(7, 55), 2075), ('CBE', 2, time(17, 40), time(17, 50), 2708), ('ERS', 3, time(23, 30), time(23, 40), 2929), ('TVC', 4, time(3, 55), None, 3149)])
    ]
    
    train_routes = []
    for train_number, route_data in routes:
        # Find train by number
        train = Train.query.filter_by(number=train_number).first()
        if not train:
            continue
            
        for station_code, sequence, arrival_time, departure_time, distance in route_data:
            # Find station by code
            station = Station.query.filter_by(code=station_code).first()
            if not station:
                # Try to find a similar station if exact match not found
                station = Station.query.filter(Station.code.like(f'%{station_code[:3]}%')).first()
                if not station:
                    continue
                
            train_route = TrainRoute(
                train_id=train.id,
                station_id=station.id,
                sequence=sequence,
                arrival_time=arrival_time,
                departure_time=departure_time,
                distance_from_start=distance
            )
            train_routes.append(train_route)
    
    db.session.add_all(train_routes)
    db.session.commit()
    logger.info(f"✅ Created {len(train_routes)} train route entries covering all trains")

def create_configurations(TatkalTimeSlot, PlatformManagement, Station, db):
    """Create essential system configurations"""
    
    # Create Tatkal time slots
    tatkal_slots = [
        TatkalTimeSlot(
            name='AC Classes Tatkal',
            coach_classes='AC1,AC2,AC3,CC',
            open_time=time(10, 0),  # 10:00 AM
            close_time=time(11, 30),  # 11:30 AM
            days_before_journey=1,
            active=True
        ),
        TatkalTimeSlot(
            name='Non-AC Classes Tatkal',
            coach_classes='SL,2S',
            open_time=time(11, 0),  # 11:00 AM
            close_time=time(12, 30),  # 12:30 PM
            days_before_journey=1,
            active=True
        )
    ]
    
    db.session.add_all(tatkal_slots)
    
    # Create platform management for major stations
    major_stations = Station.query.filter(Station.code.in_([
        'NDLS', 'CSMT', 'HWH', 'MAS', 'SBC', 'SC', 'PUNE', 'ADI'
    ])).all()
    
    platforms = []
    for station in major_stations:
        for i in range(1, 11):  # 10 platforms per major station
            platform = PlatformManagement(
                station_id=station.id,
                platform_number=str(i),
                track_number=f"T{i}",
                platform_length=400 if i <= 6 else 200,
                facilities='Waiting Room,Food Court,ATM' if i <= 3 else 'Waiting Room',
                wheelchair_accessible=True if i <= 5 else False,
                electrified=True,
                status='active'
            )
            platforms.append(platform)
    
    db.session.add_all(platforms)
    db.session.commit()
    logger.info(f"✅ Created {len(tatkal_slots)} Tatkal time slots and {len(platforms)} platform configurations")

if __name__ == '__main__':
    setup_database()
    """Create sample operational data for testing admin features"""

if __name__ == '__main__':
    setup_database()
