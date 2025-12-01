# 🌱 Database Reset & Master Seeding - NUAM Calificaciones

## 📋 Resumen

Este documento describe el proceso completo para limpiar la base de datos y poblarla con un dataset "Golden" profesional para demostración y QA.

---

## 🗑️ PASO 1: Flush Database (Limpiar BD)

**¿Qué hace?**

- Elimina TODOS los datos de la base de datos
- Mantiene el esquema (tablas, columnas, relaciones)
- Mantiene las migraciones aplicadas
- NO elimina la estructura

**Comando:**

```bash
python manage.py flush --no-input
```

**Salida esperada:**

```
Flushing...
Installing custom SQL ...
Installing indexes ...
Loaded 0 object(s) from 0 fixture(s)
```

**⚠️ ADVERTENCIA:** Esta operación es IRREVERSIBLE. Todos los datos actuales se perderán.

---

## 🌱 PASO 2: Poblar Base de Datos Maestra

**¿Qué hace?**

- Crea roles y usuarios con permisos RBAC
- Crea instrumentos financieros variados
- Crea calificaciones con 30 factores completos
- Genera historial de cargas masivas (últimos 7 días)
- Genera logs de auditoría (últimos 30 días)
- Genera intentos de login (últimos 15 días)

**Comando:**

```bash
python scripts/poblar_bd_maestra.py
```

**Tiempo estimado:** 10-15 segundos

---

## 📊 Dataset Golden Generado

### 3 Roles RBAC

| Rol                 | Permisos                           |
| ------------------- | ---------------------------------- |
| Administrador       | Acceso total, gestión de usuarios  |
| Analista Financiero | CRUD calificaciones e instrumentos |
| Auditor             | Solo lectura, acceso a auditoría   |

### 5 Usuarios

| Username    | Password      | Rol                 | Email             |
| ----------- | ------------- | ------------------- | ----------------- |
| `admin`     | `admin123`    | Administrador       | admin@nuam.cl     |
| `analista1` | `analista123` | Analista Financiero | analista1@nuam.cl |
| `analista2` | `analista123` | Analista Financiero | analista2@nuam.cl |
| `auditor1`  | `auditor123`  | Auditor             | auditor1@nuam.cl  |
| `demo`      | `demo123`     | Administrador       | demo@nuam.cl      |

### 14 Instrumentos Financieros

**Acciones (5):**

- Banco de Chile (BCH-2024)
- Empresas CMPC S.A. (CMPC-2024)
- Copec S.A. (COPEC-2024)
- Sociedad Química y Minera (SQMB-2024)
- Cencosud S.A. (CENCOSUD-2024)

**Bonos (3):**

- Bono Tesorería General 2025
- Bono Corporativo Entel
- Bono Banco BCI 2026

**Fondos (2):**

- Fondo Independencia (CFI-INDEP)
- Fondo BCI Moneda Chilena (CFI-MONEDA)

**Depósitos (2):**

- Depósito a Plazo Santander
- Depósito a Plazo Itaú

**Otros (2):**

- Pagaré Empresa XYZ
- Letra de Cambio ABC

### 30 Calificaciones Tributarias

**Características:**

- ✅ **30 factores completos** (factor_8 a factor_37)
- ✅ Factores con valores realistas (0.001 - 0.08)
- ✅ **REGLA A cumplida:** Todos los factores entre 0 y 1
- ✅ **REGLA B cumplida:** Suma factores 8-16 ≤ 1.0
- ✅ Mix de orígenes: BOLSA / CORREDORA
- ✅ Mix de fuentes: MANUAL / MASIVA
- ✅ DJ 1922 y DJ 1949
- ✅ Fechas distribuidas en últimos 90 días
- ✅ Metadata completa (secuencia, dividendo, tipo sociedad, mercado, ejercicio)

### 10 Cargas Masivas

**Distribución temporal:** Últimos 7 días

**Estados:**

- ✅ EXITOSO (60% aprox.)
- ⚠️ PARCIAL (20% aprox.)
- ❌ FALLIDO (20% aprox.)

**Propósito:** Alimentar gráfico Chart.js del Dashboard

### 50 Logs de Auditoría

**Tipos de acciones:**

- LOGIN / LOGOUT
- CREATE / UPDATE / DELETE
- BULK_UPLOAD
- EXPORT

**Distribución temporal:** Últimos 30 días

**Propósito:** Tabla de actividad reciente en Dashboard

### 20 Intentos de Login

**Mix:**

- Logins exitosos (usuarios legítimos)
- Logins fallidos (credenciales incorrectas)
- Intentos sospechosos (usernames inválidos)

**Distribución temporal:** Últimos 15 días

---

## 🧪 Verificación Post-Seeding

Después de ejecutar el script, verificar que todo se creó correctamente:

```bash
python manage.py shell
```

```python
from calificaciones.models import *
from django.contrib.auth.models import User

# Verificar conteos
print(f"Roles: {Rol.objects.count()}")
print(f"Usuarios: {User.objects.count()}")
print(f"Instrumentos: {InstrumentoFinanciero.objects.count()}")
print(f"Calificaciones: {CalificacionTributaria.objects.count()}")
print(f"Cargas Masivas: {CargaMasiva.objects.count()}")
print(f"Logs Auditoría: {LogAuditoria.objects.count()}")
print(f"Intentos Login: {IntentoLogin.objects.count()}")

# Verificar una calificación con 30 factores
cal = CalificacionTributaria.objects.first()
print(f"\nFactores de calificación #{cal.id}:")
for i in range(8, 38):
    valor = getattr(cal, f'factor_{i}')
    print(f"  factor_{i}: {valor}")
```

**Salida esperada:**

```
Roles: 3
Usuarios: 5
Instrumentos: 14
Calificaciones: 30
Cargas Masivas: 10
Logs Auditoría: 50
Intentos Login: 20

Factores de calificación #1:
  factor_8: 0.02345678
  factor_9: 0.01234567
  ...
  factor_37: 0.00987654
```

---

## 🚀 Comandos Completos (Secuencia)

```bash
# 1. Limpiar base de datos
python manage.py flush --no-input

# 2. Poblar con dataset Golden
python scripts/poblar_bd_maestra.py

# 3. Iniciar servidor para verificar
python manage.py runserver

# 4. Acceder al sistema
# URL: http://127.0.0.1:8000/
# Login: admin / admin123
```

---

## ✅ Validación del Dashboard

Después del seeding, el Dashboard debe mostrar:

1. **Métricas principales:**

   - Total de calificaciones: ~30
   - Total de instrumentos: ~14
   - Cargas masivas (últimos 7 días): ~10

2. **Gráfico Chart.js:**

   - Barras con datos de últimos 7 días
   - Estados: EXITOSO, PARCIAL, FALLIDO

3. **Tabla de actividad reciente:**

   - Últimos 10 logs de auditoría
   - Acciones variadas (LOGIN, CREATE, UPDATE, etc.)

4. **Grilla de calificaciones:**
   - 30 factores visibles (factor_8 a factor_37)
   - Valores decimales pequeños (0.001 - 0.08)
   - Columnas de metadata pobladas

---

## 🔧 Troubleshooting

### Error: "Base de datos no vacía"

El script detecta si hay >10 calificaciones y pide confirmación.

**Solución:** Ejecutar flush primero:

```bash
python manage.py flush --no-input
```

### Error: "No module named 'calificaciones'"

**Causa:** Django no está configurado correctamente.

**Solución:** Verificar que estás en el directorio raíz del proyecto:

```bash
cd C:\Users\Bryan\Desktop\nuam_project-1
python scripts/poblar_bd_maestra.py
```

### Error: "Validation error: suma de factores > 1.0"

**Causa:** Bug en generación de factores (muy poco probable).

**Solución:** Re-ejecutar el script:

```bash
python scripts/poblar_bd_maestra.py
```

---

## 📝 Notas Técnicas

### Generación de Factores

El script usa `generar_factores_validos()` que:

1. Genera factores 8-16 con suma < 1.0 (REGLA B)
2. Si la suma excede 1.0, ajusta proporcionalmente
3. Genera factores 17-37 independientes
4. Todos los factores entre 0 y 1 (REGLA A)
5. Precisión: 8 decimales

### Idempotencia

El script NO es completamente idempotente:

- Si se ejecuta múltiples veces, creará registros duplicados
- Usuarios e instrumentos se protegen con `get_or_create()`
- Calificaciones, logs y cargas siempre se crean nuevos

**Recomendación:** Ejecutar flush antes de cada seeding.

### Transaccionalidad

El script NO usa transacciones explícitas:

- Si falla a mitad, algunos datos quedarán en BD
- Para limpieza completa, ejecutar flush y reintentar

---

**Última actualización:** Diciembre 1, 2025  
**Versión:** 1.0  
**Autor:** Sistema NUAM - Calificaciones Tributarias
