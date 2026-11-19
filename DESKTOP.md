# AIWCC Desktop para Kali Linux

AIWCC Desktop empaqueta la interfaz y el puente Python en una aplicación Electron. Al abrirla, inicia automáticamente el puente local, espera a que responda y abre la ventana de escritorio. Al cerrar la aplicación, detiene el proceso del puente.

## Requisitos de desarrollo
- Kali Linux x86_64
- Node.js 20 o posterior y npm
- Python 3
- Dependencias de compilación de Electron para Linux

## Ejecutar desde el repositorio

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

Instalar el paquete DEB:

```bash
sudo apt install ./dist/aiwcc_*_amd64.deb
```

Ejecutar AppImage:

```bash
chmod +x dist/AIWCC-*.AppImage
./dist/AIWCC-*.AppImage
```

## Comportamiento y seguridad
- El puente escucha solo en loopback (`127.0.0.1`).
- Si el puerto 8765 está ocupado, la aplicación selecciona un puerto local libre y pasa ese puerto al puente.
- La ventana usa `contextIsolation`, `sandbox` y `nodeIntegration: false`.
- No hay API de ejecución de comandos ni de workflows.
- El proceso del puente se inicia y se detiene junto con la aplicación.
- Los registros del puente se guardan en el directorio de datos de usuario de Electron, dentro de `logs/bridge.log`.

Esta versión es una primera distribución de escritorio para Linux x64. No incluye todavía firma de paquetes ni actualizador automático.
