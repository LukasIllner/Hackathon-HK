# Struktura projektu

Kód byl rozdělen do modulárních souborů pro lepší organizaci a údržbu.

## Moduly

```
AI chatbot/
├── config.py           # Konfigurace - API klíče, konstanty
├── database.py         # MongoDB připojení a databázové funkce
├── tools.py            # Definice nástrojů pro Gemini AI
├── prompts.py          # Systémové instrukce pro LLM
├── chat.py             # Chat logika a zpracování zpráv
├── main.py             # ⭐ Hlavní entry point - spustit tento soubor
│
├── rande_chatbot.py    # Původní monolitický soubor (zachován pro backup)
├── requirements.txt    # Python závislosti
├── README.md           # Dokumentace
└── venv/               # Virtuální prostředí
```

## Popis modulů

### config.py
- API klíče (Gemini)
- MongoDB konfigurace
- Konstanty a nastavení
- Načítání environment variables

### database.py
- `Database` třída - správce MongoDB připojení
- `hledej_mista_na_rande()` - hlavní vyhledávací funkce
- Formátování výsledků z databáze

### tools.py
- Definice funkcí pro Gemini (FunctionDeclaration)
- Vytvoření tool objektu
- Schéma parametrů pro AI

### prompts.py
- Systémová instrukce pro LLM
- Pravidla pro volání funkcí
- Konverzační guidelines

### chat.py
- `ChatBot` třída - správce konverzace
- Zpracování zpráv od uživatele
- Volání funkcí a zpracování odpovědí

### main.py
- **Entry point** - spouštěcí soubor
- Inicializace databáze
- Hlavní smyčka aplikace
- UI a interakce s uživatelem

## Jak spustit

```bash
# Spuštění nového modulárního chatbota
./venv/bin/python main.py

# Nebo původní monolitický chatbot (backup)
./venv/bin/python rande_chatbot.py
```

## Výhody modulární struktury

✅ **Přehlednost** - každý modul má jasnou zodpovědnost
✅ **Údržba** - snadnější úpravy a opravy
✅ **Testování** - jednotlivé moduly lze testovat samostatně
✅ **Rozšiřitelnost** - snadné přidávání nových funkcí
✅ **Reusabilita** - moduly lze použít v jiných projektech

## Import mezi moduly

```python
# config.py → Žádné závislosti
# database.py → importuje config
# tools.py → importuje genai
# prompts.py → Žádné závislosti (pouze string)
# chat.py → importuje config, tools, prompts, database
# main.py → importuje database, chat
```

## Zachováno pro kompatibilitu

- `rande_chatbot.py` - původní soubor zachován jako backup
- Všechny funkce fungují stejně jako předtím
- Žádná ztráta funkcionality
