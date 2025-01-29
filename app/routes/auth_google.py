from flask import Blueprint, redirect, url_for, session, request, current_app, jsonify
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from firebase_admin import auth as firebase_auth
from datetime import datetime
from ..models import User
from ..config import Config

auth_google = Blueprint('auth_google', __name__)

@auth_google.route('/login/google')
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

@auth_google.route('/login/google/callback')
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
    custom_token = firebase_auth.create_custom_token(id_info['sub'])

    # Buscar o crear usuario en MongoDB
    user = User.objects(google_id=id_info['sub']).first()
    if not user:
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
    else:
        user.name = id_info.get('name', '')
        user.email = id_info['email']
        user.picture = id_info.get('picture', '')
        user.last_login = datetime.utcnow()
        user.save()

    # Almacenar información del usuario en la sesión
    session['user'] = {
        'id': str(user.id),
        'google_id': user.google_id,
        'email': user.email,
        'name': user.name,
        'picture': user.picture
    }

    # Devolver un JSON con el token de Firebase y la información del usuario
    return jsonify({
        "message": "Inicio de sesión con Google exitoso",
        "uid": id_info['sub'],
        "email": id_info['email'],
        "firebase_token": credentials.id_token,
        "user_info": {
            "id": str(user.id),
            "google_id": user.google_id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture
        }
    }), 200
