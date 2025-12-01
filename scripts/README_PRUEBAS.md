# 🧪 Scripts de Prueba - Sistema NUAM

Este directorio contiene el script maestro para generar datos de prueba del sistema de carga masiva con 30 factores tributarios.

## 📋 Contenido

### `generar_datos_prueba.py` - Script Maestro Consolidado

**Versión:** 2.0 - Diciembre 2025

Genera archivo Excel con datos de prueba completos para testing de carga masiva con los 30 factores tributarios (8-37).

**Características:**

- ✅ **30 factores tributarios completos** (factor_8 a factor_37)
- ✅ **3 escenarios de validación:**
  - Golden Path: Todos los factores válidos (suma < 1)
  - Range Failure: factor_37 = 5.0 (fuera de rango 0-1)
  - Sum Failure: Suma de factores 8-16 > 1.0 (violación REGLA B)
- ✅ Formato Excel (.xlsx) con estilos profesionales
- ✅ Headers dinámicos con metadata + 30 factores + observaciones
- ✅ Validación automática de reglas de negocio
- ✅ Instrumentos financieros creados en BD

**Uso:**

```bash
python scripts/generar_datos_prueba.py
```

**Salida:**

- Archivo: `test_30factores_completo.xlsx`
- Ubicación: Raíz del proyecto
- Contenido: 3 filas de prueba (Golden, Range Fail, Sum Fail)

## 🚀 Proceso Completo de Prueba

### Paso 1: Generar archivo de prueba

```bash
# Desde la raíz del proyecto
python scripts/generar_datos_prueba.py
```

Esto creará el archivo `test_30factores_completo.xlsx` con 3 escenarios de prueba.

### Paso 2: Subir archivo mediante interfaz web

1. Iniciar el servidor de desarrollo:

   ```bash
   python manage.py runserver
   ```

2. Acceder al sistema:

   - URL: http://127.0.0.1:8000/
   - Usuario: `admin`
   - Contraseña: `admin123`

3. Ir a la sección de **Carga Masiva**:

   - URL directa: http://127.0.0.1:8000/carga-masiva/

4. Seleccionar el archivo `test_30factores_completo.xlsx`

5. Hacer clic en **"Procesar Carga"**

6. Esperar el resultado del procesamiento

### Paso 3: Verificar resultados

**Resultados esperados:**

- ✅ **Fila 1 (Golden Path):** Carga exitosa
- ❌ **Fila 2 (Range Failure):** Error de validación (factor_37 = 5.0 fuera de rango)
- ❌ **Fila 3 (Sum Failure):** Error de validación (suma de factores 8-16 > 1.0)

**Verificación manual:**

1. Ir a **Dashboard** → Ver estadísticas de calificaciones
2. Ir a **Calificaciones** → Verificar los 30 factores en la grilla
3. Ir a **Auditoría** → Revisar logs de carga masiva

## 📊 Formato del Archivo Excel

El archivo de carga masiva con 30 factores debe tener las siguientes columnas:

### Columnas de Metadata

| Columna              | Tipo   | Requerido   | Descripción                      |
| -------------------- | ------ | ----------- | -------------------------------- |
| `codigo_instrumento` | Texto  | ✅ Sí       | Código único del instrumento     |
| `fecha_informe`      | Fecha  | ✅ Sí       | Formato: YYYY-MM-DD              |
| `ejercicio`          | Número | ⚠️ Opcional | Año fiscal (4 dígitos)           |
| `secuencia`          | Número | ⚠️ Opcional | Secuencia (10 dígitos)           |
| `tipo_sociedad`      | Texto  | ⚠️ Opcional | Tipo de sociedad                 |
| `fecha_pago`         | Fecha  | ⚠️ Opcional | Fecha de pago del dividendo      |
| `numero_dividendo`   | Número | ⚠️ Opcional | Número de dividendo (10 dígitos) |
| `origen`             | Texto  | ⚠️ Opcional | BOLSA / CORREDORA                |
| `fuente_origen`      | Texto  | ⚠️ Opcional | MANUAL / MASIVA                  |
| `mercado`            | Texto  | ⚠️ Opcional | Código de mercado (3 caracteres) |
| `observaciones`      | Texto  | ⚠️ Opcional | Notas adicionales                |

### Columnas de Factores (30 factores)

| Columna                   | Tipo    | Rango | Descripción                             |
| ------------------------- | ------- | ----- | --------------------------------------- |
| `factor_8`                | Decimal | 0-1   | Con crédito por IDPC ≥ 01.01.2017       |
| `factor_9`                | Decimal | 0-1   | Con crédito por IDPC ≤ 31.12.2016       |
| `factor_10` a `factor_37` | Decimal | 0-1   | Factores tributarios según DJ 1949/1922 |

**Nota:** La suma de factores 8-16 debe ser ≤ 1.00000000 (REGLA B)

## 🔍 Validaciones del Sistema

El sistema realiza las siguientes validaciones durante la carga:

### 1. Validaciones de Campos Requeridos

- ✅ `codigo_instrumento` no puede estar vacío
- ✅ `fecha_informe` debe ser una fecha válida

### 2. Validaciones de Factores (REGLA A)

- ✅ Cada factor debe estar entre 0 y 1
- ✅ Factores deben tener máximo 8 decimales
- ✅ Al menos un factor debe ser mayor que 0

### 3. Validación de Suma (REGLA B)

- ✅ La suma de factores 8-16 debe ser ≤ 1.00000000
- ✅ Validación automática al guardar

### 4. Regla de Prioridad (CORREDORA > BOLSA)

- ✅ Si existe calificación con mismo instrumento + fecha
- ✅ CORREDORA tiene prioridad sobre BOLSA
- ✅ Se omite la fila si ya existe con mayor prioridad

### 5. Creación Automática de Instrumentos

- ✅ Si `codigo_instrumento` no existe, se crea automáticamente
- ✅ Se asocia con el usuario que realiza la carga

### 6. Auditoría Completa

- ✅ Cada carga se registra en `CargaMasiva`
- ✅ Se registra en `LogAuditoria` con IP del usuario
- ✅ Cada error se detalla en `errores_detalle`

## 📈 Interpretación de Resultados

### Estado EXITOSO ✅

- Todos los registros fueron procesados correctamente
- 0 errores detectados
- Todos los datos están en la base de datos

### Estado PARCIAL ⚠️

- Algunos registros fueron procesados correctamente
- Algunos registros fallaron (ver detalles de errores)
- Se recomienda revisar y corregir los registros fallidos

### Estado FALLIDO ❌

- Ningún registro fue procesado
- Error crítico en el archivo o formato
- Revisar el archivo y volver a intentar

## 🛠️ Troubleshooting

### Error: "Campo requerido faltante"

**Causa:** Falta una columna obligatoria en el Excel
**Solución:** Asegúrate de que el archivo tenga todas las columnas requeridas

### Error: "Valor inválido"

**Causa:** Formato de dato incorrecto (ej: texto en campo numérico)
**Solución:** Verifica que los tipos de datos sean correctos

### Error: "Formato de archivo no soportado"

**Causa:** El archivo no es .xlsx o .csv
**Solución:** Convierte el archivo a formato Excel (.xlsx) o CSV

## 📝 Logs del Sistema

El sistema genera logs detallados en:

- **Logs de aplicación:** Console output del servidor Django
- **Base de datos:**
  - Tabla `calificaciones_cargamasiva`: Historial de cargas
  - Tabla `calificaciones_logauditoria`: Registro de auditoría

Para ver logs en tiempo real:

```bash
# El servidor muestra logs automáticamente
python manage.py runserver

# Ver logs de carga masiva en BD
python manage.py shell
>>> from calificaciones.models import CargaMasiva
>>> CargaMasiva.objects.order_by('-fecha_carga').first()
```

## 🎯 Próximos Pasos

Después de una carga exitosa, puedes:

1. **Ver las calificaciones:**

   - http://127.0.0.1:8000/calificaciones/

2. **Ver instrumentos:**

   - http://127.0.0.1:8000/instrumentos/

3. **Ver auditoría:**

   - http://127.0.0.1:8000/auditoria/

4. **Exportar datos:**

   - Usar funcionalidad de exportación a Excel/CSV

5. **Generar reportes:**
   - Dashboard con gráficas y estadísticas

## 📦 Consolidación de Scripts

**Versión 2.0 - Diciembre 2025**

Este README refleja la consolidación de múltiples scripts de prueba en un único script maestro:

- ❌ `generar_test_30factores.py` → Consolidado
- ❌ `generar_test_final.py` → Consolidado
- ❌ `mostrar_excel.py` → Eliminado (temporal)
- ❌ `verificar_carga.py` → Eliminado (temporal)
- ✅ `generar_datos_prueba.py` → **Script Maestro Único**

---

**Última actualización:** Diciembre 1, 2025  
**Versión del sistema:** Django 5.2.8  
**Autor:** Sistema NUAM - Calificaciones Tributarias
