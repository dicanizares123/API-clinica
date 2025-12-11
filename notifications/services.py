"""
Servicios para crear notificaciones automáticamente.
"""
from .models import Notification


class NotificationService:
    """
    Servicio para crear notificaciones de manera centralizada.
    """
    
    @staticmethod
    def notify_new_appointment(appointment):
        """
        Crea notificación cuando se agenda una nueva cita.
        Notifica al doctor asignado.
        """
        doctor = appointment.doctor_specialist.doctor
        user = doctor.user
        
        patient_name = appointment.patient.get_full_name()
        date_str = appointment.appointment_date.strftime('%d/%m/%Y')
        time_str = appointment.appointment_time.strftime('%H:%M')
        
        Notification.objects.create(
            user=user,
            notification_type='new_appointment',
            title='Nueva cita agendada',
            message=f'Tienes una nueva cita con {patient_name} el {date_str} a las {time_str}.',
            appointment=appointment
        )
    
    @staticmethod
    def notify_appointment_cancelled(appointment, cancelled_by_user=None):
        """
        Crea notificación cuando se cancela una cita.
        Notifica al doctor.
        """
        doctor = appointment.doctor_specialist.doctor
        user = doctor.user
        
        patient_name = appointment.patient.get_full_name()
        date_str = appointment.appointment_date.strftime('%d/%m/%Y')
        time_str = appointment.appointment_time.strftime('%H:%M')
        
        Notification.objects.create(
            user=user,
            notification_type='appointment_cancelled',
            title='Cita cancelada',
            message=f'La cita con {patient_name} del {date_str} a las {time_str} ha sido cancelada.',
            appointment=appointment
        )
    
    @staticmethod
    def notify_appointment_confirmed(appointment):
        """
        Crea notificación cuando se confirma una cita.
        """
        doctor = appointment.doctor_specialist.doctor
        user = doctor.user
        
        patient_name = appointment.patient.get_full_name()
        date_str = appointment.appointment_date.strftime('%d/%m/%Y')
        time_str = appointment.appointment_time.strftime('%H:%M')
        
        Notification.objects.create(
            user=user,
            notification_type='appointment_confirmed',
            title='Cita confirmada',
            message=f'{patient_name} ha confirmado su cita del {date_str} a las {time_str}.',
            appointment=appointment
        )
    
    @staticmethod
    def notify_appointment_updated(appointment, updated_fields=None):
        """
        Crea notificación cuando se actualiza una cita.
        """
        doctor = appointment.doctor_specialist.doctor
        user = doctor.user
        
        patient_name = appointment.patient.get_full_name()
        date_str = appointment.appointment_date.strftime('%d/%m/%Y')
        time_str = appointment.appointment_time.strftime('%H:%M')
        
        Notification.objects.create(
            user=user,
            notification_type='appointment_updated',
            title='Cita actualizada',
            message=f'La cita con {patient_name} del {date_str} a las {time_str} ha sido modificada.',
            appointment=appointment
        )
    
    @staticmethod
    def create_custom_notification(user, title, message, notification_type='system', appointment=None):
        """
        Crea una notificación personalizada.
        """
        return Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            appointment=appointment
        )
