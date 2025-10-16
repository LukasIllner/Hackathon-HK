// Konfigurace
const API_BASE_URL = 'http://localhost:5000/api';
const SESSION_ID = 'user_' + Math.random().toString(36).substr(2, 9);

// Inicializace mapy (Leaflet)
const map = L.map('map').setView([50.2099, 15.8325], 11);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// Globální proměnné
let highlightedMarker = null;
let allMarkers = [];

// DOM elementy
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const chatSendBtn = document.getElementById('chat-send-btn');
const chatPlaceholder = document.getElementById('chat-placeholder');

// Ikony pro různé typy míst
const typeIcons = {
    'kultura': '🏛️',
    'příroda': '🌳',
    'gastronomie': '🍽️',
    'zábava': '🎬',
    'wellness': '💆',
    'default': '📍'
};

// Funkce pro získání typu místa
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

// Přidání zprávy do chatu
function addMessage(text, isUser = false) {
    // Skrytí placeholder při první zprávě
    if (chatPlaceholder) {
        chatPlaceholder.style.display = 'none';
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${isUser ? 'user' : 'assistant'}`;
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = text;
    
    messageDiv.appendChild(bubble);
    chatMessages.appendChild(messageDiv);
    
    // Scroll dolů
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageDiv;
}

// Přidání loading animace
function addLoadingMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-assistant';
    messageDiv.id = 'loading-message';
    
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message-loading';
    loadingDiv.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
    
    messageDiv.appendChild(loadingDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageDiv;
}

// Odstranění loading animace
function removeLoadingMessage() {
    const loading = document.getElementById('loading-message');
    if (loading) {
        loading.remove();
    }
}

// Zobrazení míst na mapě
function showLocationsOnMap(locations) {
    // Vyčistit staré markery
    allMarkers.forEach(marker => map.removeLayer(marker));
    allMarkers = [];
    
    if (!locations || locations.length === 0) {
        console.log('Žádná místa k zobrazení');
        return;
    }
    
    console.log(`Zobrazuji ${locations.length} míst na mapě`);
    
    const bounds = [];
    
    locations.forEach((location, index) => {
        // Získání souřadnic
        const coords = location.souradnice || [];
        if (coords.length < 2) {
            console.warn('Místo bez souřadnic:', location.nazev);
            return;
        }
        
        const lat = coords[1];
        const lon = coords[0];
        const latLng = [lat, lon];
        bounds.push(latLng);
        
        // Typ místa
        const placeType = getPlaceType(location.kategorie);
        const icon = typeIcons[placeType] || typeIcons.default;
        
        // Vytvoření markeru
        const marker = L.marker(latLng, {
            icon: L.divIcon({
                className: 'custom-marker' + (index === 0 ? ' highlighted' : ''),
                html: icon,
                iconSize: index === 0 ? [60, 60] : [40, 40],
                iconAnchor: index === 0 ? [30, 30] : [20, 20]
            }),
            zIndexOffset: index === 0 ? 1000 : 0
        }).addTo(map);
        
        // Popup s informacemi
        marker.bindPopup(`
            <div style="text-align: center; min-width: 150px;">
                ${index === 0 ? '<b style="color: #ff1744; font-size: 14px;">💝 TOP DOPORUČENÍ</b><br>' : ''}
                <b style="font-size: 16px;">${location.nazev || 'Bez názvu'}</b><br>
                <span style="font-size: 12px; color: #666;">${location.kategorie || ''}</span><br>
                <span style="font-size: 11px; color: #999;">${location.obec || ''}</span>
            </div>
        `);
        
        // Kliknutí - zobrazení detailů
        marker.on('click', () => {
            loadAndShowPlaceDetails(location.id);
        });
        
        allMarkers.push(marker);
    });
    
    // Přiblížení na první místo nebo všechny místa
    if (bounds.length === 1) {
        map.flyTo(bounds[0], 14, { duration: 1.5 });
    } else if (bounds.length > 1) {
        map.flyToBounds(bounds, { padding: [50, 50], duration: 1.5 });
    }
    
    // Zobrazit detail prvního místa
    if (locations.length > 0) {
        loadAndShowPlaceDetails(locations[0].id);
        
        // Otevřít popup prvního místa po chvíli
        setTimeout(() => {
            if (allMarkers[0]) {
                allMarkers[0].openPopup();
            }
        }, 1000);
    }
}

// Načtení a zobrazení detailů místa
async function loadAndShowPlaceDetails(dpId) {
    if (!dpId) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/place/${dpId}`);
        if (!response.ok) {
            throw new Error('Místo nenalezeno');
        }
        
        const place = await response.json();
        showPlaceDetails(place);
        
    } catch (error) {
        console.error('Chyba načítání detailu místa:', error);
        showPlaceError(dpId, error.message);
    }
}

// Zobrazení detailů místa v sidebaru
function showPlaceDetails(place) {
    const placeInfo = document.getElementById('place-info');
    
    const name = place.nazev || place.dp_id || 'Bez názvu';
    const description = place.popis || place.zamereni_muzea || 'Žádný popis není k dispozici.';
    const website = place.www || null;
    const openingHours = place.oteviraci_doba || place.pozn_oteviraci_doba || 'Informace nejsou k dispozici';
    
    const coords = place.geometry?.coordinates || [0, 0];
    const lat = coords[1];
    const lon = coords[0];
    
    const category = place.typ_muzea || place.typ || getPlaceType(place.source_file);
    const navigateUrl = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}`;
    
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
}

// Zobrazení chyby při načítání místa
function showPlaceError(dpId, errorMsg) {
    const placeInfo = document.getElementById('place-info');
    placeInfo.innerHTML = `
        <div class="place-empty">
            <i class="fas fa-exclamation-triangle" style="color: #ff1744;"></i>
            <p style="color: #ff1744;">Chyba načítání místa</p>
            <p style="font-size: 12px;">${errorMsg}</p>
            <p style="font-size: 12px; margin-top: 10px;">ID: ${dpId}</p>
        </div>
    `;
}

// Odeslání zprávy do chatu
async function sendMessage(message) {
    if (!message || !message.trim()) return;
    
    // Přidat user zprávu
    addMessage(message, true);
    
    // Disable input
    chatInput.disabled = true;
    chatSendBtn.disabled = true;
    chatInput.value = '';
    
    // Přidat loading
    addLoadingMessage();
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: SESSION_ID,
                message: message
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Odstranit loading
        removeLoadingMessage();
        
        // Přidat odpověď AI
        if (data.response) {
            addMessage(data.response, false);
        }
        
        // Zobrazit místa na mapě pokud existují
        if (data.locations && data.locations.length > 0) {
            console.log('AI našla místa:', data.locations);
            showLocationsOnMap(data.locations);
        }
        
        // Log tool calls
        if (data.tool_calls && data.tool_calls.length > 0) {
            console.log('Tool calls:', data.tool_calls);
        }
        
    } catch (error) {
        console.error('Chyba při komunikaci s API:', error);
        removeLoadingMessage();
        addMessage('Omlouvám se, došlo k chybě při zpracování vaší zprávy. Zkuste to prosím znovu.', false);
    } finally {
        // Enable input
        chatInput.disabled = false;
        chatSendBtn.disabled = false;
        chatInput.focus();
    }
}

// Event listenery
chatSendBtn.addEventListener('click', () => {
    const message = chatInput.value.trim();
    if (message) {
        sendMessage(message);
    }
});

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const message = chatInput.value.trim();
        if (message) {
            sendMessage(message);
        }
    }
});

// Health check při startu
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            const data = await response.json();
            console.log('✓ API server online');
            console.log(`✓ Databáze: ${data.places_count} míst`);
            document.querySelector('.status-bar').classList.add('active');
            document.querySelector('.status-bar span').textContent = `Připojeno - ${data.places_count} míst`;
        }
    } catch (error) {
        console.error('⚠ API server není dostupný');
        document.querySelector('.status-bar').style.background = '#ff1744';
        document.querySelector('.status-bar span').textContent = 'Server offline - spusť app_server.py';
    }
}

// Inicializace
console.log('🚀 Aplikace spuštěna!');
console.log('📍 API URL:', API_BASE_URL);
console.log('🔑 Session ID:', SESSION_ID);

checkAPIHealth();
chatInput.focus();
