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
    """Admin dashboard with analytics"""
    total_users = User.query.count()
    total_trains = Train.query.count()
    total_bookings = Booking.query.count()
    total_revenue = db.session.query(db.func.sum(Payment.amount)).filter_by(status='success').scalar() or 0
    
    # Recent bookings
    recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(10).all()
    
    # Booking status distribution
    booking_stats = db.session.query(
        Booking.status, 
        db.func.count(Booking.id)
    ).group_by(Booking.status).all()
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_trains=total_trains,
                         total_bookings=total_bookings,
                         total_revenue=total_revenue,
                         recent_bookings=recent_bookings,
                         booking_stats=booking_stats)

@admin_bp.route('/trains')
@admin_required
def trains():
    """Manage trains"""
    trains = Train.query.all()
    return render_template('admin/trains.html', trains=trains)

@admin_bp.route('/trains/add', methods=['POST'])
@admin_required
def add_train():
    """Add new train"""
    number = request.form.get('number')
    name = request.form.get('name')
    total_seats = request.form.get('total_seats', type=int)
    fare_per_km = request.form.get('fare_per_km', type=float)
    
    if not all([number, name, total_seats, fare_per_km]):
        flash('Please fill all fields', 'error')
        return redirect(url_for('admin.trains'))
    
    if Train.query.filter_by(number=number).first():
        flash('Train number already exists', 'error')
        return redirect(url_for('admin.trains'))
    
    train = Train(
        number=number,
        name=name,
        total_seats=total_seats,
        available_seats=total_seats,
        fare_per_km=fare_per_km
    )
    
    db.session.add(train)
    db.session.commit()
    
    flash('Train added successfully', 'success')
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
    """Analytics dashboard"""
    # Revenue data for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
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
    
    # Booking trends
    booking_trends = db.session.query(
        db.func.date(Booking.booking_date),
        db.func.count(Booking.id)
    ).filter(Booking.booking_date >= thirty_days_ago).group_by(db.func.date(Booking.booking_date)).all()
    
    return render_template('admin/analytics.html',
                         daily_revenue=daily_revenue,
                         popular_trains=popular_trains,
                         booking_trends=booking_trends)

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
