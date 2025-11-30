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
# Lines: 151-350 (approx. 200 lines)
# ============================================================================

# [Functions will be migrated here in Step 5]


# ============================================================================
# SECTION 3: DASHBOARD AND REPORTING
# ============================================================================
# Functions: dashboard
# Lines: 351-500 (approx. 150 lines)
# ============================================================================

# [Functions will be migrated here in Step 6]


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
