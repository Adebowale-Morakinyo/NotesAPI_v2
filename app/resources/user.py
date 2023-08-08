from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request

from flask_jwt_extended import (
    jwt_required,
    get_raw_jwt,
    create_access_token,
    jwt_manager,
    blacklist,
)
from flask_jwt_extended.exceptions import JWTDecodeError

from app.models import User
from app.schemas.user import UserRegistrationSchema
from app import db
from passlib.hash import pbkdf2_sha256

user_bp = Blueprint('user_bp', __name__, url_prefix='/users')


class UserResource(MethodView):
    def post(self):
        try:
            data = request.get_json()

            user_registration_schema = UserRegistrationSchema()
            user = user_registration_schema.load(data)

            existing_user = User.query.filter_by(username=user.username).first()
            if existing_user:
                return {'message': 'Username already exists'}, 400

            existing_email = User.query.filter_by(email=user.email).first()
            if existing_email:
                return {'message': 'Email already exists'}, 400

            user.set_password(data['password'])  # Hash the password
            db.session.add(user)
            db.session.commit()

            return user_registration_schema.dump(user), 201
        except Exception as e:
            return {'message': 'An error occurred while processing your request'}, 500

    def login(self):
        try:
            data = request.get_json()

            user_schema = UserRegistrationSchema(only=('username', 'password'))
            user_data = user_schema.load(data)

            user = User.query.filter_by(username=user_data['username']).first()
            if user and user.check_password(user_data['password']):
                access_token = create_access_token(identity=user.id)
                return {'access_token': access_token}, 200
            else:
                return {'message': 'Invalid username or password'}, 401
        except Exception as e:
            return {'message': 'An error occurred while processing your request'}, 500

    @jwt_required()
    def logout(self):
        try:
            jti = get_raw_jwt()['jti']
            blacklist.add(jti)
            return {'message': 'Logged out successfully'}, 200
        except JWTDecodeError:
            return {'message': 'An error occurred while processing your request'}, 500


# Add the UserResource as a view to the user_bp blueprint
user_bp.add_url_rule('/register', view_func=UserResource.as_view('register_user'))
user_bp.add_url_rule('/login', view_func=UserResource.as_view('login_user'))
user_bp.add_url_rule('/logout', view_func=UserResource.as_view('logout_user'))  # Add this line
