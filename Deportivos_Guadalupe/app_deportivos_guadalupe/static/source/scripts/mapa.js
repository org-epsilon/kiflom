const mapa = L.map('mapa').setView([4.651, -74.051], 13);
const capaPuntos = L.layerGroup().addTo(mapa);
const clavePuntosGuardados = 'coderider-puntos-encuentro';
const estadoMapa = document.getElementById('estado-mapa');

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap - Deportivos Guadalupe'
}).addTo(mapa);

function mostrarEstado(mensaje) {
    if (estadoMapa) estadoMapa.textContent = mensaje;
}

function crearPopup(punto) {
    const contenido = document.createElement('div');
    const titulo = document.createElement('strong');
    titulo.textContent = punto.nombre;
    const descripcion = document.createElement('p');
    descripcion.textContent = punto.descripcion || 'Sin descripción';
    contenido.append(titulo, descripcion);
    return contenido;
}

function agregarMarcador(punto, guardar = false) {
    const marcador = L.marker(punto.coords).addTo(capaPuntos);
    marcador.bindPopup(crearPopup(punto));

    if (guardar) {
        const guardados = JSON.parse(localStorage.getItem(clavePuntosGuardados) || '[]');
        guardados.push(punto);
        localStorage.setItem(clavePuntosGuardados, JSON.stringify(guardados));
    }
}

window.agregarPuntoEncuentro = agregarMarcador;

const marcadorPrincipal = L.marker([4.651, -74.051]).addTo(capaPuntos);
marcadorPrincipal.bindPopup(crearPopup({
    nombre: 'Deportivos Guadalupe',
    descripcion: 'Showroom principal y vitrina VIP.'
}));

fetch('/static/source/data/json/sucursales.json')
    .then(respuesta => respuesta.json())
    .then(sucursales => sucursales.forEach(sede => agregarMarcador({
        nombre: sede.nombre,
        coords: sede.coordenadas,
        descripcion: sede.ciudad
    })))
    .catch(() => mostrarEstado('No se pudieron cargar las sucursales.'));

fetch('/static/source/data/geo/sede_guadalupe.geojson')
    .then(respuesta => respuesta.json())
    .then(datos => L.geoJSON(datos, {
        style: { color: '#e07a35', weight: 2, fillOpacity: 0.12 }
    }).addTo(mapa))
    .catch(() => mostrarEstado('No se pudo cargar el perímetro del showroom.'));

JSON.parse(localStorage.getItem(clavePuntosGuardados) || '[]')
    .forEach(punto => agregarMarcador(punto));

mapa.on('click', evento => {
    const nombre = document.getElementById('nombre-punto').value.trim();
    const descripcion = document.getElementById('descripcion-punto').value.trim();

    if (!nombre) {
        mostrarEstado('Escribe un nombre antes de seleccionar el mapa.');
        return;
    }

    agregarMarcador({
        nombre,
        descripcion,
        coords: [evento.latlng.lat, evento.latlng.lng]
    }, true);
    mostrarEstado(`Punto "${nombre}" añadido correctamente.`);
});

const botonLimpiarPuntos = document.getElementById('limpiar-puntos');

botonLimpiarPuntos?.addEventListener('click', () => {
    localStorage.removeItem(clavePuntosGuardados);
    window.location.reload();
});