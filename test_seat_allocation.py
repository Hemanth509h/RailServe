#!/usr/bin/env python3
"""
Test script to verify seat allocation functionality
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import app
from src.database import db
from src.models import User, Train, Station, Booking, Passenger
from src.seat_allocation import SeatAllocator
from datetime import date, datetime

def test_seat_allocation():
    """Test the seat allocation system"""
    print("🧪 Testing Seat Allocation System")
    print("=" * 40)
    
    with app.app_context():
        # Get test data
        user = User.query.filter_by(username='testuser').first()
        train = Train.query.first()
        
        if not user or not train:
            print("❌ Test user or train not found. Run setup_database.py first.")
            return False
        
        # Create a test booking
        booking = Booking(
            user_id=user.id,
            train_id=train.id,
            from_station_id=1,
            to_station_id=2,
            journey_date=date(2025, 10, 15),
            passengers=2,
            total_amount=1500.00,
            booking_type='general',
            quota='general',
            coach_class='SL',
            status='confirmed'
        )
        
        db.session.add(booking)
        db.session.flush()  # Get booking ID
        
        # Create test passengers
        passengers_data = [
            {"name": "John Doe", "age": 30, "gender": "Male", "id_proof_type": "Aadhar", "id_proof_number": "123456789012", "seat_preference": "Lower"},
            {"name": "Jane Doe", "age": 28, "gender": "Female", "id_proof_type": "Aadhar", "id_proof_number": "123456789013", "seat_preference": "Upper"}
        ]
        
        for passenger_data in passengers_data:
            passenger = Passenger(
                booking_id=booking.id,
                name=passenger_data['name'],
                age=passenger_data['age'],
                gender=passenger_data['gender'],
                id_proof_type=passenger_data['id_proof_type'],
                id_proof_number=passenger_data['id_proof_number'],
                seat_preference=passenger_data['seat_preference'],
                coach_class='SL'
            )
            db.session.add(passenger)
        
        # Test seat allocation
        print(f"📋 Created test booking ID: {booking.id}")
        print(f"🚂 Train: {train.name} ({train.number})")
        print(f"👥 Passengers: {len(passengers_data)}")
        
        # Allocate seats
        allocator = SeatAllocator()
        success = allocator.allocate_seats(booking.id)
        
        if success:
            print("✅ Seat allocation successful!")
            
            # Check allocated seats
            passengers = Passenger.query.filter_by(booking_id=booking.id).all()
            for passenger in passengers:
                print(f"🎫 {passenger.name}: Seat {passenger.seat_number}, Berth: {passenger.berth_type}")
            
            # Clean up test data
            db.session.delete(booking)
            for passenger in passengers:
                db.session.delete(passenger)
            
            db.session.commit()
            print("🧹 Test data cleaned up")
            return True
        else:
            print("❌ Seat allocation failed!")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = test_seat_allocation()
    if success:
        print("\n🎉 Seat allocation test PASSED!")
    else:
        print("\n💥 Seat allocation test FAILED!")
    
    sys.exit(0 if success else 1)