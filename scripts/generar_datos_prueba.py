"""
Script maestro de generación de datos de prueba para NUAM Calificaciones.
Genera archivos Excel con 30 factores tributarios (8-37) para testing de carga masiva.
Consolidado: v2.0 - Diciembre 2025
"""

import os
import sys
from datetime import datetime, timedelta, date
from decimal import Decimal
import random

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nuam_project.settings')
import django
django.setup()

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from calificaciones.models import InstrumentoFinanciero


def crear_instrumento_bd(codigo, nombre, tipo):
    """Crea instrumento en BD si no existe."""
    inst, created = InstrumentoFinanciero.objects.get_or_create(
        codigo_instrumento=codigo,
        defaults={'nombre_instrumento': nombre, 'tipo_instrumento': tipo, 'activo': True}
    )
    return inst


def generar_excel_prueba():
    """
    Genera archivo Excel con 30 factores tributarios completos (8-37).
    Incluye 3 escenarios: Golden, Range Failure, Sum Failure.
    """
    print(f"\n{'='*70}")
    print("GENERANDO ARCHIVO DE PRUEBA MAESTRO")
    print(f"{'='*70}\n")
    
    # Crear workbook
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = "Test 30 Factores"

    # Headers dinámicos: metadata + 30 factores + observaciones
    headers = [
        "codigo_instrumento",
        "fecha_informe",
        "origen",
        "mercado",
        "tipo_sociedad",
        "secuencia",
        "numero_dividendo",
        "ejercicio",
        "numero_dj",
    ]
    
    # Agregar 30 factores (8-37)
    for i in range(8, 38):
        headers.append(f"factor_{i}")
    
    headers.append("observaciones")

    # Formato de headers
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=10)
    
    sheet.append(headers)
    for cell in sheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    
    # Ajustar anchos de columna
    for col_num in range(1, len(headers) + 1):
        col_letter = get_column_letter(col_num)
        if col_num <= 9:  # Metadata
            sheet.column_dimensions[col_letter].width = 14
        elif col_num <= 39:  # Factores
            sheet.column_dimensions[col_letter].width = 11
        else:  # Observaciones
            sheet.column_dimensions[col_letter].width = 40
    
    # ESCENARIO 1: Golden Record (Válido)
    row1 = ['TEST-GOLD', '2025-12-01', 'BOLSA', 'ACN', 'A', 1, 0, 2025, 'DJ1949']
    for i in range(30):
        row1.append(0.01)  # Factores válidos
    row1.append('Escenario 1: Golden - Todos los factores válidos')
    sheet.append(row1)
    
    # ESCENARIO 2: Range Failure (factor_37 = 5.0)
    row2 = ['TEST-RANGE-FAIL', '2025-12-01', 'CORREDORA', 'BVS', 'C', 2, 1, 2025, 'DJ1922']
    for i in range(8, 38):
        row2.append(5.0 if i == 37 else 0.01)  # factor_37 inválido
    row2.append('Escenario 2: Range Failure - factor_37 = 5.0 (debe fallar)')
    sheet.append(row2)
    
    # ESCENARIO 3: Sum Failure (suma 8-16 > 1.0)
    row3 = ['TEST-SUM-FAIL', '2025-12-01', 'MANUAL', 'ACN', 'A', 3, 2, 2025, 'DJ1949']
    for i in range(8, 38):
        row3.append(0.2 if 8 <= i <= 16 else 0.01)  # Suma 8-16 = 1.8
    row3.append('Escenario 3: Sum Failure - Suma factores 8-16 > 1.0 (debe fallar)')
    sheet.append(row3)
    
    # Guardar archivo
    filename = "datos_prueba_30factores.xlsx"
    filepath = os.path.join(os.path.dirname(__file__), filename)
    wb.save(filepath)
    
    print(f"✅ Archivo generado: {filename}")
    print(f"📊 Total registros: 3 (1 válido, 2 inválidos)")
    print(f"📁 Ubicación: {filepath}")
    print("\nRESULTADOS ESPERADOS:")
    print("  ✓ Fila 2: GOLDEN - Éxito (1 registro)")
    print("  ✗ Fila 3: RANGE FAIL - Error rango (factor_37 = 5.0)")
    print("  ✗ Fila 4: SUM FAIL - Error suma (factores 8-16 > 1.0)")
    print("\nESTADÍSTICAS ESPERADAS:")
    print("  - Procesados: 3")
    print("  - Exitosos: 1")
    print("  - Fallidos: 2")
    print("  - Estado: PARCIAL")


def preparar_instrumentos():
    """Crea instrumentos de prueba en BD."""
    print("\n📦 Preparando instrumentos de prueba...")
    instrumentos = [
        ('TEST-GOLD', 'Instrumento Golden Test', 'Bono'),
        ('TEST-RANGE-FAIL', 'Instrumento Range Failure', 'Acción'),
        ('TEST-SUM-FAIL', 'Instrumento Sum Failure', 'Fondo'),
    ]
    for codigo, nombre, tipo in instrumentos:
        crear_instrumento_bd(codigo, nombre, tipo)
    print("✓ Instrumentos creados/verificados\n")


if __name__ == "__main__":
    print(f"\n{'#'*70}")
    print("#  SCRIPT MAESTRO DE GENERACIÓN DE DATOS DE PRUEBA")
    print(f"#  Fecha: {date.today()}")
    print(f"#  Versión: 2.0 Consolidado")
    print(f"{'#'*70}")
    
    preparar_instrumentos()
    generar_excel_prueba()
    
    print(f"\n{'='*70}")
    print("✅ PROCESO COMPLETADO")
    print(f"{'='*70}\n")
