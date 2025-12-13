from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Doctor
from flask_login import login_required
from datetime import datetime
from app import mysql

doctores_bp = Blueprint('doctores', __name__)

@doctores_bp.route('/')
@login_required
def index():
    cur = mysql.connection.cursor()
    try:
        cur.execute('SELECT * FROM doctores ORDER BY apellido, nombre')
        doctores = cur.fetchall()
        return render_template('doctores/index.html', doctores=doctores)
    finally:
        cur.close()

@doctores_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        cedula = request.form['cedula']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        telefono = request.form['telefono']
        
        try:
            Doctor.crear(cedula, nombre, apellido, telefono)
            flash('Doctor registrado exitosamente', 'success')
            return redirect(url_for('citas.nueva'))
        except Exception as e:
            flash('Error al registrar el doctor: ' + str(e), 'danger')
    
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('doctores/nuevo_doctor.html', today=today)

@doctores_bp.route('/editar/<int:id_doctor>', methods=['GET', 'POST'])
@login_required
def editar(id_doctor):
    cur = mysql.connection.cursor()
    try:
        if request.method == 'POST':
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            telefono = request.form['telefono']
            
            cur.execute('''
                UPDATE doctores 
                SET nombre = %s, 
                    apellido = %s, 
                    telefono = %s
                WHERE id_doctor = %s
            ''', (nombre, apellido, telefono, id_doctor))
            
            mysql.connection.commit()
            flash('Doctor actualizado exitosamente', 'success')
            return redirect(url_for('citas.nueva'))
        
        cur.execute('''
            SELECT id_doctor, nombre, apellido, telefono 
            FROM doctores 
            WHERE id_doctor = %s
        ''', (id_doctor,))
        
        doctor = cur.fetchone()
        
        if doctor is None:
            flash('Doctor no encontrado', 'danger')
            return redirect(url_for('citas.nueva'))
        
        doctor_data = list(doctor)
        
        return render_template('doctores/editar_doctor.html', 
                             doctor=doctor_data,
                             today=datetime.now().strftime('%Y-%m-%d'))
                             
    except Exception as e:
        flash('Error al procesar la solicitud: ' + str(e), 'danger')
        return redirect(url_for('citas.nueva'))
        
    finally:
        if cur:
            cur.close()