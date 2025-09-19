"""
Seat allocation system for train bookings
"""
import random
from sqlalchemy.orm import sessionmaker
from .models import Passenger, Booking

class SeatAllocator:
    """Handles seat number assignment for confirmed bookings"""
    
    def __init__(self):
        self.coach_prefixes = {
            'SL': ['S', 'SL'],  # Sleeper class
            'AC3': ['B', 'A'],  # AC 3 Tier
            'AC2': ['A'],       # AC 2 Tier
            'AC1': ['H'],       # AC First Class
            '2S': ['D'],        # Second Seating
            'CC': ['C']         # Chair Car
        }
        
        self.berth_types = {
            'SL': ['Lower', 'Middle', 'Upper', 'Side Lower', 'Side Upper'],
            'AC3': ['Lower', 'Middle', 'Upper', 'Side Lower', 'Side Upper'],
            'AC2': ['Lower', 'Upper', 'Side Lower', 'Side Upper'],
            'AC1': ['Lower', 'Upper'],
            '2S': ['Window', 'Aisle', 'Middle'],
            'CC': ['Window', 'Aisle', 'Middle']
        }
    
    def allocate_seats(self, booking_id):
        """
        Allocate seat numbers for all passengers in a confirmed booking
        """
        from .app import db
        
        booking = Booking.query.get(booking_id)
        if not booking or booking.status != 'confirmed':
            return False
        
        passengers = Passenger.query.filter_by(booking_id=booking_id).all()
        if not passengers:
            return False
        
        coach_class = booking.coach_class
        coach_prefixes = self.coach_prefixes.get(coach_class, ['X'])
        available_berths = self.berth_types.get(coach_class, ['Lower'])
        
        # Generate seat assignments
        assigned_seats = []
        for i, passenger in enumerate(passengers):
            # Determine coach and seat number
            coach_num = random.randint(1, 8)  # Typical train has 1-8 coaches per class
            coach_prefix = random.choice(coach_prefixes)
            seat_num = random.randint(1, 72)  # Standard coach capacity
            
            seat_number = f"{coach_prefix}{coach_num}-{seat_num}"
            
            # Assign berth type based on preference or randomly
            if passenger.seat_preference and passenger.seat_preference in available_berths:
                berth_type = passenger.seat_preference
            else:
                berth_type = random.choice(available_berths)
            
            # Ensure no duplicate seats in this booking
            while seat_number in assigned_seats:
                seat_num = random.randint(1, 72)
                seat_number = f"{coach_prefix}{coach_num}-{seat_num}"
            
            assigned_seats.append(seat_number)
            
            # Update passenger record
            passenger.seat_number = seat_number
            passenger.berth_type = berth_type
        
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error allocating seats: {e}")
            return False
    
    def get_seat_map(self, train_id, journey_date, coach_class):
        """
        Get visual seat map for a specific coach class
        """
        from .app import db
        
        # Get all confirmed bookings for this train/date/class
        passengers = db.session.query(Passenger).join(Booking).filter(
            Booking.train_id == train_id,
            Booking.journey_date == journey_date,
            Booking.coach_class == coach_class,
            Booking.status == 'confirmed',
            Passenger.seat_number.isnot(None)
        ).all()
        
        occupied_seats = {p.seat_number: {
            'name': p.name,
            'age': p.age,
            'gender': p.gender,
            'berth_type': p.berth_type
        } for p in passengers}
        
        return occupied_seats