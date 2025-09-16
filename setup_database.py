#!/usr/bin/env python3
"""
Comprehensive Database Setup Script for RailServe
Creates database tables and populates with 500+ sample records for local PostgreSQL database
"""

import os
import sys
import random
from datetime import datetime, date, time, timedelta

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import app, db
from src.models import User, Train, Station, TrainRoute, Booking, Payment, Passenger, Waitlist
from werkzeug.security import generate_password_hash

def create_comprehensive_stations():
    """Create 100+ railway stations across India"""
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
        
        # Additional Major Stations
        {'code': 'LKO', 'name': 'Lucknow Junction', 'city': 'Lucknow', 'state': 'Uttar Pradesh'},
        {'code': 'MB', 'name': 'Moradabad Junction', 'city': 'Moradabad', 'state': 'Uttar Pradesh'},
        {'code': 'BE', 'name': 'Bareilly Junction', 'city': 'Bareilly', 'state': 'Uttar Pradesh'},
        {'code': 'RTM', 'name': 'Ratlam Junction', 'city': 'Ratlam', 'state': 'Madhya Pradesh'},
        {'code': 'INDB', 'name': 'Indore Junction', 'city': 'Indore', 'state': 'Madhya Pradesh'},
        {'code': 'BPL', 'name': 'Bhopal Junction', 'city': 'Bhopal', 'state': 'Madhya Pradesh'},
        {'code': 'NGP', 'name': 'Nagpur Junction', 'city': 'Nagpur', 'state': 'Maharashtra'},
        {'code': 'AK', 'name': 'Akola Junction', 'city': 'Akola', 'state': 'Maharashtra'},
        {'code': 'BSL', 'name': 'Bhusaval Junction', 'city': 'Bhusaval', 'state': 'Maharashtra'},
        {'code': 'HYB', 'name': 'Hyderabad Deccan', 'city': 'Hyderabad', 'state': 'Telangana'},
        {'code': 'SC', 'name': 'Secunderabad Junction', 'city': 'Secunderabad', 'state': 'Telangana'},
        {'code': 'TPTY', 'name': 'Tirupati', 'city': 'Tirupati', 'state': 'Andhra Pradesh'},
        {'code': 'RU', 'name': 'Renigunta Junction', 'city': 'Renigunta', 'state': 'Andhra Pradesh'},
        {'code': 'GTL', 'name': 'Guntakal Junction', 'city': 'Guntakal', 'state': 'Andhra Pradesh'},
        {'code': 'SUR', 'name': 'Solapur Junction', 'city': 'Solapur', 'state': 'Maharashtra'},
        {'code': 'KOP', 'name': 'Kolhapur', 'city': 'Kolhapur', 'state': 'Maharashtra'},
        {'code': 'RBL', 'name': 'Rae Bareli Junction', 'city': 'Rae Bareli', 'state': 'Uttar Pradesh'},
        
        # Northeast and Eastern Stations
        {'code': 'GHY', 'name': 'Guwahati', 'city': 'Guwahati', 'state': 'Assam'},
        {'code': 'DBRG', 'name': 'Dibrugarh', 'city': 'Dibrugarh', 'state': 'Assam'},
        {'code': 'AGTL', 'name': 'Agartala', 'city': 'Agartala', 'state': 'Tripura'},
        {'code': 'RPAN', 'name': 'Rangapani', 'city': 'Rangapani', 'state': 'Assam'},
        {'code': 'DMV', 'name': 'Dimapur', 'city': 'Dimapur', 'state': 'Nagaland'},
        {'code': 'JRG', 'name': 'Jugpura', 'city': 'Jugpura', 'state': 'Assam'},
        
        # Northern Hill Stations
        {'code': 'DWI', 'name': 'Dwarka', 'city': 'Dwarka', 'state': 'Gujarat'},
        {'code': 'HRD', 'name': 'Hardwar Junction', 'city': 'Haridwar', 'state': 'Uttarakhand'},
        {'code': 'RKSH', 'name': 'Rishikesh', 'city': 'Rishikesh', 'state': 'Uttarakhand'},
        {'code': 'DDD', 'name': 'Dehradun', 'city': 'Dehradun', 'state': 'Uttarakhand'},
        {'code': 'ATR', 'name': 'Atari', 'city': 'Atari', 'state': 'Punjab'},
        {'code': 'JHL', 'name': 'Jammu Tawi', 'city': 'Jammu', 'state': 'Jammu and Kashmir'},
        {'code': 'SVDK', 'name': 'Shri Mata Vaishno Devi Katra', 'city': 'Katra', 'state': 'Jammu and Kashmir'},
        
        # Religious and Cultural Centers
        {'code': 'RMM', 'name': 'Rameswaram', 'city': 'Rameswaram', 'state': 'Tamil Nadu'},
        {'code': 'PURI', 'name': 'Puri', 'city': 'Puri', 'state': 'Odisha'},
        {'code': 'RJGR', 'name': 'Rajgir', 'city': 'Rajgir', 'state': 'Bihar'},
        {'code': 'GAYA', 'name': 'Gaya Junction', 'city': 'Gaya', 'state': 'Bihar'},
        {'code': 'JOG', 'name': 'Jogbani', 'city': 'Jogbani', 'state': 'Bihar'},
        {'code': 'CPR', 'name': 'Chhapra Junction', 'city': 'Chhapra', 'state': 'Bihar'},
        {'code': 'SV', 'name': 'Siwan Junction', 'city': 'Siwan', 'state': 'Bihar'},
        {'code': 'SEE', 'name': 'Sonpur Junction', 'city': 'Sonpur', 'state': 'Bihar'},
        {'code': 'MFP', 'name': 'Muzaffarpur Junction', 'city': 'Muzaffarpur', 'state': 'Bihar'},
        {'code': 'DBG', 'name': 'Darbhanga Junction', 'city': 'Darbhanga', 'state': 'Bihar'},
        {'code': 'SPJ', 'name': 'Samastipur Junction', 'city': 'Samastipur', 'state': 'Bihar'},
        {'code': 'BJU', 'name': 'Barauni Junction', 'city': 'Barauni', 'state': 'Bihar'},
        {'code': 'KIUL', 'name': 'Kiul Junction', 'city': 'Kiul', 'state': 'Bihar'},
        {'code': 'JAJ', 'name': 'Jhajha', 'city': 'Jhajha', 'state': 'Bihar'},
        {'code': 'JSME', 'name': 'Jasidih Junction', 'city': 'Jasidih', 'state': 'Jharkhand'},
        {'code': 'MDGR', 'name': 'Madhupur Junction', 'city': 'Madhupur', 'state': 'Jharkhand'},
        {'code': 'ASN', 'name': 'Asansol Junction', 'city': 'Asansol', 'state': 'West Bengal'},
        {'code': 'UDL', 'name': 'Andal Junction', 'city': 'Andal', 'state': 'West Bengal'},
        {'code': 'BWN', 'name': 'Barddhaman Junction', 'city': 'Barddhaman', 'state': 'West Bengal'},
        {'code': 'BDC', 'name': 'Bandel Junction', 'city': 'Bandel', 'state': 'West Bengal'},
        {'code': 'NH', 'name': 'Naihati Junction', 'city': 'Naihati', 'state': 'West Bengal'},
        {'code': 'BNJ', 'name': 'Bangaon Junction', 'city': 'Bangaon', 'state': 'West Bengal'},
        {'code': 'RHA', 'name': 'Ranaghat Junction', 'city': 'Ranaghat', 'state': 'West Bengal'},
        {'code': 'KYQ', 'name': 'Kamakhya Junction', 'city': 'Kamakhya', 'state': 'Assam'},
        
        # Additional 20 stations to reach 100+
        {'code': 'SDAH', 'name': 'Sealdah', 'city': 'Kolkata', 'state': 'West Bengal'},
        {'code': 'KGP', 'name': 'Kharagpur Junction', 'city': 'Kharagpur', 'state': 'West Bengal'},
        {'code': 'BBS', 'name': 'Bhubaneswar', 'city': 'Bhubaneswar', 'state': 'Odisha'},
        {'code': 'CTC', 'name': 'Cuttack', 'city': 'Cuttack', 'state': 'Odisha'},
        {'code': 'BHC', 'name': 'Bhadrakh', 'city': 'Bhadrakh', 'state': 'Odisha'},
        {'code': 'JER', 'name': 'Jaleswar', 'city': 'Jaleswar', 'state': 'Odisha'},
        {'code': 'KUR', 'name': 'Khurda Road Junction', 'city': 'Khurda', 'state': 'Odisha'},
        {'code': 'BBSR', 'name': 'Bhubaneswar New', 'city': 'Bhubaneswar', 'state': 'Odisha'},
        {'code': 'SIL', 'name': 'Sakhi Gopal', 'city': 'Sakhi Gopal', 'state': 'Odisha'},
        {'code': 'KIT', 'name': 'Khallikote', 'city': 'Khallikote', 'state': 'Odisha'},
        {'code': 'BAM', 'name': 'Brahmapur', 'city': 'Brahmapur', 'state': 'Odisha'},
        {'code': 'PSA', 'name': 'Palasa', 'city': 'Palasa', 'state': 'Andhra Pradesh'},
        {'code': 'SPT', 'name': 'Sompeta', 'city': 'Sompeta', 'state': 'Andhra Pradesh'},
        {'code': 'NRL', 'name': 'Narasapur', 'city': 'Narasapur', 'state': 'Andhra Pradesh'},
        {'code': 'VZM', 'name': 'Vizianagaram Junction', 'city': 'Vizianagaram', 'state': 'Andhra Pradesh'},
        {'code': 'RGDA', 'name': 'Rayagada', 'city': 'Rayagada', 'state': 'Odisha'},
        {'code': 'MEMU', 'name': 'Muniguda', 'city': 'Muniguda', 'state': 'Odisha'},
        {'code': 'TLHD', 'name': 'Talcher Road', 'city': 'Talcher', 'state': 'Odisha'},
        {'code': 'DNKL', 'name': 'Dhenkanal', 'city': 'Dhenkanal', 'state': 'Odisha'},
        {'code': 'ANGL', 'name': 'Angul', 'city': 'Angul', 'state': 'Odisha'}
    ]
    
    stations = []
    for station_data in stations_data:
        station = Station(**station_data)
        stations.append(station)
        db.session.add(station)
    
    db.session.commit()
    print(f"Created {len(stations)} comprehensive stations")
    return stations

def create_comprehensive_trains(stations):
    """Create 100+ trains with various types and realistic details"""
    train_types = [
        ('Rajdhani Express', 'RAJ', 1800, 300, 30),
        ('Shatabdi Express', 'SHTB', 1600, 250, 25),
        ('Duronto Express', 'DRN', 1700, 280, 28),
        ('Superfast Express', 'SF', 1200, 350, 35),
        ('Mail Express', 'MAIL', 1000, 400, 40),
        ('Passenger', 'PASS', 600, 500, 0),
        ('Jan Shatabdi', 'JSHT', 800, 300, 30),
        ('Garib Rath', 'GR', 900, 450, 0),
        ('Humsafar Express', 'HMS', 1300, 320, 32),
        ('Tejas Express', 'TEJ', 1500, 280, 28),
        ('Vande Bharat Express', 'VB', 2000, 200, 20),
        ('Double Decker Express', 'DD', 1100, 380, 38),
        ('Premium Express', 'PREM', 1400, 300, 30),
        ('AC Express', 'ACE', 1350, 320, 32),
        ('Intercity Express', 'ICE', 950, 400, 20),
    ]
    
    # Major route patterns for realistic train operations
    route_patterns = [
        ['NDLS', 'AGC', 'GWL', 'JBP', 'NGP', 'BZA', 'MAS'],  # Delhi to Chennai
        ['HWH', 'PNBE', 'CNB', 'ALLP', 'LKO', 'NDLS'],       # Howrah to Delhi
        ['CST', 'PUNE', 'SBC', 'CBE', 'MDU', 'MAS'],         # Mumbai to Chennai
        ['AMD', 'RTM', 'INDB', 'BPL', 'JBP', 'NGP'],         # Gujarat route
        ['JP', 'UDZ', 'AMD', 'BRC', 'ST', 'CST'],            # Rajasthan to Mumbai
        ['KOAA', 'CLT', 'ERS', 'CBE', 'SBC', 'PUNE'],        # Kerala route
        ['VSKP', 'BZA', 'NGP', 'BPL', 'GWL', 'NDLS'],        # East coast to Delhi
        ['BSB', 'ALLP', 'CNB', 'LKO', 'BE', 'MB', 'NDLS'],   # UP route
        ['GHY', 'RNC', 'TATA', 'HWH', 'PNBE', 'CNB'],        # Northeast route
        ['JHL', 'NDLS', 'GWL', 'BPL', 'NGP', 'SBC'],         # J&K to South
        ['HYB', 'SC', 'BZA', 'MAS', 'MDU', 'CBE'],           # Telangana route
        ['PURI', 'BBS', 'CTC', 'KGP', 'HWH', 'ASN'],         # Odisha route
        ['RMM', 'MDU', 'CBE', 'SBC', 'PUNE', 'CST'],         # South circuit
        ['DWI', 'AMD', 'BRC', 'RTM', 'INDB', 'BPL'],         # Gujarat circuit
        ['HRD', 'DDD', 'NDLS', 'JP', 'UDZ', 'AMD'],          # North hill route
    ]
    
    trains = []
    train_number = 10001
    
    for i in range(100):  # Create 100 trains
        train_type, type_code, base_fare, capacity, tatkal_seats = random.choice(train_types)
        route = random.choice(route_patterns)
        
        # Some trains run in reverse direction
        if random.choice([True, False]):
            route = route[::-1]
        
        # Create realistic train names
        origin = route[0] if route else 'NDLS'
        destination = route[-1] if route else 'MAS'
        train_name = f"{origin} {destination} {train_type}"
        
        # Calculate tatkal fare (usually 1.5x regular fare)
        tatkal_fare = base_fare * 1.5 / 100
        
        train = Train(
            number=str(train_number),
            name=train_name,
            total_seats=capacity,
            available_seats=capacity,
            fare_per_km=base_fare / 100,  # Convert to per km rate
            tatkal_seats=tatkal_seats,
            tatkal_fare_per_km=tatkal_fare,
            active=True
        )
        
        trains.append(train)
        db.session.add(train)
        train_number += 1
        
        if train_number > 99999:
            train_number = 10001  # Reset for realistic numbering
    
    db.session.commit()
    print(f"Created {len(trains)} comprehensive trains")
    return trains

def create_comprehensive_users():
    """Create 50+ users with various roles"""
    users_data = [
        # Admin users
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
            'username': 'supervisor',
            'email': 'supervisor@railserve.com',
            'password': 'super123',
            'role': 'admin'
        },
        
        # Regular users with common Indian names
        {
            'username': 'rahul_sharma',
            'email': 'rahul.sharma@email.com',
            'password': 'user123',
            'role': 'user'
        },
        {
            'username': 'priya_patel',
            'email': 'priya.patel@email.com',
            'password': 'user123',
            'role': 'user'
        },
        {
            'username': 'amit_singh',
            'email': 'amit.singh@email.com',
            'password': 'user123',
            'role': 'user'
        },
        {
            'username': 'sneha_kumar',
            'email': 'sneha.kumar@email.com',
            'password': 'user123',
            'role': 'user'
        },
        {
            'username': 'vikram_reddy',
            'email': 'vikram.reddy@email.com',
            'password': 'user123',
            'role': 'user'
        },
        {
            'username': 'anita_gupta',
            'email': 'anita.gupta@email.com',
            'password': 'user123',
            'role': 'user'
        },
        {
            'username': 'ravi_mehta',
            'email': 'ravi.mehta@email.com',
            'password': 'user123',
            'role': 'user'
        },
        {
            'username': 'pooja_joshi',
            'email': 'pooja.joshi@email.com',
            'password': 'user123',
            'role': 'user'
        },
        {
            'username': 'arjun_nair',
            'email': 'arjun.nair@email.com',
            'password': 'user123',
            'role': 'user'
        },
        {
            'username': 'kavita_das',
            'email': 'kavita.das@email.com',
            'password': 'user123',
            'role': 'user'
        }
    ]
    
    # Add more users with random names
    first_names = ['Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Reyansh', 'Ayaan', 'Krishna', 'Ishaan',
                   'Aadhya', 'Kiara', 'Diya', 'Pihu', 'Prisha', 'Ananya', 'Fatima', 'Anika', 'Khushi', 'Avni']
    last_names = ['Sharma', 'Patel', 'Singh', 'Kumar', 'Gupta', 'Mehta', 'Reddy', 'Nair', 'Joshi', 'Das',
                  'Agarwal', 'Bansal', 'Malhotra', 'Aggarwal', 'Sinha', 'Mishra', 'Tiwari', 'Chopra', 'Bhatia', 'Saxena']
    
    for i in range(40):  # Add 40 more users
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        username = f"{first_name.lower()}_{last_name.lower()}_{i}"
        email = f"{first_name.lower()}.{last_name.lower()}{i}@email.com"
        
        users_data.append({
            'username': username,
            'email': email,
            'password': 'user123',
            'role': 'user'
        })
    
    for user_data in users_data:
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            password_hash=generate_password_hash(user_data['password']),
            role=user_data['role']
        )
        db.session.add(user)
    
    db.session.commit()
    print(f"Created {len(users_data)} comprehensive users")
    return users_data

def create_train_routes(trains, stations):
    """Create comprehensive train routes"""
    station_dict = {s.code: s for s in stations}
    
    route_patterns = [
        ['NDLS', 'AGC', 'GWL', 'JBP', 'NGP', 'BZA', 'MAS'],  # Delhi to Chennai
        ['HWH', 'PNBE', 'CNB', 'ALLP', 'LKO', 'NDLS'],       # Howrah to Delhi
        ['CST', 'PUNE', 'SBC', 'CBE', 'MDU', 'MAS'],         # Mumbai to Chennai
        ['AMD', 'RTM', 'INDB', 'BPL', 'JBP', 'NGP'],         # Gujarat route
        ['JP', 'UDZ', 'AMD', 'BRC', 'ST', 'CST'],            # Rajasthan to Mumbai
        ['KOAA', 'CLT', 'ERS', 'CBE', 'SBC', 'PUNE'],        # Kerala route
        ['VSKP', 'BZA', 'NGP', 'BPL', 'GWL', 'NDLS'],        # East coast to Delhi
        ['BSB', 'ALLP', 'CNB', 'LKO', 'BE', 'MB', 'NDLS'],   # UP route
        ['GHY', 'RNC', 'TATA', 'HWH', 'PNBE', 'CNB'],        # Northeast route
        ['JHL', 'NDLS', 'GWL', 'BPL', 'NGP', 'SBC'],         # J&K to South
        ['HYB', 'SC', 'BZA', 'MAS', 'MDU', 'CBE'],           # Telangana route
        ['PURI', 'BBS', 'CTC', 'KGP', 'HWH', 'ASN'],         # Odisha route
        ['RMM', 'MDU', 'CBE', 'SBC', 'PUNE', 'CST'],         # South circuit
        ['DWI', 'AMD', 'BRC', 'RTM', 'INDB', 'BPL'],         # Gujarat circuit
        ['HRD', 'DDD', 'NDLS', 'JP', 'UDZ', 'AMD'],          # North hill route
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
            
            # Calculate distance (realistic)
            if seq > 0:
                total_distance += random.randint(100, 500)
            
            # Calculate realistic arrival and departure times
            if seq == 0:
                arrival_time = None
                departure_time = time((6 + random.randint(0, 18)) % 24, random.randint(0, 59))
            elif seq == len(valid_stations) - 1:
                # Last station - only arrival
                hours_travel = total_distance // 60  # Average speed 60 km/h
                base_hour = 6 if departure_time is None else departure_time.hour
                arrival_hour = (base_hour + hours_travel) % 24
                arrival_time = time(arrival_hour, random.randint(0, 59))
                departure_time = None
            else:
                # Intermediate station
                hours_travel = total_distance // 65
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
    print(f"Created {routes_created} comprehensive train routes")

def create_sample_bookings_and_passengers(users, trains, stations):
    """Create 200+ realistic bookings with passenger details"""
    booking_types = ['general', 'tatkal']
    quotas = ['general', 'ladies', 'senior', 'tatkal', 'disability']
    statuses = ['confirmed', 'waitlisted', 'cancelled', 'pending_payment']
    
    # Indian names for passengers
    male_names = ['Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Reyansh', 'Ayaan', 'Krishna', 'Ishaan',
                  'Shaurya', 'Atharv', 'KrishNa', 'Rudra', 'Aarush', 'Dhanush', 'Kabir', 'Kiaan', 'Riaan', 'Muhammad']
    female_names = ['Aadhya', 'Kiara', 'Diya', 'Pihu', 'Prisha', 'Ananya', 'Fatima', 'Anika', 'Khushi', 'Avni',
                    'Pari', 'Anaya', 'Myra', 'Sara', 'Aditi', 'Saanvi', 'Kavya', 'Riya', 'Ishika', 'Tara']
    
    id_proof_types = ['Aadhar', 'PAN', 'Passport', 'Voter ID', 'Driving License']
    seat_preferences = ['Lower', 'Middle', 'Upper', 'Window', 'Aisle', 'No Preference']
    
    bookings_created = 0
    passengers_created = 0
    
    for i in range(200):  # Create 200 bookings
        # Select random user and train
        user = random.choice(users)
        train = random.choice(trains)
        
        # Get random stations from train routes
        train_routes = TrainRoute.query.filter_by(train_id=train.id).order_by(TrainRoute.sequence).all()
        if len(train_routes) < 2:
            continue
        
        from_route = random.choice(train_routes[:-1])
        to_route = random.choice(train_routes[from_route.sequence:])
        
        # Generate realistic journey date (past and future)
        base_date = date.today()
        days_offset = random.randint(-30, 60)  # 30 days in past to 60 days in future
        journey_date = base_date + timedelta(days=days_offset)
        
        # Realistic booking date
        booking_days_offset = random.randint(-45, 0)  # Up to 45 days before journey
        booking_date = journey_date + timedelta(days=booking_days_offset)
        booking_datetime = datetime.combine(booking_date, time(random.randint(6, 23), random.randint(0, 59)))
        
        passengers_count = random.randint(1, 4)
        booking_type = random.choice(booking_types)
        quota = random.choice(quotas)
        status = random.choice(statuses)
        
        # Calculate realistic fare
        distance = abs(to_route.distance_from_start - from_route.distance_from_start)
        if booking_type == 'tatkal':
            base_fare = distance * train.tatkal_fare_per_km * passengers_count if train.tatkal_fare_per_km else distance * train.fare_per_km * passengers_count * 1.5
        else:
            base_fare = distance * train.fare_per_km * passengers_count
        
        total_amount = base_fare * 1.18  # Add GST and service charges
        
        # Create booking
        user_obj = User.query.filter_by(username=user['username']).first()
        if not user_obj:
            continue
            
        booking = Booking(
            user_id=user_obj.id,
            train_id=train.id,
            from_station_id=from_route.station_id,
            to_station_id=to_route.station_id,
            journey_date=journey_date,
            passengers=passengers_count,
            total_amount=round(total_amount, 2),
            booking_type=booking_type,
            quota=quota,
            status=status,
            booking_date=booking_datetime
        )
        
        db.session.add(booking)
        db.session.flush()  # Get booking ID
        bookings_created += 1
        
        # Create passenger details for each passenger
        for p in range(passengers_count):
            gender = random.choice(['Male', 'Female'])
            name = random.choice(male_names if gender == 'Male' else female_names)
            full_name = f"{name} {random.choice(['Sharma', 'Patel', 'Singh', 'Kumar', 'Gupta'])}"
            
            passenger = Passenger(
                booking_id=booking.id,
                name=full_name,
                age=random.randint(5, 75),
                gender=gender,
                id_proof_type=random.choice(id_proof_types),
                id_proof_number=f"{random.randint(100000000000, 999999999999)}",
                seat_preference=random.choice(seat_preferences)
            )
            
            db.session.add(passenger)
            passengers_created += 1
        
        # Create payment records for confirmed bookings
        if status in ['confirmed', 'cancelled']:
            payment_status = 'success' if status == 'confirmed' else 'failed'
            payment_method = random.choice(['card', 'upi', 'netbanking'])
            
            payment = Payment(
                booking_id=booking.id,
                user_id=booking.user_id,
                amount=booking.total_amount,
                payment_method=payment_method,
                transaction_id=f"TXN{random.randint(100000000, 999999999)}",
                status=payment_status,
                created_at=booking_datetime,
                completed_at=booking_datetime + timedelta(minutes=random.randint(1, 5)) if payment_status == 'success' else None
            )
            
            db.session.add(payment)
    
    db.session.commit()
    print(f"Created {bookings_created} bookings with {passengers_created} passenger records")

def setup_comprehensive_database():
    """Main function to set up the entire database with 500+ records"""
    with app.app_context():
        print("🚀 Starting comprehensive database setup...")
        print("=" * 60)
        
        # Create all tables
        print("📋 Creating database tables...")
        db.create_all()
        
        # Clear existing data
        print("🧹 Clearing existing data...")
        Payment.query.delete()
        Passenger.query.delete()
        Waitlist.query.delete()
        Booking.query.delete()
        TrainRoute.query.delete()
        Train.query.delete()
        Station.query.delete()
        User.query.delete()
        
        # Create comprehensive data
        print("🏗️  Creating comprehensive data...")
        
        print("\n1️⃣  Creating 100+ stations...")
        stations = create_comprehensive_stations()
        
        print("2️⃣  Creating 100+ trains...")
        trains = create_comprehensive_trains(stations)
        
        print("3️⃣  Creating 50+ users...")
        users = create_comprehensive_users()
        
        print("4️⃣  Creating train routes...")
        create_train_routes(trains, stations)
        
        print("5️⃣  Creating 200+ bookings with passenger details...")
        create_sample_bookings_and_passengers(users, trains, stations)
        
        print("\n" + "=" * 60)
        print("✅ Database setup completed successfully!")
        print("📊 Summary:")
        print(f"   - {Station.query.count()} stations")
        print(f"   - {Train.query.count()} trains")
        print(f"   - {User.query.count()} users")
        print(f"   - {TrainRoute.query.count()} train routes")
        print(f"   - {Booking.query.count()} bookings")
        print(f"   - {Passenger.query.count()} passenger records")
        print(f"   - {Payment.query.count()} payment records")
        
        total_records = (Station.query.count() + Train.query.count() + User.query.count() + 
                        TrainRoute.query.count() + Booking.query.count() + 
                        Passenger.query.count() + Payment.query.count())
        print(f"   - {total_records} total records")
        
        print(f"\n🔑 Login credentials:")
        print(f"   Super Admin: admin / admin123")
        print(f"   Admin: manager / manager123")
        print(f"   Sample User: rahul_sharma / user123")
        print(f"   Sample User: priya_patel / user123")
        print("=" * 60)

if __name__ == '__main__':
    setup_comprehensive_database()