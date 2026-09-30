# Plan técnico

Python 3.12, FastAPI, SQLAlchemy 2, SQLite, Pydantic Settings, PyJWT, bcrypt
y MCP SDK 1.26.0. Versiones fijadas y lock de dependencias probadas.

## Orden de implementación
1. Configuración, schemas de entrada/salida y modelos Usuario/Reserva.
2. Protocols de repositorios y persistencia con sesión inyectada.
3. Utilidades de hash/JWT; servicios AuthService y ReservaService.
4. Routers OAuth2/CRUD; traducción centralizada de errores de dominio a HTTPException.
5. MCP con contexto autenticado, sesión por tool y mismos servicios.
6. Fakes unitarios, integración SQLite, concurrencia y cliente MCP real.
7. Guía Windows, demostración y verificación de umbrales.

## Correspondencia con constitución
I–II: services importa únicamente Protocols, schemas y utils. Composition root en dependencies.
III: SQLAlchemy repositorios; BEGIN IMMEDIATE bloquea escrituras SQLite durante
comprobación y guardado para impedir la carrera entre dos creaciones simultáneas.
IV: JWT con purpose=access, exp, sub, issuer y audience; env sin valores reales en ZIP.
V: APIRouter y depends(get_current_user); schemas extra=forbid.
VI: Middleware ASGI limita JWT a MCP y establece ContextVar con usuario autenticado.
Token de cancelación purpose=cancel y versión de reserva impide usar una vista antigua.
VII: tests fakes sin mocks, BD temporal real, MCP con servidor efímero y pytest-cov.

## Límites
SQLite es suficiente para demostración local. El despliegue distribuido requeriría
otra estrategia de exclusión de horarios y migraciones. No se despliega el sistema
ni se necesita una API key de un proveedor de IA para correr el backend/cliente MCP.

## Procedencia SDD
Scaffold oficial Spec-Kit inicializado con integración agy; los cuatro documentos
de esta entrega son redactados y revisados en esta conversación. No son evidencia
de haber ejecutado slash commands dentro de Antigravity. docs/SPECKIT.md detalla
cómo realizar y capturar ese recorrido, requerido por la evaluación del curso.
