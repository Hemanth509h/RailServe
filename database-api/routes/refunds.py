from flask import Blueprint, request, jsonify
from models.database import db
from models.models import RefundRequest
from datetime import datetime

bp = Blueprint('refunds', __name__, url_prefix='/api/refunds')

@bp.route('/', methods=['GET'])
def get_refunds():
    refunds = RefundRequest.query.all()
    return jsonify([{
        'id': r.id,
        'booking_id': r.booking_id,
        'user_id': r.user_id,
        'tdr_number': r.tdr_number,
        'amount_paid': r.amount_paid,
        'refund_amount': r.refund_amount,
        'status': r.status,
        'filed_at': r.filed_at.isoformat() if r.filed_at else None
    } for r in refunds])

@bp.route('/<int:refund_id>', methods=['GET'])
def get_refund(refund_id):
    refund = RefundRequest.query.get_or_404(refund_id)
    return jsonify({
        'id': refund.id,
        'booking_id': refund.booking_id,
        'user_id': refund.user_id,
        'reason': refund.reason,
        'amount_paid': refund.amount_paid,
        'refund_amount': refund.refund_amount,
        'cancellation_charges': refund.cancellation_charges,
        'tdr_number': refund.tdr_number,
        'status': refund.status
    })

@bp.route('/', methods=['POST'])
def create_refund():
    data = request.json
    refund = RefundRequest(
        booking_id=data['booking_id'],
        user_id=data['user_id'],
        reason=data['reason'],
        amount_paid=data['amount_paid'],
        refund_amount=data['refund_amount'],
        cancellation_charges=data.get('cancellation_charges', 0.0),
        status=data.get('status', 'pending')
    )
    db.session.add(refund)
    db.session.commit()
    return jsonify({'id': refund.id, 'tdr_number': refund.tdr_number}), 201

@bp.route('/<int:refund_id>', methods=['PUT'])
def update_refund(refund_id):
    refund = RefundRequest.query.get_or_404(refund_id)
    data = request.json
    
    if 'status' in data:
        refund.status = data['status']
        if data['status'] in ['approved', 'completed']:
            refund.processed_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify({'message': 'Refund updated successfully'})
