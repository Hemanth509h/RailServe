"""
RailServe Database Initialization (PostgreSQL Only)
====================================================
This script initializes the PostgreSQL database with:
- 1000 Indian railway stations
- 1500 trains with seat numbers
- Train routes and seat availability
- Admin user and Tatkal time slots
"""

import os
import sys
import random
from datetime import datetime, date, time, timedelta
from werkzeug.security import generate_password_hash

# This section was already updated earlier in the file - database URL now comes from environment

from src.app import app
from src.database import db
from src.models import (
    User, Station, Train, TrainRoute, SeatAvailability, TatkalTimeSlot
)

# Coach classes in Indian Railways
COACH_CLASSES = ['AC1', 'AC2', 'AC3', 'SL', '2S', 'CC']

# Major Indian Railway Stations (40 major stations)
MAJOR_STATIONS = [
    ("New Delhi", "NDLS", "New Delhi", "Delhi"),
    ("Old Delhi", "DLI", "Delhi", "Delhi"),
    ("Hazrat Nizamuddin", "NZM", "New Delhi", "Delhi"),
    ("Anand Vihar Terminal", "ANVT", "New Delhi", "Delhi"),
    ("Chhatrapati Shivaji Maharaj Terminus", "CSTM", "Mumbai", "Maharashtra"),
    ("Mumbai Central", "BCT", "Mumbai", "Maharashtra"),
    ("Bandra Terminus", "BDTS", "Mumbai", "Maharashtra"),
    ("Lokmanya Tilak Terminus", "LTT", "Mumbai", "Maharashtra"),
    ("Howrah Junction", "HWH", "Kolkata", "West Bengal"),
    ("Sealdah", "SDAH", "Kolkata", "West Bengal"),
    ("Chennai Central", "MAS", "Chennai", "Tamil Nadu"),
    ("Chennai Egmore", "MS", "Chennai", "Tamil Nadu"),
    ("KSR Bengaluru", "SBC", "Bangalore", "Karnataka"),
    ("Yesvantpur Junction", "YPR", "Bangalore", "Karnataka"),
    ("Agra Cantonment", "AGC", "Agra", "Uttar Pradesh"),
    ("Ahmedabad Junction", "ADI", "Ahmedabad", "Gujarat"),
    ("Ambala Cantonment", "UMB", "Ambala", "Haryana"),
    ("Amritsar Junction", "ASR", "Amritsar", "Punjab"),
    ("Bhopal Junction", "BPL", "Bhopal", "Madhya Pradesh"),
    ("Chandigarh", "CDG", "Chandigarh", "Chandigarh"),
    ("Guwahati", "GHY", "Guwahati", "Assam"),
    ("Hyderabad Deccan", "HYB", "Hyderabad", "Telangana"),
    ("Jaipur Junction", "JP", "Jaipur", "Rajasthan"),
    ("Kanpur Central", "CNB", "Kanpur", "Uttar Pradesh"),
    ("Lucknow", "LKO", "Lucknow", "Uttar Pradesh"),
    ("Madurai Junction", "MDU", "Madurai", "Tamil Nadu"),
    ("Nagpur Junction", "NGP", "Nagpur", "Maharashtra"),
    ("Patna Junction", "PNBE", "Patna", "Bihar"),
    ("Pune Junction", "PUNE", "Pune", "Maharashtra"),
    ("Secunderabad Junction", "SC", "Secunderabad", "Telangana"),
    ("Thiruvananthapuram Central", "TVC", "Thiruvananthapuram", "Kerala"),
    ("Varanasi Junction", "BSB", "Varanasi", "Uttar Pradesh"),
    ("Vijayawada Junction", "BZA", "Vijayawada", "Andhra Pradesh"),
    ("Indore Junction", "INDB", "Indore", "Madhya Pradesh"),
    ("Surat", "ST", "Surat", "Gujarat"),
    ("Vadodara Junction", "BRC", "Vadodara", "Gujarat"),
    ("Rajkot Junction", "RJT", "Rajkot", "Gujarat"),
    ("Coimbatore Junction", "CBE", "Coimbatore", "Tamil Nadu"),
    ("Mysore Junction", "MYS", "Mysore", "Karnataka"),
    ("Jodhpur Junction", "JU", "Jodhpur", "Rajasthan")
]

# Indian cities for generating additional stations
INDIAN_CITIES = [
    ("Mumbai", "Maharashtra"), ("Delhi", "Delhi"), ("Bangalore", "Karnataka"),
    ("Hyderabad", "Telangana"), ("Ahmedabad", "Gujarat"), ("Chennai", "Tamil Nadu"),
    ("Kolkata", "West Bengal"), ("Pune", "Maharashtra"), ("Jaipur", "Rajasthan"),
    ("Lucknow", "Uttar Pradesh"), ("Kanpur", "Uttar Pradesh"), ("Nagpur", "Maharashtra"),
    ("Indore", "Madhya Pradesh"), ("Bhopal", "Madhya Pradesh"), ("Patna", "Bihar"),
    ("Vadodara", "Gujarat"), ("Ludhiana", "Punjab"), ("Agra", "Uttar Pradesh"),
    ("Nashik", "Maharashtra"), ("Meerut", "Uttar Pradesh"), ("Rajkot", "Gujarat"),
    ("Varanasi", "Uttar Pradesh"), ("Aurangabad", "Maharashtra"), ("Amritsar", "Punjab"),
    ("Allahabad", "Uttar Pradesh"), ("Ranchi", "Jharkhand"), ("Coimbatore", "Tamil Nadu"),
]

def reset_database():
    """Drop all tables and recreate schema"""
    print("\n[DATABASE] Resetting database...")
    db.drop_all()
    db.create_all()
    print("✓ All tables created")

def create_admin_and_tatkal():
    """Create admin user and Tatkal time slots"""
    print("\n[ADMIN & TATKAL] Creating admin user and Tatkal slots...")
    
    # Check if admin already exists
    existing_admin = User.query.filter_by(username='admin').first()
    if existing_admin:
        print("✓ Admin user already exists")
        admin = existing_admin
    else:
        admin = User(
            username='admin',
            email='admin@railserve.com',
            password_hash=generate_password_hash('admin123'),
            role='super_admin',
            active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin user created")
    
    # Tatkal time slots
    if not TatkalTimeSlot.query.first():
        ac_slot = TatkalTimeSlot(
            name='AC Classes Tatkal',
            coach_classes='AC1,AC2,AC3,CC',
            open_time=time(10, 0),
            close_time=time(23, 59),
            days_before_journey=1,
            active=True,
            created_by=admin.id
        )
        
        non_ac_slot = TatkalTimeSlot(
            name='Non-AC Classes Tatkal',
            coach_classes='SL,2S',
            open_time=time(11, 0),
            close_time=time(23, 59),
            days_before_journey=1,
            active=True,
            created_by=admin.id
        )
        
        db.session.add(ac_slot)
        db.session.add(non_ac_slot)
        db.session.commit()
        print("✓ Tatkal slots created")
    else:
        print("✓ Tatkal slots already exist")

def generate_stations(count=1000):
    """Generate stations"""
    print(f"\n[STATIONS] Generating {count} stations...")
    stations = []
    codes_used = set()
    names_used = set()
    
    # Add major stations first
    for name, code, city, state in MAJOR_STATIONS:
        stations.append(Station(
            name=name, code=code, city=city, state=state, active=True
        ))
        codes_used.add(code)
        names_used.add(name)
    
    # Generate additional stations
    station_types = ['Junction', 'Central', 'Terminal', 'City', 'Cantonment', 'Road', 'Station']
    
    for city, state in INDIAN_CITIES:
        for stype in station_types:
            if len(stations) >= count:
                break
            name = f"{city} {stype}"
            if name in names_used:
                continue
            
            code = ''.join([c[0] for c in name.split()[:3]]).upper()[:4]
            counter = 1
            while code in codes_used:
                code = code[:3] + str(counter)
                counter += 1
            
            stations.append(Station(
                name=name, code=code, city=city, state=state, active=True
            ))
            codes_used.add(code)
            names_used.add(name)
        
        if len(stations) >= count:
            break
    
    # Fill remaining with numbered stations
    counter = 1
    while len(stations) < count:
        city, state = random.choice(INDIAN_CITIES)
        name = f"{city} Station {counter}"
        if name not in names_used:
            code = f"S{counter:04d}"
            stations.append(Station(
                name=name, code=code, city=city, state=state, active=True
            ))
            names_used.add(name)
        counter += 1
    
    db.session.bulk_save_objects(stations)
    db.session.commit()
    print(f"✓ Created {len(stations)} stations")
    return Station.query.all()

def generate_trains(count=1500):
    """Generate trains with realistic Indian Railway fares"""
    print(f"\n[TRAINS] Generating {count} trains with realistic fares...")
    
    # Realistic Indian Railway fare structure (₹ per km)
    train_types = [
        {
            "name": "Rajdhani Express", 
            "prefix": "12", 
            "total_seats": 900, 
            "base_fare": 2.20,  # Premium AC train
            "tatkal_multiplier": 1.30,  # 30% Tatkal surcharge
            "tatkal_pct": 0.10
        },
        {
            "name": "Shatabdi Express", 
            "prefix": "12", 
            "total_seats": 600, 
            "base_fare": 2.80,  # Premium day train
            "tatkal_multiplier": 1.30,
            "tatkal_pct": 0.10
        },
        {
            "name": "Duronto Express", 
            "prefix": "22", 
            "total_seats": 950, 
            "base_fare": 1.75,  # Non-stop express
            "tatkal_multiplier": 1.30,
            "tatkal_pct": 0.10
        },
        {
            "name": "Mail/Express", 
            "prefix": "1", 
            "total_seats": 1400, 
            "base_fare": 0.60,  # Regular express (Sleeper class base)
            "tatkal_multiplier": 1.30,
            "tatkal_pct": 0.10
        },
        {
            "name": "Passenger", 
            "prefix": "5", 
            "total_seats": 1600, 
            "base_fare": 0.30,  # Local/slow trains
            "tatkal_multiplier": 1.10,  # Lower Tatkal for passenger
            "tatkal_pct": 0.05
        },
    ]
    
    trains = []
    for i in range(count):
        train_type = random.choice(train_types)
        source = random.choice(MAJOR_STATIONS[:20])
        dest = random.choice([s for s in MAJOR_STATIONS[:30] if s != source])
        
        number = f"{train_type['prefix']}{(10001 + i) % 10000:04d}"
        name = f"{source[2]}-{dest[2]} {train_type['name']}"
        total_seats = train_type['total_seats'] + random.randint(-100, 100)
        tatkal_seats = int(total_seats * train_type['tatkal_pct'])
        
        # Use realistic base fare
        base_fare = train_type['base_fare']
        tatkal_fare = base_fare * train_type['tatkal_multiplier']
        
        trains.append(Train(
            number=number,
            name=name,
            total_seats=total_seats,
            available_seats=total_seats,
            fare_per_km=round(base_fare, 2),
            tatkal_seats=tatkal_seats,
            tatkal_fare_per_km=round(tatkal_fare, 2),
            active=True
        ))
    
    db.session.bulk_save_objects(trains)
    db.session.commit()
    print(f"✓ Created {len(trains)} trains")
    return Train.query.all()

def create_train_routes(trains, stations):
    """Create realistic multi-station routes for all trains"""
    print("\n[ROUTES] Creating realistic multi-station train routes...")
    
    # Organize stations by major hubs for realistic route planning
    major_hubs = [s for s in stations if any(s.name.startswith(ms[0]) for ms in MAJOR_STATIONS)]
    other_stations = [s for s in stations if s not in major_hubs]
    
    routes = []
    total_routes = 0
    
    for idx, train in enumerate(trains):
        # Determine number of stops based on train type
        train_name = train.name.lower()
        if 'rajdhani' in train_name or 'duronto' in train_name:
            num_stops = random.randint(5, 8)  # Express trains with fewer stops
        elif 'shatabdi' in train_name:
            num_stops = random.randint(6, 10)  # Day trains with moderate stops
        elif 'passenger' in train_name:
            num_stops = random.randint(10, 15)  # Local trains with many stops
        else:
            num_stops = random.randint(7, 12)  # Regular express trains
        
        # Select stations for this route
        # Start and end with major hubs, include intermediate stations
        if len(major_hubs) >= 2:
            start_hub = random.choice(major_hubs)
            end_hub = random.choice([h for h in major_hubs if h.id != start_hub.id])
            
            # Mix of major and minor stations for intermediate stops
            intermediate_count = num_stops - 2
            intermediate = []
            if intermediate_count > 0:
                # Use mix of hubs and regular stations
                available_hubs = [h for h in major_hubs if h.id not in [start_hub.id, end_hub.id]]
                hub_count = min(len(available_hubs), intermediate_count // 2)
                intermediate.extend(random.sample(available_hubs, hub_count))
                
                remaining = intermediate_count - len(intermediate)
                if remaining > 0 and other_stations:
                    intermediate.extend(random.sample(other_stations, min(remaining, len(other_stations))))
            
            route_stations = [start_hub] + intermediate + [end_hub]
        else:
            # Fallback if not enough major hubs
            route_stations = random.sample(stations, min(num_stops, len(stations)))
        
        # Ensure unique stations in route
        seen = set()
        unique_route = []
        for s in route_stations:
            if s.id not in seen:
                unique_route.append(s)
                seen.add(s.id)
        route_stations = unique_route[:num_stops]
        
        # Generate route with realistic times and distances
        base_hour = random.randint(0, 23)
        base_minute = random.choice([0, 15, 30, 45])
        current_time = base_hour * 60 + base_minute  # Time in minutes from midnight
        cumulative_distance = 0
        
        for seq, station in enumerate(route_stations):
            is_first = (seq == 0)
            is_last = (seq == len(route_stations) - 1)
            
            # Calculate distance from previous station
            if seq > 0:
                # Realistic distance between stations: 50-200 km
                distance_increment = random.randint(50, 200)
                cumulative_distance += distance_increment
                
                # Calculate travel time (assuming avg 60 km/h)
                travel_minutes = distance_increment + random.randint(5, 15)
                current_time += travel_minutes
            
            # Convert current time to hours and minutes
            arrival_hour = (current_time // 60) % 24
            arrival_minute = current_time % 60
            arrival = time(arrival_hour, arrival_minute)
            
            # Departure time (halt time: 2-10 minutes, except last station)
            if not is_last:
                halt_minutes = random.randint(2, 10) if not is_first else 0
                departure_time_minutes = current_time + halt_minutes
                departure_hour = (departure_time_minutes // 60) % 24
                departure_minute = departure_time_minutes % 60
                departure = time(departure_hour, departure_minute)
                current_time = departure_time_minutes
            else:
                departure = None
            
            routes.append({
                'train_id': train.id,
                'station_id': station.id,
                'sequence': seq + 1,
                'arrival_time': None if is_first else arrival,
                'departure_time': departure,
                'distance_from_start': cumulative_distance
            })
            total_routes += 1
        
        # Progress indicator
        if (idx + 1) % 300 == 0:
            print(f"  Progress: {idx + 1}/{len(trains)} trains, {total_routes:,} route stops...")
    
    # Bulk insert all routes
    print(f"  Inserting {len(routes):,} route stops...")
    batch_size = 1000
    for i in range(0, len(routes), batch_size):
        batch = routes[i:i + batch_size]
        db.session.bulk_insert_mappings(TrainRoute, batch)
        db.session.commit()
    
    print(f"✓ Created {len(routes):,} train route stops for {len(trains)} trains")
    avg_stops = len(routes) / len(trains) if trains else 0
    print(f"  Average stops per train: {avg_stops:.1f}")

def create_seat_availability(trains):
    """Create seat availability for first 150 trains × 7 days"""
    print("\n[SEAT AVAILABILITY] Creating availability for 150 trains × 7 days...")
    
    today = date.today()
    availability = []
    total = 0
    selected_trains = trains[:150]
    
    for idx, train in enumerate(selected_trains):
        routes = TrainRoute.query.filter_by(train_id=train.id).order_by(TrainRoute.sequence).limit(2).all()
        
        if len(routes) < 2:
            continue
        
        from_station = routes[0].station_id
        to_station = routes[1].station_id
        
        for day in range(7):
            journey_date = today + timedelta(days=day)
            
            for coach_class in COACH_CLASSES:
                class_capacity = {
                    'AC1': int(train.total_seats * 0.05),
                    'AC2': int(train.total_seats * 0.15),
                    'AC3': int(train.total_seats * 0.25),
                    'SL': int(train.total_seats * 0.35),
                    '2S': int(train.total_seats * 0.15),
                    'CC': int(train.total_seats * 0.05)
                }
                
                total_class_seats = class_capacity.get(coach_class, 50)
                available_seats = random.randint(int(total_class_seats * 0.3), total_class_seats)
                
                availability.append({
                    'train_id': train.id,
                    'from_station_id': from_station,
                    'to_station_id': to_station,
                    'journey_date': journey_date,
                    'coach_class': coach_class,
                    'quota': 'general',
                    'available_seats': available_seats,
                    'waiting_list': random.randint(0, 20) if available_seats < 15 else 0,
                    'rac_seats': random.randint(0, 10) if available_seats < 25 else 0,
                    'last_updated': datetime.utcnow()
                })
                
                if len(availability) >= 500:
                    db.session.bulk_insert_mappings(SeatAvailability, availability)
                    db.session.commit()
                    total += len(availability)
                    availability = []
        
        if (idx + 1) % 30 == 0:
            print(f"  Progress: {idx + 1}/150 trains, {total:,} records...")
    
    if availability:
        db.session.bulk_insert_mappings(SeatAvailability, availability)
        db.session.commit()
        total += len(availability)
    
    print(f"✓ Created {total:,} seat availability records")

def main():
    """Main initialization function"""
    print("=" * 70)
    print(" " * 15 + "RailServe Database Initialization")
    print(" " * 20 + "(PostgreSQL Only)")
    print("=" * 70)
    print("\n📋 This will create:")
    print("  • 1000 Indian railway stations")
    print("  • 1500 trains with seat numbers")
    print("  • Realistic multi-station train routes (5-15 stations per train)")
    print("  • Seat availability (150 trains × 7 days)")
    print("  • Admin user and Tatkal time slots")
    print("=" * 70)
    
    with app.app_context():
        reset_database()
        create_admin_and_tatkal()
        stations = generate_stations(1000)
        trains = generate_trains(1500)
        create_train_routes(trains, stations)
        create_seat_availability(trains)
        
        print("\n" + "=" * 70)
        print(" " * 20 + "✓ Initialization Complete!")
        print("=" * 70)
        print(f"\n📊 Database Summary:")
        print(f"  • Stations: {Station.query.count():,}")
        print(f"  • Trains: {Train.query.count():,}")
        print(f"  • Train Routes: {TrainRoute.query.count():,}")
        print(f"  • Seat Availability: {SeatAvailability.query.count():,}")
        print(f"\n🔐 Admin Login:")
        print(f"  • Username: admin")
        print(f"  • Password: admin123")
        print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
