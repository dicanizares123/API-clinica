"""
Views para gestión de usuarios y roles.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User, Role
from .serializers import UserSerializer, RoleSerializer
from .permissions import IsAdministrador, IsAdminOrReadOnly


# ============================================================================
# ROLE VIEWSET
# ============================================================================
class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para roles del sistema.
    Solo lectura para usuarios autenticados.
    """
    queryset = Role.objects.filter(is_active=True)
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtra roles según permisos del usuario."""
        # Admins ven todos los roles
        if self.request.user.is_admin:
            return Role.objects.all()
        # Otros usuarios solo ven roles activos
        return Role.objects.filter(is_active=True)


# ============================================================================
# USER VIEWSET
# ============================================================================
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para usuarios del sistema.
    CRUD completo con permisos basados en roles.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'uuid'
    
    def get_permissions(self):
        """Define permisos según la acción."""
        if self.action in ['create', 'destroy']:
            permission_classes = [IsAdministrador]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAdministrador]
        elif self.action == 'list':
            permission_classes = [IsAdministrador]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Obtener información del usuario actual.
        GET /api/users/me/
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
