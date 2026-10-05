const mapa = L.map('mapa').setView([4.651, -74.051], 13);
const ubicacionesLayer = L.layerGroup().addTo(mapa);
const rutasLayer = L.layerGroup().addTo(mapa);
const ubicaciones = [];
const rutas = [];
let locationMode = 'location';
let routeActive = false;
let routePoints = [];
let routeGeometry = [];
let routeLine = null;

const endpoints = {
    ubicaciones: '/guadalupe/feat-map/api/ubicaciones/',
    rutas: '/guadalupe/feat-map/api/rutas/'
};

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(mapa);

function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>'"]/g, character => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
    }[character]));
}

function setStatus(message, target = 'map-status') {
    const element = document.getElementById(target);
    if (element) element.textContent = message;
}

function csrfToken() {
    return document.querySelector('meta[name="csrf-token"]')?.content || '';
}

async function requestJson(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken(),
            ...(options.headers || {})
        }
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'No se pudo completar la operación.');
    return data;
}

function markerPopup(location) {
    return `<strong>${escapeHtml(location.nombre)}</strong><br><small>${escapeHtml(location.direccion || 'Ubicación registrada')}</small>`;
}

function renderLocationMarker(location) {
    const marker = L.marker([location.latitud, location.longitud]).addTo(ubicacionesLayer);
    marker.bindPopup(markerPopup(location));
}

function renderStaticPoint(point) {
    L.marker(point.coords).addTo(ubicacionesLayer)
        .bindPopup(`<strong>${escapeHtml(point.nombre)}</strong><br><small>${escapeHtml(point.descripcion)}</small>`);
}

function redrawLocations() {
    ubicacionesLayer.clearLayers();
    ubicaciones.forEach(renderLocationMarker);
}

function drawRoute(route, fit = false) {
    if (!route.geometria?.length) return;

    // ===============================================================================================================================================================
    // LINEA DE LA RUTA YA GENERDADA!
    // ---------------------------------------------------------------------------------------------------------------------------------------------------------------
    const line = L.polyline(route.geometria.map(point => [point[0], point[1]]), {
        color: '#00a2ff', weight: 5, opacity: .88
    }).bindPopup(`<strong>${escapeHtml(route.nombre)}</strong>`).addTo(rutasLayer);
    // ===============================================================================================================================================================

    if (fit) mapa.fitBounds(line.getBounds(), { padding: [24, 24] });
}

function redrawRoutes() {
    rutasLayer.clearLayers();
    rutas.forEach(route => drawRoute(route));
}

async function loadData() {
    const [locationsResponse, routesResponse] = await Promise.all([
        fetch(endpoints.ubicaciones), fetch(endpoints.rutas)
    ]);
    const locationsData = await locationsResponse.json();
    const routesData = await routesResponse.json();
    ubicaciones.splice(0, ubicaciones.length, ...locationsData.ubicaciones);
    rutas.splice(0, rutas.length, ...routesData.rutas);
    redrawLocations();
    (window.puntosGuadalupe || []).forEach(renderStaticPoint);
    redrawRoutes();
    renderLocationsTable();
    renderRoutesTable();
}

function showPanel(panelName) {
    ['location', 'route', 'view'].forEach(name => {
        const panel = document.getElementById(`${name}-panel`);
        if (panel) panel.hidden = name !== panelName;
    });
    if (panelName === 'location') {
        document.getElementById('location-panel-title').textContent = locationMode === 'manual' ? 'Añadir ubicación manualmente' : 'Ingresar ubicación';
        document.getElementById('location-mode-label').textContent = locationMode === 'manual' ? 'Selección sobre el mapa' : 'Nueva ubicación';
        document.getElementById('location-help').textContent = locationMode === 'manual'
            ? 'Haz clic en el mapa para rellenar coordenadas y dirección.'
            : 'Escribe una dirección y el mapa ubicará el punto exacto.';
    }
}

function resetLocationForm() {
    document.getElementById('location-form').reset();
    document.getElementById('location-id').value = '';
    document.getElementById('location-submit').textContent = 'Guardar ubicación';
}

function fillLocationForm(location) {
    document.getElementById('location-id').value = location.id;
    document.getElementById('location-name').value = location.nombre;
    document.getElementById('location-description').value = location.descripcion;
    document.getElementById('location-size').value = location.tamano_sede;
    document.getElementById('location-address').value = location.direccion;
    document.getElementById('location-latitude').value = location.latitud;
    document.getElementById('location-longitude').value = location.longitud;
    document.getElementById('location-submit').textContent = 'Actualizar ubicación';
    locationMode = 'location';
    showPanel('location');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function geocode(address) {
    const response = await fetch(`https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&q=${encodeURIComponent(address)}`);
    const results = await response.json();
    if (!results.length) throw new Error('No encontramos esa dirección. Prueba con ciudad y país.');
    return { lat: Number(results[0].lat), lon: Number(results[0].lon), address: results[0].display_name };
}

async function reverseGeocode(latitude, longitude) {
    const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${latitude}&lon=${longitude}`);
    const result = await response.json();
    return result.display_name || `${latitude}, ${longitude}`;
}

async function saveLocation(event) {
    event.preventDefault();
    const id = document.getElementById('location-id').value;
    const addressField = document.getElementById('location-address');
    const latitudeField = document.getElementById('location-latitude');
    const longitudeField = document.getElementById('location-longitude');
    const payload = {
        nombre: document.getElementById('location-name').value.trim(),
        descripcion: document.getElementById('location-description').value.trim(),
        tamano_sede: document.getElementById('location-size').value,
        direccion: addressField.value.trim(),
        latitud: latitudeField.value,
        longitud: longitudeField.value
    };

    try {
        if (!payload.nombre || !payload.direccion) throw new Error('Completa el nombre y la dirección.');
        if (locationMode === 'location' && (!payload.latitud || !payload.longitud)) {
            setStatus('Buscando la dirección...', 'map-status');
            const result = await geocode(payload.direccion);
            payload.latitud = result.lat;
            payload.longitud = result.lon;
            addressField.value = result.address;
            latitudeField.value = result.lat;
            longitudeField.value = result.lon;
        }
        if (!payload.latitud || !payload.longitud) throw new Error('Selecciona un punto en el mapa.');
        const url = id ? `${endpoints.ubicaciones}${id}/` : endpoints.ubicaciones;
        const data = await requestJson(url, { method: id ? 'PUT' : 'POST', body: JSON.stringify(payload) });
        if (id) {
            const index = ubicaciones.findIndex(item => item.id === Number(id));
            if (index >= 0) ubicaciones[index] = data;
        } else ubicaciones.unshift(data);
        redrawLocations();
        renderLocationsTable();
        resetLocationForm();
        showPanel('location');
        setStatus('Ubicación guardada correctamente.');
    } catch (error) {
        setStatus(error.message, 'map-status');
    }
}

async function selectMapPoint(event) {
    if (routeActive) {
        routePoints.push([event.latlng.lat, event.latlng.lng]);
        await updateRoutePreview();
        return;
    }
    if (locationMode !== 'manual') return;
    const latitude = event.latlng.lat.toFixed(6);
    const longitude = event.latlng.lng.toFixed(6);
    document.getElementById('location-latitude').value = latitude;
    document.getElementById('location-longitude').value = longitude;
    try {
        document.getElementById('location-address').value = await reverseGeocode(latitude, longitude);
        setStatus('Punto seleccionado. Completa los datos y guarda la ubicación.');
    } catch {
        document.getElementById('location-address').value = `${latitude}, ${longitude}`;
        setStatus('Punto seleccionado. No se pudo obtener una dirección legible.');
    }
}

async function updateRoutePreview() {
    if (routePoints.length < 2) {
        setStatus(`Puntos de ruta: ${routePoints.length}. Añade al menos dos.`, 'route-status');
        return;
    }
    try {
        setStatus('Calculando trayecto por calles...', 'route-status');
        const coordinates = routePoints.map(point => `${point[1]},${point[0]}`).join(';');
        const response = await fetch(`https://router.project-osrm.org/route/v1/driving/${coordinates}?overview=full&geometries=geojson&steps=false`);
        const data = await response.json();
        if (data.code !== 'Ok') throw new Error('No se encontró una ruta para esos puntos.');
        routeGeometry = data.routes[0].geometry.coordinates.map(point => [point[1], point[0]]);
        if (routeLine) mapa.removeLayer(routeLine);

        // ===============================================================================================================================================================
        // COLOR DE LA LINEA CUANDO ESTÁS GENERANDO LA RUTA:
        // ---------------------------------------------------------------------------------------------------------------------------------------------------------------
        routeLine = L.polyline(routeGeometry, { color: '#6ee7b7', weight: 5, opacity: .9 }).addTo(mapa);
        // ---------------------------------------------------------------------------------------------------------------------------------------------------------------
        // ===============================================================================================================================================================

        setStatus(`${routePoints.length} puntos añadidos. Trayectoria ajustada a las calles.`, 'route-status');
    } catch (error) {
        setStatus(error.message, 'route-status');
    }
}

function startRoute() {
    routeActive = true;
    routePoints = [];
    routeGeometry = [];
    if (routeLine) mapa.removeLayer(routeLine);
    routeLine = null;
    document.getElementById('route-start').hidden = true;
    document.getElementById('route-name').hidden = false;
    document.getElementById('route-finish').hidden = false;
    mapa.getContainer().classList.add('route-mode');
    setStatus('Ruta iniciada. Haz clic sobre el mapa para añadir puntos.', 'route-status');
}

async function finishRoute() {
    const name = document.getElementById('route-name').value.trim();
    if (!name || routePoints.length < 2 || !routeGeometry.length) {
        setStatus('Escribe un nombre y añade al menos dos puntos conectados.', 'route-status');
        return;
    }
    try {
        const data = await requestJson(endpoints.rutas, { method: 'POST', body: JSON.stringify({ nombre: name, puntos: routePoints, geometria: routeGeometry }) });
        rutas.unshift(data);
        redrawRoutes();
        renderRoutesTable();
        routeActive = false;
        document.getElementById('route-start').hidden = false;
        document.getElementById('route-name').hidden = true;
        document.getElementById('route-finish').hidden = true;
        document.getElementById('route-name').value = '';
        if (routeLine) mapa.removeLayer(routeLine);
        routeLine = null;
        mapa.getContainer().classList.remove('route-mode');
        setStatus('Ruta guardada correctamente.', 'route-status');
    } catch (error) {
        setStatus(error.message, 'route-status');
    }
}

function renderLocationsTable() {
    const container = document.getElementById('locations-table');
    if (!ubicaciones.length) {
        container.innerHTML = '<p class="ft-muted">No hay ubicaciones guardadas todavía.</p>';
        return;
    }
    container.innerHTML = `<table class="map-data-table"><thead><tr><th>Nombre</th><th>Dirección</th><th>Tamaño</th><th>Acciones</th></tr></thead><tbody>${ubicaciones.map(item => `<tr><td>${escapeHtml(item.nombre)}</td><td>${escapeHtml(item.direccion)}</td><td>${escapeHtml(item.tamano_sede)}</td><td class="table-actions"><button type="button" title="Editar ubicación" aria-label="Editar ubicación" data-edit-location="${item.id}">✎</button><button type="button" title="Eliminar ubicación" aria-label="Eliminar ubicación" data-delete-location="${item.id}">×</button></td></tr>`).join('')}</tbody></table>`;
}

function renderRoutesTable() {
    const container = document.getElementById('routes-table');
    if (!rutas.length) {
        container.innerHTML = '<p class="ft-muted">No hay rutas guardadas todavía.</p>';
        return;
    }
    container.innerHTML = `<table class="map-data-table"><thead><tr><th>Ruta</th><th>Puntos</th><th>Creada</th><th>Acciones</th></tr></thead><tbody>${rutas.map(item => `<tr><td>${escapeHtml(item.nombre)}</td><td>${item.puntos.length}</td><td>${new Date(item.fecha_creacion).toLocaleDateString()}</td><td class="table-actions"><button type="button" title="Ver ruta" aria-label="Ver ruta" data-view-route="${item.id}">◉</button><button type="button" title="Editar nombre" aria-label="Editar nombre" data-edit-route="${item.id}">✎</button><button type="button" title="Eliminar ruta" aria-label="Eliminar ruta" data-delete-route="${item.id}">×</button></td></tr>`).join('')}</tbody></table>`;
}

async function deleteLocation(id) {
    if (!window.confirm('¿Eliminar esta ubicación?')) return;
    await requestJson(`${endpoints.ubicaciones}${id}/`, { method: 'DELETE' });
    const index = ubicaciones.findIndex(item => item.id === Number(id));
    if (index >= 0) ubicaciones.splice(index, 1);
    redrawLocations();
    renderLocationsTable();
}

async function deleteRoute(id) {
    if (!window.confirm('¿Eliminar esta ruta?')) return;
    await requestJson(`${endpoints.rutas}${id}/`, { method: 'DELETE' });
    const index = rutas.findIndex(item => item.id === Number(id));
    if (index >= 0) rutas.splice(index, 1);
    redrawRoutes();
    renderRoutesTable();
}

async function editRoute(id) {
    const route = rutas.find(item => item.id === Number(id));
    const name = window.prompt('Nuevo nombre de la ruta:', route?.nombre || '');
    if (!name?.trim()) return;
    const updated = await requestJson(`${endpoints.rutas}${id}/`, { method: 'PUT', body: JSON.stringify({ nombre: name.trim() }) });
    const index = rutas.findIndex(item => item.id === Number(id));
    if (index >= 0) rutas[index] = updated;
    renderRoutesTable();
}

document.getElementById('map-functions-toggle').addEventListener('click', event => {
    const menu = document.getElementById('map-functions-menu');
    const expanded = event.currentTarget.getAttribute('aria-expanded') === 'true';
    event.currentTarget.setAttribute('aria-expanded', String(!expanded));
    menu.hidden = expanded;
});

document.querySelectorAll('[data-map-action]').forEach(button => button.addEventListener('click', () => {
    const action = button.dataset.mapAction;
    document.getElementById('map-functions-menu').hidden = true;
    document.getElementById('map-functions-toggle').setAttribute('aria-expanded', 'false');
    if (action === 'location' || action === 'manual') {
        locationMode = action;
        resetLocationForm();
        showPanel('location');
    } else if (action === 'route') showPanel('route');
    else if (action === 'view') showPanel('view');
}));

document.querySelectorAll('[data-close-panel]').forEach(button => button.addEventListener('click', () => {
    document.getElementById(`${button.dataset.closePanel}-panel`).hidden = true;
}));

document.getElementById('location-form').addEventListener('submit', saveLocation);
document.getElementById('route-start').addEventListener('click', startRoute);
document.getElementById('route-finish').addEventListener('click', finishRoute);

document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => {
    document.querySelectorAll('[data-view]').forEach(tab => tab.classList.toggle('is-active', tab === button));
    document.getElementById('locations-table').hidden = button.dataset.view !== 'locations';
    document.getElementById('routes-table').hidden = button.dataset.view !== 'routes';
}));

document.getElementById('locations-table').addEventListener('click', event => {
    const edit = event.target.closest('[data-edit-location]');
    const remove = event.target.closest('[data-delete-location]');
    if (edit) fillLocationForm(ubicaciones.find(item => item.id === Number(edit.dataset.editLocation)));
    if (remove) deleteLocation(remove.dataset.deleteLocation).catch(error => setStatus(error.message));
});

document.getElementById('routes-table').addEventListener('click', event => {
    const view = event.target.closest('[data-view-route]');
    const edit = event.target.closest('[data-edit-route]');
    const remove = event.target.closest('[data-delete-route]');
    if (view) {
        const route = rutas.find(item => item.id === Number(view.dataset.viewRoute));
        redrawRoutes();
        const line = L.polyline(route.geometria, { color: '#ffee00', weight: 6, opacity: 1 }).addTo(rutasLayer);
        mapa.fitBounds(line.getBounds(), { padding: [24, 24] });
    }
    if (edit) editRoute(edit.dataset.editRoute).catch(error => setStatus(error.message));
    if (remove) deleteRoute(remove.dataset.deleteRoute).catch(error => setStatus(error.message));
});

mapa.on('click', selectMapPoint);
loadData().catch(error => setStatus(`No se pudieron cargar los datos: ${error.message}`));
fetch('/static/source/data/geo/sede_guadalupe.geojson')
    .then(response => response.json())
    .then(data => L.geoJSON(data, { style: { color: '#35e03e', weight: 2, fillOpacity: .12 } }).addTo(mapa));
fetch('/static/source/data/json/sucursales.json').then(response => response.json()).then(items => items.forEach(item => {
    L.marker(item.coordenadas).addTo(ubicacionesLayer).bindPopup(`<strong>${escapeHtml(item.nombre)}</strong><br>${escapeHtml(item.ciudad)}`);
}));
