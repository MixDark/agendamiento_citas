from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash
from app.models import Usuario
from app import mysql, limiter
from app.validators import PasswordValidator, UsernameValidator, InputSanitizer
from app.security_logger import SecurityLogger


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    
    # Si el usuario ya está autenticado, redirigir según su rol
    if current_user.is_authenticated:
        if current_user.es_admin:
            return redirect(url_for('admin.usuarios'))
        return redirect(url_for('citas.index'))

    if request.method == 'POST':
        username = InputSanitizer.sanitize_string(request.form.get('username', '').strip(), max_length=50)
        password = request.form.get('password', '')
        
        
        try:
            user = Usuario.get_by_username(username)
            
            if user and Usuario.verify_password(username, password):
                # Verificar si la cuenta está activa
                if not user.activo:
                    SecurityLogger.log_login_attempt(username, False)
                    flash('Tu cuenta está desactivada. Contacta al administrador.', 'danger')
                    return render_template('auth/login.html')

                # Realizar el login
                login_user(user)
                SecurityLogger.log_login_attempt(username, True)
                
                # Verificar si requiere cambio de contraseña
                if Usuario.requiere_cambio_password(username):
                    flash('Por seguridad, debe cambiar tu contraseña', 'warning')
                    return redirect(url_for('auth.change_password'))
                
                flash('Has iniciado sesión exitosamente', 'success')
                
                # Manejar la redirección 'next'
                next_page = request.args.get('next')
                
                if next_page:
                    parsed_next = urlparse(next_page)
                    if parsed_next.netloc == '' and parsed_next.path.startswith('/'):
                        if next_page != '/' and next_page != '/citas/':  # Evitar bucles de redirección
                            print(f"Redirigiendo a: {next_page}")
                            return redirect(next_page)
                
                # Redirección por defecto según el rol
                if user.es_admin:
                    return redirect(url_for('admin.usuarios'))
                
                return redirect(url_for('citas.index'))
            
            SecurityLogger.log_login_attempt(username, False)
            flash('Usuario o contraseña incorrectos', 'danger')
            
        except Exception as e:
            flash('Error al procesar el inicio de sesión', 'danger')
    
    # GET request o credenciales inválidas
    return render_template('auth/login.html')
    

@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
@limiter.limit("3 per hour")
def change_password():
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validar que las contraseñas coincidan
        if new_password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('auth/change_password.html')
        
        # Validar política de contraseñas
        is_valid, error_message = PasswordValidator.validate(new_password)
        if not is_valid:
            flash(error_message, 'danger')
            return render_template('auth/change_password.html')
        
        try:
            Usuario.cambiar_password(current_user.id, new_password)
            SecurityLogger.log_password_change(current_user.username)
            flash('Contraseña actualizada exitosamente', 'success')
            
            # Redirige según el tipo de usuario después de cambiar la contraseña
            if current_user.es_admin:
                return redirect(url_for('admin.usuarios'))
            else:
                return redirect(url_for('citas.index'))
                
        except Exception as e:
            flash('Error al cambiar la contraseña', 'danger')
    
    return render_template('auth/change_password.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def register():
    if request.method == 'POST':
        username = InputSanitizer.sanitize_string(request.form['username'], max_length=50)
        nombre = InputSanitizer.sanitize_string(request.form['nombre'], max_length=100)
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validar nombre de usuario
        is_valid, error_message = UsernameValidator.validate(username)
        if not is_valid:
            flash(error_message, 'danger')
            return render_template('auth/register.html')
        
        # Validar contraseña
        is_valid, error_message = PasswordValidator.validate(password)
        if not is_valid:
            flash(error_message, 'danger')
            return render_template('auth/register.html')
        
        # Validaciones
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('auth/register.html')
        
        # Verificar si el usuario ya existe
        existing_user = Usuario.get_by_username(username)
        if existing_user:
            flash('El nombre de usuario ya está en uso', 'danger')
            return render_template('auth/register.html')
        
        try:
            # Crear nuevo usuario
            cur = mysql.connection.cursor()
            password_hash = generate_password_hash(password)
            
            cur.execute('''
                INSERT INTO usuarios (username, password_hash, nombre, es_admin, activo)
                VALUES (%s, %s, %s, %s, %s)
            ''', (username, password_hash, nombre, False, False))
            
            mysql.connection.commit()
            cur.close()
            
            flash('Registro exitoso. Por favor inicia sesión', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            flash('Error al registrar el usuario. Por favor intenta nuevamente', 'danger')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        username = InputSanitizer.sanitize_string(request.form['username'], max_length=50)
        nombre = InputSanitizer.sanitize_string(request.form['nombre'], max_length=100)
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validar nombre de usuario
        is_valid, error_message = UsernameValidator.validate(username)
        if not is_valid:
            flash(error_message, 'danger')
            return render_template('auth/perfil.html')

        # Verificar si el username ya existe (excluyendo el usuario actual)
        cur = mysql.connection.cursor()
        cur.execute('SELECT id_usuario FROM usuarios WHERE username = %s AND id_usuario != %s', 
                   (username, current_user.id))
        existing_user = cur.fetchone()
        cur.close()

        if existing_user:
            flash('El nombre de usuario ya está en uso', 'danger')
            return render_template('auth/perfil.html')

        try:
            cur = mysql.connection.cursor()
            
            # Si se proporcionó una nueva contraseña
            if password:
                # Validar política de contraseñas
                is_valid, error_message = PasswordValidator.validate(password)
                if not is_valid:
                    flash(error_message, 'danger')
                    return render_template('auth/perfil.html')
                
                if password != confirm_password:
                    flash('Las contraseñas no coinciden', 'danger')
                    return render_template('auth/perfil.html')
                
                password_hash = generate_password_hash(password)
                cur.execute('''
                    UPDATE usuarios 
                    SET username = %s, nombre = %s, password_hash = %s 
                    WHERE id_usuario = %s
                ''', (username, nombre, password_hash, current_user.id))
            else:
                # Si no se cambió la contraseña
                cur.execute('''
                    UPDATE usuarios 
                    SET username = %s, nombre = %s 
                    WHERE id_usuario = %s
                ''', (username, nombre, current_user.id))
            
            mysql.connection.commit()
            cur.close()
            
            flash('Perfil actualizado exitosamente', 'success')
            return redirect(url_for('auth.perfil'))
            
        except Exception as e:
            flash('Error al actualizar el perfil', 'danger')
            return render_template('auth/perfil.html')

    return render_template('auth/perfil.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('auth.login'))
