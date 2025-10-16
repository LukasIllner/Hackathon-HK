# 🌹 Rande v Hradci - AI Chatbot s Mapou

Integrace AI chatbota s interaktivní mapou pro hledání míst na rande v Královéhradeckém kraji.

## ✨ Funkce

- 💬 **AI Chatbot** - Konverzační rozhraní s Google Gemini 2.0
- 🗺️ **Interaktivní mapa** - Leaflet mapa s markery míst
- 🎯 **Real-time zobrazení** - Místa se zobrazují na mapě okamžitě po vyhledání
- 📍 **1018 míst** - Hrady, zámky, restaurace, pivovary, lázně, příroda a další
- 🔄 **Udržení kontextu** - Chatbot si pamatuje předchozí konverzaci

## 🚀 Spuštění aplikace

### 1. Příprava prostředí

```bash
cd "AI chatbot"

# Aktivace virtuálního prostředí (pokud ještě není)
source venv/bin/activate  # Linux/Mac
# nebo
venv\Scripts\activate  # Windows

# Instalace závislostí
pip install -r requirements_server.txt
```

### 2. Spuštění serveru

```bash
python app_server.py
```

Server poběží na: **http://localhost:5000**

### 3. Otevření aplikace

Otevři v prohlížeči: **http://localhost:5000**

## 📁 Struktura projektu

```
AI chatbot/
├── app_server.py           # Flask server (backend + frontend)
├── chat.py                 # Chat logika (CLI verze)
├── database.py             # MongoDB funkce a vyhledávání
├── tools.py                # Definice AI tools
├── prompts.py              # Systémové instrukce pro AI
├── config.py               # Konfigurace (API klíče)
└── requirements_server.txt # Závislosti

databaze/frontend/
├── app_production.html     # Frontend UI
├── app_chat.js            # JavaScript pro chat a mapu
└── app_production.js      # Starý JS (backup)
```

## 🎮 Jak používat

1. **Zahájení konverzace**
   - Napi v chatu: "Ahoj, chci naplánovat rande"
   - Chatbot se zeptá odkud jsi

2. **Vyhledávání míst**
   - "Najdi hrady v kraji"
   - "Chci romantickou restauraci"
   - "Kde jsou pivovary?"
   - "Ukaž lázně"

3. **Interakce s mapou**
   - Místa se automaticky zobrazí na mapě
   - Klikni na marker pro zobrazení detailů
   - První místo je zvýrazněno jako TOP doporučení

## 🔧 API Endpointy

### Frontend
- `GET /` - Hlavní aplikace

### Chat API
- `POST /api/chat/message` - Poslat zprávu do chatu
- `GET /api/chat/history` - Historie konverzace
- `POST /api/chat/reset` - Reset chatu

### Places API
- `GET /api/place/<dp_id>` - Detail místa
- `GET /api/health` - Health check

## 🎯 Příklady dotazů

**Romantická místa:**
- "Chci romantické místo na rande"
- "Najdi hrady a zámky"
- "Kde jsou rozhledny?"

**Gastronomie:**
- "Hledám dobrou restauraci"
- "Najdi pivovary v kraji"

**Wellness:**
- "Kde jsou lázně?"
- "Chci relaxaci pro dva"
- "Najdi koupaliště"

**Kultura:**
- "Ukaž muzea"
- "Kde jsou divadla?"
- "Najdi galerie"

## 🐛 Řešení problémů

### Server se nespustí
```bash
# Zkontroluj MongoDB připojení v .env
cd ../databaze
cat .env
```

### Chyba "Module not found"
```bash
# Reinstaluj závislosti
pip install -r requirements_server.txt --upgrade
```

### Mapa se nezobrazuje
- Zkontroluj konzoli prohlížeče (F12)
- Ujisti se, že běží server na portu 5000

### AI neodpovídá
- Zkontroluj API klíč v `config.py`
- Zkontroluj konzoli serveru pro error logy

## 📊 Databáze

- **MongoDB Atlas** - Cloud databáze
- **1018 míst** v Královéhradeckém kraji
- **22 kategorií** - hrady, lázně, muzea, atd.
- **GeoJSON formát** - souřadnice pro mapu

## 🔐 Konfigurace

Všechny konfigurace jsou v `config.py`:
- `GEMINI_API_KEY` - API klíč pro Google Gemini
- `MONGODB_URI` - MongoDB připojení (z .env)
- `GEMINI_MODEL` - Model AI (gemini-2.0-flash-exp)

## 🎨 Technologie

**Backend:**
- Flask 3.0
- Google Gemini 2.0 Flash
- MongoDB (PyMongo)
- Python 3.12

**Frontend:**
- HTML5 + CSS3
- Vanilla JavaScript
- Leaflet.js (mapa)
- Font Awesome (ikony)

## 📝 Poznámky

- Chatbot udržuje kontext konverzace
- Každý uživatel má vlastní session
- První místo je vždy zvýrazněno jako TOP doporučení
- Mapa automaticky zoomuje na nalezená místa

## 🚧 TODO (budoucí vylepšení)

- [ ] Persistence chat historie do databáze
- [ ] Filtrování míst na mapě
- [ ] Export doporučení jako PDF
- [ ] Push notifikace
- [ ] Hodnocení míst od uživatelů
- [ ] Multi-language podpora

---

**Vytvořeno pro Hackathon HK 2025** 🇨🇿
