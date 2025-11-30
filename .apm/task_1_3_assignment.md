---
task_ref: "Task 1.3 - Execute View Unification and Code Consolidation"
agent_assignment: "Agent_Refactor"
memory_log_path: ".apm/Memory/Phase_01_Analysis_Refactoring_Unification/Task_1_3_View_Unification_Execution.md"
execution_type: "implementation"
dependency_context: true
ad_hoc_delegation: false
---

# APM Task Assignment: Execute View Unification and Code Consolidation

## Task Reference

Implementation Plan: **Task 1.3 - Execute View Unification and Code Consolidation** assigned to **Agent_Refactor**

## Context from Previous Tasks

**Task 1.1 (Initial Codebase Analysis) - COMPLETE ✅**

- Technical audit report documented 24 functions across 3 view files
- Total: 1,133 lines (views.py: 856, views_admin.py: 119, views_factores.py: 158)
- Identified duplicate: `obtener_ip_cliente()` in views.py and views_factores.py
- 22 URL routes mapped (all must be preserved)

**Task 1.2 (Unification Strategy) - COMPLETE ✅ [USER APPROVED]**

- 9-section organization structure designed
- 20-step migration sequence with git checkpoints
- Import consolidation: 31 statements → 19 (39% reduction)
- Duplicate resolution: Consolidate `obtener_ip_cliente()`, keep parallel CRUD workflows
- urls.py changes: 9 specific edits documented
- Route preservation: 100% (22/22 routes must work)

## Objective

Execute the approved unification strategy by consolidating three view files (`views.py`, `views_admin.py`, `views_factores.py`) into a single unified `views.py` following the 9-section structure, updating `urls.py` accordingly, and verifying that all 22 URL routes remain functional with 100% backward compatibility.

## Detailed Instructions

This is an **IMPLEMENTATION TASK** requiring systematic execution of the approved 20-step migration plan. Execute in the following sequence:

### Phase 1: Preparation and Backup (Steps 1-3)

**Step 1: Create Git Checkpoint**

```powershell
cd C:\Users\Bryan\Desktop\nuam_project-1
git add -A
git commit -m "Pre-unification checkpoint - Task 1.3 baseline"
git log --oneline -1  # Verify commit created
```

**Step 2: Create Backup Copies**

```powershell
# Backup all three view files
Copy-Item calificaciones\views.py calificaciones\views_backup_original.py
Copy-Item calificaciones\views_admin.py calificaciones\views_admin_backup.py
Copy-Item calificaciones\views_factores.py calificaciones\views_factores_backup.py

# Backup urls.py
Copy-Item calificaciones\urls.py calificaciones\urls_backup.py

# Verify backups created
Get-ChildItem calificaciones\*backup*.py
```

**Step 3: Create Unified Template File**

Create `calificaciones/views_unified.py` with:

1. Complete file header comment with metadata
2. Consolidated imports (19 lines, PEP 8 organized)
3. Section header comments for 9 sections
4. Empty structure ready for function migration

**Template Structure:**

```python
"""
Unified View Module for NUAM Calificaciones System
Consolidated from: views.py, views_admin.py, views_factores.py
Migration Date: 2025-11-30
Task: 1.3 - View Unification
Total Functions: 30 (22 routed + 6 utilities + 2 helpers)
Total Routes: 22 (100% preserved)
"""

# ============================================================================
# IMPORTS - PEP 8 Organized
# ============================================================================

# Standard Library (5 imports)
import csv
import io
import json
from datetime import datetime, timedelta
from decimal import Decimal

# Django Core (9 imports)
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

# Third-Party (1 import)
import openpyxl

# Local Application (4 imports)
from .forms import (
    CalificacionTributariaForm, InstrumentoForm, UsuarioRegistroForm,
    CalificacionFactoresSimpleForm
)
from .models import (
    CalificacionTributaria, InstrumentoCalificacion, LogAuditoria,
    IntentosLogin, ArchivoCargado
)
from .permissions import requiere_permiso
from .utils.calculadora_factores import calcular_clasificacion_sii

# ============================================================================
# SECTION 1: UTILITIES AND HELPERS
# ============================================================================
# Functions: obtener_ip_cliente, verificar_cuenta_bloqueada,
#            registrar_intento_login, verificar_intentos_fallidos,
#            procesar_excel, procesar_csv
# Lines: 40-150 (approx. 110 lines)
# ============================================================================

# [Functions will be migrated here in Step 4]

# ============================================================================
# SECTION 2: AUTHENTICATION AND SECURITY
# ============================================================================
# Functions: login_view, logout_view
# Lines: 151-350 (approx. 200 lines)
# ============================================================================

# [Functions will be migrated here in Step 5]

# ============================================================================
# SECTION 3: DASHBOARD AND REPORTING
# ============================================================================
# Functions: dashboard
# Lines: 351-500 (approx. 150 lines)
# ============================================================================

# [Functions will be migrated here in Step 6]

# ============================================================================
# SECTION 4: CALIFICACIONES CRUD OPERATIONS
# ============================================================================
# Functions: listar_calificaciones, crear_calificacion, editar_calificacion,
#            eliminar_calificacion, crear_calificacion_factores,
#            editar_calificacion_factores
# Lines: 501-850 (approx. 350 lines)
# ============================================================================

# [Functions will be migrated here in Steps 7-8]

# ============================================================================
# SECTION 5: INSTRUMENTOS CRUD OPERATIONS
# ============================================================================
# Functions: listar_instrumentos, crear_instrumento, editar_instrumento,
#            eliminar_instrumento
# Lines: 851-1050 (approx. 200 lines)
# ============================================================================

# [Functions will be migrated here in Step 9]

# ============================================================================
# SECTION 6: BULK OPERATIONS
# ============================================================================
# Functions: carga_masiva, exportar_excel, exportar_csv
# Lines: 1051-1300 (approx. 250 lines)
# ============================================================================

# [Functions will be migrated here in Step 10]

# ============================================================================
# SECTION 7: USER MANAGEMENT
# ============================================================================
# Functions: mi_perfil, registro, admin_gestionar_usuarios,
#            desbloquear_cuenta_manual, ver_historial_login_usuario
# Lines: 1301-1550 (approx. 250 lines)
# ============================================================================

# [Functions will be migrated here in Steps 11-12]

# ============================================================================
# SECTION 8: AUDITING AND COMPLIANCE
# ============================================================================
# Functions: registro_auditoria
# Lines: 1551-1650 (approx. 100 lines)
# ============================================================================

# [Functions will be migrated here in Step 13]

# ============================================================================
# SECTION 9: API ENDPOINTS AND MISCELLANEOUS
# ============================================================================
# Functions: calcular_factores_ajax, home
# Lines: 1651-1750 (approx. 100 lines)
# ============================================================================

# [Functions will be migrated here in Step 13]
```

**Commit after Step 3:**

```powershell
git add calificaciones\views_unified.py calificaciones\*backup*.py
git commit -m "Task 1.3 Step 3: Create unified template with imports"
```

### Phase 2: Section-by-Section Migration (Steps 4-13)

**CRITICAL INSTRUCTIONS FOR ALL MIGRATION STEPS:**

1. **Copy entire function bodies exactly** - preserve all logic, decorators, docstrings
2. **Maintain indentation and formatting** - no Black/autopep8 until Task 1.4
3. **Preserve all comments** - including inline, block, and TODO comments
4. **Keep decorator order** - @login_required, @requiere_permiso(), etc.
5. **Do NOT modify function logic** - Task 1.3 is consolidation only, not refactoring
6. **Add spacing between functions** - 2 blank lines between function definitions
7. **Verify audit logging preserved** - LogAuditoria.objects.create() calls must remain

**Step 4: Migrate Section 1 - Utilities (6 functions)**

From `views.py`, copy these functions to Section 1 of `views_unified.py`:

1. `obtener_ip_cliente(request)` - **USE THIS VERSION** (not views_factores.py duplicate)
2. `verificar_cuenta_bloqueada(username)`
3. `registrar_intento_login(username, ip, exito)`
4. `verificar_intentos_fallidos(username)`
5. `procesar_excel(archivo)`
6. `procesar_csv(archivo)`

**Verification after Step 4:**

- Read views_unified.py lines 40-150
- Confirm 6 functions present
- Check obtener_ip_cliente has correct logic (X-Forwarded-For, REMOTE_ADDR)

**Commit:**

```powershell
git add calificaciones\views_unified.py
git commit -m "Task 1.3 Step 4: Migrate Section 1 - Utilities (6 functions)"
```

**Step 5: Migrate Section 2 - Authentication (2 functions)**

From `views.py`, copy to Section 2:

1. `login_view(request)` - 83 lines, HIGH RISK ⚠️
2. `logout_view(request)`

**Special attention for login_view:**

- Preserve all 4 utility function calls
- Keep account lockout logic intact
- Maintain audit logging for successful/failed logins
- Verify redirect logic for next parameter

**Verification after Step 5:**

- Grep for "def login_view" in views_unified.py
- Confirm decorator: No decorator (custom auth logic)
- Check logout_view has @login_required

**Commit:**

```powershell
git add calificaciones\views_unified.py
git commit -m "Task 1.3 Step 5: Migrate Section 2 - Authentication (2 functions)"
```

**Step 6: Migrate Section 3 - Dashboard (1 function)**

From `views.py`, copy to Section 3:

1. `dashboard(request)` - 99 lines, HIGH RISK ⚠️

**Special attention:**

- Preserve all database queries (Count, aggregate queries)
- Maintain role-based log filtering (Administrador sees all, others see own)
- Keep all context variables for template rendering
- Verify 8+ statistics calculations

**Verification after Step 6:**

- Check decorator: @login_required
- Verify context dict has ~10 keys (total_calificaciones, log_auditoria, etc.)

**Commit:**

```powershell
git add calificaciones\views_unified.py
git commit -m "Task 1.3 Step 6: Migrate Section 3 - Dashboard (1 function)"
```

**Step 7: Migrate Section 4 Part 1 - Standard Calificaciones CRUD (4 functions)**

From `views.py`, copy to Section 4:

1. `listar_calificaciones(request)`
2. `crear_calificacion(request)` - Uses CalificacionTributariaForm, form_calificacion.html
3. `editar_calificacion(request, pk)`
4. `eliminar_calificacion(request, pk)`

**Note:** Do NOT merge with factor-based versions yet - keep separate

**Verification after Step 7:**

- All 4 functions have @login_required
- crear_calificacion uses correct form/template
- LogAuditoria entries created on create/edit/delete

**Commit:**

```powershell
git add calificaciones\views_unified.py
git commit -m "Task 1.3 Step 7: Migrate Section 4 Part 1 - Standard CRUD (4 functions)"
```

**Step 8: Migrate Section 4 Part 2 - Factor Calificaciones CRUD (2 functions)**

From `views_factores.py`, copy to Section 4 (after Part 1 functions):

1. `crear_calificacion_factores(request)` - Uses CalificacionFactoresSimpleForm, form_factores_simple.html
2. `editar_calificacion_factores(request, pk)`

**Note:** Skip `obtener_ip_cliente()` from views_factores.py (duplicate already migrated in Step 4)

**Verification after Step 8:**

- Both functions have @login_required
- crear_calificacion_factores uses correct form/template
- Factor validation logic preserved (sum of factors 8-12 ≤ 1)

**Commit:**

```powershell
git add calificaciones\views_unified.py
git commit -m "Task 1.3 Step 8: Migrate Section 4 Part 2 - Factor CRUD (2 functions)"
```

**Step 9: Migrate Section 5 - Instrumentos CRUD (4 functions)**

From `views.py`, copy to Section 5:

1. `listar_instrumentos(request)`
2. `crear_instrumento(request)`
3. `editar_instrumento(request, pk)`
4. `eliminar_instrumento(request, pk)`

**Verification after Step 9:**

- All have @login_required and @requiere_permiso decorators
- Correct form: InstrumentoForm
- Correct templates: listar_instrumentos.html, form_instrumento.html

**Commit:**

```powershell
git add calificaciones\views_unified.py
git commit -m "Task 1.3 Step 9: Migrate Section 5 - Instrumentos CRUD (4 functions)"
```

**Step 10: Migrate Section 6 - Bulk Operations (3 functions)**

From `views.py`, copy to Section 6:

1. `carga_masiva(request)` - 101 lines, HIGH RISK ⚠️
2. `exportar_excel(request)`
3. `exportar_csv(request)`

**Special attention for carga_masiva:**

- Calls procesar_excel() and procesar_csv() helpers (migrated in Step 4)
- File upload handling with FILE_SIZE validation
- Database transaction handling
- Error messages preservation

**Verification after Step 10:**

- carga_masiva has @login_required @requiere_permiso('admin')
- Export functions have @login_required
- openpyxl and csv imports working (from unified import section)

**Commit:**

```powershell
git add calificaciones\views_unified.py
git commit -m "Task 1.3 Step 10: Migrate Section 6 - Bulk Operations (3 functions)"
```

**Step 11: Migrate Section 7 Part 1 - Self-Service User Management (2 functions)**

From `views.py`, copy to Section 7:

1. `mi_perfil(request)`
2. `registro(request)`

**Verification after Step 11:**

- mi_perfil has @login_required
- registro has no decorator (public registration)
- UsuarioRegistroForm imported and used

**Commit:**

```powershell
git add calificaciones\views_unified.py
git commit -m "Task 1.3 Step 11: Migrate Section 7 Part 1 - Self-service (2 functions)"
```

**Step 12: Migrate Section 7 Part 2 - Admin User Management (3 functions)**

From `views_admin.py`, copy to Section 7 (after Part 1 functions):

1. `admin_gestionar_usuarios(request)`
2. `desbloquear_cuenta_manual(request, user_id)` - HIGH RISK ⚠️ (permission-sensitive)
3. `ver_historial_login_usuario(request, user_id)`

**Note:** views_admin.py imports obtener_ip_cliente from views - already migrated, no changes needed

**Verification after Step 12:**

- All 3 have @login_required @requiere_permiso('admin')
- desbloquear_cuenta_manual audit logging preserved
- User account state changes functional

**Commit:**

```powershell
git add calificaciones\views_unified.py
git commit -m "Task 1.3 Step 12: Migrate Section 7 Part 2 - Admin mgmt (3 functions)"
```

**Step 13: Migrate Sections 8-9 - Auditing & API (3 functions)**

From `views.py`, copy to Section 8:

1. `registro_auditoria(request)` - Auditing section

From `views_factores.py`, copy to Section 9:

1. `calcular_factores_ajax(request)` - API endpoint
2. `home(request)` - Miscellaneous

**Verification after Step 13:**

- registro_auditoria has @login_required @requiere_permiso('admin')
- calcular_factores_ajax returns JsonResponse
- home renders home.html template

**Commit:**

```powershell
git add calificaciones\views_unified.py
git commit -m "Task 1.3 Step 13: Migrate Sections 8-9 - Auditing & API (3 functions)"
```

**Final Verification Before Phase 3:**

```powershell
# Count functions in unified file
Select-String -Path calificaciones\views_unified.py -Pattern "^def " | Measure-Object
# Expected: 30 functions

# Verify no syntax errors
python manage.py check --deploy
```

### Phase 3: URLs Update and Cleanup (Steps 14-18)

**Step 14: Update urls.py**

Edit `calificaciones/urls.py` with **9 specific changes**:

**Change 1-2: Remove imports (lines 2-4)**

```python
# DELETE these lines:
from . import views_factores
from . import views_admin
```

**Change 3: Update home route (line ~8)**

```python
# BEFORE:
path('', views_factores.home, name='home'),
# AFTER:
path('', views.home, name='home'),
```

**Changes 4-6: Update admin routes (lines ~40-42)**

```python
# BEFORE:
path('admin/usuarios/', views_admin.admin_gestionar_usuarios, name='admin_gestionar_usuarios'),
path('admin/usuarios/desbloquear/<int:user_id>/', views_admin.desbloquear_cuenta_manual, name='desbloquear_cuenta'),
path('admin/usuarios/historial/<int:user_id>/', views_admin.ver_historial_login_usuario, name='ver_historial_login'),

# AFTER:
path('admin/usuarios/', views.admin_gestionar_usuarios, name='admin_gestionar_usuarios'),
path('admin/usuarios/desbloquear/<int:user_id>/', views.desbloquear_cuenta_manual, name='desbloquear_cuenta'),
path('admin/usuarios/historial/<int:user_id>/', views.ver_historial_login_usuario, name='ver_historial_login'),
```

**Changes 7-8: Update factor routes (lines ~45-46)**

```python
# BEFORE:
path('crear/factores/', views_factores.crear_calificacion_factores, name='crear_calificacion_factores'),
path('editar/factores/<int:pk>/', views_factores.editar_calificacion_factores, name='editar_calificacion_factores'),

# AFTER:
path('crear/factores/', views.crear_calificacion_factores, name='crear_calificacion_factores'),
path('editar/factores/<int:pk>/', views.editar_calificacion_factores, name='editar_calificacion_factores'),
```

**Change 9: Update AJAX route (line ~49)**

```python
# BEFORE:
path('api/calcular-factores/', views_factores.calcular_factores_ajax, name='calcular_factores_ajax'),

# AFTER:
path('api/calcular-factores/', views.calcular_factores_ajax, name='calcular_factores_ajax'),
```

**Verification after Step 14:**

```powershell
# Verify no references to old modules
Select-String -Path calificaciones\urls.py -Pattern "views_factores|views_admin"
# Expected: No matches

# Verify import line
Select-String -Path calificaciones\urls.py -Pattern "^from \. import views$"
# Expected: 1 match
```

**Commit:**

```powershell
git add calificaciones\urls.py
git commit -m "Task 1.3 Step 14: Update urls.py - remove old imports, update 6 routes"
```

**Step 15: Rename Unified File**

```powershell
# Rename views_unified.py to views_new.py (temporary)
Rename-Item calificaciones\views_unified.py calificaciones\views_new.py
git add calificaciones\views_new.py calificaciones\views_unified.py
git commit -m "Task 1.3 Step 15: Rename unified file to views_new.py"
```

**Step 16: Atomic File Swap**

```powershell
# Swap old and new views files atomically
Rename-Item calificaciones\views.py calificaciones\views_old.py
Rename-Item calificaciones\views_new.py calificaciones\views.py

# Verify swap
Test-Path calificaciones\views.py  # Should be True
Test-Path calificaciones\views_old.py  # Should be True

git add -A
git commit -m "Task 1.3 Step 16: Atomic swap - views_new.py becomes views.py"
```

**Step 17: Delete Old View Files**

```powershell
# Remove old files (keep backups for now)
Remove-Item calificaciones\views_admin.py
Remove-Item calificaciones\views_factores.py
Remove-Item calificaciones\views_old.py

# Verify deletion
Get-ChildItem calificaciones\views*.py
# Expected: views.py, views_admin_backup.py, views_factores_backup.py, views_backup_original.py

git add -A
git commit -m "Task 1.3 Step 17: Delete old view files (views_admin.py, views_factores.py, views_old.py)"
```

**Step 18: Verify admin.py (No Changes Expected)**

```powershell
# Check for imports from deleted files
Select-String -Path calificaciones\admin.py -Pattern "views_admin|views_factores"
# Expected: No matches (admin.py should only import from .models, .forms)

# If any matches found, update imports to reference views module
```

### Phase 4: Comprehensive Verification (Steps 19-20)

**Step 19: Automated Verification**

**A. Django System Check**

```powershell
python manage.py check --deploy
# Expected: No issues found
```

**B. URL Resolution Test**

Create temporary test script `test_url_resolution.py`:

```python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nuam_project.settings')
django.setup()

from django.urls import reverse

# All 22 routes that must resolve
routes = [
    'home', 'login', 'logout', 'dashboard', 'registro', 'mi_perfil',
    'listar_calificaciones', 'crear_calificacion', 'crear_calificacion_factores',
    'listar_instrumentos', 'crear_instrumento', 'carga_masiva',
    'exportar_excel', 'exportar_csv', 'registro_auditoria',
    'admin_gestionar_usuarios', 'calcular_factores_ajax',
]

routes_with_args = [
    ('editar_calificacion', {'pk': 1}),
    ('editar_calificacion_factores', {'pk': 1}),
    ('eliminar_calificacion', {'pk': 1}),
    ('editar_instrumento', {'pk': 1}),
    ('eliminar_instrumento', {'pk': 1}),
    ('desbloquear_cuenta', {'user_id': 1}),
    ('ver_historial_login', {'user_id': 1}),
]

print("Testing URL resolution for all 22 routes...\n")
errors = []

for route in routes:
    try:
        url = reverse(route)
        print(f"✅ {route:40} -> {url}")
    except Exception as e:
        errors.append(f"❌ {route}: {e}")
        print(f"❌ {route:40} -> ERROR: {e}")

for route, kwargs in routes_with_args:
    try:
        url = reverse(route, kwargs=kwargs)
        print(f"✅ {route:40} -> {url}")
    except Exception as e:
        errors.append(f"❌ {route}: {e}")
        print(f"❌ {route:40} -> ERROR: {e}")

print(f"\n{'='*60}")
if errors:
    print(f"FAILED: {len(errors)} routes could not resolve")
    for error in errors:
        print(error)
    exit(1)
else:
    print("SUCCESS: All 22 routes resolved correctly ✅")
    exit(0)
```

Run test:

```powershell
python test_url_resolution.py
# Expected: "SUCCESS: All 22 routes resolved correctly ✅"
```

**C. Import Verification**

```powershell
# Test import works
python -c "from calificaciones.views import obtener_ip_cliente, login_view, dashboard, listar_calificaciones; print('✅ Imports successful')"
```

**D. Run Existing Tests**

```powershell
# Run calificaciones test suite
pytest calificaciones/tests/ -v
# Note: Some tests may fail if they import from old modules - document for fixing
```

**Step 20: Manual Functional Verification**

**Start Development Server:**

```powershell
python manage.py runserver
```

**Test Checklist (High-Priority Routes):**

1. **Authentication (CRITICAL)**

   - [ ] Navigate to http://localhost:8000/calificaciones/login/
   - [ ] Login with valid credentials → Should redirect to dashboard
   - [ ] Verify session created, user authenticated
   - [ ] Logout → Should redirect to login page

2. **Dashboard (HIGH RISK)**

   - [ ] Navigate to http://localhost:8000/calificaciones/dashboard/
   - [ ] Verify all statistics render without errors
   - [ ] Check audit log table displays
   - [ ] Verify role-based filtering (Administrador vs Analista)

3. **Calificaciones CRUD (CORE FUNCTIONALITY)**

   - [ ] List: http://localhost:8000/calificaciones/listar/ → Table renders
   - [ ] Create Standard: http://localhost:8000/calificaciones/crear/ → Form loads
   - [ ] Create Factor: http://localhost:8000/calificaciones/crear/factores/ → Factor form loads
   - [ ] Submit calificacion → Database record created
   - [ ] Edit existing calificacion → Changes persist
   - [ ] Delete calificacion → Record removed, audit log entry created

4. **Bulk Operations (HIGH RISK)**

   - [ ] Navigate to http://localhost:8000/calificaciones/carga-masiva/
   - [ ] Upload sample CSV/XLSX file
   - [ ] Verify records imported to database
   - [ ] Test export Excel → File downloads
   - [ ] Test export CSV → File downloads

5. **Admin Functions (PERMISSION-SENSITIVE)**

   - [ ] Admin user list: http://localhost:8000/calificaciones/admin/usuarios/
   - [ ] Lock user account (5 failed logins)
   - [ ] Admin unlock: http://localhost:8000/calificaciones/admin/usuarios/desbloquear/1/
   - [ ] Verify audit log entry created for unlock
   - [ ] Test Analista user CANNOT access admin functions (403/redirect)

6. **AJAX Endpoints**

   - [ ] Open browser console on factor form
   - [ ] Trigger factor calculation AJAX call
   - [ ] Verify JSON response with classification result

7. **Template Rendering**
   - [ ] Home page: http://localhost:8000/calificaciones/
   - [ ] All templates render without TemplateDoesNotExist errors
   - [ ] Static files load (CSS, JS)

**Acceptance Criteria:**

- [ ] All 22 routes return 200 OK (or appropriate redirects)
- [ ] No 404 errors (NoReverseMatch, URL not found)
- [ ] No 500 errors (import errors, syntax errors)
- [ ] Authentication works (login, logout, session management)
- [ ] CRUD operations create database records
- [ ] Audit logging creates LogAuditoria entries
- [ ] Role-based permissions enforced (@requiere_permiso decorators)
- [ ] Factor validation works (sum ≤ 1 constraint)
- [ ] File upload/export functional
- [ ] AJAX endpoints return valid JSON

**Final Commit:**

```powershell
git add -A
git commit -m "Task 1.3 Step 20: Manual verification complete - all 22 routes functional"
```

### Post-Verification Actions

**If All Tests Pass ✅:**

```powershell
# Tag successful unification
git tag -a "task-1.3-complete" -m "View unification successful - 22 routes verified"

# Remove backup files (keep in git history)
Remove-Item calificaciones\*backup*.py
git add -A
git commit -m "Task 1.3 Cleanup: Remove backup files after successful verification"
```

**If Tests Fail ❌:**

```powershell
# Document failures
# Create failure report with specific errors
# DO NOT proceed to Task 1.4 until issues resolved

# Rollback option if critical failures:
git log --oneline -10  # Find pre-unification commit
git reset --hard <commit-hash>  # Restore to working state
```

## Expected Output

### Deliverables:

1. ✅ **Unified views.py** (~1,750 lines, 9 sections, 30 functions)
2. ✅ **Updated urls.py** (9 edits, no references to old modules)
3. ✅ **Deleted files:** views_admin.py, views_factores.py removed
4. ✅ **10 git commits** with rollback checkpoints throughout migration
5. ✅ **URL resolution test results** (22/22 routes passing)
6. ✅ **Manual verification checklist** (all items checked)
7. ✅ **Memory log** documenting complete execution

### Success Criteria:

- All 30 functions migrated to unified views.py
- All 22 URL routes resolve correctly (no NoReverseMatch errors)
- All decorators preserved (@login_required, @requiere_permiso)
- All audit logging preserved (LogAuditoria.objects.create())
- Authentication functional (login, logout, account lockout)
- CRUD operations create/update/delete database records
- Factor validation enforces business rules (sum ≤ 1)
- Bulk upload/export functional
- Role-based permissions enforced
- AJAX endpoints return valid JSON
- No import errors, no 500 errors, no template errors
- `python manage.py check --deploy` passes with no issues

### Quality Metrics:

**Code Organization:**

- 9 clear section boundaries with header comments
- Consistent 2-line spacing between functions
- All imports consolidated at top (PEP 8 organized)
- No duplicate code (obtener_ip_cliente consolidated)

**Backward Compatibility:**

- 22/22 routes functional (100%)
- All URL names preserved
- All URL paths preserved
- All templates compatible (no changes needed)

**Risk Mitigation:**

- 10 git rollback checkpoints created
- High-risk functions tested (login_view, carga_masiva, dashboard, desbloquear_cuenta_manual)
- Incremental verification at each phase

## Memory Logging

Upon completion of ALL steps (including verification), you MUST log work in: `.apm/Memory/Phase_01_Analysis_Refactoring_Unification/Task_1_3_View_Unification_Execution.md`

Follow `.apm/guides/Memory_Log_Guide.md` instructions for proper formatting with YAML frontmatter and all required sections.

Include in log:

- All 20 steps executed with results
- Git commit hashes for each checkpoint
- URL resolution test output
- Manual verification checklist results
- Any issues encountered and how resolved
- Final metrics (lines of code, functions migrated, routes verified)

## Integration Context from Task 1.2

**Approved Strategy Reference:**

- Memory Log: `.apm/Memory/Phase_01_Analysis_Refactoring_Unification/Task_1_2_Unification_Strategy.md`
- 9-section structure with function assignments
- Import consolidation: 31 → 19 statements
- Duplicate resolution: Consolidate obtener_ip_cliente, keep parallel CRUD workflows
- urls.py changes: 9 specific edits at exact line numbers

**Critical Constraints:**

- 100% backward compatibility required
- All 22 URL route names must remain unchanged
- All URL paths must remain unchanged
- No template modifications allowed
- No form consolidation (deferred to Task 1.4)
- No Black/autopep8 formatting (deferred to Task 1.4)

**High-Risk Functions (Prioritize Testing):**

1. `login_view` - Authentication critical, 83 lines, 4 dependencies
2. `carga_masiva` - File processing, 101 lines, complex logic
3. `dashboard` - Multiple queries, 99 lines, role-based filtering
4. `desbloquear_cuenta_manual` - Admin permission, account state changes

## Notes

**Execution Pattern:**
This is an implementation task requiring systematic step-by-step execution. Do NOT skip steps or combine phases. Each git commit creates a rollback point.

**Quality Requirements:**

- Exact function copying (no logic changes)
- Preserve all decorators and comments
- Maintain audit logging
- Verify incrementally (don't wait until end)
- Test high-risk functions thoroughly

**Rollback Strategy:**
If critical failures occur during verification:

1. Document exact errors encountered
2. Use `git log` to find last working commit
3. Use `git reset --hard <hash>` to restore
4. Report failures to Manager Agent for strategy revision

**Timeline:**
Estimated duration: 2-3 hours

- Phase 1: 15 minutes
- Phase 2: 60-90 minutes (section migration)
- Phase 3: 15 minutes (URLs & cleanup)
- Phase 4: 30-45 minutes (comprehensive verification)

---

**Manager Agent Note:** This task assignment prompt should be provided to Agent_Refactor (Implementation Agent) to begin Task 1.3 execution. Task 1.2 Memory Log with approved strategy is available as reference.
