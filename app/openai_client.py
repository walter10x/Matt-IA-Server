from openai import OpenAI
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Inicializar el cliente de OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_chat_completion(prompt):
    """
    Función que envía un prompt a la API de OpenAI (versión 1.46.1+) y devuelve la respuesta.
    
    :param prompt: El texto que el usuario envía para obtener una respuesta.
    :return: Respuesta generada por el modelo de OpenAI.
    """
    try:
        # Usar el método correcto para obtener respuestas de chat
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Puedes usar gpt-4 si tienes acceso
            messages=[
                {"role": "system", "content": "Eres un asistente útil. y tu Nombre es MattIA"},
                {"role": "user", "content": prompt}
            ]
        )
        # Devolver el contenido de la respuesta generada por el modelo
        return response.choices[0].message.content
    except Exception as e:
        return f"Ocurrió un error al procesar la solicitud: {str(e)}"