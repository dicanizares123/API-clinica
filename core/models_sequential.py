"""
Modelos para gestión de secuenciales de facturación electrónica.
"""
from django.db import models
from .models import BaseModel


class Sequential(BaseModel):
    """
    Modelo para gestionar el contador de secuenciales global.
    """
    
    last_sequential = models.IntegerField(
        default=0,
        verbose_name='Último Secuencial Generado',
        help_text='Último número secuencial generado (sin importar si se usó o no)'
    )
    
    class Meta:
        db_table = 'sequentials'
        verbose_name = 'Secuencial'
        verbose_name_plural = 'Secuenciales'
    
    def __str__(self):
        return f"Secuencial: {self.format_sequential(self.last_sequential)}"
    
    @staticmethod
    def format_sequential(number):
        """Retorna el número formateado con 9 dígitos."""
        return str(number).zfill(9)


class SequentialUsage(BaseModel):
    """
    Modelo para registrar cada secuencial generado y su estado.
    Permite reutilizar secuenciales que fallaron.
    """
    
    STATUS_CHOICES = [
        ('available', 'Disponible'),  # Falló al crear factura, puede reutilizarse
        ('pending', 'Pendiente'),     # Generado pero aún no se ha intentado crear factura
        ('used', 'Usado'),            # Factura creada exitosamente
    ]
    
    sequential = models.ForeignKey(
        Sequential,
        on_delete=models.CASCADE,
        related_name='usages',
        verbose_name='Secuencial'
    )
    
    sequential_number = models.IntegerField(
        verbose_name='Número Secuencial',
        help_text='Número secuencial específico'
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )
    
    class Meta:
        db_table = 'sequential_usages'
        verbose_name = 'Uso de Secuencial'
        verbose_name_plural = 'Usos de Secuenciales'
        unique_together = ['sequential', 'sequential_number']
        ordering = ['sequential', 'sequential_number']
        indexes = [
            models.Index(fields=['sequential', 'status']),
        ]
    
    def __str__(self):
        return f"{self.sequential} - {Sequential.format_sequential(self.sequential_number)} ({self.get_status_display()})"
    
    def get_formatted_sequential(self):
        """Retorna el número secuencial formateado con 9 dígitos."""
        return Sequential.format_sequential(self.sequential_number)
