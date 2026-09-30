# Guion de demostración (10–12 minutos)

## 1. Problema (1 min)
«Dos estudiantes pueden intentar reservar el mismo laboratorio en el mismo horario.
El sistema gestiona reservas propias y evita superposiciones entre cualquier usuario.»
El alcance son tres laboratorios de ejemplo y un backend local.

## 2. Arquitectura (2 min)
Abre app/services/reservas.py, app/repositories/contracts.py y un router/tool.
«REST y MCP llaman a ReservaService. El servicio recibe un repositorio por parámetro.
Los repositorios conocen la base; el servicio decide las reglas de negocio.»
Señala `_check_overlap`, `_validate`, `atomic` y los fakes en tests/fakes.py.

## 3. REST y seguridad (3 min)
Usa Swagger o scripts/demo_rest.py. Muestra 401 sin token, registro, login,
crear 201, listar, consultar, actualizar y cancelar 204 con confirmación.
Muestra un conflicto 409 y una consulta ajena 404. No muestres secretos reales.
«El JWT determina usuario_id; el cliente no puede elegir otro propietario.»

## 4. MCP (2 min)
Ejecuta scripts/demo_mcp.py --demo. Muestra nombres/descripciones de tools,
crear y listar; REST muestra la misma reserva; repetición devuelve solapamiento.
Revisa el resumen de cancelación y escribe SI solo si quieres borrarla.
«MCP es otra interfaz hacia los mismos servicios y usa el JWT del login REST.»

## 5. Tests (2 min)
Ejecuta pytest --cov=app --cov-report=term-missing --cov-report=json y el verificador.
Señala la regla R2 en spec.md y test_R2_solapamiento; luego R3 y test_R3_aislamiento.
Explica el test SQLite concurrente y test_mcp_transporte_real.

## 6. SDD (2 min)
Muestra constitución, spec, plan y tareas. Usa tus capturas auténticas del recorrido
de Antigravity, cuando lo hayas realizado. Describe una corrección real que hayas
pedido al agente; no atribuyas al estudiante las revisiones técnicas hechas aquí.

## Preguntas de defensa
| Pregunta | Respuesta |
|---|---|
| ¿Por qué la regla está en services? | REST y MCP necesitan exactamente la misma decisión. |
| ¿Por qué inyectar el repository? | Permite sustituir SQL por un fake y probar reglas sin BD. |
| ¿Qué ocurre si falta validar JWT? | Se pierde la identidad confiable y el aislamiento de datos. |
| ¿Dos usuarios pueden solaparse? | No: el conflicto se verifica sobre el laboratorio, no solo sobre el propietario. |
| ¿Cómo evitas dos solicitudes simultáneas? | Transacción SQLite BEGIN IMMEDIATE durante consulta y guardado. |
| ¿La confirmación es solo un booleano? | No: requiere también token previo, firmado, vigente y vinculado a reserva/usuario/versión. |
| ¿Por qué 404 para reserva ajena? | No revela que otra persona tiene ese ID; decisión especificada. |

Antes de presentar, ejecuta ambos scripts y los tests en el computador que usarás.
