"""
Serializers para doctores y especialidades.
"""
from rest_framework import serializers
from .models import Doctor, Specialty, DoctorSpecialty


class SpecialtySerializer(serializers.ModelSerializer):
    """
    Serializer para especialidades médicas.
    """
    
    class Meta:
        model = Specialty
        fields = [
            'id',
            'name',
            'description',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DoctorSpecialtySerializer(serializers.ModelSerializer):
    """
    Serializer para la relación Doctor-Especialidad.
    Incluye información de la especialidad.
    """
    specialty_name = serializers.CharField(source='specialty.name', read_only=True)
    specialty_description = serializers.CharField(source='specialty.description', read_only=True)
    
    class Meta:
        model = DoctorSpecialty
        fields = [
            'id',
            'specialty',
            'specialty_name',
            'specialty_description',
            'is_primary',
            'created_at'
        ]
        read_only_fields = ['created_at']


class DoctorSerializer(serializers.ModelSerializer):
    """
    Serializer para doctores.
    Incluye sus especialidades.
    """
    full_name = serializers.SerializerMethodField()
    specialties_list = DoctorSpecialtySerializer(source='specialties', many=True, read_only=True)
    primary_specialty = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctor
        fields = [
            'id',
            'uuid',
            'full_name',
            'first_names',
            'last_names',
            'document_id',
            'email',
            'phone_number',
            'specialties_list',
            'primary_specialty',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        """Retorna el nombre completo del doctor."""
        return obj.get_full_name()
    
    def get_primary_specialty(self, obj):
        """Retorna la especialidad principal del doctor."""
        try:
            primary = obj.specialties.filter(is_primary=True).first()
            if primary:
                return {
                    'id': primary.specialty.id,
                    'name': primary.specialty.name
                }
        except:
            pass
        return None


class DoctorListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar doctores.
    Para usar en el formulario de selección.
    """
    id_doctor = serializers.IntegerField(source='id', read_only=True)
    full_name = serializers.SerializerMethodField()
    primary_specialty = serializers.SerializerMethodField()
    primary_specialty_name = serializers.SerializerMethodField()
    doctor_specialist_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctor
        fields = [
            'id_doctor',
            'full_name',
            'primary_specialty',
            'primary_specialty_name',
            'doctor_specialist_id'
        ]
    
    def get_full_name(self, obj):
        """Retorna el nombre completo del doctor con título."""
        return f"Dr(a). {obj.get_full_name()}"
    
    def get_primary_specialty(self, obj):
        """Retorna el ID de la especialidad principal."""
        try:
            primary = obj.specialties.filter(is_primary=True).first()
            return primary.id if primary else None
        except:
            return None
    
    def get_primary_specialty_name(self, obj):
        """Retorna el nombre de la especialidad principal."""
        try:
            primary = obj.specialties.filter(is_primary=True).first()
            return primary.specialty.name if primary else None
        except:
            return None
    
    def get_doctor_specialist_id(self, obj):
        """Retorna el ID de DoctorSpecialty (mismo que primary_specialty)."""
        try:
            primary = obj.specialties.filter(is_primary=True).first()
            return primary.id if primary else None
        except Exception as e:
            return None
