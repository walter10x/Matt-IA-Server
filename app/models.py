from mongoengine import Document, StringField, ReferenceField, ListField, DateTimeField
from werkzeug.security import generate_password_hash
from datetime import datetime

class User(Document):
    """
    Modelo para representar a un usuario.
    """
    username = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    threads = ListField(ReferenceField('Thread'))  # Relación con hilos creados por este usuario

    def set_password(self, password):
        """
        Genera un hash seguro para la contraseña del usuario.
        """
        self.password = generate_password_hash(password)

class Thread(Document):
    """
    Modelo para representar un hilo de conversación.
    """
    user = ReferenceField(User, required=True, reverse_delete_rule=2)  # Relación con el usuario propietario
    title = StringField()  # Título opcional del hilo
    created_at = DateTimeField(default=datetime.utcnow)  # Fecha de creación

class Message(Document):
    """
    Modelo para representar un mensaje dentro de un hilo.
    """
    thread = ReferenceField(Thread, required=True, reverse_delete_rule=2)  # Relación con el hilo
    sender = StringField(required=True, choices=('user', 'system'))  # Quién envió el mensaje
    content = StringField(required=True)  # Contenido del mensaje
    created_at = DateTimeField(default=datetime.utcnow)  # Fecha de creación
