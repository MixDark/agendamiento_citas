"""
Módulo de validación y sanitización de entrada para la aplicación de agendamiento de citas.
Proporciona funciones para validar y limpiar datos de usuario.
"""
import re
import bleach
from typing import Tuple, Optional


class PasswordValidator:
    """Validador de políticas de contraseñas seguras"""
    
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    
    @staticmethod
    def validate(password: str) -> Tuple[bool, Optional[str]]:
        """
        Valida que una contraseña cumpla con los requisitos de seguridad.
        
        Requisitos:
        - Mínimo 8 caracteres
        - Al menos una letra mayúscula
        - Al menos una letra minúscula
        - Al menos un número
        
        Args:
            password: Contraseña a validar
            
        Returns:
            Tupla (es_válida, mensaje_error)
        """
        if not password:
            return False, "La contraseña es requerida"
        
        if len(password) < PasswordValidator.MIN_LENGTH:
            return False, f"La contraseña debe tener al menos {PasswordValidator.MIN_LENGTH} caracteres"
        
        if len(password) > PasswordValidator.MAX_LENGTH:
            return False, f"La contraseña no puede exceder {PasswordValidator.MAX_LENGTH} caracteres"
        
        if not re.search(r'[A-Z]', password):
            return False, "La contraseña debe contener al menos una letra mayúscula"
        
        if not re.search(r'[a-z]', password):
            return False, "La contraseña debe contener al menos una letra minúscula"
        
        if not re.search(r'\d', password):
            return False, "La contraseña debe contener al menos un número"
        
        return True, None


class EmailValidator:
    """Validador de direcciones de correo electrónico"""
    
    # Patrón RFC 5322 simplificado
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    @staticmethod
    def validate(email: str) -> Tuple[bool, Optional[str]]:
        """
        Valida que un email tenga formato válido.
        
        Args:
            email: Email a validar
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        if not email:
            return False, "El email es requerido"
        
        if len(email) > 254:  # RFC 5321
            return False, "El email es demasiado largo"
        
        if not EmailValidator.EMAIL_PATTERN.match(email):
            return False, "El formato del email no es válido"
        
        return True, None


class PhoneValidator:
    """Validador de números de teléfono"""
    
    # Acepta formatos: 1234567890, 123-456-7890, (123) 456-7890, +1 123 456 7890
    PHONE_PATTERN = re.compile(
        r'^\+?1?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$'
    )
    
    @staticmethod
    def validate(phone: str) -> Tuple[bool, Optional[str]]:
        """
        Valida que un teléfono tenga formato válido.
        
        Args:
            phone: Teléfono a validar
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        if not phone:
            return True, None  # Teléfono es opcional en algunos casos
        
        # Limpiar espacios
        phone = phone.strip()
        
        if not PhoneValidator.PHONE_PATTERN.match(phone):
            return False, "El formato del teléfono no es válido. Use: 1234567890 o (123) 456-7890"
        
        return True, None


class InputSanitizer:
    """Sanitizador de entrada HTML para prevenir XSS"""
    
    # Tags HTML permitidos (muy restrictivo)
    ALLOWED_TAGS = []
    ALLOWED_ATTRIBUTES = {}
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """
        Limpia HTML de entrada para prevenir XSS.
        Elimina todos los tags HTML.
        
        Args:
            text: Texto a sanitizar
            
        Returns:
            Texto limpio sin HTML
        """
        if not text:
            return ""
        
        # Eliminar todos los tags HTML
        cleaned = bleach.clean(
            text,
            tags=InputSanitizer.ALLOWED_TAGS,
            attributes=InputSanitizer.ALLOWED_ATTRIBUTES,
            strip=True
        )
        
        return cleaned.strip()
    
    @staticmethod
    def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
        """
        Sanitiza una cadena de texto general.
        
        Args:
            text: Texto a sanitizar
            max_length: Longitud máxima permitida
            
        Returns:
            Texto sanitizado
        """
        if not text:
            return ""
        
        # Limpiar HTML
        cleaned = InputSanitizer.sanitize_html(text)
        
        # Limitar longitud si se especifica
        if max_length and len(cleaned) > max_length:
            cleaned = cleaned[:max_length]
        
        return cleaned.strip()


class UsernameValidator:
    """Validador de nombres de usuario"""
    
    MIN_LENGTH = 3
    MAX_LENGTH = 50
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
    
    @staticmethod
    def validate(username: str) -> Tuple[bool, Optional[str]]:
        """
        Valida que un nombre de usuario sea válido.
        
        Requisitos:
        - 3-50 caracteres
        - Solo letras, números, guiones y guiones bajos
        
        Args:
            username: Nombre de usuario a validar
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        if not username:
            return False, "El nombre de usuario es requerido"
        
        if len(username) < UsernameValidator.MIN_LENGTH:
            return False, f"El nombre de usuario debe tener al menos {UsernameValidator.MIN_LENGTH} caracteres"
        
        if len(username) > UsernameValidator.MAX_LENGTH:
            return False, f"El nombre de usuario no puede exceder {UsernameValidator.MAX_LENGTH} caracteres"
        
        if not UsernameValidator.USERNAME_PATTERN.match(username):
            return False, "El nombre de usuario solo puede contener letras, números, guiones y guiones bajos"
        
        return True, None


class NameValidator:
    """Validador de nombres de personas"""
    
    MIN_LENGTH = 2
    MAX_LENGTH = 100
    # Permite letras, espacios, acentos, ñ, apóstrofes y guiones
    NAME_PATTERN = re.compile(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s'-]+$")
    
    @staticmethod
    def validate(name: str, field_name: str = "nombre") -> Tuple[bool, Optional[str]]:
        """
        Valida que un nombre sea válido.
        
        Args:
            name: Nombre a validar
            field_name: Nombre del campo para mensajes de error
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        if not name:
            return False, f"El {field_name} es requerido"
        
        name = name.strip()
        
        if len(name) < NameValidator.MIN_LENGTH:
            return False, f"El {field_name} debe tener al menos {NameValidator.MIN_LENGTH} caracteres"
        
        if len(name) > NameValidator.MAX_LENGTH:
            return False, f"El {field_name} no puede exceder {NameValidator.MAX_LENGTH} caracteres"
        
        if not NameValidator.NAME_PATTERN.match(name):
            return False, f"El {field_name} contiene caracteres no válidos"
        
        return True, None
