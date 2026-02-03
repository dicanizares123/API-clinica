# API Proxy - Olimpush Facturación Electrónica

Este módulo actúa como proxy entre el frontend y la API de Olimpush para servicios de facturación electrónica del SRI de Ecuador.

## Configuración

### 1. Variables de entorno (.env)

Agrega estas variables a tu archivo `.env`:

```bash
OLIMPUSH_API_URL=https://test-facturacion.olimpush.com/apifacturacion/v2/facturadorelectronico
OLIMPUSH_API_TOKEN=tu_token_aqui
```

**Importante**: Solicita el token `olimpush-token` al administrador del sistema de Olimpush.

### 2. URLs configuradas

El servicio está disponible en: `/api/olimpush/`

---

## Endpoints Disponibles

### 1. Validar RUC

Valida si un RUC existe en el SRI.

**Endpoint:**

```
GET /api/olimpush/ruc/{ruc}/validation/
```

**Autenticación:** JWT Bearer Token requerido

**Parámetros de ruta:**

- `ruc` (string): Número de RUC a validar (13 dígitos)

**Ejemplo de petición desde Next.js:**

```typescript
const validarRUC = async (ruc: string) => {
  const response = await fetch(
    `http://localhost:8000/api/olimpush/ruc/${ruc}/validation/`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    },
  );

  const data = await response.json();
  return data;
};

// Uso
const resultado = await validarRUC("1234567890001");
```

**Respuestas posibles:**

#### ✅ 200 - RUC existe

```json
{
  "code": 200,
  "status": "OK",
  "message": "Proceso ejecutado correctamente",
  "data": "El ruc existe"
}
```

#### ❌ 400 - RUC incorrecto (formato inválido)

```json
{
  "code": 400,
  "status": "ERROR",
  "message": "El RUC :rucConsultar no es válido. El RUC solo debe contener dígitos (0-9).",
  "data": null
}
```

#### ❌ 404 - RUC no existe

```json
{
  "code": 404,
  "status": "ERROR",
  "message": "El RUC no existe en el SRI",
  "data": null
}
```

#### ❌ 401 - Sin autenticación

```json
{
  "success": false,
  "status_code": 401,
  "message": "Las credenciales de autenticación no se proveyeron.",
  "errors": null
}
```

---

### 2. Consultar Establecimientos

Consulta todos los establecimientos asociados a un RUC.

**Endpoint:**

```
GET /api/olimpush/ruc/{ruc}/establishments/
```

**Autenticación:** JWT Bearer Token requerido

**Parámetros de ruta:**

- `ruc` (string): Número de RUC a consultar (13 dígitos)

**Ejemplo de petición desde Next.js:**

```typescript
const consultarEstablecimientos = async (ruc: string) => {
  const response = await fetch(
    `http://localhost:8000/api/olimpush/ruc/${ruc}/establishments/`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    },
  );

  const data = await response.json();
  return data;
};

// Uso
const establecimientos = await consultarEstablecimientos("1234567890001");
console.log(establecimientos.data); // Array de establecimientos
```

**Respuestas posibles:**

#### ✅ 200 - Establecimientos encontrados

```json
{
  "code": 200,
  "status": "OK",
  "message": "Proceso ejecutado correctamente",
  "data": [
    {
      "nombreFantasiaComercial": null,
      "tipoEstablecimiento": "MAT",
      "direccionCompleta": "PICHINCHA / QUITO / VIA MANUELA AGUIRRE",
      "estado": "ABIERTO",
      "numeroEstablecimiento": "001",
      "matriz": "SI"
    },
    {
      "nombreFantasiaComercial": null,
      "tipoEstablecimiento": "OFI",
      "direccionCompleta": "PICHINCHA / QUITO / SANTO DOMINGO DE LOS COLORADOS / VIA MANUELA AGUIRRE",
      "estado": "ABIERTO",
      "numeroEstablecimiento": "002",
      "matriz": "NO"
    }
  ],
  "api": "olimpush"
}
```

#### ❌ 400 - RUC incorrecto

```json
{
  "code": 400,
  "status": "ERROR",
  "message": "El RUC :rucConsultar no es válido. El RUC solo debe contener dígitos (0-9).",
  "data": null,
  "api": "olimpush"
}
```

**Campos del establecimiento:**

- `nombreFantasiaComercial`: Nombre comercial del establecimiento (puede ser null)
- `tipoEstablecimiento`: Tipo (MAT=Matriz, SUC=Sucursal, OFI=Oficina, etc.)
- `direccionCompleta`: Dirección completa del establecimiento
- `estado`: Estado actual (ABIERTO, CERRADO)
- `numeroEstablecimiento`: Código del establecimiento (001, 002, etc.)
- `matriz`: Indica si es matriz ("SI"/"NO")

---

### 3. Consultar Información Completa del RUC

Consulta información detallada del contribuyente asociado a un RUC.

**Endpoint:**

```
GET /api/olimpush/ruc/{ruc}/
```

**Autenticación:** JWT Bearer Token requerido

**Parámetros de ruta:**

- `ruc` (string): Número de RUC a consultar (13 dígitos)

**Ejemplo de petición desde Next.js:**

```typescript
const consultarRUCInfo = async (ruc: string) => {
  const response = await fetch(
    `http://localhost:8000/api/olimpush/ruc/${ruc}/`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    },
  );

  const data = await response.json();
  return data;
};

// Uso
const info = await consultarRUCInfo("2390012562001");
console.log(info.data[0].razonSocial); // Nombre de la empresa
console.log(info.data[0].representantesLegales); // Array de representantes
```

**Respuestas posibles:**

#### ✅ 200 - Información del RUC

```json
{
  "code": 200,
  "status": "OK",
  "message": "Proceso ejecutado correctamente",
  "data": [
    {
      "numeroRuc": "2390012562001",
      "razonSocial": "TELEALFACOM S.A.",
      "estadoContribuyenteRuc": "ACTIVO",
      "actividadEconomicaPrincipal": "ACTIVIDADES DE REVENTA DE SERVICIOS DE TELECOMUNICACIONES...",
      "tipoContribuyente": "SOCIEDAD",
      "regimen": "GENERAL",
      "categoria": null,
      "obligadoLlevarContabilidad": "SI",
      "agenteRetencion": "SI",
      "contribuyenteEspecial": "SI",
      "informacionFechasContribuyente": {
        "fechaInicioActividades": "2012-09-13 00:00:00.0",
        "fechaCese": "",
        "fechaReinicioActividades": "",
        "fechaActualizacion": "2025-09-01 15:55:28.0"
      },
      "representantesLegales": [
        {
          "identificacion": "1714846043",
          "nombre": "GUALOTUÑA HENRIQUEZ JUAN CARLOS"
        }
      ],
      "motivoCancelacionSuspension": null,
      "contribuyenteFantasma": "NO",
      "transaccionesInexistente": "NO"
    }
  ],
  "api": "olimpush"
}
```

#### ❌ 400 - RUC incorrecto

```json
{
  "code": 400,
  "status": "ERROR",
  "message": "El RUC :rucConsultar no es válido. El RUC solo debe contener dígitos (0-9).",
  "data": null,
  "api": "olimpush"
}
```

#### ❌ 404 - RUC no encontrado

```json
{
  "code": 404,
  "status": "ERROR",
  "message": "No se encontró información para el RUC consultado",
  "data": null,
  "api": "olimpush"
}
```

**Campos de información del contribuyente:**

- `numeroRuc`: Número de RUC
- `razonSocial`: Razón social o nombre del contribuyente
- `estadoContribuyenteRuc`: Estado (ACTIVO, SUSPENDIDO, CANCELADO)
- `actividadEconomicaPrincipal`: Descripción de la actividad económica principal
- `tipoContribuyente`: Tipo (PERSONA NATURAL, SOCIEDAD, etc.)
- `regimen`: Régimen tributario (GENERAL, RIMPE, etc.)
- `obligadoLlevarContabilidad`: "SI" o "NO"
- `agenteRetencion`: "SI" o "NO"
- `contribuyenteEspecial`: "SI" o "NO"
- `informacionFechasContribuyente`: Objeto con fechas relevantes
- `representantesLegales`: Array con identificación y nombre de representantes
- `contribuyenteFantasma`: "SI" o "NO"
- `transaccionesInexistente`: "SI" o "NO"

---

### 4. Consultar Contribuyente en Olimpush

Consulta información de un contribuyente registrado en el sistema de Olimpush (no en el SRI).

**Endpoint:**

```
GET /api/olimpush/contribuyentes/{ruc}/
```

**Autenticación:** JWT Bearer Token requerido

**Parámetros de ruta:**

- `ruc` (string): Número de RUC del contribuyente (13 dígitos)

**Ejemplo de petición desde Next.js:**

```typescript
const consultarContribuyente = async (ruc: string) => {
  const response = await fetch(
    `http://localhost:8000/api/olimpush/contribuyentes/${ruc}/`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    },
  );

  const data = await response.json();
  return data;
};

// Uso
const contribuyente = await consultarContribuyente("2390012562001");
console.log(contribuyente.data.socialReason); // Razón social
console.log(contribuyente.data.urlLogo); // URL del logo
```

**Respuestas posibles:**

#### ✅ 200 - Contribuyente encontrado

```json
{
  "code": 200,
  "status": "OK",
  "message": "Proceso ejecutado correctamente",
  "data": {
    "socialReason": "OlimPush Facturacion",
    "ruc": "2390012562001",
    "signatureDoc": "1710774640001-1766208529416.p12",
    "createAt": "2025-11-09 03:50:51",
    "urlLogo": "https://test-facturacion.olimpush.com/images/logos/1090012562001-1763932931587.png"
  },
  "api": "olimpush"
}
```

#### ❌ 404 - Contribuyente no existe

```json
{
  "code": 404,
  "status": "ERROR",
  "message": "Contribuyente no existe",
  "data": null,
  "api": "olimpush"
}
```

**Campos del contribuyente:**

- `socialReason`: Razón social del contribuyente
- `ruc`: Número de RUC
- `signatureDoc`: Nombre del archivo de firma electrónica (.p12)
- `createAt`: Fecha de registro en Olimpush
- `urlLogo`: URL completa del logo del contribuyente

**Diferencia con endpoint /ruc/{ruc}/**:

- `/ruc/{ruc}/` consulta información del **SRI** (registro público)
- `/contribuyentes/{ruc}/` consulta información del **sistema Olimpush** (configuración de facturación)

---

### 5. Registrar Logo del Contribuyente

Registra el logo de un contribuyente asociado a un RUC. El logo será utilizado en la generación del documento PDF (RIDE) de los comprobantes electrónicos, permitiendo personalización visual que refuerza la identidad corporativa de la empresa emisora.

**⚠️ Requisito previo**: Antes de registrar el logo, es necesario haber registrado al contribuyente en el sistema de Olimpush.

**⚠️ Nota importante**: El registro de logos es específico por ambiente. Si registra un logo en el ambiente de pruebas, este solo será utilizado en los documentos generados en dicho ambiente. Para usar un logo en producción, deberá registrarlo nuevamente en ese ambiente.

**Endpoint:**

```
POST /api/olimpush/contribuyentes/{ruc}/logo/
```

**Autenticación:** JWT Bearer Token requerido

**Content-Type:** `multipart/form-data`

**Parámetros de ruta:**

- `ruc` (string): Número de RUC del contribuyente (13 dígitos)

**Parámetros del body:**

- `logo` (file): Archivo de imagen. Formatos permitidos: `png`, `jpg`, `jpeg`

**Ejemplo de petición desde Next.js:**

```typescript
const registrarLogo = async (ruc: string, logoFile: File) => {
  const formData = new FormData();
  formData.append("logo", logoFile);

  const response = await fetch(
    `http://localhost:8000/api/olimpush/contribuyentes/${ruc}/logo/`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        // NO incluir Content-Type, el navegador lo establece automáticamente con el boundary
      },
      body: formData,
    },
  );

  const data = await response.json();
  return data;
};

// Uso con input file
const handleLogoUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
  const file = event.target.files?.[0];
  if (!file) return;

  // Validar extensión
  const allowedTypes = ["image/png", "image/jpeg", "image/jpg"];
  if (!allowedTypes.includes(file.type)) {
    alert("Solo se permiten archivos PNG, JPG o JPEG");
    return;
  }

  try {
    const resultado = await registrarLogo("2390012562001", file);
    console.log("Logo registrado:", resultado.data.urlLogo);
  } catch (error) {
    console.error("Error al registrar logo:", error);
  }
};
```

**Respuestas posibles:**

#### ✅ 201 - Logo registrado correctamente

```json
{
  "code": 201,
  "status": "OK",
  "message": "Logo guardado correctamente.",
  "data": {
    "urlLogo": "https://test-facturacion.olimpush.com/images/logos/2324574640001-7864009601813.png"
  },
  "api": "olimpush"
}
```

#### ❌ 404 - Contribuyente no existe

```json
{
  "code": 404,
  "status": "ERROR",
  "message": "Contribuyente no existe",
  "data": null,
  "api": "olimpush"
}
```

#### ❌ 400 - Formato de archivo no permitido

```json
{
  "success": false,
  "status_code": 400,
  "message": "Formato de archivo no permitido. Use: png, jpg, jpeg",
  "data": null,
  "api": "djangoclinica"
}
```

#### ❌ 400 - No se proporcionó archivo

```json
{
  "success": false,
  "status_code": 400,
  "message": "No se proporcionó ningún archivo de logo",
  "data": null,
  "api": "djangoclinica"
}
```

**Campos de respuesta exitosa:**

- `urlLogo`: URL completa donde está alojado el logo registrado. Este logo será usado en la generación de PDFs de facturas electrónicas.

**Recomendaciones:**

- Tamaño recomendado: 200x200 píxeles o similar
- Peso máximo recomendado: 500KB
- Formato preferido: PNG con fondo transparente
- El logo debe tener buena resolución para impresión

---

### 6. Registrar Firma Electrónica

Registra la firma electrónica (certificado digital) de un contribuyente asociado a un RUC. La firma electrónica será utilizada para firmar comprobantes electrónicos. Es necesario proporcionar la contraseña del certificado en texto plano durante el registro, ya que el certificado se cargará una sola vez y no será necesario enviar esta información cada vez que se autorice un documento electrónico.

**⚠️ Requisito previo**: Antes de registrar la firma electrónica, es necesario haber registrado al contribuyente en el sistema de Olimpush.

**⚠️ Seguridad**: La contraseña se envía en texto plano pero a través de HTTPS. El certificado se almacena de forma segura en Olimpush y no será necesario volver a enviarlo para cada documento.

**Endpoint:**

```
POST /api/olimpush/contribuyentes/{ruc}/certificado/
```

**Autenticación:** JWT Bearer Token requerido

**Content-Type:** `multipart/form-data`

**Parámetros de ruta:**

- `ruc` (string): Número de RUC del contribuyente (13 dígitos)

**Parámetros del body:**

- `firma` (file): Certificado de firma electrónica en formato `.p12`
- `password` (string): Contraseña del certificado en texto plano

**Ejemplo de petición desde Next.js:**

```typescript
const registrarFirmaElectronica = async (
  ruc: string,
  certificadoFile: File,
  password: string,
) => {
  const formData = new FormData();
  formData.append("firma", certificadoFile);
  formData.append("password", password);

  const response = await fetch(
    `http://localhost:8000/api/olimpush/contribuyentes/${ruc}/certificado/`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        // NO incluir Content-Type, el navegador lo establece automáticamente
      },
      body: formData,
    },
  );

  const data = await response.json();
  return data;
};

// Uso con input file y password
const handleCertificadoUpload = async (
  event: React.ChangeEvent<HTMLInputElement>,
) => {
  const file = event.target.files?.[0];
  if (!file) return;

  // Validar extensión
  if (!file.name.endsWith(".p12")) {
    alert("Solo se permiten archivos .p12");
    return;
  }

  // Solicitar contraseña al usuario
  const password = prompt("Ingrese la contraseña del certificado:");
  if (!password) return;

  try {
    const resultado = await registrarFirmaElectronica(
      "2390012562001",
      file,
      password,
    );
    console.log("Certificado registrado:", resultado.data);
    alert("Firma electrónica registrada correctamente");
  } catch (error) {
    console.error("Error al registrar firma:", error);
  }
};
```

**Respuestas posibles:**

#### ✅ 200 - Certificado registrado correctamente

```json
{
  "code": 200,
  "status": "OK",
  "message": "Certificado registrado correctamente.",
  "data": "1723774640001-1766208529416.p12",
  "api": "olimpush"
}
```

#### ❌ 404 - Contribuyente no existe

```json
{
  "code": 404,
  "status": "ERROR",
  "message": "Contribuyente no existe",
  "data": null,
  "api": "olimpush"
}
```

#### ❌ 400 - Formato de archivo no permitido

```json
{
  "success": false,
  "status_code": 400,
  "message": "Formato de archivo no permitido. Solo se acepta .p12",
  "data": null,
  "api": "djangoclinica"
}
```

#### ❌ 400 - No se proporcionó archivo

```json
{
  "success": false,
  "status_code": 400,
  "message": "No se proporcionó ningún archivo de certificado (.p12)",
  "data": null,
  "api": "djangoclinica"
}
```

#### ❌ 400 - No se proporcionó contraseña

```json
{
  "success": false,
  "status_code": 400,
  "message": "No se proporcionó la contraseña del certificado",
  "data": null,
  "api": "djangoclinica"
}
```

#### ❌ 400 - Contraseña incorrecta

```json
{
  "code": 400,
  "status": "ERROR",
  "message": "Contraseña del certificado incorrecta",
  "data": null,
  "api": "olimpush"
}
```

**Campos de respuesta exitosa:**

- `data`: Nombre del archivo de certificado almacenado en Olimpush. Este será el `signatureDoc` que aparece al consultar el contribuyente.

**Información importante:**

- El certificado debe ser emitido por una autoridad certificadora reconocida por el SRI (Security Data, ANF, BCE, etc.)
- El certificado debe estar vigente (no vencido)
- La contraseña debe ser correcta o la API retornará error
- Una vez registrado, el certificado se puede actualizar enviando uno nuevo
- El nombre del archivo retornado es un identificador único generado por Olimpush

**Recomendaciones de seguridad:**

- Nunca almacenar la contraseña del certificado en el frontend
- Solicitar la contraseña al usuario solo cuando vaya a registrar/actualizar el certificado
- La comunicación debe ser siempre sobre HTTPS
- Considerar implementar un formulario con input type="password"

---

### 7. Eliminar Firma Electrónica

Elimina el certificado de firma electrónica asociado a un contribuyente identificado por su RUC. Al eliminar el certificado, este dejará de utilizarse para la firma de comprobantes electrónicos. La eliminación es permanente y, una vez realizada, será necesario volver a registrar un nuevo certificado si se desea continuar con la firma de documentos electrónicos.

**⚠️ Acción irreversible**: La eliminación del certificado es permanente. Asegúrese de que realmente desea eliminar el certificado antes de ejecutar esta acción.

**Endpoint:**

```
DELETE /api/olimpush/contribuyentes/{ruc}/certificado/delete/
```

**Autenticación:** JWT Bearer Token requerido

**Parámetros de ruta:**

- `ruc` (string): Número de RUC del contribuyente (13 dígitos)

**Sin parámetros en el body**

**Ejemplo de petición desde Next.js:**

```typescript
const eliminarFirmaElectronica = async (ruc: string) => {
  const response = await fetch(
    `http://localhost:8000/api/olimpush/contribuyentes/${ruc}/certificado/delete/`,
    {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    },
  );

  const data = await response.json();
  return data;
};

// Uso con confirmación
const handleEliminarCertificado = async (ruc: string) => {
  // Confirmar acción
  const confirmacion = confirm(
    "¿Está seguro de que desea eliminar el certificado de firma electrónica? " +
      "Esta acción es irreversible.",
  );

  if (!confirmacion) return;

  try {
    const resultado = await eliminarFirmaElectronica("2390012562001");
    console.log("Certificado eliminado:", resultado.message);
    alert("Certificado eliminado correctamente");
  } catch (error) {
    console.error("Error al eliminar certificado:", error);
  }
};
```

**Respuestas posibles:**

#### ✅ 200 - Certificado eliminado correctamente

```json
{
  "code": 200,
  "status": "OK",
  "message": "Certficado eliminado correctamente.",
  "api": "olimpush"
}
```

#### ❌ 404 - Contribuyente no existe

```json
{
  "code": 404,
  "status": "ERROR",
  "message": "Contribuyente no existe",
  "data": null,
  "api": "olimpush"
}
```

**Casos de uso:**

- Renovación de certificado vencido: Eliminar el certificado antiguo antes de registrar uno nuevo
- Cambio de autoridad certificadora: Eliminar certificado actual para registrar uno de otra entidad
- Desactivación temporal: Eliminar certificado si no se desea emitir documentos electrónicos temporalmente
- Seguridad: Eliminar certificado comprometido inmediatamente

**Flujo recomendado para renovación:**

1. Verificar que el nuevo certificado es válido (.p12 y contraseña correcta)
2. Eliminar el certificado actual usando este endpoint
3. Registrar el nuevo certificado usando el endpoint de registro
4. Verificar que el nuevo certificado quedó registrado consultando el contribuyente

---

## Utilidades

### 8. Generar Clave de Acceso

Genera una clave de acceso única de 49 dígitos requerida para todos los comprobantes electrónicos en Ecuador. La clave de acceso es un identificador único que valida la autenticidad del documento electrónico ante el SRI.

**📋 Información**: La clave de acceso debe generarse antes de crear cualquier documento electrónico (factura, nota de crédito, etc.). Es un requisito obligatorio del SRI.

**Endpoint:**

```
POST /api/olimpush/util/clave-acceso/
```

**Autenticación:** JWT Bearer Token requerido

**Content-Type:** `application/json`

**Parámetros del body:**

- `origin` (string): Origen del consumo de la API (ej: "NextJS", "Web")
- `usrRequest` (string): Usuario que consume la API
- `ipRequest` (string): IP del cliente
- `transactionIde` (string): Identificación única de la transacción (puede ser un UUID)
- `payload` (object): Objeto con la información del documento:
  - `emissionDate` (string): Fecha de emisión en formato `dd/mm/yyyy`
  - `codeDocumentType` (string): Código del tipo de comprobante:
    - `01` = Factura
    - `04` = Nota de crédito
    - `05` = Nota de débito
    - `06` = Guía de remisión
    - `07` = Comprobante de retención
  - `ruc` (string): RUC del contribuyente emisor (13 dígitos)
  - `establishmentCode` (string): Código del establecimiento (3 dígitos, ej: "001")
  - `pointCode` (string): Código del punto de emisión (3 dígitos, ej: "002")
  - `sequentialNumber` (string): Número secuencial del documento (9 dígitos, ej: "000000001")

**Ejemplo de petición desde Next.js:**

```typescript
const generarClaveAcceso = async (
  emissionDate: string,
  codeDocumentType: string,
  ruc: string,
  establishmentCode: string,
  pointCode: string,
  sequentialNumber: string,
) => {
  const payload = {
    origin: "NextJS",
    usrRequest: "WebUser",
    ipRequest: "192.168.1.100",
    transactionIde: crypto.randomUUID(),
    payload: {
      emissionDate,
      codeDocumentType,
      ruc,
      establishmentCode,
      pointCode,
      sequentialNumber,
    },
  };

  const response = await fetch(
    `http://localhost:8000/api/olimpush/util/clave-acceso/`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    },
  );

  const data = await response.json();
  return data;
};

// Uso
const resultado = await generarClaveAcceso(
  "07/11/2025",
  "01",
  "1705818431001",
  "001",
  "002",
  "000000640",
);
console.log("Clave de acceso:", resultado.data);
```

**Respuestas posibles:**

#### ✅ 200 - Clave de acceso generada

```json
{
  "code": 200,
  "status": "OK",
  "message": "Proceso ejecutado correctamente",
  "data": "0711202501172377464000110030020000006406445369812",
  "api": "olimpush"
}
```

#### ❌ 400 - Campos vacíos

```json
{
  "success": false,
  "status_code": 400,
  "message": "Campo requerido faltante: payload",
  "data": null,
  "api": "djangoclinica"
}
```

#### ❌ 400 - Valores incorrectos

```json
{
  "code": 400,
  "status": "ERROR",
  "message": "El formato de fecha es incorrecto. Use dd/mm/yyyy",
  "data": null,
  "api": "olimpush"
}
```

**Campos de respuesta exitosa:**

- `data`: Clave de acceso de 49 dígitos. Este valor debe almacenarse y usarse al crear el documento electrónico.

**Estructura de la clave de acceso (49 dígitos):**

```
07112025  01  1723774640001  1  003  002  000000640  64453698  1  2
^^^^^^^^  ^^  ^^^^^^^^^^^^^  ^  ^^^  ^^^  ^^^^^^^^^  ^^^^^^^^  ^  ^
   |       |        |        |   |    |       |          |      |  |
 Fecha   Tipo    RUC       Amb Est  Pto   Secuencial  Código  Tipo Dígito
               empresa                                 numérico emisión verif
```

**Información importante:**

- La clave de acceso es única por documento
- Debe generarse antes de crear el XML del comprobante
- El formato de fecha debe ser estrictamente `dd/mm/yyyy`
- Los códigos de establecimiento y punto deben ser 3 dígitos con ceros a la izquierda
- El número secuencial debe ser 9 dígitos con ceros a la izquierda
- La clave generada incluye un dígito verificador al final

**Códigos de tipo de documento más comunes:**

| Código | Tipo de Documento        |
| ------ | ------------------------ |
| 01     | Factura                  |
| 03     | Liquidación de compra    |
| 04     | Nota de crédito          |
| 05     | Nota de débito           |
| 06     | Guía de remisión         |
| 07     | Comprobante de retención |

**Recomendaciones:**

- Generar la clave de acceso justo antes de crear el documento
- Almacenar la clave junto con el documento en la base de datos
- Usar UUID o GUID para `transactionIde`
- Validar formato de fecha antes de enviar
- Incrementar el secuencial por cada documento del mismo tipo

---

## Facturación Electrónica

### 9. Crear Factura Electrónica

Crea una factura electrónica que será enviada al SRI para autorización. Este endpoint genera el XML del comprobante, lo firma electrónicamente, lo envía al SRI para recepción y autorización, y retorna el documento autorizado en formato XML y PDF (RIDE).

**⚠️ Requisitos previos:**

1. Tener registrado el contribuyente en Olimpush
2. Haber cargado el certificado de firma electrónica del contribuyente
3. (Opcional) Haber registrado el logo para personalizar el RIDE

**📋 Proceso completo:**

1. El sistema recibe los datos de la factura
2. Genera o valida la clave de acceso
3. Crea el XML del comprobante
4. Firma electrónicamente el documento
5. Envía al SRI para recepción
6. Envía al SRI para autorización
7. Genera el PDF (RIDE) con el logo registrado
8. (Opcional) Envía el documento por email al cliente

**Endpoint:**

```
POST /api/olimpush/facturas/crear/
```

**Autenticación:** JWT Bearer Token requerido

**Content-Type:** `application/json`

**Estructura de la solicitud:**

La solicitud tiene una estructura JSON compleja con varias secciones:

1. **Datos de la transacción**: `origin`, `usrRequest`, `ipRequest`, `transactionIde`
2. **Información tributaria del emisor**: `payload.taxAuthorityInfo`
3. **Información de la factura**: `payload.invoiceInfo`
4. **Productos/Servicios**: `payload.details[]`
5. **Formas de pago**: `payload.paymentMethods[]`
6. **Firma electrónica** (opcional): `payload.signatureInfo`
7. **Atributos adicionales** (opcional): `payload.additionalAttributes[]`

**Parámetros principales del body:**

```typescript
{
  origin: string;              // Origen consumo API
  usrRequest: string;          // Usuario consumo API
  ipRequest: string;           // IP del cliente
  transactionIde: string;      // ID único de la transacción (UUID)
  payload: {
    taxAuthorityInfo: {
      socialReason: string;           // Razón social del emisor *
      commercialName: string;         // Nombre comercial *
      keyAccess?: string;             // Clave de acceso (49 dígitos) - OPCIONAL
      ruc?: string;                   // RUC emisor (13 dígitos) - requerido si no hay keyAccess
      establishmentCode?: string;     // Código establecimiento (001) - requerido si no hay keyAccess
      pointCode?: string;             // Código punto emisión (002) - requerido si no hay keyAccess
      sequentialDocument?: string;    // Secuencial (000000123) - requerido si no hay keyAccess
      mainAddress: string;            // Dirección matriz *
      retentionAgent?: string;        // Código agente retención
      rimpeContributor?: string;      // Leyenda Régimen RIMPE
    };
    invoiceInfo: {
      emissionDate?: string;          // Fecha emisión (dd/mm/yyyy) - requerido si no hay keyAccess
      establishmentAddress: string;   // Dirección del establecimiento *
      hasRequiredAccounting?: string; // Obligado contabilidad (SI/NO)
      specialTaxpayer?: string;       // Número contribuyente especial
      remissionGuideNumber?: string;  // Número guía remisión
      buyerIdType: string;            // Tipo ID cliente (05=Cédula, 04=RUC, etc.) *
      buyerIdNumber: string;          // Número ID cliente *
      buyerSocialReason: string;      // Razón social cliente *
      buyerAddress: string;           // Dirección cliente *
      buyerEmail?: string;            // Email cliente (envía automáticamente)
    };
    details: [
      {
        description: string;          // Descripción producto *
        mainCode: string;             // Código principal *
        auxiliaryCode?: string;       // Código auxiliar
        unitValue: number;            // Precio unitario *
        amount: number;               // Cantidad *
        discount: number;             // Descuento por unidad *
        tariffCodeIva: string;        // Código tarifa IVA (0, 5, 8) *
        additionalAttributes?: [      // Atributos adicionales del producto
          {
            attribute: string;        // Nombre atributo *
            value: string;            // Valor atributo *
          }
        ]
      }
    ];
    paymentMethods: [
      {
        type: string;                 // Código forma pago (01, 20, etc.) *
        total: number;                // Monto *
        timeUnit: string;             // Unidad tiempo (días, meses) *
        paymentTerm: string;          // Plazo (0, 30, etc.) *
      }
    ];
    signatureInfo?: {                 // OPCIONAL - si no se envía, usa certificado registrado
      certificateBase64: string;      // Certificado en base64
      passCertificate: string;        // Contraseña certificado
    };
    additionalAttributes?: [          // OPCIONAL - atributos adicionales de la factura
      {
        attribute: string;
        value: string;
      }
    ]
  }
}
```

**Nota sobre `keyAccess` vs campos individuales:**

- Si envías `keyAccess`, el sistema lo usa directamente y extrae automáticamente: `ruc`, `establishmentCode`, `pointCode`, `sequentialDocument`, `emissionDate`
- Si NO envías `keyAccess`, debes proporcionar todos esos campos y el sistema generará la clave automáticamente

**Ejemplo de petición desde Next.js:**

```typescript
const crearFactura = async (facturaData: any) => {
  const payload = {
    origin: "NextJS",
    usrRequest: "WebUser",
    ipRequest: "192.168.1.100",
    transactionIde: crypto.randomUUID(),
    payload: {
      taxAuthorityInfo: {
        socialReason: "Mi Empresa S.A.",
        commercialName: "Mi Empresa",
        ruc: "1705818431001",
        establishmentCode: "001",
        pointCode: "002",
        sequentialDocument: "000000001",
        mainAddress: "Quito - Ecuador",
      },
      invoiceInfo: {
        emissionDate: "02/02/2026",
        establishmentAddress: "Quito Norte",
        hasRequiredAccounting: "SI",
        buyerIdType: "05",
        buyerIdNumber: "1234567890",
        buyerSocialReason: "Juan Pérez",
        buyerAddress: "Quito",
        buyerEmail: "cliente@ejemplo.com",
      },
      details: [
        {
          description: "Consulta Médica General",
          mainCode: "CONS001",
          unitValue: 50.0,
          amount: 1,
          discount: 0,
          tariffCodeIva: "5",
        },
      ],
      paymentMethods: [
        {
          type: "01",
          total: 56.0,
          timeUnit: "dias",
          paymentTerm: "0",
        },
      ],
    },
  };

  const response = await fetch(
    `http://localhost:8000/api/olimpush/facturas/crear/`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    },
  );

  const data = await response.json();
  return data;
};

// Uso
try {
  const resultado = await crearFactura(datosFactura);

  if (resultado.data.authorization.status === "AUTORIZADO") {
    console.log("Factura autorizada!");
    console.log(
      "Número autorización:",
      resultado.data.authorization.authorizationNumber,
    );
    console.log("Clave acceso:", resultado.data.authorization.keyAccess);

    // Descargar PDF
    const pdfBase64 = resultado.data.authorization.pdfBase64;
    const pdfBlob = base64ToBlob(pdfBase64, "application/pdf");
    const url = URL.createObjectURL(pdfBlob);
    window.open(url);
  }
} catch (error) {
  console.error("Error al crear factura:", error);
}
```

**Respuestas posibles:**

#### ✅ 200 - Factura autorizada correctamente

```json
{
  "code": 200,
  "status": "OK",
  "message": "Proceso ejecutado correctamente",
  "data": {
    "reception": {
      "status": "RECIBIDA",
      "failedCommunicationWithSri": false,
      "keyAccess": "0711202501172377464000110010020000006384717444512",
      "historyInvoice": [
        {
          "description": "El documento fue recibido correctamente por el SRI",
          "status": "RECIBIDA",
          "type": "OK",
          "date": "2025-11-07 02:39:51",
          "identificador": null,
          "origin": "facturacion-electronica-api"
        }
      ]
    },
    "authorization": {
      "status": "AUTORIZADO",
      "failedCommunicationWithSri": false,
      "keyAccess": "0711202501172377464000110010020000006384717444512",
      "authorizationNumber": "0711202501172377464000110010020000006384717444512",
      "environment": "PRUEBAS",
      "authorizationDate": "2025-11-07T07:39:52.000+00:00",
      "voucher": "<?xml version=\"1.0\" encoding=\"UTF-8\"...",
      "pdfBase64": "JVBERi0xLjcKJeLjz9MKNSAwIG9iago8PC...",
      "historyInvoice": [
        {
          "description": "El comprobante fue autorizado correctamente",
          "status": "AUTORIZADO",
          "type": "OK",
          "date": "2025-11-07 02:39:53",
          "identificador": null,
          "origin": "facturacion-electronica-api"
        }
      ]
    },
    "message": "Documento autorizado correctamente"
  },
  "api": "olimpush"
}
```

#### ⚠️ 200 - Factura recibida pero no autorizada

```json
{
  "code": 200,
  "status": "OK",
  "message": "Proceso ejecutado correctamente",
  "data": {
    "reception": {
      "status": "RECIBIDA",
      "keyAccess": "...",
      "historyInvoice": [...]
    },
    "authorization": {
      "status": "NO AUTORIZADO",
      "failedCommunicationWithSri": false,
      "keyAccess": "...",
      "historyInvoice": [
        {
          "description": "Error en datos de la factura",
          "status": "NO AUTORIZADO",
          "type": "ERROR",
          "date": "2025-11-07 02:40:00",
          "identificador": "35",
          "origin": "SRI"
        }
      ]
    },
    "message": "Documento no autorizado"
  },
  "api": "olimpush"
}
```

#### ❌ 400 - Campos incorrectos

```json
{
  "code": 400,
  "status": "ERROR",
  "message": "El campo taxAuthorityInfo.ruc es requerido",
  "data": null,
  "api": "olimpush"
}
```

#### ❌ 409 - Factura duplicada

```json
{
  "code": 409,
  "status": "ERROR",
  "message": "La factura con esta clave de acceso ya existe",
  "data": null,
  "api": "olimpush"
}
```

**Campos importantes de la respuesta:**

- `reception.status`: Estado de recepción en el SRI (`RECIBIDA`, `DEVUELTA`)
- `authorization.status`: Estado de autorización (`AUTORIZADO`, `NO AUTORIZADO`)
- `authorization.authorizationNumber`: Número de autorización del SRI
- `authorization.keyAccess`: Clave de acceso del documento (49 dígitos)
- `authorization.voucher`: XML del comprobante firmado
- `authorization.pdfBase64`: PDF (RIDE) en base64
- `authorization.authorizationDate`: Fecha y hora de autorización

**Códigos de tipo de identificación del comprador:**

| Código | Tipo                        |
| ------ | --------------------------- |
| 04     | RUC                         |
| 05     | Cédula                      |
| 06     | Pasaporte                   |
| 07     | Consumidor Final            |
| 08     | Identificación del exterior |

**Códigos de tarifa IVA:**

| Código | Descripción           |
| ------ | --------------------- |
| 0      | 0% (No objeto de IVA) |
| 2      | 12% IVA               |
| 3      | 14% IVA               |
| 4      | 15% IVA               |
| 5      | 5% IVA                |
| 6      | Exento de IVA         |
| 7      | IVA diferenciado      |
| 8      | 8% IVA                |

**Códigos de forma de pago:**

| Código | Forma de Pago                                |
| ------ | -------------------------------------------- |
| 01     | Sin utilización del sistema financiero       |
| 15     | Compensación de deudas                       |
| 16     | Tarjeta de débito                            |
| 17     | Dinero electrónico                           |
| 18     | Tarjeta prepago                              |
| 19     | Tarjeta de crédito                           |
| 20     | Otros con utilización del sistema financiero |
| 21     | Endoso de títulos                            |

**Flujo recomendado:**

1. Validar datos del cliente y productos en el frontend
2. Generar clave de acceso (endpoint anterior) si no la tienes
3. Construir el payload completo de la factura
4. Enviar a este endpoint
5. Verificar `authorization.status === "AUTORIZADO"`
6. Guardar en base de datos:
   - `keyAccess`
   - `authorizationNumber`
   - `authorizationDate`
7. Mostrar/descargar el PDF al usuario
8. Almacenar el XML (`voucher`) para futuras consultas

**Información importante:**

- El proceso es sincrónico: espera la respuesta del SRI
- Tiempo de respuesta típico: 3-10 segundos
- Si el email está presente, se envía automáticamente al cliente
- El PDF incluye el logo si fue registrado previamente
- El XML firmado está en el campo `voucher`
- La clave de acceso debe ser única (no reutilizar)
- El secuencial debe incrementarse por cada factura

**Recomendaciones:**

- Implementar un sistema de retry en caso de timeout
- Guardar el estado de la factura antes de enviar al SRI
- Validar datos del cliente antes de enviar
- Usar transacciones de base de datos
- Implementar logs de auditoría
- Mantener un contador de secuenciales por establecimiento y punto
- Validar que los totales cuadren antes de enviar

---

## Suscripción

### 10. Consultar Suscripción Actual

Obtiene información detallada sobre la suscripción actual del usuario en la API de Olimpush. Este endpoint es útil para conocer el estado de la suscripción, la cantidad de documentos disponibles, los tipos de documentos autorizados y la fecha de vencimiento.

**📊 Casos de uso:**

- Verificar cuántos documentos quedan disponibles
- Validar si la suscripción está activa antes de emitir documentos
- Conocer qué tipos de documentos están habilitados
- Mostrar información de la suscripción en el dashboard
- Alertar cuando se está cerca del límite de documentos

**Endpoint:**

```
GET /api/olimpush/suscripcion/actual/
```

**Autenticación:** JWT Bearer Token requerido

**Sin parámetros**

**Ejemplo de petición desde Next.js:**

```typescript
const consultarSuscripcion = async () => {
  const response = await fetch(
    `http://localhost:8000/api/olimpush/suscripcion/actual/`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    },
  );

  const data = await response.json();
  return data;
};

// Uso
const suscripcion = await consultarSuscripcion();

if (!suscripcion.data.active) {
  alert("Suscripción inactiva");
}

const documentosRestantes =
  suscripcion.data.amountDoc - suscripcion.data.amountDocUsed;
console.log(`Documentos disponibles: ${documentosRestantes}`);

// Verificar si puede crear facturas
const puedeCrearFacturas = suscripcion.data.docs.some(
  (doc) => doc.code === "01",
);
```

**Respuestas posibles:**

#### ✅ 200 - Información de la suscripción

```json
{
  "code": 200,
  "status": "OK",
  "message": "Proceso ejecutado correctamente",
  "data": {
    "environment": "PRODUCCIÓN",
    "amountDoc": 500,
    "amountDocUsed": 0,
    "beginDate": "2025-10-01",
    "endDate": "2025-10-15",
    "active": true,
    "observation": "token creado con exito",
    "docs": [
      {
        "description": "FACTURA",
        "code": "01"
      },
      {
        "description": "GUÍA DE REMISIÓN",
        "code": "06"
      }
    ],
    "pathWsAllowed": [
      "individual",
      "util",
      "download",
      "ruc",
      "vehicles",
      "subscriptions"
    ],
    "createAt": "2025-10-01 16:41:49"
  },
  "api": "olimpush"
}
```

**Campos de la respuesta:**

- `environment`: Ambiente de la suscripción (`PRUEBAS` o `PRODUCCIÓN`)
- `amountDoc`: Cantidad total de documentos permitidos en el plan
- `amountDocUsed`: Cantidad de documentos ya utilizados
- `beginDate`: Fecha de inicio de vigencia de la suscripción
- `endDate`: Fecha de fin de vigencia de la suscripción
- `active`: Indica si la suscripción está activa (`true`/`false`)
- `observation`: Comentario adicional sobre la suscripción
- `docs`: Lista de tipos de documentos autorizados
  - `description`: Nombre del tipo de documento
  - `code`: Código del tipo de documento
- `pathWsAllowed`: Lista de servicios habilitados en la API
- `createAt`: Fecha y hora de creación de la suscripción

**Códigos de tipos de documentos:**

| Código | Tipo de Documento        |
| ------ | ------------------------ |
| 01     | Factura                  |
| 03     | Liquidación de compra    |
| 04     | Nota de crédito          |
| 05     | Nota de débito           |
| 06     | Guía de remisión         |
| 07     | Comprobante de retención |

**Servicios API (`pathWsAllowed`):**

- `individual`: Creación de documentos individuales
- `util`: Utilidades (generar clave de acceso, etc.)
- `download`: Descarga de documentos
- `ruc`: Consultas de RUC al SRI
- `vehicles`: Consultas de vehículos
- `subscriptions`: Consultas de suscripción

**Uso recomendado:**

```typescript
// Verificar antes de crear documento
const verificarSuscripcion = async () => {
  const suscripcion = await consultarSuscripcion();

  if (!suscripcion.data.active) {
    throw new Error('Suscripción inactiva');
  }

  const disponibles = suscripcion.data.amountDoc - suscripcion.data.amountDocUsed;

  if (disponibles <= 0) {
    throw new Error('No hay documentos disponibles');
  }

  if (disponibles < 10) {
    console.warn(`Quedan solo ${disponibles} documentos`);
  }

  // Verificar fecha de vencimiento
  const fechaVencimiento = new Date(suscripcion.data.endDate);
  const hoy = new Date();
  const diasRestantes = Math.ceil((fechaVencimiento - hoy) / (1000 * 60 * 60 * 24));

  if (diasRestantes < 7) {
    console.warn(`La suscripción vence en ${diasRestantes} días`);
  }

  return suscripcion.data;
};

// Dashboard de suscripción
const DashboardSuscripcion = () => {
  const [suscripcion, setSuscripcion] = useState(null);

  useEffect(() => {
    consultarSuscripcion().then(data => setSuscripcion(data.data));
  }, []);

  if (!suscripcion) return <div>Cargando...</div>;

  const porcentajeUsado = (suscripcion.amountDocUsed / suscripcion.amountDoc) * 100;

  return (
    <div>
      <h2>Suscripción {suscripcion.environment}</h2>
      <p>Estado: {suscripcion.active ? '✅ Activa' : '❌ Inactiva'}</p>
      <p>Documentos: {suscripcion.amountDocUsed} / {suscripcion.amountDoc} ({porcentajeUsado.toFixed(1)}%)</p>
      <p>Vigencia: {suscripcion.beginDate} - {suscripcion.endDate}</p>
      <h3>Documentos autorizados:</h3>
      <ul>
        {suscripcion.docs.map(doc => (
          <li key={doc.code}>{doc.description} ({doc.code})</li>
        ))}
      </ul>
    </div>
  );
};
```

**Recomendaciones:**

- Consultar al inicio de la sesión del usuario
- Cachear la información por unos minutos
- Mostrar alertas cuando quedan pocos documentos
- Alertar cuando la suscripción está próxima a vencer
- Deshabilitar funciones de facturación si `active === false`
- Verificar antes de cada creación de documento
- Implementar un dashboard de uso

---

## Consultas de Facturas

### 11. Ver y Filtrar Facturas

Consulta las facturas electrónicas emitidas con opciones de filtrado y paginación. Este endpoint es útil para listar facturas, buscar por cliente, filtrar por estado de autorización y navegar entre páginas de resultados.

**📊 Casos de uso:**

- Listar todas las facturas emitidas
- Buscar facturas de un cliente específico
- Filtrar facturas autorizadas o no autorizadas
- Implementar un historial de facturación con paginación
- Consultar facturas por RUC específico

**Endpoint:**

```
GET /api/olimpush/facturas/
```

**Autenticación:** JWT Bearer Token requerido

**Parámetros de query (todos opcionales):**

- `ruc` (string): Número de RUC del contribuyente (13 dígitos)
- `page` (integer): Número de página a consultar (por defecto: 1)
- `customer_ide` (string): Número de identificación del cliente
- `authorization_status` (string): Estado de autorización. Valores: `AUTORIZADO` o `NO AUTORIZADO`

**Ejemplo de petición desde Next.js:**

```typescript
const consultarFacturas = async (
  ruc?: string,
  page: number = 1,
  customerIde?: string,
  authorizationStatus?: "AUTORIZADO" | "NO AUTORIZADO",
) => {
  // Construir query params
  const params = new URLSearchParams();
  if (ruc) params.append("ruc", ruc);
  params.append("page", page.toString());
  if (customerIde) params.append("customer_ide", customerIde);
  if (authorizationStatus)
    params.append("authorization_status", authorizationStatus);

  const response = await fetch(
    `http://localhost:8000/api/olimpush/facturas/?${params.toString()}`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    },
  );

  const data = await response.json();
  return data;
};

// Uso - Listar todas las facturas (página 1)
const facturas = await consultarFacturas();

// Uso - Filtrar facturas autorizadas
const autorizadas = await consultarFacturas(
  undefined,
  1,
  undefined,
  "AUTORIZADO",
);

// Uso - Buscar facturas de un cliente específico
const facturasCliente = await consultarFacturas(undefined, 1, "1723774640");

// Uso - Navegar a página 2
const pagina2 = await consultarFacturas(undefined, 2);
```

**Respuestas posibles:**

#### ✅ 200 - Facturas encontradas

```json
{
  "code": 200,
  "status": "OK",
  "message": "Información obtenida correctamente.",
  "data": {
    "listData": [
      {
        "ruc": "2323774440001",
        "authorizationStatus": "AUTORIZADO",
        "authorizationDate": "2025-12-05 10:51:55.000000",
        "document": {
          "taxAuthorityInfo": {
            "environmentType": "1",
            "emissionType": "1",
            "socialReason": "OlimPush",
            "commercialName": "Servicios Profesionales de Software",
            "ruc": "2323774440001",
            "keyAccess": "0210202501172377464000110010020000016071959457519",
            "documentType": "01",
            "pointCode": "002",
            "establishmentCode": "001",
            "sequentialDocument": "000001607",
            "mainAddress": "Quevedo y Santa Ana",
            "retentionAgent": null,
            "rimpeContributor": null
          },
          "invoiceInfo": {
            "emissionDate": "05/12/2025",
            "establishmentAddress": "Quevedo",
            "hasRequiredAccounting": "NO",
            "specialTaxpayer": null,
            "remissionGuideNumber": "001-001-000000002",
            "buyerIdType": "05",
            "buyerIdNumber": "1723774640",
            "buyerSocialReason": "Ronny Chamba",
            "buyerAddress": "Quevedo y OlimPush Address",
            "buyerEmail": "micorreo@gmail.com",
            "subtotal": 179,
            "totalIva": 17.85,
            "discountTotal": 80,
            "tipAmount": 0,
            "totalAmount": 196.85
          },
          "details": [
            {
              "description": "Papel",
              "amount": 12,
              "additionalAttributes": [
                {
                  "attribute": "color",
                  "value": "rojo"
                }
              ],
              "mainCode": "001",
              "auxiliaryCode": null,
              "unitValue": 5,
              "discount": 0,
              "tariffCodeIva": "0",
              "valueIva": 0,
              "subtotal": 60,
              "total": 60
            }
          ],
          "paymentMethods": [
            {
              "type": "01",
              "total": 196.85,
              "paymentTerm": "0",
              "timeUnit": "dias"
            }
          ],
          "additionalAttributes": [
            {
              "attribute": "correo",
              "value": "soporte@olimpush.com"
            }
          ]
        },
        "histories": [
          {
            "type": "OK",
            "description": "El documento fue recibido correctamente por el SRI",
            "createAt": "2025-12-05 10:51:59.000000"
          },
          {
            "type": "OK",
            "description": "El comprobante fue autorizado correctamente.",
            "createAt": "2025-12-05 10:51:59.000000"
          },
          {
            "type": "OK",
            "description": "Correo enviado con éxito al cliente micorreo@gmail.com.",
            "createAt": "2025-12-05 10:52:03.000000"
          }
        ]
      }
    ],
    "page": {
      "totalPages": 4,
      "numElementsByPage": 10,
      "currentPage": 1,
      "totalElements": 35,
      "pagesItem": [
        {
          "number": 1,
          "current": true
        },
        {
          "number": 2,
          "current": false
        },
        {
          "number": 3,
          "current": false
        },
        {
          "number": 4,
          "current": false
        }
      ],
      "first": true,
      "last": false,
      "hasPrevious": false,
      "hasNext": true
    }
  }
}
```

#### ❌ 400 - Estado de autorización inválido

```json
{
  "success": false,
  "status_code": 400,
  "message": "authorization_status debe ser 'AUTORIZADO' o 'NO AUTORIZADO'",
  "data": null,
  "api": "djangoclinica"
}
```

**Campos de la respuesta:**

**Información de paginación (`data.page`):**

- `totalElements`: Número total de facturas encontradas
- `totalPages`: Cantidad total de páginas disponibles
- `numElementsByPage`: Número de resultados por página (10)
- `currentPage`: Número de la página actual
- `first`: Indica si es la primera página
- `last`: Indica si es la última página
- `hasPrevious`: Indica si existe página anterior
- `hasNext`: Indica si existe página siguiente
- `pagesItem`: Array con información de cada página disponible

**Información de cada factura (`data.listData[]`):**

- `ruc`: RUC del emisor
- `authorizationStatus`: Estado de autorización (`AUTORIZADO` o `NO AUTORIZADO`)
- `authorizationDate`: Fecha y hora de autorización
- `document`: Objeto con toda la información del documento
  - `taxAuthorityInfo`: Información tributaria del emisor
  - `invoiceInfo`: Información de la factura y comprador
  - `details`: Array de productos/servicios
  - `paymentMethods`: Array de formas de pago
  - `additionalAttributes`: Atributos adicionales
- `histories`: Historial de eventos del documento (recepción, autorización, envío de email)

**Recomendaciones:**

- Implementar debounce en los filtros para evitar peticiones excesivas
- Cachear resultados por página para mejorar rendimiento
- Mostrar un loader mientras se cargan las facturas
- Permitir descargar el PDF de cada factura desde la tabla
- Implementar ordenamiento por fecha, monto o estado
- Agregar un botón para exportar resultados a Excel/PDF
- Mostrar el historial de eventos al hacer clic en una factura

---

## Arquitectura

- `estado`: Estado actual (ABIERTO, CERRADO)
- `numeroEstablecimiento`: Código del establecimiento (001, 002, etc.)
- `matriz`: Indica si es matriz ("SI"/"NO")

---

## Arquitectura

```
┌─────────────┐
│  Next.js    │
│  Frontend   │
└──────┬──────┘
       │
       │ GET /api/olimpush/ruc/{ruc}/validation/
       │ Authorization: Bearer <token>
       │
       ▼
┌──────────────────────────┐
│   Django Backend         │
│   (Proxy)                │
│                          │
│   core/views.py          │
│   core/services.py       │
└──────┬───────────────────┘
       │
       │ GET /ruc/{ruc}/validation
       │ olimpush-token: <token>
       │
       ▼
┌──────────────────────────┐
│   API Olimpush           │
│   (SRI)                  │
└──────────────────────────┘
```

## Ventajas de usar Django como proxy

1. ✅ **Sin problemas de CORS**: Django hace las peticiones server-side
2. ✅ **Seguridad**: El token de Olimpush nunca se expone al cliente
3. ✅ **Control centralizado**: Logs, rate limiting y validaciones en un solo lugar
4. ✅ **Autenticación unificada**: Usas el mismo token JWT de tu app
5. ✅ **Respuestas consistentes**: Django pasa la respuesta tal cual de Olimpush

## Próximos endpoints a implementar

- [x] Validar RUC
- [x] Consultar establecimientos por RUC
- [x] Consultar información completa del RUC (SRI)
- [x] Consultar contribuyente en Olimpush
- [x] Registrar logo del contribuyente
- [x] Registrar firma electrónica del contribuyente
- [x] Eliminar firma electrónica del contribuyente
- [x] Generar clave de acceso
- [x] Crear factura electrónica
- [x] Consultar suscripción actual
- [ ] Consultar documentos emitidos
- [ ] Anular factura

---

## Testing en desarrollo

Puedes probar el endpoint con curl:

```bash
# Obtener token JWT
curl -X POST http://localhost:8000/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

# Validar RUC
curl -X GET http://localhost:8000/api/olimpush/ruc/1234567890001/validation/ \
  -H "Authorization: Bearer <tu_token_jwt>"

# Consultar establecimientos
curl -X GET http://localhost:8000/api/olimpush/ruc/1234567890001/establishments/ \
  -H "Authorization: Bearer <tu_token_jwt>"

# Consultar información completa
curl -X GET http://localhost:8000/api/olimpush/ruc/2390012562001/ \
  -H "Authorization: Bearer <tu_token_jwt>"

# Consultar contribuyente en Olimpush
curl -X GET http://localhost:8000/api/olimpush/contribuyentes/2390012562001/ \
  -H "Authorization: Bearer <tu_token_jwt>"

# Registrar logo del contribuyente
curl -X POST http://localhost:8000/api/olimpush/contribuyentes/2390012562001/logo/ \
  -H "Authorization: Bearer <tu_token_jwt>" \
  -F "logo=@/ruta/al/logo.png"

# Registrar firma electrónica del contribuyente
curl -X POST http://localhost:8000/api/olimpush/contribuyentes/2390012562001/certificado/ \
  -H "Authorization: Bearer <tu_token_jwt>" \
  -F "firma=@/ruta/al/certificado.p12" \
  -F "password=tu_password_certificado"

# Eliminar firma electrónica del contribuyente
curl -X DELETE http://localhost:8000/api/olimpush/contribuyentes/2390012562001/certificado/delete/ \
  -H "Authorization: Bearer <tu_token_jwt>" \
  -H "Content-Type: application/json"

# Generar clave de acceso
curl -X POST http://localhost:8000/api/olimpush/util/clave-acceso/ \
  -H "Authorization: Bearer <tu_token_jwt>" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Postman",
    "usrRequest": "TestUser",
    "ipRequest": "192.168.1.100",
    "transactionIde": "550e8400-e29b-41d4-a716-446655440000",
    "payload": {
      "emissionDate": "07/11/2025",
      "codeDocumentType": "01",
      "ruc": "1705818431001",
      "establishmentCode": "001",
      "pointCode": "002",
      "sequentialNumber": "000000640"
    }
  }'

# Crear factura electrónica
curl -X POST http://localhost:8000/api/olimpush/facturas/crear/ \
  -H "Authorization: Bearer <tu_token_jwt>" \
  -H "Content-Type: application/json" \
  -d @factura.json

# Ver ejemplo completo de factura.json en la documentación

# Consultar suscripción actual
curl -X GET http://localhost:8000/api/olimpush/suscripcion/actual/ \
  -H "Authorization: Bearer <tu_token_jwt>" \
  -H "Content-Type: application/json"
```

O con Postman:

1. Crear petición GET a los endpoints disponibles
2. En Headers agregar: `Authorization: Bearer <tu_token>`
3. Send

---

## Manejo de errores

El servicio retorna los errores exactos de la API de Olimpush. Los códigos HTTP más comunes:

| Código | Descripción                                 |
| ------ | ------------------------------------------- |
| 200    | Operación exitosa                           |
| 400    | Datos inválidos (formato de RUC incorrecto) |
| 401    | Token inválido o expirado                   |
| 404    | Recurso no encontrado                       |
| 502    | Error al conectar con API externa           |
| 503    | Servicio no disponible                      |
| 504    | Timeout en la petición                      |
