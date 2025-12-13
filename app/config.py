import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'clave-secreta-por-defecto'
    MYSQL_HOST = os.getenv('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.getenv('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD') or ''
    MYSQL_DB = os.getenv('MYSQL_DB') or 'consultorio_medico'


      # Configuración del servidor de correo
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')