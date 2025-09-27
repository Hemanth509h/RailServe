from .database import db
from flask_login import UserMixin
from datetime import datetime, timedelta
from sqlalchemy import event
import string
import random

class User(UserMixin, db.Model):
    """User model with role-based access control"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')  # user, admin, super_admin
    active = db.Column(db.Boolean, default=True)
    reset_token = db.Column(db.String(100))  # For password reset
    reset_token_expiry = db.Column(db.DateTime)  # Token expiry time
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)
    tatkal_timeslots = db.relationship('TatkalTimeSlot', backref='creator', lazy=True)
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
    
    @property
    def is_active(self):
        """Required by Flask-Login to check if user account is active"""
        return self.active
    
    def is_admin(self):
        return self.role in ['admin', 'super_admin']
    
    def is_super_admin(self):
        return self.role == 'super_admin'

class Station(db.Model):
    """Railway stations"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(10), nullable=False, unique=True)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Station, self).__init__(**kwargs)
    
    # Relationships
    train_routes = db.relationship('TrainRoute', backref='station', lazy=True)

class Train(db.Model):
    """Train information"""
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    fare_per_km = db.Column(db.Float, nullable=False)
    tatkal_seats = db.Column(db.Integer, default=0)  # Tatkal quota seats
    tatkal_fare_per_km = db.Column(db.Float)  # Premium Tatkal fare
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Train, self).__init__(**kwargs)
    
    # Relationships
    routes = db.relationship('TrainRoute', backref='train', lazy=True, order_by='TrainRoute.sequence')
    bookings = db.relationship('Booking', backref='train', lazy=True)

class TrainRoute(db.Model):
    """Train route information with stations"""
    id = db.Column(db.Integer, primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=False)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    sequence = db.Column(db.Integer, nullable=False)  # Order of station in route
    arrival_time = db.Column(db.Time)
    departure_time = db.Column(db.Time)
    distance_from_start = db.Column(db.Float, nullable=False)  # Distance in KM
    
    def __init__(self, **kwargs):
        super(TrainRoute, self).__init__(**kwargs)
    
    __table_args__ = (db.UniqueConstraint('train_id', 'sequence'),)

class Booking(db.Model):
    """Booking information"""
    id = db.Column(db.Integer, primary_key=True)
    pnr = db.Column(db.String(10), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=False)
    from_station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    to_station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    journey_date = db.Column(db.Date, nullable=False)
    passengers = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    booking_type = db.Column(db.String(10), default='general')  # general, tatkal
    quota = db.Column(db.String(20), default='general')  # general, ladies, senior, disability, tatkal
    coach_class = db.Column(db.String(10), default='SL')  # AC1, AC2, AC3, SL, 2S, CC
    status = db.Column(db.String(20), default='pending_payment')  # confirmed, waitlisted, cancelled, pending_payment, rac
    waitlist_type = db.Column(db.String(10), default='GNWL')  # GNWL, RAC, PQWL, RLWL, TQWL
    chart_prepared = db.Column(db.Boolean, default=False)
    berth_preference = db.Column(db.String(20), default='No Preference')  # Lower, Middle, Upper, Side Lower, Side Upper, Window, Aisle
    current_reservation = db.Column(db.Boolean, default=False)  # Post-chart booking
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    cancellation_charges = db.Column(db.Float, default=0.0)
    group_booking_id = db.Column(db.Integer, db.ForeignKey('group_booking.id'))  # Link to group booking
    loyalty_discount = db.Column(db.Float, default=0.0)  # Loyalty program discount applied
    
    def __init__(self, **kwargs):
        super(Booking, self).__init__(**kwargs)
    
    # Relationships
    from_station = db.relationship('Station', foreign_keys=[from_station_id])
    to_station = db.relationship('Station', foreign_keys=[to_station_id])
    payment = db.relationship('Payment', backref='booking', uselist=False)
    waitlist = db.relationship('Waitlist', backref='booking', uselist=False)
    passengers_details = db.relationship('Passenger', backref='booking', lazy=True)

class Passenger(db.Model):
    """Passenger details for bookings"""
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)  # Male, Female, Other
    id_proof_type = db.Column(db.String(20), nullable=False)  # Aadhar, PAN, Passport, etc.
    id_proof_number = db.Column(db.String(50), nullable=False)
    seat_preference = db.Column(db.String(20), default='No Preference')  # Lower, Middle, Upper, Window, Aisle
    coach_class = db.Column(db.String(10), default='SL')  # AC1, AC2, AC3, SL, 2S, CC
    seat_number = db.Column(db.String(20))  # Assigned seat number like "S1-45", "B2-32", "A1-18"
    berth_type = db.Column(db.String(20))  # Lower, Middle, Upper, Side Lower, Side Upper
    
    def __init__(self, **kwargs):
        super(Passenger, self).__init__(**kwargs)
    
    def get_seat_explanation(self):
        """Get a detailed explanation of the allocated seat"""
        if not self.seat_number or not self.berth_type:
            return "Seat allocation pending - will be assigned after chart preparation"
        
        # Parse seat number (e.g., "S1-45" -> coach="S1", seat="45")
        parts = self.seat_number.split('-')
        if len(parts) != 2:
            return f"Seat: {self.seat_number}, Berth: {self.berth_type}"
        
        coach_part, seat_part = parts
        
        # Extract coach type and number
        coach_type = ''.join([c for c in coach_part if c.isalpha()])
        coach_num = ''.join([c for c in coach_part if c.isdigit()])
        
        # Explain coach type
        coach_explanations = {
            'S': 'Sleeper Class',
            'SL': 'Sleeper Class', 
            'B': 'AC 3-Tier',
            'A': 'AC 2-Tier',
            'H': 'AC First Class',
            'D': 'Second Class Seating',
            'C': 'Chair Car'
        }
        
        coach_description = coach_explanations.get(coach_type, 'Coach')
        
        # Explain berth type with comfort details
        berth_explanations = {
            'Lower': 'Lower Berth - Easy access, can sit during day, ideal for elderly/families',
            'Middle': 'Middle Berth - Mid-level, foldable during day, good for adult travelers',
            'Upper': 'Upper Berth - High level, private space, suitable for agile travelers',
            'Side Lower': 'Side Lower Berth - Single berth, more privacy, can sit during day',
            'Side Upper': 'Side Upper Berth - Single upper berth, maximum privacy',
            'Window': 'Window Seat - Scenic views, natural light',
            'Aisle': 'Aisle Seat - Easy access to corridor and facilities',
            'Middle': 'Middle Seat - Between window and aisle'
        }
        
        berth_description = berth_explanations.get(self.berth_type, self.berth_type)
        
        explanation = f"Coach {coach_part} ({coach_description}), Seat {seat_part} - {berth_description}"
        
        # Add allocation reason based on preference
        if self.seat_preference and self.seat_preference != 'No Preference':
            if self.berth_type == self.seat_preference:
                explanation += f" ✓ Allocated as per your preference: {self.seat_preference}"
            else:
                explanation += f" (Your preference: {self.seat_preference} was not available)"
        
        return explanation
    
    def get_coach_location_info(self):
        """Get information about coach location and facilities"""
        if not self.seat_number:
            return "Coach location will be available after seat allocation"
        
        coach_part = self.seat_number.split('-')[0] if '-' in self.seat_number else self.seat_number
        coach_type = ''.join([c for c in coach_part if c.isalpha()])
        
        location_info = {
            'S': "Usually located in the middle of the train. Basic facilities with charging points.",
            'SL': "Usually located in the middle of the train. Basic facilities with charging points.",
            'B': "AC coaches located towards front/rear. Climate controlled with charging points and reading lights.",
            'A': "Premium AC coaches, usually towards front. Enhanced comfort with premium facilities.",
            'H': "First class coaches at the front. Luxury amenities and premium service.",
            'D': "Seating coaches, usually at front/rear. Comfortable seats for day journeys.",
            'C': "Chair car coaches with reclining seats. Good for shorter journeys."
        }
        
        return location_info.get(coach_type, "Coach location will be informed at the platform.")
    
    @property
    def comfort_rating(self):
        """Get a comfort rating for the allocated seat"""
        if not self.berth_type:
            return None
        
        comfort_scores = {
            'Lower': 9,  # Most comfortable
            'Side Lower': 8,
            'Middle': 6,
            'Upper': 5,
            'Side Upper': 7,
            'Window': 8,
            'Aisle': 7
        }
        
        return comfort_scores.get(self.berth_type, 5)


class Payment(db.Model):
    """Payment information"""
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)  # card, upi, netbanking
    transaction_id = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')  # success, failed, pending
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # CRITICAL: Database-level constraint to prevent duplicate payments
    __table_args__ = (db.UniqueConstraint('booking_id', 'status', name='uq_booking_payment_success'),)
    
    def __init__(self, **kwargs):
        super(Payment, self).__init__(**kwargs)

class Waitlist(db.Model):
    """Waitlist management"""
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=False)
    journey_date = db.Column(db.Date, nullable=False)
    position = db.Column(db.Integer, nullable=False)
    waitlist_type = db.Column(db.String(10), default='GNWL')  # GNWL, RAC, PQWL, RLWL, TQWL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Waitlist, self).__init__(**kwargs)

# Event listeners for PNR generation
@event.listens_for(Booking, 'before_insert')
def generate_pnr(mapper, connection, target):
    """Generate unique PNR number"""
    if not target.pnr:
        while True:
            pnr = ''.join(random.choices(string.digits, k=10))
            existing = connection.execute(
                db.text("SELECT id FROM booking WHERE pnr = :pnr"), 
                {"pnr": pnr}
            ).fetchone()
            if not existing:
                target.pnr = pnr
                break

class TatkalTimeSlot(db.Model):
    """Tatkal booking time slot configuration"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "AC Classes", "Non-AC Classes"
    coach_classes = db.Column(db.String(200))  # Comma-separated list: "AC1,AC2,AC3,CC"
    open_time = db.Column(db.Time, nullable=False)  # When Tatkal booking opens (e.g., 10:00 AM)
    close_time = db.Column(db.Time)  # When Tatkal booking closes (optional)
    days_before_journey = db.Column(db.Integer, default=1)  # How many days before journey date
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # Admin who created this
    
    def __init__(self, **kwargs):
        super(TatkalTimeSlot, self).__init__(**kwargs)
    
    def get_coach_classes_list(self):
        """Get list of coach classes from comma-separated string"""
        if self.coach_classes:
            return [cls.strip() for cls in self.coach_classes.split(',')]
        return []
    
    def is_currently_open(self, journey_date):
        """Check if Tatkal booking is currently open for given journey date"""
        from datetime import datetime, timedelta
        
        if not self.active:
            return False
            
        # Calculate when this time slot opens
        tatkal_open_date = journey_date - timedelta(days=self.days_before_journey)
        
        # Check if we're on or after the open date
        today = datetime.now().date()
        current_time = datetime.now().time()
        
        if today < tatkal_open_date:
            return False  # Too early
        elif today > tatkal_open_date:
            return True   # Already past open date
        else:
            # Today is the open date, check time
            if current_time >= self.open_time:
                if self.close_time:
                    return current_time <= self.close_time
                return True
            return False

class RefundRequest(db.Model):
    """TDR (Ticket Deposit Receipt) and refund management"""
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)  # Train cancelled, delay, AC failure, etc.
    amount_paid = db.Column(db.Float, nullable=False)
    refund_amount = db.Column(db.Float, nullable=False)
    cancellation_charges = db.Column(db.Float, default=0.0)
    tdr_number = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, completed
    filed_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    # Relationships
    booking = db.relationship('Booking', backref='refund_requests', lazy=True)
    user = db.relationship('User', backref='refund_requests', lazy=True)
    
    def __init__(self, **kwargs):
        super(RefundRequest, self).__init__(**kwargs)
        if not self.tdr_number:
            self.tdr_number = f"TDR{datetime.utcnow().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
    
    def validate_refund_amount(self):
        """Ensure refund amount doesn't exceed amount paid"""
        return self.refund_amount <= self.amount_paid

class TrainStatus(db.Model):
    """Live train status tracking"""
    id = db.Column(db.Integer, primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=False)
    current_station_id = db.Column(db.Integer, db.ForeignKey('station.id'))
    status = db.Column(db.String(50), default='On Time')  # On Time, Delayed, Cancelled, Diverted
    delay_minutes = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    journey_date = db.Column(db.Date, nullable=False)
    
    # Relationships
    current_station = db.relationship('Station', foreign_keys=[current_station_id])
    
    def __init__(self, **kwargs):
        super(TrainStatus, self).__init__(**kwargs)

class SeatAvailability(db.Model):
    """Real-time seat availability tracking"""
    id = db.Column(db.Integer, primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=False)
    from_station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    to_station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    journey_date = db.Column(db.Date, nullable=False)
    coach_class = db.Column(db.String(10), nullable=False)
    quota = db.Column(db.String(20), default='general')
    available_seats = db.Column(db.Integer, default=0)
    waiting_list = db.Column(db.Integer, default=0)
    rac_seats = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(SeatAvailability, self).__init__(**kwargs)

class ChartPreparation(db.Model):
    """Chart preparation tracking"""
    id = db.Column(db.Integer, primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=False)
    journey_date = db.Column(db.Date, nullable=False)
    chart_prepared_at = db.Column(db.DateTime)
    final_chart_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, prepared, final
    confirmed_from_waitlist = db.Column(db.Integer, default=0)
    cancelled_waitlist = db.Column(db.Integer, default=0)
    
    def __init__(self, **kwargs):
        super(ChartPreparation, self).__init__(**kwargs)


class GroupBooking(db.Model):
    """Group booking for multiple passengers (families, tour groups)"""
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100), nullable=False)
    group_leader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_passengers = db.Column(db.Integer, nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    contact_phone = db.Column(db.String(15), nullable=False)
    booking_type = db.Column(db.String(20), default='family')  # family, corporate, tour, religious
    special_requirements = db.Column(db.Text)
    discount_applied = db.Column(db.Float, default=0.0)
    group_discount_rate = db.Column(db.Float, default=0.0)  # Percentage discount for groups
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    group_leader = db.relationship('User', backref='group_bookings')
    individual_bookings = db.relationship('Booking', backref='group_booking', lazy=True, 
                                         foreign_keys='Booking.group_booking_id')
    
    def __init__(self, **kwargs):
        super(GroupBooking, self).__init__(**kwargs)
    
    def get_total_amount(self):
        """Calculate total amount for all bookings in the group"""
        try:
            # Use a database query instead of iterating over relationship
            from sqlalchemy import func
            result = db.session.query(func.sum(Booking.total_amount)).filter(
                Booking.group_booking_id == self.id
            ).scalar()
            return result or 0.0
        except:
            return 0.0
    
    @property
    def total_amount(self):
        """Property to access total amount for template compatibility"""
        return self.get_total_amount()
    
    def get_confirmed_bookings(self):
        """Get confirmed bookings in the group"""
        try:
            # Use a database query instead of iterating over relationship
            return Booking.query.filter(
                Booking.group_booking_id == self.id,
                Booking.status == 'confirmed'
            ).all()
        except:
            return []
    
    def get_all_passengers(self):
        """Get all passengers in the group"""
        passengers = []
        bookings = Booking.query.filter_by(group_booking_id=self.id).all()
        for booking in bookings:
            passengers.extend(booking.passengers_details)
        return passengers
    
    def get_seat_coordination_info(self):
        """Get information about seat coordination for the group"""
        passengers = self.get_all_passengers()
        if not passengers:
            return "No passengers in group yet"
        
        # Group passengers by train and coach
        train_coaches = {}
        for passenger in passengers:
            if passenger.seat_number:
                # Parse seat number (e.g., "S1-45" -> coach="S1", seat="45")
                parts = passenger.seat_number.split('-')
                if len(parts) == 2:
                    coach = parts[0]
                    bookings = Booking.query.filter_by(group_booking_id=self.id).all()
                    booking = next((b for b in bookings if passenger in b.passengers_details), None)
                    if booking and booking.train:
                        train_key = f"{booking.train.name}"
                        if train_key not in train_coaches:
                            train_coaches[train_key] = {}
                        if coach not in train_coaches[train_key]:
                            train_coaches[train_key][coach] = []
                        train_coaches[train_key][coach].append(passenger.name)
        
        if not train_coaches:
            return "Seat allocation pending for all passengers"
        
        # Generate coordination report
        info = []
        for train, coaches in train_coaches.items():
            if len(coaches) == 1:
                coach_name = list(coaches.keys())[0]
                info.append(f"✅ All passengers in {train} are in coach {coach_name}")
            else:
                coach_list = ", ".join(coaches.keys())
                info.append(f"⚠️ Passengers in {train} are spread across coaches: {coach_list}")
        
        return " | ".join(info) if info else "Seat coordination information not available"
    
    def get_payment_summary(self):
        """Get payment summary for the group"""
        total_amount = self.get_total_amount()
        confirmed_bookings = self.get_confirmed_bookings()
        paid_amount = sum(booking.total_amount for booking in confirmed_bookings if booking.payment_status == 'paid')
        
        return {
            'total_amount': total_amount,
            'paid_amount': paid_amount,
            'pending_amount': total_amount - paid_amount,
            'payment_percentage': (paid_amount / total_amount * 100) if total_amount > 0 else 0
        }

class GroupMemberInvitation(db.Model):
    """Invitations for group booking members"""
    id = db.Column(db.Integer, primary_key=True)
    group_booking_id = db.Column(db.Integer, db.ForeignKey('group_booking.id'), nullable=False)
    inviter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    invited_email = db.Column(db.String(120), nullable=False)
    invited_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # If user exists
    status = db.Column(db.String(20), default='pending')  # pending, accepted, declined, expired
    invitation_code = db.Column(db.String(50), unique=True, nullable=False)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    responded_at = db.Column(db.DateTime)
    
    # Relationships
    group_booking = db.relationship('GroupBooking', backref='member_invitations')
    inviter = db.relationship('User', foreign_keys=[inviter_id])
    invited_user = db.relationship('User', foreign_keys=[invited_user_id])
    
    def __init__(self, **kwargs):
        super(GroupMemberInvitation, self).__init__(**kwargs)
        if not self.invitation_code:
            import uuid
            self.invitation_code = str(uuid.uuid4())[:8].upper()
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(days=7)
    
    def is_expired(self):
        """Check if invitation has expired"""
        return datetime.utcnow() > self.expires_at
    
    def can_accept(self):
        """Check if invitation can still be accepted"""
        return self.status == 'pending' and not self.is_expired()

class GroupMemberPayment(db.Model):
    """Track individual payments within group bookings"""
    id = db.Column(db.Integer, primary_key=True)
    group_booking_id = db.Column(db.Integer, db.ForeignKey('group_booking.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount_due = db.Column(db.Float, nullable=False)
    amount_paid = db.Column(db.Float, default=0.0)
    payment_method = db.Column(db.String(20))  # credit_card, debit_card, upi, wallet
    payment_reference = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, partial, paid, failed
    due_date = db.Column(db.DateTime)
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    group_booking = db.relationship('GroupBooking', backref='member_payments')
    booking = db.relationship('Booking', backref='group_payment')
    user = db.relationship('User', backref='group_payments')
    
    def __init__(self, **kwargs):
        super(GroupMemberPayment, self).__init__(**kwargs)
        if not self.due_date:
            self.due_date = datetime.utcnow() + timedelta(days=3)
    
    @property
    def remaining_amount(self):
        """Amount still pending payment"""
        return max(0, self.amount_due - self.amount_paid)
    
    def is_overdue(self):
        """Check if payment is overdue"""
        return datetime.utcnow() > self.due_date and self.status != 'paid'

class GroupMessage(db.Model):
    """Messages within group bookings for coordination"""
    id = db.Column(db.Integer, primary_key=True)
    group_booking_id = db.Column(db.Integer, db.ForeignKey('group_booking.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='general')  # general, announcement, reminder
    is_important = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_by = db.Column(db.Text)  # JSON array of user IDs who have read the message
    
    # Relationships
    group_booking = db.relationship('GroupBooking', backref='messages')
    sender = db.relationship('User', backref='group_messages')
    
    def __init__(self, **kwargs):
        super(GroupMessage, self).__init__(**kwargs)
        if not self.read_by:
            self.read_by = '[]'
    
    def mark_as_read(self, user_id):
        """Mark message as read by user"""
        import json
        read_list = json.loads(self.read_by) if self.read_by else []
        if user_id not in read_list:
            read_list.append(user_id)
            self.read_by = json.dumps(read_list)
    
    def is_read_by(self, user_id):
        """Check if message is read by user"""
        import json
        read_list = json.loads(self.read_by) if self.read_by else []
        return user_id in read_list

class LoyaltyProgram(db.Model):
    """Frequent traveler loyalty program"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    membership_number = db.Column(db.String(20), unique=True, nullable=False)
    tier = db.Column(db.String(20), default='Silver')  # Silver, Gold, Platinum, Diamond
    points_earned = db.Column(db.Integer, default=0)
    points_redeemed = db.Column(db.Integer, default=0)
    total_journeys = db.Column(db.Integer, default=0)
    total_distance = db.Column(db.Float, default=0.0)
    total_spent = db.Column(db.Float, default=0.0)
    tier_valid_until = db.Column(db.Date)
    benefits_active = db.Column(db.Boolean, default=True)
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    member = db.relationship('User', backref='loyalty_program')
    
    def __init__(self, **kwargs):
        super(LoyaltyProgram, self).__init__(**kwargs)
        if not self.membership_number:
            self.membership_number = f"RL{datetime.utcnow().strftime('%Y')}{random.randint(100000, 999999)}"
    
    @property
    def current_points(self):
        """Current available points"""
        return self.points_earned - self.points_redeemed
    
    def calculate_tier(self):
        """Calculate membership tier based on annual spend"""
        if self.total_spent >= 100000:  # ₹1,00,000
            return 'Diamond'
        elif self.total_spent >= 50000:  # ₹50,000
            return 'Platinum'
        elif self.total_spent >= 25000:  # ₹25,000
            return 'Gold'
        else:
            return 'Silver'
    
    def get_discount_percentage(self):
        """Get discount percentage based on tier"""
        discounts = {
            'Silver': 2,
            'Gold': 5,
            'Platinum': 8,
            'Diamond': 12
        }
        return discounts.get(self.tier, 0)

class NotificationPreferences(db.Model):
    """User notification preferences"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    email_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=True)
    push_notifications = db.Column(db.Boolean, default=True)
    booking_confirmations = db.Column(db.Boolean, default=True)
    journey_reminders = db.Column(db.Boolean, default=True)
    train_delay_alerts = db.Column(db.Boolean, default=True)
    promotional_offers = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', backref='notification_preferences')
    
    def __init__(self, **kwargs):
        super(NotificationPreferences, self).__init__(**kwargs)

class TatkalOverride(db.Model):
    """Admin override control for Tatkal booking availability"""
    id = db.Column(db.Integer, primary_key=True)
    is_enabled = db.Column(db.Boolean, default=False)
    enabled_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    enabled_at = db.Column(db.DateTime, default=datetime.utcnow)
    override_message = db.Column(db.String(200), default='Tatkal booking enabled by admin')
    coach_classes = db.Column(db.String(200))  # Comma-separated list of classes, empty means all
    train_ids = db.Column(db.Text)  # Comma-separated list of train IDs, empty means all trains
    valid_until = db.Column(db.DateTime)  # Optional expiry time
    
    # Relationships
    admin_user = db.relationship('User', foreign_keys=[enabled_by])
    
    def __init__(self, **kwargs):
        super(TatkalOverride, self).__init__(**kwargs)
    
    def get_coach_classes_list(self):
        """Get list of coach classes from comma-separated string"""
        if self.coach_classes:
            return [cls.strip() for cls in self.coach_classes.split(',') if cls.strip()]
        return []  # Empty list means all classes
    
    def get_train_ids_list(self):
        """Get list of train IDs from comma-separated string"""
        if self.train_ids:
            return [int(tid.strip()) for tid in self.train_ids.split(',') if tid.strip().isdigit()]
        return []  # Empty list means all trains
    
    def applies_to_train(self, train_id):
        """Check if this override applies to a specific train"""
        if not self.is_valid():
            return False
        train_list = self.get_train_ids_list()
        return not train_list or train_id in train_list
    
    def is_valid(self):
        """Check if override is currently valid"""
        if not self.is_enabled:
            return False
        if self.valid_until and datetime.utcnow() > self.valid_until:
            return False
        return True
    
    @classmethod
    def get_active_override(cls):
        """Get the currently active Tatkal override"""
        return cls.query.filter_by(is_enabled=True).order_by(cls.enabled_at.desc()).first()

# New Models for Real Railway Management System Features

class PlatformManagement(db.Model):
    """Platform and track assignment management"""
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    platform_number = db.Column(db.String(10), nullable=False)  # Platform 1, 2A, 3B, etc.
    track_number = db.Column(db.String(10))  # Track assignment
    platform_length = db.Column(db.Integer)  # Length in meters
    electrified = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='active')  # active, maintenance, closed
    facilities = db.Column(db.Text)  # Waiting room, food stall, etc.
    wheelchair_accessible = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    station = db.relationship('Station', backref='platforms')
    
    def __init__(self, **kwargs):
        super(PlatformManagement, self).__init__(**kwargs)

class TrainPlatformAssignment(db.Model):
    """Real-time platform assignments for trains"""
    id = db.Column(db.Integer, primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=False)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    platform_id = db.Column(db.Integer, db.ForeignKey('platform_management.id'), nullable=False)
    journey_date = db.Column(db.Date, nullable=False)
    arrival_platform = db.Column(db.String(10))
    departure_platform = db.Column(db.String(10))
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    train = db.relationship('Train')
    station = db.relationship('Station')
    platform = db.relationship('PlatformManagement')
    assigned_by_user = db.relationship('User')
    
    def __init__(self, **kwargs):
        super(TrainPlatformAssignment, self).__init__(**kwargs)

class ComplaintManagement(db.Model):
    """Customer complaint and query management system"""
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))  # Optional, if related to booking
    category = db.Column(db.String(50), nullable=False)  # Booking, Refund, Train, Food, Staff, etc.
    subcategory = db.Column(db.String(50))  # Seat allotment, AC problem, etc.
    priority = db.Column(db.String(10), default='medium')  # low, medium, high, urgent
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved, closed
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))  # Admin handling the complaint
    resolution = db.Column(db.Text)
    satisfaction_rating = db.Column(db.Integer)  # 1-5 rating from user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='complaints')
    booking = db.relationship('Booking', backref='complaints')
    assigned_admin = db.relationship('User', foreign_keys=[assigned_to])
    
    def __init__(self, **kwargs):
        super(ComplaintManagement, self).__init__(**kwargs)
        if not self.ticket_number:
            self.ticket_number = f"CMP{datetime.utcnow().strftime('%Y%m%d')}{random.randint(1000, 9999)}"

class PerformanceMetrics(db.Model):
    """System performance and KPI tracking"""
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(100), nullable=False)  # passenger_load, on_time_performance, revenue_per_km, etc.
    metric_value = db.Column(db.Float, nullable=False)
    metric_unit = db.Column(db.String(20))  # percentage, rupees, minutes, count
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'))  # Optional, for train-specific metrics
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'))  # Optional, for station-specific metrics
    date_recorded = db.Column(db.Date, nullable=False)
    time_recorded = db.Column(db.DateTime, default=datetime.utcnow)
    benchmark_value = db.Column(db.Float)  # Target/standard value
    variance_percentage = db.Column(db.Float)  # How much above/below benchmark
    
    # Relationships
    train = db.relationship('Train')
    station = db.relationship('Station')
    
    def __init__(self, **kwargs):
        super(PerformanceMetrics, self).__init__(**kwargs)



class DynamicPricing(db.Model):
    """Dynamic pricing based on demand and occupancy"""
    id = db.Column(db.Integer, primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=False)
    journey_date = db.Column(db.Date, nullable=False)
    coach_class = db.Column(db.String(10), nullable=False)
    base_fare = db.Column(db.Float, nullable=False)
    surge_multiplier = db.Column(db.Float, default=1.0)  # 1.0 = no surge, 1.5 = 50% increase
    current_occupancy = db.Column(db.Float, default=0.0)  # Percentage occupied
    demand_factor = db.Column(db.Float, default=1.0)  # Based on historical demand
    special_event = db.Column(db.String(100))  # Festival, holiday, etc.
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    train = db.relationship('Train')
    
    def __init__(self, **kwargs):
        super(DynamicPricing, self).__init__(**kwargs)
    
    def calculate_dynamic_fare(self, base_amount):
        """Calculate final fare with dynamic pricing"""
        return base_amount * self.surge_multiplier

class PNRStatusTracking(db.Model):
    """Enhanced PNR status tracking and journey details"""
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    current_status = db.Column(db.String(50), nullable=False)  # Confirmed, RAC, Waitlisted, Chart Prepared, etc.
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    next_update_time = db.Column(db.DateTime)  # When status might change
    coach_position = db.Column(db.String(100))  # Position of coach in train (front, middle, rear)
    boarding_time = db.Column(db.Time)  # Recommended boarding time
    platform_number = db.Column(db.String(10))
    special_instructions = db.Column(db.Text)  # Any special instructions for passenger
    
    # Relationships
    booking = db.relationship('Booking', backref='pnr_tracking', uselist=False)
    
    def __init__(self, **kwargs):
        super(PNRStatusTracking, self).__init__(**kwargs)
