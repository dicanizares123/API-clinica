# Backend Clínica - Django REST API

API REST para sistema de gestión de clínica.

## Instalación

1. Clonar el repositorio
2. Crear entorno virtual:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate
   ```
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Copiar `.env.example` a `.env` y configurar variables
5. Ejecutar migraciones:
   ```bash
   python manage.py migrate
   ```
6. Crear superusuario:
   ```bash
   python manage.py createsuperuser
   ```
7. Ejecutar servidor:
   ```bash
   python manage.py runserver
   ```

## Tecnologías

- Django 5.2.7
- Django REST Framework
- Djoser (autenticación)
- JWT Authentication
- SQLite

## Endpoints principales

- `/auth/users/` - Registro
- `/auth/jwt/create/` - Login
- `/auth/jwt/refresh/` - Refresh token
- `/auth/users/me/` - Usuario actual
