# 🔒 Política de Seguridad - Sistema NUAM

## Reporte de Vulnerabilidades

Si encuentras una vulnerabilidad de seguridad en este proyecto, por favor **NO** abras un issue público. En su lugar, contacta directamente al equipo de desarrollo.

---

## Gestión de Secretos y Credenciales

### ⚠️ NUNCA incluir en el repositorio:

- ❌ Contraseñas en texto plano
- ❌ Claves de API
- ❌ SECRET_KEY de Django
- ❌ Credenciales de base de datos
- ❌ Tokens de autenticación
- ❌ Certificados SSL privados

### ✅ Mejores prácticas implementadas:

1. **Variables de Entorno**: Usar archivo `.env` para configuración sensible
2. **`.gitignore`**: El archivo `.env` está excluido del repositorio
3. **`.env.example`**: Plantilla sin valores reales para referencia
4. **Scripts de Seeding**: Usar variables de entorno, no hardcodear passwords

---

## Configuración Segura en Desarrollo

### Archivo .env (LOCAL)

```bash
# Copiar .env.example a .env
cp .env.example .env

# Editar .env con tus valores reales
SECRET_KEY=tu-clave-secreta-generada-con-django
DB_PASSWORD=tu-password-postgres
DEFAULT_TEST_PASSWORD=password-temporal-desarrollo
```

### Generar SECRET_KEY Segura

```bash
python manage.py shell
>>> from django.core.management.utils import get_random_secret_key
>>> print(get_random_secret_key())
>>> exit()
```

---

## Configuración Segura en Producción

### Checklist de Seguridad

- [ ] `DEBUG=False` en `.env`
- [ ] `ALLOWED_HOSTS` configurado con dominio real
- [ ] SECRET_KEY única y compleja (50+ caracteres)
- [ ] Contraseñas de usuarios generadas con `secrets.token_urlsafe()`
- [ ] HTTPS obligatorio (certificado SSL válido)
- [ ] CSRF_COOKIE_SECURE=True
- [ ] SESSION_COOKIE_SECURE=True
- [ ] Base de datos con credenciales rotadas
- [ ] Backups automáticos configurados
- [ ] Monitoreo de seguridad activo (Sentry, etc.)

### Variables de Entorno en Producción

**Railway / Render:**

```bash
# Establecer en panel de configuración:
SECRET_KEY=<generada-por-django>
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
DB_PASSWORD=<password-compleja-generada>
```

**AWS / GCP:**

Usar servicios de gestión de secretos:

- AWS Secrets Manager
- GCP Secret Manager
- Azure Key Vault

---

## Scripts de Seeding - Seguridad

### Script `poblar_bd_maestra.py`

Este script está diseñado **ÚNICAMENTE para desarrollo y QA**.

**⚠️ NUNCA ejecutar en producción**

**Características de seguridad:**

1. **Contraseñas desde .env**: Lee `DEFAULT_TEST_PASSWORD` de variables de entorno
2. **Fallback seguro**: Si no existe la variable, genera password aleatoria
3. **Documentación clara**: README indica que es solo desarrollo

**Uso correcto:**

```bash
# Desarrollo local
DEFAULT_TEST_PASSWORD=nuam2025dev python scripts/poblar_bd_maestra.py

# O configurar en .env:
echo "DEFAULT_TEST_PASSWORD=nuam2025dev" >> .env
python scripts/poblar_bd_maestra.py
```

---

## Autenticación y Autorización

### Sistema RBAC Implementado

- **3 Roles**: Administrador, Analista Financiero, Auditor
- **Permisos granulares**: Por vista y modelo
- **Decoradores personalizados**: `@verificar_permisos_crud()`
- **Auditoría completa**: Todos los accesos registrados en `LogAuditoria`

### Bloqueo de Cuentas

- **Intentos fallidos máximos**: 5 (configurable)
- **Duración de bloqueo**: 30 minutos
- **Ventana de intentos**: 15 minutos
- **Registro de IPs**: Todos los intentos logged

---

## Protección contra Vulnerabilidades Comunes

### SQL Injection

✅ **Protegido**: Django ORM con queries parametrizadas

### XSS (Cross-Site Scripting)

✅ **Protegido**: Templates Django con auto-escaping

### CSRF (Cross-Site Request Forgery)

✅ **Protegido**: `{% csrf_token %}` en todos los formularios

### Inyección de Archivos

✅ **Protegido**: Validación de extensiones en carga masiva (.csv, .xlsx)

### Exposición de Información

✅ **Protegido**:

- DEBUG=False en producción
- Mensajes de error genéricos para usuarios
- Logging detallado solo en archivos (no en respuestas)

---

## Dependencias y Actualizaciones

### Actualizar Dependencias Regularmente

```bash
# Verificar vulnerabilidades conocidas
pip install --upgrade pip-audit
pip-audit

# Actualizar paquetes con parches de seguridad
pip install --upgrade django
pip install --upgrade psycopg2-binary

# Regenerar requirements.txt
pip freeze > requirements.txt
```

### Monitoreo de Seguridad

**Herramientas recomendadas:**

- **Dependabot** (GitHub): Actualizaciones automáticas
- **Snyk**: Escaneo de vulnerabilidades
- **GitGuardian**: Detección de secretos expuestos
- **Sentry**: Monitoreo de errores en producción

---

## Política de Contraseñas

### Usuarios Finales

- **Longitud mínima**: 8 caracteres
- **Requisitos**: Django default validators
  - No similar al username
  - No completamente numérica
  - No común (lista de passwords débiles)

### Administradores

- **Longitud mínima**: 12 caracteres
- **Requisitos adicionales**:
  - Mayúsculas + minúsculas
  - Números + caracteres especiales
  - Rotación cada 90 días (recomendado)

---

## Backup y Recuperación

### Backup de Base de Datos

```bash
# Backup encriptado
pg_dump nuam_calificaciones_db | gpg --encrypt --recipient admin@nuam.cl > backup.sql.gpg

# Backup en Railway/Render (automático)
# Verificar configuración en panel de control
```

### Plan de Recuperación ante Desastres

1. Backups automáticos diarios (Railway/Render)
2. Snapshots semanales (almacenamiento externo)
3. Procedimiento documentado de restore
4. Testing de restore mensual

---

## Contacto de Seguridad

Para reportar vulnerabilidades de seguridad:

📧 **Email**: security@nuam.cl (preferido)  
🔐 **PGP Key**: [Disponible bajo solicitud]

**Tiempo de respuesta**: 48 horas hábiles  
**SLA de parche crítico**: 7 días

---

## Historial de Incidentes

### Diciembre 2025: GitGuardian Alert

- **Fecha**: 1 de diciembre de 2025
- **Severidad**: Media
- **Descripción**: Contraseñas de prueba hardcodeadas en scripts
- **Acción tomada**:
  - Migración a variables de entorno
  - Creación de `.env.example`
  - Actualización de documentación
  - Git history sanitization (recomendado)
- **Estado**: Resuelto

---

**Última actualización**: 1 de diciembre de 2025  
**Versión del documento**: 1.0  
**Próxima revisión**: 1 de marzo de 2026
