from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.models import User
from app.schemas.user import UserRegistrationSchema

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user_schema = UserRegistrationSchema()
    user = user_schema.load(data)

    existing_user = User.query.filter_by(username=user.username).first()
    if existing_user:
        return {'message': 'Username already exists'}, 400

    existing_email = User.query.filter_by(email=user.email).first()
    if existing_email:
        return {'message': 'Email already exists'}, 400

    user.set_password(data['password'])
    user.save_to_db()  # Use the new method to save the user to the database

    return user_schema.dump(user), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token}), 200

    return jsonify({'message': 'Invalid username or password'}), 401


@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({'message': f'Protected route for user {current_user}'}), 200
