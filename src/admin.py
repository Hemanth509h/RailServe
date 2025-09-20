from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from functools import wraps
from .models import User, Train, Station, Booking, Payment, TrainRoute, TatkalTimeSlot, TatkalOverride
from sqlalchemy import and_
from .app import db
from datetime import datetime, timedelta, date
import csv
import io

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    """Decorator to require super admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_super_admin():
            flash('Access denied. Super admin privileges required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def dashboard():
    """Enhanced admin dashboard with Tatkal insights"""
    total_users = User.query.count()
    total_trains = Train.query.count()
    total_bookings = Booking.query.count()
    total_revenue = db.session.query(db.func.sum(Payment.amount)).filter_by(status='success').scalar() or 0
    
    # Tatkal specific stats
    tatkal_bookings = Booking.query.filter_by(booking_type='tatkal').count()
    tatkal_revenue = db.session.query(db.func.sum(Booking.total_amount)).filter(
        Booking.booking_type == 'tatkal'
    ).scalar() or 0
    
    # Recent bookings with type
    recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(10).all()
    
    # Enhanced booking stats with type breakdown
    booking_stats = db.session.query(
        Booking.status, 
        Booking.booking_type,
        db.func.count(Booking.id)
    ).group_by(Booking.status, Booking.booking_type).all()
    
    # Quick actions needed
    pending_payments = Booking.query.filter_by(status='pending_payment').count()
    waitlist_count = Booking.query.filter_by(status='waitlisted').count()
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_trains=total_trains,
                         total_bookings=total_bookings,
                         total_revenue=total_revenue,
                         tatkal_bookings=tatkal_bookings,
                         tatkal_revenue=tatkal_revenue,
                         recent_bookings=recent_bookings,
                         booking_stats=booking_stats,
                         pending_payments=pending_payments,
                         waitlist_count=waitlist_count)

@admin_bp.route('/trains')
@admin_required
def trains():
    """Manage trains with search functionality"""
    search = request.args.get('search', '').strip()
    
    if search:
        # Search by train number or name
        trains = Train.query.filter(
            db.or_(
                Train.number.ilike(f'%{search}%'),
                Train.name.ilike(f'%{search}%')
            )
        ).all()
    else:
        trains = Train.query.all()
    
    return render_template('admin/trains.html', trains=trains, search=search)

@admin_bp.route('/trains/add', methods=['POST'])
@admin_required
def add_train():
    """Add new train with Tatkal configuration"""
    number = request.form.get('number')
    name = request.form.get('name')
    total_seats = request.form.get('total_seats', type=int)
    fare_per_km = request.form.get('fare_per_km', type=float)
    tatkal_seats = request.form.get('tatkal_seats', type=int) or 0
    tatkal_fare_per_km = request.form.get('tatkal_fare_per_km', type=float)
    
    if not all([number, name, total_seats, fare_per_km]):
        flash('Please fill all required fields', 'error')
        return redirect(url_for('admin.trains'))
    
    # Additional validation
    if total_seats and (total_seats < 50 or total_seats > 2000):
        flash('Total seats must be between 50 and 2000', 'error')
        return redirect(url_for('admin.trains'))
    
    if fare_per_km and (fare_per_km < 0.5 or fare_per_km > 50.0):
        flash('Fare per km must be between ₹0.50 and ₹50.00', 'error')
        return redirect(url_for('admin.trains'))
    
    if Train.query.filter_by(number=number).first():
        flash('Train number already exists', 'error')
        return redirect(url_for('admin.trains'))
    
    # Validate Tatkal seats don't exceed total seats
    if tatkal_seats and total_seats and tatkal_seats > total_seats:
        flash('Tatkal seats cannot exceed total seats', 'error')
        return redirect(url_for('admin.trains'))
    
    train = Train(
        number=number,
        name=name,
        total_seats=total_seats,
        available_seats=total_seats,
        fare_per_km=fare_per_km,
        tatkal_seats=tatkal_seats,
        tatkal_fare_per_km=tatkal_fare_per_km or (fare_per_km * 1.5 if fare_per_km else None)
    )
    
    db.session.add(train)
    db.session.commit()
    
    flash('Train added successfully with Tatkal configuration', 'success')
    return redirect(url_for('admin.trains'))

@admin_bp.route('/trains/<int:train_id>/toggle')
@admin_required
def toggle_train(train_id):
    """Toggle train active status"""
    train = Train.query.get_or_404(train_id)
    train.active = not train.active
    db.session.commit()
    
    status = 'activated' if train.active else 'deactivated'
    flash(f'Train {train.number} {status} successfully', 'success')
    return redirect(url_for('admin.trains'))

@admin_bp.route('/stations')
@admin_required
def stations():
    """Manage stations with search functionality"""
    search = request.args.get('search', '').strip()
    
    if search:
        # Search by station code, name, or city
        stations = Station.query.filter(
            db.or_(
                Station.code.ilike(f'%{search}%'),
                Station.name.ilike(f'%{search}%'),
                Station.city.ilike(f'%{search}%')
            )
        ).all()
    else:
        stations = Station.query.all()
    
    return render_template('admin/stations.html', stations=stations, search=search)

@admin_bp.route('/stations/add', methods=['POST'])
@admin_required
def add_station():
    """Add new station"""
    name = request.form.get('name')
    code = request.form.get('code')
    city = request.form.get('city')
    state = request.form.get('state')
    
    if not all([name, code, city, state]):
        flash('Please fill all fields', 'error')
        return redirect(url_for('admin.stations'))
    
    code = code.upper() if code else ''
    
    if Station.query.filter_by(name=name).first():
        flash('Station name already exists', 'error')
        return redirect(url_for('admin.stations'))
    
    if Station.query.filter_by(code=code).first():
        flash('Station code already exists', 'error')
        return redirect(url_for('admin.stations'))
    
    station = Station(
        name=name,
        code=code,
        city=city,
        state=state
    )
    
    db.session.add(station)
    db.session.commit()
    
    flash('Station added successfully', 'success')
    return redirect(url_for('admin.stations'))

@admin_bp.route('/stations/<int:station_id>/toggle')
@admin_required
def toggle_station(station_id):
    """Toggle station active status"""
    station = Station.query.get_or_404(station_id)
    station.active = not station.active
    db.session.commit()
    
    status = 'activated' if station.active else 'deactivated'
    flash(f'Station {station.name} {status} successfully', 'success')
    return redirect(url_for('admin.stations'))

@admin_bp.route('/users')
@super_admin_required
def users():
    """Manage users (Super Admin only) with search functionality"""
    search = request.args.get('search', '').strip()
    
    if search:
        # Search by username or email
        users = User.query.filter(
            db.or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        ).all()
    else:
        users = User.query.all()
    
    return render_template('admin/users.html', users=users, search=search)

@admin_bp.route('/users/<int:user_id>/toggle')
@super_admin_required
def toggle_user(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    
    # Prevent deactivating self
    if user.id == current_user.id:
        flash('Cannot deactivate your own account', 'error')
        return redirect(url_for('admin.users'))
    
    user.active = not user.active
    db.session.commit()
    
    status = 'activated' if user.active else 'blocked'
    flash(f'User {user.username} {status} successfully', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/promote')
@super_admin_required
def promote_user(user_id):
    """Promote user to admin"""
    user = User.query.get_or_404(user_id)
    
    if user.role == 'super_admin':
        flash('User is already a super admin', 'error')
        return redirect(url_for('admin.users'))
    
    user.role = 'admin' if user.role == 'user' else 'super_admin'
    db.session.commit()
    
    flash(f'User {user.username} promoted to {user.role}', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/analytics')
@admin_required
def analytics():
    """Enhanced analytics dashboard with Tatkal insights"""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Revenue data for last 30 days
    daily_revenue = db.session.query(
        db.func.date(Payment.completed_at),
        db.func.sum(Payment.amount)
    ).filter(
        Payment.status == 'success',
        Payment.completed_at >= thirty_days_ago
    ).group_by(db.func.date(Payment.completed_at)).all()
    
    # Popular trains
    popular_trains = db.session.query(
        Train.name,
        db.func.count(Booking.id)
    ).join(Booking).group_by(Train.name).order_by(db.func.count(Booking.id).desc()).limit(10).all()
    
    # Booking trends by type
    general_bookings = db.session.query(
        db.func.date(Booking.booking_date),
        db.func.count(Booking.id)
    ).filter(
        Booking.booking_date >= thirty_days_ago,
        Booking.booking_type == 'general'
    ).group_by(db.func.date(Booking.booking_date)).all()
    
    tatkal_bookings = db.session.query(
        db.func.date(Booking.booking_date),
        db.func.count(Booking.id)
    ).filter(
        Booking.booking_date >= thirty_days_ago,
        Booking.booking_type == 'tatkal'
    ).group_by(db.func.date(Booking.booking_date)).all()
    
    # Tatkal vs General revenue comparison
    tatkal_revenue = db.session.query(
        db.func.sum(Booking.total_amount)
    ).filter(
        Booking.booking_type == 'tatkal',
        Booking.booking_date >= thirty_days_ago
    ).scalar() or 0
    
    general_revenue = db.session.query(
        db.func.sum(Booking.total_amount)
    ).filter(
        Booking.booking_type == 'general',
        Booking.booking_date >= thirty_days_ago
    ).scalar() or 0
    
    # Peak booking hours
    peak_hours = db.session.query(
        db.func.extract('hour', Booking.booking_date),
        db.func.count(Booking.id)
    ).filter(
        Booking.booking_date >= thirty_days_ago
    ).group_by(db.func.extract('hour', Booking.booking_date)).order_by(db.func.count(Booking.id).desc()).limit(5).all()
    
    return render_template('admin/analytics.html',
                         daily_revenue=daily_revenue,
                         popular_trains=popular_trains,
                         general_bookings=general_bookings,
                         tatkal_bookings=tatkal_bookings,
                         tatkal_revenue=tatkal_revenue,
                         general_revenue=general_revenue,
                         peak_hours=peak_hours)

@admin_bp.route('/reports/bookings.csv')
@admin_required
def export_bookings():
    """Export bookings to CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['PNR', 'User', 'Train', 'From', 'To', 'Date', 'Passengers', 'Amount', 'Status'])
    
    # Write data
    bookings = Booking.query.all()
    for booking in bookings:
        writer.writerow([
            booking.pnr,
            booking.user.username,
            f"{booking.train.number} - {booking.train.name}",
            booking.from_station.name,
            booking.to_station.name,
            booking.journey_date.strftime('%Y-%m-%d'),
            booking.passengers,
            booking.total_amount,
            booking.status
        ])
    
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=bookings.csv'
    response.headers['Content-type'] = 'text/csv'
    
    return response

@admin_bp.route('/bookings')
@admin_required
def bookings():
    """Manage all bookings with filtering"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    booking_type_filter = request.args.get('booking_type', '')
    
    query = Booking.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    if booking_type_filter:
        query = query.filter_by(booking_type=booking_type_filter)
    
    # Add search functionality
    search = request.args.get('search', '').strip()
    if search:
        # Search by PNR, username, or train number
        query = query.join(User).join(Train).filter(
            db.or_(
                Booking.pnr.ilike(f'%{search}%'),
                User.username.ilike(f'%{search}%'),
                Train.number.ilike(f'%{search}%'),
                Train.name.ilike(f'%{search}%')
            )
        )
    
    bookings = query.order_by(Booking.booking_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/bookings.html', bookings=bookings,
                         status_filter=status_filter,
                         booking_type_filter=booking_type_filter,
                         search=search)

@admin_bp.route('/bookings/<int:booking_id>/update', methods=['POST'])
@admin_required
def update_booking_status(booking_id):
    """Update booking status (admin override)"""
    booking = Booking.query.get_or_404(booking_id)
    new_status = request.form.get('status')
    
    if new_status not in ['confirmed', 'waitlisted', 'cancelled']:
        flash('Invalid status', 'error')
        return redirect(url_for('admin.bookings'))
    
    old_status = booking.status
    booking.status = new_status
    
    # Handle seat allocation changes
    if old_status == 'confirmed' and new_status in ['cancelled', 'waitlisted']:
        # Release seats
        train = booking.train
        train.available_seats += booking.passengers
    elif old_status in ['cancelled', 'waitlisted'] and new_status == 'confirmed':
        # Allocate seats
        train = booking.train
        train.available_seats = max(0, train.available_seats - booking.passengers)
    
    db.session.commit()
    
    flash(f'Booking {booking.pnr} status updated to {new_status}', 'success')
    return redirect(url_for('admin.bookings'))

@admin_bp.route('/real-time')
@admin_required
def real_time_monitor():
    """Real-time monitoring dashboard"""
    # Recent activity (last hour)
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    
    recent_bookings = Booking.query.filter(
        Booking.booking_date >= one_hour_ago
    ).order_by(Booking.booking_date.desc()).limit(10).all()
    
    recent_payments = Payment.query.filter(
        Payment.created_at >= one_hour_ago
    ).order_by(Payment.created_at.desc()).limit(10).all()
    
    # Current system stats
    active_users = User.query.filter_by(active=True).count()
    pending_bookings = Booking.query.filter_by(status='pending_payment').count()
    waitlisted_bookings = Booking.query.filter_by(status='waitlisted').count()
    
    # High-demand trains (most bookings today)
    today = datetime.utcnow().date()
    high_demand_trains = db.session.query(
        Train.name,
        db.func.count(Booking.id)
    ).join(Booking).filter(
        db.func.date(Booking.booking_date) == today
    ).group_by(Train.name).order_by(db.func.count(Booking.id).desc()).limit(5).all()
    
    return render_template('admin/real_time.html',
                         recent_bookings=recent_bookings,
                         recent_payments=recent_payments,
                         active_users=active_users,
                         pending_bookings=pending_bookings,
                         waitlisted_bookings=waitlisted_bookings,
                         high_demand_trains=high_demand_trains)

# Real Railway Management Features

@admin_bp.route('/quota-management')
@admin_required
def quota_management():
    """Train ticket allotment and quota management"""
    trains = Train.query.all()
    return render_template('admin/quota_management.html', trains=trains)

@admin_bp.route('/quota-management/<int:train_id>', methods=['POST'])
@admin_required
def update_quota(train_id):
    """Update train quota allocation"""
    train = Train.query.get_or_404(train_id)
    
    total_seats = request.form.get('total_seats', type=int)
    tatkal_seats = request.form.get('tatkal_seats', type=int)
    tatkal_fare_per_km = request.form.get('tatkal_fare_per_km', type=float)
    
    if tatkal_seats and total_seats and tatkal_seats > total_seats:
        flash('Tatkal seats cannot exceed total seats', 'error')
        return redirect(url_for('admin.quota_management'))
    
    # Enhanced server-side validation for quota updates
    if not total_seats or total_seats < 50 or total_seats > 2000:
        flash('Total seats must be between 50 and 2000', 'error')
        return redirect(url_for('admin.quota_management'))
    
    if tatkal_seats and (tatkal_seats < 0 or tatkal_seats > total_seats):
        flash('Tatkal seats must be between 0 and total seats', 'error')
        return redirect(url_for('admin.quota_management'))
    
    if tatkal_fare_per_km and (tatkal_fare_per_km < 0.5 or tatkal_fare_per_km > 100.0):
        flash('Tatkal fare per km must be between ₹0.50 and ₹100.00', 'error')
        return redirect(url_for('admin.quota_management'))
    
    train.total_seats = total_seats
    train.available_seats = total_seats
    train.tatkal_seats = tatkal_seats or 0
    train.tatkal_fare_per_km = tatkal_fare_per_km
    
    db.session.commit()
    flash(f'Quota updated for train {train.number}', 'success')
    return redirect(url_for('admin.quota_management'))

@admin_bp.route('/tatkal-timeslots')
@admin_required
def tatkal_timeslots():
    """Manage Tatkal time slot configurations"""
    time_slots = TatkalTimeSlot.query.order_by(TatkalTimeSlot.created_at.desc()).all()
    return render_template('admin/tatkal_timeslots.html', time_slots=time_slots)

@admin_bp.route('/tatkal-timeslots/add', methods=['POST'])
@admin_required
def add_tatkal_timeslot():
    """Add new Tatkal time slot configuration"""
    name = request.form.get('name')
    coach_classes = request.form.get('coach_classes')
    open_time_str = request.form.get('open_time')
    close_time_str = request.form.get('close_time')
    days_before_journey = request.form.get('days_before_journey', type=int)
    
    if not all([name, coach_classes, open_time_str, days_before_journey]):
        flash('Please fill all required fields', 'error')
        return redirect(url_for('admin.tatkal_timeslots'))
    
    try:
        from datetime import datetime
        if not open_time_str:
            flash('Open time is required', 'error')
            return redirect(url_for('admin.tatkal_timeslots'))
        
        open_time = datetime.strptime(open_time_str, '%H:%M').time()
        close_time = datetime.strptime(close_time_str, '%H:%M').time() if close_time_str and close_time_str.strip() else None
        
        # Validate time slot
        if close_time and close_time <= open_time:
            flash('Close time must be after open time', 'error')
            return redirect(url_for('admin.tatkal_timeslots'))
        
        if days_before_journey is None or days_before_journey < 0 or days_before_journey > 30:
            flash('Days before journey must be between 0 and 30', 'error')
            return redirect(url_for('admin.tatkal_timeslots'))
        
        # Validate coach classes
        valid_classes = ['AC1', 'AC2', 'AC3', 'SL', '2S', 'CC']
        if not coach_classes:
            flash('Please select coach classes', 'error')
            return redirect(url_for('admin.tatkal_timeslots'))
        
        selected_classes = [cls.strip() for cls in coach_classes.split(',') if cls.strip()]
        invalid_classes = [cls for cls in selected_classes if cls not in valid_classes]
        
        if invalid_classes:
            flash(f'Invalid coach classes: {invalid_classes}. Valid classes: {valid_classes}', 'error')
            return redirect(url_for('admin.tatkal_timeslots'))
        
        time_slot = TatkalTimeSlot(
            name=name,
            coach_classes=coach_classes,
            open_time=open_time,
            close_time=close_time,
            days_before_journey=days_before_journey,
            created_by=current_user.id
        )
        
        db.session.add(time_slot)
        db.session.commit()
        
        flash(f'Tatkal time slot "{name}" created successfully', 'success')
        
    except ValueError as e:
        flash('Invalid time format. Use HH:MM format', 'error')
    except Exception as e:
        db.session.rollback()
        flash('Failed to create time slot. Please try again.', 'error')
    
    return redirect(url_for('admin.tatkal_timeslots'))

@admin_bp.route('/tatkal-timeslots/toggle/<int:slot_id>', methods=['POST'])
@admin_required
def toggle_tatkal_timeslot(slot_id):
    """Enable/disable Tatkal time slot"""
    time_slot = TatkalTimeSlot.query.get_or_404(slot_id)
    
    time_slot.active = not time_slot.active
    db.session.commit()
    
    status = 'enabled' if time_slot.active else 'disabled'
    flash(f'Time slot "{time_slot.name}" {status}', 'success')
    
    return redirect(url_for('admin.tatkal_timeslots'))

@admin_bp.route('/tatkal-timeslots/delete/<int:slot_id>', methods=['POST'])
@admin_required
def delete_tatkal_timeslot(slot_id):
    """Delete Tatkal time slot"""
    time_slot = TatkalTimeSlot.query.get_or_404(slot_id)
    
    slot_name = time_slot.name
    db.session.delete(time_slot)
    db.session.commit()
    
    flash(f'Time slot "{slot_name}" deleted successfully', 'success')
    return redirect(url_for('admin.tatkal_timeslots'))

@admin_bp.route('/tatkal-management')
@admin_required
def tatkal_management():
    """Tatkal booking management and monitoring"""
    # Get trains with tatkal bookings
    trains_with_tatkal = db.session.query(
        Train.id,
        Train.number,
        Train.name,
        Train.tatkal_seats,
        db.func.count(Booking.id).label('tatkal_bookings'),
        db.func.sum(Booking.total_amount).label('tatkal_revenue')
    ).join(Booking).filter(
        Booking.booking_type == 'tatkal'
    ).group_by(Train.id, Train.number, Train.name, Train.tatkal_seats).all()
    
    # Recent tatkal bookings
    recent_tatkal = Booking.query.filter_by(booking_type='tatkal').order_by(
        Booking.booking_date.desc()
    ).limit(20).all()
    
    return render_template('admin/tatkal_management.html',
                         trains_with_tatkal=trains_with_tatkal,
                         recent_tatkal=recent_tatkal)

@admin_bp.route('/route-management')
@admin_required
def route_management():
    """Train route and scheduling management"""
    trains = Train.query.all()
    stations = Station.query.filter_by(active=True).all()
    return render_template('admin/route_management.html', trains=trains, stations=stations)

@admin_bp.route('/route-management/<int:train_id>')
@admin_required
def view_train_route(train_id):
    """View and edit specific train route"""
    train = Train.query.get_or_404(train_id)
    routes = TrainRoute.query.filter_by(train_id=train_id).order_by(TrainRoute.sequence).all()
    stations = Station.query.filter_by(active=True).all()
    
    return render_template('admin/train_route_details.html',
                         train=train, routes=routes, stations=stations)

@admin_bp.route('/route-management/<int:train_id>/add-station', methods=['POST'])
@admin_required
def add_station_to_route(train_id):
    """Add station to train route"""
    train = Train.query.get_or_404(train_id)
    
    station_id = request.form.get('station_id', type=int)
    sequence = request.form.get('sequence', type=int)
    arrival_time = request.form.get('arrival_time')
    departure_time = request.form.get('departure_time')
    distance = request.form.get('distance', type=float)
    
    # Convert time strings to time objects
    arrival_time_obj = None
    departure_time_obj = None
    
    if arrival_time:
        arrival_time_obj = datetime.strptime(arrival_time, '%H:%M').time()
    if departure_time:
        departure_time_obj = datetime.strptime(departure_time, '%H:%M').time()
    
    route = TrainRoute(
        train_id=train_id,
        station_id=station_id,
        sequence=sequence,
        arrival_time=arrival_time_obj,
        departure_time=departure_time_obj,
        distance_from_start=distance
    )
    
    db.session.add(route)
    db.session.commit()
    
    flash('Station added to route successfully', 'success')
    return redirect(url_for('admin.view_train_route', train_id=train_id))

@admin_bp.route('/seat-allocation')
@admin_required
def seat_allocation():
    """Real-time seat allocation monitoring"""
    # Get date from request parameter or default to today
    date_param = request.args.get('date')
    try:
        if date_param:
            selected_date = datetime.strptime(date_param, '%Y-%m-%d').date()
        else:
            selected_date = datetime.utcnow().date()
    except ValueError:
        flash('Invalid date format', 'error')
        selected_date = datetime.utcnow().date()
    
    seat_allocation = db.session.query(
        Train.id,
        Train.number,
        Train.name,
        Train.total_seats,
        Train.tatkal_seats,
        db.func.coalesce(db.func.sum(
            db.case(
                (Booking.booking_type == 'general', Booking.passengers),
                else_=0
            )
        ), 0).label('general_booked'),
        db.func.coalesce(db.func.sum(
            db.case(
                (Booking.booking_type == 'tatkal', Booking.passengers),
                else_=0
            )
        ), 0).label('tatkal_booked')
    ).outerjoin(Booking, and_(
        Train.id == Booking.train_id,
        Booking.journey_date == selected_date,
        Booking.status == 'confirmed'
    )).group_by(Train.id, Train.number, Train.name, Train.total_seats, Train.tatkal_seats).all()
    
    return render_template('admin/seat_allocation.html',
                         seat_allocation=seat_allocation,
                         selected_date=selected_date)

@admin_bp.route('/waitlist-management')
@admin_required
def waitlist_management():
    """Waitlist monitoring and management"""
    from .models import Waitlist
    
    # Get current waitlist statistics
    waitlist_stats = db.session.query(
        Train.number,
        Train.name,
        db.func.count(Booking.id).label('waitlist_count'),
        db.func.min(Waitlist.position).label('min_position'),
        db.func.max(Waitlist.position).label('max_position')
    ).select_from(Train).join(
        Booking, Train.id == Booking.train_id
    ).join(
        Waitlist, Booking.id == Waitlist.booking_id
    ).filter(
        Booking.status == 'waitlisted'
    ).group_by(Train.id, Train.number, Train.name).all()
    
    # Recent waitlist activities
    recent_waitlist = Booking.query.filter_by(status='waitlisted').order_by(
        Booking.booking_date.desc()
    ).limit(50).all()
    
    return render_template('admin/waitlist_management.html',
                         waitlist_stats=waitlist_stats,
                         recent_waitlist=recent_waitlist)

@admin_bp.route('/fare-management')
@admin_required
def fare_management():
    """Fare structure and pricing management"""
    trains = Train.query.all()
    return render_template('admin/fare_management.html', trains=trains)

@admin_bp.route('/fare-management/<int:train_id>', methods=['POST'])
@admin_required
def update_fare(train_id):
    """Update train fare structure"""
    train = Train.query.get_or_404(train_id)
    
    fare_per_km = request.form.get('fare_per_km', type=float)
    tatkal_fare_per_km = request.form.get('tatkal_fare_per_km', type=float)
    
    train.fare_per_km = fare_per_km
    train.tatkal_fare_per_km = tatkal_fare_per_km
    
    db.session.commit()
    flash(f'Fare updated for train {train.number}', 'success')
    return redirect(url_for('admin.fare_management'))

@admin_bp.route('/emergency-quota')
@admin_required
def emergency_quota():
    """Emergency quota management"""
    trains = Train.query.all()
    return render_template('admin/emergency_quota.html', trains=trains)

@admin_bp.route('/emergency-quota/<int:train_id>/release', methods=['POST'])
@admin_required
def release_emergency_seats(train_id):
    """Release emergency quota seats"""
    train = Train.query.get_or_404(train_id)
    seats_to_release = request.form.get('seats', type=int)
    
    if seats_to_release and seats_to_release > 0:
        # Add seats to available quota
        train.available_seats += seats_to_release
        db.session.commit()
        
        flash(f'Released {seats_to_release} emergency seats for train {train.number}', 'success')
    
    return redirect(url_for('admin.emergency_quota'))

@admin_bp.route('/booking-reports')
@admin_required
def booking_reports():
    """Comprehensive booking reports and analytics"""
    # Date range from request or default to last 30 days
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=30)
    
    date_filter = request.args.get('date_range', '30')
    if date_filter == '7':
        start_date = end_date - timedelta(days=7)
    elif date_filter == '90':
        start_date = end_date - timedelta(days=90)
    
    # Booking statistics
    booking_stats_raw = db.session.query(
        db.func.date(Booking.booking_date).label('date'),
        Booking.status,
        Booking.booking_type,
        db.func.count(Booking.id).label('count'),
        db.func.sum(Booking.total_amount).label('revenue')
    ).filter(
        Booking.booking_date >= start_date,
        Booking.booking_date <= end_date
    ).group_by(
        db.func.date(Booking.booking_date),
        Booking.status,
        Booking.booking_type
    ).all()
    
    # Convert to JSON-serializable format
    booking_stats = []
    for row in booking_stats_raw:
        booking_stats.append({
            'date': row.date.strftime('%Y-%m-%d') if row.date else None,
            'status': row.status,
            'booking_type': row.booking_type,
            'count': row.count,
            'revenue': float(row.revenue) if row.revenue else 0.0
        })
    
    # Popular routes
    from sqlalchemy.orm import aliased
    Station2 = aliased(Station)
    popular_routes_raw = db.session.query(
        Station.name.label('from_station'),
        Station2.name.label('to_station'),
        db.func.count(Booking.id).label('bookings')
    ).select_from(Booking).join(
        Station, Booking.from_station_id == Station.id
    ).join(
        Station2, Booking.to_station_id == Station2.id
    ).filter(
        Booking.booking_date >= start_date
    ).group_by(
        Station.name, Station2.name
    ).order_by(db.func.count(Booking.id).desc()).limit(10).all()
    
    # Convert to JSON-serializable format
    popular_routes = []
    for row in popular_routes_raw:
        popular_routes.append({
            'from_station': row.from_station,
            'to_station': row.to_station,
            'bookings': row.bookings
        })
    
    return render_template('admin/booking_reports.html',
                         booking_stats=booking_stats,
                         popular_routes=popular_routes,
                         date_filter=date_filter,
                         start_date=start_date,
                         end_date=end_date)

# Tatkal Override Management

@admin_bp.route('/tatkal-override')
@admin_required
def tatkal_override():
    """Manage Tatkal booking override settings"""
    active_override = TatkalOverride.get_active_override()
    override_history = TatkalOverride.query.order_by(TatkalOverride.enabled_at.desc()).limit(10).all()
    
    return render_template('admin/tatkal_override.html', 
                         active_override=active_override,
                         override_history=override_history)

@admin_bp.route('/tatkal-override/enable', methods=['POST'])
@admin_required
def enable_tatkal_override():
    """Enable Tatkal booking override"""
    coach_classes = request.form.get('coach_classes', '').strip()
    override_message = request.form.get('override_message', 'Tatkal booking enabled by admin').strip()
    valid_hours = request.form.get('valid_hours', type=int)
    
    # Disable any existing active override first
    existing_overrides = TatkalOverride.query.filter_by(is_enabled=True).all()
    for override in existing_overrides:
        override.is_enabled = False
    
    # Create new override
    valid_until = None
    if valid_hours and valid_hours > 0:
        valid_until = datetime.utcnow() + timedelta(hours=valid_hours)
    
    new_override = TatkalOverride(
        is_enabled=True,
        enabled_by=current_user.id,
        override_message=override_message,
        coach_classes=coach_classes if coach_classes else None,
        valid_until=valid_until
    )
    
    db.session.add(new_override)
    db.session.commit()
    
    duration_msg = f" for {valid_hours} hours" if valid_hours else " (no expiry)"
    classes_msg = f" for classes: {coach_classes}" if coach_classes else " for all coach classes"
    flash(f'Tatkal booking override enabled{duration_msg}{classes_msg}', 'success')
    
    return redirect(url_for('admin.tatkal_override'))

@admin_bp.route('/tatkal-override/disable', methods=['POST'])
@admin_required
def disable_tatkal_override():
    """Disable Tatkal booking override"""
    active_override = TatkalOverride.get_active_override()
    if active_override:
        active_override.is_enabled = False
        db.session.commit()
        flash('Tatkal booking override disabled', 'success')
    else:
        flash('No active override to disable', 'info')
    
    return redirect(url_for('admin.tatkal_override'))

@admin_bp.route('/tatkal-override/status')
@admin_required
def tatkal_override_status():
    """Get current Tatkal override status (AJAX endpoint)"""
    active_override = TatkalOverride.get_active_override()
    
    if active_override and active_override.is_valid():
        return jsonify({
            'active': True,
            'message': active_override.override_message,
            'enabled_by': active_override.admin_user.username,
            'enabled_at': active_override.enabled_at.isoformat(),
            'coach_classes': active_override.coach_classes,
            'valid_until': active_override.valid_until.isoformat() if active_override.valid_until else None
        })
    else:
        return jsonify({
            'active': False
        })

@admin_bp.route('/waitlist-details')
@admin_required
def waitlist_details():
    """Detailed waitlist management with search functionality"""
    from .models import Waitlist
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    
    # Base query for waitlisted bookings
    query = Booking.query.filter_by(status='waitlisted')
    
    # Add search functionality
    if search:
        query = query.join(User).join(Train).filter(
            db.or_(
                Booking.pnr.ilike(f'%{search}%'),
                User.username.ilike(f'%{search}%'),
                Train.number.ilike(f'%{search}%'),
                Train.name.ilike(f'%{search}%')
            )
        )
    
    # Get paginated results
    waitlist_bookings = query.order_by(Booking.booking_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Calculate statistics
    total_waitlisted = Booking.query.filter_by(status='waitlisted').count()
    confirmed_today = Booking.query.filter(
        Booking.status == 'confirmed',
        db.func.date(Booking.booking_date) == date.today()
    ).count()
    
    trains_with_waitlist = db.session.query(Train.id).join(Booking).filter(
        Booking.status == 'waitlisted'
    ).distinct().count()
    
    # Calculate average confirmation rate (simplified)
    total_bookings = Booking.query.count()
    confirmed_bookings = Booking.query.filter_by(status='confirmed').count()
    avg_confirmation_rate = int((confirmed_bookings / total_bookings * 100)) if total_bookings > 0 else 0
    
    return render_template('admin/waitlist_details.html',
                         waitlist_bookings=waitlist_bookings,
                         search=search,
                         total_waitlisted=total_waitlisted,
                         confirmed_today=confirmed_today,
                         trains_with_waitlist=trains_with_waitlist,
                         avg_confirmation_rate=avg_confirmation_rate)

@admin_bp.route('/waitlist/<int:booking_id>/confirm', methods=['POST'])
@admin_required
def confirm_waitlist(booking_id):
    """Confirm a waitlisted booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.status != 'waitlisted':
        flash('This booking is not in waitlist status', 'error')
        return redirect(url_for('admin.waitlist_details'))
    
    # Check if seats are available
    train = booking.train
    if train.available_seats >= booking.passengers:
        booking.status = 'confirmed'
        train.available_seats -= booking.passengers
        
        # Remove from waitlist
        waitlist_entry = Waitlist.query.filter_by(booking_id=booking.id).first()
        if waitlist_entry:
            db.session.delete(waitlist_entry)
        
        db.session.commit()
        flash(f'Booking {booking.pnr} confirmed successfully', 'success')
    else:
        flash('Insufficient seats available for confirmation', 'error')
    
    return redirect(url_for('admin.waitlist_details'))

@admin_bp.route('/waitlist/<int:booking_id>/cancel', methods=['POST'])
@admin_required
def cancel_waitlist(booking_id):
    """Cancel a waitlisted booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.status != 'waitlisted':
        flash('This booking is not in waitlist status', 'error')
        return redirect(url_for('admin.waitlist_details'))
    
    booking.status = 'cancelled'
    
    # Remove from waitlist
    waitlist_entry = Waitlist.query.filter_by(booking_id=booking.id).first()
    if waitlist_entry:
        db.session.delete(waitlist_entry)
    
    db.session.commit()
    flash(f'Booking {booking.pnr} cancelled successfully', 'success')
    
    return redirect(url_for('admin.waitlist_details'))
