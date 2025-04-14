# routes/auth_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from extensions import db
from models import User

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"msg": "Missing required fields"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"msg": "User already exists"}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    if not user.check_password(password):
        return jsonify({"msg": "Incorrect Credentials"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
             "access_token": access_token,
             "user": {
                 "id": user.id,
                 "username": user.username,
                 "email": user.email
             }
         }), 200


@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    """Example protected route"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    return jsonify({
        "msg": f"Welcome {user.username}, you have accessed a protected route!"
    }), 200
