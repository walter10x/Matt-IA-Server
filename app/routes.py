from flask import Blueprint, request, jsonify  
from werkzeug.security import check_password_hash  
from .models import User, Thread, Message 
from .openai_client import get_chat_completion  
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended import create_access_token
from mongoengine.errors import DoesNotExist  # Para manejar errores de MongoDB

# Crea un Blueprint para gestionar las rutas relacionadas con los usuarios y OpenAI.
main = Blueprint('main', __name__)

@main.route('/')
def home():
    return jsonify({'message': 'Bienvenido a la API de Matt-IA'}), 200

# ENDPOINT DE REGISTRO METODO POST
@main.route('/register', methods=['POST'])
def register():
    data = request.get_json()  # Obtiene los datos enviados en formato JSON.
    username = data.get('username')  # Extrae el nombre de usuario.
    email = data.get('email')  # Extrae el email.
    password = data.get('password')  # Extrae la contraseña.

    if not username or not email or not password:
        return jsonify({'error': 'Faltan datos'}), 400

    if User.objects(username=username).first() or User.objects(email=email).first():  
        return jsonify({'error': 'Usuario o email ya registrado, inténtelo de nuevo'}), 400

    try:
        user = User(username=username, email=email)  # Crea una instancia de User con el nombre de usuario y el email.
        user.set_password(password)  # Establece la contraseña en formato hash.
        user.save()  # Guarda el usuario en la base de datos.
        return jsonify({'message': 'El usuario se ha registrado con éxito'}), 201
    except Exception as e:
        return jsonify({'error': f'Ocurrió un error: {str(e)}'}), 500

@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Email y contraseña son requeridos"}), 400

    user = User.objects(email=email).first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=str(user.id))  # Guarda la identidad del usuario (por ejemplo, ID)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Correo o contraseña incorrectos"}), 401

@main.route('/ask', methods=['POST'])
def ask_openai():
    data = request.get_json()
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({'error': 'Falta el mensaje (prompt)'}), 400

    try:
        response = get_chat_completion(prompt)  # Envía el prompt a OpenAI y obtiene una respuesta.
        return jsonify({'response': response}), 200
    except Exception as e:
        return jsonify({'error': f'Ocurrió un error al procesar la solicitud: {str(e)}'}), 500

@main.route('/test-backend', methods=['GET'])
def test_backend():
    print("El endpoint '/test-backend' ha sido llamado")
    return jsonify({'message': 'Hola, soy el backend desde Python'}), 200

@main.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.objects()
        users_list = [{'username': user.username, 'email': user.email} for user in users]
        return jsonify({'users': users_list}), 200
    except Exception as e:
        return jsonify({'error': f'Ocurrió un error al obtener los usuarios: {str(e)}'}), 500

@main.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    return jsonify({'username': user.username, 'email': user.email}), 200

# RUTAS PARA MANEJO DE HILOS Y MENSAJES

@main.route('/threads', methods=['POST'])
@jwt_required()
def create_thread():
    data = request.get_json()
    title = data.get('title')

    if not title:
        return jsonify({'error': 'El título es obligatorio'}), 400

    current_user_id = get_jwt_identity()

    # Obtener el usuario directamente desde su ID usando ReferenceField
    user = User.objects(id=current_user_id).first()

    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    # Crear el hilo con la referencia al usuario
    thread = Thread(user=user, title=title)
    thread.save()

    return jsonify({'message': 'Hilo creado con éxito', 'thread_id': str(thread.id)}), 201


@main.route('/threads', methods=['GET'])
@jwt_required()
def get_threads():
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()

    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    threads = Thread.objects(user=user)
    threads_list = [{'id': str(thread.id), 'title': thread.title, 'created_at': thread.created_at.isoformat()} for thread in threads]
    return jsonify({'threads': threads_list}), 200

@main.route('/threads/<thread_id>', methods=['DELETE'])
@jwt_required()
def delete_thread(thread_id):
    current_user_id = get_jwt_identity()  # Esto debería ser un String

    try:
        # Buscar el hilo por su ID
        thread = Thread.objects.get(id=thread_id)

        # Verificar si el hilo pertenece al usuario autenticado
        if str(thread.user.id) != str(current_user_id):  # Aseguramos que ambos son Strings
            return jsonify({'error': 'No tienes permiso para eliminar este hilo'}), 403

        # Eliminar el hilo si el usuario es el propietario
        thread.delete()

        return jsonify({'message': 'Hilo eliminado con éxito'}), 200
    except Thread.DoesNotExist:
        return jsonify({'error': 'Hilo no encontrado'}), 404




@main.route('/threads/<thread_id>/messages', methods=['POST'])
@jwt_required()
def create_message(thread_id):
    data = request.get_json()
    content = data.get('content')

    if not content:
        return jsonify({'error': 'El contenido del mensaje es obligatorio'}), 400

    current_user_id = get_jwt_identity()

    try:
        thread = Thread.objects.get(id=thread_id, user__id=current_user_id)
        message = Message(thread=thread, sender='user', content=content)
        message.save()
        return jsonify({'message': 'Mensaje creado con éxito', 'message_id': str(message.id)}), 201
    except DoesNotExist:
        return jsonify({'error': 'Hilo no encontrado o no pertenece al usuario'}), 404

@main.route('/threads/<thread_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(thread_id):
    current_user_id = get_jwt_identity()

    try:
        thread = Thread.objects.get(id=thread_id, user__id=current_user_id)
        messages = Message.objects(thread=thread)
        messages_list = [{'id': str(message.id), 'sender': message.sender, 'content': message.content, 'created_at': message.created_at.isoformat()} for message in messages]
        return jsonify({'messages': messages_list}), 200
    except DoesNotExist:
        return jsonify({'error': 'Hilo no encontrado o no pertenece al usuario'}), 404
