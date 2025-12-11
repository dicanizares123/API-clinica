# Backend Clínica - API REST con Django

Sistema de gestión de clínica médica con autenticación JWT, roles de usuario y gestión completa de citas, doctores y pacientes.

## 🏗️ Arquitectura del Sistema

### Estructura de Base de Datos

```
📦 Base de Datos
├── 👥 Users & Roles
│   ├── roles (catálogo de roles con permisos)
│   └── users (usuarios del sistema con UUID)
│
├── 👨‍⚕️ Doctores
│   ├── specialties (especialidades médicas)
│   ├── doctors (perfil de doctores con UUID)
│   └── doctor_specialty (relación N:M)
│
├── 🏥 Pacientes
│   └── patients (pacientes sin usuarios del sistema, con UUID)
│
└── 📅 Citas
    ├── appointments (citas médicas con UUID)
    ├── doctor_schedule (horarios de disponibilidad)
    └── block_time_slots (bloqueos de horarios)
```

### Roles del Sistema

| Rol               | Slug            | Permisos                               |
| ----------------- | --------------- | -------------------------------------- |
| **Administrador** | `administrador` | Acceso total al sistema                |
| **Doctor**        | `doctor`        | Gestión de citas, historiales, recetas |
| **Asistente**     | `asistente`     | Agendar citas, gestionar pacientes     |
| **Default**       | `default`       | Sin permisos (testing)                 |

### Seguridad con UUID

✅ **Tablas con UUID** (expuestas públicamente):

- `users` - Usuarios del sistema
- `doctors` - Perfiles de doctores
- `patients` - Registros de pacientes
- `appointments` - Citas médicas

⭕ **Tablas sin UUID** (uso interno):

- `roles` - Catálogo de roles
- `specialties` - Especialidades médicas
- `doctor_specialty` - Relación N:M
- `doctor_schedule` - Horarios
- `block_time_slots` - Bloqueos

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/dicanizares123/API-clinica.git
cd backendclinica
```

### 2. Crear entorno virtual

```bash
python -m venv venv
.\venv\Scripts\Activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear archivo `.env` en la raíz:

```env
SECRET_KEY=django-insecure-m%c%*wt7m_7u05u-!=po-03ru%j0z5osy%@!v17t3acys)6o_7
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Eliminar base de datos anterior (si existe)

```bash
Remove-Item db.sqlite3 -ErrorAction SilentlyContinue
```

### 6. Crear migraciones y migrar

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Inicializar roles del sistema

```bash
python manage.py shell < users/init_roles.py
```

### 8. Crear superusuario (administrador)

```bash
python manage.py createsuperuser
```

**Ejemplo:**

```
Email: admin@clinica.com
Username: admin
Password: ********
```

Este usuario tendrá automáticamente el rol de **Administrador**.

### 9. Ejecutar servidor

```bash
python manage.py runserver
```

Servidor corriendo en: http://localhost:8000

## 📡 Endpoints Principales

### Autenticación (Djoser + JWT)

```
POST   /auth/users/              # Registrar nuevo usuario
POST   /auth/jwt/create/         # Login (obtener tokens)
POST   /auth/jwt/refresh/        # Renovar access token
GET    /auth/users/me/           # Info del usuario actual
```

### Usuarios y Roles

```
GET    /api/users/               # Listar usuarios (admin)
GET    /api/users/me/            # Mi perfil
GET    /api/users/{uuid}/        # Usuario por UUID
GET    /api/roles/               # Listar roles
```

## 📦 Tecnologías

- **Django 5.2.7** - Framework web
- **Django REST Framework 3.16.1** - API REST
- **Djoser 2.3.3** - Autenticación
- **SimpleJWT 5.5.1** - Tokens JWT
- **django-cors-headers 4.9.0** - CORS
- **python-decouple 3.8** - Variables de entorno
- **SQLite** - Base de datos (desarrollo)

## 🗂️ Estructura del Proyecto

```
backendclinica/
├── clinica_crud_api/        # Configuración principal
│   ├── settings.py          # Configuración de Django
│   └── urls.py              # URLs principales
│
├── core/                    # Modelos base abstractos
│   └── models.py            # BaseModel, BaseModelWithUUID
│
├── users/                   # Usuarios y roles
│   ├── models.py            # User, Role
│   ├── serializers.py       # UserSerializer, RoleSerializer
│   ├── permissions.py       # Permisos personalizados
│   ├── views.py             # UserViewSet, RoleViewSet
│   ├── admin.py             # Configuración del admin
│   └── init_roles.py        # Script de inicialización de roles
│
├── doctors/                 # Doctores y especialidades
│   ├── models.py            # Doctor, Specialty, DoctorSpecialty
│   └── admin.py             # Configuración del admin
│
├── patients/                # Pacientes
│   ├── models.py            # Patient
│   └── admin.py             # Configuración del admin
│
├── appointments/            # Citas y horarios
│   ├── models.py            # Appointment, DoctorSchedule, BlockTimeSlot
│   └── admin.py             # Configuración del admin
│
├── manage.py                # Django management
├── requirements.txt         # Dependencias
├── .env                     # Variables de entorno
├── .gitignore              # Archivos ignorados
└── README.md               # Este archivo
```

## 📝 Notas Importantes

1. **Pacientes NO tienen usuarios**: Los pacientes se registran solo en la tabla `patients`, no pueden iniciar sesión.

2. **UUID para seguridad**: Todas las entidades expuestas públicamente usan UUID en lugar de IDs secuenciales.

3. **Roles con permisos**: Los roles tienen permisos granulares configurables desde el admin.

4. **JWT con rotación**: Los refresh tokens se rotan automáticamente y los antiguos se agregan a blacklist.

5. **CORS configurado**: El frontend en `localhost:3000` tiene acceso por defecto.

## 🔧 Comandos Útiles

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver

# Inicializar roles
python manage.py shell < users/init_roles.py

# Acceder a la shell de Django
python manage.py shell

# Acceder a la base de datos
python manage.py dbshell
```

## 👤 Autor

**Diego Cañizares**

- GitHub: [@dicanizares123](https://github.com/dicanizares123)
- Repositorio: [API-clinica](https://github.com/dicanizares123/API-clinica)
