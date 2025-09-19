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

class Restaurant(db.Model):
    """Food & Catering - Restaurant partners"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    contact_number = db.Column(db.String(15))
    email = db.Column(db.String(120))
    cuisine_type = db.Column(db.String(50))  # Vegetarian, Non-Vegetarian, Both
    rating = db.Column(db.Float, default=4.0)
    delivery_time = db.Column(db.Integer, default=30)  # minutes
    minimum_order = db.Column(db.Float, default=0.0)
    delivery_charge = db.Column(db.Float, default=0.0)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    station = db.relationship('Station', backref='restaurants')
    menu_items = db.relationship('MenuItem', backref='restaurant', lazy=True)
    food_orders = db.relationship('FoodOrder', backref='restaurant', lazy=True)
    
    def __init__(self, **kwargs):
        super(Restaurant, self).__init__(**kwargs)

class MenuItem(db.Model):
    """Food menu items for restaurants"""
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))  # Breakfast, Lunch, Dinner, Snacks, Beverages
    food_type = db.Column(db.String(20), default='Vegetarian')  # Vegetarian, Non-Vegetarian
    image_url = db.Column(db.String(200))
    preparation_time = db.Column(db.Integer, default=15)  # minutes
    available = db.Column(db.Boolean, default=True)
    is_popular = db.Column(db.Boolean, default=False)
    ingredients = db.Column(db.Text)  # JSON string of ingredients
    nutrition_info = db.Column(db.Text)  # JSON string of nutrition data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(MenuItem, self).__init__(**kwargs)

class FoodOrder(db.Model):
    """Food orders linked to train bookings"""
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    delivery_station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    delivery_charge = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, preparing, dispatched, delivered, cancelled
    special_instructions = db.Column(db.Text)
    delivery_time = db.Column(db.DateTime)
    contact_number = db.Column(db.String(15), nullable=False)
    coach_number = db.Column(db.String(10))
    seat_number = db.Column(db.String(10))
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed, refunded
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    delivery_station = db.relationship('Station', foreign_keys=[delivery_station_id])
    items = db.relationship('FoodOrderItem', backref='food_order', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(FoodOrder, self).__init__(**kwargs)
        if not self.order_number:
            self.order_number = f"FD{datetime.utcnow().strftime('%Y%m%d')}{random.randint(1000, 9999)}"

class FoodOrderItem(db.Model):
    """Individual items in a food order"""
    id = db.Column(db.Integer, primary_key=True)
    food_order_id = db.Column(db.Integer, db.ForeignKey('food_order.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    special_request = db.Column(db.String(200))
    
    # Relationships
    menu_item = db.relationship('MenuItem', backref='order_items')
    
    def __init__(self, **kwargs):
        super(FoodOrderItem, self).__init__(**kwargs)

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
    food_order_updates = db.Column(db.Boolean, default=True)
    promotional_offers = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', backref='notification_preferences')
    
    def __init__(self, **kwargs):
        super(NotificationPreferences, self).__init__(**kwargs)
