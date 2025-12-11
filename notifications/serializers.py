"""
Serializers para el sistema de notificaciones.
"""
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer para notificaciones.
    """
    type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    appointment_id = serializers.IntegerField(source='appointment.id', read_only=True, allow_null=True)
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'notification_type',
            'type_display',
            'title',
            'message',
            'appointment_id',
            'is_read',
            'read_at',
            'time_ago',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_time_ago(self, obj):
        """Retorna tiempo transcurrido desde la creación."""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff < timedelta(minutes=1):
            return "Ahora mismo"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"Hace {minutes} min"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"Hace {hours} hora{'s' if hours > 1 else ''}"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"Hace {days} día{'s' if days > 1 else ''}"
        else:
            return obj.created_at.strftime("%d/%m/%Y")
