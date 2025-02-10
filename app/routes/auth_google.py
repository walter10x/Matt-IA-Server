from urllib.parse import urlencode
from flask import Blueprint, make_response, redirect, url_for, session, request, current_app, jsonify
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from firebase_admin import auth as firebase_auth
from datetime import datetime
from ..models import User
from ..config import Config
from json import dumps

auth_google = Blueprint('auth_google', __name__)

def get_google_flow(state=None):
    return Flow.from_client_config(
        {
            "web": {
                "client_id": current_app.config['GOOGLE_CLIENT_ID'],
                "client_secret": current_app.config['GOOGLE_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
        state=state
    )

@auth_google.route('/login/google')
def google_login():
    flow = get_google_flow()
    flow.redirect_uri = current_app.config['GOOGLE_REDIRECT_URI']
    authorization_url, state = flow.authorization_url(prompt='select_account')
    session['state'] = state
    print(f"Authorization URL: {authorization_url}")
    return redirect(authorization_url)

@auth_google.route('/login/google/callback')
def google_callback():
    state = session.pop('state', None)
    print(f"State: {state}")

    try:
        flow = get_google_flow(state)
        flow.redirect_uri = current_app.config['GOOGLE_REDIRECT_URI']

        # Obtener código de autorización y token
        flow.fetch_token(code=request.args.get('code'))
        print(f"Fetched Token: {flow.credentials.token}")

        credentials = flow.credentials
        id_info = id_token.verify_oauth2_token(
            credentials.id_token, google_requests.Request(), current_app.config['GOOGLE_CLIENT_ID']
        )
        print(f"ID Info: {id_info}")

        # Crear un token de Firebase
        custom_token = firebase_auth.create_custom_token(id_info['sub'])
        print(f"Custom Token: {custom_token}")

        # Buscar o crear usuario en MongoDB
        user = User.objects(google_id=id_info['sub']).first()
        if not user:
            user = create_new_user(id_info)
        else:
            update_existing_user(user, id_info)

        # Preparar los datos para enviar al frontend
        user_data = prepare_user_data(id_info, custom_token, user)
        print(f"User Data: {user_data}")

        # Crear URL de redirección con los datos
        params = urlencode({
            "firebase_token": custom_token.decode('utf-8'),
            "email": id_info['email'],
            "user_info": dumps(user_data["user_info"])
        })
        print(f"Params: {params}")

        # Redirigir al frontend
        redirect_url = f"{current_app.config['FRONTEND_URL']}/login/google/callback?{params}"
        print(f"Redirect URL: {redirect_url}")
        return redirect(redirect_url, code=302)

    except Exception as e:
        current_app.logger.error(f"Error en google_callback: {str(e)}")
        error_params = urlencode({'error': 'Error durante la autenticación con Google'})
        redirect_url = f"{current_app.config['FRONTEND_URL']}/error?{error_params}"
        return redirect(redirect_url, code=302)

def create_new_user(id_info):
    try:
        firebase_user = firebase_auth.get_user(id_info['sub'])
    except firebase_auth.UserNotFoundError:
        firebase_user = firebase_auth.create_user(
            uid=id_info['sub'],
            email=id_info['email'],
            display_name=id_info.get('name', ''),
            photo_url=id_info.get('picture', '')
        )

    user = User.create_google_user(
        google_id=id_info['sub'],
        email=id_info['email'],
        name=id_info.get('name', ''),
        picture=id_info.get('picture', '')
    )
    user.firebase_uid = id_info['sub']
    user.save()
    return user

def update_existing_user(user, id_info):
    user.name = id_info.get('name', '')
    user.email = id_info['email']
    user.picture = id_info.get('picture', '')
    user.last_login = datetime.utcnow()
    user.save()

def prepare_user_data(id_info, custom_token, user):
    return {
        "uid": id_info['sub'],
        "email": id_info['email'],
        "firebase_token": custom_token.decode('utf-8'),
        "user_info": {
            "id": str(user.id),
            "google_id": user.google_id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture
        }
    }