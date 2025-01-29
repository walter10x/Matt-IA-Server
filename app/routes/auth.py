from flask import Blueprint, redirect, url_for, session, request, current_app, jsonify
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests  # Renombrar para evitar conflictos
import requests  # Importar el módulo requests para las solicitudes HTTP
from firebase_admin import auth as firebase_auth
from firebase_admin import exceptions as firebase_exceptions
from mongoengine import errors as mongo_errors, NotUniqueError
from ..config import Config
from ..middlewares.auth_middleware import token_required
from datetime import datetime
from ..models import User

auth = Blueprint('auth', __name__)

@auth.route('/')
def index():
    if 'user' in session:
        return f"Bienvenido a Matt-IA, {session['user']['name']}. <a href='/perfil'>Ver perfil</a> | <a href='/logout'>Cerrar sesión</a>"
    else:
        return "Bienvenido a Matt-IA. <a href='/login/google'>Iniciar sesión con Google</a>"

# ENDPOINT PARA EL REGISTRO CON FIREBASE
@auth.route('/register', methods=['POST'])
def register():
    email = request.json.get('email')
    password = request.json.get('password')
    username = request.json.get('username')

    if not email or not password or not username:
        return jsonify({"error": "Email, contraseña y nombre de usuario son requeridos"}), 400

    try:
        # Verificar si el email ya existe en Firebase
        try:
            firebase_auth.get_user_by_email(email)
            return jsonify({"error": "Este correo electrónico ya está registrado. Por favor, usa otro."}), 400
        except firebase_auth.UserNotFoundError:
            pass

        # Verificar si el email o username ya existen en MongoDB
        existing_user = User.objects(email=email).first()
        if existing_user:
            return jsonify({"error": "Este correo electrónico ya está en uso. Por favor, elige otro."}), 400

        existing_user = User.objects(username=username).first()
        if existing_user:
            return jsonify({"error": "Este nombre de usuario ya está tomado. Por favor, elige otro."}), 400

        # Crear usuario en Firebase
        firebase_user = firebase_auth.create_user(
            email=email,
            password=password
        )

        # Crear usuario en MongoDB
        mongo_user = User(
            firebase_uid=firebase_user.uid,
            email=email,
            username=username
        )
        mongo_user.save()

        return jsonify({
            "message": "Usuario registrado exitosamente",
            "uid": firebase_user.uid
        }), 201

    except firebase_exceptions.FirebaseError as e:
        return jsonify({"error": "Hubo un problema al registrar el usuario. Por favor, inténtalo de nuevo."}), 400
    except NotUniqueError as e:
        error_message = str(e)
        if 'email' in error_message:
            return jsonify({"error": "Este correo electrónico ya está en uso. Por favor, elige otro."}), 400
        elif 'username' in error_message:
            return jsonify({"error": "Este nombre de usuario ya está tomado. Por favor, elige otro."}), 400
        elif 'firebase_uid' in error_message:
            return jsonify({"error": "Ha ocurrido un error inesperado. Por favor, inténtalo de nuevo."}), 400
        else:
            return jsonify({"error": "Ha ocurrido un error al registrar el usuario. Por favor, verifica tus datos e inténtalo de nuevo."}), 400
    except mongo_errors.MongoEngineException as e:
        return jsonify({"error": "Hubo un problema al guardar tus datos. Por favor, inténtalo de nuevo."}), 400
    except Exception as e:
        error_message = str(e)
        if "duplicate key error" in error_message and "firebase_uid" in error_message:
            return jsonify({"error": "Ha ocurrido un error inesperado. Por favor, inténtalo de nuevo más tarde."}), 400
        else:
            return jsonify({"error": "Ha ocurrido un error inesperado. Por favor, inténtalo de nuevo."}), 500

# ENDPOINT PARA EL LOGIN CON FIREBASE
@auth.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    if not email or not password:
        return jsonify({"error": "Email y contraseña son requeridos"}), 400

    try:
        # Obtener la clave de API web de Firebase desde la configuración
        web_api_key = Config.FIREBASE_WEB_API_KEY

        # Usar la API REST de Firebase para iniciar sesión
        response = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={web_api_key}",
            json={
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
        )

        if response.status_code == 200:
            auth_data = response.json()
            # Verificar el token ID
            decoded_token = firebase_auth.verify_id_token(auth_data['idToken'])
            
            return jsonify({
                "message": "Inicio de sesión exitoso",
                "uid": decoded_token['uid'],
                "email": decoded_token['email'],
                "firebase_token": auth_data['idToken']
            }), 200
        else:
            return jsonify({"error": "Credenciales inválidas"}), 401

    except firebase_auth.InvalidIdTokenError:
        return jsonify({"error": "Token inválido"}), 401
    except requests.RequestException as e:
        return jsonify({"error": f"Error de red: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error en el inicio de sesión: {str(e)}"}), 500


@auth.route('/perfil')
@token_required
def perfil():
    user = User.objects(firebase_uid=request.user['uid']).first()  # Usar firebase_uid en lugar de id
    if user:
        return jsonify({
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "google_id": user.google_id,
            "firebase_uid": user.firebase_uid,
            "name": user.name,
            "picture": user.picture,
            "last_login": user.last_login,  # Fecha del último inicio de sesión
            "created_at": user.created_at,  # Fecha de creación del usuario
            # Agrega más campos según tu modelo User
        }), 200
    else:
        return jsonify({'error': 'Usuario no encontrado'}), 404

@auth.route('/logout')
@token_required
def logout():
    session.pop('user', None)
    return "Has cerrado sesión. <a href='/'>Volver al inicio</a>"

@auth.route('/protected', methods=['GET'])
@token_required
def protected():
    user = User.objects(firebase_uid=request.user['uid']).first()  # Usar firebase_uid en lugar de id
    if user:
        return jsonify({'username': user.username, 'email': user.email}), 200
    else:
        return jsonify({'error': 'Usuario no encontrado'}), 404

@auth.route('/me')
@token_required
def get_user_info():
    user = User.objects(firebase_uid=request.user['uid']).first()  # Usar firebase_uid en lugar de id
    if user:
        return jsonify({
            "id": str(user.id),
            "google_id": user.google_id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture
        }), 200
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404


