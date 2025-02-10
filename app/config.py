import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    MONGODB_URI = os.getenv('MONGODB_URI')
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_SECRET = os.getenv('GOOGLE_SECRET')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH')
    FIREBASE_WEB_API_KEY = os.getenv('FIREBASE_WEB_API_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    # FRONTEND_URL = os.getenv('FRONTEND_URL') if os.getenv('FLASK_ENV') == 'development' else os.getenv('PRODUCTION_FRONTEND_URL')
    FRONTEND_URL = os.getenv('FRONTEND_URL')
