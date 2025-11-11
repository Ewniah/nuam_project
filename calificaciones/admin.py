"""
admin.py - Configuración del panel de administración de Django
"""

from django.contrib import admin
from .models import (
    Rol, 
    PerfilUsuario, 
    InstrumentoFinanciero, 
    CalificacionTributaria,
    LogAuditoria,
    CargaMasiva
)

# Función de formato para el admin
def formato_clp(valor, decimales=2):
    """Formatea números con separador de miles (punto) y decimales (coma)"""
    if valor is None:
        return "-"
    s = f"{valor:,.{decimales}f}"
    return "$ " + s.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")

def formato_factor_admin(valor, decimales=8):
    """Formatea factores con 8 decimales"""
    if valor is None:
        return "-"
    s = f"{valor:,.{decimales}f}"
    return s.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    """Panel admin para Roles"""
    list_display = ['nombre_rol', 'descripcion']
    search_fields = ['nombre_rol']


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    """Panel admin para Perfiles de Usuario"""
    list_display = ['usuario', 'rol', 'departamento', 'telefono']
    list_filter = ['rol', 'departamento']
    search_fields = ['usuario__username', 'usuario__email']


@admin.register(InstrumentoFinanciero)
class InstrumentoFinancieroAdmin(admin.ModelAdmin):
    """Panel admin para Instrumentos Financieros"""
    list_display = ['codigo_instrumento', 'nombre_instrumento', 'tipo_instrumento', 'activo', 'fecha_creacion']
    list_filter = ['tipo_instrumento', 'activo']
    search_fields = ['codigo_instrumento', 'nombre_instrumento']
    ordering = ['codigo_instrumento']


@admin.register(CalificacionTributaria)
class CalificacionTributariaAdmin(admin.ModelAdmin):
    """Panel admin para Calificaciones Tributarias"""
    list_display = [
        'id', 
        'instrumento', 
        'mostrar_monto', 
        'mostrar_factor', 
        'metodo_ingreso',
        'numero_dj',
        'fecha_informe', 
        'usuario_creador',
        'activo'
    ]
    list_filter = ['metodo_ingreso', 'numero_dj', 'activo', 'fecha_informe']
    search_fields = ['instrumento__codigo_instrumento', 'numero_dj', 'observaciones']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion', 'usuario_creador']
    ordering = ['-fecha_creacion']
    
    fieldsets = (
        ('Información del Instrumento', {
            'fields': ('instrumento', 'numero_dj')
        }),
        ('Calificación Tributaria', {
            'fields': ('metodo_ingreso', 'monto', 'factor', 'fecha_informe')
        }),
        ('Información Adicional', {
            'fields': ('observaciones', 'activo')
        }),
        ('Auditoría', {
            'fields': ('usuario_creador', 'fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Asigna automáticamente el usuario creador"""
        if not obj.pk:
            obj.usuario_creador = request.user
        super().save_model(request, obj, form, change)
    
    def mostrar_monto(self, obj):
        """Muestra el monto formateado en CLP"""
        return formato_clp(obj.monto, 2)
    mostrar_monto.short_description = "Monto"
    mostrar_monto.admin_order_field = "monto"
    
    def mostrar_factor(self, obj):
        """Muestra el factor formateado con 8 decimales"""
        return formato_factor_admin(obj.factor, 8)
    mostrar_factor.short_description = "Factor"
    mostrar_factor.admin_order_field = "factor"


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    """Panel admin para Logs de Auditoría (solo lectura)"""
    list_display = ['fecha_hora', 'usuario', 'accion', 'tabla_afectada', 'registro_id', 'ip_address']
    list_filter = ['accion', 'tabla_afectada', 'fecha_hora']
    search_fields = ['usuario__username', 'detalles']
    readonly_fields = [
        'usuario', 'accion', 'tabla_afectada', 'registro_id', 
        'fecha_hora', 'ip_address', 'detalles'
    ]
    ordering = ['-fecha_hora']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CargaMasiva)
class CargaMasivaAdmin(admin.ModelAdmin):
    """Panel admin para Cargas Masivas"""
    list_display = [
        'archivo_nombre', 
        'usuario', 
        'fecha_carga', 
        'estado',
        'registros_procesados',
        'registros_exitosos',
        'registros_fallidos'
    ]
    list_filter = ['estado', 'fecha_carga']
    search_fields = ['archivo_nombre', 'usuario__username']
    readonly_fields = [
        'fecha_carga', 'registros_procesados', 
        'registros_exitosos', 'registros_fallidos', 'errores_detalle'
    ]
    ordering = ['-fecha_carga']
