"""
Signals para logging automático de todas las operaciones
"""

from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import CalificacionTributaria, InstrumentoFinanciero, LogAuditoria


def obtener_ip(request):
    """Obtiene la IP del usuario desde el request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Logging para Calificaciones Tributarias
@receiver(post_save, sender=CalificacionTributaria)
def log_calificacion_save(sender, instance, created, **kwargs):
    """Registra creación/modificación de calificaciones"""
    # Saltar si se llama desde una vista (la vista registrará manualmente con usuario e IP)
    # Solo registrar si no hay contexto de usuario (guardados automáticos, migraciones, etc.)
    import inspect
    frame = inspect.currentframe()
    caller_locals = frame.f_back.f_locals if frame.f_back else {}
    
    # Saltar si 'request' está en el contexto del llamador (significa que es una vista llamando save)
    if 'request' in caller_locals:
        return
    
    accion = 'CREATE' if created else 'UPDATE'
    LogAuditoria.objects.create(
        usuario=instance.usuario_creador,
        accion=accion,
        tabla_afectada='CalificacionTributaria',
        registro_id=instance.id,
        detalles=f"Instrumento: {instance.instrumento.codigo_instrumento}, Monto: {instance.monto}, Factor: {instance.factor} [Sistema]"
    )


@receiver(pre_delete, sender=CalificacionTributaria)
def log_calificacion_delete(sender, instance, **kwargs):
    """Registra eliminación de calificaciones"""
    # Saltar si se llama desde una vista (la vista registrará manualmente)
    import inspect
    frame = inspect.currentframe()
    caller_locals = frame.f_back.f_locals if frame.f_back else {}
    
    if 'request' in caller_locals:
        return
    
    LogAuditoria.objects.create(
        usuario=instance.usuario_creador,
        accion='DELETE',
        tabla_afectada='CalificacionTributaria',
        registro_id=instance.id,
        detalles=f"Eliminado: {instance.instrumento.codigo_instrumento} [Sistema]"
    )


# Logging para Instrumentos Financieros
@receiver(post_save, sender=InstrumentoFinanciero)
def log_instrumento_save(sender, instance, created, **kwargs):
    """Registra creación/modificación de instrumentos"""
    # Saltar si se llama desde una vista (la vista registrará manualmente con usuario)
    # Solo registrar si no hay contexto de usuario (guardados automáticos, migraciones, etc.)
    import inspect
    frame = inspect.currentframe()
    caller_locals = frame.f_back.f_locals if frame.f_back else {}
    
    # Saltar si 'request' está en el contexto del llamador (significa que es una vista llamando save)
    if 'request' in caller_locals:
        return
    
    accion = 'CREATE' if created else 'UPDATE'
    LogAuditoria.objects.create(
        accion=accion,
        tabla_afectada='InstrumentoFinanciero',
        registro_id=instance.id,
        detalles=f"Código: {instance.codigo_instrumento}, Tipo: {instance.tipo_instrumento} [Sistema]"
    )


# Logging de login/logout
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Registra inicio de sesión"""
    LogAuditoria.objects.create(
        usuario=user,
        accion='LOGIN',
        tabla_afectada='User',
        ip_address=obtener_ip(request),
        detalles=f"Inicio de sesión exitoso"
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Registra cierre de sesión"""
    if user:
        LogAuditoria.objects.create(
            usuario=user,
            accion='LOGOUT',
            tabla_afectada='User',
            ip_address=obtener_ip(request),
            detalles=f"Cierre de sesión"
        )
