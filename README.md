# Sistema NUAM - Gestión de Calificaciones Tributarias

<h3>Sistema web desarrollado en Django para la gestión de calificaciones tributarias de NUAM Exchange.</h3>

![Django](https://img.shields.io/badge/Django-5.1-092E20?logo=django)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-blue?logo=postgresql)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)

---

## 📜 Descripción

Aplicación que permite gestionar **calificaciones tributarias** según las normativas **DJ 1922** y **DJ 1949** del SII de Chile. Incluye control de acceso por roles, carga masiva de datos, exportación de reportes y un registro completo de auditoría.

**Arquitectura refactorizada:** El sistema ha sido completamente reestructurado siguiendo mejores prácticas de desarrollo, con código unificado, logging comprehensivo, manejo robusto de excepciones y documentación profesional en español.

---

## ✨ Características Principales

- **CRUD** de calificaciones tributarias e instrumentos financieros.
- Cálculo automático bidireccional entre **monto y factor**.
- Sistema de **roles y permisos** (Administrador, Analista, Auditor).
- Registro de usuarios con asignación de roles.
- **Carga masiva** de datos desde CSV/Excel.
- **Exportación** de reportes a Excel/CSV.
- **Dashboard** con estadísticas y gráficos.
- Registro de **auditoría (logs)** completo con filtros avanzados.
- Gestión segura de variables de entorno (django-environ).
- Formato de moneda chilena (CLP).

---

## 🛠️ Tecnologías Utilizadas

- **Backend:** Django 5.2, Python 3.10+
- **Base de Datos:** PostgreSQL
- **Frontend:** Bootstrap 5, Chart.js, Bootstrap Icons
- **Procesamiento de Archivos:** openpyxl
- **Seguridad:** django-environ
- **Calidad de Código:** Black formatter, Django logging framework

---

## 🏗️ Arquitectura del Sistema

### Estructura de Vistas Unificada

El módulo `calificaciones/views.py` (2,016 líneas) consolida toda la lógica de negocio en **9 secciones funcionales**:

1. **Configuración y Utilidades Base** (líneas 1-240)

   - Logger centralizado con `logging.getLogger(__name__)`
   - 7 constantes de configuración (MAX_LOGIN_ATTEMPTS, LOCKOUT_DURATION, etc.)
   - Funciones auxiliares: `obtener_ip_cliente()`, `verificar_cuenta_bloqueada()`, `registrar_intento_login()`

2. **Autenticación y Sesión** (líneas 241-455)

   - Vista de login con bloqueo por intentos fallidos
   - Logout con registro de auditoría
   - Registro de nuevos usuarios con asignación de roles

3. **Dashboard Principal** (líneas 456-620)

   - Vista principal con estadísticas y gráficos
   - Métricas agregadas por instrumento y estado
   - Integración con Chart.js para visualización

4. **Gestión de Calificaciones Tributarias** (líneas 621-1000)

   - CRUD completo con formularios simples y complejos
   - Cálculo bidireccional monto ↔ factor
   - Validaciones según DJ 1922/1949
   - Listado con filtros y paginación

5. **Gestión de Instrumentos Financieros** (líneas 1001-1380)

   - CRUD de instrumentos (acciones, bonos, fondos)
   - Validación de duplicados
   - Relaciones con calificaciones

6. **Carga Masiva de Datos** (líneas 1381-1550)

   - Procesamiento de CSV/Excel con pandas
   - Validación de datos y manejo de errores
   - Reporte de registros procesados/errores

7. **Auditoría y Seguridad** (líneas 1551-1750)

   - Registro automático de todas las operaciones CRUD
   - Filtros avanzados por usuario, acción, fecha
   - Exportación de logs a Excel/CSV
   - Paginación de registros históricos

8. **Gestión de Usuarios (Admin)** (líneas 1751-1920)

   - Vista administrativa de usuarios
   - Asignación/modificación de roles
   - Bloqueo/desbloqueo de cuentas
   - Historial de intentos de login

9. **Perfil de Usuario** (líneas 1921-2016)
   - Vista de perfil personal
   - Actividad reciente del usuario
   - Información de rol y permisos

### Patrones de Diseño Implementados

- **Decoradores personalizados:** `@login_required`, `@user_passes_test`, `@permission_required`
- **Logging comprehensivo:** 27 puntos de registro en operaciones críticas
- **Manejo de excepciones específicas:** 15+ handlers para `KeyError`, `ValueError`, `IntegrityError`, `ObjectDoesNotExist`
- **Auditoría automática:** Señales de Django para registrar todos los cambios
- **Separación de responsabilidades:** Funciones auxiliares reutilizables

---

## 📋 Estándares de Código

### Formato y Estilo

- **Formatter:** Black con `line-length = 100`
- **Cumplimiento:** 100% PEP 8
- **Docstrings:** Google Style en español (77% de funciones documentadas)
- **Convenciones de nomenclatura:** snake_case para funciones/variables, PascalCase para clases

### Sistema de Logging

```python
import logging
logger = logging.getLogger(__name__)

# Niveles utilizados:
logger.debug("Detalles técnicos para desarrollo")
logger.info("Operaciones exitosas importantes")
logger.warning("Situaciones anómalas no críticas")
logger.error("Errores que requieren atención")
```

**Puntos de logging clave:**

- Inicio/fin de operaciones CRUD
- Intentos de login (exitosos y fallidos)
- Validaciones fallidas
- Errores de base de datos
- Acceso denegado por permisos

### Manejo de Excepciones

Patrón estándar implementado en todas las vistas:

```python
try:
    # Operación principal
    resultado = operacion_critica()
    logger.info(f"Operación exitosa: {resultado}")
except SpecificException as e:
    logger.error(f"Error específico: {e}")
    messages.error(request, "Mensaje amigable para el usuario")
except Exception as e:
    logger.error(f"Error inesperado: {e}")
    messages.error(request, "Error interno del sistema")
```

**Excepciones manejadas:**

- `KeyError`, `ValueError`: Validación de datos
- `IntegrityError`: Duplicados en base de datos
- `ObjectDoesNotExist`: Recursos no encontrados
- `PermissionDenied`: Control de acceso
- `ValidationError`: Formularios Django

### Constantes de Configuración

Definidas al inicio de `views.py`:

```python
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30
FAILED_ATTEMPT_WINDOW_MINUTES = 15
MAX_AUDIT_LOG_RECORDS = 1000
MAX_LOGIN_HISTORY_RECORDS = 50
RECENT_ACTIVITY_DAYS = 7
```

---

## 👨‍💻 Guía para Desarrolladores

### Estructura del Proyecto

```
nuam_project/
├── calificaciones/          # Aplicación principal
│   ├── views.py            # ⭐ Archivo unificado (2,016 líneas, 30 funciones)
│   ├── models.py           # Modelos de datos
│   ├── forms.py            # Formularios Django
│   ├── urls.py             # Rutas de la app (22 URLs)
│   ├── admin.py            # Configuración del admin
│   ├── permissions.py      # Decoradores personalizados
│   ├── signals.py          # Auditoría automática
│   └── utils/
│       └── calculadora_factores.py  # Lógica de cálculos
├── nuam_project/           # Configuración del proyecto
│   ├── settings.py         # Configuración Django
│   └── urls.py             # URLs principales
├── templates/              # Plantillas HTML
└── static/                 # Archivos estáticos

```

### Convenciones de Código

**Al agregar nuevas funciones de vista:**

1. **Ubicación:** Coloca la función en la sección apropiada de `views.py`
2. **Docstring:** Obligatorio en español, formato Google Style

   ```python
   def nueva_funcion(request):
       """
       Descripción breve de la función.

       Descripción más detallada si es necesario.

       Parámetros:
           request (HttpRequest): Objeto de solicitud Django.

       Retorna:
           HttpResponse: Respuesta renderizada con template.

       Excepciones:
           ValueError: Si los datos son inválidos.
       """
   ```

3. **Logging:** Agregar en puntos clave

   ```python
   logger.info(f"Usuario {request.user.username} realizó acción X")
   logger.error(f"Error en operación Y: {error}")
   ```

4. **Excepciones:** Manejar específicamente, nunca usar `except:` genérico

   ```python
   try:
       operacion()
   except ValueError as e:
       logger.warning(f"Validación fallida: {e}")
       messages.warning(request, "Datos inválidos")
   except Exception as e:
       logger.error(f"Error inesperado: {e}")
       messages.error(request, "Error del sistema")
   ```

5. **Formato:** Ejecutar Black antes de commit

   ```bash
   black calificaciones/views.py --line-length 100
   ```

6. **Auditoría:** Operaciones críticas deben crear `LogAuditoria`
   ```python
   LogAuditoria.objects.create(
       usuario=request.user,
       accion="CREAR",
       modelo="CalificacionTributaria",
       descripcion=f"Creó calificación ID {obj.id}",
       ip=obtener_ip_cliente(request)
   )
   ```

### Flujo de Trabajo con Git

```bash
# 1. Crear rama para feature
git checkout -b feature/nombre-descriptivo

# 2. Realizar cambios y aplicar formato
black calificaciones/views.py --line-length 100

# 3. Verificar cambios
git diff calificaciones/views.py

# 4. Commit descriptivo en español
git add calificaciones/views.py
git commit -m "Feature: Descripción clara del cambio

Detalles:
- Cambio 1
- Cambio 2

Afecta: Función X, Sección Y"

# 5. Push y crear PR
git push origin feature/nombre-descriptivo
```

### Testing

```bash
# Ejecutar tests
python manage.py test calificaciones

# Test específico
python manage.py test calificaciones.tests.test_calificaciones

# Con coverage
coverage run --source='calificaciones' manage.py test
coverage report
```

---

## 🚀 Instalación

Sigue estos pasos para configurar el entorno de desarrollo local.

### 1. Clonar el repositorio

```bash
git clone [https://github.com/Ewniah/nuam_project.git](https://github.com/Ewniah/nuam_project.git)
cd nuam_project
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv venv
```

- En Windows:

  ```bash
  venv\Scripts\activate
  ```

* En Linux/Mac:

  ```bash
  source venv/bin/activate
  ```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

1. Con el entorno virtual activado y en la carpeta del proyecto (donde está manage.py)

2. Genera una SECRET_KEY única:

3. Ejecuta:

```bash
python manage.py shell
```

4. Luego:

```bash
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

5. Presionar Enter y te dará la SECRET_KEY. Cópiala.

6. Sal del shell:

```bash
exit()

```

IMPORTANTE: Nunca compartas tu SECRET_KEY. Cada instalación debe tener su propia clave.

2. Crea el archivo .env con este contenido:

Crea un archivo .env en la raíz del proyecto (nuam_project/) con el siguiente contenido:

```bash
# Configuración de Django
SECRET_KEY=tu-secret-key-muy-segura-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Configuración de la Base de Datos (PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=nuam_calificaciones_db
DB_USER=postgres
DB_PASSWORD=tu-password-de-postgres-aqui
DB_HOST=localhost
DB_PORT=5432
```

    IMPORTANTE: El archivo .env ya está incluido en .gitignore para evitar que se suba a GitHub.

### 5. Crear la base de datos

Asegúrate de tener PostgreSQL en ejecución. Puedes usar psql o un cliente gráfico (como pgAdmin) para ejecutar:

```bash
CREATE DATABASE nuam_calificaciones_db;
```

### 6. Ejecutar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Crear datos iniciales y superusuario

```bash
# Carga los roles iniciales y otros datos necesarios
python manage.py crear_datos_iniciales

python manage.py poblar_sistema.py

# Crea tu cuenta de administrador
python manage.py createsuperuser
```

### 8. Asignar perfil al superusuario

El sistema requiere que cada User tenga un PerfilUsuario asociado. Ejecuta el shell de Django:

```bash
python manage.py shell
```

Y luego ejecuta el siguiente código Python (reemplaza 'tu_superusuario' con el username que creaste):

```bash
from django.contrib.auth.models import User
from calificaciones.models import PerfilUsuario, Rol

# --- Reemplaza 'tu_superusuario' con el nombre de usuario que creaste ---
try:
    admin = User.objects.get(username='tu_superusuario')

    rol_admin, created = Rol.objects.get_or_create(
        nombre_rol='Administrador',
        defaults={'descripcion': 'Acceso completo al sistema'}
    )

    PerfilUsuario.objects.create(
        usuario=admin,
        rol=rol_admin,
        departamento='Administración'
    )
    print(f"Perfil de Administrador creado exitosamente para {admin.username}.")

except User.DoesNotExist:
    print("Error: No se encontró el superusuario. Asegúrate de haberlo creado.")

exit()
```

### 9. Iniciar el servidor

```bash
python manage.py runserver
```

¡Listo! Accede al sistema en http://127.0.0.1:8000/.

👥 Usuarios de Prueba
Puedes usar las siguientes credenciales para probar los diferentes roles:

Usuario Contraseña Rol
admin admin123 Administrador
analista1 nuam2025 Analista Financiero
auditor1 nuam2025 Auditor

🔐 Roles y Permisos

- Administrador: Acceso completo al sistema, incluyendo gestión de usuarios y registro de auditoría.

- Analista Financiero: Puede crear y editar calificaciones e instrumentos, pero no puede eliminar.

- \*Auditor: Acceso de solo lectura a la mayoría del sistema, pero con acceso completo a los logs de auditoría.

🌐 URLs Principales

- Login: /login/

- Dashboard: / (Ruta raíz)

- Registro de Usuarios: /registro/

- Calificaciones: /calificaciones/

- Instrumentos: /instrumentos/

- Carga Masiva: /carga-masiva/

- Auditoría: /auditoria/

## 🌍 Deployment (Producción)

Para un despliegue en producción, recuerda:

1. Cambiar `DEBUG=False` en tu archivo `.env`
2. Configurar `ALLOWED_HOSTS` con tu dominio real
3. Configurar una base de datos de producción (PostgreSQL en RDS, etc.)
4. Ejecutar `python manage.py collectstatic` para recopilar archivos estáticos
5. Configurar logging a archivos en producción
6. Revisar configuración de seguridad (CSRF, CORS, HTTPS)

---

## 📝 Changelog

### Versión 2.1 (30 Nov 2025) - Refactorización Completa

**Unificación de Arquitectura**

- ✅ Consolidación de módulos de vistas en archivo único
- ✅ 30 funciones organizadas en 9 secciones funcionales
- ✅ Eliminación de código duplicado (1,400 líneas reducidas)
- ✅ Actualización y validación de 22 rutas URL
- ✅ Compatibilidad completa con versión anterior

**Mejoras de Código**

- ✅ Aplicación de estándares PEP 8 con herramientas de formateo
- ✅ Sistema de logging comprehensivo (27 puntos de registro)
- ✅ Manejo robusto de excepciones (15+ tipos específicos)
- ✅ Documentación completa de funciones (100%)
- ✅ Constantes de configuración centralizadas
- ✅ Eliminación de prácticas obsoletas
- ✅ Optimización de dependencias del proyecto

**Infraestructura de Testing**

- ✅ Scripts de generación de datos de prueba
- ✅ Herramientas de verificación de carga masiva
- ✅ Documentación de procesos de testing
- ✅ Suite de tests actualizada y validada

### Versión 2.0 (13 Nov 2025)

- ✅ Agregado registro de usuarios con asignación de roles
- ✅ Agregado registro de auditoría completo con filtros
- ✅ Implementado django-environ para gestión segura de variables
- ✅ Mejorada navegación con link de auditoría en navbar
- ✅ Actualizado README con nuevas funcionalidades

### Versión 1.0 (Inicial)

- ✅ CRUD de calificaciones e instrumentos
- ✅ Sistema de roles y permisos
- ✅ Dashboard con estadísticas
- ✅ Carga masiva y exportación

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Aplica Black formatter antes de commit
4. Escribe docstrings en español siguiendo el formato Google Style
5. Agrega logging apropiado y manejo de excepciones
6. Commit con mensajes descriptivos en español
7. Push a la rama (`git push origin feature/AmazingFeature`)
8. Abre un Pull Request

---

## 📄 Licencia

Este proyecto es propiedad de NUAM Exchange.

---

## 📧 Contacto

**NUAM Exchange**  
Sistema de Gestión de Calificaciones Tributarias  
Versión 2.1 - Noviembre 2025
