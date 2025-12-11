"""
Modelos para gestión de especialidades médicas y doctores.
"""
from django.db import models
from django.conf import settings
from core.models import BaseModel, BaseModelWithUUID


# ============================================================================
# SPECIALTIES - Especialidades médicas
# ============================================================================
class Specialty(BaseModel):
    """
    Especialidades médicas disponibles en la clínica.
    
    Ejemplos: Cardiología, Pediatría, Dermatología, etc.
    
    Hereda de BaseModel:
        - id: ID interno
        - created_at: Fecha de creación
        - updated_at: Última actualización
    
    NO usa UUID porque:
        - Es un catálogo público
        - No contiene información sensible
        - Se accede por listados, no por URL individual
    """
    
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Nombre',
        help_text='Nombre de la especialidad médica'
    )
    
    description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Descripción',
        help_text='Descripción breve de la especialidad'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa',
        help_text='Indica si la especialidad está disponible'
    )
    
    class Meta:
        db_table = 'specialties'
        verbose_name = 'Especialidad'
        verbose_name_plural = 'Especialidades'
        ordering = ['name']
    
    def __str__(self):
        return self.name


# ============================================================================
# DOCTORS - Doctores de la clínica
# ============================================================================
class Doctor(BaseModelWithUUID):
    """
    Perfil de doctores de la clínica.
    
    Relación 1:1 con User (un doctor es un usuario del sistema).
    
    Hereda de BaseModelWithUUID:
        - id: ID interno para relaciones
        - uuid: UUID público para la API
        - created_at: Fecha de creación
        - updated_at: Última actualización
    
    Usa UUID porque:
        - Se expone en URLs públicas (/api/doctors/{uuid}/)
        - Contiene información profesional sensible
        - Los pacientes consultan perfiles de doctores
    """
    
    # Relación con usuario del sistema
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        verbose_name='Usuario',
        help_text='Usuario del sistema asociado al doctor'
    )
    
    # Información personal
    first_names = models.CharField(
        max_length=255,
        verbose_name='Nombres',
        help_text='Nombres completos del doctor'
    )
    
    last_names = models.CharField(
        max_length=255,
        verbose_name='Apellidos',
        help_text='Apellidos completos del doctor'
    )
    
    document_id = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Documento de identidad',
        help_text='Cédula o documento único'
    )
    
    # Información de contacto
    email = models.EmailField(
        max_length=255,
        verbose_name='Email',
        help_text='Email profesional del doctor'
    )
    
    phone_number = models.CharField(
        max_length=10,
        verbose_name='Teléfono',
        help_text='Número de contacto'
    )
    
    address = models.CharField(
        max_length=500,
        verbose_name='Dirección',
        help_text='Dirección de residencia o consultorio'
    )
    
    # Información profesional
    biography = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Biografía',
        help_text='Breve biografía profesional'
    )
    
    # Estado y fecha de contratación
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Indica si el doctor está activo en el sistema'
    )
    
    hire_date = models.DateField(
        verbose_name='Fecha de contratación',
        help_text='Fecha en que el doctor ingresó a la clínica'
    )
    
    class Meta:
        db_table = 'doctors'
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctores'
        indexes = [
            models.Index(fields=['uuid'], name='idx_doctor_uuid'),
            models.Index(fields=['document_id'], name='idx_doctor_document'),
            models.Index(fields=['is_active'], name='idx_doctor_active'),
        ]
    
    def __str__(self):
        return f"Dr(a). {self.first_names} {self.last_names}"
    
    def get_full_name(self):
        """Retorna el nombre completo del doctor."""
        return f"{self.first_names} {self.last_names}"


# ============================================================================
# DOCTOR_SPECIALTY - Tabla intermedia Doctor-Especialidad (N:M)
# ============================================================================
class DoctorSpecialty(BaseModel):
    """
    Relación muchos a muchos entre doctores y especialidades.
    Un doctor puede tener múltiples especialidades.
    Una especialidad puede ser practicada por múltiples doctores.
    
    Hereda de BaseModel:
        - id: ID interno
        - created_at: Fecha cuando se asignó la especialidad
        - updated_at: Última actualización
    
    NO usa UUID porque:
        - Es una tabla de relación interna
        - No se expone directamente en la API
        - Se accede a través de doctor o specialty
    """
    
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='specialties',
        verbose_name='Doctor',
        help_text='Doctor que tiene esta especialidad'
    )
    
    specialty = models.ForeignKey(
        Specialty,
        on_delete=models.CASCADE,
        related_name='doctors',
        verbose_name='Especialidad',
        help_text='Especialidad que practica el doctor'
    )
    
    is_primary = models.BooleanField(
        default=False,
        verbose_name='Es principal',
        help_text='Indica si es la especialidad principal del doctor'
    )
    
    class Meta:
        db_table = 'doctor_specialty'
        verbose_name = 'Especialidad del Doctor'
        verbose_name_plural = 'Especialidades de Doctores'
        unique_together = ['doctor', 'specialty']
        indexes = [
            models.Index(fields=['doctor', 'is_primary'], name='idx_doctor_primary_spec'),
        ]
    
    def __str__(self):
        primary = " (Principal)" if self.is_primary else ""
        return f"{self.doctor.get_full_name()} - {self.specialty.name}{primary}"
