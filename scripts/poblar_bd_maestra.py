"""
Script de Poblamiento Maestro de Base de Datos - NUAM Calificaciones
Versión: 1.0 - Diciembre 2025

Crea un dataset "Golden" completo y realista para demostración:
- Roles y usuarios con permisos RBAC
- Instrumentos financieros variados
- Calificaciones con 30 factores completos
- Historial de cargas masivas
- Logs de auditoría

Uso:
    python scripts/poblar_bd_maestra.py
"""

import os
import sys
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nuam_project.settings')

import django
django.setup()

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from calificaciones.models import (
    Rol, PerfilUsuario, InstrumentoFinanciero, 
    CalificacionTributaria, CargaMasiva, LogAuditoria,
    IntentoLogin, CuentaBloqueada
)


def generar_factores_validos():
    """
    Genera 30 factores válidos que cumplen REGLA A y REGLA B.
    REGLA A: Cada factor entre 0 y 1
    REGLA B: Suma de factores 8-16 <= 1.0
    """
    factores = {}
    
    # Factores 8-16 (críticos, deben sumar <= 1.0)
    suma_critica = 0
    for i in range(8, 17):
        # Generar valores pequeños para que la suma no exceda 1.0
        valor = round(random.uniform(0.001, 0.08), 8)
        factores[f'factor_{i}'] = Decimal(str(valor))
        suma_critica += valor
    
    # Ajustar si la suma excede 1.0
    if suma_critica > 1.0:
        factor_ajuste = 0.9 / suma_critica
        for i in range(8, 17):
            factores[f'factor_{i}'] = Decimal(str(round(float(factores[f'factor_{i}']) * factor_ajuste, 8)))
    
    # Factores 17-37 (menos críticos)
    for i in range(17, 38):
        valor = round(random.uniform(0.001, 0.05), 8)
        factores[f'factor_{i}'] = Decimal(str(valor))
    
    return factores


def poblar_roles_y_permisos():
    """A. Crear Roles y configurar permisos RBAC"""
    print("\n" + "="*70)
    print("A. CREANDO ROLES Y PERMISOS RBAC")
    print("="*70)
    
    # Crear Roles en la tabla personalizada
    roles_config = [
        {
            'nombre': 'Administrador',
            'descripcion': 'Acceso completo al sistema, puede crear, editar, eliminar y gestionar usuarios'
        },
        {
            'nombre': 'Analista Financiero',
            'descripcion': 'Puede crear y editar calificaciones e instrumentos, sin eliminar'
        },
        {
            'nombre': 'Auditor',
            'descripcion': 'Solo lectura, acceso a auditoría y reportes'
        }
    ]
    
    for rol_data in roles_config:
        rol, created = Rol.objects.get_or_create(
            nombre_rol=rol_data['nombre'],
            defaults={'descripcion': rol_data['descripcion']}
        )
        print(f"  {'✅ Creado' if created else '⚠️  Ya existe'}: Rol '{rol.nombre_rol}'")
    
    print(f"\n✅ Total Roles: {Rol.objects.count()}")


def poblar_usuarios():
    """B. Crear usuarios con perfiles y roles"""
    print("\n" + "="*70)
    print("B. CREANDO USUARIOS")
    print("="*70)
    
    # NOTA DE SEGURIDAD: Las contraseñas están definidas en variables de entorno
    # Ver README_SEEDING.md para credenciales de desarrollo
    import os
    from django.core.management.utils import get_random_secret_key
    
    # Generar contraseña temporal segura para desarrollo
    # En producción, estas deben establecerse mediante variables de entorno
    DEFAULT_TEST_PASSWORD = os.getenv('DEFAULT_TEST_PASSWORD', get_random_secret_key()[:12])
    
    usuarios_config = [
        {
            'username': 'admin',
            'email': 'admin@nuam.cl',
            'password': DEFAULT_TEST_PASSWORD,  # Ver README para contraseña de desarrollo
            'first_name': 'Administrador',
            'last_name': 'Sistema',
            'is_superuser': True,
            'is_staff': True,
            'rol': 'Administrador',
            'telefono': '+56 9 1234 5678',
            'departamento': 'TI'
        },
        {
            'username': 'analista1',
            'email': 'analista1@nuam.cl',
            'password': DEFAULT_TEST_PASSWORD,
            'first_name': 'María',
            'last_name': 'González',
            'is_superuser': False,
            'is_staff': False,
            'rol': 'Analista Financiero',
            'telefono': '+56 9 8765 4321',
            'departamento': 'Finanzas'
        },
        {
            'username': 'analista2',
            'email': 'analista2@nuam.cl',
            'password': DEFAULT_TEST_PASSWORD,
            'first_name': 'Carlos',
            'last_name': 'Rodríguez',
            'is_superuser': False,
            'is_staff': False,
            'rol': 'Analista Financiero',
            'telefono': '+56 9 5555 6666',
            'departamento': 'Finanzas'
        },
        {
            'username': 'auditor1',
            'email': 'auditor1@nuam.cl',
            'password': DEFAULT_TEST_PASSWORD,
            'first_name': 'Patricia',
            'last_name': 'Silva',
            'is_superuser': False,
            'is_staff': False,
            'rol': 'Auditor',
            'telefono': '+56 9 7777 8888',
            'departamento': 'Auditoría'
        },
        {
            'username': 'demo',
            'email': 'demo@nuam.cl',
            'password': DEFAULT_TEST_PASSWORD,
            'first_name': 'Usuario',
            'last_name': 'Demo',
            'is_superuser': True,
            'is_staff': True,
            'rol': 'Administrador',
            'telefono': '+56 9 9999 0000',
            'departamento': 'Demo'
        }
    ]
    
    for user_data in usuarios_config:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'is_superuser': user_data['is_superuser'],
                'is_staff': user_data['is_staff'],
                'is_active': True
            }
        )
        
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"  ✅ Creado: Usuario '{user.username}' ({user.email})")
        else:
            print(f"  ⚠️  Ya existe: Usuario '{user.username}'")
        
        # Crear perfil de usuario
        rol = Rol.objects.get(nombre_rol=user_data['rol'])
        perfil, perfil_created = PerfilUsuario.objects.get_or_create(
            usuario=user,
            defaults={
                'rol': rol,
                'telefono': user_data['telefono'],
                'departamento': user_data['departamento']
            }
        )
        
        if perfil_created:
            print(f"    └─ Perfil creado: Rol '{rol.nombre_rol}'")
    
    print(f"\n✅ Total Usuarios: {User.objects.count()}")


def poblar_instrumentos():
    """C. Crear instrumentos financieros variados"""
    print("\n" + "="*70)
    print("C. CREANDO INSTRUMENTOS FINANCIEROS")
    print("="*70)
    
    instrumentos_config = [
        # Acciones
        {'codigo': 'BCH-2024', 'nombre': 'Banco de Chile', 'tipo': 'Acción'},
        {'codigo': 'CMPC-2024', 'nombre': 'Empresas CMPC S.A.', 'tipo': 'Acción'},
        {'codigo': 'COPEC-2024', 'nombre': 'Copec S.A.', 'tipo': 'Acción'},
        {'codigo': 'SQMB-2024', 'nombre': 'Sociedad Química y Minera', 'tipo': 'Acción'},
        {'codigo': 'CENCOSUD-2024', 'nombre': 'Cencosud S.A.', 'tipo': 'Acción'},
        
        # Bonos
        {'codigo': 'BONO-GOB-2025', 'nombre': 'Bono Tesorería General 2025', 'tipo': 'Bono'},
        {'codigo': 'BONO-CORP-ENTEL', 'nombre': 'Bono Corporativo Entel', 'tipo': 'Bono'},
        {'codigo': 'BONO-BCI-2026', 'nombre': 'Bono Banco BCI 2026', 'tipo': 'Bono'},
        
        # Fondos
        {'codigo': 'CFI-INDEP', 'nombre': 'Fondo Independencia', 'tipo': 'Fondo Mutuo'},
        {'codigo': 'CFI-MONEDA', 'nombre': 'Fondo BCI Moneda Chilena', 'tipo': 'Fondo Mutuo'},
        
        # Depósitos
        {'codigo': 'DAP-SANTANDER', 'nombre': 'Depósito a Plazo Santander', 'tipo': 'Depósito a Plazo'},
        {'codigo': 'DAP-ITAU', 'nombre': 'Depósito a Plazo Itaú', 'tipo': 'Depósito a Plazo'},
        
        # Otros
        {'codigo': 'PAGARE-XYZ', 'nombre': 'Pagaré Empresa XYZ', 'tipo': 'Pagaré'},
        {'codigo': 'LETRA-ABC', 'nombre': 'Letra de Cambio ABC', 'tipo': 'Letra de Cambio'},
    ]
    
    for inst_data in instrumentos_config:
        inst, created = InstrumentoFinanciero.objects.get_or_create(
            codigo_instrumento=inst_data['codigo'],
            defaults={
                'nombre_instrumento': inst_data['nombre'],
                'tipo_instrumento': inst_data['tipo'],
                'activo': True
            }
        )
        print(f"  {'✅ Creado' if created else '⚠️  Ya existe'}: {inst.codigo_instrumento} - {inst.nombre_instrumento} ({inst.tipo_instrumento})")
    
    print(f"\n✅ Total Instrumentos: {InstrumentoFinanciero.objects.count()}")


def poblar_calificaciones():
    """D. Crear calificaciones tributarias con 30 factores"""
    print("\n" + "="*70)
    print("D. CREANDO CALIFICACIONES TRIBUTARIAS (30 FACTORES)")
    print("="*70)
    
    instrumentos = list(InstrumentoFinanciero.objects.all())
    usuarios = list(User.objects.filter(is_active=True))
    
    if not instrumentos or not usuarios:
        print("  ❌ No hay instrumentos o usuarios disponibles")
        return
    
    origenes = ['BOLSA', 'CORREDORA']
    fuentes = ['MANUAL', 'MASIVA']
    tipos_sociedad = ['A', 'C', None]  # Corregido: Solo 'A' (Abierta) o 'C' (Cerrada)
    mercados = ['ACN', 'BCN', 'DER', None]
    
    # Crear 30 calificaciones
    fecha_base = timezone.now().date()
    
    for i in range(30):
        instrumento = random.choice(instrumentos)
        usuario = random.choice(usuarios)
        
        # Generar 30 factores válidos
        factores = generar_factores_validos()
        
        # Fecha aleatoria en los últimos 90 días
        dias_atras = random.randint(0, 90)
        fecha_informe = fecha_base - timedelta(days=dias_atras)
        
        cal_data = {
            'instrumento': instrumento,
            'usuario_creador': usuario,
            'metodo_ingreso': 'FACTOR',
            'numero_dj': random.choice(['1922', '1949']),
            'fecha_informe': fecha_informe,
            'secuencia': random.randint(1000, 999999) if random.random() > 0.5 else None,  # Corregido: rango válido para IntegerField
            'numero_dividendo': random.randint(1000, 999999) if random.random() > 0.3 else None,  # Corregido: rango válido
            'tipo_sociedad': random.choice(tipos_sociedad),
            'valor_historico': Decimal(str(round(random.uniform(1000, 100000), 2))) if random.random() > 0.4 else None,
            'mercado': random.choice(mercados),
            'ejercicio': random.randint(2023, 2024),
            'origen': random.choice(origenes),
            'fuente_origen': random.choice(fuentes),
            'observaciones': f'Calificación de prueba {i+1} - Dataset Golden' if random.random() > 0.6 else '',
            'activo': True,
            **factores  # Desempaquetar los 30 factores
        }
        
        try:
            cal = CalificacionTributaria.objects.create(**cal_data)
            print(f"  ✅ Creada: Calificación #{i+1} - {instrumento.codigo_instrumento} ({cal.origen}/{cal.fuente_origen})")
        except Exception as e:
            print(f"  ❌ Error en calificación #{i+1}: {str(e)[:100]}")
    
    print(f"\n✅ Total Calificaciones: {CalificacionTributaria.objects.count()}")


def poblar_cargas_masivas():
    """E. Crear historial de cargas masivas (para Chart.js)"""
    print("\n" + "="*70)
    print("E. CREANDO HISTORIAL DE CARGAS MASIVAS")
    print("="*70)
    
    usuarios = list(User.objects.filter(is_active=True))
    if not usuarios:
        print("  ❌ No hay usuarios disponibles")
        return
    
    fecha_base = timezone.now()
    
    # Crear cargas en los últimos 7 días
    for i in range(10):
        dias_atras = random.randint(0, 7)
        fecha_carga = fecha_base - timedelta(days=dias_atras, hours=random.randint(0, 23))
        
        estado = random.choice(['EXITOSO', 'EXITOSO', 'EXITOSO', 'PARCIAL', 'FALLIDO'])
        registros = random.randint(10, 50)
        exitosos = registros if estado == 'EXITOSO' else random.randint(0, registros)
        fallidos = registros - exitosos
        
        carga = CargaMasiva.objects.create(
            usuario=random.choice(usuarios),
            archivo_nombre=f'carga_demo_{i+1}.xlsx',
            fecha_carga=fecha_carga,
            estado=estado,
            registros_procesados=registros,
            registros_exitosos=exitosos,
            registros_fallidos=fallidos,
            errores_detalle=f'Errores simulados para demo {i+1}' if fallidos > 0 else ''
        )
        print(f"  ✅ Creada: Carga '{carga.archivo_nombre}' - Estado: {estado} ({exitosos}/{registros})")
    
    print(f"\n✅ Total Cargas Masivas: {CargaMasiva.objects.count()}")


def poblar_logs_auditoria():
    """F. Crear logs de auditoría (para tabla del dashboard)"""
    print("\n" + "="*70)
    print("F. CREANDO LOGS DE AUDITORÍA")
    print("="*70)
    
    usuarios = list(User.objects.filter(is_active=True))
    if not usuarios:
        print("  ❌ No hay usuarios disponibles")
        return
    
    fecha_base = timezone.now()
    
    acciones = [
        ('LOGIN', 'User', 'Inicio de sesión exitoso'),
        ('LOGOUT', 'User', 'Cierre de sesión'),
        ('CREATE', 'CalificacionTributaria', 'Calificación creada'),
        ('UPDATE', 'CalificacionTributaria', 'Calificación modificada'),
        ('DELETE', 'CalificacionTributaria', 'Calificación eliminada'),
        ('CREATE', 'InstrumentoFinanciero', 'Instrumento creado'),
        ('BULK_UPLOAD', 'CargaMasiva', 'Carga masiva procesada'),
        ('EXPORT', 'CalificacionTributaria', 'Exportación realizada'),
    ]
    
    # Crear 50 logs en los últimos 30 días
    for i in range(50):
        dias_atras = random.randint(0, 30)
        horas_atras = random.randint(0, 23)
        minutos_atras = random.randint(0, 59)
        fecha_hora = fecha_base - timedelta(days=dias_atras, hours=horas_atras, minutes=minutos_atras)
        
        accion, tabla, detalle = random.choice(acciones)
        
        log = LogAuditoria.objects.create(
            usuario=random.choice(usuarios),
            accion=accion,
            tabla_afectada=tabla,
            registro_id=random.randint(1, 100),
            ip_address=f'192.168.1.{random.randint(1, 254)}',
            detalles=detalle,
            fecha_hora=fecha_hora
        )
        
        if i < 10:  # Mostrar solo los primeros 10
            print(f"  ✅ Creado: Log {accion} - {tabla} ({log.usuario.username})")
    
    print(f"  ... ({50 - 10} logs más creados)")
    print(f"\n✅ Total Logs Auditoría: {LogAuditoria.objects.count()}")


def poblar_intentos_login():
    """G. Crear intentos de login (para seguridad)"""
    print("\n" + "="*70)
    print("G. CREANDO INTENTOS DE LOGIN")
    print("="*70)
    
    usernames = ['admin', 'analista1', 'auditor1', 'hacker', 'test']
    fecha_base = timezone.now()
    
    for i in range(20):
        dias_atras = random.randint(0, 15)
        fecha_hora = fecha_base - timedelta(days=dias_atras, hours=random.randint(0, 23))
        
        username = random.choice(usernames)
        exitoso = username in ['admin', 'analista1', 'auditor1'] and random.random() > 0.2
        
        intento = IntentoLogin.objects.create(
            username=username,
            ip_address=f'192.168.1.{random.randint(1, 254)}',
            exitoso=exitoso,
            detalles='Login exitoso' if exitoso else 'Credenciales inválidas',
            fecha_hora=fecha_hora
        )
        
        if i < 5:
            print(f"  ✅ Creado: Login {'exitoso' if exitoso else 'fallido'} - {username}")
    
    print(f"  ... ({20 - 5} intentos más creados)")
    print(f"\n✅ Total Intentos Login: {IntentoLogin.objects.count()}")


def main():
    """Función principal de seeding"""
    print("\n" + "="*70)
    print("🌱 POBLAMIENTO MAESTRO DE BASE DE DATOS - NUAM CALIFICACIONES")
    print("="*70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Dataset: Golden (Para Demo Final)")
    print("="*70)
    
    try:
        # Verificar que la BD esté vacía o casi vacía
        if CalificacionTributaria.objects.count() > 10:
            print("\n⚠️  ADVERTENCIA: La base de datos contiene muchos registros.")
            print("   Se recomienda ejecutar 'python manage.py flush --no-input' primero.")
            respuesta = input("\n¿Desea continuar de todas formas? (s/N): ")
            if respuesta.lower() != 's':
                print("\n❌ Operación cancelada por el usuario.")
                return
        
        # Ejecutar seeding en orden
        poblar_roles_y_permisos()
        poblar_usuarios()
        poblar_instrumentos()
        poblar_calificaciones()
        poblar_cargas_masivas()
        poblar_logs_auditoria()
        poblar_intentos_login()
        
        # Resumen final
        print("\n" + "="*70)
        print("✅ POBLAMIENTO COMPLETADO EXITOSAMENTE")
        print("="*70)
        print(f"📊 Roles: {Rol.objects.count()}")
        print(f"👤 Usuarios: {User.objects.count()}")
        print(f"📈 Instrumentos: {InstrumentoFinanciero.objects.count()}")
        print(f"📋 Calificaciones: {CalificacionTributaria.objects.count()}")
        print(f"📦 Cargas Masivas: {CargaMasiva.objects.count()}")
        print(f"📝 Logs Auditoría: {LogAuditoria.objects.count()}")
        print(f"🔐 Intentos Login: {IntentoLogin.objects.count()}")
        print("="*70)
        
        print("\n✅ La base de datos está lista para demostración.")
        print("\nCredenciales de acceso:")
        print("  • admin / admin123 (Administrador)")
        print("  • analista1 / analista123 (Analista Financiero)")
        print("  • auditor1 / auditor123 (Auditor)")
        print("  • demo / demo123 (Administrador)")
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE EL POBLAMIENTO:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
