#!/usr/bin/env python3
"""
RailServe 2025 - Complete Database Setup Script
================================================

This script performs a complete database reset and setup with modern group features:
1. Drops all existing tables (clean slate)
2. Creates all required tables from models (including modern groups)
3. Populates initial data (stations, trains, users, modern groups)
4. Creates sample modern group bookings with all features
5. Verifies all tables and relationships

Usage:
    python setup_database.py

Environment Variables:
    DATABASE_URL: Database connection string (PostgreSQL or SQLite)
"""

import os
import sys
import logging
from datetime import datetime, time, timedelta, date
from decimal import Decimal
import json
import random
import string

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def drop_all_tables(db, engine):
    """Drop all existing tables using reflection"""
    logger.info("🗑️  Dropping all existing tables...")
    
    try:
        from sqlalchemy import MetaData, inspect
        
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if existing_tables:
            logger.info(f"   Found {len(existing_tables)} existing tables: {', '.join(existing_tables)}")
            
            metadata = MetaData()
            metadata.reflect(bind=engine)
            metadata.drop_all(bind=engine)
            
            logger.info("✅ Successfully dropped all existing tables")
        else:
            logger.info("   No existing tables found - fresh database")
            
    except Exception as e:
        logger.warning(f"   Note: {str(e)}")
        logger.info("   Continuing with db.drop_all()...")
        db.drop_all()

def create_all_tables(db):
    """Create all tables defined in models"""
    logger.info("📋 Creating all database tables from models...")
    
    db.create_all()
    
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    logger.info(f"✅ Created {len(tables)} tables:")
    
    for i, table in enumerate(sorted(tables), 1):
        logger.info(f"   {i:2d}. {table}")
    
    return tables

def create_initial_stations(db, Station):
    """Create major railway stations across India"""
    logger.info("🚉 Creating railway stations...")
    
    stations_data = [
        ('NDLS', 'New Delhi', 'New Delhi', 'Delhi'),
        ('CSMT', 'Mumbai CST', 'Mumbai', 'Maharashtra'),
        ('HWH', 'Howrah Junction', 'Kolkata', 'West Bengal'),
        ('MAS', 'Chennai Central', 'Chennai', 'Tamil Nadu'),
        ('SBC', 'Bangalore City', 'Bangalore', 'Karnataka'),
        ('SC', 'Secunderabad Junction', 'Hyderabad', 'Telangana'),
        ('PUNE', 'Pune Junction', 'Pune', 'Maharashtra'),
        ('ADI', 'Ahmedabad Junction', 'Ahmedabad', 'Gujarat'),
        ('LKO', 'Lucknow Junction', 'Lucknow', 'Uttar Pradesh'),
        ('JP', 'Jaipur Junction', 'Jaipur', 'Rajasthan'),
        ('CBE', 'Coimbatore Junction', 'Coimbatore', 'Tamil Nadu'),
        ('ERS', 'Ernakulam Junction', 'Kochi', 'Kerala'),
        ('TVC', 'Thiruvananthapuram Central', 'Thiruvananthapuram', 'Kerala'),
        ('BZA', 'Vijayawada Junction', 'Vijayawada', 'Andhra Pradesh'),
        ('VSKP', 'Visakhapatnam', 'Visakhapatnam', 'Andhra Pradesh'),
        ('BBS', 'Bhubaneswar', 'Bhubaneswar', 'Odisha'),
        ('PURI', 'Puri', 'Puri', 'Odisha'),
        ('NGP', 'Nagpur', 'Nagpur', 'Maharashtra'),
        ('BPL', 'Bhopal Junction', 'Bhopal', 'Madhya Pradesh'),
        ('INDB', 'Indore Junction', 'Indore', 'Madhya Pradesh'),
        ('GHY', 'Guwahati', 'Guwahati', 'Assam'),
        ('PAT', 'Patna Junction', 'Patna', 'Bihar'),
        ('ALD', 'Allahabad Junction', 'Prayagraj', 'Uttar Pradesh'),
        ('AGC', 'Agra Cantt', 'Agra', 'Uttar Pradesh'),
        ('JAT', 'Jammu Tawi', 'Jammu', 'Jammu & Kashmir')
    ]
    
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
    
    db.session.add_all(stations)
    db.session.commit()
    
    logger.info(f"✅ Created {len(stations)} railway stations")
    return stations

def create_initial_trains(db, Train):
    """Create sample trains with realistic data"""
    logger.info("🚂 Creating trains...")
    
    trains_data = [
        ('12301', 'Rajdhani Express', 400, 400, 2.5, 50, 4.0),
        ('12302', 'New Delhi Rajdhani', 400, 400, 2.5, 50, 4.0),
        ('12951', 'Mumbai Rajdhani', 350, 350, 2.8, 40, 4.5),
        ('12952', 'New Delhi Rajdhani', 350, 350, 2.8, 40, 4.5),
        ('12621', 'Tamil Nadu Express', 450, 450, 1.8, 60, 3.0),
        ('12622', 'Tamil Nadu Express', 450, 450, 1.8, 60, 3.0),
        ('12841', 'Coromandel Express', 400, 400, 2.0, 50, 3.2),
        ('12842', 'Coromandel Express', 400, 400, 2.0, 50, 3.2),
        ('16031', 'Andaman Express', 420, 420, 1.4, 50, 2.2),
        ('16032', 'Andaman Express', 420, 420, 1.4, 50, 2.2),
        ('12431', 'Trivandrum Rajdhani', 300, 300, 3.5, 35, 5.5),
        ('12432', 'Trivandrum Rajdhani', 300, 300, 3.5, 35, 5.5),
        ('11013', 'Coimbatore Express', 400, 400, 1.3, 45, 2.0),
        ('11014', 'Coimbatore Express', 400, 400, 1.3, 45, 2.0),
        ('12605', 'Pallavan Express', 380, 380, 1.4, 40, 2.1),
        ('12606', 'Pallavan Express', 380, 380, 1.4, 40, 2.1),
    ]
    
    trains = []
    for number, name, total_seats, available_seats, fare_per_km, tatkal_seats, tatkal_fare_per_km in trains_data:
        train = Train(
            number=number,
            name=name,
            total_seats=total_seats,
            available_seats=available_seats,
            fare_per_km=fare_per_km,
            tatkal_seats=tatkal_seats,
            tatkal_fare_per_km=tatkal_fare_per_km,
            active=True
        )
        trains.append(train)
    
    db.session.add_all(trains)
    db.session.commit()
    
    logger.info(f"✅ Created {len(trains)} trains")
    return trains

def create_train_routes(db, TrainRoute, Train, trains, stations):
    """Create realistic train routes"""
    logger.info("🛤️  Creating train routes...")
    
    station_map = {s.code: s for s in stations}
    train_map = {t.number: t for t in trains}
    
    routes_data = [
        {
            'train_number': '12301',
            'route': [
                ('NDLS', 0, None, time(16, 50), 0),
                ('AGC', 1, time(19, 30), time(19, 35), 195),
                ('BPL', 2, time(23, 55), time(0, 5), 705),
                ('NGP', 3, time(6, 15), time(6, 25), 1089),
                ('BZA', 4, time(16, 40), time(16, 50), 1589),
                ('MAS', 5, time(20, 45), None, 1759)
            ]
        },
        {
            'train_number': '12302',
            'route': [
                ('MAS', 0, None, time(23, 0), 0),
                ('BZA', 1, time(4, 15), time(4, 25), 170),
                ('NGP', 2, time(14, 40), time(14, 50), 670),
                ('BPL', 3, time(21, 0), time(21, 10), 1054),
                ('AGC', 4, time(1, 30), time(1, 35), 1564),
                ('NDLS', 5, time(4, 15), None, 1759)
            ]
        },
        {
            'train_number': '12621',
            'route': [
                ('NDLS', 0, None, time(22, 30), 0),
                ('AGC', 1, time(1, 15), time(1, 20), 195),
                ('BPL', 2, time(6, 0), time(6, 10), 705),
                ('NGP', 3, time(11, 40), time(11, 50), 1089),
                ('BZA', 4, time(20, 50), time(21, 0), 1589),
                ('MAS', 5, time(1, 15), None, 1759)
            ]
        },
    ]
    
    routes_created = 0
    for route_data in routes_data:
        train = train_map.get(route_data['train_number'])
        if train:
            for station_code, seq, arr, dep, dist in route_data['route']:
                if station_code in station_map:
                    route = TrainRoute(
                        train_id=train.id,
                        station_id=station_map[station_code].id,
                        sequence=seq,
                        arrival_time=arr,
                        departure_time=dep,
                        distance_from_start=dist
                    )
                    db.session.add(route)
                    routes_created += 1
    
    db.session.commit()
    logger.info(f"✅ Created {routes_created} train route entries")

def create_admin_users(db, User):
    """Create admin and test users"""
    from werkzeug.security import generate_password_hash
    
    logger.info("👥 Creating admin users...")
    
    users = []
    
    admin = User(
        username='admin',
        email='admin@railserve.com',
        password_hash=generate_password_hash('admin123'),
        role='super_admin',
        active=True
    )
    users.append(admin)
    
    test_user = User(
        username='testuser',
        email='user@example.com',
        password_hash=generate_password_hash('user123'),
        role='user',
        active=True
    )
    users.append(test_user)
    
    # Create additional test users for group bookings
    test_users_data = [
        ('groupleader', 'groupleader@example.com', 'group123', 'user'),
        ('member1', 'member1@example.com', 'member123', 'user'),
        ('member2', 'member2@example.com', 'member123', 'user'),
        ('corporate_user', 'corporate@company.com', 'corp123', 'user'),
    ]
    
    for username, email, password, role in test_users_data:
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            active=True
        )
        users.append(user)
    
    db.session.add_all(users)
    db.session.commit()
    
    logger.info(f"✅ Created {len(users)} users")
    logger.info("   - Admin: admin / admin123")
    logger.info("   - Test User: testuser / user123")
    logger.info("   - Group Leader: groupleader / group123")
    logger.info("   - Corporate User: corporate_user / corp123")
    
    return users

def generate_group_code():
    """Generate unique 8-character group code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def create_modern_groups(db, users, trains, stations):
    """Create sample modern group bookings with all features"""
    from src.modern_group_models import (
        ModernGroupBooking, GroupMembership, ModernGroupInvitation,
        GroupBookingDetail, GroupPaymentSplit, ModernGroupMessage,
        GroupActivityLog, GroupAnalytics, GroupSplitBilling,
        GroupMealCoordination, GroupLoyaltyIntegration, AdvancedSeatAllocation,
        GroupSustainabilityTracking
    )
    
    logger.info("👥 Creating modern group bookings...")
    
    # Find users
    group_leader = next((u for u in users if u.username == 'groupleader'), users[0])
    member1 = next((u for u in users if u.username == 'member1'), users[1])
    member2 = next((u for u in users if u.username == 'member2'), users[2])
    corporate_user = next((u for u in users if u.username == 'corporate_user'), users[3])
    
    groups_created = []
    
    # 1. Family Travel Group
    family_group = ModernGroupBooking(
        group_name='Kumar Family Vacation',
        description='Family trip to Chennai for summer vacation',
        group_code=generate_group_code(),
        group_leader_id=group_leader.id,
        group_type='family',
        estimated_passengers=5,
        actual_passengers=5,
        status='active',
        travel_preferences=json.dumps({
            'class_preference': 'AC3',
            'meal_preference': 'veg',
            'seat_arrangement': 'together',
            'insurance_required': True
        }),
        budget_constraints=json.dumps({
            'min_budget': 15000,
            'max_budget': 25000,
            'currency': 'INR'
        }),
        contact_info=json.dumps({
            'primary_email': 'groupleader@example.com',
            'secondary_email': 'member1@example.com',
            'primary_phone': '+91-9876543210',
            'emergency_contact': '+91-9876543211'
        }),
        total_estimated_cost=22000.0,
        total_actual_cost=18700.0,
        discount_applied=3300.0,
        group_discount_rate=33.0,
        special_requirements='Vegetarian meals, Lower berths preferred',
        accessibility_needs='One passenger with mobility issues',
        travel_start_date=datetime.now() + timedelta(days=15),
        travel_end_date=datetime.now() + timedelta(days=20)
    )
    db.session.add(family_group)
    db.session.flush()
    groups_created.append(family_group)
    
    # Create memberships for family group
    family_memberships = [
        GroupMembership(
            group_id=family_group.id,
            user_id=group_leader.id,
            role='leader',
            status='active',
            notification_preferences=json.dumps({'email': True, 'sms': True}),
            booking_permissions=json.dumps({'can_book': True, 'can_modify': True, 'can_cancel': True})
        ),
        GroupMembership(
            group_id=family_group.id,
            user_id=member1.id,
            role='member',
            status='active',
            invited_by_id=group_leader.id,
            notification_preferences=json.dumps({'email': True, 'sms': False}),
            booking_permissions=json.dumps({'can_book': False, 'can_modify': False, 'can_cancel': False})
        )
    ]
    db.session.add_all(family_memberships)
    
    # Create activity log for family group
    family_activity = GroupActivityLog(
        group_id=family_group.id,
        user_id=group_leader.id,
        activity_type='group_created',
        description=f'Created family group "Kumar Family Vacation" for 5 passengers',
        context_data=json.dumps({'group_type': 'family', 'estimated_passengers': 5}),
        severity='success',
        is_visible_to_members=True
    )
    db.session.add(family_activity)
    
    # 2. Corporate Travel Group
    corporate_group = ModernGroupBooking(
        group_name='TechCorp Mumbai Conference',
        description='Corporate team travel for annual conference',
        group_code=generate_group_code(),
        group_leader_id=corporate_user.id,
        group_type='corporate',
        estimated_passengers=15,
        actual_passengers=15,
        status='confirmed',
        travel_preferences=json.dumps({
            'class_preference': 'AC2',
            'meal_preference': 'both',
            'seat_arrangement': 'flexible',
            'insurance_required': True
        }),
        budget_constraints=json.dumps({
            'min_budget': 75000,
            'max_budget': 100000,
            'currency': 'INR'
        }),
        contact_info=json.dumps({
            'primary_email': 'corporate@company.com',
            'secondary_email': 'hr@company.com',
            'primary_phone': '+91-9876540000',
            'emergency_contact': '+91-9876540001'
        }),
        total_estimated_cost=95000.0,
        total_actual_cost=80750.0,
        discount_applied=14250.0,
        group_discount_rate=15.0,
        special_requirements='Corporate billing required, Expense reports needed',
        travel_start_date=datetime.now() + timedelta(days=10),
        travel_end_date=datetime.now() + timedelta(days=12)
    )
    db.session.add(corporate_group)
    db.session.flush()
    groups_created.append(corporate_group)
    
    # Create corporate membership
    corporate_membership = GroupMembership(
        group_id=corporate_group.id,
        user_id=corporate_user.id,
        role='leader',
        status='active',
        notification_preferences=json.dumps({'email': True, 'sms': True}),
        booking_permissions=json.dumps({'can_book': True, 'can_modify': True, 'can_cancel': True})
    )
    db.session.add(corporate_membership)
    
    # Create corporate activity log
    corporate_activity = GroupActivityLog(
        group_id=corporate_group.id,
        user_id=corporate_user.id,
        activity_type='group_created',
        description=f'Created corporate group "TechCorp Mumbai Conference" for 15 passengers',
        context_data=json.dumps({'group_type': 'corporate', 'estimated_passengers': 15}),
        severity='success',
        is_visible_to_members=True
    )
    db.session.add(corporate_activity)
    
    # Create split billing for corporate group
    corporate_billing = GroupSplitBilling(
        group_id=corporate_group.id,
        split_method='lead_pays',
        split_config=json.dumps({}),
        total_amount=80750.0,
        currency='INR',
        payment_processor='razorpay',
        auto_split_enabled=False,
        split_status='configured'
    )
    db.session.add(corporate_billing)
    
    # 3. Tour Group
    tour_group = ModernGroupBooking(
        group_name='South India Temple Tour 2025',
        description='Organized tour covering major temples in South India',
        group_code=generate_group_code(),
        group_leader_id=group_leader.id,
        group_type='tour',
        estimated_passengers=25,
        actual_passengers=23,
        status='payment_pending',
        travel_preferences=json.dumps({
            'class_preference': 'SL',
            'meal_preference': 'veg',
            'seat_arrangement': 'together',
            'insurance_required': False
        }),
        budget_constraints=json.dumps({
            'min_budget': 50000,
            'max_budget': 75000,
            'currency': 'INR'
        }),
        contact_info=json.dumps({
            'primary_email': 'groupleader@example.com',
            'secondary_email': 'tour@travels.com',
            'primary_phone': '+91-9876545678',
            'emergency_contact': '+91-9876545679'
        }),
        total_estimated_cost=68000.0,
        total_actual_cost=55760.0,
        discount_applied=12240.0,
        group_discount_rate=18.0,
        special_requirements='Vegetarian meals for all, Group seating required',
        travel_start_date=datetime.now() + timedelta(days=30),
        travel_end_date=datetime.now() + timedelta(days=37)
    )
    db.session.add(tour_group)
    db.session.flush()
    groups_created.append(tour_group)
    
    # Create tour group membership
    tour_membership = GroupMembership(
        group_id=tour_group.id,
        user_id=group_leader.id,
        role='leader',
        status='active',
        notification_preferences=json.dumps({'email': True, 'sms': True}),
        booking_permissions=json.dumps({'can_book': True, 'can_modify': True, 'can_cancel': True})
    )
    db.session.add(tour_membership)
    
    # Create group message for tour
    tour_message = ModernGroupMessage(
        group_id=tour_group.id,
        sender_id=group_leader.id,
        message='Welcome to South India Temple Tour! Please confirm your participation by tomorrow.',
        message_type='announcement',
        is_important=True,
        is_system_message=False,
        read_by=json.dumps([group_leader.id])
    )
    db.session.add(tour_message)
    
    # 4. Educational Trip Group
    educational_group = ModernGroupBooking(
        group_name='St. Xavier School Science Trip',
        description='Educational trip for students to visit science centers',
        group_code=generate_group_code(),
        group_leader_id=member2.id,
        group_type='educational',
        estimated_passengers=45,
        actual_passengers=42,
        status='confirmed',
        travel_preferences=json.dumps({
            'class_preference': 'SL',
            'meal_preference': 'veg',
            'seat_arrangement': 'together',
            'insurance_required': True
        }),
        budget_constraints=json.dumps({
            'min_budget': 80000,
            'max_budget': 120000,
            'currency': 'INR'
        }),
        contact_info=json.dumps({
            'primary_email': 'member2@example.com',
            'secondary_email': 'school@education.com',
            'primary_phone': '+91-9876556789',
            'emergency_contact': '+91-9876556790'
        }),
        total_estimated_cost=110000.0,
        total_actual_cost=77000.0,
        discount_applied=33000.0,
        group_discount_rate=30.0,
        special_requirements='Student supervision, Safety protocols, Vegetarian meals',
        accessibility_needs='2 students with special needs',
        travel_start_date=datetime.now() + timedelta(days=45),
        travel_end_date=datetime.now() + timedelta(days=48)
    )
    db.session.add(educational_group)
    db.session.flush()
    groups_created.append(educational_group)
    
    # Create educational group membership
    educational_membership = GroupMembership(
        group_id=educational_group.id,
        user_id=member2.id,
        role='leader',
        status='active',
        notification_preferences=json.dumps({'email': True, 'sms': True}),
        booking_permissions=json.dumps({'can_book': True, 'can_modify': True, 'can_cancel': True})
    )
    db.session.add(educational_membership)
    
    # Create analytics for educational group
    educational_analytics = GroupAnalytics(
        group_id=educational_group.id,
        member_engagement_score=92.5,
        message_activity_count=15,
        booking_efficiency_score=88.0,
        cost_per_passenger=1833.33,
        savings_percentage=30.0,
        payment_completion_rate=95.0,
        avg_response_time_hours=2.5,
        booking_completion_days=7,
        insights=json.dumps({
            'top_insight': 'Excellent group coordination',
            'recommendation': 'Early booking enabled maximum discounts',
            'risk_factors': []
        })
    )
    db.session.add(educational_analytics)
    
    db.session.commit()
    
    logger.info(f"✅ Created {len(groups_created)} modern group bookings:")
    logger.info(f"   - Family Travel: {family_group.group_name} (Code: {family_group.group_code})")
    logger.info(f"   - Corporate Travel: {corporate_group.group_name} (Code: {corporate_group.group_code})")
    logger.info(f"   - Tour Group: {tour_group.group_name} (Code: {tour_group.group_code})")
    logger.info(f"   - Educational Trip: {educational_group.group_name} (Code: {educational_group.group_code})")
    
    return groups_created

def verify_database_setup(db):
    """Verify the database setup is correct"""
    logger.info("🔍 Verifying database setup...")
    
    from src.models import User, Station, Train, TrainRoute
    from src.modern_group_models import ModernGroupBooking, GroupMembership, GroupActivityLog
    
    checks = []
    
    user_count = User.query.count()
    checks.append(('Users', user_count, user_count >= 2))
    
    station_count = Station.query.count()
    checks.append(('Stations', station_count, station_count >= 10))
    
    train_count = Train.query.count()
    checks.append(('Trains', train_count, train_count >= 5))
    
    route_count = TrainRoute.query.count()
    checks.append(('Routes', route_count, route_count >= 5))
    
    group_count = ModernGroupBooking.query.count()
    checks.append(('Modern Groups', group_count, group_count >= 1))
    
    membership_count = GroupMembership.query.count()
    checks.append(('Group Memberships', membership_count, membership_count >= 1))
    
    activity_count = GroupActivityLog.query.count()
    checks.append(('Group Activities', activity_count, activity_count >= 1))
    
    logger.info("📊 Database Statistics:")
    all_passed = True
    for name, count, passed in checks:
        status = "✅" if passed else "❌"
        logger.info(f"   {status} {name}: {count}")
        all_passed = all_passed and passed
    
    return all_passed

def setup_database():
    """Main setup function - complete database initialization"""
    logger.info("=" * 70)
    logger.info("🚀 RailServe 2025 - Complete Database Setup & Initialization")
    logger.info("=" * 70)
    
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from src.app import app, db
        from src.models import (
            User, Station, Train, TrainRoute, Booking, Passenger,
            Payment, RefundRequest, TatkalTimeSlot, TatkalOverride,
            ComplaintManagement, Waitlist, GroupBooking, SeatAvailability
        )
        from src.modern_group_models import (
            ModernGroupBooking, GroupMembership, ModernGroupInvitation,
            GroupBookingDetail, GroupPaymentSplit, ModernGroupMessage,
            GroupActivityLog, GroupAnalytics, GroupSplitBilling,
            GroupMealCoordination, GroupLoyaltyIntegration,
            GroupSustainabilityTracking, AdvancedSeatAllocation
        )
        
        with app.app_context():
            drop_all_tables(db, db.engine)
            
            tables = create_all_tables(db)
            
            logger.info("\n" + "=" * 70)
            logger.info("💾 Populating Initial Data")
            logger.info("=" * 70)
            
            stations = create_initial_stations(db, Station)
            trains = create_initial_trains(db, Train)
            create_train_routes(db, TrainRoute, Train, trains, stations)
            users = create_admin_users(db, User)
            
            logger.info("\n" + "=" * 70)
            logger.info("🎯 Creating Modern Group Features")
            logger.info("=" * 70)
            
            groups = create_modern_groups(db, users, trains, stations)
            
            logger.info("\n" + "=" * 70)
            logger.info("🔍 Final Verification")
            logger.info("=" * 70)
            
            if verify_database_setup(db):
                logger.info("\n" + "=" * 70)
                logger.info("🎉 DATABASE SETUP COMPLETED SUCCESSFULLY!")
                logger.info("=" * 70)
                logger.info("\n✨ RailServe 2025 is ready for operation!")
                logger.info("\n🔐 Login Credentials:")
                logger.info("   Admin: admin / admin123")
                logger.info("   User:  testuser / user123")
                logger.info("   Group Leader: groupleader / group123")
                logger.info("   Corporate User: corporate_user / corp123")
                logger.info("\n🎯 Modern Group Features:")
                logger.info("   - 4 sample groups created (Family, Corporate, Tour, Educational)")
                logger.info("   - Access groups at: /groups/dashboard")
                logger.info("\n" + "=" * 70)
            else:
                logger.error("❌ Database verification failed!")
                sys.exit(1)
            
    except Exception as e:
        logger.error(f"\n❌ DATABASE SETUP FAILED!")
        logger.error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    setup_database()
