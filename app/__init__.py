from flask import Flask
from .config import Config
from mongoengine import connect
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
import os

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)
    
    

    connect(host=os.getenv('MONGO_URI'))
    jwt = JWTManager(app)

    from .routes import main
    app.register_blueprint(main)

    return app
