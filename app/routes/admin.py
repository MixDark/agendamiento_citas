from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app.models import Usuario
from app import mysql
from app.security_logger import SecurityLogger

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('No tienes permisos de administrador.', 'danger')
            return redirect(url_for('citas.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/usuarios')
@login_required
def usuarios():
    if not current_user.es_admin:
        flash('No tienes permisos de administrador.', 'danger')
        return redirect(url_for('citas.index'))
    
    try:
        usuarios = Usuario.obtener_todos()
        return render_template('admin/usuarios.html', usuarios=usuarios)
    except Exception as e:
        flash('Error al cargar los usuarios: ' + str(e), 'danger')
        return render_template('admin/usuarios.html', usuarios=[])

@admin_bp.route('/reset_password/<int:id_usuario>', methods=['POST'])
@login_required
@admin_required
def reset_user_password(id_usuario):
    """Resetea la contraseña de un usuario"""
    try:
        # Evita que un admin se resetee su propia contraseña
        if id_usuario == current_user.id:
            return jsonify({
                'success': False,
                'message': 'No puedes resetear tu propia contraseña'
            }), 400
        
        new_password = Usuario.reset_password(id_usuario)
        SecurityLogger.log_password_reset(
            Usuario.get_by_id(id_usuario).username,
            current_user.username
        )
        return jsonify({
            'success': True,
            'password': new_password
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error al resetear la contraseña'
        }), 500

@admin_bp.route('/toggle_admin/<int:id_usuario>', methods=['POST'])
@login_required
@admin_required
def toggle_admin_status(id_usuario):
    """Cambia el estado de administrador de un usuario"""
    try:
        # Evita que un admin se quite sus propios privilegios
        if id_usuario == current_user.id:
            flash('No puedes modificar tus propios privilegios de administrador', 'danger')
            return redirect(url_for('admin.usuarios'))
        
        es_admin = Usuario.toggle_admin(id_usuario)
        estado = "agregados" if es_admin else "removidos"
        SecurityLogger.log_account_status_change(
            Usuario.get_by_id(id_usuario).username,
            f"Privilegios de admin {estado}",
            current_user.username
        )
        flash(f'Privilegios de administrador {estado} exitosamente', 'success')
    except Exception as e:
        flash('Error al cambiar privilegios de administrador', 'danger')
    
    return redirect(url_for('admin.usuarios'))

@admin_bp.route('/toggle_active/<int:id_usuario>', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(id_usuario):
    """Activa o desactiva un usuario"""
    try:
        # Evita que un admin se desactive a sí mismo
        if id_usuario == current_user.id:
            flash('No puedes desactivar tu propia cuenta', 'danger')
            return redirect(url_for('admin.usuarios'))
        
        activo = Usuario.toggle_active(id_usuario)
        estado = "activado" if activo else "desactivado"
        SecurityLogger.log_account_status_change(
            Usuario.get_by_id(id_usuario).username,
            f"Usuario {estado}",
            current_user.username
        )
        flash(f'Usuario {estado} exitosamente', 'success')
    except Exception as e:
        flash('Error al cambiar estado del usuario', 'danger')
    
    return redirect(url_for('admin.usuarios'))

