"""
Vistas para el sistema de notificaciones.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar notificaciones del usuario logueado.
    
    Endpoints:
        GET    /api/notifications/              - Listar mis notificaciones
        GET    /api/notifications/unread/       - Listar solo no leídas
        GET    /api/notifications/unread-count/ - Contar no leídas
        POST   /api/notifications/{id}/mark-read/    - Marcar como leída
        POST   /api/notifications/mark-all-read/     - Marcar todas como leídas
        DELETE /api/notifications/{id}/         - Eliminar notificación
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Solo muestra notificaciones del usuario logueado."""
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        Lista solo las notificaciones no leídas.
        
        GET /api/notifications/unread/
        """
        queryset = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        """
        Retorna el conteo de notificaciones no leídas.
        Útil para mostrar el badge en el ícono de notificaciones.
        
        GET /api/notifications/unread-count/
        
        Response: { "count": 5 }
        """
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'count': count})
    
    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """
        Marca una notificación como leída.
        
        POST /api/notifications/{id}/mark-read/
        """
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        """
        Marca todas las notificaciones como leídas.
        
        POST /api/notifications/mark-all-read/
        """
        updated = self.get_queryset().filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({
            'message': f'{updated} notificaciones marcadas como leídas'
        })
    
    def destroy(self, request, *args, **kwargs):
        """Elimina una notificación."""
        notification = self.get_object()
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
