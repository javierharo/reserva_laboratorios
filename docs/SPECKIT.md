# Recorrido SDD en Antigravity y evidencia auténtica

El curso pide /speckit.constitution, /speckit.specify, /speckit.plan,
/speckit.tasks y /speckit.implement. El proyecto ya incluye el scaffold oficial.
CLI origen: github/spec-kit, commit 2c0a57abe1e7383a864c7d5e4dfa2457d7537734.
Comando que se ejecutó aquí:

```text
specify init reservas-laboratorios --integration agy --script ps --ignore-agent-tools --non-interactive
```

En esa versión, `--ai` fue reemplazado por `--integration`; las skills se instalan
en `.agents/skills` y se llaman `/speckit-constitution`, `/speckit-specify`, etc.
El PDF usa los nombres anteriores. Usa los comandos que reconozca TU versión,
y verifica `specify init --help` antes de reinicializar nada.

## Qué está realizado y qué debes registrar

El backend y los documentos se construyeron en esta conversación. No se abrió
Antigravity ni se ejecutaron slash commands dentro de ese programa. No presentes
estos archivos como capturas o historial de una sesión que no ocurrió.

Para producir evidencia del procedimiento requerido, extrae otra copia de trabajo,
abre la carpeta en Antigravity y pide al agente revisar/recrear los artefactos y
contrastar su implementación con las reglas. Conserva el original como respaldo.
Si el instructor requiere construcción desde cero mediante esos comandos, empieza
en una carpeta nueva con el mismo alcance y utiliza este proyecto como referencia.

## Prompts listos

### Constitución
`/speckit-constitution`

Establece siete artículos para reservas de laboratorios: monolito modular con
routers/mcp/services/repositories/models/schemas/utils; DIP mediante repositorios
inyectados; SQLite y usuario_id FK; OAuth2 JWT bcrypt y .env con pydantic-settings;
CRUD REST protegido; tools MCP reutilizan servicios e identidad por JWT HTTP;
cancelación con preparación y confirmación firmada; tests fakes sin unittest.mock,
90% services y 70% global. Conflictos revisan todas las reservas del laboratorio
sin exponer datos de otros usuarios. Solo escribe la constitución.

### Especificación
`/speckit-specify`

Reservas de tres laboratorios de ejemplo: Usuario con email único y hash; Reserva
con laboratorio, fecha, inicio, fin, motivo y propietario. CRUD propio por REST y
MCP. Rechaza fin<=inicio, fechas pasadas y laboratorios inexistentes. Rechaza
solapamiento de cualquier usuario; permite horarios adyacentes. En lectura,
modificación y borrado de reserva ajena devuelve 404. Cancelación exige token
firmado preparado antes, vigente y ligado a usuario/ID/versión y confirmación
explícita. No hay frontend ni funciones adicionales. Cada regla tendrá un test.

### Aclaración
`/speckit-clarify`

Documenta: se admiten horas adyacentes; fecha actual permitida incluso si la hora
ya pasó; no cruza medianoche; catálogo fijo; horas America/Guayaquil; 404 para ID
ajeno; confirmación vence en 120 segundos; actualizaciones la invalidan.

### Plan y tareas
`/speckit-plan`

Python 3.12, FastAPI, SQLAlchemy 2, SQLite, Pydantic Settings, PyJWT, bcrypt,
MCP SDK 1.26.0 Streamable HTTP con JWT compartido. Protocols para DIP, sesiones
por solicitud/tool, transacciones SQLite BEGIN IMMEDIATE para comprobar y guardar
sin carreras. Sin frontend, Docker ni funcionalidades adicionales.

`/speckit-tasks`

Tareas por dependencias: modelos y schemas, repositorios, servicios con sus tests,
routers REST, tools MCP, integración SQLite, e2e MCP y cobertura. Una prueba
unitaria por cada regla explícita de spec.md, repositorios falsos inyectados.

### Análisis e implementación
`/speckit-analyze`

Comprueba que el plan contempla conflicto entre propietarios distintos,
protección ante creaciones concurrentes y confirmación ligada a versión.

`/speckit-implement`

Ejecuta tareas en orden. Antes de cada tarea muestra los archivos. Implementa y
prueba el mismo paso, explica cumplimiento de la constitución y declara cualquier
desviación. No incorpores frontend ni otras funciones. Al final ejecuta pytest
--cov=app --cov-report=term-missing --cov-report=json y comprueba 90% services
y 70% global. Si revisas el proyecto existente, identifica lo ya construido y
registra únicamente las modificaciones realmente ejecutadas.

## Capturas y decisiones

Conserva capturas de cada comando, artefactos producidos, tests PASS, cobertura,
CRUD Swagger y dos herramientas MCP. Si corriges al agente, registra el error
real, instrucción de corrección, cambio y test que lo verifica. No inventes
una corrección realizada por ti. `docs/REVISION.md` identifica revisiones de esta
construcción para que comprendas el criterio técnico; no es historial de Antigravity.

La plantilla de informe Moodle no fue adjuntada y no se ha rellenado.
