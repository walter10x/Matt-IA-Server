from openai import OpenAI
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Inicializar el cliente de OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_chat_completion(prompt, thread_messages):
    try:
        messages = [
            {"role": "system", "content": "Eres un asistente útil llamado MattIA. Mantén el contexto de la conversación."}
        ]
        
        # Convertir el cursor a una lista y obtener los últimos 5 mensajes
        recent_messages = list(thread_messages)[-5:]
        
        for msg in recent_messages:
            messages.append({
                "role": "user" if msg.sender == "user" else "assistant",
                "content": msg.content
            })
        
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ocurrió un error al procesar la solicitud: {str(e)}"
