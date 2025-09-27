"""
Modern Group Booking Database Models - 2025 Standards
=====================================================

Comprehensive database models for modern group booking system including:
- Enhanced group booking with metadata
- Member management and invitations
- Payment coordination and tracking
- Activity logging and analytics
- API integration support
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from decimal import Decimal
import json
from typing import Dict, Any, List, Optional
from enum import Enum as PyEnum
import uuid

from .database import db

class ModernGroupBooking(db.Model):
    """
    Enhanced group booking model with modern features
    Supports 4-999 passengers with corporate and tour capabilities
    """
    __tablename__ = 'modern_group_bookings'
    
    id = Column(Integer, primary_key=True)
    
    # Basic Information
    group_name = Column(String(200), nullable=False)
    description = Column(Text)
    group_code = Column(String(8), unique=True, nullable=False, index=True)
    group_leader_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Group Classification
    group_type = Column(Enum('family', 'corporate', 'tour', 'event', 'educational', name='group_types'), 
                       nullable=False, default='family')
    estimated_passengers = Column(Integer, nullable=False, default=4)
    actual_passengers = Column(Integer, default=0)
    
    # Status and Workflow
    status = Column(Enum('draft', 'active', 'payment_pending', 'confirmed', 'partially_paid', 'completed', 'cancelled', 
                        name='group_statuses'), nullable=False, default='draft')
    
    # Enhanced Metadata (JSON fields for flexibility)
    travel_preferences = Column(JSON)  # class_preference, meal_preference, seat_arrangement, insurance_required
    budget_constraints = Column(JSON)  # min_budget, max_budget, currency
    contact_info = Column(JSON)  # primary_email, secondary_email, primary_phone, emergency_contact
    
    # Financial Information
    total_estimated_cost = Column(Float, default=0.0)
    total_actual_cost = Column(Float, default=0.0)
    discount_applied = Column(Float, default=0.0)
    group_discount_rate = Column(Float, default=0.0)
    
    # Special Requirements
    special_requirements = Column(Text)
    accessibility_needs = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    travel_start_date = Column(DateTime)
    travel_end_date = Column(DateTime)
    
    # API and Integration
    external_ref = Column(String(100))  # For third-party integration
    api_webhook_url = Column(String(500))  # For real-time notifications
    
    # Relationships
    leader = relationship('User', backref='led_groups')
    memberships = relationship('GroupMembership', back_populates='group', cascade='all, delete-orphan')
    bookings = relationship('GroupBookingDetail', back_populates='group', cascade='all, delete-orphan')
    invitations = relationship('ModernGroupInvitation', back_populates='group', cascade='all, delete-orphan')
    messages = relationship('ModernGroupMessage', back_populates='group', cascade='all, delete-orphan')
    activities = relationship('GroupActivityLog', back_populates='group', cascade='all, delete-orphan')
    payments = relationship('GroupPaymentSplit', back_populates='group', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ModernGroupBooking {self.group_name} ({self.group_code})>'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'group_name': self.group_name,
            'description': self.description,
            'group_code': self.group_code,
            'group_type': self.group_type,
            'estimated_passengers': self.estimated_passengers,
            'actual_passengers': self.actual_passengers,
            'status': self.status,
            'travel_preferences': json.loads(str(self.travel_preferences)) if self.travel_preferences else {},
            'budget_constraints': json.loads(str(self.budget_constraints)) if self.budget_constraints else {},
            'total_estimated_cost': self.total_estimated_cost,
            'discount_applied': self.discount_applied,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'travel_start_date': self.travel_start_date.isoformat() if self.travel_start_date else None,
            'travel_end_date': self.travel_end_date.isoformat() if self.travel_end_date else None
        }
    
    def get_member_count(self) -> int:
        """Get current number of active members"""
        if hasattr(self, 'memberships') and self.memberships:
            return len([m for m in self.memberships if m.status == 'active'])
        return 0
    
    @property
    def completion_percentage(self) -> float:
        """Calculate group booking completion percentage"""
        total_steps = 6  # draft, members, bookings, payments, confirmation, completion
        completed_steps = 0
        
        if self.status != 'draft': completed_steps += 1
        if self.get_member_count() > 0: completed_steps += 1
        if len(self.bookings) > 0: completed_steps += 2
        if self.status in ['confirmed', 'completed']: completed_steps += 2
        
        return (completed_steps / total_steps) * 100

class GroupMembership(db.Model):
    """
    Group membership tracking with roles and permissions
    """
    __tablename__ = 'group_memberships'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('modern_group_bookings.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Role and Status
    role = Column(Enum('leader', 'admin', 'member', 'viewer', name='group_roles'), 
                 nullable=False, default='member')
    status = Column(Enum('active', 'inactive', 'suspended', name='membership_statuses'), 
                   nullable=False, default='active')
    
    # Membership Details
    joined_at = Column(DateTime, default=func.now(), nullable=False)
    invited_by_id = Column(Integer, ForeignKey('user.id'))
    last_active_at = Column(DateTime, default=func.now())
    
    # Member Preferences
    notification_preferences = Column(JSON)  # email, sms, push notifications
    booking_permissions = Column(JSON)  # can_book, can_modify, can_cancel
    
    # Relationships
    group = relationship('ModernGroupBooking', back_populates='memberships')
    user = relationship('User', foreign_keys=[user_id], backref='group_memberships')
    invited_by = relationship('User', foreign_keys=[invited_by_id])
    
    def __repr__(self):
        return f'<GroupMembership {self.user.username} in {self.group.group_name}>'

class ModernGroupInvitation(db.Model):
    """
    Modern invitation system with expiration and tracking
    """
    __tablename__ = 'modern_group_invitations'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('modern_group_bookings.id'), nullable=False)
    inviter_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Invitation Details
    invited_email = Column(String(255), nullable=False)
    invitation_code = Column(String(64), unique=True, nullable=False, index=True)
    message = Column(Text)
    
    # Status and Timing
    status = Column(Enum('pending', 'accepted', 'declined', 'expired', name='invitation_statuses'), 
                   nullable=False, default='pending')
    created_at = Column(DateTime, default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    responded_at = Column(DateTime)
    
    # Response Information
    joined_user_id = Column(Integer, ForeignKey('user.id'))
    decline_reason = Column(Text)
    
    # Tracking
    email_sent_count = Column(Integer, default=0)
    last_reminder_sent = Column(DateTime)
    
    # Relationships
    group = relationship('ModernGroupBooking', back_populates='invitations')
    inviter = relationship('User', foreign_keys=[inviter_id])
    joined_user = relationship('User', foreign_keys=[joined_user_id])
    
    def check_if_expired(self) -> bool:
        """Check if invitation has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    def __repr__(self):
        return f'<ModernGroupInvitation {self.invited_email} to {self.group.group_name}>'

class GroupBookingDetail(db.Model):
    """
    Individual booking details within a group booking
    """
    __tablename__ = 'group_booking_details'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('modern_group_bookings.id'), nullable=False)
    booking_id = Column(Integer, ForeignKey('booking.id'))  # Links to existing booking table
    
    # Booking Specifics
    train_id = Column(Integer, ForeignKey('train.id'))
    from_station_id = Column(Integer, ForeignKey('station.id'))
    to_station_id = Column(Integer, ForeignKey('station.id'))
    journey_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime)  # For round trips
    
    # Passenger and Pricing
    passenger_count = Column(Integer, nullable=False, default=1)
    total_base_fare = Column(Float, nullable=False, default=0.0)
    group_discount_amount = Column(Float, default=0.0)
    final_amount = Column(Float, nullable=False, default=0.0)
    
    # Status and Metadata
    booking_status = Column(Enum('pending', 'confirmed', 'waitlisted', 'cancelled', name='booking_statuses'), 
                           nullable=False, default='pending')
    booking_reference = Column(String(50))  # PNR or confirmation number
    created_by_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Special Arrangements
    coach_class = Column(String(10), default='SL')
    seat_preferences = Column(JSON)  # window, aisle, together, etc.
    meal_requirements = Column(JSON)  # veg, non-veg, special dietary needs
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    group = relationship('ModernGroupBooking', back_populates='bookings')
    booking = relationship('Booking')
    train = relationship('Train')
    from_station = relationship('Station', foreign_keys=[from_station_id])
    to_station = relationship('Station', foreign_keys=[to_station_id])
    created_by = relationship('User')
    
    def __repr__(self):
        return f'<GroupBookingDetail {self.booking_reference} for {self.group.group_name}>'

class GroupPaymentSplit(db.Model):
    """
    Payment coordination and split tracking
    """
    __tablename__ = 'group_payment_splits'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('modern_group_bookings.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Payment Details
    assigned_amount = Column(Float, nullable=False, default=0.0)
    paid_amount = Column(Float, nullable=False, default=0.0)
    currency = Column(String(3), default='INR')
    
    # Payment Method and Status
    payment_method = Column(Enum('credit_card', 'debit_card', 'upi', 'net_banking', 'wallet', 'cash', 
                                name='payment_methods'), default='upi')
    payment_status = Column(Enum('pending', 'partial', 'completed', 'failed', 'refunded', 
                                name='payment_statuses'), nullable=False, default='pending')
    
    # Transaction Information
    transaction_id = Column(String(100))
    payment_gateway_response = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    paid_at = Column(DateTime)
    due_date = Column(DateTime)
    
    # Relationships
    group = relationship('ModernGroupBooking', back_populates='payments')
    user = relationship('User')
    
    def get_outstanding_amount(self) -> float:
        """Calculate outstanding payment amount"""
        return max(0.0, float(self.assigned_amount or 0.0) - float(self.paid_amount or 0.0))
    
    def __repr__(self):
        return f'<GroupPaymentSplit {self.user.username}: ${self.assigned_amount}>'

class ModernGroupMessage(db.Model):
    """
    Real-time group communication system
    """
    __tablename__ = 'group_messages'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('modern_group_bookings.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Message Content
    message = Column(Text, nullable=False)
    message_type = Column(Enum('general', 'announcement', 'booking_update', 'payment_reminder', 'urgent', 
                              name='message_types'), nullable=False, default='general')
    
    # Message Properties
    is_important = Column(Boolean, default=False)
    is_system_message = Column(Boolean, default=False)
    reply_to_id = Column(Integer, ForeignKey('group_messages.id'))
    
    # Attachments and Media
    attachments = Column(JSON)  # File paths, URLs, etc.
    
    # Tracking
    created_at = Column(DateTime, default=func.now(), nullable=False)
    edited_at = Column(DateTime)
    read_by = Column(JSON)  # List of user IDs who have read the message
    
    # Relationships
    group = relationship('ModernGroupBooking', back_populates='messages')
    sender = relationship('User')
    replies = relationship('ModernGroupMessage', backref=backref('parent_message', remote_side=[id]))
    
    def mark_as_read(self, user_id: int):
        """Mark message as read by a user"""
        read_list = json.loads(str(self.read_by)) if self.read_by else []
        if user_id not in read_list:
            read_list.append(user_id)
            self.read_by = json.dumps(read_list)
    
    def is_read_by(self, user_id: int) -> bool:
        """Check if message has been read by a user"""
        read_list = json.loads(str(self.read_by)) if self.read_by else []
        return user_id in read_list
    
    def __repr__(self):
        return f'<ModernGroupMessage from {self.sender.username} in {self.group.group_name}>'

class GroupActivityLog(db.Model):
    """
    Comprehensive activity logging for analytics and timeline
    """
    __tablename__ = 'group_activity_logs'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('modern_group_bookings.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))  # Nullable for system activities
    
    # Activity Details
    activity_type = Column(Enum('group_created', 'member_invited', 'member_joined', 'member_left',
                               'booking_created', 'booking_confirmed', 'booking_cancelled',
                               'payment_made', 'payment_failed', 'message_sent',
                               'preferences_updated', 'status_changed', 'system_notification',
                               name='activity_types'), nullable=False)
    
    description = Column(Text, nullable=False)
    context_data = Column(JSON)  # Additional context data
    
    # Severity and Visibility
    severity = Column(Enum('info', 'warning', 'error', 'success', name='activity_severities'), 
                     nullable=False, default='info')
    is_visible_to_members = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    group = relationship('ModernGroupBooking', back_populates='activities')
    user = relationship('User')
    
    def __repr__(self):
        return f'<GroupActivityLog {self.activity_type} in {self.group.group_name}>'

class GroupAnalytics(db.Model):
    """
    Aggregated analytics and insights for group bookings
    """
    __tablename__ = 'group_analytics'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('modern_group_bookings.id'), nullable=False)
    
    # Engagement Metrics
    member_engagement_score = Column(Float, default=0.0)
    message_activity_count = Column(Integer, default=0)
    booking_efficiency_score = Column(Float, default=0.0)
    
    # Financial Metrics
    cost_per_passenger = Column(Float, default=0.0)
    savings_percentage = Column(Float, default=0.0)
    payment_completion_rate = Column(Float, default=0.0)
    
    # Time Metrics
    avg_response_time_hours = Column(Float, default=0.0)
    booking_completion_days = Column(Integer, default=0)
    
    # Insights (JSON for flexibility)
    insights = Column(JSON)  # AI-generated insights and recommendations
    
    # Update Information
    last_calculated = Column(DateTime, default=func.now())
    calculation_version = Column(String(20), default='1.0')
    
    # Relationships
    group = relationship('ModernGroupBooking')
    
    def __repr__(self):
        return f'<GroupAnalytics for {self.group.group_name}>'


class GroupSplitBilling(db.Model):
    """
    Advanced split billing system for group payments
    """
    __tablename__ = 'group_split_billing'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('modern_group_bookings.id'), nullable=False)
    split_method = Column(Enum('equal', 'percentage', 'amount', 'lead_pays', name='split_methods'), 
                         nullable=False, default='equal')
    
    # Split Configuration
    split_config = Column(JSON)  # Configuration for how to split costs
    total_amount = Column(Float, nullable=False, default=0.0)
    currency = Column(String(3), default='INR')
    
    # Payment Processing
    payment_processor = Column(String(50), default='razorpay')
    processor_config = Column(JSON)  # Gateway-specific configuration
    
    # Split Rules
    minimum_contribution = Column(Float, default=0.0)
    maximum_contribution = Column(Float)
    auto_split_enabled = Column(Boolean, default=True)
    
    # Status and Tracking
    split_status = Column(Enum('pending', 'configured', 'processing', 'completed', 'failed', 
                              name='split_statuses'), nullable=False, default='pending')
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    group = relationship('ModernGroupBooking', backref='split_billing')
    
    def calculate_split(self, total_amount: float) -> Dict[str, float]:
        """Calculate how much each member should pay"""
        if self.split_method == 'equal':
            member_count = len(self.group.memberships)
            return {str(m.user_id): total_amount / member_count for m in self.group.memberships}
        elif self.split_method == 'percentage':
            return {str(k): total_amount * (v/100) for k, v in self.split_config.items()}
        elif self.split_method == 'amount':
            return self.split_config
        elif self.split_method == 'lead_pays':
            return {str(self.group.group_leader_id): total_amount}
        return {}
    
    def __repr__(self):
        return f'<GroupSplitBilling {self.split_method} for {self.group.group_name}>'


class GroupMealCoordination(db.Model):
    """
    Group meal ordering and coordination system
    """
    __tablename__ = 'group_meal_coordination'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('modern_group_bookings.id'), nullable=False)
    
    # Meal Service Details
    service_provider = Column(String(100), default='railrecipe')  # railrecipe, irctc_ecatering
    station_code = Column(String(10), nullable=False)  # Station where meals will be delivered
    delivery_time = Column(DateTime, nullable=False)
    
    # Order Details
    meal_preferences = Column(JSON)  # veg, non-veg, jain, special dietary requirements
    bulk_order_config = Column(JSON)  # Meal quantities and types
    special_instructions = Column(Text)
    
    # Pricing and Discounts
    base_cost = Column(Float, nullable=False, default=0.0)
    bulk_discount_rate = Column(Float, default=0.0)  # Discount for bulk orders
    final_cost = Column(Float, nullable=False, default=0.0)
    
    # Order Status
    order_status = Column(Enum('pending', 'confirmed', 'prepared', 'delivered', 'cancelled', 
                              name='meal_order_statuses'), nullable=False, default='pending')
    tracking_id = Column(String(100))  # External tracking ID
    
    # Delivery Information
    coach_number = Column(String(10))
    seat_numbers = Column(JSON)  # List of seat numbers for delivery
    delivery_instructions = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    confirmed_at = Column(DateTime)
    delivered_at = Column(DateTime)
    
    # Relationships
    group = relationship('ModernGroupBooking', backref='meal_orders')
    
    def calculate_bulk_discount(self, base_amount: float) -> float:
        """Calculate bulk discount based on order size"""
        meal_count = sum(self.bulk_order_config.values()) if self.bulk_order_config else 0
        
        if meal_count >= 20:
            self.bulk_discount_rate = 15.0  # 15% for 20+ meals
        elif meal_count >= 10:
            self.bulk_discount_rate = 10.0  # 10% for 10-19 meals
        elif meal_count >= 5:
            self.bulk_discount_rate = 5.0   # 5% for 5-9 meals
        
        discount_amount = base_amount * (self.bulk_discount_rate / 100)
        return base_amount - discount_amount
    
    def __repr__(self):
        return f'<GroupMealCoordination for {self.group.group_name} at {self.station_code}>'


class GroupLoyaltyIntegration(db.Model):
    """
    Loyalty program integration for group bookings
    """
    __tablename__ = 'group_loyalty_integration'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('modern_group_bookings.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)  # Beneficiary user
    
    # Loyalty Program Details
    program_name = Column(String(100), nullable=False)  # irctc_points, railmitra_rewards
    loyalty_number = Column(String(50))
    tier_level = Column(Enum('bronze', 'silver', 'gold', 'platinum', name='loyalty_tiers'), 
                       default='bronze')
    
    # Points Calculation
    base_points = Column(Integer, default=0)
    tier_multiplier = Column(Float, default=1.0)
    group_bonus_points = Column(Integer, default=0)
    total_points_earned = Column(Integer, default=0)
    
    # Benefits Applied
    benefits_applied = Column(JSON)  # List of benefits applied to this booking
    discount_amount = Column(Float, default=0.0)
    priority_benefits = Column(JSON)  # Special benefits due to loyalty status
    
    # Cross-Program Integration
    partner_programs = Column(JSON)  # Integration with airline/hotel loyalty programs
    point_transfer_config = Column(JSON)  # Configuration for cross-program transfers
    
    # Status and Tracking
    points_status = Column(Enum('pending', 'credited', 'expired', name='points_statuses'), 
                          default='pending')
    credited_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    group = relationship('ModernGroupBooking', backref='loyalty_integrations')
    user = relationship('User')
    
    def calculate_points(self, booking_amount: float) -> int:
        """Calculate loyalty points for group booking"""
        # Base calculation: 1 point per 100 INR
        self.base_points = int(booking_amount / 100)
        
        # Apply tier multiplier
        tier_multipliers = {
            'bronze': 1.0, 'silver': 1.2, 'gold': 1.5, 'platinum': 2.0
        }
        self.tier_multiplier = tier_multipliers.get(self.tier_level, 1.0)
        
        # Group booking bonus: 20% extra points
        self.group_bonus_points = int(self.base_points * 0.2)
        
        # Calculate total
        self.total_points_earned = int(
            (self.base_points * self.tier_multiplier) + self.group_bonus_points
        )
        
        return self.total_points_earned
    
    def __repr__(self):
        return f'<GroupLoyaltyIntegration {self.program_name} for {self.user.username}>'


class AdvancedSeatAllocation(db.Model):
    """
    Advanced seat allocation system with optimization algorithms
    """
    __tablename__ = 'advanced_seat_allocation'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('modern_group_bookings.id'), nullable=False)
    train_id = Column(Integer, ForeignKey('train.id'), nullable=False)
    
    # Allocation Configuration
    allocation_algorithm = Column(Enum('basic', 'cohesion_optimized', 'preference_based', 
                                      'revenue_optimized', name='allocation_algorithms'), 
                                 default='cohesion_optimized')
    
    # Group Preferences
    keep_together = Column(Boolean, default=True)
    max_separation_distance = Column(Integer, default=2)  # Maximum rows apart
    coach_preference = Column(JSON)  # Preferred coach types
    berth_preferences = Column(JSON)  # Lower/middle/upper berth preferences
    
    # Special Requirements
    accessibility_requirements = Column(JSON)  # Wheelchair, senior citizen needs
    gender_separation_rules = Column(JSON)  # Gender-based seating rules
    age_based_priority = Column(JSON)  # Senior citizens, children priority
    
    # Allocation Results
    allocated_seats = Column(JSON)  # Final seat assignments
    allocation_score = Column(Float, default=0.0)  # Quality score of allocation
    optimization_metrics = Column(JSON)  # Detailed metrics of allocation quality
    
    # Alternative Options
    alternative_allocations = Column(JSON)  # Other possible allocations
    waitlist_position = Column(Integer)  # If seats not available
    
    # Status and Timing
    allocation_status = Column(Enum('pending', 'optimizing', 'allocated', 'confirmed', 'failed', 
                                   name='allocation_statuses'), default='pending')
    processing_time_ms = Column(Integer)  # Time taken for optimization
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    allocated_at = Column(DateTime)
    confirmed_at = Column(DateTime)
    
    # Relationships
    group = relationship('ModernGroupBooking', backref='seat_allocations')
    train = relationship('Train')
    
    def optimize_allocation(self, available_seats: List[Dict], passenger_preferences: List[Dict]) -> Dict:
        """Run seat allocation optimization algorithm"""
        import time
        start_time = time.time()
        
        if self.allocation_algorithm == 'cohesion_optimized':
            result = self._cohesion_optimization(available_seats, passenger_preferences)
        elif self.allocation_algorithm == 'preference_based':
            result = self._preference_optimization(available_seats, passenger_preferences)
        elif self.allocation_algorithm == 'revenue_optimized':
            result = self._revenue_optimization(available_seats, passenger_preferences)
        else:
            result = self._basic_allocation(available_seats, passenger_preferences)
        
        self.processing_time_ms = int((time.time() - start_time) * 1000)
        self.allocated_seats = result.get('allocation', {})
        self.allocation_score = result.get('score', 0.0)
        self.optimization_metrics = result.get('metrics', {})
        
        return result
    
    def _cohesion_optimization(self, available_seats: List[Dict], preferences: List[Dict]) -> Dict:
        """Optimize for keeping group members close together"""
        # Simplified cohesion algorithm
        score = 0.0
        allocation = {}
        
        # Group seats by coach and proximity
        coach_groups = {}
        for seat in available_seats:
            coach = seat.get('coach', 'Unknown')
            if coach not in coach_groups:
                coach_groups[coach] = []
            coach_groups[coach].append(seat)
        
        # Allocate passengers to maintain group cohesion
        passenger_count = len(preferences)
        best_coach = max(coach_groups.keys(), key=lambda c: len(coach_groups[c]))
        
        if len(coach_groups[best_coach]) >= passenger_count:
            for i, preference in enumerate(preferences):
                if i < len(coach_groups[best_coach]):
                    allocation[preference['passenger_id']] = coach_groups[best_coach][i]
                    score += 10  # High score for same coach
        
        return {
            'allocation': allocation,
            'score': score,
            'metrics': {
                'same_coach_percentage': (len(allocation) / passenger_count) * 100,
                'average_separation': 1.0  # Simplified metric
            }
        }
    
    def _preference_optimization(self, available_seats: List[Dict], preferences: List[Dict]) -> Dict:
        """Optimize based on individual passenger preferences"""
        score = 0.0
        allocation = {}
        
        for preference in preferences:
            best_seat = None
            best_score = 0
            
            for seat in available_seats:
                seat_score = 0
                
                # Match berth preference
                if preference.get('berth_preference') == seat.get('berth_type'):
                    seat_score += 5
                
                # Match window/aisle preference
                if preference.get('window_preference') and seat.get('is_window'):
                    seat_score += 3
                
                if seat_score > best_score:
                    best_score = seat_score
                    best_seat = seat
            
            if best_seat:
                allocation[preference['passenger_id']] = best_seat
                available_seats.remove(best_seat)
                score += best_score
        
        return {
            'allocation': allocation,
            'score': score,
            'metrics': {
                'preference_satisfaction': (score / (len(preferences) * 8)) * 100,
                'allocated_passengers': len(allocation)
            }
        }
    
    def _revenue_optimization(self, available_seats: List[Dict], preferences: List[Dict]) -> Dict:
        """Optimize for maximum revenue while satisfying group needs"""
        # Simplified revenue optimization
        score = 0.0
        allocation = {}
        
        # Sort seats by price (highest first for revenue optimization)
        sorted_seats = sorted(available_seats, key=lambda s: s.get('price', 0), reverse=True)
        
        for i, preference in enumerate(preferences):
            if i < len(sorted_seats):
                allocation[preference['passenger_id']] = sorted_seats[i]
                score += sorted_seats[i].get('price', 0)
        
        return {
            'allocation': allocation,
            'score': score,
            'metrics': {
                'total_revenue': score,
                'average_seat_price': score / len(allocation) if allocation else 0
            }
        }
    
    def _basic_allocation(self, available_seats: List[Dict], preferences: List[Dict]) -> Dict:
        """Basic first-come-first-served allocation"""
        score = len(preferences)
        allocation = {}
        
        for i, preference in enumerate(preferences):
            if i < len(available_seats):
                allocation[preference['passenger_id']] = available_seats[i]
        
        return {
            'allocation': allocation,
            'score': score,
            'metrics': {
                'allocation_rate': (len(allocation) / len(preferences)) * 100
            }
        }
    
    def __repr__(self):
        return f'<AdvancedSeatAllocation {self.allocation_algorithm} for {self.group.group_name}>'


class GroupSustainabilityTracking(db.Model):
    """
    Carbon footprint and sustainability tracking for group travel
    """
    __tablename__ = 'group_sustainability_tracking'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('modern_group_bookings.id'), nullable=False)
    
    # Carbon Footprint Calculation
    total_distance_km = Column(Float, nullable=False, default=0.0)
    carbon_emission_kg = Column(Float, nullable=False, default=0.0)
    emission_factor = Column(Float, default=0.14)  # kg CO2 per passenger-km for trains
    
    # Comparison with Other Transport
    air_travel_emissions = Column(Float, default=0.0)  # Estimated air travel CO2
    car_travel_emissions = Column(Float, default=0.0)  # Estimated car travel CO2
    savings_vs_air = Column(Float, default=0.0)  # CO2 savings vs air travel
    savings_vs_car = Column(Float, default=0.0)  # CO2 savings vs car travel
    
    # Sustainability Metrics
    green_score = Column(Float, default=0.0)  # Overall sustainability score (0-100)
    renewable_energy_percentage = Column(Float, default=0.0)  # If train uses renewable energy
    offsetting_options = Column(JSON)  # Available carbon offset programs
    
    # Corporate Reporting
    corporate_sustainability_data = Column(JSON)  # Data for corporate ESG reporting
    certification_standards = Column(JSON)  # ISO 14001, GRI standards compliance
    
    # Timestamps
    calculated_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    group = relationship('ModernGroupBooking', backref='sustainability_tracking')
    
    def calculate_emissions(self, distance_km: float, passenger_count: int) -> Dict[str, float]:
        """Calculate carbon emissions for the group journey"""
        self.total_distance_km = distance_km
        
        # Train emissions (much lower than air/car)
        self.carbon_emission_kg = distance_km * passenger_count * self.emission_factor
        
        # Compare with other transport modes
        # Air travel: ~0.24 kg CO2 per passenger-km
        self.air_travel_emissions = distance_km * passenger_count * 0.24
        self.savings_vs_air = self.air_travel_emissions - self.carbon_emission_kg
        
        # Car travel: ~0.18 kg CO2 per passenger-km (assuming 2 passengers per car)
        cars_needed = (passenger_count + 1) // 2  # Ceiling division
        self.car_travel_emissions = distance_km * cars_needed * 0.36  # 0.18 * 2 passengers
        self.savings_vs_car = self.car_travel_emissions - self.carbon_emission_kg
        
        # Calculate green score (higher is better)
        max_possible_savings = max(self.savings_vs_air, self.savings_vs_car)
        if max_possible_savings > 0:
            self.green_score = min(100, (max_possible_savings / self.air_travel_emissions) * 100)
        
        return {
            'train_emissions': self.carbon_emission_kg,
            'air_emissions': self.air_travel_emissions,
            'car_emissions': self.car_travel_emissions,
            'savings_vs_air': self.savings_vs_air,
            'savings_vs_car': self.savings_vs_car,
            'green_score': self.green_score
        }
    
    def generate_sustainability_report(self) -> Dict[str, Any]:
        """Generate comprehensive sustainability report"""
        return {
            'summary': {
                'total_distance': self.total_distance_km,
                'carbon_footprint': self.carbon_emission_kg,
                'green_score': self.green_score
            },
            'comparisons': {
                'vs_air_travel': {
                    'emissions_avoided': self.savings_vs_air,
                    'percentage_reduction': (self.savings_vs_air / self.air_travel_emissions * 100) if self.air_travel_emissions > 0 else 0
                },
                'vs_car_travel': {
                    'emissions_avoided': self.savings_vs_car,
                    'percentage_reduction': (self.savings_vs_car / self.car_travel_emissions * 100) if self.car_travel_emissions > 0 else 0
                }
            },
            'corporate_data': self.corporate_sustainability_data or {},
            'offsetting_options': self.offsetting_options or []
        }
    
    def __repr__(self):
        return f'<GroupSustainabilityTracking for {self.group.group_name}: {self.carbon_emission_kg}kg CO2>'