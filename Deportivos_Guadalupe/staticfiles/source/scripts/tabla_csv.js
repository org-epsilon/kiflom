// tabla_csv.js - Renderizado del inventario desde archivo CSV

async function renderizarTablaInventario() {
    const urlCSV = '/static/source/data/tabs/inventarios_autos.csv';

    try {
        const respuesta = await fetch(urlCSV);
        const textoCSV = await respuesta.text();

        // Separar las líneas del archivo CSV
        const lineas = textoCSV.trim().split('\n');
        
        const thead = document.getElementById('tabla-encabezado');
        const tbody = document.getElementById('tabla-cuerpo');

        if (!thead || !tbody) return; // Validación de existencia en el DOM

        // 1. Procesar Encabezados (Primera línea del CSV)
        const columnasHeader = lineas[0].split(',');
        thead.innerHTML = '<tr>' + columnasHeader.map(header => `<th>${header.toUpperCase().trim()}</th>`).join('') + '</tr>';

        // 2. Procesar Filas de Vehículos
        tbody.innerHTML = '';
        for (let i = 1; i < lineas.length; i++) {
            if (lineas[i].trim() === '') continue; // Ignorar líneas vacías
            
            const columnas = lineas[i].split(',');
            const filaHTML = '<tr>' + columnas.map(col => `<td>${col.trim()}</td>`).join('') + '</tr>';
            tbody.innerHTML += filaHTML;
        }

    } catch (error) {
        console.error("Error al leer el inventario de autos CSV:", error);
    }
}

document.addEventListener('DOMContentLoaded', renderizarTablaInventario);