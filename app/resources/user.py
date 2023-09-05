from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt, create_access_token, get_jwt_identity
from flask_jwt_extended.exceptions import JWTDecodeError

from app.models import User
from app.schemas import UserSchema, UserRegistrationSchema, UserLoginResponseSchema, UserProfileSchema
from app.blocklist import BLOCKLIST

user_blp = Blueprint("Users", "users", description="Operations on users")


@user_blp.route("/user/<int:user_id>")
class UserResource(MethodView):
    @jwt_required()  # Protect this route with JWT
    @user_blp.response(200, UserSchema)
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return user

    # Views for updating and deleting users will be added in future features lol


@user_blp.route("/register")
class UserRegistration(MethodView):
    @user_blp.arguments(UserRegistrationSchema)
    @user_blp.response(201,description="User created successfully.")
    def post(self, user_data):
        try:
            existing_user = User.query.filter_by(username=user_data["username"]).first()
            if existing_user:
                abort(400, message="Username already exists")

            existing_email = User.query.filter_by(email=user_data["email"]).first()
            if existing_email:
                abort(400, message="Email already exists")

            user = User(**user_data)
            user.set_password(user_data["password"])  # Hash the password
            user.save_to_db()

            return {"message": "User created successfully."}, 201
        except Exception as e:
            abort(500, message="An error occurred while processing your request")


@user_blp.route("/login")
class UserLogin(MethodView):
    @user_blp.arguments(UserRegistrationSchema(only=("username", "password")))
    @user_blp.response(200, UserLoginResponseSchema)
    def post(self, user_data):
        try:
            user = User.query.filter_by(username=user_data["username"]).first()
            if user and user.check_password(user_data["password"]):
                access_token = create_access_token(identity=user.id)
                return {"access_token": access_token}
            else:
                abort(401, message="Invalid username or password")
        except Exception as e:
            abort(500, message="An error occurred while processing your request")


@user_blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()  # Protect this route with JWT
    @user_blp.response(200, description="Logged out successfully")
    def post(self):
        try:
            jti = get_jwt()["jti"]
            BLOCKLIST.add(jti)
            return {"message": "Logged out successfully"}, 200
        except JWTDecodeError:
            abort(500, message="An error occurred while processing your request")


@user_blp.route("/profile")
class UserProfile(MethodView):
    @jwt_required()
    @user_blp.response(200, UserProfileSchema)
    def get(self):
        current_user = get_jwt_identity()
        user = User.query.get(current_user)
        return user

    @jwt_required()
    @user_blp.arguments(UserProfileSchema(partial=True))
    @user_blp.response(200, UserProfileSchema)
    def put(self, user_data):
        current_user = get_jwt_identity()
        user = User.query.get(current_user)

        for field in user_data:
            setattr(user, field, user_data[field])

        user.save_to_db()
        return user
