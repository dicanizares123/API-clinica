"""
Vistas para gestión de pacientes.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Patient
from .serializers import PatientSerializer, PatientCreateSerializer, PatientDoctorUpdateSerializer
from users.permissions import IsAdministrador
from django.db.models import Q
from core.services import django_response 



class PatientViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar pacientes.
    
    Endpoints:
        GET    /api/patients/                     - Listar pacientes (requiere auth)
        POST   /api/patients/                     - Crear/actualizar paciente (PÚBLICO)
        GET    /api/patients/{id}/                - Ver detalle (requiere auth)
        PUT    /api/patients/{id}/                - Actualizar paciente (admin: todo, doctor: sin email)
        PATCH  /api/patients/{id}/                - Actualizar parcial (admin: todo, doctor: sin email)
        DELETE /api/patients/{id}/                - Eliminar paciente (SOLO ADMIN)
        GET    /api/patients/by_document/{cedula}/ - Buscar por cédula (PÚBLICO)
    """
    queryset = Patient.objects.all().order_by('-created_at')
    
    def get_permissions(self):
        """
        Permisos personalizados:
        - create: Público (para formulario de citas)
        - by_document: Público (para buscar paciente existente)
        - destroy: Solo administrador
        - Resto: Requiere autenticación
        """
        if self.action in ['create', 'by_document']:
            return []  # Público
        if self.action == 'destroy':
            return [IsAuthenticated(), IsAdministrador()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        """
        Usa serializer diferente según acción y rol del usuario.
        """
        if self.action == 'create':
            return PatientCreateSerializer
        
        # Para update/partial_update, verificar si es admin o doctor
        if self.action in ['update', 'partial_update']:
            # Verificar que el usuario esté autenticado
            if hasattr(self.request, 'user') and self.request.user and self.request.user.is_authenticated:
                user = self.request.user
                # Si es administrador, puede editar todo
                if hasattr(user, 'role') and user.role and user.role.slug == 'administrador':
                    return PatientSerializer
                # Si es doctor u otro rol, no puede editar email
                return PatientDoctorUpdateSerializer
        
        return PatientSerializer
    
    def destroy(self, request, *args, **kwargs):
        """
        Eliminar paciente - Solo administradores.
        """
        patient = self.get_object()
        patient_name = patient.get_full_name()
        patient.delete()
        return django_response(
            data=None,
            message=f'Paciente "{patient_name}" eliminado exitosamente',
            status_code=200
        )
    
    
    @action(detail=False, methods=['get'], url_path='by_document/(?P<document_id>[^/.]+)')
    def by_document(self, request, document_id=None):
        """
        Busca un paciente por su cédula/documento de identidad.
        
        GET /api/patients/by_document/{document_id}/
        
        Ejemplo: GET /api/patients/by_document/1234567890/
        
        Response si existe:
            {
                "id": 1,
                "uuid": "...",
                "first_names": "Juan Carlos",
                "last_names": "Pérez García",
                "document_id": "1234567890",
                "email": "juan@email.com",
                "phone_number": "0987654321",
                ...
            }
        
        Response si no existe:
            {
                "exists": false,
                "message": "Paciente no encontrado"
            }
        """
        try:
            patient = Patient.objects.get(document_id=document_id)
            serializer = self.get_serializer(patient)
            return django_response(
                data=serializer.data,
                message='Paciente encontrado',
                status_code=200
            )
        except Patient.DoesNotExist:
            return django_response(
                data={'exists': False},
                message='Paciente no encontrado',
                status_code=404,
                success=False
            )
    

    def get_queryset(self):
        """
        Permite filtrar pacientes por búsqueda de texto (nombre, apellido, cédula).
        """
        queryset = super().get_queryset()
        
        # Capturar el parámetro 'search' de la URL
        search_query = self.request.query_params.get('search', None)

        if search_query:
            queryset = queryset.filter(
                Q(first_names__icontains=search_query) | 
                Q(last_names__icontains=search_query) |
                Q(document_id__icontains=search_query)
            )
            
        return queryset
    

