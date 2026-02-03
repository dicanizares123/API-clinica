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


# ============================================================================
# MODELO DE INFORMACIÓN DEL NEGOCIO
# ============================================================================
class BusinessInfo(BaseModel):
    """
    Información del negocio/clínica.
    Modelo singleton - solo debe existir un registro.
    Se usa para almacenar el RUC que se consultará en la API externa.
    """
    
    ruc = models.CharField(
        max_length=13,
        unique=True,
        verbose_name='RUC',
        help_text='RUC del negocio para consultar en el SRI (13 dígitos)'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        db_table = 'business_info'
        verbose_name = 'Información del Negocio'
        verbose_name_plural = 'Información del Negocio'
    
    def __str__(self):
        return f"RUC: {self.ruc}"
    
    def save(self, *args, **kwargs):
        """Asegurar que solo exista un registro activo."""
        if not self.pk and BusinessInfo.objects.filter(is_active=True).exists():
            raise ValueError('Solo puede existir un registro activo de información del negocio')
        return super().save(*args, **kwargs)
    
    @classmethod
    def get_instance(cls):
        """Obtener la única instancia activa o None."""
        return cls.objects.filter(is_active=True).first()
    
    @classmethod
    def get_ruc(cls):
        """Obtener el RUC configurado."""
        instance = cls.get_instance()
        return instance.ruc if instance else None


# ============================================================================
# MODELO DE PRODUCTOS/SERVICIOS
# ============================================================================
class Product(BaseModel):
    """
    Catálogo de productos y servicios.
    """
    
    description = models.CharField(
        max_length=255,
        verbose_name='Descripción',
        help_text='Descripción del producto o servicio'
    )
    
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código',
        help_text='Código único del producto'
    )
    
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio Unitario',
        help_text='Precio unitario del producto'
    )
    
    class Meta:
        db_table = 'products'
        verbose_name = 'Producto/Servicio'
        verbose_name_plural = 'Productos/Servicios'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.description}"


# ============================================================================
# MODELOS DE SECUENCIALES - Importados desde models_sequential.py
# ============================================================================
from .models_sequential import Sequential, SequentialUsage
