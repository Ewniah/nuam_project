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
    codigo_instrumento = models.CharField(max_length=50, unique=True)  # Ticker
    nombre_instrumento = models.CharField(max_length=255)
    tipo_instrumento = models.CharField(max_length=100)  # Acción, Bono, ETF, etc.
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

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
    # NUEVOS CAMPOS: 5 Factores para Demo (Feedback Profesor)
    # ==========================================
    
    # Factor 8: Con crédito por IDPC generados a contar del 01.01.2017
    monto_8 = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True,
        verbose_name="Monto Factor 8",
        help_text="Con crédito por IDPC generados a contar del 01.01.2017"
    )
    factor_8 = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True,
        verbose_name="Factor 8"
    )
    
    # Factor 9: Con crédito por IDPC generados hasta el 31.12.2016
    monto_9 = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True,
        verbose_name="Monto Factor 9",
        help_text="Con crédito por IDPC generados hasta el 31.12.2016"
    )
    factor_9 = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True,
        verbose_name="Factor 9"
    )
    
    # Factor 10
    monto_10 = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True,
        verbose_name="Monto Factor 10"
    )
    factor_10 = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True,
        verbose_name="Factor 10"
    )
    
    # Factor 11
    monto_11 = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True,
        verbose_name="Monto Factor 11"
    )
    factor_11 = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True,
        verbose_name="Factor 11"
    )
    
    # Factor 12
    monto_12 = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True,
        verbose_name="Monto Factor 12"
    )
    factor_12 = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True,
        verbose_name="Factor 12"
    )

    # Fechas y estado
    fecha_informe = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)  # Eliminación lógica

    observaciones = models.TextField(blank=True)
    
    def clean(self):
        """
        Validación personalizada: suma de factores 8-12 debe ser ≤ 1
        (Según feedback del profesor)
        """
        from django.core.exceptions import ValidationError
        
        # Calcular suma de factores 8-12
        suma_factores = sum([
            self.factor_8 or Decimal('0'),
            self.factor_9 or Decimal('0'),
            self.factor_10 or Decimal('0'),
            self.factor_11 or Decimal('0'),
            self.factor_12 or Decimal('0'),
        ])
        
        if suma_factores > Decimal('1'):
            raise ValidationError(
                f'La suma de los factores 8-12 no puede ser mayor que 1. '
                f'Suma actual: {suma_factores:.8f}'
            )

    def calcular_factor_desde_monto(self):
        """Calcula factor desde monto: Factor = Monto / 1.000.000"""
        if self.monto and self.monto > 0:
            self.factor = self.monto / Decimal('1000000')
            return self.factor
        return None
    
    def calcular_factores_demo(self):
        """
        Calcula los 5 factores de demo desde sus montos.
        Fórmula: Factor = Monto / Suma(Montos 8-12)
        """
        # Calcular suma total de montos 8-12
        suma_montos = sum([
            self.monto_8 or Decimal('0'),
            self.monto_9 or Decimal('0'),
            self.monto_10 or Decimal('0'),
            self.monto_11 or Decimal('0'),
            self.monto_12 or Decimal('0'),
        ])
        
        if suma_montos > 0:
            # Calcular cada factor
            if self.monto_8:
                self.factor_8 = (self.monto_8 / suma_montos).quantize(Decimal('0.00000001'))
            if self.monto_9:
                self.factor_9 = (self.monto_9 / suma_montos).quantize(Decimal('0.00000001'))
            if self.monto_10:
                self.factor_10 = (self.monto_10 / suma_montos).quantize(Decimal('0.00000001'))
            if self.monto_11:
                self.factor_11 = (self.monto_11 / suma_montos).quantize(Decimal('0.00000001'))
            if self.monto_12:
                self.factor_12 = (self.monto_12 / suma_montos).quantize(Decimal('0.00000001'))

    def calcular_monto_desde_factor(self):
        """Calcula monto desde factor: Monto = Factor * 1.000.000"""
        if self.factor and self.factor > 0:
            self.monto = self.factor * Decimal('1000000')
            return self.monto
        return None

    def save(self, *args, **kwargs):
        """Calcula automáticamente el valor faltante según método de ingreso"""
        # Cálculo legacy
        if self.metodo_ingreso == 'MONTO' and self.monto:
            self.calcular_factor_desde_monto()
        elif self.metodo_ingreso == 'FACTOR' and self.factor:
            self.calcular_monto_desde_factor()
        
        # Calcular factores de demo si hay montos
        if any([self.monto_8, self.monto_9, self.monto_10, self.monto_11, self.monto_12]):
            self.calcular_factores_demo()
            
            # Actualizar monto total (legacy) para que aparezca en listados
            self.monto = sum([
                self.monto_8 or Decimal('0'),
                self.monto_9 or Decimal('0'),
                self.monto_10 or Decimal('0'),
                self.monto_11 or Decimal('0'),
                self.monto_12 or Decimal('0'),
            ])
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cal. {self.id} - {self.instrumento.codigo_instrumento} - DJ {self.numero_dj}"

    class Meta:
        verbose_name_plural = "Calificaciones Tributarias"
        ordering = ['-fecha_creacion']
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
