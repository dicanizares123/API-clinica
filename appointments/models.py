"""
Modelos para gestión de citas, horarios y bloqueos de tiempo.
"""
from django.db import models
from django.conf import settings
from core.models import BaseModel, BaseModelWithUUID
from doctors.models import Doctor, DoctorSpecialty
from patients.models import Patient


# ============================================================================
# APPOINTMENTS - Citas médicas
# ============================================================================
class Appointment(BaseModelWithUUID):
    """
    Citas médicas agendadas en la clínica.
    
    Hereda de BaseModelWithUUID:
        - id: ID interno para relaciones
        - uuid: UUID público para la API
        - created_at: Fecha de creación de la cita
        - updated_at: Última actualización
    
    Usa UUID porque:
        - Se expone en URLs públicas (confirmar/cancelar cita)
        - Contiene información médica sensible
        - Pacientes acceden con el UUID (seguridad)
    """
    
    # Estados posibles de una cita
    STATUS_CHOICES = [
        ('scheduled', 'Agendada'),
        ('confirmed', 'Confirmada'),
        ('in_progress', 'En Curso'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
        ('no_show', 'No Asistió'),
    ]
    
    # Relaciones
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Paciente',
        help_text='Paciente que solicita la cita'
    )
    
    doctor_specialist = models.ForeignKey(
        DoctorSpecialty,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Doctor y Especialidad',
        help_text='Doctor y especialidad para la cita'
    )
    
    # Fecha y hora de la cita
    appointment_date = models.DateField(
        verbose_name='Fecha de la cita',
        help_text='Día programado para la cita'
    )
    
    appointment_time = models.TimeField(
        verbose_name='Hora de la cita',
        help_text='Hora programada para la cita'
    )
    
    duration_minutes = models.IntegerField(
        default=60,
        verbose_name='Duración (minutos)',
        help_text='Duración estimada de la cita en minutos (por defecto 60)'
    )
    
    # Estado y notas
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name='Estado',
        help_text='Estado actual de la cita'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Notas',
        help_text='Notas adicionales sobre la cita'
    )
    
    class Meta:
        db_table = 'appointments'
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        ordering = ['-appointment_date', '-appointment_time']
        indexes = [
            models.Index(fields=['uuid'], name='idx_appointment_uuid'),
            models.Index(fields=['patient', 'appointment_date'], name='idx_appt_patient_date'),
            models.Index(fields=['doctor_specialist', 'appointment_date'], name='idx_appt_doctor_date'),
            models.Index(fields=['status'], name='idx_appt_status'),
            models.Index(fields=['appointment_date', 'appointment_time'], name='idx_appt_datetime'),
        ]
    
    def __str__(self):
        return f"Cita: {self.patient.get_full_name()} - {self.appointment_date} {self.appointment_time}"


# ============================================================================
# DOCTOR_SCHEDULE - Horarios de disponibilidad de doctores
# ============================================================================
class DoctorSchedule(BaseModel):
    """
    Horarios de disponibilidad de los doctores.
    Define los días y horas en que un doctor atiende.
    
    Hereda de BaseModel:
        - id: ID interno
        - created_at: Fecha de creación del horario
        - updated_at: Última actualización
    
    NO usa UUID porque:
        - Es configuración interna del sistema
        - No se expone individualmente en la API
        - Se accede a través del doctor
    """
    
    # Días de la semana
    DAY_CHOICES = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='Doctor',
        help_text='Doctor al que pertenece este horario'
    )
    
    day_of_week = models.IntegerField(
        choices=DAY_CHOICES,
        verbose_name='Día de la semana',
        help_text='Día en que el doctor atiende'
    )
    
    start_time = models.TimeField(
        verbose_name='Hora de inicio',
        help_text='Hora en que inicia la atención'
    )
    
    end_time = models.TimeField(
        verbose_name='Hora de fin',
        help_text='Hora en que termina la atención'
    )
    
    slot_duration_minutes = models.IntegerField(
        default=60,
        verbose_name='Duración del slot (minutos)',
        help_text='Duración de cada slot de cita en minutos (por defecto 60)'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Indica si este horario está activo'
    )
    
    class Meta:
        db_table = 'doctor_schedule'
        verbose_name = 'Horario del Doctor'
        verbose_name_plural = 'Horarios de Doctores'
        unique_together = ['doctor', 'day_of_week', 'start_time']
        indexes = [
            models.Index(fields=['doctor', 'day_of_week'], name='idx_schedule_doctor_day'),
            models.Index(fields=['is_active'], name='idx_schedule_active'),
        ]
    
    def __str__(self):
        return f"{self.doctor.get_full_name()} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


# ============================================================================
# BLOCK_TIME_SLOTS - Bloqueos de horarios
# ============================================================================
class BlockTimeSlot(BaseModel):
    """
    Bloqueos de horarios para doctores.
    Permite bloquear slots específicos (vacaciones, reuniones, etc.)
    
    Hereda de BaseModel:
        - id: ID interno
        - created_at: Fecha de creación del bloqueo
        - updated_at: Última actualización
    
    NO usa UUID porque:
        - Es configuración interna del sistema
        - No se expone individualmente en la API
        - Gestión administrativa interna
    """
    
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='blocked_slots',
        verbose_name='Doctor',
        help_text='Doctor cuyo horario se bloquea'
    )
    
    date = models.DateField(
        verbose_name='Fecha',
        help_text='Día del bloqueo'
    )
    
    blocked_time = models.TimeField(
        verbose_name='Hora bloqueada',
        help_text='Hora específica del bloqueo'
    )
    
    reason = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Razón',
        help_text='Motivo del bloqueo (vacaciones, reunión, etc.)'
    )
    
    blocked_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blocked_slots',
        verbose_name='Bloqueado por',
        help_text='Usuario que creó el bloqueo'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Indica si el bloqueo está activo'
    )
    
    class Meta:
        db_table = 'block_time_slots'
        verbose_name = 'Bloqueo de Horario'
        verbose_name_plural = 'Bloqueos de Horarios'
        unique_together = ['doctor', 'date', 'blocked_time']
        indexes = [
            models.Index(fields=['doctor', 'date'], name='idx_block_doctor_date'),
            models.Index(fields=['is_active'], name='idx_block_active'),
        ]
    
    def __str__(self):
        return f"Bloqueo: {self.doctor.get_full_name()} - {self.date} {self.blocked_time}"
