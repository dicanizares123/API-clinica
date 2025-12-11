"""
Configuración del panel de administración para Citas y Horarios.
"""
from django import forms
from django.contrib import admin
from datetime import datetime, timedelta, time
from .models import Appointment, DoctorSchedule, BlockTimeSlot


# ============================================================================
# APPOINTMENT FORM - Formulario personalizado con horarios disponibles
# ============================================================================
class AppointmentForm(forms.ModelForm):
    """
    Formulario personalizado para citas.
    Calcula y muestra solo horarios disponibles basándose en:
    - Horarios configurados del doctor (DoctorSchedule)
    - Citas ya agendadas (Appointments)
    - Bloqueos manuales (BlockTimeSlot)
    """
    
    appointment_time = forms.ChoiceField(
        label='Hora de la cita',
        help_text='Selecciona una franja horaria disponible',
        required=True
    )
    
    class Meta:
        model = Appointment
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si ya existe la cita (edición), obtener los valores actuales
        instance = kwargs.get('instance')
        current_date = instance.appointment_date if instance else None
        current_doctor = instance.doctor_specialist.doctor if instance else None
        current_time = instance.appointment_time if instance else None
        
        # Generar opciones de horarios disponibles
        time_choices = self._get_available_time_slots(current_date, current_doctor, current_time)
        self.fields['appointment_time'].choices = time_choices
        
        # Mostrar mensaje si no hay opciones disponibles
        if len(time_choices) <= 1:  # Solo tiene la opción por defecto
            if current_date and current_doctor:
                self.fields['appointment_time'].help_text = '⚠️ No hay horarios disponibles para esta fecha y doctor. Verifica que el doctor tenga horarios configurados.'
            else:
                self.fields['appointment_time'].help_text = 'Los horarios se calcularán después de seleccionar fecha y doctor. Guarda primero con cualquier hora, luego edita para ver horarios disponibles.'
    
    def _get_available_time_slots(self, date, doctor, current_time=None):
        """
        Calcula franjas horarias disponibles.
        
        Args:
            date: Fecha de la cita
            doctor: Instancia del Doctor
            current_time: Hora actual de la cita (para edición)
        
        Returns:
            Lista de tuplas (valor, etiqueta) para el campo choice
        """
        choices = [('', '--- Selecciona una hora ---')]
        
        # Si no hay fecha o doctor, retornar vacío
        if not date or not doctor:
            return choices
        
        # Obtener día de la semana (0=Lunes, 6=Domingo)
        day_of_week = date.weekday()
        
        # Buscar horario configurado para ese día
        try:
            schedule = DoctorSchedule.objects.get(
                doctor=doctor,
                day_of_week=day_of_week,
                is_active=True
            )
        except DoctorSchedule.DoesNotExist:
            # No hay horario configurado para ese día
            return choices
        
        # Generar todas las franjas horarias posibles
        start = datetime.combine(date, schedule.start_time)
        end = datetime.combine(date, schedule.end_time)
        slot_duration = timedelta(minutes=schedule.slot_duration_minutes)
        
        time_slots = []
        current = start
        while current < end:
            time_slots.append(current.time())
            current += slot_duration
        
        # Obtener citas ya agendadas para ese doctor en esa fecha
        occupied_slots = Appointment.objects.filter(
            doctor_specialist__doctor=doctor,
            appointment_date=date,
            status__in=['scheduled', 'confirmed']
        ).values_list('appointment_time', flat=True)
        
        # Obtener bloqueos manuales para ese doctor en esa fecha
        blocked_slots = BlockTimeSlot.objects.filter(
            doctor=doctor,
            date=date,
            is_active=True
        ).values_list('blocked_time', flat=True)
        
        # Filtrar horarios disponibles
        for slot in time_slots:
            # Si es la hora actual de la cita (edición), siempre incluirla
            if current_time and slot == current_time:
                choices.append((slot.strftime('%H:%M:%S'), f"{slot.strftime('%H:%M')} (Actual)"))
            # Si el horario está ocupado o bloqueado, no mostrarlo
            elif slot in occupied_slots:
                continue
            elif slot in blocked_slots:
                continue
            else:
                choices.append((slot.strftime('%H:%M:%S'), slot.strftime('%H:%M')))
        
        return choices


# ============================================================================
# APPOINTMENT ADMIN
# ============================================================================
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Administración de citas."""
    form = AppointmentForm  # ← Usar formulario personalizado
    
    list_display = ('patient', 'get_doctor', 'appointment_date', 'appointment_time', 'status', 'created_at')
    list_filter = ('status', 'appointment_date', 'created_at')
    search_fields = ('patient__first_names', 'patient__last_names', 'doctor_specialist__doctor__first_names')
    readonly_fields = ('uuid', 'created_at', 'updated_at')
    date_hierarchy = 'appointment_date'
    
    def get_doctor(self, obj):
        """Muestra el doctor en el listado."""
        return obj.doctor_specialist.doctor.get_full_name()
    get_doctor.short_description = 'Doctor'
    
    fieldsets = (
        ('Identificación', {
            'fields': ('uuid',)
        }),
        ('Información de la Cita', {
            'fields': ('patient', 'doctor_specialist', 'appointment_date', 'appointment_time', 'duration_minutes'),
            'description': 'Nota: Los horarios disponibles se calculan automáticamente según la fecha y doctor seleccionados.'
        }),
        ('Estado', {
            'fields': ('status', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# DOCTOR SCHEDULE ADMIN
# ============================================================================
@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    """Administración de horarios de doctores."""
    list_display = ('doctor', 'day_of_week', 'start_time', 'end_time', 'slot_duration_minutes', 'is_active')
    list_filter = ('day_of_week', 'is_active', 'doctor')
    search_fields = ('doctor__first_names', 'doctor__last_names')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Doctor', {
            'fields': ('doctor',)
        }),
        ('Horario', {
            'fields': ('day_of_week', 'start_time', 'end_time', 'slot_duration_minutes', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# BLOCK TIME SLOT ADMIN
# ============================================================================
@admin.register(BlockTimeSlot)
class BlockTimeSlotAdmin(admin.ModelAdmin):
    """Administración de bloqueos de horarios."""
    list_display = ('doctor', 'date', 'blocked_time', 'reason', 'blocked_by_user', 'is_active')
    list_filter = ('is_active', 'date', 'doctor')
    search_fields = ('doctor__first_names', 'doctor__last_names', 'reason')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Bloqueo', {
            'fields': ('doctor', 'date', 'blocked_time', 'reason', 'blocked_by_user', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
