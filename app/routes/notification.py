from flask_mail import Mail, Message
from flask import current_app


class EmailNotifier:
    def __init__(self):
        self.mail = Mail(current_app)

    def enviar_notificacion_cita(self, email_paciente, nombre_paciente, nombre_doctor, fecha, hora):
        try:
            fecha_formateada = fecha.strftime("%d/%m/%Y")
            hora_formateada = hora.strftime("%H:%M")

            # Crear el mensaje HTML
            html_content = f"""
            <html>
                <body>
                    <p>Hola {nombre_paciente},</p>
                    <p>Su cita médica ha sido programada para el <strong>{fecha_formateada}</strong> 
                    a las <strong>{hora_formateada}</strong> con el profresional <strong>{nombre_doctor}</strong>.</p>
                    <h3>Información importante:</h3>
                    <ul>
                        <li>Llegue 10 minutos antes de su cita</li>
                        <li>Traiga su documento de identidad</li>
                        <li>Si no puede asistir, por favor cancele su cita con anticipación</li>
                    </ul>
                    <p>Saludos cordiales,<br>
                    Isis Med</p>
                </body>
            </html>
            """

            msg = Message(
                subject="Confirmación de cita médica",
                recipients=[email_paciente],
                html=html_content,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )

            self.mail.send(msg)
            return True, "Notificación enviada exitosamente"

        except Exception as e:
            return False, f"Error al enviar notificación: {str(e)}"