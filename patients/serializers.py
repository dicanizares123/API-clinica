"""
Serializers para gestión de pacientes.
"""
from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer para pacientes.
    Permite crear y consultar información de pacientes.
    Usado por ADMINISTRADORES - pueden editar TODO incluyendo email.
    """
    full_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id',
            'uuid',
            'first_names',
            'last_names',
            'full_name',
            'document_id',
            'email',
            'phone_number',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        """Retorna el nombre completo del paciente."""
        return obj.get_full_name()


class PatientDoctorUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para que DOCTORES actualicen pacientes.
    NO pueden editar el campo email.
    """
    full_name = serializers.SerializerMethodField(read_only=True)
    email = serializers.EmailField(read_only=True)  # Email es solo lectura para doctores
    
    class Meta:
        model = Patient
        fields = [
            'id',
            'uuid',
            'first_names',
            'last_names',
            'full_name',
            'document_id',
            'email',           # Se muestra pero no se puede editar
            'phone_number',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['uuid', 'email', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        """Retorna el nombre completo del paciente."""
        return obj.get_full_name()


class PatientCreateSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para crear pacientes desde formulario público.
    """
    
    class Meta:
        model = Patient
        fields = [
            'first_names',
            'last_names',
            'document_id',
            'email',
            'phone_number',
        ]
    
    def create(self, validated_data):
        """
        Crea o actualiza paciente basándose en document_id.
        Si ya existe un paciente con esa cédula, actualiza sus datos.
        """
        document_id = validated_data.get('document_id')
        
        # Buscar si ya existe un paciente con esa cédula
        patient, created = Patient.objects.update_or_create(
            document_id=document_id,
            defaults=validated_data
        )
        
        return patient
