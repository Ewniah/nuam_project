from django.contrib import admin
from .models import (
    Rol, 
    PerfilUsuario, 
    InstrumentoFinanciero, 
    CalificacionTributaria, 
    LogAuditoria, 
    CargaMasiva,
    IntentoLogin,
    CuentaBloqueada
)


def formato_clp(valor, decimales=2):
    """Formatea números con separador de miles (punto) y decimales (coma)"""
    if valor is None:
        return '-'
    s = f'{valor:,.{decimales}f}'
    return s.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')


def formato_factor(valor, decimales=8):
    """Formatea factores con 8 decimales"""
    if valor is None:
        return '-'
    s = f'{valor:,.{decimales}f}'
    return s.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    """Panel admin para Roles"""
    list_display = ('nombre_rol', 'descripcion')
    search_fields = ('nombre_rol',)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    """Panel admin para Perfiles de Usuario"""
    list_display = ('usuario', 'rol', 'departamento', 'telefono')
    list_filter = ('rol', 'departamento')
    search_fields = ('usuario__username', 'usuario__email')


@admin.register(InstrumentoFinanciero)
class InstrumentoFinancieroAdmin(admin.ModelAdmin):
    """Panel admin para Instrumentos Financieros"""
    list_display = ('codigo_instrumento', 'nombre_instrumento', 'tipo_instrumento', 'activo', 'fecha_creacion')
    list_filter = ('tipo_instrumento', 'activo')
    search_fields = ('codigo_instrumento', 'nombre_instrumento')
    date_hierarchy = 'fecha_creacion'


@admin.register(CalificacionTributaria)
class CalificacionTributariaAdmin(admin.ModelAdmin):
    """Panel admin para Calificaciones Tributarias con JavaScript dinámico"""
    
    list_display = (
        'id', 
        'get_codigo_instrumento', 
        'get_monto_formateado', 
        'get_factor_formateado',
        'metodo_ingreso',
        'numero_dj',
        'fecha_informe',
        'activo'
    )
    
    list_filter = ('metodo_ingreso', 'numero_dj', 'activo', 'fecha_informe')
    search_fields = ('instrumento__codigo_instrumento', 'instrumento__nombre_instrumento', 'numero_dj')
    date_hierarchy = 'fecha_creacion'
    
    fieldsets = (
        ('Información del Instrumento', {
            'fields': ('instrumento', 'usuario_creador')
        }),
        ('Método de Calificación', {
            'fields': ('metodo_ingreso',),
            'description': 'Seleccione el método de ingreso. Los campos se habilitarán automáticamente.'
        }),
        ('Valores de Calificación', {
            'fields': ('monto', 'factor'),
            'classes': ('wide',),
        }),
        ('Información DJ y Fechas', {
            'fields': ('numero_dj', 'fecha_informe', 'observaciones'),
        }),
        ('Estado', {
            'fields': ('activo',),
        }),
    )
    
    readonly_fields = ('usuario_creador',)
    
    def get_codigo_instrumento(self, obj):
        return obj.instrumento.codigo_instrumento
    get_codigo_instrumento.short_description = 'Código Instrumento'
    
    def get_monto_formateado(self, obj):
        return formato_clp(obj.monto, 4)
    get_monto_formateado.short_description = 'Monto'
    
    def get_factor_formateado(self, obj):
        return formato_factor(obj.factor, 8)
    get_factor_formateado.short_description = 'Factor'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es creación
            obj.usuario_creador = request.user
        super().save_model(request, obj, form, change)
    
    class Media:
        js = ('js/admin_calificacion.js',)


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    """Panel admin para Logs de Auditoría (solo lectura)"""
    list_display = ('fecha_hora', 'usuario', 'accion', 'tabla_afectada', 'registro_id', 'ip_address')
    list_filter = ('accion', 'tabla_afectada', 'fecha_hora')
    search_fields = ('usuario__username', 'tabla_afectada', 'detalles', 'ip_address')
    date_hierarchy = 'fecha_hora'
    
    # Solo lectura - no permitir modificar logs
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CargaMasiva)
class CargaMasivaAdmin(admin.ModelAdmin):
    """Panel admin para Cargas Masivas"""
    list_display = ('archivo_nombre', 'usuario', 'fecha_carga', 'estado', 'registros_procesados', 'registros_exitosos', 'registros_fallidos')
    list_filter = ('estado', 'fecha_carga')
    search_fields = ('archivo_nombre', 'usuario__username')
    date_hierarchy = 'fecha_carga'
    readonly_fields = ('fecha_carga', 'registros_procesados', 'registros_exitosos', 'registros_fallidos', 'errores_detalle')


# Nuevo: Admin para IntentoLogin
@admin.register(IntentoLogin)
class IntentoLoginAdmin(admin.ModelAdmin):
    """Panel admin para Intentos de Login (solo lectura)"""
    list_display = ('fecha_hora', 'username', 'ip_address', 'exitoso', 'detalles')
    list_filter = ('exitoso', 'fecha_hora')
    search_fields = ('username', 'ip_address', 'detalles')
    date_hierarchy = 'fecha_hora'
    
    # Solo lectura
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Solo superusuarios pueden eliminar (para limpieza de datos antiguos)
        return request.user.is_superuser


# Nuevo: Admin para CuentaBloqueada
@admin.register(CuentaBloqueada)
class CuentaBloqueadaAdmin(admin.ModelAdmin):
    """Panel admin para Cuentas Bloqueadas"""
    list_display = ('usuario', 'bloqueada', 'intentos_fallidos', 'fecha_bloqueo', 'fecha_desbloqueo')
    list_filter = ('bloqueada', 'fecha_bloqueo')
    search_fields = ('usuario__username', 'usuario__email', 'razon')
    date_hierarchy = 'fecha_bloqueo'
    
    readonly_fields = ('fecha_bloqueo', 'intentos_fallidos')
    
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Estado del Bloqueo', {
            'fields': ('bloqueada', 'intentos_fallidos', 'fecha_bloqueo', 'fecha_desbloqueo'),
        }),
        ('Detalles', {
            'fields': ('razon',),
        }),
    )

    # Registrar desbloqueos en auditoría cuando se realiza manualmente
    def save_model(self, request, obj, form, change):
        """Registra el desbloqueo en auditoría"""
        # Verificar si se está desbloqueando
        if change and 'bloqueada' in form.changed_data:
            # Si cambió de bloqueada=True a bloqueada=False
            if not obj.bloqueada:
                # Obtener IP del admin
                from .views import obtener_ip_cliente
                ip_address = obtener_ip_cliente(request)
                
                # Actualizar fecha de desbloqueo
                from django.utils import timezone
                obj.fecha_desbloqueo = timezone.now()
                
                # Registrar en auditoría
                LogAuditoria.objects.create(
                    usuario=request.user,  # Admin que desbloqueó
                    accion='ACCOUNT_UNLOCKED',
                    tabla_afectada='CuentaBloqueada',
                    registro_id=obj.id,
                    ip_address=ip_address,
                    detalles=f'Cuenta de {obj.usuario.username} desbloqueada manualmente por {request.user.username}'
                )
        
        super().save_model(request, obj, form, change)