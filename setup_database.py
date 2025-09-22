#!/usr/bin/env python3
"""
South Indian Railway Database Setup Script
Creates database schema and populates with South Indian railway data
1500 trains and 1250 stations focused on Tamil Nadu, Karnataka, Kerala, Andhra Pradesh, and Telangana

Usage:
    python setup_database.py

Environment Variables:
    DATABASE_URL: PostgreSQL connection string
    CREATE_ADMIN: Set to '1' to create admin user
    ADMIN_PASSWORD: Admin password (required if CREATE_ADMIN=1)
"""

import os
import sys
from datetime import datetime, time
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_database():
    """Initialize database with South Indian railway data"""
    
    # Safety check
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        logger.error("Database setup script should not be run in production!")
        sys.exit(1)
    
    logger.info("Starting South Indian Railway Database Setup...")
    logger.info("Target: 1500 trains and 1250 stations")
    logger.info("=" * 60)
    
    # Import Flask app and models
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from src.app import app, db
        from src import models  # Import all models
        
        with app.app_context():
            logger.info("Creating database schema...")
            
            # Only drop tables in development
            logger.warning("DROPPING ALL TABLES - This will delete all data!")
            db.drop_all()
            
            # Create all tables
            db.create_all()
            logger.info("Database schema created successfully")
            
            # Populate with South Indian railway data
            logger.info("Populating database with South Indian railway data...")
            populate_south_indian_data(db)
            
            logger.info("Database setup completed successfully!")
            logger.info(f"Created 1250 stations and 1500 trains focused on South India")
            
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        sys.exit(1)

def populate_south_indian_data(db):
    """Populate database with South Indian railway data"""
    
    from src.models import User, Station, Train, TrainRoute
    
    # Create admin user if requested
    create_admin_user(db, User)
    
    # Create 1250 stations (mostly South Indian)
    logger.info("Creating 1250 railway stations...")
    create_south_indian_stations(db, Station)
    
    # Create 1500 trains
    logger.info("Creating 1500 trains...")
    create_south_indian_trains(db, Train)
    
    # Create train routes
    logger.info("Creating train routes...")
    create_south_indian_routes(db, Train, Station, TrainRoute)

def create_admin_user(db, User):
    """Create admin user only if explicitly requested"""
    
    admin_password = os.environ.get('ADMIN_PASSWORD')
    create_admin = os.environ.get('CREATE_ADMIN', '').lower() in ['1', 'true', 'yes']
    
    if create_admin:
        if not admin_password:
            logger.error("CREATE_ADMIN=1 requires ADMIN_PASSWORD environment variable")
            sys.exit(1)
        
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash(admin_password)
        
        admin = User(
            username='admin',
            email='admin@railserve.com',
            password_hash=password_hash,
            role='super_admin',
            active=True,
            reset_token=None,
            reset_token_expiry=None
        )
        
        db.session.add(admin)
        db.session.commit()
        logger.info("Created admin user with provided password")
    else:
        logger.info("Skipping admin user creation (set CREATE_ADMIN=1 and ADMIN_PASSWORD to create)")

def create_south_indian_stations(db, Station):
    """Create 1250 railway stations focused on South India"""
    
    # Major South Indian stations
    major_stations = [
        # Tamil Nadu - Major stations
        ('MAS', 'Chennai Central', 'Chennai', 'TN'),
        ('MSB', 'Chennai Egmore', 'Chennai', 'TN'),
        ('TBM', 'Tambaram', 'Chennai', 'TN'),
        ('CGL', 'Chengalpattu', 'Chengalpattu', 'TN'),
        ('VM', 'Villupuram', 'Villupuram', 'TN'),
        ('CUD', 'Cuddalore Port', 'Cuddalore', 'TN'),
        ('PDY', 'Puducherry', 'Puducherry', 'PY'),
        ('TPJ', 'Tiruchirapalli Junction', 'Tiruchirappalli', 'TN'),
        ('TJ', 'Thanjavur Junction', 'Thanjavur', 'TN'),
        ('KMU', 'Kumbakonam', 'Kumbakonam', 'TN'),
        ('MV', 'Mayiladuthurai Junction', 'Mayiladuthurai', 'TN'),
        ('CDM', 'Chidambaram', 'Chidambaram', 'TN'),
        ('MDU', 'Madurai Junction', 'Madurai', 'TN'),
        ('DG', 'Dindigul Junction', 'Dindigul', 'TN'),
        ('KQN', 'Kodaikanal Road', 'Kodaikanal', 'TN'),
        ('CBE', 'Coimbatore Junction', 'Coimbatore', 'TN'),
        ('ED', 'Erode Junction', 'Erode', 'TN'),
        ('SA', 'Salem Junction', 'Salem', 'TN'),
        ('JTJ', 'Jolarpettai Junction', 'Jolarpettai', 'TN'),
        ('KPD', 'Katpadi Junction', 'Vellore', 'TN'),
        ('ARV', 'Arkonam Junction', 'Arkonam', 'TN'),
        ('RU', 'Renigunta Junction', 'Tirupati', 'AP'),
        ('TPTY', 'Tirupati', 'Tirupati', 'AP'),
        ('GDR', 'Gudur Junction', 'Gudur', 'AP'),
        ('NLR', 'Nellore', 'Nellore', 'AP'),
        ('OGL', 'Ongole', 'Ongole', 'AP'),
        ('BZA', 'Vijayawada Junction', 'Vijayawada', 'AP'),
        ('TEL', 'Tenali Junction', 'Tenali', 'AP'),
        ('GNT', 'Guntur Junction', 'Guntur', 'AP'),
        ('NLDA', 'Nalanda', 'Nalanda', 'AP'),
        
        # Karnataka - Major stations
        ('SBC', 'Bangalore City Junction', 'Bangalore', 'KA'),
        ('YPR', 'Yesvantpur Junction', 'Bangalore', 'KA'),
        ('KJM', 'Krishnarajapuram', 'Bangalore', 'KA'),
        ('YNK', 'Yelhanka Junction', 'Bangalore', 'KA'),
        ('TK', 'Tumkur', 'Tumkur', 'KA'),
        ('ASK', 'Arsikere Junction', 'Arsikere', 'KA'),
        ('RRB', 'Birur Junction', 'Birur', 'KA'),
        ('DVG', 'Davangere', 'Davangere', 'KA'),
        ('HRR', 'Harihar', 'Harihar', 'KA'),
        ('RNR', 'Ranibennur', 'Ranibennur', 'KA'),
        ('HVR', 'Haveri', 'Haveri', 'KA'),
        ('UBL', 'Hubli Junction', 'Hubli', 'KA'),
        ('DWR', 'Dharwad', 'Dharwad', 'KA'),
        ('LD', 'Londa Junction', 'Londa', 'KA'),
        ('BGM', 'Belagavi', 'Belagavi', 'KA'),
        ('GPB', 'Gokak Road', 'Gokak', 'KA'),
        ('MRJ', 'Miraj Junction', 'Miraj', 'MH'),
        ('KOP', 'Kolhapur', 'Kolhapur', 'MH'),
        ('MAJN', 'Mangalore Junction', 'Mangalore', 'KA'),
        ('KBPR', 'Kabaka Puttur', 'Puttur', 'KA'),
        ('SBHR', 'Subramanya Road', 'Subramanya', 'KA'),
        ('BNTL', 'Bantwal', 'Bantwal', 'KA'),
        ('MAQ', 'Mangalore Central', 'Mangalore', 'KA'),
        ('UD', 'Udupi', 'Udupi', 'KA'),
        ('KUDA', 'Kundapura', 'Kundapura', 'KA'),
        ('BYNR', 'Byndoor', 'Byndoor', 'KA'),
        ('KNSM', 'Kumsi', 'Kumsi', 'KA'),
        ('MRDW', 'Murdeshwar', 'Murdeshwar', 'KA'),
        ('HNA', 'Honnavar', 'Honnavar', 'KA'),
        ('KT', 'Karwar', 'Karwar', 'KA'),
        ('MYS', 'Mysore Junction', 'Mysore', 'KA'),
        ('S', 'Srirangapatnam', 'Srirangapatnam', 'KA'),
        ('MYA', 'Mandya', 'Mandya', 'KA'),
        ('CPT', 'Chamarajanagar', 'Chamarajanagar', 'KA'),
        ('SLO', 'Salem Odai', 'Salem', 'TN'),
        
        # Kerala - Major stations  
        ('TVC', 'Thiruvananthapuram Central', 'Thiruvananthapuram', 'KL'),
        ('QLN', 'Kollam Junction', 'Kollam', 'KL'),
        ('ALLP', 'Alappuzha', 'Alappuzha', 'KL'),
        ('KTYM', 'Kottayam', 'Kottayam', 'KL'),
        ('CGY', 'Changanassery', 'Changanassery', 'KL'),
        ('TRVL', 'Tiruvalla', 'Tiruvalla', 'KL'),
        ('CNGR', 'Chengannur', 'Chengannur', 'KL'),
        ('ERS', 'Ernakulam Junction', 'Kochi', 'KL'),
        ('ERN', 'Ernakulam Town', 'Kochi', 'KL'),
        ('AWY', 'Aluva', 'Aluva', 'KL'),
        ('CKI', 'Chalakudy', 'Chalakudy', 'KL'),
        ('IJK', 'Irinjalakuda', 'Irinjalakuda', 'KL'),
        ('TCR', 'Thrissur', 'Thrissur', 'KL'),
        ('OTP', 'Ottapalam', 'Ottapalam', 'KL'),
        ('SRR', 'Shoranur Junction', 'Shoranur', 'KL'),
        ('TIR', 'Tirur', 'Tirur', 'KL'),
        ('KTU', 'Kuttippuram', 'Kuttippuram', 'KL'),
        ('FK', 'Ferok', 'Ferok', 'KL'),
        ('CLT', 'Kozhikode', 'Kozhikode', 'KL'),
        ('QLD', 'Quilandi', 'Quilandi', 'KL'),
        ('BDJ', 'Vadakara', 'Vadakara', 'KL'),
        ('TLY', 'Thalassery', 'Thalassery', 'KL'),
        ('CAN', 'Kannur', 'Kannur', 'KL'),
        ('PAY', 'Payyanur', 'Payyanur', 'KL'),
        ('KZE', 'Kanhangad', 'Kanhangad', 'KL'),
        ('KGQ', 'Kasaragod', 'Kasaragod', 'KL'),
        
        # Andhra Pradesh & Telangana - Major stations
        ('SC', 'Secunderabad Junction', 'Hyderabad', 'TS'),
        ('HYB', 'Hyderabad Deccan', 'Hyderabad', 'TS'),
        ('KCG', 'Kacheguda', 'Hyderabad', 'TS'),
        ('LPI', 'Lingampalli', 'Hyderabad', 'TS'),
        ('WL', 'Warangal', 'Warangal', 'TS'),
        ('KZJ', 'Kazipet Junction', 'Kazipet', 'TS'),
        ('BPQ', 'Balharshah', 'Balharshah', 'MH'),
        ('SKZR', 'Sirkazhi', 'Sirkazhi', 'TN'),
        ('NGP', 'Nagpur', 'Nagpur', 'MH'),
        ('WR', 'Wardha Junction', 'Wardha', 'MH'),
        ('CD', 'Chandrapur', 'Chandrapur', 'MH'),
        ('MJBK', 'Manjlegaon', 'Manjlegaon', 'MH'),
    ]
    
    # Generate additional stations for Tamil Nadu
    tn_districts = ['Ariyalur', 'Chengalpattu', 'Chennai', 'Coimbatore', 'Cuddalore', 'Dharmapuri', 
                    'Dindigul', 'Erode', 'Kallakurichi', 'Kanchipuram', 'Kanyakumari', 'Karur', 
                    'Krishnagiri', 'Madurai', 'Mayurbhanj', 'Nagapattinam', 'Namakkal', 'Nilgiris',
                    'Perambalur', 'Pudukkottai', 'Ramanathapuram', 'Ranipet', 'Salem', 'Sivaganga',
                    'Tenkasi', 'Thanjavur', 'Theni', 'Thoothukudi', 'Tiruchirappalli', 'Tirunelveli',
                    'Tirupathur', 'Tiruppur', 'Tiruvallur', 'Tiruvannamalai', 'Tiruvarur', 'Vellore',
                    'Viluppuram', 'Virudhunagar']
    
    ka_districts = ['Bagalkot', 'Ballari', 'Belagavi', 'Bengaluru Rural', 'Bengaluru Urban', 'Bidar',
                    'Chamarajanagar', 'Chikballapur', 'Chikkamagaluru', 'Chitradurga', 'Dakshina Kannada',
                    'Davanagere', 'Dharwad', 'Gadag', 'Hassan', 'Haveri', 'Kalaburagi', 'Kodagu',
                    'Kolar', 'Koppal', 'Mandya', 'Mysuru', 'Raichur', 'Ramanagara', 'Shivamogga',
                    'Tumakuru', 'Udupi', 'Uttara Kannada', 'Vijayapura', 'Yadgir']
    
    kl_districts = ['Alappuzha', 'Ernakulam', 'Idukki', 'Kannur', 'Kasaragod', 'Kollam', 'Kottayam',
                    'Kozhikode', 'Malappuram', 'Palakkad', 'Pathanamthitta', 'Thiruvananthapuram',
                    'Thrissur', 'Wayanad']
    
    ap_ts_districts = ['Anantapur', 'Chittoor', 'East Godavari', 'Guntur', 'Krishna', 'Kurnool',
                       'Nellore', 'Prakasam', 'Srikakulam', 'Visakhapatnam', 'Vizianagaram',
                       'West Godavari', 'YSR Kadapa', 'Adilabad', 'Bhadradri Kothagudem', 
                       'Hyderabad', 'Jagtial', 'Jangaon', 'Jayashankar', 'Jogulamba', 'Kamareddy',
                       'Karimnagar', 'Khammam', 'Komaram Bheem', 'Mahabubabad', 'Mahabubnagar',
                       'Mancherial', 'Medak', 'Medchal', 'Mulugu', 'Nagarkurnool', 'Nalgonda',
                       'Narayanpet', 'Nirmal', 'Nizamabad', 'Peddapalli', 'Rajanna Sircilla',
                       'Rangareddy', 'Sangareddy', 'Siddipet', 'Suryapet', 'Vikarabad', 'Wanaparthy',
                       'Warangal Rural', 'Warangal Urban', 'Yadadri Bhuvanagiri']
    
    stations = []
    stations.extend([Station(name=name, code=code, city=city, state=state) 
                     for code, name, city, state in major_stations])
    
    # Keep track of generated station names to avoid duplicates
    existing_names = {station.name for station in stations}
    existing_codes = {station.code for station in stations}
    
    # Generate additional stations
    station_code_counter = 1000
    
    # Tamil Nadu stations (400 total)
    tn_count = 0
    for i in range(1000):  # Prevent infinite loop
        if tn_count >= 400 or len(stations) >= 500:
            break
        district = tn_districts[i % len(tn_districts)]
        suffix_num = i // len(tn_districts) + 1
        code = f"TN{station_code_counter}"
        
        # Create unique name
        if suffix_num == 1:
            station_type = 'Junction' if i % 3 == 0 else 'Railway Station'
            name = f"{district} {station_type}"
        else:
            station_type = random.choice(['Junction', 'Railway Station', 'Halt', 'Terminal'])
            name = f"{district} {station_type} {suffix_num}"
        
        if name not in existing_names and code not in existing_codes:
            stations.append(Station(name=name, code=code, city=district, state='TN'))
            existing_names.add(name)
            existing_codes.add(code)
            tn_count += 1
        station_code_counter += 1
    
    # Karnataka stations (300 total)
    ka_count = 0
    for i in range(1000):
        if ka_count >= 300:
            break
        district = ka_districts[i % len(ka_districts)]
        suffix_num = i // len(ka_districts) + 1
        code = f"KA{station_code_counter}"
        
        if suffix_num == 1:
            station_type = 'Junction' if i % 4 == 0 else 'Railway Station'
            name = f"{district} {station_type}"
        else:
            station_type = random.choice(['Junction', 'Railway Station', 'Halt', 'Terminal'])
            name = f"{district} {station_type} {suffix_num}"
        
        if name not in existing_names and code not in existing_codes:
            stations.append(Station(name=name, code=code, city=district, state='KA'))
            existing_names.add(name)
            existing_codes.add(code)
            ka_count += 1
        station_code_counter += 1
    
    # Kerala stations (200 total)
    kl_count = 0
    for i in range(1000):
        if kl_count >= 200:
            break
        district = kl_districts[i % len(kl_districts)]
        suffix_num = i // len(kl_districts) + 1
        code = f"KL{station_code_counter}"
        
        if suffix_num == 1:
            station_type = 'Junction' if i % 5 == 0 else 'Railway Station'
            name = f"{district} {station_type}"
        else:
            station_type = random.choice(['Junction', 'Railway Station', 'Halt', 'Terminal'])
            name = f"{district} {station_type} {suffix_num}"
        
        if name not in existing_names and code not in existing_codes:
            stations.append(Station(name=name, code=code, city=district, state='KL'))
            existing_names.add(name)
            existing_codes.add(code)
            kl_count += 1
        station_code_counter += 1
    
    # Andhra Pradesh & Telangana stations (250 total)
    ap_ts_count = 0
    for i in range(1000):
        if ap_ts_count >= 250:
            break
        district = ap_ts_districts[i % len(ap_ts_districts)]
        suffix_num = i // len(ap_ts_districts) + 1
        state = 'TS' if 'Hyderabad' in district or i % 2 == 0 else 'AP'
        code = f"{state}{station_code_counter}"
        
        if suffix_num == 1:
            station_type = 'Junction' if i % 4 == 0 else 'Railway Station'
            name = f"{district} {station_type}"
        else:
            station_type = random.choice(['Junction', 'Railway Station', 'Halt', 'Terminal'])
            name = f"{district} {station_type} {suffix_num}"
        
        if name not in existing_names and code not in existing_codes:
            stations.append(Station(name=name, code=code, city=district, state=state))
            existing_names.add(name)
            existing_codes.add(code)
            ap_ts_count += 1
        station_code_counter += 1
    
    # Fill remaining slots with mixed South Indian stations
    remaining = 1250 - len(stations)
    mixed_count = 0
    for i in range(2000):  # Prevent infinite loop
        if mixed_count >= remaining:
            break
        
        state = random.choice(['TN', 'KA', 'KL', 'AP', 'TS'])
        if state == 'TN':
            city = random.choice(tn_districts)
        elif state == 'KA':
            city = random.choice(ka_districts)
        elif state == 'KL':
            city = random.choice(kl_districts)
        else:
            city = random.choice(ap_ts_districts)
        
        code = f"{state}{station_code_counter}"
        station_type = random.choice(['Junction', 'Railway Station', 'Halt', 'Terminal'])
        name = f"{city} {station_type} {random.randint(1, 100)}"
        
        if name not in existing_names and code not in existing_codes:
            stations.append(Station(name=name, code=code, city=city, state=state))
            existing_names.add(name)
            existing_codes.add(code)
            mixed_count += 1
        station_code_counter += 1
    
    db.session.add_all(stations)
    db.session.commit()
    logger.info(f"Created {len(stations)} South Indian railway stations")

def create_south_indian_trains(db, Train):
    """Create 1500 trains focused on South Indian routes"""
    
    # South Indian train categories and names
    train_categories = [
        ('Express', 'Mail/Express'),
        ('Superfast', 'Superfast'),
        ('Passenger', 'Passenger'),
        ('MEMU', 'MEMU'),
        ('DMU', 'DMU'),
        ('Jan Shatabdi', 'Jan Shatabdi'),
        ('Intercity', 'Intercity'),
        ('Garib Rath', 'Garib Rath'),
        ('Duronto', 'Duronto'),
        ('Humsafar', 'Humsafar'),
        ('Tejas', 'Tejas'),
        ('Vande Bharat', 'Vande Bharat')
    ]
    
    south_indian_train_names = [
        'Brindavan Express', 'Mysore Express', 'Kerala Express', 'Trivandrum Express',
        'Coromandel Express', 'Tamil Nadu Express', 'Pandyan Express', 'Cheran Express',
        'Pallavan Express', 'Cholan Express', 'Cauvery Express', 'Kurinja Express',
        'Nilgiri Express', 'Annamalai Express', 'Pamban Express', 'Kanyakumari Express',
        'Mangalore Express', 'Konkan Kanya Express', 'Netravati Express', 'Matsyagandha Express',
        'Udupi Express', 'Karwar Express', 'Goa Express', 'Mandovi Express',
        'Bangalore Express', 'Mysuru Express', 'Hampi Express', 'Vijayanagar Express',
        'Hospet Express', 'Bellary Express', 'Hubli Express', 'Dharwad Express',
        'Hyderabad Express', 'Telangana Express', 'Godavari Express', 'Krishna Express',
        'Visakha Express', 'East Coast Express', 'Falaknuma Express', 'Narayanadri Express',
        'Tirumala Express', 'Padmavati Express', 'Sapthagiri Express', 'Venkatadri Express',
        'Rayalaseema Express', 'Amaravati Express', 'Vijayawada Express', 'Guntur Express',
        'Alleppey Express', 'Kochi Express', 'Malabar Express', 'Parasuram Express',
        'Jayanthi Janata Express', 'Sabari Express', 'Vanchinad Express', 'Backwater Express',
        'Spice Coast Express', 'Coconut Express', 'Cardamom Express', 'Tea Garden Express'
    ]
    
    trains = []
    train_number = 10001
    
    for i in range(1500):
        # Generate train details
        category, train_type = random.choice(train_categories)
        base_name = random.choice(south_indian_train_names)
        
        # Avoid duplicate names by adding suffix if needed
        train_name = base_name
        if i > len(south_indian_train_names):
            train_name = f"{base_name} {category}"
        
        # Set train capacity based on type
        if train_type in ['Vande Bharat', 'Tejas', 'Duronto']:
            total_seats = random.randint(350, 450)
        elif train_type in ['Superfast', 'Mail/Express']:
            total_seats = random.randint(300, 500)
        elif train_type in ['Jan Shatabdi', 'Intercity']:
            total_seats = random.randint(400, 600)
        elif train_type in ['MEMU', 'DMU']:
            total_seats = random.randint(200, 350)
        else:  # Passenger
            total_seats = random.randint(150, 300)
        
        # Set fare based on train type
        if train_type in ['Vande Bharat', 'Tejas']:
            fare_per_km = random.uniform(1.5, 2.5)
            tatkal_fare_per_km = random.uniform(2.5, 3.5)
        elif train_type in ['Duronto', 'Superfast']:
            fare_per_km = random.uniform(0.8, 1.5)
            tatkal_fare_per_km = random.uniform(1.5, 2.2)
        elif train_type in ['Mail/Express']:
            fare_per_km = random.uniform(0.5, 1.0)
            tatkal_fare_per_km = random.uniform(1.0, 1.8)
        else:
            fare_per_km = random.uniform(0.3, 0.8)
            tatkal_fare_per_km = random.uniform(0.8, 1.3)
        
        tatkal_seats = int(total_seats * 0.1)  # 10% tatkal quota
        
        train = Train(
            number=str(train_number),
            name=train_name,
            total_seats=total_seats,
            available_seats=total_seats,
            fare_per_km=fare_per_km,
            tatkal_seats=tatkal_seats,
            tatkal_fare_per_km=tatkal_fare_per_km
        )
        trains.append(train)
        train_number += 1
    
    db.session.add_all(trains)
    db.session.commit()
    logger.info(f"Created {len(trains)} South Indian trains")

def create_south_indian_routes(db, Train, Station, TrainRoute):
    """Create train routes connecting South Indian stations"""
    
    trains = Train.query.all()
    stations = Station.query.all()
    
    # Create station mapping by state
    tn_stations = [s for s in stations if s.state == 'TN']
    ka_stations = [s for s in stations if s.state == 'KA']
    kl_stations = [s for s in stations if s.state == 'KL']
    ap_stations = [s for s in stations if s.state == 'AP']
    ts_stations = [s for s in stations if s.state == 'TS']
    
    major_stations = {s.code: s for s in stations if s.code in [
        'MAS', 'MSB', 'TPJ', 'MDU', 'CBE', 'SA', 'SBC', 'YPR', 'MYS', 'UBL',
        'TVC', 'ERS', 'CLT', 'SC', 'HYB', 'BZA', 'TPTY'
    ]}
    
    routes = []
    
    for train in trains:
        # Determine route type based on train name and number
        train_num = int(train.number)
        
        if 'Express' in train.name or 'Duronto' in train.name or train_num < 11000:
            # Long distance routes (3-8 stations)
            route_stations = generate_long_distance_route(train, major_stations, stations)
        elif 'MEMU' in train.name or 'DMU' in train.name or 'Passenger' in train.name:
            # Local/regional routes (5-15 stations)
            route_stations = generate_regional_route(train, stations)
        else:
            # Medium distance routes (3-6 stations)
            route_stations = generate_medium_distance_route(train, stations)
        
        # Create route entries
        for sequence, (station, arrival_time, departure_time, distance) in enumerate(route_stations, 1):
            route = TrainRoute(
                train_id=train.id,
                station_id=station.id,
                sequence=sequence,
                arrival_time=arrival_time,
                departure_time=departure_time,
                distance_from_start=distance
            )
            routes.append(route)
    
    db.session.add_all(routes)
    db.session.commit()
    logger.info(f"Created {len(routes)} train route entries")

def generate_long_distance_route(train, major_stations, all_stations):
    """Generate long distance route connecting major cities"""
    route_stations = []
    
    # Pick 2 major stations as start and end
    major_list = list(major_stations.values())
    if len(major_list) >= 2:
        start_station = random.choice(major_list)
        end_station = random.choice([s for s in major_list if s.id != start_station.id])
        
        # Add intermediate stations
        num_intermediate = random.randint(1, 6)
        intermediate_stations = random.sample(
            [s for s in all_stations if s.id not in [start_station.id, end_station.id]], 
            min(num_intermediate, len(all_stations) - 2)
        )
        
        # Build route
        all_route_stations = [start_station] + intermediate_stations + [end_station]
        
        current_time = time(random.randint(5, 20), random.randint(0, 59))
        current_distance = 0
        
        for i, station in enumerate(all_route_stations):
            if i == 0:
                # First station - departure only
                arrival_time = current_time
                departure_time = current_time
            elif i == len(all_route_stations) - 1:
                # Last station - arrival only
                current_distance += random.randint(80, 300)
                arrival_time = add_minutes_to_time(current_time, random.randint(90, 240))
                departure_time = arrival_time
            else:
                # Intermediate station
                current_distance += random.randint(50, 200)
                arrival_time = add_minutes_to_time(current_time, random.randint(60, 180))
                departure_time = add_minutes_to_time(arrival_time, random.randint(2, 10))
                current_time = departure_time
            
            route_stations.append((station, arrival_time, departure_time, current_distance))
    
    return route_stations

def generate_regional_route(train, stations):
    """Generate regional route with more stations"""
    route_stations = []
    
    # Pick stations from same or nearby states
    available_stations = random.sample(stations, min(random.randint(5, 15), len(stations)))
    
    current_time = time(random.randint(5, 18), random.randint(0, 59))
    current_distance = 0
    
    for i, station in enumerate(available_stations):
        if i == 0:
            arrival_time = current_time
            departure_time = current_time
        elif i == len(available_stations) - 1:
            current_distance += random.randint(20, 80)
            arrival_time = add_minutes_to_time(current_time, random.randint(30, 90))
            departure_time = arrival_time
        else:
            current_distance += random.randint(15, 60)
            arrival_time = add_minutes_to_time(current_time, random.randint(20, 60))
            departure_time = add_minutes_to_time(arrival_time, random.randint(1, 5))
            current_time = departure_time
        
        route_stations.append((station, arrival_time, departure_time, current_distance))
    
    return route_stations

def generate_medium_distance_route(train, stations):
    """Generate medium distance route"""
    route_stations = []
    
    available_stations = random.sample(stations, min(random.randint(3, 6), len(stations)))
    
    current_time = time(random.randint(6, 19), random.randint(0, 59))
    current_distance = 0
    
    for i, station in enumerate(available_stations):
        if i == 0:
            arrival_time = current_time
            departure_time = current_time
        elif i == len(available_stations) - 1:
            current_distance += random.randint(60, 150)
            arrival_time = add_minutes_to_time(current_time, random.randint(60, 150))
            departure_time = arrival_time
        else:
            current_distance += random.randint(40, 120)
            arrival_time = add_minutes_to_time(current_time, random.randint(45, 120))
            departure_time = add_minutes_to_time(arrival_time, random.randint(2, 8))
            current_time = departure_time
        
        route_stations.append((station, arrival_time, departure_time, current_distance))
    
    return route_stations

def add_minutes_to_time(time_obj, minutes):
    """Add minutes to a time object"""
    total_minutes = time_obj.hour * 60 + time_obj.minute + minutes
    hours = (total_minutes // 60) % 24
    mins = total_minutes % 60
    return time(hours, mins)

if __name__ == '__main__':
    setup_database()