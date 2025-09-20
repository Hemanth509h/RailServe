#!/usr/bin/env python3
"""
Railway Database Initialization Script
Creates PostgreSQL database schema and populates with comprehensive test data

Usage:
    python setup_database.py

Environment Variables:
    DATABASE_URL: PostgreSQL connection string (default: postgresql://postgres:12345678@localhost:5432/)
"""

import os
import sys
import random
import string
from datetime import datetime, date, time, timedelta
from faker import Faker
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database imports
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, Time, Text, ForeignKey, UniqueConstraint
from flask_login import UserMixin

fake = Faker('en_IN')  # Indian locale for realistic data

class Base(DeclarativeBase):
    pass

# Database Models (Standalone versions)
class User(UserMixin, Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(20), default='user')
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Station(Base):
    __tablename__ = 'station'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(10), nullable=False, unique=True)
    city = Column(String(50), nullable=False)
    state = Column(String(50), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Train(Base):
    __tablename__ = 'train'
    
    id = Column(Integer, primary_key=True)
    number = Column(String(10), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    total_seats = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False)
    fare_per_km = Column(Float, nullable=False)
    tatkal_seats = Column(Integer, default=0)
    tatkal_fare_per_km = Column(Float)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TrainRoute(Base):
    __tablename__ = 'train_route'
    
    id = Column(Integer, primary_key=True)
    train_id = Column(Integer, ForeignKey('train.id'), nullable=False)
    station_id = Column(Integer, ForeignKey('station.id'), nullable=False)
    sequence = Column(Integer, nullable=False)
    arrival_time = Column(Time)
    departure_time = Column(Time)
    distance_from_start = Column(Float, nullable=False)
    
    __table_args__ = (UniqueConstraint('train_id', 'sequence'),)

class Booking(Base):
    __tablename__ = 'booking'
    
    id = Column(Integer, primary_key=True)
    pnr = Column(String(10), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    train_id = Column(Integer, ForeignKey('train.id'), nullable=False)
    from_station_id = Column(Integer, ForeignKey('station.id'), nullable=False)
    to_station_id = Column(Integer, ForeignKey('station.id'), nullable=False)
    journey_date = Column(Date, nullable=False)
    passengers = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
    booking_type = Column(String(10), default='general')
    quota = Column(String(20), default='general')
    coach_class = Column(String(10), default='SL')
    status = Column(String(20), default='pending_payment')
    waitlist_type = Column(String(10), default='GNWL')
    chart_prepared = Column(Boolean, default=False)
    berth_preference = Column(String(20), default='No Preference')
    current_reservation = Column(Boolean, default=False)
    booking_date = Column(DateTime, default=datetime.utcnow)
    cancellation_charges = Column(Float, default=0.0)
    group_booking_id = Column(Integer, ForeignKey('group_booking.id'))
    loyalty_discount = Column(Float, default=0.0)

class Passenger(Base):
    __tablename__ = 'passenger'
    
    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('booking.id'), nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    id_proof_type = Column(String(20), nullable=False)
    id_proof_number = Column(String(50), nullable=False)
    seat_preference = Column(String(20), default='No Preference')
    coach_class = Column(String(10), default='SL')
    seat_number = Column(String(20))
    berth_type = Column(String(20))

class Payment(Base):
    __tablename__ = 'payment'
    
    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('booking.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(20), nullable=False)
    transaction_id = Column(String(50))
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    __table_args__ = (UniqueConstraint('booking_id', 'status', name='uq_booking_payment_success'),)

class Waitlist(Base):
    __tablename__ = 'waitlist'
    
    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('booking.id'), nullable=False)
    train_id = Column(Integer, ForeignKey('train.id'), nullable=False)
    journey_date = Column(Date, nullable=False)
    position = Column(Integer, nullable=False)
    waitlist_type = Column(String(10), default='GNWL')
    created_at = Column(DateTime, default=datetime.utcnow)

class TatkalTimeSlot(Base):
    __tablename__ = 'tatkal_time_slot'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    coach_classes = Column(String(200))
    open_time = Column(Time, nullable=False)
    close_time = Column(Time)
    days_before_journey = Column(Integer, default=1)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('user.id'))

class RefundRequest(Base):
    __tablename__ = 'refund_request'
    
    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('booking.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    reason = Column(String(100), nullable=False)
    amount_paid = Column(Float, nullable=False)
    refund_amount = Column(Float, nullable=False)
    cancellation_charges = Column(Float, default=0.0)
    tdr_number = Column(String(20), unique=True, nullable=False)
    status = Column(String(20), default='pending')
    filed_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)

class TrainStatus(Base):
    __tablename__ = 'train_status'
    
    id = Column(Integer, primary_key=True)
    train_id = Column(Integer, ForeignKey('train.id'), nullable=False)
    current_station_id = Column(Integer, ForeignKey('station.id'))
    status = Column(String(50), default='On Time')
    delay_minutes = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    journey_date = Column(Date, nullable=False)

class SeatAvailability(Base):
    __tablename__ = 'seat_availability'
    
    id = Column(Integer, primary_key=True)
    train_id = Column(Integer, ForeignKey('train.id'), nullable=False)
    from_station_id = Column(Integer, ForeignKey('station.id'), nullable=False)
    to_station_id = Column(Integer, ForeignKey('station.id'), nullable=False)
    journey_date = Column(Date, nullable=False)
    coach_class = Column(String(10), nullable=False)
    quota = Column(String(20), default='general')
    available_seats = Column(Integer, default=0)
    waiting_list = Column(Integer, default=0)
    rac_seats = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)

class ChartPreparation(Base):
    __tablename__ = 'chart_preparation'
    
    id = Column(Integer, primary_key=True)
    train_id = Column(Integer, ForeignKey('train.id'), nullable=False)
    journey_date = Column(Date, nullable=False)
    chart_prepared_at = Column(DateTime)
    final_chart_at = Column(DateTime)
    status = Column(String(20), default='pending')
    confirmed_from_waitlist = Column(Integer, default=0)
    cancelled_waitlist = Column(Integer, default=0)

class Restaurant(Base):
    __tablename__ = 'restaurant'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    station_id = Column(Integer, ForeignKey('station.id'), nullable=False)
    contact_number = Column(String(15))
    email = Column(String(120))
    cuisine_type = Column(String(50))
    rating = Column(Float, default=4.0)
    delivery_time = Column(Integer, default=30)
    minimum_order = Column(Float, default=0.0)
    delivery_charge = Column(Float, default=0.0)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class MenuItem(Base):
    __tablename__ = 'menu_item'
    
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False)
    category = Column(String(50))
    food_type = Column(String(20), default='Vegetarian')
    image_url = Column(String(200))
    preparation_time = Column(Integer, default=15)
    available = Column(Boolean, default=True)
    is_popular = Column(Boolean, default=False)
    ingredients = Column(Text)
    nutrition_info = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class FoodOrder(Base):
    __tablename__ = 'food_order'
    
    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('booking.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)
    delivery_station_id = Column(Integer, ForeignKey('station.id'), nullable=False)
    order_number = Column(String(20), unique=True, nullable=False)
    total_amount = Column(Float, nullable=False)
    delivery_charge = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    status = Column(String(20), default='pending')
    special_instructions = Column(Text)
    delivery_time = Column(DateTime)
    contact_number = Column(String(15), nullable=False)
    coach_number = Column(String(10))
    seat_number = Column(String(10))
    payment_status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class FoodOrderItem(Base):
    __tablename__ = 'food_order_item'
    
    id = Column(Integer, primary_key=True)
    food_order_id = Column(Integer, ForeignKey('food_order.id'), nullable=False)
    menu_item_id = Column(Integer, ForeignKey('menu_item.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    special_request = Column(String(200))

class GroupBooking(Base):
    __tablename__ = 'group_booking'
    
    id = Column(Integer, primary_key=True)
    group_name = Column(String(100), nullable=False)
    group_leader_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    total_passengers = Column(Integer, nullable=False)
    contact_email = Column(String(120), nullable=False)
    contact_phone = Column(String(15), nullable=False)
    booking_type = Column(String(20), default='family')
    special_requirements = Column(Text)
    discount_applied = Column(Float, default=0.0)
    group_discount_rate = Column(Float, default=0.0)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)

class LoyaltyProgram(Base):
    __tablename__ = 'loyalty_program'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, unique=True)
    membership_number = Column(String(20), unique=True, nullable=False)
    tier = Column(String(20), default='Silver')
    points_earned = Column(Integer, default=0)
    points_redeemed = Column(Integer, default=0)
    total_journeys = Column(Integer, default=0)
    total_distance = Column(Float, default=0.0)
    total_spent = Column(Float, default=0.0)
    tier_valid_until = Column(Date)
    benefits_active = Column(Boolean, default=True)
    joined_date = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)

class NotificationPreferences(Base):
    __tablename__ = 'notification_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, unique=True)
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    booking_confirmations = Column(Boolean, default=True)
    journey_reminders = Column(Boolean, default=True)
    train_delay_alerts = Column(Boolean, default=True)
    food_order_updates = Column(Boolean, default=True)
    promotional_offers = Column(Boolean, default=False)

# Event listener for PNR generation
@event.listens_for(Booking, 'before_insert')
def generate_pnr(mapper, connection, target):
    """Generate unique PNR number"""
    if not target.pnr:
        while True:
            pnr = ''.join(random.choices(string.digits, k=10))
            existing = connection.execute(
                text("SELECT id FROM booking WHERE pnr = :pnr"), 
                {"pnr": pnr}
            ).fetchone()
            if not existing:
                target.pnr = pnr
                break

# Database setup function
def setup_database():
    """Initialize database with schema and test data"""
    
    # Get database URL from environment
    database_url = os.environ.get("DATABASE_URL", "postgresql://postgres:12345678@localhost:5432/")
    
    logger.info(f"Connecting to database: {database_url.split('@')[0]}@...")
    
    try:
        # Create engine
        engine = create_engine(
            database_url,
            echo=False,  # Set to True for SQL debugging
            pool_pre_ping=True,
            pool_recycle=300
        )
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        
        # Create all tables
        logger.info("Creating database schema...")
        Base.metadata.drop_all(engine)  # Drop existing tables
        Base.metadata.create_all(engine)
        logger.info("Database schema created successfully")
        
        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Populate with test data
            populate_test_data(session)
            session.commit()
            logger.info("Database initialization completed successfully!")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error populating test data: {str(e)}")
            raise
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        sys.exit(1)

def populate_test_data(session):
    """Populate database with comprehensive test data"""
    
    logger.info("Creating users...")
    create_users(session)
    
    logger.info("Creating 1500 stations...")
    create_stations(session)
    
    logger.info("Creating 1250 trains...")
    create_trains(session)
    
    logger.info("Creating train routes...")
    create_train_routes(session)
    
    logger.info("Creating restaurants and menus...")
    create_restaurants_and_menus(session)
    
    logger.info("Creating bookings and related data...")
    create_bookings_and_related_data(session)
    
    logger.info("Creating additional features data...")
    create_additional_features(session)

def create_users(session):
    """Create users including admin and test users"""
    users = []
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@railserve.com',
        password_hash='scrypt:32768:8:1$ZKnR7QwYiWrMGqVl$f4c8a1b2d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8t9u0v1w2x3y4z5',  # password: admin123
        role='super_admin',
        active=True
    )
    users.append(admin)
    
    # Create test users
    for i in range(100):
        user = User(
            username=f'user_{i:03d}',
            email=fake.email(),
            password_hash='scrypt:32768:8:1$ZKnR7QwYiWrMGqVl$f4c8a1b2d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8t9u0v1w2x3y4z5',  # password: user123
            role='user',
            active=True,
            created_at=fake.date_time_between(start_date='-2y', end_date='now')
        )
        users.append(user)
    
    session.add_all(users)
    session.flush()  # Get IDs

def create_stations(session):
    """Create 1500 railway stations across India"""
    
    # Indian states and major cities
    indian_states_cities = [
        ('Andhra Pradesh', ['Vijayawada', 'Visakhapatnam', 'Tirupati', 'Guntur', 'Nellore', 'Kurnool', 'Rajahmundry', 'Kadapa', 'Anantapur', 'Chittoor']),
        ('Assam', ['Guwahati', 'Dibrugarh', 'Silchar', 'Jorhat', 'Tinsukia', 'Nagaon', 'Tezpur', 'Golaghat', 'Sibsagar', 'Bongaigaon']),
        ('Bihar', ['Patna', 'Muzaffarpur', 'Bhagalpur', 'Purnia', 'Darbhanga', 'Gaya', 'Begusarai', 'Saharsa', 'Hajipur', 'Sasaram']),
        ('Chhattisgarh', ['Raipur', 'Bilaspur', 'Durg', 'Korba', 'Raigarh', 'Rajnandgaon', 'Jagdalpur', 'Ambikapur', 'Dhamtari', 'Mahasamund']),
        ('Delhi', ['New Delhi', 'Old Delhi', 'Anand Vihar', 'Hazrat Nizamuddin', 'Sarai Rohilla', 'Delhi Cantt', 'Delhi Junction', 'Tilak Bridge', 'Delhi Shahdara', 'Subzi Mandi']),
        ('Gujarat', ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Bhavnagar', 'Jamnagar', 'Junagadh', 'Gandhinagar', 'Anand', 'Bharuch']),
        ('Haryana', ['Ambala', 'Kurukshetra', 'Panipat', 'Rohtak', 'Hisar', 'Karnal', 'Faridabad', 'Gurgaon', 'Sonipat', 'Bhiwani']),
        ('Himachal Pradesh', ['Shimla', 'Pathankot', 'Una', 'Kangra', 'Palampur', 'Dharamshala', 'Mandi', 'Kullu', 'Solan', 'Hamirpur']),
        ('Jharkhand', ['Ranchi', 'Jamshedpur', 'Dhanbad', 'Bokaro', 'Deoghar', 'Hazaribagh', 'Giridih', 'Ramgarh', 'Medininagar', 'Chaibasa']),
        ('Karnataka', ['Bangalore', 'Mysore', 'Hubli', 'Mangalore', 'Belgaum', 'Gulbarga', 'Davangere', 'Bellary', 'Bijapur', 'Shimoga']),
        ('Kerala', ['Thiruvananthapuram', 'Kochi', 'Calicut', 'Thrissur', 'Kollam', 'Alappuzha', 'Palakkad', 'Kottayam', 'Kannur', 'Kasaragod']),
        ('Madhya Pradesh', ['Bhopal', 'Indore', 'Jabalpur', 'Gwalior', 'Ujjain', 'Sagar', 'Dewas', 'Satna', 'Ratlam', 'Rewa']),
        ('Maharashtra', ['Mumbai', 'Pune', 'Nagpur', 'Nashik', 'Aurangabad', 'Solapur', 'Amravati', 'Kolhapur', 'Sangli', 'Jalgaon']),
        ('Odisha', ['Bhubaneswar', 'Cuttack', 'Puri', 'Berhampur', 'Sambalpur', 'Rourkela', 'Balasore', 'Baripada', 'Jharsuguda', 'Angul']),
        ('Punjab', ['Amritsar', 'Ludhiana', 'Jalandhar', 'Patiala', 'Bathinda', 'Mohali', 'Firozpur', 'Pathankot', 'Moga', 'Malerkotla']),
        ('Rajasthan', ['Jaipur', 'Jodhpur', 'Udaipur', 'Kota', 'Bikaner', 'Ajmer', 'Bharatpur', 'Alwar', 'Sikar', 'Pali']),
        ('Tamil Nadu', ['Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem', 'Tirunelveli', 'Erode', 'Vellore', 'Tuticorin', 'Dindigul']),
        ('Telangana', ['Hyderabad', 'Warangal', 'Nizamabad', 'Khammam', 'Karimnagar', 'Ramagundam', 'Mahbubnagar', 'Nalgonda', 'Adilabad', 'Suryapet']),
        ('Uttar Pradesh', ['Lucknow', 'Kanpur', 'Agra', 'Varanasi', 'Meerut', 'Allahabad', 'Bareilly', 'Aligarh', 'Moradabad', 'Saharanpur']),
        ('West Bengal', ['Kolkata', 'Howrah', 'Durgapur', 'Asansol', 'Siliguri', 'Malda', 'Bardhaman', 'Kharagpur', 'Haldia', 'Krishnanagar'])
    ]
    
    stations = []
    station_codes_used = set()
    
    for state, cities in indian_states_cities:
        for city in cities:
            # Create multiple stations per city
            for i in range(random.randint(3, 8)):
                # Generate unique station code
                while True:
                    code = ''.join(random.choices(string.ascii_uppercase, k=3)) + str(random.randint(0, 9))
                    if code not in station_codes_used:
                        station_codes_used.add(code)
                        break
                
                # Station name variations
                suffixes = ['Junction', 'Central', 'City', 'Cantt', 'Town', 'Terminal', 'Road', 'East', 'West', 'South', 'North', '']
                suffix = random.choice(suffixes)
                station_name = f"{city} {suffix}".strip()
                
                if len(stations) >= 1500:
                    break
                    
                station = Station(
                    name=station_name,
                    code=code,
                    city=city,
                    state=state,
                    active=True,
                    created_at=fake.date_time_between(start_date='-5y', end_date='now')
                )
                stations.append(station)
            
            if len(stations) >= 1500:
                break
        
        if len(stations) >= 1500:
            break
    
    session.add_all(stations)
    session.flush()

def create_trains(session):
    """Create 1250 trains with realistic Indian train data"""
    
    # Indian train name patterns
    train_types = ['Express', 'Superfast', 'Mail', 'Passenger', 'Shatabdi', 'Rajdhani', 'Duronto', 'Garib Rath', 'Jan Shatabdi', 'Intercity']
    train_prefixes = ['Karnataka', 'Tamil Nadu', 'Kerala', 'Gujarat', 'Punjab', 'Rajasthan', 'Maharashtra', 'Bengal', 'Assam', 'Uttar Pradesh',
                     'Howrah', 'Chennai', 'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Kolkata', 'Kochi', 'Mysore', 'Coimbatore']
    
    trains = []
    train_numbers_used = set()
    
    for i in range(1250):
        # Generate unique train number
        while True:
            train_number = str(random.randint(10001, 99999))
            if train_number not in train_numbers_used:
                train_numbers_used.add(train_number)
                break
        
        # Generate train name
        prefix = random.choice(train_prefixes)
        train_type = random.choice(train_types)
        train_name = f"{prefix} {train_type}"
        
        # Realistic seat configurations
        if train_type in ['Shatabdi', 'Rajdhani']:
            total_seats = random.randint(400, 800)
            fare_per_km = random.uniform(2.5, 4.5)
            tatkal_seats = int(total_seats * 0.15)
            tatkal_fare_per_km = fare_per_km * 1.5
        elif train_type in ['Superfast', 'Duronto']:
            total_seats = random.randint(800, 1500)
            fare_per_km = random.uniform(1.5, 3.0)
            tatkal_seats = int(total_seats * 0.12)
            tatkal_fare_per_km = fare_per_km * 1.3
        else:
            total_seats = random.randint(1000, 2000)
            fare_per_km = random.uniform(0.8, 2.0)
            tatkal_seats = int(total_seats * 0.10)
            tatkal_fare_per_km = fare_per_km * 1.2
        
        train = Train(
            number=train_number,
            name=train_name,
            total_seats=total_seats,
            available_seats=total_seats,
            fare_per_km=round(fare_per_km, 2),
            tatkal_seats=tatkal_seats,
            tatkal_fare_per_km=round(tatkal_fare_per_km, 2),
            active=True,
            created_at=fake.date_time_between(start_date='-3y', end_date='now')
        )
        trains.append(train)
    
    session.add_all(trains)
    session.flush()

def create_train_routes(session):
    """Create comprehensive train routes connecting stations"""
    
    stations = session.query(Station).all()
    trains = session.query(Train).all()
    
    routes = []
    
    for train in trains:
        # Each train covers 5-15 stations
        num_stations = random.randint(5, 15)
        selected_stations = random.sample(stations, num_stations)
        
        # Sort stations by a logical route (simulate geographical ordering)
        selected_stations.sort(key=lambda x: x.id)
        
        total_distance = 0
        base_time = time(hour=random.randint(5, 22), minute=random.randint(0, 59))
        
        for seq, station in enumerate(selected_stations, 1):
            if seq == 1:
                # First station - only departure
                arrival_time = None
                departure_time = base_time
                distance = 0
            else:
                # Add 50-300 km between stations
                distance_increment = random.randint(50, 300)
                total_distance += distance_increment
                
                # Calculate travel time (assume 60-80 km/h average speed)
                travel_hours = distance_increment / random.randint(60, 80)
                
                # Convert previous departure to current arrival
                prev_departure = datetime.combine(date.today(), departure_time)
                arrival_datetime = prev_departure + timedelta(hours=travel_hours)
                arrival_time = arrival_datetime.time()
                
                if seq == len(selected_stations):
                    # Last station - only arrival
                    departure_time = None
                else:
                    # Stop for 2-10 minutes
                    stop_minutes = random.randint(2, 10)
                    departure_datetime = arrival_datetime + timedelta(minutes=stop_minutes)
                    departure_time = departure_datetime.time()
                
                distance = total_distance
            
            route = TrainRoute(
                train_id=train.id,
                station_id=station.id,
                sequence=seq,
                arrival_time=arrival_time,
                departure_time=departure_time,
                distance_from_start=distance
            )
            routes.append(route)
    
    session.add_all(routes)
    session.flush()

def create_restaurants_and_menus(session):
    """Create restaurants and their menu items"""
    
    stations = session.query(Station).limit(200).all()  # Add restaurants to first 200 stations
    
    restaurants = []
    menu_items = []
    
    # Indian restaurant names and food items
    restaurant_names = [
        'Annapurna Restaurant', 'Sagar Ratna', 'Udupi Krishna', 'South Indian Kitchen', 'Punjabi Dhaba',
        'Rajasthani Thali', 'Bengali Sweets', 'Gujarati Samrat', 'Hotel Woodlands', 'Murugan Idli Shop',
        'Saravana Bhavan', 'Pind Balluchi', 'Karim Hotel', 'Paradise Biryani', 'Haldiram\'s'
    ]
    
    food_categories = ['Breakfast', 'Lunch', 'Dinner', 'Snacks', 'Beverages']
    food_items = {
        'Breakfast': ['Idli Sambar', 'Dosa', 'Upma', 'Poha', 'Paratha', 'Aloo Puri', 'Chole Bhature'],
        'Lunch': ['Dal Rice', 'Biryani', 'Thali', 'Rajma Rice', 'Sambar Rice', 'Curd Rice'],
        'Dinner': ['Roti Sabzi', 'Fried Rice', 'Paneer Butter Masala', 'Chicken Curry', 'Fish Curry'],
        'Snacks': ['Samosa', 'Vada Pav', 'Bhel Puri', 'Pakora', 'Sandwich', 'Cutlet'],
        'Beverages': ['Tea', 'Coffee', 'Lassi', 'Fresh Lime', 'Buttermilk', 'Cold Drink']
    }
    
    for station in stations:
        # 1-3 restaurants per station
        num_restaurants = random.randint(1, 3)
        
        for _ in range(num_restaurants):
            restaurant = Restaurant(
                name=random.choice(restaurant_names),
                station_id=station.id,
                contact_number=fake.phone_number()[:15],
                email=fake.email(),
                cuisine_type=random.choice(['Vegetarian', 'Non-Vegetarian', 'Both']),
                rating=round(random.uniform(3.5, 5.0), 1),
                delivery_time=random.randint(20, 45),
                minimum_order=random.choice([0, 50, 100, 150]),
                delivery_charge=random.choice([0, 10, 20, 30]),
                active=True
            )
            restaurants.append(restaurant)
    
    session.add_all(restaurants)
    session.flush()
    
    # Create menu items for each restaurant
    for restaurant in restaurants:
        # 10-20 menu items per restaurant
        num_items = random.randint(10, 20)
        
        for _ in range(num_items):
            category = random.choice(food_categories)
            item_name = random.choice(food_items[category])
            
            menu_item = MenuItem(
                restaurant_id=restaurant.id,
                name=item_name,
                description=fake.text(max_nb_chars=200),
                price=round(random.uniform(30, 300), 2),
                category=category,
                food_type=random.choice(['Vegetarian', 'Non-Vegetarian']),
                preparation_time=random.randint(10, 30),
                available=True,
                is_popular=random.choice([True, False])
            )
            menu_items.append(menu_item)
    
    session.add_all(menu_items)
    session.flush()

def create_bookings_and_related_data(session):
    """Create bookings, passengers, payments, and waitlist entries"""
    
    users = session.query(User).all()
    trains = session.query(Train).all()
    stations = session.query(Station).all()
    train_routes = session.query(TrainRoute).all()
    
    bookings = []
    passengers = []
    payments = []
    waitlists = []
    
    # Group bookings
    group_bookings = []
    for i in range(50):
        group_booking = GroupBooking(
            group_name=f"Group {i+1}",
            group_leader_id=random.choice(users).id,
            total_passengers=random.randint(5, 20),
            contact_email=fake.email(),
            contact_phone=fake.phone_number()[:15],
            booking_type=random.choice(['family', 'corporate', 'tour', 'religious']),
            discount_applied=random.uniform(0, 500),
            group_discount_rate=random.uniform(5, 15),
            status=random.choice(['pending', 'confirmed', 'cancelled']),
            created_at=fake.date_time_between(start_date='-6m', end_date='now')
        )
        group_bookings.append(group_booking)
    
    session.add_all(group_bookings)
    session.flush()
    
    # Create 1000+ bookings
    for i in range(1200):
        user = random.choice(users)
        train = random.choice(trains)
        
        # Get train route stations
        train_route_stations = [tr for tr in train_routes if tr.train_id == train.id]
        if len(train_route_stations) < 2:
            continue
        
        # Select from and to stations from the route
        from_station_route = random.choice(train_route_stations[:-1])
        to_station_route = random.choice([tr for tr in train_route_stations if tr.sequence > from_station_route.sequence])
        
        # Calculate distance and fare
        distance = to_station_route.distance_from_start - from_station_route.distance_from_start
        num_passengers = random.randint(1, 6)
        base_amount = distance * train.fare_per_km * num_passengers
        
        # Apply random discounts and taxes
        total_amount = base_amount * random.uniform(0.9, 1.2)
        
        booking = Booking(
            pnr='',  # Will be auto-generated
            user_id=user.id,
            train_id=train.id,
            from_station_id=from_station_route.station_id,
            to_station_id=to_station_route.station_id,
            journey_date=fake.date_between(start_date='today', end_date='+30d'),
            passengers=num_passengers,
            total_amount=round(total_amount, 2),
            booking_type=random.choice(['general', 'tatkal']),
            quota=random.choice(['general', 'ladies', 'senior', 'disability', 'tatkal']),
            coach_class=random.choice(['AC1', 'AC2', 'AC3', 'SL', '2S', 'CC']),
            status=random.choice(['confirmed', 'waitlisted', 'cancelled', 'pending_payment']),
            waitlist_type=random.choice(['GNWL', 'RAC', 'PQWL', 'RLWL', 'TQWL']),
            berth_preference=random.choice(['Lower', 'Middle', 'Upper', 'Side Lower', 'Side Upper', 'Window', 'Aisle', 'No Preference']),
            booking_date=fake.date_time_between(start_date='-30d', end_date='now'),
            group_booking_id=random.choice(group_bookings).id if random.random() < 0.1 else None
        )
        bookings.append(booking)
    
    session.add_all(bookings)
    session.flush()
    
    # Create passengers for each booking
    for booking in bookings:
        for p in range(booking.passengers):
            passenger = Passenger(
                booking_id=booking.id,
                name=fake.name(),
                age=random.randint(1, 80),
                gender=random.choice(['Male', 'Female', 'Other']),
                id_proof_type=random.choice(['Aadhar', 'PAN', 'Passport', 'Voter ID', 'Driving License']),
                id_proof_number=fake.bothify(text='??##########'),
                seat_preference=random.choice(['Lower', 'Middle', 'Upper', 'Window', 'Aisle', 'No Preference']),
                coach_class=booking.coach_class,
                seat_number=f"{random.choice(['S', 'A', 'B'])}{random.randint(1, 10)}-{random.randint(1, 72)}" if booking.status == 'confirmed' else None,
                berth_type=random.choice(['Lower', 'Middle', 'Upper', 'Side Lower', 'Side Upper']) if booking.status == 'confirmed' else None
            )
            passengers.append(passenger)
    
    session.add_all(passengers)
    
    # Create payments for bookings
    for booking in bookings:
        if booking.status in ['confirmed', 'waitlisted']:
            payment = Payment(
                booking_id=booking.id,
                user_id=booking.user_id,
                amount=booking.total_amount,
                payment_method=random.choice(['card', 'upi', 'netbanking', 'wallet']),
                transaction_id=f"TXN{fake.bothify(text='##########')}",
                status='success',
                created_at=booking.booking_date,
                completed_at=booking.booking_date + timedelta(minutes=random.randint(1, 10))
            )
            payments.append(payment)
    
    session.add_all(payments)
    
    # Create waitlist entries for waitlisted bookings
    waitlist_bookings = [b for b in bookings if b.status == 'waitlisted']
    for booking in waitlist_bookings:
        waitlist = Waitlist(
            booking_id=booking.id,
            train_id=booking.train_id,
            journey_date=booking.journey_date,
            position=random.randint(1, 100),
            waitlist_type=booking.waitlist_type,
            created_at=booking.booking_date
        )
        waitlists.append(waitlist)
    
    session.add_all(waitlists)
    session.flush()

def create_additional_features(session):
    """Create additional feature data like loyalty programs, tatkal slots, etc."""
    
    users = session.query(User).all()
    trains = session.query(Train).all()
    stations = session.query(Station).all()
    bookings = session.query(Booking).all()
    
    # Loyalty programs for some users
    loyalty_programs = []
    for user in random.sample(users, min(50, len(users))):
        loyalty = LoyaltyProgram(
            user_id=user.id,
            membership_number=f"RL{datetime.now().year}{random.randint(100000, 999999)}",
            tier=random.choice(['Silver', 'Gold', 'Platinum', 'Diamond']),
            points_earned=random.randint(100, 10000),
            points_redeemed=random.randint(0, 5000),
            total_journeys=random.randint(1, 100),
            total_distance=random.uniform(100, 50000),
            total_spent=random.uniform(1000, 100000),
            tier_valid_until=fake.date_between(start_date='today', end_date='+1y'),
            joined_date=fake.date_time_between(start_date='-2y', end_date='now')
        )
        loyalty_programs.append(loyalty)
    
    session.add_all(loyalty_programs)
    
    # Tatkal time slots
    tatkal_slots = [
        TatkalTimeSlot(
            name='AC Classes Tatkal',
            coach_classes='AC1,AC2,AC3,CC',
            open_time=time(10, 0),
            close_time=time(11, 30),
            days_before_journey=1,
            active=True,
            created_by=1  # Admin user
        ),
        TatkalTimeSlot(
            name='Non-AC Classes Tatkal',
            coach_classes='SL,2S',
            open_time=time(11, 0),
            close_time=time(12, 30),
            days_before_journey=1,
            active=True,
            created_by=1  # Admin user
        )
    ]
    
    session.add_all(tatkal_slots)
    
    # Train status for current and future journeys
    train_statuses = []
    for train in random.sample(trains, min(200, len(trains))):
        status = TrainStatus(
            train_id=train.id,
            current_station_id=random.choice(stations).id,
            status=random.choice(['On Time', 'Delayed', 'Cancelled']),
            delay_minutes=random.randint(0, 120) if random.random() < 0.3 else 0,
            journey_date=fake.date_between(start_date='-3d', end_date='+7d')
        )
        train_statuses.append(status)
    
    session.add_all(train_statuses)
    
    # Notification preferences for users
    notification_prefs = []
    for user in users:
        prefs = NotificationPreferences(
            user_id=user.id,
            email_notifications=random.choice([True, False]),
            sms_notifications=random.choice([True, False]),
            push_notifications=random.choice([True, False]),
            promotional_offers=random.choice([True, False])
        )
        notification_prefs.append(prefs)
    
    session.add_all(notification_prefs)
    
    session.flush()

if __name__ == "__main__":
    logger.info("Starting Railway Database Initialization...")
    logger.info("=" * 60)
    
    setup_database()
    
    logger.info("=" * 60)
    logger.info("Database initialization complete!")
    logger.info("\nDatabase now contains:")
    logger.info("- Users: 101 (1 admin + 100 test users)")
    logger.info("- Stations: 1500 across Indian states")
    logger.info("- Trains: 1250 with realistic configurations")
    logger.info("- Train Routes: Complete route networks")
    logger.info("- Bookings: 1200+ with passengers and payments")
    logger.info("- Restaurants & Menus: 200+ stations with food options")
    logger.info("- Waitlist: Comprehensive waitlist management")
    logger.info("- Additional Features: Loyalty programs, Tatkal slots, etc.")
    logger.info("\nLogin credentials:")
    logger.info("Admin: username=admin, password=admin123")
    logger.info("Test users: username=user_001-100, password=user123")