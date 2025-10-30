"""
Quick Test Data Script for RailServe
Creates a small sample dataset for immediate testing
"""

from src.app import app, db
from src.models import User, Station, Train, TrainRoute, SeatAvailability
from werkzeug.security import generate_password_hash
from datetime import datetime, date, time, timedelta
import random

def create_test_data():
    """Create minimal test data for quick testing"""
    with app.app_context():
        print("\n" + "="*60)
        print("Creating Quick Test Data")
        print("="*60)
        
        # Create tables
        print("\n[1/5] Creating database tables...")
        db.create_all()
        print("✓ Tables created")
        
        # Create admin user
        print("\n[2/5] Creating admin user...")
        admin = User.query.filter_by(username='admin').first()
        if not admin:
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
        else:
            print("  Admin user already exists")
        
        # Create sample stations
        print("\n[3/5] Creating 10 sample stations...")
        stations_data = [
            ('Mumbai Central', 'MMCT', 'Mumbai', 'Maharashtra'),
            ('Delhi Junction', 'DLI', 'Delhi', 'Delhi'),
            ('Bangalore City', 'BNC', 'Bangalore', 'Karnataka'),
            ('Chennai Central', 'MAS', 'Chennai', 'Tamil Nadu'),
            ('Kolkata Howrah', 'HWH', 'Kolkata', 'West Bengal'),
            ('Pune Junction', 'PUNE', 'Pune', 'Maharashtra'),
            ('Jaipur Junction', 'JP', 'Jaipur', 'Rajasthan'),
            ('Hyderabad Deccan', 'HYB', 'Hyderabad', 'Telangana'),
            ('Ahmedabad Junction', 'ADI', 'Ahmedabad', 'Gujarat'),
            ('Lucknow Junction', 'LKO', 'Lucknow', 'Uttar Pradesh')
        ]
        
        stations = []
        for name, code, city, state in stations_data:
            station = Station.query.filter_by(code=code).first()
            if not station:
                station = Station(name=name, code=code, city=city, state=state, active=True)
                db.session.add(station)
                stations.append(station)
            else:
                stations.append(station)
        
        db.session.commit()
        print(f"✓ Created {len(stations)} stations")
        
        # Create sample trains
        print("\n[4/5] Creating 5 sample trains...")
        trains_data = [
            ('12951', 'Mumbai Rajdhani Express', 1200, 15.50),
            ('12301', 'Bangalore Rajdhani', 1100, 14.00),
            ('12259', 'Chennai Duronto Express', 1000, 12.50),
            ('12009', 'Shatabdi Express', 800, 10.00),
            ('12423', 'Dibrugarh Rajdhani', 1300, 16.00)
        ]
        
        trains = []
        for number, name, total_seats, fare in trains_data:
            train = Train.query.filter_by(number=number).first()
            if not train:
                train = Train(
                    number=number,
                    name=name,
                    total_seats=total_seats,
                    available_seats=total_seats,
                    fare_per_km=fare,
                    tatkal_seats=int(total_seats * 0.1),
                    tatkal_fare_per_km=fare * 1.3,
                    active=True
                )
                db.session.add(train)
                trains.append(train)
            else:
                trains.append(train)
        
        db.session.commit()
        print(f"✓ Created {len(trains)} trains")
        
        # Create routes and seat availability
        print("\n[5/5] Creating routes and seat availability...")
        
        coach_classes = ['AC1', 'AC2', 'AC3', 'SL', '2S', 'CC']
        today = date.today()
        
        routes_created = 0
        availability_created = 0
        
        for train in trains:
            # Create a simple route (3-5 stations)
            num_stops = random.randint(3, 5)
            selected_stations = random.sample(stations, num_stops)
            
            distance = 0
            for seq, station in enumerate(selected_stations, 1):
                if seq > 1:
                    distance += random.randint(100, 300)
                
                route = TrainRoute.query.filter_by(
                    train_id=train.id,
                    station_id=station.id
                ).first()
                
                if not route:
                    route = TrainRoute(
                        train_id=train.id,
                        station_id=station.id,
                        sequence=seq,
                        arrival_time=time(random.randint(0, 23), random.choice([0, 15, 30, 45])) if seq > 1 else None,
                        departure_time=time(random.randint(0, 23), random.choice([0, 15, 30, 45])) if seq < num_stops else None,
                        distance_from_start=distance
                    )
                    db.session.add(route)
                    routes_created += 1
            
            # Create seat availability for next 7 days
            train_routes = TrainRoute.query.filter_by(train_id=train.id).order_by(TrainRoute.sequence).all()
            
            for i in range(len(train_routes) - 1):
                from_station = train_routes[i]
                to_station = train_routes[i + 1]
                
                for days_ahead in range(7):
                    journey_date = today + timedelta(days=days_ahead)
                    
                    for coach_class in coach_classes:
                        # Calculate capacity
                        class_capacity = {
                            'AC1': int(train.total_seats * 0.05),
                            'AC2': int(train.total_seats * 0.15),
                            'AC3': int(train.total_seats * 0.25),
                            'SL': int(train.total_seats * 0.35),
                            '2S': int(train.total_seats * 0.15),
                            'CC': int(train.total_seats * 0.05)
                        }
                        
                        total_seats = class_capacity.get(coach_class, 100)
                        available = random.randint(int(total_seats * 0.4), total_seats)
                        
                        for quota in ['general', 'tatkal', 'ladies']:
                            avail = SeatAvailability.query.filter_by(
                                train_id=train.id,
                                from_station_id=from_station.station_id,
                                to_station_id=to_station.station_id,
                                journey_date=journey_date,
                                coach_class=coach_class,
                                quota=quota
                            ).first()
                            
                            if not avail:
                                avail = SeatAvailability(
                                    train_id=train.id,
                                    from_station_id=from_station.station_id,
                                    to_station_id=to_station.station_id,
                                    journey_date=journey_date,
                                    coach_class=coach_class,
                                    quota=quota,
                                    available_seats=available,
                                    waiting_list=random.randint(0, 10) if available < 20 else 0,
                                    rac_seats=random.randint(0, 5) if available < 50 else 0,
                                    last_updated=datetime.utcnow()
                                )
                                db.session.add(avail)
                                availability_created += 1
        
        db.session.commit()
        print(f"✓ Created {routes_created} routes and {availability_created} seat availability records")
        
        print("\n" + "="*60)
        print("Quick Test Data Creation Complete!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"  • Stations: {Station.query.count()}")
        print(f"  • Trains: {Train.query.count()}")
        print(f"  • Routes: {TrainRoute.query.count()}")
        print(f"  • Seat Availability: {SeatAvailability.query.count()}")
        print(f"  • Admin: admin / admin123")
        print(f"\n✅ You can now test the seat availability feature!")
        print("="*60)

if __name__ == '__main__':
    create_test_data()
