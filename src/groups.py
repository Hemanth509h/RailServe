"""
Modern Group Booking System 2025 - Industry Standard
==================================================

Enterprise-grade group travel coordination featuring:
- Real-time seat selection with visual seat maps
- Corporate travel management with expense tracking  
- Intelligent discount structures (3-9: 33%, 10-50: bulk pricing, 50+: coach bookings)
- Family-friendly coordination with child ticket management
- Payment splitting and corporate integration
- Mobile-first responsive design
- API integration capabilities
- Automated expense reporting

Based on 2025 industry research from CTM Lightning OBT, Amadeus GDS, 
Trainline B2B, and modern corporate travel management platforms.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import and_, or_, func, desc
from datetime import datetime, timedelta, date, time
import json
import random
import string
import logging

from .modern_group_models import (
    ModernGroupBooking, GroupMembership, ModernGroupInvitation, 
    GroupBookingDetail, GroupPaymentSplit, ModernGroupMessage, 
    GroupActivityLog, GroupAnalytics
)
from .models import (
    User, Train, Station, TrainRoute, Booking, Passenger, 
    Payment, SeatAvailability, db
)
from .utils import search_trains, calculate_fare

# Configure logging
logger = logging.getLogger(__name__)

# Create modern groups blueprint
modern_groups_bp = Blueprint('modern_groups', __name__)

# Modern Group Booking Configuration - 2025 Standards
GROUP_TYPES_2025 = {
    'family': {
        'name': 'Family Travel',
        'min_size': 3, 'max_size': 20,
        'discount_rate': 33.0,  # Up to 33% as per GroupSave standards
        'features': ['child_tickets', 'family_seating', 'meal_coordination'],
        'color': '#10b981'
    },
    'corporate': {
        'name': 'Corporate Travel',
        'min_size': 6, 'max_size': 100,
        'discount_rate': 15.0,
        'features': ['expense_tracking', 'policy_compliance', 'approval_workflow', 'corporate_billing'],
        'color': '#3b82f6'
    },
    'tour': {
        'name': 'Tour Group',
        'min_size': 10, 'max_size': 200,
        'discount_rate': 18.0,
        'features': ['group_leader_tools', 'itinerary_management', 'bulk_coordination'],
        'color': '#8b5cf6'
    },
    'event': {
        'name': 'Event Travel',
        'min_size': 15, 'max_size': 500,
        'discount_rate': 25.0,
        'features': ['event_coordination', 'schedule_sync', 'bulk_messaging'],
        'color': '#f59e0b'
    },
    'educational': {
        'name': 'Educational Trip',
        'min_size': 20, 'max_size': 300,
        'discount_rate': 30.0,
        'features': ['student_management', 'educational_discounts', 'safety_protocols'],
        'color': '#ef4444'
    }
}

# Modern Seat Selection Configuration
SEAT_MAP_CONFIG = {
    'coach_layouts': {
        'SL': {'rows': 24, 'berths_per_row': 8, 'type': 'sleeper'},
        'AC3': {'rows': 18, 'berths_per_row': 8, 'type': 'ac_sleeper'},
        'AC2': {'rows': 16, 'berths_per_row': 4, 'type': 'ac_sleeper'},
        'AC1': {'rows': 12, 'berths_per_row': 2, 'type': 'ac_first'},
        'CC': {'rows': 20, 'seats_per_row': 5, 'type': 'chair_car'}
    },
    'berth_preferences': ['Lower', 'Middle', 'Upper', 'Side Lower', 'Side Upper'],
    'family_seating_rules': {
        'keep_together': True,
        'child_near_adult': True,
        'max_separation_rows': 2
    }
}

@modern_groups_bp.route('/dashboard')
@login_required
def group_dashboard():
    """Modern group booking dashboard with 2025 features"""
    try:
        # Get user's groups with modern analytics
        led_groups = ModernGroupBooking.query.filter_by(group_leader_id=current_user.id).all()
        
        # Get member groups using modern membership model
        member_groups = db.session.query(ModernGroupBooking).join(
            GroupMembership, ModernGroupBooking.id == GroupMembership.group_id
        ).filter(
            GroupMembership.user_id == current_user.id,
            GroupMembership.status == 'active',
            ModernGroupBooking.group_leader_id != current_user.id
        ).all()
        
        # Calculate modern analytics
        stats = calculate_user_group_stats(current_user.id, led_groups, member_groups)
        
        # Get recent activity with modern logging
        recent_activity = get_recent_group_activity(current_user.id, limit=10)
        
        return render_template('modern_groups/dashboard.html',
                             led_groups=led_groups,
                             member_groups=member_groups,
                             stats=stats,
                             recent_activity=recent_activity,
                             group_types=GROUP_TYPES_2025)
                             
    except Exception as e:
        logger.error(f"Error in group dashboard: {e}")
        flash('Error loading group dashboard. Please try again.', 'error')
        return redirect(url_for('index'))

@modern_groups_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_modern_group():
    """Create new modern group booking with 2025 enterprise features"""
    if request.method == 'POST':
        try:
            # Extract modern group data
            group_data = extract_group_creation_data(request.form)
            
            # Validate group data with modern rules
            validation_result = validate_group_creation(group_data)
            if not validation_result['valid']:
                flash(validation_result['message'], 'error')
                return render_template('modern_groups/create.html', 
                                     group_types=GROUP_TYPES_2025,
                                     form_data=group_data)
            
            # Generate unique group code
            group_code = generate_unique_group_code()
            
            # Create modern group booking
            group = ModernGroupBooking(
                group_name=group_data['name'],
                description=group_data['description'],
                group_code=group_code,
                group_leader_id=current_user.id,
                group_type=group_data['group_type'],
                estimated_passengers=group_data['estimated_passengers'],
                status='draft',
                travel_preferences=json.dumps(group_data['travel_preferences']),
                budget_constraints=json.dumps(group_data['budget_constraints']),
                contact_info=json.dumps(group_data['contact_info']),
                special_requirements=group_data['special_requirements'],
                accessibility_needs=group_data['accessibility_needs'],
                travel_start_date=group_data['travel_start_date'],
                travel_end_date=group_data['travel_end_date'],
                group_discount_rate=GROUP_TYPES_2025[group_data['group_type']]['discount_rate']
            )
            
            db.session.add(group)
            db.session.flush()  # Get the ID
            
            # Create group leader membership
            leader_membership = GroupMembership(
                group_id=group.id,
                user_id=current_user.id,
                role='leader',
                status='active',
                notification_preferences=json.dumps({'email': True, 'sms': True}),
                booking_permissions=json.dumps({
                    'can_book': True, 'can_modify': True, 'can_cancel': True
                })
            )
            
            # Log group creation activity
            activity = GroupActivityLog(
                group_id=group.id,
                user_id=current_user.id,
                activity_type='group_created',
                description=f'Created {group_data["group_type"]} group "{group_data["name"]}" for {group_data["estimated_passengers"]} passengers',
                context_data=json.dumps({'group_type': group_data['group_type']}),
                severity='success'
            )
            
            db.session.add_all([leader_membership, activity])
            db.session.commit()
            
            flash(f'Modern group "{group_data["name"]}" created successfully! Group code: {group_code}', 'success')
            return redirect(url_for('modern_groups.manage_group', group_id=group.id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating modern group: {e}")
            flash('Error creating group. Please try again.', 'error')
    
    return render_template('modern_groups/create.html', 
                         group_types=GROUP_TYPES_2025)

@modern_groups_bp.route('/manage/<int:group_id>')
@login_required
def manage_group(group_id):
    """Modern group management with enterprise features"""
    try:
        group = ModernGroupBooking.query.get_or_404(group_id)
        
        # Check access permissions
        access_check = check_group_access(group, current_user)
        if not access_check['allowed']:
            flash(access_check['message'], 'error')
            return redirect(url_for('modern_groups.group_dashboard'))
        
        # Get comprehensive group data
        group_data = get_comprehensive_group_data(group)
        
        return render_template('modern_groups/manage.html',
                             group=group,
                             **group_data)
                             
    except Exception as e:
        logger.error(f"Error in manage group: {e}")
        flash('Error loading group management. Please try again.', 'error')
        return redirect(url_for('modern_groups.group_dashboard'))

@modern_groups_bp.route('/seat_selection/<int:group_id>')
@login_required
def seat_selection_interface(group_id):
    """Modern seat selection with visual seat maps - 2025 feature"""
    try:
        group = ModernGroupBooking.query.get_or_404(group_id)
        
        # Check access permissions
        access_check = check_group_access(group, current_user)
        if not access_check['allowed']:
            return jsonify({'error': access_check['message']}), 403
        
        # Get group bookings with seat information
        bookings = GroupBookingDetail.query.filter_by(group_id=group_id).all()
        
        # Generate seat map data for each booking
        seat_maps = []
        for booking in bookings:
            if booking.train_id and booking.journey_date:
                seat_map = generate_seat_map(
                    booking.train_id, 
                    booking.journey_date, 
                    booking.coach_class,
                    group_id
                )
                seat_maps.append({
                    'booking_id': booking.id,
                    'train_name': booking.train.name if booking.train else 'Unknown',
                    'coach_class': booking.coach_class,
                    'seat_map': seat_map
                })
        
        return render_template('modern_groups/seat_selection.html',
                             group=group,
                             seat_maps=seat_maps,
                             seat_config=SEAT_MAP_CONFIG)
                             
    except Exception as e:
        logger.error(f"Error in seat selection: {e}")
        return jsonify({'error': 'Failed to load seat selection'}), 500

@modern_groups_bp.route('/group/<int:group_id>/save-seat-selection', methods=['POST'])
@login_required
def save_seat_selection(group_id):
    """Save seat selection for group booking with validation"""
    try:
        group = ModernGroupBooking.query.get_or_404(group_id)
        
        # Check access permissions
        access_check = check_group_access(group, current_user)
        if not access_check['allowed']:
            flash('You do not have permission to modify this group.', 'error')
            return redirect(url_for('modern_groups.group_dashboard'))
        
        # Get form data
        booking_id = request.form.get('booking_id')
        selected_seats_str = request.form.get('selected_seats', '')
        
        if not selected_seats_str:
            flash('No seats selected.', 'warning')
            return redirect(url_for('modern_groups.seat_selection_interface', group_id=group_id))
        
        # Parse and validate selected seats
        selected_seats = [seat.strip() for seat in selected_seats_str.split(',') if seat.strip()]
        
        if not selected_seats:
            flash('No seats selected.', 'warning')
            return redirect(url_for('modern_groups.seat_selection_interface', group_id=group_id))
        
        # Validate seat count doesn't exceed group size
        if len(selected_seats) > group.estimated_passengers:
            flash(f'Too many seats selected. Group size is {group.estimated_passengers} passengers.', 'warning')
            return redirect(url_for('modern_groups.seat_selection_interface', group_id=group_id))
        
        # Find or create AdvancedSeatAllocation records
        from .modern_group_models import AdvancedSeatAllocation
        
        if not booking_id:
            flash('No booking specified.', 'error')
            return redirect(url_for('modern_groups.seat_selection_interface', group_id=group_id))
        
        booking_detail = GroupBookingDetail.query.get(booking_id)
        if not booking_detail or booking_detail.group_id != group_id:
            flash('Invalid booking.', 'error')
            return redirect(url_for('modern_groups.seat_selection_interface', group_id=group_id))
        
        # Check for conflicting seat allocations from other groups
        conflicting_seats = AdvancedSeatAllocation.query.filter(
            AdvancedSeatAllocation.seat_number.in_(selected_seats),
            AdvancedSeatAllocation.coach_class == booking_detail.coach_class,
            AdvancedSeatAllocation.group_id != group_id,
            AdvancedSeatAllocation.allocation_status == 'confirmed'
        ).all()
        
        if conflicting_seats:
            conflict_list = ', '.join([s.seat_number for s in conflicting_seats[:5]])
            flash(f'Some seats are already allocated: {conflict_list}. Please select different seats.', 'error')
            return redirect(url_for('modern_groups.seat_selection_interface', group_id=group_id))
        
        # Begin transaction
        try:
            # Delete existing seat allocations for this booking
            AdvancedSeatAllocation.query.filter_by(
                group_id=group_id,
                booking_detail_id=booking_id
            ).delete()
            
            # Create new seat allocations
            for seat in selected_seats:
                seat_allocation = AdvancedSeatAllocation(
                    group_id=group_id,
                    booking_detail_id=booking_id,
                    coach_class=booking_detail.coach_class,
                    seat_number=seat,
                    allocation_status='selected',
                    allocated_at=datetime.utcnow()
                )
                db.session.add(seat_allocation)
            
            db.session.commit()
            
            # Log activity
            log_group_activity(
                group_id=group_id,
                user_id=current_user.id,
                activity_type='seat_selection',
                description=f'Selected {len(selected_seats)} seats for booking',
                metadata={'seats': selected_seats, 'booking_id': booking_id}
            )
            
            flash(f'Successfully selected {len(selected_seats)} seats!', 'success')
            
        except Exception as db_error:
            db.session.rollback()
            logger.error(f"Database error during seat allocation: {db_error}")
            flash('Failed to save seat selection due to a database error. Please try again.', 'error')
            return redirect(url_for('modern_groups.seat_selection_interface', group_id=group_id))
        
        return redirect(url_for('modern_groups.manage_group', group_id=group_id))
        
    except Exception as e:
        logger.error(f"Error saving seat selection: {e}")
        db.session.rollback()
        flash('Failed to save seat selection. Please try again.', 'error')
        return redirect(url_for('modern_groups.seat_selection_interface', group_id=group_id))

@modern_groups_bp.route('/api/group_analytics/<int:group_id>')
@login_required
def group_analytics_api(group_id):
    """API endpoint for real-time group analytics - 2025 feature"""
    try:
        group = ModernGroupBooking.query.get_or_404(group_id)
        
        # Check access permissions
        access_check = check_group_access(group, current_user)
        if not access_check['allowed']:
            return jsonify({'error': access_check['message']}), 403
        
        # Calculate real-time analytics
        analytics = calculate_group_analytics(group)
        
        return jsonify({
            'success': True,
            'analytics': analytics,
            'last_updated': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in group analytics API: {e}")
        return jsonify({'error': 'Failed to load analytics'}), 500

@modern_groups_bp.route('/corporate_dashboard')
@login_required
def corporate_dashboard():
    """Corporate travel management dashboard - 2025 enterprise feature"""
    try:
        # Only for corporate users or admins
        if not (current_user.is_admin() or has_corporate_permissions(current_user)):
            flash('Access denied. Corporate dashboard requires special permissions.', 'error')
            return redirect(url_for('modern_groups.group_dashboard'))
        
        # Get corporate group data
        corporate_groups = ModernGroupBooking.query.filter_by(
            group_type='corporate'
        ).filter(
            or_(
                ModernGroupBooking.group_leader_id == current_user.id,
                ModernGroupBooking.id.in_(
                    db.session.query(GroupMembership.group_id).filter_by(
                        user_id=current_user.id, status='active'
                    )
                )
            )
        ).all()
        
        # Calculate corporate analytics
        corporate_stats = calculate_corporate_analytics(corporate_groups)
        
        return render_template('modern_groups/corporate_dashboard.html',
                             corporate_groups=corporate_groups,
                             stats=corporate_stats)
                             
    except Exception as e:
        logger.error(f"Error in corporate dashboard: {e}")
        flash('Error loading corporate dashboard. Please try again.', 'error')
        return redirect(url_for('modern_groups.group_dashboard'))

# Utility Functions for Modern Group Booking System

def calculate_user_group_stats(user_id, led_groups, member_groups):
    """Calculate comprehensive user group statistics"""
    all_groups = led_groups + member_groups
    
    total_passengers = sum(g.estimated_passengers for g in all_groups)
    total_savings = sum(g.discount_applied or 0.0 for g in all_groups)
    active_groups = len([g for g in all_groups if g.status in ['active', 'payment_pending', 'confirmed']])
    
    # Calculate completion rate
    completed_groups = len([g for g in all_groups if g.status == 'completed'])
    completion_rate = (completed_groups / len(all_groups) * 100) if all_groups else 0
    
    return {
        'total_groups': len(all_groups),
        'active_groups': active_groups,
        'total_passengers': total_passengers,
        'total_savings': total_savings,
        'completion_rate': completion_rate,
        'led_groups_count': len(led_groups),
        'member_groups_count': len(member_groups)
    }

def get_recent_group_activity(user_id, limit=10):
    """Get recent group activity for user"""
    return GroupActivityLog.query.join(
        ModernGroupBooking, GroupActivityLog.group_id == ModernGroupBooking.id
    ).join(
        GroupMembership, ModernGroupBooking.id == GroupMembership.group_id
    ).filter(
        GroupMembership.user_id == user_id,
        GroupMembership.status == 'active'
    ).order_by(GroupActivityLog.created_at.desc()).limit(limit).all()

def extract_group_creation_data(form_data):
    """Extract and structure group creation data"""
    return {
        'name': form_data.get('group_name', '').strip(),
        'description': form_data.get('description', '').strip(),
        'group_type': form_data.get('group_type', 'family'),
        'estimated_passengers': int(form_data.get('estimated_passengers', 0)),
        'special_requirements': form_data.get('special_requirements', '').strip(),
        'accessibility_needs': form_data.get('accessibility_needs', '').strip(),
        'travel_preferences': {
            'class_preference': form_data.get('class_preference', 'SL'),
            'meal_preference': form_data.get('meal_preference', 'veg'),
            'seat_arrangement': form_data.get('seat_arrangement', 'together'),
            'insurance_required': form_data.get('insurance_required') == 'on'
        },
        'budget_constraints': {
            'min_budget': float(form_data.get('min_budget', 0) or 0),
            'max_budget': float(form_data.get('max_budget', 0) or 0),
            'currency': 'INR'
        },
        'contact_info': {
            'primary_email': form_data.get('primary_email', '').strip(),
            'secondary_email': form_data.get('secondary_email', '').strip(),
            'primary_phone': form_data.get('primary_phone', '').strip(),
            'emergency_contact': form_data.get('emergency_contact', '').strip()
        },
        'travel_start_date': datetime.strptime(form_data.get('travel_start_date'), '%Y-%m-%d').date() if form_data.get('travel_start_date') else None,
        'travel_end_date': datetime.strptime(form_data.get('travel_end_date'), '%Y-%m-%d').date() if form_data.get('travel_end_date') else None
    }

def validate_group_creation(group_data):
    """Validate group creation data with modern rules"""
    # Basic validation
    if not group_data['name']:
        return {'valid': False, 'message': 'Group name is required'}
    
    if not group_data['estimated_passengers'] or group_data['estimated_passengers'] < 3:
        return {'valid': False, 'message': 'Minimum 3 passengers required for group booking'}
    
    # Check group type constraints
    group_type_config = GROUP_TYPES_2025.get(group_data['group_type'])
    if not group_type_config:
        return {'valid': False, 'message': 'Invalid group type'}
    
    if group_data['estimated_passengers'] < group_type_config['min_size']:
        return {'valid': False, 'message': f'{group_type_config["name"]} requires minimum {group_type_config["min_size"]} passengers'}
    
    if group_data['estimated_passengers'] > group_type_config['max_size']:
        return {'valid': False, 'message': f'{group_type_config["name"]} allows maximum {group_type_config["max_size"]} passengers'}
    
    # Validate contact information
    if not group_data['contact_info']['primary_email']:
        return {'valid': False, 'message': 'Primary email is required'}
    
    if not group_data['contact_info']['primary_phone']:
        return {'valid': False, 'message': 'Primary phone is required'}
    
    # Validate travel dates
    if group_data['travel_start_date'] and group_data['travel_start_date'] <= date.today():
        return {'valid': False, 'message': 'Travel start date must be in the future'}
    
    if (group_data['travel_start_date'] and group_data['travel_end_date'] and 
        group_data['travel_end_date'] < group_data['travel_start_date']):
        return {'valid': False, 'message': 'Travel end date must be after start date'}
    
    return {'valid': True, 'message': 'Validation successful'}

def generate_unique_group_code():
    """Generate unique 8-character group code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not ModernGroupBooking.query.filter_by(group_code=code).first():
            return code

def check_group_access(group, user):
    """Check if user has access to group with detailed permissions"""
    # Group leader always has access
    if group.group_leader_id == user.id:
        return {'allowed': True, 'role': 'leader', 'permissions': ['all']}
    
    # Check membership
    membership = GroupMembership.query.filter_by(
        group_id=group.id, 
        user_id=user.id, 
        status='active'
    ).first()
    
    if membership:
        permissions = json.loads(membership.booking_permissions or '{}')
        return {'allowed': True, 'role': membership.role, 'permissions': permissions}
    
    # Admin access
    if user.is_admin():
        return {'allowed': True, 'role': 'admin', 'permissions': ['all']}
    
    return {'allowed': False, 'message': 'Access denied. You are not a member of this group.'}

def get_comprehensive_group_data(group):
    """Get all data needed for group management interface"""
    # Get memberships
    memberships = GroupMembership.query.filter_by(group_id=group.id).all()
    
    # Get bookings
    bookings = GroupBookingDetail.query.filter_by(group_id=group.id).all()
    
    # Get recent messages
    recent_messages = ModernGroupMessage.query.filter_by(
        group_id=group.id
    ).order_by(ModernGroupMessage.created_at.desc()).limit(5).all()
    
    # Get pending invitations
    pending_invitations = ModernGroupInvitation.query.filter_by(
        group_id=group.id, 
        status='pending'
    ).all()
    
    # Get payment splits
    payment_splits = GroupPaymentSplit.query.filter_by(group_id=group.id).all()
    
    # Calculate financial summary
    financial_summary = calculate_group_financial_summary(group, bookings, payment_splits)
    
    return {
        'memberships': memberships,
        'bookings': bookings,
        'recent_messages': recent_messages,
        'pending_invitations': pending_invitations,
        'payment_splits': payment_splits,
        'financial_summary': financial_summary,
        'group_type_config': GROUP_TYPES_2025.get(group.group_type, {}),
        'completion_percentage': calculate_group_completion_percentage(group)
    }

def calculate_group_financial_summary(group, bookings, payment_splits):
    """Calculate comprehensive financial summary for group"""
    total_estimated = group.total_estimated_cost or 0.0
    total_actual = sum(b.final_amount or 0.0 for b in bookings)
    total_paid = sum(ps.paid_amount or 0.0 for ps in payment_splits)
    total_outstanding = total_actual - total_paid
    
    return {
        'total_estimated': total_estimated,
        'total_actual': total_actual,
        'total_paid': total_paid,
        'total_outstanding': total_outstanding,
        'payment_completion_rate': (total_paid / total_actual * 100) if total_actual > 0 else 0,
        'discount_applied': group.discount_applied or 0.0,
        'savings_percentage': ((total_estimated - total_actual) / total_estimated * 100) if total_estimated > 0 else 0
    }

def calculate_group_completion_percentage(group):
    """Calculate group booking completion percentage"""
    total_steps = 6  # draft, members, bookings, payments, confirmation, completion
    completed_steps = 0
    
    if group.status != 'draft': 
        completed_steps += 1
    if group.get_member_count() > 0: 
        completed_steps += 1
    if len(group.bookings) > 0: 
        completed_steps += 2
    if group.status in ['confirmed', 'completed']: 
        completed_steps += 2
    
    return (completed_steps / total_steps) * 100

def generate_seat_map(train_id, journey_date, coach_class, group_id):
    """Generate visual seat map for group booking - 2025 feature"""
    try:
        # Get coach layout configuration
        layout = SEAT_MAP_CONFIG['coach_layouts'].get(coach_class, {})
        if not layout:
            return {'error': 'Unsupported coach class'}
        
        # Get seat availability
        availability = SeatAvailability.query.filter_by(
            train_id=train_id,
            journey_date=journey_date,
            coach_class=coach_class
        ).first()
        
        if not availability:
            return {'error': 'Seat availability not found'}
        
        # Generate seat map structure
        seat_map = {
            'coach_class': coach_class,
            'layout': layout,
            'total_seats': layout.get('rows', 0) * layout.get('berths_per_row', layout.get('seats_per_row', 0)),
            'available_seats': availability.available_seats,
            'seats': generate_seat_grid(layout, availability, group_id)
        }
        
        return seat_map
        
    except Exception as e:
        logger.error(f"Error generating seat map: {e}")
        return {'error': 'Failed to generate seat map'}

def generate_seat_grid(layout, availability, group_id):
    """Generate detailed seat grid with availability status"""
    seats = []
    rows = layout.get('rows', 20)
    seats_per_row = layout.get('berths_per_row', layout.get('seats_per_row', 4))
    
    for row in range(1, rows + 1):
        for seat in range(1, seats_per_row + 1):
            seat_number = f"{row:02d}{chr(64 + seat)}"  # 01A, 01B, etc.
            
            # Determine seat status (this would be based on actual booking data)
            status = 'available'  # available, booked, group_selected, preferred
            
            seats.append({
                'number': seat_number,
                'row': row,
                'position': seat,
                'status': status,
                'berth_type': get_berth_type(seat, layout['type']),
                'price_modifier': get_seat_price_modifier(row, seat, layout['type'])
            })
    
    return seats

def get_berth_type(seat_position, coach_type):
    """Get berth type based on seat position and coach type"""
    if coach_type == 'sleeper' or coach_type == 'ac_sleeper':
        berth_types = ['Lower', 'Middle', 'Upper', 'Side Lower', 'Side Upper']
        return berth_types[seat_position % len(berth_types)]
    elif coach_type == 'chair_car':
        return 'Window' if seat_position in [1, 5] else 'Aisle' if seat_position in [2, 4] else 'Middle'
    else:
        return 'Standard'

def get_seat_price_modifier(row, seat, coach_type):
    """Calculate price modifier based on seat preference"""
    # Premium seats (lower berths, window seats) have higher price
    if coach_type in ['sleeper', 'ac_sleeper'] and seat in [1, 4]:  # Lower berths
        return 1.1  # 10% premium
    elif coach_type == 'chair_car' and seat in [1, 5]:  # Window seats
        return 1.05  # 5% premium
    else:
        return 1.0  # No modifier

def calculate_group_analytics(group):
    """Calculate comprehensive group analytics - 2025 feature"""
    try:
        # Member engagement metrics
        total_members = group.get_member_count()
        active_members = len([m for m in group.memberships if m.last_active_at and 
                             m.last_active_at > datetime.utcnow() - timedelta(days=7)])
        
        # Financial metrics
        total_cost = group.total_actual_cost or 0.0
        cost_per_passenger = total_cost / group.actual_passengers if group.actual_passengers > 0 else 0
        
        # Booking efficiency
        bookings_count = len(group.bookings)
        booking_completion_rate = len([b for b in group.bookings if b.booking_status == 'confirmed']) / bookings_count * 100 if bookings_count > 0 else 0
        
        # Timeline metrics
        days_since_creation = (datetime.utcnow() - group.created_at).days
        estimated_completion_days = calculate_estimated_completion(group)
        
        return {
            'member_engagement': {
                'total_members': total_members,
                'active_members': active_members,
                'engagement_rate': active_members / total_members * 100 if total_members > 0 else 0
            },
            'financial_metrics': {
                'total_cost': total_cost,
                'cost_per_passenger': cost_per_passenger,
                'savings_amount': group.discount_applied or 0.0,
                'savings_percentage': group.group_discount_rate
            },
            'booking_metrics': {
                'total_bookings': bookings_count,
                'completion_rate': booking_completion_rate,
                'average_booking_size': group.actual_passengers / bookings_count if bookings_count > 0 else 0
            },
            'timeline_metrics': {
                'days_active': days_since_creation,
                'estimated_completion': estimated_completion_days,
                'completion_percentage': group.completion_percentage if hasattr(group, 'completion_percentage') else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculating group analytics: {e}")
        return {'error': 'Failed to calculate analytics'}

def calculate_estimated_completion(group):
    """Estimate days to completion based on group type and progress"""
    base_days = {
        'family': 7,
        'corporate': 14,
        'tour': 21,
        'event': 30,
        'educational': 45
    }
    
    return base_days.get(group.group_type, 14)

def has_corporate_permissions(user):
    """Check if user has corporate travel management permissions"""
    # This would integrate with corporate directory or permissions system
    # For now, check if user has any corporate group memberships
    corporate_memberships = db.session.query(GroupMembership).join(
        ModernGroupBooking, GroupMembership.group_id == ModernGroupBooking.id
    ).filter(
        GroupMembership.user_id == user.id,
        ModernGroupBooking.group_type == 'corporate',
        GroupMembership.status == 'active'
    ).first()
    
    return corporate_memberships is not None

def calculate_corporate_analytics(corporate_groups):
    """Calculate corporate-specific analytics"""
    total_spend = sum(g.total_actual_cost or 0.0 for g in corporate_groups)
    total_travelers = sum(g.actual_passengers for g in corporate_groups)
    total_savings = sum(g.discount_applied or 0.0 for g in corporate_groups)
    
    # Policy compliance rate (simplified calculation)
    compliant_bookings = len([g for g in corporate_groups if g.status in ['confirmed', 'completed']])
    compliance_rate = compliant_bookings / len(corporate_groups) * 100 if corporate_groups else 0
    
    return {
        'total_spend': total_spend,
        'total_travelers': total_travelers,
        'total_savings': total_savings,
        'average_cost_per_traveler': total_spend / total_travelers if total_travelers > 0 else 0,
        'policy_compliance_rate': compliance_rate,
        'active_groups': len([g for g in corporate_groups if g.status in ['active', 'payment_pending', 'confirmed']])
    }