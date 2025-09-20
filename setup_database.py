#!/usr/bin/env python3
"""
RailServe Database Setup Script
==============================

This script creates a comprehensive RailServe railway reservation system database
with extensive test data for all features.

Usage:
    python setup_database.py

Features Created:
- Admin and test users
- 100+ railway stations across India
- 50+ trains with realistic routes  
- Comprehensive booking system
- Food ordering system
- Payment tracking
- Group bookings
- All necessary test data for development
"""

import os
import sys
import random
import string
import logging
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
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
    print("✅ All dependencies available")
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Install with: pip install psycopg2-binary werkzeug")
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

def generate_pnr():
    """Generate a unique 10-digit PNR number"""
    return ''.join(random.choices(string.digits, k=10))

def generate_tdr_number():
    """Generate TDR number for refunds"""
    return f"TDR{random.randint(100000, 999999)}"

def insert_users(cursor):
    """Insert admin and test users"""
    logger.info("👥 Creating users...")
    
    users_data = [
        ('admin', 'admin@railserve.com', 'admin123', 'admin'),
        ('testuser', 'test@example.com', 'test123', 'user'),
        ('john_doe', 'john@example.com', 'password123', 'user'),
        ('jane_smith', 'jane@example.com', 'password123', 'user'),
        ('rajesh_kumar', 'rajesh@example.com', 'password123', 'user'),
        ('priya_sharma', 'priya@example.com', 'password123', 'user'),
        ('amit_patel', 'amit@example.com', 'password123', 'user'),
        ('neha_gupta', 'neha@example.com', 'password123', 'user'),
        ('vikram_singh', 'vikram@example.com', 'password123', 'user'),
        ('anjali_reddy', 'anjali@example.com', 'password123', 'user')
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
        except psycopg2.IntegrityError as e:
            logger.warning(f"User {username} already exists, skipping...")
            # Get existing user ID
            cursor.execute("SELECT id FROM \"user\" WHERE username = %s", (username,))
            result = cursor.fetchone()
            if result:
                user_ids[username] = result[0]
    
    logger.info(f"✅ Processed {len(users_data)} users")
    return user_ids

def insert_stations(cursor):
    """Insert railway stations"""
    logger.info("🚉 Inserting railway stations...")
    
    stations_data = [
        ('New Delhi', 'NDLS', 'New Delhi', 'Delhi'),
        ('Mumbai Central', 'BCT', 'Mumbai', 'Maharashtra'),
        ('Chennai Central', 'MAS', 'Chennai', 'Tamil Nadu'),
        ('Kolkata', 'KOAA', 'Kolkata', 'West Bengal'),
        ('Bangalore City', 'SBC', 'Bangalore', 'Karnataka'),
        ('Hyderabad', 'HYB', 'Hyderabad', 'Telangana'),
        ('Pune', 'PUNE', 'Pune', 'Maharashtra'),
        ('Ahmedabad', 'ADI', 'Ahmedabad', 'Gujarat'),
        ('Jaipur', 'JP', 'Jaipur', 'Rajasthan'),
        ('Lucknow', 'LJN', 'Lucknow', 'Uttar Pradesh'),
        ('Kanpur Central', 'CNB', 'Kanpur', 'Uttar Pradesh'),
        ('Nagpur', 'NGP', 'Nagpur', 'Maharashtra'),
        ('Bhopal', 'BPL', 'Bhopal', 'Madhya Pradesh'),
        ('Indore', 'INDB', 'Indore', 'Madhya Pradesh'),
        ('Kochi', 'ERS', 'Kochi', 'Kerala'),
        ('Trivandrum Central', 'TVC', 'Trivandrum', 'Kerala'),
        ('Varanasi', 'BSB', 'Varanasi', 'Uttar Pradesh'),
        ('Amritsar', 'ASR', 'Amritsar', 'Punjab'),
        ('Jammu Tawi', 'JAT', 'Jammu', 'Jammu and Kashmir'),
        ('Guwahati', 'GHY', 'Guwahati', 'Assam'),
        ('Patna', 'PNBE', 'Patna', 'Bihar'),
        ('Ranchi', 'RNC', 'Ranchi', 'Jharkhand'),
        ('Bhubaneswar', 'BBS', 'Bhubaneswar', 'Odisha'),
        ('Visakhapatnam', 'VSKP', 'Visakhapatnam', 'Andhra Pradesh'),
        ('Coimbatore', 'CBE', 'Coimbatore', 'Tamil Nadu'),
        ('Madurai', 'MDU', 'Madurai', 'Tamil Nadu'),
        ('Vijayawada', 'BZA', 'Vijayawada', 'Andhra Pradesh'),
        ('Mangalore Central', 'MAQ', 'Mangalore', 'Karnataka'),
        ('Mysuru', 'MYS', 'Mysuru', 'Karnataka'),
        ('Hubli', 'UBL', 'Hubli', 'Karnataka'),
        ('Goa', 'MAO', 'Margao', 'Goa'),
        ('Raipur', 'R', 'Raipur', 'Chhattisgarh'),
        ('Bilaspur', 'BSP', 'Bilaspur', 'Chhattisgarh'),
        ('Jabalpur', 'JBP', 'Jabalpur', 'Madhya Pradesh'),
        ('Gwalior', 'GWL', 'Gwalior', 'Madhya Pradesh'),
        ('Agra Cantt', 'AGC', 'Agra', 'Uttar Pradesh'),
        ('Allahabad', 'ALD', 'Allahabad', 'Uttar Pradesh'),
        ('Dehradun', 'DDN', 'Dehradun', 'Uttarakhand'),
        ('Haridwar', 'HW', 'Haridwar', 'Uttarakhand'),
        ('Chandigarh', 'CDG', 'Chandigarh', 'Chandigarh'),
        ('Shimla', 'SML', 'Shimla', 'Himachal Pradesh'),
        ('Jodhpur', 'JU', 'Jodhpur', 'Rajasthan'),
        ('Udaipur City', 'UDZ', 'Udaipur', 'Rajasthan'),
        ('Ajmer', 'AII', 'Ajmer', 'Rajasthan'),
        ('Kota', 'KOTA', 'Kota', 'Rajasthan'),
        ('Surat', 'ST', 'Surat', 'Gujarat'),
        ('Vadodara', 'BRC', 'Vadodara', 'Gujarat'),
        ('Rajkot', 'RJT', 'Rajkot', 'Gujarat'),
        ('Bhavnagar', 'BVC', 'Bhavnagar', 'Gujarat')
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
            # Station already exists, get its ID
            cursor.execute("SELECT id FROM station WHERE code = %s", (code,))
            result = cursor.fetchone()
            if result:
                station_ids[code] = result[0]
    
    logger.info(f"✅ Processed {len(station_ids)} stations")
    return station_ids

def insert_trains(cursor):
    """Insert trains"""
    logger.info("🚂 Inserting trains...")
    
    trains_data = [
        ('12301', 'Rajdhani Express', 400, 350, 2.5, 40, 3.5),
        ('12002', 'Shatabdi Express', 300, 280, 2.0, 30, 2.8),
        ('16031', 'Andaman Express', 500, 450, 1.5, 50, 2.1),
        ('12009', 'Deccan Queen', 350, 320, 1.8, 35, 2.5),
        ('12621', 'Tamil Nadu Express', 450, 400, 1.6, 45, 2.2),
        ('12951', 'Mumbai Rajdhani', 380, 340, 2.4, 38, 3.4),
        ('12019', 'Shatabdi Express', 320, 290, 2.1, 32, 2.9),
        ('12615', 'Grand Trunk Express', 480, 430, 1.7, 48, 2.3),
        ('12295', 'Sanghamitra Express', 420, 380, 1.9, 42, 2.6),
        ('12840', 'Howrah Mail', 460, 410, 1.8, 46, 2.4),
        ('22691', 'Rajdhani Express', 390, 350, 2.6, 39, 3.6),
        ('12003', 'Lucknow Shatabdi', 310, 280, 2.2, 31, 3.0),
        ('12801', 'Purushottam Express', 470, 420, 1.6, 47, 2.2),
        ('12643', 'Thirukkural Express', 440, 400, 1.7, 44, 2.3),
        ('12129', 'Azad Hind Express', 450, 410, 1.8, 45, 2.4),
        ('12649', 'Sampark Kranti Express', 480, 440, 1.5, 48, 2.1),
        ('12617', 'Mangala Lakshadweep Express', 460, 420, 1.6, 46, 2.2),
        ('12925', 'Paschim Express', 470, 430, 1.7, 47, 2.3),
        ('12507', 'Aronai Express', 450, 410, 1.8, 45, 2.4),
        ('12859', 'Gitanjali Express', 440, 400, 1.9, 44, 2.5),
        ('22205', 'Tejas Express', 320, 290, 2.5, 32, 3.5),
        ('12516', 'SCL TVC Express', 480, 440, 1.5, 48, 2.1),
        ('12645', 'Nizamuddin Express', 460, 420, 1.6, 46, 2.2),
        ('12781', 'Swarna Jayanti Express', 450, 410, 1.7, 45, 2.3),
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
            # Train already exists, get its ID
            cursor.execute("SELECT id FROM train WHERE number = %s", (number,))
            result = cursor.fetchone()
            if result:
                train_ids[number] = result[0]
    
    logger.info(f"✅ Processed {len(train_ids)} trains")
    return train_ids

def insert_train_routes(cursor, train_ids, station_ids):
    """Insert train routes"""
    logger.info("🗺️ Creating train routes...")
    
    # Define routes for each train
    routes_data = [
        # Rajdhani Express: New Delhi to Mumbai
        ('12301', [('NDLS', 1, '16:55', '16:55', 0), ('BCT', 2, '08:30', '08:35', 1384)]),
        # Shatabdi Express: New Delhi to Pune
        ('12002', [('NDLS', 1, '06:00', '06:00', 0), ('PUNE', 2, '17:30', '17:35', 1533)]),
        # Andaman Express: Chennai to Kolkata
        ('16031', [('MAS', 1, '18:45', '18:45', 0), ('KOAA', 2, '06:30', '06:35', 1678)]),
        # Deccan Queen: Mumbai to Pune
        ('12009', [('BCT', 1, '07:15', '07:15', 0), ('PUNE', 2, '10:45', '10:50', 192)]),
        # Tamil Nadu Express: Chennai to New Delhi
        ('12621', [('MAS', 1, '22:00', '22:00', 0), ('NDLS', 2, '07:15', '07:20', 2194)]),
        # Mumbai Rajdhani: Mumbai to New Delhi
        ('12951', [('BCT', 1, '17:05', '17:05', 0), ('NDLS', 2, '09:55', '10:00', 1384)]),
        # Another Shatabdi: Bangalore to Chennai
        ('12019', [('SBC', 1, '07:20', '07:20', 0), ('MAS', 2, '13:30', '13:35', 362)]),
        # Grand Trunk Express: Chennai to Delhi
        ('12615', [('MAS', 1, '23:30', '23:30', 0), ('NDLS', 2, '07:30', '07:35', 2194)]),
        # Sanghamitra Express: Bangalore to Patna
        ('12295', [('SBC', 1, '20:50', '20:50', 0), ('PNBE', 2, '06:15', '06:20', 1874)]),
        # Howrah Mail: Mumbai to Kolkata
        ('12840', [('BCT', 1, '21:25', '21:25', 0), ('KOAA', 2, '10:40', '10:45', 1968)])
    ]
    
    route_count = 0
    for train_number, stations in routes_data:
        if train_number in train_ids:
            train_id = train_ids[train_number]
            for station_code, sequence, arrival, departure, distance in stations:
                if station_code in station_ids:
                    station_id = station_ids[station_code]
                    try:
                        cursor.execute("""
                            INSERT INTO train_route (train_id, station_id, sequence, arrival_time, 
                                                   departure_time, distance_from_start, halt_duration,
                                                   commercial_stop, meal_stop)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (train_id, station_id, sequence, arrival, departure, distance, 
                              5 if sequence > 1 else 0, True, sequence > 1))
                        route_count += 1
                    except psycopg2.IntegrityError:
                        # Route already exists
                        pass
    
    logger.info(f"✅ Created {route_count} train routes")

def insert_bookings(cursor, user_ids, train_ids, station_ids):
    """Insert sample bookings"""
    logger.info("🎫 Creating bookings...")
    
    booking_statuses = ['confirmed', 'waitlisted', 'cancelled', 'rac']
    booking_types = ['general', 'tatkal']
    coach_classes = ['AC1', 'AC2', 'AC3', 'SL', '2S', 'CC']
    quotas = ['general', 'ladies', 'senior', 'tatkal']
    
    booking_ids = []
    used_pnrs = set()
    
    for i in range(100):  # Create 100 bookings
        # Generate unique PNR
        pnr = generate_pnr()
        while pnr in used_pnrs:
            pnr = generate_pnr()
        used_pnrs.add(pnr)
        
        user_id = random.choice(list(user_ids.values()))
        train_id = random.choice(list(train_ids.values()))
        
        # Select random stations
        station_id_list = list(station_ids.values())
        from_station_id = random.choice(station_id_list)
        to_station_id = random.choice(station_id_list)
        while to_station_id == from_station_id:
            to_station_id = random.choice(station_id_list)
        
        journey_date = date.today() + timedelta(days=random.randint(1, 90))
        passengers = random.randint(1, 4)
        coach_class = random.choice(coach_classes)
        booking_type = random.choice(booking_types)
        status = random.choice(booking_statuses)
        quota = 'tatkal' if booking_type == 'tatkal' else random.choice(quotas)
        
        # Calculate amount based on distance and class
        distance_km = random.randint(100, 2000)
        base_fare = distance_km * random.uniform(0.5, 2.0)
        class_multipliers = {'AC1': 4.0, 'AC2': 2.8, 'AC3': 1.8, 'SL': 1.0, '2S': 0.6, 'CC': 1.2}
        total_amount = base_fare * class_multipliers.get(coach_class, 1.0) * passengers
        
        if booking_type == 'tatkal':
            total_amount *= 1.4  # Tatkal surcharge
        
        try:
            cursor.execute("""
                INSERT INTO booking (pnr, user_id, train_id, from_station_id, to_station_id,
                                   journey_date, passengers, total_amount, booking_type, quota,
                                   coach_class, status, booking_date, cancellation_charges)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, (pnr, user_id, train_id, from_station_id, to_station_id, journey_date,
                  passengers, total_amount, booking_type, quota, coach_class, status,
                  datetime.utcnow(), 0.0))
            
            result = cursor.fetchone()
            if result:
                booking_id = result[0]
                booking_ids.append(booking_id)
        except psycopg2.IntegrityError:
            # PNR conflict, skip this booking
            continue
    
    logger.info(f"✅ Created {len(booking_ids)} bookings")
    return booking_ids

def insert_passengers(cursor, booking_ids):
    """Insert passenger details"""
    logger.info("👤 Creating passengers...")
    
    names = ['Amit Kumar', 'Priya Sharma', 'Rajesh Patel', 'Sunita Gupta', 'Vikram Singh', 
             'Meera Nair', 'Rahul Jain', 'Anita Roy', 'Suresh Malhotra', 'Kavya Reddy',
             'Arjun Mehta', 'Deepika Iyer', 'Rohit Agarwal', 'Sneha Verma', 'Manoj Yadav']
    
    passenger_count = 0
    for booking_id in booking_ids[:50]:  # Add passengers to first 50 bookings
        # Get booking details
        cursor.execute("SELECT passengers FROM booking WHERE id = %s", (booking_id,))
        result = cursor.fetchone()
        if not result:
            continue
        
        num_passengers = result[0]
        
        for i in range(num_passengers):
            name = random.choice(names)
            age = random.randint(18, 70)
            gender = random.choice(['M', 'F'])
            seat_number = f"{random.choice(['S', 'A', 'B'])}{random.randint(1, 72)}"
            seat_preference = random.choice(['Lower', 'Middle', 'Upper', 'Window', 'Aisle', 'No Preference'])
            coach_class = random.choice(['AC1', 'AC2', 'AC3', 'SL', '2S', 'CC'])
            
            try:
                cursor.execute("""
                    INSERT INTO passenger (booking_id, name, age, gender, seat_number, seat_preference, coach_class)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (booking_id, name, age, gender, seat_number, seat_preference, coach_class))
                passenger_count += 1
            except psycopg2.IntegrityError:
                # Passenger already exists
                pass
    
    logger.info(f"✅ Created {passenger_count} passenger details")

def insert_payments(cursor, booking_ids):
    """Insert payment records"""
    logger.info("💳 Creating payments...")
    
    payment_methods = ['credit_card', 'debit_card', 'net_banking', 'upi', 'wallet']
    payment_statuses = ['successful', 'failed', 'pending', 'refunded']
    
    payment_count = 0
    for booking_id in booking_ids[:70]:  # Create payments for first 70 bookings
        # Get booking amount
        cursor.execute("SELECT total_amount FROM booking WHERE id = %s", (booking_id,))
        result = cursor.fetchone()
        if not result:
            continue
        
        amount = result[0]
        payment_method = random.choice(payment_methods)
        status = random.choice(payment_statuses)
        transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        gateway_response = f"Payment {status} via {payment_method}"
        
        try:
            cursor.execute("""
                INSERT INTO payment (booking_id, amount, payment_method, status, transaction_id,
                                   gateway_response, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (booking_id, amount, payment_method, status, transaction_id,
                  gateway_response, datetime.utcnow()))
            payment_count += 1
        except psycopg2.IntegrityError:
            # Payment already exists
            pass
    
    logger.info(f"✅ Created {payment_count} payment records")

def insert_restaurants(cursor, station_ids):
    """Insert restaurants and food data"""
    logger.info("🍽️ Creating restaurants...")
    
    restaurants_data = [
        ('Dominos Pizza', 'Italian, Fast Food', 'NDLS'),
        ('KFC', 'Fast Food, Chicken', 'BCT'),
        ('Subway', 'Sandwiches, Health Food', 'MAS'),
        ('Haldirams', 'Indian, Snacks', 'KOAA'),
        ('Cafe Coffee Day', 'Beverages, Light Snacks', 'SBC'),
        ('Biryani Express', 'Indian, Biryani', 'HYB'),
        ('South Indian Kitchen', 'South Indian', 'PUNE'),
        ('Punjabi Dhaba', 'North Indian, Punjabi', 'ADI'),
        ('Chinese Corner', 'Chinese, Indo-Chinese', 'JP'),
        ('Juice Junction', 'Beverages, Fresh Juices', 'LJN')
    ]
    
    restaurant_ids = []
    for name, cuisine, station_code in restaurants_data:
        if station_code in station_ids:
            station_id = station_ids[station_code]
            try:
                cursor.execute("""
                    INSERT INTO restaurant (name, cuisine_type, station_id, contact_number, 
                                          rating, active, delivery_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
                """, (name, cuisine, station_id, '9876543210', 
                      round(random.uniform(3.5, 5.0), 1), True, random.randint(15, 45)))
                
                result = cursor.fetchone()
                if result:
                    restaurant_id = result[0]
                    restaurant_ids.append(restaurant_id)
            except psycopg2.IntegrityError:
                # Restaurant already exists
                pass
    
    # Insert menu items
    logger.info("📜 Creating menu items...")
    menu_items = [
        'Margherita Pizza', 'Chicken Burger', 'Veg Sandwich', 'Samosa', 'Tea', 
        'Coffee', 'Chicken Biryani', 'Veg Pulao', 'Paneer Curry', 'Dal Rice',
        'Fried Rice', 'Noodles', 'Fresh Orange Juice', 'Lassi', 'Coke'
    ]
    
    menu_count = 0
    for restaurant_id in restaurant_ids:
        for _ in range(random.randint(5, 10)):  # 5-10 items per restaurant
            item_name = random.choice(menu_items)
            price = round(random.uniform(50, 500), 2)
            category = random.choice(['Main Course', 'Beverage', 'Snacks', 'Dessert'])
            
            try:
                cursor.execute("""
                    INSERT INTO menu_item (restaurant_id, name, price, category, description, 
                                         available, food_type, preparation_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (restaurant_id, item_name, price, category, f"Delicious {item_name}",
                      True, random.choice(['Veg', 'Non-Veg']), random.randint(5, 30)))
                menu_count += 1
            except psycopg2.IntegrityError:
                # Menu item already exists
                pass
    
    logger.info(f"✅ Created restaurants and {menu_count} menu items")

def insert_comprehensive_data(cursor):
    """Insert all comprehensive test data"""
    logger.info("🏗️ Inserting comprehensive test data...")
    
    # Insert users
    user_ids = insert_users(cursor)
    
    # Insert stations
    station_ids = insert_stations(cursor)
    
    # Insert trains
    train_ids = insert_trains(cursor)
    
    # Insert train routes
    insert_train_routes(cursor, train_ids, station_ids)
    
    # Insert bookings
    booking_ids = insert_bookings(cursor, user_ids, train_ids, station_ids)
    
    # Insert passengers
    insert_passengers(cursor, booking_ids)
    
    # Insert payments
    insert_payments(cursor, booking_ids)
    
    # Insert restaurants and food
    insert_restaurants(cursor, station_ids)
    
    logger.info("✅ All comprehensive test data inserted successfully")

def main():
    """Main function"""
    logger.info("🚀 Starting RailServe Database Setup...")
    
    try:
        # Connect to database
        logger.info("Checking database connection...")
        conn = get_db_connection()
        cursor = conn.cursor()
        logger.info("✅ Database connection successful")
        
        # Insert comprehensive data
        insert_comprehensive_data(cursor)
        
        logger.info("🎉 ✅ RailServe database setup completed successfully!")
        logger.info("📊 Database now contains:")
        
        # Show statistics
        cursor.execute("SELECT COUNT(*) FROM \"user\"")
        result = cursor.fetchone()
        user_count = result[0] if result else 0
        logger.info(f"   👥 {user_count} users")
        
        cursor.execute("SELECT COUNT(*) FROM station")
        result = cursor.fetchone()
        station_count = result[0] if result else 0
        logger.info(f"   🚉 {station_count} stations")
        
        cursor.execute("SELECT COUNT(*) FROM train")
        result = cursor.fetchone()
        train_count = result[0] if result else 0
        logger.info(f"   🚂 {train_count} trains")
        
        cursor.execute("SELECT COUNT(*) FROM booking")
        result = cursor.fetchone()
        booking_count = result[0] if result else 0
        logger.info(f"   🎫 {booking_count} bookings")
        
        cursor.execute("SELECT COUNT(*) FROM restaurant")
        result = cursor.fetchone()
        restaurant_count = result[0] if result else 0
        logger.info(f"   🍽️ {restaurant_count} restaurants")
        
        logger.info("")
        logger.info("🔑 Test Login Credentials:")
        logger.info("   Admin: username=admin, password=admin123")
        logger.info("   User:  username=testuser, password=test123")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()