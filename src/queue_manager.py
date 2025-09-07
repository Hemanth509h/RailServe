from collections import deque
import threading
from .models import Waitlist, Booking, Train
from .app import db
from datetime import datetime

class WaitlistManager:
    """FIFO queue-based waitlist management system"""
    
    def __init__(self):
        self._queues = {}  # train_id_date -> deque
        self._lock = threading.Lock()
    
    def _get_queue_key(self, train_id, journey_date):
        """Generate queue key for train and date"""
        return f"{train_id}_{journey_date}"
    
    def _get_queue(self, train_id, journey_date):
        """Get or create queue for train and date"""
        queue_key = self._get_queue_key(train_id, journey_date)
        
        if queue_key not in self._queues:
            self._queues[queue_key] = deque()
            # Load existing waitlist from database
            self._load_waitlist_from_db(train_id, journey_date, queue_key)
        
        return self._queues[queue_key]
    
    def _load_waitlist_from_db(self, train_id, journey_date, queue_key):
        """Load existing waitlist from database"""
        waitlist_entries = Waitlist.query.filter_by(
            train_id=train_id,
            journey_date=journey_date
        ).order_by(Waitlist.position).all()
        
        for entry in waitlist_entries:
            self._queues[queue_key].append({
                'booking_id': entry.booking_id,
                'position': entry.position,
                'created_at': entry.created_at
            })
    
    def add_to_waitlist(self, booking_id, train_id, journey_date):
        """Add booking to waitlist"""
        with self._lock:
            queue = self._get_queue(train_id, journey_date)
            
            # Get next position
            position = len(queue) + 1
            
            # Add to queue
            queue_item = {
                'booking_id': booking_id,
                'position': position,
                'created_at': datetime.utcnow()
            }
            queue.append(queue_item)
            
            # Add to database
            waitlist_entry = Waitlist(
                booking_id=booking_id,
                train_id=train_id,
                journey_date=journey_date,
                position=position
            )
            
            db.session.add(waitlist_entry)
            db.session.commit()
            
            return position
    
    def remove_from_waitlist(self, booking_id, train_id, journey_date):
        """Remove booking from waitlist"""
        with self._lock:
            queue = self._get_queue(train_id, journey_date)
            
            # Find and remove from queue
            for i, item in enumerate(queue):
                if item['booking_id'] == booking_id:
                    queue.remove(item)
                    break
            
            # Update positions in queue
            for i, item in enumerate(queue):
                item['position'] = i + 1
            
            # Update database
            Waitlist.query.filter_by(booking_id=booking_id).delete()
            
            # Update positions in database
            waitlist_entries = Waitlist.query.filter_by(
                train_id=train_id,
                journey_date=journey_date
            ).order_by(Waitlist.created_at).all()
            
            for i, entry in enumerate(waitlist_entries):
                entry.position = i + 1
            
            db.session.commit()
    
    def get_waitlist_position(self, booking_id, train_id, journey_date):
        """Get waitlist position for booking"""
        queue = self._get_queue(train_id, journey_date)
        
        for item in queue:
            if item['booking_id'] == booking_id:
                return item['position']
        
        return None
    
    def process_waitlist(self, train_id, journey_date, available_seats=None):
        """Process waitlist when seats become available"""
        with self._lock:
            if available_seats is None:
                train = Train.query.get(train_id)
                if not train:
                    return
                available_seats = train.available_seats
            
            queue = self._get_queue(train_id, journey_date)
            confirmed_bookings = []
            
            while available_seats > 0 and queue:
                # Get first booking in queue
                next_item = queue.popleft()
                booking = Booking.query.get(next_item['booking_id'])
                
                if not booking or booking.status != 'waitlisted':
                    continue
                
                if booking.passengers <= available_seats:
                    # Confirm booking
                    booking.status = 'confirmed'
                    available_seats -= booking.passengers
                    confirmed_bookings.append(booking)
                    
                    # Remove from waitlist database
                    Waitlist.query.filter_by(booking_id=booking.id).delete()
                else:
                    # Put back in queue if not enough seats
                    queue.appendleft(next_item)
                    break
            
            # Update train available seats
            train = Train.query.get(train_id)
            if train:
                train.available_seats = available_seats
            
            # Update positions for remaining waitlist
            for i, item in enumerate(queue):
                item['position'] = i + 1
                waitlist_entry = Waitlist.query.filter_by(
                    booking_id=item['booking_id']
                ).first()
                if waitlist_entry:
                    waitlist_entry.position = i + 1
            
            db.session.commit()
            
            return confirmed_bookings
    
    def get_waitlist_size(self, train_id, journey_date):
        """Get current waitlist size"""
        queue = self._get_queue(train_id, journey_date)
        return len(queue)
    
    def get_waitlist_details(self, train_id, journey_date):
        """Get detailed waitlist information"""
        queue = self._get_queue(train_id, journey_date)
        details = []
        
        for item in queue:
            booking = Booking.query.get(item['booking_id'])
            if booking:
                details.append({
                    'booking_id': booking.id,
                    'pnr': booking.pnr,
                    'user': booking.user.username,
                    'passengers': booking.passengers,
                    'position': item['position'],
                    'created_at': item['created_at']
                })
        
        return details
    
    def clear_expired_waitlists(self):
        """Clear waitlists for past dates"""
        from datetime import date
        
        expired_waitlists = Waitlist.query.filter(
            Waitlist.journey_date < date.today()
        ).all()
        
        for waitlist in expired_waitlists:
            # Cancel associated booking
            booking = Booking.query.get(waitlist.booking_id)
            if booking and booking.status == 'waitlisted':
                booking.status = 'cancelled'
        
        # Delete expired waitlist entries
        Waitlist.query.filter(
            Waitlist.journey_date < date.today()
        ).delete()
        
        db.session.commit()
        
        # Clear from memory queues
        expired_keys = []
        for key in self._queues.keys():
            try:
                train_id, date_str = key.split('_')
                queue_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                if queue_date < date.today():
                    expired_keys.append(key)
            except ValueError:
                continue
        
        for key in expired_keys:
            del self._queues[key]

# Global instance
waitlist_manager = WaitlistManager()
