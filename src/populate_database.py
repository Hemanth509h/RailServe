#!/usr/bin/env python3
"""
Database Population Script for RailServe
Populates the database with 150 trains and comprehensive station network
"""

from .app import app, db
from .models import User, Train, Station, TrainRoute, Booking, Payment
from werkzeug.security import generate_password_hash
from datetime import datetime, time
import random

def populate_stations():
    """Create comprehensive Indian railway stations"""
    stations_data = [
        # Major Metropolitan Cities
        {'code': 'NDLS', 'name': 'New Delhi', 'city': 'Delhi', 'state': 'Delhi'},
        {'code': 'CST', 'name': 'Chhatrapati Shivaji Terminus', 'city': 'Mumbai', 'state': 'Maharashtra'},
        {'code': 'HWH', 'name': 'Howrah Junction', 'city': 'Kolkata', 'state': 'West Bengal'},
        {'code': 'MAS', 'name': 'Chennai Central', 'city': 'Chennai', 'state': 'Tamil Nadu'},
        {'code': 'SBC', 'name': 'Bangalore City', 'city': 'Bangalore', 'state': 'Karnataka'},
        {'code': 'PUNE', 'name': 'Pune Junction', 'city': 'Pune', 'state': 'Maharashtra'},
        {'code': 'AMD', 'name': 'Ahmedabad Junction', 'city': 'Ahmedabad', 'state': 'Gujarat'},
        {'code': 'JP', 'name': 'Jaipur Junction', 'city': 'Jaipur', 'state': 'Rajasthan'},
        
        # Major Junction Cities
        {'code': 'AGC', 'name': 'Agra Cantt', 'city': 'Agra', 'state': 'Uttar Pradesh'},
        {'code': 'ALLP', 'name': 'Allahabad Junction', 'city': 'Allahabad', 'state': 'Uttar Pradesh'},
        {'code': 'BCT', 'name': 'Mumbai Central', 'city': 'Mumbai', 'state': 'Maharashtra'},
        {'code': 'BZA', 'name': 'Vijayawada Junction', 'city': 'Vijayawada', 'state': 'Andhra Pradesh'},
        {'code': 'CNB', 'name': 'Kanpur Central', 'city': 'Kanpur', 'state': 'Uttar Pradesh'},
        {'code': 'GWL', 'name': 'Gwalior Junction', 'city': 'Gwalior', 'state': 'Madhya Pradesh'},
        {'code': 'JBP', 'name': 'Jabalpur Junction', 'city': 'Jabalpur', 'state': 'Madhya Pradesh'},
        {'code': 'VSKP', 'name': 'Visakhapatnam Junction', 'city': 'Visakhapatnam', 'state': 'Andhra Pradesh'},
        
        # Tourist and Heritage Cities
        {'code': 'UDZ', 'name': 'Udaipur City', 'city': 'Udaipur', 'state': 'Rajasthan'},
        {'code': 'JU', 'name': 'Jodhpur Junction', 'city': 'Jodhpur', 'state': 'Rajasthan'},
        {'code': 'BKN', 'name': 'Bikaner Junction', 'city': 'Bikaner', 'state': 'Rajasthan'},
        {'code': 'KOAA', 'name': 'Kochuveli', 'city': 'Thiruvananthapuram', 'state': 'Kerala'},
        {'code': 'ERS', 'name': 'Ernakulam Junction', 'city': 'Kochi', 'state': 'Kerala'},
        {'code': 'CLT', 'name': 'Kozhikode', 'city': 'Kozhikode', 'state': 'Kerala'},
        {'code': 'MDU', 'name': 'Madurai Junction', 'city': 'Madurai', 'state': 'Tamil Nadu'},
        {'code': 'CBE', 'name': 'Coimbatore Junction', 'city': 'Coimbatore', 'state': 'Tamil Nadu'},
        
        # Industrial Cities
        {'code': 'RJPB', 'name': 'Rjndr Ngr Bihar', 'city': 'Patna', 'state': 'Bihar'},
        {'code': 'PNBE', 'name': 'Patna Junction', 'city': 'Patna', 'state': 'Bihar'},
        {'code': 'RNC', 'name': 'Ranchi Junction', 'city': 'Ranchi', 'state': 'Jharkhand'},
        {'code': 'TATA', 'name': 'Tatanagar Junction', 'city': 'Jamshedpur', 'state': 'Jharkhand'},
        {'code': 'BSB', 'name': 'Varanasi Junction', 'city': 'Varanasi', 'state': 'Uttar Pradesh'},
        {'code': 'GKP', 'name': 'Gorakhpur Junction', 'city': 'Gorakhpur', 'state': 'Uttar Pradesh'},
        
        # Coastal Cities
        {'code': 'VAPI', 'name': 'Vapi', 'city': 'Vapi', 'state': 'Gujarat'},
        {'code': 'ST', 'name': 'Surat', 'city': 'Surat', 'state': 'Gujarat'},
        {'code': 'BRC', 'name': 'Vadodara Junction', 'city': 'Vadodara', 'state': 'Gujarat'},
        {'code': 'GOA', 'name': 'Goa', 'city': 'Panaji', 'state': 'Goa'},
        {'code': 'MAJN', 'name': 'Mangalore Junction', 'city': 'Mangalore', 'state': 'Karnataka'},
        {'code': 'QLM', 'name': 'Quilon Junction', 'city': 'Kollam', 'state': 'Kerala'},
        
        # Hill Stations and Special Destinations
        {'code': 'DWI', 'name': 'Dwarka', 'city': 'Dwarka', 'state': 'Gujarat'},
        {'code': 'RMM', 'name': 'Rameswaram', 'city': 'Rameswaram', 'state': 'Tamil Nadu'},
        {'code': 'PURI', 'name': 'Puri', 'city': 'Puri', 'state': 'Odisha'},
        {'code': 'HRD', 'name': 'Hardwar Junction', 'city': 'Haridwar', 'state': 'Uttarakhand'},
        {'code': 'RKSH', 'name': 'Rishikesh', 'city': 'Rishikesh', 'state': 'Uttarakhand'},
        {'code': 'DDD', 'name': 'Dehradun', 'city': 'Dehradun', 'state': 'Uttarakhand'},
        
        # Border and Strategic Cities
        {'code': 'ATR', 'name': 'Atari', 'city': 'Atari', 'state': 'Punjab'},
        {'code': 'JHL', 'name': 'Jammu Tawi', 'city': 'Jammu', 'state': 'Jammu and Kashmir'},
        {'code': 'SVDK', 'name': 'Shri Mata Vaishno Devi Katra', 'city': 'Katra', 'state': 'Jammu and Kashmir'},
        {'code': 'GHY', 'name': 'Guwahati', 'city': 'Guwahati', 'state': 'Assam'},
        {'code': 'DBRG', 'name': 'Dibrugarh', 'city': 'Dibrugarh', 'state': 'Assam'},
        
        # Additional Important Stations
        {'code': 'LKO', 'name': 'Lucknow Junction', 'city': 'Lucknow', 'state': 'Uttar Pradesh'},
        {'code': 'MB', 'name': 'Moradabad Junction', 'city': 'Moradabad', 'state': 'Uttar Pradesh'},
        {'code': 'BE', 'name': 'Bareilly Junction', 'city': 'Bareilly', 'state': 'Uttar Pradesh'},
        {'code': 'RTM', 'name': 'Ratlam Junction', 'city': 'Ratlam', 'state': 'Madhya Pradesh'},
        {'code': 'INDB', 'name': 'Indore Junction', 'city': 'Indore', 'state': 'Madhya Pradesh'},
        {'code': 'BPL', 'name': 'Bhopal Junction', 'city': 'Bhopal', 'state': 'Madhya Pradesh'},
        {'code': 'NGP', 'name': 'Nagpur Junction', 'city': 'Nagpur', 'state': 'Maharashtra'},
        {'code': 'AK', 'name': 'Akola Junction', 'city': 'Akola', 'state': 'Maharashtra'},
        {'code': 'BSL', 'name': 'Bhusaval Junction', 'city': 'Bhusaval', 'state': 'Maharashtra'},
    ]
    
    stations = []
    for station_data in stations_data:
        station = Station(**station_data)
        stations.append(station)
        db.session.add(station)
    
    db.session.commit()
    print(f"Added {len(stations)} stations")
    return stations

def populate_trains():
    """Create 150 trains with realistic details"""
    train_types = [
        ('Rajdhani Express', 'RAJ', 1800, 100),
        ('Shatabdi Express', 'SHTB', 1600, 80),
        ('Duronto Express', 'DRN', 1700, 90),
        ('Superfast Express', 'SF', 1200, 120),
        ('Mail Express', 'MAIL', 1000, 150),
        ('Passenger', 'PASS', 600, 200),
        ('Jan Shatabdi', 'JSHT', 800, 100),
        ('Garib Rath', 'GR', 900, 180),
        ('Humsafar Express', 'HMS', 1300, 110),
        ('Tejas Express', 'TEJ', 1500, 85),
        ('Vande Bharat Express', 'VB', 2000, 70),
        ('Double Decker Express', 'DD', 1100, 130),
    ]
    
    route_patterns = [
        ['NDLS', 'AGC', 'GWL', 'JBP', 'NGP', 'BZA', 'MAS'],  # North to South
        ['HWH', 'PNBE', 'CNB', 'ALLP', 'LKO', 'NDLS'],       # East to North
        ['CST', 'PUNE', 'SBC', 'CBE', 'MDU', 'MAS'],         # West to South
        ['AMD', 'RTM', 'INDB', 'BPL', 'JBP', 'NGP'],         # Gujarat to MP
        ['JP', 'UDZ', 'AMD', 'BRC', 'ST', 'CST'],            # Rajasthan to Mumbai
        ['KOAA', 'CLT', 'ERS', 'CBE', 'SBC', 'PUNE'],        # Kerala to Maharashtra
        ['VSKP', 'BZA', 'NGP', 'BPL', 'GWL', 'NDLS'],        # Coastal to Delhi
        ['BSB', 'ALLP', 'CNB', 'LKO', 'BE', 'MB', 'NDLS'],   # UP cities to Delhi
        ['GHY', 'RNC', 'TATA', 'HWH', 'PNBE', 'CNB'],        # Northeast to East
        ['JHL', 'NDLS', 'GWL', 'BPL', 'NGP', 'SBC'],         # J&K to South
    ]
    
    trains = []
    train_number = 12001
    
    for i in range(150):
        train_type, type_code, base_fare, capacity = random.choice(train_types)
        route = random.choice(route_patterns)
        
        # Some trains run in reverse direction
        if random.choice([True, False]):
            route = route[::-1]
        
        train_name = f"{route[0]} {route[-1]} {train_type}"
        
        train = Train(
            number=str(train_number),
            name=train_name,
            total_seats=capacity,
            available_seats=capacity,
            fare_per_km=base_fare / 100,  # Convert base fare to per km rate
            active=True
        )
        
        trains.append(train)
        db.session.add(train)
        train_number += 1
        
        if train_number > 99999:
            train_number = 10001  # Reset to avoid very large numbers
    
    db.session.commit()
    print(f"Added {len(trains)} trains")
    return trains

def populate_train_routes(trains, stations):
    """Create train routes connecting stations"""
    station_dict = {s.code: s for s in stations}
    
    route_patterns = [
        ['NDLS', 'AGC', 'GWL', 'JBP', 'NGP', 'BZA', 'MAS'],  # North to South
        ['HWH', 'PNBE', 'CNB', 'ALLP', 'LKO', 'NDLS'],       # East to North
        ['CST', 'PUNE', 'SBC', 'CBE', 'MDU', 'MAS'],         # West to South
        ['AMD', 'RTM', 'INDB', 'BPL', 'JBP', 'NGP'],         # Gujarat to MP
        ['JP', 'UDZ', 'AMD', 'BRC', 'ST', 'CST'],            # Rajasthan to Mumbai
        ['KOAA', 'CLT', 'ERS', 'CBE', 'SBC', 'PUNE'],        # Kerala to Maharashtra
        ['VSKP', 'BZA', 'NGP', 'BPL', 'GWL', 'NDLS'],        # Coastal to Delhi
        ['BSB', 'ALLP', 'CNB', 'LKO', 'BE', 'MB', 'NDLS'],   # UP cities to Delhi
        ['GHY', 'RNC', 'TATA', 'HWH', 'PNBE', 'CNB'],        # Northeast to East
        ['JHL', 'NDLS', 'GWL', 'BPL', 'NGP', 'SBC'],         # J&K to South
        ['PURI', 'VSKP', 'BZA', 'NGP', 'INDB', 'AMD'],       # East coast to West
        ['RMM', 'MDU', 'CBE', 'SBC', 'PUNE', 'CST'],         # South Tamil Nadu to Mumbai
        ['DWI', 'AMD', 'BRC', 'RTM', 'INDB', 'BPL'],         # Gujarat circuit
        ['HRD', 'DDD', 'NDLS', 'JP', 'UDZ', 'AMD'],          # North India tour
        ['MAJN', 'CBE', 'SBC', 'NGP', 'BPL', 'NDLS'],        # Coastal Karnataka to Delhi
    ]
    
    routes_created = 0
    
    for i, train in enumerate(trains):
        # Use pattern based on train index
        pattern_index = i % len(route_patterns)
        route_pattern = route_patterns[pattern_index]
        
        # Some trains run in reverse
        if i % 3 == 0:
            route_pattern = route_pattern[::-1]
        
        # Filter stations that exist in our database
        valid_stations = [code for code in route_pattern if code in station_dict]
        
        if len(valid_stations) < 2:
            continue
        
        total_distance = 0
        departure_time = time(6, 0)  # Start at 6 AM
        
        for seq, station_code in enumerate(valid_stations):
            station = station_dict[station_code]
            
            # Calculate distance (approximate)
            if seq > 0:
                total_distance += random.randint(100, 500)
            
            # Calculate arrival and departure times
            if seq == 0:
                arrival_time = None
                departure_time = time((6 + random.randint(0, 18)) % 24, random.randint(0, 59))
            elif seq == len(valid_stations) - 1:
                # Last station - only arrival
                hours_travel = total_distance // 50  # Approximate speed 50 km/h
                base_hour = 6 if departure_time is None else departure_time.hour
                arrival_hour = (base_hour + hours_travel) % 24
                arrival_time = time(arrival_hour, random.randint(0, 59))
                departure_time = None
            else:
                # Intermediate station
                hours_travel = total_distance // 60
                arrival_hour = (6 + hours_travel) % 24
                arrival_time = time(arrival_hour, random.randint(0, 59))
                departure_time = time((arrival_hour + random.randint(0, 1)) % 24, random.randint(0, 59))
            
            route = TrainRoute(
                train_id=train.id,
                station_id=station.id,
                sequence=seq + 1,
                arrival_time=arrival_time,
                departure_time=departure_time,
                distance_from_start=total_distance
            )
            
            db.session.add(route)
            routes_created += 1
    
    db.session.commit()
    print(f"Added {routes_created} train routes")

def create_sample_users():
    """Create sample users for testing"""
    users = [
        {
            'username': 'admin',
            'email': 'admin@railserve.com',
            'password': 'admin123',
            'role': 'super_admin',
            'full_name': 'System Administrator'
        },
        {
            'username': 'manager',
            'email': 'manager@railserve.com',
            'password': 'manager123',
            'role': 'admin',
            'full_name': 'Railway Manager'
        },
        {
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'user123',
            'role': 'user',
            'full_name': 'John Doe'
        },
        {
            'username': 'jane_smith',
            'email': 'jane@example.com',
            'password': 'user123',
            'role': 'user',
            'full_name': 'Jane Smith'
        },
        {
            'username': 'test_user',
            'email': 'test@example.com',
            'password': 'test123',
            'role': 'user',
            'full_name': 'Test User'
        }
    ]
    
    for user_data in users:
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if not existing_user:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password']),
                role=user_data['role']
            )
            db.session.add(user)
    
    db.session.commit()
    print("Added sample users")

def main():
    """Main function to populate the entire database"""
    with app.app_context():
        print("Starting database population...")
        
        # Create all tables
        db.create_all()
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("Clearing existing data...")
        TrainRoute.query.delete()
        Train.query.delete()
        Station.query.delete()
        
        # Populate stations first
        print("Populating stations...")
        stations = populate_stations()
        
        # Populate trains
        print("Populating trains...")
        trains = populate_trains()
        
        # Create train routes
        print("Creating train routes...")
        populate_train_routes(trains, stations)
        
        # Create sample users
        print("Creating sample users...")
        create_sample_users()
        
        print("\nDatabase population completed successfully!")
        print(f"Total stations: {len(stations)}")
        print(f"Total trains: {len(trains)}")
        print("Sample users created with following credentials:")
        print("Admin: admin / admin123")
        print("Manager: manager / manager123")
        print("User: john_doe / user123")

if __name__ == '__main__':
    main()