# 🌹 Rande v Hradci - AI Chatbot Aplikace

Interaktivní webová aplikace pro hledání míst na rande v Královéhradeckém kraji s AI chatbotem a mapou.

## ✨ Funkce

- 💬 **AI Chatbot** - Konverzace s Google Gemini 2.0 Flash
- 🗺️ **Leaflet Mapa** - Interaktivní zobrazení míst
- 📍 **1018 míst** - Hrady, zámky, restaurace, pivovary, lázně, příroda
- 🎯 **Real-time** - Místa se zobrazují na mapě okamžitě
- 🔄 **Kontext** - Chatbot si pamatuje předchozí konverzaci

## 🚀 Rychlé spuštění

### 1. Instalace závislostí

```bash
cd "AI chatbot"
source venv/bin/activate  # nebo venv\Scripts\activate na Windows
pip install -r requirements_server.txt
```

### 2. Spuštění serveru

```bash
python app_server.py
```

### 3. Otevření aplikace

Otevři prohlížeč: **http://localhost:5000**

## 📁 Struktura projektu

```
prototyp 1/
├── AI chatbot/              # Backend + AI chatbot
│   ├── app_server.py        # 🔥 Hlavní Flask server
│   ├── database.py          # MongoDB funkce
│   ├── tools.py             # AI tools definice
│   ├── prompts.py           # Systémové instrukce
│   ├── config.py            # Konfigurace
│   └── docs/                # Dokumentace
│
├── databaze/
│   ├── .env                 # MongoDB credentials
│   ├── frontend/
│   │   ├── app_production.html  # 🎨 Frontend UI
│   │   └── app_chat.js          # 🔥 JavaScript logika
│   └── README.md            # Databáze dokumentace
│
└── data HK - rande geojson/ # GeoJSON data (1018 míst)
```

## 🎮 Jak používat

1. **Zahájení konverzace**
   ```
   Ahoj, chci naplánovat rande
   ```

2. **Vyhledávání míst**
   ```
   najdi hrady
   najdi pivovary v hradci
   kde jsou lázně?
   chci romantickou restauraci
   ```

3. **Interakce**
   - Místa se automaticky zobrazí na mapě
   - První místo je zvýrazněno jako TOP
   - Klikni na marker pro detail

## 🔧 API Endpointy

**Frontend:**
- `GET /` - Hlavní aplikace

**Chat:**
- `POST /api/chat/message` - Poslat zprávu
- `GET /api/chat/history` - Historie
- `POST /api/chat/reset` - Reset

**Places:**
- `GET /api/place/<dp_id>` - Detail místa
- `GET /api/health` - Health check

## 📊 Databáze

- **MongoDB Atlas** - Cloud databáze
- **1018 míst** v 22 kategoriích
- **GeoJSON** formát pro mapu

### Kategorie míst:
Hrady a zámky | Muzea | Pivovary | Restaurace | Zoo | Divadla | Kina | Přírodní zajímavosti | Rozhledny | Botanické zahrady | Lázně | Koupaliště | Golf | Sporty | Hudební kluby | Zábavní centra | Církevní památky | Národní památky | Technické památky | Rybaření | Solné jeskyně | Festivaly

## 🎨 Technologie

**Backend:**
- Flask 3.0
- Google Gemini 2.0 Flash (AI)
- MongoDB + PyMongo
- Python 3.12

**Frontend:**
- HTML5 + CSS3
- Vanilla JavaScript
- Leaflet.js (mapa)
- Font Awesome (ikony)

## 🐛 Řešení problémů

### Server se nespustí
```bash
# Zkontroluj MongoDB credentials
cd databaze
cat .env
```

### AI neodpovídá
- Zkontroluj API klíč v `AI chatbot/config.py`
- Sleduj server logy v terminálu

### Mapa se nezobrazuje
- Otevři konzoli prohlížeče (F12)
- Zkontroluj že server běží na portu 5000

## 📝 Další dokumentace

- `AI chatbot/README_INTEGRATION.md` - Detailní návod k integraci
- `databaze/README.md` - MongoDB setup a usage
- `databaze/frontend/README_FRONTEND.md` - Frontend dokumentace

## 🔐 Konfigurace

Všechny konfigurace jsou v `AI chatbot/config.py`:
- `GEMINI_API_KEY` - API klíč pro Google Gemini
- `MONGODB_URI` - MongoDB připojení (z .env)
- `GEMINI_MODEL` - AI model

## 🌐 Branch

Aktuální branch: `feature/chatbot-frontend-integration`

---

**Vytvořeno pro Hackathon HK 2025** 🇨🇿
