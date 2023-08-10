from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_smorest import Api

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    jwt.init_app(app)

    from app.auth.routes import auth_bp
    from app.resources.note import note_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(note_bp)

    api = Api(app, spec_kwargs={'title': 'Notes API', 'version': 'v2'})
    api.register_blueprint(auth_bp)
    api.register_blueprint(note_bp)

    with app.app_context():
        db.create_all()  # Initialize database

    return app
