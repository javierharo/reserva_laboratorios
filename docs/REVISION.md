# Revisión técnica real de esta construcción

## API del CLI Spec-Kit
El comando del PDF con `--ai agy` falló: el CLI descargado ya no reconoce --ai.
Se consultó `specify init --help` y se inicializó con `--integration agy`.
No se cambió la arquitectura ni el alcance para resolverlo.

## Cancelación y reutilización de IDs SQLite
Durante la revisión del código se detectó que la clave primaria SQLite puede
reutilizar el último ID borrado. Una confirmación anterior vinculada solo a ID y
versión podría entonces coincidir con una reserva nueva del mismo usuario.
Se añadió `sqlite_autoincrement=True` al modelo Reserva: los IDs borrados no se
reciclan. Se añadió `test_cancelacion_no_reutiliza_id` contra SQLite real para
demostrar que la confirmación antigua no cancela una reserva nueva.
Esta es una corrección del agente durante esta conversación, no una instrucción
de corrección del estudiante ni una captura de Antigravity.

## Decisiones revisables
- Los conflictos revisan todos los propietarios, mientras los listados son privados.
- BEGIN IMMEDIATE serializa transacciones para que comprobar/guardar sea atómico.
- JWT de acceso y confirmación tienen finalidades distintas y no son intercambiables.
- 404 para reserva ajena evita revelar su existencia; está declarado en la spec.
- El servidor valida preparación/confirmación; el cliente pide aprobación humana.
  Un servidor no puede comprobar por sí mismo que una persona haya pulsado «sí»;
  el cliente de demostración sí solicita esa entrada. No se atribuye esa capacidad al JWT.
- No se usa frontend ni se incluyen funciones fuera del alcance acordado.
