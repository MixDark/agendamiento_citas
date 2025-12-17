from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Cita, Paciente, Doctor
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from mysql.connector import Error
from app.routes.notification import EmailNotifier
from app import mysql
from flask import jsonify

citas_bp = Blueprint('citas', __name__)


@citas_bp.route('/')
@login_required
def index():
    # Si es admin, redirigir al panel de administración
    if current_user.es_admin:
        return redirect(url_for('admin.usuarios'))

    try:
        # Obtener parámetros de filtrado
        filter_type = request.args.get('filter_type', 'day')  # 'day' o 'month'

        # Obtener fecha actual para los selectores
        today = datetime.today()

        if filter_type == 'day':
            filter_date_str = request.args.get(
                'date', today.strftime('%Y-%m-%d'))
            filter_date = datetime.strptime(filter_date_str, '%Y-%m-%d').date()
            filter_month = today.strftime('%Y-%m')
            title = "Próximas citas"

            # Usar el método optimizado para filtrar por día
            filtered_citas = Cita.obtener_todas(
                fecha=filter_date
            )
        else:  # month
            filter_date_str = today.strftime('%Y-%m-%d')
            filter_date = today.date()
            filter_month_str = request.args.get(
                'month', today.strftime('%Y-%m'))
            filter_year, filter_month_num = map(
                int, filter_month_str.split('-'))
            title = "Próximas citas"

            # Usar el método optimizado para filtrar por mes
            filtered_citas = Cita.obtener_todas(
                año_mes=(filter_year, filter_month_num)
            )

        # Contar citas por estado
        total_citas = len(filtered_citas)
        programadas = 0
        completadas = 0
        canceladas = 0

        for cita in filtered_citas:
            # El estado está en la posición 6 según la salida de depuración
            estado = cita[6]

            if estado == 'programada':
                programadas += 1
            elif estado == 'completada':
                completadas += 1
            elif estado == 'cancelada':
                canceladas += 1

        return render_template(
            'citas/index.html',
            citas=filtered_citas,
            filter_type=filter_type,
            filter_date=filter_date_str,
            filter_month=filter_month_str if filter_type == 'month' else filter_month,
            title=title,
            total_citas=total_citas,
            programadas=programadas,
            completadas=completadas,
            canceladas=canceladas
        )

    except Exception as e:
        import traceback
        traceback.print_exc()  # Imprimir el stack trace para depuración
        flash('Error al cargar las citas: ' + str(e), 'danger')
        return render_template(
            'citas/index.html',
            citas=[],  # Pasar una lista vacía en caso de error
            filter_type='day',
            filter_date=today.strftime('%Y-%m-%d'),
            filter_month=today.strftime('%Y-%m'),
            title="Citas del día",
            total_citas=0,
            programadas=0,
            completadas=0,
            canceladas=0
        )


@citas_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    if request.method == 'POST':
        try:
            id_paciente = request.form['id_paciente']
            id_doctor = request.form['id_doctor']
            fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
            hora = datetime.strptime(request.form['hora'], '%H:%M').time()
            motivo = request.form['motivo']

            # Verificar disponibilidad
            cita_existente = Cita.verificar_disponibilidad(fecha, hora)
            if cita_existente:
                flash(f'Ya existe una cita programada para el {fecha} a las {hora}. '
                      'Por favor, seleccione otro horario.', 'danger')
                pacientes = Paciente.obtener_todos()
                doctores = Doctor.obtener_todos()
                today = datetime.now().strftime('%Y-%m-%d')
                return render_template('citas/nueva_cita.html',
                                       pacientes=pacientes,
                                       doctores=doctores,
                                       today=today)

            # Crear la cita
            cita = Cita.crear(id_paciente, id_doctor, fecha, hora, motivo)

            # Obtener del paciente y el doctor para la notificación
            paciente = Paciente.obtener_por_id(id_paciente)
            doctor = Doctor.obtener_por_id(id_doctor)

            if paciente and paciente.email:
                try:
                    # Inicializar el notificador de email
                    notifier = EmailNotifier()

                    # Enviar notificación
                    success, message = notifier.enviar_notificacion_cita(
                        email_paciente=paciente.email,
                        nombre_paciente=paciente.nombre_completo,
                        nombre_doctor=doctor.nombre_completo,
                        fecha=fecha,
                        hora=hora
                    )

                    if success:
                        flash(
                            'Cita creada exitosamente y notificación enviada', 'success')
                    else:
                        flash(
                            f'Cita creada exitosamente, pero hubo un problema con la notificación: {message}', 'warning')
                except Exception as e:
                    flash(
                        'Cita creada exitosamente, pero hubo un error al enviar la notificación: ' + str(e), 'warning')
            else:
                flash('Cita creada exitosamente, pero no se pudo enviar la notificación '
                      'porque el paciente no tiene correo electrónico registrado', 'warning')

            return redirect(url_for('citas.agendamiento'))

        except ValueError as e:
            flash('Error en el formato de fecha u hora', 'danger')
        except Exception as e:
            flash('Error al crear la cita: ' + str(e), 'danger')

    try:
        # Obtener datos necesarios para el formulario
        pacientes = Paciente.obtener_todos()
        doctores = Doctor.obtener_todos()
        today = datetime.now().strftime('%Y-%m-%d')

        return render_template('citas/nueva_cita.html',
                               pacientes=pacientes,
                               doctores=doctores,
                               today=today)
    except Exception as e:
        flash('Error al cargar los datos: ' + str(e), 'danger')
        return redirect(url_for('citas.agendamiento'))


@citas_bp.route('/<int:id_cita>/editar', methods=['GET', 'POST'])
@login_required
def editar(id_cita):
    if request.method == 'POST':
        try:
            fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
            hora = datetime.strptime(request.form['hora'], '%H:%M').time()
            motivo = request.form['motivo']
            estado = request.form['estado']

            # Verificar si ya existe una cita en esa fecha y hora (excluyendo la cita actual)
            cita_existente = Cita.verificar_disponibilidad(
                fecha, hora, excluir_id=id_cita)
            if cita_existente:
                flash(f'Ya existe otra cita programada para el {fecha} a las {hora}. '
                      'Por favor, seleccione otro horario.', 'danger')
                cita = Cita.obtener_por_id(id_cita)
                return render_template('citas/editar_cita.html', cita=cita)

            Cita.actualizar(id_cita, fecha, hora, motivo, estado)
            flash('Cita actualizada exitosamente', 'success')
            return redirect(url_for('citas.agendamiento'))

        except ValueError as e:
            flash('Error en el formato de fecha u hora', 'danger')
        except Error as e:
            if e.errno == 1062:
                flash(f'Ya existe otra cita programada para el {fecha} a las {hora}. '
                      'Por favor, seleccione otro horario.', 'danger')
            else:
                flash('Error al actualizar la cita: ' + str(e), 'danger')
        except Exception as e:
            flash('Error al actualizar la cita: ' + str(e), 'danger')

    try:
        cita = Cita.obtener_por_id(id_cita)
        if not cita:
            flash('Cita no encontrada', 'danger')
            return redirect(url_for('citas.agendamiento'))
        return render_template('citas/editar_cita.html', cita=cita)
    except Exception as e:
        flash('Error al cargar la cita: ' + str(e), 'danger')
        return redirect(url_for('citas.agendamiento'))


@citas_bp.route('/<int:id_cita>/eliminar', methods=['POST'])
@login_required
def eliminar(id_cita):
    try:
        cita = Cita.obtener_por_id(id_cita)
        if not cita:
            flash('Cita no encontrada', 'danger')
            return redirect(url_for('citas.agendamiento'))

        Cita.eliminar(id_cita)
        flash('Cita eliminada exitosamente', 'success')
        return redirect(url_for('citas.agendamiento'))
    except Exception as e:
        flash('Error al eliminar la cita: ' + str(e), 'danger')
    return redirect(url_for('citas.agendamiento'))


@citas_bp.route('/agendamiento')
@login_required
def agendamiento():
    cur = mysql.connection.cursor()
    try:
        # Obtener solo las citas programadas
        cur.execute('''
            SELECT 
                c.id_cita,
                c.fecha,
                c.hora,
                c.estado,
                c.motivo,
                p.nombre,
                p.apellido,
                d.nombre,
                d.apellido         
            FROM citas c 
            JOIN pacientes p ON c.id_paciente = p.id_paciente 
            JOIN doctores d ON c.id_doctor = d.id_doctor        
            WHERE c.estado = 'programada'
            ORDER BY c.fecha DESC, c.hora DESC
        ''')
        citas = cur.fetchall()
        return render_template('citas/agendamiento.html', citas=citas)
    finally:
        cur.close()
