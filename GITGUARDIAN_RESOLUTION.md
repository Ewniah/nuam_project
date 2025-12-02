# 🔐 Resolución de Alerta GitGuardian - Credenciales Expuestas

**Fecha**: 1 de diciembre de 2025  
**Severidad**: MEDIA  
**Estado**: RESUELTO

---

## 📋 Descripción del Problema

GitGuardian detectó contraseñas de prueba hardcodeadas en el repositorio GitHub `Ewniah/nuam_project`, específicamente en el commit del 1 de diciembre de 2025 a las 22:55:40 UTC.

**Archivos afectados:**

- `scripts/poblar_bd_maestra.py` - Contraseñas en texto plano en diccionario `usuarios_config`
- `scripts/README_SEEDING.md` - Tabla con credenciales de usuarios de prueba
- `README.md` - Tabla con credenciales de demostración

**Tipo de secreto detectado**: Company Email Password

---

## ⚠️ Análisis de Riesgo

### Contexto

Las contraseñas detectadas son **únicamente para entornos de desarrollo y QA**:

- `admin123`, `analista123`, `auditor123`, `demo123`
- Usuarios: admin, analista1, analista2, auditor1, demo
- Dominio: `@nuam.cl` (interno)

### Impacto Real

- ✅ **BAJO**: No hay datos reales en producción afectados
- ✅ **BAJO**: Las contraseñas son solo para base de datos de desarrollo local
- ✅ **BAJO**: No se expusieron claves API, tokens de autenticación, o SECRET_KEY real
- ⚠️ **MEDIO**: Mala práctica de seguridad - hardcodear contraseñas en código

### Riesgo si no se corrige

- Alguien podría usar estas credenciales si el sistema se despliega con el script de seeding sin cambiar passwords
- Violación de mejores prácticas de desarrollo seguro
- Acumulación de alertas de seguridad que dificultan detectar problemas reales

---

## ✅ Solución Implementada

### 1. Migración a Variables de Entorno

**Archivo modificado**: `scripts/poblar_bd_maestra.py`

```python
# ANTES (INSEGURO):
usuarios_config = [
    {
        'username': 'admin',
        'password': 'admin123',  # ❌ Hardcodeado
        # ...
    }
]

# DESPUÉS (SEGURO):
import os
from django.core.management.utils import get_random_secret_key

DEFAULT_TEST_PASSWORD = os.getenv('DEFAULT_TEST_PASSWORD', get_random_secret_key()[:12])

usuarios_config = [
    {
        'username': 'admin',
        'password': DEFAULT_TEST_PASSWORD,  # ✅ Desde variable de entorno
        # ...
    }
]
```

### 2. Creación de `.env.example`

**Archivo creado**: `.env.example`

```bash
# Plantilla sin valores reales
DEFAULT_TEST_PASSWORD=nuam2025dev

# NOTA: Copiar a .env y establecer contraseña real
```

### 3. Actualización de Documentación

**Archivos modificados**:

- `README.md` - Tabla de usuarios actualizada (sin contraseñas hardcodeadas)
- `scripts/README_SEEDING.md` - Instrucciones de configuración con `.env`

**Nueva tabla de usuarios**:

| Usuario   | Rol                 | Contraseña         |
| --------- | ------------------- | ------------------ |
| admin     | Administrador       | Ver archivo `.env` |
| analista1 | Analista Financiero | Ver archivo `.env` |
| ...       | ...                 | ...                |

### 4. Creación de SECURITY.md

**Archivo creado**: `SECURITY.md`

Documenta:

- Política de gestión de secretos
- Mejores prácticas de seguridad
- Configuración segura en desarrollo y producción
- Historial de incidentes de seguridad
- Contacto para reportar vulnerabilidades

### 5. Verificación de .gitignore

**Confirmado**: `.env` ya está en `.gitignore`

```ignore
# Environment variables - IMPORTANTE para django-environ
.env
.env.local
.env.*.local
.env.production
.env.development
```

---

## 🔧 Instrucciones para Desarrolladores

### Configuración en Desarrollo

```bash
# 1. Copiar plantilla
cp .env.example .env

# 2. Editar .env y establecer contraseña
nano .env

# 3. Agregar línea:
DEFAULT_TEST_PASSWORD=tu_password_desarrollo_aqui

# 4. Ejecutar script de seeding
python scripts/poblar_bd_maestra.py
```

### Configuración en Producción

**⚠️ NUNCA ejecutar script de seeding en producción**

Crear usuarios manualmente con contraseñas seguras:

```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@nuam.cl
# Password: [GENERAR CON HERRAMIENTA SEGURA]
```

---

## 🧹 Limpieza del Historial de Git (OPCIONAL)

**⚠️ ADVERTENCIA**: Esta operación reescribe el historial de Git y puede causar problemas si otros desarrolladores tienen clones del repositorio.

### Opción 1: BFG Repo-Cleaner (Recomendado)

```bash
# Instalar BFG
# macOS: brew install bfg
# Windows: descargar JAR de https://rtyley.github.io/bfg-repo-cleaner/

# Crear lista de contraseñas a eliminar
echo "admin123" > passwords.txt
echo "analista123" >> passwords.txt
echo "auditor123" >> passwords.txt
echo "demo123" >> passwords.txt

# Ejecutar BFG
bfg --replace-text passwords.txt

# Limpiar referencias
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (CUIDADO)
git push --force
```

### Opción 2: git filter-branch (Método manual)

```bash
# Filtrar archivos específicos
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch scripts/poblar_bd_maestra.py" \
  --prune-empty --tag-name-filter cat -- --all

# Force push
git push origin --force --all
```

### Opción 3: NO hacer nada (Recomendado para este caso)

**Razón**: Las contraseñas son solo para desarrollo local y ya están mitigadas con la solución implementada.

**Ventajas**:

- No rompe clones existentes
- No requiere coordinación con equipo
- El commit actual con el fix queda documentado en historial

---

## 📊 Verificación Post-Fix

### Checklist de Validación

- [x] Contraseñas eliminadas del código fuente
- [x] Variables de entorno implementadas
- [x] `.env.example` creado como plantilla
- [x] `.gitignore` incluye `.env`
- [x] Documentación actualizada (README, README_SEEDING)
- [x] SECURITY.md creado
- [x] Script de seeding funcional con nueva configuración
- [ ] GitGuardian alert marcada como "False Positive" o "Fixed"
- [ ] (Opcional) Historial de Git limpiado

### Testing del Fix

```bash
# 1. Configurar .env
echo "DEFAULT_TEST_PASSWORD=test123" > .env

# 2. Ejecutar script
python scripts/poblar_bd_maestra.py

# 3. Verificar que se crearon usuarios
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.count()
5
>>> exit()

# 4. Probar login
python manage.py runserver
# Navegar a http://127.0.0.1:8000/login/
# Username: admin
# Password: test123 (la que estableciste en .env)
```

---

## 🎯 Acciones en GitGuardian

### Marcar el Incidente

1. Ir al email de GitGuardian
2. Click en "Fix this secret leak"
3. Seleccionar acción:
   - ✅ **"Mark as Fixed"** - Si se implementó la solución
   - ⚠️ **"Mark as False Positive"** - Si consideras que no es un riesgo real

### Justificación para "Mark as Fixed"

- Contraseñas eliminadas del código fuente
- Migración a variables de entorno completada
- Documentación de seguridad implementada
- `.env` correctamente en `.gitignore`
- Script funcional con nueva configuración

### Justificación para "Mark as False Positive"

- Contraseñas solo para desarrollo local (no producción)
- No hay datos sensibles reales expuestos
- Sistema requiere configuración adicional para funcionar

**Recomendación**: Usar **"Mark as Fixed"** y mantener registro en SECURITY.md

---

## 📚 Lecciones Aprendidas

### ✅ Mejores Prácticas Aplicadas

1. **Nunca hardcodear secretos** - Usar variables de entorno
2. **Documentar configuración** - Crear `.env.example` sin valores reales
3. **Separar entornos** - Diferenciar desarrollo/producción
4. **Auditar código** - Revisar antes de commits públicos
5. **Respuesta rápida** - Corregir alertas de seguridad inmediatamente

### 🔄 Mejoras Futuras

- [ ] Implementar pre-commit hooks para detectar secretos
- [ ] Usar herramientas como `detect-secrets` en CI/CD
- [ ] Considerar servicios de gestión de secretos (AWS Secrets Manager)
- [ ] Añadir tests de seguridad automatizados
- [ ] Rotación automática de credenciales en producción

---

## 📞 Referencias y Contacto

**Documentación relacionada**:

- `SECURITY.md` - Política de seguridad completa
- `.env.example` - Plantilla de configuración
- `scripts/README_SEEDING.md` - Guía de seeding con .env

**Herramientas utilizadas**:

- GitGuardian - https://www.gitguardian.com/
- django-environ - https://django-environ.readthedocs.io/

**Contacto de seguridad**: security@nuam.cl

---

**Última actualización**: 1 de diciembre de 2025  
**Responsable**: Equipo de Desarrollo NUAM  
**Estado**: RESUELTO ✅
