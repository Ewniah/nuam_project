from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Rol(models.Model):
    """Se definen roles de usuario RBAC: Admin, Analista, Auditor, etc."""
    nombre_rol = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre_rol

    class Meta:
        verbose_name_plural = "Roles"


class PerfilUsuario(models.Model):
    """Se extiende el modelo User para incluir roles y datos adicionales."""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)
    telefono = models.CharField(max_length=20, blank=True)
    departamento = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.rol.nombre_rol if self.rol else 'Sin rol'}"

    class Meta:
        verbose_name_plural = "Perfiles de Usuario"


class InstrumentoFinanciero(models.Model):
    """Cátalogo de instrumentos financieros. Ej: Acciones, Bonos, ETFs, etc."""
    codigo_instrumento = models.CharField(max_length=50, unique=True, blank=True)  # Ticker - autogenerado si vacío
    nombre_instrumento = models.CharField(max_length=255)
    tipo_instrumento = models.CharField(max_length=100)  # Acción, Bono, ETF, etc.
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def _generar_codigo_unico(self):
        """Genera un código único basado en el nombre del instrumento."""
        import re
        from django.utils.text import slugify
        
        # Extraer iniciales o acrónimo del nombre
        palabras = self.nombre_instrumento.upper().split()
        
        # Opción 1: Si tiene menos de 3 palabras, usar iniciales
        if len(palabras) <= 3:
            codigo_base = ''.join([p[0] for p in palabras if p])
        else:
            # Opción 2: Usar primeras 2-3 iniciales de palabras principales (excluir artículos/preposiciones)
            palabras_clave = [p for p in palabras if p not in ['S.A.', 'S.A', 'SA', 'DE', 'DEL', 'LA', 'LAS', 'LOS', 'EL']]
            codigo_base = ''.join([p[0] for p in palabras_clave[:4] if p])
        
        # Limitar a 10 caracteres
        codigo_base = codigo_base[:10]
        
        # Verificar unicidad
        codigo = codigo_base
        contador = 1
        while InstrumentoFinanciero.objects.filter(codigo_instrumento=codigo).exclude(pk=self.pk).exists():
            # Agregar sufijo numérico si existe duplicado
            codigo = f"{codigo_base}{contador}"
            contador += 1
            if contador > 999:  # Límite de seguridad
                import uuid
                codigo = f"{codigo_base[:6]}{str(uuid.uuid4())[:4].upper()}"
                break
        
        return codigo

    def save(self, *args, **kwargs):
        """Genera código automáticamente si está vacío."""
        if not self.codigo_instrumento:
            self.codigo_instrumento = self._generar_codigo_unico()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo_instrumento} - {self.nombre_instrumento}"

    class Meta:
        verbose_name_plural = "Instrumentos Financieros"
        indexes = [
            models.Index(fields=['codigo_instrumento']),
        ]


class CalificacionTributaria(models.Model):
    """
    Tabla central: Calificaciones tributarias según DJ 1949 y DJ 1922 del SII.
    Permite ingreso por MONTO o FACTOR con conversión automática.
    Fórmula: Factor = Monto / 1.000.000
    """
    METODO_CALCULO = [
        ('MONTO', 'Ingreso por Monto'),
        ('FACTOR', 'Ingreso por Factor'),
    ]

    # Relaciones
    instrumento = models.ForeignKey(InstrumentoFinanciero, on_delete=models.CASCADE)
    usuario_creador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    # Campos principales (legacy - mantener por compatibilidad)
    monto = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    factor = models.DecimalField(max_digits=18, decimal_places=8, null=True, blank=True)
    metodo_ingreso = models.CharField(max_length=10, choices=METODO_CALCULO, default='MONTO')

    # Información DJ
    numero_dj = models.CharField(max_length=10, blank=True, help_text="DJ 1949 o 1922")
    
    # ==========================================
    # CAMPOS METADATA ADMINISTRATIVOS
    # Según especificación "3.1 Archivo de carga" (HDU_Inacap.xlsx)
    # ==========================================
    secuencia = models.IntegerField(
        default=0, 
        null=True, 
        blank=True,
        help_text="Número de secuencia del registro (10 dígitos)"
    )
    numero_dividendo = models.IntegerField(
        default=0, 
        null=True, 
        blank=True,
        help_text="Número de dividendo asociado (10 dígitos)"
    )
    tipo_sociedad = models.CharField(
        max_length=1,
        choices=[
            ('A', 'Abierta'),
            ('C', 'Cerrada'),
        ],
        null=True,
        blank=True,
        help_text="Tipo de sociedad: A=Abierta, C=Cerrada"
    )
    valor_historico = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=0,
        null=True,
        blank=True,
        help_text="Valor histórico del instrumento (10 dígitos)"
    )
    mercado = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        help_text="Código de mercado (ej: ACN, 3 chars)"
    )
    ejercicio = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Año de ejercicio tributario (4 dígitos)"
    )
    
    # ==========================================
    # FACTORES TRIBUTARIOS COMPLETOS (8-37)
    # Según DJ 1949 y DJ 1922 del SII
    # ==========================================
    
    # Factores 8-16: Líneas del formulario DJ
    factor_8 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 8")
    factor_9 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 9")
    factor_10 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 10")
    factor_11 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 11")
    factor_12 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 12")
    factor_13 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 13")
    factor_14 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 14")
    factor_15 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 15")
    factor_16 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 16")
    
    # Factores 17-25: Líneas adicionales DJ
    factor_17 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 17")
    factor_18 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 18")
    factor_19 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 19")
    factor_20 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 20")
    factor_21 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 21")
    factor_22 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 22")
    factor_23 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 23")
    factor_24 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 24")
    factor_25 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 25")
    
    # Factores 26-37: Líneas finales DJ
    factor_26 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 26")
    factor_27 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 27")
    factor_28 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 28")
    factor_29 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 29")
    factor_30 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 30")
    factor_31 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 31")
    factor_32 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 32")
    factor_33 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 33")
    factor_34 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 34")
    factor_35 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 35")
    factor_36 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 36")
    factor_37 = models.DecimalField(max_digits=10, decimal_places=8, default=0, null=True, blank=True, verbose_name="Factor 37")

    # Fechas y estado
    fecha_informe = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)  # Eliminación lógica

    observaciones = models.TextField(blank=True, null=True)
    
    def clean(self):
        """
        Validación estricta de integridad de datos tributarios.
        
        REGLA A: Cada factor debe estar entre 0 y 1 (rango válido)
        REGLA B: La suma de factores 8-16 no puede superar 1.0
        
        Raises:
            ValidationError: Si alguna regla es violada
        """
        from django.core.exceptions import ValidationError
        
        # REGLA A: Validar rango individual de cada factor (0 <= factor <= 1)
        for i in range(8, 38):  # Factores 8 a 37
            field_name = f'factor_{i}'
            factor_value = getattr(self, field_name, None)
            
            if factor_value is not None:
                if factor_value < Decimal('0') or factor_value > Decimal('1'):
                    raise ValidationError(
                        f'El {field_name} debe estar entre 0 y 1. Valor recibido: {factor_value}'
                    )
        
        # REGLA B: Validar suma de factores 8-16 (límite crítico)
        suma_factores_criticos = sum([
            getattr(self, f'factor_{i}', None) or Decimal('0')
            for i in range(8, 17)  # Factores 8 a 16
        ])
        
        if suma_factores_criticos > Decimal('1'):
            raise ValidationError(
                'La suma de los factores 8 al 16 no puede superar 1.'
            )

    def calcular_factor_desde_monto(self):
        """Calcula factor desde monto: Factor = Monto / 1.000.000"""
        if self.monto and self.monto > 0:
            self.factor = self.monto / Decimal('1000000')
            return self.factor
        return None

    def calcular_monto_desde_factor(self):
        """Calcula monto desde factor: Monto = Factor * 1.000.000"""
        if self.factor and self.factor > 0:
            self.monto = self.factor * Decimal('1000000')
            return self.monto
        return None

    def save(self, *args, **kwargs):
        """
        Guarda el registro con validación estricta de integridad de datos.
        
        Proceso:
            1. Cálculos legacy (monto ↔ factor)
            2. Validación completa via full_clean()
            3. Persistencia en base de datos
        """
        # Cálculo legacy de compatibilidad
        if self.metodo_ingreso == 'MONTO' and self.monto:
            self.calcular_factor_desde_monto()
        elif self.metodo_ingreso == 'FACTOR' and self.factor:
            self.calcular_monto_desde_factor()
        
        # Ejecutar todas las validaciones antes de guardar
        self.full_clean()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cal. {self.id} - {self.instrumento.codigo_instrumento} - DJ {self.numero_dj}"

    class Meta:
        verbose_name_plural = "Calificaciones Tributarias"
        ordering = ['-fecha_creacion']
        unique_together = ['instrumento', 'fecha_informe', 'numero_dj']
        indexes = [
            models.Index(fields=['fecha_informe']),
            models.Index(fields=['numero_dj']),
        ]


class LogAuditoria(models.Model):
    """Registro inmutable de operaciones (cumplimiento Ley 21.663)"""
    ACCIONES = [
        ('CREATE', 'Crear'),
        ('READ', 'Consultar'),
        ('UPDATE', 'Modificar'),
        ('DELETE', 'Eliminar'),
        ('LOGIN', 'Inicio de sesión'),
        ('LOGIN_FAILED', 'Intento de login fallido'),  # Nuevo
        ('LOGOUT', 'Cierre de sesión'),
        ('ACCOUNT_LOCKED', 'Cuenta bloqueada'),  # Nuevo
        ('ACCOUNT_UNLOCKED', 'Cuenta desbloqueada'),  # Nuevo
    ]

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=20, choices=ACCIONES)  # ✅ Aumentado de 10 a 20
    tabla_afectada = models.CharField(max_length=50)
    registro_id = models.IntegerField(null=True, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    detalles = models.TextField(blank=True)

    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.fecha_hora}"

    class Meta:
        verbose_name_plural = "Logs de Auditoría"
        ordering = ['-fecha_hora']


class IntentoLogin(models.Model):
    """ Creación de registros para intentos de login fallidos y exitosos """
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    fecha_hora = models.DateTimeField(auto_now_add=True)
    exitoso = models.BooleanField(default=False)
    detalles = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.username} - {'Exitoso' if self.exitoso else 'Fallido'} - {self.fecha_hora}"

    class Meta:
        verbose_name_plural = "Intentos de Login"
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['username', 'fecha_hora']),
            models.Index(fields=['ip_address', 'fecha_hora']),
        ]


class CuentaBloqueada(models.Model):
    """ Creación de registros para cuentas bloqueadas tras múltiples intentos fallidos"""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    fecha_bloqueo = models.DateTimeField(auto_now_add=True)
    fecha_desbloqueo = models.DateTimeField(null=True, blank=True)
    intentos_fallidos = models.IntegerField(default=0)
    bloqueada = models.BooleanField(default=True)
    razon = models.TextField(blank=True)

    def __str__(self):
        return f"{self.usuario.username} - {'Bloqueada' if self.bloqueada else 'Desbloqueada'}"

    class Meta:
        verbose_name_plural = "Cuentas Bloqueadas"
        ordering = ['-fecha_bloqueo']


class CargaMasiva(models.Model):
    """Trazabilidad de cargas masivas de archivos CSV/Excel"""
    ESTADOS = [
        ('PROCESANDO', 'Procesando'),
        ('EXITOSO', 'Exitoso'),
        ('PARCIAL', 'Parcial con errores'),
        ('FALLIDO', 'Fallido'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    archivo_nombre = models.CharField(max_length=255)
    archivo = models.FileField(upload_to='cargas_masivas/', null=True)
    fecha_carga = models.DateTimeField(auto_now_add=True)
    registros_procesados = models.IntegerField(default=0)
    registros_exitosos = models.IntegerField(default=0)
    registros_fallidos = models.IntegerField(default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PROCESANDO')
    errores_detalle = models.TextField(blank=True)

    def __str__(self):
        return f"{self.archivo_nombre} - {self.estado}"

    class Meta:
        verbose_name_plural = "Cargas Masivas"
        ordering = ['-fecha_carga']


class ArchivoCargado(models.Model):
    """
    Registro de archivos cargados para detectar duplicados.
    Usa hash SHA-256 para identificar archivos idénticos.
    (NUEVO - Hora 8: Detección de Duplicados)
    """
    nombre_archivo = models.CharField(max_length=255)
    hash_archivo = models.CharField(max_length=64, unique=True, db_index=True)  # SHA-256
    fecha_carga = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    carga_masiva = models.ForeignKey(CargaMasiva, on_delete=models.CASCADE, null=True, blank=True)
    
    @staticmethod
    def calcular_hash(archivo):
        """
        Calcula el hash SHA-256 de un archivo.
        
        Args:
            archivo: FileField o archivo subido
        
        Returns:
            str: Hash SHA-256 en hexadecimal
        """
        import hashlib
        
        hash_sha256 = hashlib.sha256()
        
        # Leer el archivo en chunks para no cargar todo en memoria
        for chunk in archivo.chunks():
            hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def __str__(self):
        return f"{self.nombre_archivo} ({self.fecha_carga.strftime('%Y-%m-%d')})"
    
    class Meta:
        verbose_name_plural = "Archivos Cargados"
        ordering = ['-fecha_carga']
