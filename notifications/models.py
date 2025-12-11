"""
Modelos para el sistema de notificaciones.
"""
from django.db import models
from django.conf import settings
from core.models import BaseModel


class Notification(BaseModel):
    """
    Modelo para almacenar notificaciones de usuarios.
    """
    
    # Tipos de notificación
    TYPE_CHOICES = [
        ('new_appointment', 'Nueva Cita'),
        ('appointment_cancelled', 'Cita Cancelada'),
        ('appointment_confirmed', 'Cita Confirmada'),
        ('appointment_completed', 'Cita Completada'),
        ('appointment_updated', 'Cita Actualizada'),
        ('reminder', 'Recordatorio'),
        ('system', 'Sistema'),
    ]
    
    # Usuario destinatario de la notificación
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Usuario'
    )
    
    # Tipo de notificación
    notification_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default='system',
        verbose_name='Tipo'
    )
    
    # Contenido
    title = models.CharField(
        max_length=255,
        verbose_name='Título'
    )
    
    message = models.TextField(
        verbose_name='Mensaje'
    )
    
    # Referencia opcional a una cita
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name='Cita relacionada'
    )
    
    # Estado de lectura
    is_read = models.BooleanField(
        default=False,
        verbose_name='Leída'
    )
    
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de lectura'
    )
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read'], name='idx_notification_user_read'),
            models.Index(fields=['user', '-created_at'], name='idx_notification_user_date'),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    def mark_as_read(self):
        """Marca la notificación como leída."""
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
