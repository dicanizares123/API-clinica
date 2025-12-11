"""
Configuración del panel de administración para Doctores y Especialidades.
"""
from django.contrib import admin
from .models import Doctor, Specialty, DoctorSpecialty


# ============================================================================
# SPECIALTY ADMIN
# ============================================================================
@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    """Administración de especialidades médicas."""
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# DOCTOR SPECIALTY INLINE
# ============================================================================
class DoctorSpecialtyInline(admin.TabularInline):
    """Inline para especialidades del doctor."""
    model = DoctorSpecialty
    extra = 1
    fields = ('specialty', 'is_primary')


# ============================================================================
# DOCTOR ADMIN
# ============================================================================
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """Administración de doctores."""
    list_display = ('get_full_name', 'document_id', 'email', 'phone_number', 'is_active', 'hire_date')
    list_filter = ('is_active', 'hire_date', 'created_at')
    search_fields = ('first_names', 'last_names', 'document_id', 'email')
    readonly_fields = ('uuid', 'created_at', 'updated_at')
    inlines = [DoctorSpecialtyInline]
    
    def get_full_name(self, obj):
        """Muestra el nombre completo en el listado."""
        return obj.get_full_name()
    get_full_name.short_description = 'Nombre completo'
    
    fieldsets = (
        ('Identificación', {
            'fields': ('uuid', 'user', 'document_id')
        }),
        ('Información Personal', {
            'fields': ('first_names', 'last_names', 'email', 'phone_number', 'address')
        }),
        ('Información Profesional', {
            'fields': ('biography', 'hire_date', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
