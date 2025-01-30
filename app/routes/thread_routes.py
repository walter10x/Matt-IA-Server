from datetime import datetime
from flask import Blueprint, current_app, request, jsonify
from ..models import User, Thread, Message
from ..middlewares.auth_middleware import token_required

# Crear un nuevo Blueprint
thread_routes = Blueprint('thread_routes', __name__)

@thread_routes.route('/threads', methods=['POST'])
@token_required
def create_thread():
    data = request.get_json()
    title = data.get('title')

    if not title:
        return jsonify({'error': 'El título es requerido'}), 400

    try:
        user = User.objects(firebase_uid=request.user['uid']).first()
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        new_thread = Thread(user=user, title=title)
        new_thread.save()

        return jsonify({
            'message': 'Hilo creado exitosamente',
            'thread': {
                'id': str(new_thread.id),
                'title': new_thread.title,
                'created_at': new_thread.created_at,
                'updated_at': new_thread.updated_at,
                'is_active': new_thread.is_active,
                'user': {
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email
                }
            }
        }), 201

    except Exception as e:
        current_app.logger.error(f'Error al crear el hilo: {str(e)}')
        return jsonify({'error': 'Ocurrió un error al crear el hilo. Por favor, inténtelo de nuevo más tarde.'}), 500

@thread_routes.route('/threads/<thread_id>/messages', methods=['POST'])
@token_required
def add_message(thread_id):
    data = request.get_json()
    content = data.get('content')
    sender = data.get('sender')  # 'user' o 'assistant'

    if not content or not sender:
        return jsonify({'error': 'El contenido y el remitente son requeridos'}), 400

    if sender not in ['user', 'assistant']:
        return jsonify({'error': 'El remitente debe ser "user" o "assistant"'}), 400

    try:
        user = User.objects(firebase_uid=request.user['uid']).first()
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        thread = Thread.objects(id=thread_id, user=user).first()
        if not thread:
            return jsonify({'error': 'Hilo no encontrado o no pertenece al usuario'}), 404

        new_message = Message(thread=thread, sender=sender, content=content)
        new_message.save()

        thread.add_message(new_message)
        thread.save()

        return jsonify({
            'message': 'Mensaje añadido exitosamente',
            'thread_id': str(thread.id),
            'message': {
                'id': str(new_message.id),
                'sender': new_message.sender,
                'content': new_message.content,
                'created_at': new_message.created_at
            }
        }), 201

    except Exception as e:
        return jsonify({'error': f'Ocurrió un error al añadir el mensaje: {str(e)}'}), 500


@thread_routes.route('/threads', methods=['GET'])
@token_required
def get_user_threads():
    """Obtiene todos los hilos del usuario autenticado."""
    try:
        user = User.objects(firebase_uid=request.user['uid']).first()
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        threads = Thread.objects(user=user).order_by('-updated_at')  # Ordena por fecha de actualización, más reciente primero

        return jsonify({
            'threads': [
                {
                    'id': str(thread.id),
                    'title': thread.title,
                    'created_at': thread.created_at.isoformat(),
                    'updated_at': thread.updated_at.isoformat(),
                    'is_active': thread.is_active,
                    'message_count': len(thread.messages)
                } for thread in threads
            ]
        }), 200

    except Exception as e:
        current_app.logger.error(f'Error al obtener los hilos: {str(e)}')
        return jsonify({'error': f'Ocurrió un error al obtener los hilos: {str(e)}'}), 500
    


@thread_routes.route('/threads/<thread_id>/messages', methods=['GET'])
@token_required
def get_thread_messages(thread_id):
    """Obtiene todos los mensajes de un hilo específico."""
    try:
        # Verificar que el usuario esté autenticado
        user = User.objects(firebase_uid=request.user['uid']).first()
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Buscar el hilo por ID y asegurarse de que pertenece al usuario autenticado
        thread = Thread.objects(id=thread_id, user=user).first()
        if not thread:
            return jsonify({'error': 'Hilo no encontrado o no pertenece al usuario'}), 404

        # Recuperar todos los mensajes asociados al hilo, ordenados por fecha de creación
        messages = Message.objects(thread=thread).order_by('created_at')

        # Serializar los mensajes para devolverlos en la respuesta
        return jsonify({
            'thread': {
                'id': str(thread.id),
                'title': thread.title,
                'created_at': thread.created_at.isoformat(),
                'updated_at': thread.updated_at.isoformat(),
                'is_active': thread.is_active
            },
            'messages': [
                {
                    'id': str(message.id),
                    'sender': message.sender,
                    'content': message.content,
                    'created_at': message.created_at.isoformat(),
                    'metadata': message.metadata
                } for message in messages
            ]
        }), 200

    except Exception as e:
        current_app.logger.error(f'Error al obtener los mensajes del hilo: {str(e)}')
        return jsonify({'error': f'Ocurrió un error al obtener los mensajes: {str(e)}'}), 500



# @thread_routes.route('/threads/<thread_id>', methods=['GET'])
# @token_required
# def get_thread(thread_id):
#     try:
#         user = User.objects(firebase_uid=request.user['uid']).first()
#         if not user:
#             return jsonify({'error': 'Usuario no encontrado'}), 404

#         thread = Thread.objects(id=thread_id, user=user).first()
#         if not thread:
#             return jsonify({'error': 'Hilo no encontrado o no pertenece al usuario'}), 404

#         messages = Message.objects(thread=thread).order_by('created_at')

#         return jsonify({
#             'thread': {
#                 'id': str(thread.id),
#                 'title': thread.title,
#                 'created_at': thread.created_at.isoformat(),
#                 'updated_at': thread.updated_at.isoformat(),
#                 'is_active': thread.is_active,
#                 'messages': [
#                     {
#                         'id': str(message.id),
#                         'content': message.content,
#                         'created_at': message.created_at.isoformat(),
#                         'sender': message.sender
#                     } for message in messages
#                 ]
#             }
#         }), 200

#     except Exception as e:
#         current_app.logger.error(f'Error al obtener el hilo: {str(e)}')
#         return jsonify({'error': 'Ocurrió un error al obtener el hilo. Por favor, inténtelo de nuevo más tarde.'}), 500



