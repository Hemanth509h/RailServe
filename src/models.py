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
    status = db.Column(db.String(20), default='pending_payment')  # confirmed, waitlisted, cancelled, pending_payment
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    
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
