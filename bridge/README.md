# AIWCC Local Bridge

Puente local de observabilidad para AIWCC. La primera versión es deliberadamente **solo lectura**: publica el estado del host y una detección básica de OpenCode, sin ejecutar tareas, comandos arbitrarios ni modificar configuraciones.

## Requisitos
- Kali Linux / Linux con Python 3.9 o posterior.
- OpenCode es opcional para iniciar el panel; si está instalado, el puente intenta detectar su versión, proceso, modelo configurado y cantidad de servidores MCP declarados en `~/.config/opencode/opencode.json`.

## Inicio
Desde la raíz del repositorio:

```bash
python3 bridge/server.py
```

Abre **http://127.0.0.1:8765**. El servidor escucha exclusivamente en loopback (no expone el puerto a la red). Para cambiar el puerto:

```bash
AIWCC_PORT=8766 python3 bridge/server.py
```

## API
- `GET /api/health` — salud del puente.
- `GET /api/status` — host, detección de OpenCode y eventos recientes.
- `GET /api/events` — eventos recientes.

## Seguridad y alcance
- Solo enlaza a `127.0.0.1`.
- No ofrece endpoints POST, ejecución de shell, acceso a archivos arbitrarios ni control remoto.
- Los datos de estado son informativos; la detección de un proceso no garantiza que una sesión de OpenCode acepte trabajos.
- Los servidores MCP se cuentan desde la configuración local; no se afirma que estén conectados ni saludables.
- La telemetría de modelos, tokens, solicitudes y respuestas requiere integraciones específicas y autenticadas; no se simula como si fuera real.

Para detenerlo, usa `Ctrl+C` en la terminal donde se inició.


## Pruebas automatizadas

Desde la raíz del repositorio:

```bash
python3 -m unittest discover -s bridge -p 'test_*.py' -v
python3 -m py_compile bridge/server.py bridge/test_server.py
```
