from flask import Flask
from config import Configs
from api.routes import api_blu


def create_app():
    app = Flask(__name__)
    app.config.from_object(Configs)
    app.register_blueprint(api_blu)
    return app
