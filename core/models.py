"""
Modelos base abstractos para toda la aplicación.
Proveen campos comunes como id, timestamps y UUID.
"""
from django.db import models
import uuid

# ============================================================================
# MODELO BASE - Para tablas internas/catálogos
# ============================================================================
class BaseModel(models.Model):
    """
    Modelo abstracto base para todas las tablas.
    
    Campos:
        - id: Autoincremental para uso interno y relaciones en DB
        - created_at: Timestamp de creación (automático)
        - updated_at: Timestamp de última actualización (automático)
    
    Uso: Para tablas que NO se exponen en URLs públicas
    Ejemplo: Especialidades, Configuraciones, Horarios, Roles
    """
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    
    class Meta:
        abstract = True  # No crea tabla, solo herencia
        ordering = ['-created_at']


# ============================================================================
# MODELO BASE CON UUID - Para tablas expuestas públicamente
# ============================================================================
class BaseModelWithUUID(BaseModel):
    """
    Modelo abstracto para tablas que necesitan UUID público.
    
    Campos adicionales:
        - uuid: Identificador único global para URLs públicas (imposible de adivinar)
    
    Uso: Para tablas con datos sensibles o expuestas en la API
    Ejemplo: Users, Doctors, Patients, Appointments
    
    Ventajas:
        - Seguridad: UUIDs imposibles de enumerar/adivinar
        - Privacidad: Oculta el número real de registros
        - Escalabilidad: Únicos globalmente, útil para replicación
    """
    uuid = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True, 
        db_index=True,
        verbose_name='UUID público'
    )
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
