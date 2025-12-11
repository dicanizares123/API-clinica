# 📝 Integración del Formulario de Citas - Guía Completa

## 🎯 Flujo del Formulario

Tu formulario necesita **3 pasos** principales:

```
1. Registrar/Buscar Paciente → Obtener patient_id
2. Seleccionar Doctor → Obtener doctor_id y doctor_specialist_id
3. Seleccionar Fecha y Hora → Crear la cita
```

---

## 📋 Endpoints Necesarios (TODOS PÚBLICOS)

### 1️⃣ Buscar Paciente por Cédula

**Úsalo primero para verificar si el paciente ya existe**

```javascript
GET http://localhost:8000/api/patients/by_document/{cedula}/
```

**Ejemplo:**

```javascript
const searchPatient = async (documentId) => {
  const response = await fetch(
    `http://localhost:8000/api/patients/by_document/${documentId}/`
  );

  if (response.ok) {
    const patient = await response.json();
    console.log("Paciente encontrado:", patient);
    return patient; // Tiene patient.id
  } else {
    console.log("Paciente no existe, debe registrarse");
    return null;
  }
};
```

**Respuesta si existe:**

```json
{
  "id": 1,
  "uuid": "a1b2c3d4-...",
  "first_names": "Juan Carlos",
  "last_names": "Pérez García",
  "full_name": "Juan Carlos Pérez García",
  "document_id": "1234567890",
  "email": "juan@email.com",
  "phone_number": "0987654321",
  "address": "",
  "is_active": true,
  "created_at": "2025-11-19T10:00:00Z",
  "updated_at": "2025-11-19T10:00:00Z"
}
```

**Respuesta si NO existe (404):**

```json
{
  "exists": false,
  "message": "Paciente no encontrado"
}
```

---

### 2️⃣ Crear/Actualizar Paciente

**Si el paciente no existe o quiere actualizar sus datos**

```javascript
POST http://localhost:8000/api/patients/
Content-Type: application/json

{
  "first_names": "Juan Carlos",
  "last_names": "Pérez García",
  "document_id": "1234567890",
  "email": "juan@email.com",
  "phone_number": "0987654321",
  "address": ""  // Opcional
}
```

**Ejemplo:**

```javascript
const createPatient = async (formData) => {
  const response = await fetch("http://localhost:8000/api/patients/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      first_names: formData.firstName,
      last_names: formData.lastName,
      document_id: formData.documentId,
      email: formData.email,
      phone_number: formData.phone,
      address: formData.address || "",
    }),
  });

  const patient = await response.json();
  console.log("Paciente creado/actualizado:", patient);
  return patient.id; // Guardar este ID para la cita
};
```

**Comportamiento:**

- Si la cédula ya existe: **Actualiza** los datos del paciente
- Si la cédula no existe: **Crea** un nuevo paciente

**Respuesta (201 Created):**

```json
{
  "id": 1,
  "uuid": "a1b2c3d4-...",
  "first_names": "Juan Carlos",
  "last_names": "Pérez García",
  "full_name": "Juan Carlos Pérez García",
  "document_id": "1234567890",
  "email": "juan@email.com",
  "phone_number": "0987654321",
  "address": "",
  "is_active": true,
  "created_at": "2025-11-19T10:00:00Z",
  "updated_at": "2025-11-19T10:00:00Z"
}
```

---

### 3️⃣ Listar Doctores Disponibles

**Para llenar el select de doctores**

```javascript
GET http://localhost:8000/api/doctors/
```

**Ejemplo:**

```javascript
const loadDoctors = async () => {
  const response = await fetch("http://localhost:8000/api/doctors/");
  const doctors = await response.json();

  // Llenar select
  const selectDoctor = document.getElementById("doctor");
  selectDoctor.innerHTML =
    '<option value="">-- Selecciona un doctor --</option>';

  doctors.forEach((doctor) => {
    const option = document.createElement("option");
    option.value = doctor.primary_specialty; // ID del DoctorSpecialty
    option.textContent = `${doctor.full_name} - ${doctor.primary_specialty_name}`;
    option.dataset.doctorId = doctor.id; // Guardar ID del doctor
    selectDoctor.appendChild(option);
  });
};
```

**Respuesta (200 OK):**

```json
[
  {
    "id": 1,
    "full_name": "Dr(a). María González Pérez",
    "primary_specialty": 1,
    "primary_specialty_name": "Psicología Clínica",
    "professional_id": "PSI-12345"
  },
  {
    "id": 2,
    "full_name": "Dr(a). Carlos Ramírez López",
    "primary_specialty": 2,
    "primary_specialty_name": "Medicina General",
    "professional_id": "MED-67890"
  }
]
```

---

### 4️⃣ Consultar Horarios Disponibles

**Cuando el usuario selecciona fecha y doctor**

```javascript
GET http://localhost:8000/api/available-slots/?doctor={doctor_id}&date={YYYY-MM-DD}
```

**Ejemplo:**

```javascript
const loadAvailableSlots = async (doctorId, date) => {
  const response = await fetch(
    `http://localhost:8000/api/available-slots/?doctor=${doctorId}&date=${date}`
  );

  const data = await response.json();

  if (data.available_slots.length === 0) {
    document.getElementById("slots-message").textContent =
      "No hay horarios disponibles para esta fecha";
    document.getElementById("time-select").innerHTML = "";
    return;
  }

  // Llenar select de horarios
  const selectTime = document.getElementById("time-select");
  selectTime.innerHTML = data.available_slots
    .map((slot) => `<option value="${slot}">${slot.substring(0, 5)}</option>`)
    .join("");
};
```

**Respuesta (200 OK):**

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

---

### 5️⃣ Crear la Cita

**Cuando el usuario confirma el agendamiento**

```javascript
POST http://localhost:8000/api/appointments/
Content-Type: application/json

{
  "patient": 1,
  "doctor_specialist": 1,
  "appointment_date": "2025-11-20",
  "appointment_time": "09:00:00",
  "duration_minutes": 60,
  "notes": ""
}
```

**Ejemplo:**

```javascript
const createAppointment = async (patientId, doctorSpecialtyId, date, time) => {
  const response = await fetch("http://localhost:8000/api/appointments/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      patient: patientId,
      doctor_specialist: doctorSpecialtyId,
      appointment_date: date,
      appointment_time: time,
      duration_minutes: 60,
      notes: "",
    }),
  });

  if (response.ok) {
    const appointment = await response.json();
    alert(
      `✅ Cita agendada exitosamente!\nFecha: ${appointment.appointment_date}\nHora: ${appointment.appointment_time}\nCódigo: ${appointment.uuid}`
    );
    return appointment;
  } else {
    const error = await response.json();
    alert(`❌ Error: ${JSON.stringify(error)}`);
  }
};
```

**Respuesta (201 Created):**

```json
{
  "id": 5,
  "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "patient": 1,
  "patient_name": "Juan Carlos Pérez García",
  "doctor_specialist": 1,
  "doctor_name": "Dr(a). María González Pérez",
  "specialty_name": "Psicología Clínica",
  "appointment_date": "2025-11-20",
  "appointment_time": "09:00:00",
  "duration_minutes": 60,
  "status": "scheduled",
  "status_display": "Agendada",
  "notes": "",
  "created_at": "2025-11-19T10:30:00Z",
  "updated_at": "2025-11-19T10:30:00Z"
}


## 📊 Resumen de Endpoints

| Paso | Endpoint                              | Método | ¿Público? | Propósito                 |
| ---- | ------------------------------------- | ------ | --------- | ------------------------- |
| 1    | `/api/patients/by_document/{cedula}/` | GET    | ✅        | Buscar paciente existente |
| 2    | `/api/patients/`                      | POST   | ✅        | Crear/actualizar paciente |
| 3    | `/api/doctors/`                       | GET    | ✅        | Listar doctores           |
| 4    | `/api/available-slots/`               | GET    | ✅        | Ver horarios disponibles  |
| 5    | `/api/appointments/`                  | POST   | ✅        | Agendar la cita           |


## ✅ Validaciones Automáticas

El backend valida automáticamente:

1. ✅ Que el doctor tenga horario configurado para ese día
2. ✅ Que la hora esté dentro del horario del doctor
3. ✅ Que no haya otra cita en ese horario
4. ✅ Que el horario no esté bloqueado
5. ✅ Que la cédula del paciente sea única
```
