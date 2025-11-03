"""
Train Generation
================
Generates trains with realistic fares.
"""

import random
from src.database import db
from src.models import Train
from .constants import MAJOR_STATIONS, TRAIN_TYPES


def generate_trains(count=1500):
    """Generate trains with realistic Indian Railway fares"""
    print(f"\n[TRAINS] Generating {count} trains with realistic fares...")
    
    trains = []
    for i in range(count):
        train_type = random.choice(TRAIN_TYPES)
        source = random.choice(MAJOR_STATIONS[:20])
        dest = random.choice([s for s in MAJOR_STATIONS[:30] if s != source])
        
        number = f"{train_type['prefix']}{(10001 + i) % 10000:04d}"
        name = f"{source[2]}-{dest[2]} {train_type['name']}"
        total_seats = train_type['total_seats'] + random.randint(-100, 100)
        tatkal_seats = int(total_seats * train_type['tatkal_pct'])
        
        base_fare = train_type['base_fare']
        tatkal_fare = base_fare * train_type['tatkal_multiplier']
        
        trains.append(Train(
            number=number,
            name=name,
            total_seats=total_seats,
            available_seats=total_seats,
            fare_per_km=round(base_fare, 2),
            tatkal_seats=tatkal_seats,
            tatkal_fare_per_km=round(tatkal_fare, 2),
            active=True
        ))
    
    db.session.bulk_save_objects(trains)
    db.session.commit()
    print(f"✓ Created {len(trains)} trains")
    return Train.query.all()
