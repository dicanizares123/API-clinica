# 📅 API de Sistema de Citas - Documentación Completa

## 🌐 Endpoints Públicos vs Privados

### ✅ Endpoints PÚBLICOS (sin autenticación)

Estos endpoints están disponibles para **formularios web públicos** sin necesidad de login:

- **`GET /api/available-slots/`** - Consultar horarios disponibles de un doctor
- **`POST /api/appointments/`** - Crear/agendar una nueva cita

### 🔒 Endpoints PRIVADOS (requieren autenticación)

El resto de endpoints requieren JWT Token (login):

- Listar/ver/modificar/eliminar citas existentes
- Gestionar horarios de doctores
- Bloquear horarios
- Cancelar/confirmar citas

---

## 🔑 Autenticación (para endpoints privados)

### Obtener Token (Login)

```bash
POST http://localhost:8000/auth/jwt/create/
Content-Type: application/json

{
  "email": "tu@email.com",
  "password": "tu_contraseña"
}

# Respuesta:
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Usar el Token en las peticiones

```bash
Authorization: Bearer <access_token>
```

---

## 📋 Endpoints Principales

### 1. 🔍 Consultar Horarios Disponibles

**Endpoint más importante para el frontend - PÚBLICO (sin autenticación)**

```bash
GET http://localhost:8000/api/available-slots/?doctor={doctor_id}&date={YYYY-MM-DD}
# Sin necesidad de Authorization header
```

**Parámetros Query:**

- `doctor` (requerido): ID del doctor
- `date` (requerido): Fecha en formato YYYY-MM-DD

**Ejemplo de petición:**

```javascript
// ✅ PÚBLICO - No necesita token
const response = await fetch(
  "http://localhost:8000/api/available-slots/?doctor=1&date=2025-11-20"
);

const data = await response.json();
console.log(data);
```

**Respuesta exitosa (200 OK):**

```json
{
  "date": "2025-11-20",
  "day_name": "Miércoles",
  "available_slots": ["09:00:00", "11:00:00", "13:00:00", "16:00:00"],
  "total_slots": 8,
  "available_count": 4,
  "occupied_count": 3,
  "blocked_count": 1
}
```

**Respuesta cuando no hay horarios disponibles:**

```json
{
  "date": "2025-11-20",
  "day_name": "Miércoles",
  "available_slots": [],
  "total_slots": 0,
  "available_count": 0,
  "occupied_count": 0,
  "blocked_count": 0,
  "message": "El doctor no tiene horario configurado para Miércoles"
}
```

**Errores posibles:**

```json
// 400 Bad Request - Falta parámetro doctor
{
  "error": "El parámetro \"doctor\" es requerido"
}

// 400 Bad Request - Falta parámetro date
{
  "error": "El parámetro \"date\" es requerido (formato: YYYY-MM-DD)"
}

// 400 Bad Request - Formato de fecha inválido
{
  "error": "Formato de fecha inválido. Use YYYY-MM-DD"
}

// 404 Not Found - Doctor no existe
{
  "detail": "No encontrado."
}
```

---

### 2. ➕ Crear una Cita

**PÚBLICO (sin autenticación) - Para formulario web público**

```bash
POST http://localhost:8000/api/appointments/
Content-Type: application/json
# Sin necesidad de Authorization header

{
  "patient": 1,
  "doctor_specialist": 1,
  "appointment_date": "2025-11-20",
  "appointment_time": "09:00:00",
  "duration_minutes": 60,
  "notes": "Primera consulta"
}
```

**Ejemplo en JavaScript:**

```javascript
// ✅ PÚBLICO - No necesita token de autenticación
const createAppointment = async () => {
  const response = await fetch("http://localhost:8000/api/appointments/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      // NO se necesita Authorization header
    },
    body: JSON.stringify({
      patient: 1,
      doctor_specialist: 1,
      appointment_date: "2025-11-20",
      appointment_time: "09:00:00",
      duration_minutes: 60,
      notes: "Primera consulta",
    }),
  });

  if (response.ok) {
    const data = await response.json();
    console.log("✅ Cita creada:", data);
  } else {
    const error = await response.json();
    console.error("❌ Error:", error);
  }
};
```

**Respuesta exitosa (201 Created):**

```json
{
  "id": 5,
  "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "patient": 1,
  "patient_name": "Juan Pérez García",
  "doctor_specialist": 1,
  "doctor_name": "Dra. María González",
  "specialty_name": "Psicología Clínica",
  "appointment_date": "2025-11-20",
  "appointment_time": "09:00:00",
  "duration_minutes": 60,
  "status": "scheduled",
  "status_display": "Agendada",
  "notes": "Primera consulta",
  "created_at": "2025-11-19T10:30:00Z",
  "updated_at": "2025-11-19T10:30:00Z"
}
```

**Errores de validación (400 Bad Request):**

```json
// Horario no disponible
{
  "non_field_errors": [
    "Ya existe una cita agendada en ese horario."
  ]
}

// Doctor no trabaja ese día
{
  "non_field_errors": [
    "El doctor no tiene horario configurado para Miércoles."
  ]
}

// Hora fuera del horario del doctor
{
  "non_field_errors": [
    "La hora debe estar entre 09:00 y 17:00."
  ]
}

// Horario bloqueado
{
  "non_field_errors": [
    "Este horario ha sido bloqueado y no está disponible."
  ]
}
```

---

### 3. 📖 Listar Todas las Citas

```bash
GET http://localhost:8000/api/appointments/
Authorization: Bearer <token>
```

**Filtros disponibles (query params):**

- `?patient=1` - Citas de un paciente específico
- `?doctor=1` - Citas de un doctor específico
- `?date=2025-11-20` - Citas de una fecha específica
- `?status=scheduled` - Citas con un status específico

**Ejemplos:**

```bash
# Todas las citas de un paciente
GET http://localhost:8000/api/appointments/?patient=1

# Todas las citas de un doctor en una fecha
GET http://localhost:8000/api/appointments/?doctor=1&date=2025-11-20

# Citas confirmadas
GET http://localhost:8000/api/appointments/?status=confirmed
```

**Respuesta (200 OK):**

```json
[
  {
    "id": 1,
    "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "patient": 1,
    "patient_name": "Juan Pérez García",
    "doctor_specialist": 1,
    "doctor_name": "Dra. María González",
    "specialty_name": "Psicología Clínica",
    "appointment_date": "2025-11-20",
    "appointment_time": "09:00:00",
    "duration_minutes": 60,
    "status": "scheduled",
    "status_display": "Agendada",
    "notes": "",
    "created_at": "2025-11-19T10:00:00Z",
    "updated_at": "2025-11-19T10:00:00Z"
  },
  {
    "id": 2,
    ...
  }
]
```

---

### 4. 🔎 Ver Detalle de una Cita

```bash
GET http://localhost:8000/api/appointments/{id}/
Authorization: Bearer <token>
```

**Ejemplo:**

```bash
GET http://localhost:8000/api/appointments/1/
```

**Respuesta (200 OK):**

```json
{
  "id": 1,
  "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "patient": 1,
  "patient_name": "Juan Pérez García",
  "doctor_specialist": 1,
  "doctor_name": "Dra. María González",
  "specialty_name": "Psicología Clínica",
  "appointment_date": "2025-11-20",
  "appointment_time": "09:00:00",
  "duration_minutes": 60,
  "status": "scheduled",
  "status_display": "Agendada",
  "notes": "",
  "created_at": "2025-11-19T10:00:00Z",
  "updated_at": "2025-11-19T10:00:00Z"
}
```

---

### 5. ✏️ Actualizar una Cita

**Actualización completa (PUT):**

```bash
PUT http://localhost:8000/api/appointments/{id}/
Authorization: Bearer <token>
Content-Type: application/json

{
  "patient": 1,
  "doctor_specialist": 1,
  "appointment_date": "2025-11-21",
  "appointment_time": "10:00:00",
  "duration_minutes": 60,
  "status": "confirmed",
  "notes": "Paciente confirmó asistencia"
}
```

**Actualización parcial (PATCH):**

```bash
PATCH http://localhost:8000/api/appointments/{id}/
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "confirmed",
  "notes": "Paciente confirmó asistencia"
}
```

---

### 6. ❌ Cancelar una Cita

```bash
POST http://localhost:8000/api/appointments/{id}/cancel/
Authorization: Bearer <token>
```

**Ejemplo en JavaScript:**

```javascript
const cancelAppointment = async (appointmentId) => {
  const response = await fetch(
    `http://localhost:8000/api/appointments/${appointmentId}/cancel/`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  const data = await response.json();
  console.log(data.message); // "Cita cancelada exitosamente"
};
```

**Respuesta (200 OK):**

```json
{
  "message": "Cita cancelada exitosamente",
  "appointment": {
    "id": 1,
    "status": "cancelled",
    "status_display": "Cancelada",
    ...
  }
}
```

---

### 7. ✅ Confirmar una Cita

```bash
POST http://localhost:8000/api/appointments/{id}/confirm/
Authorization: Bearer <token>
```

**Respuesta (200 OK):**

```json
{
  "message": "Cita confirmada exitosamente",
  "appointment": {
    "id": 1,
    "status": "confirmed",
    "status_display": "Confirmada",
    ...
  }
}
```

---

### 8. 🗑️ Eliminar una Cita

```bash
DELETE http://localhost:8000/api/appointments/{id}/
Authorization: Bearer <token>
```

**Respuesta (204 No Content):**
Sin contenido en el body.

---

## ⏰ Gestión de Horarios del Doctor

### 9. Ver Horarios de un Doctor

```bash
GET http://localhost:8000/api/schedules/by_doctor/{doctor_id}/
Authorization: Bearer <token>
```

**Ejemplo:**

```bash
GET http://localhost:8000/api/schedules/by_doctor/1/
```

**Respuesta (200 OK):**

```json
[
  {
    "id": 1,
    "doctor": 1,
    "doctor_name": "Dra. María González",
    "day_of_week": 0,
    "day_name": "Lunes",
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "slot_duration_minutes": 60,
    "is_active": true,
    "created_at": "2025-11-19T08:00:00Z",
    "updated_at": "2025-11-19T08:00:00Z"
  },
  {
    "id": 2,
    "doctor": 1,
    "doctor_name": "Dra. María González",
    "day_of_week": 1,
    "day_name": "Martes",
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "slot_duration_minutes": 60,
    "is_active": true,
    "created_at": "2025-11-19T08:00:00Z",
    "updated_at": "2025-11-19T08:00:00Z"
  }
]
```

### 10. Crear Horario para Doctor

```bash
POST http://localhost:8000/api/schedules/
Authorization: Bearer <token>
Content-Type: application/json

{
  "doctor": 1,
  "day_of_week": 0,
  "start_time": "09:00:00",
  "end_time": "17:00:00",
  "slot_duration_minutes": 60,
  "is_active": true
}
```

**Nota:** Solo usuarios con rol `administrador` o `doctor` pueden crear horarios.

---

## 🚫 Gestión de Bloqueos de Horarios

### 11. Bloquear un Horario

```bash
POST http://localhost:8000/api/blocked-slots/
Authorization: Bearer <token>
Content-Type: application/json

{
  "doctor": 1,
  "date": "2025-11-20",
  "blocked_time": "14:00:00",
  "reason": "Reunión administrativa",
  "is_active": true
}
```

**Respuesta (201 Created):**

```json
{
  "id": 1,
  "doctor": 1,
  "doctor_name": "Dra. María González",
  "date": "2025-11-20",
  "blocked_time": "14:00:00",
  "reason": "Reunión administrativa",
  "blocked_by_user": 2,
  "blocked_by_username": "admin@clinica.com",
  "is_active": true,
  "created_at": "2025-11-19T11:00:00Z",
  "updated_at": "2025-11-19T11:00:00Z"
}
```

### 12. Listar Bloqueos

```bash
GET http://localhost:8000/api/blocked-slots/
Authorization: Bearer <token>

# Filtrar por doctor
GET http://localhost:8000/api/blocked-slots/?doctor=1

# Filtrar por fecha
GET http://localhost:8000/api/blocked-slots/?date=2025-11-20
```

---

## 📊 Estados de Citas

| Valor         | Nombre     | Descripción                            |
| ------------- | ---------- | -------------------------------------- |
| `scheduled`   | Agendada   | Cita creada, pendiente de confirmación |
| `confirmed`   | Confirmada | Paciente confirmó su asistencia        |
| `in_progress` | En Curso   | Cita en progreso (doctor atendiendo)   |
| `completed`   | Completada | Cita finalizada exitosamente           |
| `cancelled`   | Cancelada  | Cita cancelada                         |
| `no_show`     | No Asistió | Paciente no se presentó                |

---

## 🔄 Flujo Completo de Agendamiento (Frontend Público)

```javascript
// ✅ FLUJO COMPLETAMENTE PÚBLICO - Sin necesidad de autenticación

// 1. Usuario selecciona doctor y fecha
const doctorId = 1;
const selectedDate = "2025-11-20";

// 2. Consultar horarios disponibles (PÚBLICO)
const slotsResponse = await fetch(
  `http://localhost:8000/api/available-slots/?doctor=${doctorId}&date=${selectedDate}`
  // Sin headers de autenticación
);

const slotsData = await slotsResponse.json();

// 3. Mostrar horarios disponibles al usuario
console.log("Horarios disponibles:", slotsData.available_slots);
// ["09:00:00", "11:00:00", "13:00:00", "16:00:00"]

// 4. Usuario selecciona un horario
const selectedTime = "09:00:00";

// 5. Crear la cita (PÚBLICO)
const appointmentResponse = await fetch(
  "http://localhost:8000/api/appointments/",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      // Sin Authorization header
    },
    body: JSON.stringify({
      patient: 1,
      doctor_specialist: 1,
      appointment_date: selectedDate,
      appointment_time: selectedTime,
      duration_minutes: 60,
      notes: "",
    }),
  }
);

if (appointmentResponse.ok) {
  const appointment = await appointmentResponse.json();
  console.log("✅ Cita creada exitosamente:", appointment);
  // Mostrar confirmación al usuario con el UUID de la cita
  console.log("UUID de la cita:", appointment.uuid);
} else {
  const error = await appointmentResponse.json();
  console.error("❌ Error al crear cita:", error);
  // Mostrar error al usuario
}
```

---

## 🛡️ Permisos y Seguridad

### Roles y Acceso

| Endpoint                     | Público (sin login) | Administrador | Doctor         | Asistente |
| ---------------------------- | ------------------- | ------------- | -------------- | --------- |
| **Ver horarios disponibles** | ✅ PÚBLICO          | ✅            | ✅             | ✅        |
| **Crear citas**              | ✅ PÚBLICO          | ✅            | ✅             | ✅        |
| Ver/listar citas             | ❌                  | Todas         | Solo sus citas | Todas     |
| Modificar citas              | ❌                  | ✅            | Solo sus citas | ✅        |
| Cancelar citas               | ❌                  | ✅            | ✅             | ✅        |
| Gestionar horarios           | ❌                  | ✅            | Solo los suyos | ❌        |
| Bloquear horarios            | ❌                  | ✅            | Solo los suyos | ❌        |

---

## 🧪 Pruebas con cURL

### Ejemplo completo con cURL:

```bash
# 1. Hacer login
curl -X POST http://localhost:8000/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@clinica.com","password":"admin123"}'

# Guardar el access token de la respuesta
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 2. Consultar horarios disponibles
curl -X GET "http://localhost:8000/api/available-slots/?doctor=1&date=2025-11-20" \
  -H "Authorization: Bearer $TOKEN"

# 3. Crear una cita
curl -X POST http://localhost:8000/api/appointments/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient": 1,
    "doctor_specialist": 1,
    "appointment_date": "2025-11-20",
    "appointment_time": "09:00:00",
    "duration_minutes": 60
  }'

# 4. Listar todas las citas
curl -X GET http://localhost:8000/api/appointments/ \
  -H "Authorization: Bearer $TOKEN"

# 5. Cancelar una cita
curl -X POST http://localhost:8000/api/appointments/1/cancel/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## ⚠️ Errores Comunes

### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Solución:** Incluye el header `Authorization: Bearer <token>`

### 403 Forbidden

```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Solución:** Tu usuario no tiene los permisos necesarios para esta acción.

### 404 Not Found

```json
{
  "detail": "No encontrado."
}
```

**Solución:** El recurso (cita, doctor, etc.) no existe.

---

## 📞 Soporte

Para más información sobre la implementación del backend, revisa:

- `appointments/serializers.py` - Lógica de validación
- `appointments/views.py` - Lógica de endpoints
- `appointments/models.py` - Estructura de la base de datos
