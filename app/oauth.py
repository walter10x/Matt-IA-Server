import os
from flask_dance.contrib.google import make_google_blueprint

def init_google_oauth(app):
    google_bp = make_google_blueprint(
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_SECRET"),
        scope=["profile", "email"],
        redirect_to="main.auth_callback"
    )
    app.register_blueprint(google_bp, url_prefix="/login")


__all__ = ["init_google_oauth"]
