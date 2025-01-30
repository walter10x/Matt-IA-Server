from flask import request, jsonify
from functools import wraps
from firebase_admin import auth as firebase_auth
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from ..config import Config

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Verificar el token de Firebase
            decoded_token = firebase_auth.verify_id_token(token)
            request.user = {'uid': decoded_token['uid'], 'email': decoded_token['email']}
        except Exception as e:
            try:
                # Verificar el token de Google
                id_info = id_token.verify_oauth2_token(token, google_requests.Request(), Config.GOOGLE_CLIENT_ID)
                request.user = {'uid': id_info['sub'], 'email': id_info['email']}
            except Exception as e:
                return jsonify({'message': 'Token is invalid!'}), 401

        return f(*args, **kwargs)
    return decorated_function

