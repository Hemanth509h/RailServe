from flask import Blueprint, request, jsonify
from models.database import db
from models.models import PerformanceMetrics, SeatAvailability, DynamicPricing
from datetime import datetime

bp = Blueprint('performance', __name__, url_prefix='/api/performance')

@bp.route('/metrics', methods=['GET'])
def get_metrics():
    metrics = PerformanceMetrics.query.all()
    return jsonify([{
        'id': m.id,
        'train_id': m.train_id,
        'journey_date': m.journey_date.isoformat() if m.journey_date else None,
        'on_time_percentage': m.on_time_percentage,
        'total_passengers': m.total_passengers,
        'revenue_generated': m.revenue_generated
    } for m in metrics])

@bp.route('/metrics', methods=['POST'])
def create_metrics():
    data = request.json
    metrics = PerformanceMetrics(
        train_id=data['train_id'],
        journey_date=datetime.fromisoformat(data['journey_date']).date() if isinstance(data['journey_date'], str) else data['journey_date'],
        on_time_percentage=data.get('on_time_percentage', 0.0),
        average_delay_minutes=data.get('average_delay_minutes', 0),
        total_passengers=data.get('total_passengers', 0),
        revenue_generated=data.get('revenue_generated', 0.0),
        cancellations=data.get('cancellations', 0),
        waitlist_confirmed=data.get('waitlist_confirmed', 0)
    )
    db.session.add(metrics)
    db.session.commit()
    return jsonify({'id': metrics.id}), 201

@bp.route('/availability', methods=['GET'])
def get_availability():
    train_id = request.args.get('train_id')
    journey_date = request.args.get('journey_date')
    
    query = SeatAvailability.query
    if train_id:
        query = query.filter_by(train_id=int(train_id))
    if journey_date:
        query = query.filter_by(journey_date=datetime.fromisoformat(journey_date).date())
    
    availability = query.all()
    return jsonify([{
        'id': a.id,
        'train_id': a.train_id,
        'from_station_id': a.from_station_id,
        'to_station_id': a.to_station_id,
        'journey_date': a.journey_date.isoformat() if a.journey_date else None,
        'coach_class': a.coach_class,
        'available_seats': a.available_seats,
        'waiting_list': a.waiting_list,
        'rac_seats': a.rac_seats
    } for a in availability])

@bp.route('/availability', methods=['POST'])
def create_availability():
    data = request.json
    availability = SeatAvailability(
        train_id=data['train_id'],
        from_station_id=data['from_station_id'],
        to_station_id=data['to_station_id'],
        journey_date=datetime.fromisoformat(data['journey_date']).date() if isinstance(data['journey_date'], str) else data['journey_date'],
        coach_class=data['coach_class'],
        quota=data.get('quota', 'general'),
        available_seats=data.get('available_seats', 0),
        waiting_list=data.get('waiting_list', 0),
        rac_seats=data.get('rac_seats', 0)
    )
    db.session.add(availability)
    db.session.commit()
    return jsonify({'id': availability.id}), 201

@bp.route('/pricing', methods=['GET'])
def get_pricing():
    pricing = DynamicPricing.query.all()
    return jsonify([{
        'id': p.id,
        'train_id': p.train_id,
        'coach_class': p.coach_class,
        'surge_pricing_enabled': p.surge_pricing_enabled,
        'base_fare_multiplier': p.base_fare_multiplier
    } for p in pricing])

@bp.route('/pricing', methods=['POST'])
def create_pricing():
    data = request.json
    pricing = DynamicPricing(
        train_id=data['train_id'],
        coach_class=data['coach_class'],
        base_fare_multiplier=data.get('base_fare_multiplier', 1.0),
        surge_pricing_enabled=data.get('surge_pricing_enabled', False),
        demand_threshold_high=data.get('demand_threshold_high', 80),
        demand_threshold_medium=data.get('demand_threshold_medium', 50),
        high_demand_multiplier=data.get('high_demand_multiplier', 1.5),
        medium_demand_multiplier=data.get('medium_demand_multiplier', 1.2),
        active=data.get('active', True)
    )
    db.session.add(pricing)
    db.session.commit()
    return jsonify({'id': pricing.id}), 201
