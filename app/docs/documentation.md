Documentación de la Aplicación Backend.

Descripción General:
Esta aplicación es un servidor backend desarrollado con Flask que proporciona servicios de autenticación de usuarios, gestión de conversaciones y consultas a OpenAI. Utiliza MongoDB como base de datos y Firebase para la autenticación de usuarios.
Tecnologías Principales
Flask: Framework web de Python
MongoDB: Base de datos NoSQL
Firebase: Plataforma de desarrollo de aplicaciones
OpenAI: API para inteligencia artificial
Configuración
Requisitos Previos
Python 3.7+
pip (gestor de paquetes de Python)
MongoDB
Cuenta de Firebase
Cuenta de OpenAI
Instalación
Clone el repositorio:
bash
git clone <url_del_repositorio>
cd <nombre_del_directorio>
Instale las dependencias:
bash
pip install -r requirements.txt

Configure las variables de entorno:

Cree un archivo .env en el directorio raíz con el siguiente contenido:

SECRET_KEY=your_secret_key
MONGODB_URI=your_mongodb_uri
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_SECRET=your_google_secret
GOOGLE_REDIRECT_URI=your_google_redirect_uri
FIREBASE_CREDENTIALS_PATH=path_to_your_firebase_credentials.json
FIREBASE_WEB_API_KEY=your_firebase_web_api_key
JWT_SECRET_KEY=your_jwt_secret_key
OPENAI_API_KEY=your_openai_api_key
Certificados SSL
Para manejar solicitudes HTTPS, se requieren certificados SSL. Los archivos server.key y server.crt deben generarse y ubicarse en un directorio seguro. Asegúrese de actualizar la configuración de Flask para usar estos certificados1.

Estructura del Proyecto:
.
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models/
│   │   ├── user.py
│   │   ├── thread.py
│   │   └── message.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── auth_google.py
│   │   ├── thread_routes.py
│   │   └── openai_routes.py
│   └── services/
│       └── openai_client.py
├── .env
├── requirements.txt
└── run.py

Modelos de Datos:

User
Representa a un usuario en el sistema.
Thread
Representa un hilo de conversación.
Message
Representa un mensaje dentro de un hilo.

API Endpoints:

Autenticación
POST /register: Registra un nuevo usuario
POST /login: Inicia sesión con Firebase
GET /login/google: Inicia el flujo de autenticación con Google
GET /login/google/callback: Maneja la respuesta de autenticación de Google
GET /perfil: Obtiene el perfil del usuario autenticado
PUT /update: Actualiza los datos del usuario
DELETE /delete: Elimina la cuenta del usuario
GET /logout: Cierra la sesión del usuario
GET /me: Obtiene información del usuario autenticado
Hilos y Mensajes
POST /threads: Crea un nuevo hilo
POST /threads/<thread_id>/messages: Añade un mensaje a un hilo
GET /threads: Obtiene todos los hilos del usuario
GET /threads/<thread_id>/messages: Obtiene los mensajes de un hilo específico

OpenAI:

POST /ai/ask: Realiza una consulta a OpenAI y guarda la interacción
Seguridad
La aplicación utiliza JWT (JSON Web Tokens) para la autenticación. El middleware token_required verifica la validez del token en las rutas protegidas.
Integración con OpenAI
El servicio openai_client.py maneja las interacciones con la API de OpenAI, permitiendo generar respuestas basadas en el contexto de la conversación.
Ejecución
Para iniciar el servidor de desarrollo:
bash
flask run
Para producción, se recomienda usar un servidor WSGI como Gunicorn.
Contribución
Para contribuir al proyecto, por favor siga las mejores prácticas de desarrollo y envíe pull requests para su revisión.

Licencia:

Este proyecto está bajo la Licencia MIT