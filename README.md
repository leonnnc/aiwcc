# AI Workflow Command Center (AIWCC)

AIWCC es una central local de observabilidad para el entorno de desarrollo: host Kali, OpenCode, proveedores, modelos, servidores MCP e integraciones.

## Estado de esta versión

La interfaz web incluye:
- Topología visual con nodos, conexiones múltiples y enlaces SVG.
- Movimiento de nodos, selección de puertos de entrada/salida y persistencia local del diagrama.
- Panel de navegación e inspector contraíbles.
- Estado del host y OpenCode obtenido desde el Bridge local.
- Actividad basada en eventos permitidos enviados por el plugin de OpenCode.

La aplicación de escritorio Electron para Linux x64 está configurada en `package.json` y `electron/`. El workflow de GitHub Actions valida el código, ejecuta pruebas del Bridge y genera paquetes AppImage y DEB.

## Alcance y límites

- El Bridge es de observabilidad local y solo lectura: no ejecuta comandos, no lanza workflows ni modifica OpenCode.
- El número MCP mostrado corresponde a servidores declarados en la configuración; no certifica que estén conectados o saludables.
- La telemetría depende de instalar el plugin y reiniciar OpenCode.
- La topología es una representación visual editable; no implica que cada línea sea una conexión de red real.
- La versión actual no incluye actualizador automático ni firma de paquetes.

## Ejecutar como aplicación de escritorio

Requisitos: Kali Linux x86_64, Node.js 20+, npm y Python 3.

```bash
npm install
npm start
```

## Generar instaladores

```bash
npm install
npm run dist:linux
```

Los artefactos se generan en `dist/`:
- `AIWCC-*.AppImage`
- `aiwcc_*_amd64.deb`

Consulta [DESKTOP.md](DESKTOP.md) para instalar y ejecutar los paquetes.

## Bridge y telemetría

```bash
python3 bridge/server.py
```

El servidor escucha solo en `127.0.0.1`. Para integrar eventos de OpenCode, consulta [bridge/README.md](bridge/README.md).

## Desarrollo y pruebas

```bash
node --check electron/main.cjs
python3 -m py_compile bridge/server.py bridge/test_server.py
python3 -m unittest discover -s bridge -p 'test_*.py' -v
npm run dist:linux
```

El workflow ejecuta estas validaciones automáticamente en cada push a `main` y al publicar una etiqueta `desktop-v*`.

## Seguridad

No añadas API keys, tokens, contraseñas, prompts ni respuestas al repositorio. La telemetría transmite solo tipos de evento permitidos y marcas de tiempo; no reenvía contenido de prompts, respuestas, argumentos de herramientas ni credenciales.
