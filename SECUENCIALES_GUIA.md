# Guía de Uso - Sistema de Secuenciales

## 📋 Descripción General

El sistema de secuenciales permite generar números secuenciales únicos para facturación electrónica, con capacidad de reutilizar secuenciales que fallaron en el proceso de creación de facturas.

## 🔢 ¿Qué es un Secuencial?

Un secuencial es un número único de 9 dígitos que identifica cada factura electrónica. Por ejemplo:

- `000000001` (primera factura)
- `000000002` (segunda factura)
- `000000003` (tercera factura)

## 🎯 Estados de los Secuenciales

Cada secuencial puede tener 3 estados:

| Estado        | Descripción                           | Cuándo se usa                           |
| ------------- | ------------------------------------- | --------------------------------------- |
| **pending**   | Secuencial generado pero aún no usado | Cuando se genera por primera vez        |
| **available** | Secuencial disponible para reutilizar | Cuando la API externa retorna error 400 |
| **used**      | Secuencial usado exitosamente         | Cuando la factura se crea correctamente |

## 📡 Endpoints Disponibles

### 1. Generar Secuencial

**Endpoint:** `POST /api/core/secuencial/generar/`

**Autenticación:** JWT Token requerido

**Body:** Vacío `{}`

**Respuesta Exitosa:**

```json
{
  "sequential": "000000001",
  "sequential_id": 1,
  "status": "pending",
  "reused": false,
  "message": "Nuevo secuencial generado"
}
```

**Respuesta con Reutilización:**

```json
{
  "sequential": "000000005",
  "sequential_id": 5,
  "status": "pending",
  "reused": true,
  "message": "Secuencial reutilizado (previamente fallido)"
}
```

**Campos de la Respuesta:**

- `sequential`: Número secuencial formateado (9 dígitos)
- `sequential_id`: ID del registro (necesario para marcar estado)
- `status`: Estado actual del secuencial
- `reused`: Indica si es un secuencial reutilizado o nuevo
- `message`: Mensaje descriptivo

---

### 2. Marcar Estado del Secuencial

**Endpoint:** `POST /api/core/secuencial/marcar-estado/`

**Autenticación:** JWT Token requerido

**Body:**

```json
{
  "sequential_id": 1,
  "status": "available"
}
```

**Parámetros:**

- `sequential_id`: ID devuelto al generar el secuencial
- `status`: Puede ser `"available"` o `"used"`

**Respuesta Exitosa:**

```json
{
  "message": "Estado actualizado correctamente",
  "sequential": "000000001",
  "status": "available"
}
```

**Respuesta de Error (no está pending):**

```json
{
  "error": "El secuencial no está en estado pending (estado actual: used)",
  "sequential": "000000001",
  "current_status": "used"
}
```

## 🔄 Flujo de Uso Completo

### Escenario 1: Factura Exitosa

```
1. Usuario hace clic en "Generar Secuencial"
   ↓
2. Frontend → POST /api/core/secuencial/generar/
   ↓
3. Backend devuelve: { sequential: "000000001", sequential_id: 1 }
   ↓
4. Frontend intenta crear factura en API Olimpush
   ↓
5. API Olimpush responde: 200 OK (éxito)
   ↓
6. Frontend → POST /api/core/secuencial/marcar-estado/
   Body: { sequential_id: 1, status: "used" }
   ↓
7. ✅ Secuencial marcado como "used" (no se puede reutilizar)
```

### Escenario 2: Factura con Error 400 (Reutilizable)

```
1. Usuario hace clic en "Generar Secuencial"
   ↓
2. Frontend → POST /api/core/secuencial/generar/
   ↓
3. Backend devuelve: { sequential: "000000002", sequential_id: 2 }
   ↓
4. Frontend intenta crear factura en API Olimpush
   ↓
5. API Olimpush responde: 400 Bad Request (error)
   ↓
6. Frontend → POST /api/core/secuencial/marcar-estado/
   Body: { sequential_id: 2, status: "available" }
   ↓
7. 🔄 Secuencial marcado como "available" (se podrá reutilizar)
   ↓
8. Próxima vez que se llame generar/, retornará este secuencial
```

### Escenario 3: Factura con Error 409 (Conflict)

```
1. Usuario hace clic en "Generar Secuencial"
   ↓
2. Frontend → POST /api/core/secuencial/generar/
   ↓
3. Backend devuelve: { sequential: "000000003", sequential_id: 3 }
   ↓
4. Frontend intenta crear factura en API Olimpush
   ↓
5. API Olimpush responde: 409 Conflict (firma no registrada, u otro problema)
   ↓
6. Frontend → POST /api/core/secuencial/marcar-estado/
   Body: { sequential_id: 3, status: "available" }
   ↓
7. 🔄 Secuencial marcado como "available" (se podrá reutilizar)
```

## 💻 Ejemplos de Código

### JavaScript/TypeScript (Frontend)

```typescript
// 1. Generar secuencial
async function generarSecuencial() {
  const response = await fetch(
    "http://localhost:8000/api/core/secuencial/generar/",
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}),
    },
  );

  const data = await response.json();
  console.log(data.sequential); // "000000001"
  return data;
}

// 2. Crear factura y manejar resultado
async function crearFacturaCompleta() {
  // Generar secuencial
  const { sequential, sequential_id } = await generarSecuencial();

  try {
    // Intentar crear factura en Olimpush
    const facturaResponse = await crearFacturaOlimpush(sequential);

    if (facturaResponse.status === 200) {
      // Éxito: marcar como usado
      await marcarSecuencial(sequential_id, "used");
      console.log("✅ Factura creada exitosamente");
    }
  } catch (error) {
    if (error.status === 400) {
      // Error 400: marcar como disponible para reutilizar
      await marcarSecuencial(sequential_id, "available");
      console.log("🔄 Secuencial marcado como disponible para reutilizar");
    } else if (error.status === 409) {
      // Error 409: marcar como disponible (firma no registrada, etc)
      await marcarSecuencial(sequential_id, "available");
      console.log("🔄 Error 409 - Secuencial marcado como disponible");
    }
  }
}

// 3. Marcar estado del secuencial
async function marcarSecuencial(sequentialId, status) {
  await fetch("http://localhost:8000/api/core/secuencial/marcar-estado/", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      sequential_id: sequentialId,
      status: status, // "available" o "used"
    }),
  });
}
```

### Python (Testing)

```python
import requests

# Configuración
BASE_URL = "http://localhost:8000"
TOKEN = "tu_jwt_token_aqui"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 1. Generar secuencial
def generar_secuencial():
    response = requests.post(
        f"{BASE_URL}/api/core/secuencial/generar/",
        headers=HEADERS,
        json={}
    )
    data = response.json()
    print(f"Sequential: {data['sequential']}")
    print(f"ID: {data['sequential_id']}")
    return data

# 2. Marcar estado
def marcar_estado(sequential_id, status):
    response = requests.post(
        f"{BASE_URL}/api/core/secuencial/marcar-estado/",
        headers=HEADERS,
        json={
            "sequential_id": sequential_id,
            "status": status
        }
    )
    print(response.json())

# Ejemplo de uso
if __name__ == "__main__":
    # Generar secuencial
    resultado = generar_secuencial()

    # Simular error 400 -> marcar como disponible
    marcar_estado(resultado['sequential_id'], 'available')

    # El siguiente generar_secuencial() reutilizará este número
```

## 🧪 Pruebas con cURL

### Generar Secuencial

```bash
curl -X POST http://localhost:8000/api/core/secuencial/generar/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Marcar como Disponible (Error 400)

```bash
curl -X POST http://localhost:8000/api/core/secuencial/marcar-estado/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sequential_id": 1,
    "status": "available"
  }'
```

### Marcar como Usado (Éxito)

```bash
curl -X POST http://localhost:8000/api/core/secuencial/marcar-estado/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sequential_id": 1,
    "status": "used"
  }'
```

## ⚙️ Lógica Interna

### Generación de Secuenciales

1. **Primera Verificación:** Busca secuenciales con estado `'available'`
   - Si encuentra uno, lo reutiliza y cambia su estado a `'pending'`
2. **Si no hay disponibles:** Genera nuevo secuencial
   - Incrementa el contador: `last_sequential + 1`
   - Crea registro con estado `'pending'`
   - Formatea a 9 dígitos: `000000001`

### Actualización de Estados

- Solo se pueden actualizar secuenciales en estado `'pending'`
- Estados válidos: `'available'` o `'used'`
- Una vez marcado como `'used'`, no se puede cambiar

## ❓ Preguntas Frecuentes

### ¿Qué pasa si no marco el estado de un secuencial?

Quedará en estado `'pending'` y no se reutilizará. Es importante marcar siempre el estado después de intentar crear la factura.

### ¿Cuándo debo marcar como "available"?

- Cuando la API externa (Olimpush) devuelve error **400 Bad Request**
- Cuando la API externa devuelve error **409 Conflict** (firma no registrada, problemas de configuración, etc.)
- En cualquier error que indique que el secuencial NO fue usado realmente

### ¿Cuándo debo marcar como "used"?

- Cuando la factura se crea exitosamente (200 OK)
- Cuando estés seguro de que el secuencial fue consumido/registrado en el sistema externo

### ¿Los secuenciales empiezan desde 1?

Sí, el primer secuencial generado será `000000001`.

### ¿Puedo resetear el contador?

Sí, pero requiere acceso a la base de datos. Puedes eliminar los registros de `SequentialUsage` y resetear `last_sequential` a 0 en la tabla `sequentials`.

## 🔒 Seguridad

- ✅ Todos los endpoints requieren autenticación JWT
- ✅ Transacciones atómicas para evitar duplicados
- ✅ Validación de estados antes de actualizar

## 📊 Tablas de Base de Datos

### `sequentials`

```sql
id                   BIGINT (PK)
last_sequential      INTEGER
created_at           DATETIME
updated_at           DATETIME
```

### `sequential_usages`

```sql
id                   BIGINT (PK)
sequential_id        BIGINT (FK)
sequential_number    INTEGER
status               VARCHAR(10)  -- 'available', 'pending', 'used'
created_at           DATETIME
updated_at           DATETIME
```

## 🚀 Migraciones

Para aplicar estos modelos a la base de datos:

```bash
python manage.py makemigrations core
python manage.py migrate
```

---

**Última actualización:** Febrero 2026
