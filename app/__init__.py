from flask import Flask
from flask_smorest import Api
from flask_jwt_extended import JWTManager

from db import db
from .blocklist import BLOCKLIST
jwt = JWTManager()


def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(f"config.{config_name.capitalize()}Config")

    db.init_app(app)
    jwt.init_app(app)

    api = Api(app)

    from .resources.note import note_blp
    from .resources.user import user_blp
    from .resources.tag import tag_blp

    api.register_blueprint(note_blp)
    api.register_blueprint(user_blp)
    api.register_blueprint(tag_blp)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    with app.app_context():
        db.create_all()

    return app
