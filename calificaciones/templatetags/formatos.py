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
