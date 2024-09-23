from flask import Flask
from flask_cors import CORS  # Importar CORS
from app import create_app

app = create_app()

# Aplicar CORS a toda la aplicación
CORS(app)

if __name__ == '__main__':
    print(f"SECRET_KEY: {app.config['SECRET_KEY']}")  # Imprimir la clave secreta
    app.run(debug=True)
