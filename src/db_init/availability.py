"""
Seat Availability Generation
=============================
Creates seat availability records for trains.
"""

import random
from datetime import date, datetime, timedelta
from src.database import db
from src.models import TrainRoute, SeatAvailability
from .constants import COACH_CLASSES, CLASS_CAPACITY_PERCENTAGES


def create_seat_availability(trains):
    """Create seat availability for first 150 trains × 7 days"""
    print("\n[SEAT AVAILABILITY] Creating availability for 150 trains × 7 days...")
    
    today = date.today()
    availability = []
    total = 0
    selected_trains = trains[:150]
    
    for idx, train in enumerate(selected_trains):
        routes = TrainRoute.query.filter_by(train_id=train.id).order_by(TrainRoute.sequence).limit(2).all()
        
        if len(routes) < 2:
            continue
        
        from_station = routes[0].station_id
        to_station = routes[1].station_id
        
        for day in range(7):
            journey_date = today + timedelta(days=day)
            
            for coach_class in COACH_CLASSES:
                total_class_seats = int(train.total_seats * CLASS_CAPACITY_PERCENTAGES.get(coach_class, 0.1))
                available_seats = random.randint(int(total_class_seats * 0.3), total_class_seats)
                
                availability.append({
                    'train_id': train.id,
                    'from_station_id': from_station,
                    'to_station_id': to_station,
                    'journey_date': journey_date,
                    'coach_class': coach_class,
                    'quota': 'general',
                    'available_seats': available_seats,
                    'waiting_list': random.randint(0, 20) if available_seats < 15 else 0,
                    'rac_seats': random.randint(0, 10) if available_seats < 25 else 0,
                    'last_updated': datetime.utcnow()
                })
                
                if len(availability) >= 500:
                    db.session.bulk_insert_mappings(SeatAvailability, availability)
                    db.session.commit()
                    total += len(availability)
                    availability = []
        
        if (idx + 1) % 30 == 0:
            print(f"  Progress: {idx + 1}/150 trains, {total:,} records...")
    
    if availability:
        db.session.bulk_insert_mappings(SeatAvailability, availability)
        db.session.commit()
        total += len(availability)
    
    print(f"✓ Created {total:,} seat availability records")
