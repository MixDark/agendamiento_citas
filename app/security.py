"""
Módulo de seguridad de aplicación (Flask)
"""
from flask import Flask


class SecurityHeaders:
    """Headers de seguridad a nivel aplicación"""

    @staticmethod
    def init_app(app: Flask):

        @app.after_request
        def set_security_headers(response):

            # Previene MIME sniffing
            response.headers['X-Content-Type-Options'] = 'nosniff'

            # Protección XSS legacy (no rompe nada)
            response.headers['X-XSS-Protection'] = '1; mode=block'

            # Política de referrer
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

            # Política de permisos
            response.headers['Permissions-Policy'] = (
                "geolocation=(), microphone=(), camera=()"
            )

            return response

        return app


class SecurityConfig:
    """Configuración de seguridad lógica"""

    # Cookies seguras
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = True

    # Sesión
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutos

    # CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    @staticmethod
    def init_app(app: Flask):

        app.config.update(
            SESSION_COOKIE_HTTPONLY=SecurityConfig.SESSION_COOKIE_HTTPONLY,
            SESSION_COOKIE_SAMESITE=SecurityConfig.SESSION_COOKIE_SAMESITE,
            SESSION_COOKIE_SECURE=not app.debug,
            PERMANENT_SESSION_LIFETIME=SecurityConfig.PERMANENT_SESSION_LIFETIME,
            WTF_CSRF_ENABLED=SecurityConfig.WTF_CSRF_ENABLED,
            WTF_CSRF_TIME_LIMIT=SecurityConfig.WTF_CSRF_TIME_LIMIT,
        )

        return app
