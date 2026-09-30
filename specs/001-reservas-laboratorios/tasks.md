# Tareas

## Preparación
- [x] T001 Crear configuración y schemas en app/utils/config.py y app/schemas/.
- [x] T002 Crear modelos y sesión en app/models/ y app/utils/database.py.
- [x] T003 Crear contratos y repositorios en app/repositories/.

## US1 — Seguridad
- [x] T004 [US1] Crear hash/JWT en app/utils/security.py y tests unitarios de seguridad.
- [x] T005 [US1] Implementar AuthService en app/services/auth.py con fake en tests/.
- [x] T006 [US1] Implementar login/registro y dependencias en app/routers/auth.py.

## US2 — Reservas
- [x] T007 [US2] Escribir pruebas R1–R5 con repositorio fake en tests/test_reservas.py.
- [x] T008 [US2] Implementar reglas y CRUD en app/services/reservas.py.
- [x] T009 [US2] Implementar CRUD REST en app/routers/reservas.py.

## US3 — Cancelación y MCP
- [x] T010 [US3] Implementar confirmación vinculada y pruebas R6 en app/services/reservas.py.
- [x] T011 [US3] Implementar tools y middleware autenticado en app/mcp/server.py.
- [x] T012 [US3] Implementar demo con cliente oficial en scripts/demo_mcp.py.

## Verificación y entrega
- [x] T013 Verificar BD y concurrencia en tests/test_integration.py.
- [x] T014 Verificar HTTP MCP real en tests/test_mcp_e2e.py.
- [x] T015 Ejecutar cobertura y comprobar servicios con scripts/verificar_cobertura.py.
- [x] T016 Crear guía de instalación, SDD y demo en README.md y docs/.
