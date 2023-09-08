from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import logging

from db import db
from mail import mail
from .blocklist import BLOCKLIST


def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(f"config.{config_name.capitalize()}Config")

    # Configure logging
    logging.basicConfig(level=logging.DEBUG)

    db.init_app(app)
    jwt = JWTManager(app)

    mail.init_app(app)

    migrate = Migrate(app, db)
    api = Api(app)

    from .resources.note import note_blp
    from .resources.user import user_blp
    from .resources.tag import tag_blp

    api.register_blueprint(note_blp)
    api.register_blueprint(user_blp)
    api.register_blueprint(tag_blp)

    # Blocklist configuration for user logout
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )

    # Error handlers for JWT-related errors
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"message": "Signature verification failed.", "error": "invalid_token"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            "description": "Request does not contain an access token.",
            "error": "authorization_required"
        }), 401

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )

    with app.app_context():
        db.create_all()

    return app
