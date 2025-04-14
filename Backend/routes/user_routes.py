# routes/user_routes.py
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User
from extensions import db
from flask import Blueprint

user_bp = Blueprint("user_bp", __name__)

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.isoformat()
    }), 200

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user_id = int(get_jwt_identity())
    if current_user_id != user_id:
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.get_json()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    new_username = data.get('username')
    if new_username:
        user.username = new_username

    db.session.commit()
    return jsonify({"msg": "User updated successfully"}), 200
