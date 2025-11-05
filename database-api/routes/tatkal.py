from flask import Blueprint, request, jsonify
from models.database import db
from models.models import TatkalTimeSlot, TatkalOverride
from datetime import datetime

bp = Blueprint('tatkal', __name__, url_prefix='/api/tatkal')

@bp.route('/timeslots', methods=['GET'])
def get_timeslots():
    timeslots = TatkalTimeSlot.query.filter_by(active=True).all()
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'coach_classes': t.coach_classes,
        'open_time': t.open_time.isoformat() if t.open_time else None,
        'close_time': t.close_time.isoformat() if t.close_time else None,
        'days_before_journey': t.days_before_journey,
        'active': t.active
    } for t in timeslots])

@bp.route('/timeslots', methods=['POST'])
def create_timeslot():
    data = request.json
    timeslot = TatkalTimeSlot(
        name=data['name'],
        coach_classes=data['coach_classes'],
        open_time=data['open_time'],
        close_time=data.get('close_time'),
        days_before_journey=data.get('days_before_journey', 1),
        created_by=data.get('created_by'),
        active=data.get('active', True)
    )
    db.session.add(timeslot)
    db.session.commit()
    return jsonify({'id': timeslot.id}), 201

@bp.route('/override', methods=['GET'])
def get_override():
    override = TatkalOverride.query.filter_by(is_enabled=True).first()
    if not override:
        return jsonify({'is_enabled': False})
    return jsonify({
        'id': override.id,
        'is_enabled': override.is_enabled,
        'override_message': override.override_message,
        'coach_classes': override.coach_classes,
        'train_ids': override.train_ids
    })

@bp.route('/override', methods=['POST'])
def create_override():
    data = request.json
    override = TatkalOverride(
        is_enabled=data.get('is_enabled', True),
        enabled_by=data['enabled_by'],
        override_message=data.get('override_message', 'Tatkal booking enabled by admin'),
        coach_classes=data.get('coach_classes'),
        train_ids=data.get('train_ids'),
        valid_until=datetime.fromisoformat(data['valid_until']) if data.get('valid_until') else None
    )
    db.session.add(override)
    db.session.commit()
    return jsonify({'id': override.id}), 201
