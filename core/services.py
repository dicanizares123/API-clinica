"""
Servicios para integración con API externa de Olimpush.
"""
import requests
from django.conf import settings
from rest_framework import status as http_status
from rest_framework.response import Response


def django_response(data, message=None, status_code=200, success=True):
    """
    Helper para crear respuestas consistentes de la API Django.
    
    Args:
        data: Datos a retornar
        message: Mensaje descriptivo
        status_code: Código HTTP
        success: Indicador de éxito
        
    Returns:
        Response: Objeto Response con formato estandarizado
    """
    response_data = {
        "success": success,
        "status_code": status_code,
        "message": message,
        "data": data,
        "api": "djangoclinica"
    }
    return Response(response_data, status=status_code)


class OlimpushService:
    """Servicio para interactuar con la API de facturación de Olimpush."""
    
    BASE_URL = settings.OLIMPUSH_API_URL
    TOKEN = settings.OLIMPUSH_API_TOKEN
    
    @classmethod
    def _get_headers(cls, multipart=False):
        """Retorna los headers necesarios para las peticiones.
        
        Args:
            multipart: Si True, no incluye Content-Type para permitir multipart/form-data
        """
        headers = {
            'olimpush-token': cls.TOKEN,
            'Accept': 'application/json'
        }
        if not multipart:
            headers['Content-Type'] = 'application/json'
        return headers
    
    @classmethod
    def _make_request(cls, method: str, endpoint: str, data: dict = None, timeout: int = 30):
        """
        Hace una petición a la API de Olimpush y retorna la respuesta exacta.
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            endpoint: Endpoint de la API (ej: '/ruc/123456789/validation')
            data: Datos para enviar en el body (solo para POST)
            timeout: Tiempo máximo de espera en segundos
            
        Returns:
            tuple: (response_data: dict, status_code: int)
        """
        url = f"{cls.BASE_URL}{endpoint}"
        headers = cls._get_headers()
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                return {
                    "code": 500,
                    "status": "ERROR",
                    "message": f"Método HTTP no soportado: {method}",
                    "data": None,
                    "api": "olimpush"
                }, http_status.HTTP_500_INTERNAL_SERVER_ERROR
            
            # Retornar la respuesta JSON con campo 'api' identificador
            try:
                response_data = response.json()
                # Agregar campo para identificar origen de la respuesta
                response_data['api'] = 'olimpush'
                return response_data, response.status_code
            except ValueError:
                # Si la respuesta no es JSON válido
                return {
                    "code": response.status_code,
                    "status": "ERROR",
                    "message": "Respuesta inválida de la API externa",
                    "data": response.text,
                    "api": "olimpush"
                }, response.status_code
                
        except requests.Timeout:
            return {
                "code": 504,
                "status": "ERROR",
                "message": "Tiempo de espera agotado al consultar la API de facturación",
                "data": None,
                "api": "olimpush"
            }, http_status.HTTP_504_GATEWAY_TIMEOUT
            
        except requests.ConnectionError:
            return {
                "code": 503,
                "status": "ERROR",
                "message": "No se pudo conectar con el servicio de facturación",
                "data": None,
                "api": "olimpush"
            }, http_status.HTTP_503_SERVICE_UNAVAILABLE
            
        except requests.RequestException as e:
            return {
                "code": 502,
                "status": "ERROR",
                "message": f"Error al comunicarse con la API externa: {str(e)}",
                "data": None,
                "api": "olimpush"
            }, http_status.HTTP_502_BAD_GATEWAY
    
    @classmethod
    def _make_request_with_file(cls, method: str, endpoint: str, files: dict = None, data: dict = None, timeout: int = 30):
        """
        Hace una petición con archivos a la API de Olimpush.
        
        Args:
            method: Método HTTP (POST, PUT)
            endpoint: Endpoint de la API
            files: Diccionario con archivos a enviar
            data: Diccionario con datos adicionales (campos de texto)
            timeout: Tiempo máximo de espera en segundos
            
        Returns:
            tuple: (response_data: dict, status_code: int)
        """
        url = f"{cls.BASE_URL}{endpoint}"
        headers = cls._get_headers(multipart=True)
        
        try:
            if method.upper() == 'POST':
                response = requests.post(url, headers=headers, files=files, data=data, timeout=timeout)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, files=files, data=data, timeout=timeout)
            else:
                return {
                    "code": 500,
                    "status": "ERROR",
                    "message": f"Método HTTP no soportado para archivos: {method}",
                    "data": None,
                    "api": "olimpush"
                }, http_status.HTTP_500_INTERNAL_SERVER_ERROR
            
            # Retornar la respuesta JSON con campo 'api' identificador
            try:
                response_data = response.json()
                response_data['api'] = 'olimpush'
                return response_data, response.status_code
            except ValueError:
                return {
                    "code": response.status_code,
                    "status": "ERROR",
                    "message": "Respuesta inválida de la API externa",
                    "data": response.text,
                    "api": "olimpush"
                }, response.status_code
                
        except requests.Timeout:
            return {
                "code": 504,
                "status": "ERROR",
                "message": "Tiempo de espera agotado al consultar la API de facturación",
                "data": None,
                "api": "olimpush"
            }, http_status.HTTP_504_GATEWAY_TIMEOUT
            
        except requests.ConnectionError:
            return {
                "code": 503,
                "status": "ERROR",
                "message": "No se pudo conectar con el servicio de facturación",
                "data": None,
                "api": "olimpush"
            }, http_status.HTTP_503_SERVICE_UNAVAILABLE
            
        except requests.RequestException as e:
            return {
                "code": 502,
                "status": "ERROR",
                "message": f"Error al comunicarse con la API externa: {str(e)}",
                "data": None,
                "api": "olimpush"
            }, http_status.HTTP_502_BAD_GATEWAY
    
    # ========================================================================
    # ENDPOINTS DE VALIDACIÓN DE RUC
    # ========================================================================
    
    @classmethod
    def validar_ruc(cls, ruc: str):
        """
        Valida si un RUC existe en el SRI.
        
        GET /ruc/:rucConsultar/validation
        
        Args:
            ruc: Número de RUC a validar
            
        Returns:
            tuple: (response_data, status_code)
            
        Respuestas posibles:
            200 - RUC existe
            400 - RUC incorrecto (formato inválido)
            404 - RUC no existe
        """
        return cls._make_request('GET', f'/ruc/{ruc}/validation')
    
    @classmethod
    def consultar_establecimientos(cls, ruc: str):
        """
        Consulta todos los establecimientos asociados a un RUC.
        
        GET /ruc/:rucConsultar/establishments
        
        Args:
            ruc: Número de RUC a consultar
            
        Returns:
            tuple: (response_data, status_code)
            
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
                    "direccionCompleta": "...",
                    "estado": "ABIERTO",
                    "numeroEstablecimiento": "001",
                    "matriz": "SI"
                }
            ]
        }
        """
        return cls._make_request('GET', f'/ruc/{ruc}/establishments')
    
    @classmethod
    def consultar_ruc_info(cls, ruc: str):
        """
        Consulta información completa de un RUC (datos del contribuyente).
        
        GET /ruc/:rucConsultar
        
        Args:
            ruc: Número de RUC a consultar
            
        Returns:
            tuple: (response_data, status_code)
            
        Respuestas posibles:
            200 - Información completa del RUC
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
            ]
        }
        """
        return cls._make_request('GET', f'/ruc/{ruc}/details')
    
    @classmethod
    def consultar_contribuyente(cls, ruc: str):
        """
        Consulta información de un contribuyente en el sistema de Olimpush.
        
        GET /contribuyentes/:RUC
        
        Args:
            ruc: Número de RUC del contribuyente
            
        Returns:
            tuple: (response_data, status_code)
            
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
            }
        }
        """
        return cls._make_request('GET', f'/contribuyentes/{ruc}')
    
    @classmethod
    def registrar_logo(cls, ruc: str, logo_file):
        """
        Registra el logo de un contribuyente en el sistema de Olimpush.
        
        POST /contribuyentes/:RUC/logo
        
        Args:
            ruc: Número de RUC del contribuyente
            logo_file: Archivo de imagen (png, jpg, jpeg)
            
        Returns:
            tuple: (response_data, status_code)
            
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
            }
        }
        """
        files = {'logo': logo_file}
        return cls._make_request_with_file('POST', f'/contribuyentes/{ruc}/logo', files=files)
    
    @classmethod
    def registrar_firma_electronica(cls, ruc: str, firma_file, password: str):
        """
        Registra la firma electrónica de un contribuyente en el sistema de Olimpush.
        
        POST /contribuyentes/:RUC/certificado
        
        Args:
            ruc: Número de RUC del contribuyente
            firma_file: Archivo de certificado .p12
            password: Contraseña del certificado en texto plano
            
        Returns:
            tuple: (response_data, status_code)
            
        Respuestas posibles:
            200 - Certificado registrado correctamente
            404 - Contribuyente no existe
            400 - Error en el formato del archivo o contraseña incorrecta
        
        Ejemplo de respuesta exitosa:
        {
            "code": 200,
            "status": "OK",
            "message": "Certificado registrado correctamente.",
            "data": "1723774640001-1766208529416.p12"
        }
        """
        files = {'firma': firma_file}
        data = {'password': password}
        return cls._make_request_with_file('POST', f'/contribuyentes/{ruc}/certificado', files=files, data=data)
    
    @classmethod
    def eliminar_firma_electronica(cls, ruc: str):
        """
        Elimina la firma electrónica de un contribuyente en el sistema de Olimpush.
        
        DELETE /contribuyentes/:RUC/certificado
        
        Args:
            ruc: Número de RUC del contribuyente
            
        Returns:
            tuple: (response_data, status_code)
            
        Respuestas posibles:
            200 - Certificado eliminado correctamente
            404 - Contribuyente no existe
        
        Ejemplo de respuesta exitosa:
        {
            "code": 200,
            "status": "OK",
            "message": "Certficado eliminado correctamente."
        }
        """
        return cls._make_request('DELETE', f'/contribuyentes/{ruc}/certificado')
    
    # ========================================================================
    # ENDPOINTS DE UTILIDADES
    # ========================================================================
    
    @classmethod
    def generar_clave_acceso(cls, payload_data: dict):
        """
        Genera una clave de acceso para documentos electrónicos.
        
        POST /util/keyAccess
        
        Args:
            payload_data: Diccionario con la información para generar la clave:
                - origin: Origen consumo API
                - usrRequest: Usuario consumo API
                - ipRequest: IP del cliente
                - transactionIde: Identificación de la transacción
                - payload: Objeto con:
                    - emissionDate: Fecha de emisión (dd/mm/yyyy)
                    - codeDocumentType: Código tipo de comprobante
                    - ruc: RUC del contribuyente
                    - establishmentCode: Código de establecimiento (ej: 001)
                    - pointCode: Código punto de emisión (ej: 002)
                    - sequentialNumber: Número secuencial (ej: 000000002)
            
        Returns:
            tuple: (response_data, status_code)
            
        Respuestas posibles:
            200 - Clave de acceso generada correctamente
            400 - Campos vacíos o valores incorrectos
        
        Ejemplo de respuesta exitosa:
        {
            "code": 200,
            "status": "OK",
            "message": "Proceso ejecutado correctamente",
            "data": "0711202501172377464000110030020000006406445369812"
        }
        """
        return cls._make_request('POST', '/util/keyAccess', data=payload_data)
    
    # ========================================================================
    # ENDPOINTS DE FACTURACIÓN ELECTRÓNICA
    # ========================================================================
    
    @classmethod
    def crear_factura(cls, factura_data: dict):
        """
        Crea una factura electrónica en el sistema de Olimpush.
        
        POST /individual/invoice/create
        
        Args:
            factura_data: Diccionario con la información completa de la factura:
                - origin: Origen consumo API
                - usrRequest: Usuario consumo API
                - ipRequest: IP del cliente
                - transactionIde: Identificación de la transacción
                - payload: Objeto con:
                    - taxAuthorityInfo: Información tributaria del emisor
                    - invoiceInfo: Información de la factura y cliente
                    - details: Lista de productos/servicios
                    - paymentMethods: Lista de formas de pago
                    - signatureInfo: (Opcional) Información de firma electrónica
                    - additionalAttributes: (Opcional) Atributos adicionales
            
        Returns:
            tuple: (response_data, status_code)
            
        Respuestas posibles:
            200 - Factura creada y autorizada
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
                    "keyAccess": "...",
                    ...
                },
                "authorization": {
                    "status": "AUTORIZADO",
                    "authorizationNumber": "...",
                    "pdfBase64": "...",
                    "voucher": "...",
                    ...
                },
                "message": "Documento autorizado correctamente"
            }
        }
        """
        return cls._make_request('POST', '/individual/invoice/create', data=factura_data)
    
    # ========================================================================
    # ENDPOINTS DE SUSCRIPCIÓN
    # ========================================================================
    
    @classmethod
    def consultar_suscripcion_actual(cls):
        """
        Consulta información de la suscripción actual del usuario en Olimpush.
        
        GET /subscriptions/current
        
        Returns:
            tuple: (response_data, status_code)
            
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
                "observation": "token creado con exito",
                "docs": [
                    {
                        "description": "FACTURA",
                        "code": "01"
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
            }
        }
        """
        return cls._make_request('GET', '/subscriptions/current')
    
    @classmethod
    def consultar_facturas(cls, ruc=None, page=1, customer_ide=None, authorization_status=None):
        """
        Consulta facturas emitidas con filtros opcionales.
        
        Args:
            ruc: Número de RUC del contribuyente (opcional)
            page: Número de página (por defecto: 1)
            customer_ide: Número de identificación del cliente (opcional)
            authorization_status: Estado de autorización (AUTORIZADO o NO AUTORIZADO) (opcional)
        
        Returns:
            tuple: (response_data, status_code)
        
        Ejemplo de respuesta exitosa:
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
                        "document": {...},
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
        # Construir query params manualmente
        query_params = []
        
        if ruc:
            query_params.append(f'ruc={ruc}')
        
        query_params.append(f'page={page}')
        
        if customer_ide:
            query_params.append(f'customerIde={customer_ide}')
        
        if authorization_status:
            query_params.append(f'authorizationStatus={authorization_status}')
        
        # Construir endpoint con query string
        query_string = '&'.join(query_params)
        endpoint = f'/individual/invoice?{query_string}'
        
        return cls._make_request('GET', endpoint)
