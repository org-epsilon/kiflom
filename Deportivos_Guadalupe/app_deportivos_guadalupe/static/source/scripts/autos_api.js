// autos_api.js - Consumo asíncrono de datos del concesionario

async function obtenerDatosSucursales() {
    const urlJSON = '/static/source/data/json/sucursales.json';

    try {
        const respuesta = await fetch(urlJSON);
        if (!respuesta.ok) {
            throw new Error(`Error en la petición: ${respuesta.status}`);
        }
        
        const sucursales = await respuesta.json();
        console.log("Sucursales de Deportivos Guadalupe cargadas con éxito:", sucursales);
        
        // Ejemplo de iteración de datos para la interfaz
        sucursales.forEach(sede => {
            console.log(`Sede ID ${sede.id}: ${sede.nombre} en ${sede.ciudad}`);
        });

    } catch (error) {
        console.error("No se pudieron cargar los datos de las sucursales:", error);
    }
}

// Ejecutar cuando la página cargue por completo
document.addEventListener('DOMContentLoaded', obtenerDatosSucursales);