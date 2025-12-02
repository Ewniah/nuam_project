"""
Filtros personalizados para formatear números en formato chileno
"""
from django import template

register = template.Library()

@register.filter
def formato_clp(value, decimales=2):
    """
    Formatea un número como moneda chilena: $ 1.500.000,00
    """
    try:
        decimales = int(decimales)
        s = f"{float(value):,.{decimales}f}"
        # Intercambiar . y , para formato chileno
        return "$ " + s.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")
    except (ValueError, TypeError):
        return value if value is not None else "-"

@register.filter
def formato_factor(value, decimales=8):
    """
    Formatea un factor tributario: 12,50000000
    """
    try:
        decimales = int(decimales)
        s = f"{float(value):,.{decimales}f}"
        # Intercambiar . y , para formato chileno
        return s.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")
    except (ValueError, TypeError):
        return value if value is not None else "-"

@register.filter
def sumar_factores(calificacion):
    """
    Suma todos los 30 factores tributarios (factor_8 a factor_37) de una calificación.
    Maneja valores None correctamente retornando 0 en su lugar.
    
    Uso en template:
        {% load formatos %}
        {{ calificacion|sumar_factores|floatformat:2 }}
    
    Args:
        calificacion: Instancia de CalificacionTributaria
    
    Returns:
        Decimal: Suma total de los 30 factores (0 si hay error)
    """
    try:
        from decimal import Decimal
        total = Decimal('0')
        for i in range(8, 38):
            valor_factor = getattr(calificacion, f'factor_{i}', None)
            if valor_factor is not None:
                total += Decimal(str(valor_factor))
        return total
    except (AttributeError, TypeError, ValueError) as e:
        return Decimal('0')
