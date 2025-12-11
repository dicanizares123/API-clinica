"""
Script de inicialización de roles predefinidos.
Ejecutar con: python manage.py shell < users/init_roles.py
"""
from users.models import Role

# ============================================================================
# ROLES PREDEFINIDOS DEL SISTEMA
# ============================================================================

roles_data = [
    {
        'name': 'Administrador',
        'slug': 'administrador',
        'description': 'Acceso total al sistema. Puede gestionar usuarios, doctores, pacientes y todas las configuraciones.',
        'can_manage_users': True,
        'can_manage_doctors': True,
        'can_view_all_appointments': True,
        'can_manage_schedules': True,
        'can_view_medical_records': True,
        'can_create_prescriptions': True,
        'can_manage_patients': True,
        'is_active': True,
    },
    {
        'name': 'Doctor',
        'slug': 'doctor',
        'description': 'Personal médico. Puede gestionar citas, ver historiales médicos y emitir recetas.',
        'can_manage_users': False,
        'can_manage_doctors': False,
        'can_view_all_appointments': True,
        'can_manage_schedules': False,
        'can_view_medical_records': True,
        'can_create_prescriptions': True,
        'can_manage_patients': True,
        'is_active': True,
    },
    {
        'name': 'Asistente',
        'slug': 'asistente',
        'description': 'Asistente administrativo. Puede agendar citas y gestionar pacientes.',
        'can_manage_users': False,
        'can_manage_doctors': False,
        'can_view_all_appointments': True,
        'can_manage_schedules': True,
        'can_view_medical_records': False,
        'can_create_prescriptions': False,
        'can_manage_patients': True,
        'is_active': True,
    },
    {
        'name': 'Usuario Default',
        'slug': 'default',
        'description': 'Usuario sin permisos. Usado para testing de seguridad.',
        'can_manage_users': False,
        'can_manage_doctors': False,
        'can_view_all_appointments': False,
        'can_manage_schedules': False,
        'can_view_medical_records': False,
        'can_create_prescriptions': False,
        'can_manage_patients': False,
        'is_active': True,
    },
]

print("=" * 80)
print("INICIALIZANDO ROLES DEL SISTEMA")
print("=" * 80)

for role_data in roles_data:
    role, created = Role.objects.get_or_create(
        slug=role_data['slug'],
        defaults=role_data
    )
    
    if created:
        print(f"✅ Rol creado: {role.name}")
    else:
        # Actualizar permisos si el rol ya existe
        for key, value in role_data.items():
            setattr(role, key, value)
        role.save()
        print(f"🔄 Rol actualizado: {role.name}")

print("=" * 80)
print("ROLES INICIALIZADOS CORRECTAMENTE")
print("=" * 80)
print("\nRoles disponibles:")
for role in Role.objects.all():
    print(f"  - {role.name} ({role.slug})")
