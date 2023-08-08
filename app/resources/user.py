from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request

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


user_bp.add_url_rule('/register', view_func=UserResource.as_view('register_user'))
