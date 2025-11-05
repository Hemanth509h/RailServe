from flask import Blueprint, request, jsonify
from models.database import db
from models.models import Station

bp = Blueprint('stations', __name__, url_prefix='/api/stations')

@bp.route('/', methods=['GET'])
def get_stations():
    stations = Station.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'code': s.code,
        'city': s.city,
        'state': s.state,
        'active': s.active
    } for s in stations])

@bp.route('/<int:station_id>', methods=['GET'])
def get_station(station_id):
    station = Station.query.get_or_404(station_id)
    return jsonify({
        'id': station.id,
        'name': station.name,
        'code': station.code,
        'city': station.city,
        'state': station.state,
        'active': station.active
    })

@bp.route('/code/<code>', methods=['GET'])
def get_station_by_code(code):
    station = Station.query.filter_by(code=code).first()
    if not station:
        return jsonify({'error': 'Station not found'}), 404
    return jsonify({
        'id': station.id,
        'name': station.name,
        'code': station.code,
        'city': station.city,
        'state': station.state,
        'active': station.active
    })

@bp.route('/', methods=['POST'])
def create_station():
    data = request.json
    station = Station(
        name=data['name'],
        code=data['code'],
        city=data['city'],
        state=data['state'],
        active=data.get('active', True)
    )
    db.session.add(station)
    db.session.commit()
    return jsonify({'id': station.id}), 201

@bp.route('/<int:station_id>', methods=['PUT'])
def update_station(station_id):
    station = Station.query.get_or_404(station_id)
    data = request.json
    
    if 'name' in data:
        station.name = data['name']
    if 'code' in data:
        station.code = data['code']
    if 'city' in data:
        station.city = data['city']
    if 'state' in data:
        station.state = data['state']
    if 'active' in data:
        station.active = data['active']
    
    db.session.commit()
    return jsonify({'message': 'Station updated successfully'})

@bp.route('/<int:station_id>', methods=['DELETE'])
def delete_station(station_id):
    station = Station.query.get_or_404(station_id)
    db.session.delete(station)
    db.session.commit()
    return jsonify({'message': 'Station deleted successfully'})
