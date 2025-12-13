"""
Módulo de logging de eventos de seguridad.
Registra intentos de login fallidos, cambios de contraseña, y otros eventos de seguridad.
"""
import logging
from datetime import datetime
from functools import wraps
from flask import request
from flask_login import current_user


# Configurar logger de seguridad
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# Handler para archivo
file_handler = logging.FileHandler('logs/security.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)

# Formato del log
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)

# Agregar handler si no existe
if not security_logger.handlers:
    security_logger.addHandler(file_handler)


class SecurityLogger:
    """Clase para logging de eventos de seguridad"""
    
    @staticmethod
    def log_login_attempt(username: str, success: bool, ip_address: str = None):
        """
        Registra un intento de login.
        
        Args:
            username: Nombre de usuario que intentó hacer login
            success: Si el login fue exitoso
            ip_address: Dirección IP del cliente
        """
        ip = ip_address or request.remote_addr
        status = "EXITOSO" if success else "FALLIDO"
        
        security_logger.info(
            f"Login {status} - Usuario: {username} - IP: {ip}"
        )
    
    @staticmethod
    def log_password_change(username: str, changed_by: str = None):
        """
        Registra un cambio de contraseña.
        
        Args:
            username: Usuario cuya contraseña fue cambiada
            changed_by: Usuario que realizó el cambio (para admins)
        """
        if changed_by:
            security_logger.info(
                f"Contraseña cambiada - Usuario: {username} - Cambiada por: {changed_by}"
            )
        else:
            security_logger.info(
                f"Contraseña cambiada - Usuario: {username} - Auto-cambio"
            )
    
    @staticmethod
    def log_password_reset(username: str, reset_by: str):
        """
        Registra un reset de contraseña por administrador.
        
        Args:
            username: Usuario cuya contraseña fue reseteada
            reset_by: Administrador que realizó el reset
        """
        security_logger.warning(
            f"Contraseña reseteada - Usuario: {username} - Reseteada por admin: {reset_by}"
        )
    
    @staticmethod
    def log_access_denied(username: str, resource: str, reason: str):
        """
        Registra un acceso denegado.
        
        Args:
            username: Usuario que intentó acceder
            resource: Recurso al que se intentó acceder
            reason: Razón del rechazo
        """
        ip = request.remote_addr
        security_logger.warning(
            f"Acceso denegado - Usuario: {username} - Recurso: {resource} - "
            f"Razón: {reason} - IP: {ip}"
        )
    
    @staticmethod
    def log_rate_limit_exceeded(username: str = None, endpoint: str = None):
        """
        Registra cuando se excede el límite de rate limiting.
        
        Args:
            username: Usuario que excedió el límite (si está autenticado)
            endpoint: Endpoint que fue limitado
        """
        ip = request.remote_addr
        user = username or "Anónimo"
        
        security_logger.warning(
            f"Rate limit excedido - Usuario: {user} - Endpoint: {endpoint} - IP: {ip}"
        )
    
    @staticmethod
    def log_csrf_failure(username: str = None):
        """
        Registra un fallo de validación CSRF.
        
        Args:
            username: Usuario que intentó la acción (si está autenticado)
        """
        ip = request.remote_addr
        user = username or "Anónimo"
        
        security_logger.warning(
            f"Fallo de validación CSRF - Usuario: {user} - IP: {ip} - "
            f"Endpoint: {request.endpoint}"
        )
    
    @staticmethod
    def log_account_status_change(username: str, action: str, changed_by: str):
        """
        Registra cambios en el estado de cuenta (activar/desactivar, admin).
        
        Args:
            username: Usuario afectado
            action: Acción realizada (activado, desactivado, admin agregado, etc.)
            changed_by: Usuario que realizó el cambio
        """
        security_logger.info(
            f"Estado de cuenta cambiado - Usuario: {username} - "
            f"Acción: {action} - Cambiado por: {changed_by}"
        )


def log_security_event(event_type: str):
    """
    Decorador para logging automático de eventos de seguridad.
    
    Args:
        event_type: Tipo de evento a registrar
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Ejecutar la función
            result = f(*args, **kwargs)
            
            # Registrar el evento
            username = current_user.username if current_user.is_authenticated else "Anónimo"
            ip = request.remote_addr
            
            security_logger.info(
                f"Evento: {event_type} - Usuario: {username} - IP: {ip}"
            )
            
            return result
        return decorated_function
    return decorator
