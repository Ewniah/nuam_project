Sistema NUAM - Gestión de Calificaciones Tributarias

Sistema web desarrollado en Django para la gestión de calificaciones tributarias de instrumentos financieros para NUAM Exchange.

DESCRIPCIÓN

Aplicación que permite gestionar calificaciones tributarias según normativas DJ 1922 y DJ 1949 del SII de Chile, con control de acceso por roles, carga masiva de datos, exportación de reportes y registro completo de auditoría.

CARACTERÍSTICAS

CRUD de calificaciones tributarias e instrumentos

Cálculo automático entre monto y factor

Sistema de roles (Administrador, Analista, Auditor)

Registro de usuarios con asignación de roles

Carga masiva desde CSV/Excel

Exportación a Excel/CSV

Dashboard con estadísticas y gráficos

Registro de auditoría completo con filtros avanzados

Gestión segura de variables de entorno (django-environ)

Formato chileno (CLP)

TECNOLOGÍAS

Backend: Django 5.1, Python 3.10+

Base de Datos: PostgreSQL

Frontend: Bootstrap 5, Chart.js, Bootstrap Icons

Procesamiento: pandas, openpyxl

Seguridad: django-environ

INSTALACIÓN

Clonar repositorio

git clone https://github.com/Ewniah/nuam_project.git
cd nuam_project

Crear entorno virtual

python -m venv venv

Windows:
venv\Scripts\activate

Linux/Mac:
source venv/bin/activate

Instalar dependencias

pip install -r requirements.txt

Configurar variables de entorno

Crea un archivo .env en la raíz del proyecto con el siguiente contenido:

SECRET_KEY=tu-secret-key-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.postgresql
DB_NAME=nuam_calificaciones_db
DB_USER=postgres
DB_PASSWORD=tu-password-aqui
DB_HOST=localhost
DB_PORT=5432

IMPORTANTE: Nunca subas el archivo .env a GitHub. Ya está incluido en .gitignore.

Crear base de datos en PostgreSQL

CREATE DATABASE nuam_calificaciones_db;

Ejecutar migraciones

python manage.py makemigrations
python manage.py migrate

Crear datos iniciales

python manage.py crear_datos_iniciales
python manage.py createsuperuser

Crear perfil para el superusuario

python manage.py shell

Luego ejecuta:

from django.contrib.auth.models import User
from calificaciones.models import PerfilUsuario, Rol

admin = User.objects.get(username='admin')
rol_admin, created = Rol.objects.get_or_create(
nombre_rol='Administrador',
defaults={'descripcion': 'Acceso completo al sistema'}
)
PerfilUsuario.objects.create(
usuario=admin,
rol=rol_admin,
departamento='Administración'
)
exit()

Iniciar servidor

python manage.py runserver

Acceder a: http://127.0.0.1:8000/

URLS PRINCIPALES

Login: http://127.0.0.1:8000/login/
Dashboard: http://127.0.0.1:8000/
Registro usuarios: http://127.0.0.1:8000/registro/
Calificaciones: http://127.0.0.1:8000/calificaciones/
Instrumentos: http://127.0.0.1:8000/instrumentos/
Carga Masiva: http://127.0.0.1:8000/carga-masiva/
Auditoría: http://127.0.0.1:8000/auditoria/

USUARIOS DE PRUEBA

Usuario | Contraseña | Rol
admin | admin123 | Administrador
analista1 | nuam2025 | Analista Financiero
auditor1 | nuam2025 | Auditor

ROLES Y PERMISOS

Administrador: Acceso completo al sistema, incluido registro de auditoría

Analista Financiero: Crear y editar calificaciones (no eliminar)

Auditor: Solo lectura + acceso completo a logs de auditoría

FUNCIONALIDADES PRINCIPALES

Gestión de Calificaciones

Ingresar calificación por monto: Sistema calcula factor automáticamente

Ingresar calificación por factor: Sistema calcula monto automáticamente

Editar y eliminar (según permisos de rol)

Búsqueda y filtros avanzados

Registro de Usuarios

Formulario completo con validaciones

Asignación de roles al momento del registro

Creación automática de perfil de usuario

Validación de email único

Registro de Auditoría

Registro automático de todas las operaciones CRUD

Registro de login/logout de usuarios

Filtros por: acción, usuario, tabla afectada, fechas

Paginación de resultados

Solo accesible para Administradores y Auditores

Carga Masiva

Importar múltiples registros desde CSV/Excel

Validación de datos en tiempo real

Reporte de errores detallado

Template de ejemplo descargable

Exportación de Reportes

Exportar calificaciones a Excel con formato profesional

Exportar a CSV para procesamiento externo

Filtros aplicables antes de exportar

SEGURIDAD

Variables de entorno protegidas con django-environ

SECRET_KEY y credenciales de BD no expuestas en el código

Archivo .env excluido del repositorio

Sistema de autenticación robusto

Control de acceso basado en roles (RBAC)

Registro completo de auditoría para trazabilidad

ESTRUCTURA DEL PROYECTO

nuam_project/
├── calificaciones/ App principal
│ ├── models.py Modelos de BD
│ ├── views.py Lógica de negocio
│ ├── forms.py Formularios
│ ├── urls.py URLs de la app
│ └── templates/ Templates HTML
├── nuam_project/ Configuración
│ ├── settings.py Configuración (con environ)
│ └── urls.py URLs principales
├── templates/ Templates globales
├── static/ Archivos estáticos
├── .env Variables de entorno (NO SUBIR)
├── .gitignore Archivos ignorados por Git
├── requirements.txt Dependencias
└── README.md Este archivo

DEPENDENCIAS PRINCIPALES

Django==5.1
psycopg2-binary
pandas
openpyxl
django-environ

DEPLOYMENT

Para producción:

Cambiar DEBUG=False en .env

Configurar ALLOWED_HOSTS correctamente

Configurar base de datos de producción

Recopilar archivos estáticos: python manage.py collectstatic

Usar servidor WSGI (Gunicorn, uWSGI)

Configurar servidor web (Nginx, Apache)

LICENCIA

Proyecto Integrado - NUAM Exchange 2025

AUTOR

Bryan Alegría Pastén - Proyecto Integrado 2025

Copyright 2025 Sistema NUAM

CHANGELOG

Versión 2.0 (13 Nov 2025)

Agregado registro de usuarios con asignación de roles

Agregado registro de auditoría completo con filtros

Implementado django-environ para gestión segura de variables

Mejorada navegación con link de auditoría en navbar

Actualizado README con nuevas funcionalidades

Versión 1.0 (Inicial)

CRUD de calificaciones e instrumentos

Sistema de roles y permisos

Dashboard con estadísticas

Carga masiva y exportación
