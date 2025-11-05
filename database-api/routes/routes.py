from flask import Blueprint, request, jsonify
from models.database import db
from models.models import TrainRoute, Station

bp = Blueprint('routes', __name__, url_prefix='/api/routes')

@bp.route('/train/<int:train_id>', methods=['GET'])
def get_train_routes(train_id):
    routes = TrainRoute.query.filter_by(train_id=train_id).order_by(TrainRoute.sequence).all()
    return jsonify([{
        'id': r.id,
        'train_id': r.train_id,
        'station_id': r.station_id,
        'sequence': r.sequence,
        'arrival_time': r.arrival_time.isoformat() if r.arrival_time else None,
        'departure_time': r.departure_time.isoformat() if r.departure_time else None,
        'distance_from_start': r.distance_from_start,
        'station_name': r.station.name if r.station else None,
        'station_code': r.station.code if r.station else None
    } for r in routes])

@bp.route('/', methods=['POST'])
def create_route():
    data = request.json
    route = TrainRoute(
        train_id=data['train_id'],
        station_id=data['station_id'],
        sequence=data['sequence'],
        arrival_time=data.get('arrival_time'),
        departure_time=data.get('departure_time'),
        distance_from_start=data['distance_from_start']
    )
    db.session.add(route)
    db.session.commit()
    return jsonify({'id': route.id}), 201

@bp.route('/<int:route_id>', methods=['PUT'])
def update_route(route_id):
    route = TrainRoute.query.get_or_404(route_id)
    data = request.json
    
    for field in ['station_id', 'sequence', 'arrival_time', 'departure_time', 'distance_from_start']:
        if field in data:
            setattr(route, field, data[field])
    
    db.session.commit()
    return jsonify({'message': 'Route updated successfully'})

@bp.route('/<int:route_id>', methods=['DELETE'])
def delete_route(route_id):
    route = TrainRoute.query.get_or_404(route_id)
    db.session.delete(route)
    db.session.commit()
    return jsonify({'message': 'Route deleted successfully'})
