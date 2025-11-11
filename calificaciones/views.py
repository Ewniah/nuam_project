"""
Vistas para el sistema de calificaciones tributarias
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.http import HttpResponse
from .models import CalificacionTributaria, InstrumentoFinanciero, CargaMasiva, LogAuditoria
from .forms import CalificacionTributariaForm, InstrumentoFinancieroForm, CargaMasivaForm
from .permissions import (
    requiere_administrador,
    requiere_analista_o_admin,
    requiere_permiso_lectura,
)
import pandas as pd
import io
import csv
from datetime import datetime, timedelta
from decimal import Decimal
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# ==================== DASHBOARD ====================

@login_required
def dashboard(request):
    """Vista principal del sistema con estadísticas completas"""
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
    calificaciones_por_metodo = list(CalificacionTributaria.objects.filter(activo=True).values('metodo_ingreso').annotate(
        total=Count('id')
    ))
    
    # Instrumentos por tipo
    instrumentos_por_tipo = list(InstrumentoFinanciero.objects.filter(activo=True).values('tipo_instrumento').annotate(
        total=Count('id')
    ))
    
    # Actividad reciente (últimos 30 días)
    fecha_limite = datetime.now().date() - timedelta(days=30)
    calificaciones_recientes_30d = CalificacionTributaria.objects.filter(
        activo=True,
        fecha_creacion__gte=fecha_limite
    ).count()
    
    # Calificaciones recientes para la tabla
    calificaciones_recientes = CalificacionTributaria.objects.filter(activo=True).order_by('-fecha_creacion')[:5]
    
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
    top_instrumentos = list(CalificacionTributaria.objects.filter(activo=True).values(
        'instrumento__codigo_instrumento',
        'instrumento__nombre_instrumento'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:5])
    
    context = {
        'total_calificaciones': total_calificaciones,
        'total_instrumentos': total_instrumentos,
        'total_usuarios': total_usuarios,
        'calificaciones_recientes_30d': calificaciones_recientes_30d,
        'calificaciones_por_metodo': calificaciones_por_metodo,
        'instrumentos_por_tipo': instrumentos_por_tipo,
        'calificaciones_recientes': calificaciones_recientes,
        'logs_recientes': logs_recientes,
        'top_instrumentos': top_instrumentos,
        'today': datetime.now(),
        'saludo': saludo,
        'icono_saludo': icono_saludo,
    }
    return render(request, 'calificaciones/dashboard.html', context)



# ==================== CALIFICACIONES CRUD ====================

@requiere_permiso_lectura
def listar_calificaciones(request):
    """Lista todas las calificaciones con filtros y paginación"""
    query = request.GET.get('q', '')
    metodo = request.GET.get('metodo', '')
    dj = request.GET.get('dj', '')
    
    calificaciones = CalificacionTributaria.objects.filter(activo=True)
    
    # Filtro por búsqueda de texto
    if query:
        calificaciones = calificaciones.filter(
            Q(instrumento__codigo_instrumento__icontains=query) |
            Q(instrumento__nombre_instrumento__icontains=query) |
            Q(numero_dj__icontains=query)
        )
    
    # Filtro por método
    if metodo:
        calificaciones = calificaciones.filter(metodo_ingreso=metodo)
    
    # Filtro por DJ
    if dj:
        calificaciones = calificaciones.filter(numero_dj=dj)
    
    calificaciones = calificaciones.order_by('-fecha_creacion')
    
    # Paginación: 15 registros por página
    paginator = Paginator(calificaciones, 15)
    page = request.GET.get('page')
    
    try:
        calificaciones_page = paginator.page(page)
    except PageNotAnInteger:
        calificaciones_page = paginator.page(1)
    except EmptyPage:
        calificaciones_page = paginator.page(paginator.num_pages)
    
    context = {
        'calificaciones': calificaciones_page,
        'query': query,
    }
    return render(request, 'calificaciones/listar_calificaciones.html', context)


@requiere_analista_o_admin
def crear_calificacion(request):
    """Crear nueva calificación - Solo Analista o Admin"""
    if request.method == 'POST':
        form = CalificacionTributariaForm(request.POST)
        if form.is_valid():
            calificacion = form.save(commit=False)
            calificacion.usuario_creador = request.user
            calificacion.save()
            messages.success(request, 'Calificación tributaria creada exitosamente.')
            return redirect('listar_calificaciones')
    else:
        form = CalificacionTributariaForm()
    
    return render(request, 'calificaciones/form_calificacion.html', {
        'form': form,
        'titulo': 'Crear Calificación Tributaria'
    })


@requiere_analista_o_admin
def editar_calificacion(request, pk):
    """Editar calificación - Solo Analista o Admin"""
    calificacion = get_object_or_404(CalificacionTributaria, pk=pk)
    
    if request.method == 'POST':
        form = CalificacionTributariaForm(request.POST, instance=calificacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Calificación actualizada exitosamente.')
            return redirect('listar_calificaciones')
    else:
        form = CalificacionTributariaForm(instance=calificacion)
    
    return render(request, 'calificaciones/form_calificacion.html', {
        'form': form,
        'titulo': 'Editar Calificación Tributaria',
        'calificacion': calificacion
    })


@requiere_administrador
def eliminar_calificacion(request, pk):
    """Eliminar calificación - Solo Administrador"""
    calificacion = get_object_or_404(CalificacionTributaria, pk=pk)
    
    if request.method == 'POST':
        calificacion.activo = False
        calificacion.save()
        messages.success(request, 'Calificación eliminada exitosamente.')
        return redirect('listar_calificaciones')
    
    return render(request, 'calificaciones/confirmar_eliminar.html', {
        'objeto': calificacion,
        'tipo': 'Calificación Tributaria'
    })


# ==================== INSTRUMENTOS CRUD ====================

@requiere_permiso_lectura
def listar_instrumentos(request):
    """Lista todos los instrumentos - Todos pueden ver"""
    instrumentos = InstrumentoFinanciero.objects.filter(activo=True).order_by('codigo_instrumento')
    return render(request, 'calificaciones/listar_instrumentos.html', {'instrumentos': instrumentos})


@requiere_administrador
def crear_instrumento(request):
    """Crear nuevo instrumento - Solo Administrador"""
    if request.method == 'POST':
        form = InstrumentoFinancieroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Instrumento financiero creado exitosamente.')
            return redirect('listar_instrumentos')
    else:
        form = InstrumentoFinancieroForm()
    
    return render(request, 'calificaciones/form_instrumento.html', {
        'form': form,
        'titulo': 'Crear Instrumento Financiero'
    })


@requiere_administrador
def editar_instrumento(request, pk):
    """Editar instrumento - Solo Administrador"""
    instrumento = get_object_or_404(InstrumentoFinanciero, pk=pk)
    
    if request.method == 'POST':
        form = InstrumentoFinancieroForm(request.POST, instance=instrumento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Instrumento actualizado exitosamente.')
            return redirect('listar_instrumentos')
    else:
        form = InstrumentoFinancieroForm(instance=instrumento)
    
    return render(request, 'calificaciones/form_instrumento.html', {
        'form': form,
        'titulo': 'Editar Instrumento Financiero',
        'instrumento': instrumento
    })


# ==================== CARGA MASIVA ====================

@requiere_analista_o_admin
def carga_masiva(request):
    """Vista para carga masiva - Solo Analista o Admin"""
    if request.method == 'POST':
        form = CargaMasivaForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo']
            
            # Crear registro de carga
            carga = CargaMasiva.objects.create(
                usuario=request.user,
                archivo_nombre=archivo.name,
                archivo=archivo,
                estado='PROCESANDO'
            )
            
            try:
                # IMPORTANTE: Reiniciar el puntero del archivo
                archivo.seek(0)
                
                # Leer el contenido del archivo
                contenido = archivo.read()
                
                # Leer archivo según extensión
                if archivo.name.endswith('.csv'):
                    # Intentar diferentes codificaciones
                    try:
                        contenido_str = contenido.decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            contenido_str = contenido.decode('latin-1')
                        except:
                            contenido_str = contenido.decode('iso-8859-1')
                    
                    df = pd.read_csv(io.StringIO(contenido_str))
                    
                elif archivo.name.endswith('.xlsx'):
                    df = pd.read_excel(io.BytesIO(contenido), engine='openpyxl')
                else:
                    raise Exception("Formato de archivo no soportado. Use CSV o XLSX")
                
                # Verificar que el DataFrame tiene columnas
                if df.empty or len(df.columns) == 0:
                    raise Exception("El archivo está vacío o no tiene columnas válidas")
                
                # Limpiar nombres de columnas
                df.columns = df.columns.str.strip()
                
                exitosos = 0
                fallidos = 0
                errores = []
                
                # Procesar cada fila
                for index, row in df.iterrows():
                    try:
                        # Buscar instrumento
                        codigo = str(row['codigo_instrumento']).strip()
                        instrumento = InstrumentoFinanciero.objects.get(
                            codigo_instrumento=codigo
                        )
                        
                        # Obtener método de ingreso
                        metodo = str(row.get('metodo_ingreso', 'MONTO')).strip().upper()
                        
                        # Obtener monto y factor
                        monto = row.get('monto')
                        factor = row.get('factor')
                        
                        # Convertir a None si están vacíos, sino a Decimal
                        if pd.isna(monto) or str(monto).strip() == '':
                            monto = None
                        else:
                            monto = Decimal(str(monto))
                        
                        if pd.isna(factor) or str(factor).strip() == '':
                            factor = None
                        else:
                            factor = Decimal(str(factor))
                        
                        # Crear calificación
                        CalificacionTributaria.objects.create(
                            instrumento=instrumento,
                            usuario_creador=request.user,
                            metodo_ingreso=metodo,
                            monto=monto,
                            factor=factor,
                            numero_dj=str(row.get('numero_dj', '')).strip(),
                            fecha_informe=pd.to_datetime(row['fecha_informe']).date(),
                            observaciones=str(row.get('observaciones', '')).strip()
                        )
                        exitosos += 1
                        
                    except InstrumentoFinanciero.DoesNotExist:
                        fallidos += 1
                        errores.append(f"Fila {index + 2}: Instrumento '{codigo}' no encontrado")
                    except KeyError as e:
                        fallidos += 1
                        errores.append(f"Fila {index + 2}: Columna faltante - {str(e)}")
                    except Exception as e:
                        fallidos += 1
                        errores.append(f"Fila {index + 2}: {str(e)}")
                
                # Actualizar registro de carga
                carga.registros_procesados = len(df)
                carga.registros_exitosos = exitosos
                carga.registros_fallidos = fallidos
                carga.errores_detalle = '\n'.join(errores) if errores else ''
                carga.estado = 'EXITOSO' if fallidos == 0 else ('PARCIAL' if exitosos > 0 else 'FALLIDO')
                carga.save()
                
                if exitosos > 0:
                    messages.success(request, f'Carga completada: {exitosos} exitosos, {fallidos} fallidos.')
                else:
                    messages.warning(request, f'No se pudo procesar ningún registro. {fallidos} fallidos.')
                    
                if errores:
                    messages.warning(request, f'Errores encontrados: {len(errores)}. Revise el detalle en el historial.')
                
                return redirect('listar_calificaciones')
                
            except Exception as e:
                carga.estado = 'FALLIDO'
                carga.errores_detalle = str(e)
                carga.save()
                messages.error(request, f'Error al procesar archivo: {str(e)}')
    else:
        form = CargaMasivaForm()
    
    # Listar cargas anteriores
    cargas_anteriores = CargaMasiva.objects.filter(usuario=request.user).order_by('-fecha_carga')[:10]
    
    return render(request, 'calificaciones/carga_masiva.html', {
        'form': form,
        'cargas_anteriores': cargas_anteriores
    })


# ==================== EXPORTACIÓN DE REPORTES ====================

@login_required
def exportar_calificaciones_excel(request):
    """Exporta calificaciones a Excel con formato profesional"""
    
    # Obtener filtros de búsqueda si existen
    query = request.GET.get('q', '')
    calificaciones = CalificacionTributaria.objects.filter(activo=True)
    
    if query:
        calificaciones = calificaciones.filter(
            Q(instrumento__codigo_instrumento__icontains=query) |
            Q(instrumento__nombre_instrumento__icontains=query) |
            Q(numero_dj__icontains=query)
        )
    
    calificaciones = calificaciones.order_by('-fecha_creacion')
    
    # Crear workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Calificaciones Tributarias"
    
    # Estilos
    header_fill = PatternFill(start_color="0066CC", end_color="0066CC", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True, size=12)
    
    # Encabezados
    headers = ['ID', 'Instrumento', 'Tipo', 'Monto (CLP)', 'Factor', 'Método', 'DJ', 'Fecha Informe', 'Usuario', 'Observaciones']
    ws.append(headers)
    
    # Aplicar estilo a encabezados
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Agregar datos
    for cal in calificaciones:
        # Formatear monto y factor
        monto_str = f"${cal.monto:,.2f}".replace(",", "TEMP").replace(".", ",").replace("TEMP", ".") if cal.monto else "-"
        factor_str = f"{cal.factor:,.8f}".replace(",", "TEMP").replace(".", ",").replace("TEMP", ".") if cal.factor else "-"
        
        ws.append([
            cal.id,
            cal.instrumento.codigo_instrumento,
            cal.instrumento.tipo_instrumento,
            monto_str,
            factor_str,
            cal.get_metodo_ingreso_display(),
            cal.numero_dj,
            cal.fecha_informe.strftime('%d/%m/%Y'),
            cal.usuario_creador.username,
            cal.observaciones or ""
        ])
    
    # Ajustar ancho de columnas
    for col_num in range(1, len(headers) + 1):
        column_letter = get_column_letter(col_num)
        ws.column_dimensions[column_letter].width = 15
    
    # Columna de observaciones más ancha
    ws.column_dimensions['J'].width = 30
    
    # Preparar respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f'calificaciones_tributarias_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    wb.save(response)
    return response


@login_required
def exportar_calificaciones_csv(request):
    """Exporta calificaciones a CSV"""
    
    # Obtener filtros de búsqueda si existen
    query = request.GET.get('q', '')
    calificaciones = CalificacionTributaria.objects.filter(activo=True)
    
    if query:
        calificaciones = calificaciones.filter(
            Q(instrumento__codigo_instrumento__icontains=query) |
            Q(instrumento__nombre_instrumento__icontains=query) |
            Q(numero_dj__icontains=query)
        )
    
    calificaciones = calificaciones.order_by('-fecha_creacion')
    
    # Crear respuesta CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    filename = f'calificaciones_tributarias_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    # Escribir BOM para Excel en español
    response.write('\ufeff')
    
    writer = csv.writer(response)
    
    # Encabezados
    writer.writerow(['ID', 'Instrumento', 'Tipo', 'Monto (CLP)', 'Factor', 'Método', 'DJ', 'Fecha Informe', 'Usuario', 'Observaciones'])
    
    # Datos
    for cal in calificaciones:
        monto_str = f"{cal.monto:.2f}" if cal.monto else ""
        factor_str = f"{cal.factor:.8f}" if cal.factor else ""
        
        writer.writerow([
            cal.id,
            cal.instrumento.codigo_instrumento,
            cal.instrumento.tipo_instrumento,
            monto_str,
            factor_str,
            cal.get_metodo_ingreso_display(),
            cal.numero_dj,
            cal.fecha_informe.strftime('%d/%m/%Y'),
            cal.usuario_creador.username,
            cal.observaciones or ""
        ])
    
    return response

# ==================== CREACIÓN DE PERFIL DEL USUARIO ====================

@login_required
def mi_perfil(request):
    """Vista del perfil del usuario"""
    from django.contrib.auth.models import User
    
    # Obtener el perfil del usuario
    try:
        perfil = request.user.perfilusuario
    except:
        perfil = None
    
    # Estadísticas del usuario
    calificaciones_creadas = CalificacionTributaria.objects.filter(
        usuario_creador=request.user,
        activo=True
    ).count()
    
    ultimas_calificaciones = CalificacionTributaria.objects.filter(
        usuario_creador=request.user,
        activo=True
    ).order_by('-fecha_creacion')[:5]
    
    # Logs de actividad del usuario
    logs_usuario = LogAuditoria.objects.filter(
        usuario=request.user
    ).order_by('-fecha_hora')[:10]
    
    context = {
        'perfil': perfil,
        'calificaciones_creadas': calificaciones_creadas,
        'ultimas_calificaciones': ultimas_calificaciones,
        'logs_usuario': logs_usuario,
    }
    
    return render(request, 'calificaciones/mi_perfil.html', context)
