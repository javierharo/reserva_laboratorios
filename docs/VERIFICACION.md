# Verificación de entrega

Fecha: 2026-09-29 (Ecuador). Entorno: Linux, Python 3.12.14.

## Resultado medido
- 27 tests PASS, sin tests omitidos ni fallidos.
- app/services: 100.00% de cobertura de líneas.
- Global app: 99.79% de cobertura de líneas (468/469).
- Umbrales services 90% y global 70%: PASS.
- Ruff: All checks passed.

Comando: pytest --cov=app --cov-report=term-missing --cov-report=json.
Comprobación adicional: python scripts/verificar_cobertura.py.
La cobertura mide líneas ejecutadas; no demuestra ausencia de todos los errores posibles.

## Alcance de verificación
Tests unitarios R1–R8 con fakes inyectados, hash bcrypt, JWT inválido/expirado/mal firmado,
integración SQLite real, CRUD y aislamiento REST, concurrencia de dos creaciones,
confirmaciones vinculadas y no reutilización de IDs, transporte MCP HTTP con cliente oficial.

Ambos scripts de demostración se ejecutaron contra uvicorn local:
REST: 401, crear 201, conflicto entre usuarios 409, acceso ajeno 404, consulta/listado,
actualizar 200, preparación y cancelación 204.
MCP: seis tools, crear/listar, error de solapamiento, misma reserva visible en REST,
preparación y cancelación confirmada.

Se detectaron tres avisos de deprecación de dependencias (no errores):
alias BlockingPortal en Starlette y el cliente streamablehttp_client del SDK MCP.
La entrega fija las versiones verificadas; no se reescribió el sistema para eliminarlos.

## Límites y pendientes del estudiante
- No se ejecutó en un computador Windows; la guía usa Python 3.12, dependencias
  fijadas y tzdata para que America/Guayaquil esté disponible también allí.
- Scaffold Spec-Kit oficial instalado. Los documentos se redactaron en esta conversación;
  falta ejecutar/capturar el flujo del curso en Antigravity, según docs/SPECKIT.md.
- No se subió a GitHub ni Moodle; no se rellenó la plantilla de informe Moodle.
- No se entrega .env, BD con datos de prueba ni entorno virtual.

## Trazabilidad de la rúbrica
| Criterio | Evidencia en el proyecto |
|---|---|
| Arquitectura (20%) | app/services, Protocols en app/repositories/contracts.py, composición en dependencies.py |
| Seguridad (20%) | app/utils/security.py, config.py, routers/dependencies.py y middleware MCP |
| REST/MCP (25%) | app/routers/reservas.py, app/mcp/server.py y demos ejecutadas |
| Testing (20%) | tests/test_reservas.py, test_auth.py, test_integration.py y test_mcp_e2e.py |
| SDD (15%) | Cuatro documentos; recorrido Antigravity y evidencia del estudiante pendientes |
