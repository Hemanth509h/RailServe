#!/usr/bin/env python3
"""
Railway Database Setup Script - South Indian Railway Focus
Creates essential database schema with South Indian railway data

Features:
- 1250 stations (majority from South India)
- 1500 trains with realistic routes
- 2 users (regular user and admin)
- Complete railway functionality including TDR (Ticket Deposit Receipt) system
- All essential models for booking, refunds, chart preparation, and administration

Usage:
    python setup_database.py

Environment Variables:
    DATABASE_URL: PostgreSQL connection string (optional - defaults to SQLite)
    ADMIN_PASSWORD: Admin password (defaults to 'admin123')
"""

import os
import sys
from datetime import datetime, date, time, timedelta
import logging
import random
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_database():
    """Initialize database with comprehensive Indian railway data"""
    
    # Safety check - don't run in production
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        logger.error("Database setup script should not be run in production!")
        sys.exit(1)
    
    logger.info("🚂 Starting Comprehensive Railway Database Setup")
    logger.info("Creating: 1250 stations (South India focus), 1500 trains, 2 users")
    logger.info("=" * 80)
    
    # Import Flask app and models
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from src.app import app, db
        
        with app.app_context():
            # Import all essential models for comprehensive railway system
            from src.models import (
                User, Station, Train, TrainRoute, 
                Booking, Passenger, Payment, RefundRequest,
                ChartPreparation, TrainStatus, SeatAvailability,
                TatkalTimeSlot, Waitlist, GroupBooking, GroupMessage,
                GroupMemberPayment, GroupMemberInvitation,
                LoyaltyProgram, NotificationPreferences, TatkalOverride,
                PlatformManagement, TrainPlatformAssignment, ComplaintManagement,
                PerformanceMetrics, DynamicPricing, PNRStatusTracking
            )
            
            logger.info("Dropping existing tables...")
            db.drop_all()
            
            logger.info("Creating essential database schema...")
            db.create_all()
            
            # Verify essential tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            essential_tables = ['user', 'station', 'train', 'train_route', 'booking', 
                              'passenger', 'payment', 'refund_request', 'chart_preparation', 
                              'train_status', 'seat_availability', 'tatkal_time_slot', 
                              'waitlist', 'group_booking', 'group_message', 'group_member_payment',
                              'group_member_invitation', 'loyalty_program', 'notification_preferences',
                              'tatkal_override', 'platform_management', 'train_platform_assignment',
                              'complaint_management', 'performance_metrics', 'dynamic_pricing',
                              'pnr_status_tracking']
            
            created_tables = [t for t in essential_tables if t in tables]
            logger.info(f"✅ Created {len(created_tables)} essential tables: {', '.join(created_tables)}")
            logger.info(f"Removed unwanted tables - keeping only essential railway booking functionality")
            
            # Create users
            logger.info("Creating user accounts...")
            create_users(User, db)
            
            # Create comprehensive station data
            logger.info("Creating 1250 railway stations (South India focus)...")
            create_comprehensive_stations(Station, db)
            
            # Create extensive train network
            logger.info("Creating 1500 trains with realistic routes...")
            create_comprehensive_trains(Train, db)
            
            # Create train routes
            logger.info("Creating comprehensive train routes...")
            create_comprehensive_routes(Train, Station, TrainRoute, db)
            
            # Create essential system configurations
            logger.info("Creating system configurations...")
            create_system_configurations(TatkalTimeSlot, PlatformManagement, db)
            
            logger.info("🎉 Database setup completed successfully!")
            logger.info("Indian Railway System with 1250 stations, 1500 trains, and complete management system is ready")
            logger.info(f"Tables created: {', '.join(sorted(created_tables))}")
            
    except Exception as e:
        logger.error(f"❌ Database setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def create_users(User, db):
    """Create admin and regular user accounts"""
    from werkzeug.security import generate_password_hash
    
    # Admin user
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    admin = User(
        username='admin',
        email='admin@railway.gov.in',
        password_hash=generate_password_hash(admin_password),
        role='super_admin',
        active=True
    )
    
    # Regular user
    user = User(
        username='user',
        email='user@example.com',
        password_hash=generate_password_hash('user123'),
        role='user',
        active=True
    )
    
    db.session.add_all([admin, user])
    db.session.commit()
    logger.info("✅ Created admin (admin/admin123) and user (user/user123) accounts")

def create_comprehensive_stations(Station, db):
    """Create 1250 railway stations with South India focus"""
    
    # South Indian stations (majority focus)
    south_stations = [
        # Tamil Nadu - Major stations
        ('MAS', 'Chennai Central', 'Chennai', 'Tamil Nadu'),
        ('MSB', 'Chennai Beach', 'Chennai', 'Tamil Nadu'), 
        ('MS', 'Chennai Egmore', 'Chennai', 'Tamil Nadu'),
        ('TBM', 'Tambaram', 'Chennai', 'Tamil Nadu'),
        ('CGL', 'Chengalpattu', 'Chengalpattu', 'Tamil Nadu'),
        ('VM', 'Villupuram Junction', 'Villupuram', 'Tamil Nadu'),
        ('VRI', 'Vriddhachalam Junction', 'Vriddhachalam', 'Tamil Nadu'),
        ('TPJ', 'Tiruchirapalli Junction', 'Tiruchirappalli', 'Tamil Nadu'),
        ('TJ', 'Thanjavur Junction', 'Thanjavur', 'Tamil Nadu'),
        ('KMU', 'Kumbakonam', 'Kumbakonam', 'Tamil Nadu'),
        ('MV', 'Mayiladuthurai Junction', 'Mayiladuthurai', 'Tamil Nadu'),
        ('CDM', 'Chidambaram', 'Chidambaram', 'Tamil Nadu'),
        ('CU', 'Cuddalore Port', 'Cuddalore', 'Tamil Nadu'),
        ('PDY', 'Puducherry', 'Puducherry', 'Puducherry'),
        ('SHI', 'Shivakasi', 'Shivakasi', 'Tamil Nadu'),
        ('MDU', 'Madurai Junction', 'Madurai', 'Tamil Nadu'),
        ('DG', 'Dindigul Junction', 'Dindigul', 'Tamil Nadu'),
        ('KRR', 'Karur Junction', 'Karur', 'Tamil Nadu'),
        ('ED', 'Erode Junction', 'Erode', 'Tamil Nadu'),
        ('SA', 'Salem Junction', 'Salem', 'Tamil Nadu'),
        ('CBE', 'Coimbatore Junction', 'Coimbatore', 'Tamil Nadu'),
        ('PGT', 'Palakkad Town', 'Palakkad', 'Kerala'),
        ('TCR', 'Thrissur', 'Thrissur', 'Kerala'),
        ('AWY', 'Aluva', 'Ernakulam', 'Kerala'),
        ('ERS', 'Ernakulam Junction', 'Kochi', 'Kerala'),
        ('ERN', 'Ernakulam Town', 'Kochi', 'Kerala'),
        ('KTYM', 'Kottayam', 'Kottayam', 'Kerala'),
        ('CNGR', 'Chengannur', 'Chengannur', 'Kerala'),
        ('KYJ', 'Kayankulam Junction', 'Kayankulam', 'Kerala'),
        ('QLN', 'Kollam Junction', 'Kollam', 'Kerala'),
        ('TVC', 'Thiruvananthapuram Central', 'Thiruvananthapuram', 'Kerala'),
        ('CAPE', 'Kanyakumari', 'Kanyakumari', 'Tamil Nadu'),
        ('TEN', 'Tirunelveli Junction', 'Tirunelveli', 'Tamil Nadu'),
        ('VPT', 'Virudhunagar Junction', 'Virudhunagar', 'Tamil Nadu'),
        ('RMD', 'Ramanathapuram', 'Ramanathapuram', 'Tamil Nadu'),
        ('RMM', 'Rameswaram', 'Rameswaram', 'Tamil Nadu'),
        ('TMV', 'Tindivanam', 'Tindivanam', 'Tamil Nadu'),
        ('MLDT', 'Malda Town', 'Malda', 'West Bengal'),
        ('CLT', 'Kozhikode', 'Kozhikode', 'Kerala'),
        ('TLY', 'Thalassery', 'Thalassery', 'Kerala'),
        ('CAN', 'Kannur', 'Kannur', 'Kerala'),
        ('PAY', 'Payyanur', 'Payyanur', 'Kerala'),
        ('KZE', 'Kanhangad', 'Kanhangad', 'Kerala'),
        ('MAQ', 'Mangalore Junction', 'Mangalore', 'Karnataka'),
        ('MAJN', 'Mangalore Junction', 'Mangalore', 'Karnataka'),
        ('UD', 'Udupi', 'Udupi', 'Karnataka'),
        ('KUDA', 'Kundapura', 'Kundapura', 'Karnataka'),
        ('BYNR', 'Byndoor', 'Byndoor', 'Karnataka'),
        ('BTJL', 'Bhatkal', 'Bhatkal', 'Karnataka'),
        ('HNA', 'Honnavar', 'Honnavar', 'Karnataka'),
        ('KT', 'Kumta', 'Kumta', 'Karnataka'),
        ('GOK', 'Gokarna Road', 'Gokarna', 'Karnataka'),
        ('ANK', 'Ankola', 'Ankola', 'Karnataka'),
        ('KUD', 'Kudal', 'Kudal', 'Maharashtra'),
        
        # Karnataka - Major stations
        ('SBC', 'Bangalore City', 'Bangalore', 'Karnataka'),
        ('BNC', 'Bangalore Cantonment', 'Bangalore', 'Karnataka'),
        ('YPR', 'Yesvantpur Junction', 'Bangalore', 'Karnataka'),
        ('KJM', 'Krishnarajapuram', 'Bangalore', 'Karnataka'),
        ('BAND', 'Banaswadi', 'Bangalore', 'Karnataka'),
        ('MYS', 'Mysore Junction', 'Mysore', 'Karnataka'),
        ('ASK', 'Arsikere Junction', 'Arsikere', 'Karnataka'),
        ('HAS', 'Hassan Junction', 'Hassan', 'Karnataka'),
        ('SMET', 'Shimoga Town', 'Shimoga', 'Karnataka'),
        ('DVG', 'Davangere', 'Davangere', 'Karnataka'),
        ('UBL', 'Hubli Junction', 'Hubli', 'Karnataka'),
        ('DWR', 'Dharwad', 'Dharwad', 'Karnataka'),
        ('BGM', 'Belagavi', 'Belagavi', 'Karnataka'),
        ('GPB', 'Ghatprabha', 'Ghatprabha', 'Karnataka'),
        ('RNR', 'Ratnagiri', 'Ratnagiri', 'Maharashtra'),
        ('BAP', 'Belapur CBD', 'Navi Mumbai', 'Maharashtra'),
        ('TNA', 'Thane', 'Thane', 'Maharashtra'),
        ('KYN', 'Kalyan Junction', 'Kalyan', 'Maharashtra'),
        ('LNL', 'Lonavala', 'Lonavala', 'Maharashtra'),
        ('PUNE', 'Pune Junction', 'Pune', 'Maharashtra'),
        ('KRD', 'Karad', 'Karad', 'Maharashtra'),
        ('STR', 'Satara', 'Satara', 'Maharashtra'),
        ('KOP', 'Kolhapur CSMT', 'Kolhapur', 'Maharashtra'),
        
        # Andhra Pradesh & Telangana
        ('SC', 'Secunderabad Junction', 'Hyderabad', 'Telangana'),
        ('HYB', 'Hyderabad Deccan', 'Hyderabad', 'Telangana'),
        ('KCG', 'Kacheguda', 'Hyderabad', 'Telangana'),
        ('BMT', 'Begumpet', 'Hyderabad', 'Telangana'),
        ('LPI', 'Lingampalli', 'Hyderabad', 'Telangana'),
        ('WL', 'Warangal', 'Warangal', 'Telangana'),
        ('KZJ', 'Kazipet Junction', 'Warangal', 'Telangana'),
        ('BZA', 'Vijayawada Junction', 'Vijayawada', 'Andhra Pradesh'),
        ('TEL', 'Tenali Junction', 'Tenali', 'Andhra Pradesh'),
        ('OGL', 'Ongole', 'Ongole', 'Andhra Pradesh'),
        ('NLR', 'Nellore', 'Nellore', 'Andhra Pradesh'),
        ('GDR', 'Gudur Junction', 'Gudur', 'Andhra Pradesh'),
        ('RU', 'Renigunta Junction', 'Tirupati', 'Andhra Pradesh'),
        ('TPTY', 'Tirupati', 'Tirupati', 'Andhra Pradesh'),
        ('PUT', 'Puttur', 'Puttur', 'Andhra Pradesh'),
        ('KPD', 'Katpadi Junction', 'Vellore', 'Tamil Nadu'),
        ('JTJ', 'Jolarpettai Junction', 'Jolarpettai', 'Tamil Nadu'),
        ('BWT', 'Bangarapet', 'Bangarapet', 'Karnataka'),
        ('KJG', 'Karajgi', 'Karajgi', 'Karnataka'),
        ('GTL', 'Guntakal Junction', 'Guntakal', 'Andhra Pradesh'),
        ('ATP', 'Anantapur', 'Anantapur', 'Andhra Pradesh'),
        ('DMM', 'Dharmavaram Junction', 'Dharmavaram', 'Andhra Pradesh'),
        ('VSKP', 'Visakhapatnam', 'Visakhapatnam', 'Andhra Pradesh'),
        ('DVD', 'Duvvada', 'Visakhapatnam', 'Andhra Pradesh'),
        ('AKP', 'Anakapalle', 'Anakapalle', 'Andhra Pradesh'),
        ('TUNI', 'Tuni', 'Tuni', 'Andhra Pradesh'),
        ('RJY', 'Rajahmundry', 'Rajahmundry', 'Andhra Pradesh'),
        ('EE', 'Eluru', 'Eluru', 'Andhra Pradesh'),
        ('TEL', 'Tenali Junction', 'Tenali', 'Andhra Pradesh'),
        
        # Kerala - Additional stations
        ('PUU', 'Punalur', 'Punalur', 'Kerala'),
        ('SCT', 'Sengottai', 'Sengottai', 'Tamil Nadu'),
        ('TSI', 'Tenkasi Junction', 'Tenkasi', 'Tamil Nadu'),
        ('VPT', 'Virudhunagar Junction', 'Virudhunagar', 'Tamil Nadu'),
        ('SRT', 'Shoranur Junction', 'Shoranur', 'Kerala'),
        ('OTP', 'Ottapalam', 'Ottapalam', 'Kerala'),
        ('PLL', 'Pallipuram', 'Pallipuram', 'Kerala'),
        ('TIR', 'Tirur', 'Tirur', 'Kerala'),
        ('KTU', 'Kuttippuram', 'Kuttippuram', 'Kerala'),
        ('FK', 'Ferok', 'Ferok', 'Kerala'),
        ('WKI', 'Wadackanchery', 'Wadackanchery', 'Kerala'),
        ('TCR', 'Thrissur', 'Thrissur', 'Kerala'),
        ('PNQ', 'Punkunnam', 'Thrissur', 'Kerala'),
        ('IJK', 'Irinjalakuda', 'Irinjalakuda', 'Kerala'),
        ('CKI', 'Chalakudy', 'Chalakudy', 'Kerala'),
        ('AFK', 'Angamaly', 'Angamaly', 'Kerala'),
        ('AWY', 'Aluva', 'Aluva', 'Kerala'),
        ('ERS', 'Ernakulam Junction', 'Ernakulam', 'Kerala'),
        ('ERN', 'Ernakulam Town', 'Ernakulam', 'Kerala'),
        ('IPL', 'Idappally', 'Idappally', 'Kerala'),
        ('TRTR', 'Tripunithura', 'Tripunithura', 'Kerala'),
        ('KLMR', 'Kalamassery', 'Kalamassery', 'Kerala'),
        ('AWY', 'Aluva', 'Aluva', 'Kerala'),
    ]
    
    # Add North, East, West, and Central Indian stations to reach 1250 total
    other_stations = [
        # North India - Major stations
        ('NDLS', 'New Delhi', 'New Delhi', 'Delhi'),
        ('DEL', 'Delhi Junction', 'Delhi', 'Delhi'),
        ('DLI', 'Delhi', 'Delhi', 'Delhi'),
        ('NZM', 'Hazrat Nizamuddin', 'Delhi', 'Delhi'),
        ('ANVT', 'Anand Vihar Terminal', 'Delhi', 'Delhi'),
        ('DSB', 'Sadar Bazar', 'Delhi', 'Delhi'),
        ('LKO', 'Lucknow Junction', 'Lucknow', 'Uttar Pradesh'),
        ('CNB', 'Kanpur Central', 'Kanpur', 'Uttar Pradesh'),
        ('PRYJ', 'Prayagraj Junction', 'Prayagraj', 'Uttar Pradesh'),
        ('BSB', 'Varanasi Junction', 'Varanasi', 'Uttar Pradesh'),
        ('GKP', 'Gorakhpur Junction', 'Gorakhpur', 'Uttar Pradesh'),
        ('AGC', 'Agra Cantt', 'Agra', 'Uttar Pradesh'),
        ('MTJ', 'Mathura Junction', 'Mathura', 'Uttar Pradesh'),
        ('AF', 'Agra Fort', 'Agra', 'Uttar Pradesh'),
        ('TDL', 'Tundla Junction', 'Tundla', 'Uttar Pradesh'),
        ('ETW', 'Etawah Junction', 'Etawah', 'Uttar Pradesh'),
        ('CNB', 'Kanpur Central', 'Kanpur', 'Uttar Pradesh'),
        ('ON', 'Unnao Junction', 'Unnao', 'Uttar Pradesh'),
        ('LJN', 'Lucknow NE Railway', 'Lucknow', 'Uttar Pradesh'),
        ('GD', 'Gonda Junction', 'Gonda', 'Uttar Pradesh'),
        ('BST', 'Basti', 'Basti', 'Uttar Pradesh'),
        ('KLD', 'Khalilabad', 'Khalilabad', 'Uttar Pradesh'),
        ('GKP', 'Gorakhpur Junction', 'Gorakhpur', 'Uttar Pradesh'),
        ('DEOS', 'Deoria Sadar', 'Deoria', 'Uttar Pradesh'),
        ('SV', 'Siwan Junction', 'Siwan', 'Bihar'),
        ('CPR', 'Chhapra Junction', 'Chhapra', 'Bihar'),
        ('PNBE', 'Patna Junction', 'Patna', 'Bihar'),
        ('DNR', 'Danapur', 'Patna', 'Bihar'),
        ('RJPB', 'Rajendranagar', 'Patna', 'Bihar'),
        ('KIUL', 'Kiul Junction', 'Kiul', 'Bihar'),
        ('JAJ', 'Jhajha', 'Jhajha', 'Bihar'),
        ('JSME', 'Jasidih Junction', 'Jasidih', 'Jharkhand'),
        ('MDP', 'Madhupur Junction', 'Madhupur', 'Jharkhand'),
        ('ASN', 'Asansol Junction', 'Asansol', 'West Bengal'),
        
        # West India
        ('CSMT', 'Mumbai CST', 'Mumbai', 'Maharashtra'),
        ('LTT', 'Lokmanya Tilak Terminus', 'Mumbai', 'Maharashtra'),
        ('KYN', 'Kalyan Junction', 'Kalyan', 'Maharashtra'),
        ('NK', 'Nasik Road', 'Nasik', 'Maharashtra'),
        ('MMR', 'Manmad Junction', 'Manmad', 'Maharashtra'),
        ('BSL', 'Bhusaval Junction', 'Bhusaval', 'Maharashtra'),
        ('AK', 'Akola Junction', 'Akola', 'Maharashtra'),
        ('BD', 'Badnera Junction', 'Badnera', 'Maharashtra'),
        ('NGP', 'Nagpur', 'Nagpur', 'Maharashtra'),
        ('G', 'Gondia Junction', 'Gondia', 'Maharashtra'),
        ('R', 'Raipur Junction', 'Raipur', 'Chhattisgarh'),
        ('BIA', 'Bilaspur Junction', 'Bilaspur', 'Chhattisgarh'),
        ('JSG', 'Jharsuguda Junction', 'Jharsuguda', 'Odisha'),
        ('ROU', 'Rourkela', 'Rourkela', 'Odisha'),
        ('CKP', 'Chakradharpur', 'Chakradharpur', 'Jharkhand'),
        ('TATA', 'Tatanagar Junction', 'Jamshedpur', 'Jharkhand'),
        ('KGP', 'Kharagpur Junction', 'Kharagpur', 'West Bengal'),
        ('SRC', 'Santragachi Junction', 'Howrah', 'West Bengal'),
        ('HWH', 'Howrah Junction', 'Kolkata', 'West Bengal'),
        ('SDAH', 'Sealdah', 'Kolkata', 'West Bengal'),
        ('BWN', 'Barddhaman Junction', 'Bardhaman', 'West Bengal'),
        
        # Gujarat & Rajasthan
        ('ADI', 'Ahmedabad Junction', 'Ahmedabad', 'Gujarat'),
        ('BRC', 'Vadodara Junction', 'Vadodara', 'Gujarat'),
        ('ST', 'Surat', 'Surat', 'Gujarat'),
        ('BH', 'Bharuch Junction', 'Bharuch', 'Gujarat'),
        ('RTM', 'Ratlam Junction', 'Ratlam', 'Madhya Pradesh'),
        ('UJN', 'Ujjain Junction', 'Ujjain', 'Madhya Pradesh'),
        ('INDB', 'Indore Junction', 'Indore', 'Madhya Pradesh'),
        ('KOTA', 'Kota Junction', 'Kota', 'Rajasthan'),
        ('JP', 'Jaipur Junction', 'Jaipur', 'Rajasthan'),
        ('AF', 'Ajmer Junction', 'Ajmer', 'Rajasthan'),
        ('JU', 'Jodhpur Junction', 'Jodhpur', 'Rajasthan'),
        ('JSM', 'Jaisalmer', 'Jaisalmer', 'Rajasthan'),
        ('UDZ', 'Udaipur City', 'Udaipur', 'Rajasthan'),
        ('COR', 'Chittorgarh', 'Chittorgarh', 'Rajasthan'),
        
        # Central India
        ('BPL', 'Bhopal Junction', 'Bhopal', 'Madhya Pradesh'),
        ('HBJ', 'Habibganj', 'Bhopal', 'Madhya Pradesh'),
        ('JBP', 'Jabalpur', 'Jabalpur', 'Madhya Pradesh'),
        ('KTE', 'Katni', 'Katni', 'Madhya Pradesh'),
        ('STA', 'Satna', 'Satna', 'Madhya Pradesh'),
        ('MKP', 'Manikpur Junction', 'Manikpur', 'Uttar Pradesh'),
        ('GWL', 'Gwalior', 'Gwalior', 'Madhya Pradesh'),
        ('JHS', 'Jhansi Junction', 'Jhansi', 'Uttar Pradesh'),
        ('ORAI', 'Orai', 'Orai', 'Uttar Pradesh'),
        ('HPP', 'Hamirpur Road', 'Hamirpur', 'Uttar Pradesh'),
        
        # East India additional
        ('BBS', 'Bhubaneswar', 'Bhubaneswar', 'Odisha'),
        ('CTC', 'Cuttack', 'Cuttack', 'Odisha'),
        ('PURI', 'Puri', 'Puri', 'Odisha'),
        ('KUR', 'Khurda Road Junction', 'Khurda', 'Odisha'),
        ('BHC', 'Bhadrak', 'Bhadrak', 'Odisha'),
        ('BLS', 'Balasore', 'Balasore', 'Odisha'),
        
        # Northeast
        ('GHY', 'Guwahati', 'Guwahati', 'Assam'),
        ('KYQ', 'Kamakhya', 'Guwahati', 'Assam'),
        ('DLG', 'Dimapur', 'Dimapur', 'Nagaland'),
        ('FKG', 'Furkating Junction', 'Furkating', 'Assam'),
        ('MXN', 'Mariani Junction', 'Mariani', 'Assam'),
        ('NTSK', 'New Tinsukia', 'Tinsukia', 'Assam'),
        
        # Himachal & J&K
        ('JAT', 'Jammu Tawi', 'Jammu', 'Jammu & Kashmir'),
        ('UHP', 'Udhampur', 'Udhampur', 'Jammu & Kashmir'),
        ('KKDE', 'Kurukshetra', 'Kurukshetra', 'Haryana'),
        ('UMB', 'Ambala Cantt', 'Ambala', 'Haryana'),
        ('CDG', 'Chandigarh', 'Chandigarh', 'Chandigarh'),
        ('LDH', 'Ludhiana Junction', 'Ludhiana', 'Punjab'),
        ('JRC', 'Jalandhar City', 'Jalandhar', 'Punjab'),
        ('ASR', 'Amritsar Junction', 'Amritsar', 'Punjab'),
        ('ATT', 'Attari', 'Attari', 'Punjab'),
        ('DLI', 'Delhi', 'Delhi', 'Delhi'),
        ('KLK', 'Kalka', 'Kalka', 'Haryana'),
        ('SML', 'Shimla', 'Shimla', 'Himachal Pradesh'),
        ('UNA', 'Una Himachal', 'Una', 'Himachal Pradesh'),
        ('NLDM', 'Nangal Dam', 'Nangal', 'Punjab'),
    ]
    
    # Generate more stations to reach 1250 total
    additional_stations = []
    station_prefixes = ['KK', 'MM', 'NN', 'PP', 'RR', 'SS', 'TT', 'VV', 'WW', 'XX', 'YY', 'ZZ']
    south_cities = [
        'Salem', 'Coimbatore', 'Madurai', 'Trichy', 'Vellore', 'Tirunelveli', 
        'Erode', 'Dindigul', 'Karur', 'Tirupur', 'Namakkal', 'Dharmapuri',
        'Krishnagiri', 'Sivakasi', 'Rajapalayam', 'Sivaganga', 'Pudukkottai',
        'Ariyalur', 'Perambalur', 'Nagapattinam', 'Kanchipuram', 'Tiruvallur',
        'Vellore', 'Tiruvannamalai', 'Cuddalore', 'Kallakurichi', 'Ranipet',
        'Tenkasi', 'Virudhunagar', 'Theni', 'Kanyakumari', 'Tirunelveli',
        'Mysore', 'Tumkur', 'Bellary', 'Gulbarga', 'Bijapur', 'Bagalkot',
        'Bidar', 'Koppal', 'Gadag', 'Haveri', 'Uttara Kannada', 'Udupi',
        'Dakshina Kannada', 'Hassan', 'Kodagu', 'Mandya', 'Ramanagara', 'Kolar',
        'Chikkaballapur', 'Chitradurga', 'Davanagere', 'Shivamogga', 'Belagavi',
        'Vijayapura', 'Bagalkot', 'Bidar', 'Kalaburagi', 'Koppal', 'Raichur',
        'Yadgir', 'Chamarajanagar', 'Chikkamagaluru', 'Hassan', 'Kodagu',
        'Thiruvananthapuram', 'Kollam', 'Pathanamthitta', 'Alappuzha', 'Kottayam',
        'Idukki', 'Ernakulam', 'Thrissur', 'Palakkad', 'Malappuram', 'Kozhikode',
        'Wayanad', 'Kannur', 'Kasaragod', 'Hyderabad', 'Medchal', 'Rangareddy',
        'Vikarabad', 'Sangareddy', 'Medak', 'Kamareddy', 'Nizamabad', 'Jagtial',
        'Peddapalli', 'Jayashankar', 'Bhadradri', 'Mahabubabad', 'Warangal',
        'Hanamkonda', 'Jangaon', 'Siddipet', 'Yadadri', 'Rajanna', 'Karimnagar',
        'Mancherial', 'Adilabad', 'Komaram', 'Asifabad', 'Nirmal', 'Nizamabad',
        'Kamareddy', 'Rajanna Sircilla', 'Karimnagar', 'Peddapalli', 'Mancherial'
    ]
    
    # Generate additional South Indian stations
    counter = 1000
    for i in range(1200):  # Generate 1200 more stations to ensure we have enough unique ones
        prefix = random.choice(station_prefixes)
        city = random.choice(south_cities)
        state = random.choice(['Tamil Nadu', 'Karnataka', 'Kerala', 'Telangana', 'Andhra Pradesh'])
        
        code = f"{prefix}{counter:03d}"  # Use 3 digits to ensure uniqueness
        suffix = random.choice(['Junction', 'Central', 'Town', 'Road', 'Halt', 'Terminal', 'City', 'Cantt', 'Park'])
        name = f"{city} {suffix} {i % 100:02d}"  # Add number to ensure name uniqueness
        
        additional_stations.append((code, name, city, state))
        counter += 1
    
    # Combine all stations
    all_stations = south_stations + other_stations + additional_stations
    
    # Remove duplicates by code and name
    seen_codes = set()
    seen_names = set()
    unique_stations = []
    
    for code, name, city, state in all_stations:
        if code not in seen_codes and name not in seen_names:
            seen_codes.add(code)
            seen_names.add(name)
            unique_stations.append((code, name, city, state))
    
    # Take first 1250 unique stations
    stations_data = unique_stations[:1250]
    
    stations = []
    for code, name, city, state in stations_data:
        station = Station(
            name=name,
            code=code,
            city=city,
            state=state,
            active=True
        )
        stations.append(station)
    
    # Add stations in batches to handle large dataset
    batch_size = 100
    for i in range(0, len(stations), batch_size):
        batch = stations[i:i + batch_size]
        db.session.add_all(batch)
        db.session.commit()
        logger.info(f"Added stations batch {i//batch_size + 1}/{(len(stations)-1)//batch_size + 1}")
    
    logger.info(f"✅ Created {len(stations)} railway stations (South India focus)")

def create_comprehensive_trains(Train, db):
    """Create 1500 trains with realistic configurations"""
    
    # Train types with realistic parameters
    train_types = [
        ('Rajdhani Express', 400, 3.5, 40, 5.0),
        ('Shatabdi Express', 350, 3.0, 35, 4.5),
        ('Vande Bharat Express', 500, 4.0, 50, 6.0),
        ('Duronto Express', 450, 2.8, 45, 4.0),
        ('Superfast Express', 400, 2.0, 40, 3.0),
        ('Mail/Express', 380, 1.5, 38, 2.5),
        ('Intercity Express', 300, 1.8, 30, 2.8),
        ('Jan Shatabdi Express', 320, 2.2, 32, 3.2),
        ('Garib Rath', 350, 1.2, 35, 2.0),
        ('Humsafar Express', 380, 2.5, 38, 3.8),
        ('Tejas Express', 400, 3.2, 40, 4.8),
        ('Double Decker Express', 450, 2.8, 45, 4.2),
        ('AC Express', 350, 2.5, 35, 3.5),
        ('Passenger Express', 250, 0.8, 25, 1.2),
        ('Fast Passenger', 280, 1.0, 28, 1.6),
        ('MEMU', 200, 0.6, 20, 1.0),
        ('DMU', 150, 0.5, 15, 0.8),
        ('Local Express', 220, 0.7, 22, 1.1),
        ('Regional Express', 280, 1.2, 28, 2.0),
        ('Premium Express', 420, 3.8, 42, 5.5)
    ]
    
    # Famous Indian train names
    famous_trains = [
        'Rajdhani Express', 'Shatabdi Express', 'Duronto Express', 'Tamil Nadu Express',
        'Kerala Express', 'Karnataka Express', 'Andhra Pradesh Express', 'Deccan Queen',
        'Chennai Express', 'Mumbai Express', 'Bangalore Express', 'Mysore Express',
        'Coromandel Express', 'Island Express', 'Konkan Kanya Express', 'Mangalore Express',
        'Brindavan Express', 'Lalbagh Express', 'Chamundi Express', 'Tippu Express',
        'Udyan Express', 'Janmabhoomi Express', 'Godavari Express', 'Krishna Express',
        'Rayalaseema Express', 'Hamsa Express', 'Kaveri Express', 'Ganga Kaveri Express',
        'Trivandrum Express', 'Kanyakumari Express', 'Madras Mail', 'Grand Trunk Express',
        'Golden Temple Mail', 'Punjab Mail', 'Howrah Express', 'Kalka Mail',
        'Himalayan Queen', 'Nilgiri Express', 'Blue Mountain Express', 'Western Express',
        'Central Express', 'Eastern Express', 'Northern Express', 'Southern Express',
        'Gomti Express', 'Saryu Yamuna Express', 'Mahananda Express', 'Kanchanjunga Express',
        'Darjeeling Mail', 'Assam Express', 'Brahmaputra Mail', 'Northeast Express',
        'Capital Express', 'Rajya Rani Express', 'Jan Seva Express', 'Lok Shakti Express',
        'Sampark Kranti Express', 'Humsafar Express', 'Antyodaya Express', 'Tejas Express',
        'Vande Bharat Express', 'Gatimaan Express', 'Double Decker Express', 'AC Express'
    ]
    
    trains = []
    train_number = 12001
    
    for i in range(1500):
        # Select train type and configuration
        train_type, base_seats, base_fare, base_tatkal_seats, base_tatkal_fare = random.choice(train_types)
        
        # Select or generate train name
        if i < len(famous_trains):
            train_name = famous_trains[i]
        else:
            # Generate names for remaining trains
            prefixes = ['Super', 'Express', 'Fast', 'Premium', 'Special', 'Intercity', 'Jan', 'Sampark']
            suffixes = ['Express', 'Mail', 'Passenger', 'Special', 'Link']
            regions = ['South', 'North', 'East', 'West', 'Central', 'Coast', 'Hill', 'Valley']
            
            if random.random() < 0.3:  # 30% regional names
                train_name = f"{random.choice(regions)} {random.choice(suffixes)}"
            else:  # 70% prefix-suffix combinations
                train_name = f"{random.choice(prefixes)} {random.choice(suffixes)}"
        
        # Add variation to base parameters
        total_seats = base_seats + random.randint(-80, 120)
        fare_per_km = base_fare + random.uniform(-0.5, 0.8)
        tatkal_seats = base_tatkal_seats + random.randint(-10, 15)
        tatkal_fare_per_km = base_tatkal_fare + random.uniform(-0.8, 1.2)
        
        # Ensure reasonable bounds
        total_seats = max(120, min(600, total_seats))
        fare_per_km = max(0.4, min(5.0, fare_per_km))
        tatkal_seats = max(8, min(total_seats // 8, tatkal_seats))
        tatkal_fare_per_km = max(0.6, min(7.0, tatkal_fare_per_km))
        
        train = Train(
            number=str(train_number),
            name=train_name,
            total_seats=total_seats,
            available_seats=random.randint(total_seats - 100, total_seats),  # Some booking variation
            fare_per_km=fare_per_km,
            tatkal_seats=tatkal_seats,
            tatkal_fare_per_km=tatkal_fare_per_km,
            active=True
        )
        trains.append(train)
        train_number += 1
    
    # Add trains in batches
    batch_size = 50
    for i in range(0, len(trains), batch_size):
        batch = trains[i:i + batch_size]
        db.session.add_all(batch)
        db.session.commit()
        logger.info(f"Added trains batch {i//batch_size + 1}/{(len(trains)-1)//batch_size + 1}")
    
    logger.info(f"✅ Created {len(trains)} trains with realistic configurations")

def create_comprehensive_routes(Train, Station, TrainRoute, db):
    """Create comprehensive train routes connecting stations"""
    
    trains = Train.query.all()
    stations = Station.query.all()
    
    # Create station groups by region for logical routing
    station_groups = {
        'South': [s for s in stations if s.state in ['Tamil Nadu', 'Karnataka', 'Kerala', 'Andhra Pradesh', 'Telangana']],
        'North': [s for s in stations if s.state in ['Delhi', 'Uttar Pradesh', 'Punjab', 'Haryana', 'Himachal Pradesh', 'Jammu & Kashmir']],
        'West': [s for s in stations if s.state in ['Maharashtra', 'Gujarat', 'Rajasthan', 'Madhya Pradesh']],
        'East': [s for s in stations if s.state in ['West Bengal', 'Bihar', 'Jharkhand', 'Odisha']],
        'Northeast': [s for s in stations if s.state in ['Assam', 'Nagaland', 'Manipur', 'Mizoram', 'Tripura', 'Arunachal Pradesh', 'Meghalaya', 'Sikkim']],
        'Central': [s for s in stations if s.state in ['Chhattisgarh', 'Madhya Pradesh']]
    }
    
    routes = []
    route_batch_count = 0
    
    for train_idx, train in enumerate(trains):
        try:
            # Determine route type and length
            if 'Rajdhani' in train.name or 'Duronto' in train.name:
                route_length = random.randint(8, 15)  # Long distance
            elif 'Express' in train.name:
                route_length = random.randint(4, 10)  # Medium distance
            else:
                route_length = random.randint(3, 6)   # Short distance
            
            # Select starting region (bias towards South for South India focus)
            if random.random() < 0.6:  # 60% chance to start from South
                start_region = 'South'
            else:
                start_region = random.choice(list(station_groups.keys()))
            
            if not station_groups[start_region]:
                continue
                
            # Build route
            route_stations = []
            current_region = start_region
            
            # Add starting station
            start_station = random.choice(station_groups[current_region])
            route_stations.append(start_station)
            
            # Add intermediate stations
            for i in range(route_length - 2):
                # 70% chance to stay in same region, 30% to change
                if random.random() < 0.7 and len(station_groups[current_region]) > 1:
                    # Stay in same region
                    available_stations = [s for s in station_groups[current_region] if s not in route_stations]
                    if available_stations:
                        route_stations.append(random.choice(available_stations))
                    else:
                        # Change region if no stations available
                        other_regions = [r for r in station_groups.keys() if r != current_region and station_groups[r]]
                        if other_regions:
                            current_region = random.choice(other_regions)
                            route_stations.append(random.choice(station_groups[current_region]))
                else:
                    # Change region
                    other_regions = [r for r in station_groups.keys() if r != current_region and station_groups[r]]
                    if other_regions:
                        current_region = random.choice(other_regions)
                        available_stations = [s for s in station_groups[current_region] if s not in route_stations]
                        if available_stations:
                            route_stations.append(random.choice(available_stations))
            
            # Add end station from different region if possible
            end_regions = [r for r in station_groups.keys() if r != start_region and station_groups[r]]
            if end_regions:
                end_region = random.choice(end_regions)
                end_candidates = [s for s in station_groups[end_region] if s not in route_stations]
                if end_candidates:
                    route_stations.append(random.choice(end_candidates))
                else:
                    # Fallback to any station not in route
                    all_candidates = [s for s in stations if s not in route_stations]
                    if all_candidates:
                        route_stations.append(random.choice(all_candidates))
            else:
                # Fallback to any station not in route
                all_candidates = [s for s in stations if s not in route_stations]
                if all_candidates:
                    route_stations.append(random.choice(all_candidates))
            
            # Create route entries with realistic timings
            if len(route_stations) < 2:
                continue
                
            total_distance = 0
            current_time = time(random.randint(0, 23), random.randint(0, 59))  # Random start time
            
            for sequence, station in enumerate(route_stations):
                if sequence == 0:
                    # First station
                    departure_time = current_time
                    arrival_time = None
                    distance = 0
                elif sequence == len(route_stations) - 1:
                    # Last station
                    segment_distance = random.randint(80, 300)
                    total_distance += segment_distance
                    
                    # Add travel time (roughly 60-80 km/h average)
                    travel_minutes = int(segment_distance * random.uniform(0.75, 1.25)) + random.randint(5, 20)
                    current_time = add_minutes_to_time(current_time, travel_minutes)
                    
                    arrival_time = current_time
                    departure_time = None
                    distance = total_distance
                else:
                    # Intermediate station
                    segment_distance = random.randint(80, 300)
                    total_distance += segment_distance
                    
                    # Add travel time
                    travel_minutes = int(segment_distance * random.uniform(0.75, 1.25)) + random.randint(5, 20)
                    current_time = add_minutes_to_time(current_time, travel_minutes)
                    
                    arrival_time = current_time
                    
                    # Add halt time (2-20 minutes depending on station importance)
                    if 'Junction' in station.name or 'Central' in station.name:
                        halt_minutes = random.randint(8, 20)  # Major stations
                    else:
                        halt_minutes = random.randint(2, 8)   # Minor stations
                        
                    current_time = add_minutes_to_time(current_time, halt_minutes)
                    departure_time = current_time
                    distance = total_distance
                
                route = TrainRoute(
                    train_id=train.id,
                    station_id=station.id,
                    sequence=sequence + 1,
                    arrival_time=arrival_time,
                    departure_time=departure_time,
                    distance_from_start=distance
                )
                routes.append(route)
                
            # Batch commit every 100 trains to manage memory
            if (train_idx + 1) % 100 == 0:
                db.session.add_all(routes)
                db.session.commit()
                route_batch_count += len(routes)
                logger.info(f"Added routes for trains 1-{train_idx + 1} (Total routes: {route_batch_count})")
                routes = []  # Clear batch
                
        except Exception as e:
            logger.warning(f"Failed to create route for train {train.number}: {str(e)}")
            continue
    
    # Add remaining routes
    if routes:
        db.session.add_all(routes)
        db.session.commit()
        route_batch_count += len(routes)
    
    logger.info(f"✅ Created comprehensive routes for 1500 trains (Total routes: {route_batch_count})")

def add_minutes_to_time(time_obj, minutes):
    """Add minutes to a time object, handling day overflow"""
    dt = datetime.combine(date.today(), time_obj)
    dt += timedelta(minutes=minutes)
    return dt.time()

def create_sample_bookings(User, Train, Station, Booking, Passenger, Payment, db):
    """Create sample bookings for testing"""
    
    users = User.query.all()
    trains = Train.query.limit(100).all()  # Use first 100 trains for bookings
    
    if not users or not trains:
        logger.warning("⚠️  Missing users or trains for creating bookings")
        return
    
    bookings = []
    passengers = []
    payments = []
    
    # Create 200 sample bookings
    for i in range(200):
        try:
            user = random.choice(users)
            train = random.choice(trains)
            
            # Get route stations
            route_stations = [route.station for route in train.routes]
            if len(route_stations) < 2:
                continue
            
            from_station = random.choice(route_stations[:-1])
            remaining_stations = route_stations[route_stations.index(from_station) + 1:]
            to_station = random.choice(remaining_stations)
            
            # Generate booking details
            journey_date = date.today() + timedelta(days=random.randint(1, 45))
            passenger_count = random.randint(1, 6)
            
            # Calculate amount
            from_route = next((r for r in train.routes if r.station_id == from_station.id), None)
            to_route = next((r for r in train.routes if r.station_id == to_station.id), None)
            
            if not from_route or not to_route:
                continue
            
            distance = abs(to_route.distance_from_start - from_route.distance_from_start)
            base_amount = distance * train.fare_per_km * passenger_count
            total_amount = base_amount + random.uniform(50, 200)  # Add taxes and fees
            
            # Generate PNR
            pnr = f"PNR{2000000 + i}"
            
            # Status distribution
            status_choices = ['confirmed', 'waitlisted', 'cancelled']
            status = random.choices(status_choices, weights=[75, 20, 5])[0]
            
            booking = Booking(
                pnr=pnr,
                user_id=user.id,
                train_id=train.id,
                from_station_id=from_station.id,
                to_station_id=to_station.id,
                journey_date=journey_date,
                passengers=passenger_count,
                total_amount=total_amount,
                booking_type=random.choice(['general', 'tatkal']),
                quota='general',
                coach_class=random.choice(['SL', 'AC3', 'AC2', 'AC1', '2S', 'CC']),
                status=status
            )
            bookings.append(booking)
            
        except Exception as e:
            logger.warning(f"Failed to create booking {i}: {str(e)}")
            continue
    
    # Add bookings in batch
    db.session.add_all(bookings)
    db.session.commit()
    
    # Create passenger details
    for booking in bookings:
        for p_num in range(booking.passengers):
            passenger = Passenger(
                booking_id=booking.id,
                name=f"Passenger {p_num + 1}",
                age=random.randint(18, 75),
                gender=random.choice(['Male', 'Female']),
                id_proof_type='Aadhar',
                id_proof_number=f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            )
            passengers.append(passenger)
    
    db.session.add_all(passengers)
    db.session.commit()
    
    logger.info(f"✅ Created {len(bookings)} sample bookings with passenger details")

def create_system_configurations(TatkalTimeSlot, PlatformManagement, db):
    """Create essential system configurations"""
    from datetime import time
    
    # Create Tatkal time slots
    tatkal_ac = TatkalTimeSlot(
        name="AC Classes Tatkal",
        coach_classes="AC1,AC2,AC3,CC",
        open_time=time(10, 0),  # 10:00 AM
        close_time=time(23, 59),  # 11:59 PM
        days_before_journey=1,
        active=True
    )
    
    tatkal_nonac = TatkalTimeSlot(
        name="Non-AC Classes Tatkal", 
        coach_classes="SL,2S",
        open_time=time(11, 0),  # 11:00 AM
        close_time=time(23, 59),  # 11:59 PM
        days_before_journey=1,
        active=True
    )
    
    db.session.add_all([tatkal_ac, tatkal_nonac])
    
    # Create platform management entries for major stations
    major_stations = [
        ('MAS', 'Chennai Central', 12),
        ('SBC', 'Bangalore City', 10),
        ('TVC', 'Thiruvananthapuram Central', 6),
        ('CBE', 'Coimbatore Junction', 8),
        ('MDU', 'Madurai Junction', 6),
        ('ERS', 'Ernakulam Junction', 5),
        ('TPJ', 'Tiruchirapalli Junction', 7)
    ]
    
    platforms = []
    for code, name, platform_count in major_stations:
        # Find station by code
        station = Station.query.filter_by(code=code).first()
        if station:
            for i in range(1, platform_count + 1):
                platform = PlatformManagement(
                    station_id=station.id,
                    platform_number=str(i),
                    track_number=f"T{i}",
                    platform_length=400 if i <= 3 else 300,  # meters
                    electrified=True,
                    status='active'
                )
                platforms.append(platform)
    
    db.session.add_all(platforms)
    db.session.commit()
    logger.info(f"✅ Created {len(platforms)} platform entries and Tatkal configurations")

if __name__ == '__main__':
    setup_database()