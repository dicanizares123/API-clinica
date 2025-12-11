"""
Modelos relacionados con usuarios y roles del sistema.
Solo usuarios con roles específicos tienen acceso al sistema.
Los pacientes NO tienen usuarios, solo registros en tabla patients.
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from core.models import BaseModel, BaseModelWithUUID


# ============================================================================
# ROLES - Tabla de roles del sistema
# ============================================================================
class Role(BaseModel):
    """
    Roles del sistema con permisos configurables.
    
    Roles predefinidos:
        - administrador: Acceso total al sistema
        - doctor: Gestión de citas, historiales, recetas
        - asistente: Apoyo administrativo, agendamiento de citas
        - default: Sin permisos (para testing de seguridad)
    
    Hereda de BaseModel:
        - id: ID interno
        - created_at: Fecha de creación
        - updated_at: Última actualización
    """
    
    name = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='Nombre del rol',
        help_text='Nombre único del rol (ej: administrador, doctor)'
    )
    
    slug = models.SlugField(
        max_length=50, 
        unique=True,
        verbose_name='Slug',
        help_text='Identificador en minúsculas sin espacios'
    )
    
    description = models.TextField(
        blank=True, 
        verbose_name='Descripción',
        help_text='Descripción detallada del rol y sus responsabilidades'
    )
    
    # ========================================================================
    # PERMISOS GENERALES
    # ========================================================================
    can_manage_users = models.BooleanField(
        default=False, 
        verbose_name='Gestionar usuarios',
        help_text='Crear, editar y eliminar usuarios del sistema'
    )
    
    can_manage_doctors = models.BooleanField(
        default=False, 
        verbose_name='Gestionar doctores',
        help_text='Administrar perfiles de doctores y especialidades'
    )
    
    can_view_all_appointments = models.BooleanField(
        default=False, 
        verbose_name='Ver todas las citas',
        help_text='Acceso a todas las citas del sistema'
    )
    
    can_manage_schedules = models.BooleanField(
        default=False, 
        verbose_name='Gestionar horarios',
        help_text='Configurar horarios y disponibilidad de doctores'
    )
    
    can_view_medical_records = models.BooleanField(
        default=False, 
        verbose_name='Ver historiales médicos',
        help_text='Acceso a historiales médicos de pacientes'
    )
    
    can_create_prescriptions = models.BooleanField(
        default=False, 
        verbose_name='Crear recetas',
        help_text='Emitir recetas médicas'
    )
    
    can_manage_patients = models.BooleanField(
        default=False,
        verbose_name='Gestionar pacientes',
        help_text='Crear, editar y ver información de pacientes'
    )
    
    # ========================================================================
    # ESTADO
    # ========================================================================
    is_active = models.BooleanField(
        default=True, 
        verbose_name='Activo',
        help_text='Indica si el rol está activo en el sistema'
    )
    
    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['name']
    
    def __str__(self):
        return self.name


# ============================================================================
# USER MANAGER - Maneja creación de usuarios
# ============================================================================
class UserManager(BaseUserManager):
    """
    Manager personalizado para el modelo User.
    Maneja la creación de usuarios regulares y superusuarios.
    """
    
    def create_user(self, email, username, password=None, **extra_fields):
        """
        Crea y guarda un usuario regular.
        
        Args:
            email: Email único del usuario (requerido)
            username: Nombre de usuario único (requerido)
            password: Contraseña (será hasheada automáticamente)
            **extra_fields: Campos adicionales como role, nombres, etc.
        
        Returns:
            User: Instancia del usuario creado
        """
        if not email:
            raise ValueError('El email es obligatorio')
        if not username:
            raise ValueError('El username es obligatorio')
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)  # Hashea la contraseña
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Crea y guarda un superusuario (administrador total).
        
        Args:
            email: Email del superusuario
            username: Username del superusuario
            password: Contraseña del superusuario
            **extra_fields: Campos adicionales
        
        Returns:
            User: Instancia del superusuario creado
        """
        # Obtener o crear rol de administrador
        from users.models import Role
        admin_role, created = Role.objects.get_or_create(
            slug='administrador',
            defaults={
                'name': 'Administrador',
                'description': 'Acceso total al sistema',
                'can_manage_users': True,
                'can_manage_doctors': True,
                'can_view_all_appointments': True,
                'can_manage_schedules': True,
                'can_view_medical_records': True,
                'can_create_prescriptions': True,
                'can_manage_patients': True,
            }
        )
        
        # Establecer permisos de superusuario por defecto
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)  # ← NUEVO: Superusuario siempre activo
        extra_fields.setdefault('role', admin_role)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        
        return self.create_user(email, username, password, **extra_fields)


# ============================================================================
# USER MODEL - Solo para personal del sistema
# ============================================================================
class User(BaseModelWithUUID, AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuario personalizado con autenticación por email.
    
    IMPORTANTE: 
    - Solo usuarios del sistema (administradores, doctores, asistentes)
    - Los pacientes NO tienen usuarios, se registran en tabla 'patients'
    
    Hereda de BaseModelWithUUID:
        - id: ID interno para relaciones
        - uuid: UUID público para la API
        - created_at: Fecha de creación
        - updated_at: Última actualización
    
    Relación con Role:
        - role: ForeignKey a tabla roles (administrador, doctor, asistente, default)
    """
    
    # ========================================================================
    # CAMPOS BÁSICOS
    # ========================================================================
    email = models.EmailField(
        unique=True, 
        max_length=255, 
        verbose_name='Correo electrónico',
        help_text='Email único para autenticación'
    )
    
    username = models.CharField(
        max_length=150, 
        unique=True, 
        verbose_name='Nombre de usuario',
        help_text='Username único para el sistema'
    )
    
    first_names = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name='Nombres',
        help_text='Nombres completos del usuario'
    )
    
    last_names = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name='Apellidos',
        help_text='Apellidos completos del usuario'
    )
    
    # ========================================================================
    # ROL - Relación con tabla Role
    # ========================================================================
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,  # No permite eliminar roles en uso
        related_name='users',
        verbose_name='Rol',
        help_text='Rol que determina los permisos del usuario',
        null=True,  # Temporal para migración
        blank=True
    )
    
    # ========================================================================
    # ESTADOS Y FLAGS
    # ========================================================================
    is_active = models.BooleanField(
        default=False,  # ← CAMBIADO: Usuarios vienen desactivados por defecto
        verbose_name='Activo',
        help_text='Indica si el usuario puede acceder al sistema. El administrador debe activarlo manualmente.'
    )
    
    is_staff = models.BooleanField(
        default=False, 
        verbose_name='Es staff',
        help_text='Permite acceso al panel de administración de Django'
    )
    
    is_superuser = models.BooleanField(
        default=False, 
        verbose_name='Es superusuario',
        help_text='Otorga todos los permisos sin asignarlos explícitamente'
    )
    
    # ========================================================================
    # CAMPOS DE AUTENTICACIÓN
    # ========================================================================
    date_joined = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Fecha de registro'
    )
    
    last_login = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name='Último acceso'
    )
    
    # ========================================================================
    # CONFIGURACIÓN DEL MANAGER
    # ========================================================================
    objects = UserManager()
    
    # Campo usado para autenticación (email en lugar de username)
    USERNAME_FIELD = 'email'
    
    # Campos requeridos además de email y password
    REQUIRED_FIELDS = ['username']
    
    # ========================================================================
    # META OPTIONS
    # ========================================================================
    class Meta:
        db_table = 'users'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        indexes = [
            models.Index(fields=['uuid'], name='idx_user_uuid'),
            models.Index(fields=['email'], name='idx_user_email'),
            models.Index(fields=['role'], name='idx_user_role'),
        ]
    
    # ========================================================================
    # MÉTODOS
    # ========================================================================
    def __str__(self):
        """Representación en string del usuario"""
        role_name = self.role.name if self.role else 'Sin rol'
        return f"{self.email} - {role_name}"
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario"""
        full_name = f"{self.first_names} {self.last_names}".strip()
        return full_name if full_name else self.username
    
    def get_short_name(self):
        """Retorna el nombre corto del usuario"""
        return self.first_names or self.username
    
    # ========================================================================
    # PROPERTIES - Para verificación rápida de roles
    # ========================================================================
    @property
    def is_admin(self):
        """Verifica si el usuario es administrador"""
        return self.role and self.role.slug == 'administrador'
    
    @property
    def is_doctor(self):
        """Verifica si el usuario es doctor"""
        return self.role and self.role.slug == 'doctor'
    
    @property
    def is_asistente(self):
        """Verifica si el usuario es asistente"""
        return self.role and self.role.slug == 'asistente'
    
    @property
    def has_medical_permissions(self):
        """Verifica si el usuario tiene permisos médicos (doctor o asistente)"""
        return self.role and self.role.slug in ['doctor', 'asistente']
