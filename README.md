# AI Workflow Command Center (AIWCC)

Panel web inicial para visualizar y administrar un ecosistema de desarrollo con Kali Linux, OpenCode, modelos de IA, proveedores, MCP e integraciones.

## Estado actual

Esta versión es un **prototipo frontend estático**. Incluye:
- Panel lateral izquierdo e inspector derecho contraíbles.
- Vista de topología con nodos seleccionables.
- Indicadores, estado de servicios y actividad de demostración.
- Diseño adaptable a escritorio y pantallas pequeñas.

## Limitaciones conocidas

- Los datos y eventos de la topología son demostrativos.
- El puente local todavía no está conectado.
- Los nodos aún no implementan el editor completo de workflows (arrastrar, conectar, zoom, persistencia).
- No ejecuta comandos en Kali ni se conecta a OpenCode.

## Ejecutar localmente

Abre `index.html` en un navegador. No requiere dependencias para esta versión estática.

## Próximas etapas

1. Editor visual de nodos: arrastrar y soltar, puertos de conexión y múltiples enlaces.
2. Persistencia de posiciones y conexiones.
3. Backend/puente local autenticado para telemetría y acciones autorizadas.
4. Integración real con OpenCode, MCP y servicios del entorno Kali.
5. Registro de eventos, permisos, auditoría y pruebas.

## Seguridad

No incluir API keys, tokens, contraseñas ni datos sensibles en el repositorio.
