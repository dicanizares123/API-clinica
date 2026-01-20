"""
URLs para el sistema de citas.
Define las rutas de la API REST.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AppointmentViewSet,
    DoctorScheduleViewSet,
    BlockTimeSlotViewSet,
    AvailableSlotsViewSet, 
    
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'schedules', DoctorScheduleViewSet, basename='schedule')
router.register(r'blocked-slots', BlockTimeSlotViewSet, basename='blocked-slot')
router.register(r'available-slots', AvailableSlotsViewSet, basename='available-slots')

urlpatterns = [
    path('', include(router.urls)), 

    # URL especifico para el grafico 

]
