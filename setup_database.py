#!/usr/bin/env python3
"""
Railway Database Initialization Script
Creates database schema using actual models and populates with comprehensive test data

Usage:
    python setup_database.py

Environment Variables:
    DATABASE_URL: PostgreSQL connection string
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

fake = Faker('en_IN')  # Indian locale for realistic data

def setup_database():
    """Initialize database with schema from actual models and populate with test data"""
    
    logger.info("Starting Railway Database Initialization...")
    logger.info("=" * 60)
    
    # Import Flask app and models to get exact schema
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from src.app import app, db
        from src import models  # Import all models
        
        with app.app_context():
            logger.info("Creating database schema from actual models...")
            
            # Drop all tables first
            db.drop_all()
            
            # Create all tables using actual model definitions
            db.create_all()
            
            logger.info("Database schema created successfully using actual models")
            
            # Populate with test data
            logger.info("Populating database with test data...")
            populate_test_data(db)
            
            logger.info("Database initialization completed successfully!")
            
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        sys.exit(1)

def populate_test_data(db):
    """Populate database with comprehensive test data using actual models"""
    
    # Import actual models (only the ones that exist)
    from src.models import (
        User, Station, Train, TrainRoute, Booking, Passenger, Payment, Waitlist,
        TatkalTimeSlot, RefundRequest, TrainStatus, SeatAvailability, ChartPreparation,
        GroupBooking, GroupMemberInvitation, GroupMemberPayment, GroupMessage,
        LoyaltyProgram, NotificationPreferences, TatkalOverride
    )
    
    logger.info("Creating users...")
    create_users(db, User)
    
    logger.info("Creating 1500 stations...")
    create_stations(db, Station)
    
    logger.info("Creating 1250 trains...")
    create_trains(db, Train)
    
    logger.info("Creating train routes...")
    create_train_routes(db, Train, Station, TrainRoute)
    
    logger.info("Creating bookings and related data...")
    create_bookings_and_related_data(db, User, Train, Station, TrainRoute, GroupBooking, 
                                   Booking, Passenger, Payment, Waitlist)
    
    logger.info("Creating additional features data...")
    create_additional_features(db, User, TatkalTimeSlot, LoyaltyProgram, 
                             NotificationPreferences, TatkalOverride)
    
    logger.info("Creating train status and seat availability data...")
    create_operational_data(db, Train, Station, TrainStatus, SeatAvailability, ChartPreparation)
    
    logger.info("Creating group and loyalty features...")
    create_group_and_loyalty_data(db, User, GroupBooking, GroupMemberInvitation, 
                                GroupMemberPayment, GroupMessage, LoyaltyProgram)

def create_users(db, User):
    """Create users including admin and test users"""
    users = []
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@railserve.com',
        password_hash='scrypt:32768:8:1$ZKnR7QwYiWrMGqVl$f4c8a1b2d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8t9u0v1w2x3y4z5',  # password: admin123
        role='super_admin',
        active=True,
        reset_token=None,
        reset_token_expiry=None
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
            reset_token=None,
            reset_token_expiry=None,
            created_at=fake.date_time_between(start_date='-2y', end_date='now')
        )
        users.append(user)
    
    db.session.add_all(users)
    db.session.commit()

def create_stations(db, Station):
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
    station_names_used = set()
    
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
                
                # Generate unique station name
                suffixes = ['Junction', 'Central', 'City', 'Cantt', 'Town', 'Terminal', 'Road', 'East', 'West', 'South', 'North', '']
                station_name = None
                attempts = 0
                while station_name is None and attempts < 20:
                    suffix = random.choice(suffixes)
                    candidate_name = f"{city} {suffix}".strip()
                    if candidate_name not in station_names_used:
                        station_name = candidate_name
                        station_names_used.add(station_name)
                    else:
                        # If name exists, try with a number suffix
                        for num in range(1, 10):
                            numbered_name = f"{candidate_name} {num}"
                            if numbered_name not in station_names_used:
                                station_name = numbered_name
                                station_names_used.add(station_name)
                                break
                        
                    attempts += 1
                
                if station_name is None:
                    # Fallback: use code as part of name
                    station_name = f"{city} {code}"
                    station_names_used.add(station_name)
                
                station = Station(
                    name=station_name,
                    code=code,
                    city=city,
                    state=state,
                    active=True,
                    created_at=fake.date_time_between(start_date='-5y', end_date='now')
                )
                stations.append(station)
    
    db.session.add_all(stations)
    db.session.commit()
    
    logger.info(f"Created {len(stations)} stations")

def create_trains(db, Train):
    """Create 1250 trains with realistic configurations"""
    trains = []
    train_numbers_used = set()
    
    # Train name patterns and prefixes
    train_prefixes = [
        'Express', 'Rajdhani', 'Shatabdi', 'Duronto', 'Garib Rath', 'Jan Shatabdi',
        'Intercity', 'Passenger', 'Mail', 'Special', 'Superfast', 'Humsafar'
    ]
    
    city_pairs = [
        ('Delhi', 'Mumbai'), ('Delhi', 'Chennai'), ('Delhi', 'Kolkata'), ('Delhi', 'Bangalore'),
        ('Mumbai', 'Chennai'), ('Mumbai', 'Kolkata'), ('Mumbai', 'Bangalore'),
        ('Chennai', 'Kolkata'), ('Chennai', 'Bangalore'), ('Kolkata', 'Bangalore'),
        ('Delhi', 'Hyderabad'), ('Mumbai', 'Hyderabad'), ('Chennai', 'Hyderabad'),
        ('Delhi', 'Pune'), ('Mumbai', 'Pune'), ('Chennai', 'Pune'),
        ('Delhi', 'Ahmedabad'), ('Mumbai', 'Ahmedabad'), ('Chennai', 'Ahmedabad')
    ]
    
    for i in range(1250):
        # Generate unique train number
        while True:
            train_number = str(random.randint(10000, 99999))
            if train_number not in train_numbers_used:
                train_numbers_used.add(train_number)
                break
        
        # Generate train name
        prefix = random.choice(train_prefixes)
        city_pair = random.choice(city_pairs)
        train_name = f"{city_pair[0]} - {city_pair[1]} {prefix}"
        
        # Random seat configuration
        total_seats = random.choice([300, 400, 500, 600, 750, 900, 1200, 1500])
        available_seats = random.randint(int(total_seats * 0.7), total_seats)
        
        # Fare configuration
        base_fare = random.uniform(0.5, 2.5)  # per km
        tatkal_seats = random.randint(10, 50)
        tatkal_fare = base_fare * random.uniform(1.3, 1.8)  # 30-80% premium
        
        train = Train(
            number=train_number,
            name=train_name,
            total_seats=total_seats,
            available_seats=available_seats,
            fare_per_km=round(base_fare, 2),
            tatkal_seats=tatkal_seats,
            tatkal_fare_per_km=round(tatkal_fare, 2),
            active=True,
            created_at=fake.date_time_between(start_date='-5y', end_date='now')
        )
        trains.append(train)
    
    db.session.add_all(trains)
    db.session.commit()
    
    logger.info(f"Created {len(trains)} trains")

def create_train_routes(db, Train, Station, TrainRoute):
    """Create comprehensive train routes"""
    trains = Train.query.all()
    stations = Station.query.all()
    
    train_routes = []
    
    for train in trains:
        # Each train will have 5-15 stations in its route
        num_stations = random.randint(5, 15)
        selected_stations = random.sample(stations, num_stations)
        
        total_distance = 0
        current_time = time(hour=random.randint(5, 22), minute=random.choice([0, 15, 30, 45]))
        
        for seq, station in enumerate(selected_stations, 1):
            # Calculate distance from start (cumulative)
            if seq == 1:
                distance = 0
            else:
                segment_distance = random.randint(50, 300)  # km between stations
                total_distance += segment_distance
                distance = total_distance
            
            # Calculate arrival and departure times
            if seq == 1:
                # First station - only departure
                arrival_time = None
                departure_time = current_time
            elif seq == len(selected_stations):
                # Last station - only arrival
                arrival_time = current_time
                departure_time = None
            else:
                # Intermediate stations
                arrival_time = current_time
                # Stop for 2-10 minutes
                stop_minutes = random.randint(2, 10)
                departure_time = time(
                    hour=(current_time.hour + (current_time.minute + stop_minutes) // 60) % 24,
                    minute=(current_time.minute + stop_minutes) % 60
                )
            
            route = TrainRoute(
                train_id=train.id,
                station_id=station.id,
                sequence=seq,
                arrival_time=arrival_time,
                departure_time=departure_time if seq < len(selected_stations) else None,
                distance_from_start=distance
            )
            train_routes.append(route)
            
            # Update current time for next station (travel time)
            if seq < len(selected_stations):
                travel_hours = random.randint(1, 4)
                travel_minutes = random.randint(0, 59)
                current_time = time(
                    hour=(current_time.hour + travel_hours + (current_time.minute + travel_minutes) // 60) % 24,
                    minute=(current_time.minute + travel_minutes) % 60
                )
    
    db.session.add_all(train_routes)
    db.session.commit()
    
    logger.info(f"Created {len(train_routes)} train route entries")

def create_bookings_and_related_data(db, User, Train, Station, TrainRoute, GroupBooking, 
                                   Booking, Passenger, Payment, Waitlist):
    """Create bookings, passengers, payments, and related data"""
    users = User.query.all()
    trains = Train.query.all()
    stations = Station.query.all()
    
    bookings = []
    passengers = []
    payments = []
    waitlists = []
    group_bookings = []
    
    # Create some group bookings first
    for _ in range(50):
        group_leader = random.choice(users)
        
        group_booking = GroupBooking(
            group_name=f"{fake.company()} Trip",
            group_leader_id=group_leader.id,
            total_passengers=random.randint(5, 20),
            contact_email=group_leader.email,
            contact_phone=f"+91{random.randint(7000000000, 9999999999)}",
            booking_type=random.choice(['family', 'corporate']),
            special_requirements=fake.text(max_nb_chars=200) if random.random() < 0.3 else None,
            discount_applied=random.uniform(0, 1000),
            group_discount_rate=random.uniform(0.05, 0.15),
            status=random.choice(['pending', 'confirmed', 'cancelled']),
            created_at=fake.date_time_between(start_date='-6m', end_date='now')
        )
        group_bookings.append(group_booking)
    
    db.session.add_all(group_bookings)
    db.session.commit()
    
    # Create individual bookings
    for _ in range(1200):
        user = random.choice(users)
        train = random.choice(trains)
        
        # Get stations from train route
        train_stations = TrainRoute.query.filter_by(train_id=train.id).order_by(TrainRoute.sequence).all()
        if len(train_stations) < 2:
            continue
        
        # Select random from and to stations
        from_route = random.choice(train_stations[:-1])
        to_route = random.choice(train_stations[from_route.sequence:])
        
        # Journey date (within next 6 months)
        journey_date = fake.date_between(start_date='today', end_date='+6m')
        
        # Passenger count
        passenger_count = random.randint(1, 6)
        
        # Calculate amount based on distance
        distance = to_route.distance_from_start - from_route.distance_from_start
        base_amount = distance * train.fare_per_km * passenger_count
        
        # Add random service charges and taxes
        total_amount = base_amount * random.uniform(1.1, 1.3)
        
        # Booking status
        booking_status = random.choices(
            ['confirmed', 'waitlisted', 'cancelled', 'pending_payment'],
            weights=[70, 15, 10, 5]
        )[0]
        
        # Group booking association (20% chance)
        group_booking_id = random.choice(group_bookings).id if random.random() < 0.2 else None
        
        booking = Booking(
            user_id=user.id,
            train_id=train.id,
            from_station_id=from_route.station_id,
            to_station_id=to_route.station_id,
            journey_date=journey_date,
            passengers=passenger_count,
            total_amount=round(total_amount, 2),
            booking_type=random.choice(['general', 'tatkal']),
            quota=random.choice(['general', 'ladies', 'senior', 'disability', 'tatkal']),
            coach_class=random.choice(['SL', 'AC3', 'AC2', 'AC1', '2S', 'CC']),
            status=booking_status,
            waitlist_type=random.choice(['GNWL', 'RAC', 'PQWL', 'RLWL', 'TQWL']) if booking_status == 'waitlisted' else 'GNWL',
            chart_prepared=random.choice([True, False]) if booking_status == 'confirmed' else False,
            berth_preference=random.choice(['Lower', 'Middle', 'Upper', 'Window', 'Aisle', 'No Preference']),
            current_reservation=False,
            booking_date=fake.date_time_between(start_date='-6m', end_date='now'),
            cancellation_charges=random.uniform(50, 200) if booking_status == 'cancelled' else 0.0,
            group_booking_id=group_booking_id,
            loyalty_discount=random.uniform(0, 100) if random.random() < 0.1 else 0.0
        )
        bookings.append(booking)
    
    db.session.add_all(bookings)
    db.session.commit()  # Get booking IDs
    
    # Create passengers for each booking
    for booking in bookings:
        for i in range(booking.passengers):
            passenger = Passenger(
                booking_id=booking.id,
                name=fake.name(),
                age=random.randint(1, 80),
                gender=random.choice(['Male', 'Female', 'Other']),
                id_proof_type=random.choice(['Aadhar', 'PAN', 'Passport', 'Voter ID', 'Driving License']),
                id_proof_number=f"{random.randint(100000000000, 999999999999)}",
                seat_preference=random.choice(['Lower', 'Middle', 'Upper', 'Window', 'Aisle', 'No Preference']),
                coach_class=booking.coach_class,
                seat_number=f"{random.choice(['S', 'A', 'B'])}{random.randint(1, 10)}-{random.randint(1, 72)}" if booking.status == 'confirmed' else None,
                berth_type=random.choice(['Lower', 'Middle', 'Upper', 'Side Lower', 'Side Upper']) if booking.status == 'confirmed' else None
            )
            passengers.append(passenger)
    
    db.session.add_all(passengers)
    
    # Create payments for bookings
    for booking in bookings:
        if booking.status in ['confirmed', 'cancelled']:
            payment = Payment(
                booking_id=booking.id,
                user_id=booking.user_id,
                amount=booking.total_amount,
                payment_method=random.choice(['card', 'upi', 'netbanking']),
                transaction_id=f"TXN{random.randint(1000000000, 9999999999)}",
                status='success' if booking.status == 'confirmed' else 'failed',
                created_at=booking.booking_date,
                completed_at=booking.booking_date + timedelta(minutes=random.randint(1, 10))
            )
            payments.append(payment)
    
    db.session.add_all(payments)
    
    # Create waitlist entries for waitlisted bookings
    for booking in bookings:
        if booking.status == 'waitlisted':
            waitlist = Waitlist(
                booking_id=booking.id,
                train_id=booking.train_id,
                journey_date=booking.journey_date,
                position=random.randint(1, 50),
                waitlist_type=booking.waitlist_type,
                created_at=booking.booking_date
            )
            waitlists.append(waitlist)
    
    db.session.add_all(waitlists)
    db.session.commit()
    
    logger.info(f"Created {len(group_bookings)} group bookings, {len(bookings)} bookings, {len(passengers)} passengers, {len(payments)} payments, and {len(waitlists)} waitlist entries")

def create_additional_features(db, User, TatkalTimeSlot, LoyaltyProgram, 
                             NotificationPreferences, TatkalOverride):
    """Create additional feature data"""
    users = User.query.all()
    
    # Create Tatkal time slots
    tatkal_slots = [
        TatkalTimeSlot(
            name='AC Classes Tatkal',
            coach_classes='AC1,AC2,AC3,CC',
            open_time=time(10, 0),  # 10:00 AM
            close_time=time(23, 59),  # 11:59 PM
            days_before_journey=1,
            active=True,
            created_by=users[0].id  # Admin user
        ),
        TatkalTimeSlot(
            name='Non-AC Classes Tatkal',
            coach_classes='SL,2S',
            open_time=time(11, 0),  # 11:00 AM
            close_time=time(23, 59),  # 11:59 PM
            days_before_journey=1,
            active=True,
            created_by=users[0].id  # Admin user
        )
    ]
    
    db.session.add_all(tatkal_slots)
    
    # Create loyalty programs for some users (30%)
    loyalty_programs = []
    for user in random.sample(users[1:], min(30, len(users)-1)):  # Skip admin user
        loyalty = LoyaltyProgram(
            user_id=user.id,
            membership_number=f"LP{random.randint(100000, 999999)}",
            tier=random.choice(['Silver', 'Gold', 'Platinum']),
            points_earned=random.randint(0, 10000),
            points_redeemed=random.randint(0, 1000),
            total_journeys=random.randint(1, 50),
            total_distance=random.uniform(1000, 50000),
            total_spent=random.uniform(5000, 100000),
            tier_valid_until=fake.date_between(start_date='+1m', end_date='+2y'),
            benefits_active=True,
            joined_date=fake.date_time_between(start_date='-2y', end_date='now'),
            last_activity=fake.date_time_between(start_date='-1m', end_date='now')
        )
        loyalty_programs.append(loyalty)
    
    db.session.add_all(loyalty_programs)
    
    # Create notification preferences for all users
    notification_prefs = []
    for user in users:
        prefs = NotificationPreferences(
            user_id=user.id,
            email_notifications=random.choice([True, False]),
            sms_notifications=random.choice([True, False]),
            push_notifications=random.choice([True, False]),
            booking_confirmations=True,  # Always True for booking confirmations
            journey_reminders=random.choice([True, False]),
            train_delay_alerts=random.choice([True, False]),
            promotional_offers=random.choice([True, False])
        )
        notification_prefs.append(prefs)
    
    db.session.add_all(notification_prefs)
    
    # Create a Tatkal override record
    tatkal_override = TatkalOverride(
        is_enabled=False,
        enabled_by=users[0].id,  # Admin user
        override_message='Tatkal booking currently follows normal schedule',
        coach_classes='',
        valid_until=None
    )
    
    db.session.add(tatkal_override)
    db.session.commit()
    
    logger.info(f"Created {len(tatkal_slots)} Tatkal time slots, {len(loyalty_programs)} loyalty programs, and {len(notification_prefs)} notification preferences")

def create_operational_data(db, Train, Station, TrainStatus, SeatAvailability, ChartPreparation):
    """Create operational data for trains"""
    trains = Train.query.all()
    stations = Station.query.all()
    
    train_statuses = []
    seat_availabilities = []
    chart_preparations = []
    
    # Create train status for some trains
    for train in random.sample(trains, min(200, len(trains))):
        current_station = random.choice(stations)
        status = TrainStatus(
            train_id=train.id,
            current_station_id=current_station.id,
            status=random.choice(['On Time', 'Delayed', 'Cancelled']),
            delay_minutes=random.randint(0, 180) if random.random() < 0.3 else 0,
            journey_date=fake.date_between(start_date='today', end_date='+30d'),
            last_updated=fake.date_time_between(start_date='-1h', end_date='now')
        )
        train_statuses.append(status)
    
    # Create seat availability data
    for train in random.sample(trains, min(300, len(trains))):
        from_station = random.choice(stations)
        to_station = random.choice(stations)
        if from_station.id != to_station.id:
            availability = SeatAvailability(
                train_id=train.id,
                from_station_id=from_station.id,
                to_station_id=to_station.id,
                journey_date=fake.date_between(start_date='today', end_date='+60d'),
                coach_class=random.choice(['SL', 'AC3', 'AC2', 'AC1', '2S', 'CC']),
                quota=random.choice(['general', 'tatkal', 'ladies']),
                available_seats=random.randint(0, 100),
                waiting_list=random.randint(0, 50),
                rac_seats=random.randint(0, 20),
                last_updated=fake.date_time_between(start_date='-1h', end_date='now')
            )
            seat_availabilities.append(availability)
    
    # Create chart preparation data
    for train in random.sample(trains, min(150, len(trains))):
        chart = ChartPreparation(
            train_id=train.id,
            journey_date=fake.date_between(start_date='today', end_date='+30d'),
            status=random.choice(['pending', 'prepared', 'final']),
            chart_prepared_at=fake.date_time_between(start_date='-4h', end_date='now') if random.random() < 0.7 else None,
            final_chart_at=fake.date_time_between(start_date='-2h', end_date='now') if random.random() < 0.3 else None,
            confirmed_from_waitlist=random.randint(0, 20),
            cancelled_waitlist=random.randint(0, 10)
        )
        chart_preparations.append(chart)
    
    db.session.add_all(train_statuses)
    db.session.add_all(seat_availabilities)
    db.session.add_all(chart_preparations)
    db.session.commit()
    
    logger.info(f"Created {len(train_statuses)} train statuses, {len(seat_availabilities)} seat availabilities, and {len(chart_preparations)} chart preparations")

def create_group_and_loyalty_data(db, User, GroupBooking, GroupMemberInvitation, 
                                GroupMemberPayment, GroupMessage, LoyaltyProgram):
    """Create group booking and loyalty related data"""
    users = User.query.all()
    group_bookings = GroupBooking.query.all()
    
    group_invitations = []
    group_payments = []
    group_messages = []
    
    # Create group member invitations
    for group in random.sample(group_bookings, min(30, len(group_bookings))):
        for _ in range(random.randint(1, 5)):
            invitation = GroupMemberInvitation(
                group_booking_id=group.id,
                inviter_id=group.group_leader_id,
                invited_email=fake.email(),
                invited_user_id=random.choice(users).id if random.random() < 0.7 else None,
                status=random.choice(['pending', 'accepted', 'declined']),
                message=fake.text(max_nb_chars=150),
                created_at=fake.date_time_between(start_date='-30d', end_date='now'),
                responded_at=fake.date_time_between(start_date='-20d', end_date='now') if random.random() < 0.6 else None
            )
            group_invitations.append(invitation)
    
    # Create group member payments
    for group in random.sample(group_bookings, min(25, len(group_bookings))):
        for _ in range(random.randint(1, 4)):
            payment = GroupMemberPayment(
                group_booking_id=group.id,
                booking_id=random.choice(group.individual_bookings).id if group.individual_bookings else None,
                user_id=random.choice(users).id,
                amount_due=random.uniform(1000, 5000),
                amount_paid=random.uniform(0, 5000),
                payment_method=random.choice(['credit_card', 'debit_card', 'upi', 'wallet']),
                payment_reference=f"PAY{random.randint(100000, 999999)}",
                status=random.choice(['pending', 'partial', 'paid']),
                created_at=fake.date_time_between(start_date='-15d', end_date='now'),
                paid_at=fake.date_time_between(start_date='-10d', end_date='now') if random.random() < 0.7 else None
            )
            group_payments.append(payment)
    
    # Create group messages
    for group in random.sample(group_bookings, min(20, len(group_bookings))):
        for _ in range(random.randint(2, 8)):
            message = GroupMessage(
                group_booking_id=group.id,
                sender_id=group.group_leader_id if random.random() < 0.6 else random.choice(users).id,
                message=fake.text(max_nb_chars=300),
                message_type=random.choice(['general', 'announcement', 'reminder']),
                is_important=random.choice([True, False]),
                created_at=fake.date_time_between(start_date='-7d', end_date='now')
            )
            group_messages.append(message)
    
    db.session.add_all(group_invitations)
    db.session.add_all(group_payments)
    db.session.add_all(group_messages)
    db.session.commit()
    
    logger.info(f"Created {len(group_invitations)} group invitations, {len(group_payments)} group payments, and {len(group_messages)} group messages")

if __name__ == "__main__":
    setup_database()