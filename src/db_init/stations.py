"""
Station Generation
==================
Generates railway stations for the system.
"""

import random
from src.database import db
from src.models import Station
from .constants import MAJOR_STATIONS, INDIAN_CITIES


def generate_stations(count=1000):
    """Generate stations"""
    print(f"\n[STATIONS] Generating {count} stations...")
    stations = []
    codes_used = set()
    names_used = set()
    
    for name, code, city, state in MAJOR_STATIONS:
        stations.append(Station(
            name=name, code=code, city=city, state=state, active=True
        ))
        codes_used.add(code)
        names_used.add(name)
    
    station_types = ['Junction', 'Central', 'Terminal', 'City', 'Cantonment', 'Road', 'Station']
    
    for city, state in INDIAN_CITIES:
        for stype in station_types:
            if len(stations) >= count:
                break
            name = f"{city} {stype}"
            if name in names_used:
                continue
            
            code = ''.join([c[0] for c in name.split()[:3]]).upper()[:4]
            counter = 1
            while code in codes_used:
                code = code[:3] + str(counter)
                counter += 1
            
            stations.append(Station(
                name=name, code=code, city=city, state=state, active=True
            ))
            codes_used.add(code)
            names_used.add(name)
        
        if len(stations) >= count:
            break
    
    counter = 1
    while len(stations) < count:
        city, state = random.choice(INDIAN_CITIES)
        name = f"{city} Station {counter}"
        if name not in names_used:
            code = f"S{counter:04d}"
            stations.append(Station(
                name=name, code=code, city=city, state=state, active=True
            ))
            names_used.add(name)
        counter += 1
    
    db.session.bulk_save_objects(stations)
    db.session.commit()
    print(f"✓ Created {len(stations)} stations")
    return Station.query.all()
