# 🧪 Scripts de Prueba - Sistema NUAM

Este directorio contiene scripts para generar datos de prueba y verificar el funcionamiento del sistema de carga masiva.

## 📋 Contenido

### 1. `generar_datos_prueba.py`

Genera un archivo Excel con datos de ejemplo para probar la carga masiva.

**Características:**

- ✅ 20 registros de calificaciones tributarias
- ✅ 5 tipos diferentes de instrumentos financieros
- ✅ Mezcla de registros con MONTO y FACTOR
- ✅ Fechas distribuidas en los últimos 60 días
- ✅ Números de DJ únicos
- ✅ Algunas observaciones de ejemplo
- ✅ Formato Excel compatible con el sistema

**Uso:**

```bash
python scripts/generar_datos_prueba.py
```

**Salida:**

- Archivo: `datos_prueba_carga_masiva.xlsx`
- Ubicación: Raíz del proyecto

### 2. `verificar_carga.py`

Script de validación post-carga que verifica la integridad de los datos cargados.

**Funcionalidades:**

- ✅ Verifica el estado de la última carga masiva
- ✅ Lista instrumentos financieros creados
- ✅ Lista calificaciones tributarias creadas
- ✅ Muestra estadísticas por método de ingreso
- ✅ Verifica registros de auditoría
- ✅ Valida integridad de datos (foreign keys, campos requeridos)
- ✅ Compara con el archivo Excel original

**Uso:**

```bash
python scripts/verificar_carga.py
```

## 🚀 Proceso Completo de Prueba

### Paso 1: Generar archivo de prueba

```bash
# Desde la raíz del proyecto
python scripts/generar_datos_prueba.py
```

Esto creará el archivo `datos_prueba_carga_masiva.xlsx` con 20 registros de ejemplo.

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

4. Seleccionar el archivo `datos_prueba_carga_masiva.xlsx`

5. Hacer clic en **"Procesar Carga"**

6. Esperar el resultado del procesamiento

### Paso 3: Verificar la carga

```bash
# Ejecutar script de verificación
python scripts/verificar_carga.py
```

Este script mostrará:

- ✅ Estado de la carga (EXITOSO/PARCIAL/FALLIDO)
- 📊 Cantidad de registros procesados
- 📋 Lista de instrumentos creados
- 📋 Lista de calificaciones creadas
- 📈 Estadísticas por método de ingreso
- 🔍 Validación de integridad de datos
- 📊 Comparación con archivo original

## 📊 Formato del Archivo Excel

El archivo de carga masiva debe tener las siguientes columnas:

| Columna              | Tipo    | Requerido        | Descripción                                        |
| -------------------- | ------- | ---------------- | -------------------------------------------------- |
| `codigo_instrumento` | Texto   | ✅ Sí            | Código único del instrumento                       |
| `nombre_instrumento` | Texto   | ⚠️ Opcional      | Nombre descriptivo del instrumento                 |
| `tipo_instrumento`   | Texto   | ⚠️ Opcional      | Tipo: Bono, Depósito, Crédito, Pagaré, Letra, Otro |
| `monto`              | Número  | ⚠️ Condicional\* | Monto en pesos chilenos                            |
| `factor`             | Decimal | ⚠️ Condicional\* | Factor entre 0 y 1                                 |
| `metodo_ingreso`     | Texto   | ✅ Sí            | MONTO o FACTOR                                     |
| `numero_dj`          | Texto   | ⚠️ Opcional      | Número de Declaración Jurada                       |
| `fecha_informe`      | Fecha   | ✅ Sí            | Formato: YYYY-MM-DD                                |
| `observaciones`      | Texto   | ⚠️ Opcional      | Notas adicionales                                  |

**Nota:** \* Debe especificarse `monto` O `factor`, no ambos.

## 🔍 Validaciones del Sistema

El sistema realiza las siguientes validaciones durante la carga:

1. **Campos requeridos:**

   - `codigo_instrumento` no puede estar vacío
   - `fecha_informe` debe ser una fecha válida

2. **Validación condicional:**

   - Si `metodo_ingreso` = "MONTO", debe tener `monto` (no `factor`)
   - Si `metodo_ingreso` = "FACTOR", debe tener `factor` (no `monto`)

3. **Creación automática:**

   - Si el `codigo_instrumento` no existe, se crea automáticamente
   - Se asocia con el usuario que realiza la carga

4. **Auditoría:**
   - Cada carga se registra en `CargaMasiva`
   - Se registra en `LogAuditoria` con IP del usuario
   - Cada error se detalla en `errores_detalle`

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

---

**Fecha de creación:** Noviembre 30, 2025  
**Versión del sistema:** Django 5.2.8  
**Autor:** Sistema NUAM - Calificaciones Tributarias
