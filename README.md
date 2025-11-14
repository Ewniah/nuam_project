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
