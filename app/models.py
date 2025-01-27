from mongoengine import Document, StringField, ReferenceField, ListField, DateTimeField, BooleanField, EmailField, DictField
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(Document):
    """
    Modelo para representar a un usuario.
    """
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password = StringField()
    google_id = StringField(unique=True, sparse=True)
    name = StringField()
    picture = StringField()
    threads = ListField(ReferenceField('Thread'))
    created_at = DateTimeField(default=datetime.utcnow)
    last_login = DateTimeField()
    firebase_uid = StringField(required=True, unique=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @classmethod
    def create_google_user(cls, google_id, email, name, picture):
        user = cls(
            google_id=google_id,
            email=email,
            username=email.split('@')[0],  # Usar la parte local del email como username
            name=name,
            picture=picture
        )
        user.save()
        return user

class Thread(Document):
    """
    Modelo para representar un hilo de conversación.
    """
    user = ReferenceField(User, required=True, reverse_delete_rule=2)
    title = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    is_active = BooleanField(default=True)
    messages = ListField(ReferenceField('Message'))
    context_summary = StringField() # Nuevo campo para almacenar un resumen o contexto general del hilo

    def add_message(self, message):
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
        self.save()

    def update_context_summary(self,summary):
        self.context_summary = summary
        self.save()    

class Message(Document):
    """
    Modelo para representar un mensaje dentro de un hilo.
    """
    thread = ReferenceField(Thread, required=True, reverse_delete_rule=2)
    sender = StringField(required=True, choices=('user', 'system', 'assistant'))
    content = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    metadata = DictField() # Nuevo campo para almacenar metadatos del mensaje
   
    def add_metadata(self, key, value):
        if not self.metadata:
            self.metadata = {}
        self.metadata[key] = value
        self.save()
