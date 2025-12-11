"""
Serializers para el modelo User y Role.
Convierten objetos Python a JSON y viceversa.
"""
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers
from .models import User, Role


# ============================================================================
# ROLE SERIALIZER
# ============================================================================
class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar información de roles.
    """
    class Meta:
        model = Role
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'can_manage_users',
            'can_manage_doctors',
            'can_view_all_appointments',
            'can_manage_schedules',
            'can_view_medical_records',
            'can_create_prescriptions',
            'can_manage_patients',
            'is_active',
        )
        read_only_fields = ('id',)


# ============================================================================
# USER CREATE SERIALIZER - Para registro de nuevos usuarios
# ============================================================================
class UserCreateSerializer(BaseUserCreateSerializer):
    """
    Serializer para crear nuevos usuarios del sistema.
    
    Validaciones:
    - Solo administradores pueden crear doctores/asistentes
    - No se pueden crear administradores via API (solo por consola)
    - Por defecto crea usuarios con rol 'default'
    """
    role_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('uuid', 'email', 'username', 'password', 'first_names', 'last_names', 'role_id')
        read_only_fields = ('uuid',)
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate_role_id(self, value):
        """
        Valida que solo administradores puedan crear usuarios con permisos.
        """
        request = self.context.get('request')
        
        try:
            role = Role.objects.get(id=value)
        except Role.DoesNotExist:
            raise serializers.ValidationError("El rol especificado no existe")
        
        # Solo admin puede crear doctores o asistentes
        if role.slug in ['doctor', 'asistente']:
            if not request or not hasattr(request.user, 'role') or not request.user.is_admin:
                raise serializers.ValidationError(
                    "Solo los administradores pueden crear doctores o asistentes"
                )
        
        # Nadie puede crear administradores via API
        if role.slug == 'administrador':
            raise serializers.ValidationError(
                "No se pueden crear administradores via API. Use python manage.py createsuperuser"
            )
        
        return value
    
    def create(self, validated_data):
        """
        Crea el usuario con el rol especificado.
        """
        role_id = validated_data.pop('role_id', None)
        
        # Si no se especifica rol, asignar rol 'default'
        if role_id:
            role = Role.objects.get(id=role_id)
        else:
            role, created = Role.objects.get_or_create(
                slug='default',
                defaults={
                    'name': 'Usuario Default',
                    'description': 'Usuario sin permisos para testing'
                }
            )
        
        validated_data['role'] = role
        return super().create(validated_data)


# ============================================================================
# USER SERIALIZER - Para mostrar información de usuarios
# ============================================================================
class UserSerializer(BaseUserSerializer):
    """
    Serializer para mostrar información de usuarios existentes.
    """
    role = RoleSerializer(read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = (
            'uuid',
            'email',
            'username',
            'first_names',
            'last_names',
            'role',
            'role_name',
            'is_active',
            'date_joined',
            'last_login'
        )
        read_only_fields = ('uuid', 'date_joined', 'last_login')
