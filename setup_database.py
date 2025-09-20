#!/usr/bin/env python3
"""
RailServe Comprehensive Database Setup Script
=============================================

This script creates a complete RailServe railway reservation system database
with extensive test data including 1500 stations, 1000 trains, and comprehensive
fake data for testing all features.

## Usage:
    export DATABASE_URL="postgresql://user:password@localhost:5432/railserve"
    python setup_database.py

## Features Created:
- 1500+ railway stations across India
- 1000+ trains with different classes and routes  
- Comprehensive route networks
- Waitlist management with realistic positions
- Food ordering system with restaurants and menus
- Group bookings for families/corporate
- PDF ticket generation support
- Real-time train status tracking
- TDR filing and refund processing
- Tatkal booking system
- Loyalty programs
- Complete booking quotas and types

## Test Data Includes:
- Admin users and regular users
- Confirmed bookings with seat assignments
- Waitlisted bookings with positions
- RAC bookings
- Tatkal bookings
- Food orders across different stations
- Train status updates
- Group bookings
- Refund requests
- Loyalty program memberships
"""

import os
import sys
import random
import string
import logging
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any, Optional
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:12345678@localhost:5432/railserve")

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    from werkzeug.security import generate_password_hash
    print("✅ All dependencies available")
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Install with: pip install psycopg2-binary werkzeug")
    sys.exit(1)

def create_database_if_needed():
    """Create the database if it doesn't exist"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(DATABASE_URL)
        db_name = parsed.path[1:]  # Remove leading slash
        
        # Connect to postgres database to create our database
        postgres_url = DATABASE_URL.replace(f'/{db_name}', '/postgres')
        
        logger.info("Checking if database exists...")
        conn = psycopg2.connect(postgres_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            logger.info(f"Creating database '{db_name}'...")
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            logger.info("✅ Database created")
        else:
            logger.info("✅ Database already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Database creation failed: {e}")
        return False

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return None

def create_tables(conn):
    """Create all database tables with comprehensive schema"""
    logger.info("🏗️ Creating database tables...")
    
    cursor = conn.cursor()
    
    # Drop all tables first (clean slate)
    cursor.execute("""
        DROP TABLE IF EXISTS notification_preferences CASCADE;
        DROP TABLE IF EXISTS loyalty_program CASCADE;
        DROP TABLE IF EXISTS tatkal_override CASCADE;
        DROP TABLE IF EXISTS food_order_item CASCADE;
        DROP TABLE IF EXISTS food_order CASCADE;
        DROP TABLE IF EXISTS menu_item CASCADE;
        DROP TABLE IF EXISTS restaurant CASCADE;
        DROP TABLE IF EXISTS chart_preparation CASCADE;
        DROP TABLE IF EXISTS seat_availability CASCADE;
        DROP TABLE IF EXISTS train_status CASCADE;
        DROP TABLE IF EXISTS refund_request CASCADE;
        DROP TABLE IF EXISTS tatkal_time_slot CASCADE;
        DROP TABLE IF EXISTS waitlist CASCADE;
        DROP TABLE IF EXISTS payment CASCADE;
        DROP TABLE IF EXISTS passenger CASCADE;
        DROP TABLE IF EXISTS booking CASCADE;
        DROP TABLE IF EXISTS group_booking CASCADE;
        DROP TABLE IF EXISTS train_route CASCADE;
        DROP TABLE IF EXISTS train CASCADE;
        DROP TABLE IF EXISTS station CASCADE;
        DROP TABLE IF EXISTS "user" CASCADE;
    """)
    
    # Create all tables matching the ORM models
    cursor.execute("""
        -- Users table with comprehensive authentication and roles
        CREATE TABLE "user" (
            id SERIAL PRIMARY KEY,
            username VARCHAR(64) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(256) NOT NULL,
            role VARCHAR(20) DEFAULT 'user',
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Railway stations - comprehensive coverage
        CREATE TABLE station (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            code VARCHAR(10) NOT NULL UNIQUE,
            city VARCHAR(50) NOT NULL,
            state VARCHAR(50) NOT NULL,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Trains with comprehensive features
        CREATE TABLE train (
            id SERIAL PRIMARY KEY,
            number VARCHAR(10) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            total_seats INTEGER NOT NULL,
            available_seats INTEGER NOT NULL,
            fare_per_km FLOAT NOT NULL,
            tatkal_seats INTEGER DEFAULT 0,
            tatkal_fare_per_km FLOAT,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Train routes with comprehensive coverage
        CREATE TABLE train_route (
            id SERIAL PRIMARY KEY,
            train_id INTEGER REFERENCES train(id) NOT NULL,
            station_id INTEGER REFERENCES station(id) NOT NULL,
            sequence INTEGER NOT NULL,
            arrival_time TIME,
            departure_time TIME,
            distance_from_start FLOAT NOT NULL DEFAULT 0,
            UNIQUE(train_id, sequence)
        );
        
        -- Group bookings for families/corporate
        CREATE TABLE group_booking (
            id SERIAL PRIMARY KEY,
            group_name VARCHAR(100) NOT NULL,
            group_leader_id INTEGER REFERENCES "user"(id),
            total_passengers INTEGER DEFAULT 0,
            contact_email VARCHAR(120),
            contact_phone VARCHAR(15),
            booking_type VARCHAR(20) DEFAULT 'family',
            special_requirements TEXT,
            discount_applied FLOAT DEFAULT 0.0,
            group_discount_rate FLOAT DEFAULT 0.0,
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Bookings with comprehensive features
        CREATE TABLE booking (
            id SERIAL PRIMARY KEY,
            pnr VARCHAR(10) NOT NULL UNIQUE,
            user_id INTEGER REFERENCES "user"(id) NOT NULL,
            train_id INTEGER REFERENCES train(id) NOT NULL,
            from_station_id INTEGER REFERENCES station(id) NOT NULL,
            to_station_id INTEGER REFERENCES station(id) NOT NULL,
            journey_date DATE NOT NULL,
            passengers INTEGER NOT NULL,
            total_amount FLOAT NOT NULL,
            booking_type VARCHAR(10) DEFAULT 'general',
            quota VARCHAR(20) DEFAULT 'general',
            coach_class VARCHAR(10) DEFAULT 'SL',
            status VARCHAR(20) DEFAULT 'pending_payment',
            waitlist_type VARCHAR(10) DEFAULT 'GNWL',
            chart_prepared BOOLEAN DEFAULT FALSE,
            berth_preference VARCHAR(20) DEFAULT 'No Preference',
            current_reservation BOOLEAN DEFAULT FALSE,
            booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cancellation_charges FLOAT DEFAULT 0.0,
            group_booking_id INTEGER REFERENCES group_booking(id),
            loyalty_discount FLOAT DEFAULT 0.0
        );
        
        -- Passengers with comprehensive seat allocation
        CREATE TABLE passenger (
            id SERIAL PRIMARY KEY,
            booking_id INTEGER REFERENCES booking(id) NOT NULL,
            name VARCHAR(100) NOT NULL,
            age INTEGER NOT NULL,
            gender VARCHAR(10) NOT NULL,
            id_proof_type VARCHAR(20) NOT NULL,
            id_proof_number VARCHAR(50) NOT NULL,
            seat_preference VARCHAR(20) DEFAULT 'No Preference',
            coach_class VARCHAR(10) DEFAULT 'SL',
            seat_number VARCHAR(20),
            berth_type VARCHAR(20)
        );
        
        -- Payments with comprehensive tracking
        CREATE TABLE payment (
            id SERIAL PRIMARY KEY,
            booking_id INTEGER REFERENCES booking(id) NOT NULL,
            user_id INTEGER REFERENCES "user"(id) NOT NULL,
            amount FLOAT NOT NULL,
            payment_method VARCHAR(20) NOT NULL,
            transaction_id VARCHAR(50),
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            CONSTRAINT uq_booking_payment_success UNIQUE(booking_id, status)
        );
        
        -- Waitlist management with comprehensive tracking
        CREATE TABLE waitlist (
            id SERIAL PRIMARY KEY,
            booking_id INTEGER REFERENCES booking(id) NOT NULL,
            train_id INTEGER REFERENCES train(id) NOT NULL,
            journey_date DATE NOT NULL,
            position INTEGER NOT NULL,
            waitlist_type VARCHAR(10) DEFAULT 'GNWL',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tatkal time slots for premium booking
        CREATE TABLE tatkal_time_slot (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            coach_classes VARCHAR(200),
            open_time TIME NOT NULL,
            close_time TIME,
            days_before_journey INTEGER DEFAULT 1,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER REFERENCES "user"(id)
        );
        
        -- Refund requests and TDR management
        CREATE TABLE refund_request (
            id SERIAL PRIMARY KEY,
            booking_id INTEGER REFERENCES booking(id) NOT NULL,
            user_id INTEGER REFERENCES "user"(id) NOT NULL,
            reason VARCHAR(100) NOT NULL,
            amount_paid FLOAT NOT NULL,
            refund_amount FLOAT NOT NULL,
            cancellation_charges FLOAT DEFAULT 0.0,
            tdr_number VARCHAR(20) UNIQUE NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            filed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP
        );
        
        -- Train status tracking for real-time updates
        CREATE TABLE train_status (
            id SERIAL PRIMARY KEY,
            train_id INTEGER REFERENCES train(id) NOT NULL,
            current_station_id INTEGER REFERENCES station(id),
            status VARCHAR(50) DEFAULT 'On Time',
            delay_minutes INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            journey_date DATE NOT NULL
        );
        
        -- Seat availability tracking
        CREATE TABLE seat_availability (
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
        );
        
        -- Chart preparation tracking
        CREATE TABLE chart_preparation (
            id SERIAL PRIMARY KEY,
            train_id INTEGER REFERENCES train(id) NOT NULL,
            journey_date DATE NOT NULL,
            chart_prepared_at TIMESTAMP,
            final_chart_at TIMESTAMP,
            status VARCHAR(20) DEFAULT 'pending',
            confirmed_from_waitlist INTEGER DEFAULT 0,
            cancelled_waitlist INTEGER DEFAULT 0
        );
        
        -- Food service restaurants
        CREATE TABLE restaurant (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            station_id INTEGER REFERENCES station(id),
            contact_number VARCHAR(15),
            email VARCHAR(120),
            cuisine_type VARCHAR(50),
            rating FLOAT DEFAULT 4.0,
            delivery_time INTEGER DEFAULT 30,
            minimum_order FLOAT DEFAULT 0.0,
            delivery_charge FLOAT DEFAULT 0.0,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Food menu items
        CREATE TABLE menu_item (
            id SERIAL PRIMARY KEY,
            restaurant_id INTEGER REFERENCES restaurant(id) NOT NULL,
            name VARCHAR(100) NOT NULL,
            description VARCHAR(500),
            price FLOAT NOT NULL,
            category VARCHAR(50),
            food_type VARCHAR(20) DEFAULT 'Vegetarian',
            image_url VARCHAR(200),
            preparation_time INTEGER DEFAULT 15,
            available BOOLEAN DEFAULT TRUE,
            is_popular BOOLEAN DEFAULT FALSE,
            ingredients TEXT,
            nutrition_info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Food orders linked to bookings
        CREATE TABLE food_order (
            id SERIAL PRIMARY KEY,
            booking_id INTEGER REFERENCES booking(id) NOT NULL,
            user_id INTEGER REFERENCES "user"(id) NOT NULL,
            restaurant_id INTEGER REFERENCES restaurant(id) NOT NULL,
            delivery_station_id INTEGER REFERENCES station(id) NOT NULL,
            order_number VARCHAR(20) UNIQUE NOT NULL,
            total_amount FLOAT NOT NULL,
            delivery_charge FLOAT DEFAULT 0.0,
            tax_amount FLOAT DEFAULT 0.0,
            status VARCHAR(20) DEFAULT 'pending',
            special_instructions TEXT,
            delivery_time TIMESTAMP,
            contact_number VARCHAR(15) NOT NULL,
            coach_number VARCHAR(10),
            seat_number VARCHAR(10),
            payment_status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Food order items
        CREATE TABLE food_order_item (
            id SERIAL PRIMARY KEY,
            food_order_id INTEGER REFERENCES food_order(id) NOT NULL,
            menu_item_id INTEGER REFERENCES menu_item(id) NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price FLOAT NOT NULL,
            total_price FLOAT NOT NULL,
            special_request VARCHAR(200)
        );
        
        -- Loyalty program for frequent travelers
        CREATE TABLE loyalty_program (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES "user"(id) NOT NULL UNIQUE,
            membership_number VARCHAR(20) UNIQUE NOT NULL,
            tier VARCHAR(20) DEFAULT 'Silver',
            points_earned INTEGER DEFAULT 0,
            points_redeemed INTEGER DEFAULT 0,
            total_journeys INTEGER DEFAULT 0,
            total_distance FLOAT DEFAULT 0.0,
            total_spent FLOAT DEFAULT 0.0,
            tier_valid_until DATE,
            benefits_active BOOLEAN DEFAULT TRUE,
            joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- User notification preferences
        CREATE TABLE notification_preferences (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES "user"(id) NOT NULL UNIQUE,
            email_notifications BOOLEAN DEFAULT TRUE,
            sms_notifications BOOLEAN DEFAULT TRUE,
            push_notifications BOOLEAN DEFAULT TRUE,
            booking_confirmations BOOLEAN DEFAULT TRUE,
            journey_reminders BOOLEAN DEFAULT TRUE,
            train_delay_alerts BOOLEAN DEFAULT TRUE,
            food_order_updates BOOLEAN DEFAULT TRUE,
            promotional_offers BOOLEAN DEFAULT FALSE
        );
        
        -- Tatkal override for emergency bookings
        CREATE TABLE tatkal_override (
            id SERIAL PRIMARY KEY,
            train_id INTEGER REFERENCES train(id) NOT NULL,
            journey_date DATE NOT NULL,
            override_reason VARCHAR(200) NOT NULL,
            additional_quota INTEGER DEFAULT 0,
            created_by INTEGER REFERENCES "user"(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            active BOOLEAN DEFAULT TRUE
        );
    """)
    
    conn.commit()
    cursor.close()
    logger.info("✅ Database tables created")

def generate_pnr():
    """Generate a unique 10-digit PNR"""
    return ''.join(random.choices(string.digits, k=10))

def generate_tdr_number():
    """Generate a unique TDR number"""
    return f"TDR{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"

def generate_order_number():
    """Generate a unique food order number"""
    return f"FD{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"

def generate_membership_number():
    """Generate a unique loyalty membership number"""
    return f"RL{datetime.now().strftime('%Y')}{random.randint(100000, 999999)}"

def get_comprehensive_stations_data():
    """Generate comprehensive stations data for all major Indian railway stations"""
    
    # Major stations across all Indian states
    major_stations = [
        # Delhi
        ('New Delhi Railway Station', 'NDLS', 'Delhi', 'Delhi'),
        ('Old Delhi Junction', 'DLI', 'Delhi', 'Delhi'),
        ('Nizamuddin Railway Station', 'NZM', 'Delhi', 'Delhi'),
        ('Anand Vihar Terminal', 'ANVT', 'Delhi', 'Delhi'),
        ('Delhi Sarai Rohilla', 'DEE', 'Delhi', 'Delhi'),
        ('Delhi Cantt', 'DEC', 'Delhi', 'Delhi'),
        
        # Mumbai
        ('Mumbai Central', 'MMCT', 'Mumbai', 'Maharashtra'),
        ('Chhatrapati Shivaji Terminus', 'CSMT', 'Mumbai', 'Maharashtra'),
        ('Lokmanya Tilak Terminus', 'LTT', 'Mumbai', 'Maharashtra'),
        ('Mumbai Bandra Terminus', 'BDTS', 'Mumbai', 'Maharashtra'),
        ('Dadar Central', 'DR', 'Mumbai', 'Maharashtra'),
        ('Kurla Junction', 'LTT', 'Mumbai', 'Maharashtra'),
        
        # Chennai
        ('Chennai Central', 'MAS', 'Chennai', 'Tamil Nadu'),
        ('Chennai Egmore', 'MS', 'Chennai', 'Tamil Nadu'),
        ('Chennai Beach', 'MSB', 'Chennai', 'Tamil Nadu'),
        
        # Kolkata
        ('Kolkata Howrah', 'HWH', 'Kolkata', 'West Bengal'),
        ('Sealdah', 'SDAH', 'Kolkata', 'West Bengal'),
        ('Kolkata Station', 'KOAA', 'Kolkata', 'West Bengal'),
        
        # Bangalore
        ('Bangalore City Junction', 'SBC', 'Bangalore', 'Karnataka'),
        ('Bangalore Cantonment', 'BNC', 'Bangalore', 'Karnataka'),
        ('Yeshwantpur Junction', 'YPR', 'Bangalore', 'Karnataka'),
        
        # Hyderabad
        ('Hyderabad Deccan', 'HYB', 'Hyderabad', 'Telangana'),
        ('Secunderabad Junction', 'SC', 'Secunderabad', 'Telangana'),
        ('Kacheguda', 'KCG', 'Hyderabad', 'Telangana'),
        
        # Other major cities
        ('Pune Junction', 'PUNE', 'Pune', 'Maharashtra'),
        ('Ahmedabad Junction', 'ADI', 'Ahmedabad', 'Gujarat'),
        ('Jaipur Junction', 'JP', 'Jaipur', 'Rajasthan'),
        ('Lucknow Junction', 'LJN', 'Lucknow', 'Uttar Pradesh'),
        ('Kanpur Central', 'CNB', 'Kanpur', 'Uttar Pradesh'),
        ('Agra Cantt', 'AGC', 'Agra', 'Uttar Pradesh'),
        ('Varanasi Junction', 'BSB', 'Varanasi', 'Uttar Pradesh'),
        ('Patna Junction', 'PNBE', 'Patna', 'Bihar'),
        ('Bhopal Junction', 'BPL', 'Bhopal', 'Madhya Pradesh'),
        ('Indore Junction', 'INDB', 'Indore', 'Madhya Pradesh'),
        ('Nagpur Junction', 'NGP', 'Nagpur', 'Maharashtra'),
        ('Coimbatore Junction', 'CBE', 'Coimbatore', 'Tamil Nadu'),
        ('Thiruvananthapuram Central', 'TVC', 'Thiruvananthapuram', 'Kerala'),
        ('Guwahati Junction', 'GHY', 'Guwahati', 'Assam'),
        ('Surat', 'ST', 'Surat', 'Gujarat'),
        ('Vadodara Junction', 'BRC', 'Vadodara', 'Gujarat'),
        ('Rajkot Junction', 'RJT', 'Rajkot', 'Gujarat'),
        ('Jodhpur Junction', 'JU', 'Jodhpur', 'Rajasthan'),
        ('Kota Junction', 'KOTA', 'Kota', 'Rajasthan'),
        ('Ajmer Junction', 'AII', 'Ajmer', 'Rajasthan'),
        ('Bikaner Junction', 'BKN', 'Bikaner', 'Rajasthan'),
        ('Udaipur City', 'UDZ', 'Udaipur', 'Rajasthan'),
        ('Amritsar Junction', 'ASR', 'Amritsar', 'Punjab'),
        ('Ludhiana Junction', 'LDH', 'Ludhiana', 'Punjab'),
        ('Jalandhar City', 'JRC', 'Jalandhar', 'Punjab'),
        ('Chandigarh Junction', 'CDG', 'Chandigarh', 'Chandigarh'),
        ('Jammu Tawi', 'JAT', 'Jammu', 'Jammu and Kashmir'),
        ('Srinagar', 'SINA', 'Srinagar', 'Jammu and Kashmir'),
        ('Dehradun', 'DDN', 'Dehradun', 'Uttarakhand'),
        ('Haridwar Junction', 'HW', 'Haridwar', 'Uttarakhand'),
        ('Rishikesh', 'RKSH', 'Rishikesh', 'Uttarakhand'),
        ('Shimla', 'SML', 'Shimla', 'Himachal Pradesh'),
        ('Manali', 'MNLI', 'Manali', 'Himachal Pradesh'),
    ]
    
    # Generate additional stations to reach 1500+
    state_cities = {
        'Uttar Pradesh': ['Allahabad', 'Gorakhpur', 'Bareilly', 'Aligarh', 'Moradabad', 'Saharanpur', 'Firozabad', 'Jhansi', 'Muzaffarnagar', 'Mathura', 'Rampur', 'Shahjahanpur', 'Farrukhabad', 'Khurja', 'Hardoi', 'Raebareli', 'Etawah', 'Orai', 'Bahraich', 'Kheri', 'Sitapur', 'Lalitpur', 'Pilibhit', 'Hathras', 'Banda', 'Unnao', 'Jalaun', 'Ballia', 'Hamirpur', 'Fatehpur', 'Pratapgarh', 'Azamgarh', 'Sultanpur', 'Maharajganj', 'Gonda', 'Basti', 'Siddhartnagar', 'Faizabad', 'Amethi', 'Kushinagar', 'Deoria', 'Mau', 'Ghazipur', 'Jaunpur', 'Chandauli', 'Bhadohi', 'Mirzapur', 'Sonbhadra'],
        'Maharashtra': ['Nashik', 'Aurangabad', 'Solapur', 'Amravati', 'Kolhapur', 'Sangli', 'Malegaon', 'Akola', 'Latur', 'Dhule', 'Ahmednagar', 'Chandrapur', 'Parbhani', 'Ichalkaranji', 'Jalgaon', 'Ambernath', 'Bhusawal', 'Panvel', 'Badlapur', 'Beed', 'Gondia', 'Satara', 'Barshi', 'Yavatmal', 'Achalpur', 'Osmanabad', 'Nandurbar', 'Wardha', 'Udgir', 'Hinganghat'],
        'Tamil Nadu': ['Madurai', 'Salem', 'Tirupur', 'Erode', 'Vellore', 'Thoothukudi', 'Dindigul', 'Thanjavur', 'Ranipet', 'Sivakasi', 'Karur', 'Udhagamandalam', 'Hosur', 'Nagercoil', 'Kanchipuram', 'Kumarakonam', 'Pudukkottai', 'Ambur', 'Pollachi', 'Rajapalayam', 'Virudhunagar', 'Tindivanam', 'Aruppukkottai', 'Paramakudi', 'Singaperumalkoil', 'Srivilliputhur', 'Gudiyatham', 'Vaniyambadi', 'Gingee', 'Tiruvannamalai'],
        'West Bengal': ['Durgapur', 'Asansol', 'Siliguri', 'Bardhaman', 'Malda', 'Baharampur', 'Habra', 'Kharagpur', 'Shantipur', 'Dankuni', 'Serampore', 'Raiganj', 'Krishnanagar', 'Gourpur', 'Ranaghat', 'Haldia', 'Halisahar', 'Howrah', 'Chandannagar', 'Bally', 'Barrackpore', 'Bankura', 'Purulia', 'Midnapore', 'Balurghat', 'Jalpaiguri', 'Cooch Behar', 'Darjeeling', 'Kalimpong'],
        'Karnataka': ['Mysore', 'Hubli', 'Mangalore', 'Belgaum', 'Gulbarga', 'Davanagere', 'Bellary', 'Bijapur', 'Shimoga', 'Tumkur', 'Raichur', 'Bidar', 'Hospet', 'Gadag', 'Udupi', 'Bhadravati', 'Chitradurga', 'Kolar', 'Mandya', 'Hassan', 'Dharwad', 'Bagalkot', 'Karwar', 'Chamrajnagar', 'Chikmagalur', 'Koppal', 'Haveri', 'Davangere', 'Yadgir'],
        'Gujarat': ['Rajkot', 'Bhavnagar', 'Jamnagar', 'Gandhinagar', 'Junagadh', 'Gandhidham', 'Anand', 'Morbi', 'Mahesana', 'Bharuch', 'Vapi', 'Navsari', 'Veraval', 'Porbandar', 'Godhra', 'Bhuj', 'Ankleshwar', 'Botad', 'Palanpur', 'Deesa', 'Dhoraji', 'Jetpur', 'Radhanpur', 'Mahuva', 'Modasa', 'Keshod', 'Mangrol', 'Unjha', 'Sidhpur', 'Viramgam'],
        'Rajasthan': ['Kota', 'Ajmer', 'Bikaner', 'Udaipur', 'Jodhpur', 'Bhilwara', 'Alwar', 'Bharatpur', 'Sikar', 'Pali', 'Sri Ganganagar', 'Kishangarh', 'Baran', 'Dhaulpur', 'Tonk', 'Beawar', 'Hanumangarh', 'Gangapur City', 'Banswara', 'Makrana', 'Sujangarh', 'Sardarshahar', 'Ladnu', 'Nokha', 'Nagaur', 'Jhunjhunu', 'Churu', 'Jhalawar', 'Barmer', 'Jaisalmer'],
        'Punjab': ['Bathinda', 'Patiala', 'Mohali', 'Firozpur', 'Batala', 'Pathankot', 'Moga', 'Abohar', 'Malerkotla', 'Khanna', 'Phagwara', 'Muktsar', 'Barnala', 'Rajpura', 'Hoshiarpur', 'Kapurthala', 'Faridkot', 'Sunam', 'Jagraon', 'Gurdaspur', 'Kharar', 'Gobindgarh', 'Mansa', 'Malout', 'Nabha', 'Tarn Taran', 'Jandiala Guru', 'Sahibzada Ajit Singh Nagar', 'Zirakpur', 'Kot Kapura'],
        'Haryana': ['Faridabad', 'Gurgaon', 'Panipat', 'Ambala', 'Yamunanagar', 'Rohtak', 'Hisar', 'Karnal', 'Sonipat', 'Panchkula', 'Bhiwani', 'Sirsa', 'Bahadurgarh', 'Jind', 'Thanesar', 'Kaithal', 'Palwal', 'Rewari', 'Hansi', 'Narnaul', 'Fatehabad', 'Gohana', 'Tohana', 'Narwana', 'Mandi Dabwali', 'Ladwa', 'Sohna', 'Safidon', 'Taraori', 'Mahendragarh'],
        'Madhya Pradesh': ['Indore', 'Bhopal', 'Jabalpur', 'Gwalior', 'Ujjain', 'Sagar', 'Dewas', 'Satna', 'Ratlam', 'Rewa', 'Murwara', 'Singrauli', 'Burhanpur', 'Khandwa', 'Morena', 'Bhind', 'Guna', 'Shivpuri', 'Vidisha', 'Chhatarpur', 'Damoh', 'Mandsaur', 'Khargone', 'Neemuch', 'Pithampur', 'Narmadapuram', 'Itarsi', 'Sehore', 'Ashta', 'Sendhwa'],
        'Bihar': ['Gaya', 'Bhagalpur', 'Muzaffarpur', 'Purnia', 'Darbhanga', 'Bihar Sharif', 'Arrah', 'Begusarai', 'Katihar', 'Munger', 'Chhapra', 'Danapur', 'Saharsa', 'Hajipur', 'Sasaram', 'Dehri', 'Siwan', 'Motihari', 'Nawada', 'Bagaha', 'Buxar', 'Kishanganj', 'Sitamarhi', 'Jamalpur', 'Jehanabad', 'Aurangabad', 'Lakhisarai', 'Sheikhpura', 'Madhepura', 'Supaul'],
        'Odisha': ['Bhubaneswar', 'Cuttack', 'Rourkela', 'Brahmapur', 'Sambalpur', 'Puri', 'Balasore', 'Bhadrak', 'Baripada', 'Jharsuguda', 'Jeypore', 'Balangir', 'Rayagada', 'Koraput', 'Kendujhar', 'Sundargarh', 'Paradip', 'Barbil', 'Khordha', 'Jatni', 'Anugul', 'Talcher', 'Rajgangpur', 'Titlagarh', 'Bhawanipatna', 'Nabarangpur', 'Malkangiri', 'Nuapada', 'Kalahandi', 'Kandhamal'],
        'Assam': ['Guwahati', 'Silchar', 'Dibrugarh', 'Jorhat', 'Nagaon', 'Tinsukia', 'Tezpur', 'Bongaigaon', 'Dhubri', 'Diphu', 'North Lakhimpur', 'Karimganj', 'Sivasagar', 'Goalpara', 'Barpeta', 'Mangaldoi', 'Haflong', 'Hailakandi', 'Morigaon', 'Nalbari', 'Rangia', 'Mariani', 'Digboi', 'Doom Dooma', 'Makum', 'Margherita', 'Namrup', 'Duliajan', 'Tingkhong', 'Sadiya'],
        'Kerala': ['Kochi', 'Kozhikode', 'Thrissur', 'Kollam', 'Alappuzha', 'Kottayam', 'Palakkad', 'Malappuram', 'Kannur', 'Kasaragod', 'Idukki', 'Pathanamthitta', 'Wayanad', 'Ernakulam', 'Cherthala', 'Kayamkulam', 'Changanassery', 'Muvattupuzha', 'Kothamangalam', 'Perumbavoor', 'Angamaly', 'Chalakudy', 'Guruvayoor', 'Kodungallur', 'Irinjalakuda', 'Kunnamkulam', 'Ottappalam', 'Shoranur', 'Nilambur', 'Tirur'],
        'Andhra Pradesh': ['Visakhapatnam', 'Vijayawada', 'Guntur', 'Nellore', 'Kurnool', 'Rajahmundry', 'Tirupati', 'Kadapa', 'Kakinada', 'Anantapur', 'Vizianagaram', 'Eluru', 'Ongole', 'Nandyal', 'Machilipatnam', 'Adoni', 'Tenali', 'Proddatur', 'Chittoor', 'Hindupur', 'Bhimavaram', 'Madanapalle', 'Guntakal', 'Dharmavaram', 'Gudivada', 'Narasaraopet', 'Tadipatri', 'Mangalagiri', 'Chilakaluripet', 'Yemmiganur'],
        'Telangana': ['Warangal', 'Nizamabad', 'Khammam', 'Karimnagar', 'Ramagundam', 'Mahbubnagar', 'Nalgonda', 'Adilabad', 'Suryapet', 'Miryalaguda', 'Jagtial', 'Mancherial', 'Nirmal', 'Kamareddy', 'Wanaparthy', 'Kothagudem', 'Bodhan', 'Sangareddy', 'Metpally', 'Zaheerabad', 'Medak', 'Siddipet', 'Jangaon', 'Bhongir', 'Vikarabad', 'Kodad', 'Suryapet', 'Palvancha', 'Manuguru', 'Bellampalli'],
        'Jharkhand': ['Ranchi', 'Jamshedpur', 'Dhanbad', 'Bokaro', 'Deoghar', 'Phusro', 'Hazaribagh', 'Giridih', 'Ramgarh', 'Medininagar', 'Chirkunda', 'Sahibganj', 'Chaibasa', 'Dumka', 'Madhupur', 'Gumla', 'Mihijam', 'Lohardaga', 'Hunterganj', 'Chakradharpur', 'Jhumri Telaiya', 'Koderma', 'Daltonganj', 'Godda', 'Saunda', 'Rajmahal', 'Simdega', 'Khunti', 'Saraikela', 'Pakur'],
        'Chhattisgarh': ['Raipur', 'Bhilai', 'Korba', 'Bilaspur', 'Durg', 'Rajnandgaon', 'Jagdalpur', 'Raigarh', 'Ambikapur', 'Mahasamund', 'Dhamtari', 'Kanker', 'Bastar', 'Sukma', 'Kondagaon', 'Narayanpur', 'Bijapur', 'Dantewada', 'Gariaband', 'Balod', 'Baloda Bazar', 'Bemetara', 'Mungeli', 'Surajpur', 'Balrampur', 'Jashpur', 'Korea', 'Surguja', 'Janjgir-Champa', 'Kabirdham'],
        'Uttarakhand': ['Dehradun', 'Haridwar', 'Roorkee', 'Haldwani', 'Rudrapur', 'Kashipur', 'Rishikesh', 'Kotdwar', 'Ramnagar', 'Manglaur', 'Laksar', 'Muzaffarnagar', 'Najibabad', 'Bijnor', 'Kichha', 'Sitarganj', 'Jaspur', 'Bazpur', 'Gadarpur', 'Khatima', 'Tanakpur', 'Champawat', 'Lohaghat', 'Pithoragarh', 'Joshimath', 'Gopeshwar', 'Karnaprayag', 'Srinagar', 'Pauri', 'Lansdowne'],
        'Himachal Pradesh': ['Shimla', 'Dharamshala', 'Solan', 'Mandi', 'Palampur', 'Baddi', 'Nahan', 'Una', 'Hamirpur', 'Bilaspur', 'Kullu', 'Chamba', 'Kangra', 'Nurpur', 'Amb', 'Mehatpur', 'Gagret', 'Daulatpur', 'Arki', 'Nalagarh', 'Kasauli', 'Parwanoo', 'Kalka', 'Pinjore', 'Naraingarh', 'Jagadhri', 'Yamunanagar', 'Kurukshetra', 'Thanesar', 'Shahabad'],
        'Jammu and Kashmir': ['Jammu', 'Srinagar', 'Anantnag', 'Baramulla', 'Sopore', 'Kupwara', 'Handwara', 'Bandipora', 'Ganderbal', 'Budgam', 'Pulwama', 'Shopian', 'Kulgam', 'Rajouri', 'Poonch', 'Reasi', 'Ramban', 'Doda', 'Kishtwar', 'Udhampur', 'Kathua', 'Samba', 'Leh', 'Kargil', 'Drass', 'Zanskar', 'Nubra', 'Turtuk', 'Diskit', 'Hunder'],
        'Goa': ['Panaji', 'Vasco da Gama', 'Margao', 'Mapusa', 'Ponda', 'Bicholim', 'Curchorem', 'Sanquelim', 'Valpoi', 'Quepem', 'Cuncolim', 'Canacona', 'Pernem', 'Aldona', 'Arambol', 'Anjuna', 'Calangute', 'Candolim', 'Benaulim', 'Colva', 'Palolem', 'Agonda', 'Chaudi', 'Loutolim', 'Chinchinim', 'Cortalim', 'Dabolim', 'Verna', 'Bogmalo', 'Majorda'],
        'Manipur': ['Imphal', 'Thoubal', 'Bishnupur', 'Churachandpur', 'Senapati', 'Ukhrul', 'Chandel', 'Tamenglong', 'Jiribam', 'Kangpokpi', 'Tengnoupal', 'Pherzawl', 'Noney', 'Kamjong', 'Kakching', 'Mayang Imphal', 'Wangjing', 'Sugnu', 'Moreh', 'Mao', 'Purul', 'Tamei', 'Litan', 'Pallel', 'Wangjing', 'Lilong', 'Thoubal', 'Kakching', 'Wangoi', 'Sekmai'],
        'Meghalaya': ['Shillong', 'Tura', 'Jowai', 'Nongpoh', 'Baghmara', 'Williamnagar', 'Resubelpara', 'Ampati', 'Mawkyrwat', 'Nongstoin', 'Mairang', 'Ranikor', 'Mawsynram', 'Cherrapunji', 'Dawki', 'Bholaganj', 'Umiam', 'Byrnihat', 'Ri-Bhoi', 'Sohra', 'Laitkyrhong', 'Mawphlang', 'Mawlai', 'Laban', 'Lawsohtun', 'Nongthymmai', 'Laitumkhrah', 'Jhalupara', 'Polo', 'Mawlyngot'],
        'Tripura': ['Agartala', 'Dharmanagar', 'Udaipur', 'Kailasahar', 'Belonia', 'Khowai', 'Ambassa', 'Kamalpur', 'Sabroom', 'Sonamura', 'Bishalgarh', 'Teliamura', 'Gandacherra', 'Kumarghat', 'Panisagar', 'Fatikroy', 'Jirania', 'Mohanpur', 'Melaghar', 'Mandai', 'Kakraban', 'Kanchanpur', 'Rajnagar', 'Matabari', 'Boxanagar', 'Simna', 'Dhalai', 'Longtharai', 'Chawmanu', 'Amarpur'],
        'Mizoram': ['Aizawl', 'Lunglei', 'Saiha', 'Champhai', 'Kolasib', 'Serchhip', 'Mamit', 'Lawngtlai', 'Saitual', 'Khawzawl', 'Hnahthial', 'Bairabi', 'Vairengte', 'Thenzawl', 'Darlawn', 'Tlabung', 'Zawlnuam', 'Biate', 'Khawhai', 'Tuipang', 'Sangau', 'Chawngte', 'Tuirial', 'Demagiri', 'Kawrthah', 'Phullen', 'Ratu', 'Kawlkulh', 'Tlungvel', 'Kawmzawl'],
        'Nagaland': ['Kohima', 'Dimapur', 'Mokokchung', 'Tuensang', 'Wokha', 'Mon', 'Zunheboto', 'Phek', 'Longleng', 'Kiphire', 'Peren', 'Chumukedima', 'Niuland', 'Noklak', 'Shamator', 'Tuli', 'Changtongya', 'Aboi', 'Longkhim', 'Tizit', 'Chessore', 'Angetyongpang', 'Mopungchuket', 'Yongnyah', 'Noksen', 'Longkhum', 'Ungma', 'Ao Senden', 'Longsa', 'Changsang'],
        'Arunachal Pradesh': ['Itanagar', 'Naharlagun', 'Pasighat', 'Aalo', 'Bomdila', 'Tawang', 'Ziro', 'Tezu', 'Changlang', 'Khonsa', 'Seppa', 'Yingkiong', 'Anini', 'Daporijo', 'Basar', 'Koloriang', 'Roing', 'Namsai', 'Longding', 'Taliha', 'Vijaynagar', 'Miao', 'Deomali', 'Jairampur', 'Margherita', 'Ledo', 'Digboi', 'Doom Dooma', 'Tinsukia', 'Duliajan'],
        'Sikkim': ['Gangtok', 'Namchi', 'Geyzing', 'Mangan', 'Jorethang', 'Singtam', 'Rangpo', 'Nayabazar', 'Ranipool', 'Tadong', 'Deorali', 'Rhenock', 'Pakyong', 'Soreng', 'Yuksom', 'Pelling', 'Ravangla', 'Legship', 'Dentam', 'Kalimpong', 'Lachung', 'Lachen', 'Chungthang', 'Phodong', 'Kabi', 'Singhik', 'Dikchu', 'Samdong', 'Martam', 'Rongli'],
        'Andaman and Nicobar Islands': ['Port Blair', 'Diglipur', 'Mayabunder', 'Rangat', 'Car Nicobar', 'Havelock', 'Neil Island', 'Long Island', 'Little Andaman', 'Baratang', 'Hutbay', 'Campbell Bay', 'Great Nicobar', 'Katchal', 'Nancowry', 'Teressa', 'Camorta', 'Trinket', 'Chowra', 'Tillangchong', 'Hut Bay', 'Ferrargunj', 'Bambooflat', 'Garacharma', 'Wandoor', 'Chiriyatapu', 'Collinpur', 'Manglutan', 'Prothrapur', 'Tushnabad'],
        'Dadra and Nagar Haveli and Daman and Diu': ['Daman', 'Diu', 'Silvassa', 'Naroli', 'Rakholi', 'Dudhani', 'Samarvarni', 'Vansda', 'Khanvel', 'Kelvani', 'Dahikhed', 'Karachgam', 'Khadoli', 'Zari', 'Galonda', 'Rudana', 'Amli', 'Velugam', 'Dapada', 'Khanpur', 'Sayli', 'Kherdi', 'Kilvani', 'Masat', 'Patlara', 'Bhilad', 'Vapi', 'Umergam', 'Dharampur', 'Kaprada'],
        'Lakshadweep': ['Kavaratti', 'Agatti', 'Minicoy', 'Amini', 'Andrott', 'Kalpeni', 'Kadmat', 'Kiltan', 'Chetlat', 'Bitra', 'Bangaram', 'Thinnakara', 'Parali I', 'Parali II', 'Suheli Par', 'Cheriyam', 'Valiyakara', 'Tilakkam', 'Pitti', 'Kalpitti'],
        'Puducherry': ['Puducherry', 'Karaikal', 'Mahe', 'Yanam', 'Villianur', 'Ariyankuppam', 'Bahour', 'Mannadipet', 'Nettapakkam', 'Ozhukarai', 'Kirumampakkam', 'Kalapet', 'Embalam', 'Thirubhuvanai', 'Poraiyar', 'Korkadu', 'Kottucherry', 'Thuthipet', 'Veerampattinam', 'Kalitheerthalkuppam']
    }
    
    all_stations = list(major_stations)
    station_codes_used = {code for _, code, _, _ in major_stations}
    
    # Generate additional stations from each state
    for state, cities in state_cities.items():
        for city in cities:
            if len(all_stations) >= 1500:
                break
                
            # Generate station code
            code_attempts = 0
            while code_attempts < 10:
                if len(city) >= 3:
                    code = city[:3].upper().replace(' ', '')
                    if len(code) < 3:
                        code += 'X' * (3 - len(code))
                else:
                    code = city.upper() + 'X' * (3 - len(city))
                
                # Add random suffix if code exists
                if code in station_codes_used:
                    code = code[:2] + random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                else:
                    break
                code_attempts += 1
            
            if code not in station_codes_used:
                station_name = f"{city} Junction"
                all_stations.append((station_name, code, city, state))
                station_codes_used.add(code)
    
    # Fill remaining slots with generated stations
    while len(all_stations) < 1500:
        city_prefixes = ['New', 'Old', 'East', 'West', 'North', 'South', 'Central']
        city_suffixes = ['Junction', 'Terminal', 'City', 'Cantt', 'Road']
        
        prefix = random.choice(city_prefixes)
        base_name = random.choice([city for cities in state_cities.values() for city in cities])
        suffix = random.choice(city_suffixes)
        station_name = f"{prefix} {base_name} {suffix}"
        
        # Generate unique code
        code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=3))
        while code in station_codes_used:
            code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=3))
        
        state = random.choice(list(state_cities.keys()))
        city = base_name
        
        all_stations.append((station_name, code, city, state))
        station_codes_used.add(code)
    
    return all_stations[:1500]

def get_comprehensive_trains_data():
    """Generate comprehensive trains data with 1000+ trains"""
    
    # Base train types and their characteristics
    train_types = {
        'Rajdhani': {'seats': (400, 500), 'fare': (0.75, 1.20), 'tatkal': (40, 60), 'tatkal_fare': (1.10, 1.50)},
        'Shatabdi': {'seats': (300, 400), 'fare': (0.85, 1.35), 'tatkal': (30, 50), 'tatkal_fare': (1.20, 1.60)},
        'Duronto': {'seats': (450, 550), 'fare': (0.70, 1.10), 'tatkal': (45, 65), 'tatkal_fare': (1.05, 1.45)},
        'Express': {'seats': (400, 600), 'fare': (0.40, 0.70), 'tatkal': (50, 80), 'tatkal_fare': (0.60, 1.00)},
        'Mail': {'seats': (350, 500), 'fare': (0.35, 0.65), 'tatkal': (40, 70), 'tatkal_fare': (0.55, 0.95)},
        'Passenger': {'seats': (200, 350), 'fare': (0.25, 0.45), 'tatkal': (20, 40), 'tatkal_fare': (0.40, 0.70)},
        'Superfast': {'seats': (400, 550), 'fare': (0.50, 0.80), 'tatkal': (45, 75), 'tatkal_fare': (0.70, 1.10)},
        'Intercity': {'seats': (250, 400), 'fare': (0.45, 0.75), 'tatkal': (25, 45), 'tatkal_fare': (0.65, 1.05)},
        'Jan Shatabdi': {'seats': (300, 450), 'fare': (0.60, 0.90), 'tatkal': (30, 50), 'tatkal_fare': (0.85, 1.25)},
        'Garib Rath': {'seats': (400, 500), 'fare': (0.40, 0.70), 'tatkal': (40, 60), 'tatkal_fare': (0.60, 1.00)},
        'Humsafar': {'seats': (350, 450), 'fare': (0.65, 0.95), 'tatkal': (35, 55), 'tatkal_fare': (0.90, 1.30)},
        'Tejas': {'seats': (300, 400), 'fare': (0.80, 1.20), 'tatkal': (30, 50), 'tatkal_fare': (1.15, 1.55)},
        'Vande Bharat': {'seats': (500, 600), 'fare': (1.00, 1.50), 'tatkal': (50, 70), 'tatkal_fare': (1.40, 1.90)},
        'Double Decker': {'seats': (600, 800), 'fare': (0.55, 0.85), 'tatkal': (60, 90), 'tatkal_fare': (0.80, 1.20)},
        'AC Express': {'seats': (350, 450), 'fare': (0.70, 1.00), 'tatkal': (35, 55), 'tatkal_fare': (1.00, 1.40)}
    }
    
    # Indian city names for train naming
    major_cities = [
        'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune', 'Ahmedabad',
        'Jaipur', 'Surat', 'Lucknow', 'Kanpur', 'Nagpur', 'Patna', 'Indore', 'Thane', 'Bhopal',
        'Visakhapatnam', 'Vadodara', 'Firozabad', 'Ludhiana', 'Rajkot', 'Agra', 'Siliguri',
        'Nashik', 'Faridabad', 'Patiala', 'Ghaziabad', 'Kalyan', 'Dombivli', 'Howrah', 'Ranchi',
        'Jabalpur', 'Gwalior', 'Coimbatore', 'Vijayawada', 'Jodhpur', 'Madurai', 'Raipur',
        'Kota', 'Guwahati', 'Chandigarh', 'Solapur', 'Hubli', 'Dharwad', 'Bareilly', 'Moradabad',
        'Mysore', 'Gurgaon', 'Aligarh', 'Jalandhar', 'Tiruchirappalli', 'Bhubaneswar', 'Salem',
        'Mira', 'Bhiwandi', 'Saharanpur', 'Gorakhpur', 'Bikaner', 'Amravati', 'Noida', 'Jamshedpur',
        'Bhilai', 'Cuttack', 'Kochi', 'Udaipur', 'Bhavnagar', 'Dehradun', 'Asansol', 'Nanded',
        'Kolhapur', 'Ajmer', 'Akola', 'Gulbarga', 'Jamnagar', 'Ujjain', 'Loni', 'Sikar',
        'Jhansi', 'Ulhasnagar', 'Nellore', 'Jammu', 'Sangli', 'Miraj', 'Belgaum', 'Mangalore',
        'Ambattur', 'Tirunelveli', 'Malegaon', 'Gaya', 'Jalgaon', 'Udaipur', 'Maheshtala',
        'Rajpur', 'Sonarpur', 'Kharagpur', 'Durgapur', 'Meerut', 'Dhanbad', 'Muzaffarpur',
        'Bhagalpur', 'Arrah', 'Purnia', 'Munger', 'Chhapra', 'Darbhanga', 'Begusarai', 'Katihar',
        'Saharsa', 'Hajipur', 'Sasaram', 'Dehri', 'Siwan', 'Motihari', 'Nawada', 'Bagaha'
    ]
    
    trains = []
    used_numbers = set()
    
    # Generate 1000+ trains
    for i in range(1000):
        # Generate unique train number
        while True:
            train_number = str(random.randint(10000, 99999))
            if train_number not in used_numbers:
                used_numbers.add(train_number)
                break
        
        # Choose train type
        train_type = random.choice(list(train_types.keys()))
        type_config = train_types[train_type]
        
        # Generate train name
        city1 = random.choice(major_cities)
        city2 = random.choice(major_cities)
        while city2 == city1:
            city2 = random.choice(major_cities)
        
        if random.choice([True, False]):
            train_name = f"{city1} {train_type}"
        else:
            train_name = f"{city1} {city2} {train_type}"
        
        # Generate characteristics
        total_seats = random.randint(*type_config['seats'])
        available_seats = total_seats  # Initially all available
        fare_per_km = round(random.uniform(*type_config['fare']), 2)
        tatkal_seats = random.randint(*type_config['tatkal'])
        tatkal_fare_per_km = round(random.uniform(*type_config['tatkal_fare']), 2)
        
        trains.append((
            train_number, train_name, total_seats, available_seats, 
            fare_per_km, tatkal_seats, tatkal_fare_per_km
        ))
    
    return trains

def get_existing_seats_for_train_date_class(cursor, train_id, journey_date, coach_class):
    """Get all existing seat numbers for a specific train/date/class combination"""
    cursor.execute("""
        SELECT DISTINCT p.seat_number 
        FROM passenger p 
        JOIN booking b ON p.booking_id = b.id 
        WHERE b.train_id = %s AND b.journey_date = %s AND b.coach_class = %s 
        AND p.seat_number IS NOT NULL AND b.status = 'confirmed'
    """, (train_id, journey_date, coach_class))
    
    return {row[0] for row in cursor.fetchall() if row[0]}

def generate_unique_seats_for_booking(cursor, train_id, journey_date, coach_class, count):
    """Generate globally unique seat numbers for a specific train/date/class"""
    coach_prefixes = {
        'SL': ['S', 'SL'], 'AC3': ['B', 'A'], 'AC2': ['A'], 
        'AC1': ['H'], '2S': ['D'], 'CC': ['C']
    }
    
    berth_types = {
        'SL': ['Lower', 'Middle', 'Upper', 'Side Lower', 'Side Upper'],
        'AC3': ['Lower', 'Middle', 'Upper', 'Side Lower', 'Side Upper'],
        'AC2': ['Lower', 'Upper', 'Side Lower', 'Side Upper'],
        'AC1': ['Lower', 'Upper'],
        '2S': ['Window', 'Aisle', 'Middle'],
        'CC': ['Window', 'Aisle', 'Middle']
    }
    
    # Get all existing seats for this train/date/class combination
    existing_seats = get_existing_seats_for_train_date_class(cursor, train_id, journey_date, coach_class)
    
    prefixes = coach_prefixes.get(coach_class, ['X'])
    available_berths = berth_types.get(coach_class, ['Lower'])
    
    seats = []
    attempts = 0
    max_attempts = 1000
    
    while len(seats) < count and attempts < max_attempts:
        coach_num = random.randint(1, 12)
        seat_num = random.randint(1, 80)
        prefix = random.choice(prefixes)
        seat_number = f"{prefix}{coach_num}-{seat_num}"
        berth_type = random.choice(available_berths)
        
        if seat_number not in existing_seats:
            seats.append((seat_number, berth_type))
            existing_seats.add(seat_number)
        
        attempts += 1
    
    return seats

def insert_comprehensive_data(conn):
    """Insert comprehensive test data with 1500 stations, 1000 trains, and extensive fake data"""
    logger.info("📊 Inserting comprehensive test data...")
    
    cursor = conn.cursor()
    
    # 1. Create users with different roles
    logger.info("👤 Creating users...")
    users_data = [
        ('admin', 'admin@railserve.com', generate_password_hash('admin123'), 'super_admin'),
        ('railway_admin', 'railway@railserve.com', generate_password_hash('railway123'), 'admin'),
        ('station_master', 'station@railserve.com', generate_password_hash('station123'), 'admin'),
        ('testuser', 'user@test.com', generate_password_hash('user123'), 'user'),
        ('john_doe', 'john@test.com', generate_password_hash('john123'), 'user'),
        ('jane_smith', 'jane@test.com', generate_password_hash('jane123'), 'user'),
        ('travel_agent', 'agent@railserve.com', generate_password_hash('agent123'), 'user'),
        ('frequent_traveler', 'frequent@railserve.com', generate_password_hash('frequent123'), 'user'),
        ('family_head', 'family@railserve.com', generate_password_hash('family123'), 'user'),
        ('corporate_user', 'corporate@railserve.com', generate_password_hash('corporate123'), 'user'),
    ]
    
    # Add 100 more random users for realistic data
    for i in range(10, 110):
        username = f"user{i}"
        email = f"user{i}@test.com"
        password = generate_password_hash(f"pass{i}")
        users_data.append((username, email, password, 'user'))
    
    user_ids = {}
    for username, email, password_hash, role in users_data:
        cursor.execute("""
            INSERT INTO "user" (username, email, password_hash, role) 
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (username, email, password_hash, role))
        user_id = cursor.fetchone()[0]
        user_ids[username] = user_id
    
    # 2. Create 1500 stations
    logger.info("🚉 Creating 1500 railway stations...")
    stations_data = get_comprehensive_stations_data()
    
    station_ids = {}
    for name, code, city, state in stations_data:
        cursor.execute("""
            INSERT INTO station (name, code, city, state) 
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (name, code, city, state))
        station_id = cursor.fetchone()[0]
        station_ids[code] = station_id
    
    # 3. Create 1000 trains
    logger.info("🚂 Creating 1000 trains...")
    trains_data = get_comprehensive_trains_data()
    
    train_ids = {}
    for number, name, total_seats, available_seats, fare_per_km, tatkal_seats, tatkal_fare_per_km in trains_data:
        cursor.execute("""
            INSERT INTO train (number, name, total_seats, available_seats, fare_per_km, tatkal_seats, tatkal_fare_per_km) 
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (number, name, total_seats, available_seats, fare_per_km, tatkal_seats, tatkal_fare_per_km))
        train_id = cursor.fetchone()[0]
        train_ids[number] = train_id
    
    # 4. Create comprehensive train routes
    logger.info("🛤️ Creating train routes...")
    station_codes = list(station_ids.keys())
    
    # Create routes for each train (connecting random stations)
    for train_number in list(train_ids.keys())[:200]:  # Create routes for first 200 trains
        train_id = train_ids[train_number]
        
        # Select 3-8 stations for this route
        route_length = random.randint(3, 8)
        route_stations = random.sample(station_codes, route_length)
        
        total_distance = 0
        for i, station_code in enumerate(route_stations):
            station_id = station_ids[station_code]
            sequence = i + 1
            
            # Generate realistic times
            if i == 0:  # Starting station
                departure_time = time(random.randint(0, 23), random.choice([0, 15, 30, 45]))
                arrival_time = None
            elif i == len(route_stations) - 1:  # Ending station
                arrival_time = time(random.randint(0, 23), random.choice([0, 15, 30, 45]))
                departure_time = None
            else:  # Intermediate station
                arrival_time = time(random.randint(0, 23), random.choice([0, 15, 30, 45]))
                departure_time = time(random.randint(0, 23), random.choice([0, 15, 30, 45]))
            
            # Calculate distance (incremental)
            if i > 0:
                total_distance += random.randint(50, 300)
            
            cursor.execute("""
                INSERT INTO train_route (train_id, station_id, sequence, arrival_time, departure_time, distance_from_start)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (train_id, station_id, sequence, arrival_time, departure_time, total_distance))
    
    # 5. Create Tatkal time slots
    logger.info("⏰ Creating Tatkal time slots...")
    tatkal_slots = [
        ('AC Classes Tatkal', 'AC1,AC2,AC3,CC', time(10, 0), time(11, 0), 1),
        ('Non-AC Classes Tatkal', 'SL,2S', time(11, 0), time(12, 0), 1),
        ('Premium Tatkal', 'AC1,AC2', time(10, 0), None, 1),
        ('General Tatkal', 'SL,2S,CC', time(11, 0), None, 1),
    ]
    
    for name, coach_classes, open_time, close_time, days_before in tatkal_slots:
        cursor.execute("""
            INSERT INTO tatkal_time_slot (name, coach_classes, open_time, close_time, days_before_journey, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, coach_classes, open_time, close_time, days_before, user_ids['admin']))
    
    # 6. Create Group Bookings
    logger.info("👥 Creating group bookings...")
    group_types = ['family', 'corporate', 'tour', 'religious']
    group_names = [
        'Sharma Family Trip', 'Tech Corp Outing', 'Golden Temple Yatra', 'College Reunion',
        'Wedding Party Travel', 'Business Conference', 'Pilgrimage Group', 'School Excursion',
        'Extended Family Vacation', 'Company Retreat', 'Religious Gathering', 'Cultural Tour'
    ]
    
    group_booking_ids = {}
    for i, group_name in enumerate(group_names):
        leader_username = random.choice(['family_head', 'corporate_user', 'travel_agent'])
        total_passengers = random.randint(5, 50)
        booking_type = random.choice(group_types)
        discount_rate = random.uniform(5.0, 15.0)  # 5-15% group discount
        
        cursor.execute("""
            INSERT INTO group_booking (group_name, group_leader_id, total_passengers, 
                                     contact_email, contact_phone, booking_type, 
                                     group_discount_rate, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (group_name, user_ids[leader_username], total_passengers,
              f"leader{i}@example.com", f"98765432{i:02d}", booking_type, discount_rate, 'confirmed'))
        
        group_booking_ids[group_name] = cursor.fetchone()[0]
    
    # 7. Create comprehensive bookings with different statuses
    logger.info("🎫 Creating comprehensive bookings...")
    
    # Get some train and station IDs for booking creation
    available_trains = list(train_ids.keys())[:50]  # Use first 50 trains
    available_stations = list(station_ids.keys())[:100]  # Use first 100 stations
    
    booking_statuses = ['confirmed', 'waitlisted', 'cancelled', 'rac']
    coach_classes = ['SL', 'AC3', 'AC2', 'AC1', '2S', 'CC']
    quotas = ['general', 'ladies', 'senior_citizen', 'tatkal', 'premium_tatkal']
    
    booking_ids = []
    
    # Create 500 diverse bookings
    for i in range(500):
        user_key = random.choice(list(user_ids.keys()))
        user_id = user_ids[user_key]
        train_number = random.choice(available_trains)
        train_id = train_ids[train_number]
        
        from_station_code = random.choice(available_stations)
        to_station_code = random.choice(available_stations)
        while to_station_code == from_station_code:
            to_station_code = random.choice(available_stations)
        
        from_station_id = station_ids[from_station_code]
        to_station_id = station_ids[to_station_code]
        
        # Journey date (mix of past, current, and future)
        base_date = datetime.now().date()
        journey_date = base_date + timedelta(days=random.randint(-30, 60))
        
        passengers = random.randint(1, 6)
        coach_class = random.choice(coach_classes)
        status = random.choice(booking_statuses)
        quota = random.choice(quotas)
        
        # Calculate amount based on distance and class
        distance = random.randint(100, 1500)
        base_fare = distance * random.uniform(0.5, 1.5)
        if coach_class in ['AC1', 'AC2']:
            base_fare *= random.uniform(2.0, 3.0)
        elif coach_class == 'AC3':
            base_fare *= random.uniform(1.5, 2.0)
        
        total_amount = base_fare * passengers
        
        # Group booking assignment (20% chance)
        group_booking_id = None
        if random.random() < 0.2:
            group_booking_id = random.choice(list(group_booking_ids.values()))
        
        pnr = generate_pnr()
        
        cursor.execute("""
            INSERT INTO booking (pnr, user_id, train_id, from_station_id, to_station_id,
                               journey_date, passengers, total_amount, coach_class, status,
                               quota, group_booking_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (pnr, user_id, train_id, from_station_id, to_station_id, journey_date,
              passengers, total_amount, coach_class, status, quota, group_booking_id))
        
        booking_id = cursor.fetchone()[0]
        booking_ids.append((booking_id, train_id, journey_date, coach_class, passengers, status))
    
    # 8. Create passengers with seat allocation
    logger.info("👤 Creating passengers with seat allocation...")
    
    passenger_names = [
        'Aarav Sharma', 'Vivaan Singh', 'Aditya Kumar', 'Vihaan Gupta', 'Arjun Verma',
        'Sai Patel', 'Reyansh Jain', 'Ayaan Khan', 'Krishna Yadav', 'Ishaan Agarwal',
        'Ananya Singh', 'Diya Sharma', 'Aadhya Gupta', 'Kavya Kumar', 'Pihu Verma',
        'Myra Patel', 'Aarna Jain', 'Kiara Khan', 'Ira Yadav', 'Riya Agarwal',
        'Rajesh Sharma', 'Suresh Kumar', 'Ramesh Gupta', 'Mahesh Verma', 'Dinesh Patel',
        'Priya Singh', 'Pooja Sharma', 'Sunita Gupta', 'Meera Kumar', 'Rekha Verma'
    ]
    
    id_proof_types = ['Aadhar', 'PAN Card', 'Passport', 'Driving License', 'Voter ID']
    genders = ['Male', 'Female', 'Other']
    
    for booking_id, train_id, journey_date, coach_class, passenger_count, status in booking_ids:
        # Generate unique seats for this booking if confirmed
        if status == 'confirmed':
            seats = generate_unique_seats_for_booking(cursor, train_id, journey_date, coach_class, passenger_count)
        else:
            seats = [(None, None)] * passenger_count
        
        for p in range(passenger_count):
            name = random.choice(passenger_names)
            age = random.randint(1, 80)
            gender = random.choice(genders)
            id_proof_type = random.choice(id_proof_types)
            id_proof_number = ''.join(random.choices(string.digits + string.ascii_uppercase, k=12))
            
            seat_number, berth_type = seats[p] if p < len(seats) else (None, None)
            
            cursor.execute("""
                INSERT INTO passenger (booking_id, name, age, gender, id_proof_type, id_proof_number,
                                     coach_class, seat_number, berth_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (booking_id, name, age, gender, id_proof_type, id_proof_number,
                  coach_class, seat_number, berth_type))
    
    # 9. Create payments
    logger.info("💳 Creating payment records...")
    
    # Get confirmed and some pending bookings for payments
    cursor.execute("SELECT id, total_amount, user_id FROM booking WHERE status IN ('confirmed', 'pending_payment') LIMIT 400")
    payment_bookings = cursor.fetchall()
    
    payment_methods = ['card', 'upi', 'netbanking', 'wallet']
    payment_statuses = ['success', 'failed', 'pending']
    
    for booking_id, amount, user_id in payment_bookings:
        method = random.choice(payment_methods)
        status = random.choice(payment_statuses)
        transaction_id = f"TXN{random.randint(100000000, 999999999)}"
        
        created_at = datetime.now() - timedelta(days=random.randint(0, 30))
        completed_at = created_at + timedelta(minutes=random.randint(1, 30)) if status == 'success' else None
        
        cursor.execute("""
            INSERT INTO payment (booking_id, user_id, amount, payment_method, transaction_id, 
                               status, created_at, completed_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (booking_id, user_id, amount, method, transaction_id, status, created_at, completed_at))
    
    # 10. Create waitlist entries
    logger.info("⏳ Creating waitlist entries...")
    
    # Get waitlisted bookings
    cursor.execute("SELECT id, train_id, journey_date FROM booking WHERE status = 'waitlisted'")
    waitlisted_bookings = cursor.fetchall()
    
    waitlist_types = ['GNWL', 'RAC', 'PQWL', 'RLWL', 'TQWL']
    
    for i, (booking_id, train_id, journey_date) in enumerate(waitlisted_bookings):
        position = i + 1  # Sequential positions
        waitlist_type = random.choice(waitlist_types)
        
        cursor.execute("""
            INSERT INTO waitlist (booking_id, train_id, journey_date, position, waitlist_type)
            VALUES (%s, %s, %s, %s, %s)
        """, (booking_id, train_id, journey_date, position, waitlist_type))
    
    # 11. Create restaurants and food service
    logger.info("🍽️ Creating restaurants and food service...")
    
    cuisine_types = ['North Indian', 'South Indian', 'Chinese', 'Continental', 'Fast Food', 'Beverages', 'Snacks']
    restaurant_names = [
        'Railway Canteen', 'Express Dhaba', 'Station Bites', 'Travel Treats', 'Quick Meals',
        'Hunger Express', 'Rail Kitchen', 'Journey Cafe', 'Platform Pantry', 'Track Treats',
        'Spice Route', 'Curry Express', 'Dosa Corner', 'Biryani House', 'Tandoor Express'
    ]
    
    restaurant_ids = {}
    # Create restaurants at major stations
    major_station_codes = list(station_ids.keys())[:50]
    
    for i, station_code in enumerate(major_station_codes):
        if i < len(restaurant_names):
            name = restaurant_names[i]
        else:
            name = f"Restaurant {i+1}"
        
        station_id = station_ids[station_code]
        cuisine = random.choice(cuisine_types)
        rating = round(random.uniform(3.5, 5.0), 1)
        delivery_time = random.randint(20, 45)
        
        cursor.execute("""
            INSERT INTO restaurant (name, station_id, cuisine_type, rating, delivery_time,
                                  contact_number, email, active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (name, station_id, cuisine, rating, delivery_time,
              f"9876543{i:03d}", f"restaurant{i}@rail.com", True))
        
        restaurant_ids[name] = cursor.fetchone()[0]
    
    # 12. Create menu items
    logger.info("🍛 Creating menu items...")
    
    menu_items = {
        'North Indian': [
            ('Dal Makhani', 'Rich and creamy lentil curry', 120, 'Vegetarian'),
            ('Butter Chicken', 'Tender chicken in tomato-based curry', 180, 'Non-Vegetarian'),
            ('Paneer Butter Masala', 'Cottage cheese in rich gravy', 150, 'Vegetarian'),
            ('Roti', 'Fresh wheat bread', 15, 'Vegetarian'),
            ('Jeera Rice', 'Cumin flavored basmati rice', 80, 'Vegetarian')
        ],
        'South Indian': [
            ('Masala Dosa', 'Crispy crepe with potato filling', 80, 'Vegetarian'),
            ('Idli Sambar', 'Steamed rice cakes with lentil curry', 60, 'Vegetarian'),
            ('Chicken Biryani', 'Aromatic rice with chicken', 200, 'Non-Vegetarian'),
            ('Filter Coffee', 'Traditional South Indian coffee', 25, 'Vegetarian'),
            ('Vada Sambar', 'Fried lentil donuts with curry', 70, 'Vegetarian')
        ],
        'Chinese': [
            ('Veg Fried Rice', 'Wok-tossed rice with vegetables', 100, 'Vegetarian'),
            ('Chicken Manchurian', 'Sweet and sour chicken balls', 160, 'Non-Vegetarian'),
            ('Veg Noodles', 'Stir-fried noodles with vegetables', 90, 'Vegetarian'),
            ('Hot and Sour Soup', 'Tangy soup with vegetables', 60, 'Vegetarian'),
            ('Spring Rolls', 'Crispy vegetable rolls', 80, 'Vegetarian')
        ],
        'Fast Food': [
            ('Burger', 'Grilled chicken burger with fries', 120, 'Non-Vegetarian'),
            ('Veg Sandwich', 'Multi-layered vegetable sandwich', 70, 'Vegetarian'),
            ('French Fries', 'Crispy golden potato fries', 50, 'Vegetarian'),
            ('Chicken Roll', 'Spiced chicken wrap', 100, 'Non-Vegetarian'),
            ('Cold Drink', 'Chilled soft drink', 30, 'Vegetarian')
        ],
        'Beverages': [
            ('Tea', 'Hot Indian chai', 15, 'Vegetarian'),
            ('Coffee', 'Fresh brewed coffee', 20, 'Vegetarian'),
            ('Lassi', 'Sweet yogurt drink', 40, 'Vegetarian'),
            ('Fresh Juice', 'Seasonal fruit juice', 50, 'Vegetarian'),
            ('Mineral Water', 'Packaged drinking water', 20, 'Vegetarian')
        ]
    }
    
    menu_item_ids = {}
    for restaurant_name, restaurant_id in restaurant_ids.items():
        # Get cuisine type for this restaurant
        cursor.execute("SELECT cuisine_type FROM restaurant WHERE id = %s", (restaurant_id,))
        cuisine_type = cursor.fetchone()[0]
        
        # Add items for this cuisine type
        if cuisine_type in menu_items:
            for item_name, description, price, food_type in menu_items[cuisine_type]:
                cursor.execute("""
                    INSERT INTO menu_item (restaurant_id, name, description, price, 
                                         category, food_type, available, is_popular)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                """, (restaurant_id, item_name, description, price, cuisine_type,
                      food_type, True, random.choice([True, False])))
                
                menu_item_ids[f"{restaurant_name}_{item_name}"] = cursor.fetchone()[0]
    
    # 13. Create food orders
    logger.info("🍕 Creating food orders...")
    
    # Get some confirmed bookings for food orders
    cursor.execute("""
        SELECT b.id, b.user_id, tr.station_id 
        FROM booking b 
        JOIN train_route tr ON b.train_id = tr.train_id 
        WHERE b.status = 'confirmed' 
        AND tr.sequence > 1 
        LIMIT 100
    """)
    food_booking_data = cursor.fetchall()
    
    order_statuses = ['pending', 'confirmed', 'preparing', 'dispatched', 'delivered']
    
    for booking_id, user_id, delivery_station_id in food_booking_data:
        # Find restaurant at this station
        cursor.execute("SELECT id FROM restaurant WHERE station_id = %s LIMIT 1", (delivery_station_id,))
        restaurant_result = cursor.fetchone()
        
        if restaurant_result:
            restaurant_id = restaurant_result[0]
            order_number = generate_order_number()
            total_amount = random.uniform(100, 500)
            status = random.choice(order_statuses)
            
            cursor.execute("""
                INSERT INTO food_order (booking_id, user_id, restaurant_id, delivery_station_id,
                                      order_number, total_amount, status, contact_number,
                                      special_instructions)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, (booking_id, user_id, restaurant_id, delivery_station_id, order_number,
                  total_amount, status, f"98765{random.randint(10000, 99999)}",
                  random.choice(['Extra spicy', 'Less oil', 'No onions', 'Pack separately', ''])))
            
            food_order_id = cursor.fetchone()[0]
            
            # Add food order items
            cursor.execute("SELECT id, price FROM menu_item WHERE restaurant_id = %s LIMIT 3", (restaurant_id,))
            available_items = cursor.fetchall()
            
            for item_id, unit_price in available_items:
                quantity = random.randint(1, 3)
                total_price = unit_price * quantity
                
                cursor.execute("""
                    INSERT INTO food_order_item (food_order_id, menu_item_id, quantity, unit_price, total_price)
                    VALUES (%s, %s, %s, %s, %s)
                """, (food_order_id, item_id, quantity, unit_price, total_price))
    
    # 14. Create loyalty programs
    logger.info("🏆 Creating loyalty programs...")
    
    # Create loyalty programs for frequent users
    frequent_users = list(user_ids.keys())[10:60]  # 50 users with loyalty programs
    
    tiers = ['Silver', 'Gold', 'Platinum', 'Diamond']
    
    for username in frequent_users:
        user_id = user_ids[username]
        membership_number = generate_membership_number()
        tier = random.choice(tiers)
        points_earned = random.randint(500, 5000)
        points_redeemed = random.randint(0, points_earned // 2)
        total_journeys = random.randint(5, 50)
        total_spent = random.uniform(10000, 100000)
        
        cursor.execute("""
            INSERT INTO loyalty_program (user_id, membership_number, tier, points_earned, 
                                       points_redeemed, total_journeys, total_spent)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, membership_number, tier, points_earned, points_redeemed,
              total_journeys, total_spent))
    
    # 15. Create train status updates
    logger.info("🚉 Creating train status updates...")
    
    train_statuses = ['On Time', 'Delayed', 'Cancelled', 'Diverted', 'Rescheduled']
    
    # Create status updates for trains over the next few days
    for train_number in list(train_ids.keys())[:100]:
        train_id = train_ids[train_number]
        
        for day_offset in range(0, 7):  # Next 7 days
            journey_date = datetime.now().date() + timedelta(days=day_offset)
            status = random.choice(train_statuses)
            delay_minutes = random.randint(0, 300) if status == 'Delayed' else 0
            
            # Get a random station from this train's route
            cursor.execute("""
                SELECT station_id FROM train_route WHERE train_id = %s 
                ORDER BY sequence LIMIT 1 OFFSET %s
            """, (train_id, random.randint(0, 2)))
            
            station_result = cursor.fetchone()
            current_station_id = station_result[0] if station_result else None
            
            cursor.execute("""
                INSERT INTO train_status (train_id, current_station_id, status, delay_minutes, journey_date)
                VALUES (%s, %s, %s, %s, %s)
            """, (train_id, current_station_id, status, delay_minutes, journey_date))
    
    # 16. Create refund requests
    logger.info("💰 Creating refund requests...")
    
    # Get some cancelled bookings for refund requests
    cursor.execute("SELECT id, user_id, total_amount FROM booking WHERE status = 'cancelled' LIMIT 50")
    cancelled_bookings = cursor.fetchall()
    
    refund_reasons = [
        'Train Cancelled', 'Medical Emergency', 'Change of Plans', 'Train Delay', 
        'AC Failure', 'Family Emergency', 'Work Commitment', 'Weather Conditions'
    ]
    
    for booking_id, user_id, amount_paid in cancelled_bookings:
        reason = random.choice(refund_reasons)
        cancellation_charges = amount_paid * random.uniform(0.05, 0.20)  # 5-20% charges
        refund_amount = amount_paid - cancellation_charges
        tdr_number = generate_tdr_number()
        status = random.choice(['pending', 'approved', 'rejected', 'completed'])
        
        cursor.execute("""
            INSERT INTO refund_request (booking_id, user_id, reason, amount_paid, 
                                      refund_amount, cancellation_charges, tdr_number, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (booking_id, user_id, reason, amount_paid, refund_amount, 
              cancellation_charges, tdr_number, status))
    
    # 17. Create notification preferences for all users
    logger.info("🔔 Creating notification preferences...")
    
    for username, user_id in user_ids.items():
        cursor.execute("""
            INSERT INTO notification_preferences (user_id, email_notifications, sms_notifications,
                                                push_notifications, booking_confirmations, 
                                                journey_reminders, train_delay_alerts, 
                                                food_order_updates, promotional_offers)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, True, True, random.choice([True, False]), True, True, 
              True, random.choice([True, False]), random.choice([True, False])))
    
    conn.commit()
    cursor.close()
    logger.info("✅ Comprehensive test data inserted successfully")

def main():
    """Main function to set up the complete database"""
    logger.info("🚀 Starting RailServe Comprehensive Database Setup...")
    
    # Create database if needed
    if not create_database_if_needed():
        return False
    
    # Get connection
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        # Create all tables
        create_tables(conn)
        
        # Insert comprehensive test data
        insert_comprehensive_data(conn)
        
        # Verify data
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM station")
        station_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM train")
        train_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM booking")
        booking_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM passenger")
        passenger_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM waitlist")
        waitlist_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        logger.info("✅ Database setup completed successfully!")
        logger.info(f"📊 Final Statistics:")
        logger.info(f"   🚉 Stations: {station_count}")
        logger.info(f"   🚂 Trains: {train_count}")
        logger.info(f"   🎫 Bookings: {booking_count}")
        logger.info(f"   👤 Passengers: {passenger_count}")
        logger.info(f"   ⏳ Waitlist Entries: {waitlist_count}")
        
        logger.info("\n🔑 Login Credentials:")
        logger.info("   Admin: admin / admin123")
        logger.info("   Railway Admin: railway_admin / railway123")
        logger.info("   Test User: testuser / user123")
        logger.info("\n🌐 Features Available:")
        logger.info("   ✓ Complete booking system with seat allocation")
        logger.info("   ✓ Waitlist management with positions")
        logger.info("   ✓ Food ordering system")
        logger.info("   ✓ Group bookings")
        logger.info("   ✓ Tatkal booking system")
        logger.info("   ✓ Loyalty programs")
        logger.info("   ✓ Train status tracking")
        logger.info("   ✓ Refund management")
        logger.info("   ✓ Comprehensive admin dashboard")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        conn.rollback()
        conn.close()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)