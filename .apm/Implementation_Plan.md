# NUAM Project Refactoring – Implementation Plan

**Memory Strategy:** Dynamic-MD (directory structure with Markdown logs)
**Last Modification:** Initial creation by Setup Agent
**Project Overview:** Django-based tax qualification management system refactoring project focusing on view unification, code standardization, and comprehensive validation. Critical mandate: consolidate three active view files into unified structure while maintaining 100% backward compatibility and functionality. Target: December 12, 2025 presentation deadline.

---

## Phase 1: Analysis, Refactoring, and Structural Unification

### Task 1.1 – Initial Codebase Analysis and Technical Audit │ Agent_Analysis

- **Objective:** Perform comprehensive technical audit of the Django codebase to establish baseline understanding, identify legacy patterns and technical debt, document consolidation opportunities beyond the three view files, and create actionable refactoring roadmap.
- **Output:** Technical audit report documenting current codebase state, organizational fragmentation patterns, code smells, technical debt areas, Django best practice violations, and prioritized list of files/modules requiring consolidation or improvement.
- **Guidance:** Focus on identifying duplicated logic, shared imports, and coupling patterns across view files. Assess models, forms, URLs, and utility modules for consolidation potential. Document specific Django anti-patterns (inconsistent error handling, missing logging, poor naming conventions). Prioritize findings by refactoring impact and risk level.

**Sub-tasks:**

- Analyze all three view files (`views.py`, `views_admin.py`, `views_factores.py`) to identify duplicated logic patterns, shared import statements, organizational fragmentation issues, current URL route structure, and function interdependencies that inform consolidation strategy
- Review `models.py`, `forms.py`, `urls.py`, and utility modules (`calificaciones/utils/`) to identify additional consolidation opportunities, assess coupling with view files, and document any circular dependencies or tight coupling requiring refactoring attention
- Document legacy code patterns, code smells (long functions, god objects, magic numbers), technical debt areas (missing error handling, hardcoded values), and violations of Django best practices in naming conventions, project structure, and error handling approaches
- Create comprehensive technical audit report summarizing all findings, prioritizing refactoring areas by impact and risk (critical/high/medium/low), identifying specific files beyond views that may benefit from consolidation, and providing actionable recommendations for Phase 1 execution

### Task 1.2 – View Files Unification Strategy and Route Mapping │ Agent_Analysis

- **Objective:** Develop detailed strategy for merging three active view files (`views.py`, `views_admin.py`, `views_factores.py`) into single unified structure while guaranteeing preservation of all existing URL routes, maintaining backward compatibility, and establishing verification approach.
- **Output:** Comprehensive unification plan document containing complete route-to-function mapping, unified file organization strategy, backward compatibility verification checklist, function migration sequence, and User-approved consolidation approach ready for execution.
- **Guidance:** Depends on: Task 1.1 Output. Map every URL route to its view function across all three files to prevent route breakage. Design logical function grouping strategy (admin operations, factor calculations, CRUD operations, utility functions). Address potential Django routing edge cases requiring research. Obtain explicit User approval before proceeding to implementation phase.

**Sub-tasks:**

1. **Ad-Hoc Delegation:** If complex Django routing patterns are discovered (class-based views with multiple dispatch methods, custom URL resolvers, namespace conflicts), delegate edge case research to specialized agent for resolution guidance.
2. **Route Mapping Analysis:** Map all existing URL routes to their corresponding view functions across `views.py`, `views_admin.py`, `views_factores.py`, documenting route names, URL patterns, HTTP methods, function signatures, decorators, and any route-specific middleware or permission requirements.
3. **Organization Strategy Design:** Design unified `views.py` organization strategy including function ordering logic, logical grouping approach (admin functions at top, factor calculation functions in middle, CRUD functions grouped by model, utility functions at bottom), import consolidation strategy, and documentation structure for navigability.
4. **Unification Plan Creation:** Create detailed unification plan documenting route preservation verification checklist, function migration sequence (which functions move in which order), testing approach for each migrated route, rollback markers for incremental verification, and risk mitigation strategies for complex functions.
5. **User Approval Gate:** Present complete unification strategy to User for approval, addressing any concerns about route preservation, function organization, or migration risks before proceeding to Task 1.3 execution.

### Task 1.3 – Execute View Unification and Code Consolidation │ Agent_Refactor

- **Objective:** Execute approved unification strategy by merging all logic from `views_admin.py` and `views_factores.py` into single consolidated `views.py` file, eliminating original separate files, consolidating any additional files identified in Task 1.1 audit, and verifying all routes remain functional.
- **Output:** Single unified `views.py` file containing all view logic organized according to approved strategy, removal of `views_admin.py` and `views_factores.py` files, updated import references across project, consolidated additional files if identified, and verification confirmation that all URL routes resolve correctly.
- **Guidance:** Depends on: Task 1.2 Output by Agent_Analysis. Follow approved organization strategy precisely. Consolidate duplicate imports and shared initialization logic. Update any internal references in forms, models, or tests. If Task 1.1 identified additional consolidation candidates, apply same unification principles. Verify routes incrementally during migration for early issue detection.

**Sub-tasks:**

1. **View File Merging:** Merge all functions from `views_admin.py` and `views_factores.py` into unified `views.py` following the approved organization strategy, consolidating duplicate imports (Django imports, model imports, form imports), shared initialization logic, and common decorator patterns while preserving all function signatures and business logic.
2. **File Cleanup and Reference Updates:** Remove original `views_admin.py` and `views_factores.py` files from the project and update any internal import references that might exist in other modules (`urls.py`, `forms.py`, test files, management commands) to point to the unified `views.py` structure.
3. **Extended Consolidation:** If Task 1.1 technical audit identified additional consolidation candidates (utility modules with overlapping functions, form files with duplicate validation, or other fragmented code), execute their consolidation following same principles of unified, cohesive structure while maintaining functionality.
4. **Route Verification:** Verify all URL routes resolve correctly to unified view functions through systematic route testing using Django's `resolve()` function, imports validation to ensure no broken references, and manual verification of critical routes (admin dashboard, factor calculation endpoints, CRUD operations).

### Task 1.4 – Apply Code Standardization and Best Practices │ Agent_Refactor

- **Objective:** Apply comprehensive code quality standards across entire refactored codebase including PEP 8 compliance, Black code formatting, consistent exception handling patterns, Django logging framework integration, and improved function/class documentation to meet professional Django development standards.
- **Output:** Fully standardized codebase with Black formatting applied, PEP 8 compliance verified, robust exception handling patterns implemented across all views, Django logging integrated for all CRUD and business logic operations, and comprehensive docstrings added to all functions, classes, and modules.
- **Guidance:** Depends on: Task 1.3 Output. Run Black formatter on all Python files to ensure style consistency. Implement try-except blocks with user-friendly error messages and technical logging. Add logger statements for all CRUD operations (create, update, delete), bulk operations, and factor calculations including user, timestamp, and affected objects. Update docstrings to reflect unified structure and document complex business logic.

**Sub-tasks:**

1. **Automated Formatting:** Run Black formatter on all Python files in the project (`black calificaciones/ nuam_project/ --line-length 88`) to enforce consistent code style; verify PEP 8 compliance across refactored codebase using flake8 or similar linting tool to catch any remaining style violations.
2. **Exception Handling Standardization:** Implement robust and consistent exception handling patterns across all unified view logic, wrapping database operations in try-except blocks, ensuring user-friendly error messages displayed via Django messages framework while technical details (stack traces, error context) are logged appropriately for debugging.
3. **Django Logging Integration:** Integrate Django logging framework across all CRUD operations (CalificacionTributaria and InstrumentoFinanciero create/update/delete), mass data operations (bulk upload/export), and critical business logic (factor calculations, sum validation, data transformations), ensuring all operations log user identity, timestamp, affected objects, and operation outcome (success/failure).
4. **Documentation Enhancement:** Add or update docstrings for all functions (view functions, helper functions, model methods), classes (models, forms, custom managers), and modules to reflect the new unified structure, document function parameters and return values, explain complex business logic (factor calculations, validation rules), and improve overall code documentation quality for future maintainability.

### Task 1.5 – Update Architecture and Developer Documentation │ Agent_Analysis

- **Objective:** Update all project documentation to accurately reflect the refactored codebase structure including architecture documentation showing unified view organization, developer setup guides reflecting cleaned dependencies, and comprehensive migration/change log for development team transition guidance.
- **Output:** Updated architecture documentation reflecting unified view structure, revised developer setup and onboarding guides aligned with refactored codebase, detailed migration/change log documenting all structural changes and providing team guidance, and any updated diagrams or reference materials reflecting new organization.
- **Guidance:** Depends on: Task 1.4 Output by Agent_Refactor. Document the consolidated view structure with clear organization explanation. Update README.md and any setup guides to reflect refactored file structure. Create detailed change log documenting what changed, why it changed, and how team members should navigate the new structure. Address any database migration changes if they occurred.

**Sub-tasks:**

1. **Architecture Documentation Update:** Update architecture and structure documentation (README.md architecture section, any separate architecture docs) to reflect the new unified view structure, documenting the consolidated organization (single `views.py` with logical grouping), eliminated files (`views_admin.py`, `views_factores.py` removed), and rationale for structural changes.
2. **Setup Guide Revision:** Update developer setup and onboarding guides to reflect the cleaned-up dependencies and new codebase structure, ensuring new developers understand the unified architecture, know where to find specific functionality (admin functions, factor logic, CRUD operations), and have updated file navigation guidance.
3. **Migration/Change Log Creation:** Create detailed migration/change log documenting the view unification changes, any database adjustments or migration updates that occurred, guidance for development team on navigating the refactored codebase, mapping of old function locations to new locations, and explanation of new code organization principles for ongoing development.

## Phase 2: Environment Setup and Data Preparation

### Task 2.1 – Development Environment Configuration and Dependency Installation │ Agent_Environment

- **Objective:** Configure clean local development environment with Python virtual environment, install all project dependencies using frozen versions from requirements.txt, configure environment variables for database and Django settings, and verify installation readiness for database operations.
- **Output:** Fully configured development environment with activated virtual environment, all dependencies installed (Django 5.2.8, PostgreSQL adapter, testing libraries), `.env` file configured with database credentials and SECRET_KEY, successful Django configuration check, and documented environment ready for Phase 2 database operations.
- **Guidance:** Use frozen dependency versions to minimize risk (Django 5.2.8, psycopg2-binary 2.9.11, pytest 8.3.4 as specified in requirements.txt). Coordinate with User to obtain PostgreSQL credentials if not available. Generate new SECRET_KEY using Django's `get_random_secret_key()` utility. Verify environment with `python manage.py check` before proceeding.

**Sub-tasks:**

1. **Virtual Environment Setup:** Create and activate Python virtual environment using `python -m venv venv` and activation script (`venv\Scripts\activate` on Windows); install all dependencies from `requirements.txt` using frozen versions to ensure consistency with production environment (`pip install -r requirements.txt`).
2. **Environment Configuration:** Configure `.env` file with database credentials (DB_NAME=nuam_calificaciones_db, DB_USER, DB_PASSWORD, DB_HOST=localhost, DB_PORT=5432), generate and set SECRET_KEY using Django's utility function, set DEBUG=True for development, and configure ALLOWED_HOSTS; coordinate with User to obtain PostgreSQL credentials if needed.
3. **Installation Verification:** Verify Django installation and project configuration by running basic management commands (`python manage.py check` to validate settings, `python manage.py showmigrations` to verify migration detection) and confirm no critical configuration errors.
4. **Readiness Documentation:** Document any dependency issues encountered during installation, version conflicts if any arose, PostgreSQL connection parameters confirmed, and explicit confirmation that environment is ready for database operations in Task 2.2.

### Task 2.2 – Database Schema Creation and Migration Validation │ Agent_Environment

- **Objective:** Create PostgreSQL database for the project, execute Django migrations to establish database schema structure, validate migrations correctly reflect refactored codebase (especially after view unification), identify and resolve any migration inconsistencies, and verify complete schema integrity.
- **Output:** PostgreSQL database (`nuam_calificaciones_db`) created and accessible, all Django migrations executed successfully, validated migration files reflecting refactored models structure, any migration adjustments completed if inconsistencies found, and verified database schema with all tables, indexes, and constraints properly established.
- **Guidance:** Depends on: Task 2.1 Output. Coordinate with User for database creation permissions if needed. Pay special attention to migration validation after Phase 1 refactoring changes. Review existing migration files for legacy issues or inconsistencies introduced during refactoring. Create new migrations if model adjustments occurred. Verify schema completeness using PostgreSQL inspection tools or Django ORM queries.

**Sub-tasks:**

1. **Database Creation Coordination:** Coordinate with User to create PostgreSQL database (`nuam_calificaciones_db`) using `CREATE DATABASE nuam_calificaciones_db;` command in PostgreSQL, or verify database already exists and is accessible with correct permissions for the configured database user.
2. **Migration Execution:** Execute Django migrations to create database schema structure: first run `python manage.py makemigrations` to detect any new migrations needed after refactoring, then run `python manage.py migrate` to apply all migrations and create tables, indexes, and constraints in PostgreSQL.
3. **Migration Validation Analysis:** Review migration files in `calificaciones/migrations/` directory to validate they correctly reflect the refactored codebase structure (especially factor fields 8-12, model validations, indexes), identify any inconsistencies or legacy migration issues introduced during refactoring, and document findings.
4. **Migration Adjustments:** If migration issues identified in validation (inconsistent field definitions, missing indexes, legacy cruft), adjust migration files by editing them directly or create new migrations using `python manage.py makemigrations` to ensure clean schema state matching refactored models exactly.
5. **Schema Completeness Verification:** Verify database schema completeness by checking all expected tables exist (`Rol`, `PerfilUsuario`, `InstrumentoFinanciero`, `CalificacionTributaria`, `LogAuditoria`), all indexes are properly created (código_instrumento, fecha_informe, numero_dj indexes), and all constraints match model definitions (foreign keys, unique constraints, factor validation).

### Task 2.3 – Real Data Generation Command Implementation │ Agent_Environment

- **Objective:** Create new Django management command that generates realistic, production-like test data reflecting current business logic including proper factor calculations (factors 8-12), role-based user accounts, diverse financial instruments, tax qualifications with valid factor distributions, and comprehensive audit log entries.
- **Output:** New management command file `calificaciones/management/commands/generate_real_data.py` implemented with comprehensive data generation logic, command executed successfully populating database with production-like test data, verified data integrity with correct factor calculations (sum ≤ 1), proper role assignments, and realistic audit trails.
- **Guidance:** Depends on: Task 2.2 Output. Replace old test data commands (poblar_sistema.py, populate_demo_data.py) which use outdated logic. Generate users for all roles (Administrador, Analista, Auditor) with PerfilUsuario relationships. Create diverse instruments (stocks, bonds, ETFs). Generate qualifications ensuring factor 8-12 sum ≤ 1 validation. Create realistic audit log entries. Use Faker library for realistic data variation.

**Sub-tasks:**

1. **Command File Creation:** Create new management command file `calificaciones/management/commands/generate_real_data.py` following Django management command structure (inherit from `BaseCommand`, implement `handle()` method), with command-line arguments for data volume control (number of users, instruments, qualifications to generate).
2. **Data Generation Implementation:** Implement comprehensive data generation logic: create users with all three roles (Administrador with full permissions, Analista with create/edit permissions, Auditor with read-only), create PerfilUsuario instances linking users to roles with departamento assignments, generate diverse financial instruments (various tipos: Acción, Bono, ETF, Fondo Mutuo) with realistic códigos and nombres, create tax qualifications (CalificacionTributaria) with factor calculations ensuring factors 8-12 mathematically sum to ≤ 1, and generate audit log entries (LogAuditoria) reflecting realistic operations (CREATE, UPDATE, DELETE, LOGIN events) with proper user associations and timestamps.
3. **Command Execution:** Execute the management command to populate database with comprehensive test data set using `python manage.py generate_real_data`, specifying appropriate data volumes (e.g., 10 users, 50 instruments, 200 qualifications) to simulate realistic production environment for testing purposes.
4. **Data Integrity Verification:** Verify data integrity after generation: check user-role assignments are correct (users have PerfilUsuario with appropriate Rol), instrument variety is sufficient (multiple instrument types represented), qualification factor calculations are mathematically correct (factors 8-12 sum to ≤ 1.0 for all records), audit logs are properly generated with correct user associations and action types, and data relationships are valid (foreign keys intact, no orphaned records).

## Phase 3: Testing and Functional Validation

### Task 3.1 – Comprehensive Test Suite Design and Implementation │ Agent_QA

- **Objective:** Create complete pytest-based test suite from scratch covering all application functionality including CRUD operations, critical business rule validation (factor sum ≤ 1), role-based permission enforcement, audit logging verification, bulk operation testing, and unified view backward compatibility validation.
- **Output:** Comprehensive test suite in `calificaciones/tests/` directory with test files covering all functional areas (test_models.py, test_views.py, test_permissions.py, test_audit.py, test_bulk_operations.py), high test coverage of critical business rules and refactored view logic, and test fixtures providing necessary test data for all scenarios.
- **Guidance:** Create tests from scratch as existing tests are unreliable. Focus heavily on critical factor validation (sum factors 8-12 ≤ 1) which is core business rule. Test all three role types (Administrador, Analista, Auditor) with their specific permissions. Verify unified views maintain backward compatibility with all original routes. Use pytest-django framework and fixtures for test data setup.

**Sub-tasks:**

1. **CRUD Operation Tests:** Create test files structure in `calificaciones/tests/` directory (test_models.py, test_views.py) and implement comprehensive CRUD operation tests for CalificacionTributaria model (create, read, update, delete with all factor fields 8-12) and InstrumentoFinanciero model (all CRUD operations with código, nombre, tipo fields), including form validation tests and database integrity verification.
2. **Critical Business Rule Tests:** Implement critical business rule tests focusing on factor validation logic: test that sum of factors 8-12 equals or is less than 1 (acceptance cases), test that sum > 1 raises ValidationError (rejection cases), test bidirectional monto-factor calculations (monto to factor conversion, factor to monto conversion), test data integrity constraints (required fields, decimal precision, date validations).
3. **Role-Based Permission Tests:** Implement comprehensive role-based permission tests using pytest-django: create test users for each role (Administrador, Analista, Auditor), verify Administrador has full access to all CRUD operations and user management, verify Analista can create and edit but cannot delete records, verify Auditor has read-only access across all views and cannot modify data, test permission enforcement at view level and model level.
4. **Audit Logging Tests:** Implement audit logging tests to verify all CRUD operations generate appropriate LogAuditoria entries: test CalificacionTributaria create/update/delete operations log correctly, test bulk upload operations generate audit entries, test audit logs contain correct user identity, accurate timestamps, affected object references, and appropriate action types (CREATE, UPDATE, DELETE), verify audit log immutability.
5. **Bulk Operation Tests:** Implement bulk operation tests for CSV/Excel functionality: test bulk upload from valid CSV/Excel files with multiple qualifications, test data validation during bulk operations (reject invalid factor sums, reject malformed data), test export features generate correct CSV/Excel files with all data, test error handling for corrupted files or invalid formats.
6. **Unified View Backward Compatibility Tests:** Implement unified view tests to verify all routes from original `views_admin.py` and `views_factores.py` work correctly through unified `views.py`: test URL resolution for all admin routes (user management, dashboard), test factor calculation routes resolve correctly, test CRUD operation routes remain functional, verify route names unchanged, confirm backward compatibility with any external integrations or bookmarks.

### Task 3.2 – Test Execution and Results Analysis │ Agent_QA

- **Objective:** Execute complete test suite using pytest with coverage reporting, analyze test results to identify failures and coverage gaps, implement fixes for failing tests through iterative debugging, and achieve 100% test pass rate demonstrating refactored system maintains full functionality.
- **Output:** Complete test execution report showing 100% test pass rate, pytest coverage report with metrics for refactored codebase, documented resolution of all test failures encountered, analysis of any uncovered code paths, and confirmation that all critical functionality validated through automated testing.
- **Guidance:** Depends on: Task 3.1 Output. Run pytest with coverage flags to identify gaps. Analyze failures systematically: distinguish between test errors (incorrect test expectations) and implementation errors (bugs in refactored code). Fix implementation bugs in refactored views/models. Iterate execution until all tests pass. Document final coverage metrics and any deliberate exclusions from coverage.

**Sub-tasks:**

1. **Initial Test Execution:** Execute complete test suite using pytest with coverage reporting enabled (`pytest --cov=calificaciones --cov-report=html --cov-report=term tests/`) to generate comprehensive test results and code coverage analysis for the refactored codebase.
2. **Results Analysis:** Analyze test results and coverage report in detail: identify all failing tests with their error messages and stack traces, locate uncovered code paths in refactored views and models, determine root causes of failures (business logic errors vs test expectation mismatches vs refactoring bugs), prioritize fixes by severity and impact.
3. **Iterative Fixing:** Implement fixes for failing tests through systematic debugging: correct business logic errors in refactored implementation (view functions, model methods, validation logic), adjust test expectations if refactored logic is correct but test assumptions outdated, refactor problematic code if structural issues discovered in refactored implementation, add additional test cases for uncovered code paths identified in coverage report.
4. **Final Verification:** Re-execute test suite iteratively after each fix round until 100% test pass rate achieved; document final test execution report with all tests passing (X tests passed, 0 failed), coverage metrics showing percentage of code covered, any remaining uncovered code paths with justification for exclusion, and confirmation that all critical business rules validated successfully.

### Task 3.3 – Manual End-to-End Validation and User Sign-off │ Agent_QA

- **Objective:** Perform manual end-to-end testing of refactored application through web interface to validate functionality from user perspective, coordinate User testing of critical scenarios to ensure usability and correctness, and obtain formal User sign-off confirming 100% functionality preservation and readiness for production deployment consideration.
- **Output:** Django development server running and accessible, comprehensive manual testing checklist completed with all scenarios verified, User-performed testing validation of critical functionality (unified views, factor calculations, role-based access), documented manual testing results with any UI/UX observations, and formal User sign-off approval confirming refactored system ready for production.
- **Guidance:** Depends on: Task 3.2 Output. Manual testing complements automated tests by validating user experience, UI rendering, and real-world workflows. Guide User through systematic testing using prepared checklist. Focus User attention on unified view functionality (verify no broken routes), factor validation (test sum ≤ 1 enforcement), and role-based behavior. Document any UI issues separate from functional issues. Obtain explicit sign-off before considering Phase 3 complete.

**Sub-tasks:**

1. **Server Setup and Access Verification:** Start Django development server using `python manage.py runserver` on appropriate port (default 8000), verify application is accessible via browser at `http://127.0.0.1:8000/`, confirm login page renders correctly, test authentication with generated test users from Task 2.3 (Administrador, Analista, Auditor accounts).
2. **Testing Checklist Creation:** Create comprehensive manual testing checklist covering all critical functionality: CRUD operations through web UI (create new calificación, edit existing, view details, delete with confirmation), factor calculations and validation (test entering factors 8-12, verify sum ≤ 1 enforcement shows error when exceeded), role-based access verification (login as each role type, attempt operations beyond permissions, verify appropriate restrictions), bulk upload/export features (upload CSV, download Excel export), audit log generation visibility (check that operations appear in audit log), navigation and UI consistency across unified views.
3. **User Testing Coordination:** Guide User through manual end-to-end testing workflow using the prepared checklist, coordinate systematic testing of critical scenarios including unified view functionality (verify admin routes work, factor routes functional, no 404 errors), factor validation rules (attempt to create qualification with sum > 1, confirm rejection), role-based behavior (test Analista cannot delete, Auditor cannot edit), and bulk operations (upload sample data file).
4. **Results Documentation:** Document comprehensive manual testing results including: checklist items completed with pass/fail status, any UI issues observed (rendering problems, confusing workflows, styling inconsistencies), User feedback on functionality preservation and usability, performance observations (page load times, calculation speed), comparison notes between refactored system and original system behavior.
5. **Formal Sign-off:** Obtain formal User sign-off confirming that refactored system maintains 100% functionality, meets quality standards (code organization, performance, usability), successfully unifies view structure without functionality loss, and is ready for production deployment consideration (pending additional staging validation and database backup procedures).
