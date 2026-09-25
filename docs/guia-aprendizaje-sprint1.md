# Guía de Aprendizaje - Sprint 1: Fundamentos y Entorno

## Objetivo del Sprint
Configurar la arquitectura base del proyecto "Deportivos Guadalupe" utilizando Python y Django, implementando un árbol de directorios organizado para el manejo de archivos estáticos y multimedia.

## Hitos Alcanzados
1. **Entornos Virtuales:** Creación y activación de un entorno virtual (`venv`) para aislar las dependencias del proyecto.
2. **Arquitectura MVT (Model-View-Template):** 
   - Creación del proyecto principal y la aplicación de autos deportivos.
   - Conexión exitosa entre las URLs del proyecto y las URLs de la app.
   - Renderizado de vistas HTML (Login y Garaje).
3. **Manejo de Archivos Estáticos (`static`):**
   - Configuración de `settings.py` para servir archivos locales.
   - Organización estructural por tipo de archivo: `audios/`, `videos/`, `imagenes/`, `libs/`, `scripts/` y `data/`.
4. **Integración Multimedia:**
   - Uso de etiquetas `<audio>` y `<video>` en HTML5 con subtítulos `.vtt`.
   - Incorporación de mapas interactivos con Leaflet.js.

## Siguientes Pasos (Sprint 2)
- Implementar peticiones asíncronas con `fetch()` en JavaScript.
- Conectar modelos de bases de datos para el inventario de vehículos.
- Integrar visor de modelos 3D mediante `iframes` de Sketchfab.