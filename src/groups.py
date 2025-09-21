"""
Group Booking System
Allows families, corporate groups, and tour operators to book multiple tickets together
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from .models import (
    GroupBooking, Booking, User, Train, Station, TrainRoute, 
    Passenger, LoyaltyProgram, db
)
from .utils import search_trains, calculate_fare
from .app import app

groups_bp = Blueprint('groups', __name__)

@groups_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_group_booking():
    """Create a new group booking"""
    if request.method == 'POST':
        group_name = request.form.get('group_name')
        total_passengers = request.form.get('total_passengers')
        booking_type = request.form.get('booking_type', 'family')
        contact_email = request.form.get('contact_email')
        contact_phone = request.form.get('contact_phone')
        special_requirements = request.form.get('special_requirements', '')
        
        # Validation
        if not all([group_name, total_passengers, contact_email, contact_phone]):
            flash('Please fill all required fields', 'error')
            return render_template('groups/create.html')
        
        try:
            total_passengers = int(total_passengers) if total_passengers else 0
            if total_passengers < 4:  # Minimum for group booking
                flash('Group bookings require minimum 4 passengers', 'error')
                return render_template('groups/create.html')
        except (ValueError, TypeError):
            flash('Invalid number of passengers', 'error')
            return render_template('groups/create.html')
        
        # Calculate group discount based on size
        group_discount_rate = 0.0
        if total_passengers >= 20:
            group_discount_rate = 15.0  # 15% for large groups
        elif total_passengers >= 10:
            group_discount_rate = 10.0  # 10% for medium groups
        elif total_passengers >= 6:
            group_discount_rate = 5.0   # 5% for small groups
        
        try:
            # Create group booking
            group_booking = GroupBooking(
                group_name=group_name,
                group_leader_id=current_user.id,
                total_passengers=total_passengers,
                contact_email=contact_email,
                contact_phone=contact_phone,
                booking_type=booking_type,
                special_requirements=special_requirements,
                group_discount_rate=group_discount_rate,
                status='pending'
            )
            
            db.session.add(group_booking)
            db.session.commit()
            
            flash(f'Group booking "{group_name}" created successfully! Group discount: {group_discount_rate}%', 'success')
            return redirect(url_for('groups.manage_group', group_id=group_booking.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error creating group booking. Please try again.', 'error')
            return render_template('groups/create.html')
    
    return render_template('groups/create.html')

@groups_bp.route('/manage/<int:group_id>')
@login_required
def manage_group(group_id):
    """Manage a group booking"""
    group = GroupBooking.query.get_or_404(group_id)
    
    # Verify user is group leader or admin
    if group.group_leader_id != current_user.id and not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('groups.my_groups'))
    
    # Get all bookings in this group
    bookings = Booking.query.filter_by(group_booking_id=group_id).all()
    
    # Calculate statistics
    confirmed_count = len([b for b in bookings if b.status == 'confirmed'])
    total_amount = sum(b.total_amount for b in bookings)
    discount_amount = group.discount_applied
    
    return render_template('groups/manage.html', 
                         group=group, 
                         bookings=bookings,
                         confirmed_count=confirmed_count,
                         total_amount=total_amount,
                         discount_amount=discount_amount)

@groups_bp.route('/add_booking/<int:group_id>', methods=['GET', 'POST'])
@login_required
def add_group_train_booking(group_id):
    """Add a train booking to the group"""
    group = GroupBooking.query.get_or_404(group_id)
    
    # Verify access
    if group.group_leader_id != current_user.id and not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('groups.my_groups'))
    
    if request.method == 'POST':
        from_station = request.form.get('from_station')
        to_station = request.form.get('to_station')
        journey_date = request.form.get('journey_date')
        train_id = request.form.get('train_id')
        passengers = request.form.get('passengers')
        coach_class = request.form.get('coach_class', 'SL')
        
        if not all([from_station, to_station, journey_date, train_id, passengers]):
            flash('Please fill all required fields', 'error')
            return redirect(url_for('groups.add_group_train_booking', group_id=group_id))
        
        try:
            passengers = int(passengers) if passengers else 0
            train_id = int(train_id) if train_id else 0
            
            # Verify remaining capacity in group
            current_bookings = Booking.query.filter_by(group_booking_id=group_id).all()
            current_passenger_count = sum(b.passengers for b in current_bookings)
            
            if current_passenger_count + passengers > group.total_passengers:
                flash(f'Exceeds group capacity. Available slots: {group.total_passengers - current_passenger_count}', 'error')
                return redirect(url_for('groups.add_group_train_booking', group_id=group_id))
            
            # Validate journey date is not in the past
            parsed_journey_date = datetime.strptime(journey_date or '', '%Y-%m-%d').date()
            tomorrow = (datetime.now() + timedelta(days=1)).date()
            if parsed_journey_date < tomorrow:
                flash('Journey date must be at least tomorrow', 'error')
                return redirect(url_for('groups.add_group_train_booking', group_id=group_id))
            
            # Calculate fare (this would use your existing fare calculation logic)
            base_fare = passengers * 500  # Simplified calculation
            
            # Apply group discount
            group_discount = (base_fare * group.group_discount_rate) / 100
            total_amount = base_fare - group_discount
            
            # Create booking
            booking = Booking(
                user_id=current_user.id,
                train_id=train_id,
                from_station_id=int(from_station) if from_station else 0,
                to_station_id=int(to_station) if to_station else 0,
                journey_date=parsed_journey_date,
                passengers=passengers,
                total_amount=total_amount,
                coach_class=coach_class,
                group_booking_id=group_id,
                status='pending_payment'
            )
            
            db.session.add(booking)
            
            # Update group discount applied
            group.discount_applied += group_discount
            
            db.session.commit()
            
            flash(f'Booking added to group! Group discount applied: ₹{group_discount:.2f}', 'success')
            return redirect(url_for('groups.manage_group', group_id=group_id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error adding booking to group. Please try again.', 'error')
    
    # Get available trains for booking
    stations = Station.query.order_by(Station.name).all()
    trains = Train.query.filter_by(active=True).order_by(Train.name).all()
    
    # Calculate minimum date (tomorrow)
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    return render_template('groups/add_booking.html', 
                         group=group, 
                         stations=stations, 
                         trains=trains,
                         min_date=tomorrow)

@groups_bp.route('/my_groups')
@login_required
def my_groups():
    """Show user's group bookings"""
    # Groups where user is the leader
    led_groups = GroupBooking.query.filter_by(group_leader_id=current_user.id).all()
    
    # Groups where user has bookings (member of group)
    member_groups = db.session.query(GroupBooking).join(Booking).filter(
        and_(
            Booking.user_id == current_user.id,
            Booking.group_booking_id.isnot(None),
            GroupBooking.group_leader_id != current_user.id
        )
    ).distinct().all()
    
    return render_template('groups/my_groups.html', 
                         led_groups=led_groups, 
                         member_groups=member_groups)

@groups_bp.route('/search_trains_api')
@login_required
def search_trains_api():
    """API endpoint for searching trains (for AJAX)"""
    from_station = request.args.get('from_station')
    to_station = request.args.get('to_station')
    journey_date = request.args.get('journey_date')
    
    if not all([from_station, to_station, journey_date]):
        return jsonify({'trains': []})
    
    trains = search_trains(from_station, to_station, journey_date)
    
    train_data = []
    for train in trains:
        train_data.append({
            'id': train.id,
            'number': train.number,
            'name': train.name,
            'available_seats': train.available_seats,
            'fare_per_km': train.fare_per_km
        })
    
    return jsonify({'trains': train_data})

@groups_bp.route('/cancel_group/<int:group_id>', methods=['POST'])
@login_required
def cancel_group_booking(group_id):
    """Cancel entire group booking"""
    group = GroupBooking.query.get_or_404(group_id)
    
    # Verify access
    if group.group_leader_id != current_user.id and not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('groups.my_groups'))
    
    try:
        # Cancel all individual bookings in the group
        bookings = Booking.query.filter_by(group_booking_id=group_id).all()
        for booking in bookings:
            if booking.status in ['confirmed', 'waitlisted']:
                booking.status = 'cancelled'
        
        group.status = 'cancelled'
        db.session.commit()
        
        flash(f'Group booking "{group.group_name}" has been cancelled', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error cancelling group booking. Please try again.', 'error')
    
    return redirect(url_for('groups.my_groups'))

# Admin routes for group booking management

@groups_bp.route('/admin/groups')
@login_required
def admin_groups():
    """Admin: View all group bookings"""
    if not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    groups = GroupBooking.query.order_by(GroupBooking.created_at.desc()).all()
    
    # Calculate statistics
    total_groups = len(groups)
    active_groups = len([g for g in groups if g.status in ['pending', 'confirmed']])
    total_passengers = sum(g.total_passengers for g in groups if g.status != 'cancelled')
    
    return render_template('groups/admin_groups.html', 
                         groups=groups,
                         total_groups=total_groups,
                         active_groups=active_groups,
                         total_passengers=total_passengers)