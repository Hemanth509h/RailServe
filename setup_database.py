#!/usr/bin/env python3
"""
Railway Database Setup Script - Essential Data Only
Creates database schema and populates with only trains, stations, and train routes

Usage:
    python setup_database.py

Environment Variables:
    DATABASE_URL: PostgreSQL connection string
    CREATE_ADMIN: Set to '1' to create admin user
    ADMIN_PASSWORD: Admin password (required if CREATE_ADMIN=1)
"""

import os
import sys
from datetime import datetime, time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_database():
    """Initialize database with essential railway data only"""
    
    # Safety check
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        logger.error("Database setup script should not be run in production!")
        sys.exit(1)
    
    logger.info("Starting Railway Database Setup (Essential Data Only)...")
    logger.info("=" * 60)
    
    # Import Flask app and models
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from src.app import app, db
        from src import models  # Import all models
        
        with app.app_context():
            logger.info("Creating database schema...")
            
            # Only drop tables in development
            logger.warning("DROPPING ALL TABLES - This will delete all data!")
            db.drop_all()
            
            # Create all tables
            db.create_all()
            logger.info("Database schema created successfully")
            
            # Populate with essential data only
            logger.info("Populating database with essential railway data...")
            populate_essential_data(db)
            
            logger.info("Database setup completed successfully!")
            
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        sys.exit(1)

def populate_essential_data(db):
    """Populate database with only essential railway data"""
    
    from src.models import User, Station, Train, TrainRoute
    
    # Create admin user if requested
    create_admin_user(db, User)
    
    # Create essential stations
    logger.info("Creating major railway stations...")
    create_essential_stations(db, Station)
    
    # Create essential trains
    logger.info("Creating essential trains...")
    create_essential_trains(db, Train)
    
    # Create train routes
    logger.info("Creating train routes...")
    create_train_routes(db, Train, Station, TrainRoute)

def create_admin_user(db, User):
    """Create admin user only if explicitly requested"""
    
    admin_password = os.environ.get('ADMIN_PASSWORD')
    create_admin = os.environ.get('CREATE_ADMIN', '').lower() in ['1', 'true', 'yes']
    
    if create_admin:
        if not admin_password:
            logger.error("CREATE_ADMIN=1 requires ADMIN_PASSWORD environment variable")
            sys.exit(1)
        
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash(admin_password)
        
        admin = User(
            username='admin',
            email='admin@railserve.com',
            password_hash=password_hash,
            role='super_admin',
            active=True,
            reset_token=None,
            reset_token_expiry=None
        )
        
        db.session.add(admin)
        db.session.commit()
        logger.info("Created admin user with provided password")
    else:
        logger.info("Skipping admin user creation (set CREATE_ADMIN=1 and ADMIN_PASSWORD to create)")

def create_essential_stations(db, Station):
    """Create major railway stations across India"""
    
    # Essential major railway stations
    essential_stations = [
        # Metro cities and major junctions
        ('NDLS', 'New Delhi', 'Delhi', 'DL', 'Metro'),
        ('CST', 'Mumbai CST', 'Mumbai', 'MH', 'Metro'),
        ('HWH', 'Howrah Junction', 'Kolkata', 'WB', 'Metro'),
        ('MAS', 'Chennai Central', 'Chennai', 'TN', 'Metro'),
        ('SBC', 'Bangalore City Junction', 'Bangalore', 'KA', 'Metro'),
        ('PUNE', 'Pune Junction', 'Pune', 'MH', 'Metro'),
        ('AMH', 'Ahmadabad Junction', 'Ahmedabad', 'GJ', 'Metro'),
        ('HYB', 'Hyderabad Deccan', 'Hyderabad', 'TS', 'Metro'),
        
        # Major junctions
        ('JUC', 'Jalandhar City', 'Jalandhar', 'PB', 'Junction'),
        ('ASR', 'Amritsar Junction', 'Amritsar', 'PB', 'Junction'),
        ('LDH', 'Ludhiana Junction', 'Ludhiana', 'PB', 'Junction'),
        ('UMB', 'Ambala Cantonment', 'Ambala', 'HR', 'Junction'),
        ('CDG', 'Chandigarh', 'Chandigarh', 'CH', 'Junction'),
        ('JP', 'Jaipur Junction', 'Jaipur', 'RJ', 'Junction'),
        ('JU', 'Jodhpur Junction', 'Jodhpur', 'RJ', 'Junction'),
        ('UDZ', 'Udaipur City', 'Udaipur', 'RJ', 'Junction'),
        
        # Eastern region
        ('PNBE', 'Patna Junction', 'Patna', 'BR', 'Junction'),
        ('DNR', 'Danapur', 'Patna', 'BR', 'Junction'),
        ('GYA', 'Gaya Junction', 'Gaya', 'BR', 'Junction'),
        ('MFP', 'Muzaffarpur Junction', 'Muzaffarpur', 'BR', 'Junction'),
        ('GKP', 'Gorakhpur Junction', 'Gorakhpur', 'UP', 'Junction'),
        ('LKO', 'Lucknow', 'Lucknow', 'UP', 'Junction'),
        ('CNB', 'Kanpur Central', 'Kanpur', 'UP', 'Junction'),
        ('AGC', 'Agra Cantonment', 'Agra', 'UP', 'Junction'),
        ('ANVT', 'Anand Vihar Terminal', 'Delhi', 'DL', 'Terminal'),
        
        # Western region
        ('BCT', 'Mumbai Central', 'Mumbai', 'MH', 'Terminal'),
        ('LTT', 'Lokmanya Tilak Terminus', 'Mumbai', 'MH', 'Terminal'),
        ('CSTM', 'Chhatrapati Shivaji Maharaj Terminus', 'Mumbai', 'MH', 'Terminal'),
        ('ST', 'Surat', 'Surat', 'GJ', 'Junction'),
        ('BRC', 'Vadodara Junction', 'Vadodara', 'GJ', 'Junction'),
        ('RTM', 'Ratlam Junction', 'Ratlam', 'MP', 'Junction'),
        ('UJN', 'Ujjain Junction', 'Ujjain', 'MP', 'Junction'),
        ('BINA', 'Bina Junction', 'Bina', 'MP', 'Junction'),
        ('JBP', 'Jabalpur', 'Jabalpur', 'MP', 'Junction'),
        ('NGP', 'Nagpur', 'Nagpur', 'MH', 'Junction'),
        
        # Southern region  
        ('TCR', 'Tiruchirappalli', 'Tiruchirappalli', 'TN', 'Junction'),
        ('MDU', 'Madurai Junction', 'Madurai', 'TN', 'Junction'),
        ('CBE', 'Coimbatore Junction', 'Coimbatore', 'TN', 'Junction'),
        ('SA', 'Salem Junction', 'Salem', 'TN', 'Junction'),
        ('TVC', 'Thiruvananthapuram Central', 'Thiruvananthapuram', 'KL', 'Terminal'),
        ('ERS', 'Ernakulam Junction', 'Kochi', 'KL', 'Junction'),
        ('CLT', 'Kozhikode', 'Kozhikode', 'KL', 'Junction'),
        ('CAN', 'Kannur', 'Kannur', 'KL', 'Junction'),
        ('MAJN', 'Mangalore Junction', 'Mangalore', 'KA', 'Junction'),
        ('UBL', 'Hubli Junction', 'Hubli', 'KA', 'Junction'),
        ('BGM', 'Belagavi', 'Belagavi', 'KA', 'Junction'),
        
        # Northeastern states
        ('GHY', 'Guwahati', 'Guwahati', 'AS', 'Junction'),
        ('DBRG', 'Dibrugarh', 'Dibrugarh', 'AS', 'Junction'),
        ('SLGR', 'Silchar', 'Silchar', 'AS', 'Junction'),
        ('KYQ', 'Kamakhya', 'Guwahati', 'AS', 'Junction'),
        ('APDJ', 'Alipur Duar Junction', 'Alipur Duar', 'WB', 'Junction'),
        ('NJP', 'New Jalpaiguri', 'Siliguri', 'WB', 'Junction'),
    ]
    
    stations = []
    for code, name, city, state, station_type in essential_stations:
        station = Station(
            name=name,
            code=code,
            city=city,
            state=state,
            zone='Northern Railway',  # Simplified - normally this would be more specific
            latitude=0.0,  # These would be populated with real coordinates
            longitude=0.0,
            elevation=0,
            station_type=station_type
        )
        stations.append(station)
    
    db.session.add_all(stations)
    db.session.commit()
    logger.info(f"Created {len(stations)} essential railway stations")

def create_essential_trains(db, Train):
    """Create essential trains connecting major routes"""
    
    # Essential trains - major express and superfast trains
    essential_trains = [
        # Rajdhani Express trains
        ('12301', 'New Delhi Howrah Rajdhani Express', 'Rajdhani', 'Express', 'Daily'),
        ('12951', 'New Delhi Mumbai Central Rajdhani Express', 'Rajdhani', 'Express', 'Daily'),
        ('12429', 'New Delhi Bangalore Rajdhani Express', 'Rajdhani', 'Express', 'Tue,Fri,Sun'),
        ('12431', 'New Delhi Trivandrum Rajdhani Express', 'Rajdhani', 'Express', 'Tue,Fri'),
        ('12423', 'New Delhi Dibrugarh Rajdhani Express', 'Rajdhani', 'Express', 'Wed,Sat'),
        
        # Shatabdi Express trains
        ('12001', 'New Delhi Bhopal Shatabdi Express', 'Shatabdi', 'Express', 'Daily'),
        ('12051', 'New Delhi Amritsar Shatabdi Express', 'Shatabdi', 'Express', 'Daily'),
        ('12009', 'New Delhi Amritsar Shatabdi Express', 'Shatabdi', 'Express', 'Daily'),
        ('12028', 'Mumbai Chennai Shatabdi Express', 'Shatabdi', 'Express', 'Daily'),
        
        # Duronto Express trains
        ('12259', 'New Delhi Kanyakumari Duronto Express', 'Duronto', 'Express', 'Tue,Thu,Sun'),
        ('12273', 'New Delhi Howrah Duronto Express', 'Duronto', 'Express', 'Daily'),
        
        # Major Mail/Express trains
        ('12617', 'Mangala Lakshadweep Express', 'Mail/Express', 'Express', 'Daily'),
        ('12615', 'Grand Trunk Express', 'Mail/Express', 'Express', 'Daily'),
        ('12723', 'Telangana Express', 'Mail/Express', 'Express', 'Daily'),
        ('12841', 'Coromandel Express', 'Mail/Express', 'Express', 'Daily'),
        ('12859', 'Gitanjali Express', 'Mail/Express', 'Express', 'Daily'),
        
        # Popular long-distance trains
        ('16031', 'Andaman Express', 'Mail/Express', 'Express', 'Tue,Fri,Sun'),
        ('16093', 'Lucknow Mail', 'Mail/Express', 'Express', 'Daily'),
        ('12649', 'Karnataka Express', 'Mail/Express', 'Express', 'Daily'),
        ('12925', 'Paschim Express', 'Mail/Express', 'Express', 'Daily'),
        ('12555', 'Gorakhdham Express', 'Mail/Express', 'Express', 'Daily'),
        
        # Inter-city trains
        ('12249', 'Howrah Yesvantpur Duronto Express', 'Duronto', 'Express', 'Mon,Wed,Sat'),
        ('12653', 'Rock Fort Express', 'Mail/Express', 'Express', 'Daily'),
        ('12801', 'Purushottam Express', 'Mail/Express', 'Express', 'Daily'),
        ('12875', 'Neelachal Express', 'Mail/Express', 'Express', 'Daily'),
        ('12311', 'Kalka Mail', 'Mail/Express', 'Express', 'Daily'),
        
        # Regional connectivity
        ('14005', 'Lichchavi Express', 'Mail/Express', 'Express', 'Daily'),
        ('14015', 'Sadbhavana Express', 'Mail/Express', 'Express', 'Daily'),
        ('14021', 'Vibhuti Express', 'Mail/Express', 'Express', 'Daily'),
        ('15023', 'Gorkha Express', 'Mail/Express', 'Express', 'Daily'),
        ('15051', 'Ganga Kaveri Express', 'Mail/Express', 'Express', 'Wed,Sat'),
    ]
    
    trains = []
    for number, name, train_type, category, frequency in essential_trains:
        train = Train(
            number=number,
            name=name,
            type=train_type,
            category=category,
            frequency=frequency,
            total_coaches=18,  # Standard assumption
            departure_time=time(6, 0),  # Default times - would be station-specific normally
            arrival_time=time(18, 0),
            distance=1000,  # Placeholder - would be calculated from routes
            duration=720,  # 12 hours placeholder
            base_fare=500.0,  # Base fare in rupees
            reservation_quota={'General': 70, 'Ladies': 10, 'Senior Citizen': 5, 'Tatkal': 10, 'Other': 5}
        )
        trains.append(train)
    
    db.session.add_all(trains)
    db.session.commit()
    logger.info(f"Created {len(trains)} essential trains")

def create_train_routes(db, Train, Station, TrainRoute):
    """Create basic train routes connecting stations"""
    
    # Get all trains and stations
    trains = Train.query.all()
    stations = Station.query.all()
    
    # Create a mapping of station codes to station objects
    station_map = {station.code: station for station in stations}
    
    # Define some basic routes for major trains
    route_definitions = [
        # Rajdhani routes
        ('12301', [
            ('NDLS', 1, time(16, 55), time(16, 55), 0),
            ('CNB', 2, time(22, 45), time(22, 50), 438),
            ('PNBE', 3, time(4, 40), time(4, 45), 985),
            ('HWH', 4, time(10, 20), time(10, 20), 1441)
        ]),
        ('12951', [
            ('NDLS', 1, time(16, 30), time(16, 30), 0),
            ('JU', 2, time(6, 45), time(6, 50), 558),
            ('BCT', 3, time(8, 35), time(8, 35), 1384)
        ]),
        
        # Shatabdi routes
        ('12001', [
            ('NDLS', 1, time(6, 15), time(6, 15), 0),
            ('JBP', 2, time(14, 45), time(14, 50), 708),
            ('BINA', 3, time(16, 35), time(16, 35), 770)
        ]),
        
        # Express train routes
        ('12617', [
            ('NDLS', 1, time(11, 15), time(11, 15), 0),
            ('LKO', 2, time(17, 30), time(17, 35), 518),
            ('ERS', 3, time(4, 20), time(4, 20), 2081)
        ]),
        
        # More routes for other trains
        ('12615', [
            ('MAS', 1, time(13, 30), time(13, 30), 0),
            ('HWH', 2, time(7, 50), time(7, 50), 1663)
        ]),
        
        ('12649', [
            ('NDLS', 1, time(21, 30), time(21, 30), 0),
            ('SBC', 2, time(6, 20), time(6, 20), 2444)
        ])
    ]
    
    routes = []
    for train_number, route_stations in route_definitions:
        train = Train.query.filter_by(number=train_number).first()
        if not train:
            continue
            
        for station_code, sequence, arrival_time, departure_time, distance in route_stations:
            station = station_map.get(station_code)
            if not station:
                continue
                
            route = TrainRoute(
                train_id=train.id,
                station_id=station.id,
                sequence_number=sequence,
                arrival_time=arrival_time,
                departure_time=departure_time,
                distance_from_origin=distance,
                platform_number=1,  # Default platform
                stop_duration=5 if sequence not in [1, len(route_stations)] else 0  # 5 min stops, except origin/destination
            )
            routes.append(route)
    
    db.session.add_all(routes)
    db.session.commit()
    logger.info(f"Created {len(routes)} train route entries")

if __name__ == '__main__':
    setup_database()