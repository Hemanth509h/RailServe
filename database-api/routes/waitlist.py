from flask import Blueprint, request, jsonify
from models.database import db
from models.models import Waitlist
from datetime import datetime

bp = Blueprint('waitlist', __name__, url_prefix='/api/waitlist')

@bp.route('/', methods=['GET'])
def get_waitlists():
    waitlists = Waitlist.query.all()
    return jsonify([{
        'id': w.id,
        'booking_id': w.booking_id,
        'train_id': w.train_id,
        'journey_date': w.journey_date.isoformat() if w.journey_date else None,
        'position': w.position,
        'waitlist_type': w.waitlist_type
    } for w in waitlists])

@bp.route('/booking/<int:booking_id>', methods=['GET'])
def get_waitlist_by_booking(booking_id):
    waitlist = Waitlist.query.filter_by(booking_id=booking_id).first()
    if not waitlist:
        return jsonify({'error': 'Waitlist entry not found'}), 404
    return jsonify({
        'id': waitlist.id,
        'booking_id': waitlist.booking_id,
        'train_id': waitlist.train_id,
        'position': waitlist.position,
        'waitlist_type': waitlist.waitlist_type
    })

@bp.route('/', methods=['POST'])
def create_waitlist():
    data = request.json
    waitlist = Waitlist(
        booking_id=data['booking_id'],
        train_id=data['train_id'],
        journey_date=datetime.fromisoformat(data['journey_date']).date() if isinstance(data['journey_date'], str) else data['journey_date'],
        position=data['position'],
        waitlist_type=data.get('waitlist_type', 'GNWL')
    )
    db.session.add(waitlist)
    db.session.commit()
    return jsonify({'id': waitlist.id}), 201

@bp.route('/<int:waitlist_id>', methods=['PUT'])
def update_waitlist(waitlist_id):
    waitlist = Waitlist.query.get_or_404(waitlist_id)
    data = request.json
    
    if 'position' in data:
        waitlist.position = data['position']
    
    db.session.commit()
    return jsonify({'message': 'Waitlist updated successfully'})

@bp.route('/<int:waitlist_id>', methods=['DELETE'])
def delete_waitlist(waitlist_id):
    waitlist = Waitlist.query.get_or_404(waitlist_id)
    db.session.delete(waitlist)
    db.session.commit()
    return jsonify({'message': 'Waitlist entry deleted successfully'})
