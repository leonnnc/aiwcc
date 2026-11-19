# AIWCC Local Bridge

Puente local de observabilidad para AIWCC. Publica el estado del host y una detección básica de OpenCode. No ejecuta tareas, comandos arbitrarios ni modifica configuraciones.

## Requisitos

- Kali Linux / Linux con Python 3.9 o posterior.
- OpenCode es opcional; si está instalado, el Bridge intenta detectar versión, proceso, modelo configurado y cantidad de servidores MCP declarados en `~/.config/opencode/opencode.json`.

## Inicio

Desde la raíz del repositorio:

```bash
python3 bridge/server.py
```

Abre **http://127.0.0.1:8765**. El servidor escucha exclusivamente en loopback. Para cambiar el puerto:

```bash
AIWCC_PORT=8766 python3 bridge/server.py
```

## API

- `GET /api/health` — salud del Bridge.
- `GET /api/status` — host, detección de OpenCode y eventos recientes.
- `GET /api/events` — eventos recientes.
- `POST /api/telemetry` — recibe exclusivamente eventos JSON incluidos en una lista permitida; tamaño máximo 4 KiB.

## Seguridad y alcance

- Solo enlaza a `127.0.0.1`.
- El POST no ejecuta comandos ni acepta contenido de prompts, respuestas, archivos, argumentos de herramientas o credenciales.
- Los eventos se reducen a tipo y marca de tiempo; el Bridge genera títulos y descripciones locales.
- Los servidores MCP se cuentan desde la configuración local; no se afirma que estén conectados ni saludables.
- La detección de un proceso no garantiza que una sesión de OpenCode acepte trabajos.
- El Bridge no ofrece API para ejecutar workflows, shell ni acciones remotas.

## Pruebas automatizadas

Desde la raíz:

```bash
python3 -m unittest discover -s bridge -p 'test_*.py' -v
python3 -m py_compile bridge/server.py bridge/test_server.py
```

## Telemetría real de OpenCode

El repositorio incluye `.opencode/plugins/aiwcc-telemetry.js`. Para habilitar los eventos globalmente:

```bash
mkdir -p ~/.config/opencode/plugins
cp .opencode/plugins/aiwcc-telemetry.js ~/.config/opencode/plugins/aiwcc-telemetry.js
```

1. Inicia AIWCC Desktop o el Bridge con `python3 bridge/server.py`.
2. Reinicia OpenCode para cargar el plugin.
3. Abre AIWCC. La interfaz consulta el estado cada cuatro segundos.

El plugin utiliza `ctx.event.subscribe()`, cancela la suscripción al descargarse y reenvía únicamente los tipos permitidos. Los nombres de eventos se basan en la API oficial de OpenCode; esa API es experimental y puede cambiar. Si el Bridge está desconectado, la telemetría se descarta y OpenCode continúa funcionando.

Documentación oficial: [API de eventos](https://opencode.ai/docs/api) · [Plugins](https://opencode.ai/docs/build/plugins/migrate-v1/).
