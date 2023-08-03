from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_smorest import Api

from .auth.routes import auth_bp
from .resources.note import note_bp

app = Flask(__name__)

app.config.from_object('config.Config')
db = SQLAlchemy(app)
jwt = JWTManager(app)

app.register_blueprint(auth_bp)
app.register_blueprint(note_bp)
