# Constitución — Reservas de laboratorios

## I. Arquitectura
Monolito modular: routers, mcp, services, repositories, models, schemas y utils.
REST y MCP son adaptadores de los mismos servicios. No contienen reglas de reservas.

## II. SOLID y DIP
Los servicios reciben repositorios mediante parámetros y dependen de Protocol.
No importan repositorios SQLAlchemy. Los tests unitarios inyectan fakes; no usan unittest.mock.

## III. Persistencia
Usuario y Reserva se relacionan mediante usuario_id como clave foránea.
Toda lectura individual o listado privado de reservas filtra usuario_id.
La consulta de conflictos puede revisar reservas de TODOS los usuarios del mismo laboratorio,
pero devuelve exclusivamente un booleano y no expone sus datos.
Los repositorios persisten; el servicio decide si existe un conflicto.
Comprobar y guardar se ejecutan en una transacción SQLite BEGIN IMMEDIATE.

## IV. Seguridad
Registro propio, OAuth2 Password Bearer y JWT HS256 de duración limitada.
Contraseñas bcrypt, nunca texto plano en BD ni respuestas.
JWT_SECRET proviene de .env con pydantic-settings, sin valor predeterminado real.
.env se excluye de Git y de la entrega; .env.example sí se versiona.
Todas las rutas de reservas y laboratorios requieren JWT válido. MCP usa el mismo JWT
en Authorization: Bearer, jamás un usuario_id enviado por el cliente.

## V. REST
CRUD completo, schemas separados de modelos. Identidad desde dependencia autenticada.
Los errores de dominio se traducen a HTTPException. Validación de formatos produce 422.
No se revelan datos de reservas ajenas: se responde 404 tanto si no existe como si no es propia.

## VI. MCP
Cada tool llama al mismo servicio utilizado por REST; las descripciones documentan sus efectos.
Errores de dominio: {"error": "mensaje", "code": "codigo"}.
Cancelar requiere una preparación previa, una confirmación firmada de corta duración
y confirmar=true. El servidor comprueba usuario, ID, versión y finalidad del token.
La interfaz cliente debe mostrar el resumen y pedir aprobación humana antes de cancelar.

## VII. Pruebas y gobierno
Una prueba unitaria identificable por cada regla R1–R8 de spec.md.
Cobertura services >=90%, global >=70%, pytest-cov y al menos una integración con SQLite real.
Una prueba MCP por transporte real con el cliente oficial del SDK.
Las modificaciones de reglas deben actualizar spec, plan, tareas y pruebas.
Toda desviación se documenta antes de alterar el alcance; no se mezclan capas silenciosamente.

Versión: 1.0.0. Ratificada: 2026-09-29. Última revisión: 2026-09-29.
