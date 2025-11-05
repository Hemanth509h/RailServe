from flask import Blueprint, request, jsonify
from models.database import db
from models.models import ComplaintManagement
from datetime import datetime
import random

bp = Blueprint('complaints', __name__, url_prefix='/api/complaints')

@bp.route('/', methods=['GET'])
def get_complaints():
    complaints = ComplaintManagement.query.all()
    return jsonify([{
        'id': c.id,
        'ticket_number': c.ticket_number,
        'user_id': c.user_id,
        'category': c.category,
        'subject': c.subject,
        'status': c.status,
        'priority': c.priority,
        'created_at': c.created_at.isoformat() if c.created_at else None
    } for c in complaints])

@bp.route('/<int:complaint_id>', methods=['GET'])
def get_complaint(complaint_id):
    complaint = ComplaintManagement.query.get_or_404(complaint_id)
    return jsonify({
        'id': complaint.id,
        'ticket_number': complaint.ticket_number,
        'user_id': complaint.user_id,
        'booking_id': complaint.booking_id,
        'category': complaint.category,
        'subject': complaint.subject,
        'description': complaint.description,
        'status': complaint.status,
        'priority': complaint.priority,
        'resolution': complaint.resolution
    })

@bp.route('/', methods=['POST'])
def create_complaint():
    data = request.json
    ticket_number = f"CMP{datetime.utcnow().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
    
    complaint = ComplaintManagement(
        ticket_number=ticket_number,
        user_id=data['user_id'],
        booking_id=data.get('booking_id'),
        category=data['category'],
        subcategory=data.get('subcategory'),
        priority=data.get('priority', 'medium'),
        subject=data['subject'],
        description=data['description'],
        status=data.get('status', 'open')
    )
    db.session.add(complaint)
    db.session.commit()
    return jsonify({'id': complaint.id, 'ticket_number': complaint.ticket_number}), 201

@bp.route('/<int:complaint_id>', methods=['PUT'])
def update_complaint(complaint_id):
    complaint = ComplaintManagement.query.get_or_404(complaint_id)
    data = request.json
    
    for field in ['status', 'priority', 'resolution', 'assigned_to']:
        if field in data:
            setattr(complaint, field, data[field])
    
    if 'status' in data and data['status'] == 'resolved':
        complaint.resolved_at = datetime.utcnow()
    
    complaint.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Complaint updated successfully'})
