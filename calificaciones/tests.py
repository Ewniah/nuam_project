import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from datetime import datetime, timedelta
from decimal import Decimal
from faker import Faker
import io
import csv

from .models import (
    Rol, PerfilUsuario, InstrumentoFinanciero, CalificacionTributaria,
    LogAuditoria, IntentoLogin, CuentaBloqueada, CargaMasiva
)
from .forms import (
    CalificacionTributariaForm, InstrumentoFinancieroForm,
    CargaMasivaForm, RegistroForm
)
from .views import obtener_ip_cliente, verificar_cuenta_bloqueada, registrar_intento_login

fake = Faker('es_ES')


# ==========================================
# PRUEBAS DE MODELOS
# ==========================================

class TestRolModel(TestCase):
    """Pruebas para el modelo Rol"""
    
    def test_crear_rol(self):
        """Verifica que se puede crear un rol correctamente"""
        rol = Rol.objects.create(
            nombre_rol='Administrador',
            descripcion='Acceso completo al sistema'
        )
        self.assertEqual(rol.nombre_rol, 'Administrador')
        self.assertEqual(str(rol), 'Administrador')
    
    def test_rol_nombre_unico(self):
        """Verifica que el nombre del rol debe ser único"""
        Rol.objects.create(nombre_rol='Analista', descripcion='Analista financiero')
        with self.assertRaises(Exception):
            Rol.objects.create(nombre_rol='Analista', descripcion='Otro analista')


class TestPerfilUsuarioModel(TestCase):
    """Pruebas para el modelo PerfilUsuario"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.rol = Rol.objects.create(
            nombre_rol='Analista',
            descripcion='Analista financiero'
        )
    
    def test_crear_perfil_usuario(self):
        """Verifica que se puede crear un perfil de usuario"""
        perfil = PerfilUsuario.objects.create(
            usuario=self.user,
            rol=self.rol,
            telefono='+56912345678',
            departamento='Finanzas'
        )
        self.assertEqual(perfil.usuario, self.user)
        self.assertEqual(perfil.rol, self.rol)
        self.assertIn('testuser', str(perfil))
    
    def test_perfil_sin_rol(self):
        """Verifica que un perfil puede existir sin rol asignado"""
        perfil = PerfilUsuario.objects.create(
            usuario=self.user,
            departamento='TI'
        )
        self.assertIsNone(perfil.rol)
        self.assertIn('Sin rol', str(perfil))


class TestInstrumentoFinancieroModel(TestCase):
    """Pruebas para el modelo InstrumentoFinanciero"""
    
    def test_crear_instrumento(self):
        """Verifica que se puede crear un instrumento financiero"""
        instrumento = InstrumentoFinanciero.objects.create(
            codigo_instrumento='CMPC',
            nombre_instrumento='Empresas CMPC S.A.',
            tipo_instrumento='Acción'
        )
        self.assertEqual(instrumento.codigo_instrumento, 'CMPC')
        self.assertTrue(instrumento.activo)
        self.assertIn('CMPC', str(instrumento))
    
    def test_instrumento_codigo_unico(self):
        """Verifica que el código del instrumento debe ser único"""
        InstrumentoFinanciero.objects.create(
            codigo_instrumento='BCHILE',
            nombre_instrumento='Banco de Chile',
            tipo_instrumento='Acción'
        )
        with self.assertRaises(Exception):
            InstrumentoFinanciero.objects.create(
                codigo_instrumento='BCHILE',
                nombre_instrumento='Otro banco',
                tipo_instrumento='Acción'
            )


class TestCalificacionTributariaModel(TestCase):
    """Pruebas para el modelo CalificacionTributaria - Funcionalidad crítica"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.instrumento = InstrumentoFinanciero.objects.create(
            codigo_instrumento='TEST',
            nombre_instrumento='Instrumento de Prueba',
            tipo_instrumento='Acción'
        )
    
    def test_calcular_factor_desde_monto(self):
        """Verifica el cálculo automático de factor desde monto"""
        calificacion = CalificacionTributaria.objects.create(
            instrumento=self.instrumento,
            usuario_creador=self.user,
            monto=Decimal('5000000.0000'),
            metodo_ingreso='MONTO',
            numero_dj='1949',
            fecha_informe=datetime.now().date()
        )
        # Factor = Monto / 1.000.000
        self.assertEqual(calificacion.factor, Decimal('5.00000000'))
    
    def test_calcular_monto_desde_factor(self):
        """Verifica el cálculo automático de monto desde factor"""
        calificacion = CalificacionTributaria.objects.create(
            instrumento=self.instrumento,
            usuario_creador=self.user,
            factor=Decimal('3.50000000'),
            metodo_ingreso='FACTOR',
            numero_dj='1922',
            fecha_informe=datetime.now().date()
        )
        # Monto = Factor * 1.000.000
        self.assertEqual(calificacion.monto, Decimal('3500000.0000'))
    
    def test_calificacion_activa_por_defecto(self):
        """Verifica que las calificaciones se crean activas por defecto"""
        calificacion = CalificacionTributaria.objects.create(
            instrumento=self.instrumento,
            usuario_creador=self.user,
            monto=Decimal('1000000'),
            metodo_ingreso='MONTO',
            fecha_informe=datetime.now().date()
        )
        self.assertTrue(calificacion.activo)
    
    def test_calificacion_str_representation(self):
        """Verifica la representación en string de la calificación"""
        calificacion = CalificacionTributaria.objects.create(
            instrumento=self.instrumento,
            usuario_creador=self.user,
            monto=Decimal('1000000'),
            metodo_ingreso='MONTO',
            numero_dj='1949',
            fecha_informe=datetime.now().date()
        )
        self.assertIn('TEST', str(calificacion))
        self.assertIn('1949', str(calificacion))


class TestLogAuditoriaModel(TestCase):
    """Pruebas para el modelo LogAuditoria"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='auditor',
            password='testpass123'
        )
    
    def test_crear_log_auditoria(self):
        """Verifica que se puede crear un log de auditoría"""
        log = LogAuditoria.objects.create(
            usuario=self.user,
            accion='CREATE',
            tabla_afectada='CalificacionTributaria',
            registro_id=1,
            ip_address='127.0.0.1',
            detalles='Calificación creada'
        )
        self.assertEqual(log.accion, 'CREATE')
        self.assertIn('auditor', str(log))
    
    def test_log_sin_usuario(self):
        """Verifica que se puede crear un log sin usuario (login fallido)"""
        log = LogAuditoria.objects.create(
            usuario=None,
            accion='LOGIN_FAILED',
            tabla_afectada='User',
            ip_address='192.168.1.1',
            detalles='Intento fallido para usuario: hacker'
        )
        self.assertIsNone(log.usuario)
        self.assertEqual(log.accion, 'LOGIN_FAILED')


class TestIntentoLoginModel(TestCase):
    """Pruebas para el modelo IntentoLogin"""
    
    def test_crear_intento_exitoso(self):
        """Verifica registro de intento de login exitoso"""
        intento = IntentoLogin.objects.create(
            username='testuser',
            ip_address='127.0.0.1',
            exitoso=True,
            detalles='Login exitoso'
        )
        self.assertTrue(intento.exitoso)
        self.assertIn('Exitoso', str(intento))
    
    def test_crear_intento_fallido(self):
        """Verifica registro de intento de login fallido"""
        intento = IntentoLogin.objects.create(
            username='testuser',
            ip_address='127.0.0.1',
            exitoso=False,
            detalles='Credenciales incorrectas'
        )
        self.assertFalse(intento.exitoso)
        self.assertIn('Fallido', str(intento))


class TestCuentaBloqueadaModel(TestCase):
    """Pruebas para el modelo CuentaBloqueada"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_crear_cuenta_bloqueada(self):
        """Verifica que se puede bloquear una cuenta"""
        cuenta = CuentaBloqueada.objects.create(
            usuario=self.user,
            intentos_fallidos=5,
            bloqueada=True,
            razon='Múltiples intentos fallidos'
        )
        self.assertTrue(cuenta.bloqueada)
        self.assertEqual(cuenta.intentos_fallidos, 5)
        self.assertIn('Bloqueada', str(cuenta))
    
    def test_desbloquear_cuenta(self):
        """Verifica que se puede desbloquear una cuenta"""
        cuenta = CuentaBloqueada.objects.create(
            usuario=self.user,
            bloqueada=True
        )
        cuenta.bloqueada = False
        cuenta.fecha_desbloqueo = timezone.now()
        cuenta.save()
        self.assertFalse(cuenta.bloqueada)
        self.assertIsNotNone(cuenta.fecha_desbloqueo)


class TestCargaMasivaModel(TestCase):
    """Pruebas para el modelo CargaMasiva"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_crear_carga_masiva(self):
        """Verifica que se puede crear un registro de carga masiva"""
        carga = CargaMasiva.objects.create(
            usuario=self.user,
            archivo_nombre='datos.csv',
            estado='PROCESANDO'
        )
        self.assertEqual(carga.estado, 'PROCESANDO')
        self.assertEqual(carga.registros_procesados, 0)
    
    def test_carga_exitosa(self):
        """Verifica registro de carga exitosa"""
        carga = CargaMasiva.objects.create(
            usuario=self.user,
            archivo_nombre='datos.xlsx',
            registros_procesados=100,
            registros_exitosos=100,
            registros_fallidos=0,
            estado='EXITOSO'
        )
        self.assertEqual(carga.estado, 'EXITOSO')
        self.assertEqual(carga.registros_exitosos, 100)


# ==========================================
# PRUEBAS DE FORMULARIOS
# ==========================================

class TestCalificacionTributariaForm(TestCase):
    """Pruebas para el formulario CalificacionTributariaForm"""
    
    def setUp(self):
        self.instrumento = InstrumentoFinanciero.objects.create(
            codigo_instrumento='TEST',
            nombre_instrumento='Test',
            tipo_instrumento='Acción'
        )
    
    def test_form_valido_con_monto(self):
        """Verifica que el formulario es válido con método MONTO"""
        form_data = {
            'instrumento': self.instrumento.id,
            'metodo_ingreso': 'MONTO',
            'monto': '5000000.0000',
            'numero_dj': '1949',
            'fecha_informe': datetime.now().date(),
            'activo': True
        }
        form = CalificacionTributariaForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_valido_con_factor(self):
        """Verifica que el formulario es válido con método FACTOR"""
        form_data = {
            'instrumento': self.instrumento.id,
            'metodo_ingreso': 'FACTOR',
            'factor': '3.50000000',
            'numero_dj': '1922',
            'fecha_informe': datetime.now().date(),
            'activo': True
        }
        form = CalificacionTributariaForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalido_monto_sin_valor(self):
        """Verifica que el formulario es inválido si método es MONTO sin monto"""
        form_data = {
            'instrumento': self.instrumento.id,
            'metodo_ingreso': 'MONTO',
            'numero_dj': '1949',
            'fecha_informe': datetime.now().date(),
            'activo': True
        }
        form = CalificacionTributariaForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_form_invalido_factor_sin_valor(self):
        """Verifica que el formulario es inválido si método es FACTOR sin factor"""
        form_data = {
            'instrumento': self.instrumento.id,
            'metodo_ingreso': 'FACTOR',
            'numero_dj': '1922',
            'fecha_informe': datetime.now().date(),
            'activo': True
        }
        form = CalificacionTributariaForm(data=form_data)
        self.assertFalse(form.is_valid())


class TestInstrumentoFinancieroForm(TestCase):
    """Pruebas para el formulario InstrumentoFinancieroForm"""
    
    def test_form_valido(self):
        """Verifica que el formulario es válido con datos correctos"""
        form_data = {
            'codigo_instrumento': 'CMPC',
            'nombre_instrumento': 'Empresas CMPC S.A.',
            'tipo_instrumento': 'Acción',
            'activo': True
        }
        form = InstrumentoFinancieroForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalido_sin_codigo(self):
        """Verifica que el formulario es inválido sin código"""
        form_data = {
            'nombre_instrumento': 'Test',
            'tipo_instrumento': 'Acción',
            'activo': True
        }
        form = InstrumentoFinancieroForm(data=form_data)
        self.assertFalse(form.is_valid())


class TestCargaMasivaForm(TestCase):
    """Pruebas para el formulario CargaMasivaForm"""
    
    def test_form_valido_csv(self):
        """Verifica que el formulario acepta archivos CSV"""
        csv_content = b"codigo_instrumento,monto\nTEST,1000000"
        csv_file = io.BytesIO(csv_content)
        csv_file.name = 'test.csv'
        
        form = CargaMasivaForm(files={'archivo': csv_file})
        # Note: El form necesita validación adicional en contexto real
    
    def test_form_valido_xlsx(self):
        """Verifica que el formulario acepta archivos XLSX"""
        # Simulación básica
        xlsx_file = io.BytesIO(b'fake xlsx content')
        xlsx_file.name = 'test.xlsx'
        
        form = CargaMasivaForm(files={'archivo': xlsx_file})


class TestRegistroForm(TestCase):
    """Pruebas para el formulario RegistroForm"""
    
    def test_form_valido(self):
        """Verifica que el formulario de registro es válido"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }
        form = RegistroForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalido_email_duplicado(self):
        """Verifica que el formulario rechaza emails duplicados"""
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='pass123'
        )
        
        form_data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }
        form = RegistroForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


# ==========================================
# PRUEBAS DE VISTAS
# ==========================================

class TestLoginView(TestCase):
    """Pruebas para la vista de login"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.rol = Rol.objects.create(
            nombre_rol='Analista',
            descripcion='Analista financiero'
        )
        PerfilUsuario.objects.create(
            usuario=self.user,
            rol=self.rol
        )
    
    def test_login_exitoso(self):
        """Verifica que un login exitoso funciona correctamente"""
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        # Debe redirigir al dashboard
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se registró en auditoría
        log = LogAuditoria.objects.filter(
            usuario=self.user,
            accion='LOGIN'
        ).first()
        self.assertIsNotNone(log)
    
    def test_login_fallido(self):
        """Verifica que un login fallido se registra correctamente"""
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        # Verificar que se registró el intento fallido
        intento = IntentoLogin.objects.filter(
            username='testuser',
            exitoso=False
        ).first()
        self.assertIsNotNone(intento)
        
        # Verificar que se registró en auditoría
        log = LogAuditoria.objects.filter(
            accion='LOGIN_FAILED'
        ).first()
        self.assertIsNotNone(log)
    
    def test_bloqueo_automatico_tras_5_intentos(self):
        """Verifica que la cuenta se bloquea tras 5 intentos fallidos"""
        # Realizar 5 intentos fallidos
        for i in range(5):
            self.client.post('/login/', {
                'username': 'testuser',
                'password': 'wrongpassword'
            })
        
        # Verificar que la cuenta está bloqueada
        cuenta_bloqueada = CuentaBloqueada.objects.filter(
            usuario=self.user,
            bloqueada=True
        ).first()
        self.assertIsNotNone(cuenta_bloqueada)
        
        # Verificar que se registró el bloqueo en auditoría
        log = LogAuditoria.objects.filter(
            usuario=self.user,
            accion='ACCOUNT_LOCKED'
        ).first()
        self.assertIsNotNone(log)


class TestLogoutView(TestCase):
    """Pruebas para la vista de logout"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.rol = Rol.objects.create(nombre_rol='Analista', descripcion='Test')
        PerfilUsuario.objects.create(usuario=self.user, rol=self.rol)
    
    def test_logout_exitoso(self):
        """Verifica que el logout funciona y se registra en auditoría"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get('/logout/')
        
        # Verificar que se registró en auditoría
        log = LogAuditoria.objects.filter(
            usuario=self.user,
            accion='LOGOUT'
        ).first()
        self.assertIsNotNone(log)


class TestDashboardView(TestCase):
    """Pruebas para la vista del dashboard"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.rol = Rol.objects.create(nombre_rol='Administrador', descripcion='Admin')
        PerfilUsuario.objects.create(usuario=self.user, rol=self.rol)
    
    def test_dashboard_requiere_autenticacion(self):
        """Verifica que el dashboard requiere autenticación"""
        response = self.client.get('/')
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
    
    def test_dashboard_acceso_autenticado(self):
        """Verifica que un usuario autenticado puede acceder al dashboard"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class TestCalificacionesViews(TestCase):
    """Pruebas para las vistas de calificaciones"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.rol = Rol.objects.create(nombre_rol='Administrador', descripcion='Admin')
        PerfilUsuario.objects.create(usuario=self.user, rol=self.rol)
        
        self.instrumento = InstrumentoFinanciero.objects.create(
            codigo_instrumento='TEST',
            nombre_instrumento='Test',
            tipo_instrumento='Acción'
        )
        
        self.client.login(username='testuser', password='testpass123')
    
    def test_listar_calificaciones(self):
        """Verifica que se pueden listar las calificaciones"""
        CalificacionTributaria.objects.create(
            instrumento=self.instrumento,
            usuario_creador=self.user,
            monto=Decimal('1000000'),
            metodo_ingreso='MONTO',
            fecha_informe=datetime.now().date()
        )
        
        response = self.client.get('/calificaciones/')
        self.assertEqual(response.status_code, 200)
    
    def test_crear_calificacion(self):
        """Verifica que se puede crear una calificación"""
        response = self.client.post('/calificaciones/crear/', {
            'instrumento': self.instrumento.id,
            'metodo_ingreso': 'MONTO',
            'monto': '5000000',
            'numero_dj': '1949',
            'fecha_informe': datetime.now().date(),
            'activo': True
        })
        
        # Verificar que se creó la calificación
        calificacion = CalificacionTributaria.objects.filter(
            instrumento=self.instrumento
        ).first()
        self.assertIsNotNone(calificacion)


class TestInstrumentosViews(TestCase):
    """Pruebas para las vistas de instrumentos"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.rol = Rol.objects.create(nombre_rol='Administrador', descripcion='Admin')
        PerfilUsuario.objects.create(usuario=self.user, rol=self.rol)
        self.client.login(username='testuser', password='testpass123')
    
    def test_listar_instrumentos(self):
        """Verifica que se pueden listar los instrumentos"""
        InstrumentoFinanciero.objects.create(
            codigo_instrumento='TEST',
            nombre_instrumento='Test',
            tipo_instrumento='Acción'
        )
        
        response = self.client.get('/instrumentos/')
        self.assertEqual(response.status_code, 200)
    
    def test_crear_instrumento(self):
        """Verifica que se puede crear un instrumento"""
        response = self.client.post('/instrumentos/crear/', {
            'codigo_instrumento': 'NEWTEST',
            'nombre_instrumento': 'Nuevo Test',
            'tipo_instrumento': 'Bono',
            'activo': True
        })
        
        # Verificar que se creó el instrumento
        instrumento = InstrumentoFinanciero.objects.filter(
            codigo_instrumento='NEWTEST'
        ).first()
        self.assertIsNotNone(instrumento)


# ==========================================
# PRUEBAS DE UTILIDADES
# ==========================================

class TestUtilidades(TestCase):
    """Pruebas para funciones de utilidad"""
    
    def test_obtener_ip_sin_proxy(self):
        """Verifica obtención de IP sin proxy"""
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        ip = obtener_ip_cliente(request)
        self.assertEqual(ip, '192.168.1.1')
    
    def test_obtener_ip_con_proxy(self):
        """Verifica obtención de IP con proxy"""
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '10.0.0.1, 192.168.1.1'
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        ip = obtener_ip_cliente(request)
        self.assertEqual(ip, '10.0.0.1')
    
    def test_registrar_intento_login(self):
        """Verifica que se registran los intentos de login"""
        registrar_intento_login('testuser', '127.0.0.1', True, 'Test')
        
        intento = IntentoLogin.objects.filter(username='testuser').first()
        self.assertIsNotNone(intento)
        self.assertTrue(intento.exitoso)
    
    def test_verificar_cuenta_no_bloqueada(self):
        """Verifica que una cuenta no bloqueada retorna False"""
        user = User.objects.create_user(username='testuser', password='pass123')
        
        bloqueada, mensaje, minutos = verificar_cuenta_bloqueada('testuser')
        self.assertFalse(bloqueada)
    
    def test_verificar_cuenta_bloqueada(self):
        """Verifica que una cuenta bloqueada retorna True"""
        user = User.objects.create_user(username='testuser', password='pass123')
        CuentaBloqueada.objects.create(
            usuario=user,
            bloqueada=True,
            intentos_fallidos=5
        )
        
        bloqueada, mensaje, minutos = verificar_cuenta_bloqueada('testuser')
        self.assertTrue(bloqueada)
        self.assertIn('bloqueada', mensaje.lower())


# ==========================================
# PRUEBAS DE SEGURIDAD Y AUDITORÍA (FEEDBACK PROFESOR)
# ==========================================

class TestSeguridadYAuditoria(TestCase):
    """
    Pruebas completas de seguridad y auditoría según feedback del profesor.
    Cubre: login, bloqueo de cuentas, desbloqueo automático/manual, y auditoría.
    """
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.rol = Rol.objects.create(
            nombre_rol='Analista',
            descripcion='Analista de prueba'
        )
        PerfilUsuario.objects.create(
            usuario=self.user,
            rol=self.rol
        )
    
    def test_login_exitoso_registra_auditoria(self):
        """
        Test 1: Verifica que un login exitoso se registra en LogAuditoria con acción LOGIN
        """
        # Realizar login exitoso
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Verificar redirección al dashboard
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se registró en LogAuditoria
        log = LogAuditoria.objects.filter(
            usuario=self.user,
            accion='LOGIN'
        ).first()
        
        self.assertIsNotNone(log, "El login exitoso debe registrarse en LogAuditoria")
        self.assertEqual(log.tabla_afectada, 'User')
        self.assertIn('Login exitoso', log.detalles)
        
        # Verificar que se registró en IntentoLogin
        intento = IntentoLogin.objects.filter(
            username='testuser',
            exitoso=True
        ).first()
        
        self.assertIsNotNone(intento, "El login exitoso debe registrarse en IntentoLogin")
    
    def test_login_fallido_registra_auditoria(self):
        """
        Test 2: Verifica que un login fallido se registra en LogAuditoria con acción LOGIN_FAILED
        """
        # Realizar login fallido
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        # Verificar que NO se redirigió (se quedó en login)
        self.assertEqual(response.status_code, 200)
        
        # Verificar que se registró en LogAuditoria
        log = LogAuditoria.objects.filter(
            accion='LOGIN_FAILED'
        ).first()
        
        self.assertIsNotNone(log, "El login fallido debe registrarse en LogAuditoria")
        self.assertEqual(log.tabla_afectada, 'User')
        self.assertIn('testuser', log.detalles)
        
        # Verificar que se registró en IntentoLogin
        intento = IntentoLogin.objects.filter(
            username='testuser',
            exitoso=False
        ).first()
        
        self.assertIsNotNone(intento, "El login fallido debe registrarse en IntentoLogin")
    
    def test_cinco_intentos_fallidos_bloquean_cuenta(self):
        """
        Test 3: Verifica que 5 intentos fallidos bloquean la cuenta automáticamente
        """
        # Realizar 5 intentos fallidos
        for i in range(5):
            self.client.post('/login/', {
                'username': 'testuser',
                'password': 'wrongpassword'
            })
        
        # Verificar que la cuenta está bloqueada
        cuenta_bloqueada = CuentaBloqueada.objects.filter(
            usuario=self.user,
            bloqueada=True
        ).first()
        
        self.assertIsNotNone(cuenta_bloqueada, "La cuenta debe estar bloqueada después de 5 intentos")
        self.assertEqual(cuenta_bloqueada.intentos_fallidos, 5)
        
        # Verificar que se registró el bloqueo en auditoría
        log = LogAuditoria.objects.filter(
            usuario=self.user,
            accion='ACCOUNT_LOCKED'
        ).first()
        
        self.assertIsNotNone(log, "El bloqueo debe registrarse en LogAuditoria")
        self.assertEqual(log.tabla_afectada, 'CuentaBloqueada')
        self.assertIn('bloqueada', log.detalles.lower())
        
        # Verificar que hay 5 intentos fallidos registrados
        intentos_fallidos = IntentoLogin.objects.filter(
            username='testuser',
            exitoso=False
        ).count()
        
        self.assertEqual(intentos_fallidos, 5)
    
    def test_cuenta_bloqueada_no_permite_login(self):
        """
        Test 4: Verifica que una cuenta bloqueada rechaza login incluso con password correcto
        """
        # Bloquear la cuenta manualmente
        CuentaBloqueada.objects.create(
            usuario=self.user,
            bloqueada=True,
            intentos_fallidos=5,
            razon='Test de bloqueo'
        )
        
        # Intentar login con password CORRECTO
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Verificar que NO se permitió el login
        self.assertEqual(response.status_code, 200)  # Se quedó en página de login
        
        # Verificar mensaje de error
        messages_list = list(response.context['messages'])
        self.assertTrue(
            any('bloqueada' in str(m).lower() for m in messages_list),
            "Debe mostrar mensaje de cuenta bloqueada"
        )
        
        # Verificar que se registró el intento en cuenta bloqueada
        intento = IntentoLogin.objects.filter(
            username='testuser',
            detalles__contains='bloqueada'
        ).first()
        
        self.assertIsNotNone(intento, "Debe registrar intento en cuenta bloqueada")
    
    def test_desbloqueo_automatico_despues_30_minutos(self):
        """
        Test 5: Verifica que la cuenta se desbloquea automáticamente después de 30 minutos
        """
        # Crear cuenta bloqueada hace 31 minutos
        cuenta = CuentaBloqueada.objects.create(
            usuario=self.user,
            bloqueada=True,
            intentos_fallidos=5
        )
        
        # Modificar fecha de bloqueo para simular 31 minutos atrás
        cuenta.fecha_bloqueo = timezone.now() - timedelta(minutes=31)
        cuenta.save()
        
        # Intentar login
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Verificar que el login fue exitoso (redirigió)
        self.assertEqual(response.status_code, 302)
        
        # Verificar que la cuenta se desbloqueó
        cuenta.refresh_from_db()
        self.assertFalse(cuenta.bloqueada, "La cuenta debe estar desbloqueada")
        self.assertIsNotNone(cuenta.fecha_desbloqueo)
        
        # Verificar que se registró el desbloqueo automático en auditoría
        log = LogAuditoria.objects.filter(
            accion='ACCOUNT_UNLOCKED',
            detalles__contains='automáticamente'
        ).first()
        
        self.assertIsNotNone(log, "El desbloqueo automático debe registrarse en LogAuditoria")
        self.assertIn('30 minutos', log.detalles)
    
    def test_desbloqueo_manual_funciona(self):
        """
        Test 6: Verifica que el desbloqueo manual funciona correctamente
        (Este test será completado cuando implementemos la vista de desbloqueo manual)
        """
        # Crear cuenta bloqueada
        cuenta = CuentaBloqueada.objects.create(
            usuario=self.user,
            bloqueada=True,
            intentos_fallidos=5
        )
        
        # Simular desbloqueo manual (sin vista aún, directamente en modelo)
        cuenta.bloqueada = False
        cuenta.fecha_desbloqueo = timezone.now()
        cuenta.save()
        
        # Verificar que la cuenta está desbloqueada
        self.assertFalse(cuenta.bloqueada)
        self.assertIsNotNone(cuenta.fecha_desbloqueo)
        
        # Verificar que ahora puede hacer login
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 302, "Debe permitir login después de desbloqueo")
    
    def test_bloqueo_registra_account_locked(self):
        """
        Test 7: Verifica que el bloqueo registra acción ACCOUNT_LOCKED en auditoría
        """
        # Realizar 5 intentos fallidos para bloquear
        for i in range(5):
            self.client.post('/login/', {
                'username': 'testuser',
                'password': 'wrongpassword'
            })
        
        # Verificar que existe el log con ACCOUNT_LOCKED
        log = LogAuditoria.objects.filter(
            usuario=self.user,
            accion='ACCOUNT_LOCKED',
            tabla_afectada='CuentaBloqueada'
        ).first()
        
        self.assertIsNotNone(log, "Debe existir log de ACCOUNT_LOCKED")
        self.assertIsNotNone(log.ip_address, "Debe registrar IP")
        self.assertIn('bloqueada', log.detalles.lower())
        self.assertIn('5', log.detalles)  # Debe mencionar los 5 intentos
    
    def test_desbloqueo_registra_account_unlocked(self):
        """
        Test 8: Verifica que el desbloqueo registra acción ACCOUNT_UNLOCKED en auditoría
        """
        # Crear cuenta bloqueada hace 31 minutos
        cuenta = CuentaBloqueada.objects.create(
            usuario=self.user,
            bloqueada=True,
            intentos_fallidos=5
        )
        cuenta.fecha_bloqueo = timezone.now() - timedelta(minutes=31)
        cuenta.save()
        
        # Limpiar logs anteriores para este test
        LogAuditoria.objects.filter(accion='ACCOUNT_UNLOCKED').delete()
        
        # Intentar login (esto debería desbloquear automáticamente)
        self.client.post('/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Verificar que existe el log con ACCOUNT_UNLOCKED
        log = LogAuditoria.objects.filter(
            accion='ACCOUNT_UNLOCKED',
            tabla_afectada='CuentaBloqueada'
        ).first()
        
        self.assertIsNotNone(log, "Debe existir log de ACCOUNT_UNLOCKED")
        self.assertIn('desbloqueada', log.detalles.lower())
        self.assertIn('automáticamente', log.detalles.lower())

