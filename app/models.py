from app import mysql
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
import random
import string

class Paciente:
    @staticmethod
    def obtener_todos():
        cur = mysql.connection.cursor()
        cur.execute('SELECT id_paciente, nombre, apellido FROM pacientes ORDER BY nombre, apellido')
        pacientes = cur.fetchall()
        cur.close()
        return pacientes
    
    def __init__(self, id_paciente, nombre, apellido, telefono, email, fecha_nacimiento):
        self.id_paciente = id_paciente
        self.nombre = nombre
        self.apellido = apellido
        self.telefono = telefono
        self.email = email
        self.fecha_nacimiento = fecha_nacimiento

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    @staticmethod
    def obtener_por_id(id_paciente):
        cur = mysql.connection.cursor()
        try:
            cur.execute('''
                SELECT 
                    p.id_paciente,
                    p.nombre,
                    p.apellido,
                    p.telefono,
                    p.email,
                    p.fecha_nacimiento
                FROM pacientes p
                WHERE p.id_paciente = %s
            ''', (id_paciente,))
            
            resultado = cur.fetchone()
            
            if resultado:
                # Crear objeto Paciente con los valores de la tupla
                return Paciente(
                    id_paciente=resultado[0],  # id_paciente
                    nombre=resultado[1],       # nombre
                    apellido=resultado[2],     # apellido
                    telefono=resultado[3],     # telefono
                    email=resultado[4],        # email
                    fecha_nacimiento=resultado[5]  # fecha_nacimiento
                )
            return None
            
        except Exception as e:
            print(f"Error al obtener paciente: {str(e)}")
            return None
        finally:
            cur.close()

    @staticmethod
    def crear(id_paciente,nombre, apellido, telefono, email, fecha_nacimiento):
        cur = mysql.connection.cursor()
        cur.execute('''
            INSERT INTO pacientes (id_paciente, nombre, apellido, telefono, email, fecha_nacimiento)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (id_paciente, nombre, apellido, telefono, email, fecha_nacimiento))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def actualizar(id_paciente, nombre, apellido, telefono, email, fecha_nacimiento):
        cur = None
        try:
            cur = mysql.connection.cursor()            
            cur.execute('''
                UPDATE pacientes 
                SET nombre = %s, 
                    apellido = %s, 
                    telefono = %s, 
                    email = %s, 
                    fecha_nacimiento = %s,
                    actualizado_en = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (nombre, apellido, telefono, email, fecha_nacimiento, id_paciente))
            mysql.connection.commit()
        finally:
            if cur:
                cur.close()      

class Doctor:
    @staticmethod
    def obtener_todos():
        """Obtiene todos los doctores ordenados por nombre y apellido"""
        cur = mysql.connection.cursor()
        try:
            cur.execute('SELECT id_doctor, nombre, apellido FROM doctores ORDER BY nombre, apellido')
            doctores = cur.fetchall()
            return doctores
        except Exception as e:
            print(f"Error al obtener todos los doctores: {str(e)}")
            return []
        finally:
            cur.close()
    
    def __init__(self, id_doctor, nombre, apellido, telefono):
        """Constructor de la clase Doctor"""
        self.id_doctor = id_doctor
        self.nombre = nombre
        self.apellido = apellido
        self.telefono = telefono

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    @staticmethod
    def obtener_por_id(id_doctor):
        """Obtiene un doctor por su ID"""
        cur = mysql.connection.cursor()
        try:
            cur.execute('''
                SELECT 
                    id_doctor,
                    nombre,
                    apellido,
                    telefono
                FROM doctores
                WHERE id_doctor = %s
            ''', (id_doctor,))
            
            resultado = cur.fetchone()
            
            if resultado:
                # Crear objeto Doctor con los valores de la tupla
                return Doctor(
                    id_doctor=resultado[0],
                    nombre=resultado[1],
                    apellido=resultado[2],
                    telefono=resultado[3]
                )
            return None
            
        except Exception as e:
            print(f"Error al obtener doctor: {str(e)}")
            return None
        finally:
            cur.close()

    @staticmethod
    def crear(id_doctor, nombre, apellido, telefono):
        """Crea un nuevo doctor en la base de datos"""
        cur = mysql.connection.cursor()
        try:
            cur.execute('''
                INSERT INTO doctores (id_doctor, nombre, apellido, telefono)
                VALUES (%s, %s, %s, %s)
            ''', (id_doctor, nombre, apellido, telefono))
            mysql.connection.commit()
            return cur.lastrowid  # Devuelve el ID del nuevo doctor
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al crear doctor: {str(e)}")
            return None
        finally:
            cur.close()

    @staticmethod
    def actualizar(id_doctor, nombre, apellido, telefono):
        """Actualiza los datos de un doctor existente"""
        cur = mysql.connection.cursor()
        try:
            cur.execute('''
                UPDATE doctores 
                SET nombre = %s, 
                    apellido = %s, 
                    telefono = %s, 
                    actualizado_en = CURRENT_TIMESTAMP
                WHERE id_doctor = %s
            ''', (nombre, apellido, telefono, id_doctor))
            mysql.connection.commit()
            return cur.rowcount > 0  # Devuelve True si se actualizó algún registro
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al actualizar doctor: {str(e)}")
            return False
        finally:
            cur.close()            
            
    @staticmethod
    def buscar(termino):
        """Busca doctores por nombre o apellido"""
        cur = mysql.connection.cursor()
        try:
            cur.execute('''
                SELECT id_doctor, nombre, apellido, telefono
                FROM doctores
                WHERE nombre LIKE %s OR apellido LIKE %s
                ORDER BY nombre, apellido
            ''', (f'%{termino}%', f'%{termino}%'))
            
            resultados = cur.fetchall()
            doctores = []
            
            for resultado in resultados:
                doctores.append(Doctor(
                    id_doctor=resultado[0],
                    nombre=resultado[1],
                    apellido=resultado[2],
                    telefono=resultado[3]
                ))
                
            return doctores
        except Exception as e:
            print(f"Error al buscar doctores: {str(e)}")
            return []
        finally:
            cur.close()
            
    @staticmethod
    def verificar_disponibilidad(id_doctor, fecha, hora):
        """Verifica si un doctor está disponible en una fecha y hora específicas"""
        cur = mysql.connection.cursor()
        try:
            # Verificar si ya tiene una cita en ese horario
            cur.execute('''
                SELECT COUNT(*) 
                FROM citas 
                WHERE id_doctor = %s AND fecha = %s AND hora = %s
            ''', (id_doctor, fecha, hora))
            
            count = cur.fetchone()[0]
            return count == 0  # Disponible si no hay citas
        except Exception as e:
            print(f"Error al verificar disponibilidad: {str(e)}")
            return False
        finally:
            cur.close() 

class Cita:
    @staticmethod
    def obtener_todas(fecha=None, año_mes=None):
        cur = mysql.connection.cursor()
        
        # Base de la consulta
        query = '''
            SELECT c.id_cita, p.nombre, p.apellido, c.fecha, c.hora, 
                c.motivo, c.estado, d.nombre, d.apellido
            FROM citas c
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN doctores d ON c.id_doctor = d.id_doctor
            WHERE 1=1
        '''
        
        params = []
                
        # Filtrar por fecha exacta
        if fecha is not None:
            query += ' AND c.fecha = %s'
            params.append(fecha)
        
        # Filtrar por año y mes
        if año_mes is not None:
            año, mes = año_mes
            query += ' AND YEAR(c.fecha) = %s AND MONTH(c.fecha) = %s'
            params.extend([año, mes])
        
        # Ordenar los resultados
        query += ' ORDER BY c.fecha ASC, c.hora ASC'
        
        # Ejecutar la consulta
        cur.execute(query, tuple(params))
        
        citas = cur.fetchall()
        cur.close()
        return citas

    @staticmethod
    def verificar_disponibilidad(fecha, hora, excluir_id=None):
        """Verifica si existe una cita en la fecha y hora especificadas"""
        cur = mysql.connection.cursor()
        try:
            if excluir_id:
                cur.execute('''
                    SELECT COUNT(*) FROM citas 
                    WHERE fecha = %s AND hora = %s AND id_cita != %s
                ''', (fecha, hora, excluir_id))
            else:
                cur.execute('''
                    SELECT COUNT(*) FROM citas 
                    WHERE fecha = %s AND hora = %s
                ''', (fecha, hora))
            
            count = cur.fetchone()[0]
            return count > 0
        finally:
            cur.close()

    @staticmethod
    def crear(id_paciente, id_doctor, fecha, hora, motivo):
        # Primero verificar disponibilidad
        if Cita.verificar_disponibilidad(fecha, hora):
            raise ValueError(f'Ya existe una cita programada para el {fecha} a las {hora}')
        
        cur = mysql.connection.cursor()
        try:
            cur.execute('''
                INSERT INTO citas (id_paciente, id_doctor, fecha, hora, motivo, estado)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (id_paciente, id_doctor, fecha, hora, motivo, 'programada'))
            mysql.connection.commit()
        finally:
            cur.close()

    @staticmethod
    def actualizar(id_cita, fecha, hora, motivo, estado):
        # Verificar disponibilidad excluyendo la cita actual
        if Cita.verificar_disponibilidad(fecha, hora, excluir_id=id_cita):
            raise ValueError(f'Ya existe una cita programada para el {fecha} a las {hora}')
        
        cur = mysql.connection.cursor()
        try:
            cur.execute('''
                UPDATE citas 
                SET fecha=%s, hora=%s, motivo=%s, estado=%s
                WHERE id_cita=%s
            ''', (fecha, hora, motivo, estado, id_cita))
            mysql.connection.commit()
        finally:
            cur.close()

    @staticmethod
    def eliminar(id_cita):
        cur = mysql.connection.cursor()
        try:
            cur.execute('DELETE FROM citas WHERE id_cita=%s', (id_cita,))
            mysql.connection.commit()
        finally:
            cur.close()

    @staticmethod
    def obtener_por_id(id_cita):
        cur = mysql.connection.cursor()
        try:
            cur.execute('''
                SELECT 
                    c.id_cita,          -- 0
                    c.id_paciente,      -- 1
                    c.fecha,            -- 2
                    c.hora,             -- 3
                    c.motivo,           -- 4
                    c.estado,           -- 5
                    c.created_at,       -- 6
                    p.nombre,           -- 7
                    p.apellido,         -- 8
                    c.id_doctor,        -- 9
                    d.nombre,           -- 10
                    d.apellido          -- 11
                FROM citas c
                JOIN pacientes p ON c.id_paciente = p.id_paciente
                JOIN doctores d ON c.id_doctor = d.id_doctor
                WHERE c.id_cita = %s
            ''', (id_cita,))
            return cur.fetchone()
        finally:
            cur.close()

    @staticmethod
    def obtener_pacientes_con_citas():
        """
        Obtiene la lista de pacientes que han tenido citas
        """
        cur = mysql.connection.cursor()
        try:
            cur.execute('''
                SELECT DISTINCT 
                    p.id_paciente, 
                    p.nombre, 
                    p.apellido
                FROM pacientes p
                JOIN citas c ON p.id_paciente = c.id_paciente
                ORDER BY p.nombre, p.apellido
            ''')
            return cur.fetchall()
        finally:
            cur.close()            

class Usuario(UserMixin):
    def __init__(self, id, username, nombre, es_admin=False, activo=True):
        self.id = id
        self.username = username
        self.nombre = nombre
        self.es_admin = bool(es_admin) 
        self.activo = bool(activo)

    @property
    def is_admin(self):
        return self.es_admin  # Retornar es_admin para compatibilidad con el template

    @property
    def is_active(self):
        return self.activo

    @staticmethod
    def get_by_id(user_id):
        cur = mysql.connection.cursor()
        try:
            cur.execute('SELECT id_usuario, username, nombre, es_admin, activo FROM usuarios WHERE id_usuario = %s', (user_id,))
            user_data = cur.fetchone()
            if user_data:
                return Usuario(
                    id=user_data[0],
                    username=user_data[1],
                    nombre=user_data[2],
                    es_admin=user_data[3],
                    activo=user_data[4]
                )
            return None
        finally:
            cur.close()

    @staticmethod
    def get_by_username(username):
        cur = mysql.connection.cursor()
        try:
            cur.execute('SELECT * FROM usuarios WHERE username = %s', (username,))
            user_data = cur.fetchone()
            if user_data:
                return Usuario(
                    id=user_data[0],
                    username=user_data[1],
                    nombre=user_data[3],
                    es_admin=user_data[4],
                    activo=user_data[5]
                )
            return None
        finally:
            cur.close()

    @staticmethod
    def verify_password(username, password):
        cur = mysql.connection.cursor()
        try:
            cur.execute('SELECT password_hash FROM usuarios WHERE username = %s', (username,))
            result = cur.fetchone()
            if result:
                return check_password_hash(result[0], password)
            return False
        finally:
            cur.close()

    @staticmethod
    def generate_random_password(length=8):
        """Genera una contraseña aleatoria"""
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for i in range(length))

    @staticmethod
    def reset_password(user_id):
        """Resetea la contraseña de un usuario y retorna la nueva contraseña"""
        cur = mysql.connection.cursor()
        try:
            # Genera nueva contraseña
            new_password = Usuario.generate_random_password()
            password_hash = generate_password_hash(new_password)
            
            # Actualiza la contraseña y marca para cambio obligatorio
            cur.execute('''
                UPDATE usuarios 
                SET password_hash = %s, requiere_cambio_password = TRUE 
                WHERE id_usuario = %s
            ''', (password_hash, user_id))
            
            mysql.connection.commit()
            return new_password
        except Exception as e:
            mysql.connection.rollback()
            raise e
        finally:
            cur.close()

    @staticmethod
    def toggle_admin(user_id):
        """Cambia el estado de administrador de un usuario"""
        cur = mysql.connection.cursor()
        try:
            # Primero obtiene el estado actual
            cur.execute('SELECT es_admin FROM usuarios WHERE id_usuario = %s', (user_id,))
            result = cur.fetchone()
            if not result:
                raise ValueError("Usuario no encontrado")
            
            nuevo_estado = not result[0]
            
            # Actualiza el estado
            cur.execute('''
                UPDATE usuarios 
                SET es_admin = %s 
                WHERE id_usuario = %s
            ''', (nuevo_estado, user_id))
            
            mysql.connection.commit()
            return nuevo_estado
        except Exception as e:
            mysql.connection.rollback()
            raise e
        finally:
            cur.close()

    @staticmethod
    def toggle_active(user_id):
        """Activa o desactiva un usuario"""
        cur = mysql.connection.cursor()
        try:
            # Primero obtiene el estado actual
            cur.execute('SELECT activo FROM usuarios WHERE id_usuario = %s', (user_id,))
            result = cur.fetchone()
            if not result:
                raise ValueError("Usuario no encontrado")
            
            nuevo_estado = not result[0]
            
            # Actualiza el estado
            cur.execute('''
                UPDATE usuarios 
                SET activo = %s 
                WHERE id_usuario = %s
            ''', (nuevo_estado, user_id))
            
            mysql.connection.commit()
            return nuevo_estado
        except Exception as e:
            mysql.connection.rollback()
            raise e
        finally:
            cur.close()

    @staticmethod
    def obtener_todos():
        """Obtiene todos los usuarios"""
        cur = mysql.connection.cursor()
        try:
            cur.execute('''
                SELECT id_usuario, username, nombre, es_admin, activo 
                FROM usuarios 
                ORDER BY nombre
            ''')
            return cur.fetchall()
        finally:
            cur.close()

    @staticmethod
    def requiere_cambio_password(username):
        """Verifica si el usuario necesita cambiar su contraseña"""
        cur = mysql.connection.cursor()
        try:
            cur.execute('SELECT requiere_cambio_password FROM usuarios WHERE username = %s', (username,))
            result = cur.fetchone()
            return result[0] if result else False
        finally:
            cur.close()

    @staticmethod
    def cambiar_password(user_id, new_password):
        """Cambia la contraseña de un usuario y resetea el flag de cambio requerido"""
        cur = mysql.connection.cursor()
        try:
            password_hash = generate_password_hash(new_password)
            cur.execute('''
                UPDATE usuarios 
                SET password_hash = %s, requiere_cambio_password = FALSE 
                WHERE id_usuario = %s
            ''', (password_hash, user_id))
            
            mysql.connection.commit()
            return True
        except Exception as e:
            mysql.connection.rollback()
            raise e
        finally:
            cur.close()