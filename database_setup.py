#!/usr/bin/env python3
"""
Complete Database Setup Script for RailServe Train Booking System
This script creates and populates the PostgreSQL database with:
- 1000 railway stations across India
- 1000 trains with realistic details  
- Train routes connecting stations
- Admin users and test data

Usage:
    python database_setup.py

Environment Variables Required:
    DATABASE_URL - PostgreSQL connection string (optional, uses Replit's if not provided)
    SESSION_SECRET - Secret key for sessions (optional, uses default if not provided)
"""

import os
import sys
import random
import logging
from datetime import datetime, time, date, timedelta
from typing import List, Dict, Any, Tuple

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

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

class RailwayDatabaseSetup:
    """Complete railway database setup and population"""
    
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
    
    def create_tables(self) -> bool:
        """Create all database tables"""
        try:
            logger.info("🏗️  Creating database tables...")
            
            # Import Flask app to trigger table creation
            from src.app import app, db
            with app.app_context():
                db.create_all()
            
            logger.info("✅ Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Table creation failed: {e}")
            return False
    
    def reset_data(self) -> bool:
        """Clear existing data (destructive operation)"""
        try:
            with self.Session() as session:
                logger.info("🗑️  Clearing existing data...")
                # Delete in correct order to respect foreign key constraints
                session.execute(text("DELETE FROM waitlist"))
                session.execute(text("DELETE FROM payment"))
                session.execute(text("DELETE FROM passenger"))
                session.execute(text("DELETE FROM booking"))
                session.execute(text("DELETE FROM train_route"))
                session.execute(text("DELETE FROM train"))
                session.execute(text("DELETE FROM station"))
                session.execute(text("DELETE FROM \"user\" WHERE role != 'super_admin'"))
                session.commit()
                logger.info("✅ Data cleared successfully")
                return True
        except Exception as e:
            logger.error(f"❌ Data clearing failed: {e}")
            return False
    
    def generate_station_data(self) -> List[Dict[str, str]]:
        """Generate 1000 railway stations across India efficiently"""
        
        # Base stations with real Indian railway stations
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
            {'code': 'ALLP', 'name': 'Allahabad Junction', 'city': 'Allahabad', 'state': 'Uttar Pradesh'},
            {'code': 'BCT', 'name': 'Mumbai Central', 'city': 'Mumbai', 'state': 'Maharashtra'},
            {'code': 'BZA', 'name': 'Vijayawada Junction', 'city': 'Vijayawada', 'state': 'Andhra Pradesh'},
            {'code': 'CNB', 'name': 'Kanpur Central', 'city': 'Kanpur', 'state': 'Uttar Pradesh'},
            {'code': 'GWL', 'name': 'Gwalior Junction', 'city': 'Gwalior', 'state': 'Madhya Pradesh'},
            {'code': 'JBP', 'name': 'Jabalpur Junction', 'city': 'Jabalpur', 'state': 'Madhya Pradesh'},
            {'code': 'VSKP', 'name': 'Visakhapatnam Junction', 'city': 'Visakhapatnam', 'state': 'Andhra Pradesh'},
            {'code': 'UDZ', 'name': 'Udaipur City', 'city': 'Udaipur', 'state': 'Rajasthan'},
            {'code': 'JU', 'name': 'Jodhpur Junction', 'city': 'Jodhpur', 'state': 'Rajasthan'},
            {'code': 'BKN', 'name': 'Bikaner Junction', 'city': 'Bikaner', 'state': 'Rajasthan'},
            {'code': 'TVC', 'name': 'Trivandrum Central', 'city': 'Thiruvananthapuram', 'state': 'Kerala'},
        ]
        
        # Pre-generate Indian cities and states for faster processing
        city_state_combinations = [
            ('Agra', 'Uttar Pradesh'), ('Lucknow', 'Uttar Pradesh'), ('Kanpur', 'Uttar Pradesh'), ('Varanasi', 'Uttar Pradesh'),
            ('Mumbai', 'Maharashtra'), ('Pune', 'Maharashtra'), ('Nagpur', 'Maharashtra'), ('Nashik', 'Maharashtra'),
            ('Chennai', 'Tamil Nadu'), ('Coimbatore', 'Tamil Nadu'), ('Madurai', 'Tamil Nadu'), ('Salem', 'Tamil Nadu'),
            ('Bangalore', 'Karnataka'), ('Mysore', 'Karnataka'), ('Hubli', 'Karnataka'), ('Mangalore', 'Karnataka'),
            ('Ahmedabad', 'Gujarat'), ('Surat', 'Gujarat'), ('Vadodara', 'Gujarat'), ('Rajkot', 'Gujarat'),
            ('Jaipur', 'Rajasthan'), ('Jodhpur', 'Rajasthan'), ('Kota', 'Rajasthan'), ('Udaipur', 'Rajasthan'),
            ('Kolkata', 'West Bengal'), ('Howrah', 'West Bengal'), ('Durgapur', 'West Bengal'), ('Asansol', 'West Bengal'),
            ('Bhopal', 'Madhya Pradesh'), ('Indore', 'Madhya Pradesh'), ('Gwalior', 'Madhya Pradesh'), ('Jabalpur', 'Madhya Pradesh'),
            ('Thiruvananthapuram', 'Kerala'), ('Kochi', 'Kerala'), ('Kozhikode', 'Kerala'), ('Thrissur', 'Kerala'),
            ('Visakhapatnam', 'Andhra Pradesh'), ('Vijayawada', 'Andhra Pradesh'), ('Guntur', 'Andhra Pradesh'), ('Nellore', 'Andhra Pradesh'),
            ('Ludhiana', 'Punjab'), ('Amritsar', 'Punjab'), ('Jalandhar', 'Punjab'), ('Patiala', 'Punjab'),
            ('Patna', 'Bihar'), ('Gaya', 'Bihar'), ('Bhagalpur', 'Bihar'), ('Muzaffarpur', 'Bihar'),
            ('Ranchi', 'Jharkhand'), ('Jamshedpur', 'Jharkhand'), ('Dhanbad', 'Jharkhand'), ('Bokaro', 'Jharkhand'),
            ('Bhubaneswar', 'Odisha'), ('Cuttack', 'Odisha'), ('Rourkela', 'Odisha'), ('Sambalpur', 'Odisha'),
        ]
        
        # Extend the list to have enough combinations for 1000 stations
        while len(city_state_combinations) < 1000:
            city_state_combinations.extend(city_state_combinations[:min(50, 1000 - len(city_state_combinations))])
        
        station_types = ['Junction', 'Central', 'City', 'Cantt', 'Road', 'Terminal']
        stations = major_stations.copy()
        
        # Generate stations efficiently without constant duplicate checking
        used_codes = {s['code'] for s in stations}
        used_names = {s['name'] for s in stations}
        
        counter = 0
        for city, state in city_state_combinations:
            if len(stations) >= 1000:
                break
            
            station_type = station_types[counter % len(station_types)]
            counter += 1
            
            # Generate unique code efficiently
            code = f"{city[:2].upper()}{station_type[:2].upper()}{counter:03d}"
            while code in used_codes:
                counter += 1
                code = f"{city[:2].upper()}{station_type[:2].upper()}{counter:03d}"
            
            # Generate name
            name = f"{city} {station_type}"
            if name in used_names:
                name = f"{city} {station_type} {counter}"
            
            stations.append({
                'code': code,
                'name': name,
                'city': city,
                'state': state
            })
            
            used_codes.add(code)
            used_names.add(name)
        
        return stations[:1000]
    
    def populate_stations(self) -> bool:
        """Populate 1000 stations"""
        try:
            logger.info("🚉 Generating and populating 1000 stations...")
            stations_data = self.generate_station_data()
            
            with self.Session() as session:
                created_count = 0
                batch_size = 100
                
                for i in range(0, len(stations_data), batch_size):
                    batch = stations_data[i:i + batch_size]
                    
                    for station_data in batch:
                        try:
                            session.execute(text("""
                                INSERT INTO station (code, name, city, state, active, created_at) 
                                VALUES (:code, :name, :city, :state, true, :created_at)
                                ON CONFLICT (code) DO UPDATE SET 
                                    name = EXCLUDED.name,
                                    city = EXCLUDED.city,
                                    state = EXCLUDED.state,
                                    active = true
                            """), {**station_data, 'created_at': datetime.utcnow()})
                            created_count += 1
                        except IntegrityError:
                            session.rollback()
                            session.begin()
                            continue
                    
                    session.commit()
                    logger.info(f"📍 Processed {min(i + batch_size, len(stations_data))} stations...")
                
                logger.info(f"✅ Stations populated successfully: {created_count} stations")
                return True
                
        except Exception as e:
            logger.error(f"❌ Station population failed: {e}")
            return False
    
    def populate_trains(self) -> bool:
        """Populate 1000 trains with realistic details"""
        train_types = [
            ('Rajdhani Express', 'RAJ', 18.00, 72, 22.00, 18),
            ('Shatabdi Express', 'SHTB', 16.00, 78, 20.00, 15),
            ('Duronto Express', 'DRN', 17.00, 90, 21.00, 20),
            ('Garib Rath', 'GR', 9.50, 180, 12.00, 35),
            ('Superfast Express', 'SF', 12.00, 120, 15.00, 25),
            ('Mail Express', 'MAIL', 10.50, 150, 13.00, 30),
            ('Express', 'EXP', 8.50, 200, 11.00, 40),
            ('Passenger', 'PASS', 4.50, 250, 6.00, 50),
            ('Jan Shatabdi', 'JSHT', 8.00, 100, 10.50, 20),
            ('Humsafar Express', 'HMS', 13.50, 110, 17.00, 22),
            ('Tejas Express', 'TEJ', 15.50, 85, 19.50, 17),
            ('Vande Bharat Express', 'VB', 22.00, 56, 28.00, 12),
            ('Double Decker Express', 'DD', 14.00, 120, 18.00, 24),
            ('Antyodaya Express', 'ANTD', 6.00, 240, 8.00, 48),
            ('Jan Sadharan Express', 'JS', 7.00, 220, 9.50, 44)
        ]
        
        try:
            logger.info("🚄 Generating and populating 1000 trains...")
            
            with self.Session() as session:
                created_count = 0
                train_number = 10001
                
                for i in range(1000):
                    train_type, type_code, fare_per_km, total_seats, tatkal_fare, tatkal_seats = random.choice(train_types)
                    
                    # Generate realistic train numbers
                    if train_type in ['Rajdhani Express', 'Shatabdi Express']:
                        train_number = random.choice(range(12001, 12999))
                    elif train_type == 'Duronto Express':
                        train_number = random.choice(range(22201, 22999))
                    elif 'Express' in train_type:
                        train_number = random.choice(range(11001, 19999))
                    else:
                        train_number = random.choice(range(51001, 59999))
                    
                    # Ensure unique train number
                    while True:
                        result = session.execute(text("SELECT id FROM train WHERE number = :number"), 
                                               {'number': str(train_number)})
                        if not result.fetchone():
                            break
                        train_number += 1
                        if train_number > 99999:
                            train_number = 10001
                    
                    train_name = f"{train_type}"
                    
                    # Add some variation to seats and fare
                    total_seats += random.randint(-20, 20)
                    total_seats = max(total_seats, 30)  # Minimum 30 seats
                    fare_per_km += random.uniform(-2.0, 2.0)
                    fare_per_km = max(fare_per_km, 2.0)  # Minimum fare
                    tatkal_fare += random.uniform(-3.0, 3.0)
                    tatkal_fare = max(tatkal_fare, fare_per_km + 2.0)  # Tatkal always higher
                    
                    try:
                        session.execute(text("""
                            INSERT INTO train (number, name, total_seats, available_seats, fare_per_km, 
                                             tatkal_seats, tatkal_fare_per_km, active, created_at) 
                            VALUES (:number, :name, :total_seats, :available_seats, :fare_per_km,
                                   :tatkal_seats, :tatkal_fare_per_km, true, :created_at)
                        """), {
                            'number': str(train_number),
                            'name': train_name,
                            'total_seats': total_seats,
                            'available_seats': total_seats,
                            'fare_per_km': round(fare_per_km, 2),
                            'tatkal_seats': tatkal_seats,
                            'tatkal_fare_per_km': round(tatkal_fare, 2),
                            'created_at': datetime.utcnow()
                        })
                        created_count += 1
                        
                        if created_count % 100 == 0:
                            session.commit()
                            logger.info(f"🚂 Created {created_count} trains...")
                            
                    except IntegrityError:
                        session.rollback()
                        session.begin()
                        continue
                
                session.commit()
                logger.info(f"✅ Trains populated successfully: {created_count} trains")
                return True
                
        except Exception as e:
            logger.error(f"❌ Train population failed: {e}")
            return False
    
    def create_train_routes(self) -> bool:
        """Create train routes connecting stations efficiently"""
        try:
            logger.info("🛤️  Creating train routes...")
            
            with self.Session() as session:
                # Get all stations and trains
                stations_result = session.execute(text("SELECT id, code, name, city, state FROM station ORDER BY id"))
                stations = [dict(row._mapping) for row in stations_result]
                
                trains_result = session.execute(text("SELECT id, number, name FROM train ORDER BY id"))
                trains = [dict(row._mapping) for row in trains_result]
                
                logger.info(f"📊 Found {len(stations)} stations and {len(trains)} trains")
                
                route_count = 0
                batch_size = 500  # Process routes in batches
                route_batch = []
                
                # Create routes for each train (3-6 stations per route for efficiency)
                for i, train in enumerate(trains):
                    route_stations = random.sample(stations, random.randint(3, 6))
                    route_stations = sorted(route_stations, key=lambda x: (x['state'], x['city']))
                    
                    total_distance = 0
                    current_time = time(hour=random.randint(6, 20), minute=random.choice([0, 30]))
                    
                    for sequence, station in enumerate(route_stations, 1):
                        # Calculate distance efficiently
                        if sequence == 1:
                            distance_from_start = 0.0
                        else:
                            distance_increment = random.uniform(80, 200)  # Standardized distance range
                            total_distance += distance_increment
                            distance_from_start = total_distance
                        
                        # Calculate times more efficiently
                        if sequence == 1:
                            arrival_time = None
                            departure_time = current_time
                        elif sequence == len(route_stations):
                            # Last station - arrival only
                            travel_time_minutes = random.randint(60, 120)
                            current_datetime = datetime.combine(date.today(), current_time)
                            arrival_datetime = current_datetime + timedelta(minutes=travel_time_minutes)
                            arrival_time = arrival_datetime.time()
                            departure_time = None
                        else:
                            # Intermediate station
                            travel_time_minutes = random.randint(45, 90)
                            current_datetime = datetime.combine(date.today(), current_time)
                            arrival_datetime = current_datetime + timedelta(minutes=travel_time_minutes)
                            arrival_time = arrival_datetime.time()
                            
                            # Fixed stop duration for efficiency
                            stop_duration = random.choice([5, 10, 15])
                            departure_datetime = arrival_datetime + timedelta(minutes=stop_duration)
                            departure_time = departure_datetime.time()
                            current_time = departure_time
                        
                        # Add to batch instead of inserting immediately
                        route_batch.append({
                            'train_id': train['id'],
                            'station_id': station['id'],
                            'sequence': sequence,
                            'arrival_time': arrival_time,
                            'departure_time': departure_time,
                            'distance_from_start': round(distance_from_start, 2)
                        })
                        
                        route_count += 1
                    
                    # Process batch when it reaches batch_size
                    if len(route_batch) >= batch_size:
                        session.execute(text("""
                            INSERT INTO train_route (train_id, station_id, sequence, arrival_time, 
                                                   departure_time, distance_from_start)
                            VALUES (:train_id, :station_id, :sequence, :arrival_time, 
                                   :departure_time, :distance_from_start)
                        """), route_batch)
                        session.commit()
                        route_batch = []
                        
                    if (i + 1) % 100 == 0:
                        logger.info(f"🎯 Processed {i + 1} trains (Total route entries: {route_count})")
                
                # Process remaining batch
                if route_batch:
                    session.execute(text("""
                        INSERT INTO train_route (train_id, station_id, sequence, arrival_time, 
                                               departure_time, distance_from_start)
                        VALUES (:train_id, :station_id, :sequence, :arrival_time, 
                               :departure_time, :distance_from_start)
                    """), route_batch)
                    session.commit()
                
                logger.info(f"✅ Train routes created successfully: {route_count} route entries")
                return True
                
        except Exception as e:
            logger.error(f"❌ Train route creation failed: {e}")
            return False
    
    def create_admin_user(self) -> bool:
        """Create admin user for system access"""
        try:
            with self.Session() as session:
                logger.info("👤 Creating admin user...")
                
                # Check if admin user already exists
                result = session.execute(text("SELECT id FROM \"user\" WHERE username = 'admin'"))
                if result.fetchone():
                    logger.info("ℹ️  Admin user already exists")
                    return True
                
                password_hash = generate_password_hash("admin123")
                
                session.execute(text("""
                    INSERT INTO \"user\" (username, email, password_hash, role, active, created_at) 
                    VALUES ('admin', 'admin@railserve.com', :password_hash, 'super_admin', true, :created_at)
                """), {
                    'password_hash': password_hash,
                    'created_at': datetime.utcnow()
                })
                
                session.commit()
                logger.info("✅ Admin user created successfully: admin / admin123")
                return True
                
        except Exception as e:
            logger.error(f"❌ Admin user creation failed: {e}")
            return False
    
    def create_sample_users(self) -> bool:
        """Create sample users for testing"""
        try:
            with self.Session() as session:
                logger.info("👥 Creating sample users...")
                
                users_data = [
                    ('john_doe', 'john@example.com', 'password123'),
                    ('jane_smith', 'jane@example.com', 'password123'),
                    ('rajesh_kumar', 'rajesh@example.com', 'password123'),
                    ('priya_sharma', 'priya@example.com', 'password123'),
                    ('amit_patel', 'amit@example.com', 'password123')
                ]
                
                created_count = 0
                for username, email, password in users_data:
                    # Check if user exists
                    result = session.execute(text("SELECT id FROM \"user\" WHERE username = :username"), 
                                           {'username': username})
                    if result.fetchone():
                        continue
                    
                    password_hash = generate_password_hash(password)
                    session.execute(text("""
                        INSERT INTO \"user\" (username, email, password_hash, role, active, created_at) 
                        VALUES (:username, :email, :password_hash, 'user', true, :created_at)
                    """), {
                        'username': username,
                        'email': email,
                        'password_hash': password_hash,
                        'created_at': datetime.utcnow()
                    })
                    created_count += 1
                
                session.commit()
                logger.info(f"✅ Sample users created: {created_count} users (Password: password123)")
                return True
                
        except Exception as e:
            logger.error(f"❌ Sample user creation failed: {e}")
            return False

def get_database_url() -> str:
    """Get database URL from environment or use Replit default"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.info("Using Replit's PostgreSQL database")
        return "postgresql://neondb_owner:npg_password@database:5432/neondb"
    return database_url

def main():
    """Main execution function"""
    print("🚂 RailServe Database Setup & Population Script")
    print("=" * 50)
    
    # Get database URL
    database_url = get_database_url()
    
    # Initialize setup
    setup = RailwayDatabaseSetup(database_url)
    
    # Verify connection
    if not setup.verify_connection():
        logger.error("Cannot proceed without database connection")
        sys.exit(1)
    
    logger.info("🚀 Starting complete database setup...")
    
    success = True
    
    # Create tables
    if not setup.create_tables():
        success = False
    
    # Reset existing data
    if not setup.reset_data():
        success = False
    
    # Populate stations (1000)
    if not setup.populate_stations():
        success = False
    
    # Populate trains (1000)  
    if not setup.populate_trains():
        success = False
    
    # Create train routes
    if not setup.create_train_routes():
        success = False
    
    # Create admin user
    if not setup.create_admin_user():
        success = False
    
    # Create sample users
    if not setup.create_sample_users():
        success = False
    
    if success:
        print("\n" + "=" * 50)
        logger.info("🎉 Database setup completed successfully!")
        logger.info("📊 Created:")
        logger.info("   • 1000 Railway Stations across India")
        logger.info("   • 1000 Trains with realistic details")
        logger.info("   • Train Routes connecting stations")
        logger.info("   • Admin user (admin/admin123)")
        logger.info("   • Sample users for testing")
        logger.info("🌐 Your train booking system is ready to use!")
        print("=" * 50)
    else:
        logger.error("💥 Database setup completed with errors!")
        sys.exit(1)

if __name__ == '__main__':
    main()