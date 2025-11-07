from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from .models import User
from .database import db
from .validators import FormValidator
import secrets
from datetime import datetime, timedelta
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login with comprehensive validation"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = FormValidator.sanitize_input(request.form.get('username', ''))
        password = request.form.get('password', '')
        
        # COMPREHENSIVE LOGIN VALIDATION
        if not username or not password:
            flash('Both username and password are required', 'error')
            return render_template('login.html')
        
        # Validate username format
        is_valid, error_msg = FormValidator.validate_username(username)
        if not is_valid:
            flash('Invalid username or password', 'error')  # Generic message for security
            return render_template('login.html')
        
        # Validate password length (basic check without revealing requirements)
        if len(password) < 3 or len(password) > 128:
            flash('Invalid username or password', 'error')
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
    """User registration with comprehensive validation"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = FormValidator.sanitize_input(request.form.get('username', ''))
        email = FormValidator.sanitize_input(request.form.get('email', ''))
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        phone = FormValidator.sanitize_input(request.form.get('phone', ''))
        
        # COMPREHENSIVE REGISTRATION VALIDATION
        
        # 1. Check all required fields
        is_valid, error_msg = FormValidator.validate_required_fields(
            {'username': username, 'email': email, 'password': password, 'confirm_password': confirm_password},
            ['username', 'email', 'password', 'confirm_password']
        )
        if not is_valid:
            flash(error_msg or 'Please fill in all required fields', 'error')
            return render_template('register.html')
        
        # 2. Validate username
        is_valid, error_msg = FormValidator.validate_username(username)
        if not is_valid:
            flash(error_msg or 'Invalid username', 'error')
            return render_template('register.html')
        
        # 3. Validate email
        is_valid, error_msg, normalized_email = FormValidator.validate_email_address(email)
        if not is_valid:
            flash(error_msg or 'Invalid email address', 'error')
            return render_template('register.html')
        
        # 4. Validate password
        is_valid, error_msg = FormValidator.validate_password(password, confirm_password)
        if not is_valid:
            flash(error_msg or 'Invalid password', 'error')
            return render_template('register.html')
        
        # 5. Validate phone (optional)
        if phone:
            is_valid, error_msg = FormValidator.validate_phone_number(phone, required=False)
            if not is_valid:
                flash(error_msg or 'Invalid phone number', 'error')
                return render_template('register.html')
        
        # 6. Check for existing username
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different username.', 'error')
            return render_template('register.html')
        
        # 7. Check for existing email
        if User.query.filter_by(email=normalized_email or email).first():
            flash('Email address already registered. Please use a different email or login.', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=normalized_email or email,
            password_hash=generate_password_hash(password),
            role='user'
        )
        
        # Add phone if User model has phone field (optional - comment out if not in model)
        # if hasattr(user, 'phone') and phone:
        #     user.phone = phone
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in with your credentials.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            return render_template('register.html')
    
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
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            
            # Store token with expiry (24 hours)
            from datetime import datetime, timedelta
            user.reset_token = reset_token
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=24)
            db.session.commit()
            
            # Send email with reset link
            from .email_service import email_service
            reset_url = url_for('auth.reset_password', token=reset_token, _external=True)
            
            if email_service.send_password_reset(user.email, user.username, reset_token, reset_url):
                flash(f'Password reset instructions have been sent to {email}.', 'info')
            else:
                # Fallback for demo purposes when email is not configured
                flash(f'Password reset instructions have been sent to {email}. '
                      f'For demo purposes, your reset link is: {reset_url}', 'info')
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
        
        if not password or len(password) < 8:
            flash('Password must be at least 8 characters with letters and numbers', 'error')
            return render_template('reset_password.html', token=token)
        
        # Enhanced password policy
        import re
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$', password):
            flash('Password must contain at least 8 characters including letters and numbers', 'error')
            return render_template('reset_password.html', token=token)
        
        user = User.query.filter_by(email=email, reset_token=token).first()
        
        # SECURITY FIX: Validate token expiry and authenticity
        if user and user.active and user.reset_token == token and user.reset_token_expiry:
            from datetime import datetime
            if datetime.utcnow() > user.reset_token_expiry:
                flash('Password reset link has expired. Please request a new one.', 'error')
                return render_template('reset_password.html', token=token)
            
            # Reset password and clear token
            user.password_hash = generate_password_hash(password)
            user.reset_token = None
            user.reset_token_expiry = None
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

@auth_bp.route('/edit_profile', methods=['POST'])
@login_required
def edit_profile():
    """Update user profile information"""
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    
    # Validate required fields
    if not username or not email:
        flash('Username and email are required', 'error')
        return redirect(url_for('auth.profile'))
    
    # Check for duplicate username (excluding current user)
    existing_user = User.query.filter(User.username == username, User.id != current_user.id).first()
    if existing_user:
        flash('Username already exists. Please choose a different one.', 'error')
        return redirect(url_for('auth.profile'))
    
    # Check for duplicate email (excluding current user)
    existing_email = User.query.filter(User.email == email, User.id != current_user.id).first()
    if existing_email:
        flash('Email already exists. Please use a different email address.', 'error')
        return redirect(url_for('auth.profile'))
    
    # Validate email format
    import re
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        flash('Please enter a valid email address', 'error')
        return redirect(url_for('auth.profile'))
    
    # Update user information
    current_user.username = username
    current_user.email = email
    
    # Add phone number if User model has phone field (optional)
    if hasattr(current_user, 'phone'):
        current_user.phone = phone
    
    try:
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating your profile. Please try again.', 'error')
    
    return redirect(url_for('auth.profile'))

@auth_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        flash('All password fields are required', 'error')
        return redirect(url_for('auth.profile'))
    
    # Type safety - ensure values are not None
    assert current_password is not None
    assert new_password is not None
    assert confirm_password is not None
    
    # Verify current password
    if not check_password_hash(current_user.password_hash, current_password):
        flash('Current password is incorrect', 'error')
        return redirect(url_for('auth.profile'))
    
    # Check if new passwords match
    if new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('auth.profile'))
    
    # Enhanced password policy
    import re
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$', new_password):
        flash('Password must contain at least 8 characters including letters and numbers', 'error')
        return redirect(url_for('auth.profile'))
    
    # Don't allow same password
    if check_password_hash(current_user.password_hash, new_password):
        flash('New password must be different from current password', 'error')
        return redirect(url_for('auth.profile'))
    
    # Update password
    current_user.password_hash = generate_password_hash(new_password)
    
    try:
        db.session.commit()
        flash('Password changed successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while changing your password. Please try again.', 'error')
    
    return redirect(url_for('auth.profile'))
