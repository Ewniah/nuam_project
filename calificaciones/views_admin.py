from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .models import CuentaBloqueada, LogAuditoria, IntentoLogin, PerfilUsuario
from .permissions import requiere_permiso
from .views import obtener_ip_cliente


# ==========================================
# VISTAS DE ADMINISTRACIÓN
# ==========================================

@login_required
@requiere_permiso('admin')
def admin_gestionar_usuarios(request):
    """
    Panel de gestión de usuarios para administradores.
    Muestra todos los usuarios con información de bloqueos e intentos de login.
    """
    # Obtener todos los usuarios con sus perfiles
    usuarios = User.objects.all().select_related('perfilusuario__rol').order_by('username')
    
    # Agregar información adicional a cada usuario
    for usuario in usuarios:
        # Verificar si tiene cuenta bloqueada
        usuario.cuenta_bloqueada = CuentaBloqueada.objects.filter(
            usuario=usuario,
            bloqueada=True
        ).first()
        
        # Contar intentos de login recientes (últimos 7 días)
        fecha_limite = timezone.now() - timedelta(days=7)
        usuario.intentos_recientes = IntentoLogin.objects.filter(
            username=usuario.username,
            fecha_hora__gte=fecha_limite
        ).count()
        
        # Contar intentos fallidos recientes
        usuario.intentos_fallidos_recientes = IntentoLogin.objects.filter(
            username=usuario.username,
            exitoso=False,
            fecha_hora__gte=fecha_limite
        ).count()
    
    context = {
        'usuarios': usuarios,
        'total_usuarios': usuarios.count(),
        'usuarios_bloqueados': sum(1 for u in usuarios if hasattr(u, 'cuenta_bloqueada') and u.cuenta_bloqueada),
    }
    
    return render(request, 'calificaciones/admin/gestionar_usuarios.html', context)


@login_required
@requiere_permiso('admin')
def desbloquear_cuenta_manual(request, user_id):
    """
    Desbloquea manualmente una cuenta de usuario.
    Registra la acción en LogAuditoria con ACCOUNT_UNLOCKED.
    """
    # Obtener el usuario a desbloquear
    user = get_object_or_404(User, id=user_id)
    
    # Buscar cuenta bloqueada
    cuenta_bloqueada = CuentaBloqueada.objects.filter(
        usuario=user,
        bloqueada=True
    ).first()
    
    if not cuenta_bloqueada:
        messages.warning(request, f'La cuenta de {user.username} no está bloqueada.')
        return redirect('admin_gestionar_usuarios')
    
    # Desbloquear la cuenta
    cuenta_bloqueada.bloqueada = False
    cuenta_bloqueada.fecha_desbloqueo = timezone.now()
    cuenta_bloqueada.save()
    
    # Registrar en auditoría (CRÍTICO - Feedback del profesor)
    ip_address = obtener_ip_cliente(request)
    LogAuditoria.objects.create(
        usuario=request.user,  # Admin que desbloqueó
        accion='ACCOUNT_UNLOCKED',
        tabla_afectada='CuentaBloqueada',
        registro_id=cuenta_bloqueada.id,
        ip_address=ip_address,
        detalles=f'Cuenta de {user.username} desbloqueada manualmente por {request.user.username}'
    )
    
    messages.success(
        request,
        f'✅ Cuenta de {user.username} desbloqueada exitosamente.'
    )
    
    return redirect('admin_gestionar_usuarios')


@login_required
@requiere_permiso('admin')
def ver_historial_login_usuario(request, user_id):
    """
    Muestra el historial completo de intentos de login de un usuario.
    """
    user = get_object_or_404(User, id=user_id)
    
    # Obtener todos los intentos de login del usuario
    intentos = IntentoLogin.objects.filter(
        username=user.username
    ).order_by('-fecha_hora')[:50]  # Últimos 50 intentos
    
    # Obtener logs de auditoría relacionados con login
    logs_login = LogAuditoria.objects.filter(
        usuario=user,
        accion__in=['LOGIN', 'LOGOUT', 'ACCOUNT_LOCKED', 'ACCOUNT_UNLOCKED']
    ).order_by('-fecha_hora')[:50]
    
    context = {
        'usuario': user,
        'intentos': intentos,
        'logs_login': logs_login,
    }
    
    return render(request, 'calificaciones/admin/historial_login.html', context)
