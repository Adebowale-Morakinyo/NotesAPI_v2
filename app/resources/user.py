from flask.views import MethodView
from flask_smorest import Blueprint, abort

from app.models import User
from app.schamas import UserSchema

user_blp = Blueprint("Users", "users", description="Operations on users")


@user_blp.route("/user/<int:user_id>")
class UserResource(MethodView):
    @user_blp.response(200, UserSchema)
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return user
