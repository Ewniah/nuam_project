"""
Unified View Module for NUAM Calificaciones System
Consolidated from: views.py, views_admin.py, views_factores.py
Migration Date: 2025-11-30
Task: 1.3 - View Unification
Total Functions: 30 (22 routed + 6 utilities + 2 helpers)
Total Routes: 22 (100% preserved)
"""

# ============================================================================
# IMPORTS - PEP 8 Organized
# ============================================================================

# Standard Library (5 imports)
import csv
import io
import json
from datetime import datetime, timedelta
from decimal import Decimal

# Django Core (9 imports)
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

# Third-Party (1 import)
import openpyxl

# Local Application (4 imports)
from .forms import (
    CalificacionTributariaForm, InstrumentoFinancieroForm, CargaMasivaForm,
    RegistroForm, CalificacionFactoresSimpleForm
)
from .models import (
    CalificacionTributaria, InstrumentoFinanciero, LogAuditoria, 
    CargaMasiva, Rol, PerfilUsuario, IntentoLogin, CuentaBloqueada, ArchivoCargado
)
from .permissions import requiere_permiso
from .utils.calculadora_factores import calcular_clasificacion_sii


# ============================================================================
# SECTION 1: UTILITIES AND HELPERS
# ============================================================================
# Functions: obtener_ip_cliente, verificar_cuenta_bloqueada, 
#            registrar_intento_login, verificar_intentos_fallidos,
#            procesar_excel, procesar_csv
# Lines: 52-250 (approx. 200 lines)
# ============================================================================

def obtener_ip_cliente(request):
    """Obtiene la IP real del cliente considerando proxies"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def verificar_cuenta_bloqueada(username):
    """
    Verifica si una cuenta está bloqueada
    Retorna: (bloqueada: bool, mensaje: str, minutos_restantes: int)
    """
    try:
        user = User.objects.get(username=username)
        cuenta_bloqueada = CuentaBloqueada.objects.filter(usuario=user, bloqueada=True).first()
        
        if cuenta_bloqueada:
            # Verificar si ya pasó el tiempo de bloqueo (30 minutos)
            tiempo_bloqueo = timezone.now() - cuenta_bloqueada.fecha_bloqueo
            MINUTOS_BLOQUEO = 30
            
            if tiempo_bloqueo.total_seconds() < MINUTOS_BLOQUEO * 60:
                minutos_restantes = int((MINUTOS_BLOQUEO * 60 - tiempo_bloqueo.total_seconds()) / 60)
                return True, f"Cuenta bloqueada. Intente nuevamente en {minutos_restantes} minutos.", minutos_restantes
            else:
                # ✅ ACTUALIZADO: Desbloquear automáticamente y registrar en auditoría
                cuenta_bloqueada.bloqueada = False
                cuenta_bloqueada.fecha_desbloqueo = timezone.now()
                cuenta_bloqueada.save()
                
                # Registrar desbloqueo automático en auditoría
                LogAuditoria.objects.create(
                    usuario=user,
                    accion='ACCOUNT_UNLOCKED',
                    tabla_afectada='CuentaBloqueada',
                    registro_id=cuenta_bloqueada.id,
                    ip_address='SYSTEM',  # Sistema automático
                    detalles=f'Cuenta de {user.username} desbloqueada automáticamente después de 30 minutos'
                )
                
                return False, "", 0
        
        return False, "", 0
    except User.DoesNotExist:
        return False, "", 0


def registrar_intento_login(username, ip_address, exitoso, detalles=""):
    """Registra todos los intentos de login en la base de datos"""
    IntentoLogin.objects.create(
        username=username,
        ip_address=ip_address,
        exitoso=exitoso,
        detalles=detalles
    )


def verificar_intentos_fallidos(username, ip_address):
    """
    Verifica intentos fallidos en los últimos 15 minutos
    Si hay 5 o más intentos fallidos, bloquea la cuenta
    Retorna: (debe_bloquear: bool, intentos: int)
    """
    INTENTOS_MAXIMOS = 5
    VENTANA_TIEMPO = 15  # minutos
    
    tiempo_limite = timezone.now() - timedelta(minutes=VENTANA_TIEMPO)
    
    # Contar intentos fallidos recientes
    intentos_fallidos = IntentoLogin.objects.filter(
        username=username,
        exitoso=False,
        fecha_hora__gte=tiempo_limite
    ).count()
    
    if intentos_fallidos >= INTENTOS_MAXIMOS:
        try:
            user = User.objects.get(username=username)
            
            # Crear o actualizar registro de cuenta bloqueada
            cuenta_bloqueada, created = CuentaBloqueada.objects.get_or_create(
                usuario=user,
                defaults={
                    'intentos_fallidos': intentos_fallidos,
                    'bloqueada': True,
                    'razon': f'Bloqueada automáticamente por {intentos_fallidos} intentos fallidos'
                }
            )
            
            if not created:
                cuenta_bloqueada.bloqueada = True
                cuenta_bloqueada.intentos_fallidos = intentos_fallidos
                cuenta_bloqueada.fecha_bloqueo = timezone.now()
                cuenta_bloqueada.save()
            
            # Registrar en auditoría
            LogAuditoria.objects.create(
                usuario=user,
                accion='ACCOUNT_LOCKED',
                tabla_afectada='CuentaBloqueada',
                registro_id=cuenta_bloqueada.id,
                ip_address=ip_address,
                detalles=f'Cuenta bloqueada por {intentos_fallidos} intentos fallidos'
            )
            
            return True, intentos_fallidos
        except User.DoesNotExist:
            pass
    
    return False, intentos_fallidos


def procesar_excel(archivo):
    """Procesa archivo Excel y retorna lista de registros"""
    wb = openpyxl.load_workbook(archivo)
    sheet = wb.active
    registros = []
    
    headers = [cell.value for cell in sheet[1]]
    
    for row in sheet.iter_rows(min_row=2, values_only=True):
        registro = dict(zip(headers, row))
        if registro.get('codigo_instrumento'):
            registros.append(registro)
    
    return registros


def procesar_csv(archivo):
    """Procesa archivo CSV y retorna lista de registros"""
    contenido = archivo.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(contenido))
    return list(reader)


# ============================================================================
# SECTION 2: AUTHENTICATION AND SECURITY
# ============================================================================
# Functions: login_view, logout_view
# Lines: 251-370 (approx. 120 lines)
# ============================================================================

def login_view(request):
    """Vista de login con auditoría completa y sistema de bloqueo"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        ip_address = obtener_ip_cliente(request)
        
        # 1. Verificar si la cuenta está bloqueada
        bloqueada, mensaje_bloqueo, minutos = verificar_cuenta_bloqueada(username)
        if bloqueada:
            messages.error(request, mensaje_bloqueo)
            registrar_intento_login(username, ip_address, False, "Intento en cuenta bloqueada")
            return render(request, 'registration/login.html')
        
        # 2. Intentar autenticar
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login exitoso
            login(request, user)
            
            # Registrar intento exitoso
            registrar_intento_login(username, ip_address, True, "Login exitoso")
            
            # Registrar en auditoría
            LogAuditoria.objects.create(
                usuario=user,
                accion='LOGIN',
                tabla_afectada='User',
                registro_id=user.id,
                ip_address=ip_address,
                detalles=f'Login exitoso desde {ip_address}'
            )
            
            # Limpiar bloqueo si existía
            CuentaBloqueada.objects.filter(usuario=user).update(
                bloqueada=False,
                intentos_fallidos=0,
                fecha_desbloqueo=timezone.now()
            )
            
            messages.success(request, f'¡Bienvenido {user.first_name or user.username}!')
            return redirect('dashboard')
        else:
            # Login fallido
            registrar_intento_login(username, ip_address, False, "Credenciales incorrectas")
            
            # Registrar en auditoría (sin usuario porque falló)
            LogAuditoria.objects.create(
                usuario=None,
                accion='LOGIN_FAILED',
                tabla_afectada='User',
                ip_address=ip_address,
                detalles=f'Intento fallido para usuario: {username}'
            )
            
            # Verificar si debe bloquearse la cuenta
            debe_bloquear, intentos = verificar_intentos_fallidos(username, ip_address)
            
            if debe_bloquear:
                messages.error(
                    request, 
                    f'Cuenta bloqueada por múltiples intentos fallidos. '
                    f'Intente nuevamente en 30 minutos.'
                )
            else:
                intentos_restantes = 5 - intentos
                if intentos_restantes <= 2:
                    messages.warning(
                        request, 
                        f'Credenciales incorrectas. Le quedan {intentos_restantes} intentos '
                        f'antes de que su cuenta sea bloqueada.'
                    )
                else:
                    messages.error(request, 'Credenciales incorrectas. Intente nuevamente.')
    
    return render(request, 'registration/login.html')


@login_required
def logout_view(request):
    """Cierra sesión y registra en auditoría"""
    ip_address = obtener_ip_cliente(request)
    
    LogAuditoria.objects.create(
        usuario=request.user,
        accion='LOGOUT',
        tabla_afectada='User',
        registro_id=request.user.id,
        ip_address=ip_address,
        detalles=f'Logout desde {ip_address}'
    )
    
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('login')


# ============================================================================
# SECTION 3: DASHBOARD AND REPORTING
# ============================================================================
# Functions: dashboard
# Lines: 371-470 (approx. 100 lines)
# ============================================================================

@login_required
@requiere_permiso('consultar')
def dashboard(request):
    """Dashboard principal con estadísticas del sistema"""
    from datetime import datetime
    
    # Mensaje de bienvenida según hora del día
    hora_actual = datetime.now().hour
    if hora_actual < 12:
        saludo = "Buenos días"
        icono_saludo = "☀️"
    elif hora_actual < 19:
        saludo = "Buenas tardes"
        icono_saludo = "🌤️"
    else:
        saludo = "Buenas noches"
        icono_saludo = "🌙"
    
    # Estadísticas generales
    total_calificaciones = CalificacionTributaria.objects.filter(activo=True).count()
    total_instrumentos = InstrumentoFinanciero.objects.filter(activo=True).count()
    total_usuarios = User.objects.filter(is_active=True).count()
    
    # Calificaciones por método
    calificaciones_por_metodo = list(
        CalificacionTributaria.objects.filter(activo=True)
        .values('metodo_ingreso')
        .annotate(total=Count('id'))
    )
    
    # Instrumentos por tipo
    instrumentos_por_tipo = list(
        InstrumentoFinanciero.objects.filter(activo=True)
        .values('tipo_instrumento')
        .annotate(total=Count('id'))
    )
    
    # Actividad reciente (últimos 30 días)
    fecha_limite = datetime.now().date() - timedelta(days=30)
    calificaciones_recientes_30d = CalificacionTributaria.objects.filter(
        activo=True,
        fecha_creacion__gte=fecha_limite
    ).count()
    
    # ✅ CORRECCIÓN: Usar el mismo nombre que en el template
    calificaciones_recientes = CalificacionTributaria.objects.filter(
        activo=True
    ).select_related('instrumento', 'usuario_creador').order_by('-fecha_creacion')[:5]
    
    # Logs de auditoría recientes (solo para admin y auditor)
    logs_recientes = None
    try:
        if request.user.is_superuser:
            logs_recientes = LogAuditoria.objects.all().order_by('-fecha_hora')[:5]
        elif hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.rol:
            if request.user.perfilusuario.rol.nombre_rol in ['Administrador', 'Auditor']:
                logs_recientes = LogAuditoria.objects.all().order_by('-fecha_hora')[:5]
    except:
        logs_recientes = None
    
    # Top 5 instrumentos más utilizados
    top_instrumentos = list(
        CalificacionTributaria.objects.filter(activo=True)
        .values(
            'instrumento__codigo_instrumento',
            'instrumento__nombre_instrumento'
        )
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )
    
    # Estadísticas de cargas masivas
    cargas_exitosas = CargaMasiva.objects.filter(estado='EXITOSO').count()
    cargas_fallidas = CargaMasiva.objects.filter(estado='FALLIDO').count()
    
    context = {
        'total_calificaciones': total_calificaciones,
        'total_instrumentos': total_instrumentos,
        'total_usuarios': total_usuarios,
        'calificaciones_recientes_30d': calificaciones_recientes_30d,
        'calificaciones_por_metodo': calificaciones_por_metodo,
        'instrumentos_por_tipo': instrumentos_por_tipo,
        'calificaciones_recientes': calificaciones_recientes,  # ✅ Nombre correcto
        'logs_recientes': logs_recientes,
        'top_instrumentos': top_instrumentos,
        'today': datetime.now(),
        'saludo': saludo,
        'icono_saludo': icono_saludo,
        'cargas_exitosas': cargas_exitosas,
        'cargas_fallidas': cargas_fallidas,
    }
    
    return render(request, 'calificaciones/dashboard.html', context)


# ============================================================================
# SECTION 4: CALIFICACIONES CRUD OPERATIONS
# ============================================================================
# Functions: listar_calificaciones, crear_calificacion, editar_calificacion,
#            eliminar_calificacion, crear_calificacion_factores,
#            editar_calificacion_factores
# Lines: 501-850 (approx. 350 lines)
# ============================================================================

# [Functions will be migrated here in Steps 7-8]


# ============================================================================
# SECTION 5: INSTRUMENTOS CRUD OPERATIONS
# ============================================================================
# Functions: listar_instrumentos, crear_instrumento, editar_instrumento,
#            eliminar_instrumento
# Lines: 851-1050 (approx. 200 lines)
# ============================================================================

# [Functions will be migrated here in Step 9]


# ============================================================================
# SECTION 6: BULK OPERATIONS
# ============================================================================
# Functions: carga_masiva, exportar_excel, exportar_csv
# Lines: 1051-1300 (approx. 250 lines)
# ============================================================================

# [Functions will be migrated here in Step 10]


# ============================================================================
# SECTION 7: USER MANAGEMENT
# ============================================================================
# Functions: mi_perfil, registro, admin_gestionar_usuarios,
#            desbloquear_cuenta_manual, ver_historial_login_usuario
# Lines: 1301-1550 (approx. 250 lines)
# ============================================================================

# [Functions will be migrated here in Steps 11-12]


# ============================================================================
# SECTION 8: AUDITING AND COMPLIANCE
# ============================================================================
# Functions: registro_auditoria
# Lines: 1551-1650 (approx. 100 lines)
# ============================================================================

# [Functions will be migrated here in Step 13]


# ============================================================================
# SECTION 9: API ENDPOINTS AND MISCELLANEOUS
# ============================================================================
# Functions: calcular_factores_ajax, home
# Lines: 1651-1750 (approx. 100 lines)
# ============================================================================

# [Functions will be migrated here in Step 13]
