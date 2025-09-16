from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from functools import wraps
from .models import User, Train, Station, Booking, Payment, TrainRoute
from .app import db
from datetime import datetime, timedelta
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
    """Manage trains"""
    trains = Train.query.all()
    return render_template('admin/trains.html', trains=trains)

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
        flash('Please fill all fields', 'error')
        return redirect(url_for('admin.trains'))
    
    if Train.query.filter_by(number=number).first():
        flash('Train number already exists', 'error')
        return redirect(url_for('admin.trains'))
    
    # Validate Tatkal seats don't exceed total seats
    if tatkal_seats is not None and total_seats is not None and tatkal_seats > total_seats:
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
    """Manage stations"""
    stations = Station.query.all()
    return render_template('admin/stations.html', stations=stations)

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
    """Manage users (Super Admin only)"""
    users = User.query.all()
    return render_template('admin/users.html', users=users)

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
    
    bookings = query.order_by(Booking.booking_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/bookings.html', bookings=bookings,
                         status_filter=status_filter,
                         booking_type_filter=booking_type_filter)

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
