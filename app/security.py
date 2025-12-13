"""
Módulo de seguridad para la aplicación de agendamiento de citas.
Proporciona configuración de headers de seguridad HTTP y otras medidas de protección.
"""
from flask import Flask


class SecurityHeaders:
    """Configurador de headers de seguridad HTTP"""
    
    @staticmethod
    def init_app(app: Flask):
        """
        Inicializa los headers de seguridad para la aplicación Flask.
        
        Args:
            app: Instancia de la aplicación Flask
        """
        
        @app.after_request
        def set_security_headers(response):
            """Agrega headers de seguridad a todas las respuestas"""
            
            # Prevenir MIME type sniffing
            response.headers['X-Content-Type-Options'] = 'nosniff'
            
            # Prevenir clickjacking
            response.headers['X-Frame-Options'] = 'DENY'
            
            # Habilitar protección XSS del navegador
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            # Forzar HTTPS en producción (solo si está en HTTPS)
            if app.config.get('PREFERRED_URL_SCHEME') == 'https':
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            # Content Security Policy (política restrictiva)
            # Permite solo recursos del mismo origen y Bootstrap CDN
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://code.jquery.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
                "img-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )
            response.headers['Content-Security-Policy'] = csp
            
            # Política de referrer (no enviar información sensible)
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Política de permisos (deshabilitar características no usadas)
            response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
            
            return response
        
        return app


class SecurityConfig:
    """Configuración de seguridad adicional"""
    
    # Configuración de sesiones seguras
    SESSION_COOKIE_SECURE = True  # Solo HTTPS en producción
    SESSION_COOKIE_HTTPONLY = True  # No accesible desde JavaScript
    SESSION_COOKIE_SAMESITE = 'Lax'  # Protección CSRF adicional
    
    # Tiempo de expiración de sesión (30 minutos)
    PERMANENT_SESSION_LIFETIME = 1800
    
    # Configuración de CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # Sin límite de tiempo para tokens CSRF
    
    @staticmethod
    def init_app(app: Flask):
        """
        Aplica configuración de seguridad a la aplicación.
        
        Args:
            app: Instancia de la aplicación Flask
        """
        # Aplicar configuración de sesiones
        app.config['SESSION_COOKIE_HTTPONLY'] = SecurityConfig.SESSION_COOKIE_HTTPONLY
        app.config['SESSION_COOKIE_SAMESITE'] = SecurityConfig.SESSION_COOKIE_SAMESITE
        
        # Solo forzar HTTPS en producción
        if not app.debug:
            app.config['SESSION_COOKIE_SECURE'] = SecurityConfig.SESSION_COOKIE_SECURE
        
        app.config['PERMANENT_SESSION_LIFETIME'] = SecurityConfig.PERMANENT_SESSION_LIFETIME
        
        # Configuración CSRF
        app.config['WTF_CSRF_ENABLED'] = SecurityConfig.WTF_CSRF_ENABLED
        app.config['WTF_CSRF_TIME_LIMIT'] = SecurityConfig.WTF_CSRF_TIME_LIMIT
        
        return app
