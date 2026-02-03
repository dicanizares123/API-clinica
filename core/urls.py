"""
URLs del módulo core.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Información del negocio
    path('business/ruc/', views.get_business_ruc, name='business-ruc'),
    
    # Productos/Servicios
    path('productos/', views.productos_list_create, name='productos-list-create'),
    path('productos/<int:pk>/', views.producto_detail, name='producto-detail'),
    
    # Proxy a API de Olimpush - Facturación Electrónica
    path('olimpush/ruc/<str:ruc>/validation/', views.validar_ruc, name='olimpush-validar-ruc'),
    path('olimpush/ruc/<str:ruc>/establishments/', views.consultar_establecimientos, name='olimpush-establecimientos'),
    path('olimpush/ruc/<str:ruc>/', views.consultar_ruc_info, name='olimpush-ruc-info'),
    path('olimpush/contribuyentes/<str:ruc>/', views.consultar_contribuyente, name='olimpush-contribuyente'),
    path('olimpush/contribuyentes/<str:ruc>/logo/', views.registrar_logo, name='olimpush-registrar-logo'),
    path('olimpush/contribuyentes/<str:ruc>/certificado/', views.registrar_firma_electronica, name='olimpush-registrar-firma'),
    path('olimpush/contribuyentes/<str:ruc>/certificado/delete/', views.eliminar_firma_electronica, name='olimpush-eliminar-firma'),
    
    # Utilidades Olimpush
    path('olimpush/util/clave-acceso/', views.generar_clave_acceso, name='olimpush-generar-clave-acceso'),
    
    # Facturación Electrónica Olimpush
    path('olimpush/facturas/crear/', views.crear_factura, name='olimpush-crear-factura'),
    path('olimpush/facturas/', views.consultar_facturas, name='olimpush-consultar-facturas'),
    
    # Suscripción Olimpush
    path('olimpush/suscripcion/actual/', views.consultar_suscripcion_actual, name='olimpush-suscripcion-actual'),
    
    # Gestión de Secuenciales para Facturación Electrónica
    path('secuencial/generar/', views.generar_secuencial, name='generar-secuencial'),
    path('secuencial/marcar-estado/', views.marcar_estado_secuencial, name='marcar-estado-secuencial'),
]
