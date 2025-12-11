"""
Modelos para gestión de pacientes.
Los pacientes NO tienen usuarios en el sistema.
"""
from django.db import models
from core.models import BaseModelWithUUID


# ============================================================================
# PATIENTS - Pacientes de la clínica
# ============================================================================
class Patient(BaseModelWithUUID):
    """
    Registro de pacientes de la clínica.
    
    IMPORTANTE:
    - Los pacientes NO tienen usuarios del sistema
    - No pueden iniciar sesión
    - Solo son registros administrados por el personal
    
    Hereda de BaseModelWithUUID:
        - id: ID interno para relaciones
        - uuid: UUID público para la API
        - created_at: Fecha de registro
        - updated_at: Última actualización
    
    Usa UUID porque:
        - Se expone en URLs públicas (agendar cita con /api/patients/{uuid}/)
        - Contiene información personal sensible (HIPAA/protección de datos)
        - Necesita ser imposible de enumerar por seguridad
    """
    
    # Información personal
    first_names = models.CharField(
        max_length=255,
        verbose_name='Nombres',
        help_text='Nombres completos del paciente'
    )
    
    last_names = models.CharField(
        max_length=255,
        verbose_name='Apellidos',
        help_text='Apellidos completos del paciente'
    )
    
    document_id = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Documento de identidad',
        help_text='Cédula o documento único del paciente'
    )
    
    # Información de contacto
    email = models.EmailField(
        max_length=255,
        verbose_name='Email',
        help_text='Correo electrónico para notificaciones'
    )
    
    phone_number = models.CharField(
        max_length=10,
        verbose_name='Teléfono',
        help_text='Número de contacto del paciente'
    )
    
    address = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Dirección',
        help_text='Dirección de residencia (opcional)'
    )
    
    # Estado
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Indica si el paciente está activo en el sistema'
    )
    
    class Meta:
        db_table = 'patients'
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        indexes = [
            models.Index(fields=['uuid'], name='idx_patient_uuid'),
            models.Index(fields=['document_id'], name='idx_patient_document'),
            models.Index(fields=['email'], name='idx_patient_email'),
            models.Index(fields=['is_active'], name='idx_patient_active'),
        ]
    
    def __str__(self):
        return f"{self.first_names} {self.last_names}"
    
    def get_full_name(self):
        """Retorna el nombre completo del paciente."""
        return f"{self.first_names} {self.last_names}"
