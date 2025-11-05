from flask import Blueprint, request, jsonify
from models.database import db
from models.models import Train

bp = Blueprint('trains', __name__, url_prefix='/api/trains')

@bp.route('/', methods=['GET'])
def get_trains():
    trains = Train.query.all()
    return jsonify([{
        'id': t.id,
        'number': t.number,
        'name': t.name,
        'total_seats': t.total_seats,
        'available_seats': t.available_seats,
        'fare_per_km': t.fare_per_km,
        'tatkal_seats': t.tatkal_seats,
        'tatkal_fare_per_km': t.tatkal_fare_per_km,
        'active': t.active
    } for t in trains])

@bp.route('/<int:train_id>', methods=['GET'])
def get_train(train_id):
    train = Train.query.get_or_404(train_id)
    return jsonify({
        'id': train.id,
        'number': train.number,
        'name': train.name,
        'total_seats': train.total_seats,
        'available_seats': train.available_seats,
        'fare_per_km': train.fare_per_km,
        'tatkal_seats': train.tatkal_seats,
        'tatkal_fare_per_km': train.tatkal_fare_per_km,
        'active': train.active
    })

@bp.route('/number/<number>', methods=['GET'])
def get_train_by_number(number):
    train = Train.query.filter_by(number=number).first()
    if not train:
        return jsonify({'error': 'Train not found'}), 404
    return jsonify({
        'id': train.id,
        'number': train.number,
        'name': train.name,
        'total_seats': train.total_seats,
        'available_seats': train.available_seats,
        'fare_per_km': train.fare_per_km
    })

@bp.route('/', methods=['POST'])
def create_train():
    data = request.json
    train = Train(
        number=data['number'],
        name=data['name'],
        total_seats=data['total_seats'],
        available_seats=data['available_seats'],
        fare_per_km=data['fare_per_km'],
        tatkal_seats=data.get('tatkal_seats', 0),
        tatkal_fare_per_km=data.get('tatkal_fare_per_km'),
        active=data.get('active', True)
    )
    db.session.add(train)
    db.session.commit()
    return jsonify({'id': train.id}), 201

@bp.route('/<int:train_id>', methods='PUT'])
def update_train(train_id):
    train = Train.query.get_or_404(train_id)
    data = request.json
    
    for field in ['name', 'total_seats', 'available_seats', 'fare_per_km', 'tatkal_seats', 'tatkal_fare_per_km', 'active']:
        if field in data:
            setattr(train, field, data[field])
    
    db.session.commit()
    return jsonify({'message': 'Train updated successfully'})

@bp.route('/<int:train_id>', methods=['DELETE'])
def delete_train(train_id):
    train = Train.query.get_or_404(train_id)
    db.session.delete(train)
    db.session.commit()
    return jsonify({'message': 'Train deleted successfully'})
