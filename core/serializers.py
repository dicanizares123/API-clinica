"""
Serializers del módulo core.
"""
from rest_framework import serializers
from .models import BusinessInfo, Product


class BusinessInfoSerializer(serializers.ModelSerializer):
    """Serializer para información del negocio."""
    
    class Meta:
        model = BusinessInfo
        fields = ['id', 'ruc', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer para productos/servicios."""
    
    class Meta:
        model = Product
        fields = ['id', 'description', 'code', 'unit_price']
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer para productos/servicios."""
    
    class Meta:
        model = Product
        fields = ['id', 'description', 'code', 'unit_price']
        read_only_fields = ['id']
