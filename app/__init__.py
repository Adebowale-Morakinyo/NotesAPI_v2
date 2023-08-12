from flask import Flask
from flask_jwt_extended import JWTManager
from flask_smorest import Api
from db import db

from app.auth.routes import auth_bp
from app.resources.note import note_bp

app = Flask(__name__)

app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["API_TITLE"] = "Notes API"
app.config["API_VERSION"] = "v2"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

api = Api(app)

api.register_blueprint(auth_bp)
api.register_blueprint(note_bp)
