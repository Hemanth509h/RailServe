#!/usr/bin/env python3
"""
RailServe Railway Reservation System - Universal Database Setup
===============================================================

This script sets up the complete RailServe database with all tables and comprehensive data.
Works in any environment - local, cloud, or production deployment.

Features:
- Creates all database tables using SQLAlchemy models
- Populates 1500 railway stations across India
- Creates 1000 trains with realistic details
- Generates comprehensive train routes
- Creates sample users, admin accounts
- Configures Tatkal time slots and quotas
- Populates food & catering data
- Creates sample bookings and test data

Usage:
    # Using environment variables
    export DATABASE_URL="postgresql://user:password@localhost:5432/railserve"
    export SESSION_SECRET="your-secret-key"
    python setup_database.py

    # Using command line arguments
    python setup_database.py --db-url postgresql://user:password@localhost:5432/railserve

Environment Variables:
    DATABASE_URL - PostgreSQL connection string
    SESSION_SECRET - Flask session secret (optional)
    ADMIN_PASSWORD - Admin user password (default: admin123)
"""

import os
import sys
import random
import logging
import argparse
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime, time, date, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the src directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from werkzeug.security import generate_password_hash
except ImportError as e:
    print(f"❌ Required dependencies not found: {e}")
    print("Please install: pip install sqlalchemy psycopg2-binary werkzeug flask flask-sqlalchemy flask-login")
    sys.exit(1)

class RailServeUniversalSetup:
    """Universal RailServe database setup for any environment"""
    
    def __init__(self, database_url: str, admin_password: Optional[str] = None):
        self.database_url = database_url
        self.admin_password = admin_password or os.environ.get('ADMIN_PASSWORD', 'admin123')
        self.engine = None
        self.Session = None
        
        # Set session secret if not already set
        if not os.environ.get('SESSION_SECRET'):
            os.environ['SESSION_SECRET'] = 'railserve-universal-secret-key-2025'
    
    def create_database_if_not_exists(self) -> bool:
        """Create the database if it doesn't exist"""
        try:
            parsed_url = urlparse(self.database_url)
            db_name = parsed_url.path[1:]  # Remove leading slash
            
            # Connect to PostgreSQL server
            logger.info("🔌 Connecting to PostgreSQL server...")
            
            # Create connection to postgres database first
            postgres_url = self.database_url.replace(f'/{db_name}', '/postgres')
            conn = psycopg2.connect(postgres_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
            exists = cursor.fetchone()
            
            if not exists:
                logger.info(f"🗄️  Creating database '{db_name}'...")
                cursor.execute(f'CREATE DATABASE "{db_name}"')
                logger.info(f"✅ Database '{db_name}' created successfully")
            else:
                logger.info(f"📄 Database '{db_name}' already exists")
            
            cursor.close()
            conn.close()
            return True
            
        except psycopg2.OperationalError as e:
            logger.error(f"❌ Database creation failed: {e}")
            logger.info("💡 Make sure PostgreSQL is running and connection details are correct")
            return False
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False
    
    def connect_database(self) -> bool:
        """Connect to the PostgreSQL database"""
        try:
            logger.info("🔌 Connecting to PostgreSQL database...")
            self.engine = create_engine(self.database_url)
            self.Session = sessionmaker(bind=self.engine)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("✅ Database connection successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
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
    
    def generate_comprehensive_stations(self) -> List[Dict[str, str]]:
        """Generate 1500 railway stations across India with realistic data"""
        logger.info("🚉 Generating 1500 railway stations across India...")
        
        # Major railway stations with real codes and names
        major_stations = [
            # Metro cities and major junctions
            {'code': 'NDLS', 'name': 'New Delhi', 'city': 'Delhi', 'state': 'Delhi'},
            {'code': 'CST', 'name': 'Chhatrapati Shivaji Terminus', 'city': 'Mumbai', 'state': 'Maharashtra'},
            {'code': 'HWH', 'name': 'Howrah Junction', 'city': 'Kolkata', 'state': 'West Bengal'},
            {'code': 'MAS', 'name': 'Chennai Central', 'city': 'Chennai', 'state': 'Tamil Nadu'},
            {'code': 'SBC', 'name': 'Bangalore City', 'city': 'Bangalore', 'state': 'Karnataka'},
            {'code': 'PUNE', 'name': 'Pune Junction', 'city': 'Pune', 'state': 'Maharashtra'},
            {'code': 'AMD', 'name': 'Ahmedabad Junction', 'city': 'Ahmedabad', 'state': 'Gujarat'},
            {'code': 'JP', 'name': 'Jaipur Junction', 'city': 'Jaipur', 'state': 'Rajasthan'},
            {'code': 'AGC', 'name': 'Agra Cantt', 'city': 'Agra', 'state': 'Uttar Pradesh'},
            {'code': 'LKO', 'name': 'Lucknow', 'city': 'Lucknow', 'state': 'Uttar Pradesh'},
            
            # State capitals and important cities
            {'code': 'BBS', 'name': 'Bhubaneswar', 'city': 'Bhubaneswar', 'state': 'Odisha'},
            {'code': 'GHY', 'name': 'Guwahati', 'city': 'Guwahati', 'state': 'Assam'},
            {'code': 'TVC', 'name': 'Trivandrum Central', 'city': 'Thiruvananthapuram', 'state': 'Kerala'},
            {'code': 'HYB', 'name': 'Hyderabad Deccan', 'city': 'Hyderabad', 'state': 'Telangana'},
            {'code': 'PNBE', 'name': 'Patna Junction', 'city': 'Patna', 'state': 'Bihar'},
            {'code': 'BPL', 'name': 'Bhopal Junction', 'city': 'Bhopal', 'state': 'Madhya Pradesh'},
            {'code': 'RNC', 'name': 'Ranchi', 'city': 'Ranchi', 'state': 'Jharkhand'},
            {'code': 'CDG', 'name': 'Chandigarh', 'city': 'Chandigarh', 'state': 'Chandigarh'},
            {'code': 'INDB', 'name': 'Indore Junction', 'city': 'Indore', 'state': 'Madhya Pradesh'},
            {'code': 'BZA', 'name': 'Vijayawada Junction', 'city': 'Vijayawada', 'state': 'Andhra Pradesh'},
        ]
        
        # Comprehensive list of Indian cities by state for realistic station generation
        indian_cities_by_state = {
            'Andhra Pradesh': ['Visakhapatnam', 'Guntur', 'Nellore', 'Kurnool', 'Rajahmundry', 'Kadapa', 'Anantapur', 'Eluru', 'Ongole', 'Nandyal'],
            'Arunachal Pradesh': ['Itanagar', 'Naharlagun', 'Pasighat', 'Tezpur', 'Bomdila', 'Ziro', 'Alongkhar', 'Roing', 'Tezu', 'Changlang'],
            'Assam': ['Dibrugarh', 'Silchar', 'Tinsukia', 'Jorhat', 'Nagaon', 'Tezpur', 'Bongaigaon', 'Karimganj', 'Sivasagar', 'Goalpara'],
            'Bihar': ['Gaya', 'Bhagalpur', 'Muzaffarpur', 'Darbhanga', 'Bihar Sharif', 'Arrah', 'Begusarai', 'Katihar', 'Munger', 'Chhapra'],
            'Chhattisgarh': ['Raipur', 'Bilaspur', 'Korba', 'Bhilai', 'Raigarh', 'Rajnandgaon', 'Jagdalpur', 'Ambikapur', 'Dhamtari', 'Mahasamund'],
            'Delhi': ['New Delhi', 'Delhi Cantt', 'Delhi Sarai Rohilla', 'Anand Vihar', 'Delhi Junction', 'Tilak Bridge', 'Delhi Shahdara', 'Nizamuddin', 'Old Delhi', 'Krishna Nagar'],
            'Goa': ['Vasco da Gama', 'Margao', 'Panaji', 'Mapusa', 'Ponda', 'Bicholim', 'Curchorem', 'Sanvordem', 'Canacona', 'Pernem'],
            'Gujarat': ['Surat', 'Vadodara', 'Rajkot', 'Bhavnagar', 'Jamnagar', 'Gandhinagar', 'Anand', 'Navsari', 'Morbi', 'Mehsana'],
            'Haryana': ['Faridabad', 'Gurgaon', 'Panipat', 'Ambala', 'Yamunanagar', 'Rohtak', 'Hisar', 'Karnal', 'Sonipat', 'Panchkula'],
            'Himachal Pradesh': ['Shimla', 'Dharamshala', 'Solan', 'Mandi', 'Palampur', 'Una', 'Kullu', 'Hamirpur', 'Bilaspur', 'Nahan'],
            'Jharkhand': ['Jamshedpur', 'Dhanbad', 'Bokaro', 'Deoghar', 'Phusro', 'Hazaribagh', 'Giridih', 'Ramgarh', 'Medininagar', 'Chirkunda'],
            'Karnataka': ['Mysore', 'Hubli', 'Mangalore', 'Belgaum', 'Davangere', 'Bellary', 'Bijapur', 'Shimoga', 'Tumkur', 'Raichur'],
            'Kerala': ['Kochi', 'Kozhikode', 'Thrissur', 'Alappuzha', 'Kollam', 'Palakkad', 'Kottayam', 'Kannur', 'Kasaragod', 'Malappuram'],
            'Madhya Pradesh': ['Indore', 'Gwalior', 'Jabalpur', 'Ujjain', 'Sagar', 'Dewas', 'Satna', 'Ratlam', 'Rewa', 'Singrauli'],
            'Maharashtra': ['Nagpur', 'Nashik', 'Aurangabad', 'Solapur', 'Amravati', 'Kolhapur', 'Akola', 'Latur', 'Dhule', 'Ahmednagar'],
            'Manipur': ['Imphal', 'Thoubal', 'Bishnupur', 'Churachandpur', 'Senapati', 'Ukhrul', 'Tamenglong', 'Chandel', 'Jiribam', 'Kakching'],
            'Meghalaya': ['Shillong', 'Tura', 'Cherrapunji', 'Jowai', 'Nongstoin', 'Baghmara', 'Ampati', 'Resubelpara', 'Mawkyrwat', 'Williamnagar'],
            'Mizoram': ['Aizawl', 'Lunglei', 'Saiha', 'Champhai', 'Kolasib', 'Serchhip', 'Lawngtlai', 'Mamit', 'Zawlnuam', 'Hnahthial'],
            'Nagaland': ['Kohima', 'Dimapur', 'Mokokchung', 'Tuensang', 'Wokha', 'Zunheboto', 'Phek', 'Kiphire', 'Longleng', 'Peren'],
            'Odisha': ['Cuttack', 'Rourkela', 'Berhampur', 'Sambalpur', 'Puri', 'Balasore', 'Bhadrak', 'Baripada', 'Jharsuguda', 'Jeypore'],
            'Punjab': ['Ludhiana', 'Amritsar', 'Jalandhar', 'Patiala', 'Bathinda', 'Mohali', 'Firozpur', 'Batala', 'Pathankot', 'Moga'],
            'Rajasthan': ['Jodhpur', 'Udaipur', 'Kota', 'Bikaner', 'Ajmer', 'Bhilwara', 'Alwar', 'Bharatpur', 'Sikar', 'Pali'],
            'Sikkim': ['Gangtok', 'Namchi', 'Geyzing', 'Mangan', 'Rangpo', 'Jorethang', 'Nayabazar', 'Singtam', 'Ranipool', 'Pakyong'],
            'Tamil Nadu': ['Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem', 'Tirunelveli', 'Erode', 'Vellore', 'Thoothukudi', 'Dindigul', 'Thanjavur'],
            'Telangana': ['Warangal', 'Nizamabad', 'Khammam', 'Karimnagar', 'Ramagundam', 'Mahbubnagar', 'Nalgonda', 'Adilabad', 'Suryapet', 'Miryalaguda'],
            'Tripura': ['Agartala', 'Dharmanagar', 'Udaipur', 'Kailashahar', 'Belonia', 'Khowai', 'Ambassa', 'Ranir Bazar', 'Sonamura', 'Sabroom'],
            'Uttar Pradesh': ['Kanpur', 'Varanasi', 'Meerut', 'Allahabad', 'Bareilly', 'Aligarh', 'Moradabad', 'Saharanpur', 'Gorakhpur', 'Firozabad'],
            'Uttarakhand': ['Dehradun', 'Haridwar', 'Roorkee', 'Haldwani', 'Rudrapur', 'Kashipur', 'Rishikesh', 'Kotdwar', 'Pithoragarh', 'Almora'],
            'West Bengal': ['Durgapur', 'Asansol', 'Siliguri', 'Barddhaman', 'Malda', 'Kharagpur', 'Haldia', 'Krishnanagar', 'Raniganj', 'Nabadwip']
        }
        
        station_types = ['Junction', 'Central', 'City', 'Cantt', 'Road', 'Terminal', 'Town', 'Nagar', 'Main', 'East', 'West', 'North', 'South']
        stations = major_stations.copy()
        
        # Track used codes and names to avoid duplicates
        used_codes = {s['code'] for s in stations}
        used_names = {s['name'] for s in stations}
        
        station_counter = 1001
        
        # Generate stations from all Indian cities
        for state, cities in indian_cities_by_state.items():
            for city in cities:
                # Generate 2-4 stations per city depending on size
                num_stations = random.randint(2, 4) if len(cities) > 5 else random.randint(1, 2)
                
                for _ in range(num_stations):
                    if len(stations) >= 1500:
                        break
                    
                    station_type = random.choice(station_types)
                    
                    # Generate unique station code
                    base_code = city[:3].upper()
                    if station_type in ['Junction', 'Central', 'Main']:
                        code = base_code[:2] + station_type[:2].upper()
                    else:
                        code = base_code + str(station_counter % 100).zfill(2)
                    
                    # Ensure uniqueness
                    attempt = 0
                    while code in used_codes and attempt < 10:
                        station_counter += 1
                        code = base_code[:2] + str(station_counter % 1000).zfill(3)
                        attempt += 1
                    
                    if code in used_codes:
                        continue
                    
                    # Generate station name
                    name = f"{city} {station_type}"
                    if name in used_names:
                        name = f"{city} {station_type} {station_counter}"
                    
                    stations.append({
                        'code': code,
                        'name': name,
                        'city': city,
                        'state': state
                    })
                    
                    used_codes.add(code)
                    used_names.add(name)
                    station_counter += 1
                
                if len(stations) >= 1500:
                    break
            
            if len(stations) >= 1500:
                break
        
        # Fill remaining slots with generated stations
        while len(stations) < 1500:
            state = random.choice(list(indian_cities_by_state.keys()))
            city = random.choice(indian_cities_by_state[state])
            station_type = random.choice(station_types)
            
            code = f"{city[:2].upper()}{station_type[:2].upper()}{station_counter % 1000:03d}"
            name = f"{city} {station_type} {station_counter}"
            
            if code not in used_codes and name not in used_names:
                stations.append({
                    'code': code,
                    'name': name,
                    'city': city,
                    'state': state
                })
                used_codes.add(code)
                used_names.add(name)
            
            station_counter += 1
        
        logger.info(f"✅ Generated {len(stations)} stations")
        return stations[:1500]
    
    def generate_comprehensive_trains(self) -> List[Dict[str, Any]]:
        """Generate 1000 trains with realistic details and variety"""
        logger.info("🚂 Generating 1000 trains with realistic details...")
        
        # Realistic train types with their characteristics
        train_types = [
            # Premium trains
            ('Rajdhani Express', 'RAJ', 18.00, 72, 22.00, 18, (12001, 12999)),
            ('Shatabdi Express', 'SHTB', 16.00, 78, 20.00, 15, (12001, 12799)),
            ('Vande Bharat Express', 'VB', 22.00, 56, 28.00, 12, (22435, 22999)),
            ('Duronto Express', 'DRN', 17.00, 90, 21.00, 20, (22201, 22999)),
            ('Tejas Express', 'TEJ', 15.50, 85, 19.50, 17, (22119, 22999)),
            
            # Express trains
            ('Superfast Express', 'SF', 12.00, 120, 15.00, 25, (11001, 19999)),
            ('Mail Express', 'MAIL', 10.50, 150, 13.00, 30, (11001, 19999)),
            ('Express', 'EXP', 8.50, 200, 11.00, 40, (11001, 19999)),
            ('Jan Shatabdi', 'JSHT', 8.00, 100, 10.50, 20, (12051, 12999)),
            ('Humsafar Express', 'HMS', 13.50, 110, 17.00, 22, (14001, 14999)),
            ('Double Decker Express', 'DD', 14.00, 120, 18.00, 24, (12273, 12999)),
            
            # Regular trains
            ('Passenger', 'PASS', 4.50, 250, 6.00, 50, (51001, 59999)),
            ('Fast Passenger', 'FPASS', 5.50, 220, 7.00, 45, (51001, 59999)),
            ('Garib Rath', 'GR', 9.50, 180, 12.00, 35, (12901, 12999)),
            ('Antyodaya Express', 'ANTD', 6.00, 240, 8.00, 48, (20501, 20999)),
            ('Jan Sadharan Express', 'JS', 7.00, 220, 9.50, 44, (20001, 20999)),
            
            # Special trains
            ('Intercity Express', 'IC', 9.00, 160, 11.50, 30, (12601, 12999)),
            ('MEMU', 'MEMU', 3.50, 300, 4.50, 60, (66001, 69999)),
            ('EMU', 'EMU', 2.50, 400, 3.50, 80, (66001, 69999)),
        ]
        
        trains = []
        used_numbers = set()
        
        for i in range(1000):
            train_type, type_code, fare_per_km, total_seats, tatkal_fare, tatkal_seats, number_range = random.choice(train_types)
            
            # Generate realistic train number within range
            attempts = 0
            while attempts < 50:
                if train_type in ['Rajdhani Express', 'Shatabdi Express']:
                    train_number = random.randint(12001, 12999)
                elif train_type == 'Duronto Express':
                    train_number = random.randint(22201, 22999)
                elif train_type == 'Vande Bharat Express':
                    train_number = random.randint(22435, 22999)
                elif 'Express' in train_type or 'Tejas' in train_type or 'Humsafar' in train_type:
                    train_number = random.randint(11001, 19999)
                elif train_type in ['Passenger', 'Fast Passenger']:
                    train_number = random.randint(51001, 59999)
                elif train_type in ['MEMU', 'EMU']:
                    train_number = random.randint(66001, 69999)
                else:
                    train_number = random.randint(number_range[0], number_range[1])
                
                if train_number not in used_numbers:
                    used_numbers.add(train_number)
                    break
                attempts += 1
            else:
                # Fallback if we can't find unique number in range
                train_number = 10001 + i
                while train_number in used_numbers:
                    train_number += 1
                used_numbers.add(train_number)
            
            # Add variation to base values
            total_seats += random.randint(-30, 30)
            total_seats = max(total_seats, 50)  # Minimum 50 seats
            
            fare_per_km += random.uniform(-2.0, 3.0)
            fare_per_km = max(fare_per_km, 2.0)  # Minimum fare
            
            tatkal_fare += random.uniform(-3.0, 4.0)
            tatkal_fare = max(tatkal_fare, fare_per_km + 2.0)  # Tatkal always higher
            
            tatkal_seats = min(tatkal_seats, total_seats // 4)  # Max 25% tatkal seats
            
            # Generate train names with variety
            route_suffixes = ['Express', 'Mail', 'Passenger', 'Special', 'Link', 'SF', 'Intercity']
            if train_type in ['Rajdhani Express', 'Shatabdi Express', 'Duronto Express', 'Vande Bharat Express']:
                name = train_type
            else:
                name = f"{random.choice(['Delhi', 'Mumbai', 'Chennai', 'Kolkata', 'Bangalore', 'Hyderabad', 'Pune', 'Ahmedabad'])} {random.choice(route_suffixes)}"
            
            trains.append({
                'number': str(train_number),
                'name': name,
                'total_seats': total_seats,
                'available_seats': total_seats,
                'fare_per_km': round(fare_per_km, 2),
                'tatkal_seats': tatkal_seats,
                'tatkal_fare_per_km': round(tatkal_fare, 2),
                'active': True,
                'created_at': datetime.utcnow()
            })
        
        logger.info(f"✅ Generated {len(trains)} trains")
        return trains
    
    def populate_stations(self, stations_data: List[Dict[str, str]]) -> bool:
        """Populate 1500 stations"""
        try:
            logger.info("🚉 Populating 1500 stations...")
            
            from src.app import app, db
            
            with app.app_context():
                created_count = 0
                batch_size = 100
                
                with db.session.begin():
                    for i in range(0, len(stations_data), batch_size):
                        batch = stations_data[i:i + batch_size]
                        
                        for station_data in batch:
                            try:
                                db.session.execute(text("""
                                    INSERT INTO station (code, name, city, state, active, created_at) 
                                    VALUES (:code, :name, :city, :state, true, :created_at)
                                    ON CONFLICT (code) DO UPDATE SET 
                                        name = EXCLUDED.name,
                                        city = EXCLUDED.city,
                                        state = EXCLUDED.state,
                                        active = true
                                """), {**station_data, 'created_at': datetime.utcnow()})
                                created_count += 1
                            except Exception as e:
                                logger.warning(f"Failed to insert station {station_data.get('code')}: {e}")
                                continue
                        
                        if i % 500 == 0:
                            logger.info(f"📍 Processed {min(i + batch_size, len(stations_data))} stations...")
                
                logger.info(f"✅ Stations populated successfully: {created_count} stations")
                return True
                
        except Exception as e:
            logger.error(f"❌ Station population failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def populate_trains(self, trains_data: List[Dict[str, Any]]) -> bool:
        """Populate 1000 trains"""
        try:
            logger.info("🚂 Populating 1000 trains...")
            
            from src.app import app, db
            
            with app.app_context():
                created_count = 0
                batch_size = 50
                
                with db.session.begin():
                    for i in range(0, len(trains_data), batch_size):
                        batch = trains_data[i:i + batch_size]
                        
                        for train_data in batch:
                            try:
                                db.session.execute(text("""
                                    INSERT INTO train (number, name, total_seats, available_seats, fare_per_km, 
                                                     tatkal_seats, tatkal_fare_per_km, active, created_at) 
                                    VALUES (:number, :name, :total_seats, :available_seats, :fare_per_km,
                                           :tatkal_seats, :tatkal_fare_per_km, :active, :created_at)
                                    ON CONFLICT (number) DO UPDATE SET
                                        name = EXCLUDED.name,
                                        total_seats = EXCLUDED.total_seats,
                                        available_seats = EXCLUDED.available_seats,
                                        fare_per_km = EXCLUDED.fare_per_km,
                                        tatkal_seats = EXCLUDED.tatkal_seats,
                                        tatkal_fare_per_km = EXCLUDED.tatkal_fare_per_km,
                                        active = EXCLUDED.active
                                """), train_data)
                                created_count += 1
                            except Exception as e:
                                logger.warning(f"Failed to insert train {train_data.get('number')}: {e}")
                                continue
                        
                        if i % 200 == 0:
                            logger.info(f"🚂 Processed {min(i + batch_size, len(trains_data))} trains...")
                
                logger.info(f"✅ Trains populated successfully: {created_count} trains")
                return True
                
        except Exception as e:
            logger.error(f"❌ Train population failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_comprehensive_routes(self) -> bool:
        """Create comprehensive train routes connecting stations"""
        try:
            logger.info("🛤️  Creating comprehensive train routes...")
            
            from src.app import app, db
            
            with app.app_context():
                # Get all stations and trains
                stations = db.session.execute(text("SELECT id, code, name, city, state FROM station ORDER BY id")).fetchall()
                trains = db.session.execute(text("SELECT id, number, name FROM train ORDER BY id")).fetchall()
                
                logger.info(f"📊 Creating routes for {len(trains)} trains using {len(stations)} stations")
                
                route_count = 0
                batch_size = 100
                routes_batch = []
                
                # Create routes for each train
                for train in trains:
                    # Select 3-8 stations per route for variety
                    num_stations = random.randint(3, 8)
                    route_stations = random.sample(list(stations), num_stations)
                    
                    # Sort by geographical logic (state, then city)
                    route_stations = sorted(route_stations, key=lambda x: (x.state, x.city))
                    
                    total_distance = 0
                    # Start time between 4 AM and 11 PM
                    start_hour = random.randint(4, 23)
                    current_time = time(hour=start_hour, minute=random.choice([0, 15, 30, 45]))
                    
                    for sequence, station in enumerate(route_stations, 1):
                        # Calculate distance
                        if sequence == 1:
                            distance_from_start = 0.0
                        else:
                            # Distance between stations: 50-300 km
                            distance_increment = random.uniform(50, 300)
                            total_distance += distance_increment
                            distance_from_start = total_distance
                        
                        # Calculate times
                        if sequence == 1:
                            # First station - departure only
                            arrival_time = None
                            departure_time = current_time
                        elif sequence == len(route_stations):
                            # Last station - arrival only
                            travel_time_minutes = random.randint(45, 120)
                            current_datetime = datetime.combine(date.today(), current_time)
                            arrival_datetime = current_datetime + timedelta(minutes=travel_time_minutes)
                            arrival_time = arrival_datetime.time()
                            departure_time = None
                        else:
                            # Intermediate station
                            travel_time_minutes = random.randint(30, 90)
                            current_datetime = datetime.combine(date.today(), current_time)
                            arrival_datetime = current_datetime + timedelta(minutes=travel_time_minutes)
                            arrival_time = arrival_datetime.time()
                            
                            # Stop duration: 2-15 minutes
                            stop_duration = random.choice([2, 5, 10, 15])
                            departure_datetime = arrival_datetime + timedelta(minutes=stop_duration)
                            departure_time = departure_datetime.time()
                            current_time = departure_time
                        
                        routes_batch.append({
                            'train_id': train.id,
                            'station_id': station.id,
                            'sequence': sequence,
                            'arrival_time': arrival_time,
                            'departure_time': departure_time,
                            'distance_from_start': round(distance_from_start, 2)
                        })
                        
                        route_count += 1
                        
                        # Batch insert
                        if len(routes_batch) >= batch_size:
                            self._insert_route_batch(routes_batch)
                            routes_batch = []
                    
                    if len(routes_batch) > 0 and route_count % 1000 == 0:
                        self._insert_route_batch(routes_batch)
                        routes_batch = []
                        logger.info(f"🛤️  Created {route_count} route entries...")
                
                # Insert remaining routes
                if routes_batch:
                    self._insert_route_batch(routes_batch)
                
                logger.info(f"✅ Train routes created successfully: {route_count} route entries")
                return True
                
        except Exception as e:
            logger.error(f"❌ Route creation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _insert_route_batch(self, routes_batch):
        """Helper method to insert route batch"""
        from src.app import app, db
        
        try:
            with db.session.begin():
                for route in routes_batch:
                    db.session.execute(text("""
                        INSERT INTO train_route (train_id, station_id, sequence, arrival_time, departure_time, distance_from_start)
                        VALUES (:train_id, :station_id, :sequence, :arrival_time, :departure_time, :distance_from_start)
                        ON CONFLICT (train_id, sequence) DO UPDATE SET
                            station_id = EXCLUDED.station_id,
                            arrival_time = EXCLUDED.arrival_time,
                            departure_time = EXCLUDED.departure_time,
                            distance_from_start = EXCLUDED.distance_from_start
                    """), route)
        except Exception as e:
            logger.warning(f"Failed to insert route batch: {e}")
    
    def populate_comprehensive_data(self) -> bool:
        """Populate comprehensive additional data"""
        try:
            logger.info("📊 Populating comprehensive additional data...")
            
            from src.app import app, db
            from src.models import User, TatkalTimeSlot, Restaurant, MenuItem
            
            with app.app_context():
                # Create admin and sample users
                admin_user = User.query.filter_by(username='admin').first()
                if not admin_user:
                    admin_user = User(
                        username='admin',
                        email='admin@railserve.com',
                        password_hash=generate_password_hash(self.admin_password),
                        role='super_admin',
                        active=True
                    )
                    db.session.add(admin_user)
                    logger.info(f"👤 Created admin user (username: admin, password: {self.admin_password})")
                
                # Create sample regular users
                sample_users = [
                    {'username': 'user1', 'email': 'user1@example.com', 'password': 'password123'},
                    {'username': 'user2', 'email': 'user2@example.com', 'password': 'password123'},
                    {'username': 'testuser', 'email': 'test@example.com', 'password': 'test123'},
                ]
                
                for user_data in sample_users:
                    if not User.query.filter_by(username=user_data['username']).first():
                        user = User(
                            username=user_data['username'],
                            email=user_data['email'],
                            password_hash=generate_password_hash(user_data['password']),
                            role='user',
                            active=True
                        )
                        db.session.add(user)
                
                # Create Tatkal time slots
                if TatkalTimeSlot.query.count() == 0:
                    tatkal_slots = [
                        {
                            'name': 'AC Classes Tatkal',
                            'coach_classes': 'AC1,AC2,AC3,CC',
                            'open_time': time(10, 0),
                            'days_before_journey': 1,
                            'active': True,
                            'created_by': admin_user.id
                        },
                        {
                            'name': 'Non-AC Classes Tatkal',
                            'coach_classes': 'SL,2S',
                            'open_time': time(11, 0),
                            'days_before_journey': 1,
                            'active': True,
                            'created_by': admin_user.id
                        },
                        {
                            'name': 'Premium Tatkal',
                            'coach_classes': 'AC1,AC2',
                            'open_time': time(10, 0),
                            'days_before_journey': 1,
                            'active': True,
                            'created_by': admin_user.id
                        }
                    ]
                    
                    for slot_data in tatkal_slots:
                        slot = TatkalTimeSlot(**slot_data)
                        db.session.add(slot)
                    
                    logger.info(f"⏰ Created {len(tatkal_slots)} Tatkal time slots")
                
                # Create sample restaurants and food data
                if Restaurant.query.count() == 0:
                    # Get some stations for restaurants
                    major_stations = db.session.execute(text("""
                        SELECT id, name FROM station 
                        WHERE city IN ('Delhi', 'Mumbai', 'Chennai', 'Kolkata', 'Bangalore', 'Hyderabad', 'Pune', 'Ahmedabad')
                        LIMIT 20
                    """)).fetchall()
                    
                    restaurant_names = [
                        'Rajdhani Foods', 'South Express Kitchen', 'Mumbai Tiffin Center', 'Bengal Delights',
                        'Karnataka Cuisine', 'Telangana Tastes', 'Pune Pantry', 'Gujarat Gujari',
                        'Railway Refreshments', 'Express Eatery', 'Junction Junctions', 'Platform Plates',
                        'Coach Cafe', 'Train Track Treats', 'Station Snacks', 'Rail Restaurant'
                    ]
                    
                    for i, station in enumerate(major_stations):
                        restaurant = Restaurant(
                            name=restaurant_names[i % len(restaurant_names)],
                            station_id=station.id,
                            contact_number=f"98765{10000 + i:05d}",
                            email=f"restaurant{i}@railserve.com",
                            cuisine_type=random.choice(['North Indian', 'South Indian', 'Continental', 'Chinese', 'Multi-cuisine']),
                            rating=random.uniform(3.5, 5.0),
                            delivery_time=random.randint(15, 45),
                            minimum_order=random.uniform(50, 150),
                            delivery_charge=random.uniform(10, 30),
                            active=True
                        )
                        db.session.add(restaurant)
                        db.session.flush()
                        
                        # Add menu items for each restaurant
                        menu_items = [
                            {'name': 'Veg Thali', 'price': 120, 'category': 'Lunch', 'food_type': 'Vegetarian'},
                            {'name': 'Chicken Biryani', 'price': 180, 'category': 'Lunch', 'food_type': 'Non-Vegetarian'},
                            {'name': 'Masala Dosa', 'price': 80, 'category': 'Breakfast', 'food_type': 'Vegetarian'},
                            {'name': 'Tea', 'price': 15, 'category': 'Beverages', 'food_type': 'Vegetarian'},
                            {'name': 'Coffee', 'price': 20, 'category': 'Beverages', 'food_type': 'Vegetarian'},
                            {'name': 'Sandwich', 'price': 60, 'category': 'Snacks', 'food_type': 'Vegetarian'},
                        ]
                        
                        for item_data in menu_items:
                            menu_item = MenuItem(
                                restaurant_id=restaurant.id,
                                name=item_data['name'],
                                description=f"Delicious {item_data['name']} from {restaurant.name}",
                                price=item_data['price'],
                                category=item_data['category'],
                                food_type=item_data['food_type'],
                                preparation_time=random.randint(10, 30),
                                available=True,
                                is_popular=random.choice([True, False])
                            )
                            db.session.add(menu_item)
                    
                    logger.info(f"🍽️ Created {len(major_stations)} restaurants with menu items")
                
                db.session.commit()
                logger.info("✅ Comprehensive additional data populated successfully")
                return True
                
        except Exception as e:
            logger.error(f"❌ Additional data population failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify_setup(self) -> bool:
        """Verify the comprehensive database setup"""
        try:
            logger.info("🔍 Verifying comprehensive database setup...")
            
            from src.app import app, db
            from src.models import User, Station, Train, TrainRoute, TatkalTimeSlot, Restaurant
            
            with app.app_context():
                # Check table counts
                user_count = User.query.count()
                station_count = Station.query.count()
                train_count = Train.query.count()
                route_count = TrainRoute.query.count()
                tatkal_count = TatkalTimeSlot.query.count()
                restaurant_count = Restaurant.query.count()
                
                logger.info(f"📊 Database verification:")
                logger.info(f"   Users: {user_count}")
                logger.info(f"   Stations: {station_count}")
                logger.info(f"   Trains: {train_count}")
                logger.info(f"   Train Routes: {route_count}")
                logger.info(f"   Tatkal Slots: {tatkal_count}")
                logger.info(f"   Restaurants: {restaurant_count}")
                
                # Check admin user
                admin_user = User.query.filter_by(username='admin').first()
                if admin_user and admin_user.role == 'super_admin':
                    logger.info("✅ Admin user verified")
                else:
                    logger.warning("⚠️  Admin user not found or incorrect role")
                
                # Check data completeness
                success = (user_count >= 1 and station_count >= 1400 and 
                          train_count >= 900 and route_count >= 3000)
                
                if success:
                    logger.info("✅ Database setup verification completed successfully")
                else:
                    logger.warning("⚠️  Database setup verification found issues")
                
                return success
                
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return False
    
    def run_complete_setup(self) -> bool:
        """Run the complete comprehensive database setup"""
        logger.info("🚀 Starting RailServe comprehensive database setup...")
        
        # Step 1: Create database if needed
        if not self.create_database_if_not_exists():
            return False
        
        # Step 2: Connect to database
        if not self.connect_database():
            return False
        
        # Step 3: Create tables
        if not self.create_tables():
            return False
        
        # Step 4: Generate and populate stations
        stations_data = self.generate_comprehensive_stations()
        if not self.populate_stations(stations_data):
            return False
        
        # Step 5: Generate and populate trains
        trains_data = self.generate_comprehensive_trains()
        if not self.populate_trains(trains_data):
            return False
        
        # Step 6: Create train routes
        if not self.create_comprehensive_routes():
            return False
        
        # Step 7: Populate additional data
        if not self.populate_comprehensive_data():
            return False
        
        # Step 8: Verify setup
        if not self.verify_setup():
            return False
        
        logger.info("🎉 RailServe comprehensive database setup completed successfully!")
        logger.info("📝 Setup Summary:")
        logger.info("   • 1500 railway stations across India")
        logger.info("   • 1000 trains with realistic details")
        logger.info("   • Comprehensive train routes")
        logger.info("   • Admin and sample user accounts")
        logger.info("   • Tatkal booking configuration")
        logger.info("   • Food & catering data")
        logger.info("   • Complete railway reservation system")
        logger.info("")
        logger.info("🔑 Login credentials:")
        logger.info(f"   Admin: username='admin', password='{self.admin_password}'")
        logger.info("   User: username='testuser', password='test123'")
        logger.info("")
        logger.info("📱 Next steps:")
        logger.info("   1. Start your Flask application")
        logger.info("   2. Configure web server settings")
        logger.info("   3. Set up production environment")
        
        return True

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='RailServe Universal Database Setup')
    parser.add_argument('--db-url', type=str, help='Database URL (overrides DATABASE_URL env var)')
    parser.add_argument('--admin-password', type=str, default='admin123', help='Admin user password')
    parser.add_argument('--skip-create-db', action='store_true', help='Skip database creation step')
    return parser.parse_args()

def main():
    """Main function to run the setup"""
    args = parse_arguments()
    
    # Get database URL from args or environment
    database_url = args.db_url or os.environ.get('DATABASE_URL')
    
    if not database_url:
        logger.error("❌ Database URL not provided")
        logger.info("Please provide database URL via:")
        logger.info("  1. Environment variable: export DATABASE_URL='postgresql://user:password@localhost:5432/railserve'")
        logger.info("  2. Command line argument: --db-url postgresql://user:password@localhost:5432/railserve")
        sys.exit(1)
    
    setup = RailServeUniversalSetup(database_url, args.admin_password)
    
    try:
        success = setup.run_complete_setup()
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