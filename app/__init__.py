from flask import Flask
from .config import Config
from mongoengine import connect
from dotenv import load_dotenv
import os

def create_app():
    # Cargar variables de entorno
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    # Conexión a MongoDB
    connect(host=os.getenv('MONGO_URI'))

    # Registro de las rutas
    from .routes import main
    app.register_blueprint(main)

    return app
