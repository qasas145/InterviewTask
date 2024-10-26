from flask import Flask
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from config import Config
import redis

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize JWT
    jwt = JWTManager(app)

    # MongoDB setup
    client = MongoClient(app.config["MONGO_URI"])
    app.db = client.get_database()


    # Register routes
    from .routes import api
    app.register_blueprint(api)

    return app
