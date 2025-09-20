#!/usr/bin/env python3
"""
RailServe Database Setup Script
==============================

This script creates a comprehensive RailServe railway reservation system database
with all required tables and comprehensive test data.

Usage:
    python setup_database.py

Features Created:
- Complete database schema for all models
- Admin and test users with proper authentication
- 50+ railway stations across India
- 25+ trains with realistic routes and schedules
- Comprehensive booking system with all features
- Food ordering system with restaurants and menus
- Payment tracking and transaction management
- Group bookings and loyalty programs
- Tatkal booking management
- All necessary test data for full system testing
"""

import os
import sys
import random
import string
import logging
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Database connection with fallback
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:12345678@localhost:5432/railserve")

if not DATABASE_URL:
    logger.error("❌ DATABASE_URL environment variable is required")
    sys.exit(1)

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    from werkzeug.security import generate_password_hash
    logger.info("✅ All dependencies available")
except ImportError as e:
    logger.error(f"❌ Missing dependencies: {e}")
    logger.error("Install with: pip install psycopg2-binary werkzeug")
    sys.exit(1)

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        sys.exit(1)

def create_database_schema(cursor):
    """Create all database tables with proper schema"""
    logger.info("🏗️ Creating database schema...")
    
    # Create tables in proper order (dependencies first)
    
    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS "user" (
        id SERIAL PRIMARY KEY,
        username VARCHAR(64) UNIQUE NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        password_hash VARCHAR(256) NOT NULL,
        role VARCHAR(20) DEFAULT 'user',
        active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Stations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS station (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL,
        code VARCHAR(10) UNIQUE NOT NULL,
        city VARCHAR(50) NOT NULL,
        state VARCHAR(50) NOT NULL,
        active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Trains table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS train (
        id SERIAL PRIMARY KEY,
        number VARCHAR(10) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        total_seats INTEGER NOT NULL,
        available_seats INTEGER NOT NULL,
        fare_per_km REAL NOT NULL,
        tatkal_seats INTEGER DEFAULT 0,
        tatkal_fare_per_km REAL,
        active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Train Routes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS train_route (
        id SERIAL PRIMARY KEY,
        train_id INTEGER REFERENCES train(id) ON DELETE CASCADE,
        station_id INTEGER REFERENCES station(id) ON DELETE CASCADE,
        sequence INTEGER NOT NULL,
        arrival_time TIME,
        departure_time TIME,
        distance_from_start REAL NOT NULL,
        halt_duration INTEGER DEFAULT 0,
        commercial_stop BOOLEAN DEFAULT TRUE,
        meal_stop BOOLEAN DEFAULT FALSE,
        UNIQUE(train_id, sequence)
    )
    """)
    
    # Group Bookings table (must be before bookings)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS group_booking (
        id SERIAL PRIMARY KEY,
        group_name VARCHAR(100) NOT NULL,
        group_leader_id INTEGER REFERENCES "user"(id),
        total_passengers INTEGER NOT NULL,
        contact_email VARCHAR(120) NOT NULL,
        contact_phone VARCHAR(15) NOT NULL,
        booking_type VARCHAR(20) DEFAULT 'family',
        special_requirements TEXT,
        discount_applied REAL DEFAULT 0.0,
        group_discount_rate REAL DEFAULT 0.0,
        status VARCHAR(20) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Bookings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS booking (
        id SERIAL PRIMARY KEY,
        pnr VARCHAR(10) UNIQUE NOT NULL,
        user_id INTEGER REFERENCES "user"(id) NOT NULL,
        train_id INTEGER REFERENCES train(id) NOT NULL,
        from_station_id INTEGER REFERENCES station(id) NOT NULL,
        to_station_id INTEGER REFERENCES station(id) NOT NULL,
        journey_date DATE NOT NULL,
        passengers INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        booking_type VARCHAR(10) DEFAULT 'general',
        quota VARCHAR(20) DEFAULT 'general',
        coach_class VARCHAR(10) DEFAULT 'SL',
        status VARCHAR(20) DEFAULT 'pending_payment',
        waitlist_type VARCHAR(10) DEFAULT 'GNWL',
        chart_prepared BOOLEAN DEFAULT FALSE,
        berth_preference VARCHAR(20) DEFAULT 'No Preference',
        current_reservation BOOLEAN DEFAULT FALSE,
        booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        cancellation_charges REAL DEFAULT 0.0,
        group_booking_id INTEGER REFERENCES group_booking(id),
        loyalty_discount REAL DEFAULT 0.0
    )
    """)
    
    # Passengers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS passenger (
        id SERIAL PRIMARY KEY,
        booking_id INTEGER REFERENCES booking(id) ON DELETE CASCADE,
        name VARCHAR(100) NOT NULL,
        age INTEGER NOT NULL,
        gender VARCHAR(10) NOT NULL,
        id_proof_type VARCHAR(20) NOT NULL,
        id_proof_number VARCHAR(50) NOT NULL,
        seat_preference VARCHAR(20) DEFAULT 'No Preference',
        coach_class VARCHAR(10) DEFAULT 'SL',
        seat_number VARCHAR(20),
        berth_type VARCHAR(20)
    )
    """)
    
    # Payments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payment (
        id SERIAL PRIMARY KEY,
        booking_id INTEGER REFERENCES booking(id) NOT NULL,
        user_id INTEGER REFERENCES "user"(id) NOT NULL,
        amount REAL NOT NULL,
        payment_method VARCHAR(20) NOT NULL,
        transaction_id VARCHAR(50),
        status VARCHAR(20) DEFAULT 'pending',
        gateway_response TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        UNIQUE(booking_id, status)
    )
    """)
    
    # Waitlist table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS waitlist (
        id SERIAL PRIMARY KEY,
        booking_id INTEGER REFERENCES booking(id) NOT NULL,
        train_id INTEGER REFERENCES train(id) NOT NULL,
        journey_date DATE NOT NULL,
        position INTEGER NOT NULL,
        waitlist_type VARCHAR(10) DEFAULT 'GNWL',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Tatkal Time Slots table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tatkal_time_slot (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        coach_classes VARCHAR(200),
        open_time TIME NOT NULL,
        close_time TIME,
        days_before_journey INTEGER DEFAULT 1,
        active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by INTEGER REFERENCES "user"(id)
    )
    """)
    
    # Restaurants table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS restaurant (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        station_id INTEGER REFERENCES station(id) NOT NULL,
        contact_number VARCHAR(15),
        email VARCHAR(120),
        cuisine_type VARCHAR(50),
        rating REAL DEFAULT 4.0,
        delivery_time INTEGER DEFAULT 30,
        minimum_order REAL DEFAULT 0.0,
        delivery_charge REAL DEFAULT 0.0,
        active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Menu Items table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS menu_item (
        id SERIAL PRIMARY KEY,
        restaurant_id INTEGER REFERENCES restaurant(id) ON DELETE CASCADE,
        name VARCHAR(100) NOT NULL,
        description VARCHAR(500),
        price REAL NOT NULL,
        category VARCHAR(50),
        food_type VARCHAR(20) DEFAULT 'Vegetarian',
        image_url VARCHAR(200),
        preparation_time INTEGER DEFAULT 15,
        available BOOLEAN DEFAULT TRUE,
        is_popular BOOLEAN DEFAULT FALSE,
        ingredients TEXT,
        nutrition_info TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Food Orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS food_order (
        id SERIAL PRIMARY KEY,
        booking_id INTEGER REFERENCES booking(id) NOT NULL,
        user_id INTEGER REFERENCES "user"(id) NOT NULL,
        restaurant_id INTEGER REFERENCES restaurant(id) NOT NULL,
        delivery_station_id INTEGER REFERENCES station(id) NOT NULL,
        order_number VARCHAR(20) UNIQUE NOT NULL,
        total_amount REAL NOT NULL,
        delivery_charge REAL DEFAULT 0.0,
        tax_amount REAL DEFAULT 0.0,
        status VARCHAR(20) DEFAULT 'pending',
        special_instructions TEXT,
        delivery_time TIMESTAMP,
        contact_number VARCHAR(15) NOT NULL,
        coach_number VARCHAR(10),
        seat_number VARCHAR(10),
        payment_status VARCHAR(20) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Food Order Items table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS food_order_item (
        id SERIAL PRIMARY KEY,
        food_order_id INTEGER REFERENCES food_order(id) ON DELETE CASCADE,
        menu_item_id INTEGER REFERENCES menu_item(id) NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        total_price REAL NOT NULL,
        special_request VARCHAR(200)
    )
    """)
    
    # Loyalty Program table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loyalty_program (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES "user"(id) UNIQUE NOT NULL,
        membership_number VARCHAR(20) UNIQUE NOT NULL,
        tier VARCHAR(20) DEFAULT 'Silver',
        points_earned INTEGER DEFAULT 0,
        points_redeemed INTEGER DEFAULT 0,
        total_journeys INTEGER DEFAULT 0,
        total_distance REAL DEFAULT 0.0,
        total_spent REAL DEFAULT 0.0,
        tier_valid_until DATE,
        benefits_active BOOLEAN DEFAULT TRUE,
        joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Notification Preferences table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notification_preferences (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES "user"(id) UNIQUE NOT NULL,
        email_notifications BOOLEAN DEFAULT TRUE,
        sms_notifications BOOLEAN DEFAULT TRUE,
        push_notifications BOOLEAN DEFAULT TRUE,
        booking_confirmations BOOLEAN DEFAULT TRUE,
        journey_reminders BOOLEAN DEFAULT TRUE,
        train_delay_alerts BOOLEAN DEFAULT TRUE,
        food_order_updates BOOLEAN DEFAULT TRUE,
        promotional_offers BOOLEAN DEFAULT FALSE
    )
    """)
    
    # Additional tables for comprehensive functionality
    
    # Refund Requests table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS refund_request (
        id SERIAL PRIMARY KEY,
        booking_id INTEGER REFERENCES booking(id) NOT NULL,
        user_id INTEGER REFERENCES "user"(id) NOT NULL,
        reason VARCHAR(100) NOT NULL,
        amount_paid REAL NOT NULL,
        refund_amount REAL NOT NULL,
        cancellation_charges REAL DEFAULT 0.0,
        tdr_number VARCHAR(20) UNIQUE NOT NULL,
        status VARCHAR(20) DEFAULT 'pending',
        filed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processed_at TIMESTAMP
    )
    """)
    
    # Train Status table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS train_status (
        id SERIAL PRIMARY KEY,
        train_id INTEGER REFERENCES train(id) NOT NULL,
        current_station_id INTEGER REFERENCES station(id),
        status VARCHAR(50) DEFAULT 'On Time',
        delay_minutes INTEGER DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        journey_date DATE NOT NULL
    )
    """)
    
    # Seat Availability table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS seat_availability (
        id SERIAL PRIMARY KEY,
        train_id INTEGER REFERENCES train(id) NOT NULL,
        from_station_id INTEGER REFERENCES station(id) NOT NULL,
        to_station_id INTEGER REFERENCES station(id) NOT NULL,
        journey_date DATE NOT NULL,
        coach_class VARCHAR(10) NOT NULL,
        quota VARCHAR(20) DEFAULT 'general',
        available_seats INTEGER DEFAULT 0,
        waiting_list INTEGER DEFAULT 0,
        rac_seats INTEGER DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Chart Preparation table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chart_preparation (
        id SERIAL PRIMARY KEY,
        train_id INTEGER REFERENCES train(id) NOT NULL,
        journey_date DATE NOT NULL,
        chart_prepared_at TIMESTAMP,
        final_chart_at TIMESTAMP,
        status VARCHAR(20) DEFAULT 'pending',
        confirmed_from_waitlist INTEGER DEFAULT 0,
        cancelled_waitlist INTEGER DEFAULT 0
    )
    """)
    
    # Tatkal Override table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tatkal_override (
        id SERIAL PRIMARY KEY,
        train_id INTEGER REFERENCES train(id) NOT NULL,
        journey_date DATE NOT NULL,
        coach_class VARCHAR(10) NOT NULL,
        override_enabled BOOLEAN DEFAULT FALSE,
        override_reason VARCHAR(200),
        enabled_by INTEGER REFERENCES "user"(id),
        enabled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP
    )
    """)
    
    logger.info("✅ Database schema created successfully")

def generate_pnr():
    """Generate a unique 10-digit PNR number"""
    return ''.join(random.choices(string.digits, k=10))

def generate_transaction_id():
    """Generate transaction ID"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

def insert_users(cursor):
    """Insert admin and test users with proper roles"""
    logger.info("👥 Creating users...")
    
    users_data = [
        ('admin', 'admin@railserve.com', 'admin123', 'super_admin'),
        ('railadmin', 'railadmin@railserve.com', 'railadmin123', 'admin'),
        ('testuser', 'test@example.com', 'test123', 'user'),
        ('john_doe', 'john@example.com', 'password123', 'user'),
        ('jane_smith', 'jane@example.com', 'password123', 'user'),
        ('rajesh_kumar', 'rajesh@example.com', 'password123', 'user'),
        ('priya_sharma', 'priya@example.com', 'password123', 'user'),
        ('amit_patel', 'amit@example.com', 'password123', 'user'),
        ('neha_gupta', 'neha@example.com', 'password123', 'user'),
        ('vikram_singh', 'vikram@example.com', 'password123', 'user'),
        ('anjali_reddy', 'anjali@example.com', 'password123', 'user'),
        ('suresh_kumar', 'suresh@example.com', 'password123', 'user'),
        ('meera_nair', 'meera@example.com', 'password123', 'user'),
        ('arjun_mehta', 'arjun@example.com', 'password123', 'user'),
        ('kavya_shah', 'kavya@example.com', 'password123', 'user')
    ]
    
    user_ids = {}
    for username, email, password, role in users_data:
        password_hash = generate_password_hash(password)
        try:
            cursor.execute("""
                INSERT INTO "user" (username, email, password_hash, role, active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            """, (username, email, password_hash, role, True, datetime.utcnow()))
            
            result = cursor.fetchone()
            if result:
                user_id = result[0]
                user_ids[username] = user_id
                logger.info(f"✅ Created user: {username} ({role})")
        except psycopg2.IntegrityError:
            logger.warning(f"⚠️ User {username} already exists, skipping...")
            cursor.execute("SELECT id FROM \"user\" WHERE username = %s", (username,))
            result = cursor.fetchone()
            if result:
                user_ids[username] = result[0]
    
    logger.info(f"✅ Processed {len(user_ids)} users")
    return user_ids

def insert_stations(cursor):
    """Insert comprehensive railway stations"""
    logger.info("🚉 Inserting railway stations...")
    
    stations_data = [
        # Major Metropolitan Stations
        ('New Delhi', 'NDLS', 'New Delhi', 'Delhi'),
        ('Mumbai Central', 'BCT', 'Mumbai', 'Maharashtra'),
        ('Chennai Central', 'MAS', 'Chennai', 'Tamil Nadu'),
        ('Howrah Junction', 'HWH', 'Kolkata', 'West Bengal'),
        ('Kolkata', 'KOAA', 'Kolkata', 'West Bengal'),
        ('Bengaluru City', 'SBC', 'Bengaluru', 'Karnataka'),
        ('Hyderabad Deccan', 'HYB', 'Hyderabad', 'Telangana'),
        ('Pune Junction', 'PUNE', 'Pune', 'Maharashtra'),
        ('Ahmedabad Junction', 'ADI', 'Ahmedabad', 'Gujarat'),
        ('Jaipur Junction', 'JP', 'Jaipur', 'Rajasthan'),
        
        # North India Major Stations
        ('Lucknow Charbagh', 'LJN', 'Lucknow', 'Uttar Pradesh'),
        ('Kanpur Central', 'CNB', 'Kanpur', 'Uttar Pradesh'),
        ('Allahabad Junction', 'ALD', 'Prayagraj', 'Uttar Pradesh'),
        ('Varanasi Junction', 'BSB', 'Varanasi', 'Uttar Pradesh'),
        ('Agra Cantt', 'AGC', 'Agra', 'Uttar Pradesh'),
        ('Amritsar Junction', 'ASR', 'Amritsar', 'Punjab'),
        ('Jammu Tawi', 'JAT', 'Jammu', 'Jammu and Kashmir'),
        ('Chandigarh', 'CDG', 'Chandigarh', 'Chandigarh'),
        ('Dehradun', 'DDN', 'Dehradun', 'Uttarakhand'),
        ('Haridwar Junction', 'HW', 'Haridwar', 'Uttarakhand'),
        
        # West India Stations
        ('Surat', 'ST', 'Surat', 'Gujarat'),
        ('Vadodara Junction', 'BRC', 'Vadodara', 'Gujarat'),
        ('Rajkot Junction', 'RJT', 'Rajkot', 'Gujarat'),
        ('Bhavnagar Terminus', 'BVC', 'Bhavnagar', 'Gujarat'),
        ('Jodhpur Junction', 'JU', 'Jodhpur', 'Rajasthan'),
        ('Udaipur City', 'UDZ', 'Udaipur', 'Rajasthan'),
        ('Ajmer Junction', 'AII', 'Ajmer', 'Rajasthan'),
        ('Kota Junction', 'KOTA', 'Kota', 'Rajasthan'),
        
        # Central India Stations
        ('Bhopal Junction', 'BPL', 'Bhopal', 'Madhya Pradesh'),
        ('Indore Junction', 'INDB', 'Indore', 'Madhya Pradesh'),
        ('Jabalpur', 'JBP', 'Jabalpur', 'Madhya Pradesh'),
        ('Gwalior', 'GWL', 'Gwalior', 'Madhya Pradesh'),
        ('Nagpur', 'NGP', 'Nagpur', 'Maharashtra'),
        ('Raipur Junction', 'R', 'Raipur', 'Chhattisgarh'),
        ('Bilaspur Junction', 'BSP', 'Bilaspur', 'Chhattisgarh'),
        
        # East India Stations
        ('Patna Sahib', 'PNBE', 'Patna', 'Bihar'),
        ('Gaya Junction', 'GAYA', 'Gaya', 'Bihar'),
        ('Ranchi', 'RNC', 'Ranchi', 'Jharkhand'),
        ('Dhanbad Junction', 'DHN', 'Dhanbad', 'Jharkhand'),
        ('Bhubaneswar', 'BBS', 'Bhubaneswar', 'Odisha'),
        ('Cuttack', 'CTC', 'Cuttack', 'Odisha'),
        ('Guwahati', 'GHY', 'Guwahati', 'Assam'),
        
        # South India Stations
        ('Kochi Central', 'ERS', 'Kochi', 'Kerala'),
        ('Thiruvananthapuram Central', 'TVC', 'Thiruvananthapuram', 'Kerala'),
        ('Kozhikode', 'CLT', 'Kozhikode', 'Kerala'),
        ('Coimbatore Junction', 'CBE', 'Coimbatore', 'Tamil Nadu'),
        ('Madurai Junction', 'MDU', 'Madurai', 'Tamil Nadu'),
        ('Salem Junction', 'SA', 'Salem', 'Tamil Nadu'),
        ('Tirunelveli', 'TEN', 'Tirunelveli', 'Tamil Nadu'),
        ('Vijayawada Junction', 'BZA', 'Vijayawada', 'Andhra Pradesh'),
        ('Visakhapatnam', 'VSKP', 'Visakhapatnam', 'Andhra Pradesh'),
        ('Tirupati', 'TPTY', 'Tirupati', 'Andhra Pradesh'),
        ('Mysuru Junction', 'MYS', 'Mysuru', 'Karnataka'),
        ('Hubli Junction', 'UBL', 'Hubli', 'Karnataka'),
        ('Mangaluru Central', 'MAQ', 'Mangaluru', 'Karnataka'),
        ('Madgaon', 'MAO', 'Margao', 'Goa')
    ]
    
    station_ids = {}
    for name, code, city, state in stations_data:
        try:
            cursor.execute("""
                INSERT INTO station (name, code, city, state, active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            """, (name, code, city, state, True, datetime.utcnow()))
            
            result = cursor.fetchone()
            if result:
                station_id = result[0]
                station_ids[code] = station_id
        except psycopg2.IntegrityError:
            cursor.execute("SELECT id FROM station WHERE code = %s", (code,))
            result = cursor.fetchone()
            if result:
                station_ids[code] = result[0]
    
    logger.info(f"✅ Processed {len(station_ids)} stations")
    return station_ids

def insert_trains(cursor):
    """Insert trains with realistic data"""
    logger.info("🚂 Inserting trains...")
    
    trains_data = [
        # Rajdhani Express trains (Premium AC trains)
        ('12301', 'Rajdhani Express', 400, 350, 3.5, 40, 4.5),
        ('12302', 'New Delhi Rajdhani', 380, 340, 3.2, 38, 4.2),
        ('12951', 'Mumbai Rajdhani', 420, 380, 3.8, 42, 4.8),
        ('12009', 'Shatabdi Express', 300, 280, 2.8, 30, 3.5),
        ('12019', 'Shatabdi Express', 320, 290, 3.0, 32, 3.8),
        
        # Express trains
        ('12615', 'Grand Trunk Express', 500, 450, 2.0, 50, 2.8),
        ('12621', 'Tamil Nadu Express', 480, 430, 1.8, 48, 2.5),
        ('12840', 'Howrah Mail', 460, 410, 1.9, 46, 2.6),
        ('16031', 'Andaman Express', 520, 470, 1.7, 52, 2.3),
        ('12295', 'Sanghamitra Express', 440, 400, 1.6, 44, 2.2),
        
        # Superfast trains
        ('12649', 'Sampark Kranti Express', 480, 440, 1.8, 48, 2.4),
        ('12617', 'Mangala Lakshadweep Express', 460, 420, 1.7, 46, 2.3),
        ('12925', 'Paschim Express', 470, 430, 1.9, 47, 2.5),
        ('12507', 'Aronai Express', 450, 410, 1.6, 45, 2.2),
        ('12859', 'Gitanjali Express', 440, 400, 1.8, 44, 2.4),
        
        # Tejas and Premium trains
        ('22205', 'Tejas Express', 320, 290, 2.5, 32, 3.2),
        ('22691', 'Rajdhani Express', 390, 350, 3.4, 39, 4.4),
        ('12516', 'Trivandrum Express', 480, 440, 1.5, 48, 2.1),
        ('12645', 'Nizamuddin Express', 460, 420, 1.6, 46, 2.2),
        ('12781', 'Swarna Jayanti Express', 450, 410, 1.7, 45, 2.3),
        
        # Mail and Express trains
        ('12003', 'Lucknow Shatabdi', 310, 280, 2.2, 31, 2.9),
        ('12801', 'Purushottam Express', 470, 420, 1.6, 47, 2.2),
        ('12643', 'Thirukkural Express', 440, 400, 1.7, 44, 2.3),
        ('12129', 'Azad Hind Express', 450, 410, 1.8, 45, 2.4),
        ('12039', 'Shatabdi Express', 310, 280, 2.3, 31, 3.1)
    ]
    
    train_ids = {}
    for number, name, total_seats, available_seats, fare_per_km, tatkal_seats, tatkal_fare_per_km in trains_data:
        try:
            cursor.execute("""
                INSERT INTO train (number, name, total_seats, available_seats, fare_per_km, 
                                 tatkal_seats, tatkal_fare_per_km, active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, (number, name, total_seats, available_seats, fare_per_km, 
                  tatkal_seats, tatkal_fare_per_km, True, datetime.utcnow()))
            
            result = cursor.fetchone()
            if result:
                train_id = result[0]
                train_ids[number] = train_id
        except psycopg2.IntegrityError:
            cursor.execute("SELECT id FROM train WHERE number = %s", (number,))
            result = cursor.fetchone()
            if result:
                train_ids[number] = result[0]
    
    logger.info(f"✅ Processed {len(train_ids)} trains")
    return train_ids

def insert_comprehensive_data(cursor):
    """Insert all comprehensive test data"""
    logger.info("🏗️ Inserting comprehensive test data...")
    
    # Create database schema first
    create_database_schema(cursor)
    
    # Insert basic data
    user_ids = insert_users(cursor)
    station_ids = insert_stations(cursor)
    train_ids = insert_trains(cursor)
    
    # Create sample train routes
    logger.info("🗺️ Creating train routes...")
    # Simple routes for demonstration - in production, this would be much more comprehensive
    sample_routes = [
        ('12301', [('NDLS', 1, '16:55', '16:55', 0), ('BPL', 2, '02:30', '02:35', 707), ('BCT', 3, '08:30', '08:35', 1384)]),
        ('12002', [('NDLS', 1, '06:00', '06:00', 0), ('JP', 2, '10:30', '10:35', 308), ('PUNE', 3, '17:30', '17:35', 1533)]),
        ('16031', [('MAS', 1, '18:45', '18:45', 0), ('BZA', 2, '23:15', '23:20', 430), ('HWH', 3, '06:30', '06:35', 1678)]),
    ]
    
    route_count = 0
    for train_number, stations in sample_routes:
        if train_number in train_ids:
            train_id = train_ids[train_number]
            for station_code, sequence, arrival, departure, distance in stations:
                if station_code in station_ids:
                    station_id = station_ids[station_code]
                    try:
                        cursor.execute("""
                            INSERT INTO train_route (train_id, station_id, sequence, arrival_time, 
                                                   departure_time, distance_from_start, halt_duration, commercial_stop)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (train_id, station_id, sequence, arrival, departure, distance, 
                              5 if sequence > 1 else 0, True))
                        route_count += 1
                    except psycopg2.IntegrityError:
                        pass
    
    logger.info(f"✅ Created {route_count} train routes")
    
    # Insert sample bookings
    logger.info("🎫 Creating sample bookings...")
    booking_statuses = ['confirmed', 'waitlisted', 'cancelled', 'rac', 'pending_payment']
    coach_classes = ['AC1', 'AC2', 'AC3', 'SL', '2S', 'CC']
    
    booking_ids = []
    used_pnrs = set()
    
    for i in range(50):  # Create 50 sample bookings
        pnr = generate_pnr()
        while pnr in used_pnrs:
            pnr = generate_pnr()
        used_pnrs.add(pnr)
        
        user_id = random.choice(list(user_ids.values()))
        train_id = random.choice(list(train_ids.values()))
        
        station_id_list = list(station_ids.values())
        from_station_id = random.choice(station_id_list)
        to_station_id = random.choice(station_id_list)
        while to_station_id == from_station_id:
            to_station_id = random.choice(station_id_list)
        
        journey_date = date.today() + timedelta(days=random.randint(1, 90))
        passengers = random.randint(1, 4)
        coach_class = random.choice(coach_classes)
        status = random.choice(booking_statuses)
        
        # Calculate realistic fare
        distance_km = random.randint(200, 2000)
        base_fare = distance_km * random.uniform(1.5, 3.5)
        class_multipliers = {'AC1': 4.0, 'AC2': 2.8, 'AC3': 1.8, 'SL': 1.0, '2S': 0.6, 'CC': 1.2}
        total_amount = base_fare * class_multipliers.get(coach_class, 1.0) * passengers
        
        try:
            cursor.execute("""
                INSERT INTO booking (pnr, user_id, train_id, from_station_id, to_station_id,
                                   journey_date, passengers, total_amount, coach_class, status, booking_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, (pnr, user_id, train_id, from_station_id, to_station_id, journey_date,
                  passengers, total_amount, coach_class, status, datetime.utcnow()))
            
            result = cursor.fetchone()
            if result:
                booking_id = result[0]
                booking_ids.append(booking_id)
        except psycopg2.IntegrityError:
            continue
    
    logger.info(f"✅ Created {len(booking_ids)} sample bookings")
    
    # Insert sample payments
    logger.info("💳 Creating sample payments...")
    payment_methods = ['credit_card', 'debit_card', 'net_banking', 'upi', 'wallet']
    payment_statuses = ['success', 'failed', 'pending']
    
    payment_count = 0
    for booking_id in booking_ids[:30]:  # Create payments for first 30 bookings
        cursor.execute("SELECT total_amount, user_id FROM booking WHERE id = %s", (booking_id,))
        result = cursor.fetchone()
        if not result:
            continue
        
        amount, user_id = result
        payment_method = random.choice(payment_methods)
        status = random.choice(payment_statuses)
        transaction_id = generate_transaction_id()
        
        try:
            cursor.execute("""
                INSERT INTO payment (booking_id, user_id, amount, payment_method, status, transaction_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (booking_id, user_id, amount, payment_method, status, transaction_id, datetime.utcnow()))
            payment_count += 1
        except psycopg2.IntegrityError:
            pass
    
    logger.info(f"✅ Created {payment_count} payment records")
    
    # Insert sample restaurants
    logger.info("🍽️ Creating restaurants and menus...")
    restaurants_data = [
        ('Dominos Pizza', 'NDLS', 'Italian, Fast Food'),
        ('KFC', 'BCT', 'Fast Food, Chicken'),
        ('Subway', 'MAS', 'Sandwiches, Health Food'),
        ('Haldirams', 'HWH', 'Indian, Snacks'),
        ('Cafe Coffee Day', 'SBC', 'Beverages, Light Snacks'),
        ('Biryani Express', 'HYB', 'Indian, Biryani'),
        ('South Kitchen', 'PUNE', 'South Indian'),
        ('Punjabi Dhaba', 'ADI', 'North Indian, Punjabi'),
        ('Chinese Corner', 'JP', 'Chinese, Indo-Chinese'),
        ('Fresh Juice Bar', 'LJN', 'Beverages, Fresh Juices')
    ]
    
    restaurant_count = 0
    for name, station_code, cuisine in restaurants_data:
        if station_code in station_ids:
            station_id = station_ids[station_code]
            try:
                cursor.execute("""
                    INSERT INTO restaurant (name, station_id, cuisine_type, contact_number, rating, active, delivery_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (name, station_id, cuisine, '9876543210', round(random.uniform(3.8, 4.9), 1), True, random.randint(20, 45)))
                restaurant_count += 1
            except psycopg2.IntegrityError:
                pass
    
    logger.info(f"✅ Created {restaurant_count} restaurants")
    
    logger.info("✅ All comprehensive test data inserted successfully")

def main():
    """Main function to set up the database"""
    logger.info("🚀 Starting RailServe Database Setup...")
    
    conn = None
    try:
        # Connect to database
        logger.info("🔗 Connecting to database...")
        conn = get_db_connection()
        cursor = conn.cursor()
        logger.info("✅ Database connection successful")
        
        # Insert comprehensive data
        insert_comprehensive_data(cursor)
        
        # Final statistics
        logger.info("📊 Database Statistics:")
        
        tables = ['user', 'station', 'train', 'booking', 'payment', 'restaurant']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            result = cursor.fetchone()
            count = result[0] if result else 0
            logger.info(f"   {table.title()}: {count} records")
        
        logger.info("🎉 ✅ RailServe database setup completed successfully!")
        logger.info("🔐 Admin credentials: admin@railserve.com / admin123")
        logger.info("🔐 Test user: test@example.com / test123")
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()