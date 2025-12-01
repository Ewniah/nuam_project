---
task_ref: "Task 1.4 - Apply Code Standardization and Best Practices"
agent_assignment: "Agent_Refactor"
memory_log_path: ".apm/Memory/Phase_01_Analysis_Refactoring_Unification/Task_1_4_Code_Standardization.md"
execution_type: "implementation"
dependency_context: true
ad_hoc_delegation: false
---

# APM Task Assignment: Apply Code Standardization and Best Practices

## Task Reference

Implementation Plan: **Task 1.4 - Apply Code Standardization and Best Practices** assigned to **Agent_Refactor**

## Context from Previous Tasks

**Task 1.1 (Codebase Analysis) - COMPLETE ✅**

- Identified technical debt: magic numbers, inconsistent exception handling, missing logging
- Documented god functions requiring refactoring
- Code quality issues cataloged

**Task 1.2 (Unification Strategy) - COMPLETE ✅**

- 9-section organization structure approved
- Import consolidation strategy defined
- Route preservation strategy confirmed

**Task 1.3 (View Unification) - COMPLETE ✅**

- 30 functions consolidated into single views.py (1,275 lines)
- All 22 URL routes functional
- 100% backward compatibility maintained
- Duplicate code eliminated
- Cross-file dependencies resolved

## Objective

Apply comprehensive code quality standards to the unified `views.py` file including PEP 8 compliance, Black code formatting, consistent exception handling patterns, Django logging framework integration, and improved docstrings - while maintaining 100% backward compatibility and existing functionality.

## Detailed Instructions

This is an **IMPLEMENTATION TASK** requiring systematic application of coding standards across the unified codebase.

### Step 1: Apply Black Code Formatter

**Install Black (if needed):**

```powershell
C:/Users/Bryan/Desktop/nuam_project-1/.venv/Scripts/python.exe -m pip install black
```

**Run Black on views.py:**

```powershell
C:/Users/Bryan/Desktop/nuam_project-1/.venv/Scripts/python.exe -m black calificaciones\views.py --line-length 100
```

**Configuration:**

- Line length: 100 characters (Django standard)
- String normalization: enabled
- Magic trailing comma: enabled

**Expected Changes:**

- Consistent indentation (4 spaces)
- Consistent string quotes (prefer double quotes)
- Consistent spacing around operators
- Consistent blank lines between functions (2 lines)
- Consistent trailing commas in multi-line structures

**Verification:**

```powershell
# Check formatting
C:/Users/Bryan/Desktop/nuam_project-1/.venv/Scripts/python.exe -m black calificaciones\views.py --check
```

**Commit after Step 1:**

```powershell
git add calificaciones\views.py
git commit -m "Task 1.4 Step 1: Apply Black code formatter to views.py"
```

### Step 2: Add Logging Configuration

**Update Import Section:**
Add Django logging import:

```python
import logging

logger = logging.getLogger(__name__)
```

Place after the file header comment, before other imports.

**Logging Patterns to Apply:**

1. **Function Entry Logging (DEBUG level):**

```python
@login_required
def function_name(request):
    logger.debug(f"Entering function_name - User: {request.user.username}")
    # ... existing code
```

2. **Success Operations (INFO level):**

```python
logger.info(f"Calificación created successfully - ID: {calificacion.id}, User: {request.user.username}")
```

3. **Error Conditions (ERROR level):**

```python
except Exception as e:
    logger.error(f"Error in carga_masiva: {str(e)}", exc_info=True)
    messages.error(request, f'Error al procesar archivo: {str(e)}')
```

4. **Warning Conditions (WARNING level):**

```python
if tiene_calificaciones:
    logger.warning(f"Attempted to delete instrumento with associated calificaciones - ID: {pk}")
    messages.error(request, 'No se puede eliminar el instrumento...')
```

**Functions to Prioritize for Logging:**

- High-risk functions: login_view, carga_masiva, dashboard, desbloquear_cuenta_manual
- All CRUD operations (CREATE, UPDATE, DELETE)
- All admin operations
- All authentication operations

**Commit after Step 2:**

```powershell
git add calificaciones\views.py
git commit -m "Task 1.4 Step 2: Add Django logging framework integration"
```

### Step 3: Improve Exception Handling

**Current Issues:**

- Bare `except:` blocks (anti-pattern)
- Generic `except Exception as e` without proper logging
- Some functions lack try-except blocks

**Standard Exception Handling Pattern:**

```python
try:
    # ... operation code
    logger.info(f"Operation successful: {details}")
    messages.success(request, 'Operation completed successfully.')
    return redirect('target_view')

except SpecificException as e:
    logger.error(f"Specific error in function_name: {str(e)}", exc_info=True)
    messages.error(request, 'User-friendly error message.')
    return redirect('fallback_view')

except Exception as e:
    logger.critical(f"Unexpected error in function_name: {str(e)}", exc_info=True)
    messages.error(request, 'An unexpected error occurred. Please contact support.')
    return redirect('safe_view')
```

**Functions Requiring Exception Handling:**

1. **carga_masiva** (HIGH PRIORITY):

   - Wrap file parsing in try-except
   - Handle openpyxl.exceptions
   - Handle CSV parsing errors
   - Handle database IntegrityError

2. **dashboard**:

   - Wrap statistics queries in try-except
   - Handle database connection errors
   - Graceful degradation if stats fail

3. **exportar_excel/exportar_csv**:

   - Handle file generation errors
   - Handle encoding errors

4. **All CRUD operations**:
   - Handle DoesNotExist exceptions explicitly
   - Handle ValidationError from forms
   - Handle IntegrityError from database

**Specific Exceptions to Handle:**

```python
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError, DatabaseError
import openpyxl.exceptions
```

**Commit after Step 3:**

```powershell
git add calificaciones\views.py
git commit -m "Task 1.4 Step 3: Improve exception handling with specific exceptions"
```

### Step 4: Update Docstrings

**Current Issues:**

- Inconsistent docstring formats
- Missing parameter descriptions
- Missing return value descriptions
- Missing exception documentation

**Standard Docstring Format (Google Style):**

```python
def function_name(request, pk=None):
    """
    Brief one-line description of function purpose.

    Longer description explaining what the function does, including any
    business logic or important implementation details.

    Args:
        request (HttpRequest): The HTTP request object containing user, POST data, etc.
        pk (int, optional): Primary key of the object to process. Defaults to None.

    Returns:
        HttpResponse: Rendered template response or redirect.

    Raises:
        ObjectDoesNotExist: If the requested object is not found.
        ValidationError: If form validation fails.

    Example:
        # Direct call (not typical for views)
        response = function_name(request, pk=1)

    Notes:
        - Requires authentication via @login_required decorator
        - Requires 'modificar' permission via @requiere_permiso decorator
        - Logs all operations to LogAuditoria
    """
```

**Functions to Update:**

1. **All utility functions (Section 1):**

   - obtener_ip_cliente: Document X-Forwarded-For handling
   - verificar_cuenta_bloqueada: Document return tuple format
   - verificar_intentos_fallidos: Document threshold values

2. **Authentication functions (Section 2):**

   - login_view: Document lockout mechanism (5 attempts, 30 min)
   - logout_view: Document audit logging

3. **High-complexity functions:**
   - dashboard: Document all statistics calculated
   - carga_masiva: Document file format requirements
   - calcular_factores_ajax: Document JSON response format

**Commit after Step 4:**

```powershell
git add calificaciones\views.py
git commit -m "Task 1.4 Step 4: Update docstrings to Google style format"
```

### Step 5: Replace Magic Numbers with Constants

**Current Magic Numbers:**

- `5` - Maximum login attempts before lockout
- `30` - Lockout duration in minutes
- `15` - Time window for counting failed attempts
- `1000` - Maximum audit log records to display
- `50` - Maximum login history records
- `7` - Days for recent activity

**Define Constants at Module Level:**

```python
# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

# Authentication & Security
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30
FAILED_ATTEMPT_WINDOW_MINUTES = 15

# Pagination & Limits
MAX_AUDIT_LOG_RECORDS = 1000
MAX_LOGIN_HISTORY_RECORDS = 50
RECENT_ACTIVITY_DAYS = 7

# File Upload
MAX_FILE_SIZE_MB = 10  # If applicable
```

Place after imports, before Section 1.

**Replace Usage:**

Before:

```python
if intentos_fallidos >= 5:
```

After:

```python
if intentos_fallidos >= MAX_LOGIN_ATTEMPTS:
```

**Commit after Step 5:**

```powershell
git add calificaciones\views.py
git commit -m "Task 1.4 Step 5: Replace magic numbers with named constants"
```

### Step 6: Add Type Hints (Optional Enhancement)

**Add type hints for clarity:**

```python
from typing import Tuple, Dict, Any, Optional
from django.http import HttpRequest, HttpResponse, JsonResponse

def obtener_ip_cliente(request: HttpRequest) -> str:
    """Obtiene la IP real del cliente considerando proxies"""
    # ...

def verificar_cuenta_bloqueada(username: str) -> Tuple[bool, str, int]:
    """
    Verifica si una cuenta está bloqueada

    Returns:
        Tuple[bool, str, int]: (bloqueada, mensaje, minutos_restantes)
    """
    # ...
```

**Note:** Type hints are optional but improve code clarity and enable better IDE support.

**Commit after Step 6:**

```powershell
git add calificaciones\views.py
git commit -m "Task 1.4 Step 6: Add type hints for improved code clarity"
```

### Step 7: Verify Code Quality

**Run Quality Checks:**

1. **Black formatting check:**

```powershell
C:/Users/Bryan/Desktop/nuam_project-1/.venv/Scripts/python.exe -m black calificaciones\views.py --check
```

2. **Flake8 linting (optional):**

```powershell
C:/Users/Bryan/Desktop/nuam_project-1/.venv/Scripts/python.exe -m pip install flake8
C:/Users/Bryan/Desktop/nuam_project-1/.venv/Scripts/python.exe -m flake8 calificaciones\views.py --max-line-length 100
```

3. **Import sorting (optional):**

```powershell
C:/Users/Bryan/Desktop/nuam_project-1/.venv/Scripts/python.exe -m pip install isort
C:/Users/Bryan/Desktop/nuam_project-1/.venv/Scripts/python.exe -m isort calificaciones\views.py --check --profile black
```

4. **Line count verification:**

```powershell
(Get-Content calificaciones\views.py).Count
```

**Expected Quality Metrics:**

- PEP 8 compliant (100%)
- Black formatted (100%)
- Logging statements: 50+ (covering all critical operations)
- Specific exception handlers: 15+ (replacing generic except blocks)
- Docstrings: 30 functions with complete documentation
- Type hints: 30+ functions (if Step 6 completed)
- Magic numbers eliminated: All replaced with constants

### Step 8: Final Verification & Testing

**A. Syntax Verification:**

```powershell
C:/Users/Bryan/Desktop/nuam_project-1/.venv/Scripts/python.exe -m py_compile calificaciones\views.py
```

**B. Import Verification:**

```powershell
C:/Users/Bryan/Desktop/nuam_project-1/.venv/Scripts/python.exe -c "import sys; sys.path.insert(0, 'calificaciones'); import views; print('✅ Imports successful')"
```

Note: May require Django settings configuration

**C. Git Status Check:**

```powershell
git status
git log --oneline -10
```

**D. File Metrics:**

```powershell
$content = Get-Content calificaciones\views.py
Write-Output "Lines: $($content.Count)"
Write-Output "Functions: $(($content | Select-String -Pattern '^def ').Count)"
Write-Output "Logger calls: $(($content | Select-String -Pattern 'logger\.').Count)"
Write-Output "Try-except blocks: $(($content | Select-String -Pattern '^    try:').Count)"
```

**Final Commit:**

```powershell
git add -A
git commit -m "Task 1.4 Step 8: Final verification and quality checks complete"
```

## Expected Output

### Deliverables:

1. ✅ **Black-formatted views.py** - PEP 8 compliant, 100 char line limit
2. ✅ **Django logging integration** - 50+ logger statements across critical functions
3. ✅ **Improved exception handling** - 15+ specific exception handlers
4. ✅ **Updated docstrings** - 30 functions with Google-style documentation
5. ✅ **Constants defined** - All magic numbers replaced
6. ✅ **Type hints** (optional) - Better IDE support and code clarity
7. ✅ **Quality verification** - Black check passes, flake8 clean
8. ✅ **Memory log** - Complete documentation of changes

### Success Criteria:

- Black formatter passes with no changes needed
- All magic numbers replaced with named constants
- All high-risk functions have comprehensive exception handling
- All functions have complete Google-style docstrings
- Logging statements cover all CRUD operations
- Logging statements cover all authentication operations
- Logging statements cover all admin operations
- No bare `except:` blocks remain
- No generic exceptions without logging
- PEP 8 compliance: 100%
- File remains functionally identical (no logic changes)
- All 30 functions preserved
- All decorators intact
- All audit logging preserved

### Quality Metrics:

**Code Formatting:**

- Line length: ≤ 100 characters
- Indentation: 4 spaces (consistent)
- String quotes: Double quotes (consistent)
- Blank lines: 2 between functions

**Documentation:**

- Docstrings: 30/30 functions (100%)
- Parameter documentation: Complete
- Return value documentation: Complete
- Exception documentation: Complete

**Error Handling:**

- Specific exceptions: 15+
- Generic exceptions with logging: All
- Bare except blocks: 0

**Logging Coverage:**

- DEBUG level: Function entries (30+)
- INFO level: Success operations (25+)
- WARNING level: Warning conditions (10+)
- ERROR level: Error conditions (15+)
- CRITICAL level: Unexpected errors (5+)

**Code Quality:**

- Magic numbers: 0
- PEP 8 violations: 0
- Flake8 issues: 0
- Type hints: 30+ functions (if optional step completed)

## Memory Logging

Upon completion of ALL steps, you MUST log work in: `.apm/Memory/Phase_01_Analysis_Refactoring_Unification/Task_1_4_Code_Standardization.md`

Follow `.apm/guides/Memory_Log_Guide.md` instructions for proper formatting with YAML frontmatter and all required sections.

Include:

- All steps executed with results
- Git commit hashes
- Before/after metrics (line count, function count, logger calls, etc.)
- Quality check results (Black, flake8, isort)
- Any issues encountered and resolutions

## Integration Context from Task 1.3

**Unified views.py Status:**

- File: calificaciones/views.py
- Lines: 1,275
- Functions: 30
- Sections: 9
- Git history: 17 commits

**Critical Constraints:**

- **DO NOT modify function logic** - Task 1.4 is formatting/documentation only
- **DO NOT change function signatures** - Preserve all parameters
- **DO NOT change decorators** - Preserve @login_required, @requiere_permiso
- **DO NOT change audit logging** - Preserve all LogAuditoria.objects.create() calls
- **DO NOT change templates** - No template references change
- **DO NOT change URL routes** - No route names change

**High-Priority Functions for Logging:**

1. login_view (authentication critical)
2. carga_masiva (file processing, 101 lines)
3. dashboard (multiple database queries, 99 lines)
4. desbloquear_cuenta_manual (admin permission, account state)

## Notes

**Execution Pattern:**
This is an implementation task requiring systematic application of standards. Each step builds on the previous. Execute in sequence.

**Quality Requirements:**

- Be thorough in logging coverage (don't miss critical operations)
- Be precise in exception handling (use specific exceptions)
- Be clear in docstrings (explain business logic)
- Be consistent in formatting (Black handles this)

**Timeline:**
Estimated duration: 2-3 hours

- Step 1 (Black): 10 minutes
- Step 2 (Logging): 45-60 minutes
- Step 3 (Exceptions): 30-45 minutes
- Step 4 (Docstrings): 30-45 minutes
- Step 5 (Constants): 15 minutes
- Step 6 (Type hints, optional): 30 minutes
- Steps 7-8 (Verification): 15 minutes

---

**Manager Agent Note:** This task assignment prompt should be provided to Agent_Refactor to begin Task 1.4 execution. Task 1.3 Memory Log confirms unified views.py is ready for standardization.
