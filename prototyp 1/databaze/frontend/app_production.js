// Konfigurace API
const API_BASE_URL = 'http://localhost:5000/api';

// Inicializace mapy
const map = L.map('map').setView([50.2099, 15.8325], 11);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// Globální proměnné
let highlightedMarker = null;
let lastCommand = null;

// Ikony pro různé typy míst
const typeIcons = {
    'kultura': '🏛️',
    'příroda': '🌳',
    'gastronomie': '🍽️',
    'zábava': '🎬',
    'wellness': '💆',
    'default': '📍'
};

// Funkce pro získání typu místa ze source_file
function getPlaceType(sourceFile) {
    if (!sourceFile) return 'default';

    const lower = sourceFile.toLowerCase();

    if (lower.includes('hrad') || lower.includes('zamek') || lower.includes('pamat') ||
        lower.includes('divad') || lower.includes('muzea') || lower.includes('galerie') ||
        lower.includes('cirkevni')) {
        return 'kultura';
    }
    if (lower.includes('prirodni') || lower.includes('park') || lower.includes('rozhled')) {
        return 'příroda';
    }
    if (lower.includes('pivovar') || lower.includes('restaurace') || lower.includes('kavarna')) {
        return 'gastronomie';
    }
    if (lower.includes('kino') || lower.includes('zabav') || lower.includes('zoo')) {
        return 'zábava';
    }
    if (lower.includes('lazne') || lower.includes('koupani') || lower.includes('wellness')) {
        return 'wellness';
    }

    return 'default';
}

// Načtení místa z API podle dp_id
async function loadPlaceFromAPI(dpId) {
    try {
        const response = await fetch(`${API_BASE_URL}/place/${dpId}`);

        if (!response.ok) {
            if (response.status === 404) {
                throw new Error(`Místo s ID "${dpId}" nebylo nalezeno v databázi`);
            }
            throw new Error(`API error: ${response.status}`);
        }

        const place = await response.json();
        return place;

    } catch (error) {
        console.error('Chyba načítání z API:', error);
        throw error;
    }
}

// Zvýraznění místa na mapě
function highlightPlace(place) {
    console.log('Zvýrazňuji místo:', place.nazev || place.dp_id);

    // Odstraň předchozí zvýraznění
    if (highlightedMarker) {
        map.removeLayer(highlightedMarker);
    }

    // Získej souřadnice z geometry
    const coordinates = place.geometry?.coordinates || [15.8325, 50.2099];
    const latLng = [coordinates[1], coordinates[0]]; // [lat, lon]

    // Detekuj typ místa
    const placeType = getPlaceType(place.source_file);
    const icon = typeIcons[placeType] || typeIcons.default;

    // Vytvoř zvýrazněný marker
    highlightedMarker = L.marker(latLng, {
        icon: L.divIcon({
            className: 'custom-marker highlighted',
            html: icon,
            iconSize: [60, 60],
            iconAnchor: [30, 30]
        }),
        zIndexOffset: 1000
    }).addTo(map);

    // Animace přiblížení
    map.flyTo(latLng, 14, {
        duration: 1.5
    });

    // Zobraz detaily
    showPlaceDetails(place);

    // Otevři popup po chvíli
    setTimeout(() => {
        highlightedMarker.bindPopup(`
            <div style="text-align: center;">
                <b style="color: #ff1744; font-size: 16px;">💝 DOPORUČENÍ CHATBOTA</b><br>
                <b>${place.nazev || place.dp_id}</b>
            </div>
        `).openPopup();
    }, 1000);
}

// Zobrazení detailů místa v sidebaru
function showPlaceDetails(place) {
    const placeInfo = document.getElementById('place-info');

    // Zpracuj data z MongoDB
    const name = place.nazev || place.dp_id || 'Bez názvu';
    const description = place.popis || place.zamereni_muzea || 'Žádný popis není k dispozici.';
    const website = place.www || null;
    const openingHours = place.oteviraci_doba || place.pozn_oteviraci_doba || 'Informace nejsou k dispozici';

    // Souřadnice
    const coords = place.geometry?.coordinates || [0, 0];
    const lat = coords[1];
    const lon = coords[0];

    // Kategorie/typ
    const category = place.typ_muzea || place.typ || getPlaceType(place.source_file);

    // Google Maps URL pro navigaci
    const navigateUrl = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}`;

    const actionsHtml = `
        <div class="place-actions">
            <a href="${navigateUrl}" target="_blank" class="place-btn btn-navigate">
                <i class="fas fa-directions"></i> Navigovat
            </a>
            ${website ? `
                <a href="${website}" target="_blank" class="place-btn btn-website">
                    <i class="fas fa-external-link-alt"></i> Web
                </a>
            ` : ''}
        </div>
    `;

    placeInfo.innerHTML = `
        <div class="place-title">${name}</div>
        <div class="place-category">${category}</div>

        <div class="place-description">${description}</div>

        <div class="place-details">
            <div class="detail-row">
                <i class="fas fa-map-marker-alt"></i>
                <span>${lat.toFixed(4)}, ${lon.toFixed(4)}</span>
            </div>

            <div class="detail-row">
                <i class="fas fa-clock"></i>
                <span>${openingHours}</span>
            </div>

            ${place.telefon ? `
                <div class="detail-row">
                    <i class="fas fa-phone"></i>
                    <span>${place.telefon}</span>
                </div>
            ` : ''}

            ${place.email ? `
                <div class="detail-row">
                    <i class="fas fa-envelope"></i>
                    <span>${place.email}</span>
                </div>
            ` : ''}

            <div class="detail-row">
                <i class="fas fa-database"></i>
                <span>ID: ${place.dp_id}</span>
            </div>
        </div>

        ${actionsHtml}
    `;
}

// Načítání příkazů od chatbota
async function checkChatbotCommand() {
    try {
        const response = await fetch('chatbot_command.json?t=' + Date.now());
        const command = await response.json();

        const commandHash = JSON.stringify(command);

        if (commandHash !== lastCommand) {
            lastCommand = commandHash;

            if (command.action === 'show' && command.dp_id) {
                console.log('Nový příkaz od chatbota:', command);

                // Zobraz loading
                document.querySelector('.loading').classList.add('active');

                try {
                    // Načti místo z API
                    const place = await loadPlaceFromAPI(command.dp_id);

                    // Zobraz na mapě
                    highlightPlace(place);

                } catch (error) {
                    console.error('Chyba zobrazení místa:', error);

                    // Zobraz error v sidebaru
                    const placeInfo = document.getElementById('place-info');
                    placeInfo.innerHTML = `
                        <div class="place-empty">
                            <i class="fas fa-exclamation-triangle" style="color: #ff1744;"></i>
                            <p style="color: #ff1744;">Chyba načítání místa</p>
                            <p style="font-size: 12px;">${error.message}</p>
                            <p style="font-size: 12px; margin-top: 10px;">ID: ${command.dp_id}</p>
                        </div>
                    `;
                } finally {
                    document.querySelector('.loading').classList.remove('active');
                }
            }
        }
    } catch (error) {
        // Soubor ještě neexistuje nebo je chyba - to je OK
        console.log('Čekám na příkaz od chatbota...');
    }
}

// Health check API
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✓ API server je online');
            document.querySelector('.status-bar').classList.add('active');
        }
    } catch (error) {
        console.warn('⚠ API server není dostupný. Ujisti se že běží: python api_server.py');
        document.querySelector('.status-bar').style.background = '#ff9800';
        document.querySelector('.status-bar span').textContent = 'API server offline';
    }
}

// Inicializace
console.log('Aplikace spuštěna! Čekám na příkazy z chatbota...');
console.log('API: ' + API_BASE_URL);

// Kontrola API při startu
checkAPIHealth();

// Polling každé 2 sekundy
setInterval(checkChatbotCommand, 2000);
