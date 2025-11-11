"""
Comando para crear datos iniciales del sistema
Uso: python manage.py crear_datos_iniciales
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from calificaciones.models import Rol, PerfilUsuario, InstrumentoFinanciero
from datetime import date


class Command(BaseCommand):
    help = 'Crea datos iniciales para el sistema NUAM'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creando datos iniciales...')
        
        # 1. Crear Roles
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
                self.stdout.write(self.style.SUCCESS(f'✓ Rol creado: {rol.nombre_rol}'))
        
        # 2. Crear Instrumentos Financieros de ejemplo
        instrumentos_data = [
            {'codigo': 'CMPC', 'nombre': 'Empresas CMPC S.A.', 'tipo': 'Acción'},
            {'codigo': 'BCHILE', 'nombre': 'Banco de Chile', 'tipo': 'Acción'},
            {'codigo': 'COPEC', 'nombre': 'Empresas Copec S.A.', 'tipo': 'Acción'},
            {'codigo': 'ENELAM', 'nombre': 'Enel Américas S.A.', 'tipo': 'Acción'},
            {'codigo': 'SQM-B', 'nombre': 'Sociedad Química y Minera de Chile', 'tipo': 'Acción'},
            {'codigo': 'BCU26', 'nombre': 'Bono Banco Central Venc. 2026', 'tipo': 'Bono'},
            {'codigo': 'PDBC144', 'nombre': 'Pagaré Banco Central 144 días', 'tipo': 'Bono'},
            {'codigo': 'FMUTUO1', 'nombre': 'Fondo Mutuo Renta Fija', 'tipo': 'Fondo Mutuo'},
        ]
        
        for inst_info in instrumentos_data:
            inst, created = InstrumentoFinanciero.objects.get_or_create(
                codigo_instrumento=inst_info['codigo'],
                defaults={
                    'nombre_instrumento': inst_info['nombre'],
                    'tipo_instrumento': inst_info['tipo']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Instrumento creado: {inst.codigo_instrumento}'))
        
        # 3. Crear usuarios de prueba (si no existen)
        usuarios_data = [
            {'username': 'analista1', 'email': 'analista1@nuam.cl', 'password': 'nuam2025', 'rol': 'Analista Financiero'},
            {'username': 'auditor1', 'email': 'auditor1@nuam.cl', 'password': 'nuam2025', 'rol': 'Auditor'},
        ]
        
        for user_info in usuarios_data:
            user, created = User.objects.get_or_create(
                username=user_info['username'],
                defaults={
                    'email': user_info['email'],
                    'first_name': user_info['username'].capitalize(),
                }
            )
            if created:
                user.set_password(user_info['password'])
                user.save()
                
                # Crear perfil
                rol = Rol.objects.get(nombre_rol=user_info['rol'])
                PerfilUsuario.objects.create(usuario=user, rol=rol, departamento='Finanzas')
                
                self.stdout.write(self.style.SUCCESS(f'✓ Usuario creado: {user.username} (contraseña: {user_info["password"]})'))
        
        self.stdout.write(self.style.SUCCESS('\n¡Datos iniciales creados exitosamente!'))
