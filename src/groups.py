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
    Passenger, LoyaltyProgram, GroupMemberInvitation, 
    GroupMemberPayment, GroupMessage, db
)
from .utils import search_trains, calculate_fare
from flask import current_app as app

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

# Enhanced Group Booking Features

@groups_bp.route('/invite_member/<int:group_id>', methods=['GET', 'POST'])
@login_required
def invite_member(group_id):
    """Invite a member to join the group"""
    group = GroupBooking.query.get_or_404(group_id)
    
    # Verify access
    if group.group_leader_id != current_user.id:
        flash('Only group leaders can invite members', 'error')
        return redirect(url_for('groups.manage_group', group_id=group_id))
    
    if request.method == 'POST':
        invited_email = request.form.get('invited_email')
        message = request.form.get('message', '')
        
        if not invited_email:
            flash('Email address is required', 'error')
            return render_template('groups/invite_member.html', group=group)
        
        # Check if email is already invited
        existing_invitation = GroupMemberInvitation.query.filter_by(
            group_booking_id=group_id,
            invited_email=invited_email,
            status='pending'
        ).first()
        
        if existing_invitation and not existing_invitation.is_expired():
            flash('This email address already has a pending invitation', 'warning')
            return render_template('groups/invite_member.html', group=group)
        
        try:
            # Check if user exists
            invited_user = User.query.filter_by(email=invited_email).first()
            
            invitation = GroupMemberInvitation(
                group_booking_id=group_id,
                inviter_id=current_user.id,
                invited_email=invited_email,
                invited_user_id=invited_user.id if invited_user else None,
                message=message
            )
            
            db.session.add(invitation)
            db.session.commit()
            
            flash(f'Invitation sent to {invited_email}! Invitation code: {invitation.invitation_code}', 'success')
            return redirect(url_for('groups.manage_group', group_id=group_id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error sending invitation. Please try again.', 'error')
    
    return render_template('groups/invite_member.html', group=group)

@groups_bp.route('/join_group/<invitation_code>')
@login_required
def join_group(invitation_code):
    """Join group using invitation code"""
    invitation = GroupMemberInvitation.query.filter_by(
        invitation_code=invitation_code
    ).first_or_404()
    
    if not invitation.can_accept():
        flash('This invitation has expired or is no longer valid', 'error')
        return redirect(url_for('groups.my_groups'))
    
    # Check if user's email matches invitation
    if current_user.email != invitation.invited_email:
        flash('This invitation is not for your email address', 'error')
        return redirect(url_for('groups.my_groups'))
    
    try:
        invitation.status = 'accepted'
        invitation.responded_at = datetime.utcnow()
        invitation.invited_user_id = current_user.id
        
        db.session.commit()
        
        flash(f'Successfully joined group "{invitation.group_booking.group_name}"!', 'success')
        return redirect(url_for('groups.manage_group', group_id=invitation.group_booking_id))
        
    except Exception as e:
        db.session.rollback()
        flash('Error joining group. Please try again.', 'error')
        return redirect(url_for('groups.my_groups'))

@groups_bp.route('/group_payments/<int:group_id>')
@login_required
def group_payments(group_id):
    """View payment coordination for group"""
    group = GroupBooking.query.get_or_404(group_id)
    
    # Verify access - group leader or member
    is_member = any(booking.user_id == current_user.id for booking in group.individual_bookings)
    if group.group_leader_id != current_user.id and not is_member:
        flash('Access denied', 'error')
        return redirect(url_for('groups.my_groups'))
    
    payment_summary = group.get_payment_summary()
    member_payments = GroupMemberPayment.query.filter_by(group_booking_id=group_id).all()
    
    return render_template('groups/payments.html', 
                         group=group, 
                         payment_summary=payment_summary,
                         member_payments=member_payments)

@groups_bp.route('/group_messages/<int:group_id>', methods=['GET', 'POST'])
@login_required
def group_messages(group_id):
    """Group messaging for coordination"""
    group = GroupBooking.query.get_or_404(group_id)
    
    # Verify access - group leader or member
    is_member = any(booking.user_id == current_user.id for booking in group.individual_bookings)
    if group.group_leader_id != current_user.id and not is_member:
        flash('Access denied', 'error')
        return redirect(url_for('groups.my_groups'))
    
    if request.method == 'POST':
        message_text = request.form.get('message')
        message_type = request.form.get('message_type', 'general')
        is_important = request.form.get('is_important') == 'on'
        
        if message_text:
            try:
                message = GroupMessage(
                    group_booking_id=group_id,
                    sender_id=current_user.id,
                    message=message_text,
                    message_type=message_type,
                    is_important=is_important
                )
                
                db.session.add(message)
                db.session.commit()
                
                flash('Message sent successfully!', 'success')
                
            except Exception as e:
                db.session.rollback()
                flash('Error sending message. Please try again.', 'error')
    
    messages = GroupMessage.query.filter_by(group_booking_id=group_id).order_by(GroupMessage.created_at.desc()).all()
    
    # Mark messages as read
    for message in messages:
        if not message.is_read_by(current_user.id):
            message.mark_as_read(current_user.id)
    
    db.session.commit()
    
    return render_template('groups/messages.html', group=group, messages=messages)

@groups_bp.route('/enhanced_manage/<int:group_id>')
@login_required  
def enhanced_manage_group(group_id):
    """Enhanced group management with new features"""
    group = GroupBooking.query.get_or_404(group_id)
    
    # Verify access
    is_member = any(booking.user_id == current_user.id for booking in group.individual_bookings)
    if group.group_leader_id != current_user.id and not is_member and not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('groups.my_groups'))
    
    # Get enhanced information
    payment_summary = group.get_payment_summary()
    seat_coordination = group.get_seat_coordination_info()
    recent_messages = GroupMessage.query.filter_by(group_booking_id=group_id).order_by(GroupMessage.created_at.desc()).limit(3).all()
    pending_invitations = GroupMemberInvitation.query.filter_by(group_booking_id=group_id, status='pending').all()
    
    return render_template('groups/enhanced_manage.html', 
                         group=group,
                         payment_summary=payment_summary,
                         seat_coordination=seat_coordination,
                         recent_messages=recent_messages,
                         pending_invitations=pending_invitations)

@groups_bp.route('/send_payment_reminder/<int:group_id>', methods=['POST'])
@login_required
def send_payment_reminder(group_id):
    """Send payment reminder to a group member"""
    group = GroupBooking.query.get_or_404(group_id)
    
    # Verify access - only group leader can send reminders
    if group.group_leader_id != current_user.id:
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': 'User ID required'})
        
        # Find the user and their booking
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'})
        
        # For now, just mark that a reminder was sent
        # In a real app, you'd send an email here
        flash(f'Payment reminder sent to {user.email}', 'success')
        return jsonify({'success': True, 'message': 'Reminder sent successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Error sending reminder'})

@groups_bp.route('/add_passenger/<int:group_id>', methods=['GET', 'POST'])
@login_required
def add_passenger_to_group(group_id):
    """Add individual passenger details to a group"""
    group = GroupBooking.query.get_or_404(group_id)
    
    # Verify access - only group leader and members can add passengers
    is_member = any(booking.user_id == current_user.id for booking in group.individual_bookings)
    if group.group_leader_id != current_user.id and not is_member and not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('groups.my_groups'))
    
    if request.method == 'POST':
        passenger_name = request.form.get('passenger_name')
        passenger_age = request.form.get('passenger_age')
        passenger_gender = request.form.get('passenger_gender')
        id_proof_type = request.form.get('id_proof_type')
        id_proof_number = request.form.get('id_proof_number')
        seat_preference = request.form.get('seat_preference', 'No Preference')
        
        # Validation
        if not all([passenger_name, passenger_age, passenger_gender, id_proof_type, id_proof_number]):
            flash('Please fill all required fields', 'error')
            return render_template('groups/add_passenger.html', group=group)
        
        try:
            passenger_age = int(passenger_age)
            if passenger_age < 1 or passenger_age > 120:
                flash('Please enter a valid age between 1 and 120', 'error')
                return render_template('groups/add_passenger.html', group=group)
        except (ValueError, TypeError):
            flash('Please enter a valid age', 'error')
            return render_template('groups/add_passenger.html', group=group)
        
        # Check if we've reached the group capacity by counting existing passengers
        all_passengers = group.get_all_passengers()
        if len(all_passengers) >= group.total_passengers:
            flash(f'Group capacity reached. Maximum {group.total_passengers} passengers allowed.', 'error')
            return render_template('groups/add_passenger.html', group=group)
        
        try:
            # Create a temporary booking to associate the passenger with
            # This will be linked to actual train bookings later
            temp_booking = Booking(
                pnr=f"TEMP-{group.id}-{len(all_passengers)+1}",
                user_id=current_user.id,
                train_id=1,  # Temporary train ID - will be updated when actual booking is made
                from_station_id=1,  # Temporary station ID
                to_station_id=2,  # Temporary station ID
                journey_date=datetime.now().date() + timedelta(days=7),  # Default future date
                passengers=1,
                total_amount=0.0,
                group_booking_id=group_id,
                status='passenger_only'  # Special status for passenger-only records
            )
            
            db.session.add(temp_booking)
            db.session.flush()  # Get the booking ID
            
            # Create passenger record
            passenger = Passenger(
                booking_id=temp_booking.id,
                name=passenger_name,
                age=passenger_age,
                gender=passenger_gender,
                id_proof_type=id_proof_type,
                id_proof_number=id_proof_number,
                seat_preference=seat_preference
            )
            
            db.session.add(passenger)
            db.session.commit()
            
            flash(f'Passenger "{passenger_name}" added successfully to the group!', 'success')
            return redirect(url_for('groups.manage_group_passengers', group_id=group_id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error adding passenger. Please try again.', 'error')
            return render_template('groups/add_passenger.html', group=group)
    
    return render_template('groups/add_passenger.html', group=group)

@groups_bp.route('/manage_passengers/<int:group_id>')
@login_required
def manage_group_passengers(group_id):
    """Manage all passengers in the group"""
    group = GroupBooking.query.get_or_404(group_id)
    
    # Verify access
    is_member = any(booking.user_id == current_user.id for booking in group.individual_bookings)
    if group.group_leader_id != current_user.id and not is_member and not current_user.is_admin():
        flash('Access denied', 'error')
        return redirect(url_for('groups.my_groups'))
    
    # Get all passengers in the group
    all_passengers = group.get_all_passengers()
    
    # Categorize passengers by booking status
    confirmed_passengers = []
    pending_passengers = []
    
    for passenger in all_passengers:
        if passenger.booking.status == 'passenger_only':
            pending_passengers.append(passenger)
        else:
            confirmed_passengers.append(passenger)
    
    return render_template('groups/manage_passengers.html', 
                         group=group, 
                         confirmed_passengers=confirmed_passengers,
                         pending_passengers=pending_passengers,
                         remaining_slots=group.total_passengers - len(all_passengers))

@groups_bp.route('/remove_passenger/<int:passenger_id>', methods=['POST'])
@login_required
def remove_passenger_from_group(passenger_id):
    """Remove a passenger from the group"""
    passenger = Passenger.query.get_or_404(passenger_id)
    group = passenger.booking.group_booking
    
    # Verify access - only group leader can remove passengers
    if group.group_leader_id != current_user.id and not current_user.is_admin():
        flash('Only group leaders can remove passengers', 'error')
        return redirect(url_for('groups.manage_group_passengers', group_id=group.id))
    
    # Don't allow removal if passenger is part of a confirmed booking
    if passenger.booking.status != 'passenger_only':
        flash('Cannot remove passenger from confirmed booking. Cancel the booking first.', 'error')
        return redirect(url_for('groups.manage_group_passengers', group_id=group.id))
    
    try:
        passenger_name = passenger.name
        booking_to_remove = passenger.booking
        
        # Remove passenger and associated temporary booking
        db.session.delete(passenger)
        db.session.delete(booking_to_remove)
        db.session.commit()
        
        flash(f'Passenger "{passenger_name}" removed from the group.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error removing passenger. Please try again.', 'error')
    
    return redirect(url_for('groups.manage_group_passengers', group_id=group.id))

@groups_bp.route('/confirm_group_booking/<int:group_id>', methods=['POST', 'GET'])
@login_required
def confirm_group_booking(group_id):
    """Confirm the entire group booking"""
    group = GroupBooking.query.get_or_404(group_id)
    
    # Verify access - only group leader can confirm
    if group.group_leader_id != current_user.id:
        flash('Only group leaders can confirm bookings', 'error')
        return redirect(url_for('groups.manage_group', group_id=group_id))
    
    # Check if all payments are completed
    payment_summary = group.get_payment_summary()
    if payment_summary.get('pending_amount', 0) > 0:
        flash('All payments must be completed before confirming the group booking', 'error')
        return redirect(url_for('groups.group_payments', group_id=group_id))
    
    try:
        # Update all bookings in the group to confirmed
        bookings = Booking.query.filter_by(group_booking_id=group_id).all()
        for booking in bookings:
            if booking.status == 'pending_payment':
                booking.status = 'confirmed'
        
        group.status = 'confirmed'
        db.session.commit()
        
        flash(f'Group booking "{group.group_name}" has been confirmed!', 'success')
        return redirect(url_for('groups.manage_group', group_id=group_id))
        
    except Exception as e:
        db.session.rollback()
        flash('Error confirming group booking. Please try again.', 'error')
        return redirect(url_for('groups.group_payments', group_id=group_id))