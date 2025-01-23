import os
from flask_dance.contrib.google import make_google_blueprint

def init_google_oauth(app):
    """
    Configura Google OAuth utilizando Flask-Dance.
    """
    google_blueprint = make_google_blueprint(
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_SECRET"),
        scope=["profile", "email"],
        redirect_to="main.auth_callback"  # Aquí aseguramos que la redirección sea a 'main.auth_callback'
    )
    app.register_blueprint(google_blueprint, url_prefix="/google")
