# 🏥 Sistema de agendamiento de citas médicas

Sistema web completo para la gestión de citas médicas desarrollado con Flask, MySQL y Bootstrap. Incluye autenticación de usuarios, gestión de pacientes, doctores, citas y un panel de administración.

## 🌟 Características principales

### Gestión de citas
- ✅ Crear, editar y eliminar citas
- ✅ Visualización por día o mes
- ✅ Estados de citas (Programada, Completada, Cancelada)
- ✅ Verificación de disponibilidad de horarios
- ✅ Notificaciones por correo electrónico

### Gestión de pacientes
- ✅ Registro completo de pacientes
- ✅ Historial de citas por paciente
- ✅ Búsqueda y filtrado
- ✅ Información de contacto

### Gestión de doctores
- ✅ Registro de doctores
- ✅ Verificación de disponibilidad
- ✅ Historial de citas por doctor

### Panel de administración
- ✅ Gestión de usuarios
- ✅ Asignación de roles (Admin/Usuario)
- ✅ Activación/desactivación de cuentas
- ✅ Reset de contraseñas

### Seguridad
- 🔐 Autenticación con Flask-Login
- 🛡️ Protección CSRF en todos los formularios
- 🚦 Rate limiting (protección contra fuerza bruta)
- 🔒 Headers de seguridad HTTP
- 🧹 Validación y sanitización de entrada
- 📊 Logging de eventos de seguridad
- 🔑 Políticas de contraseñas seguras

## 🚀 Tecnologías utilizadas

- **Backend:** Flask 3.0.0
- **Base de Datos:** MySQL
- **ORM:** Flask-MySQLdb
- **Autenticación:** Flask-Login
- **Email:** Flask-Mail
- **Seguridad:** Flask-WTF (CSRF), Flask-Limiter (Rate Limiting), Bleach (XSS)
- **Frontend:** Bootstrap 5, JavaScript
- **Servidor:** Waitress (Windows) / Gunicorn (Linux)

## 📋 Requisitos previos

- Python 3.8 o superior
- MySQL 5.7 o superior
- pip (gestor de paquetes de Python)

## 🔧 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/agendamiento_citas.git
cd agendamiento_citas
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos

Ejecutar el script SQL para crear la base de datos:

```bash
mysql -u root -p < BD.sql
```

### 5. Configurar variables de entorno

Copiar el archivo de ejemplo y configurar:

```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Editar `.env` con tus credenciales:

```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=tu_contraseña
MYSQL_DB=consultorio_medico
SECRET_KEY=genera_una_clave_con_el_script
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_contraseña_de_aplicacion
MAIL_DEFAULT_SENDER=tu_email@gmail.com
```

### 6. Generar SECRET_KEY segura

```bash
python generate_secret_key.py
```

Copiar la clave generada al archivo `.env`.

## ▶️ Ejecución

### Modo desarrollo

```bash
python run.py
```

La aplicación se abrirá automáticamente en `http://localhost:8000`

### Modo producción

```bash
python produccion.py
```

El script detectará automáticamente tu sistema operativo y usará:
- **Waitress** en Windows
- **Gunicorn** en Linux/Mac

## 👤 Usuarios por defecto

Después de ejecutar el script SQL, puedes iniciar sesión con:

- **Usuario:** admin
- **Contraseña:** admin123

> ⚠️ **Importante:** Cambia la contraseña del administrador después del primer inicio de sesión.

## 📁 Estructura del proyecto

```
agendamiento_citas/
├── app/
│   ├── __init__.py           # Inicialización de la aplicación
│   ├── config.py             # Configuración
│   ├── models.py             # Modelos de datos
│   ├── validators.py         # Validadores de entrada
│   ├── security.py           # Configuración de seguridad
│   ├── security_logger.py    # Logging de seguridad
│   ├── routes/               # Rutas de la aplicación
│   │   ├── auth.py           # Autenticación
│   │   ├── admin.py          # Panel de administración
│   │   ├── citas.py          # Gestión de citas
│   │   ├── pacientes.py      # Gestión de pacientes
│   │   ├── doctores.py       # Gestión de doctores
│   │   └── historico.py      # Historial
│   └── templates/            # Plantillas HTML
├── logs/                     # Logs de seguridad
├── .env                      # Variables de entorno (no incluido en Git)
├── .env.example              # Plantilla de variables de entorno
├── .gitignore                # Archivos ignorados por Git
├── BD.sql                    # Script de base de datos
├── requirements.txt          # Dependencias
├── run.py                    # Servidor de desarrollo
├── produccion.py             # Servidor de producción
└── generate_secret_key.py   # Generador de SECRET_KEY
```

## 🔐 Seguridad

Este proyecto implementa múltiples capas de seguridad:

- **Protección CSRF:** Tokens en todos los formularios
- **Rate Limiting:** 
  - Login: 5 intentos/minuto
  - Registro: 3 registros/hora
  - Cambio de contraseña: 3 cambios/hora
- **Headers HTTP:** X-Frame-Options, CSP, X-XSS-Protection, etc.
- **Validación de entrada:** Sanitización HTML, validación de formatos
- **Sesiones seguras:** HttpOnly, SameSite, expiración automática
- **Logging:** Registro de eventos de seguridad en `logs/security.log`

## 📧 Configuración de email

Para usar notificaciones por correo:

1. Habilitar "Verificación en 2 pasos" en tu cuenta de Gmail
2. Generar una "Contraseña de aplicación"
3. Usar esa contraseña en `MAIL_PASSWORD` del archivo `.env`

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 👨‍💻 Autor

**Tu Nombre**

## 🐛 Reportar problemas

Si encuentras algún bug o tienes sugerencias, por favor abre un [issue](https://github.com/tu-usuario/agendamiento_citas/issues).

## 📸 Capturas de Pantalla

### Pantalla principal
<img width="1270" height="611" alt="Pantalla principal" src="https://github.com/user-attachments/assets/0740c79e-af2f-4148-a203-2c451d4a0b3b" />

### Panel de administración
<img width="1919" height="619" alt="Admin" src="https://github.com/user-attachments/assets/f3f8df4a-ef5b-4246-9364-7036e1f1fa6f" />


---

⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub!
