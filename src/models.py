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
    
    def get_dietary_tags(self):
        """Get dietary restriction tags for the menu item"""
        tags = []
        if self.food_type == 'Vegetarian':
            tags.append('Vegetarian')
        elif self.food_type == 'Non-Vegetarian':
            tags.append('Non-Vegetarian')
        
        # Parse ingredients for common dietary restrictions
        if self.ingredients:
            ingredients_lower = self.ingredients.lower()
            if 'dairy' not in ingredients_lower and 'milk' not in ingredients_lower and 'cheese' not in ingredients_lower:
                tags.append('Dairy-Free')
            if 'gluten' not in ingredients_lower and 'wheat' not in ingredients_lower:
                tags.append('Gluten-Free')
            if 'nuts' not in ingredients_lower and 'peanut' not in ingredients_lower:
                tags.append('Nut-Free')
            if 'jain' in ingredients_lower or ('onion' not in ingredients_lower and 'garlic' not in ingredients_lower):
                tags.append('Jain-Friendly')
        
        return tags
    
    def matches_dietary_preferences(self, preferences):
        """Check if menu item matches user dietary preferences"""
        if not preferences:
            return True
        
        item_tags = self.get_dietary_tags()
        for preference in preferences:
            if preference not in item_tags:
                return False
        return True
    
    def get_average_rating(self):
        """Get average rating for this menu item"""
        reviews = FoodReview.query.filter_by(menu_item_id=self.id).all()
        if not reviews:
            return 0.0
        return sum(review.rating for review in reviews) / len(reviews)
    
    def get_recommendation_score(self, time_of_day=None):
        """Get recommendation score based on various factors"""
        base_score = self.get_average_rating() * 2  # Rating component (0-10)
        
        # Time-based scoring
        time_bonus = 0
        if time_of_day:
            hour = time_of_day.hour
            if self.category == 'Breakfast' and 6 <= hour <= 10:
                time_bonus = 3
            elif self.category == 'Lunch' and 11 <= hour <= 15:
                time_bonus = 3
            elif self.category == 'Dinner' and 18 <= hour <= 22:
                time_bonus = 3
            elif self.category == 'Snacks' and (hour < 6 or hour > 22 or 15 < hour < 18):
                time_bonus = 2
        
        # Popularity bonus
        popularity_bonus = 2 if self.is_popular else 0
        
        return min(10, base_score + time_bonus + popularity_bonus)

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

class UserDietaryPreference(db.Model):
    """User dietary preferences and restrictions"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    dietary_restrictions = db.Column(db.Text)  # JSON array of restrictions
    allergies = db.Column(db.Text)  # JSON array of allergies
    cuisine_preferences = db.Column(db.Text)  # JSON array of preferred cuisines
    spice_level = db.Column(db.String(20), default='Medium')  # Mild, Medium, Spicy, Very Spicy
    preferred_meal_times = db.Column(db.Text)  # JSON object with meal time preferences
    special_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='dietary_preference')
    
    def __init__(self, **kwargs):
        super(UserDietaryPreference, self).__init__(**kwargs)
        if not self.dietary_restrictions:
            self.dietary_restrictions = '[]'
        if not self.allergies:
            self.allergies = '[]'
        if not self.cuisine_preferences:
            self.cuisine_preferences = '[]'
        if not self.preferred_meal_times:
            self.preferred_meal_times = '{"breakfast": "07:00", "lunch": "12:00", "dinner": "19:00"}'
    
    def get_dietary_restrictions(self):
        """Get dietary restrictions as list"""
        import json
        return json.loads(self.dietary_restrictions) if self.dietary_restrictions else []
    
    def get_allergies(self):
        """Get allergies as list"""
        import json
        return json.loads(self.allergies) if self.allergies else []
    
    def get_cuisine_preferences(self):
        """Get cuisine preferences as list"""
        import json
        return json.loads(self.cuisine_preferences) if self.cuisine_preferences else []

class FoodReview(db.Model):
    """Customer reviews and ratings for restaurants and menu items"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'))  # Optional, for item-specific reviews
    food_order_id = db.Column(db.Integer, db.ForeignKey('food_order.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review_text = db.Column(db.Text)
    food_quality = db.Column(db.Integer)  # 1-5 rating for food quality
    delivery_speed = db.Column(db.Integer)  # 1-5 rating for delivery speed
    packaging_quality = db.Column(db.Integer)  # 1-5 rating for packaging
    would_recommend = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='food_reviews')
    restaurant = db.relationship('Restaurant', backref='reviews')
    menu_item = db.relationship('MenuItem', backref='reviews')
    food_order = db.relationship('FoodOrder', backref='review')
    
    def __init__(self, **kwargs):
        super(FoodReview, self).__init__(**kwargs)

class GroupFoodOrder(db.Model):
    """Coordinated food orders for group bookings"""
    id = db.Column(db.Integer, primary_key=True)
    group_booking_id = db.Column(db.Integer, db.ForeignKey('group_booking.id'), nullable=False)
    coordinator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Who is coordinating
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    delivery_station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    group_order_number = db.Column(db.String(20), unique=True, nullable=False)
    total_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='collecting')  # collecting, confirmed, preparing, dispatched, delivered, cancelled
    deadline_for_orders = db.Column(db.DateTime)  # Deadline for group members to place orders
    special_instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    group_booking = db.relationship('GroupBooking', backref='group_food_orders')
    coordinator = db.relationship('User', backref='coordinated_food_orders')
    restaurant = db.relationship('Restaurant', backref='group_orders')
    delivery_station = db.relationship('Station', foreign_keys=[delivery_station_id])
    individual_orders = db.relationship('FoodOrder', backref='group_food_order', lazy=True)
    
    def __init__(self, **kwargs):
        super(GroupFoodOrder, self).__init__(**kwargs)
        if not self.group_order_number:
            self.group_order_number = f"GFD{datetime.utcnow().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
        if not self.deadline_for_orders:
            # Default deadline: 2 hours from creation
            self.deadline_for_orders = datetime.utcnow() + timedelta(hours=2)
    
    def get_order_summary(self):
        """Get summary of all orders in this group food order"""
        orders = FoodOrder.query.filter_by(group_food_order_id=self.id).all()
        total_orders = len(orders)
        total_amount = sum(order.total_amount for order in orders)
        
        # Count by status
        status_counts = {}
        for order in orders:
            status_counts[order.status] = status_counts.get(order.status, 0) + 1
        
        return {
            'total_orders': total_orders,
            'total_amount': total_amount,
            'status_counts': status_counts,
            'average_order_value': total_amount / total_orders if total_orders > 0 else 0
        }

class FoodOrderTracking(db.Model):
    """Detailed tracking for food order status updates"""
    id = db.Column(db.Integer, primary_key=True)
    food_order_id = db.Column(db.Integer, db.ForeignKey('food_order.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(500))
    estimated_delivery_time = db.Column(db.DateTime)
    actual_time = db.Column(db.DateTime)
    location = db.Column(db.String(100))  # Current location for delivery tracking
    updated_by = db.Column(db.String(50))  # System, Restaurant, Delivery Partner
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    food_order = db.relationship('FoodOrder', backref='tracking_updates')
    
    def __init__(self, **kwargs):
        super(FoodOrderTracking, self).__init__(**kwargs)

class FoodRecommendation(db.Model):
    """AI-powered food recommendations for users"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    recommendation_score = db.Column(db.Float, nullable=False)  # 0-10 score
    recommendation_reason = db.Column(db.Text)  # Why this was recommended
    context = db.Column(db.String(50))  # time_of_day, popular, dietary_match, etc.
    shown_at = db.Column(db.DateTime, default=datetime.utcnow)
    clicked = db.Column(db.Boolean, default=False)
    ordered = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', backref='food_recommendations')
    menu_item = db.relationship('MenuItem', backref='recommendations')
    
    def __init__(self, **kwargs):
        super(FoodRecommendation, self).__init__(**kwargs)

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
        for booking in self.individual_bookings:
            passengers.extend(booking.passengers)
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
                    booking = next((b for b in self.individual_bookings if passenger in b.passengers), None)
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
    food_order_updates = db.Column(db.Boolean, default=True)
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
