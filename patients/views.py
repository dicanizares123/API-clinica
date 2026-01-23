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
            user = self.request.user
            # Si es administrador, puede editar todo
            if user.role and user.role.slug == 'administrador':
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
        return Response({
            'message': f'Paciente "{patient_name}" eliminado exitosamente'
        }, status=status.HTTP_200_OK)
    

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
    

