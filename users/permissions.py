"""
Permisos personalizados basados en roles.
Controlan el acceso a diferentes recursos de la API.
"""
from rest_framework import permissions


# ============================================================================
# PERMISO: Solo Administradores
# ============================================================================
class IsAdministrador(permissions.BasePermission):
    """
    Permite acceso solo a usuarios con rol 'administrador'.
    
    Uso:
        - Crear/eliminar usuarios
        - Gestionar configuración del sistema
        - Acceso total a todos los recursos
    """
    
    def has_permission(self, request, view):
        """Verifica si el usuario es administrador."""
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role and
            request.user.role.slug == 'administrador'
        )


# ============================================================================
# PERMISO: Personal Médico (Doctor o Asistente)
# ============================================================================
class IsPersonalMedico(permissions.BasePermission):
    """
    Permite acceso a doctores y asistentes (personal médico).
    
    Uso:
        - Gestionar citas
        - Ver/crear historiales médicos
        - Acceder a información de pacientes
    """
    
    def has_permission(self, request, view):
        """Verifica si el usuario es doctor o asistente."""
        return (
            request.user and 
            request.user.is_authenticated and
            request.user.role and
            request.user.role.slug in ['doctor', 'asistente']
        )


# ============================================================================
# PERMISO: Administrador o Personal Médico
# ============================================================================
class IsAdminOrPersonalMedico(permissions.BasePermission):
    """
    Permite acceso a administradores, doctores y asistentes.
    
    Uso:
        - Listar pacientes
        - Ver reportes generales
        - Acceso a recursos compartidos
    """
    
    def has_permission(self, request, view):
        """Verifica si el usuario es admin o personal médico."""
        return (
            request.user and 
            request.user.is_authenticated and
            request.user.role and
            request.user.role.slug in ['administrador', 'doctor', 'asistente']
        )


# ============================================================================
# PERMISO: Solo el dueño del recurso o Admin
# ============================================================================
class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permite acceso al dueño del recurso o a administradores.
    
    Uso:
        - Editar perfil propio
        - Ver información personal
        - Operaciones CRUD sobre recursos propios
    """
    
    def has_object_permission(self, request, view, obj):
        """Verifica si el usuario es dueño del objeto o administrador."""
        return (
            request.user and 
            request.user.is_authenticated and
            (obj == request.user or (request.user.role and request.user.role.slug == 'administrador'))
        )


# ============================================================================
# PERMISO: Solo lectura para autenticados, escritura para admins
# ============================================================================
class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Lectura para cualquier usuario autenticado.
    Escritura (POST, PUT, PATCH, DELETE) solo para administradores.
    
    Uso:
        - Catálogos (especialidades, tipos de consulta)
        - Información pública del sistema
    """
    
    def has_permission(self, request, view):
        """Verifica permisos según el método HTTP."""
        # Permitir GET, HEAD, OPTIONS para usuarios autenticados
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # POST, PUT, PATCH, DELETE solo para admins
        return (
            request.user and 
            request.user.is_authenticated and
            request.user.role and
            request.user.role.slug == 'administrador'
        )
