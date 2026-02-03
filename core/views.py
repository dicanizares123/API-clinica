"""
Vistas generales del sistema.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .services import OlimpushService, django_response
from .models import BusinessInfo, Product
from .serializers import BusinessInfoSerializer, ProductSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API Root - Información general de la API de Clínica.
    
    Esta API proporciona endpoints para gestionar:
    - Usuarios y autenticación
    - Pacientes
    - Doctores
    - Citas médicas
    - Notificaciones
    
    ## Autenticación
    La mayoría de endpoints requieren autenticación JWT.
    
    Para obtener un token:
    ```
    POST /auth/jwt/create/
    {
        "email": "usuario@ejemplo.com",
        "password": "tu_password"
    }
    ```
    
    Luego incluye el token en el header:
    ```
    Authorization: Bearer <tu_token>
    ```
    
    ## Documentación
    - Documentación interactiva: /docs/
    - Admin panel: /admin/
    
    ## Endpoints principales
    - /auth/ - Autenticación y gestión de usuarios
    - /api/patients/ - Gestión de pacientes
    - /api/doctors/ - Gestión de doctores
    - /api/appointments/ - Gestión de citas
    - /api/notifications/ - Notificaciones del sistema
    """
    return Response({
        'message': 'API de Gestión de Clínica',
        'version': '1.0.0',
        'documentation': request.build_absolute_uri('/docs/'),
        'endpoints': {
            'authentication': {
                'login': '/auth/jwt/create/',
                'refresh': '/auth/jwt/refresh/',
                'logout': '/auth/logout/',
                'register': '/auth/users/',
            },
            'patients': '/api/patients/',
            'doctors': '/api/doctors/',
            'appointments': '/api/appointments/',
            'notifications': '/api/notifications/',
        },
        'documentation_endpoints': {
            'api_docs': '/docs/',
            'admin': '/admin/',
        }
    }, status=status.HTTP_200_OK)


# ============================================================================
# PROXY A API DE OLIMPUSH - FACTURACIÓN ELECTRÓNICA
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validar_ruc(request, ruc):
    """
    Valida si un RUC existe en el SRI consultando la API de Olimpush.
    Retorna la respuesta exacta de la API externa.
    
    GET /api/olimpush/ruc/{ruc}/validation/
    
    Respuestas posibles:
        200 - RUC existe
        400 - RUC incorrecto (formato inválido)
        404 - RUC no existe
    
    Ejemplo de respuesta exitosa:
    {
        "code": 200,
        "status": "OK",
        "message": "Proceso ejecutado correctamente",
        "data": "El ruc existe"
    }
    """
    response_data, status_code = OlimpushService.validar_ruc(ruc)
    return Response(response_data, status=status_code)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def consultar_establecimientos(request, ruc):
    """
    Consulta todos los establecimientos asociados a un RUC.
    Retorna la respuesta exacta de la API externa de Olimpush.
    
    GET /api/olimpush/ruc/{ruc}/establishments/
    
    Respuestas posibles:
        200 - Lista de establecimientos
        400 - RUC incorrecto (formato inválido)
    
    Ejemplo de respuesta exitosa:
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
                "direccionCompleta": "PICHINCHA / QUITO / SANTO DOMINGO...",
                "estado": "ABIERTO",
                "numeroEstablecimiento": "002",
                "matriz": "NO"
            }
        ]
    }
    """
    response_data, status_code = OlimpushService.consultar_establecimientos(ruc)
    return Response(response_data, status=status_code)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def consultar_ruc_info(request, ruc):
    """
    Consulta información completa de un RUC (datos del contribuyente).
    Retorna la respuesta exacta de la API externa de Olimpush.
    
    GET /api/olimpush/ruc/{ruc}/
    
    Respuestas posibles:
        200 - Información completa del contribuyente
        400 - RUC incorrecto (formato inválido)
        404 - RUC no encontrado
    
    Ejemplo de respuesta exitosa:
    {
        "code": 200,
        "status": "OK",
        "message": "Proceso ejecutado correctamente",
        "data": [
            {
                "numeroRuc": "2390012562001",
                "razonSocial": "TELEALFACOM S.A.",
                "estadoContribuyenteRuc": "ACTIVO",
                "actividadEconomicaPrincipal": "...",
                "tipoContribuyente": "SOCIEDAD",
                "regimen": "GENERAL",
                "obligadoLlevarContabilidad": "SI",
                "agenteRetencion": "SI",
                "contribuyenteEspecial": "SI",
                "informacionFechasContribuyente": {...},
                "representantesLegales": [...]
            }
        ],
        "api": "olimpush"
    }
    """
    response_data, status_code = OlimpushService.consultar_ruc_info(ruc)
    return Response(response_data, status=status_code)


# ============================================================================
# ENDPOINT PARA BUSINESS INFO
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_business_ruc(request):
    """
    Obtiene el RUC del negocio configurado.
    
    GET /api/business/ruc/
    
    Respuesta exitosa:
    {
        "success": true,
        "status_code": 200,
        "message": "RUC del negocio obtenido exitosamente",
        "data": {
            "ruc": "1234567890001"
        },
        "api": "djangoclinica"
    }
    
    Respuesta sin RUC configurado:
    {
        "success": false,
        "status_code": 404,
        "message": "No hay RUC configurado en el sistema",
        "data": null,
        "api": "djangoclinica"
    }
    """
    business = BusinessInfo.get_instance()
    
    if not business:
        return django_response(
            data=None,
            message='No hay RUC configurado en el sistema',
            status_code=404,
            success=False
        )
    
    return django_response(
        data={'ruc': business.ruc},
        message='RUC del negocio obtenido exitosamente',
        status_code=200
    )


# ============================================================================
# ENDPOINTS PARA PRODUCTOS/SERVICIOS
# ============================================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def productos_list_create(request):
    """
    Lista todos los productos o crea uno nuevo.
    
    GET /api/core/productos/
    Retorna lista de todos los productos con: descripción, código y precio unitario
    
    POST /api/core/productos/
    Crea un nuevo producto
    
    Body para POST:
    {
        "description": "CITA PSICOLOGICA",
        "code": "COD001",
        "unit_price": 26.09
    }
    
    Respuesta:
    {
        "id": 1,
        "description": "CITA PSICOLOGICA",
        "code": "COD001",
        "unit_price": "26.09"
    }
    """
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def producto_detail(request, pk):
    """
    Obtiene, actualiza o elimina un producto específico.
    
    GET /api/core/productos/{id}/
    PUT /api/core/productos/{id}/
    DELETE /api/core/productos/{id}/
    """
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({
            'error': 'Producto no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def consultar_contribuyente(request, ruc):
    """
    Consulta información de un contribuyente en el sistema de Olimpush.
    Retorna la respuesta exacta de la API externa.
    
    GET /api/olimpush/contribuyentes/{ruc}/
    
    Respuestas posibles:
        200 - Información del contribuyente
        404 - Contribuyente no existe
    
    Ejemplo de respuesta exitosa:
    {
        "code": 200,
        "status": "OK",
        "message": "Proceso ejecutado correctamente",
        "data": {
            "socialReason": "OlimPush Facturacion",
            "ruc": "2390012562001",
            "signatureDoc": "1710774640001-1766208529416.p12",
            "createAt": "2025-11-09 03:50:51",
            "urlLogo": "https://test-facturacion.olimpush.com/images/logos/..."
        },
        "api": "olimpush"
    }
    """
    response_data, status_code = OlimpushService.consultar_contribuyente(ruc)
    return Response(response_data, status=status_code)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registrar_logo(request, ruc):
    """
    Registra el logo de un contribuyente en el sistema de Olimpush.
    El logo será utilizado en la generación del PDF (RIDE) de los comprobantes electrónicos.
    
    POST /api/olimpush/contribuyentes/{ruc}/logo/
    
    Body: multipart/form-data
        - logo: Archivo de imagen (png, jpg, jpeg)
    
    Respuestas posibles:
        201 - Logo registrado correctamente
        404 - Contribuyente no existe
        400 - Error en el formato del archivo
    
    Ejemplo de respuesta exitosa:
    {
        "code": 201,
        "status": "OK",
        "message": "Logo guardado correctamente.",
        "data": {
            "urlLogo": "https://test-facturacion.olimpush.com/images/logos/..."
        },
        "api": "olimpush"
    }
    """
    # Validar que se envió el archivo
    if 'logo' not in request.FILES:
        return Response({
            "success": False,
            "status_code": 400,
            "message": "No se proporcionó ningún archivo de logo",
            "data": None,
            "api": "djangoclinica"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    logo_file = request.FILES['logo']
    
    # Validar extensión del archivo
    allowed_extensions = ['png', 'jpg', 'jpeg']
    file_extension = logo_file.name.split('.')[-1].lower()
    
    if file_extension not in allowed_extensions:
        return Response({
            "success": False,
            "status_code": 400,
            "message": f"Formato de archivo no permitido. Use: {', '.join(allowed_extensions)}",
            "data": None,
            "api": "djangoclinica"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Enviar a Olimpush
    response_data, status_code = OlimpushService.registrar_logo(ruc, logo_file)
    return Response(response_data, status=status_code)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registrar_firma_electronica(request, ruc):
    """
    Registra la firma electrónica de un contribuyente en el sistema de Olimpush.
    La firma será utilizada para firmar comprobantes electrónicos.
    
    POST /api/olimpush/contribuyentes/{ruc}/certificado/
    
    Body: multipart/form-data
        - firma: Archivo de certificado .p12
        - password: Contraseña del certificado en texto plano
    
    Respuestas posibles:
        200 - Certificado registrado correctamente
        404 - Contribuyente no existe
        400 - Error en el formato del archivo o contraseña incorrecta
    
    Ejemplo de respuesta exitosa:
    {
        "code": 200,
        "status": "OK",
        "message": "Certificado registrado correctamente.",
        "data": "1723774640001-1766208529416.p12",
        "api": "olimpush"
    }
    """
    # Validar que se envió el archivo
    if 'firma' not in request.FILES:
        return Response({
            "success": False,
            "status_code": 400,
            "message": "No se proporcionó ningún archivo de certificado (.p12)",
            "data": None,
            "api": "djangoclinica"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validar que se envió la contraseña
    password = request.data.get('password')
    if not password:
        return Response({
            "success": False,
            "status_code": 400,
            "message": "No se proporcionó la contraseña del certificado",
            "data": None,
            "api": "djangoclinica"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    firma_file = request.FILES['firma']
    
    # Validar extensión del archivo
    file_extension = firma_file.name.split('.')[-1].lower()
    
    if file_extension != 'p12':
        return Response({
            "success": False,
            "status_code": 400,
            "message": "Formato de archivo no permitido. Solo se acepta .p12",
            "data": None,
            "api": "djangoclinica"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Enviar a Olimpush
    response_data, status_code = OlimpushService.registrar_firma_electronica(ruc, firma_file, password)
    return Response(response_data, status=status_code)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_firma_electronica(request, ruc):
    """
    Elimina la firma electrónica de un contribuyente en el sistema de Olimpush.
    La eliminación es permanente y será necesario registrar un nuevo certificado
    si se desea continuar con la firma de documentos electrónicos.
    
    DELETE /api/olimpush/contribuyentes/{ruc}/certificado/
    
    Respuestas posibles:
        200 - Certificado eliminado correctamente
        404 - Contribuyente no existe
    
    Ejemplo de respuesta exitosa:
    {
        "code": 200,
        "status": "OK",
        "message": "Certficado eliminado correctamente.",
        "api": "olimpush"
    }
    """
    response_data, status_code = OlimpushService.eliminar_firma_electronica(ruc)
    return Response(response_data, status=status_code)


# ============================================================================
# UTILIDADES OLIMPUSH
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generar_clave_acceso(request):
    """
    Genera una clave de acceso para documentos electrónicos.
    La clave de acceso es un identificador único de 49 dígitos requerido
    para todos los comprobantes electrónicos en Ecuador.
    
    POST /api/olimpush/util/clave-acceso/
    
    Body: application/json
        - origin: Origen consumo API
        - usrRequest: Usuario consumo API
        - ipRequest: IP del cliente
        - transactionIde: Identificación de la transacción
        - payload: Objeto con datos del documento
            - emissionDate: Fecha de emisión (dd/mm/yyyy)
            - codeDocumentType: Código tipo comprobante (01=Factura, etc.)
            - ruc: RUC del contribuyente
            - establishmentCode: Código establecimiento (001)
            - pointCode: Código punto emisión (002)
            - sequentialNumber: Número secuencial (000000001)
    
    Respuestas posibles:
        200 - Clave de acceso generada
        400 - Campos vacíos o valores incorrectos
    
    Ejemplo de respuesta exitosa:
    {
        "code": 200,
        "status": "OK",
        "message": "Proceso ejecutado correctamente",
        "data": "0711202501172377464000110030020000006406445369812",
        "api": "olimpush"
    }
    """
    # Validar campos requeridos
    required_fields = ['origin', 'usrRequest', 'ipRequest', 'transactionIde', 'payload']
    for field in required_fields:
        if field not in request.data:
            return Response({
                "success": False,
                "status_code": 400,
                "message": f"Campo requerido faltante: {field}",
                "data": None,
                "api": "djangoclinica"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validar campos del payload
    payload = request.data.get('payload', {})
    required_payload_fields = [
        'emissionDate', 'codeDocumentType', 'ruc',
        'establishmentCode', 'pointCode', 'sequentialNumber'
    ]
    
    for field in required_payload_fields:
        if field not in payload:
            return Response({
                "success": False,
                "status_code": 400,
                "message": f"Campo requerido faltante en payload: {field}",
                "data": None,
                "api": "djangoclinica"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Enviar a Olimpush
    response_data, status_code = OlimpushService.generar_clave_acceso(request.data)
    return Response(response_data, status=status_code)


# ============================================================================
# FACTURACIÓN ELECTRÓNICA OLIMPUSH
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_factura(request):
    """
    Crea una factura electrónica en el sistema de Olimpush.
    El documento se envía al SRI para autorización y firma electrónica.
    
    POST /api/olimpush/facturas/crear/
    
    Body: application/json (estructura compleja - ver documentación)
        - origin: Origen consumo API
        - usrRequest: Usuario consumo API
        - ipRequest: IP del cliente
        - transactionIde: ID de transacción
        - payload:
            - taxAuthorityInfo: Info tributaria del emisor
            - invoiceInfo: Info de la factura y cliente
            - details: Lista de productos/servicios
            - paymentMethods: Lista de formas de pago
            - signatureInfo: (Opcional) Firma electrónica
            - additionalAttributes: (Opcional) Atributos adicionales
    
    Respuestas posibles:
        200 - Factura creada y autorizada por el SRI
        200 - Factura recibida pero no autorizada
        400 - Campos incorrectos
        409 - Factura duplicada
    
    Ejemplo de respuesta exitosa:
    {
        "code": 200,
        "status": "OK",
        "message": "Proceso ejecutado correctamente",
        "data": {
            "reception": {
                "status": "RECIBIDA",
                "keyAccess": "..."
            },
            "authorization": {
                "status": "AUTORIZADO",
                "authorizationNumber": "...",
                "pdfBase64": "..."
            },
            "message": "Documento autorizado correctamente"
        },
        "api": "olimpush"
    }
    """
    # Validar campos requeridos principales
    required_fields = ['origin', 'usrRequest', 'ipRequest', 'transactionIde', 'payload']
    for field in required_fields:
        if field not in request.data:
            return Response({
                "success": False,
                "status_code": 400,
                "message": f"Campo requerido faltante: {field}",
                "data": None,
                "api": "djangoclinica"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    payload = request.data.get('payload', {})
    
    # Validar sección taxAuthorityInfo
    if 'taxAuthorityInfo' not in payload:
        return Response({
            "success": False,
            "status_code": 400,
            "message": "Campo requerido faltante en payload: taxAuthorityInfo",
            "data": None,
            "api": "djangoclinica"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validar sección invoiceInfo
    if 'invoiceInfo' not in payload:
        return Response({
            "success": False,
            "status_code": 400,
            "message": "Campo requerido faltante en payload: invoiceInfo",
            "data": None,
            "api": "djangoclinica"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validar detalles (productos/servicios)
    if 'details' not in payload or not isinstance(payload['details'], list) or len(payload['details']) == 0:
        return Response({
            "success": False,
            "status_code": 400,
            "message": "Campo requerido faltante en payload: details (debe ser una lista con al menos un producto)",
            "data": None,
            "api": "djangoclinica"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validar formas de pago
    if 'paymentMethods' not in payload or not isinstance(payload['paymentMethods'], list) or len(payload['paymentMethods']) == 0:
        return Response({
            "success": False,
            "status_code": 400,
            "message": "Campo requerido faltante en payload: paymentMethods (debe ser una lista con al menos una forma de pago)",
            "data": None,
            "api": "djangoclinica"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Enviar a Olimpush
    response_data, status_code = OlimpushService.crear_factura(request.data)
    return Response(response_data, status=status_code)


# ============================================================================
# SUSCRIPCIÓN OLIMPUSH
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def consultar_suscripcion_actual(request):
    """
    Consulta información de la suscripción actual del usuario en Olimpush.
    
    GET /api/olimpush/suscripcion/actual/
    
    Retorna información sobre:
    - Estado de la suscripción (activa/inactiva)
    - Cantidad de documentos disponibles y utilizados
    - Fechas de inicio y vencimiento
    - Tipos de documentos autorizados
    - Servicios habilitados
    
    Respuestas posibles:
        200 - Información de la suscripción
    
    Ejemplo de respuesta exitosa:
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
            "docs": [...],
            "pathWsAllowed": [...]
        },
        "api": "olimpush"
    }
    """
    response_data, status_code = OlimpushService.consultar_suscripcion_actual()
    return Response(response_data, status=status_code)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def consultar_facturas(request):
    """
    Consulta facturas emitidas con filtros opcionales y paginación.
    
    GET /api/olimpush/facturas/
    
    Parámetros de query opcionales:
        - ruc: Número de RUC del contribuyente
        - page: Número de página (por defecto: 1)
        - customer_ide: Número de identificación del cliente
        - authorization_status: Estado de autorización (AUTORIZADO o NO AUTORIZADO)
    
    Ejemplo:
        GET /api/olimpush/facturas/?ruc=2323774440001&page=1&authorization_status=AUTORIZADO
    
    Respuesta exitosa:
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
                        "taxAuthorityInfo": {...},
                        "invoiceInfo": {...},
                        "details": [...],
                        "paymentMethods": [...]
                    },
                    "histories": [...]
                }
            ],
            "page": {
                "totalPages": 4,
                "numElementsByPage": 10,
                "currentPage": 1,
                "totalElements": 35,
                "first": true,
                "last": false,
                "hasPrevious": false,
                "hasNext": true
            }
        }
    }
    """
    # Obtener parámetros de query
    ruc = request.query_params.get('ruc')
    page = request.query_params.get('page', 1)
    customer_ide = request.query_params.get('customer_ide')
    authorization_status = request.query_params.get('authorization_status')
    
    # Validar page
    try:
        page = int(page)
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1
    
    # Validar authorization_status si se proporciona
    if authorization_status and authorization_status not in ['AUTORIZADO', 'NO AUTORIZADO']:
        return Response({
            "success": False,
            "status_code": 400,
            "message": "authorization_status debe ser 'AUTORIZADO' o 'NO AUTORIZADO'",
            "data": None,
            "api": "djangoclinica"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Consultar facturas
    response_data, status_code = OlimpushService.consultar_facturas(
        ruc=ruc,
        page=page,
        customer_ide=customer_ide,
        authorization_status=authorization_status
    )
    return Response(response_data, status=status_code)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generar_secuencial(request):
    """
    Genera el siguiente secuencial disponible para facturación electrónica.
    
    Lógica:
    1. Busca secuenciales marcados como 'available' (fallidos, reutilizables)
    2. Si no hay disponibles, genera nuevo secuencial (último + 1)
    3. Marca el secuencial como 'pending'
    4. Retorna el secuencial formateado en 9 dígitos
    
    Body: {} (vacío) - No requiere parámetros
    
    Respuesta:
    {
        "sequential": "000000001",
        "sequential_id": 1,
        "status": "pending",
        "message": "Secuencial generado correctamente"
    }
    """
    from .models_sequential import Sequential, SequentialUsage
    from django.db import transaction
    
    try:
        with transaction.atomic():
            # Obtener o crear el único registro de secuencial
            sequential_obj, created = Sequential.objects.get_or_create(
                id=1,
                defaults={'last_sequential': 0}
            )
            
            # Buscar secuenciales disponibles (fallidos anteriormente)
            available_sequential = SequentialUsage.objects.filter(
                sequential=sequential_obj,
                status='available'
            ).order_by('sequential_number').first()
            
            if available_sequential:
                # Reutilizar secuencial disponible
                available_sequential.status = 'pending'
                available_sequential.save()
                
                return Response({
                    'sequential': Sequential.format_sequential(available_sequential.sequential_number),
                    'sequential_id': available_sequential.id,
                    'status': 'pending',
                    'reused': True,
                    'message': 'Secuencial reutilizado (previamente fallido)'
                }, status=200)
            else:
                # Generar nuevo secuencial
                new_sequential_number = sequential_obj.last_sequential + 1
                sequential_obj.last_sequential = new_sequential_number
                sequential_obj.save()
                
                # Crear registro de uso
                usage = SequentialUsage.objects.create(
                    sequential=sequential_obj,
                    sequential_number=new_sequential_number,
                    status='pending'
                )
                
                return Response({
                    'sequential': Sequential.format_sequential(new_sequential_number),
                    'sequential_id': usage.id,
                    'status': 'pending',
                    'reused': False,
                    'message': 'Nuevo secuencial generado'
                }, status=200)
                
    except Exception as e:
        return Response({
            'error': f'Error al generar secuencial: {str(e)}'
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def marcar_estado_secuencial(request):
    """
    Marca el estado de un secuencial después de intentar crear la factura.
    
    Casos de uso:
    - Error 400 en API Olimpush: Marcar como 'available' (reutilizable)
    - Error 409 en API Olimpush: Marcar como 'available' (firma no registrada, etc)
    - Éxito en creación: Marcar como 'used'
    
    Body esperado:
    {
        "sequential_id": 1,
        "status": "available" | "used"
    }
    
    Respuesta:
    {
        "message": "Estado actualizado correctamente",
        "sequential": "000000001",
        "status": "available"
    }
    """
    from .models_sequential import SequentialUsage
    
    sequential_id = request.data.get('sequential_id')
    new_status = request.data.get('status')
    
    # Validar campos
    if not sequential_id or not new_status:
        return Response({
            'error': 'Se requieren los campos: sequential_id, status'
        }, status=400)
    
    if new_status not in ['available', 'used']:
        return Response({
            'error': 'El status debe ser "available" o "used"'
        }, status=400)
    
    try:
        usage = SequentialUsage.objects.get(id=sequential_id)
        
        # Verificar que esté en estado pending
        if usage.status != 'pending':
            return Response({
                'error': f'El secuencial no está en estado pending (estado actual: {usage.status})',
                'sequential': usage.get_formatted_sequential(),
                'current_status': usage.status
            }, status=400)
        
        # Actualizar estado
        usage.status = new_status
        usage.save()
        
        return Response({
            'message': 'Estado actualizado correctamente',
            'sequential': usage.get_formatted_sequential(),
            'status': usage.status
        }, status=200)
        
    except SequentialUsage.DoesNotExist:
        return Response({
            'error': 'Secuencial no encontrado'
        }, status=404)
    except Exception as e:
        return Response({
            'error': f'Error al actualizar estado: {str(e)}'
        }, status=500)
