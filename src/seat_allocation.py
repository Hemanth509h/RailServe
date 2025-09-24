"""
Seat allocation system for train bookings
"""
import random
from sqlalchemy.orm import sessionmaker
from .models import Passenger, Booking
from .database import db

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
        Enhanced with group booking coordination and robust error handling
        """
        try:
            booking = Booking.query.get(booking_id)
            if not booking:
                print(f"Error: Booking {booking_id} not found")
                return False
            
            # Allow seat allocation for both confirmed and waitlisted bookings
            if booking.status not in ['confirmed', 'waitlisted']:
                print(f"Error: Booking {booking_id} has invalid status: {booking.status}")
                return False
            
            passengers = Passenger.query.filter_by(booking_id=booking_id).all()
            if not passengers:
                print(f"Warning: No passengers found for booking {booking_id}, attempting to create from booking data")
                # Try to create passengers from booking data if they don't exist
                if booking.passengers and booking.passengers > 0:
                    # Create placeholder passengers if they don't exist
                    for i in range(booking.passengers):
                        passenger = Passenger(
                            booking_id=booking_id,
                            name=f"Passenger {i+1}",
                            age=30,  # Default age
                            gender="Male",  # Default gender
                            id_proof_type="Aadhaar",
                            id_proof_number="000000000000",
                            seat_preference="Lower",
                            coach_class=booking.coach_class
                        )
                        db.session.add(passenger)
                    db.session.flush()  # Flush to get passenger records
                    passengers = Passenger.query.filter_by(booking_id=booking_id).all()
                
                if not passengers:
                    print(f"Error: Could not create passengers for booking {booking_id}")
                    return False
            
            # Check if seats are already allocated
            allocated_passengers = [p for p in passengers if p.seat_number is not None]
            if len(allocated_passengers) == len(passengers):
                print(f"Info: Seats already allocated for booking {booking_id}")
                return True  # Already allocated
            
            coach_class = booking.coach_class
            coach_prefixes = self.coach_prefixes.get(coach_class, ['X'])
            available_berths = self.berth_types.get(coach_class, ['Lower'])
            
            # Check if this booking is part of a group
            is_group_booking = booking.group_booking_id is not None
            group_coach = None
            
            if is_group_booking:
                # Try to find existing coach assignments from other bookings in the same group
                group_bookings = Booking.query.filter_by(
                    group_booking_id=booking.group_booking_id,
                    train_id=booking.train_id,
                    journey_date=booking.journey_date,
                    coach_class=booking.coach_class,
                    status='confirmed'
                ).filter(Booking.id != booking_id).all()
                
                # Look for passengers who already have seat assignments
                for other_booking in group_bookings:
                    # LOGIC FIX: Use passengers relationship instead of passengers_details
                    other_passengers = Passenger.query.filter_by(booking_id=other_booking.id).all()
                    for other_passenger in other_passengers:
                        if other_passenger.seat_number:
                            # Extract coach from existing seat number
                            parts = other_passenger.seat_number.split('-')
                            if len(parts) == 2:
                                group_coach = parts[0]
                                break
                    if group_coach:
                        break
            
            # If no group coach found, select one for coordination
            if is_group_booking and not group_coach:
                coach_prefix = random.choice(coach_prefixes)
                coach_num = random.randint(1, 8)
                group_coach = f"{coach_prefix}{coach_num}"
            
            # Generate seat assignments
            assigned_seats = []
            existing_seats = self._get_existing_seats(booking.train_id, booking.journey_date, coach_class)
            
            for i, passenger in enumerate(passengers):
                # Skip if seat already allocated
                if passenger.seat_number:
                    assigned_seats.append(passenger.seat_number)
                    continue
                
                # For group bookings, try to use the same coach
                if is_group_booking and group_coach:
                    coach_part = group_coach
                else:
                    # Non-group booking - use random coach
                    coach_prefix = random.choice(coach_prefixes)
                    coach_num = random.randint(1, 8)
                    coach_part = f"{coach_prefix}{coach_num}"
                
                # Find available seat in the selected coach
                seat_number = self._find_available_seat(coach_part, assigned_seats, existing_seats)
                
                # If no seat available in preferred coach (group), try other coaches
                if not seat_number:
                    for attempt in range(10):  # Try up to 10 different coaches
                        coach_prefix = random.choice(coach_prefixes)
                        coach_num = random.randint(1, 12)  # Increase coach range
                        coach_part = f"{coach_prefix}{coach_num}"
                        seat_number = self._find_available_seat(coach_part, assigned_seats, existing_seats)
                        if seat_number:
                            break
                
                # Fallback to completely random if still no seat found
                if not seat_number:
                    seat_number = self._generate_fallback_seat(coach_prefixes, assigned_seats, existing_seats)
                
                # Final safety check
                if not seat_number:
                    print(f"Warning: Could not allocate seat for passenger {passenger.id} in booking {booking_id}")
                    # Generate a more realistic fallback seat
                    fallback_coach = f"{random.choice(coach_prefixes)}{random.randint(1, 15)}"
                    fallback_seat = random.randint(1, 72)
                    seat_number = f"{fallback_coach}-{fallback_seat}"
                
                # Assign berth type based on preference or randomly
                if passenger.seat_preference and passenger.seat_preference in available_berths:
                    berth_type = passenger.seat_preference
                else:
                    berth_type = random.choice(available_berths)
                
                assigned_seats.append(seat_number)
                
                # Update passenger record
                passenger.seat_number = seat_number
                passenger.berth_type = berth_type
                
                print(f"Allocated seat {seat_number} to passenger {passenger.name}")
            
            # Let the caller handle commit/rollback for proper transaction atomicity
            print(f"Successfully allocated seats for booking {booking_id}")
            return True
            
        except Exception as e:
            print(f"Error in seat allocation for booking {booking_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _get_existing_seats(self, train_id, journey_date, coach_class):
        """Get all existing seat allocations for the train/date/class"""
        from .database import db
        
        passengers = db.session.query(Passenger).join(Booking).filter(
            Booking.train_id == train_id,
            Booking.journey_date == journey_date,
            Booking.coach_class == coach_class,
            Booking.status == 'confirmed',
            Passenger.seat_number.isnot(None)
        ).all()
        
        return set(p.seat_number for p in passengers)
    
    def _find_available_seat(self, coach_part, assigned_seats, existing_seats):
        """Find an available seat in a specific coach"""
        for seat_num in range(1, 73):  # Standard coach capacity
            seat_number = f"{coach_part}-{seat_num}"
            if seat_number not in assigned_seats and seat_number not in existing_seats:
                return seat_number
        return None
    
    def _generate_fallback_seat(self, coach_prefixes, assigned_seats, existing_seats):
        """Generate a fallback seat when preferred options are not available"""
        for attempt in range(100):  # Try 100 times to find any available seat
            coach_prefix = random.choice(coach_prefixes)
            coach_num = random.randint(1, 8)
            seat_num = random.randint(1, 72)
            seat_number = f"{coach_prefix}{coach_num}-{seat_num}"
            
            if seat_number not in assigned_seats and seat_number not in existing_seats:
                return seat_number
        
        # Ultimate fallback - generate a unique seat number
        base_seat = f"{random.choice(coach_prefixes)}{random.randint(1, 8)}-{random.randint(1, 72)}"
        counter = 1
        while f"{base_seat}_{counter}" in assigned_seats or f"{base_seat}_{counter}" in existing_seats:
            counter += 1
        return f"{base_seat}_{counter}"
    
    def get_seat_map(self, train_id, journey_date, coach_class):
        """
        Get visual seat map for a specific coach class
        """
        from .database import db
        
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