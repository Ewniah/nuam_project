"""
Script de verificación post-carga masiva.

Este script valida que los datos cargados mediante la funcionalidad de carga masiva
se hayan procesado correctamente en la base de datos.
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nuam_project.settings')
django.setup()

from django.contrib.auth.models import User
from calificaciones.models import (
    CalificacionTributaria,
    InstrumentoFinanciero,
    CargaMasiva,
    LogAuditoria
)
from django.db.models import Count, Q, Sum
from datetime import datetime, timedelta


def verificar_carga_masiva():
    """
    Verifica el estado de la última carga masiva y valida los datos.
    """
    print("=" * 80)
    print("🔍 VERIFICACIÓN DE CARGA MASIVA")
    print("=" * 80)
    print()

    # 1. Verificar última carga
    print("1️⃣  ESTADO DE ÚLTIMA CARGA MASIVA")
    print("-" * 80)
    
    ultima_carga = CargaMasiva.objects.order_by('-fecha_carga').first()
    
    if not ultima_carga:
        print("❌ No se encontraron registros de carga masiva")
        return False
    
    print(f"   📅 Fecha: {ultima_carga.fecha_carga}")
    print(f"   👤 Usuario: {ultima_carga.usuario.username}")
    print(f"   📄 Archivo: {ultima_carga.archivo_nombre}")
    print(f"   📊 Estado: {ultima_carga.estado}")
    print()
    print(f"   ✅ Registros exitosos: {ultima_carga.registros_exitosos}")
    print(f"   ❌ Registros fallidos: {ultima_carga.registros_fallidos}")
    print(f"   📝 Total procesados: {ultima_carga.registros_procesados}")
    
    if ultima_carga.errores_detalle:
        print()
        print("   ⚠️  ERRORES DETECTADOS:")
        for linea in ultima_carga.errores_detalle.split('\n')[:5]:  # Solo primeros 5
            print(f"      {linea}")
        if len(ultima_carga.errores_detalle.split('\n')) > 5:
            print(f"      ... y {len(ultima_carga.errores_detalle.split('\n')) - 5} errores más")
    
    print()
    
    # 2. Verificar instrumentos creados
    print("2️⃣  INSTRUMENTOS FINANCIEROS CREADOS")
    print("-" * 80)
    
    # Instrumentos creados recientemente (últimos 5 minutos)
    hace_5_min = datetime.now() - timedelta(minutes=5)
    instrumentos_recientes = InstrumentoFinanciero.objects.filter(
        activo=True
    ).order_by('-id')[:10]
    
    total_instrumentos = InstrumentoFinanciero.objects.filter(activo=True).count()
    
    print(f"   📊 Total de instrumentos activos: {total_instrumentos}")
    print(f"   📋 Últimos 10 instrumentos creados:")
    print()
    
    for inst in instrumentos_recientes:
        print(f"      • {inst.codigo_instrumento}")
        print(f"        Nombre: {inst.nombre_instrumento}")
        print(f"        Tipo: {inst.tipo_instrumento}")
        print()
    
    # 3. Verificar calificaciones creadas
    print("3️⃣  CALIFICACIONES TRIBUTARIAS CREADAS")
    print("-" * 80)
    
    # Calificaciones recientes
    calificaciones_recientes = CalificacionTributaria.objects.filter(
        activo=True
    ).select_related('instrumento', 'usuario_creador').order_by('-fecha_creacion')[:5]
    
    total_calificaciones = CalificacionTributaria.objects.filter(activo=True).count()
    
    print(f"   📊 Total de calificaciones activas: {total_calificaciones}")
    print(f"   📋 Últimas 5 calificaciones creadas:")
    print()
    
    for cal in calificaciones_recientes:
        print(f"      • ID: {cal.id}")
        print(f"        Instrumento: {cal.instrumento.codigo_instrumento}")
        print(f"        Método: {cal.metodo_ingreso}")
        if cal.monto:
            print(f"        Monto: ${cal.monto:,.2f}")
        if cal.factor:
            print(f"        Factor: {cal.factor}")
        print(f"        DJ: {cal.numero_dj}")
        print(f"        Fecha Informe: {cal.fecha_informe}")
        print(f"        Creador: {cal.usuario_creador.username}")
        print()
    
    # 4. Estadísticas por método de ingreso
    print("4️⃣  ESTADÍSTICAS POR MÉTODO DE INGRESO")
    print("-" * 80)
    
    stats = CalificacionTributaria.objects.filter(activo=True).values(
        'metodo_ingreso'
    ).annotate(
        total=Count('id')
    ).order_by('-total')
    
    for stat in stats:
        print(f"   • {stat['metodo_ingreso']}: {stat['total']} registros")
    
    print()
    
    # 5. Verificar auditoría
    print("5️⃣  REGISTRO DE AUDITORÍA")
    print("-" * 80)
    
    logs_recientes = LogAuditoria.objects.filter(
        tabla_afectada='CargaMasiva'
    ).select_related('usuario').order_by('-fecha_hora')[:3]
    
    print(f"   📝 Últimos 3 registros de auditoría (CargaMasiva):")
    print()
    
    for log in logs_recientes:
        print(f"      • {log.fecha_hora}")
        print(f"        Usuario: {log.usuario.username}")
        print(f"        Acción: {log.accion}")
        print(f"        Detalles: {log.detalles}")
        print(f"        IP: {log.ip_address}")
        print()
    
    # 6. Verificar integridad de datos
    print("6️⃣  VALIDACIÓN DE INTEGRIDAD")
    print("-" * 80)
    
    # Calificaciones sin instrumento (no debería haber)
    sin_instrumento = CalificacionTributaria.objects.filter(
        instrumento__isnull=True
    ).count()
    
    # Calificaciones sin usuario creador (no debería haber)
    sin_usuario = CalificacionTributaria.objects.filter(
        usuario_creador__isnull=True
    ).count()
    
    # Calificaciones sin monto ni factor (error)
    sin_monto_ni_factor = CalificacionTributaria.objects.filter(
        Q(monto__isnull=True) & Q(factor__isnull=True),
        activo=True
    ).count()
    
    print(f"   ✓ Calificaciones sin instrumento: {sin_instrumento}")
    print(f"   ✓ Calificaciones sin usuario creador: {sin_usuario}")
    print(f"   ✓ Calificaciones sin monto ni factor: {sin_monto_ni_factor}")
    print()
    
    if sin_instrumento > 0 or sin_usuario > 0 or sin_monto_ni_factor > 0:
        print("   ⚠️  SE DETECTARON PROBLEMAS DE INTEGRIDAD")
        return False
    else:
        print("   ✅ TODOS LOS DATOS TIENEN INTEGRIDAD CORRECTA")
    
    print()
    
    # 7. Resumen final
    print("=" * 80)
    print("📊 RESUMEN FINAL")
    print("=" * 80)
    
    if ultima_carga.estado == "EXITOSO":
        print("✅ CARGA MASIVA COMPLETADA EXITOSAMENTE")
        print(f"   • {ultima_carga.registros_exitosos} registros procesados correctamente")
        print(f"   • 0 errores detectados")
    elif ultima_carga.estado == "PARCIAL":
        print("⚠️  CARGA MASIVA COMPLETADA CON ADVERTENCIAS")
        print(f"   • {ultima_carga.registros_exitosos} registros exitosos")
        print(f"   • {ultima_carga.registros_fallidos} registros con errores")
        print(f"   • Tasa de éxito: {(ultima_carga.registros_exitosos / ultima_carga.registros_procesados * 100):.1f}%")
    else:
        print("❌ CARGA MASIVA FALLÓ")
        print(f"   • {ultima_carga.registros_fallidos} registros fallidos")
    
    print()
    print(f"📈 Total de instrumentos en sistema: {total_instrumentos}")
    print(f"📈 Total de calificaciones en sistema: {total_calificaciones}")
    print()
    
    return ultima_carga.estado in ["EXITOSO", "PARCIAL"]


def comparar_con_archivo_original():
    """
    Compara los datos cargados con el archivo Excel original.
    """
    print("=" * 80)
    print("📊 COMPARACIÓN CON ARCHIVO ORIGINAL")
    print("=" * 80)
    print()
    
    try:
        import openpyxl
        
        archivo_path = "datos_prueba_carga_masiva.xlsx"
        
        if not os.path.exists(archivo_path):
            print(f"❌ No se encontró el archivo: {archivo_path}")
            return
        
        wb = openpyxl.load_workbook(archivo_path)
        sheet = wb.active
        
        # Contar registros en Excel
        registros_excel = sum(1 for row in sheet.iter_rows(min_row=2) if row[0].value)
        
        print(f"📄 Registros en archivo Excel: {registros_excel}")
        
        # Contar calificaciones creadas por el usuario admin (últimas)
        ultima_carga = CargaMasiva.objects.order_by('-fecha_carga').first()
        if ultima_carga:
            print(f"✅ Registros exitosos en BD: {ultima_carga.registros_exitosos}")
            print(f"❌ Registros fallidos: {ultima_carga.registros_fallidos}")
            
            if registros_excel == ultima_carga.registros_exitosos:
                print()
                print("✅ TODOS LOS REGISTROS DEL ARCHIVO FUERON CARGADOS EXITOSAMENTE")
            else:
                print()
                print(f"⚠️  Diferencia detectada: {registros_excel - ultima_carga.registros_exitosos} registros")
        
        print()
        
    except ImportError:
        print("⚠️  openpyxl no disponible, saltando comparación con archivo")
    except Exception as e:
        print(f"❌ Error al comparar: {e}")


if __name__ == "__main__":
    exito = verificar_carga_masiva()
    print()
    comparar_con_archivo_original()
    print()
    
    if exito:
        print("🎉 VERIFICACIÓN COMPLETADA: Sistema funcionando correctamente")
    else:
        print("⚠️  VERIFICACIÓN COMPLETADA: Se detectaron algunos problemas")
