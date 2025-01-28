from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Thread, Message
from ..services.openai_client import get_chat_completion

ai = Blueprint('ai', __name__)

@ai.route('/ask', methods=['POST'])
@jwt_required()
def ask_openai():
    """Consulta a OpenAI."""
    current_user_firebase_uid = get_jwt_identity()  # Obtiene el firebase_uid del usuario autenticado
    data = request.get_json()
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({'error': 'Falta el mensaje (prompt)'}), 400

    try:
        # Buscar al usuario por firebase_uid
        user = User.objects(firebase_uid=current_user_firebase_uid).first()
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Verificar si ya existe un hilo activo para el usuario
        active_thread = Thread.objects(user=user).first()
        if not active_thread:
            # Si no existe, crea uno nuevo
            active_thread = Thread(user=user, title="Nuevo chat")
            active_thread.save()

        # Obtener respuesta de OpenAI
        response = get_chat_completion(prompt)

        # Guardar mensaje del usuario
        user_message = Message(thread=active_thread, sender='user', content=prompt)
        user_message.save()

        # Guardar respuesta del asistente
        assistant_message = Message(thread=active_thread, sender='assistant', content=response)
        assistant_message.save()

        return jsonify({
            'response': response,
            'thread_id': str(active_thread.id),
            'user_message_id': str(user_message.id),
            'assistant_message_id': str(assistant_message.id)
        }), 200
    except Exception as e:
        current_app.logger.error(f'Error en ask_openai: {str(e)}')
        return jsonify({'error': f'Ocurrió un error al procesar la solicitud: {str(e)}'}), 500
