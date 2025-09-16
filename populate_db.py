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
        
        # Create stations
        print("Creating stations...")
        stations_data = [
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
        ]
        
        stations = []
        for station_data in stations_data:
            station = Station(**station_data)
            stations.append(station)
            db.session.add(station)
        
        db.session.commit()
        print(f"Created {len(stations)} stations")
        
        # Create trains
        print("Creating trains...")
        trains_data = [
            {'number': '12001', 'name': 'New Delhi Howrah Rajdhani Express', 'total_seats': 300, 'fare_per_km': 15.0},
            {'number': '12002', 'name': 'Howrah New Delhi Rajdhani Express', 'total_seats': 300, 'fare_per_km': 15.0},
            {'number': '12951', 'name': 'Mumbai Central New Delhi Rajdhani Express', 'total_seats': 280, 'fare_per_km': 16.0},
            {'number': '12952', 'name': 'New Delhi Mumbai Central Rajdhani Express', 'total_seats': 280, 'fare_per_km': 16.0},
            {'number': '12621', 'name': 'Chennai Central New Delhi Tamil Nadu Express', 'total_seats': 350, 'fare_per_km': 12.0},
            {'number': '12622', 'name': 'New Delhi Chennai Central Tamil Nadu Express', 'total_seats': 350, 'fare_per_km': 12.0},
            {'number': '12640', 'name': 'Bangalore City Chennai Central Brindavan Express', 'total_seats': 200, 'fare_per_km': 10.0},
            {'number': '12639', 'name': 'Chennai Central Bangalore City Brindavan Express', 'total_seats': 200, 'fare_per_km': 10.0},
            {'number': '12053', 'name': 'Ahmedabad Howrah Janshatabdi Express', 'total_seats': 250, 'fare_per_km': 8.0},
            {'number': '12054', 'name': 'Howrah Ahmedabad Janshatabdi Express', 'total_seats': 250, 'fare_per_km': 8.0},
        ]
        
        trains = []
        for train_data in trains_data:
            train = Train(
                number=train_data['number'],
                name=train_data['name'],
                total_seats=train_data['total_seats'],
                available_seats=train_data['total_seats'],
                fare_per_km=train_data['fare_per_km'],
                active=True
            )
            trains.append(train)
            db.session.add(train)
        
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
        
        # Create some train routes
        print("Creating train routes...")
        route_count = 0
        
        # Simple route: Delhi to Howrah
        delhi_station = Station.query.filter_by(code='NDLS').first()
        agra_station = Station.query.filter_by(code='AGC').first()
        lucknow_station = Station.query.filter_by(code='LKO').first()
        howrah_station = Station.query.filter_by(code='HWH').first()
        train_12001 = Train.query.filter_by(number='12001').first()
        
        if all([delhi_station, agra_station, lucknow_station, howrah_station, train_12001]):
            routes = [
                {'station': delhi_station, 'sequence': 1, 'departure_time': time(6, 0), 'distance': 0},
                {'station': agra_station, 'sequence': 2, 'arrival_time': time(8, 30), 'departure_time': time(8, 35), 'distance': 200},
                {'station': lucknow_station, 'sequence': 3, 'arrival_time': time(14, 15), 'departure_time': time(14, 25), 'distance': 450},
                {'station': howrah_station, 'sequence': 4, 'arrival_time': time(22, 30), 'distance': 1440}
            ]
            
            for route_data in routes:
                route = TrainRoute(
                    train_id=train_12001.id,
                    station_id=route_data['station'].id,
                    sequence=route_data['sequence'],
                    arrival_time=route_data.get('arrival_time'),
                    departure_time=route_data.get('departure_time'),
                    distance_from_start=route_data['distance']
                )
                db.session.add(route)
                route_count += 1
        
        db.session.commit()
        print(f"Created {route_count} train routes")
        
        print("\n✅ Database population completed!")
        print(f"📊 Summary:")
        print(f"   - {len(stations)} stations")
        print(f"   - {len(trains)} trains")
        print(f"   - {len(users_data)} users")
        print(f"   - {route_count} train routes")
        print(f"\n🔑 Login credentials:")
        print(f"   Admin: admin / admin123")
        print(f"   Manager: manager / manager123") 
        print(f"   User: john_doe / user123")
        print(f"   Test User: test_user / test123")

if __name__ == '__main__':
    populate_database()