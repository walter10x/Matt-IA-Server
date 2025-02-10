from flask import Blueprint, request, jsonify, current_app, make_response
from ..models import User, Thread, Message
from ..services.openai_client import get_chat_completion
from ..middlewares.auth_middleware import token_required
from datetime import datetime

ai = Blueprint('ai', __name__)

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    return response

@ai.route('/ask', methods=['POST', 'OPTIONS'])
@token_required
def ask_openai():
    """Consulta a OpenAI y guarda la interacción en un hilo."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    current_user_firebase_uid = request.user['uid']
    data = request.get_json()
    prompt = data.get('prompt')
    thread_id = data.get('thread_id')

    if not prompt:
        return jsonify({'error': 'Falta el mensaje (prompt)'}), 400

    try:
        user = User.objects(firebase_uid=current_user_firebase_uid).first()
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        if thread_id:
            active_thread = Thread.objects(id=thread_id, user=user).first()
            if not active_thread:
                return jsonify({'error': 'Hilo no encontrado o no pertenece al usuario'}), 404
        else:
            active_thread = Thread(user=user, title=prompt[:50])
            active_thread.save()

        thread_messages = Message.objects(thread=active_thread).order_by('created_at')
        response = get_chat_completion(prompt, thread_messages)

        user_message = Message(thread=active_thread, sender='user', content=prompt)
        user_message.save()

        assistant_message = Message(thread=active_thread, sender='assistant', content=response)
        assistant_message.save()

        active_thread.add_message(user_message)
        active_thread.add_message(assistant_message)
        active_thread.updated_at = datetime.utcnow()
        active_thread.save()

        response = jsonify({
            'thread_id': str(active_thread.id),
            'user_message': user_message.to_dict(),
            'assistant_message': assistant_message.to_dict()
        })
        
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 200

    except Exception as e:
        current_app.logger.error(f'Error en ask_openai: {str(e)}')
        error_response = jsonify({'error': f'Ocurrió un error al procesar la solicitud: {str(e)}'})
        error_response.headers.add("Access-Control-Allow-Origin", "*")
        return error_response, 500
