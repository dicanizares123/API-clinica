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
            return Response(serializer.data)
        except Patient.DoesNotExist:
            return Response({
                'exists': False,
                'message': 'Paciente no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
