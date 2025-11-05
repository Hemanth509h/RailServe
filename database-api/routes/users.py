from flask import Blueprint, request, jsonify
from models.database import db
from models.models import User
from datetime import datetime

bp = Blueprint('users', __name__, url_prefix='/api/users')

@bp.route('/', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'role': u.role,
        'active': u.active,
        'created_at': u.created_at.isoformat() if u.created_at else None
    } for u in users])

@bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'password_hash': user.password_hash,
        'role': user.role,
        'active': user.active,
        'reset_token': user.reset_token,
        'reset_token_expiry': user.reset_token_expiry.isoformat() if user.reset_token_expiry else None,
        'created_at': user.created_at.isoformat() if user.created_at else None
    })

@bp.route('/by-username/<username>', methods=['GET'])
def get_user_by_username(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'password_hash': user.password_hash,
        'role': user.role,
        'active': user.active,
        'created_at': user.created_at.isoformat() if user.created_at else None
    })

@bp.route('/by-email/<email>', methods=['GET'])
def get_user_by_email(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'password_hash': user.password_hash,
        'role': user.role,
        'active': user.active
    })

@bp.route('/', methods=['POST'])
def create_user():
    data = request.json
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=data['password_hash'],
        role=data.get('role', 'user'),
        active=data.get('active', True)
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id, 'username': user.username}), 201

@bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    
    if 'email' in data:
        user.email = data['email']
    if 'role' in data:
        user.role = data['role']
    if 'active' in data:
        user.active = data['active']
    if 'reset_token' in data:
        user.reset_token = data['reset_token']
    if 'reset_token_expiry' in data:
        user.reset_token_expiry = datetime.fromisoformat(data['reset_token_expiry']) if data['reset_token_expiry'] else None
    
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})
