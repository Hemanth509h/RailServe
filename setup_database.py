#!/usr/bin/env python3
"""
RailServe Railway Reservation System - Complete Database Setup
==============================================================

This script sets up the complete RailServe database with all tables and comprehensive data.
Works in any environment - local, cloud, or production deployment.

Database Tables Created:
- user: User authentication and role management
- station: Railway stations (1500+ stations across India)
- train: Train information with Tatkal support (1000+ trains)
- train_route: Train route mapping with stations and timing
- booking: Comprehensive booking system with quotas and status
- passenger: Detailed passenger information
- payment: Payment processing and transaction management
- waitlist: Waitlist management with position tracking
- tatkal_time_slot: Tatkal booking time configuration
- refund_request: TDR filing and refund management
- train_status: Live train status tracking
- seat_availability: Real-time seat availability
- chart_preparation: Chart preparation tracking
- restaurant: Food & catering partners
- menu_item: Food menu items
- food_order: Food orders linked to bookings
- food_order_item: Individual food order items
- group_booking: Group booking management
- loyalty_program: Frequent traveler loyalty program
- notification_preferences: User notification settings

Features Supported:
- Complete authentication system with role-based access
- Tatkal booking with real Indian Railways timing rules
- Group bookings for families and corporate travel
- Food ordering system integrated with train bookings
- Loyalty program with tier-based discounts
- Waitlist management with FIFO queuing
- PDF ticket generation support
- Real-time train status and seat availability
- TDR filing and refund processing
- Comprehensive booking quotas (General, Ladies, Senior Citizen, Disability)

Usage:
    # Using environment variables
    export DATABASE_URL="postgresql://user:password@localhost:5432/railserve"
    export SESSION_SECRET="your-secret-key"
    python setup_database.py

    # Using command line arguments
    python setup_database.py --db-url postgresql://user:password@localhost:5432/railserve

    # With custom admin password
    export ADMIN_PASSWORD="your-admin-password"
    python setup_database.py

Environment Variables:
    DATABASE_URL - PostgreSQL connection string
    SESSION_SECRET - Flask session secret (auto-generated if not set)
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

class RailServeCompleteSetup:
    """Complete RailServe database setup for any environment"""
    
    def __init__(self, database_url: str, admin_password: Optional[str] = None):
        self.database_url = database_url
        self.admin_password = admin_password or os.environ.get('ADMIN_PASSWORD', 'admin123')
        self.engine = None
        self.Session = None
        
        # Set session secret if not already set
        if not os.environ.get('SESSION_SECRET'):
            os.environ['SESSION_SECRET'] = 'railserve-complete-secret-key-2025'
    
    def create_database_if_not_exists(self) -> bool:
        """Create the database if it doesn't exist"""
        try:
            parsed_url = urlparse(self.database_url)
            db_name = parsed_url.path[1:]  # Remove leading slash
            
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
            self.engine = create_engine(
                self.database_url,
                pool_recycle=300,
                pool_pre_ping=True,
                echo=False
            )
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
            
            # Set the DATABASE_URL environment variable for Flask app
            os.environ['DATABASE_URL'] = self.database_url
            
            # Import Flask app to trigger table creation
            from app import app, db
            
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
        logger.info("🚉 Generating 1500+ railway stations across India...")
        
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
        """Generate 1000+ trains with realistic details and variety"""
        logger.info("🚂 Generating 1000+ trains with realistic details...")
        
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
        """Populate stations"""
        try:
            logger.info(f"🚉 Populating {len(stations_data)} stations...")
            
            # Set the DATABASE_URL environment variable for Flask app
            os.environ['DATABASE_URL'] = self.database_url
            
            from app import app, db
            
            with app.app_context():
                created_count = 0
                batch_size = 100
                
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
                    
                    db.session.commit()
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
        """Populate trains"""
        try:
            logger.info(f"🚂 Populating {len(trains_data)} trains...")
            
            # Set the DATABASE_URL environment variable for Flask app
            os.environ['DATABASE_URL'] = self.database_url
            
            from app import app, db
            
            with app.app_context():
                created_count = 0
                batch_size = 100
                
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
                                    active = true
                            """), train_data)
                            created_count += 1
                        except Exception as e:
                            logger.warning(f"Failed to insert train {train_data.get('number')}: {e}")
                            continue
                    
                    db.session.commit()
                    if i % 500 == 0:
                        logger.info(f"🚂 Processed {min(i + batch_size, len(trains_data))} trains...")
                
                logger.info(f"✅ Trains populated successfully: {created_count} trains")
                return True
                
        except Exception as e:
            logger.error(f"❌ Train population failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_train_routes(self) -> bool:
        """Create realistic train routes connecting stations"""
        try:
            logger.info("🛤️  Creating train routes...")
            
            # Set the DATABASE_URL environment variable for Flask app
            os.environ['DATABASE_URL'] = self.database_url
            
            from app import app, db
            
            with app.app_context():
                # Get all stations and trains
                stations = db.session.execute(text("SELECT id, code, name, city FROM station ORDER BY id")).fetchall()
                trains = db.session.execute(text("SELECT id, number, name FROM train ORDER BY id")).fetchall()
                
                if not stations or not trains:
                    logger.error("❌ No stations or trains found")
                    return False
                
                station_list = [{'id': s[0], 'code': s[1], 'name': s[2], 'city': s[3]} for s in stations]
                train_list = [{'id': t[0], 'number': t[1], 'name': t[2]} for t in trains]
                
                routes_created = 0
                
                # Create routes for each train
                for train in train_list[:500]:  # Create routes for first 500 trains to keep it manageable
                    try:
                        # Select 3-10 stations randomly for each train route
                        num_stations = random.randint(3, 10)
                        selected_stations = random.sample(station_list, num_stations)
                        
                        # Sort stations to create a logical route
                        route_stations = sorted(selected_stations, key=lambda x: x['id'])
                        
                        current_distance = 0
                        base_time = datetime.strptime("06:00", "%H:%M").time()
                        
                        for seq, station in enumerate(route_stations):
                            if seq > 0:
                                # Add distance (50-200 km between stations)
                                current_distance += random.randint(50, 200)
                            
                            # Calculate arrival and departure times
                            if seq == 0:
                                # First station - only departure
                                arrival_time = None
                                departure_time = base_time
                            elif seq == len(route_stations) - 1:
                                # Last station - only arrival
                                minutes_to_add = (seq * 45) + random.randint(0, 30)
                                arrival_time = (datetime.combine(date.today(), base_time) + 
                                              timedelta(minutes=minutes_to_add)).time()
                                departure_time = None
                            else:
                                # Intermediate station - both arrival and departure
                                minutes_to_add = (seq * 45) + random.randint(0, 30)
                                arrival_time = (datetime.combine(date.today(), base_time) + 
                                              timedelta(minutes=minutes_to_add)).time()
                                departure_time = (datetime.combine(date.today(), arrival_time) + 
                                                timedelta(minutes=random.randint(2, 10))).time()
                            
                            db.session.execute(text("""
                                INSERT INTO train_route (train_id, station_id, sequence, arrival_time, 
                                                        departure_time, distance_from_start)
                                VALUES (:train_id, :station_id, :sequence, :arrival_time, 
                                       :departure_time, :distance_from_start)
                                ON CONFLICT (train_id, sequence) DO NOTHING
                            """), {
                                'train_id': train['id'],
                                'station_id': station['id'],
                                'sequence': seq + 1,
                                'arrival_time': arrival_time,
                                'departure_time': departure_time,
                                'distance_from_start': current_distance
                            })
                            routes_created += 1
                        
                        if routes_created % 100 == 0:
                            db.session.commit()
                            logger.info(f"🛤️  Created {routes_created} route entries...")
                            
                    except Exception as e:
                        logger.warning(f"Failed to create route for train {train['number']}: {e}")
                        continue
                
                db.session.commit()
                logger.info(f"✅ Train routes created successfully: {routes_created} route entries")
                return True
                
        except Exception as e:
            logger.error(f"❌ Train route creation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_sample_users(self) -> bool:
        """Create sample users including admin accounts"""
        try:
            logger.info("👤 Creating sample users...")
            
            # Set the DATABASE_URL environment variable for Flask app
            os.environ['DATABASE_URL'] = self.database_url
            
            from app import app, db
            
            with app.app_context():
                users_data = [
                    {
                        'username': 'admin',
                        'email': 'admin@railserve.com',
                        'password_hash': generate_password_hash(self.admin_password),
                        'role': 'super_admin',
                        'active': True,
                        'created_at': datetime.utcnow()
                    },
                    {
                        'username': 'manager',
                        'email': 'manager@railserve.com', 
                        'password_hash': generate_password_hash('manager123'),
                        'role': 'admin',
                        'active': True,
                        'created_at': datetime.utcnow()
                    },
                    {
                        'username': 'testuser',
                        'email': 'user@test.com',
                        'password_hash': generate_password_hash('test123'),
                        'role': 'user',
                        'active': True,
                        'created_at': datetime.utcnow()
                    },
                    {
                        'username': 'demo',
                        'email': 'demo@railserve.com',
                        'password_hash': generate_password_hash('demo123'),
                        'role': 'user',
                        'active': True,
                        'created_at': datetime.utcnow()
                    }
                ]
                
                created_count = 0
                for user_data in users_data:
                    try:
                        db.session.execute(text("""
                            INSERT INTO "user" (username, email, password_hash, role, active, created_at)
                            VALUES (:username, :email, :password_hash, :role, :active, :created_at)
                            ON CONFLICT (username) DO UPDATE SET
                                email = EXCLUDED.email,
                                password_hash = EXCLUDED.password_hash,
                                role = EXCLUDED.role,
                                active = EXCLUDED.active
                        """), user_data)
                        created_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to insert user {user_data.get('username')}: {e}")
                        continue
                
                db.session.commit()
                logger.info(f"✅ Users created successfully: {created_count} users")
                logger.info(f"🔑 Admin credentials: admin / {self.admin_password}")
                return True
                
        except Exception as e:
            logger.error(f"❌ User creation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def setup_tatkal_configuration(self) -> bool:
        """Setup Tatkal time slot configuration"""
        try:
            logger.info("⏰ Setting up Tatkal booking configuration...")
            
            # Set the DATABASE_URL environment variable for Flask app
            os.environ['DATABASE_URL'] = self.database_url
            
            from app import app, db
            
            with app.app_context():
                # Get admin user ID
                admin_user = db.session.execute(text("""
                    SELECT id FROM "user" WHERE role = 'super_admin' LIMIT 1
                """)).fetchone()
                
                if not admin_user:
                    logger.warning("No admin user found, creating Tatkal slots without creator")
                    admin_id = None
                else:
                    admin_id = admin_user[0]
                
                tatkal_slots = [
                    {
                        'name': 'AC Classes Tatkal',
                        'coach_classes': 'AC1,AC2,AC3,CC',
                        'open_time': time(10, 0),  # 10:00 AM
                        'close_time': None,
                        'days_before_journey': 1,
                        'active': True,
                        'created_at': datetime.utcnow(),
                        'created_by': admin_id
                    },
                    {
                        'name': 'Non-AC Classes Tatkal',
                        'coach_classes': 'SL,2S',
                        'open_time': time(11, 0),  # 11:00 AM
                        'close_time': None,
                        'days_before_journey': 1,
                        'active': True,
                        'created_at': datetime.utcnow(),
                        'created_by': admin_id
                    }
                ]
                
                created_count = 0
                for slot_data in tatkal_slots:
                    try:
                        db.session.execute(text("""
                            INSERT INTO tatkal_time_slot (name, coach_classes, open_time, close_time,
                                                        days_before_journey, active, created_at, created_by)
                            VALUES (:name, :coach_classes, :open_time, :close_time,
                                   :days_before_journey, :active, :created_at, :created_by)
                            ON CONFLICT (name) DO UPDATE SET
                                coach_classes = EXCLUDED.coach_classes,
                                open_time = EXCLUDED.open_time,
                                close_time = EXCLUDED.close_time,
                                days_before_journey = EXCLUDED.days_before_journey,
                                active = EXCLUDED.active
                        """), slot_data)
                        created_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to insert Tatkal slot {slot_data.get('name')}: {e}")
                        continue
                
                db.session.commit()
                logger.info(f"✅ Tatkal configuration created: {created_count} time slots")
                return True
                
        except Exception as e:
            logger.error(f"❌ Tatkal configuration failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_sample_restaurants(self) -> bool:
        """Create sample restaurants and menu items"""
        try:
            logger.info("🍽️  Creating sample restaurants and menu items...")
            
            # Set the DATABASE_URL environment variable for Flask app
            os.environ['DATABASE_URL'] = self.database_url
            
            from app import app, db
            
            with app.app_context():
                # Get some stations for restaurants
                stations = db.session.execute(text("""
                    SELECT id, name, city FROM station 
                    WHERE city IN ('Delhi', 'Mumbai', 'Chennai', 'Kolkata', 'Bangalore', 'Hyderabad', 'Pune', 'Ahmedabad')
                    LIMIT 20
                """)).fetchall()
                
                if not stations:
                    logger.warning("No major stations found, skipping restaurant creation")
                    return True
                
                station_list = [{'id': s[0], 'name': s[1], 'city': s[2]} for s in stations]
                
                restaurants_created = 0
                menu_items_created = 0
                
                restaurant_types = [
                    ('Vegetarian Paradise', 'Vegetarian', 4.2),
                    ('Spice Route', 'Both', 4.0),
                    ('Healthy Bites', 'Vegetarian', 4.5),
                    ('Royal Kitchen', 'Both', 4.3),
                    ('Quick Meals', 'Both', 3.8),
                    ('Traditional Tastes', 'Vegetarian', 4.1),
                    ('Express Dine', 'Both', 3.9),
                    ('Fresh N Fast', 'Vegetarian', 4.4)
                ]
                
                menu_categories = {
                    'Breakfast': ['Idli Sambar', 'Dosa', 'Poha', 'Upma', 'Paratha', 'Bread Omelette'],
                    'Lunch': ['Rice & Dal', 'Biryani', 'Thali', 'Roti Sabji', 'Fried Rice', 'Rajma Rice'],
                    'Dinner': ['Paneer Butter Masala', 'Dal Makhani', 'Chicken Curry', 'Fish Fry', 'Mutton Biryani', 'Veg Biryani'],
                    'Snacks': ['Samosa', 'Pakora', 'Sandwich', 'Burger', 'Pizza', 'Chaat'],
                    'Beverages': ['Tea', 'Coffee', 'Fresh Juice', 'Lassi', 'Cold Drink', 'Water Bottle']
                }
                
                for station in station_list:
                    # Create 1-2 restaurants per station
                    num_restaurants = random.randint(1, 2)
                    
                    for _ in range(num_restaurants):
                        restaurant_name, cuisine_type, base_rating = random.choice(restaurant_types)
                        restaurant_name = f"{restaurant_name} - {station['city']}"
                        
                        restaurant_data = {
                            'name': restaurant_name,
                            'station_id': station['id'],
                            'contact_number': f"+91{random.randint(9000000000, 9999999999)}",
                            'email': f"contact@{restaurant_name.lower().replace(' ', '').replace('-', '')}.com",
                            'cuisine_type': cuisine_type,
                            'rating': round(base_rating + random.uniform(-0.3, 0.3), 1),
                            'delivery_time': random.randint(20, 45),
                            'minimum_order': random.choice([0, 50, 100, 150]),
                            'delivery_charge': random.choice([0, 10, 20, 30]),
                            'active': True,
                            'created_at': datetime.utcnow()
                        }
                        
                        try:
                            result = db.session.execute(text("""
                                INSERT INTO restaurant (name, station_id, contact_number, email, cuisine_type,
                                                      rating, delivery_time, minimum_order, delivery_charge, 
                                                      active, created_at)
                                VALUES (:name, :station_id, :contact_number, :email, :cuisine_type,
                                       :rating, :delivery_time, :minimum_order, :delivery_charge, 
                                       :active, :created_at)
                                RETURNING id
                            """), restaurant_data)
                            
                            restaurant_id = result.fetchone()[0]
                            restaurants_created += 1
                            
                            # Create menu items for this restaurant
                            for category, items in menu_categories.items():
                                num_items = random.randint(1, 3)
                                selected_items = random.sample(items, min(num_items, len(items)))
                                
                                for item_name in selected_items:
                                    base_price = {
                                        'Breakfast': random.randint(30, 80),
                                        'Lunch': random.randint(80, 200),
                                        'Dinner': random.randint(100, 300),
                                        'Snacks': random.randint(20, 100),
                                        'Beverages': random.randint(15, 60)
                                    }.get(category, 50)
                                    
                                    menu_item_data = {
                                        'restaurant_id': restaurant_id,
                                        'name': item_name,
                                        'description': f"Delicious {item_name} prepared fresh",
                                        'price': base_price + random.randint(-10, 20),
                                        'category': category,
                                        'food_type': 'Vegetarian' if cuisine_type == 'Vegetarian' else random.choice(['Vegetarian', 'Non-Vegetarian']),
                                        'preparation_time': random.randint(10, 30),
                                        'available': True,
                                        'is_popular': random.choice([True, False]),
                                        'created_at': datetime.utcnow()
                                    }
                                    
                                    db.session.execute(text("""
                                        INSERT INTO menu_item (restaurant_id, name, description, price, category,
                                                             food_type, preparation_time, available, is_popular, created_at)
                                        VALUES (:restaurant_id, :name, :description, :price, :category,
                                               :food_type, :preparation_time, :available, :is_popular, :created_at)
                                    """), menu_item_data)
                                    menu_items_created += 1
                            
                        except Exception as e:
                            logger.warning(f"Failed to create restaurant {restaurant_name}: {e}")
                            continue
                
                db.session.commit()
                logger.info(f"✅ Restaurants created: {restaurants_created} restaurants, {menu_items_created} menu items")
                return True
                
        except Exception as e:
            logger.error(f"❌ Restaurant creation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_complete_setup(self) -> bool:
        """Run the complete database setup process"""
        logger.info("🚀 Starting RailServe Complete Database Setup")
        logger.info("=" * 60)
        
        steps = [
            ("Create Database", self.create_database_if_not_exists),
            ("Connect to Database", self.connect_database),
            ("Create All Tables", self.create_tables),
            ("Generate Stations Data", lambda: setattr(self, '_stations_data', self.generate_comprehensive_stations()) or True),
            ("Populate Stations", lambda: self.populate_stations(self._stations_data)),
            ("Generate Trains Data", lambda: setattr(self, '_trains_data', self.generate_comprehensive_trains()) or True),
            ("Populate Trains", lambda: self.populate_trains(self._trains_data)),
            ("Create Train Routes", self.create_train_routes),
            ("Create Sample Users", self.create_sample_users),
            ("Setup Tatkal Configuration", self.setup_tatkal_configuration),
            ("Create Sample Restaurants", self.create_sample_restaurants)
        ]
        
        for step_name, step_function in steps:
            logger.info(f"📋 {step_name}...")
            try:
                if not step_function():
                    logger.error(f"❌ {step_name} failed")
                    return False
                logger.info(f"✅ {step_name} completed")
            except Exception as e:
                logger.error(f"❌ {step_name} failed with error: {e}")
                return False
        
        logger.info("=" * 60)
        logger.info("🎉 RailServe Complete Database Setup Completed Successfully!")
        logger.info("Database Features Available:")
        logger.info("  • User authentication (admin/manager/user roles)")
        logger.info("  • 1500+ Railway stations across India")
        logger.info("  • 1000+ Trains with realistic details")
        logger.info("  • Comprehensive train routes")
        logger.info("  • Tatkal booking with real timing rules")
        logger.info("  • Group booking system")
        logger.info("  • Food ordering system")
        logger.info("  • Loyalty program")
        logger.info("  • Waitlist management")
        logger.info("  • Payment processing")
        logger.info("  • PDF ticket generation support")
        logger.info("  • Real-time status tracking")
        logger.info(f"🔑 Admin Login: admin / {self.admin_password}")
        logger.info("=" * 60)
        
        return True

def main():
    """Main function to run the setup"""
    parser = argparse.ArgumentParser(description='RailServe Complete Database Setup')
    parser.add_argument('--db-url', help='Database URL (overrides DATABASE_URL env var)')
    parser.add_argument('--admin-password', help='Admin password (overrides ADMIN_PASSWORD env var)')
    
    args = parser.parse_args()
    
    # Get database URL
    database_url = args.db_url or os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ Database URL not provided")
        print("Set DATABASE_URL environment variable or use --db-url argument")
        print("Example: postgresql://user:password@localhost:5432/railserve")
        sys.exit(1)
    
    # Get admin password
    admin_password = args.admin_password or os.environ.get('ADMIN_PASSWORD')
    
    # Run setup
    setup = RailServeCompleteSetup(database_url, admin_password)
    
    if setup.run_complete_setup():
        logger.info("🎉 Setup completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Setup failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()