#!/usr/bin/env python3
"""
Supabase PostgreSQL Database Initialization Script
Populates database with 1000 Indian railway stations and 1250 trains with real routes and pricing
"""

import os
import sys
from datetime import datetime, date, timedelta, time
import random
from faker import Faker

fake = Faker('en_IN')  # Indian locale for realistic data

# Import Flask app to get database connection
from src.app import app, db
from src.models import (
    User, Station, Train, TrainRoute, SeatAvailability, 
    TatkalTimeSlot, DynamicPricing, PerformanceMetrics
)
from werkzeug.security import generate_password_hash

# Real Indian railway stations (top 100+ major stations)
MAJOR_INDIAN_STATIONS = [
    # Metro cities and major junctions
    ("Mumbai Central", "BCT", "Mumbai", "Maharashtra"),
    ("Chhatrapati Shivaji Terminus", "CSMT", "Mumbai", "Maharashtra"),
    ("New Delhi", "NDLS", "Delhi", "Delhi"),
    ("Old Delhi", "DLI", "Delhi", "Delhi"),
    ("Chennai Central", "MAS", "Chennai", "Tamil Nadu"),
    ("Howrah Junction", "HWH", "Kolkata", "West Bengal"),
    ("Bangalore City", "SBC", "Bangalore", "Karnataka"),
    ("Hyderabad Deccan", "HYB", "Hyderabad", "Telangana"),
    ("Pune Junction", "PUNE", "Pune", "Maharashtra"),
    ("Ahmedabad Junction", "ADI", "Ahmedabad", "Gujarat"),
    
    # Important railway junctions
    ("Kanpur Central", "CNB", "Kanpur", "Uttar Pradesh"),
    ("Lucknow", "LKO", "Lucknow", "Uttar Pradesh"),
    ("Jaipur Junction", "JP", "Jaipur", "Rajasthan"),
    ("Bhopal Junction", "BPL", "Bhopal", "Madhya Pradesh"),
    ("Nagpur Junction", "NGP", "Nagpur", "Maharashtra"),
    ("Vijayawada Junction", "BZA", "Vijayawada", "Andhra Pradesh"),
    ("Visakhapatnam", "VSKP", "Visakhapatnam", "Andhra Pradesh"),
    ("Secunderabad Junction", "SC", "Secunderabad", "Telangana"),
    ("Coimbatore Junction", "CBE", "Coimbatore", "Tamil Nadu"),
    ("Madurai Junction", "MDU", "Madurai", "Tamil Nadu"),
    
    # North India
    ("Amritsar Junction", "ASR", "Amritsar", "Punjab"),
    ("Chandigarh", "CDG", "Chandigarh", "Chandigarh"),
    ("Ludhiana Junction", "LDH", "Ludhiana", "Punjab"),
    ("Jalandhar City", "JUC", "Jalandhar", "Punjab"),
    ("Jammu Tawi", "JAT", "Jammu", "Jammu & Kashmir"),
    ("Pathankot Junction", "PTK", "Pathankot", "Punjab"),
    ("Dehradun", "DDN", "Dehradun", "Uttarakhand"),
    ("Haridwar Junction", "HW", "Haridwar", "Uttarakhand"),
    ("Varanasi Junction", "BSB", "Varanasi", "Uttar Pradesh"),
    ("Allahabad Junction", "ALD", "Allahabad", "Uttar Pradesh"),
    
    # East India
    ("Patna Junction", "PNBE", "Patna", "Bihar"),
    ("Gaya Junction", "GAYA", "Gaya", "Bihar"),
    ("Ranchi Junction", "RNC", "Ranchi", "Jharkhand"),
    ("Tatanagar Junction", "TATA", "Jamshedpur", "Jharkhand"),
    ("Bhubaneswar", "BBS", "Bhubaneswar", "Odisha"),
    ("Puri", "PURI", "Puri", "Odisha"),
    ("Cuttack", "CTC", "Cuttack", "Odisha"),
    ("Guwahati", "GHY", "Guwahati", "Assam"),
    ("Dibrugarh", "DBRG", "Dibrugarh", "Assam"),
    ("Agartala", "AGTL", "Agartala", "Tripura"),
    
    # West India
    ("Surat", "ST", "Surat", "Gujarat"),
    ("Vadodara Junction", "BRC", "Vadodara", "Gujarat"),
    ("Rajkot Junction", "RJT", "Rajkot", "Gujarat"),
    ("Gandhinagar", "GNC", "Gandhinagar", "Gujarat"),
    ("Indore Junction", "INDB", "Indore", "Madhya Pradesh"),
    ("Ujjain Junction", "UJN", "Ujjain", "Madhya Pradesh"),
    ("Gwalior Junction", "GWL", "Gwalior", "Madhya Pradesh"),
    ("Jodhpur Junction", "JU", "Jodhpur", "Rajasthan"),
    ("Udaipur City", "UDZ", "Udaipur", "Rajasthan"),
    ("Bikaner Junction", "BKN", "Bikaner", "Rajasthan"),
    
    # South India
    ("Thiruvananthapuram Central", "TVC", "Thiruvananthapuram", "Kerala"),
    ("Ernakulam Junction", "ERS", "Kochi", "Kerala"),
    ("Kozhikode", "CLT", "Kozhikode", "Kerala"),
    ("Thrissur", "TCR", "Thrissur", "Kerala"),
    ("Mangalore Central", "MAQ", "Mangalore", "Karnataka"),
    ("Mysore Junction", "MYS", "Mysore", "Karnataka"),
    ("Hubli Junction", "UBL", "Hubli", "Karnataka"),
    ("Tirupati", "TPTY", "Tirupati", "Andhra Pradesh"),
    ("Nellore", "NLR", "Nellore", "Andhra Pradesh"),
    ("Rajahmundry", "RJY", "Rajahmundry", "Andhra Pradesh"),
    
    # Central India
    ("Raipur Junction", "R", "Raipur", "Chhattisgarh"),
    ("Bilaspur Junction", "BSP", "Bilaspur", "Chhattisgarh"),
    ("Jabalpur Junction", "JBP", "Jabalpur", "Madhya Pradesh"),
    ("Itarsi Junction", "ET", "Itarsi", "Madhya Pradesh"),
    ("Kota Junction", "KOTA", "Kota", "Rajasthan"),
    ("Ajmer Junction", "AII", "Ajmer", "Rajasthan"),
    ("Solapur Junction", "SUR", "Solapur", "Maharashtra"),
    ("Aurangabad", "AWB", "Aurangabad", "Maharashtra"),
    ("Nashik Road", "NK", "Nashik", "Maharashtra"),
    ("Kolhapur", "KOP", "Kolhapur", "Maharashtra"),
    
    # Additional important stations
    ("Agra Cantt", "AGC", "Agra", "Uttar Pradesh"),
    ("Mathura Junction", "MTJ", "Mathura", "Uttar Pradesh"),
    ("Bareilly", "BE", "Bareilly", "Uttar Pradesh"),
    ("Gorakhpur Junction", "GKP", "Gorakhpur", "Uttar Pradesh"),
    ("Meerut City", "MTC", "Meerut", "Uttar Pradesh"),
    ("Aligarh Junction", "ALJN", "Aligarh", "Uttar Pradesh"),
    ("Darbhanga Junction", "DBG", "Darbhanga", "Bihar"),
    ("Muzaffarpur Junction", "MFP", "Muzaffarpur", "Bihar"),
    ("Bhagalpur", "BGP", "Bhagalpur", "Bihar"),
    ("Asansol Junction", "ASN", "Asansol", "West Bengal"),
    ("Durgapur", "DGR", "Durgapur", "West Bengal"),
    ("Siliguri Junction", "SGUJ", "Siliguri", "West Bengal"),
    ("Malda Town", "MLDT", "Malda", "West Bengal"),
    ("Rourkela Junction", "ROU", "Rourkela", "Odisha"),
    ("Sambalpur", "SBP", "Sambalpur", "Odisha"),
    ("Berhampur", "BAM", "Berhampur", "Odisha"),
    ("Salem Junction", "SA", "Salem", "Tamil Nadu"),
    ("Tirunelveli Junction", "TEN", "Tirunelveli", "Tamil Nadu"),
    ("Trichy Junction", "TPJ", "Tiruchirappalli", "Tamil Nadu"),
    ("Vellore Cantt", "VLR", "Vellore", "Tamil Nadu"),
    ("Guntur Junction", "GNT", "Guntur", "Andhra Pradesh"),
    ("Warangal", "WL", "Warangal", "Telangana"),
    ("Nizamabad Junction", "NZB", "Nizamabad", "Telangana"),
]

# Train types with realistic pricing (fare per km in INR)
TRAIN_TYPES = {
    "Rajdhani Express": {"base_fare": 2.20, "tatkal_multiplier": 1.3, "prefix": "12", "total_seats": 400, "tatkal_seats": 40},
    "Shatabdi Express": {"base_fare": 2.80, "tatkal_multiplier": 1.3, "prefix": "12", "total_seats": 500, "tatkal_seats": 50},
    "Duronto Express": {"base_fare": 1.75, "tatkal_multiplier": 1.3, "prefix": "12", "total_seats": 600, "tatkal_seats": 60},
    "Garib Rath": {"base_fare": 1.20, "tatkal_multiplier": 1.2, "prefix": "12", "total_seats": 700, "tatkal_seats": 70},
    "Humsafar Express": {"base_fare": 1.60, "tatkal_multiplier": 1.25, "prefix": "12", "total_seats": 450, "tatkal_seats": 45},
    "Vande Bharat": {"base_fare": 3.50, "tatkal_multiplier": 1.4, "prefix": "20", "total_seats": 400, "tatkal_seats": 40},
    "Tejas Express": {"base_fare": 3.00, "tatkal_multiplier": 1.35, "prefix": "12", "total_seats": 400, "tatkal_seats": 40},
    "Mail/Express": {"base_fare": 0.60, "tatkal_multiplier": 1.3, "prefix": "11", "total_seats": 1000, "tatkal_seats": 100},
    "Superfast Express": {"base_fare": 0.80, "tatkal_multiplier": 1.3, "prefix": "12", "total_seats": 900, "tatkal_seats": 90},
    "Passenger": {"base_fare": 0.30, "tatkal_multiplier": 1.1, "prefix": "52", "total_seats": 800, "tatkal_seats": 30},
}

# Famous Indian train names by route
FAMOUS_TRAINS = [
    ("Rajdhani Express", ["New Delhi", "Mumbai Central"]),
    ("Rajdhani Express", ["New Delhi", "Howrah Junction"]),
    ("Rajdhani Express", ["New Delhi", "Bangalore City"]),
    ("Rajdhani Express", ["New Delhi", "Chennai Central"]),
    ("Shatabdi Express", ["New Delhi", "Amritsar Junction"]),
    ("Shatabdi Express", ["New Delhi", "Kanpur Central"]),
    ("Shatabdi Express", ["Mumbai Central", "Ahmedabad Junction"]),
    ("Shatabdi Express", ["Chennai Central", "Bangalore City"]),
    ("Duronto Express", ["Mumbai Central", "Howrah Junction"]),
    ("Duronto Express", ["New Delhi", "Vijayawada Junction"]),
    ("Vande Bharat", ["New Delhi", "Varanasi Junction"]),
    ("Vande Bharat", ["Mumbai Central", "Ahmedabad Junction"]),
]

def generate_station_code():
    """Generate a unique station code"""
    return ''.join(random.choices('ABCDEFGHIJKLMNPQRSTUVWXYZ', k=random.randint(2, 4)))

def initialize_database():
    """Initialize the database with comprehensive railway data"""
    
    print("="*70)
    print("           Supabase PostgreSQL Database Initialization")
    print("                    RailServe Application")
    print("="*70)
    print()
    print("📋 This will create:")
    print("  • 1000 Indian railway stations")
    print("  • 1250 trains with realistic routes and pricing")
    print("  • Multi-station train routes (5-15 stations per train)")
    print("  • Seat availability (150 trains × 7 days)")
    print("  • Admin user and Tatkal time slots")
    print("="*70)
    print()
    
    with app.app_context():
        # Drop all tables and recreate
        print("[DATABASE] Creating all tables in Supabase PostgreSQL...")
        db.drop_all()
        db.create_all()
        print("✓ All tables created in Supabase")
        print()
        
        # Create admin user
        print("[ADMIN & TATKAL] Creating admin user and Tatkal slots...")
        admin = User(
            username='admin',
            email='admin@railserve.com',
            password_hash=generate_password_hash('admin123'),
            role='super_admin',
            active=True
        )
        db.session.add(admin)
        
        db.session.commit()
        
        # Create Tatkal time slots
        ac_slot = TatkalTimeSlot(
            name='AC Classes Tatkal',
            coach_classes='AC1,AC2,AC3,CC',
            open_time=time(10, 0),
            close_time=time(18, 0),
            days_before_journey=1,
            active=True,
            created_by=admin.id
        )
        non_ac_slot = TatkalTimeSlot(
            name='Non-AC Classes Tatkal',
            coach_classes='SL,2S',
            open_time=time(11, 0),
            close_time=time(18, 0),
            days_before_journey=1,
            active=True,
            created_by=admin.id
        )
        db.session.add(ac_slot)
        db.session.add(non_ac_slot)
        db.session.commit()
        print("✓ Admin user created (username: admin, password: admin123)")
        print("✓ Tatkal slots created (AC: 10:00 AM, Non-AC: 11:00 AM)")
        print()
        
        # Create stations
        print(f"[STATIONS] Generating 1000 stations (including {len(MAJOR_INDIAN_STATIONS)} major stations)...")
        stations = []
        used_codes = set()
        
        # Add major stations first
        for name, code, city, state in MAJOR_INDIAN_STATIONS:
            station = Station(
                name=name,
                code=code,
                city=city,
                state=state,
                active=True
            )
            stations.append(station)
            used_codes.add(code)
        
        # Generate additional stations to reach 1000
        indian_cities = [
            ("Maharashtra", ["Thane", "Navi Mumbai", "Kalyan", "Vasai", "Panvel"]),
            ("Gujarat", ["Anand", "Mehsana", "Jamnagar", "Bhavnagar", "Vapi"]),
            ("Tamil Nadu", ["Hosur", "Kanchipuram", "Thanjavur", "Karur", "Dindigul"]),
            ("Karnataka", ["Belgaum", "Gulbarga", "Bellary", "Shimoga", "Tumkur"]),
            ("Uttar Pradesh", ["Moradabad", "Saharanpur", "Firozabad", "Jhansi", "Ayodhya"]),
            ("Rajasthan", ["Alwar", "Bharatpur", "Sikar", "Pali", "Chittorgarh"]),
            ("Madhya Pradesh", {"Sagar", "Satna", "Rewa", "Dewas", "Katni"}),
            ("West Bengal", ["Bardhaman", "Howrah", "Kharagpur", "Krishnanagar", "Barrackpore"]),
            ("Bihar", ["Chapra", "Sasaram", "Begusarai", "Katihar", "Purnia"]),
            ("Andhra Pradesh", ["Kakinada", "Anantapur", "Kurnool", "Kadapa", "Eluru"]),
        ]
        
        used_names = {s.name for s in stations}
        
        while len(stations) < 1000:
            state, cities = random.choice(indian_cities)
            if isinstance(cities, set):
                cities = list(cities)
            city = random.choice(cities)
            
            # Generate station name with unique suffix
            suffix = random.choice(["Junction", "City", "Cantt", "Road", "Town", "Central", "Terminal", ""])
            station_name = f"{city} {suffix}".strip()
            
            # Ensure name uniqueness by adding counter if needed
            base_name = station_name
            counter = 1
            while station_name in used_names:
                station_name = f"{base_name} {counter}"
                counter += 1
            
            # Generate unique code
            code = generate_station_code()
            while code in used_codes:
                code = generate_station_code()
            
            used_codes.add(code)
            used_names.add(station_name)
            station = Station(
                name=station_name,
                code=code,
                city=city,
                state=state,
                active=True
            )
            stations.append(station)
        
        db.session.bulk_save_objects(stations)
        db.session.commit()
        print(f"✓ Created {len(stations)} stations")
        print()
        
        # Reload stations from database to get IDs
        all_stations = Station.query.all()
        station_by_name = {s.name: s for s in all_stations}
        
        # Create trains
        print("[TRAINS] Generating 1250 trains with realistic fares...")
        trains = []
        used_train_numbers = set()
        train_counter = {train_type: 1 for train_type in TRAIN_TYPES.keys()}
        
        # Create famous trains first
        for train_type, route_cities in FAMOUS_TRAINS:
            config = TRAIN_TYPES[train_type]
            
            # Ensure unique train number
            train_number = f"{config['prefix']}{train_counter[train_type]:03d}"
            while train_number in used_train_numbers:
                train_counter[train_type] += 1
                train_number = f"{config['prefix']}{train_counter[train_type]:03d}"
            used_train_numbers.add(train_number)
            train_counter[train_type] += 1
            
            origin = route_cities[0]
            destination = route_cities[-1]
            train_name = f"{origin.split()[0]}-{destination.split()[0]} {train_type}"
            
            train = Train(
                number=train_number,
                name=train_name,
                total_seats=config['total_seats'],
                available_seats=config['total_seats'],
                fare_per_km=config['base_fare'],
                tatkal_seats=config['tatkal_seats'],
                tatkal_fare_per_km=config['base_fare'] * config['tatkal_multiplier'],
                active=True
            )
            trains.append(train)
        
        # Generate remaining trains
        while len(trains) < 1250:
            train_type = random.choice(list(TRAIN_TYPES.keys()))
            config = TRAIN_TYPES[train_type]
            
            # Ensure unique train number
            train_number = f"{config['prefix']}{train_counter[train_type]:03d}"
            while train_number in used_train_numbers:
                train_counter[train_type] += 1
                train_number = f"{config['prefix']}{train_counter[train_type]:03d}"
            used_train_numbers.add(train_number)
            train_counter[train_type] += 1
            
            # Pick random origin and destination
            origin = random.choice(all_stations)
            destination = random.choice(all_stations)
            while destination.id == origin.id:
                destination = random.choice(all_stations)
            
            train_name = f"{origin.city}-{destination.city} {train_type}"
            
            train = Train(
                number=train_number,
                name=train_name,
                total_seats=config['total_seats'],
                available_seats=config['total_seats'],
                fare_per_km=config['base_fare'],
                tatkal_seats=config['tatkal_seats'],
                tatkal_fare_per_km=config['base_fare'] * config['tatkal_multiplier'],
                active=True
            )
            trains.append(train)
        
        db.session.bulk_save_objects(trains)
        db.session.commit()
        print(f"✓ Created {len(trains)} trains with realistic Indian Railway pricing")
        print()
        
        # Reload trains from database to get IDs
        all_trains = Train.query.all()
        
        # Create train routes
        print("[ROUTES] Creating realistic multi-station train routes...")
        routes = []
        total_routes = 0
        
        for idx, train in enumerate(all_trains, 1):
            # Each train has 5-15 stations in its route
            num_stations = random.randint(5, 15)
            route_stations = random.sample(all_stations, num_stations)
            
            cumulative_distance = 0
            for seq, station in enumerate(route_stations, 1):
                if seq == 1:
                    distance_increment = 0
                else:
                    distance_increment = random.randint(50, 300)  # km between stations
                cumulative_distance += distance_increment
                
                # Generate arrival and departure times
                if seq == 1:
                    departure_hour = random.randint(0, 23)
                    departure_min = random.choice([0, 15, 30, 45])
                    arrival_time = None
                    departure_time = time(departure_hour, departure_min)
                elif seq == len(route_stations):
                    arrival_time = time(random.randint(0, 23), random.choice([0, 15, 30, 45]))
                    departure_time = None
                else:
                    arrival_time = time(random.randint(0, 23), random.choice([0, 15, 30, 45]))
                    departure_time = time((arrival_time.hour + random.randint(0, 1)) % 24, 
                                        random.choice([0, 15, 30, 45]))
                
                route = TrainRoute(
                    train_id=train.id,
                    station_id=station.id,
                    sequence=seq,
                    arrival_time=arrival_time,
                    departure_time=departure_time,
                    distance_from_start=cumulative_distance
                )
                routes.append(route)
            
            total_routes += num_stations
            
            if (idx) % 100 == 0:
                print(f"  ✅ Created routes for {idx} trains ({total_routes} total stops)")
        
        db.session.bulk_save_objects(routes)
        db.session.commit()
        print(f"✓ Created {total_routes} route stops for {len(all_trains)} trains")
        print(f"  Average stops per train: {total_routes/len(all_trains):.1f}")
        print()
        
        # Seat availability is calculated dynamically based on bookings
        print("[SEAT AVAILABILITY] Skipping pre-population (calculated dynamically from bookings)")
        print("✓ Seat availability will be calculated in real-time based on train routes and bookings")
        print()
        
        print("="*70)
        print("                  ✓ Initialization Complete!")
        print("="*70)
        print()
        print("📊 Database Summary:")
        print(f"  • Stations: {len(all_stations):,} (including major Indian railway stations)")
        print(f"  • Trains: {len(all_trains):,} (Rajdhani, Shatabdi, Duronto, etc.)")
        print(f"  • Train Routes: {total_routes:,} route stops (avg {total_routes/len(all_trains):.1f} per train)")
        print(f"  • Seat Availability: Calculated dynamically")
        print()
        print("🔐 Admin Login:")
        print("  • Username: admin")
        print("  • Password: admin123")
        print()
        print("="*70)

if __name__ == '__main__':
    initialize_database()
