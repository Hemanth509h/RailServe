from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Booking, Payment
from .app import db
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import random
import string

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/pay/<int:booking_id>')
@login_required
def pay(booking_id):
    """Payment page"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user owns the booking
    if booking.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Check if payment already exists
    if booking.payment and booking.payment.status == 'success':
        flash('Payment already completed', 'info')
        return redirect(url_for('auth.profile'))
    
    return render_template('payment.html', booking=booking)

@payment_bp.route('/process/<int:booking_id>', methods=['POST'])
@login_required
def process_payment(booking_id):
    """Process payment with idempotency protection"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user owns the booking
    if booking.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # CRITICAL FIX: Check for existing successful payment (idempotency)
    if booking.payment and booking.payment.status == 'success':
        flash('Payment already completed', 'info')
        return redirect(url_for('payment.success', booking_id=booking.id))
    
    payment_method = request.form.get('payment_method')
    
    if not payment_method:
        flash('Please select a payment method', 'error')
        return redirect(url_for('payment.pay', booking_id=booking_id))
    
    try:
        # Double-check for existing payment (race condition protection)
        existing_payment = Payment.query.filter_by(booking_id=booking.id, status='success').first()
        if existing_payment:
            flash('Payment already completed', 'info')
            return redirect(url_for('payment.success', booking_id=booking.id))
        
        # Generate transaction ID
        transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        
        # Create payment record with amount verification
        payment = Payment(
            booking_id=booking.id,
            user_id=current_user.id,
            amount=booking.total_amount,  # Verified against booking amount
            payment_method=payment_method,
            transaction_id=transaction_id,
            status='success',  # Simulating successful payment
            completed_at=datetime.utcnow()
        )
        
        db.session.add(payment)
        
        # Update booking status based on current state
        if booking.status == 'waitlisted':
            # Keep as waitlisted but mark payment as completed
            pass
        elif booking.status == 'pending_payment':
            booking.status = 'confirmed'
        
        # Commit all changes
        db.session.commit()
        
        flash(f'Payment successful! Transaction ID: {transaction_id}', 'success')
        return redirect(url_for('payment.success', booking_id=booking.id))
        
    except IntegrityError as e:
        # Handle duplicate payment constraint violation 
        db.session.rollback()
        if 'uq_booking_payment_success' in str(e):
            # Payment already exists for this booking
            flash('Payment already completed for this booking', 'info')
            return redirect(url_for('payment.success', booking_id=booking_id))
        else:
            flash('Payment processing failed due to data conflict. Please try again.', 'error')
            return redirect(url_for('payment.pay', booking_id=booking_id))
    except Exception as e:
        db.session.rollback()
        flash('Payment processing failed. Please try again.', 'error')
        return redirect(url_for('payment.pay', booking_id=booking_id))

@payment_bp.route('/success/<int:booking_id>')
@login_required
def success(booking_id):
    """Payment success page"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user owns the booking
    if booking.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    return render_template('payment_success.html', booking=booking)

@payment_bp.route('/failure/<int:booking_id>')
@login_required
def failure(booking_id):
    """Payment failure page"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user owns the booking
    if booking.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    return render_template('payment_failure.html', booking=booking)
