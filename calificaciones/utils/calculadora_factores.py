"""
Calculadora de Factores Tributarios
Versión Completa con 30 factores (8-37)

Según especificaciones del HDU_Inacap.xlsx:
- Los factores deben ser decimales redondeados al 8vo decimal
- La suma de los factores 8-16 no debe superar 1 (REGLA B)
- Cada factor debe estar entre 0 y 1 (REGLA A)
- Fórmula general: Factor = Monto / Suma Total de Montos
"""

from decimal import Decimal, ROUND_HALF_UP


class CalculadoraFactores:
    """
    Calculadora de factores tributarios completa.
    Maneja 30 factores (8-37) con validaciones según DJ 1949 y 1922.
    """
    
    @staticmethod
    def calcular_factor_desde_monto(monto, suma_total):
        """
        Calcula un factor individual desde su monto.
        
        Args:
            monto (Decimal): Monto del factor
            suma_total (Decimal): Suma total de todos los montos
        
        Returns:
            Decimal: Factor calculado, redondeado a 8 decimales
        """
        if not monto or not suma_total or suma_total == 0:
            return Decimal('0.00000000')
        
        monto = Decimal(str(monto))
        suma_total = Decimal(str(suma_total))
        
        # Calcular factor y redondear a 8 decimales
        factor = monto / suma_total
        return factor.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calcular_todos_los_factores(montos_dict):
        """
        Calcula TODOS los 30 factores (8-37) desde un diccionario de montos.
        
        Args:
            montos_dict (dict): Diccionario con keys 'monto_8' a 'monto_37'
        
        Returns:
            dict: Diccionario con keys 'factor_8' a 'factor_37'
        
        Example:
            >>> montos = {
            ...     'monto_8': Decimal('500000'),
            ...     'monto_9': Decimal('300000'),
            ...     'monto_10': Decimal('200000'),
            ...     # ... resto de montos
            ... }
            >>> factores = CalculadoraFactores.calcular_todos_los_factores(montos)
            >>> factores['factor_8']
            Decimal('0.50000000')
        """
        # Calcular suma total de TODOS los montos (8-37)
        suma_total = sum([
            Decimal(str(montos_dict.get(f'monto_{i}', 0) or 0))
            for i in range(8, 38)
        ])
        
        factores = {}
        
        # Calcular cada factor (8-37)
        for i in range(8, 38):
            monto_key = f'monto_{i}'
            factor_key = f'factor_{i}'
            monto = montos_dict.get(monto_key, 0) or 0
            
            factores[factor_key] = CalculadoraFactores.calcular_factor_desde_monto(
                monto, suma_total
            )
        
        return factores
    
    @staticmethod
    def validar_suma_factores(factores_dict):
        """
        Valida que la suma de factores 8-16 sea ≤ 1 (REGLA B).
        
        Args:
            factores_dict (dict): Diccionario con keys 'factor_8' a 'factor_37'
        
        Returns:
            tuple: (es_valido: bool, mensaje_error: str, suma: Decimal)
        
        Example:
            >>> factores = {
            ...     'factor_8': Decimal('0.5'),
            ...     'factor_9': Decimal('0.3'),
            ...     'factor_10': Decimal('0.2'),
            ...     # ... resto de factores
            ... }
            >>> es_valido, mensaje, suma = CalculadoraFactores.validar_suma_factores(factores)
            >>> es_valido
            True
        """
        # REGLA B: Calcular suma de factores 8-16 (críticos)
        suma_critica = sum([
            Decimal(str(factores_dict.get(f'factor_{i}', 0) or 0))
            for i in range(8, 17)
        ])
        
        if suma_critica > Decimal('1'):
            mensaje = (
                f'La suma de los factores 8-16 es {suma_critica:.8f}, '
                f'debe ser ≤ 1.00000000 (REGLA B)'
            )
            return False, mensaje, suma_critica
        
        return True, '', suma_critica
    
    @staticmethod
    def formatear_factor(factor):
        """
        Formatea un factor a 8 decimales.
        
        Args:
            factor (Decimal or float or str): Factor a formatear
        
        Returns:
            Decimal: Factor formateado a 8 decimales
        """
        if factor is None:
            return Decimal('0.00000000')
        
        factor_decimal = Decimal(str(factor))
        return factor_decimal.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def obtener_nombres_factores():
        """
        Retorna un diccionario con los nombres descriptivos de cada factor.
        Según hoja "Homologación columnas" del HDU y DJ 1949/1922.
        
        Returns:
            dict: Diccionario con keys 'factor_8' a 'factor_37' y sus nombres
        """
        nombres = {
            'factor_8': 'Con crédito por IDPC generados a contar del 01.01.2017',
            'factor_9': 'Con crédito por IDPC generados hasta el 31.12.2016',
        }
        
        # Generar nombres genéricos para factores 10-37
        for i in range(10, 38):
            nombres[f'factor_{i}'] = f'Factor {i}'
        
        return nombres


# Función auxiliar para uso en vistas
def calcular_factores_desde_request(request_data):
    """
    Función auxiliar para calcular factores desde datos de request.
    Soporta TODOS los 30 factores (8-37).
    
    Args:
        request_data (dict): Datos del request con montos (monto_8 a monto_37)
    
    Returns:
        dict: Diccionario con factores calculados y validación
    """
    # Extraer montos del request para TODOS los factores (8-37)
    montos = {}
    for i in range(8, 38):
        monto_key = f'monto_{i}'
        if monto_key in request_data:
            try:
                montos[monto_key] = Decimal(str(request_data[monto_key]))
            except (ValueError, TypeError):
                montos[monto_key] = Decimal('0')
        else:
            montos[monto_key] = Decimal('0')
    
    # Calcular factores
    factores = CalculadoraFactores.calcular_todos_los_factores(montos)
    
    # Validar suma (REGLA B: factores 8-16 <= 1)
    es_valido, mensaje, suma = CalculadoraFactores.validar_suma_factores(factores)
    
    return {
        'factores': factores,
        'es_valido': es_valido,
        'mensaje_error': mensaje,
        'suma_factores': suma,
        'nombres': CalculadoraFactores.obtener_nombres_factores()
    }
