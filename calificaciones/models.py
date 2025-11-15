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

    # Campos principales
    monto = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    factor = models.DecimalField(max_digits=18, decimal_places=8, null=True, blank=True)
    metodo_ingreso = models.CharField(max_length=10, choices=METODO_CALCULO, default='MONTO')

    # Información DJ
    numero_dj = models.CharField(max_length=10, blank=True, help_text="DJ 1949 o 1922")

    # Fechas y estado
    fecha_informe = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)  # Eliminación lógica

    observaciones = models.TextField(blank=True)

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
        """Calcula automáticamente el valor faltante según método de ingreso"""
        if self.metodo_ingreso == 'MONTO' and self.monto:
            self.calcular_factor_desde_monto()
        elif self.metodo_ingreso == 'FACTOR' and self.factor:
            self.calcular_monto_desde_factor()
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
