# Formato de Respuestas API

Todas las respuestas de la API incluyen un campo `api` para identificar su origen.

## Campo identificador: `api`

Este campo indica de dónde proviene la respuesta:

- **`"api": "djangoclinica"`** - Respuesta de la API Django propia
- **`"api": "olimpush"`** - Respuesta del servicio externo de Olimpush (facturación)

---

## Respuestas de Django (`api: "djangoclinica"`)

### ✅ Respuesta exitosa

```json
{
  "success": true,
  "status_code": 200,
  "message": "Paciente encontrado",
  "data": {
    "id": 1,
    "first_names": "Juan",
    "last_names": "Pérez",
    "document_id": "1234567890"
  },
  "api": "djangoclinica"
}
```

### ❌ Respuesta de error

```json
{
  "success": false,
  "status_code": 404,
  "message": "Paciente no encontrado",
  "errors": null,
  "api": "djangoclinica"
}
```

### ❌ Error de autenticación

```json
{
  "success": false,
  "status_code": 401,
  "message": "Las credenciales de autenticación no se proveyeron.",
  "errors": null,
  "api": "djangoclinica"
}
```

---

## Respuestas de Olimpush (`api: "olimpush"`)

### ✅ Respuesta exitosa (RUC válido)

```json
{
  "code": 200,
  "status": "OK",
  "message": "Proceso ejecutado correctamente",
  "data": "El ruc existe",
  "api": "olimpush"
}
```

### ❌ Error 400 (RUC inválido)

```json
{
  "code": 400,
  "status": "ERROR",
  "message": "El RUC :rucConsultar no es válido. El RUC solo debe contener dígitos (0-9).",
  "data": null,
  "api": "olimpush"
}
```

### ❌ Error 404 (RUC no existe)

```json
{
  "code": 404,
  "status": "ERROR",
  "message": "El RUC no existe en el SRI",
  "data": null,
  "api": "olimpush"
}
```

### ❌ Error de conexión (generado por Django proxy)

```json
{
  "code": 503,
  "status": "ERROR",
  "message": "No se pudo conectar con el servicio de facturación",
  "data": null,
  "api": "olimpush"
}
```

---

## Uso en Frontend

### Detección del origen de la respuesta

```typescript
const response = await fetch("/api/endpoint");
const json = await response.json();

// Identificar origen de la respuesta
if (json.api === "djangoclinica") {
  // Respuesta de tu API Django
  if (json.success) {
    console.log("Éxito Django:", json.data);
  } else {
    console.error("Error Django:", json.message);
  }
} else if (json.api === "olimpush") {
  // Respuesta de API externa Olimpush
  if (json.status === "OK") {
    console.log("Éxito Olimpush:", json.data);
  } else {
    console.error("Error Olimpush:", json.message);
  }
}
```

### Función helper para manejo unificado

```typescript
interface APIResponse {
  // Django
  success?: boolean;
  status_code?: number;
  // Olimpush
  code?: number;
  status?: string;
  // Común
  message: string;
  data: any;
  api: "djangoclinica" | "olimpush";
}

function handleAPIResponse(response: APIResponse) {
  const isSuccess =
    response.api === "djangoclinica"
      ? response.success
      : response.status === "OK";

  if (isSuccess) {
    return { success: true, data: response.data };
  } else {
    return { success: false, error: response.message };
  }
}

// Uso
const result = handleAPIResponse(json);
if (result.success) {
  console.log(result.data);
} else {
  console.error(result.error);
}
```

---

## Diferencias en formato

| Campo       | Django                 | Olimpush               |
| ----------- | ---------------------- | ---------------------- |
| **Éxito**   | `success: true/false`  | `status: "OK"/"ERROR"` |
| **Código**  | `status_code: 200`     | `code: 200`            |
| **Mensaje** | `message: "..."`       | `message: "..."`       |
| **Datos**   | `data: {...}`          | `data: {...}`          |
| **Origen**  | `api: "djangoclinica"` | `api: "olimpush"`      |

---

## Beneficios

✅ **Identificación clara**: Sabes inmediatamente de dónde viene la respuesta  
✅ **Debugging facilitado**: Logs más descriptivos  
✅ **Manejo condicional**: Puedes aplicar lógica diferente según el origen  
✅ **Monitoreo**: Estadísticas separadas por servicio  
✅ **Troubleshooting**: Identificar rápidamente si el problema es interno o externo
