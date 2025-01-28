from flask import Blueprint, redirect, url_for, session, request, current_app, jsonify
from google_auth_oauthlib.flow import Flow
import jwt
from flask_jwt_extended import get_jwt_identity, jwt_required,create_access_token
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests  # Renombrar para evitar conflictos
import requests  # Importar el módulo requests para las solicitudes HTTP
from firebase_admin import auth as firebase_auth
from firebase_admin import exceptions as firebase_exceptions
from mongoengine import errors as mongo_errors, NotUniqueError
from ..config import Config

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
        web_api_key = Config.FIREBASE_WEB_API_KEY

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
            decoded_token = firebase_auth.verify_id_token(auth_data['idToken'])
            
            # Generar token JWT
            jwt_token = create_access_token(identity=decoded_token['uid']) #Antes usaba el 'uid' 
            
            # Imprimir el token JWT
            print("Token JWT generado:", jwt_token)
            
            # Decodificar el token JWT para ver su contenido
            decoded_jwt = jwt.decode(jwt_token, options={"verify_signature": False})
            print("Contenido del token JWT:", decoded_jwt)
            
            return jsonify({
                "message": "Inicio de sesión exitoso",
                "uid": decoded_token['uid'],
                "email": decoded_token['email'],
                "firebase_token": auth_data['idToken'],
                "jwt_token": jwt_token
            }), 200
        else:
            return jsonify({"error": "Credenciales inválidas"}), 401

    except firebase_auth.InvalidIdTokenError:
        return jsonify({"error": "Token inválido"}), 401
    except requests.RequestException as e:
        return jsonify({"error": f"Error de red: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error en el inicio de sesión: {str(e)}"}), 500

@auth.route('/login/google')
def google_login():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": current_app.config['GOOGLE_CLIENT_ID'],
                "client_secret": current_app.config['GOOGLE_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']
    )
    flow.redirect_uri = current_app.config['GOOGLE_REDIRECT_URI']
    authorization_url, state = flow.authorization_url(prompt='select_account')
    session['state'] = state
    return redirect(authorization_url)

@auth.route('/login/google/callback')
def google_callback():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": current_app.config['GOOGLE_CLIENT_ID'],
                "client_secret": current_app.config['GOOGLE_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
        state=session['state']
    )
    flow.redirect_uri = current_app.config['GOOGLE_REDIRECT_URI']

    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    id_info = id_token.verify_oauth2_token(
        credentials.id_token, google_requests.Request(), current_app.config['GOOGLE_CLIENT_ID']
    )

    # Crear un token personalizado de Firebase
    custom_token = firebase_auth.create_custom_token(id_info['sub'])  # Uso del alias corregido

    # Buscar o crear usuario en MongoDB
    user = User.objects(google_id=id_info['sub']).first()
    if user:
        user.name = id_info.get('name', '')
        user.email = id_info['email']
        user.picture = id_info.get('picture', '')
        user.last_login = datetime.utcnow()
        user.save()
    else:
        # Crear usuario en Firebase si no existe
        try:
            firebase_user = firebase_auth.get_user(id_info['sub'])
        except firebase_auth.UserNotFoundError:
            firebase_user = firebase_auth.create_user(
                uid=id_info['sub'],
                email=id_info['email'],
                display_name=id_info.get('name', ''),
                photo_url=id_info.get('picture', '')
            )

        # Crear usuario en MongoDB
        user = User.create_google_user(
            google_id=id_info['sub'],
            email=id_info['email'],
            name=id_info.get('name', ''),
            picture=id_info.get('picture', '')
        )
        user.firebase_uid = id_info['sub']
        user.save()

    # Generar token JWT
    #jwt_token = create_access_token(identity=str(user.id))
    jwt_token = create_access_token(identity=id_info['sub'])
    
    

    # Almacenar información del usuario en la sesión
    session['user'] = {
        'id': str(user.id),
        'google_id': user.google_id,
        'email': user.email,
        'name': user.name,
        'picture': user.picture,
        'jwt_token': jwt_token  # Agregar el token JWT a la sesión
    }

    # Devolver un JSON con el token JWT y la información del usuario
    return jsonify({
        "message": "Inicio de sesión con Google exitoso",
        "uid": id_info['sub'],
        "email": id_info['email'],
        "redirect_url": url_for('auth.perfil'),
        "jwt_token": jwt_token,
        "user_info": {
            "id": str(user.id),
            "google_id": user.google_id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture
        }
    }), 200

@auth.route('/perfil')
@jwt_required()
def perfil():
    current_user_id = get_jwt_identity()
    user = User.objects(firebase_uid=current_user_id).first()  # Usar firebase_uid en lugar de id
    if user:
        return jsonify({'username': user.username, 'email': user.email}), 200
    else:
        return jsonify({'error': 'Usuario no encontrado'}), 404

@auth.route('/logout')
#@jwt_required()
def logout():
    session.pop('user', None)
    return "Has cerrado sesión. <a href='/'>Volver al inicio</a>"

@auth.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.objects(firebase_uid=current_user_id).first()  # Usar firebase_uid en lugar de id
    if user:
        return jsonify({'username': user.username, 'email': user.email}), 200
    else:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    

@auth.route('/me')
@jwt_required()
def get_user_info():
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
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


