from mongoengine import connect
import os
from dotenv import load_dotenv

load_dotenv()

# Conectar con MongoDB usando la URI de tu .env
connect(host=os.getenv('MONGO_URI'))

print("Conexión exitosa a MongoDB")
