
from django.contrib import admin
from django.urls import path, include 
from auth.views import LogoutView 
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')), 
    path('auth/', include('djoser.urls.jwt')),
    path('auth/logout/', LogoutView.as_view()),
    
    # API REST
    path('api/', include('appointments.urls')),
    path('api/', include('patients.urls')),
    path('api/', include('doctors.urls')),
    path('api/', include('notifications.urls')), 

    # Documentación API 
    path('docs/', include_docs_urls(title='API Documentación'))


]
