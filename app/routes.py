from flask import Blueprint, request, jsonify  # Importa Blueprint para manejar las rutas, request para obtener datos del cuerpo de la solicitud y jsonify para retornar respuestas en formato JSON.
from werkzeug.security import check_password_hash  # Para verificar el hash de la contraseña en futuros endpoints.
from .models import User  # Importa el modelo User desde models.py.
from .openai_client import get_chat_completion  # Importa la función que interactúa con la API de OpenAI.

# Crea un Blueprint para gestionar las rutas relacionadas con los usuarios y OpenAI.
main = Blueprint('main', __name__)

# ENDPOINT DE REGISTRO METODO POST
@main.route('/register', methods=['POST'])
def register():
    """
    Endpoint para registrar un nuevo usuario.

    :return: Mensaje de éxito o error en formato JSON.
    """
    data = request.get_json()  # Obtiene los datos enviados en formato JSON.
    username = data.get('username')  # Extrae el nombre de usuario.
    email = data.get('email')  # Extrae el email.
    password = data.get('password')  # Extrae la contraseña.

    # Validación para asegurarse de que se envíen todos los campos requeridos.
    if not username or not email or not password:
        return jsonify({'error': 'Faltan datos'}), 400  # Si falta algún dato, retorna un error.

    # Comprueba si el nombre de usuario o el email ya están registrados.
    if User.objects(username=username).first() or User.objects(email=email).first():  
        return jsonify({'error': 'Usuario o email ya registrado, inténtelo de nuevo'}), 400  # Retorna un error si ya están registrados.

    # Crea un nuevo usuario y guarda en la base de datos.
    try:
        user = User(username=username, email=email)  # Crea una instancia de User con el nombre de usuario y el email.
        user.set_password(password)  # Establece la contraseña en formato hash.
        user.save()  # Guarda el usuario en la base de datos.
        return jsonify({'message': 'El usuario se ha registrado con éxito'}), 201  # Retorna un mensaje de éxito.
    except Exception as e:
        return jsonify({'error': f'Ocurrió un error: {str(e)}'}), 500  # Retorna un error en caso de fallo al guardar.

# ENDPOINT para OpenAI "ask" método POST
@main.route('/ask', methods=['POST'])
def ask_openai():
    """
    Endpoint para enviar una pregunta a la API de OpenAI y obtener una respuesta.

    :return: Respuesta generada por la API de OpenAI.
    """
    data = request.get_json()  # Obtiene los datos en formato JSON de la solicitud.
    prompt = data.get('prompt')  # Extrae el mensaje (prompt) del cuerpo de la solicitud.

    if not prompt:  # Si no se proporciona el prompt, retorna un error.
        return jsonify({'error': 'Falta el mensaje (prompt)'}), 400

    # Llama a la función para obtener una respuesta de OpenAI.
    try:
        response = get_chat_completion(prompt)  # Envía el prompt a OpenAI y obtiene una respuesta.
        return jsonify({'response': response}), 200  # Retorna la respuesta generada por OpenAI.
    except Exception as e:
        return jsonify({'error': f'Ocurrió un error al procesar la solicitud: {str(e)}'}), 500  # Manejo de errores en caso de fallo en la API de OpenAI.

@main.route('/test-backend', methods=['GET'])
def test_backend():
    """
    Endpoint para verificar que el backend está funcionando.
    Retorna un mensaje simple.
    """
    print("El endpoint '/test-backend' ha sido llamado")
    return jsonify({'message': 'Hola, soy el backend desde Python'}), 200