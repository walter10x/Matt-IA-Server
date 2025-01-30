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
    from .routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # Importar y registrar el blueprint de OpenAI
    from .routes.openai_routes import ai as ai_blueprint
    app.register_blueprint(ai_blueprint, url_prefix='/ai')
   
    from .routes.auth_google import auth_google as auth_google_blueprint
    app.register_blueprint(auth_google_blueprint)

    from .routes.thread_routes import thread_routes as thread_routes_blueprint
    app.register_blueprint(thread_routes_blueprint)
  
    return app
