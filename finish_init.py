from datetime import datetime, date, time, timedelta
from src.app import app, db
from src.models import Train, TrainRoute, SeatAvailability, TatkalTimeSlot, User
import random

COACH_CLASSES = ['AC1', 'AC2', 'AC3', 'SL', '2S', 'CC']

with app.app_context():
    print("Finishing database initialization...")
    
    print("\n[1/2] Creating limited seat availability...")
    trains = Train.query.limit(150).all()
    today = date.today()
    total_records = 0
    availability_data = []
    
    for train in trains:
        routes = TrainRoute.query.filter_by(train_id=train.id).order_by(TrainRoute.sequence).limit(2).all()
        if len(routes) < 2:
            continue
        
        from_station_id = routes[0].station_id
        to_station_id = routes[1].station_id
        
        for days in range(7):
            journey_date = today + timedelta(days=days)
            for coach_class in COACH_CLASSES:
                capacity = int(train.total_seats * {'AC1': 0.05, 'AC2': 0.15, 'AC3': 0.25, 'SL': 0.35, '2S': 0.15, 'CC': 0.05}[coach_class])
                available = random.randint(int(capacity * 0.5), capacity)
                
                availability_data.append({
                    'train_id': train.id,
                    'from_station_id': from_station_id,
                    'to_station_id': to_station_id,
                    'journey_date': journey_date,
                    'coach_class': coach_class,
                    'quota': 'general',
                    'available_seats': available,
                    'waiting_list': random.randint(0, 10) if available < 10 else 0,
                    'rac_seats': random.randint(0, 5) if available < 20 else 0,
                    'last_updated': datetime.utcnow()
                })
                total_records += 1
                
                if len(availability_data) >= 500:
                    db.session.bulk_insert_mappings(SeatAvailability, availability_data)
                    db.session.commit()
                    availability_data = []
    
    if availability_data:
        db.session.bulk_insert_mappings(SeatAvailability, availability_data)
        db.session.commit()
    
    print(f"✓ Created {total_records:,} seat availability records")
    
    print("\n[2/2] Creating Tatkal time slots...")
    admin = User.query.filter_by(role='super_admin').first()
    if admin and not TatkalTimeSlot.query.first():
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
        print("✓ Tatkal slots created")
    else:
        print("✓ Tatkal slots already exist")
    
    print("\nDatabase initialization complete!")
    print(f"Stats: {Train.query.count()} trains, {TrainRoute.query.count()} routes, {SeatAvailability.query.count():,} availability records")
