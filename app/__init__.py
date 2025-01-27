from flask import Flask
from mongoengine import connect
import firebase_admin
from firebase_admin import credentials
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Conexión a MongoDB
    connect(host=app.config['MONGODB_URI'])

    # Inicialización de Firebase
    cred = credentials.Certificate(app.config['FIREBASE_CREDENTIALS_PATH'])
    firebase_admin.initialize_app(cred)

    # Importar y registrar rutas
    from .routes import main
    app.register_blueprint(main)

    return app
