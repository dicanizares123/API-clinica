"""
Servicio para envío de correos electrónicos.
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Servicio centralizado para envío de emails.
    """
    
    @staticmethod
    def send_appointment_confirmation(appointment):
        """
        Envía email de confirmación cuando se agenda una cita.
        Se envía al paciente.
        """
        patient = appointment.patient
        doctor = appointment.doctor_specialist.doctor
        specialty = appointment.doctor_specialist.specialty
        
        subject = '✅ Cita Agendada Exitosamente - Clínica'
        
        # Datos para el template
        context = {
            'patient_name': patient.get_full_name(),
            'doctor_name': doctor.get_full_name(),
            'specialty': specialty.name,
            'date': appointment.appointment_date.strftime('%d/%m/%Y'),
            'time': appointment.appointment_time.strftime('%H:%M'),
            'duration': appointment.duration_minutes,
            'appointment_uuid': str(appointment.uuid),
            'clinic_name': getattr(settings, 'SITE_NAME', 'Clínica'),
        }
        
        # HTML del email
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #10b981; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
                .appointment-details {{ background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #10b981; }}
                .detail-row {{ display: flex; margin: 10px 0; }}
                .detail-label {{ font-weight: bold; width: 120px; color: #6b7280; }}
                .detail-value {{ color: #111827; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
                .uuid {{ background-color: #e5e7eb; padding: 8px 12px; border-radius: 4px; font-family: monospace; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ ¡Cita Agendada!</h1>
                </div>
                <div class="content">
                    <p>Hola <strong>{context['patient_name']}</strong>,</p>
                    <p>Tu cita ha sido agendada exitosamente. A continuación los detalles:</p>
                    
                    <div class="appointment-details">
                        <div class="detail-row">
                            <span class="detail-label">📅 Fecha:</span>
                            <span class="detail-value">{context['date']}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">🕐 Hora:</span>
                            <span class="detail-value">{context['time']}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">👨‍⚕️ Doctor:</span>
                            <span class="detail-value">Dr(a). {context['doctor_name']}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">🏥 Especialidad:</span>
                            <span class="detail-value">{context['specialty']}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">⏱️ Duración:</span>
                            <span class="detail-value">{context['duration']} minutos</span>
                        </div>
                    </div>
                    
                    <p><strong>Código de tu cita:</strong></p>
                    <p class="uuid">{context['appointment_uuid']}</p>
                    
                    <p style="margin-top: 20px;">
                        <strong>Recomendaciones:</strong>
                    </p>
                    <ul>
                        <li>Llega 10 minutos antes de tu cita</li>
                        <li>Trae tu documento de identidad</li>
                        <li>Si necesitas cancelar, hazlo con al menos 24 horas de anticipación</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>{context['clinic_name']}</p>
                    <p>Este es un correo automático, por favor no responder.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Versión texto plano
        plain_message = f"""
¡Cita Agendada Exitosamente!

Hola {context['patient_name']},

Tu cita ha sido agendada exitosamente. Aquí están los detalles:

📅 Fecha: {context['date']}
🕐 Hora: {context['time']}
👨‍⚕️ Doctor: Dr(a). {context['doctor_name']}
🏥 Especialidad: {context['specialty']}
⏱️ Duración: {context['duration']} minutos

Código de tu cita: {context['appointment_uuid']}

Recomendaciones:
- Llega 10 minutos antes de tu cita
- Trae tu documento de identidad
- Si necesitas cancelar, hazlo con al menos 24 horas de anticipación

{context['clinic_name']}
        """
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[patient.email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Email de confirmación enviado a {patient.email}")
            return True
        except Exception as e:
            logger.error(f"Error enviando email a {patient.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_appointment_cancelled(appointment, cancelled_by=None):
        """
        Envía email cuando se cancela una cita.
        """
        patient = appointment.patient
        doctor = appointment.doctor_specialist.doctor
        
        subject = '❌ Cita Cancelada - Clínica'
        
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #ef4444; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>❌ Cita Cancelada</h1>
                </div>
                <div class="content">
                    <p>Hola <strong>{patient.get_full_name()}</strong>,</p>
                    <p>Tu cita ha sido cancelada:</p>
                    <ul>
                        <li><strong>Fecha:</strong> {appointment.appointment_date.strftime('%d/%m/%Y')}</li>
                        <li><strong>Hora:</strong> {appointment.appointment_time.strftime('%H:%M')}</li>
                        <li><strong>Doctor:</strong> Dr(a). {doctor.get_full_name()}</li>
                    </ul>
                    <p>Si deseas reagendar tu cita, puedes hacerlo a través de nuestra plataforma.</p>
                </div>
                <div class="footer">
                    <p>{getattr(settings, 'SITE_NAME', 'Clínica')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_message = f"""
Cita Cancelada

Hola {patient.get_full_name()},

Tu cita ha sido cancelada:
- Fecha: {appointment.appointment_date.strftime('%d/%m/%Y')}
- Hora: {appointment.appointment_time.strftime('%H:%M')}
- Doctor: Dr(a). {doctor.get_full_name()}

Si deseas reagendar tu cita, puedes hacerlo a través de nuestra plataforma.
        """
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[patient.email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Email de cancelación enviado a {patient.email}")
            return True
        except Exception as e:
            logger.error(f"Error enviando email de cancelación: {str(e)}")
            return False
    
    @staticmethod
    def send_appointment_reminder(appointment):
        """
        Envía recordatorio de cita (para usar con un job programado).
        """
        patient = appointment.patient
        doctor = appointment.doctor_specialist.doctor
        
        subject = '🔔 Recordatorio de Cita - Mañana'
        
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #3b82f6; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔔 Recordatorio de Cita</h1>
                </div>
                <div class="content">
                    <p>Hola <strong>{patient.get_full_name()}</strong>,</p>
                    <p>Te recordamos que tienes una cita programada para mañana:</p>
                    <ul>
                        <li><strong>Fecha:</strong> {appointment.appointment_date.strftime('%d/%m/%Y')}</li>
                        <li><strong>Hora:</strong> {appointment.appointment_time.strftime('%H:%M')}</li>
                        <li><strong>Doctor:</strong> Dr(a). {doctor.get_full_name()}</li>
                    </ul>
                    <p>¡Te esperamos!</p>
                </div>
                <div class="footer">
                    <p>{getattr(settings, 'SITE_NAME', 'Clínica')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_message = f"""
Recordatorio de Cita

Hola {patient.get_full_name()},

Te recordamos que tienes una cita programada para mañana:
- Fecha: {appointment.appointment_date.strftime('%d/%m/%Y')}
- Hora: {appointment.appointment_time.strftime('%H:%M')}
- Doctor: Dr(a). {doctor.get_full_name()}

¡Te esperamos!
        """
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[patient.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error(f"Error enviando recordatorio: {str(e)}")
            return False
