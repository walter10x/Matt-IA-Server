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
            picture=picture,
            firebase_uid=google_id  # Asegúrate de que firebase_uid tenga un valor válido
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

    def update_context_summary(self):
        """
        Genera un resumen de la conversación en el hilo.
        """
        user_messages = [msg.content for msg in self.messages if msg.sender == 'user']  # Filtra mensajes del usuario
        assistant_messages = [msg.content for msg in self.messages if msg.sender == 'assistant']  # Filtra mensajes del asistente
        
        summary = "Resumen de la conversación:\n"  # Inicializa el resumen
        summary += "\n".join([f"Usuario: {msg}" for msg in user_messages])  # Agrega mensajes del usuario al resumen
        summary += "\n" + "\n".join([f"Asistente: {msg}" for msg in assistant_messages])  # Agrega mensajes del asistente al resumen
        
        self.context_summary = summary  # Asigna el resumen al campo context_summary
        self.save()  # Guarda los cambios en la base de datos 

class Message(Document):
    """
    Modelo para representar un mensaje dentro de un hilo.
    """
    thread = ReferenceField('Thread', required=True, reverse_delete_rule=2)
    sender = StringField(required=True, choices=('user', 'system', 'assistant'))
    content = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    metadata = DictField()  # Campo para almacenar metadatos del mensaje

    def add_metadata(self, key, value):
        """
        Añade o actualiza un metadato del mensaje.
        """
        if not self.metadata:
            self.metadata = {}
        self.metadata[key] = value
        self.save()

    def to_dict(self):
        """
        Convierte el mensaje a un diccionario para facilitar su serialización.
        """
        return {
            'id': str(self.id),
            'sender': self.sender,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }