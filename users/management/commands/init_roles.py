"""
Comando para inicializar los roles del sistema.
Uso: python manage.py init_roles
"""
from django.core.management.base import BaseCommand
from users.models import Role


class Command(BaseCommand):
    help = 'Inicializa los roles predefinidos del sistema'

    def handle(self, *args, **kwargs):
        """
        Crea los roles predefinidos si no existen.
        """
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

        self.stdout.write("=" * 80)
        self.stdout.write(self.style.WARNING("INICIALIZANDO ROLES DEL SISTEMA"))
        self.stdout.write("=" * 80)

        created_count = 0
        updated_count = 0

        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                slug=role_data['slug'],
                defaults=role_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Rol creado: {role.name}')
                )
            else:
                # Actualizar permisos si el rol ya existe
                for key, value in role_data.items():
                    setattr(role, key, value)
                role.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'🔄 Rol actualizado: {role.name}')
                )

        self.stdout.write("=" * 80)
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ PROCESO COMPLETADO: {created_count} roles creados, {updated_count} actualizados'
            )
        )
        self.stdout.write("=" * 80)
        self.stdout.write("\nRoles disponibles:")
        for role in Role.objects.all().order_by('name'):
            status = "✓ Activo" if role.is_active else "✗ Inactivo"
            self.stdout.write(f"  • {role.name} ({role.slug}) - {status}")
        self.stdout.write("")
