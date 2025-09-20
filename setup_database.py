#!/usr/bin/env python3
"""
RailServe Comprehensive Database Setup Script
=============================================

This script creates a complete RailServe railway reservation system database
with extensive test data including 1500 stations, 1000 trains, and comprehensive
fake data for testing all features.

Usage:
    export DATABASE_URL="postgresql://user:password@localhost:5432/railserve"
    python setup_database.py

Features Created:
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

Test Data Includes:
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
from typing import List, Dict, Any, Optional, Tuple
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    logger.error("❌ DATABASE_URL environment variable is required")
    sys.exit(1)

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    from werkzeug.security import generate_password_hash
    print("✅ All dependencies available")
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Install with: pip install psycopg2-binary werkzeug")
    sys.exit(1)

def create_database_if_needed() -> bool:
    """Check database connection (database should already exist)"""
    try:
        logger.info("Checking database connection...")
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
        logger.info("✅ Database connection successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
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
        DROP TABLE IF EXISTS route CASCADE;
        DROP TABLE IF EXISTS train_coach CASCADE;
        DROP TABLE IF EXISTS train_schedule CASCADE;
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
            phone VARCHAR(15),
            date_of_birth DATE,
            gender VARCHAR(10),
            address TEXT,
            city VARCHAR(50),
            state VARCHAR(50),
            pincode VARCHAR(10),
            id_proof_type VARCHAR(20),
            id_proof_number VARCHAR(50),
            emergency_contact VARCHAR(15),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Railway stations - comprehensive coverage
        CREATE TABLE station (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            code VARCHAR(10) NOT NULL UNIQUE,
            city VARCHAR(50) NOT NULL,
            state VARCHAR(50) NOT NULL,
            zone VARCHAR(20),
            division VARCHAR(50),
            latitude DECIMAL(10, 8),
            longitude DECIMAL(11, 8),
            elevation INTEGER DEFAULT 0,
            platforms INTEGER DEFAULT 1,
            electric_traction BOOLEAN DEFAULT FALSE,
            facilities TEXT,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Routes table for train route management
        CREATE TABLE route (
            id SERIAL PRIMARY KEY,
            route_name VARCHAR(100) NOT NULL,
            route_code VARCHAR(20) UNIQUE,
            total_distance DECIMAL(8,2) DEFAULT 0,
            estimated_duration INTERVAL,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Trains with comprehensive features
        CREATE TABLE train (
            id SERIAL PRIMARY KEY,
            number VARCHAR(10) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            train_type VARCHAR(30) DEFAULT 'Express',
            total_seats INTEGER NOT NULL,
            available_seats INTEGER NOT NULL,
            fare_per_km DECIMAL(8,2) NOT NULL,
            tatkal_seats INTEGER DEFAULT 0,
            tatkal_fare_per_km DECIMAL(8,2),
            speed_kmph INTEGER DEFAULT 80,
            pantry_car BOOLEAN DEFAULT FALSE,
            wifi_available BOOLEAN DEFAULT FALSE,
            charging_points BOOLEAN DEFAULT FALSE,
            route_id INTEGER REFERENCES route(id),
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Train schedule table for departure/arrival times
        CREATE TABLE train_schedule (
            id SERIAL PRIMARY KEY,
            train_id INTEGER REFERENCES train(id) NOT NULL,
            departure_station_id INTEGER REFERENCES station(id) NOT NULL,
            arrival_station_id INTEGER REFERENCES station(id) NOT NULL,
            departure_time TIME NOT NULL,
            arrival_time TIME NOT NULL,
            journey_days VARCHAR(20) DEFAULT 'Daily',
            effective_from DATE NOT NULL,
            effective_until DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Train coaches for different classes
        CREATE TABLE train_coach (
            id SERIAL PRIMARY KEY,
            train_id INTEGER REFERENCES train(id) NOT NULL,
            coach_type VARCHAR(20) NOT NULL, -- AC1, AC2, AC3, SL, 2S, CC
            coach_count INTEGER DEFAULT 1,
            seats_per_coach INTEGER NOT NULL,
            base_fare_multiplier DECIMAL(4,2) DEFAULT 1.0,
            amenities TEXT,
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
            distance_from_start DECIMAL(8,2) NOT NULL DEFAULT 0,
            halt_duration INTEGER DEFAULT 2, -- minutes
            platform_number VARCHAR(5),
            commercial_stop BOOLEAN DEFAULT TRUE,
            meal_stop BOOLEAN DEFAULT FALSE,
            UNIQUE(train_id, sequence)
        );
        
        -- Group bookings for families/corporate
        CREATE TABLE group_booking (
            id SERIAL PRIMARY KEY,
            group_name VARCHAR(100) NOT NULL,
            group_leader_id INTEGER REFERENCES "user"(id),
            group_type VARCHAR(20) DEFAULT 'family', -- family, corporate, tour
            total_passengers INTEGER DEFAULT 0,
            contact_email VARCHAR(120),
            contact_phone VARCHAR(15),
            booking_type VARCHAR(20) DEFAULT 'general',
            special_requirements TEXT,
            discount_applied DECIMAL(8,2) DEFAULT 0.0,
            group_discount_rate DECIMAL(5,2) DEFAULT 0.0,
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
            total_amount DECIMAL(10,2) NOT NULL,
            booking_type VARCHAR(10) DEFAULT 'general', -- general, tatkal, premium
            quota VARCHAR(20) DEFAULT 'general', -- general, tatkal, ladies, handicapped, senior_citizen, etc.
            coach_class VARCHAR(10) DEFAULT 'SL', -- AC1, AC2, AC3, SL, 2S, CC
            status VARCHAR(20) DEFAULT 'pending_payment',
            waitlist_type VARCHAR(10) DEFAULT 'GNWL', -- GNWL, PQWL, RLWL, etc.
            chart_prepared BOOLEAN DEFAULT FALSE,
            berth_preference VARCHAR(20) DEFAULT 'No Preference',
            current_reservation BOOLEAN DEFAULT FALSE,
            mobile_number VARCHAR(15),
            email_address VARCHAR(120),
            boarding_station_id INTEGER REFERENCES station(id),
            destination_station_id INTEGER REFERENCES station(id),
            distance_km DECIMAL(8,2) DEFAULT 0,
            booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cancellation_charges DECIMAL(8,2) DEFAULT 0.0,
            group_booking_id INTEGER REFERENCES group_booking(id),
            loyalty_discount DECIMAL(8,2) DEFAULT 0.0,
            senior_citizen_discount DECIMAL(8,2) DEFAULT 0.0
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
            coach_number VARCHAR(10),
            berth_type VARCHAR(20), -- Lower, Middle, Upper, Side Lower, Side Upper
            meal_preference VARCHAR(20) DEFAULT 'Vegetarian',
            special_needs TEXT,
            contact_number VARCHAR(15)
        );
        
        -- Payments with comprehensive tracking
        CREATE TABLE payment (
            id SERIAL PRIMARY KEY,
            booking_id INTEGER REFERENCES booking(id) NOT NULL,
            user_id INTEGER REFERENCES "user"(id) NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            payment_method VARCHAR(20) NOT NULL, -- card, netbanking, upi, wallet
            transaction_id VARCHAR(50),
            gateway_transaction_id VARCHAR(100),
            gateway_response TEXT,
            status VARCHAR(20) DEFAULT 'pending', -- pending, success, failed, refunded
            failure_reason TEXT,
            refund_amount DECIMAL(10,2) DEFAULT 0,
            refund_transaction_id VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            refunded_at TIMESTAMP
        );
        
        -- Waitlist management with comprehensive tracking
        CREATE TABLE waitlist (
            id SERIAL PRIMARY KEY,
            booking_id INTEGER REFERENCES booking(id) NOT NULL,
            train_id INTEGER REFERENCES train(id) NOT NULL,
            journey_date DATE NOT NULL,
            coach_class VARCHAR(10) NOT NULL,
            position INTEGER NOT NULL,
            waitlist_type VARCHAR(10) DEFAULT 'GNWL', -- GNWL, PQWL, RLWL, TQWL
            initial_position INTEGER,
            confirmed_at TIMESTAMP,
            cancelled_at TIMESTAMP,
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
            max_bookings_per_user INTEGER DEFAULT 6,
            advance_reservation_period INTEGER DEFAULT 120, -- days
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER REFERENCES "user"(id)
        );
        
        -- Refund requests and TDR management
        CREATE TABLE refund_request (
            id SERIAL PRIMARY KEY,
            booking_id INTEGER REFERENCES booking(id) NOT NULL,
            user_id INTEGER REFERENCES "user"(id) NOT NULL,
            refund_type VARCHAR(20) NOT NULL, -- TDR, cancellation, no_show
            reason VARCHAR(100) NOT NULL,
            description TEXT,
            amount_paid DECIMAL(10,2) NOT NULL,
            refund_amount DECIMAL(10,2) NOT NULL,
            cancellation_charges DECIMAL(10,2) DEFAULT 0.0,
            processing_fee DECIMAL(8,2) DEFAULT 0.0,
            tdr_number VARCHAR(20) UNIQUE NOT NULL,
            supporting_documents TEXT, -- JSON array of document URLs
            status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected, processed
            admin_comments TEXT,
            processed_by INTEGER REFERENCES "user"(id),
            filed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP,
            refund_processed_at TIMESTAMP
        );
        
        -- Train status tracking for real-time updates
        CREATE TABLE train_status (
            id SERIAL PRIMARY KEY,
            train_id INTEGER REFERENCES train(id) NOT NULL,
            current_station_id INTEGER REFERENCES station(id),
            next_station_id INTEGER REFERENCES station(id),
            status VARCHAR(50) DEFAULT 'On Time', -- On Time, Delayed, Cancelled, Diverted
            delay_minutes INTEGER DEFAULT 0,
            platform_number VARCHAR(5),
            expected_arrival TIME,
            expected_departure TIME,
            actual_arrival TIME,
            actual_departure TIME,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            journey_date DATE NOT NULL,
            route_status VARCHAR(20) DEFAULT 'normal', -- normal, diverted, short_terminated
            updated_by INTEGER REFERENCES "user"(id)
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
            total_seats INTEGER NOT NULL,
            available_seats INTEGER DEFAULT 0,
            waiting_list INTEGER DEFAULT 0,
            rac_seats INTEGER DEFAULT 0,
            confirmed_seats INTEGER DEFAULT 0,
            current_status VARCHAR(20) DEFAULT 'AVAILABLE', -- AVAILABLE, RAC, WAITING
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(train_id, from_station_id, to_station_id, journey_date, coach_class, quota)
        );
        
        -- Chart preparation tracking
        CREATE TABLE chart_preparation (
            id SERIAL PRIMARY KEY,
            train_id INTEGER REFERENCES train(id) NOT NULL,
            journey_date DATE NOT NULL,
            coach_class VARCHAR(10) NOT NULL,
            chart_prepared_at TIMESTAMP,
            final_chart_at TIMESTAMP,
            status VARCHAR(20) DEFAULT 'pending', -- pending, prepared, finalized
            confirmed_from_waitlist INTEGER DEFAULT 0,
            cancelled_waitlist INTEGER DEFAULT 0,
            rac_confirmed INTEGER DEFAULT 0,
            total_passengers INTEGER DEFAULT 0,
            prepared_by INTEGER REFERENCES "user"(id),
            UNIQUE(train_id, journey_date, coach_class)
        );
        
        -- Food service restaurants
        CREATE TABLE restaurant (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            station_id INTEGER REFERENCES station(id),
            license_number VARCHAR(50),
            contact_number VARCHAR(15),
            email VARCHAR(120),
            address TEXT,
            cuisine_type VARCHAR(50),
            food_safety_rating VARCHAR(10),
            rating DECIMAL(3,1) DEFAULT 4.0,
            total_reviews INTEGER DEFAULT 0,
            delivery_time INTEGER DEFAULT 30, -- minutes
            minimum_order DECIMAL(8,2) DEFAULT 0.0,
            delivery_charge DECIMAL(8,2) DEFAULT 0.0,
            packaging_charge DECIMAL(8,2) DEFAULT 0.0,
            operating_hours VARCHAR(50) DEFAULT '24x7',
            days_closed VARCHAR(50),
            active BOOLEAN DEFAULT TRUE,
            verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Food menu items
        CREATE TABLE menu_item (
            id SERIAL PRIMARY KEY,
            restaurant_id INTEGER REFERENCES restaurant(id) NOT NULL,
            name VARCHAR(100) NOT NULL,
            description VARCHAR(500),
            price DECIMAL(8,2) NOT NULL,
            discounted_price DECIMAL(8,2),
            category VARCHAR(50), -- Breakfast, Lunch, Dinner, Snacks, Beverages
            food_type VARCHAR(20) DEFAULT 'Vegetarian', -- Vegetarian, Non-Vegetarian, Vegan
            spice_level VARCHAR(20) DEFAULT 'Medium', -- Mild, Medium, Spicy, Extra Spicy
            image_url VARCHAR(200),
            preparation_time INTEGER DEFAULT 15,
            available BOOLEAN DEFAULT TRUE,
            is_popular BOOLEAN DEFAULT FALSE,
            is_recommended BOOLEAN DEFAULT FALSE,
            ingredients TEXT,
            allergen_info TEXT,
            nutrition_info TEXT, -- JSON string
            calories INTEGER,
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
            total_amount DECIMAL(10,2) NOT NULL,
            item_total DECIMAL(10,2) NOT NULL,
            delivery_charge DECIMAL(8,2) DEFAULT 0.0,
            packaging_charge DECIMAL(8,2) DEFAULT 0.0,
            tax_amount DECIMAL(8,2) DEFAULT 0.0,
            discount_amount DECIMAL(8,2) DEFAULT 0.0,
            final_amount DECIMAL(10,2) NOT NULL,
            status VARCHAR(20) DEFAULT 'pending', -- pending, confirmed, preparing, ready, delivered, cancelled
            special_instructions TEXT,
            delivery_time TIMESTAMP,
            estimated_delivery TIME,
            actual_delivery_time TIMESTAMP,
            contact_number VARCHAR(15) NOT NULL,
            alternate_contact VARCHAR(15),
            coach_number VARCHAR(10),
            seat_number VARCHAR(10),
            payment_method VARCHAR(20),
            payment_status VARCHAR(20) DEFAULT 'pending',
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            review TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Food order items
        CREATE TABLE food_order_item (
            id SERIAL PRIMARY KEY,
            food_order_id INTEGER REFERENCES food_order(id) NOT NULL,
            menu_item_id INTEGER REFERENCES menu_item(id) NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            unit_price DECIMAL(8,2) NOT NULL,
            total_price DECIMAL(10,2) NOT NULL,
            special_request VARCHAR(200),
            customizations TEXT -- JSON string for any customizations
        );
        
        -- Loyalty program for frequent travelers
        CREATE TABLE loyalty_program (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES "user"(id) NOT NULL UNIQUE,
            membership_number VARCHAR(20) UNIQUE NOT NULL,
            tier VARCHAR(20) DEFAULT 'Silver', -- Silver, Gold, Platinum, Diamond
            points_earned INTEGER DEFAULT 0,
            points_redeemed INTEGER DEFAULT 0,
            points_balance INTEGER DEFAULT 0,
            lifetime_points INTEGER DEFAULT 0,
            total_journeys INTEGER DEFAULT 0,
            total_distance DECIMAL(10,2) DEFAULT 0.0,
            total_spent DECIMAL(12,2) DEFAULT 0.0,
            tier_valid_until DATE,
            next_tier VARCHAR(20),
            points_to_next_tier INTEGER DEFAULT 0,
            benefits_active BOOLEAN DEFAULT TRUE,
            tier_benefits TEXT, -- JSON string of benefits
            referral_code VARCHAR(20) UNIQUE,
            referrals_count INTEGER DEFAULT 0,
            joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tier_upgrade_date TIMESTAMP
        );
        
        -- User notification preferences
        CREATE TABLE notification_preferences (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES "user"(id) NOT NULL UNIQUE,
            email_notifications BOOLEAN DEFAULT TRUE,
            sms_notifications BOOLEAN DEFAULT TRUE,
            push_notifications BOOLEAN DEFAULT TRUE,
            whatsapp_notifications BOOLEAN DEFAULT FALSE,
            booking_confirmations BOOLEAN DEFAULT TRUE,
            journey_reminders BOOLEAN DEFAULT TRUE,
            train_delay_alerts BOOLEAN DEFAULT TRUE,
            pnr_status_updates BOOLEAN DEFAULT TRUE,
            food_order_updates BOOLEAN DEFAULT TRUE,
            payment_confirmations BOOLEAN DEFAULT TRUE,
            refund_updates BOOLEAN DEFAULT TRUE,
            promotional_offers BOOLEAN DEFAULT FALSE,
            loyalty_updates BOOLEAN DEFAULT TRUE,
            security_alerts BOOLEAN DEFAULT TRUE,
            newsletter BOOLEAN DEFAULT FALSE
        );
        
        -- Tatkal override for emergency bookings
        CREATE TABLE tatkal_override (
            id SERIAL PRIMARY KEY,
            train_id INTEGER REFERENCES train(id) NOT NULL,
            journey_date DATE NOT NULL,
            override_reason VARCHAR(200) NOT NULL,
            additional_quota INTEGER DEFAULT 0,
            coach_classes VARCHAR(100), -- comma separated list
            special_fare_multiplier DECIMAL(4,2) DEFAULT 1.0,
            max_bookings_per_user INTEGER DEFAULT 6,
            priority_level INTEGER DEFAULT 1, -- 1=highest, 5=lowest
            created_by INTEGER REFERENCES "user"(id),
            approved_by INTEGER REFERENCES "user"(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at TIMESTAMP,
            expires_at TIMESTAMP,
            active BOOLEAN DEFAULT TRUE
        );
    """)
    
    # Create indexes for better performance
    cursor.execute("""
        -- Create essential indexes
        CREATE INDEX idx_booking_user_id ON booking(user_id);
        CREATE INDEX idx_booking_train_id ON booking(train_id);
        CREATE INDEX idx_booking_journey_date ON booking(journey_date);
        CREATE INDEX idx_booking_pnr ON booking(pnr);
        CREATE INDEX idx_booking_status ON booking(status);
        
        CREATE INDEX idx_passenger_booking_id ON passenger(booking_id);
        
        CREATE INDEX idx_train_route_train_id ON train_route(train_id);
        CREATE INDEX idx_train_route_sequence ON train_route(train_id, sequence);
        
        CREATE INDEX idx_waitlist_booking_id ON waitlist(booking_id);
        CREATE INDEX idx_waitlist_position ON waitlist(train_id, journey_date, position);
        
        CREATE INDEX idx_payment_booking_id ON payment(booking_id);
        CREATE INDEX idx_payment_status ON payment(status);
        
        CREATE INDEX idx_food_order_booking_id ON food_order(booking_id);
        CREATE INDEX idx_food_order_status ON food_order(status);
        
        CREATE INDEX idx_train_status_journey_date ON train_status(train_id, journey_date);
        CREATE INDEX idx_seat_availability_search ON seat_availability(train_id, journey_date, coach_class);
        
        CREATE INDEX idx_station_code ON station(code);
        CREATE INDEX idx_station_city ON station(city);
        CREATE INDEX idx_train_number ON train(number);
        
        CREATE INDEX idx_loyalty_user_id ON loyalty_program(user_id);
        CREATE INDEX idx_loyalty_membership_number ON loyalty_program(membership_number);
    """)
    
    conn.commit()
    cursor.close()
    logger.info("✅ Database tables created")

def generate_pnr() -> str:
    """Generate a unique 10-digit PNR"""
    return ''.join(random.choices(string.digits, k=10))

def generate_tdr_number() -> str:
    """Generate a unique TDR number"""
    return f"TDR{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"

def generate_order_number() -> str:
    """Generate a unique food order number"""
    return f"FD{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"

def generate_membership_number() -> str:
    """Generate a unique loyalty membership number"""
    return f"RL{datetime.now().strftime('%Y')}{random.randint(100000, 999999)}"

def get_comprehensive_stations_data() -> List[Tuple[str, str, str, str, str, str]]:
    """Generate comprehensive stations data for all major Indian railway stations"""
    
    # Major stations across all Indian states with zones and divisions
    major_stations = [
        # Delhi - Northern Railway
        ('New Delhi Railway Station', 'NDLS', 'Delhi', 'Delhi', 'NR', 'Delhi'),
        ('Old Delhi Junction', 'DLI', 'Delhi', 'Delhi', 'NR', 'Delhi'),
        ('Nizamuddin Railway Station', 'NZM', 'Delhi', 'Delhi', 'NR', 'Delhi'),
        ('Anand Vihar Terminal', 'ANVT', 'Delhi', 'Delhi', 'NR', 'Delhi'),
        ('Delhi Sarai Rohilla', 'DEE', 'Delhi', 'Delhi', 'NR', 'Delhi'),
        ('Delhi Cantt', 'DEC', 'Delhi', 'Delhi', 'NR', 'Delhi'),
        
        # Mumbai - Western & Central Railway
        ('Mumbai Central', 'MMCT', 'Mumbai', 'Maharashtra', 'WR', 'Mumbai'),
        ('Chhatrapati Shivaji Maharaj Terminus', 'CSMT', 'Mumbai', 'Maharashtra', 'CR', 'Mumbai'),
        ('Lokmanya Tilak Terminus', 'LTT', 'Mumbai', 'Maharashtra', 'CR', 'Mumbai'),
        ('Mumbai Bandra Terminus', 'BDTS', 'Mumbai', 'Maharashtra', 'WR', 'Mumbai'),
        ('Dadar Central', 'DR', 'Mumbai', 'Maharashtra', 'CR', 'Mumbai'),
        ('Kurla Junction', 'KYN', 'Mumbai', 'Maharashtra', 'CR', 'Mumbai'),
        
        # Chennai - Southern Railway
        ('Chennai Central', 'MAS', 'Chennai', 'Tamil Nadu', 'SR', 'Chennai'),
        ('Chennai Egmore', 'MS', 'Chennai', 'Tamil Nadu', 'SR', 'Chennai'),
        ('Chennai Beach', 'MSB', 'Chennai', 'Tamil Nadu', 'SR', 'Chennai'),
        
        # Kolkata - Eastern Railway
        ('Kolkata Howrah', 'HWH', 'Kolkata', 'West Bengal', 'ER', 'Howrah'),
        ('Sealdah', 'SDAH', 'Kolkata', 'West Bengal', 'ER', 'Sealdah'),
        ('Kolkata Station', 'KOAA', 'Kolkata', 'West Bengal', 'ER', 'Kolkata'),
        
        # Bangalore - South Western Railway
        ('Bangalore City Junction', 'SBC', 'Bangalore', 'Karnataka', 'SWR', 'Bangalore'),
        ('Bangalore Cantonment', 'BNC', 'Bangalore', 'Karnataka', 'SWR', 'Bangalore'),
        ('Yeshwantpur Junction', 'YPR', 'Bangalore', 'Karnataka', 'SWR', 'Bangalore'),
        
        # Hyderabad - South Central Railway
        ('Hyderabad Deccan', 'HYB', 'Hyderabad', 'Telangana', 'SCR', 'Hyderabad'),
        ('Secunderabad Junction', 'SC', 'Secunderabad', 'Telangana', 'SCR', 'Secunderabad'),
        ('Kacheguda', 'KCG', 'Hyderabad', 'Telangana', 'SCR', 'Hyderabad'),
        
        # Other major cities
        ('Pune Junction', 'PUNE', 'Pune', 'Maharashtra', 'CR', 'Pune'),
        ('Ahmedabad Junction', 'ADI', 'Ahmedabad', 'Gujarat', 'WR', 'Ahmedabad'),
        ('Jaipur Junction', 'JP', 'Jaipur', 'Rajasthan', 'NWR', 'Jaipur'),
        ('Lucknow Junction', 'LJN', 'Lucknow', 'Uttar Pradesh', 'NER', 'Lucknow'),
        ('Kanpur Central', 'CNB', 'Kanpur', 'Uttar Pradesh', 'NCR', 'Kanpur'),
        ('Agra Cantt', 'AGC', 'Agra', 'Uttar Pradesh', 'NCR', 'Agra'),
        ('Varanasi Junction', 'BSB', 'Varanasi', 'Uttar Pradesh', 'NER', 'Varanasi'),
        ('Patna Junction', 'PNBE', 'Patna', 'Bihar', 'ECR', 'Patna'),
        ('Bhopal Junction', 'BPL', 'Bhopal', 'Madhya Pradesh', 'WCR', 'Bhopal'),
        ('Indore Junction', 'INDB', 'Indore', 'Madhya Pradesh', 'WCR', 'Indore'),
        ('Nagpur Junction', 'NGP', 'Nagpur', 'Maharashtra', 'CR', 'Nagpur'),
        ('Coimbatore Junction', 'CBE', 'Coimbatore', 'Tamil Nadu', 'SR', 'Coimbatore'),
        ('Thiruvananthapuram Central', 'TVC', 'Thiruvananthapuram', 'Kerala', 'SR', 'Thiruvananthapuram'),
        ('Guwahati Junction', 'GHY', 'Guwahati', 'Assam', 'NFR', 'Guwahati'),
        ('Surat', 'ST', 'Surat', 'Gujarat', 'WR', 'Surat'),
        ('Vadodara Junction', 'BRC', 'Vadodara', 'Gujarat', 'WR', 'Vadodara'),
        ('Rajkot Junction', 'RJT', 'Rajkot', 'Gujarat', 'WR', 'Rajkot'),
        ('Jodhpur Junction', 'JU', 'Jodhpur', 'Rajasthan', 'NWR', 'Jodhpur'),
        ('Kota Junction', 'KOTA', 'Kota', 'Rajasthan', 'WCR', 'Kota'),
        ('Ajmer Junction', 'AII', 'Ajmer', 'Rajasthan', 'NWR', 'Ajmer'),
        ('Bikaner Junction', 'BKN', 'Bikaner', 'Rajasthan', 'NWR', 'Bikaner'),
        ('Udaipur City', 'UDZ', 'Udaipur', 'Rajasthan', 'NWR', 'Udaipur'),
        ('Amritsar Junction', 'ASR', 'Amritsar', 'Punjab', 'NR', 'Firozpur'),
        ('Ludhiana Junction', 'LDH', 'Ludhiana', 'Punjab', 'NR', 'Firozpur'),
        ('Jalandhar City', 'JRC', 'Jalandhar', 'Punjab', 'NR', 'Firozpur'),
        ('Chandigarh Junction', 'CDG', 'Chandigarh', 'Chandigarh', 'NR', 'Ambala'),
        ('Jammu Tawi', 'JAT', 'Jammu', 'Jammu and Kashmir', 'NR', 'Firozpur'),
        ('Srinagar', 'SINA', 'Srinagar', 'Jammu and Kashmir', 'NR', 'Firozpur'),
        ('Dehradun', 'DDN', 'Dehradun', 'Uttarakhand', 'NR', 'Dehradun'),
        ('Haridwar Junction', 'HW', 'Haridwar', 'Uttarakhand', 'NR', 'Moradabad'),
        ('Rishikesh', 'RKSH', 'Rishikesh', 'Uttarakhand', 'NR', 'Dehradun'),
        ('Shimla', 'SML', 'Shimla', 'Himachal Pradesh', 'NR', 'Ambala'),
        ('Manali', 'MNLI', 'Manali', 'Himachal Pradesh', 'NR', 'Ambala'),
    ]
    
    # Generate additional stations to reach 1500+
    state_cities = {
        'Uttar Pradesh': ['Allahabad', 'Gorakhpur', 'Bareilly', 'Aligarh', 'Moradabad', 'Saharanpur', 'Firozabad', 'Jhansi', 'Muzaffarnagar', 'Mathura', 'Rampur', 'Shahjahanpur', 'Farrukhabad', 'Khurja', 'Hardoi', 'Raebareli', 'Etawah', 'Orai', 'Bahraich', 'Kheri', 'Sitapur', 'Lalitpur', 'Pilibhit', 'Hathras', 'Banda', 'Unnao', 'Jalaun', 'Ballia', 'Hamirpur', 'Fatehpur', 'Pratapgarh', 'Azamgarh', 'Sultanpur', 'Maharajganj', 'Gonda', 'Basti', 'Siddhartnagar', 'Faizabad', 'Amethi', 'Kushinagar', 'Deoria', 'Mau', 'Ghazipur', 'Jaunpur', 'Chandauli', 'Bhadohi', 'Mirzapur', 'Sonbhadra'],
        'Maharashtra': ['Nashik', 'Aurangabad', 'Solapur', 'Amravati', 'Kolhapur', 'Sangli', 'Malegaon', 'Akola', 'Latur', 'Dhule', 'Ahmednagar', 'Chandrapur', 'Parbhani', 'Ichalkaranji', 'Jalgaon', 'Ambernath', 'Bhusawal', 'Panvel', 'Badlapur', 'Beed', 'Gondia', 'Satara', 'Barshi', 'Yavatmal', 'Achalpur', 'Osmanabad', 'Nandurbar', 'Wardha', 'Udgir', 'Hinganghat'],
        'Tamil Nadu': ['Madurai', 'Salem', 'Tirupur', 'Erode', 'Vellore', 'Thoothukudi', 'Dindigul', 'Thanjavur', 'Ranipet', 'Sivakasi', 'Karur', 'Udhagamandalam', 'Hosur', 'Nagercoil', 'Kanchipuram', 'Kumarakonam', 'Pudukkottai', 'Ambur', 'Pollachi', 'Rajapalayam', 'Virudhunagar', 'Tindivananam', 'Tiruvannamalai', 'Cuddalore', 'Neyveli', 'Nagapattinam', 'Mayiladuthurai', 'Chidambaram', 'Villupuram', 'Tindivanam'],
        'Karnataka': ['Mysore', 'Hubli', 'Dharwad', 'Belgaum', 'Mangalore', 'Gulbarga', 'Bijapur', 'Bellary', 'Tumkur', 'Raichur', 'Bidar', 'Hospet', 'Gadag', 'Davangere', 'Chitradurga', 'Hassan', 'Shimoga', 'Udupi', 'Karwar', 'Bagalkot', 'Koppal', 'Haveri', 'Chikmagalur', 'Mandya', 'Kolar', 'Chamarajanagar', 'Chikkaballapur', 'Kodagu', 'Ramanagara', 'Yadgir'],
        'West Bengal': ['Durgapur', 'Asansol', 'Siliguri', 'Bardhaman', 'Malda', 'Kharagpur', 'Haldia', 'Krishnanagar', 'Ranaghat', 'Nabadwip', 'Santipur', 'Serampore', 'Baharampur', 'Chandannagar', 'Dankuni', 'Halisahar', 'Hugli', 'Kamarhati', 'Panihati', 'South Dumdum', 'Titagarh', 'Uttarpara', 'Bhatpara', 'Naihati', 'Baranagar', 'Rishra', 'Madhyamgram', 'Barrackpore', 'Bidhan Nagar', 'New Barrackpore'],
        'Gujarat': ['Gandhinagar', 'Junagadh', 'Bhavnagar', 'Anand', 'Navsari', 'Morbi', 'Mehsana', 'Bhuj', 'Surendranagar', 'Gandhidham', 'Bharuch', 'Valsad', 'Godhra', 'Patan', 'Veraval', 'Porbandar', 'Palanpur', 'Vapi', 'Gondal', 'Jetpur', 'Kalol', 'Dahod', 'Botad', 'Amreli', 'Deesa', 'Mahuva'],
        'Rajasthan': ['Alwar', 'Bharatpur', 'Sikar', 'Pali', 'Tonk', 'Kishangarh', 'Beawar', 'Hanumangarh', 'Gangapur City', 'Churu', 'Jhunjhunu', 'Sri Ganganagar', 'Sawai Madhopur', 'Makrana', 'Sujangarh', 'Lachhmangarh', 'Ratangarh', 'Sadulpur', 'Taranagar', 'Ladnu', 'Didwana', 'Nokha', 'Suratgarh', 'Padampur', 'Raisinghnagar', 'Anupgarh'],
        'Kerala': ['Kochi', 'Kozhikode', 'Thrissur', 'Kollam', 'Palakkad', 'Alappuzha', 'Kottayam', 'Kannur', 'Malappuram', 'Trichur', 'Ernakulam', 'Kasaragod', 'Pathanamthitta', 'Idukki', 'Wayanad', 'Palai', 'Changanassery', 'Kayamkulam', 'Neyyattinkara', 'Attingal', 'Varkala', 'Paravur', 'Angamaly', 'Perumbavoor', 'Muvattupuzha'],
        'Andhra Pradesh': ['Visakhapatnam', 'Vijayawada', 'Guntur', 'Nellore', 'Kurnool', 'Rajahmundry', 'Kadapa', 'Kakinada', 'Anantapur', 'Tirupati', 'Eluru', 'Nandyal', 'Chittoor', 'Machilipatnam', 'Adoni', 'Tenali', 'Proddatur', 'Hindupur', 'Bhimavaram', 'Madanapalle', 'Guntakal', 'Dharmavaram', 'Gudivada', 'Narasaraopet', 'Tadpatri', 'Chilakaluripet', 'Yemmiganur', 'Kadiri', 'Chirala', 'Amalapuram'],
        'Telangana': ['Warangal', 'Nizamabad', 'Karimnagar', 'Khammam', 'Mahbubnagar', 'Nalgonda', 'Adilabad', 'Suryapet', 'Miryalaguda', 'Jagtial', 'Mancherial', 'Kothagudem', 'Ramagundam', 'Siddipet', 'Palwancha', 'Bodhan', 'Sangareddy', 'Metpally', 'Zaheerabad', 'Kamareddy', 'Gadwal', 'Wanaparthy', 'Narayanpet', 'Vikarabad', 'Medak'],
        'Odisha': ['Bhubaneswar', 'Cuttack', 'Rourkela', 'Berhampur', 'Sambalpur', 'Puri', 'Balasore', 'Bhadrak', 'Baripada', 'Jharsuguda', 'Jeypore', 'Barbil', 'Kendujhar', 'Sunabeda', 'Rayagada', 'Paradip', 'Dhenkanal', 'Koraput', 'Bolangir', 'Bhawanipatna', 'Malkangiri', 'Nabarangpur', 'Nuapada', 'Kalahandi', 'Kandhamal'],
        'Madhya Pradesh': ['Gwalior', 'Jabalpur', 'Ujjain', 'Sagar', 'Dewas', 'Satna', 'Ratlam', 'Rewa', 'Murwara', 'Singrauli', 'Burhanpur', 'Khandwa', 'Morena', 'Bhind', 'Chhindwara', 'Guna', 'Shivpuri', 'Vidisha', 'Chhatarpur', 'Damoh', 'Mandsaur', 'Khargone', 'Neemuch', 'Pithampur', 'Tikamgarh', 'Shahdol', 'Umaria', 'Katni', 'Maihar', 'Nagda'],
        'Bihar': ['Gaya', 'Bhagalpur', 'Muzaffarpur', 'Darbhanga', 'Purnia', 'Arrah', 'Begusarai', 'Katihar', 'Munger', 'Chhapra', 'Sasaram', 'Hajipur', 'Dehri', 'Siwan', 'Motihari', 'Saharsa', 'Bettiah', 'Bagaha', 'Forbesganj', 'Kishanganj', 'Nawada', 'Jamui', 'Jehanabad', 'Aurangabad', 'Lakhisarai', 'Sheikhpura', 'Nalanda', 'Rohtas', 'Buxar', 'Kaimur'],
        'Chhattisgarh': ['Raipur', 'Bhilai', 'Korba', 'Bilaspur', 'Durg', 'Rajnandgaon', 'Jagdalpur', 'Raigarh', 'Ambikapur', 'Mahasamund', 'Dhamtari', 'Chirmiri', 'Janjgir', 'Sakti', 'Tilda', 'Mungeli', 'Ratanpur', 'Akaltara', 'Champa', 'Jashpur', 'Manendragarh', 'Baikunthpur', 'Wadrafnagar', 'Koriya', 'Surajpur'],
        'Jharkhand': ['Ranchi', 'Jamshedpur', 'Dhanbad', 'Bokaro', 'Deoghar', 'Hazaribagh', 'Giridih', 'Ramgarh', 'Medininagar', 'Phusro', 'Adityapur', 'Chaibasa', 'Dumka', 'Sahibganj', 'Godda', 'Pakur', 'Mihijam', 'Chas', 'Govindpur', 'Madhupur', 'Kodarma', 'Chatra', 'Hunterganj', 'Lohardaga', 'Chauparan'],
        'Punjab': ['Patiala', 'Bathinda', 'Mohali', 'Pathankot', 'Hoshiarpur', 'Batala', 'Moga', 'Abohar', 'Malerkotla', 'Khanna', 'Phagwara', 'Muktsar', 'Barnala', 'Rajpura', 'Firozpur', 'Kapurthala', 'Sangrur', 'Faridkot', 'Gurdaspur', 'Kharar', 'Gobindgarh', 'Mandi Gobindgarh', 'Morinda', 'Nakodar', 'Jagraon', 'Sunam', 'Dhuri', 'Malaud', 'Rampura Phul', 'Samana'],
        'Haryana': ['Faridabad', 'Gurgaon', 'Panipat', 'Ambala', 'Yamunanagar', 'Rohtak', 'Hisar', 'Karnal', 'Sonipat', 'Panchkula', 'Bhiwani', 'Sirsa', 'Bahadurgarh', 'Jind', 'Thanesar', 'Kaithal', 'Rewari', 'Narnaul', 'Pundri', 'Kosli', 'Palwal', 'Hansi', 'Mahendragarh', 'Ladwa', 'Sohna', 'Mewat', 'Fatehabad', 'Ratia', 'Tohana', 'Adampur'],
        'Himachal Pradesh': ['Solan', 'Mandi', 'Palampur', 'Sundernagar', 'Chamba', 'Una', 'Kullu', 'Hamirpur', 'Bilaspur', 'Kangra', 'Dharamshala', 'Nahan', 'Keylong', 'Kinnaur', 'Lahaul', 'Spiti', 'Kasauli', 'Nalagarh', 'Amb', 'Mehatpur', 'Gagret', 'Haroli', 'Dehra', 'Jaswan', 'Nadaun'],
        'Uttarakhand': ['Nainital', 'Roorkee', 'Haldwani', 'Rudrapur', 'Kashipur', 'Pithoragarh', 'Almora', 'Mussoorie', 'Tehri', 'Pauri', 'Chamoli', 'Bageshwar', 'Champawat', 'Rudraprayag', 'Uttarkashi', 'Kotdwar', 'Vikasnagar', 'Herbertpur', 'Laksar', 'Manglaur', 'Bhagwanpur', 'Kichha', 'Sitarganj', 'Ramnagar', 'Bazpur'],
        'Assam': ['Dibrugarh', 'Silchar', 'Nagaon', 'Tinsukia', 'Jorhat', 'Bongaigaon', 'Tezpur', 'Diphu', 'North Lakhimpur', 'Karimganj', 'Sivasagar', 'Goalpara', 'Barpeta', 'Mangaldoi', 'Nalbari', 'Rangia', 'Hailakandi', 'Morigaon', 'Hojai', 'Lanka', 'Lumding', 'Mariani', 'Naharkatiya', 'Duliajan', 'Doom Dooma'],
        'Meghalaya': ['Shillong', 'Tura', 'Cherrapunji', 'Jowai', 'Nongpoh', 'Baghmara', 'Ampati', 'Resubelpara', 'Nongstoin', 'Khliehriat', 'Williamnagar', 'Mairang', 'Mawkyrwat', 'Ranikor', 'Mawphlang', 'Byrnihat', 'Umiam', 'Ri Bhoi', 'Dawki', 'Bhoirymbong'],
        'Tripura': ['Agartala', 'Dharmanagar', 'Udaipur', 'Kailasahar', 'Belonia', 'Khowai', 'Amarpur', 'Ranirbazar', 'Sonamura', 'Sabroom', 'Kumarghat', 'Bishalghar', 'Kamalpur', 'Ambassa', 'Gandacharra', 'Kanchanpur', 'Panisagar', 'Damcherra', 'Longtharai', 'Rajnagar'],
        'Manipur': ['Imphal', 'Thoubal', 'Bishnupur', 'Churachandpur', 'Senapati', 'Ukhrul', 'Chandel', 'Tamenglong', 'Jiribam', 'Kakching', 'Tengnoupal', 'Kamjong', 'Noney', 'Pherzawl', 'Kangpokpi', 'Mayang Imphal', 'Porompat', 'Lamlai', 'Sugnu', 'Moreh'],
        'Mizoram': ['Aizawl', 'Lunglei', 'Saiha', 'Champhai', 'Kolasib', 'Serchhip', 'Mamit', 'Lawngtlai', 'Saitual', 'Khawzawl', 'Hnahthial', 'Bairabi', 'Vairengte', 'Tlabung', 'Kawrthah', 'Darlawn', 'Thenzawl', 'Khawhai', 'Lengpui', 'Reiek'],
        'Nagaland': ['Kohima', 'Dimapur', 'Mokokchung', 'Tuensang', 'Wokha', 'Mon', 'Zunheboto', 'Phek', 'Longleng', 'Kiphire', 'Peren', 'Chumukedima', 'Niuland', 'Noklak', 'Shamator', 'Tuli', 'Changtongya', 'Aboi', 'Longkhim', 'Tizit'],
        'Arunachal Pradesh': ['Itanagar', 'Naharlagun', 'Pasighat', 'Aalo', 'Bomdila', 'Tawang', 'Ziro', 'Tezu', 'Changlang', 'Khonsa', 'Seppa', 'Yingkiong', 'Anini', 'Daporijo', 'Basar', 'Koloriang', 'Roing', 'Namsai', 'Longding', 'Taliha'],
        'Sikkim': ['Gangtok', 'Namchi', 'Geyzing', 'Mangan', 'Jorethang', 'Singtam', 'Rangpo', 'Nayabazar', 'Ranipool', 'Tadong', 'Deorali', 'Rhenock', 'Pakyong', 'Soreng', 'Yuksom', 'Pelling', 'Ravangla', 'Legship', 'Dentam', 'Kalimpong']
    }
    
    # Zone and division mappings
    zone_division_map = {
        'NR': ['Delhi', 'Ambala', 'Firozpur', 'Lucknow', 'Moradabad'],
        'SR': ['Chennai', 'Madurai', 'Palakkad', 'Thiruvananthapuram', 'Tiruchirappalli', 'Salem'],
        'ER': ['Howrah', 'Sealdah', 'Asansol', 'Malda'],
        'WR': ['Mumbai', 'Ahmedabad', 'Vadodara', 'Rajkot', 'Ratlam', 'Bhavnagar'],
        'CR': ['Mumbai', 'Pune', 'Solapur', 'Bhusaval', 'Nagpur'],
        'NCR': ['Allahabad', 'Agra', 'Jhansi'],
        'NER': ['Gorakhpur', 'Varanasi', 'Lucknow'],
        'NFR': ['Alipurduar', 'Rangiya', 'Lumding', 'Tinsukia', 'Katihar'],
        'SER': ['Chakradharpur', 'Kharagpur', 'Ranchi', 'Adra'],
        'ECR': ['Danapur', 'Dhanbad', 'Mugalsarai', 'Pt Deen Dayal Upadhyaya'],
        'ECoR': ['Khurda Road', 'Sambalpur', 'Waltair'],
        'SCR': ['Secunderabad', 'Hyderabad', 'Vijayawada', 'Guntur', 'Guntakal', 'Nanded'],
        'SWR': ['Bangalore', 'Hubli', 'Mysore'],
        'WCR': ['Jabalpur', 'Bhopal', 'Kota'],
        'NWR': ['Jaipur', 'Ajmer', 'Bikaner', 'Jodhpur'],
        'SRR': ['Bilaspur', 'Raipur', 'Nagpur']
    }
    
    all_stations = list(major_stations)
    station_codes_used = {code for _, code, _, _, _, _ in major_stations}
    
    # Generate additional stations from each state
    for state, cities in state_cities.items():
        # Determine zone for the state
        if state in ['Delhi', 'Punjab', 'Haryana', 'Himachal Pradesh', 'Jammu and Kashmir', 'Uttarakhand']:
            zone = 'NR'
            division = random.choice(['Delhi', 'Ambala', 'Firozpur', 'Lucknow', 'Moradabad'])
        elif state in ['Uttar Pradesh']:
            zone = random.choice(['NR', 'NCR', 'NER'])
            division = random.choice(['Delhi', 'Moradabad', 'Lucknow', 'Allahabad', 'Agra', 'Jhansi', 'Gorakhpur', 'Varanasi'])
        elif state in ['Maharashtra']:
            zone = random.choice(['WR', 'CR'])
            division = random.choice(['Mumbai', 'Pune', 'Solapur', 'Bhusaval', 'Nagpur', 'Ahmedabad'])
        elif state in ['Gujarat']:
            zone = 'WR'
            division = random.choice(['Ahmedabad', 'Vadodara', 'Rajkot', 'Ratlam', 'Bhavnagar'])
        elif state in ['Tamil Nadu', 'Kerala']:
            zone = 'SR'
            division = random.choice(['Chennai', 'Madurai', 'Palakkad', 'Thiruvananthapuram', 'Tiruchirappalli', 'Salem'])
        elif state in ['West Bengal', 'Tripura']:
            zone = 'ER'
            division = random.choice(['Howrah', 'Sealdah', 'Asansol', 'Malda'])
        elif state in ['Assam', 'Meghalaya', 'Manipur', 'Mizoram', 'Nagaland', 'Arunachal Pradesh']:
            zone = 'NFR'
            division = random.choice(['Alipurduar', 'Rangiya', 'Lumding', 'Tinsukia', 'Katihar'])
        elif state in ['Bihar']:
            zone = 'ECR'
            division = random.choice(['Danapur', 'Dhanbad', 'Mugalsarai', 'Pt Deen Dayal Upadhyaya'])
        elif state in ['Odisha']:
            zone = 'ECoR'
            division = random.choice(['Khurda Road', 'Sambalpur', 'Waltair'])
        elif state in ['Andhra Pradesh', 'Telangana']:
            zone = 'SCR'
            division = random.choice(['Secunderabad', 'Hyderabad', 'Vijayawada', 'Guntur', 'Guntakal', 'Nanded'])
        elif state in ['Karnataka']:
            zone = 'SWR'
            division = random.choice(['Bangalore', 'Hubli', 'Mysore'])
        elif state in ['Madhya Pradesh']:
            zone = 'WCR'
            division = random.choice(['Jabalpur', 'Bhopal', 'Kota'])
        elif state in ['Rajasthan']:
            zone = 'NWR'
            division = random.choice(['Jaipur', 'Ajmer', 'Bikaner', 'Jodhpur'])
        elif state in ['Chhattisgarh']:
            zone = 'SRR'
            division = random.choice(['Bilaspur', 'Raipur'])
        elif state in ['Jharkhand']:
            zone = 'SER'
            division = random.choice(['Chakradharpur', 'Ranchi', 'Adra'])
        else:
            zone = 'CR'
            division = 'Mumbai'
        
        for city in cities:
            if len(all_stations) >= 1500:
                break
                
            # Generate station code
            base_code = city[:3].upper().replace(' ', '') if len(city) >= 3 else city.upper() + 'X' * (3 - len(city))
            
            # Ensure unique code
            code = base_code
            suffix = 1
            while code in station_codes_used:
                if len(base_code) >= 2:
                    code = base_code[:2] + str(suffix)
                else:
                    code = base_code + str(suffix)
                suffix += 1
                if suffix > 99:  # Avoid infinite loop
                    code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=3))
                    while code in station_codes_used:
                        code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=3))
                    break
            
            station_name = f"{city} Junction"
            all_stations.append((station_name, code, city, state, zone, division))
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
        zone = random.choice(['NR', 'SR', 'ER', 'WR', 'CR', 'NCR', 'NER', 'NFR', 'SER', 'ECR', 'ECoR', 'SCR', 'SWR', 'WCR', 'NWR'])
        division = random.choice(zone_division_map.get(zone, ['Mumbai']))
        
        all_stations.append((station_name, code, city, state, zone, division))
        station_codes_used.add(code)
    
    return all_stations[:1500]

def get_comprehensive_trains_data() -> List[Tuple]:
    """Generate comprehensive trains data with 1000+ trains"""
    
    # Base train types and their characteristics
    train_types = {
        'Rajdhani Express': {'seats': (400, 500), 'fare': (0.75, 1.20), 'tatkal': (40, 60), 'tatkal_fare': (1.10, 1.50), 'speed': (110, 130)},
        'Shatabdi Express': {'seats': (300, 400), 'fare': (0.85, 1.35), 'tatkal': (30, 50), 'tatkal_fare': (1.20, 1.60), 'speed': (110, 130)},
        'Duronto Express': {'seats': (450, 550), 'fare': (0.70, 1.10), 'tatkal': (45, 65), 'tatkal_fare': (1.05, 1.45), 'speed': (100, 120)},
        'Superfast Express': {'seats': (400, 600), 'fare': (0.50, 0.80), 'tatkal': (50, 80), 'tatkal_fare': (0.70, 1.10), 'speed': (90, 110)},
        'Express': {'seats': (400, 600), 'fare': (0.40, 0.70), 'tatkal': (50, 80), 'tatkal_fare': (0.60, 1.00), 'speed': (70, 90)},
        'Mail Express': {'seats': (350, 500), 'fare': (0.35, 0.65), 'tatkal': (40, 70), 'tatkal_fare': (0.55, 0.95), 'speed': (70, 85)},
        'Passenger': {'seats': (200, 350), 'fare': (0.25, 0.45), 'tatkal': (20, 40), 'tatkal_fare': (0.40, 0.70), 'speed': (40, 60)},
        'Intercity Express': {'seats': (250, 400), 'fare': (0.45, 0.75), 'tatkal': (25, 45), 'tatkal_fare': (0.65, 1.05), 'speed': (75, 95)},
        'Jan Shatabdi Express': {'seats': (300, 450), 'fare': (0.60, 0.90), 'tatkal': (30, 50), 'tatkal_fare': (0.85, 1.25), 'speed': (100, 120)},
        'Garib Rath Express': {'seats': (400, 500), 'fare': (0.40, 0.70), 'tatkal': (40, 60), 'tatkal_fare': (0.60, 1.00), 'speed': (90, 110)},
        'Humsafar Express': {'seats': (350, 450), 'fare': (0.65, 0.95), 'tatkal': (35, 55), 'tatkal_fare': (0.90, 1.30), 'speed': (100, 120)},
        'Tejas Express': {'seats': (300, 400), 'fare': (0.80, 1.20), 'tatkal': (30, 50), 'tatkal_fare': (1.15, 1.55), 'speed': (110, 130)},
        'Vande Bharat Express': {'seats': (500, 600), 'fare': (1.00, 1.50), 'tatkal': (50, 70), 'tatkal_fare': (1.40, 1.90), 'speed': (130, 160)},
        'Double Decker Express': {'seats': (600, 800), 'fare': (0.55, 0.85), 'tatkal': (60, 90), 'tatkal_fare': (0.80, 1.20), 'speed': (80, 100)},
        'AC Express': {'seats': (350, 450), 'fare': (0.70, 1.00), 'tatkal': (35, 55), 'tatkal_fare': (1.00, 1.40), 'speed': (85, 105)},
        'Antyodaya Express': {'seats': (500, 700), 'fare': (0.30, 0.50), 'tatkal': (50, 80), 'tatkal_fare': (0.45, 0.75), 'speed': (60, 80)},
        'Sampark Kranti Express': {'seats': (450, 550), 'fare': (0.50, 0.80), 'tatkal': (45, 65), 'tatkal_fare': (0.70, 1.10), 'speed': (85, 105)},
        'Jan Sadharan Express': {'seats': (400, 600), 'fare': (0.35, 0.60), 'tatkal': (40, 70), 'tatkal_fare': (0.50, 0.85), 'speed': (65, 85)},
        'Premium Express': {'seats': (300, 400), 'fare': (0.90, 1.40), 'tatkal': (30, 50), 'tatkal_fare': (1.25, 1.70), 'speed': (100, 130)},
        'MEMU': {'seats': (150, 300), 'fare': (0.20, 0.40), 'tatkal': (15, 30), 'tatkal_fare': (0.30, 0.60), 'speed': (40, 70)}
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
        # Generate unique train number (5-digit format)
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
        
        # Naming patterns
        naming_patterns = [
            f"{city1} {train_type}",
            f"{city1} {city2} {train_type}",
            f"{city2} {city1} {train_type}",
            f"{city1}-{city2} {train_type}",
            f"{train_type}"
        ]
        
        train_name = random.choice(naming_patterns)
        
        # Generate characteristics
        total_seats = random.randint(*type_config['seats'])
        available_seats = total_seats  # Initially all available
        fare_per_km = round(random.uniform(*type_config['fare']), 2)
        tatkal_seats = random.randint(*type_config['tatkal'])
        tatkal_fare_per_km = round(random.uniform(*type_config['tatkal_fare']), 2)
        speed_kmph = random.randint(*type_config['speed'])
        
        # Additional features
        pantry_car = random.choice([True, False]) if train_type not in ['Passenger', 'MEMU'] else False
        wifi_available = random.choice([True, False]) if train_type in ['Rajdhani Express', 'Shatabdi Express', 'Vande Bharat Express', 'Tejas Express'] else False
        charging_points = random.choice([True, False]) if train_type not in ['Passenger'] else False
        
        trains.append((
            train_number, train_name, train_type.split()[0], total_seats, available_seats, 
            fare_per_km, tatkal_seats, tatkal_fare_per_km, speed_kmph,
            pantry_car, wifi_available, charging_points
        ))
    
    return trains

def get_seat_number(seat_type: str, coach_class: str) -> str:
    """Generate realistic seat numbers based on coach class"""
    if coach_class == 'SL':  # Sleeper
        berth_numbers = list(range(1, 73))  # SL coaches typically have 72 berths
        return str(random.choice(berth_numbers))
    elif coach_class in ['AC3', 'AC2']:  # AC 3-tier, AC 2-tier
        berth_numbers = list(range(1, 65))  # AC coaches typically have 64 berths
        return str(random.choice(berth_numbers))
    elif coach_class == 'AC1':  # AC First Class
        cabin_numbers = list(range(1, 25))  # AC First Class has fewer berths
        return str(random.choice(cabin_numbers))
    elif coach_class == '2S':  # Second Sitting
        seat_numbers = list(range(1, 101))  # Sitting coaches have more seats
        return str(random.choice(seat_numbers))
    elif coach_class == 'CC':  # Chair Car
        seat_numbers = list(range(1, 79))  # Chair Car
        return str(random.choice(seat_numbers))
    else:
        return str(random.randint(1, 72))

def get_berth_type(coach_class: str) -> str:
    """Get berth type based on coach class"""
    if coach_class in ['SL', 'AC3']:
        return random.choice(['Lower', 'Middle', 'Upper', 'Side Lower', 'Side Upper'])
    elif coach_class == 'AC2':
        return random.choice(['Lower', 'Upper', 'Side Lower', 'Side Upper'])
    elif coach_class == 'AC1':
        return random.choice(['Lower', 'Upper'])
    elif coach_class in ['2S', 'CC']:
        return 'Seat'
    else:
        return 'Lower'

def insert_comprehensive_data(conn):
    """Insert comprehensive test data covering all features"""
    cursor = conn.cursor()
    logger.info("🏗️ Inserting comprehensive test data...")
    
    # 1. Create admin and test users
    logger.info("👥 Creating users...")
    
    users_data = [
        ('admin', 'admin@railserve.com', 'admin123', 'super_admin'),
        ('railway_admin', 'railway.admin@railserve.com', 'railway123', 'admin'),
        ('station_master', 'station.master@railserve.com', 'station123', 'admin'),
        ('testuser', 'test@example.com', 'user123', 'user'),
        ('john_doe', 'john.doe@email.com', 'password123', 'user'),
        ('jane_smith', 'jane.smith@email.com', 'password123', 'user'),
        ('rajesh_kumar', 'rajesh.kumar@email.com', 'password123', 'user'),
        ('priya_sharma', 'priya.sharma@email.com', 'password123', 'user'),
        ('amit_patel', 'amit.patel@email.com', 'password123', 'user'),
        ('sunita_gupta', 'sunita.gupta@email.com', 'password123', 'user'),
        ('rahul_singh', 'rahul.singh@email.com', 'password123', 'user'),
        ('meera_nair', 'meera.nair@email.com', 'password123', 'user'),
        ('vikram_malhotra', 'vikram.malhotra@email.com', 'password123', 'user'),
        ('anita_roy', 'anita.roy@email.com', 'password123', 'user'),
        ('suresh_jain', 'suresh.jain@email.com', 'password123', 'user')
    ]
    
    user_ids = {}
    
    for username, email, password, role in users_data:
        password_hash = generate_password_hash(password)
        phone = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        
        cursor.execute("""
            INSERT INTO "user" (username, email, password_hash, role, phone, 
                              date_of_birth, gender, address, city, state, pincode)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (username, email, password_hash, role, phone,
              date(1980 + random.randint(0, 30), random.randint(1, 12), random.randint(1, 28)),
              random.choice(['Male', 'Female']),
              f"{random.randint(1, 999)} Sample Street",
              random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata']),
              random.choice(['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'West Bengal']),
              str(random.randint(100000, 999999))))
        
        user_id = cursor.fetchone()[0]
        user_ids[username] = user_id
    
    # 2. Insert comprehensive stations data
    logger.info("🚉 Inserting 1500+ stations...")
    stations_data = get_comprehensive_stations_data()
    station_ids = {}
    
    for i, (name, code, city, state, zone, division) in enumerate(stations_data):
        # Add realistic coordinates (approximate)
        latitude = round(random.uniform(8.0, 37.0), 6)  # India's latitude range
        longitude = round(random.uniform(68.0, 97.0), 6)  # India's longitude range
        
        # Check if station already exists by name or code
        cursor.execute("SELECT id FROM station WHERE name = %s OR code = %s", (name, code))
        existing = cursor.fetchone()
        
        if existing:
            station_id = existing[0]
        else:
            cursor.execute("""
                INSERT INTO station (name, code, city, state, zone, division, 
                                   latitude, longitude, platforms, electric_traction, facilities)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                RETURNING id
            """, (name, code, city, state, zone, division, latitude, longitude,
                  random.randint(1, 12),  # platforms
                  random.choice([True, False]),  # electric traction
                  'Waiting Room, Food Court, WiFi, Parking'))
            
            station_id = cursor.fetchone()[0]
        station_ids[code] = station_id
    
    # 3. Insert comprehensive trains data
    logger.info("🚂 Inserting 1000+ trains...")
    trains_data = get_comprehensive_trains_data()
    train_ids = {}
    
    for (number, name, train_type, total_seats, available_seats, fare_per_km, 
         tatkal_seats, tatkal_fare_per_km, speed_kmph, pantry_car, wifi_available, charging_points) in trains_data:
        
        cursor.execute("""
            INSERT INTO train (number, name, train_type, total_seats, available_seats, 
                             fare_per_km, tatkal_seats, tatkal_fare_per_km, speed_kmph,
                             pantry_car, wifi_available, charging_points)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (number, name, train_type, total_seats, available_seats, fare_per_km,
              tatkal_seats, tatkal_fare_per_km, speed_kmph, pantry_car, wifi_available, charging_points))
        
        train_id = cursor.fetchone()[0]
        train_ids[number] = train_id
    
    # 4. Create train routes for each train
    logger.info("🗺️ Creating train routes...")
    
    station_list = list(station_ids.keys())
    for train_number, train_id in list(train_ids.items())[:200]:  # Create routes for first 200 trains
        # Create a route with 3-8 stations
        route_length = random.randint(3, 8)
        selected_stations = random.sample(station_list, route_length)
        
        distance = 0
        for seq, station_code in enumerate(selected_stations, 1):
            if seq == 1:
                arrival_time = None
                departure_time = time(random.randint(6, 22), random.randint(0, 59))
            elif seq == len(selected_stations):
                arrival_time = time(random.randint(6, 22), random.randint(0, 59))
                departure_time = None
            else:
                arrival_time = time(random.randint(6, 22), random.randint(0, 59))
                departure_time = time(random.randint(6, 22), random.randint(0, 59))
            
            distance += random.randint(50, 300) if seq > 1 else 0
            
            cursor.execute("""
                INSERT INTO train_route (train_id, station_id, sequence, arrival_time, 
                                       departure_time, distance_from_start, halt_duration,
                                       platform_number, commercial_stop)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (train_id, station_ids[station_code], seq, arrival_time, departure_time, 
                  distance, random.randint(2, 10), str(random.randint(1, 8)), True))
    
    # 5. Create train coaches for each train
    logger.info("🚃 Creating train coaches...")
    
    coach_classes = ['AC1', 'AC2', 'AC3', 'SL', '2S', 'CC']
    for train_id in list(train_ids.values())[:100]:  # Add coaches for first 100 trains
        # Each train gets 2-4 different coach types
        selected_classes = random.sample(coach_classes, random.randint(2, 4))
        
        for coach_type in selected_classes:
            if coach_type == 'AC1':
                seats_per_coach = random.randint(18, 24)
                multiplier = 3.5
            elif coach_type == 'AC2':
                seats_per_coach = random.randint(48, 52)
                multiplier = 2.5
            elif coach_type == 'AC3':
                seats_per_coach = random.randint(64, 72)
                multiplier = 1.8
            elif coach_type == 'SL':
                seats_per_coach = random.randint(72, 78)
                multiplier = 1.0
            elif coach_type == '2S':
                seats_per_coach = random.randint(90, 104)
                multiplier = 0.6
            else:  # CC
                seats_per_coach = random.randint(72, 78)
                multiplier = 1.2
            
            cursor.execute("""
                INSERT INTO train_coach (train_id, coach_type, coach_count, seats_per_coach, 
                                       base_fare_multiplier, amenities)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (train_id, coach_type, random.randint(1, 3), seats_per_coach, multiplier,
                  'Reading Light, Charging Point, Clean Bedding'))
    
    # 6. Create group bookings
    logger.info("👨‍👩‍👧‍👦 Creating group bookings...")
    
    group_booking_ids = []
    for i in range(50):  # Create 50 group bookings
        group_name = f"Family Group {i+1}" if random.choice([True, False]) else f"Corporate Group {i+1}"
        group_type = 'family' if 'Family' in group_name else 'corporate'
        
        cursor.execute("""
            INSERT INTO group_booking (group_name, group_leader_id, group_type, total_passengers,
                                     contact_email, contact_phone, special_requirements,
                                     group_discount_rate, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (group_name, random.choice(list(user_ids.values())), group_type,
              random.randint(4, 15), 'group@example.com', '9876543210',
              'Adjoining seats requested', random.choice([5.0, 10.0, 15.0]), 'confirmed'))
        
        group_booking_ids.append(cursor.fetchone()[0])
    
    # 7. Create comprehensive bookings
    logger.info("🎫 Creating comprehensive bookings...")
    
    booking_ids = []
    booking_statuses = ['confirmed', 'waitlisted', 'cancelled', 'pending_payment']
    booking_types = ['general', 'tatkal', 'premium']
    quotas = ['general', 'tatkal', 'ladies', 'handicapped', 'senior_citizen', 'defense', 'parliament']
    coach_classes = ['AC1', 'AC2', 'AC3', 'SL', '2S', 'CC']
    
    for i in range(2000):  # Create 2000 bookings
        pnr = generate_pnr()
        user_id = random.choice(list(user_ids.values()))
        train_id = random.choice(list(train_ids.values()))
        
        # Select random stations for journey
        available_stations = list(station_ids.values())
        from_station_id = random.choice(available_stations)
        to_station_id = random.choice(available_stations)
        while to_station_id == from_station_id:
            to_station_id = random.choice(available_stations)
        
        journey_date = date.today() + timedelta(days=random.randint(1, 120))
        passengers = random.randint(1, 6)
        coach_class = random.choice(coach_classes)
        booking_type = random.choice(booking_types)
        status = random.choice(booking_statuses)
        quota = random.choice(quotas) if booking_type == 'general' else 'tatkal'
        distance_km = random.randint(100, 2000)
        
        # Calculate amount based on distance and class
        base_fare = distance_km * random.uniform(0.5, 2.0)
        class_multipliers = {'AC1': 4.0, 'AC2': 2.8, 'AC3': 1.8, 'SL': 1.0, '2S': 0.6, 'CC': 1.2}
        total_amount = base_fare * class_multipliers.get(coach_class, 1.0) * passengers
        
        if booking_type == 'tatkal':
            total_amount *= 1.4  # Tatkal surcharge
        
        group_booking_id = random.choice(group_booking_ids) if random.random() < 0.1 else None
        
        cursor.execute("""
            INSERT INTO booking (pnr, user_id, train_id, from_station_id, to_station_id,
                               journey_date, passengers, total_amount, booking_type, quota,
                               coach_class, status, mobile_number, email_address,
                               boarding_station_id, destination_station_id, distance_km,
                               group_booking_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (pnr, user_id, train_id, from_station_id, to_station_id, journey_date,
              passengers, total_amount, booking_type, quota, coach_class, status,
              '9876543210', 'passenger@example.com', from_station_id, to_station_id,
              distance_km, group_booking_id))
        
        booking_id = cursor.fetchone()[0]
        booking_ids.append(booking_id)
    
    # 8. Create passengers for each booking
    logger.info("👤 Creating passengers...")
    
    names = ['Amit Kumar', 'Priya Sharma', 'Rajesh Patel', 'Sunita Gupta', 'Vikram Singh', 
             'Meera Nair', 'Rahul Jain', 'Anita Roy', 'Suresh Malhotra', 'Kavya Reddy',
             'Arjun Mehta', 'Deepika Iyer', 'Rohit Agarwal', 'Sneha Verma', 'Manoj Yadav']
    
    for booking_id in booking_ids:
        # Get booking details
        cursor.execute("""
            SELECT passengers, coach_class, status FROM booking WHERE id = %s
        """, (booking_id,))
        result = cursor.fetchone()
        if result is None:
            continue
            
        passengers_count, coach_class, booking_status = result
        
        for p in range(passengers_count):
            name = random.choice(names)
            age = random.randint(5, 75)
            gender = random.choice(['Male', 'Female'])
            id_proof_type = random.choice(['Aadhar', 'PAN', 'Passport', 'Driving License'])
            id_proof_number = ''.join([str(random.randint(0, 9)) for _ in range(12)])
            
            # Assign seat only for confirmed bookings
            seat_number = get_seat_number('confirmed', coach_class) if booking_status == 'confirmed' else None
            coach_number = f"{random.choice(['A', 'B', 'S', 'D'])}{random.randint(1, 12)}" if booking_status == 'confirmed' else None
            berth_type = get_berth_type(coach_class) if booking_status == 'confirmed' else None
            
            cursor.execute("""
                INSERT INTO passenger (booking_id, name, age, gender, id_proof_type, id_proof_number,
                                     seat_number, coach_number, berth_type, coach_class, meal_preference)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (booking_id, name, age, gender, id_proof_type, id_proof_number,
                  seat_number, coach_number, berth_type, coach_class, 
                  random.choice(['Vegetarian', 'Non-Vegetarian', 'Jain'])))
    
    # 9. Create payments for bookings
    logger.info("💳 Creating payments...")
    
    payment_methods = ['card', 'netbanking', 'upi', 'wallet']
    payment_statuses = ['success', 'failed', 'pending', 'refunded']
    
    for booking_id in booking_ids[:1500]:  # Create payments for first 1500 bookings
        # Get booking amount
        cursor.execute("SELECT total_amount FROM booking WHERE id = %s", (booking_id,))
        result = cursor.fetchone()
        if result is None:
            continue
            
        amount = result[0]
        payment_method = random.choice(payment_methods)
        status = random.choice(payment_statuses)
        
        # Create transaction IDs
        transaction_id = f"TXN{datetime.now().strftime('%Y%m%d')}{random.randint(10000, 99999)}"
        gateway_transaction_id = f"GW{random.randint(1000000000, 9999999999)}"
        
        completed_at = datetime.now() - timedelta(days=random.randint(0, 30)) if status == 'success' else None
        
        cursor.execute("""
            INSERT INTO payment (booking_id, user_id, amount, payment_method, transaction_id,
                                gateway_transaction_id, status, completed_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (booking_id, random.choice(list(user_ids.values())), amount, payment_method,
              transaction_id, gateway_transaction_id, status, completed_at))
    
    # 10. Create waitlist entries
    logger.info("⏳ Creating waitlist entries...")
    
    # Get waitlisted bookings
    cursor.execute("SELECT id, train_id, journey_date, coach_class FROM booking WHERE status = 'waitlisted'")
    waitlisted_bookings = cursor.fetchall()
    
    waitlist_types = ['GNWL', 'PQWL', 'RLWL', 'TQWL']
    
    for booking_id, train_id, journey_date, coach_class in waitlisted_bookings:
        waitlist_type = random.choice(waitlist_types)
        position = random.randint(1, 50)
        initial_position = position + random.randint(0, 10)
        
        cursor.execute("""
            INSERT INTO waitlist (booking_id, train_id, journey_date, coach_class, position,
                                waitlist_type, initial_position)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (booking_id, train_id, journey_date, coach_class, position, waitlist_type, initial_position))
    
    # 11. Create tatkal time slots
    logger.info("⚡ Creating tatkal time slots...")
    
    tatkal_slots = [
        ('AC Classes', 'AC1,AC2,AC3', '10:00:00', '11:00:00', 1),
        ('Sleeper Class', 'SL', '11:00:00', '12:00:00', 1),
        ('Chair Car', 'CC,2S', '10:00:00', '11:00:00', 1),
        ('Premium Tatkal', 'AC1,AC2', '10:00:00', '10:30:00', 1)
    ]
    
    for name, coach_classes, open_time, close_time, days_before in tatkal_slots:
        cursor.execute("""
            INSERT INTO tatkal_time_slot (name, coach_classes, open_time, close_time, 
                                        days_before_journey, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, coach_classes, open_time, close_time, days_before, user_ids['admin']))
    
    # 12. Create restaurants for food service
    logger.info("🍽️ Creating restaurants...")
    
    restaurant_names = [
        'Delhi Darbar', 'Punjab Kitchen', 'South Indian Delight', 'Gujarati Thali',
        'Bengali Bites', 'Rajasthani Rasoi', 'Mumbai Street Food', 'Hyderabad Biryani',
        'Chennai Express', 'Kolkata Kathi', 'Agra Sweets', 'Jaipur Snacks',
        'Lucknow Kebabs', 'Amritsar Kulcha', 'Mysore Masala', 'Goa Fish Curry'
    ]
    
    restaurant_ids = []
    for i, name in enumerate(restaurant_names):
        station_id = random.choice(list(station_ids.values()))
        
        cursor.execute("""
            INSERT INTO restaurant (name, station_id, contact_number, email, cuisine_type,
                                  rating, delivery_time, minimum_order, delivery_charge,
                                  food_safety_rating, verified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (name, station_id, '9876543210', f'{name.lower().replace(" ", "")}@food.com',
              random.choice(['North Indian', 'South Indian', 'Chinese', 'Continental', 'Fast Food']),
              round(random.uniform(3.5, 4.9), 1), random.randint(20, 45),
              random.randint(100, 300), random.randint(20, 50),
              random.choice(['A+', 'A', 'B+']), True))
        
        restaurant_ids.append(cursor.fetchone()[0])
    
    # 13. Create menu items for restaurants
    logger.info("📜 Creating menu items...")
    
    menu_items = [
        ('Paneer Butter Masala', 'Breakfast', 'Vegetarian', 180),
        ('Chicken Biryani', 'Lunch', 'Non-Vegetarian', 250),
        ('Masala Dosa', 'Breakfast', 'Vegetarian', 120),
        ('Fish Curry Rice', 'Lunch', 'Non-Vegetarian', 200),
        ('Chole Bhature', 'Breakfast', 'Vegetarian', 150),
        ('Mutton Curry', 'Dinner', 'Non-Vegetarian', 300),
        ('Veg Thali', 'Lunch', 'Vegetarian', 220),
        ('Chicken Tandoori', 'Dinner', 'Non-Vegetarian', 280),
        ('Idli Sambar', 'Breakfast', 'Vegetarian', 80),
        ('Prawn Curry', 'Dinner', 'Non-Vegetarian', 320),
        ('Rajma Rice', 'Lunch', 'Vegetarian', 160),
        ('Seekh Kebab', 'Dinner', 'Non-Vegetarian', 240),
        ('Aloo Paratha', 'Breakfast', 'Vegetarian', 100),
        ('Butter Chicken', 'Dinner', 'Non-Vegetarian', 280),
        ('Samosa', 'Snacks', 'Vegetarian', 40),
        ('Tea', 'Beverages', 'Vegetarian', 20),
        ('Coffee', 'Beverages', 'Vegetarian', 25),
        ('Cold Drink', 'Beverages', 'Vegetarian', 30)
    ]
    
    menu_item_ids = []
    for restaurant_id in restaurant_ids:
        # Each restaurant gets 8-12 menu items
        selected_items = random.sample(menu_items, random.randint(8, 12))
        
        for name, category, food_type, base_price in selected_items:
            price = base_price + random.randint(-20, 50)  # Price variation
            
            cursor.execute("""
                INSERT INTO menu_item (restaurant_id, name, category, food_type, price,
                                     preparation_time, is_popular, calories)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, (restaurant_id, name, category, food_type, price,
                  random.randint(10, 30), random.choice([True, False]),
                  random.randint(200, 800)))
            
            menu_item_ids.append(cursor.fetchone()[0])
    
    # 14. Create food orders
    logger.info("🍕 Creating food orders...")
    
    # Get confirmed bookings for food orders
    cursor.execute("SELECT id FROM booking WHERE status = 'confirmed' LIMIT 300")
    confirmed_booking_ids = [row[0] for row in cursor.fetchall()]
    
    food_order_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled']
    
    for i in range(200):  # Create 200 food orders
        booking_id = random.choice(confirmed_booking_ids)
        restaurant_id = random.choice(restaurant_ids)
        delivery_station_id = random.choice(list(station_ids.values()))
        
        order_number = generate_order_number()
        
        # Get random menu items for this order
        cursor.execute("SELECT id, price FROM menu_item WHERE restaurant_id = %s", (restaurant_id,))
        available_items = cursor.fetchall()
        
        if not available_items:
            continue
        
        selected_items = random.sample(available_items, random.randint(1, 4))
        
        item_total = 0
        order_items = []
        for item_id, price in selected_items:
            quantity = random.randint(1, 3)
            total_price = price * quantity
            item_total += total_price
            order_items.append((item_id, quantity, price, total_price))
        
        delivery_charge = random.randint(20, 50)
        tax_amount = item_total * 0.05  # 5% tax
        final_amount = item_total + delivery_charge + tax_amount
        
        status = random.choice(food_order_statuses)
        
        cursor.execute("""
            INSERT INTO food_order (booking_id, user_id, restaurant_id, delivery_station_id,
                                  order_number, item_total, delivery_charge, tax_amount,
                                  final_amount, status, contact_number, coach_number, seat_number)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (booking_id, random.choice(list(user_ids.values())), restaurant_id, delivery_station_id,
              order_number, item_total, delivery_charge, tax_amount, final_amount, status,
              '9876543210', f"S{random.randint(1, 12)}", str(random.randint(1, 72))))
        
        food_order_id = cursor.fetchone()[0]
        
        # Insert food order items
        for item_id, quantity, unit_price, total_price in order_items:
            cursor.execute("""
                INSERT INTO food_order_item (food_order_id, menu_item_id, quantity, unit_price, total_price)
                VALUES (%s, %s, %s, %s, %s)
            """, (food_order_id, item_id, quantity, unit_price, total_price))
    
    # 15. Create loyalty program memberships
    logger.info("🏆 Creating loyalty programs...")
    
    tiers = ['Silver', 'Gold', 'Platinum', 'Diamond']
    
    for username, user_id in user_ids.items():
        if username in ['admin', 'railway_admin', 'station_master']:
            continue  # Skip admin users
        
        membership_number = generate_membership_number()
        tier = random.choice(tiers)
        points_earned = random.randint(1000, 50000)
        points_redeemed = random.randint(0, points_earned // 2)
        points_balance = points_earned - points_redeemed
        
        cursor.execute("""
            INSERT INTO loyalty_program (user_id, membership_number, tier, points_earned,
                                       points_redeemed, points_balance, total_journeys,
                                       total_distance, total_spent, tier_valid_until)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, membership_number, tier, points_earned, points_redeemed, points_balance,
              random.randint(5, 50), random.uniform(1000, 25000), random.uniform(10000, 200000),
              date.today() + timedelta(days=365)))
    
    # 16. Create train status entries
    logger.info("🚂 Creating train status entries...")
    
    statuses = ['On Time', 'Delayed', 'Cancelled', 'Diverted']
    
    for i, train_id in enumerate(list(train_ids.values())[:100]):  # Status for first 100 trains
        status = random.choice(statuses)
        delay_minutes = random.randint(0, 120) if status == 'Delayed' else 0
        current_station_id = random.choice(list(station_ids.values()))
        journey_date = date.today() + timedelta(days=random.randint(0, 30))
        
        cursor.execute("""
            INSERT INTO train_status (train_id, current_station_id, status, delay_minutes,
                                    journey_date, platform_number)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (train_id, current_station_id, status, delay_minutes, journey_date,
              str(random.randint(1, 8))))
    
    # 17. Create seat availability entries
    logger.info("💺 Creating seat availability...")
    
    for i, train_id in enumerate(list(train_ids.values())[:50]):  # Availability for first 50 trains
        # Create availability for next 30 days
        for days_ahead in range(1, 31):
            journey_date = date.today() + timedelta(days=days_ahead)
            
            # Create availability for different coach classes
            for coach_class in ['AC1', 'AC2', 'AC3', 'SL', '2S']:
                from_station_id = random.choice(list(station_ids.values()))
                to_station_id = random.choice(list(station_ids.values()))
                
                total_seats = random.randint(50, 200)
                confirmed_seats = random.randint(0, total_seats)
                waiting_list = random.randint(0, 50)
                rac_seats = random.randint(0, 10)
                available_seats = max(0, total_seats - confirmed_seats - rac_seats)
                
                current_status = 'AVAILABLE' if available_seats > 10 else ('RAC' if rac_seats > 0 else 'WAITING')
                
                cursor.execute("""
                    INSERT INTO seat_availability (train_id, from_station_id, to_station_id,
                                                 journey_date, coach_class, total_seats,
                                                 available_seats, waiting_list, rac_seats,
                                                 confirmed_seats, current_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (train_id, from_station_id, to_station_id, journey_date, coach_class,
                      total_seats, available_seats, waiting_list, rac_seats, confirmed_seats, current_status))
    
    # 18. Create refund requests
    logger.info("💰 Creating refund requests...")
    
    # Get some cancelled bookings for refund requests
    cursor.execute("SELECT id, user_id, total_amount FROM booking WHERE status = 'cancelled' LIMIT 100")
    cancelled_bookings = cursor.fetchall()
    
    refund_statuses = ['pending', 'approved', 'rejected', 'processed']
    refund_reasons = ['Train Cancelled', 'Medical Emergency', 'Change of Plans', 'Wrong Booking', 'Technical Issue']
    
    for booking_id, user_id, total_amount in cancelled_bookings[:50]:  # Create 50 refund requests
        tdr_number = generate_tdr_number()
        reason = random.choice(refund_reasons)
        cancellation_charges = total_amount * random.uniform(0.1, 0.3)  # 10-30% cancellation charges
        refund_amount = total_amount - cancellation_charges
        status = random.choice(refund_statuses)
        
        cursor.execute("""
            INSERT INTO refund_request (booking_id, user_id, refund_type, reason, amount_paid, 
                                      refund_amount, cancellation_charges, tdr_number, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (booking_id, user_id, 'cancellation', reason, total_amount, refund_amount, 
              cancellation_charges, tdr_number, status))
    
    # 19. Create notification preferences for all users
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
    
    # 20. Create chart preparation entries
    logger.info("📋 Creating chart preparation entries...")
    
    for i, train_id in enumerate(list(train_ids.values())[:20]):  # Charts for first 20 trains
        journey_date = date.today() + timedelta(days=random.randint(1, 7))
        
        for coach_class in ['AC1', 'AC2', 'AC3', 'SL']:
            cursor.execute("""
                INSERT INTO chart_preparation (train_id, journey_date, coach_class, status,
                                             confirmed_from_waitlist, total_passengers, prepared_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (train_id, journey_date, coach_class, 'prepared',
                  random.randint(0, 10), random.randint(50, 200), user_ids['admin']))
    
    # 21. Create tatkal override entries
    logger.info("⚡ Creating tatkal override entries...")
    
    for i in range(10):  # Create 10 tatkal overrides
        train_id = random.choice(list(train_ids.values()))
        journey_date = date.today() + timedelta(days=random.randint(1, 7))
        
        cursor.execute("""
            INSERT INTO tatkal_override (train_id, journey_date, override_reason, additional_quota,
                                       coach_classes, created_by, approved_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (train_id, journey_date, 'High Demand Route', random.randint(50, 100),
              'AC1,AC2,AC3', user_ids['admin'], user_ids['railway_admin']))
    
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
        result = cursor.fetchone()
        station_count = result[0] if result else 0
        
        cursor.execute("SELECT COUNT(*) FROM train")
        result = cursor.fetchone()
        train_count = result[0] if result else 0
        
        cursor.execute("SELECT COUNT(*) FROM booking")
        result = cursor.fetchone()
        booking_count = result[0] if result else 0
        
        cursor.execute("SELECT COUNT(*) FROM passenger")
        result = cursor.fetchone()
        passenger_count = result[0] if result else 0
        
        cursor.execute("SELECT COUNT(*) FROM waitlist")
        result = cursor.fetchone()
        waitlist_count = result[0] if result else 0
        
        cursor.execute("SELECT COUNT(*) FROM food_order")
        result = cursor.fetchone()
        food_order_count = result[0] if result else 0
        
        cursor.execute("SELECT COUNT(*) FROM loyalty_program")
        result = cursor.fetchone()
        loyalty_count = result[0] if result else 0
        
        cursor.close()
        conn.close()
        
        logger.info("✅ Database setup completed successfully!")
        logger.info(f"📊 Final Statistics:")
        logger.info(f"   🚉 Stations: {station_count}")
        logger.info(f"   🚂 Trains: {train_count}")
        logger.info(f"   🎫 Bookings: {booking_count}")
        logger.info(f"   👤 Passengers: {passenger_count}")
        logger.info(f"   ⏳ Waitlist Entries: {waitlist_count}")
        logger.info(f"   🍽️ Food Orders: {food_order_count}")
        logger.info(f"   🏆 Loyalty Members: {loyalty_count}")
        
        logger.info("\n🔑 Login Credentials:")
        logger.info("   Super Admin: admin / admin123")
        logger.info("   Railway Admin: railway_admin / railway123")
        logger.info("   Station Master: station_master / station123")
        logger.info("   Test User: testuser / user123")
        
        logger.info("\n🌐 Features Available:")
        logger.info("   ✓ Complete booking system with seat allocation")
        logger.info("   ✓ Waitlist management with positions")
        logger.info("   ✓ Food ordering system with restaurants & menus")
        logger.info("   ✓ Group bookings for families & corporate")
        logger.info("   ✓ Tatkal booking system with time slots")
        logger.info("   ✓ Loyalty programs with tiers and benefits")
        logger.info("   ✓ Real-time train status tracking")
        logger.info("   ✓ Comprehensive refund & TDR management")
        logger.info("   ✓ Multi-class coaches and seat allocation")
        logger.info("   ✓ Route management with stations")
        logger.info("   ✓ Payment processing with multiple gateways")
        logger.info("   ✓ Chart preparation and seat confirmation")
        logger.info("   ✓ Emergency quota and overrides")
        logger.info("   ✓ Comprehensive admin dashboard")
        logger.info("   ✓ User notification preferences")
        logger.info("   ✓ 1500+ railway stations across India")
        logger.info("   ✓ 1000+ trains with realistic schedules")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        conn.close()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)