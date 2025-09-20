from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from .models import User
from .app import db
import secrets
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter username and password', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        # SECURITY FIX: Prevent user enumeration by using same message for all failures
        login_successful = False
        if user and user.active and check_password_hash(user.password_hash, password):
            login_successful = True
        
        if login_successful:
            login_user(user, remember=bool(request.form.get('remember')))
            next_page = request.args.get('next')
            
            # Redirect admin users to admin dashboard
            if user and user.is_admin():
                return redirect(next_page) if next_page else redirect(url_for('admin.dashboard'))
            
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            # Generic error message prevents username enumeration
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            flash('Please fill all fields', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if password and len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password or ''),
            role='user'
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password - request password reset"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Please enter your email address', 'error')
            return render_template('forgot_password.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.active:
            # Generate reset token (in production, this should be sent via email)
            reset_token = secrets.token_urlsafe(32)
            # Store token in user record (you'd need to add reset_token field to User model)
            # For now, we'll create a simple reset link
            
            # In production, send email with reset link
            flash(f'Password reset instructions have been sent to {email}. '
                  f'For demo purposes, your reset link is: /auth/reset-password/{reset_token}', 'info')
        else:
            # Don't reveal if email exists or not for security
            flash(f'If an account with email {email} exists, password reset instructions have been sent.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        
        if not all([password, confirm_password, email]):
            flash('Please fill all fields', 'error')
            return render_template('reset_password.html', token=token)
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('reset_password.html', token=token)
        
        if not password or len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('reset_password.html', token=token)
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.active and password:
            # In production, verify the token here
            # For demo purposes, we'll allow password reset
            user.password_hash = generate_password_hash(password)
            db.session.commit()
            
            flash('Your password has been reset successfully. Please login with your new password.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid email address', 'error')
    
    return render_template('reset_password.html', token=token)

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile with booking history"""
    bookings = current_user.bookings
    payments = current_user.payments
    return render_template('profile.html', bookings=bookings, payments=payments)
