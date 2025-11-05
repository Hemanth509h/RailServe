"""
Database Initialization Orchestrator
=====================================
Coordinates the entire database seeding process.
"""

from src.app import app
from src.models import Station, Train, TrainRoute, SeatAvailability
from .db_utils import reset_database
from .admin import create_admin_and_tatkal
from .stations import generate_stations
from .trains import generate_trains
from .routes import create_train_routes
from .availability import create_seat_availability


def initialize_database():
    """Main initialization function"""
    print("=" * 70)
    print(" " * 15 + "RailServe Database Initialization")
    print(" " * 20 + "(SQLite)")
    print("=" * 70)
    print("\n📋 This will create:")
    print("  • 1000 Indian railway stations")
    print("  • 1250 trains with seat numbers")
    print("  • Realistic multi-station train routes (5-15 stations per train)")
    print("  • Seat availability (150 trains × 7 days)")
    print("  • Admin user and Tatkal time slots")
    print("=" * 70)
    
    with app.app_context():
        reset_database()
        create_admin_and_tatkal()
        stations = generate_stations(1000)
        trains = generate_trains(1250)
        create_train_routes(trains, stations)
        create_seat_availability(trains)
        
        print("\n" + "=" * 70)
        print(" " * 20 + "✓ Initialization Complete!")
        print("=" * 70)
        print(f"\n📊 Database Summary:")
        print(f"  • Stations: {Station.query.count():,}")
        print(f"  • Trains: {Train.query.count():,}")
        print(f"  • Train Routes: {TrainRoute.query.count():,}")
        print(f"  • Seat Availability: {SeatAvailability.query.count():,}")
        print(f"\n🔐 Admin Login:")
        print(f"  • Username: admin")
        print(f"  • Password: admin123")
        print("\n" + "=" * 70)
