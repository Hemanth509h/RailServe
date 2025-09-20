#!/usr/bin/env python3
"""
RailServe Comprehensive Test Data Generator
==========================================

This script generates massive amounts of test data for the RailServe system:
- 1250 railway stations across India
- 1500 trains with realistic routes
- Comprehensive test data for all features including waiting lists

Usage:
    python generate_comprehensive_data.py
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

# Database connection
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    logger.error("❌ DATABASE_URL environment variable is required")
    sys.exit(1)

try:
    import psycopg2
    from werkzeug.security import generate_password_hash
    logger.info("✅ All dependencies available")
except ImportError as e:
    logger.error(f"❌ Missing dependencies: {e}")
    sys.exit(1)

# Indian states and major cities for realistic station generation
INDIAN_STATES = {
    'Andhra Pradesh': ['Visakhapatnam', 'Vijayawada', 'Guntur', 'Nellore', 'Kurnool', 'Kakinada', 'Rajahmundry', 'Tirupati', 'Anantapur', 'Kadapa'],
    'Assam': ['Guwahati', 'Silchar', 'Dibrugarh', 'Jorhat', 'Tinsukia', 'Nagaon', 'Tezpur', 'Karimganj', 'Dhubri', 'Bongaigaon'],
    'Bihar': ['Patna', 'Gaya', 'Bhagalpur', 'Muzaffarpur', 'Purnia', 'Darbhanga', 'Bihar Sharif', 'Arrah', 'Begusarai', 'Katihar'],
    'Chhattisgarh': ['Raipur', 'Bhilai', 'Korba', 'Bilaspur', 'Durg', 'Rajnandgaon', 'Jagdalpur', 'Raigarh', 'Ambikapur', 'Mahasamund'],
    'Gujarat': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Bhavnagar', 'Jamnagar', 'Junagadh', 'Gandhinagar', 'Anand', 'Mehsana'],
    'Haryana': ['Faridabad', 'Gurgaon', 'Panipat', 'Ambala', 'Yamunanagar', 'Rohtak', 'Hisar', 'Karnal', 'Sonipat', 'Panchkula'],
    'Himachal Pradesh': ['Shimla', 'Mandi', 'Solan', 'Dharamshala', 'Una', 'Kullu', 'Hamirpur', 'Bilaspur', 'Chamba', 'Kangra'],
    'Jharkhand': ['Ranchi', 'Jamshedpur', 'Dhanbad', 'Bokaro', 'Deoghar', 'Phusro', 'Hazaribagh', 'Giridih', 'Ramgarh', 'Medininagar'],
    'Karnataka': ['Bangalore', 'Mysore', 'Hubli', 'Mangalore', 'Belgaum', 'Davangere', 'Bellary', 'Bijapur', 'Shimoga', 'Tumkur'],
    'Kerala': ['Thiruvananthapuram', 'Kochi', 'Kozhikode', 'Thrissur', 'Kollam', 'Palakkad', 'Alappuzha', 'Malappuram', 'Kannur', 'Kasaragod'],
    'Madhya Pradesh': ['Bhopal', 'Indore', 'Gwalior', 'Jabalpur', 'Ujjain', 'Sagar', 'Dewas', 'Satna', 'Ratlam', 'Rewa'],
    'Maharashtra': ['Mumbai', 'Pune', 'Nagpur', 'Thane', 'Nashik', 'Kolhapur', 'Aurangabad', 'Nanded', 'Solapur', 'Jalgaon'],
    'Odisha': ['Bhubaneswar', 'Cuttack', 'Rourkela', 'Berhampur', 'Sambalpur', 'Puri', 'Balasore', 'Bhadrak', 'Baripada', 'Jharsuguda'],
    'Punjab': ['Ludhiana', 'Amritsar', 'Jalandhar', 'Patiala', 'Bathinda', 'Mohali', 'Firozpur', 'Batala', 'Pathankot', 'Moga'],
    'Rajasthan': ['Jaipur', 'Jodhpur', 'Kota', 'Bikaner', 'Ajmer', 'Udaipur', 'Bhilwara', 'Alwar', 'Bharatpur', 'Sikar'],
    'Tamil Nadu': ['Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem', 'Tirunelveli', 'Tiruppur', 'Vellore', 'Erode', 'Thoothukkudi'],
    'Telangana': ['Hyderabad', 'Warangal', 'Nizamabad', 'Khammam', 'Karimnagar', 'Ramagundam', 'Mahbubnagar', 'Nalgonda', 'Adilabad', 'Suryapet'],
    'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Ghaziabad', 'Agra', 'Varanasi', 'Meerut', 'Allahabad', 'Bareilly', 'Aligarh', 'Moradabad'],
    'West Bengal': ['Kolkata', 'Howrah', 'Durgapur', 'Asansol', 'Siliguri', 'Bardhaman', 'Malda', 'Baharampur', 'Habra', 'Kharagpur'],
    'Delhi': ['New Delhi', 'Old Delhi', 'Dwarka', 'Rohini', 'Janakpuri', 'Laxmi Nagar', 'Karol Bagh', 'Connaught Place', 'Saket', 'Vasant Kunj'],
    'Goa': ['Panaji', 'Vasco da Gama', 'Margao', 'Mapusa', 'Ponda', 'Bicholim', 'Curchorem', 'Sanquelim', 'Valpoi', 'Quepem']
}

# Train name prefixes and suffixes
TRAIN_PREFIXES = ['Rajdhani', 'Shatabdi', 'Duronto', 'Garib Rath', 'Jan Shatabdi', 'Intercity', 'Express', 'Mail', 'Passenger', 'Super Fast']
TRAIN_SUFFIXES = ['Express', 'Mail', 'Special', 'Link Express', 'Passenger', 'Fast Passenger', 'Jan Shatabdi', 'Intercity Express']

# Coach classes and their details
COACH_CLASSES = {
    'AC1': {'name': 'AC First Class', 'fare_multiplier': 4.0, 'seats_per_coach': 18},
    'AC2': {'name': 'AC 2 Tier', 'fare_multiplier': 2.5, 'seats_per_coach': 46},
    'AC3': {'name': 'AC 3 Tier', 'fare_multiplier': 1.8, 'seats_per_coach': 64},
    'SL': {'name': 'Sleeper', 'fare_multiplier': 1.0, 'seats_per_coach': 72},
    '2S': {'name': 'Second Sitting', 'fare_multiplier': 0.6, 'seats_per_coach': 104},
    'CC': {'name': 'Chair Car', 'fare_multiplier': 1.2, 'seats_per_coach': 78}
}

def generate_pnr():
    """Generate a realistic PNR number"""
    return ''.join(random.choices(string.digits, k=10))

def generate_train_number():
    """Generate a realistic train number"""
    return ''.join(random.choices(string.digits, k=5))

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(DATABASE_URL)

def create_stations(num_stations=1250):
    """Create comprehensive railway stations"""
    logger.info(f"🚉 Creating {num_stations} railway stations...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    stations_created = 0
    
    # Get existing stations to avoid duplicates
    cursor.execute("SELECT name FROM station")
    existing_stations = {row[0] for row in cursor.fetchall()}
    
    for state, cities in INDIAN_STATES.items():
        for city in cities:
            if stations_created >= num_stations:
                break
                
            # Create multiple stations per major city
            station_types = ['Junction', 'Central', 'Railway Station', 'Terminus', 'City']
            
            for station_type in station_types:
                if stations_created >= num_stations:
                    break
                    
                station_name = f"{city} {station_type}"
                if station_name in existing_stations:
                    continue
                    
                # Generate unique station code
                attempts = 0
                while attempts < 10:
                    if station_type == 'Junction':
                        code = f"{city[:3].upper()}J"
                    elif station_type == 'Central':
                        code = f"{city[:3].upper()}C"
                    elif station_type == 'Terminus':
                        code = f"{city[:3].upper()}T"
                    else:
                        code = f"{city[:2].upper()}{random.choice(string.ascii_uppercase)}{random.choice(string.digits)}"
                    
                    # Check if code exists
                    cursor.execute("SELECT id FROM station WHERE code = %s", (code,))
                    if not cursor.fetchone():
                        break
                    attempts += 1
                else:
                    # Generate completely random code if all attempts failed
                    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                
                try:
                    cursor.execute("""
                        INSERT INTO station (name, code, city, state, active, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (name) DO NOTHING
                    """, (station_name, code, city, state, True, datetime.utcnow()))
                    
                    if cursor.rowcount > 0:
                        stations_created += 1
                        existing_stations.add(station_name)
                        
                except psycopg2.IntegrityError:
                    conn.rollback()
                    continue
                    
        if stations_created >= num_stations:
            break
    
    # If we still need more stations, create smaller towns/villages
    remaining = num_stations - stations_created
    if remaining > 0:
        logger.info(f"Creating {remaining} additional smaller stations...")
        
        for i in range(remaining):
            # Generate smaller town names
            town_prefixes = ['New', 'Old', 'East', 'West', 'North', 'South', 'Upper', 'Lower']
            town_suffixes = ['pur', 'ganj', 'abad', 'nagar', 'ghat', 'kund', 'gaon', 'wadi', 'pura', 'khera']
            
            prefix = random.choice(town_prefixes) if random.random() < 0.3 else ''
            suffix = random.choice(town_suffixes)
            
            # Create base name
            consonants = 'bcdfghjklmnpqrstvwxyz'
            vowels = 'aeiou'
            base_length = random.randint(3, 6)
            base_name = ''
            for j in range(base_length):
                if j % 2 == 0:
                    base_name += random.choice(consonants)
                else:
                    base_name += random.choice(vowels)
            
            town_name = f"{prefix} {base_name.title()}{suffix}" if prefix else f"{base_name.title()}{suffix}"
            station_name = f"{town_name} Railway Station"
            
            if station_name in existing_stations:
                continue
                
            # Random state and city assignment
            state = random.choice(list(INDIAN_STATES.keys()))
            city = random.choice(INDIAN_STATES[state])
            
            # Generate unique code
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            attempts = 0
            while attempts < 10:
                cursor.execute("SELECT id FROM station WHERE code = %s", (code,))
                if not cursor.fetchone():
                    break
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                attempts += 1
            
            try:
                cursor.execute("""
                    INSERT INTO station (name, code, city, state, active, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO NOTHING
                """, (station_name, code, city, state, True, datetime.utcnow()))
                
                if cursor.rowcount > 0:
                    stations_created += 1
                    existing_stations.add(station_name)
                    
            except psycopg2.IntegrityError:
                conn.rollback()
                continue
    
    conn.commit()
    cursor.close()
    conn.close()
    
    logger.info(f"✅ Created {stations_created} railway stations")
    return stations_created

def create_trains(num_trains=1500):
    """Create comprehensive train data"""
    logger.info(f"🚂 Creating {num_trains} trains...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    trains_created = 0
    
    # Get existing train numbers
    cursor.execute("SELECT number FROM train")
    existing_numbers = {row[0] for row in cursor.fetchall()}
    
    for i in range(num_trains):
        # Generate unique train number
        attempts = 0
        while attempts < 20:
            train_number = generate_train_number()
            if train_number not in existing_numbers:
                break
            attempts += 1
        else:
            continue
            
        # Generate train name
        prefix = random.choice(TRAIN_PREFIXES)
        suffix = random.choice(TRAIN_SUFFIXES)
        
        # Create route between two random states
        origin_state = random.choice(list(INDIAN_STATES.keys()))
        dest_state = random.choice(list(INDIAN_STATES.keys()))
        
        if origin_state == dest_state:
            origin_city = random.choice(INDIAN_STATES[origin_state])
            dest_city = random.choice([c for c in INDIAN_STATES[origin_state] if c != origin_city])
        else:
            origin_city = random.choice(INDIAN_STATES[origin_state])
            dest_city = random.choice(INDIAN_STATES[dest_state])
        
        if prefix in ['Rajdhani', 'Shatabdi', 'Duronto']:
            train_name = f"{origin_city} {dest_city} {prefix}"
        else:
            train_name = f"{origin_city} {dest_city} {suffix}"
        
        # Train characteristics based on type
        if prefix in ['Rajdhani', 'Duronto']:
            total_seats = random.randint(800, 1200)
            fare_per_km = random.uniform(1.8, 3.5)
            tatkal_seats = int(total_seats * 0.10)  # 10% tatkal quota
        elif prefix == 'Shatabdi':
            total_seats = random.randint(400, 600)
            fare_per_km = random.uniform(2.2, 4.0)
            tatkal_seats = int(total_seats * 0.15)  # 15% tatkal quota
        elif prefix == 'Garib Rath':
            total_seats = random.randint(600, 900)
            fare_per_km = random.uniform(0.8, 1.5)
            tatkal_seats = int(total_seats * 0.08)  # 8% tatkal quota
        else:
            total_seats = random.randint(500, 1000)
            fare_per_km = random.uniform(1.0, 2.5)
            tatkal_seats = int(total_seats * 0.12)  # 12% tatkal quota
        
        available_seats = random.randint(int(total_seats * 0.3), total_seats)
        tatkal_fare_per_km = fare_per_km * random.uniform(1.8, 2.5)  # Tatkal premium
        
        try:
            cursor.execute("""
                INSERT INTO train (number, name, total_seats, available_seats, fare_per_km, 
                                 tatkal_seats, tatkal_fare_per_km, active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (number) DO NOTHING
            """, (train_number, train_name, total_seats, available_seats, fare_per_km, 
                  tatkal_seats, tatkal_fare_per_km, True, datetime.utcnow()))
            
            if cursor.rowcount > 0:
                trains_created += 1
                existing_numbers.add(train_number)
                
        except psycopg2.IntegrityError:
            conn.rollback()
            continue
    
    conn.commit()
    cursor.close()
    conn.close()
    
    logger.info(f"✅ Created {trains_created} trains")
    return trains_created

def create_train_routes():
    """Create comprehensive train routes"""
    logger.info("🗺️ Creating train routes...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all trains and stations
    cursor.execute("SELECT id, number, name FROM train ORDER BY id")
    trains = cursor.fetchall()
    
    cursor.execute("SELECT id, name, city, state FROM station ORDER BY id")
    stations = cursor.fetchall()
    
    routes_created = 0
    
    for train_id, train_number, train_name in trains:
        # Check if train already has routes
        cursor.execute("SELECT COUNT(*) FROM train_route WHERE train_id = %s", (train_id,))
        if cursor.fetchone()[0] > 0:
            continue
            
        # Create route with 3-15 stations
        num_stations = random.randint(3, 15)
        route_stations = random.sample(stations, min(num_stations, len(stations)))
        
        # Sort by a logical order (could be improved with geographical data)
        route_stations.sort(key=lambda x: x[0])  # Simple sort by station id
        
        total_distance = 0
        
        for idx, (station_id, station_name, city, state) in enumerate(route_stations):
            sequence = idx + 1
            
            # Calculate distance (simplified - random but increasing)
            if idx == 0:
                distance_from_start = 0
            else:
                segment_distance = random.randint(50, 300)  # 50-300 km between stations
                total_distance += segment_distance
                distance_from_start = total_distance
            
            # Generate arrival/departure times
            base_time = datetime.combine(date.today(), time(6, 0))  # Start at 6 AM
            travel_minutes = int(distance_from_start * 0.8)  # Assume 0.8 minutes per km
            
            current_time = base_time + timedelta(minutes=travel_minutes)
            
            if idx == 0:
                # First station - only departure
                arrival_time = None
                departure_time = current_time.time()
            elif idx == len(route_stations) - 1:
                # Last station - only arrival
                arrival_time = current_time.time()
                departure_time = None
            else:
                # Intermediate station - arrival and departure
                arrival_time = current_time.time()
                departure_time = (current_time + timedelta(minutes=random.randint(2, 15))).time()
            
            try:
                cursor.execute("""
                    INSERT INTO train_route (train_id, station_id, sequence, arrival_time, 
                                           departure_time, distance_from_start)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (train_id, station_id, sequence, arrival_time, departure_time, distance_from_start))
                
            except psycopg2.IntegrityError:
                conn.rollback()
                continue
        
        routes_created += 1
        
        # Commit every 50 trains to avoid large transactions
        if routes_created % 50 == 0:
            conn.commit()
            logger.info(f"  ✅ Created routes for {routes_created} trains...")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    logger.info(f"✅ Created routes for {routes_created} trains")
    return routes_created

def create_comprehensive_bookings():
    """Create comprehensive booking data including waitlists"""
    logger.info("🎫 Creating comprehensive booking data...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get users, trains, and stations
    cursor.execute("SELECT id FROM \"user\" WHERE role = 'user'")
    users = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM train")
    trains = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM station")
    stations = [row[0] for row in cursor.fetchall()]
    
    bookings_created = 0
    booking_statuses = ['confirmed', 'waitlisted', 'rac', 'cancelled']
    quota_types = ['general', 'ladies', 'senior', 'disability', 'tatkal']
    waitlist_types = ['GNWL', 'RAC', 'PQWL', 'RLWL', 'TQWL']
    
    # Create 2000 bookings with varied scenarios
    for i in range(2000):
        if not users or not trains or len(stations) < 2:
            break
            
        user_id = random.choice(users)
        train_id = random.choice(trains)
        
        # Select different stations for from/to
        from_station_id, to_station_id = random.sample(stations, 2)
        
        # Journey date (past, present, future)
        base_date = datetime.now().date()
        journey_date = base_date + timedelta(days=random.randint(-30, 60))
        
        passengers = random.randint(1, 6)
        coach_class = random.choice(list(COACH_CLASSES.keys()))
        
        # Calculate fare
        distance = random.randint(100, 1500)  # Simplified distance
        base_fare = distance * COACH_CLASSES[coach_class]['fare_multiplier'] * 0.5
        total_amount = base_fare * passengers
        
        # Add random variations for different booking types
        booking_type = random.choice(['general', 'tatkal'])
        if booking_type == 'tatkal':
            total_amount *= random.uniform(1.8, 2.5)
        
        quota = random.choice(quota_types)
        if quota == 'tatkal':
            booking_type = 'tatkal'
        
        # Determine status based on realistic scenarios
        status_weights = {'confirmed': 0.65, 'waitlisted': 0.20, 'rac': 0.10, 'cancelled': 0.05}
        status = random.choices(list(status_weights.keys()), list(status_weights.values()))[0]
        
        waitlist_type = random.choice(waitlist_types) if status in ['waitlisted', 'rac'] else 'GNWL'
        
        # Generate unique PNR
        attempts = 0
        while attempts < 10:
            pnr = generate_pnr()
            cursor.execute("SELECT id FROM booking WHERE pnr = %s", (pnr,))
            if not cursor.fetchone():
                break
            attempts += 1
        else:
            continue
        
        # Booking date
        booking_date = journey_date - timedelta(days=random.randint(0, 45))
        booking_datetime = datetime.combine(booking_date, time(random.randint(0, 23), random.randint(0, 59)))
        
        try:
            cursor.execute("""
                INSERT INTO booking (pnr, user_id, train_id, from_station_id, to_station_id,
                                   journey_date, passengers, total_amount, booking_type, quota,
                                   coach_class, status, waitlist_type, booking_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (pnr, user_id, train_id, from_station_id, to_station_id, journey_date,
                  passengers, total_amount, booking_type, quota, coach_class, status,
                  waitlist_type, booking_datetime))
            
            bookings_created += 1
            
        except psycopg2.IntegrityError:
            conn.rollback()
            continue
    
    conn.commit()
    cursor.close()
    conn.close()
    
    logger.info(f"✅ Created {bookings_created} comprehensive bookings")
    return bookings_created

def create_waitlist_data():
    """Create detailed waitlist data"""
    logger.info("⏳ Creating waitlist data...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get bookings with waitlist status
    cursor.execute("""
        SELECT id FROM booking 
        WHERE status IN ('waitlisted', 'rac')
    """)
    waitlist_bookings = [row[0] for row in cursor.fetchall()]
    
    waitlist_created = 0
    
    for booking_id in waitlist_bookings:
        position = random.randint(1, 150)
        likelihood = random.randint(20, 95)  # Percentage chance of confirmation
        
        try:
            cursor.execute("""
                INSERT INTO waitlist (booking_id, position, likelihood, status, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (booking_id) DO NOTHING
            """, (booking_id, position, likelihood, 'active', datetime.utcnow()))
            
            if cursor.rowcount > 0:
                waitlist_created += 1
                
        except psycopg2.IntegrityError:
            conn.rollback()
            continue
    
    conn.commit()
    cursor.close()
    conn.close()
    
    logger.info(f"✅ Created {waitlist_created} waitlist entries")
    return waitlist_created

def create_comprehensive_payments():
    """Create comprehensive payment data"""
    logger.info("💳 Creating comprehensive payment data...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get bookings without payments
    cursor.execute("""
        SELECT b.id, b.user_id, b.total_amount, b.status, b.booking_date
        FROM booking b
        LEFT JOIN payment p ON b.id = p.booking_id
        WHERE p.id IS NULL
    """)
    bookings_without_payments = cursor.fetchall()
    
    payments_created = 0
    payment_methods = ['credit_card', 'debit_card', 'upi', 'net_banking', 'wallet']
    payment_statuses = ['completed', 'pending', 'failed', 'refunded']
    
    for booking_id, user_id, amount, booking_status, booking_date in bookings_without_payments:
        # Determine payment status based on booking status
        if booking_status == 'cancelled':
            status = random.choice(['completed', 'refunded'])
        elif booking_status in ['confirmed', 'waitlisted', 'rac']:
            status = 'completed'
        else:
            status = random.choice(payment_statuses)
        
        method = random.choice(payment_methods)
        
        # Generate transaction ID
        transaction_id = f"TXN{random.randint(100000000, 999999999)}"
        
        # Payment date close to booking date
        payment_date = booking_date + timedelta(minutes=random.randint(0, 120))
        
        try:
            cursor.execute("""
                INSERT INTO payment (booking_id, user_id, amount, method, status, 
                                   transaction_id, payment_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (booking_id, user_id, amount, method, status, transaction_id, payment_date))
            
            payments_created += 1
            
        except psycopg2.IntegrityError:
            conn.rollback()
            continue
    
    conn.commit()
    cursor.close()
    conn.close()
    
    logger.info(f"✅ Created {payments_created} payment records")
    return payments_created

def main():
    """Main function to generate all comprehensive data"""
    logger.info("🚀 Starting comprehensive data generation for RailServe...")
    
    try:
        # Create stations
        stations_count = create_stations(1250)
        
        # Create trains
        trains_count = create_trains(1500)
        
        # Create train routes
        routes_count = create_train_routes()
        
        # Create comprehensive bookings
        bookings_count = create_comprehensive_bookings()
        
        # Create waitlist data
        waitlist_count = create_waitlist_data()
        
        # Create comprehensive payments
        payments_count = create_comprehensive_payments()
        
        logger.info("🎉 ✅ Comprehensive data generation completed successfully!")
        logger.info(f"📊 Data Summary:")
        logger.info(f"   Stations: {stations_count}")
        logger.info(f"   Trains: {trains_count}")
        logger.info(f"   Train Routes: {routes_count}")
        logger.info(f"   Bookings: {bookings_count}")
        logger.info(f"   Waitlist Entries: {waitlist_count}")
        logger.info(f"   Payments: {payments_count}")
        
    except Exception as e:
        logger.error(f"❌ Error during data generation: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)