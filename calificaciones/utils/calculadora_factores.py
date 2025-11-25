"""
Calculadora de Factores Tributarios
Versión Demo con 5 factores (8-12)

Según especificaciones del HDU_Inacap.xlsx:
- Los factores deben ser decimales redondeados al 8vo decimal
- La suma de los factores 8-12 no debe superar 1
- Fórmula general: Factor = Monto / Suma Total de Montos
"""

from decimal import Decimal, ROUND_HALF_UP


class CalculadoraFactores:
    """
    Calculadora de factores tributarios para demo.
    Maneja 5 factores (8-12) con validaciones según feedback del profesor.
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
        Calcula los 5 factores de demo desde un diccionario de montos.
        
        Args:
            montos_dict (dict): Diccionario con keys 'monto_8' a 'monto_12'
        
        Returns:
            dict: Diccionario con keys 'factor_8' a 'factor_12'
        
        Example:
            >>> montos = {
            ...     'monto_8': Decimal('500000'),
            ...     'monto_9': Decimal('300000'),
            ...     'monto_10': Decimal('200000'),
            ...     'monto_11': Decimal('0'),
            ...     'monto_12': Decimal('0')
            ... }
            >>> factores = CalculadoraFactores.calcular_todos_los_factores(montos)
            >>> factores['factor_8']
            Decimal('0.50000000')
        """
        # Calcular suma total de montos 8-12
        suma_total = sum([
            Decimal(str(montos_dict.get(f'monto_{i}', 0) or 0))
            for i in range(8, 13)
        ])
        
        factores = {}
        
        # Calcular cada factor
        for i in range(8, 13):
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
        Valida que la suma de factores 8-12 sea ≤ 1.
        
        Args:
            factores_dict (dict): Diccionario con keys 'factor_8' a 'factor_12'
        
        Returns:
            tuple: (es_valido: bool, mensaje_error: str, suma: Decimal)
        
        Example:
            >>> factores = {
            ...     'factor_8': Decimal('0.5'),
            ...     'factor_9': Decimal('0.3'),
            ...     'factor_10': Decimal('0.2'),
            ...     'factor_11': Decimal('0'),
            ...     'factor_12': Decimal('0')
            ... }
            >>> es_valido, mensaje, suma = CalculadoraFactores.validar_suma_factores(factores)
            >>> es_valido
            True
        """
        # Calcular suma de factores 8-12
        suma = sum([
            Decimal(str(factores_dict.get(f'factor_{i}', 0) or 0))
            for i in range(8, 13)
        ])
        
        if suma > Decimal('1'):
            mensaje = (
                f'La suma de los factores 8-12 es {suma:.8f}, '
                f'debe ser ≤ 1.00000000'
            )
            return False, mensaje, suma
        
        return True, '', suma
    
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
        Según hoja "Homologación columnas" del HDU.
        
        Returns:
            dict: Diccionario con keys 'factor_8' a 'factor_12' y sus nombres
        """
        return {
            'factor_8': 'Con crédito por IDPC generados a contar del 01.01.2017',
            'factor_9': 'Con crédito por IDPC generados hasta el 31.12.2016',
            'factor_10': 'Factor 10',
            'factor_11': 'Factor 11',
            'factor_12': 'Factor 12',
        }


# Función auxiliar para uso en vistas
def calcular_factores_desde_request(request_data):
    """
    Función auxiliar para calcular factores desde datos de request.
    
    Args:
        request_data (dict): Datos del request con montos
    
    Returns:
        dict: Diccionario con factores calculados y validación
    """
    # Extraer montos del request
    montos = {}
    for i in range(8, 13):
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
    
    # Validar suma
    es_valido, mensaje, suma = CalculadoraFactores.validar_suma_factores(factores)
    
    return {
        'factores': factores,
        'es_valido': es_valido,
        'mensaje_error': mensaje,
        'suma_factores': suma,
        'nombres': CalculadoraFactores.obtener_nombres_factores()
    }
