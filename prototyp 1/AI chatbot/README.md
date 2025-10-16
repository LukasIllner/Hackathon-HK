# 🌹 Asistent pro Rande v Královéhradeckém kraji

AI chatbot pro doporučování romantických a zajímavých míst na rande v Královéhradeckém kraji.

## Funkce

- 💬 **Konverzace v češtině** - plně česky mluvící asistent
- 🗄️ **Reálná databáze** - více než 1000 míst v kraji
- 🎯 **Chytré doporučování** - chápe kontext a vaše preference
- 💝 **Zaměření na rande** - romantická místa, výlety pro dva, společné zážitky
- 📍 **Geolokace** - hledání míst podle polohy
- 🏰 **Různé kategorie** - hrady, muzea, pivovary, příroda, rozhledny a další

## Instalace

1. Vytvoření virtuálního prostředí:
```bash
python3 -m venv venv
```

2. Instalace závislostí:
```bash
./venv/bin/pip install -r requirements.txt
```

3. Spuštění chatbota:
```bash
./venv/bin/python rande_chatbot.py
```

## Příklady dotazů

- "Kam na romantické rande v Hradci Králové?"
- "Hledám zajímavé místo na výlet pro dva"
- "Jaké hrady jsou v kraji?"
- "Máte tip na kulturní večer?"
- "Kde najdu pěknou rozhlednu s výhledem?"
- "Jaké jsou nejlepší pivovary v regionu?"

## Databáze

Chatbot má přístup k více než 1000 místům včetně:

- 🏰 Hrady a zámky
- 🎨 Muzea a galerie
- 🍺 Pivovary
- 🦁 Zoo a zooparky
- 🎭 Divadla a filharmonie
- 🎬 Kina
- 🏊 Letní koupání
- ⚽ Sportovní centra
- 🌳 Přírodní zajímavosti
- 👁️ Rozhledny a výhlídky
- 🌸 Botanické zahrady
- 💆 Lázně a wellness
- 🎡 Zábavní centra

## Technologie

- **Gemini 2.0 Flash** - AI model s funkcemi pro volání nástrojů
- **MongoDB Atlas** - cloudová databáze s turistickými místy
- **Python** - backend implementace

## Jak to funguje

1. Uživatel se ptá v češtině na místa na rande
2. Gemini AI analyzuje dotaz a rozhodne se zavolat databázový nástroj
3. Databáze vrátí relevantní místa
4. AI zformuluje přátelskou odpověď v češtině s doporučeními

## Požadavky

- Python 3.8+
- MongoDB Atlas účet (konfigurace v `../databaze/.env`)
- Gemini API klíč (již nakonfigurován)
