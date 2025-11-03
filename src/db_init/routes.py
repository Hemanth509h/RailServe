"""
Train Route Generation
======================
Creates realistic multi-station routes for trains — in small batches (100 at a time).
"""

import random
from datetime import time
from src.database import db
from src.models import TrainRoute
from .constants import MAJOR_STATIONS


def create_train_routes(trains, stations):
    """Create realistic multi-station routes for all trains in batches"""
    print("\n[ROUTES] Creating realistic multi-station train routes (100 at a time)...")

    # Categorize stations
    major_hubs = [s for s in stations if any(s.name.startswith(ms[0]) for ms in MAJOR_STATIONS)]
    other_stations = [s for s in stations if s not in major_hubs]

    total_routes = 0
    batch_routes = []
    batch_count = 0

    for idx, train in enumerate(trains, start=1):
        train_name = train.name.lower()

        # Decide number of stops based on train type
        if 'rajdhani' in train_name or 'duronto' in train_name:
            num_stops = random.randint(5, 8)
        elif 'shatabdi' in train_name:
            num_stops = random.randint(6, 10)
        elif 'passenger' in train_name:
            num_stops = random.randint(10, 15)
        else:
            num_stops = random.randint(7, 12)

        # Choose route pattern
        if len(major_hubs) >= 2:
            start_hub = random.choice(major_hubs)
            end_hub = random.choice([h for h in major_hubs if h.id != start_hub.id])

            intermediate_count = num_stops - 2
            intermediate = []

            if intermediate_count > 0:
                available_hubs = [h for h in major_hubs if h.id not in [start_hub.id, end_hub.id]]
                hub_count = min(len(available_hubs), intermediate_count // 2)
                intermediate.extend(random.sample(available_hubs, hub_count))

                remaining = intermediate_count - len(intermediate)
                if remaining > 0 and other_stations:
                    intermediate.extend(random.sample(other_stations, min(remaining, len(other_stations))))

            route_stations = [start_hub] + intermediate + [end_hub]
        else:
            route_stations = random.sample(stations, min(num_stops, len(stations)))

        # Ensure uniqueness
        seen = set()
        unique_route = []
        for s in route_stations:
            if s.id not in seen:
                unique_route.append(s)
                seen.add(s.id)
        route_stations = unique_route[:num_stops]

        # Timing and distance simulation
        base_hour = random.randint(0, 23)
        base_minute = random.choice([0, 15, 30, 45])
        current_time = base_hour * 60 + base_minute
        cumulative_distance = 0

        for seq, station in enumerate(route_stations):
            is_first = (seq == 0)
            is_last = (seq == len(route_stations) - 1)

            if seq > 0:
                distance_increment = random.randint(50, 200)
                cumulative_distance += distance_increment
                travel_minutes = distance_increment + random.randint(5, 15)
                current_time += travel_minutes

            arrival_hour = (current_time // 60) % 24
            arrival_minute = current_time % 60
            arrival = time(arrival_hour, arrival_minute)

            if not is_last:
                halt_minutes = random.randint(2, 10) if not is_first else 0
                departure_time_minutes = current_time + halt_minutes
                departure_hour = (departure_time_minutes // 60) % 24
                departure_minute = departure_time_minutes % 60
                departure = time(departure_hour, departure_minute)
                current_time = departure_time_minutes
            else:
                departure = None

            batch_routes.append({
                'train_id': train.id,
                'station_id': station.id,
                'sequence': seq + 1,
                'arrival_time': None if is_first else arrival,
                'departure_time': departure,
                'distance_from_start': cumulative_distance
            })
            total_routes += 1

        # Every 100 trains, insert into DB and clear memory
        if idx % 100 == 0 or idx == len(trains):
            batch_count += 1
            try:
                db.session.bulk_insert_mappings(TrainRoute, batch_routes)
                db.session.commit()
                print(f"  ✅ Batch {batch_count}: Inserted routes for {idx} trains "
                      f"({len(batch_routes):,} new stops, total {total_routes:,})")
            except Exception as e:
                db.session.rollback()
                print(f"  ⚠️ Error in batch {batch_count}: {e}")
            batch_routes.clear()  # free memory

    avg_stops = total_routes / len(trains) if trains else 0
    print(f"\n✓ Created {total_routes:,} total route stops for {len(trains)} trains")
    print(f"  Average stops per train: {avg_stops:.1f}")
