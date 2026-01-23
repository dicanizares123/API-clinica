from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    """
    Manejador global de excepciones.
    Intercepta los errores de DRF y estandariza la respuesta JSON.
    """

     # 1. Llamamos al manejador por defecto de DRF primero
    # Esto nos devuelve la respuesta estándar (Response object) o None
    response = exception_handler(exc, context) 

    # 2. Si DRF manejó el error (es un error conocido como 400, 403, 404)
    if response is not None:
        
        # Estructura base que queremos devolver siempre
        custom_data = {
            "success": False,
            "status_code": response.status_code,
            "message": "Ha ocurrido un error",
            "errors": None
        } 

    # --- CASO 1: Errores de Validación (400) ---
    if response.status_code == 400:
        custom_data["message"] = "Error en los datos enviados."
        custom_data["errors"] = response.data  # Aquí van los campos {email: [...], password: [...]} 
    
    # --- CASO 2: Autenticación y Permisos (401, 403) ---
    elif response.status_code in [401, 403]:
        # DRF suele devolver {'detail': 'No tienes permisos...'}
        # Lo movemos al campo 'message' para que sea más limpio
        if 'detail' in response.data:
            custom_data["message"] = response.data['detail']
        else:
            custom_data["message"] = "No autorizado."
    
    # --- CASO 3: Not Found (404) ---
    elif response.status_code == 404:
        custom_data["message"] = "El recurso solicitado no existe."

    # Reemplazamos los datos originales por nuestra estructura bonita
    response.data = custom_data

    return response