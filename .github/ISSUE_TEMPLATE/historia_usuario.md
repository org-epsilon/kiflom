# Historia de Usuario: Visualización de Catálogo Interactivo 3D

**Épica:** Experiencia de Usuario y Catálogo Multimedia
**ID:** US-001
**Puntos de Historia (Story Points):** 5

## Descripción
**COMO** cliente potencial de Deportivos Guadalupe,
**QUIERO** seleccionar una marca en la barra de navegación para ver la información detallada del vehículo y un modelo 3D interactivo,
**PARA** poder explorar el diseño del auto desde todos los ángulos antes de agendar un Test Drive.

## Criterios de Aceptación
1. **Filtro por marca:** Al hacer clic en el logo de una marca (ej. Bugatti), la página debe mostrar solo los vehículos de esa marca.
2. **Visualización 3D:** La vista de detalle del auto debe incluir un reproductor 3D (vía Sketchfab embed).
3. **Interacción:** El usuario debe poder rotar el modelo 3D con el clic sostenido y hacer zoom con la rueda del ratón.
4. **Diseño Responsivo:** El contenedor del modelo 3D debe adaptarse al tamaño de la pantalla (móvil y escritorio) sin romper la estructura de la página.
5. **Tema Oscuro:** El iframe embebido debe utilizar el parámetro `ui_theme=dark` para mantener la estética del concesionario.