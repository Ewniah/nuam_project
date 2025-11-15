"""
Comando para poblar el sistema con datos de demostración completos
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from calificaciones.models import *
from datetime import date, timedelta
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Pobla el sistema con datos de demostración completos'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('\n🚀 Poblando sistema con datos de demostración...\n'))
        
        # 1. Obtener o crear usuarios
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.create_superuser('admin', 'admin@nuam.cl', 'Admin1234.')
            self.stdout.write('  ✓ Superusuario creado')
        
        # 2. Crear roles
        roles_data = [
            {'nombre': 'Administrador', 'desc': 'Acceso completo al sistema, gestión de usuarios y configuración'},
            {'nombre': 'Analista Financiero', 'desc': 'Creación y modificación de calificaciones tributarias'},
            {'nombre': 'Auditor', 'desc': 'Solo lectura, generación de reportes y consulta de logs'},
        ]
        
        for rol_info in roles_data:
            rol, created = Rol.objects.get_or_create(
                nombre_rol=rol_info['nombre'],
                defaults={'descripcion': rol_info['desc']}
            )
            if created:
                self.stdout.write(f'  ✓ Rol creado: {rol.nombre_rol}')
        
        # 3. Crear usuarios de prueba con perfiles
        usuarios_data = [
            {'username': 'analista1', 'email': 'analista1@nuam.cl', 'first_name': 'María', 'last_name': 'González', 'rol': 'Analista Financiero', 'dept': 'Finanzas'},
            {'username': 'analista2', 'email': 'analista2@nuam.cl', 'first_name': 'Pedro', 'last_name': 'Martínez', 'rol': 'Analista Financiero', 'dept': 'Finanzas'},
            {'username': 'auditor1', 'email': 'auditor1@nuam.cl', 'first_name': 'Carmen', 'last_name': 'Silva', 'rol': 'Auditor', 'dept': 'Auditoría'},
        ]
        
        for user_data in usuarios_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )
            if created:
                user.set_password('nuam2025')
                user.save()
                
                rol = Rol.objects.get(nombre_rol=user_data['rol'])
                PerfilUsuario.objects.create(
                    usuario=user,
                    rol=rol,
                    departamento=user_data['dept'],
                    telefono=f'+569{random.randint(10000000, 99999999)}'
                )
                self.stdout.write(f'  ✓ Usuario creado: {user.username} ({user_data["rol"]})')
        
        # 4. Crear instrumentos financieros chilenos reales
        instrumentos_data = [
            {'codigo': 'CMPC', 'nombre': 'Empresas CMPC S.A.', 'tipo': 'Acción'},
            {'codigo': 'BCHILE', 'nombre': 'Banco de Chile', 'tipo': 'Acción'},
            {'codigo': 'COPEC', 'nombre': 'Empresas Copec S.A.', 'tipo': 'Acción'},
            {'codigo': 'ENELAM', 'nombre': 'Enel Américas S.A.', 'tipo': 'Acción'},
            {'codigo': 'SQM-B', 'nombre': 'Sociedad Química y Minera de Chile', 'tipo': 'Acción'},
            {'codigo': 'FALABELLA', 'nombre': 'Falabella S.A.', 'tipo': 'Acción'},
            {'codigo': 'LTM', 'nombre': 'Latam Airlines Group S.A.', 'tipo': 'Acción'},
            {'codigo': 'VAPORES', 'nombre': 'Compañía Sud Americana de Vapores', 'tipo': 'Acción'},
            {'codigo': 'BCU26', 'nombre': 'Bono BCU Vencimiento 2026', 'tipo': 'Bono'},
            {'codigo': 'BCU28', 'nombre': 'Bono BCU Vencimiento 2028', 'tipo': 'Bono'},
            {'codigo': 'PDBC144', 'nombre': 'Pagaré Banco Central 144 días', 'tipo': 'Bono'},
            {'codigo': 'FMRFIJA', 'nombre': 'Fondo Mutuo Renta Fija', 'tipo': 'Fondo Mutuo'},
            {'codigo': 'FMRVARIABLE', 'nombre': 'Fondo Mutuo Renta Variable', 'tipo': 'Fondo Mutuo'},
            {'codigo': 'FMMIXTO', 'nombre': 'Fondo Mutuo Mixto', 'tipo': 'Fondo Mutuo'},
        ]
        
        for inst_data in instrumentos_data:
            inst, created = InstrumentoFinanciero.objects.get_or_create(
                codigo_instrumento=inst_data['codigo'],
                defaults={
                    'nombre_instrumento': inst_data['nombre'],
                    'tipo_instrumento': inst_data['tipo']
                }
            )
            if created:
                self.stdout.write(f'  ✓ Instrumento creado: {inst.codigo_instrumento}')
        
        # 5. Crear calificaciones tributarias variadas
        instrumentos = InstrumentoFinanciero.objects.all()
        fecha_base = date.today()
        
        calificaciones_ejemplos = [
            # Ingresos por MONTO
            {'codigo': 'CMPC', 'metodo': 'MONTO', 'monto': 15000000, 'dj': '1949', 'obs': 'Inversión en acciones CMPC'},
            {'codigo': 'BCHILE', 'metodo': 'MONTO', 'monto': 25000000, 'dj': '1949', 'obs': 'Cartera de inversión Banco de Chile'},
            {'codigo': 'COPEC', 'metodo': 'MONTO', 'monto': 18500000, 'dj': '1949', 'obs': 'Posición en Copec'},
            {'codigo': 'FALABELLA', 'metodo': 'MONTO', 'monto': 12750000, 'dj': '1949', 'obs': 'Inversión retail'},
            {'codigo': 'BCU26', 'metodo': 'MONTO', 'monto': 100000000, 'dj': '1949', 'obs': 'Bono del Banco Central'},
            # Ingresos por FACTOR
            {'codigo': 'ENELAM', 'metodo': 'FACTOR', 'factor': 22.5, 'dj': '1922', 'obs': 'Factor declarado DJ 1922'},
            {'codigo': 'SQM-B', 'metodo': 'FACTOR', 'factor': 45.125, 'dj': '1922', 'obs': 'Minería - DJ 1922'},
            {'codigo': 'LTM', 'metodo': 'FACTOR', 'factor': 8.75, 'dj': '1922', 'obs': 'Aerolínea - Factor tributario'},
            {'codigo': 'FMRFIJA', 'metodo': 'FACTOR', 'factor': 150.5, 'dj': '1922', 'obs': 'Fondo mutuo renta fija'},
            {'codigo': 'FMMIXTO', 'metodo': 'FACTOR', 'factor': 85.25, 'dj': '1922', 'obs': 'Fondo mixto diversificado'},
        ]
        
        usuarios_lista = [admin_user] + list(User.objects.filter(username__startswith='analista'))
        
        for i, cal_data in enumerate(calificaciones_ejemplos):
            try:
                instrumento = InstrumentoFinanciero.objects.get(codigo_instrumento=cal_data['codigo'])
                usuario = random.choice(usuarios_lista)
                
                cal = CalificacionTributaria(
                    instrumento=instrumento,
                    usuario_creador=usuario,
                    metodo_ingreso=cal_data['metodo'],
                    numero_dj=cal_data['dj'],
                    fecha_informe=fecha_base - timedelta(days=i*5),
                    observaciones=cal_data['obs']
                )
                
                if cal_data['metodo'] == 'MONTO':
                    cal.monto = Decimal(str(cal_data['monto']))
                else:
                    cal.factor = Decimal(str(cal_data['factor']))
                
                cal.save()
                self.stdout.write(f'  ✓ Calificación creada: {instrumento.codigo_instrumento} ({cal_data["metodo"]})')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error: {str(e)}'))
        
        # Estadísticas finales
        self.stdout.write(self.style.SUCCESS(f'\n📊 Resumen del sistema:'))
        self.stdout.write(f'   • Roles: {Rol.objects.count()}')
        self.stdout.write(f'   • Usuarios: {User.objects.count()}')
        self.stdout.write(f'   • Perfiles: {PerfilUsuario.objects.count()}')
        self.stdout.write(f'   • Instrumentos: {InstrumentoFinanciero.objects.count()}')
        self.stdout.write(f'   • Calificaciones: {CalificacionTributaria.objects.filter(activo=True).count()}')
        self.stdout.write(f'   • Logs de auditoría: {LogAuditoria.objects.count()}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ ¡Sistema poblado exitosamente!\n'))
