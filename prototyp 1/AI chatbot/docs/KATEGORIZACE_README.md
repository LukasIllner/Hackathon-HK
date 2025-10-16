# 🏷️ Automatická kategorizace míst pomocí AI

## Co to dělá?

Místo spoléhání se na názvy souborů, každé místo v databázi dostane **vlastní seznam kategorií** přiřazených pomocí Gemini AI.

## Výhody nového systému

### ❌ Staré (podle názvu souboru)
```
Hrad Kost → source_file: "Hrady.geojson"
Vyhledávání: {"source_file": {"$regex": "Hrady"}}
Kategorie: pouze "Hrady"
```

### ✅ Nové (AI kategorizace)
```
Hrad Kost → kategorie: ["hrad", "historické", "památka", "turistika", "kulturní", "romantické"]
Vyhledávání: {"kategorie": {"$in": ["hrad"]}}
Kategorie: 6 relevantních tagů!
```

## 📊 Výsledky testu

Test na 5 místech ukázal:

| Místo | Původní kategorie | AI kategorie |
|-------|------------------|--------------|
| Hrad Kost | Hrady | hrad, historické, památka, turistika, kulturní, romantické |
| Lázně | Lázně | lázně, wellness, relaxace, klidné, pro páry, rodinné |
| Muzeum Villa Nova | Muzea a galerie | museum, kulturní, historické, památka, venkovní, rodinné |
| Bakovský pivovar | Pivovary | pivovar, restaurace, turistika, venkovní, klidné |

## 🚀 Jak spustit

### 1. Test kategorizace (5 míst)
```bash
cd "AI chatbot"
./venv/bin/python test_kategorizace.py
```

Výstup: Každé místo bude mít pole `test_kategorie` v MongoDB

### 2. Plná kategorizace (všech 1018 míst)
```bash
./venv/bin/python kategorizace_mist.py
```

**Upozornění:** 
- Trvá ~30-60 minut (1018 míst × ~2 sec/místo)
- Používá Gemini API (cca 1000 calls)
- Přidá pole `kategorie` do VŠECH dokumentů

### Možnosti při spuštění:
1. Kategorizovat všechna místa (přepíše existující)
2. Pouze místa bez kategorií

## 📋 Dostupné kategorie

42 kategorií v 8 skupinách:

### 🏰 Typ místa
hrad, zámek, museum, galerie, divadlo, kino, pivovar, restaurace, kavárna

### 💆 Wellness & Relaxace
wellness, lázně, relaxace, spa, solná jeskyně

### 🏊 Vodní aktivity
koupání, aquapark, koupaliště, bazén, plavání

### 🌳 Příroda
příroda, les, park, zahrada, botanical, rozhledna, výhled, vyhlídka, hora, kopec

### 🏃 Aktivity
sport, aktivní, turistika, hiking, golf, rybaření, cyklistika

### 🎭 Kultura & Historie
kulturní, historické, památka, církevní, technické, národní

### 🎉 Zábava
zábava, zábavní, zoo, zvířata, festival, hudba, koncert, živá hudba

### 🎯 Atmosféra
romantické, klidné, tiché, pokojné, aktivní, rušné, rodinné, pro páry, venkovní, vnitřní, letní, zimní

## 🔧 Jak to funguje

### Proces:
1. Script načte místo z MongoDB
2. Vytvoří prompt s informacemi:
   - Název místa
   - Typ ze souboru
   - Obec/okres
   - Typ muzea (pokud je)
   - Popis (pokud je)
3. Zavolá Gemini API
4. LLM vrátí JSON array kategorií
5. Validuje kategorie (pouze ze seznamu)
6. Uloží do pole `kategorie` v MongoDB

### Příklad promptu:
```
Kategorizuj toto místo:

Název: Hrad Kost
Typ: Hrady
Obec: Libošovice

Vyber 3-6 kategorií ze seznamu:
romantické, hrad, zámek, museum...

Vrať POUZE JSON array:
```

### Odpověď LLM:
```json
["hrad", "historické", "památka", "turistika", "kulturní", "romantické"]
```

## 📈 Statistiky po kategorizaci

Script automaticky ukáže:
- Počet aktualizovaných míst
- Top 10 nejpoužívanějších kategorií
- Chyby (pokud byly)

## 🔄 Aktualizace vyhledávání

Po přidání kategorií je třeba upravit databázové dotazy:

### Staré (source_file):
```python
query = {"source_file": {"$regex": "Lázně", "$options": "i"}}
```

### Nové (kategorie):
```python
query = {"kategorie": {"$in": ["lázně"]}}
# Nebo více kategorií:
query = {"kategorie": {"$in": ["lázně", "wellness", "relaxace"]}}
```

## 🎯 Výhody

✅ **Přesnější** - AI rozumí kontextu, ne jen názvu
✅ **Vícevrstvé** - Každé místo má 3-6 kategorií
✅ **Flexibilní** - Snadné vyhledávání podle různých aspektů
✅ **Semantické** - "wellness" najde lázně i solné jeskyně
✅ **Rozšiřitelné** - Snadné přidání nových kategorií

## ⚠️ Poznámky

- **Rate limiting**: Script čeká 0.5s mezi dotazy
- **Validace**: Pouze kategorie ze seznamu se uloží
- **Fallback**: Při chybě se použije základní kategorie
- **Progress bar**: tqdm ukazuje průběh
- **MongoDB**: Kategorie se přidávají jako array

## 📝 Soubory

- `kategorizace_mist.py` - Hlavní script (celá databáze)
- `test_kategorizace.py` - Test script (5 míst)
- `KATEGORIZACE_README.md` - Tato dokumentace

## 🚦 Status

✅ Test kategorizace funguje
⏸️ Plná kategorizace čeká na spuštění
🔜 Aktualizace vyhledávacích funkcí
