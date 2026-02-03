from django.contrib import admin
from .models import BusinessInfo, Product


@admin.register(BusinessInfo)
class BusinessInfoAdmin(admin.ModelAdmin):
    """
    Administración de información del negocio.
    """
    list_display = ['ruc', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['ruc']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('ruc', 'is_active')
        }),
        ('Información de Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Permitir crear solo si no existe ningún registro activo."""
        return not BusinessInfo.objects.filter(is_active=True).exists()
    
    def has_delete_permission(self, request, obj=None):
        """Permitir eliminar."""
        return True 
    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Administración de productos/servicios.
    """
    list_display = ['description', 'code', 'unit_price', 'created_at']
    search_fields = ['description', 'code']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Detalles del Producto/Servicio', {
            'fields': ('description', 'code', 'unit_price')
        }),
        ('Información de Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )