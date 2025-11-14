# Sistema NUAM - Gestión de Calificaciones Tributarias

<h3>Sistema web desarrollado en Django para la gestión de calificaciones tributarias de NUAM Exchange.</h3>

![Django](https://img.shields.io/badge/Django-5.1-092E20?logo=django)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-blue?logo=postgresql)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap)

---

## 📜 Descripción

Aplicación que permite gestionar **calificaciones tributarias** según las normativas **DJ 1922** y **DJ 1949** del SII de Chile. Incluye control de acceso por roles, carga masiva de datos, exportación de reportes y un registro completo de auditoría.

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

- **Backend:** Django 5.1, Python 3.10+
- **Base de Datos:** PostgreSQL
- **Frontend:** Bootstrap 5, Chart.js, Bootstrap Icons
- **Procesamiento de Datos:** pandas, openpyxl
- **Seguridad:** django-environ

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

🌍 Deployment (Producción)
Para un despliegue en producción, recuerda:

1. Cambiar DEBUG=False en tu archivo .env.

2. Configurar ALLOWED_HOSTS con tu dominio real.

3. Configurar una base de datos de producción (PostgreSQL en RDS, etc.).

4. Ejecutar python manage.py collectstatic para recopilar archivos estáticos.

5. Usar un servidor WSGI (como Gunicorn) y un servidor web (como Nginx).

🔄 Changelog
Versión 2.0 (13 Nov 2025) \* Agregado registro de usuarios con asignación de roles.

    * Agregado registro de auditoría completo con filtros.

    * Implementado django-environ para gestión segura de variables.

    * Mejorada navegación con link de auditoría en navbar.

    * Actualizado README con nuevas funcionalidades.

Versión 1.0 (Inicial) \* CRUD de calificaciones e instrumentos.

    * Sistema de roles y permisos.

    * Dashboard con estadísticas.

    * Carga masiva y exportación.
