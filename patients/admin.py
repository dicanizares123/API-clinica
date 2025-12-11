"""
Configuración del panel de administración para Pacientes.
"""
from django.contrib import admin
from .models import Patient


# ============================================================================
# PATIENT ADMIN
# ============================================================================
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """Administración de pacientes."""
    list_display = ('get_full_name', 'document_id', 'email', 'phone_number', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('first_names', 'last_names', 'document_id', 'email', 'phone_number')
    readonly_fields = ('uuid', 'created_at', 'updated_at')
    
    def get_full_name(self, obj):
        """Muestra el nombre completo en el listado."""
        return obj.get_full_name()
    get_full_name.short_description = 'Nombre completo'
    
    fieldsets = (
        ('Identificación', {
            'fields': ('uuid', 'document_id')
        }),
        ('Información Personal', {
            'fields': ('first_names', 'last_names', 'email', 'phone_number', 'address')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
