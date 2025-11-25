"""
Tests para el sistema de calificaciones tributarias
Cubre: modelos, vistas, cálculos de factores y formularios
"""
import pytest
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from calificaciones.models import (
    CalificacionTributaria,
    InstrumentoFinanciero,
    PerfilUsuario,
    Rol
)


@pytest.mark.django_db
class TestCalificacionTributariaModel(TestCase):
    """Tests para el modelo CalificacionTributaria"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        # Crear usuario
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Crear rol
        self.rol = Rol.objects.create(
            nombre_rol='Analista Financiero',
            descripcion='Rol de prueba'
        )
        
        # Crear perfil
        self.perfil = PerfilUsuario.objects.create(
            usuario=self.user,
            rol=self.rol
        )
        
        # Crear instrumento
        self.instrumento = InstrumentoFinanciero.objects.create(
            codigo_instrumento='TEST001',
            nombre_instrumento='Instrumento de Prueba',
            tipo_instrumento='BONO',
            activo=True
        )
    
    def test_crear_calificacion_basica(self):
        """Test: Crear una calificación básica"""
        calificacion = CalificacionTributaria.objects.create(
            instrumento=self.instrumento,
            monto=Decimal('1000000'),
            factor=Decimal('0.12345678'),
            numero_dj='123',
            fecha_informe='2025-01-01',
            metodo_ingreso='MONTO',
            usuario_creador=self.user
        )
        
        assert calificacion.id is not None
        assert calificacion.monto == Decimal('1000000')
        assert calificacion.activo is True
    
    def test_calcular_factores_demo(self):
        """Test: Cálculo automático de factores desde montos"""
        calificacion = CalificacionTributaria.objects.create(
            instrumento=self.instrumento,
            monto_8=Decimal('100000'),
            monto_9=Decimal('200000'),
            monto_10=Decimal('300000'),
            monto_11=Decimal('400000'),
            monto_12=Decimal('500000'),
            numero_dj='123',
            fecha_informe='2025-01-01',
            metodo_ingreso='FACTOR',
            usuario_creador=self.user
        )
        
        # Verificar que los factores se calcularon
        assert calificacion.factor_8 is not None
        assert calificacion.factor_9 is not None
        assert calificacion.factor_10 is not None
        assert calificacion.factor_11 is not None
        assert calificacion.factor_12 is not None
        
        # Verificar que el monto total se calculó
        expected_total = Decimal('1500000')  # suma de todos los montos
        assert calificacion.monto == expected_total
    
    def test_monto_total_actualizado(self):
        """Test: El monto total se actualiza con la suma de montos detallados"""
        calificacion = CalificacionTributaria.objects.create(
            instrumento=self.instrumento,
            monto_8=Decimal('100'),
            monto_9=Decimal('200'),
            monto_10=Decimal('300'),
            monto_11=Decimal('400'),
            monto_12=Decimal('500'),
            numero_dj='123',
            fecha_informe='2025-01-01',
            metodo_ingreso='FACTOR',
            usuario_creador=self.user
        )
        
        assert calificacion.monto == Decimal('1500')


@pytest.mark.django_db
class TestCalificacionViews(TestCase):
    """Tests para las vistas de calificaciones"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        
        # Crear usuario con permisos
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        
        # Crear rol (solo con campos que existen en el modelo)
        self.rol = Rol.objects.create(
            nombre_rol='Analista Financiero',
            descripcion='Rol de prueba'
        )
        
        # Crear perfil
        self.perfil = PerfilUsuario.objects.create(
            usuario=self.user,
            rol=self.rol
        )
        
        # Crear instrumento
        self.instrumento = InstrumentoFinanciero.objects.create(
            codigo_instrumento='TEST001',
            nombre_instrumento='Instrumento de Prueba',
            tipo_instrumento='BONO',
            activo=True
        )
        
        # Login
        self.client.login(username='testuser', password='testpass123')
    
    def test_listar_calificaciones_view(self):
        """Test: Vista de listado de calificaciones"""
        # Crear una calificación
        CalificacionTributaria.objects.create(
            instrumento=self.instrumento,
            monto=Decimal('1000000'),
            factor=Decimal('0.12345678'),
            numero_dj='123',
            fecha_informe='2025-01-01',
            metodo_ingreso='MONTO',
            usuario_creador=self.user
        )
        
        response = self.client.get(reverse('listar_calificaciones'))
        
        assert response.status_code == 200
        assert 'calificaciones' in response.context
        assert len(response.context['calificaciones']) == 1
    
    def test_crear_calificacion_factores_get(self):
        """Test: GET de formulario de creación con factores"""
        response = self.client.get(reverse('crear_calificacion_factores'))
        
        assert response.status_code == 200
        assert 'form' in response.context
    
    def test_crear_calificacion_factores_post(self):
        """Test: POST para crear calificación con factores"""
        data = {
            'instrumento': self.instrumento.id,
            'monto_8': '100000',
            'monto_9': '200000',
            'monto_10': '300000',
            'monto_11': '400000',
            'monto_12': '500000',
            'numero_dj': '456',
            'fecha_informe': '2025-01-15',
            'metodo_ingreso': 'FACTOR'
        }
        
        response = self.client.post(
            reverse('crear_calificacion_factores'),
            data=data
        )
        
        # Verificar redirección
        assert response.status_code == 302
        
        # Verificar que se creó la calificación
        calificacion = CalificacionTributaria.objects.filter(numero_dj='456').first()
        assert calificacion is not None
        assert calificacion.monto == Decimal('1500000')
    
    def test_dashboard_view(self):
        """Test: Vista del dashboard"""
        response = self.client.get(reverse('dashboard'))
        
        assert response.status_code == 200
        assert 'total_calificaciones' in response.context


@pytest.mark.django_db
class TestFactorCalculations(TestCase):
    """Tests específicos para cálculos de factores"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.rol = Rol.objects.create(
            nombre_rol='Analista Financiero',
            descripcion='Rol de prueba'
        )
        
        self.perfil = PerfilUsuario.objects.create(
            usuario=self.user,
            rol=self.rol
        )
        
        self.instrumento = InstrumentoFinanciero.objects.create(
            codigo_instrumento='TEST001',
            nombre_instrumento='Instrumento de Prueba',
            tipo_instrumento='BONO',
            activo=True
        )
    
    def test_factor_calculation_precision(self):
        """Test: Precisión de cálculo de factores (8 decimales)"""
        calificacion = CalificacionTributaria.objects.create(
            instrumento=self.instrumento,
            monto_8=Decimal('123456.78'),
            monto_9=Decimal('0'),
            monto_10=Decimal('0'),
            monto_11=Decimal('0'),
            monto_12=Decimal('0'),
            numero_dj='123',
            fecha_informe='2025-01-01',
            metodo_ingreso='FACTOR',
            usuario_creador=self.user
        )
        
        # Verificar que el factor tiene 8 decimales
        factor_str = str(calificacion.factor_8)
        if '.' in factor_str:
            decimals = len(factor_str.split('.')[1])
            assert decimals <= 8
    
    def test_multiple_factors_calculation(self):
        """Test: Cálculo de múltiples factores simultáneamente"""
        calificacion = CalificacionTributaria.objects.create(
            instrumento=self.instrumento,
            monto_8=Decimal('100'),
            monto_9=Decimal('200'),
            monto_10=Decimal('300'),
            monto_11=Decimal('400'),
            monto_12=Decimal('500'),
            numero_dj='123',
            fecha_informe='2025-01-01',
            metodo_ingreso='FACTOR',
            usuario_creador=self.user
        )
        
        # Todos los factores deben estar calculados
        assert calificacion.factor_8 is not None
        assert calificacion.factor_9 is not None
        assert calificacion.factor_10 is not None
        assert calificacion.factor_11 is not None
        assert calificacion.factor_12 is not None
        
        # Los factores deben ser diferentes (a menos que los montos sean iguales)
        # En este caso, como los montos son diferentes, los factores también deberían serlo
        factors = [
            calificacion.factor_8,
            calificacion.factor_9,
            calificacion.factor_10,
            calificacion.factor_11,
            calificacion.factor_12
        ]
        
        # Verificar que hay al menos alguna variación
        assert len(set(factors)) > 1


@pytest.mark.django_db
class TestInstrumentoFinanciero(TestCase):
    """Tests para el modelo InstrumentoFinanciero"""
    
    def test_crear_instrumento(self):
        """Test: Crear un instrumento financiero"""
        instrumento = InstrumentoFinanciero.objects.create(
            codigo_instrumento='BOND001',
            nombre_instrumento='Bono Corporativo',
            tipo_instrumento='BONO',
            activo=True
        )
        
        assert instrumento.id is not None
        assert instrumento.codigo_instrumento == 'BOND001'
        assert instrumento.activo is True
    
    def test_instrumento_str(self):
        """Test: Representación en string del instrumento"""
        instrumento = InstrumentoFinanciero.objects.create(
            codigo_instrumento='BOND001',
            nombre_instrumento='Bono Corporativo',
            tipo_instrumento='BONO',
            activo=True
        )
        
        expected = 'BOND001 - Bono Corporativo'
        assert str(instrumento) == expected


# Comando para ejecutar los tests:
# pytest calificaciones/tests/test_calificaciones.py -v
# o
# python manage.py test calificaciones.tests.test_calificaciones
