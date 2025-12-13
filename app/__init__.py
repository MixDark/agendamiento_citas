from flask import Flask, redirect, url_for
from flask_login import current_user
from flask_mysqldb import MySQL
from app.config import Config
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.security import SecurityHeaders, SecurityConfig
import os

mysql = MySQL()
mail = Mail()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def create_app():
    """Crea y configura la aplicación Flask"""
    app = Flask(__name__)
    login_manager = LoginManager()
    app.config.from_object(Config)
    
    # Inicializar Flask-Mail
    mail.init_app(app)
    
    # Inicializar protección CSRF
    csrf.init_app(app)
    
    # Inicializar rate limiting
    limiter.init_app(app)
    
    # Aplicar configuración de seguridad
    SecurityConfig.init_app(app)
    SecurityHeaders.init_app(app)
    
    # Crear directorio de logs si no existe
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Configuración de MySQL
    app.config['MYSQL_HOST'] = Config.MYSQL_HOST
    app.config['MYSQL_USER'] = Config.MYSQL_USER
    app.config['MYSQL_PASSWORD'] = Config.MYSQL_PASSWORD
    app.config['MYSQL_DB'] = Config.MYSQL_DB
        
    mysql.init_app(app)

    # Configurar Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicie sesión para acceder a esta página'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import Usuario
        return Usuario.get_by_id(user_id)    
    
    # Registrar blueprints
    from app.routes.citas import citas_bp
    from app.routes.pacientes import pacientes_bp
    from app.routes.auth import auth_bp
    from app.routes.historico import historico_bp
    from app.routes.admin import admin_bp
    from app.routes.doctores import doctores_bp
    
    app.register_blueprint(citas_bp, url_prefix='/citas')
    app.register_blueprint(pacientes_bp, url_prefix='/pacientes')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(historico_bp, url_prefix='/historico') 
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(doctores_bp, url_prefix='/doctores')

    # Ruta raíz
    @app.route('/')
    def index():
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.es_admin:
            return redirect(url_for('admin.usuarios'))
        return redirect(url_for('citas.index'))

    # Filtro para formatear hora
    @app.template_filter('format_time')
    def format_time(td):
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"
    
    # Filtro para formatear fecha
    @app.template_filter('format_date')
    def format_date(date):
        if date:
            return date.strftime("%d/%m/%Y")
        return ""

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()