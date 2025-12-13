from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from app import mysql
import io
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from flask import send_file, jsonify
from datetime import datetime, timedelta, date, time

historico_bp = Blueprint('historico', __name__)


@historico_bp.route('/fecha')
@login_required
def historico_fecha():
    # Obtener parámetros de filtro
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')

    # Si no hay filtros aplicados, mostrar la página sin datos
    if not fecha_inicio and not fecha_fin:
        return render_template('historico/historico_fecha.html', citas=None)

    # Si hay filtros, consultar la base de datos
    cur = mysql.connection.cursor()
    try:
        # Construir la consulta base
        query = '''
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
            WHERE c.estado IN ('Completada', 'Cancelada')
        '''

        params = []

        # Añadir filtros si se proporcionaron
        if fecha_inicio:
            query += " AND c.fecha >= %s"
            params.append(fecha_inicio)

        if fecha_fin:
            query += " AND c.fecha <= %s"
            params.append(fecha_fin)

        # Ordenar los resultados
        query += " ORDER BY c.fecha DESC, c.hora DESC"

        # Ejecutar la consulta
        cur.execute(query, params)
        citas = cur.fetchall()

        return render_template('historico/historico_fecha.html', citas=citas,
                               fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    finally:
        cur.close()


@historico_bp.route('/paciente')
@login_required
def historico_paciente():
    cur = mysql.connection.cursor()
    try:
        # Obtener la lista de pacientes para el selector
        cur.execute('''
            SELECT id_paciente, nombre, apellido 
            FROM pacientes
            ORDER BY apellido, nombre
        ''')
        pacientes = cur.fetchall()
        return render_template('historico/historico_paciente.html', pacientes=pacientes)
    finally:
        cur.close()


@historico_bp.route('/doctor')
@login_required
def historico_doctor():
    cur = mysql.connection.cursor()
    try:
        # Obtener la lista de doctores para el selector
        cur.execute('''
            SELECT id_doctor, nombre, apellido 
            FROM doctores
            ORDER BY apellido, nombre
        ''')
        doctores = cur.fetchall()
        return render_template('historico/historico_doctor.html', doctores=doctores)
    finally:
        cur.close()


@historico_bp.route('/api/paciente/<int:paciente_id>')
@login_required
def api_historico_paciente(paciente_id):
    cur = mysql.connection.cursor()
    try:
        cur.execute('''
            SELECT 
                c.id_cita,
                DATE_FORMAT(c.fecha, '%%d/%%m/%%Y') as fecha,
                c.hora,
                c.estado,
                c.motivo,
                CONCAT(p.nombre, ' ', p.apellido) as paciente,
                CONCAT(d.nombre, ' ', d.apellido) as doctor    
            FROM citas c 
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN doctores d ON c.id_doctor = d.id_doctor          
            WHERE c.id_paciente = %s AND c.estado IN ('Completada', 'Cancelada')
            ORDER BY c.fecha DESC, c.hora DESC
        ''', (paciente_id,))

        # Obtener los nombres de las columnas
        columns = [desc[0] for desc in cur.description]

        # Convertir los resultados a una lista de diccionarios
        citas = []
        for row in cur.fetchall():
            # Crear un diccionario para esta fila
            cita = {}

            # Procesar cada columna
            for i, value in enumerate(row):
                column_name = columns[i]

                # Manejar tipos de datos especiales
                if isinstance(value, timedelta):
                    # Convertir timedelta a formato de hora (HH:MM)
                    total_seconds = int(value.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    cita[column_name] = f"{hours:02d}:{minutes:02d}"
                elif isinstance(value, (datetime, date)):
                    # Formatear fechas si es necesario
                    cita[column_name] = value.strftime('%d/%m/%Y')
                elif isinstance(value, time):
                    # Formatear horas si es necesario
                    cita[column_name] = value.strftime('%H:%M')
                else:
                    # Valores normales
                    cita[column_name] = value

            citas.append(cita)

        return jsonify(citas)
    except Exception as e:
        print(f"Error en api_historico_paciente: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


@historico_bp.route('/api/doctor/<int:doctor_id>')
@login_required
def api_historico_doctor(doctor_id):
    cur = mysql.connection.cursor()
    try:
        cur.execute('''
            SELECT 
                c.id_cita,
                DATE_FORMAT(c.fecha, '%%d/%%m/%%Y') as fecha,
                c.hora,
                c.estado,
                c.motivo,
                CONCAT(p.nombre, ' ', p.apellido) as paciente,
                CONCAT(d.nombre, ' ', d.apellido) as doctor    
            FROM citas c 
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN doctores d ON c.id_doctor = d.id_doctor          
            WHERE c.id_doctor = %s AND c.estado IN ('Completada', 'Cancelada')
            ORDER BY c.fecha DESC, c.hora DESC
        ''', (doctor_id,))

        # Obtener los nombres de las columnas
        columns = [desc[0] for desc in cur.description]

        # Convertir los resultados a una lista de diccionarios
        citas = []
        for row in cur.fetchall():
            # Crear un diccionario para esta fila
            cita = {}

            # Procesar cada columna
            for i, value in enumerate(row):
                column_name = columns[i]

                # Manejar tipos de datos especiales
                if isinstance(value, timedelta):
                    # Convertir timedelta a formato de hora (HH:MM)
                    total_seconds = int(value.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    cita[column_name] = f"{hours:02d}:{minutes:02d}"
                elif isinstance(value, (datetime, date)):
                    # Formatear fechas si es necesario
                    cita[column_name] = value.strftime('%d/%m/%Y')
                elif isinstance(value, time):
                    # Formatear horas si es necesario
                    cita[column_name] = value.strftime('%H:%M')
                else:
                    # Valores normales
                    cita[column_name] = value

            citas.append(cita)

        return jsonify(citas)
    except Exception as e:
        print(f"Error en api_historico_doctor: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


@historico_bp.route('/exportar/doctor/<int:doctor_id>')
@login_required
def exportar_excel_doctor(doctor_id):
    try:
        # Obtener información del doctor
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT nombre, apellido FROM doctores WHERE id_doctor = %s', (doctor_id,))
        doctor_info = cur.fetchone()

        if not doctor_info:
            return jsonify({"error": "Doctor no encontrado"}), 404

        doctor_nombre = f"{doctor_info[0]} {doctor_info[1]}"

        # Obtener las citas
        cur.execute('''
            SELECT 
                c.id_cita,
                DATE_FORMAT(c.fecha, '%%d/%%m/%%Y') as fecha,
                c.hora,
                c.estado,
                c.motivo,
                CONCAT(p.nombre, ' ', p.apellido) as paciente,
                CONCAT(d.nombre, ' ', d.apellido) as doctor    
            FROM citas c 
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN doctores d ON c.id_doctor = d.id_doctor          
            WHERE c.id_doctor = %s AND c.estado IN ('completada', 'cancelada')
            ORDER BY c.fecha DESC, c.hora DESC
        ''', (doctor_id,))

        citas = cur.fetchall()
        cur.close()

        # Generar el Excel
        titulo = f"Histórico de citas - Dr. {doctor_nombre}"
        nombre_archivo = f"Historico_Doctor_{doctor_info[1]}_{doctor_info[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return generar_excel_historico(citas, titulo, nombre_archivo)

    except Exception as e:
        print(f"Error al exportar a Excel: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@historico_bp.route('/exportar/paciente/<int:paciente_id>')
@login_required
def exportar_excel_paciente(paciente_id):
    try:
        # Obtener información del paciente
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT nombre, apellido FROM pacientes WHERE id_paciente = %s', (paciente_id,))
        paciente_info = cur.fetchone()

        if not paciente_info:
            return jsonify({"error": "Paciente no encontrado"}), 404

        paciente_nombre = f"{paciente_info[0]} {paciente_info[1]}"

        # Obtener las citas
        cur.execute('''
            SELECT 
                c.id_cita,
                DATE_FORMAT(c.fecha, '%%d/%%m/%%Y') as fecha,
                c.hora,
                c.estado,
                c.motivo,
                CONCAT(p.nombre, ' ', p.apellido) as paciente,
                CONCAT(d.nombre, ' ', d.apellido) as doctor    
            FROM citas c 
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN doctores d ON c.id_doctor = d.id_doctor          
            WHERE c.id_paciente = %s AND c.estado IN ('completada', 'cancelada')
            ORDER BY c.fecha DESC, c.hora DESC
        ''', (paciente_id,))

        citas = cur.fetchall()
        cur.close()

        # Generar el Excel
        titulo = f"Histórico de citas - Paciente: {paciente_nombre}"
        nombre_archivo = f"Historico_Paciente_{paciente_info[1]}_{paciente_info[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return generar_excel_historico(citas, titulo, nombre_archivo)

    except Exception as e:
        print(f"Error al exportar a Excel: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@historico_bp.route('/exportar/fecha')
@login_required
def exportar_excel_fecha():
    try:
        # Obtener parámetros de fecha
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')

        if not fecha_inicio or not fecha_fin:
            return jsonify({"error": "Se requieren ambas fechas"}), 400

        # Convertir a objetos de fecha
        try:
            fecha_inicio_obj = datetime.strptime(
                fecha_inicio, '%Y-%m-%d').date()
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido"}), 400

        # Obtener las citas para el rango de fechas
        cur = mysql.connection.cursor()
        cur.execute('''
            SELECT 
                c.id_cita,
                DATE_FORMAT(c.fecha, '%%d/%%m/%%Y') as fecha,
                c.hora,
                c.estado,
                c.motivo,
                CONCAT(p.nombre, ' ', p.apellido) as paciente,
                CONCAT(d.nombre, ' ', d.apellido) as doctor    
            FROM citas c 
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN doctores d ON c.id_doctor = d.id_doctor          
            WHERE c.fecha BETWEEN %s AND %s AND c.estado IN ('completada', 'cancelada')
            ORDER BY c.fecha DESC, c.hora DESC
        ''', (fecha_inicio_obj, fecha_fin_obj))

        citas = cur.fetchall()
        cur.close()

        # Generar el Excel
        titulo = f"Histórico de citas - Período: {fecha_inicio} al {fecha_fin}"
        nombre_archivo = f"Historico_Citas_{fecha_inicio}_{fecha_fin}.xlsx"

        return generar_excel_historico(citas, titulo, nombre_archivo)

    except Exception as e:
        print(f"Error al exportar a Excel: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def generar_excel_historico(datos, titulo, nombre_archivo):
    """
    Función auxiliar para generar un archivo Excel con el histórico de citas

    Args:
        datos: Lista de tuplas con los datos de las citas
        titulo: Título del reporte
        nombre_archivo: Nombre del archivo a generar

    Returns:
        Respuesta Flask con el archivo Excel adjunto
    """
    try:
        # Crear un nuevo libro de Excel
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Histórico de citas"

        # Estilos
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(
            start_color="0066CC", end_color="0066CC", fill_type="solid")
        centered = Alignment(horizontal="center", vertical="center")

        # Título del reporte
        ws.merge_cells('A1:F1')
        ws['A1'] = titulo
        ws['A1'].font = Font(bold=True, size=14)
        ws['A1'].alignment = Alignment(horizontal="center")

        # Fecha de generación
        ws.merge_cells('A2:F2')
        ws['A2'] = f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        ws['A2'].alignment = Alignment(horizontal="right")

        # Encabezados
        headers = ["Fecha", "Hora", "Paciente", "Doctor", "Motivo", "Estado"]
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=4, column=col_num)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = centered

        # Datos
        if not datos:
            ws.merge_cells('A5:F5')
            ws['A5'] = "No hay registros históricos"
            ws['A5'].alignment = Alignment(horizontal="center")
        else:
            for row_num, cita in enumerate(datos, 5):
                # Fecha
                ws.cell(row=row_num, column=1).value = cita[1]

                # Hora (formatear si es un objeto timedelta)
                hora = cita[2]
                if isinstance(hora, timedelta):
                    total_seconds = int(hora.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    hora_str = f"{hours:02d}:{minutes:02d}"
                else:
                    hora_str = str(hora)
                ws.cell(row=row_num, column=2).value = hora_str

                # Paciente
                ws.cell(row=row_num, column=3).value = cita[5]

                # Doctor
                ws.cell(row=row_num, column=4).value = cita[6]

                # Motivo
                ws.cell(row=row_num, column=5).value = cita[4]

                # Estado
                estado_cell = ws.cell(row=row_num, column=6)
                estado_cell.value = cita[3]

                # Color según el estado
                if cita[3].lower() == 'completada':
                    estado_cell.fill = PatternFill(
                        start_color="90EE90", end_color="90EE90", fill_type="solid")
                elif cita[3].lower() == 'cancelada':
                    estado_cell.fill = PatternFill(
                        start_color="FFC0CB", end_color="FFC0CB", fill_type="solid")

        # Ajustar anchos de columna
        column_widths = {}

        # Calcular el ancho máximo para cada columna
        for row in ws.rows:
            for cell in row:
                if cell.value:
                    # Obtener la columna solo si no es una celda combinada
                    if not isinstance(cell, openpyxl.cell.cell.MergedCell):
                        col_letter = cell.column_letter
                        # Inicializar si es la primera vez que vemos esta columna
                        if col_letter not in column_widths:
                            column_widths[col_letter] = 0
                        # Actualizar el ancho máximo
                        column_widths[col_letter] = max(
                            column_widths[col_letter], len(str(cell.value)))

        # Aplicar los anchos calculados
        for col_letter, width in column_widths.items():
            ws.column_dimensions[col_letter].width = width + 2

        # Guardar a un buffer en memoria
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        # Enviar el archivo
        return send_file(
            output,
            as_attachment=True,
            download_name=nombre_archivo,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        print(f"Error al generar Excel: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
