# 🗺️ Frontend - Mapová aplikace pro Hackathon HK

Interaktivní webová mapa pro zobrazení doporučení míst od AI chatbota.

---

## 🚀 Rychlý start (Pro prezentaci)

### 1️⃣ Spusť API server (Terminal 1)

```bash
# Install dependencies
pip install -r requirements_api.txt

# Spusť API server
python api_server.py
```

Měl bys vidět:
```
✓ Připojeno k MongoDB: hackathon_hk.places
🚀 Spouštím API server...
📍 URL: http://localhost:5000
```

### 2️⃣ Spusť frontend (Terminal 2)

```bash
# Spusť HTTP server
python3 -m http.server 8000
```

### 3️⃣ Otevři aplikaci

Otevři v prohlížeči: **http://localhost:8000/app_production.html**

---

## 📁 Produkční soubory

```
frontend/
├── app_production.html         # Hlavní HTML aplikace
├── app_production.js           # JavaScript logika
├── api_server.py               # Flask API server
├── requirements_api.txt        # Python dependencies
├── .env                        # MongoDB credentials
├── chatbot_command.json        # Komunikační soubor
└── README_FRONTEND.md          # Tento soubor
```

---

## 🔄 Jak to funguje

### Komunikační flow:

```
1. Chatbot → Zapíše do chatbot_command.json
   {
     "action": "show",
     "dp_id": "MG1"
   }

2. Frontend (každé 2s) → Detekuje změnu

3. Frontend → Zavolá API
   GET http://localhost:5000/api/place/MG1

4. API Server → Dotáže se MongoDB

5. MongoDB → Vrátí kompletní data místa

6. Frontend → Zobrazí na mapě + info panel
```

---

## 🔌 API Endpointy

### GET /api/place/{dp_id}
Získá místo podle dp_id

**Příklad:**
```bash
curl http://localhost:5000/api/place/MG1
```

**Response:**
```json
{
  "dp_id": "MG1",
  "ds_id": "4080",
  "nazev": "Archeologické muzeum v přírodě Villa Nova Uhřínov",
  "geometry": {
    "type": "Point",
    "coordinates": [16.3503822, 50.2509742]
  },
  "www": "https://www.villanova.cz/",
  ...
}
```

### GET /api/health
Health check - ověř že API běží

### GET /api/places?limit=100
Získá všechna místa (pro debugging)

### GET /api/search?q=hrad
Vyhledá místa podle názvu

---

## 🎯 Pro chatbot (Kolega)

### Co musíš udělat:

1. **Načti data z MongoDB**
   ```python
   from pymongo import MongoClient
   from dotenv import load_dotenv
   import os

   load_dotenv()
   client = MongoClient(os.getenv('MONGODB_URI'))
   db = client['hackathon_hk']
   collection = db['places']
   ```

2. **Vyber místo podle požadavků uživatele**
   ```python
   # Např. romantické místo
   place = collection.find_one({'typ': 'romantické'})
   dp_id = place['dp_id']
   ```

3. **Zapiš do chatbot_command.json**
   ```python
   import json

   command = {
       "action": "show",
       "dp_id": dp_id
   }

   with open('chatbot_command.json', 'w') as f:
       json.dump(command, f)
   ```

4. **Frontend automaticky zobrazí místo na mapě!**

---

## 📊 Struktura MongoDB dat

Každé místo obsahuje:

```json
{
  "dp_id": "HRAD1",              // Unikátní ID (POUŽÍVEJ PRO KOMUNIKACI)
  "ds_id": "100001",            // Sekundární ID
  "nazev": "Hrad Náchod",       // Název místa
  "popis": "Popis...",           // Popis
  "geometry": {                  // Souřadnice (GeoJSON)
    "type": "Point",
    "coordinates": [lon, lat]
  },
  "source_file": "Hrady.geojson", // Zdroj (pro typ místa)
  "www": "http://...",           // Web (optional)
  "telefon": "+420...",          // Telefon (optional)
  "email": "...",                // Email (optional)
  "oteviraci_doba": "...",       // Otevírací doba
  "typ": "...",                  // Typ místa
  ...                            // Další metadata
}
```

---

## 🐛 Troubleshooting

### "API server offline"
- Ujisti se že běží: `python api_server.py`
- Zkontroluj že běží na portu 5000

### "Místo nenalezeno"
- Zkontroluj že `dp_id` v `chatbot_command.json` existuje v databázi
- Použij: `curl http://localhost:5000/api/places` pro seznam všech ID

### "Connection refused"
- API server neběží
- Zkontroluj `.env` soubor s MongoDB credentials

### "CORS error"
- Flask-CORS je nainstalovaný? `pip install flask-cors`

---

## 🎨 Frontend funkce

### ✅ Implementováno:
- Interaktivní mapa (Leaflet)
- Zvýraznění místa na mapě
- Info panel s detaily
- Tlačítko "Navigovat" (Google Maps)
- Tlačítko "Web" (pokud existuje)
- Auto-refresh každé 2s (polling chatbot_command.json)
- Error handling
- Loading animace
- Smooth animace přiblížení

### Info panel zobrazuje:
- Název místa
- Kategorie/typ
- Popis
- Souřadnice
- Otevírací doba
- Telefon (pokud existuje)
- Email (pokud existuje)
- ID místa

---

## 💻 Development

### Pro vývoj (s lokální testovací DB):

Použij původní soubory:
- `app.html` + `app.js` + `places_database.json`

### Pro produkci (s MongoDB):

Použij:
- `app_production.html` + `app_production.js` + `api_server.py`

---

## 📱 Pro prezentaci na Hackathonu

### Setup:

1. **Na notebooku:**
   ```bash
   # Terminal 1
   python api_server.py

   # Terminal 2
   python3 -m http.server 8000
   ```

2. **Otevři v prohlížeči:**
   ```
   http://localhost:8000/app_production.html
   ```

3. **HDMI → Prezentační obrazovka**

4. **Chatbot zapisuje do `chatbot_command.json`**

5. **Profit! 🎉**

---

## 🔐 MongoDB Credentials

Jsou v `.env` souboru:
```env
MONGODB_URI=mongodb+srv://lukaskillner:...@cluster0...
DATABASE_NAME=hackathon_hk
COLLECTION_NAME=places
```

**DŮLEŽITÉ:** `.env` je v `.gitignore`, nepushuj ho na GitHub!

---

## 📞 Kontakt

Otázky? Píš kolegovi co dělá chatbota! 😄

---

**Created for Hackathon HK 2025** 🚀
