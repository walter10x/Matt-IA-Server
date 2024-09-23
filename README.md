# Matt-IA-API

## Descripción
Breve descripción del proyecto.

## Configuración del Entorno

Para ejecutar este proyecto, necesitas configurar un archivo `.env` en la raíz del proyecto con las siguientes variables:

1. Crea un archivo `.env` en la raíz del proyecto.
2. Añade las siguientes variables al archivo:


- `tu_clave_api_de_openai`: Tu clave API de OpenAI. Puedes obtenerla en [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)
- `tu_uri_de_mongodb`: La URI de conexión a tu base de datos MongoDB. Si estás usando una instancia local, podría ser algo como "mongodb://localhost:27017/nombre_de_tu_bd"
- `tu_clave_secreta`: Una clave secreta para tu aplicación. Debe ser una cadena larga y aleatoria.
- La `API_URL` está configurada para desarrollo local. Ajústala según tu entorno de despliegue.

**Importante**: Nunca compartas tu archivo `.env` o expongas estas claves públicamente. Asegúrate de que `.env` esté incluido en tu `.gitignore`.
