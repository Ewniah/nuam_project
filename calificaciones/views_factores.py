from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CalificacionTributaria, InstrumentoFinanciero, LogAuditoria
from .permissions import requiere_permiso
import json


def home(request):
    """Vista para la página de inicio"""
    return render(request, 'home.html')


def obtener_ip_cliente(request):
    """Obtiene la IP real del cliente considerando proxies"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
@requiere_permiso('crear')
def crear_calificacion_factores(request):
    """Vista para crear calificaciones con el formulario simplificado de 5 factores"""
    from .forms import CalificacionFactoresSimpleForm
    
    if request.method == 'POST':
        form = CalificacionFactoresSimpleForm(request.POST)
        
        if form.is_valid():
            calificacion = form.save(commit=False)
            calificacion.usuario_creador = request.user
            
            try:
                calificacion.save()
                
                ip_address = obtener_ip_cliente(request)
                LogAuditoria.objects.create(
                    usuario=request.user,
                    accion='CREATE',
                    tabla_afectada='CalificacionTributaria',
                    registro_id=calificacion.id,
                    ip_address=ip_address,
                    detalles=f'Calificación creada con factores: {calificacion.instrumento.codigo_instrumento}'
                )
                
                messages.success(
                    request,
                    'Calificación creada exitosamente. Factores calculados automáticamente.'
                )
                return redirect('listar_calificaciones')
                
            except Exception as e:
                messages.error(request, f'Error al guardar la calificación: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = CalificacionFactoresSimpleForm()
    
    instrumentos = InstrumentoFinanciero.objects.filter(activo=True)
    tipos_instrumentos = {inst.id: inst.tipo_instrumento for inst in instrumentos}
    
    context = {
        'form': form,
        'titulo': 'Nueva Calificación con Factores',
        'accion': 'Crear',
        'tipos_instrumentos_json': json.dumps(tipos_instrumentos)
    }
    
    return render(request, 'calificaciones/form_factores_simple.html', context)


@login_required
@requiere_permiso('modificar')
def editar_calificacion_factores(request, pk):
    """Vista para editar calificaciones con el formulario simplificado de 5 factores"""
    from .forms import CalificacionFactoresSimpleForm
    
    calificacion = get_object_or_404(CalificacionTributaria, pk=pk, activo=True)
    
    if request.method == 'POST':
        form = CalificacionFactoresSimpleForm(request.POST, instance=calificacion)
        if form.is_valid():
            calificacion = form.save(commit=False)
            calificacion.usuario_creador = request.user
            calificacion.save()
            
            ip_address = obtener_ip_cliente(request)
            LogAuditoria.objects.create(
                usuario=request.user,
                accion='UPDATE',
                tabla_afectada='CalificacionTributaria',
                registro_id=calificacion.id,
                ip_address=ip_address,
                detalles=f'Calificación editada: {calificacion.instrumento.codigo_instrumento}'
            )
            
            messages.success(request, 'Calificación actualizada exitosamente.')
            return redirect('listar_calificaciones')
    else:
        form = CalificacionFactoresSimpleForm(instance=calificacion)
    
    instrumentos = InstrumentoFinanciero.objects.filter(activo=True)
    tipos_instrumentos = {inst.id: inst.tipo_instrumento for inst in instrumentos}
    
    context = {
        'form': form,
        'calificacion': calificacion,
        'titulo': 'Editar Calificación',
        'accion': 'Actualizar',
        'tipos_instrumentos_json': json.dumps(tipos_instrumentos)
    }
    return render(request, 'calificaciones/form_factores_simple.html', context)


def calcular_factores_ajax(request):
    """API endpoint para calcular factores automáticamente vía AJAX"""
    from django.http import JsonResponse
    from decimal import Decimal
    
    try:
        montos = {
            'monto_8': request.GET.get('monto_8', '0'),
            'monto_9': request.GET.get('monto_9', '0'),
            'monto_10': request.GET.get('monto_10', '0'),
            'monto_11': request.GET.get('monto_11', '0'),
            'monto_12': request.GET.get('monto_12', '0'),
        }
        
        # Convertir a Decimal
        montos_decimal = {}
        for key, value in montos.items():
            try:
                montos_decimal[key] = Decimal(value) if value else Decimal('0')
            except:
                montos_decimal[key] = Decimal('0')
        
        # Calcular suma total
        suma_montos = sum(montos_decimal.values())
        
        # Calcular factores
        factores = {}
        for key, monto in montos_decimal.items():
            factor_key = key.replace('monto', 'factor')
            if suma_montos > 0:
                factores[factor_key] = str(round(monto / suma_montos, 8))
            else:
                factores[factor_key] = '0.00000000'
        
        # Calcular suma de factores
        suma_factores = sum(Decimal(f) for f in factores.values())
        
        return JsonResponse({
            'success': True,
            'factores': factores,
            'suma_montos': str(suma_montos),
            'suma_factores': str(suma_factores),
            'es_valido': abs(suma_factores - Decimal('1.0')) < Decimal('0.00000001'),
            'mensaje_error': '',
            'nombres': {
                'factor_8': 'Factor 8',
                'factor_9': 'Factor 9',
                'factor_10': 'Factor 10',
                'factor_11': 'Factor 11',
                'factor_12': 'Factor 12',
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
