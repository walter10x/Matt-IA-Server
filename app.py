from flask import Flask, session
from flask_session import Session
from flask_cors import CORS


from flask_cors import CORS  # Importar CORS
from dotenv import load_dotenv
load_dotenv()  # Carga las variables de entorno del archivo .env
from app import create_app


app = create_app()

# Configuración de sesiones
app.config['SECRET_KEY'] = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Aplicar CORS a toda la aplicación
CORS(app)

if __name__ == '__main__':
    print(f"SECRET_KEY: {app.config['SECRET_KEY']}")  # Imprimir la clave secreta
    app.run(
        debug=True,
        ssl_context=("certs/server.crt", "certs/server.key")
    )
