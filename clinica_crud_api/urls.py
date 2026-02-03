
from django.contrib import admin
from django.urls import path, include 
from auth.views import LogoutView 
from rest_framework.documentation import include_docs_urls
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes, api_view
from core.views import api_root

urlpatterns = [
    # Página principal de la API
    path('', api_root, name='api-root'),
    
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')), 
    path('auth/', include('djoser.urls.jwt')),
    path('auth/logout/', LogoutView.as_view()),
    
    # API REST
    path('api/', include('appointments.urls')),
    path('api/', include('patients.urls')),
    path('api/', include('doctors.urls')),
    path('api/', include('notifications.urls')),
    path('api/', include('core.urls')),  # Proxy a Olimpush, 

    # Documentación API (sin autenticación en desarrollo)
    path('docs/', include_docs_urls(
        title='API Documentación - Clínica',
        description='Documentación completa de la API REST para el sistema de gestión de clínica médica.',
        permission_classes=[AllowAny]
    ))


]
