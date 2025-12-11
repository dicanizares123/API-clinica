"""
URLs para doctores y especialidades.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoctorViewSet, SpecialtyViewSet, DoctorSpecialtyViewSet

router = DefaultRouter()
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'specialties', SpecialtyViewSet, basename='specialty')
router.register(r'doctor-specialties', DoctorSpecialtyViewSet, basename='doctor-specialty')

urlpatterns = [
    path('', include(router.urls)),
]
