# Reservas de laboratorios — Proyecto integrador

Backend sencillo para reservar laboratorios sin horarios superpuestos.
Sin frontend. Swagger permite la demostración REST y el cliente oficial permite la demo MCP.
Los datos de laboratorio son ejemplos; no representan disponibilidad institucional real.

## 1. Instalar en Windows (PowerShell)

Extrae el ZIP y abre una terminal dentro de `reservas-laboratorios` (donde está este README).
Necesitas Python 3.12 y conexión a Internet para instalar dependencias.

```powershell
py -3.12 --version
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe scripts\configurar.py
.\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
```

No hace falta activar el entorno virtual ni modificar la política de PowerShell.
Mantén esta terminal abierta. Ctrl+C detiene el servidor.

Abre http://127.0.0.1:8000/docs.
Si el puerto está ocupado, usa `--port 8001` y pasa `--url http://127.0.0.1:8001` a las demos.
`configurar.py` genera una clave aleatoria para `.env` y no sobrescribe uno existente.

Linux/macOS: `python3 -m venv .venv`, `.venv/bin/python -m pip install -r requirements.lock.txt`,
`.venv/bin/python scripts/configurar.py`,
`.venv/bin/python -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000`.

## 2. Demostración automática en otra terminal

```powershell
.\.venv\Scripts\python.exe scripts\demo_rest.py
.\.venv\Scripts\python.exe scripts\demo_mcp.py --demo
```

Cada demo crea cuentas locales con credenciales aleatorias; no las imprime.
Las demos crean una reserva para mañana y solicitan `SI` antes de cancelarla.
Si no confirmas, la reserva queda en la BD de demostración.
MCP sin `--demo` pide credenciales existentes y solo lista herramientas y reservas.

## 3. Demostración manual en Swagger

1. POST `/auth/registro`: registra un email de prueba y contraseña de 8–72 bytes.
2. Pulsa **Authorize**: username=email, password=tu contraseña; deja client_id/secret vacíos.
3. GET `/laboratorios/`: muestra los IDs disponibles.
4. POST `/reservas/`: usa una fecha futura real y el cuerpo siguiente.
5. Repite exactamente la reserva: debe responder 409 por solapamiento.
6. GET lista/individual y PUT: consulta y reemplaza los datos completos.
7. POST `/{id}/preparar-cancelacion`: revisa el resumen y copia `confirmacion`.
8. DELETE: confirmar=true, `X-Confirmacion`=token copiado; devuelve 204.
9. Cierra la autorización y llama GET `/reservas/`: debe responder 401.

```json
{
  "laboratorio_id": 1,
  "fecha": "2030-01-10",
  "hora_inicio": "09:00",
  "hora_fin": "10:00",
  "motivo": "Práctica de redes LAN"
}
```

Cambia la fecha si ya está en el pasado. Las horas usan Ecuador continental.
Dos reservas 09:00–10:00 y 10:00–11:00 son válidas; 09:30–10:30 produce conflicto.

## 4. Pruebas y cobertura

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing --cov-report=json
.\.venv\Scripts\python.exe scripts\verificar_cobertura.py
.\.venv\Scripts\python.exe -m ruff check app tests scripts
```

La suite usa BD SQLite temporal y un puerto efímero para MCP; no altera `reservas.db`.
Umbrales: services >=90% y global >=70%. El verificador falla si alguno no se cumple.
Consulta el resultado de esta entrega en `docs/VERIFICACION.md`.

## 5. Arquitectura

| Carpeta | Responsabilidad |
|---|---|
| app/routers | OAuth2, rutas REST y traducción HTTP |
| app/mcp | Tools y autenticación por transporte HTTP |
| app/services | Reglas de reserva y autenticación; reciben repositorios |
| app/repositories | Contratos Protocol y persistencia SQLAlchemy |
| app/models | Tablas Usuario/Reserva y FK |
| app/schemas | Entradas/salidas, formatos y validaciones |
| app/utils | Settings, JWT, hash, errores y BD |
| tests | Fakes, reglas unitarias, integración y MCP real |

REST y MCP llaman a `ReservaService`. No se acepta usuario_id del cliente.
La consulta de conflictos revisa todos los usuarios del mismo laboratorio sin exponer sus reservas.
SQLite serializa transacciones para evitar dobles reservas simultáneas; se utiliza un proceso local.

## 6. Spec-Kit y entrega

`constitution.md`, `spec.md`, `plan.md` y `tasks.md` describen esta implementación.
El scaffold oficial de Spec-Kit para Antigravity se incluye en `.agents` y `.specify`.
**Estos documentos fueron redactados aquí; no sustituyen la evidencia de ejecutar el
flujo en Antigravity que pide el curso.** Sigue `docs/SPECKIT.md` y conserva capturas reales.
Después documenta el trabajo usando la plantilla de informe de Moodle.

No subas `.env`, bases `.db`, `.venv` ni tokens al repositorio. El ZIP no los incluye.
Inicializa Git localmente cuando estés listo: `git init`, `git add .`, `git commit`.
No se ha creado ni publicado un repositorio remoto.

## Problemas frecuentes

- `py` no existe: instala Python 3.12 o usa `python` si apunta a 3.12.
- Error JWT_SECRET: ejecuta configurar.py; si `.env` ya existe, verifica una clave aleatoria de 32+ caracteres.
- 401: token caducado, sin Bearer o credenciales incorrectas; inicia sesión de nuevo.
- 409: el laboratorio ya está ocupado; cambia hora, fecha o laboratorio.
- 404: ID inexistente o reserva de otro usuario; no se revelan sus datos.
- Confirmación inválida: prepara otra; vence y una actualización invalida la anterior.
- MCP: usa `http://127.0.0.1:8000/mcp/` con barra final, Streamable HTTP y Authorization: Bearer.
- No necesita Docker, Postgres, Ollama ni una API key para funcionar.
