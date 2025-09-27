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