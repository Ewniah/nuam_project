# Sistema NUAM - Gestión de Calificaciones Tributarias

Sistema web desarrollado en Django para la gestión de calificaciones tributarias de instrumentos financieros para NUAM Exchange.

## 📋 Descripción

Aplicación que permite gestionar calificaciones tributarias según normativas DJ 1922 y DJ 1949 del SII de Chile, con control de acceso por roles, carga masiva de datos y exportación de reportes.

## ✨ Características

- ✅ CRUD de calificaciones tributarias e instrumentos
- ✅ Cálculo automático entre monto y factor
- ✅ Sistema de roles (Administrador, Analista, Auditor)
- ✅ Carga masiva desde CSV/Excel
- ✅ Exportación a Excel/CSV
- ✅ Dashboard con estadísticas y gráficos
- ✅ Registro de auditoría
- ✅ Formato chileno (CLP)

## 🛠️ Tecnologías

- **Backend**: Django 5.1, Python 3.10+
- **Base de Datos**: PostgreSQL
- **Frontend**: Bootstrap 5, Chart.js
- **Procesamiento**: pandas, openpyxl

## 📦 Instalación

### 1. Clonar repositorio

git clone https://github.com/tu-usuario/nuam_project.git
cd sistema-nuam

### 2. Crear entorno virtual

python -m venv venv
venv\Scripts\activate # Windows
source venv/bin/activate # Linux/Mac

### 3. Instalar dependencias

pip install -r requirements.txt

### 4. Configurar base de datos

Editar `nuam_project/settings.py`:

DATABASES = {
'default': {
'ENGINE': 'django.db.backends.postgresql',
'NAME': 'nuam_db',
'USER': 'tu_usuario',
'PASSWORD': 'tu_contraseña',
'HOST': 'localhost',
'PORT': '5432',
}
}

### 5. Ejecutar migraciones

python manage.py makemigrations
python manage.py migrate

### 6. Crear datos iniciales

python manage.py crear_datos_iniciales
python manage.py createsuperuser

### 7. Iniciar servidor

python manage.py runserver

Acceder a: http://127.0.0.1:8000/

## 👥 Usuarios de Prueba

| Usuario   | Contraseña | Rol           |
| --------- | ---------- | ------------- |
| admin     | admin123   | Administrador |
| analista1 | nuam2025   | Analista      |
| auditor1  | nuam2025   | Auditor       |

## 🔐 Roles y Permisos

**Administrador**: Acceso completo  
**Analista Financiero**: Crear/editar (no eliminar)  
**Auditor**: Solo lectura + logs

## 📝 Uso Básico

1. **Ingresar calificación por monto**: Sistema calcula factor automáticamente
2. **Ingresar calificación por factor**: Sistema calcula monto automáticamente
3. **Carga masiva**: Importar múltiples registros desde CSV/Excel
4. **Exportar**: Descargar reportes en Excel o CSV

## 📄 Licencia

Proyecto Integrado - NUAM Exchange 2025

## 👨‍💻 Autor

Bryan Alegría Pastén - Proyecto Integrado 2025

---

**© 2025 Sistema NUAM**
