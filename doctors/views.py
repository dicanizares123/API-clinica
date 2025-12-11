"""
Vistas para gestión de doctores y especialidades.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Doctor, Specialty, DoctorSpecialty
from .serializers import (
    DoctorSerializer,
    DoctorListSerializer,
    SpecialtySerializer,
    DoctorSpecialtySerializer
)


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar doctores.
    
    Endpoints:
        GET /api/doctors/            - Listar doctores activos (PÚBLICO)
        GET /api/doctors/{id}/       - Ver detalle de doctor (PÚBLICO)
    
    Solo lectura, no permite crear/modificar doctores desde la API.
    """
    queryset = Doctor.objects.filter(is_active=True).order_by('first_names')
    permission_classes = []  # Público para que formulario pueda listar doctores
    
    def get_serializer_class(self):
        """
        Usa serializer simplificado para lista, completo para detalle.
        """
        if self.action == 'list':
            return DoctorListSerializer
        return DoctorSerializer


class SpecialtyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar especialidades médicas.
    
    Endpoints:
        GET /api/specialties/        - Listar especialidades (PÚBLICO)
        GET /api/specialties/{id}/   - Ver detalle (PÚBLICO)
    """
    queryset = Specialty.objects.filter(is_active=True).order_by('name')
    serializer_class = SpecialtySerializer
    permission_classes = []  # Público


class DoctorSpecialtyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar relaciones Doctor-Especialidad.
    
    Endpoints:
        GET /api/doctor-specialties/     - Listar todas las relaciones (requiere auth)
        GET /api/doctor-specialties/{id}/ - Ver detalle (requiere auth)
    """
    queryset = DoctorSpecialty.objects.all().select_related('doctor', 'specialty')
    serializer_class = DoctorSpecialtySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Permite filtrar por doctor.
        """
        queryset = super().get_queryset()
        doctor_id = self.request.query_params.get('doctor', None)
        
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        
        return queryset
