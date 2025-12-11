"""
Configuración del panel de administración para Users y Roles.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role


# ============================================================================
# ROLE ADMIN
# ============================================================================
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Administración de roles del sistema.
    """
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'slug', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'description', 'is_active')
        }),
        ('Permisos', {
            'fields': (
                'can_manage_users',
                'can_manage_doctors',
                'can_view_all_appointments',
                'can_manage_schedules',
                'can_view_medical_records',
                'can_create_prescriptions',
                'can_manage_patients',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# USER ADMIN
# ============================================================================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Administración de usuarios del sistema.
    """
    list_display = ('email', 'username', 'get_role_name', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'username', 'first_names', 'last_names')
    ordering = ('-date_joined',)
    readonly_fields = ('uuid', 'date_joined', 'last_login', 'created_at', 'updated_at')
    
    def get_role_name(self, obj):
        """Muestra el nombre del rol en el listado"""
        return obj.role.name if obj.role else 'Sin rol'
    get_role_name.short_description = 'Rol'
    
    fieldsets = (
        ('Identificación', {
            'fields': ('uuid', 'email', 'username', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_names', 'last_names')
        }),
        ('Rol y Permisos', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Fechas', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role', 'is_staff', 'is_active')
        }),
    )
