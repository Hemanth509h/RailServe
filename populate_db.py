#!/usr/bin/env python3
"""
Simple Database Population Script for RailServe
Creates stations, trains, and sample users for the railway booking system.
"""

import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import app, db
from src.models import User, Train, Station, TrainRoute
from werkzeug.security import generate_password_hash
from datetime import time
import random

def populate_database():
    """Populate the database with sample data"""
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        # Clear existing data (optional)
        print("Clearing existing data...")
        TrainRoute.query.delete()
        Train.query.delete()
        Station.query.delete()
        User.query.delete()
        
        # Create stations (1000 stations)
        print("Creating 1000 stations...")
        
        # Major stations (first 50)
        major_stations = [
            {'code': 'NDLS', 'name': 'New Delhi', 'city': 'Delhi', 'state': 'Delhi'},
            {'code': 'CST', 'name': 'Chhatrapati Shivaji Terminus', 'city': 'Mumbai', 'state': 'Maharashtra'},
            {'code': 'HWH', 'name': 'Howrah Junction', 'city': 'Kolkata', 'state': 'West Bengal'},
            {'code': 'MAS', 'name': 'Chennai Central', 'city': 'Chennai', 'state': 'Tamil Nadu'},
            {'code': 'SBC', 'name': 'Bangalore City', 'city': 'Bangalore', 'state': 'Karnataka'},
            {'code': 'PUNE', 'name': 'Pune Junction', 'city': 'Pune', 'state': 'Maharashtra'},
            {'code': 'AMD', 'name': 'Ahmedabad Junction', 'city': 'Ahmedabad', 'state': 'Gujarat'},
            {'code': 'JP', 'name': 'Jaipur Junction', 'city': 'Jaipur', 'state': 'Rajasthan'},
            {'code': 'AGC', 'name': 'Agra Cantt', 'city': 'Agra', 'state': 'Uttar Pradesh'},
            {'code': 'LKO', 'name': 'Lucknow Junction', 'city': 'Lucknow', 'state': 'Uttar Pradesh'},
            {'code': 'BCT', 'name': 'Mumbai Central', 'city': 'Mumbai', 'state': 'Maharashtra'},
            {'code': 'BZA', 'name': 'Vijayawada Junction', 'city': 'Vijayawada', 'state': 'Andhra Pradesh'},
            {'code': 'CNB', 'name': 'Kanpur Central', 'city': 'Kanpur', 'state': 'Uttar Pradesh'},
            {'code': 'GWL', 'name': 'Gwalior Junction', 'city': 'Gwalior', 'state': 'Madhya Pradesh'},
            {'code': 'JBP', 'name': 'Jabalpur Junction', 'city': 'Jabalpur', 'state': 'Madhya Pradesh'},
            {'code': 'VSKP', 'name': 'Visakhapatnam Junction', 'city': 'Visakhapatnam', 'state': 'Andhra Pradesh'},
            {'code': 'UDZ', 'name': 'Udaipur City', 'city': 'Udaipur', 'state': 'Rajasthan'},
            {'code': 'JU', 'name': 'Jodhpur Junction', 'city': 'Jodhpur', 'state': 'Rajasthan'},
            {'code': 'BKN', 'name': 'Bikaner Junction', 'city': 'Bikaner', 'state': 'Rajasthan'},
            {'code': 'KOAA', 'name': 'Kochuveli', 'city': 'Thiruvananthapuram', 'state': 'Kerala'},
            {'code': 'ERS', 'name': 'Ernakulam Junction', 'city': 'Kochi', 'state': 'Kerala'},
            {'code': 'CLT', 'name': 'Kozhikode', 'city': 'Kozhikode', 'state': 'Kerala'},
            {'code': 'MDU', 'name': 'Madurai Junction', 'city': 'Madurai', 'state': 'Tamil Nadu'},
            {'code': 'CBE', 'name': 'Coimbatore Junction', 'city': 'Coimbatore', 'state': 'Tamil Nadu'},
            {'code': 'RJPB', 'name': 'Rjndr Ngr Bihar', 'city': 'Patna', 'state': 'Bihar'},
            {'code': 'PNBE', 'name': 'Patna Junction', 'city': 'Patna', 'state': 'Bihar'},
            {'code': 'RNC', 'name': 'Ranchi Junction', 'city': 'Ranchi', 'state': 'Jharkhand'},
            {'code': 'TATA', 'name': 'Tatanagar Junction', 'city': 'Jamshedpur', 'state': 'Jharkhand'},
            {'code': 'BSB', 'name': 'Varanasi Junction', 'city': 'Varanasi', 'state': 'Uttar Pradesh'},
            {'code': 'GKP', 'name': 'Gorakhpur Junction', 'city': 'Gorakhpur', 'state': 'Uttar Pradesh'},
            {'code': 'VAPI', 'name': 'Vapi', 'city': 'Vapi', 'state': 'Gujarat'},
            {'code': 'ST', 'name': 'Surat', 'city': 'Surat', 'state': 'Gujarat'},
            {'code': 'BRC', 'name': 'Vadodara Junction', 'city': 'Vadodara', 'state': 'Gujarat'},
            {'code': 'GOA', 'name': 'Goa', 'city': 'Panaji', 'state': 'Goa'},
            {'code': 'MAJN', 'name': 'Mangalore Junction', 'city': 'Mangalore', 'state': 'Karnataka'},
            {'code': 'QLM', 'name': 'Quilon Junction', 'city': 'Kollam', 'state': 'Kerala'},
            {'code': 'DWI', 'name': 'Dwarka', 'city': 'Dwarka', 'state': 'Gujarat'},
            {'code': 'RMM', 'name': 'Rameswaram', 'city': 'Rameswaram', 'state': 'Tamil Nadu'},
            {'code': 'PURI', 'name': 'Puri', 'city': 'Puri', 'state': 'Odisha'},
            {'code': 'HRD', 'name': 'Hardwar Junction', 'city': 'Haridwar', 'state': 'Uttarakhand'},
            {'code': 'RKSH', 'name': 'Rishikesh', 'city': 'Rishikesh', 'state': 'Uttarakhand'},
            {'code': 'DDD', 'name': 'Dehradun', 'city': 'Dehradun', 'state': 'Uttarakhand'},
            {'code': 'ATR', 'name': 'Atari', 'city': 'Atari', 'state': 'Punjab'},
            {'code': 'JHL', 'name': 'Jammu Tawi', 'city': 'Jammu', 'state': 'Jammu and Kashmir'},
            {'code': 'SVDK', 'name': 'Shri Mata Vaishno Devi Katra', 'city': 'Katra', 'state': 'Jammu and Kashmir'},
            {'code': 'GHY', 'name': 'Guwahati', 'city': 'Guwahati', 'state': 'Assam'},
            {'code': 'DBRG', 'name': 'Dibrugarh', 'city': 'Dibrugarh', 'state': 'Assam'},
            {'code': 'MB', 'name': 'Moradabad Junction', 'city': 'Moradabad', 'state': 'Uttar Pradesh'},
            {'code': 'BE', 'name': 'Bareilly Junction', 'city': 'Bareilly', 'state': 'Uttar Pradesh'},
            {'code': 'RTM', 'name': 'Ratlam Junction', 'city': 'Ratlam', 'state': 'Madhya Pradesh'},
        ]
        
        # Indian states and sample cities for generating realistic station data
        states_cities = {
            'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Agra', 'Varanasi', 'Allahabad', 'Meerut', 'Bareilly', 'Aligarh', 'Moradabad', 'Gorakhpur'],
            'Maharashtra': ['Mumbai', 'Pune', 'Nagpur', 'Nashik', 'Aurangabad', 'Solapur', 'Amravati', 'Kolhapur', 'Sangli', 'Ahmednagar'],
            'Tamil Nadu': ['Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem', 'Erode', 'Tirunelveli', 'Vellore', 'Thoothukudi', 'Dindigul'],
            'Karnataka': ['Bangalore', 'Mysore', 'Hubli', 'Mangalore', 'Belgaum', 'Gulbarga', 'Davanagere', 'Bellary', 'Bijapur', 'Shimoga'],
            'Gujarat': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Bhavnagar', 'Jamnagar', 'Junagadh', 'Gandhinagar', 'Anand', 'Bharuch'],
            'Rajasthan': ['Jaipur', 'Jodhpur', 'Udaipur', 'Bikaner', 'Ajmer', 'Alwar', 'Bharatpur', 'Pali', 'Sikar', 'Tonk'],
            'West Bengal': ['Kolkata', 'Howrah', 'Durgapur', 'Asansol', 'Siliguri', 'Burdwan', 'Malda', 'Kharagpur', 'Haldia', 'Krishnanagar'],
            'Madhya Pradesh': ['Bhopal', 'Indore', 'Jabalpur', 'Gwalior', 'Ujjain', 'Sagar', 'Dewas', 'Satna', 'Ratlam', 'Rewa'],
            'Kerala': ['Thiruvananthapuram', 'Kochi', 'Kozhikode', 'Thrissur', 'Kollam', 'Palakkad', 'Alappuzha', 'Malappuram', 'Kannur', 'Kasaragod'],
            'Andhra Pradesh': ['Visakhapatnam', 'Vijayawada', 'Guntur', 'Nellore', 'Kurnool', 'Rajahmundry', 'Kadapa', 'Kakinada', 'Anantapur', 'Tirupati'],
            'Telangana': ['Hyderabad', 'Warangal', 'Nizamabad', 'Khammam', 'Karimnagar', 'Mahbubnagar', 'Nalgonda', 'Adilabad', 'Miryalaguda', 'Suryapet'],
            'Odisha': ['Bhubaneswar', 'Cuttack', 'Rourkela', 'Brahmapur', 'Sambalpur', 'Puri', 'Balasore', 'Bhadrak', 'Baripada', 'Jharsuguda'],
            'Punjab': ['Chandigarh', 'Ludhiana', 'Amritsar', 'Jalandhar', 'Patiala', 'Bathinda', 'Mohali', 'Hoshiarpur', 'Batala', 'Pathankot'],
            'Haryana': ['Gurgaon', 'Faridabad', 'Panipat', 'Ambala', 'Yamunanagar', 'Rohtak', 'Hisar', 'Karnal', 'Sonipat', 'Panchkula'],
            'Bihar': ['Patna', 'Gaya', 'Bhagalpur', 'Muzaffarpur', 'Purnia', 'Darbhanga', 'Bihar Sharif', 'Arrah', 'Begusarai', 'Katihar'],
            'Jharkhand': ['Ranchi', 'Jamshedpur', 'Dhanbad', 'Bokaro', 'Deoghar', 'Phusro', 'Hazaribagh', 'Giridih', 'Ramgarh', 'Medininagar'],
            'Assam': ['Guwahati', 'Silchar', 'Dibrugarh', 'Jorhat', 'Nagaon', 'Tinsukia', 'Tezpur', 'Bongaigaon', 'Karimganj', 'Sivasagar'],
            'Uttarakhand': ['Dehradun', 'Haridwar', 'Roorkee', 'Haldwani', 'Rudrapur', 'Kashipur', 'Rishikesh', 'Kotdwar', 'Jaspur', 'Kichha'],
            'Himachal Pradesh': ['Shimla', 'Dharamshala', 'Solan', 'Mandi', 'Palampur', 'Una', 'Kullu', 'Hamirpur', 'Bilaspur', 'Chamba'],
            'Jammu and Kashmir': ['Jammu', 'Srinagar', 'Kathua', 'Udhampur', 'Anantnag', 'Baramulla', 'Kupwara', 'Pulwama', 'Rajouri', 'Poonch'],
            'Chhattisgarh': ['Raipur', 'Bhilai', 'Bilaspur', 'Korba', 'Durg', 'Jagdalpur', 'Ambikapur', 'Chirmiri', 'Dhamtari', 'Mahasamund'],
            'Goa': ['Panaji', 'Margao', 'Vasco da Gama', 'Mapusa', 'Ponda', 'Bicholim', 'Curchorem', 'Sanquelim', 'Cuncolim', 'Quepem']
        }
        
        stations_data = major_stations.copy()
        
        # Generate additional 950 stations to reach 1000 total
        station_counter = 1001
        existing_names = {station['name'] for station in major_stations}
        existing_codes = {station['code'] for station in major_stations}
        
        for state, cities in states_cities.items():
            for city in cities:
                for i in range(1, 6):  # 5 stations per city
                    station_suffix = ['Jn', 'City', 'Cantt', 'Town', 'Central'][i-1]
                    base_code = f"{city[:3].upper()}{i:02d}"
                    name = f"{city} {station_suffix}"
                    
                    # Ensure unique code
                    code = base_code
                    counter = 1
                    while code in existing_codes:
                        code = f"{city[:3].upper()}{i:02d}{counter}"
                        counter += 1
                    
                    # Skip if name already exists, but ensure we have unique code
                    if name not in existing_names:
                        stations_data.append({
                            'code': code,
                            'name': name,
                            'city': city,
                            'state': state
                        })
                        existing_names.add(name)
                        existing_codes.add(code)
                    
                    station_counter += 1
                    if len(stations_data) >= 1000:
                        break
                if len(stations_data) >= 1000:
                    break
            if len(stations_data) >= 1000:
                break
        
        stations = []
        for station_data in stations_data:
            station = Station(**station_data)
            stations.append(station)
            db.session.add(station)
        
        db.session.commit()
        print(f"Created {len(stations)} stations")
        
        # Create trains (500 trains)
        print("Creating 500 trains...")
        
        train_types = [
            ('Rajdhani Express', 350, 18.0),
            ('Shatabdi Express', 320, 16.0),
            ('Duronto Express', 380, 17.0),
            ('Superfast Express', 450, 14.0),
            ('Mail Express', 500, 12.0),
            ('Passenger', 600, 8.0),
            ('Jan Shatabdi', 280, 10.0),
            ('Garib Rath', 550, 9.0),
            ('Humsafar Express', 400, 15.0),
            ('Tejas Express', 300, 20.0),
            ('Vande Bharat Express', 250, 25.0),
            ('Double Decker Express', 480, 13.0),
            ('Intercity Express', 420, 11.0),
            ('Express', 500, 10.0),
            ('Local', 800, 6.0)
        ]
        
        # Route patterns for train generation
        route_patterns = [
            ['New Delhi', 'Mumbai'],
            ['Kolkata', 'Chennai'], 
            ['Bangalore', 'Delhi'],
            ['Hyderabad', 'Pune'],
            ['Ahmedabad', 'Kolkata'],
            ['Jaipur', 'Mumbai'],
            ['Chennai', 'Bangalore'],
            ['Delhi', 'Kolkata'],
            ['Mumbai', 'Chennai'],
            ['Pune', 'Delhi'],
            ['Goa', 'Mumbai'],
            ['Kerala', 'Delhi'],
            ['Rajasthan', 'Gujarat'],
            ['Punjab', 'Haryana'],
            ['Bihar', 'West Bengal'],
            ['Assam', 'Delhi'],
            ['Karnataka', 'Tamil Nadu'],
            ['Madhya Pradesh', 'Maharashtra'],
            ['Uttar Pradesh', 'Delhi'],
            ['Odisha', 'West Bengal']
        ]
        
        trains = []
        train_number = 10001
        
        for i in range(500):
            train_type, capacity, base_fare = random.choice(train_types)
            route = random.choice(route_patterns)
            
            # Some variation in capacity and fare
            capacity += random.randint(-50, 100)
            base_fare += random.uniform(-2.0, 3.0)
            
            # Ensure minimum values
            capacity = max(150, capacity)
            base_fare = max(5.0, base_fare)
            
            train_name = f"{route[0]} {route[1]} {train_type}"
            
            # Calculate Tatkal configuration
            tatkal_seats = int(capacity * 0.15)  # 15% Tatkal quota
            tatkal_fare = round(base_fare * 1.5, 2)  # 1.5x regular fare
            
            train = Train(
                number=str(train_number),
                name=train_name,
                total_seats=capacity,
                available_seats=capacity,
                fare_per_km=round(base_fare, 2),
                tatkal_seats=tatkal_seats,
                tatkal_fare_per_km=tatkal_fare,
                active=True
            )
            
            trains.append(train)
            db.session.add(train)
            train_number += 1
            
            # Progress indicator
            if (i + 1) % 100 == 0:
                print(f"  Generated {i + 1}/500 trains...")
        
        db.session.commit()
        print(f"Created {len(trains)} trains")
        
        # Create sample users
        print("Creating sample users...")
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@railserve.com', 
                'password': 'admin123',
                'role': 'super_admin'
            },
            {
                'username': 'manager',
                'email': 'manager@railserve.com',
                'password': 'manager123', 
                'role': 'admin'
            },
            {
                'username': 'john_doe',
                'email': 'john@example.com',
                'password': 'user123',
                'role': 'user'
            },
            {
                'username': 'test_user',
                'email': 'test@example.com',
                'password': 'test123',
                'role': 'user'
            }
        ]
        
        for user_data in users_data:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password']),
                role=user_data['role']
            )
            db.session.add(user)
        
        db.session.commit()
        print(f"Created {len(users_data)} sample users")
        
        # Create comprehensive train routes (1000+ routes)
        print("Creating train routes for all trains...")
        route_count = 0
        
        # Get all trains and stations
        all_trains = Train.query.all()
        all_stations = Station.query.all()
        
        # Group stations by state for realistic routing
        stations_by_state = {}
        for station in all_stations:
            state = station.state
            if state not in stations_by_state:
                stations_by_state[state] = []
            stations_by_state[state].append(station)
        
        # Major route patterns (state-to-state connections)
        major_routes = [
            ['Delhi', 'Uttar Pradesh', 'Bihar', 'West Bengal'],
            ['Delhi', 'Rajasthan', 'Gujarat', 'Maharashtra'], 
            ['Maharashtra', 'Karnataka', 'Tamil Nadu'],
            ['Delhi', 'Haryana', 'Punjab', 'Jammu and Kashmir'],
            ['West Bengal', 'Odisha', 'Andhra Pradesh', 'Tamil Nadu'],
            ['Gujarat', 'Maharashtra', 'Karnataka', 'Kerala'],
            ['Uttar Pradesh', 'Madhya Pradesh', 'Maharashtra'],
            ['Delhi', 'Uttarakhand', 'Himachal Pradesh'],
            ['Bihar', 'Jharkhand', 'West Bengal'],
            ['Assam', 'West Bengal', 'Odisha'],
            ['Telangana', 'Karnataka', 'Tamil Nadu'],
            ['Rajasthan', 'Madhya Pradesh', 'Maharashtra'],
            ['Punjab', 'Haryana', 'Delhi', 'Uttar Pradesh'],
            ['Kerala', 'Tamil Nadu', 'Karnataka'],
            ['Chhattisgarh', 'Odisha', 'Andhra Pradesh']
        ]
        
        # Create routes for each train
        for train_idx, train in enumerate(all_trains):
            try:
                # Choose route pattern based on train index
                route_pattern = major_routes[train_idx % len(major_routes)]
                
                # Build station sequence for this route
                route_stations = []
                total_distance = 0
                
                for state_idx, state in enumerate(route_pattern):
                    if state in stations_by_state and stations_by_state[state]:
                        # Pick 1-2 stations from each state
                        state_stations = random.sample(
                            stations_by_state[state], 
                            min(2, len(stations_by_state[state]))
                        )
                        
                        for station in state_stations:
                            if len(route_stations) < 8:  # Max 8 stations per train
                                route_stations.append(station)
                
                # Ensure minimum 3 stations per route
                if len(route_stations) < 3:
                    # Add more random stations if needed
                    additional_stations = random.sample(all_stations, 3 - len(route_stations))
                    route_stations.extend(additional_stations)
                
                # Create train route entries
                departure_hour = random.randint(4, 22)  # Trains depart between 4 AM and 10 PM
                
                for seq, station in enumerate(route_stations[:8]):  # Limit to 8 stations
                    # Calculate distance (approximate)
                    if seq == 0:
                        distance = 0
                        arrival_time = None
                        departure_time = time(departure_hour, random.randint(0, 59))
                    else:
                        # Add realistic distance between stations
                        segment_distance = random.randint(80, 300)
                        total_distance += segment_distance
                        
                        # Calculate travel time (approximate 60 km/h average)
                        travel_hours = segment_distance // 60
                        travel_minutes = random.randint(0, 59)
                        
                        arrival_hour = (departure_hour + travel_hours) % 24
                        arrival_time = time(arrival_hour, travel_minutes)
                        
                        # Departure time (if not last station)
                        if seq < len(route_stations) - 1:
                            stop_duration = random.randint(2, 15)  # 2-15 minute stop
                            departure_hour = (arrival_hour + (stop_duration // 60)) % 24
                            departure_minute = (travel_minutes + (stop_duration % 60)) % 60
                            departure_time = time(departure_hour, departure_minute)
                        else:
                            departure_time = None  # Last station
                    
                    # Create route entry
                    route = TrainRoute(
                        train_id=train.id,
                        station_id=station.id,
                        sequence=seq + 1,
                        arrival_time=arrival_time,
                        departure_time=departure_time,
                        distance_from_start=total_distance
                    )
                    
                    db.session.add(route)
                    route_count += 1
                
                # Progress indicator - commit less frequently for speed
                if (train_idx + 1) % 100 == 0:
                    print(f"  Created routes for {train_idx + 1}/500 trains...")
                    db.session.commit()  # Commit in larger batches
                
            except Exception as e:
                print(f"  Warning: Could not create route for train {train.number}: {e}")
                continue
        
        # Final commit
        db.session.commit()
        print(f"Created {route_count} train routes")
        
        print("\n✅ Database population completed!")
        print(f"📊 Summary:")
        print(f"   - {len(stations)} stations")
        print(f"   - {len(trains)} trains") 
        print(f"   - {len(users_data)} users")
        print(f"   - {route_count} train routes")
        print(f"\n🚀 System Features:")
        print(f"   - Tatkal booking enabled on all trains")
        print(f"   - Concurrent booking protection")
        print(f"   - Passenger details collection")
        print(f"   - Waitlist management") 
        print(f"   - Admin dashboard with analytics")
        print(f"\n🔑 Login credentials:")
        print(f"   Super Admin: admin / admin123")
        print(f"   Admin: manager / manager123") 
        print(f"   User: john_doe / user123")
        print(f"   Test User: test_user / test123")
        print(f"\n🎯 Ready for production deployment!")

if __name__ == '__main__':
    populate_database()