"""
Vistas (ViewSets) para el sistema de citas.
Endpoints de la API REST para gestionar citas, horarios y disponibilidad.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from .models import Appointment, DoctorSchedule, BlockTimeSlot
from .serializers import (
    AppointmentSerializer,
    AppointmentCreateSerializer,
    DoctorScheduleSerializer,
    BlockTimeSlotSerializer,
    AvailableSlotsSerializer
)
from doctors.models import Doctor
from users.permissions import IsAdministrador, IsPersonalMedico
from notifications.services import NotificationService
from notifications.email_service import EmailService


# ============================================================================
# APPOINTMENT VIEWSET
# ============================================================================
class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar citas médicas.
    
    Endpoints:
        GET    /api/appointments/              - Listar todas las citas (requiere auth)
        POST   /api/appointments/              - Crear nueva cita (PÚBLICO)
        GET    /api/appointments/{id}/         - Ver detalle de una cita (requiere auth)
        PUT    /api/appointments/{id}/         - Actualizar cita completa (requiere auth)
        PATCH  /api/appointments/{id}/         - Actualizar cita parcial (requiere auth)
        DELETE /api/appointments/{id}/         - Eliminar cita (requiere auth)
        GET    /api/appointments/{id}/cancel/  - Cancelar cita (requiere auth)
    """
    queryset = Appointment.objects.all().select_related(
        'patient',
        'doctor_specialist__doctor',
        'doctor_specialist__specialty'
    ).order_by('-appointment_date', '-appointment_time')
    
    def get_permissions(self):
        """
        Permisos personalizados por acción:
        - create: Público (sin autenticación) para formulario web
        - create_authenticated: Requiere auth (para doctora/admin)
        - destroy: Solo administrador
        - Resto: Requiere autenticación
        """
        if self.action == 'create':
            return []  # Sin permisos = público
        if self.action == 'destroy':
            return [IsAuthenticated(), IsAdministrador()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        """
        Usa serializer diferente para creación vs listado/detalle.
        """
        if self.action == 'create':
            return AppointmentCreateSerializer
        return AppointmentSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Sobrescribe create para retornar datos completos después de crear.
        Crea notificación automática para el doctor y envía email al paciente.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()
        
        # Crear notificación para el doctor
        try:
            NotificationService.notify_new_appointment(appointment)
        except Exception as e:
            # No fallar si la notificación falla
            pass
        
        # Enviar email de confirmación al paciente
        try:
            EmailService.send_appointment_confirmation(appointment)
        except Exception as e:
            # No fallar si el email falla
            pass
        
        # Usar AppointmentSerializer para la respuesta con todos los datos
        response_serializer = AppointmentSerializer(appointment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def get_queryset(self):
        """
        Filtra citas según el rol del usuario:
        - Administrador: Ve todas las citas
        - Doctor: Ve solo sus citas
        - Otros: Ve todas (se puede personalizar)
        """
        user = self.request.user
        queryset = super().get_queryset()
        
        # Si es doctor, mostrar solo sus citas
        if user.is_doctor:
            queryset = queryset.filter(doctor_specialist__doctor__user=user)
        
        # Filtros por query params
        patient_id = self.request.query_params.get('patient', None)
        doctor_id = self.request.query_params.get('doctor', None)
        date = self.request.query_params.get('date', None)
        status_filter = self.request.query_params.get('status', None)
        
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        if doctor_id:
            queryset = queryset.filter(doctor_specialist__doctor_id=doctor_id)
        
        if date:
            queryset = queryset.filter(appointment_date=date)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancela una cita cambiando su status a 'cancelled'.
        
        POST /api/appointments/{id}/cancel/
        
        Response:
            {
                "message": "Cita cancelada exitosamente",
                "appointment": {...}
            }
        """
        appointment = self.get_object()
        appointment.status = 'cancelled'
        appointment.save()
        
        # Crear notificación
        try:
            NotificationService.notify_appointment_cancelled(appointment)
        except:
            pass
        
        # Enviar email de cancelación al paciente
        try:
            EmailService.send_appointment_cancelled(appointment)
        except:
            pass
        
        serializer = self.get_serializer(appointment)
        return Response({
            'message': 'Cita cancelada exitosamente',
            'appointment': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Confirma una cita cambiando su status a 'confirmed'.
        
        POST /api/appointments/{id}/confirm/
        
        Response:
            {
                "message": "Cita confirmada exitosamente",
                "appointment": {...}
            }
        """
        appointment = self.get_object()
        appointment.status = 'confirmed'
        appointment.save()
        
        # Crear notificación
        try:
            NotificationService.notify_appointment_confirmed(appointment)
        except:
            pass
        
        serializer = self.get_serializer(appointment)
        return Response({
            'message': 'Cita confirmada exitosamente',
            'appointment': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Marca una cita como completada.
        
        POST /api/appointments/{id}/complete/
        """
        appointment = self.get_object()
        appointment.status = 'completed'
        appointment.save()
        
        serializer = self.get_serializer(appointment)
        return Response({
            'message': 'Cita completada exitosamente',
            'appointment': serializer.data
        })
    
    @action(detail=True, methods=['patch'], url_path='change-status')
    def change_status(self, request, pk=None):
        """
        Cambia el status de una cita.
        
        PATCH /api/appointments/{id}/change-status/
        Body: { "status": "confirmed" }
        
        Status válidos: scheduled, confirmed, in_progress, completed, cancelled, no_show
        """
        appointment = self.get_object()
        new_status = request.data.get('status')
        
        valid_statuses = ['scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show']
        
        if not new_status:
            return Response(
                {'error': 'El campo "status" es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Status inválido. Opciones: {", ".join(valid_statuses)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = new_status
        appointment.save()
        
        serializer = self.get_serializer(appointment)
        return Response({
            'message': f'Status cambiado a "{appointment.get_status_display()}"',
            'appointment': serializer.data
        })
    
    @action(detail=False, methods=['post'], url_path='create-authenticated')
    def create_authenticated(self, request):
        """
        Crea una cita desde el panel de la doctora/admin (requiere autenticación).
        Si es doctor, automáticamente usa su doctor_specialist.
        
        POST /api/appointments/create-authenticated/
        Body: {
            "patient": 1,
            "doctor_specialist": 1,  // Opcional si es doctor (usa el suyo)
            "appointment_date": "2025-11-25",
            "appointment_time": "10:00:00",
            "duration_minutes": 60,
            "notes": "Consulta de seguimiento"
        }
        """
        user = request.user
        data = request.data.copy()
        
        # Si es doctor y no envía doctor_specialist, usar el suyo automáticamente
        if hasattr(user, 'doctor_profile') and 'doctor_specialist' not in data:
            doctor = user.doctor_profile
            # Obtener la especialidad principal del doctor
            primary_specialty = doctor.specialties.filter(is_primary=True).first()
            if not primary_specialty:
                primary_specialty = doctor.specialties.first()
            
            if primary_specialty:
                data['doctor_specialist'] = primary_specialty.id
            else:
                return Response(
                    {'error': 'No tienes especialidades asignadas'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = AppointmentCreateSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()
        
        response_serializer = AppointmentSerializer(appointment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], url_path='my-calendar')
    def my_calendar(self, request):
        """
        Obtiene las citas del doctor logueado para el calendario.
        Optimizado para mostrar en vista semanal/mensual.
        
        GET /api/appointments/my-calendar/
        GET /api/appointments/my-calendar/?start_date=2025-11-10&end_date=2025-11-16
        
        Response:
            [
                {
                    "id": 1,
                    "title": "Consulta - Juan Pérez",
                    "start": "2025-11-10T09:00:00",
                    "end": "2025-11-10T10:00:00",
                    "patient_name": "Juan Pérez",
                    "patient_email": "juan@email.com",
                    "patient_phone": "0987654321",
                    "specialty": "Psicología Clínica",
                    "status": "scheduled",
                    "color": "#10b981",
                    "notes": ""
                },
                ...
            ]
        """
        user = request.user
        
        # Verificar que sea un doctor (usando el related_name correcto)
        if not hasattr(user, 'doctor_profile'):
            return Response(
                {'error': 'Este endpoint es solo para doctores. Tu usuario no tiene un perfil de doctor vinculado.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        doctor = user.doctor_profile
        
        # Filtrar por rango de fechas si se proporcionan
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = Appointment.objects.filter(
            doctor_specialist__doctor=doctor
        ).select_related(
            'patient',
            'doctor_specialist__specialty'
        ).order_by('appointment_date', 'appointment_time')
        
        if start_date:
            queryset = queryset.filter(appointment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(appointment_date__lte=end_date)
        
        # Colores según el status o tipo de cita
        status_colors = {
            'scheduled': '#10b981',   # Verde - Consulta
            'confirmed': '#3b82f6',   # Azul - Terapia
            'in_progress': '#f59e0b', # Amarillo
            'completed': '#6b7280',   # Gris
            'cancelled': '#ef4444',   # Rojo - Emergencia/Cancelada
            'no_show': '#dc2626',     # Rojo oscuro
        }
        
        # Formatear datos para el calendario
        calendar_events = []
        for appointment in queryset:
            # Calcular hora de fin
            start_datetime = datetime.combine(
                appointment.appointment_date,
                appointment.appointment_time
            )
            end_datetime = start_datetime + timedelta(minutes=appointment.duration_minutes)
            
            event = {
                'id': appointment.id,
                'uuid': str(appointment.uuid),
                'title': f"{appointment.doctor_specialist.specialty.name} - {appointment.patient.get_full_name()}",
                'start': start_datetime.isoformat(),
                'end': end_datetime.isoformat(),
                'patient_id': appointment.patient.id,
                'patient_name': appointment.patient.get_full_name(),
                'patient_email': appointment.patient.email,
                'patient_phone': appointment.patient.phone_number,
                'specialty': appointment.doctor_specialist.specialty.name,
                'status': appointment.status,
                'status_display': appointment.get_status_display(),
                'color': status_colors.get(appointment.status, '#10b981'),
                'duration_minutes': appointment.duration_minutes,
                'notes': appointment.notes or '',
            }
            calendar_events.append(event)
        
        return Response(calendar_events)


# ============================================================================
# DOCTOR SCHEDULE VIEWSET
# ============================================================================
class DoctorScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar horarios de doctores.
    
    Endpoints:
        GET    /api/schedules/                 - Listar todos los horarios
        POST   /api/schedules/                 - Crear nuevo horario
        GET    /api/schedules/{id}/            - Ver detalle de un horario
        PUT    /api/schedules/{id}/            - Actualizar horario completo
        PATCH  /api/schedules/{id}/            - Actualizar horario parcial
        DELETE /api/schedules/{id}/            - Eliminar horario
        GET    /api/schedules/by_doctor/{doctor_id}/ - Horarios de un doctor específico
    """
    queryset = DoctorSchedule.objects.all().select_related('doctor').order_by('doctor', 'day_of_week')
    serializer_class = DoctorScheduleSerializer
    permission_classes = [IsAuthenticated, IsPersonalMedico]
    
    def get_queryset(self):
        """
        Permite filtrar horarios por doctor.
        """
        queryset = super().get_queryset()
        doctor_id = self.request.query_params.get('doctor', None)
        
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        
        return queryset
    
    @action(detail=False, methods=['get'], url_path='by_doctor/(?P<doctor_id>[^/.]+)')
    def by_doctor(self, request, doctor_id=None):
        """
        Obtiene todos los horarios de un doctor específico.
        
        GET /api/schedules/by_doctor/{doctor_id}/
        
        Response:
            [
                {
                    "id": 1,
                    "day_of_week": 0,
                    "day_name": "Lunes",
                    "start_time": "09:00:00",
                    "end_time": "17:00:00",
                    "slot_duration_minutes": 60,
                    ...
                },
                ...
            ]
        """
        schedules = self.queryset.filter(doctor_id=doctor_id, is_active=True)
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)


# ============================================================================
# BLOCK TIME SLOT VIEWSET
# ============================================================================
class BlockTimeSlotViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar bloqueos de horarios.
    
    Endpoints:
        GET    /api/blocked-slots/             - Listar todos los bloqueos
        POST   /api/blocked-slots/             - Crear nuevo bloqueo
        GET    /api/blocked-slots/{id}/        - Ver detalle de un bloqueo
        PUT    /api/blocked-slots/{id}/        - Actualizar bloqueo completo
        PATCH  /api/blocked-slots/{id}/        - Actualizar bloqueo parcial
        DELETE /api/blocked-slots/{id}/        - Eliminar bloqueo
    """
    queryset = BlockTimeSlot.objects.all().select_related('doctor', 'blocked_by_user').order_by('-date', 'blocked_time')
    serializer_class = BlockTimeSlotSerializer
    permission_classes = [IsAuthenticated, IsPersonalMedico]
    
    def get_queryset(self):
        """
        Permite filtrar bloqueos por doctor y fecha.
        """
        queryset = super().get_queryset()
        doctor_id = self.request.query_params.get('doctor', None)
        date = self.request.query_params.get('date', None)
        
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        
        if date:
            queryset = queryset.filter(date=date)
        
        return queryset


# ============================================================================
# AVAILABLE SLOTS VIEWSET
# ============================================================================
class AvailableSlotsViewSet(viewsets.ViewSet):
    """
    ViewSet para consultar horarios disponibles.
    
    Endpoints:
        GET /api/available-slots/?doctor={doctor_id}&date={YYYY-MM-DD}
        
    Calcula y retorna los horarios disponibles considerando:
    - Horarios configurados (DoctorSchedule)
    - Citas ya agendadas (Appointments)
    - Bloqueos manuales (BlockTimeSlot)
    
    PÚBLICO: No requiere autenticación (para formulario público de citas)
    """
    permission_classes = []  # Sin autenticación = público
    
    def list(self, request):
        """
        Obtiene horarios disponibles para un doctor en una fecha específica.
        
        Query Parameters:
            - doctor (required): ID del doctor
            - date (required): Fecha en formato YYYY-MM-DD
        
        Example:
            GET /api/available-slots/?doctor=1&date=2025-11-20
        
        Response:
            {
                "date": "2025-11-20",
                "day_name": "Miércoles",
                "available_slots": ["09:00:00", "11:00:00", "13:00:00", "16:00:00"],
                "total_slots": 8,
                "available_count": 4,
                "occupied_count": 3,
                "blocked_count": 1
            }
        """
        # Validar parámetros requeridos
        doctor_id = request.query_params.get('doctor')
        date_str = request.query_params.get('date')
        
        if not doctor_id:
            return Response(
                {'error': 'El parámetro "doctor" es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not date_str:
            return Response(
                {'error': 'El parámetro "date" es requerido (formato: YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que el doctor exista
        doctor = get_object_or_404(Doctor, pk=doctor_id)
        
        # Parsear fecha
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
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
            return Response({
                'date': date_str,
                'day_name': date.strftime('%A'),
                'available_slots': [],
                'total_slots': 0,
                'available_count': 0,
                'occupied_count': 0,
                'blocked_count': 0,
                'message': f'El doctor no tiene horario configurado para {date.strftime("%A")}'
            })
        
        # Generar todas las franjas horarias posibles
        start_datetime = datetime.combine(date, schedule.start_time)
        end_datetime = datetime.combine(date, schedule.end_time)
        slot_duration = timedelta(minutes=schedule.slot_duration_minutes)
        
        all_slots = []
        current = start_datetime
        while current < end_datetime:
            all_slots.append(current.time())
            current += slot_duration
        
        total_slots = len(all_slots)
        
        # Obtener citas ya agendadas
        occupied_slots = set(
            Appointment.objects.filter(
                doctor_specialist__doctor=doctor,
                appointment_date=date,
                status__in=['scheduled', 'confirmed']
            ).values_list('appointment_time', flat=True)
        )
        
        # Obtener bloqueos manuales
        blocked_slots = set(
            BlockTimeSlot.objects.filter(
                doctor=doctor,
                date=date,
                is_active=True
            ).values_list('blocked_time', flat=True)
        )
        
        # Calcular horarios disponibles
        available_slots = [
            slot for slot in all_slots
            if slot not in occupied_slots and slot not in blocked_slots
        ]
        
        # Preparar respuesta
        response_data = {
            'date': date_str,
            'day_name': date.strftime('%A'),
            'available_slots': [slot.strftime('%H:%M:%S') for slot in available_slots],
            'total_slots': total_slots,
            'available_count': len(available_slots),
            'occupied_count': len(occupied_slots),
            'blocked_count': len(blocked_slots)
        }
        
        serializer = AvailableSlotsSerializer(data=response_data)
        serializer.is_valid()
        
        return Response(serializer.data)
