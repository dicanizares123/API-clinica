"""
Serializers para el sistema de citas.
Convierten los modelos de Django a JSON y viceversa.
"""
from rest_framework import serializers
from .models import Appointment, DoctorSchedule, BlockTimeSlot
from doctors.models import Doctor, DoctorSpecialty
from patients.models import Patient
from datetime import datetime, timedelta


# ============================================================================
# DOCTOR SCHEDULE SERIALIZER
# ============================================================================
class DoctorScheduleSerializer(serializers.ModelSerializer):
    """
    Serializer para horarios de doctores.
    Muestra la configuración de horarios por día de la semana.
    """
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DoctorSchedule
        fields = [
            'id',
            'doctor',
            'doctor_name',
            'day_of_week',
            'day_name',
            'start_time',
            'end_time',
            'slot_duration_minutes',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_doctor_name(self, obj):
        """Retorna el nombre completo del doctor."""
        return obj.doctor.get_full_name()


# ============================================================================
# BLOCK TIME SLOT SERIALIZER
# ============================================================================
class BlockTimeSlotSerializer(serializers.ModelSerializer):
    """
    Serializer para bloqueos de horarios.
    Permite a doctores/admins bloquear slots específicos.
    """
    doctor_name = serializers.SerializerMethodField()
    blocked_by_username = serializers.SerializerMethodField()
    
    class Meta:
        model = BlockTimeSlot
        fields = [
            'id',
            'doctor',
            'doctor_name',
            'date',
            'blocked_time',
            'reason',
            'blocked_by_user',
            'blocked_by_username',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'blocked_by_user']
    
    def get_doctor_name(self, obj):
        """Retorna el nombre completo del doctor."""
        return obj.doctor.get_full_name()
    
    def get_blocked_by_username(self, obj):
        """Retorna el email del usuario que bloqueó."""
        if obj.blocked_by_user:
            return obj.blocked_by_user.email
        return None
    
    def create(self, validated_data):
        """
        Asigna automáticamente el usuario que crea el bloqueo.
        """
        user = self.context['request'].user
        validated_data['blocked_by_user'] = user
        return super().create(validated_data)


# ============================================================================
# APPOINTMENT SERIALIZER
# ============================================================================
class AppointmentSerializer(serializers.ModelSerializer):
    """
    Serializer para citas médicas.
    Incluye validación de disponibilidad de horarios.
    """
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    doctor_specialist = serializers.PrimaryKeyRelatedField(queryset=DoctorSpecialty.objects.all())
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    specialty_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id',
            'uuid',
            'patient',
            'patient_name',
            'doctor_specialist',
            'doctor_name',
            'specialty_name',
            'appointment_date',
            'appointment_time',
            'duration_minutes',
            'status',
            'status_display',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']
    
    def get_patient_name(self, obj):
        """Retorna el nombre completo del paciente."""
        return obj.patient.get_full_name()
    
    def get_doctor_name(self, obj):
        """Retorna el nombre completo del doctor."""
        return obj.doctor_specialist.doctor.get_full_name()
    
    def get_specialty_name(self, obj):
        """Retorna el nombre de la especialidad."""
        return obj.doctor_specialist.specialty.name
    
    def validate(self, data):
        """
        Valida que el horario esté disponible antes de crear/actualizar la cita.
        Solo valida horarios si se están cambiando campos relevantes.
        """
        instance = self.instance
        
        # Obtener valores: del data si se envían, o del instance si existe
        appointment_date = data.get('appointment_date')
        appointment_time = data.get('appointment_time')
        doctor_specialist = data.get('doctor_specialist')
        
        # Si es actualización parcial (PATCH) y no se envían campos de horario, no validar
        if instance:
            # Usar valores existentes si no se proporcionan nuevos
            if appointment_date is None:
                appointment_date = instance.appointment_date
            if appointment_time is None:
                appointment_time = instance.appointment_time
            if doctor_specialist is None:
                doctor_specialist = instance.doctor_specialist
            
            # Si solo se actualizan campos como notes o status, no validar horarios
            horario_fields = {'appointment_date', 'appointment_time', 'doctor_specialist', 'patient'}
            if not any(field in data for field in horario_fields):
                return data
        
        # Si no hay doctor_specialist, no podemos validar (error de datos)
        if doctor_specialist is None:
            raise serializers.ValidationError("El campo doctor_specialist es requerido.")
        
        # Obtener el doctor del doctor_specialist
        doctor = doctor_specialist.doctor
        
        # 1. Verificar que el doctor tenga horario configurado para ese día
        day_of_week = appointment_date.weekday()
        try:
            schedule = DoctorSchedule.objects.get(
                doctor=doctor,
                day_of_week=day_of_week,
                is_active=True
            )
        except DoctorSchedule.DoesNotExist:
            raise serializers.ValidationError(
                f"El doctor no tiene horario configurado para {appointment_date.strftime('%A')}."
            )
        
        # 2. Verificar que la hora esté dentro del horario del doctor
        if appointment_time < schedule.start_time or appointment_time >= schedule.end_time:
            raise serializers.ValidationError(
                f"La hora debe estar entre {schedule.start_time.strftime('%H:%M')} "
                f"y {schedule.end_time.strftime('%H:%M')}."
            )
        
        # 3. Verificar que no haya otra cita en ese horario
        conflicting_appointments = Appointment.objects.filter(
            doctor_specialist__doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status__in=['scheduled', 'confirmed']
        )
        
        # Si estamos actualizando, excluir la cita actual
        if instance:
            conflicting_appointments = conflicting_appointments.exclude(pk=instance.pk)
        
        if conflicting_appointments.exists():
            raise serializers.ValidationError(
                "Ya existe una cita agendada en ese horario."
            )
        
        # 4. Verificar que el horario no esté bloqueado
        blocked = BlockTimeSlot.objects.filter(
            doctor=doctor,
            date=appointment_date,
            blocked_time=appointment_time,
            is_active=True
        ).exists()
        
        if blocked:
            raise serializers.ValidationError(
                "Este horario ha sido bloqueado y no está disponible."
            )
        
        return data


# ============================================================================
# APPOINTMENT CREATE SERIALIZER
# ============================================================================
class AppointmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para crear citas.
    Acepta IDs directamente en lugar de objetos completos.
    """
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    doctor_specialist = serializers.PrimaryKeyRelatedField(queryset=DoctorSpecialty.objects.all())
    
    class Meta:
        model = Appointment
        fields = [
            'patient',
            'doctor_specialist',
            'appointment_date',
            'appointment_time',
            'duration_minutes',
            'notes'
        ]
    
    def validate(self, data):
        """
        Valida disponibilidad del horario antes de crear la cita.
        """
        appointment_date = data.get('appointment_date')
        appointment_time = data.get('appointment_time')
        doctor_specialist = data.get('doctor_specialist')
        
        # Obtener el doctor del doctor_specialist
        doctor = doctor_specialist.doctor
        
        # 1. Verificar que el doctor tenga horario configurado para ese día
        day_of_week = appointment_date.weekday()
        try:
            schedule = DoctorSchedule.objects.get(
                doctor=doctor,
                day_of_week=day_of_week,
                is_active=True
            )
        except DoctorSchedule.DoesNotExist:
            raise serializers.ValidationError(
                f"El doctor no tiene horario configurado para {appointment_date.strftime('%A')}."
            )
        
        # 2. Verificar que la hora esté dentro del horario del doctor
        if appointment_time < schedule.start_time or appointment_time >= schedule.end_time:
            raise serializers.ValidationError(
                f"La hora debe estar entre {schedule.start_time.strftime('%H:%M')} "
                f"y {schedule.end_time.strftime('%H:%M')}."
            )
        
        # 3. Verificar que no haya otra cita en ese horario
        conflicting_appointments = Appointment.objects.filter(
            doctor_specialist__doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status__in=['scheduled', 'confirmed']
        )
        
        if conflicting_appointments.exists():
            raise serializers.ValidationError(
                "Ya existe una cita agendada en ese horario."
            )
        
        # 4. Verificar que el horario no esté bloqueado
        blocked = BlockTimeSlot.objects.filter(
            doctor=doctor,
            date=appointment_date,
            blocked_time=appointment_time,
            is_active=True
        ).exists()
        
        if blocked:
            raise serializers.ValidationError(
                "Este horario ha sido bloqueado y no está disponible."
            )
        
        return data
    
    def create(self, validated_data):
        """
        Crea la cita con status 'scheduled' por defecto.
        """
        validated_data['status'] = 'scheduled'
        return super().create(validated_data)


# ============================================================================
# AVAILABLE SLOTS SERIALIZER
# ============================================================================
class AvailableSlotsSerializer(serializers.Serializer):
    """
    Serializer para mostrar horarios disponibles.
    No está vinculado a un modelo, solo devuelve datos calculados.
    """
    date = serializers.DateField()
    day_name = serializers.CharField()
    available_slots = serializers.ListField(child=serializers.TimeField())
    total_slots = serializers.IntegerField()
    available_count = serializers.IntegerField()
    occupied_count = serializers.IntegerField()
    blocked_count = serializers.IntegerField()
