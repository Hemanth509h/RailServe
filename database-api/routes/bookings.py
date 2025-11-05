from flask import Blueprint, request, jsonify
from models.database import db
from models.models import Booking, Passenger
from datetime import datetime, date

bp = Blueprint('bookings', __name__, url_prefix='/api/bookings')

@bp.route('/', methods=['GET'])
def get_bookings():
    user_id = request.args.get('user_id')
    if user_id:
        bookings = Booking.query.filter_by(user_id=int(user_id)).all()
    else:
        bookings = Booking.query.all()
    
    return jsonify([{
        'id': b.id,
        'pnr': b.pnr,
        'user_id': b.user_id,
        'train_id': b.train_id,
        'from_station_id': b.from_station_id,
        'to_station_id': b.to_station_id,
        'journey_date': b.journey_date.isoformat() if b.journey_date else None,
        'passengers': b.passengers,
        'total_amount': b.total_amount,
        'status': b.status,
        'booking_type': b.booking_type,
        'coach_class': b.coach_class
    } for b in bookings])

@bp.route('/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return jsonify({
        'id': booking.id,
        'pnr': booking.pnr,
        'user_id': booking.user_id,
        'train_id': booking.train_id,
        'from_station_id': booking.from_station_id,
        'to_station_id': booking.to_station_id,
        'journey_date': booking.journey_date.isoformat() if booking.journey_date else None,
        'passengers': booking.passengers,
        'total_amount': booking.total_amount,
        'status': booking.status,
        'booking_type': booking.booking_type,
        'quota': booking.quota,
        'coach_class': booking.coach_class,
        'waitlist_type': booking.waitlist_type,
        'booking_date': booking.booking_date.isoformat() if booking.booking_date else None
    })

@bp.route('/pnr/<pnr>', methods=['GET'])
def get_booking_by_pnr(pnr):
    booking = Booking.query.filter_by(pnr=pnr).first()
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    return jsonify({
        'id': booking.id,
        'pnr': booking.pnr,
        'user_id': booking.user_id,
        'train_id': booking.train_id,
        'from_station_id': booking.from_station_id,
        'to_station_id': booking.to_station_id,
        'journey_date': booking.journey_date.isoformat() if booking.journey_date else None,
        'passengers': booking.passengers,
        'total_amount': booking.total_amount,
        'status': booking.status,
        'booking_type': booking.booking_type,
        'coach_class': booking.coach_class
    })

@bp.route('/', methods=['POST'])
def create_booking():
    data = request.json
    booking = Booking(
        user_id=data['user_id'],
        train_id=data['train_id'],
        from_station_id=data['from_station_id'],
        to_station_id=data['to_station_id'],
        journey_date=datetime.fromisoformat(data['journey_date']).date() if isinstance(data['journey_date'], str) else data['journey_date'],
        passengers=data['passengers'],
        total_amount=data['total_amount'],
        booking_type=data.get('booking_type', 'general'),
        quota=data.get('quota', 'general'),
        coach_class=data.get('coach_class', 'SL'),
        status=data.get('status', 'pending_payment'),
        waitlist_type=data.get('waitlist_type', 'GNWL')
    )
    db.session.add(booking)
    db.session.commit()
    return jsonify({'id': booking.id, 'pnr': booking.pnr}), 201

@bp.route('/<int:booking_id>', methods=['PUT'])
def update_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    data = request.json
    
    for field in ['status', 'total_amount', 'coach_class', 'waitlist_type']:
        if field in data:
            setattr(booking, field, data[field])
    
    db.session.commit()
    return jsonify({'message': 'Booking updated successfully'})

@bp.route('/<int:booking_id>/passengers', methods=['GET'])
def get_booking_passengers(booking_id):
    passengers = Passenger.query.filter_by(booking_id=booking_id).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'age': p.age,
        'gender': p.gender,
        'id_proof_type': p.id_proof_type,
        'id_proof_number': p.id_proof_number,
        'seat_number': p.seat_number,
        'berth_type': p.berth_type
    } for p in passengers])

@bp.route('/<int:booking_id>/passengers', methods=['POST'])
def add_passenger():
    data = request.json
    passenger = Passenger(
        booking_id=data['booking_id'],
        name=data['name'],
        age=data['age'],
        gender=data['gender'],
        id_proof_type=data['id_proof_type'],
        id_proof_number=data['id_proof_number'],
        seat_preference=data.get('seat_preference', 'No Preference'),
        coach_class=data.get('coach_class', 'SL')
    )
    db.session.add(passenger)
    db.session.commit()
    return jsonify({'id': passenger.id}), 201
