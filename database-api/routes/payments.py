from flask import Blueprint, request, jsonify
from models.database import db
from models.models import Payment
from datetime import datetime

bp = Blueprint('payments', __name__, url_prefix='/api/payments')

@bp.route('/', methods=['GET'])
def get_payments():
    payments = Payment.query.all()
    return jsonify([{
        'id': p.id,
        'booking_id': p.booking_id,
        'user_id': p.user_id,
        'amount': p.amount,
        'payment_method': p.payment_method,
        'transaction_id': p.transaction_id,
        'status': p.status,
        'created_at': p.created_at.isoformat() if p.created_at else None
    } for p in payments])

@bp.route('/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    return jsonify({
        'id': payment.id,
        'booking_id': payment.booking_id,
        'user_id': payment.user_id,
        'amount': payment.amount,
        'payment_method': payment.payment_method,
        'transaction_id': payment.transaction_id,
        'status': payment.status,
        'created_at': payment.created_at.isoformat() if payment.created_at else None,
        'completed_at': payment.completed_at.isoformat() if payment.completed_at else None
    })

@bp.route('/booking/<int:booking_id>', methods=['GET'])
def get_payment_by_booking(booking_id):
    payment = Payment.query.filter_by(booking_id=booking_id).first()
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    return jsonify({
        'id': payment.id,
        'booking_id': payment.booking_id,
        'amount': payment.amount,
        'status': payment.status
    })

@bp.route('/', methods=['POST'])
def create_payment():
    data = request.json
    payment = Payment(
        booking_id=data['booking_id'],
        user_id=data['user_id'],
        amount=data['amount'],
        payment_method=data['payment_method'],
        transaction_id=data.get('transaction_id'),
        status=data.get('status', 'pending')
    )
    db.session.add(payment)
    db.session.commit()
    return jsonify({'id': payment.id}), 201

@bp.route('/<int:payment_id>', methods=['PUT'])
def update_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    data = request.json
    
    if 'status' in data:
        payment.status = data['status']
        if data['status'] == 'success':
            payment.completed_at = datetime.utcnow()
    if 'transaction_id' in data:
        payment.transaction_id = data['transaction_id']
    
    db.session.commit()
    return jsonify({'message': 'Payment updated successfully'})
