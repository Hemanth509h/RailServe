from .database import db
from datetime import datetime, timedelta
from sqlalchemy import event
import string
import random

class User(db.Model):
    """User model with role-based access control"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')
    active = db.Column(db.Boolean, default=True)
    reset_token = db.Column(db.String(100))
    reset_token_expiry = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    bookings = db.relationship('Booking', backref='user', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)
    tatkal_timeslots = db.relationship('TatkalTimeSlot', backref='creator', lazy=True)

class Station(db.Model):
    """Railway stations"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(10), nullable=False, unique=True)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    train_routes = db.relationship('TrainRoute', backref='station', lazy=True)

class Train(db.Model):
    """Train information"""
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    fare_per_km = db.Column(db.Float, nullable=False)
    tatkal_seats = db.Column(db.Integer, default=0)
    tatkal_fare_per_km = db.Column(db.Float)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    routes = db.relationship('TrainRoute', backref='train', lazy=True, order_by='TrainRoute.sequence')
    bookings = db.relationship('Booking', backref='train', lazy=True)

class TrainRoute(db.Model):
    """Train route information with stations"""
    id = db.Column(db.Integer, primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=False)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    sequence = db.Column(db.Integer, nullable=False)
    arrival_time = db.Column(db.Time)
    departure_time = db.Column(db.Time)
    distance_from_start = db.Column(db.Float, nullable=False)
    
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
    booking_type = db.Column(db.String(10), default='general')
    quota = db.Column(db.String(20), default='general')
    coach_class = db.Column(db.String(10), default='SL')
    status = db.Column(db.String(20), default='pending_payment')
    waitlist_type = db.Column(db.String(10), default='GNWL')
    chart_prepared = db.Column(db.Boolean, default=False)
    berth_preference = db.Column(db.String(20), default='No Preference')
    current_reservation = db.Column(db.Boolean, default=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    cancellation_charges = db.Column(db.Float, default=0.0)
    loyalty_discount = db.Column(db.Float, default=0.0)
    
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
    gender = db.Column(db.String(10), nullable=False)
    id_proof_type = db.Column(db.String(20), nullable=False)
    id_proof_number = db.Column(db.String(50), nullable=False)
    seat_preference = db.Column(db.String(20), default='No Preference')
    coach_class = db.Column(db.String(10), default='SL')
    seat_number = db.Column(db.String(20))
    berth_type = db.Column(db.String(20))

class Payment(db.Model):
    """Payment information"""
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    transaction_id = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    __table_args__ = (db.UniqueConstraint('booking_id', 'status', name='uq_booking_payment_success'),)

class Waitlist(db.Model):
    """Waitlist management"""
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=False)
    journey_date = db.Column(db.Date, nullable=False)
    position = db.Column(db.Integer, nullable=False)
    waitlist_type = db.Column(db.String(10), default='GNWL')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    name = db.Column(db.String(100), nullable=False)
    coach_classes = db.Column(db.String(200))
    open_time = db.Column(db.Time, nullable=False)
    close_time = db.Column(db.Time)
    days_before_journey = db.Column(db.Integer, default=1)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

class TatkalOverride(db.Model):
    """Admin override control for Tatkal booking availability"""
    id = db.Column(db.Integer, primary_key=True)
    is_enabled = db.Column(db.Boolean, default=False)
    enabled_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    enabled_at = db.Column(db.DateTime, default=datetime.utcnow)
    override_message = db.Column(db.String(200), default='Tatkal booking enabled by admin')
    coach_classes = db.Column(db.String(200))
    train_ids = db.Column(db.Text)
    valid_until = db.Column(db.DateTime)
    
    admin_user = db.relationship('User', foreign_keys=[enabled_by])

class RefundRequest(db.Model):
    """TDR and refund management"""
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    refund_amount = db.Column(db.Float, nullable=False)
    cancellation_charges = db.Column(db.Float, default=0.0)
    tdr_number = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default='pending')
    filed_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    booking = db.relationship('Booking', backref='refund_requests', lazy=True)
    user = db.relationship('User', backref='refund_requests', lazy=True)

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

class ComplaintManagement(db.Model):
    """Customer complaint and query management system"""
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))
    category = db.Column(db.String(50), nullable=False)
    subcategory = db.Column(db.String(50))
    priority = db.Column(db.String(10), default='medium')
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='open')
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    resolution = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    user = db.relationship('User', foreign_keys=[user_id], backref='complaints')
    booking = db.relationship('Booking', backref='complaints')
    assigned_user = db.relationship('User', foreign_keys=[assigned_to])

class PerformanceMetrics(db.Model):
    """Performance tracking for trains and routes"""
    id = db.Column(db.Integer, primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=False)
    journey_date = db.Column(db.Date, nullable=False)
    on_time_percentage = db.Column(db.Float, default=0.0)
    average_delay_minutes = db.Column(db.Integer, default=0)
    total_passengers = db.Column(db.Integer, default=0)
    revenue_generated = db.Column(db.Float, default=0.0)
    cancellations = db.Column(db.Integer, default=0)
    waitlist_confirmed = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    train = db.relationship('Train', backref='performance_metrics')

class DynamicPricing(db.Model):
    """Dynamic pricing rules for demand-based fare adjustments"""
    id = db.Column(db.Integer, primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=False)
    coach_class = db.Column(db.String(10), nullable=False)
    base_fare_multiplier = db.Column(db.Float, default=1.0)
    surge_pricing_enabled = db.Column(db.Boolean, default=False)
    demand_threshold_high = db.Column(db.Integer, default=80)
    demand_threshold_medium = db.Column(db.Integer, default=50)
    high_demand_multiplier = db.Column(db.Float, default=1.5)
    medium_demand_multiplier = db.Column(db.Float, default=1.2)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    train = db.relationship('Train', backref='pricing_rules')

class PlatformManagement(db.Model):
    """Platform and track assignment management"""
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    platform_number = db.Column(db.String(10), nullable=False)
    track_number = db.Column(db.String(10))
    platform_length = db.Column(db.Integer)
    electrified = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='active')
    facilities = db.Column(db.Text)
    wheelchair_accessible = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    station = db.relationship('Station', backref='platforms')

class LoyaltyProgram(db.Model):
    """Frequent traveler loyalty program"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    membership_number = db.Column(db.String(20), unique=True, nullable=False)
    tier = db.Column(db.String(20), default='Silver')
    points_earned = db.Column(db.Integer, default=0)
    points_redeemed = db.Column(db.Integer, default=0)
    total_journeys = db.Column(db.Integer, default=0)
    total_distance = db.Column(db.Float, default=0.0)
    total_spent = db.Column(db.Float, default=0.0)
    tier_valid_until = db.Column(db.Date)
    benefits_active = db.Column(db.Boolean, default=True)
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    member = db.relationship('User', backref='loyalty_program')
