# Especificación — Reservas de laboratorios

## Objetivo y alcance
Usuarios autenticados reservan uno de tres laboratorios de ejemplo (Computación,
Redes y Telecomunicaciones). No se incluye frontend, roles de administrador, correos
ni integración con sistemas UNACH. Los nombres son datos de demostración.

## Historias de usuario
US1: registrarme e iniciar sesión para gestionar mis reservas sin acceder a las ajenas.
US2: crear, consultar, listar y reemplazar una reserva, evitando conflictos de horario.
US3: revisar el resumen y confirmar una cancelación; utilizar el mismo sistema desde MCP.

## Entidades
Usuario: id, email único normalizado, password_hash.
Reserva: id, usuario_id FK, laboratorio_id (1–3), fecha, hora_inicio, hora_fin,
motivo (1–200 caracteres), version (entero para invalidar confirmaciones antiguas).
Las horas son locales de Ecuador continental, sin zona ni fracción de segundo.

## Reglas de negocio y pruebas obligatorias
R1: fin > inicio, sin reserva que cruce medianoche. test_R1_horario_invalido.
R2: para el mismo laboratorio y fecha, inicio_nuevo < fin_existente y
fin_nuevo > inicio_existente es conflicto, sin importar el propietario.
Se aplica a creación y actualización. Intervalos adyacentes se permiten.
test_R2_solapamiento y test_R2_actualizacion.
R3: listar, consultar, actualizar y cancelar operan solo sobre reservas del usuario.
No existe acceso a reservas ajenas mediante ID; respuesta 404 sin revelar propietario.
test_R3_aislamiento.
R4: fecha no anterior al día actual de America/Guayaquil. El día actual está permitido,
incluso para horas ya transcurridas (alcance deliberado de este MVP).
test_R4_fecha_pasada.
R5: laboratorio debe ser 1, 2 o 3. test_R5_laboratorio.
R6: cancelación exige confirmar=true y token firmado de preparación, ligado a usuario,
reserva y versión; caduca en 120 segundos. No sirve JWT de acceso ni otra confirmación.
test_R6_confirmacion.
R7: registro rechaza email duplicado ignorando mayúsculas. test_R7_email_duplicado.
R8: solo contraseña correcta permite login; JWT caducado, mal firmado o de otro tipo
no autentica. test_R8_login y test_R8_tokens.

## Contrato REST
| Método | Ruta | Éxito | Requiere JWT |
|---|---|---|---|
| POST | /auth/registro | 201 usuario sin hash | No |
| POST | /auth/token | 200 access_token, token_type | No, formulario OAuth2 |
| GET | /laboratorios/ | 200 catálogo | Sí |
| POST | /reservas/ | 201 reserva | Sí |
| GET | /reservas/?skip=0&limit=20 | 200 lista propia | Sí |
| GET | /reservas/{id} | 200 reserva propia | Sí |
| PUT | /reservas/{id} | 200 reemplazo completo | Sí |
| POST | /reservas/{id}/preparar-cancelacion | 200 resumen y confirmacion | Sí |
| DELETE | /reservas/{id}?confirmar=true | 204 | Sí, X-Confirmacion adicional |

Crear/PUT: laboratorio_id, fecha YYYY-MM-DD, hora_inicio HH:MM, hora_fin HH:MM, motivo.
Errores: 400 reglas inválidas/confirmación, 404 no encontrada o ajena,
409 solapamiento/email duplicado, 401 sin autenticación, 422 formato.
Campos extra como usuario_id se rechazan con 422. Paginación: skip>=0, limit 1–100.
Contraseña: mínimo 8 caracteres y máximo 72 bytes UTF-8 por límite bcrypt.

## Contrato MCP
Streamable HTTP /mcp con Authorization: Bearer del login REST.
Tools: crear_reserva, listar_reservas, consultar_reserva, actualizar_reserva,
preparar_cancelacion, cancelar_reserva. Identidad extraída por middleware del JWT.
Las entradas replican schemas REST; errores {error, code}. Preparar no borra.
Cancelar exige confirmacion y confirmar=true; el operador debe aprobar tras ver el resumen.

## Criterios de aceptación
CRUD REST completo y al menos dos tools MCP demostrados en vivo.
Dos usuarios con horarios superpuestos reciben un rechazo sin exposición de datos ajenos.
Un test por regla, >=90% services y >=70% global medidos automáticamente.
Integración real SQLite, comprobación de concurrencia y demo del transporte MCP.
Los documentos describen el comportamiento implementado y sus límites.

## Decisiones de aclaración
Se permiten intervalos adyacentes. Se permiten fechas actuales y futuras.
Catálogo fijo para mantener el alcance simple. SQLite local, un proceso uvicorn.
404 para reserva ajena es una decisión de privacidad; difiere del 403 del ejemplo opcional
del PDF y queda declarada aquí. No se añade capacidad, recurrencia ni aprobación institucional.
