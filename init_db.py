"""
RailServe Database Initialization Script
=========================================

This script initializes the RailServe database with:
- 1250 railway stations across India
- 1500 trains with routes
- Seat availability data for all coach classes
- Sample admin user for testing

Run this script once to set up the complete database:
    python init_db.py
"""

from src.app import app, db
from src.models import (
    User, Station, Train, TrainRoute, SeatAvailability,
    TatkalTimeSlot, LoyaltyProgram, NotificationPreferences
)
from werkzeug.security import generate_password_hash
from datetime import datetime, time, date, timedelta
from faker import Faker
import random

fake = Faker('en_IN')

INDIAN_CITIES = [
    ('Mumbai', 'Maharashtra'), ('Delhi', 'Delhi'), ('Bangalore', 'Karnataka'), 
    ('Hyderabad', 'Telangana'), ('Ahmedabad', 'Gujarat'), ('Chennai', 'Tamil Nadu'),
    ('Kolkata', 'West Bengal'), ('Pune', 'Maharashtra'), ('Jaipur', 'Rajasthan'),
    ('Lucknow', 'Uttar Pradesh'), ('Kanpur', 'Uttar Pradesh'), ('Nagpur', 'Maharashtra'),
    ('Indore', 'Madhya Pradesh'), ('Thane', 'Maharashtra'), ('Bhopal', 'Madhya Pradesh'),
    ('Visakhapatnam', 'Andhra Pradesh'), ('Pimpri-Chinchwad', 'Maharashtra'), 
    ('Patna', 'Bihar'), ('Vadodara', 'Gujarat'), ('Ghaziabad', 'Uttar Pradesh'),
    ('Ludhiana', 'Punjab'), ('Agra', 'Uttar Pradesh'), ('Nashik', 'Maharashtra'),
    ('Faridabad', 'Haryana'), ('Meerut', 'Uttar Pradesh'), ('Rajkot', 'Gujarat'),
    ('Kalyan-Dombivali', 'Maharashtra'), ('Vasai-Virar', 'Maharashtra'), 
    ('Varanasi', 'Uttar Pradesh'), ('Srinagar', 'Jammu and Kashmir'),
    ('Aurangabad', 'Maharashtra'), ('Dhanbad', 'Jharkhand'), ('Amritsar', 'Punjab'),
    ('Navi Mumbai', 'Maharashtra'), ('Allahabad', 'Uttar Pradesh'), 
    ('Ranchi', 'Jharkhand'), ('Howrah', 'West Bengal'), ('Coimbatore', 'Tamil Nadu'),
    ('Jabalpur', 'Madhya Pradesh'), ('Gwalior', 'Madhya Pradesh'),
    ('Vijayawada', 'Andhra Pradesh'), ('Jodhpur', 'Rajasthan'), ('Madurai', 'Tamil Nadu'),
    ('Raipur', 'Chhattisgarh'), ('Kota', 'Rajasthan'), ('Chandigarh', 'Chandigarh'),
    ('Guwahati', 'Assam'), ('Solapur', 'Maharashtra'), ('Hubballi-Dharwad', 'Karnataka'),
    ('Tiruchirappalli', 'Tamil Nadu'), ('Bareilly', 'Uttar Pradesh'),
    ('Mysore', 'Karnataka'), ('Tiruppur', 'Tamil Nadu'), ('Gurgaon', 'Haryana'),
    ('Aligarh', 'Uttar Pradesh'), ('Jalandhar', 'Punjab'), ('Bhubaneswar', 'Odisha'),
    ('Salem', 'Tamil Nadu'), ('Warangal', 'Telangana'), ('Guntur', 'Andhra Pradesh'),
    ('Bhiwandi', 'Maharashtra'), ('Saharanpur', 'Uttar Pradesh'), 
    ('Gorakhpur', 'Uttar Pradesh'), ('Bikaner', 'Rajasthan'), ('Amravati', 'Maharashtra'),
    ('Noida', 'Uttar Pradesh'), ('Jamshedpur', 'Jharkhand'), ('Bhilai', 'Chhattisgarh'),
    ('Cuttack', 'Odisha'), ('Firozabad', 'Uttar Pradesh'), ('Kochi', 'Kerala'),
    ('Nellore', 'Andhra Pradesh'), ('Bhavnagar', 'Gujarat'), ('Dehradun', 'Uttarakhand'),
    ('Durgapur', 'West Bengal'), ('Asansol', 'West Bengal'), ('Rourkela', 'Odisha'),
    ('Nanded', 'Maharashtra'), ('Kolhapur', 'Maharashtra'), ('Ajmer', 'Rajasthan'),
    ('Akola', 'Maharashtra'), ('Gulbarga', 'Karnataka'), ('Jamnagar', 'Gujarat'),
    ('Ujjain', 'Madhya Pradesh'), ('Loni', 'Uttar Pradesh'), ('Siliguri', 'West Bengal'),
    ('Jhansi', 'Uttar Pradesh'), ('Ulhasnagar', 'Maharashtra'), ('Jammu', 'Jammu and Kashmir'),
    ('Mangalore', 'Karnataka'), ('Erode', 'Tamil Nadu'), ('Belgaum', 'Karnataka'),
    ('Ambattur', 'Tamil Nadu'), ('Tirunelveli', 'Tamil Nadu'), ('Malegaon', 'Maharashtra'),
    ('Gaya', 'Bihar'), ('Jalgaon', 'Maharashtra'), ('Udaipur', 'Rajasthan'),
    ('Maheshtala', 'West Bengal'), ('Davanagere', 'Karnataka'), ('Kozhikode', 'Kerala'),
    ('Kurnool', 'Andhra Pradesh'), ('Rajpur Sonarpur', 'West Bengal'), 
    ('Rajahmundry', 'Andhra Pradesh'), ('Bokaro', 'Jharkhand'), ('South Dumdum', 'West Bengal'),
    ('Bellary', 'Karnataka'), ('Patiala', 'Punjab'), ('Gopalpur', 'West Bengal'),
    ('Agartala', 'Tripura'), ('Bhagalpur', 'Bihar'), ('Muzaffarnagar', 'Uttar Pradesh'),
    ('Bhatpara', 'West Bengal'), ('Panihati', 'West Bengal'), ('Latur', 'Maharashtra'),
    ('Dhule', 'Maharashtra'), ('Rohtak', 'Haryana'), ('Korba', 'Chhattisgarh'),
    ('Bhilwara', 'Rajasthan'), ('Berhampur', 'Odisha'), ('Muzaffarpur', 'Bihar'),
    ('Ahmednagar', 'Maharashtra'), ('Mathura', 'Uttar Pradesh'), ('Kollam', 'Kerala'),
    ('Avadi', 'Tamil Nadu'), ('Kadapa', 'Andhra Pradesh'), ('Kamarhati', 'West Bengal'),
    ('Sambalpur', 'Odisha'), ('Bilaspur', 'Chhattisgarh'), ('Shahjahanpur', 'Uttar Pradesh'),
    ('Satara', 'Maharashtra'), ('Bijapur', 'Karnataka'), ('Rampur', 'Uttar Pradesh'),
    ('Shivamogga', 'Karnataka'), ('Chandrapur', 'Maharashtra'), ('Junagadh', 'Gujarat'),
    ('Thrissur', 'Kerala'), ('Alwar', 'Rajasthan'), ('Bardhaman', 'West Bengal'),
    ('Kulti', 'West Bengal'), ('Kakinada', 'Andhra Pradesh'), ('Nizamabad', 'Telangana'),
    ('Parbhani', 'Maharashtra'), ('Tumkur', 'Karnataka'), ('Khammam', 'Telangana'),
    ('Ozhukarai', 'Puducherry'), ('Bihar Sharif', 'Bihar'), ('Panipat', 'Haryana'),
    ('Darbhanga', 'Bihar'), ('Bally', 'West Bengal'), ('Aizawl', 'Mizoram'),
    ('Dewas', 'Madhya Pradesh'), ('Ichalkaranji', 'Maharashtra'), ('Karnal', 'Haryana'),
    ('Bathinda', 'Punjab'), ('Jalna', 'Maharashtra'), ('Eluru', 'Andhra Pradesh'),
    ('Kirari Suleman Nagar', 'Delhi'), ('Barasat', 'West Bengal'), ('Purnia', 'Bihar'),
    ('Satna', 'Madhya Pradesh'), ('Mau', 'Uttar Pradesh'), ('Sonipat', 'Haryana'),
    ('Farrukhabad', 'Uttar Pradesh'), ('Sagar', 'Madhya Pradesh'), 
    ('Rourkela', 'Odisha'), ('Durg', 'Chhattisgarh'), ('Imphal', 'Manipur'),
    ('Ratlam', 'Madhya Pradesh'), ('Hapur', 'Uttar Pradesh'), ('Arrah', 'Bihar'),
    ('Karimnagar', 'Telangana'), ('Etawah', 'Uttar Pradesh'), ('Ambernath', 'Maharashtra'),
    ('North Dumdum', 'West Bengal'), ('Bharatpur', 'Rajasthan'), ('Begusarai', 'Bihar'),
    ('New Delhi', 'Delhi'), ('Chhapra', 'Bihar'), ('Kadapa', 'Andhra Pradesh'),
    ('Ramagundam', 'Telangana'), ('Pali', 'Rajasthan'), ('Satna', 'Madhya Pradesh'),
    ('Vizianagaram', 'Andhra Pradesh'), ('Katihar', 'Bihar'), ('Hardwar', 'Uttarakhand'),
    ('Sonipat', 'Haryana'), ('Nagercoil', 'Tamil Nadu'), ('Thanjavur', 'Tamil Nadu'),
    ('Murwara', 'Madhya Pradesh'), ('Naihati', 'West Bengal'), ('Sambhal', 'Uttar Pradesh'),
    ('Nadiad', 'Gujarat'), ('Yamunanagar', 'Haryana'), ('English Bazar', 'West Bengal'),
    ('Eluru', 'Andhra Pradesh'), ('Munger', 'Bihar'), ('Panchkula', 'Haryana'),
    ('Raayachuru', 'Karnataka'), ('Panvel', 'Maharashtra'), ('Deoghar', 'Jharkhand'),
    ('Ongole', 'Andhra Pradesh'), ('Nandyal', 'Andhra Pradesh'), ('Morena', 'Madhya Pradesh'),
    ('Bhiwani', 'Haryana'), ('Porbandar', 'Gujarat'), ('Palakkad', 'Kerala'),
    ('Anand', 'Gujarat'), ('Puruliya', 'West Bengal'), ('Barasat', 'West Bengal'),
    ('Kharagpur', 'West Bengal'), ('Unnao', 'Uttar Pradesh'), ('Shillong', 'Meghalaya'),
]

TRAIN_NAME_PREFIXES = [
    'Rajdhani', 'Shatabdi', 'Duronto', 'Garib Rath', 'Humsafar', 'Tejas', 'Vande Bharat',
    'Jan Shatabdi', 'Sampark Kranti', 'Yuva', 'Antyodaya', 'Suvidha', 'Double Decker',
    'AC Express', 'SF Express', 'Mail', 'Passenger', 'Express', 'Local', 'Intercity'
]

TRAIN_NAME_SUFFIXES = [
    'Express', 'Special', 'Link', 'Superfast', 'Intercity', 'Fast', 'Premium', 'Deluxe',
    'Zonal', 'Regional', 'Metro', 'Shuttle', 'AC', 'Mail', 'Passenger'
]

COACH_CLASSES = ['AC1', 'AC2', 'AC3', 'SL', '2S', 'CC']

def generate_station_code(city_name, existing_codes):
    """Generate unique 3-4 letter station code"""
    base_code = ''.join([c[0] for c in city_name.split()[:3]]).upper()
    if len(base_code) < 3:
        base_code = city_name[:3].upper()
    
    code = base_code[:4]
    counter = 1
    while code in existing_codes:
        code = base_code[:3] + str(counter)
        counter += 1
    
    return code

def create_stations(num_stations=1250):
    """Create railway stations"""
    print(f"\nGenerating {num_stations} stations...")
    stations = []
    existing_codes = set()
    existing_names = set()
    
    station_types = ['Junction', 'Central', 'Terminal', 'City', 'Cantt', 'Road']
    
    cities_used = 0
    for city, state in INDIAN_CITIES:
        if cities_used >= num_stations:
            break
            
        station_name = f"{city} Junction"
        if station_name not in existing_names:
            code = generate_station_code(city, existing_codes)
            station = Station(
                name=station_name,
                code=code,
                city=city,
                state=state,
                active=True
            )
            stations.append(station)
            existing_codes.add(code)
            existing_names.add(station_name)
            cities_used += 1
    
    for city, state in INDIAN_CITIES:
        if cities_used >= num_stations:
            break
            
        for stype in station_types:
            if cities_used >= num_stations:
                break
                
            station_name = f"{city} {stype}"
            if station_name not in existing_names:
                code = generate_station_code(f"{city}{stype}", existing_codes)
                station = Station(
                    name=station_name,
                    code=code,
                    city=city,
                    state=state,
                    active=True
                )
                stations.append(station)
                existing_codes.add(code)
                existing_names.add(station_name)
                cities_used += 1
    
    while cities_used < num_stations:
        city = fake.city()
        state = random.choice([s for _, s in INDIAN_CITIES])
        station_type = random.choice(station_types)
        station_name = f"{city} {station_type}"
        
        if station_name not in existing_names:
            code = generate_station_code(f"{city}{station_type}", existing_codes)
            station = Station(
                name=station_name,
                code=code,
                city=city,
                state=state,
                active=True
            )
            stations.append(station)
            existing_codes.add(code)
            existing_names.add(station_name)
            cities_used += 1
    
    db.session.bulk_save_objects(stations)
    db.session.commit()
    print(f"✓ Created {len(stations)} stations")
    return Station.query.all()

def create_trains(num_trains=1500, stations=None):
    """Create trains with routes"""
    print(f"\nGenerating {num_trains} trains...")
    trains = []
    existing_numbers = set()
    
    for i in range(num_trains):
        train_number = str(10000 + i).zfill(5)
        while train_number in existing_numbers:
            train_number = str(random.randint(10000, 99999))
        
        prefix = random.choice(TRAIN_NAME_PREFIXES)
        suffix = random.choice(TRAIN_NAME_SUFFIXES)
        
        source_station = random.choice(stations)
        dest_station = random.choice([s for s in stations if s.id != source_station.id])
        
        train_name = f"{source_station.city} {dest_station.city} {prefix} {suffix}"
        
        total_seats = random.randint(500, 1200)
        tatkal_seats = int(total_seats * 0.1)
        
        train = Train(
            number=train_number,
            name=train_name,
            total_seats=total_seats,
            available_seats=total_seats,
            fare_per_km=random.uniform(0.5, 2.5),
            tatkal_seats=tatkal_seats,
            tatkal_fare_per_km=random.uniform(1.5, 4.0),
            active=True
        )
        trains.append(train)
        existing_numbers.add(train_number)
        
        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1}/{num_trains} trains...")
    
    db.session.bulk_save_objects(trains)
    db.session.commit()
    print(f"✓ Created {len(trains)} trains")
    return Train.query.all()

def create_train_routes(trains, stations):
    """Create routes for trains"""
    print(f"\nGenerating train routes...")
    routes = []
    route_count = 0
    
    for train in trains:
        num_stops = random.randint(3, 15)
        selected_stations = random.sample(stations, min(num_stops, len(stations)))
        
        current_distance = 0
        current_time = time(random.randint(0, 23), random.choice([0, 15, 30, 45]))
        
        for seq, station in enumerate(selected_stations, 1):
            if seq > 1:
                current_distance += random.randint(50, 300)
            
            arrival = current_time if seq > 1 else None
            
            stop_duration = random.randint(2, 10) if seq < len(selected_stations) else 0
            departure_hour = (current_time.hour + (current_time.minute + stop_duration) // 60) % 24
            departure_minute = (current_time.minute + stop_duration) % 60
            departure = time(departure_hour, departure_minute)
            
            route = TrainRoute(
                train_id=train.id,
                station_id=station.id,
                sequence=seq,
                arrival_time=arrival,
                departure_time=departure if seq < len(selected_stations) else None,
                distance_from_start=current_distance
            )
            routes.append(route)
            route_count += 1
            
            current_time = departure
        
        if route_count % 1000 == 0:
            print(f"  Generated {route_count} route entries...")
    
    db.session.bulk_save_objects(routes)
    db.session.commit()
    print(f"✓ Created {len(routes)} route entries for {len(trains)} trains")

def create_seat_availability(trains, stations):
    """Create seat availability data for all coach classes"""
    print(f"\nGenerating seat availability data...")
    availability_records = []
    
    today = date.today()
    
    train_sample = random.sample(trains, min(500, len(trains)))
    
    for train in train_sample:
        train_routes = TrainRoute.query.filter_by(train_id=train.id).order_by(TrainRoute.sequence).all()
        
        if len(train_routes) < 2:
            continue
        
        for i in range(min(5, len(train_routes) - 1)):
            from_station = train_routes[i]
            to_station = train_routes[i + 1]
            
            for days_ahead in range(90):
                journey_date = today + timedelta(days=days_ahead)
                
                for coach_class in COACH_CLASSES:
                    class_capacity = {
                        'AC1': int(train.total_seats * 0.05),
                        'AC2': int(train.total_seats * 0.15),
                        'AC3': int(train.total_seats * 0.25),
                        'SL': int(train.total_seats * 0.35),
                        '2S': int(train.total_seats * 0.15),
                        'CC': int(train.total_seats * 0.05)
                    }
                    
                    total_class_seats = class_capacity.get(coach_class, 100)
                    available = random.randint(int(total_class_seats * 0.3), total_class_seats)
                    
                    for quota in ['general', 'tatkal', 'ladies']:
                        availability = SeatAvailability(
                            train_id=train.id,
                            from_station_id=from_station.station_id,
                            to_station_id=to_station.station_id,
                            journey_date=journey_date,
                            coach_class=coach_class,
                            quota=quota,
                            available_seats=available,
                            waiting_list=random.randint(0, 20) if available < 10 else 0,
                            rac_seats=random.randint(0, 5) if available < 30 else 0,
                            last_updated=datetime.utcnow()
                        )
                        availability_records.append(availability)
    
    db.session.bulk_save_objects(availability_records)
    db.session.commit()
    print(f"✓ Created {len(availability_records)} seat availability records")

def create_admin_user():
    """Create default admin user"""
    print("\nCreating admin user...")
    
    existing_admin = User.query.filter_by(username='admin').first()
    if existing_admin:
        print("  Admin user already exists")
        return existing_admin
    
    admin = User(
        username='admin',
        email='admin@railserve.com',
        password_hash=generate_password_hash('admin123'),
        role='super_admin',
        active=True
    )
    db.session.add(admin)
    db.session.commit()
    print(f"✓ Created admin user (username: admin, password: admin123)")
    return admin

def create_tatkal_timeslots():
    """Create Tatkal time slot configurations"""
    print("\nCreating Tatkal time slots...")
    
    existing = TatkalTimeSlot.query.first()
    if existing:
        print("  Tatkal time slots already exist")
        return
    
    admin = User.query.filter_by(role='super_admin').first()
    
    ac_slot = TatkalTimeSlot(
        name='AC Classes Tatkal',
        coach_classes='AC1,AC2,AC3,CC',
        open_time=time(10, 0),
        close_time=time(23, 59),
        days_before_journey=1,
        active=True,
        created_by=admin.id if admin else None
    )
    
    non_ac_slot = TatkalTimeSlot(
        name='Non-AC Classes Tatkal',
        coach_classes='SL,2S',
        open_time=time(11, 0),
        close_time=time(23, 59),
        days_before_journey=1,
        active=True,
        created_by=admin.id if admin else None
    )
    
    db.session.add(ac_slot)
    db.session.add(non_ac_slot)
    db.session.commit()
    print("✓ Created Tatkal time slots")

def main():
    """Main initialization function"""
    print("="*60)
    print("RailServe Database Initialization")
    print("="*60)
    
    with app.app_context():
        print("\n[1/6] Creating database tables...")
        db.create_all()
        print("✓ Database tables created")
        
        print("\n[2/6] Creating admin user...")
        admin = create_admin_user()
        
        print("\n[3/6] Creating stations...")
        stations = create_stations(num_stations=1250)
        
        print("\n[4/6] Creating trains...")
        trains = create_trains(num_trains=1500, stations=stations)
        
        print("\n[5/6] Creating train routes...")
        create_train_routes(trains, stations)
        
        print("\n[6/6] Creating seat availability data...")
        create_seat_availability(trains, stations)
        
        print("\n[7/7] Creating Tatkal configurations...")
        create_tatkal_timeslots()
        
        print("\n" + "="*60)
        print("Database Initialization Complete!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"  • Stations: {Station.query.count()}")
        print(f"  • Trains: {Train.query.count()}")
        print(f"  • Train Routes: {TrainRoute.query.count()}")
        print(f"  • Seat Availability Records: {SeatAvailability.query.count()}")
        print(f"  • Admin User: admin / admin123")
        print(f"\n✅ RailServe is ready to use!")
        print("="*60)

if __name__ == '__main__':
    main()
