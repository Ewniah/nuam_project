"""
Signals para logging automático de operaciones del sistema.

DISEÑO DE AUDITORÍA (Post E2 Fix):
- Los signals SOLO registran operaciones automáticas del sistema (migraciones, scripts, etc.)
- Las operaciones de usuario WEB son registradas directamente por las vistas
- Middleware ContextoAuditoriaMiddleware detecta si hay request activo
- Si hay_contexto_usuario() = True → SKIP (vista registrará con IP)
- Si hay_contexto_usuario() = False → REGISTRAR como [Sistema]

Beneficios:
✓ Atribución singular: 1 log por operación
✓ IP siempre capturada en logs de usuario
✓ Separación clara: Sistema vs Usuario
✓ No más inspección de frames (frágil)
"""

from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import CalificacionTributaria, InstrumentoFinanciero, LogAuditoria
from .middleware import hay_contexto_usuario


def obtener_ip(request):
    """
    Obtiene la dirección IP del usuario desde el request.
    
    Args:
        request: HttpRequest de Django
        
    Returns:
        str: Dirección IP del cliente
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# =============================================================================
# SIGNALS DE AUDITORÍA - OPERACIONES DEL SISTEMA
# =============================================================================
# Estos signals SOLO se ejecutan cuando NO hay un request de usuario activo.
# Las operaciones web de usuario son auditadas directamente por las vistas.
# =============================================================================

@receiver(post_save, sender=CalificacionTributaria)
def log_calificacion_save(sender, instance, created, **kwargs):
    """
    Registra creación/modificación de calificaciones SOLO para operaciones del sistema.
    
    Skip si hay_contexto_usuario() = True (operación web, vista registrará).
    Registra con etiqueta [Sistema] si operación automática (migración, script, etc.).
    
    Args:
        sender: Clase del modelo (CalificacionTributaria)
        instance: Instancia guardada
        created: True si es creación, False si es actualización
        **kwargs: Argumentos adicionales del signal
    """
    # CRITICAL: Skip si hay request activo (operación de usuario web)
    if hay_contexto_usuario():
        return
    
    # Solo llegamos aquí si es operación del sistema (sin request)
    accion = 'CREATE' if created else 'UPDATE'
    LogAuditoria.objects.create(
        usuario=instance.usuario_creador,
        accion=accion,
        tabla_afectada='CalificacionTributaria',
        registro_id=instance.id,
        ip_address=None,  # No hay IP en operaciones del sistema
        detalles=f"Instrumento: {instance.instrumento.codigo_instrumento}, Monto: {instance.monto}, Factor: {instance.factor} [Sistema]"
    )


@receiver(pre_delete, sender=CalificacionTributaria)
def log_calificacion_delete(sender, instance, **kwargs):
    """
    Registra eliminación de calificaciones SOLO para operaciones del sistema.
    
    Skip si hay_contexto_usuario() = True (operación web, vista registrará).
    
    Args:
        sender: Clase del modelo (CalificacionTributaria)
        instance: Instancia a eliminar
        **kwargs: Argumentos adicionales del signal
    """
    # CRITICAL: Skip si hay request activo (operación de usuario web)
    if hay_contexto_usuario():
        return
    
    # Solo llegamos aquí si es operación del sistema (sin request)
    LogAuditoria.objects.create(
        usuario=instance.usuario_creador,
        accion='DELETE',
        tabla_afectada='CalificacionTributaria',
        registro_id=instance.id,
        ip_address=None,  # No hay IP en operaciones del sistema
        detalles=f"Eliminado: {instance.instrumento.codigo_instrumento} [Sistema]"
    )


@receiver(post_save, sender=InstrumentoFinanciero)
def log_instrumento_save(sender, instance, created, **kwargs):
    """
    Registra creación/modificación de instrumentos SOLO para operaciones del sistema.
    
    Skip si hay_contexto_usuario() = True (operación web, vista registrará).
    Registra con etiqueta [Sistema] si operación automática.
    
    NOTA: InstrumentoFinanciero no tiene campo usuario_creador, por eso
    el log queda con usuario=None para operaciones del sistema.
    
    Args:
        sender: Clase del modelo (InstrumentoFinanciero)
        instance: Instancia guardada
        created: True si es creación, False si es actualización
        **kwargs: Argumentos adicionales del signal
    """
    # CRITICAL: Skip si hay request activo (operación de usuario web)
    if hay_contexto_usuario():
        return
    
    # Solo llegamos aquí si es operación del sistema (sin request)
    accion = 'CREATE' if created else 'UPDATE'
    LogAuditoria.objects.create(
        usuario=None,  # Sistema automático, no hay usuario asociado
        accion=accion,
        tabla_afectada='InstrumentoFinanciero',
        registro_id=instance.id,
        ip_address=None,  # No hay IP en operaciones del sistema
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
