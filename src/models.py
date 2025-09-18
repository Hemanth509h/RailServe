from .app import db
from flask_login import UserMixin
from datetime import datetime
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
    
    def __init__(self, **kwargs):
        super(Passenger, self).__init__(**kwargs)

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
    reason = db.Column(db.String(100), nullable=False)  # Train cancelled, delay, AC failure, etc.
    amount_paid = db.Column(db.Float, nullable=False)
    refund_amount = db.Column(db.Float, nullable=False)
    cancellation_charges = db.Column(db.Float, default=0.0)
    tdr_number = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, completed
    filed_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    def __init__(self, **kwargs):
        super(RefundRequest, self).__init__(**kwargs)
        if not self.tdr_number:
            self.tdr_number = f"TDR{datetime.utcnow().strftime('%Y%m%d')}{random.randint(1000, 9999)}"

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
