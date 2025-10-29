
from django.contrib import admin
from django.urls import path, include 
from auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')), 
    path('auth/', include('djoser.urls.jwt')),
    path('auth/logout/', LogoutView.as_view()),
    
]
