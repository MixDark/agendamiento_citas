from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Paciente
from flask_login import login_required
from datetime import datetime
from app import mysql

pacientes_bp = Blueprint('pacientes', __name__)

@pacientes_bp.route('/')
@login_required
def index():
    cur = mysql.connection.cursor()
    try:
        cur.execute('SELECT * FROM pacientes ORDER BY apellido, nombre')
        pacientes = cur.fetchall()
        return render_template('pacientes/index.html', pacientes=pacientes)
    finally:
        cur.close()

@pacientes_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        cedula = request.form['cedula']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        telefono = request.form['telefono']
        email = request.form['email']
        fecha_nacimiento = request.form['fecha_nacimiento']
        
        try:
            Paciente.crear(cedula,nombre, apellido, telefono, email, fecha_nacimiento)
            flash('Paciente registrado exitosamente', 'success')
            return redirect(url_for('pacientes.index'))
        except Exception as e:
            flash('Error al registrar el paciente: ' + str(e), 'danger')
    
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('pacientes/nuevo_paciente.html', today=today)

@pacientes_bp.route('/editar/<int:id_paciente>', methods=['GET', 'POST'])
@login_required
def editar(id_paciente):
    cur = mysql.connection.cursor()
    try:
        if request.method == 'POST':
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            telefono = request.form['telefono']
            email = request.form['email']
            fecha_nacimiento = request.form['fecha_nacimiento']
            
            cur.execute('''
                UPDATE pacientes 
                SET nombre = %s, 
                    apellido = %s, 
                    telefono = %s, 
                    email = %s, 
                    fecha_nacimiento = %s
                WHERE id_paciente = %s
            ''', (nombre, apellido, telefono, email, fecha_nacimiento, id_paciente))
            
            mysql.connection.commit()
            flash('Paciente actualizado exitosamente', 'success')
            return redirect(url_for('pacientes.index'))
        
        cur.execute('''
            SELECT id_paciente, nombre, apellido, telefono, email, fecha_nacimiento 
            FROM pacientes 
            WHERE id_paciente = %s
        ''', (id_paciente,))
        
        paciente = cur.fetchone()
        
        if paciente is None:
            flash('Paciente no encontrado', 'danger')
            return redirect(url_for('pacientes.index'))
        
        paciente_data = list(paciente)
        
        return render_template('pacientes/editar_paciente.html', 
                             paciente=paciente_data,
                             today=datetime.now().strftime('%Y-%m-%d'))
                             
    except Exception as e:
        flash('Error al procesar la solicitud: ' + str(e), 'danger')
        return redirect(url_for('pacientes.index'))
        
    finally:
        if cur:
            cur.close()
@pacientes_bp.route('/eliminar/<int:id_paciente>', methods=['POST'])
@login_required
def eliminar(id_paciente):
    cur = mysql.connection.cursor()
    try:
        cur.execute('DELETE FROM pacientes WHERE id_paciente = %s', (id_paciente,))
        mysql.connection.commit()
        flash('Paciente eliminado exitosamente', 'success')
    except Exception as e:
        flash('Error al eliminar el paciente: ' + str(e), 'danger')
    finally:
        cur.close()
    
    return redirect(url_for('pacientes.index'))