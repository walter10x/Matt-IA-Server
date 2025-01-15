# @main.route('/ask', methods=['POST'])
# @jwt_required()
# def ask_openai():
#     current_user_id = get_jwt_identity()
#     user = User.objects.get(id=current_user_id)
#     data = request.get_json()
#     prompt = data.get('prompt')

#     if not prompt:
#         return jsonify({'error': 'Falta el mensaje (prompt)'}), 400

#     try:
#         # Obtener o crear un hilo activo
#         active_thread = Thread.objects(user=user, is_active=True).first()
#         if not active_thread:
#             active_thread = Thread(user=user, title="Nuevo chat", is_active=True)
#             active_thread.save()

#         # Obtener respuesta de OpenAI
#         response = get_chat_completion(prompt)

#         # Guardar mensaje del usuario
#         user_message = Message(thread=active_thread, sender='user', content=prompt)
#         user_message.save()

#         # Guardar respuesta del asistente
#         assistant_message = Message(thread=active_thread, sender='assistant', content=response)
#         assistant_message.save()

#         return jsonify({
#             'response': response, 
#             'thread_id': str(active_thread.id),
#             'user_message_id': str(user_message.id),
#             'assistant_message_id': str(assistant_message.id)
#         }), 200
#     except Exception as e:
#         current_app.logger.error(f'Error en ask_openai: {str(e)}')
#         return jsonify({'error': f'Ocurrió un error al procesar la solicitud: {str(e)}'}), 500
