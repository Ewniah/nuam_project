"""
Management command para poblar la base de datos con datos de demostración
Uso: python manage.py populate_demo_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from calificaciones.models import (
    Rol,
    PerfilUsuario,
    InstrumentoFinanciero,
    CalificacionTributaria
)
from decimal import Decimal
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de demostración'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando población de datos...'))
        
        # 1. Crear roles
        self.stdout.write('Creando roles...')
        roles_data = [
            {'nombre_rol': 'Administrador', 'descripcion': 'Acceso total al sistema'},
            {'nombre_rol': 'Analista Financiero', 'descripcion': 'Puede crear y modificar calificaciones'},
            {'nombre_rol': 'Auditor', 'descripcion': 'Solo lectura y auditoría'},
            {'nombre_rol': 'Consultor', 'descripcion': 'Consulta de información'},
        ]
        
        roles = {}
        for rol_data in roles_data:
            rol, created = Rol.objects.get_or_create(
                nombre_rol=rol_data['nombre_rol'],
                defaults={'descripcion': rol_data['descripcion']}
            )
            roles[rol_data['nombre_rol']] = rol
            if created:
                self.stdout.write(f'  ✓ Rol creado: {rol.nombre_rol}')
        
        # 2. Crear usuarios de demostración
        self.stdout.write('\nCreando usuarios...')
        usuarios_data = [
            {
                'username': 'admin',
                'email': 'admin@nuam.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'Sistema',
                'is_staff': True,
                'is_superuser': True,
                'rol': 'Administrador'
            },
            {
                'username': 'analista1',
                'email': 'analista1@nuam.com',
                'password': 'analista123',
                'first_name': 'María',
                'last_name': 'González',
                'is_staff': True,
                'rol': 'Analista Financiero'
            },
            {
                'username': 'analista2',
                'email': 'analista2@nuam.com',
                'password': 'analista123',
                'first_name': 'Carlos',
                'last_name': 'Rodríguez',
                'is_staff': True,
                'rol': 'Analista Financiero'
            },
            {
                'username': 'auditor1',
                'email': 'auditor@nuam.com',
                'password': 'auditor123',
                'first_name': 'Ana',
                'last_name': 'Martínez',
                'rol': 'Auditor'
            },
        ]
        
        usuarios = {}
        for user_data in usuarios_data:
            rol_nombre = user_data.pop('rol')
            password = user_data.pop('password')
            
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(f'  ✓ Usuario creado: {user.username}')
            
            # Crear perfil
            perfil, _ = PerfilUsuario.objects.get_or_create(
                usuario=user,
                defaults={'rol': roles[rol_nombre]}
            )
            
            usuarios[user.username] = user
        
        # 3. Crear instrumentos financieros
        self.stdout.write('\nCreando instrumentos financieros...')
        instrumentos_data = [
            # Bonos
            {'codigo': 'BONO-CORP-2025', 'nombre': 'Bono Corporativo 2025', 'tipo': 'BONO'},
            {'codigo': 'BONO-GOB-2026', 'nombre': 'Bono Gobierno Chile 2026', 'tipo': 'BONO'},
            {'codigo': 'BONO-BANK-2025', 'nombre': 'Bono Bancario Santander 2025', 'tipo': 'BONO'},
            {'codigo': 'BONO-CORP-2027', 'nombre': 'Bono Corporativo Latam 2027', 'tipo': 'BONO'},
            
            # Acciones
            {'codigo': 'CMPC', 'nombre': 'Empresas CMPC S.A.', 'tipo': 'ACCION'},
            {'codigo': 'SQM-B', 'nombre': 'Sociedad Química y Minera', 'tipo': 'ACCION'},
            {'codigo': 'COPEC', 'nombre': 'Empresas Copec S.A.', 'tipo': 'ACCION'},
            {'codigo': 'ENELAM', 'nombre': 'Enel Américas S.A.', 'tipo': 'ACCION'},
            
            # Fondos
            {'codigo': 'FONDO-A', 'nombre': 'Fondo Mutuo Renta Fija A', 'tipo': 'FONDO'},
            {'codigo': 'FONDO-B', 'nombre': 'Fondo Mutuo Balanceado B', 'tipo': 'FONDO'},
            {'codigo': 'FONDO-C', 'nombre': 'Fondo Mutuo Acciones C', 'tipo': 'FONDO'},
            
            # Derivados
            {'codigo': 'FUT-CLP-USD', 'nombre': 'Futuro CLP/USD', 'tipo': 'DERIVADO'},
            {'codigo': 'OPT-IPSA', 'nombre': 'Opción sobre IPSA', 'tipo': 'DERIVADO'},
        ]
        
        instrumentos = {}
        for inst_data in instrumentos_data:
            instrumento, created = InstrumentoFinanciero.objects.get_or_create(
                codigo_instrumento=inst_data['codigo'],
                defaults={
                    'nombre_instrumento': inst_data['nombre'],
                    'tipo_instrumento': inst_data['tipo'],
                    'activo': True
                }
            )
            instrumentos[inst_data['codigo']] = instrumento
            if created:
                self.stdout.write(f'  ✓ Instrumento creado: {instrumento.codigo_instrumento}')
        
        # 4. Crear calificaciones tributarias
        self.stdout.write('\nCreando calificaciones tributarias...')
        
        # Calificaciones con factores múltiples (nuevas)
        calificaciones_factores = [
            {
                'instrumento': 'BONO-CORP-2025',
                'montos': [100000, 200000, 300000, 400000, 500000],
                'dj': '2025-001',
                'fecha': datetime.now() - timedelta(days=2),
                'usuario': 'analista1'
            },
            {
                'instrumento': 'BONO-GOB-2026',
                'montos': [150000, 250000, 350000, 450000, 550000],
                'dj': '2025-002',
                'fecha': datetime.now() - timedelta(days=5),
                'usuario': 'analista2'
            },
            {
                'instrumento': 'CMPC',
                'montos': [80000, 160000, 240000, 320000, 400000],
                'dj': '2025-003',
                'fecha': datetime.now() - timedelta(days=7),
                'usuario': 'analista1'
            },
            {
                'instrumento': 'SQM-B',
                'montos': [120000, 240000, 360000, 480000, 600000],
                'dj': '2025-004',
                'fecha': datetime.now() - timedelta(days=10),
                'usuario': 'analista2'
            },
            {
                'instrumento': 'FONDO-A',
                'montos': [90000, 180000, 270000, 360000, 450000],
                'dj': '2025-005',
                'fecha': datetime.now() - timedelta(days=12),
                'usuario': 'analista1'
            },
        ]
        
        for cal_data in calificaciones_factores:
            calificacion = CalificacionTributaria.objects.create(
                instrumento=instrumentos[cal_data['instrumento']],
                monto_8=Decimal(str(cal_data['montos'][0])),
                monto_9=Decimal(str(cal_data['montos'][1])),
                monto_10=Decimal(str(cal_data['montos'][2])),
                monto_11=Decimal(str(cal_data['montos'][3])),
                monto_12=Decimal(str(cal_data['montos'][4])),
                numero_dj=cal_data['dj'],
                fecha_informe=cal_data['fecha'],
                metodo_ingreso='FACTOR',
                usuario_creador=usuarios[cal_data['usuario']],
                activo=True
            )
            self.stdout.write(f'  ✓ Calificación creada: {calificacion.instrumento.codigo_instrumento} (DJ: {calificacion.numero_dj})')
        
        # Calificaciones legacy (con monto y factor directo)
        calificaciones_legacy = [
            {
                'instrumento': 'BONO-BANK-2025',
                'monto': 1000000,
                'factor': 0.12345678,
                'dj': '2024-098',
                'fecha': datetime.now() - timedelta(days=30),
                'usuario': 'analista1'
            },
            {
                'instrumento': 'COPEC',
                'monto': 850000,
                'factor': 0.10987654,
                'dj': '2024-099',
                'fecha': datetime.now() - timedelta(days=35),
                'usuario': 'analista2'
            },
            {
                'instrumento': 'ENELAM',
                'monto': 920000,
                'factor': 0.11234567,
                'dj': '2024-100',
                'fecha': datetime.now() - timedelta(days=40),
                'usuario': 'analista1'
            },
        ]
        
        for cal_data in calificaciones_legacy:
            calificacion = CalificacionTributaria.objects.create(
                instrumento=instrumentos[cal_data['instrumento']],
                monto=Decimal(str(cal_data['monto'])),
                factor=Decimal(str(cal_data['factor'])),
                numero_dj=cal_data['dj'],
                fecha_informe=cal_data['fecha'],
                metodo_ingreso='MONTO',
                usuario_creador=usuarios[cal_data['usuario']],
                activo=True
            )
            self.stdout.write(f'  ✓ Calificación legacy creada: {calificacion.instrumento.codigo_instrumento}')
        
        # Resumen
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('✓ Población de datos completada exitosamente!'))
        self.stdout.write('\nResumen:')
        self.stdout.write(f'  - Roles: {Rol.objects.count()}')
        self.stdout.write(f'  - Usuarios: {User.objects.count()}')
        self.stdout.write(f'  - Instrumentos: {InstrumentoFinanciero.objects.filter(activo=True).count()}')
        self.stdout.write(f'  - Calificaciones: {CalificacionTributaria.objects.filter(activo=True).count()}')
        self.stdout.write('\nCredenciales de acceso:')
        self.stdout.write('  - Admin: admin / admin123')
        self.stdout.write('  - Analista 1: analista1 / analista123')
        self.stdout.write('  - Analista 2: analista2 / analista123')
        self.stdout.write('  - Auditor: auditor1 / auditor123')
        self.stdout.write('='*50)
