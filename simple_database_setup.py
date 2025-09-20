#!/usr/bin/env python3
"""
Simple Railway Database Setup - Guaranteed to Work
==================================================
"""

import os
import random
import logging
from datetime import datetime, date, timedelta

import psycopg2
from werkzeug.security import generate_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def setup_simple_data():
    """Setup a smaller but comprehensive dataset that's guaranteed to work"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        # Clear all data first
        logger.info("🧹 Clearing existing data...")
        cursor.execute("TRUNCATE TABLE station, train, \"user\" RESTART IDENTITY CASCADE;")
        
        # Insert sample users
        logger.info("👥 Creating sample users...")
        users_data = [
            ('admin', 'admin@railserve.com', 'admin123', 'admin'),
            ('john_doe', 'john@example.com', 'password123', 'user'),
            ('jane_smith', 'jane@example.com', 'password123', 'user'),
        ]
        
        user_ids = {}
        for username, email, password, role in users_data:
            password_hash = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO "user" (username, email, password_hash, role, phone, 
                                  date_of_birth, gender, address, city, state, pincode)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, (username, email, password_hash, role, f"98765{random.randint(10000, 99999)}",
                  date(1990, 1, 1), 'Male', '123 Sample St', 'Mumbai', 'Maharashtra', '400001'))
            user_ids[username] = cursor.fetchone()[0]
        
        # Insert major stations
        logger.info("🚉 Creating major railway stations...")
        stations_data = [
            ('New Delhi Railway Station', 'NDLS', 'Delhi', 'Delhi', 'NR', 'Delhi'),
            ('Mumbai Central', 'MMCT', 'Mumbai', 'Maharashtra', 'WR', 'Mumbai'),
            ('Chennai Central', 'MAS', 'Chennai', 'Tamil Nadu', 'SR', 'Chennai'),
            ('Howrah Junction', 'HWH', 'Kolkata', 'West Bengal', 'ER', 'Kolkata'),
            ('Bangalore City', 'SBC', 'Bangalore', 'Karnataka', 'SWR', 'Bangalore'),
            ('Hyderabad Deccan', 'HYB', 'Hyderabad', 'Telangana', 'SCR', 'Hyderabad'),
            ('Pune Junction', 'PUNE', 'Pune', 'Maharashtra', 'CR', 'Pune'),
            ('Jaipur Junction', 'JP', 'Jaipur', 'Rajasthan', 'NWR', 'Jaipur'),
            ('Lucknow Charbagh', 'LKO', 'Lucknow', 'Uttar Pradesh', 'NER', 'Lucknow'),
            ('Ahmedabad Junction', 'ADI', 'Ahmedabad', 'Gujarat', 'WR', 'Ahmedabad'),
        ]
        
        station_ids = {}
        for name, code, city, state, zone, division in stations_data:
            cursor.execute("""
                INSERT INTO station (name, code, city, state, zone, division, 
                                   latitude, longitude, platforms, electric_traction, facilities)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, (name, code, city, state, zone, division,
                  round(random.uniform(8.0, 37.0), 6),
                  round(random.uniform(68.0, 97.0), 6),
                  random.randint(6, 16),
                  True,
                  'Waiting Room, Food Court, WiFi, Parking, ATM'))
            station_ids[code] = cursor.fetchone()[0]
        
        # Insert popular trains
        logger.info("🚂 Creating popular trains...")
        trains_data = [
            ('12951', 'Mumbai Rajdhani Express', 'Rajdhani', 378, 350, 2.50, 30, 4.00, 130, True, True, True),
            ('12302', 'Kolkata Rajdhani Express', 'Rajdhani', 378, 340, 2.50, 30, 4.00, 130, True, True, True),
            ('12001', 'Shatabdi Express', 'Shatabdi', 522, 500, 1.80, 50, 2.70, 160, True, True, True),
            ('12009', 'Shatabdi Express', 'Shatabdi', 522, 480, 1.80, 50, 2.70, 160, True, True, True),
            ('16031', 'Andaman Express', 'Express', 1200, 1100, 1.20, 100, 1.80, 100, True, False, True),
            ('22691', 'Rajdhani Express', 'Rajdhani', 378, 360, 2.50, 30, 4.00, 130, True, True, True),
            ('12280', 'Taj Express', 'Express', 800, 750, 1.50, 80, 2.25, 110, True, False, True),
            ('12002', 'Bhopal Shatabdi', 'Shatabdi', 522, 490, 1.80, 50, 2.70, 160, True, True, True),
            ('22470', 'Bikaner Express', 'Express', 1000, 920, 1.30, 100, 1.95, 90, False, False, True),
            ('12012', 'Kalka Shatabdi', 'Shatabdi', 522, 510, 1.80, 50, 2.70, 160, True, True, True),
        ]
        
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
            train_ids[number] = cursor.fetchone()[0]
        
        # Create some sample bookings
        logger.info("📋 Creating sample bookings...")
        station_codes = list(station_ids.keys())
        train_numbers = list(train_ids.keys())
        
        for i in range(20):
            source_code = random.choice(station_codes)
            dest_code = random.choice([s for s in station_codes if s != source_code])
            train_number = random.choice(train_numbers)
            user_id = random.choice(list(user_ids.values()))
            
            journey_date = date.today() + timedelta(days=random.randint(1, 30))
            booking_date = datetime.now() - timedelta(days=random.randint(0, 10))
            
            cursor.execute("""
                INSERT INTO booking (user_id, train_id, source_station_id, destination_station_id,
                                   journey_date, booking_date, status, total_fare, booking_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, (user_id, train_ids[train_number], station_ids[source_code], station_ids[dest_code],
                  journey_date, booking_date, 
                  random.choice(['confirmed', 'waitlisted', 'cancelled']),
                  random.randint(500, 5000),
                  random.choice(['general', 'tatkal', 'premium'])))
        
        conn.commit()
        logger.info("✅ Simple database setup completed successfully!")
        
        # Print summary
        cursor.execute("SELECT COUNT(*) FROM station")
        station_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM train")
        train_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM booking")
        booking_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM \"user\"")
        user_count = cursor.fetchone()[0]
        
        logger.info(f"📊 Database Summary:")
        logger.info(f"   - Stations: {station_count}")
        logger.info(f"   - Trains: {train_count}")
        logger.info(f"   - Bookings: {booking_count}")
        logger.info(f"   - Users: {user_count}")
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    setup_simple_data()