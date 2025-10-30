import csv
import os
from datetime import datetime, date, time, timedelta
from src.app import app, db
from src.models import (
    User, Station, Train, TrainRoute, SeatAvailability,
    TatkalTimeSlot
)
from werkzeug.security import generate_password_hash
import random

COACH_CLASSES = ['AC1', 'AC2', 'AC3', 'SL', '2S', 'CC']

def reset_database():
    print("\n[RESET] Dropping all existing tables...")
    db.drop_all()
    print("✓ All tables dropped")
    
    print("[RESET] Creating fresh database schema...")
    db.create_all()
    print("✓ Database schema created")

def load_stations_from_csv():
    print("\n[STATIONS] Loading stations from CSV...")
    csv_path = 'data/stations.csv'
    
    if not os.path.exists(csv_path):
        print(f"ERROR: {csv_path} not found!")
        return []
    
    stations_data = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stations_data.append({
                'name': row['name'],
                'code': row['code'],
                'city': row['city'],
                'state': row['state'],
                'active': row['active'].lower() == 'true',
                'created_at': datetime.utcnow()
            })
    
    db.session.bulk_insert_mappings(Station, stations_data)
    db.session.commit()
    print(f"✓ Loaded {len(stations_data)} stations")
    
    return Station.query.all()

def load_trains_from_csv():
    print("\n[TRAINS] Loading trains from CSV...")
    csv_path = 'data/trains.csv'
    
    if not os.path.exists(csv_path):
        print(f"ERROR: {csv_path} not found!")
        return []
    
    trains_data = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_seats = int(row['total_seats'])
            trains_data.append({
                'number': row['number'],
                'name': row['name'],
                'total_seats': total_seats,
                'available_seats': total_seats,
                'fare_per_km': float(row['fare_per_km']),
                'tatkal_seats': int(row['tatkal_seats']),
                'tatkal_fare_per_km': float(row['tatkal_fare_per_km']),
                'active': row['active'].lower() == 'true',
                'created_at': datetime.utcnow()
            })
    
    db.session.bulk_insert_mappings(Train, trains_data)
    db.session.commit()
    print(f"✓ Loaded {len(trains_data)} trains")
    
    return Train.query.all()

def create_train_routes(trains, stations):
    print("\n[ROUTES] Generating train routes...")
    
    if len(stations) < 5:
        print("ERROR: Not enough stations for routes!")
        return
    
    routes_data = []
    total_routes = 0
    batch_size = 50
    
    for idx, train in enumerate(trains):
        num_stops = random.randint(3, 8)
        selected_stations = random.sample(stations, min(num_stops, len(stations)))
        
        current_distance = 0
        base_hour = random.randint(0, 23)
        base_minute = random.choice([0, 15, 30, 45])
        current_minutes = base_hour * 60 + base_minute
        
        for seq, station in enumerate(selected_stations, 1):
            if seq > 1:
                current_distance += random.randint(50, 250)
                current_minutes += random.randint(30, 180)
            
            arrival_minutes = current_minutes if seq > 1 else None
            
            if seq < len(selected_stations):
                stop_duration = random.randint(2, 10)
                departure_minutes = current_minutes + stop_duration
            else:
                departure_minutes = None
            
            routes_data.append({
                'train_id': train.id,
                'station_id': station.id,
                'sequence': seq,
                'arrival_time': time(arrival_minutes // 60 % 24, arrival_minutes % 60) if arrival_minutes else None,
                'departure_time': time(departure_minutes // 60 % 24, departure_minutes % 60) if departure_minutes else None,
                'distance_from_start': current_distance
            })
            total_routes += 1
            
            if seq < len(selected_stations):
                current_minutes = departure_minutes
        
        if (idx + 1) % batch_size == 0:
            db.session.bulk_insert_mappings(TrainRoute, routes_data)
            db.session.commit()
            print(f"  Processed {idx + 1}/{len(trains)} trains...")
            routes_data = []
    
    if routes_data:
        db.session.bulk_insert_mappings(TrainRoute, routes_data)
        db.session.commit()
    
    print(f"✓ Created {total_routes} route entries")

def create_limited_seat_availability(trains, days_ahead=14, sample_trains=200):
    print(f"\n[AVAILABILITY] Generating seat availability for {days_ahead} days ahead...")
    
    today = date.today()
    total_records = 0
    
    train_sample = random.sample(trains, min(sample_trains, len(trains)))
    print(f"  Sampling {len(train_sample)} trains for availability data...")
    
    availability_data = []
    batch_size = 1000
    
    for train_idx, train in enumerate(train_sample):
        train_routes = TrainRoute.query.filter_by(train_id=train.id).order_by(TrainRoute.sequence).all()
        
        if len(train_routes) < 2:
            continue
        
        route_pairs = [(train_routes[i], train_routes[i+1]) for i in range(min(2, len(train_routes)-1))]
        
        for from_route, to_route in route_pairs:
            for days in range(days_ahead):
                journey_date = today + timedelta(days=days)
                
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
                    available = random.randint(int(total_class_seats * 0.4), total_class_seats)
                    
                    availability_data.append({
                        'train_id': train.id,
                        'from_station_id': from_route.station_id,
                        'to_station_id': to_route.station_id,
                        'journey_date': journey_date,
                        'coach_class': coach_class,
                        'quota': 'general',
                        'available_seats': available,
                        'waiting_list': random.randint(0, 15) if available < 10 else 0,
                        'rac_seats': random.randint(0, 5) if available < 20 else 0,
                        'last_updated': datetime.utcnow()
                    })
                    
                    if len(availability_data) >= batch_size:
                        db.session.bulk_insert_mappings(SeatAvailability, availability_data)
                        db.session.commit()
                        total_records += len(availability_data)
                        availability_data = []
        
        if (train_idx + 1) % 20 == 0:
            print(f"  Processed {train_idx + 1}/{len(train_sample)} trains, {total_records:,} records...")
    
    if availability_data:
        db.session.bulk_insert_mappings(SeatAvailability, availability_data)
        db.session.commit()
        total_records += len(availability_data)
    
    print(f"✓ Created {total_records:,} seat availability records")

def create_admin_user():
    print("\n[ADMIN] Creating admin user...")
    
    admin = User(
        username='admin',
        email='admin@railserve.com',
        password_hash=generate_password_hash('admin123'),
        role='super_admin',
        active=True
    )
    db.session.add(admin)
    db.session.commit()
    print("✓ Admin user created (username: admin, password: admin123)")
    return admin

def create_tatkal_timeslots(admin):
    print("\n[TATKAL] Creating Tatkal time slots...")
    
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
    print("✓ Tatkal time slots created")

def main():
    print("=" * 70)
    print(" " * 15 + "RailServe Database Initialization")
    print("=" * 70)
    
    with app.app_context():
        reset_database()
        
        print("\n[1/6] Creating admin user...")
        admin = create_admin_user()
        
        print("\n[2/6] Loading stations...")
        stations = load_stations_from_csv()
        print(f"  Total stations: {len(stations)}")
        
        print("\n[3/6] Loading trains...")
        trains = load_trains_from_csv()
        print(f"  Total trains: {len(trains)}")
        
        print("\n[4/6] Creating train routes...")
        create_train_routes(trains, stations)
        
        print("\n[5/6] Creating seat availability (limited to 14 days)...")
        create_limited_seat_availability(trains, days_ahead=14, sample_trains=200)
        
        print("\n[6/6] Creating Tatkal configurations...")
        create_tatkal_timeslots(admin)
        
        print("\n" + "=" * 70)
        print(" " * 20 + "Initialization Complete!")
        print("=" * 70)
        print(f"\n📊 Summary:")
        print(f"  • Stations: {Station.query.count():,}")
        print(f"  • Trains: {Train.query.count():,}")
        print(f"  • Train Routes: {TrainRoute.query.count():,}")
        print(f"  • Seat Availability: {SeatAvailability.query.count():,}")
        print(f"  • Admin Credentials: admin / admin123")
        print(f"\n✅ RailServe is ready to use!")
        print("=" * 70)

if __name__ == '__main__':
    main()
