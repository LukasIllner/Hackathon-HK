# Jak funguje kategorizace a vyhledávání

## 🗂️ Struktura dat v MongoDB

### 1. Import dat
Každý GeoJSON soubor z adresáře `data HK - rande geojson/` se importuje do MongoDB:

```
data HK - rande geojson/
├── Lázně.geojson              → source_file: "data_hk_rande/Lázně.geojson"
├── Letní koupání.geojson      → source_file: "data_hk_rande/Letní koupání.geojson"
├── Hrady.geojson              → source_file: "data_hk_rande/Hrady.geojson"
└── ... (22 souborů celkem)
```

### 2. Každý dokument v MongoDB obsahuje

```json
{
  "nazev": "Janské Lázně",                    // Název místa
  "source_file": "data_hk_rande/Lázně.geojson",  // ⭐ KLÍČ PRO KATEGORIZACI
  "nazev_obce": "Janské Lázně",
  "nazev_okresu": "Trutnov",
  "www": "http://www.janskelazne.com/",
  "geometry": {
    "type": "Point",
    "coordinates": [15.xxx, 50.xxx]
  },
  "pristupnost": "ano",
  // ... další pole
}
```

## 🔍 Jak funguje vyhledávání

### Princip: REGEX vyhledávání v poli `source_file`

Když řekneš "**Najdi lázně**":

```python
# 1. LLM zavolá funkci s parametry:
hledej_mista_na_rande(
    typ_dotazu="category",    # Typ dotazu
    kategorie="Lázně"         # Co hledat
)

# 2. Funkce vytvoří MongoDB dotaz:
query = {
    "source_file": {
        "$regex": "Lázně",     # Hledej "Lázně" v názvu souboru
        "$options": "i"        # Case-insensitive (nerozlišuj velká/malá)
    }
}

# 3. MongoDB najde všechny dokumenty kde:
#    source_file obsahuje text "Lázně"
#    = data_hk_rande/Lázně.geojson ✅
```

### Příklady dotazů

#### ✅ "Ukaž mi lázně"
```python
query = {"source_file": {"$regex": "Lázně", "$options": "i"}}
# Najde: data_hk_rande/Lázně.geojson
# Vrátí: 5 lázní (Janské Lázně, Lázně Bělohrad...)
```

#### ✅ "Kde jsou koupaliště?"
```python
query = {"source_file": {"$regex": "Letní koupání", "$options": "i"}}
# Najde: data_hk_rande/Letní koupání.geojson
# Vrátí: aquaparky, koupaliště, písníky...
```

#### ✅ "Hrady v kraji"
```python
query = {"source_file": {"$regex": "Hrady", "$options": "i"}}
# Najde: data_hk_rande/Hrady.geojson
# Vrátí: Hrad Kost, Hrad Pecka...
```

## 🎯 Speciální kategorie

### Kombinované dotazy

Když řekneš "**Romantická místa**":
```python
romantic_categories = [
    "Zámky", "Hrady", "Rozhledny", "Přírodní", 
    "Botanické", "Lázně", "Pivovary", "Divadla",
    "Muzea", "Galerie", "Kina", "Restaurace"
]

# Vytvoří dotaz který najde COKOLIV z tohoto
query = {
    "source_file": {
        "$regex": "Zámky|Hrady|Rozhledny|Přírodní|...",  # | = NEBO
        "$options": "i"
    }
}
```

### Wellness kategorie
```python
wellness_categories = ["Lázně", "Solné jeskyně", "Koupání"]
# Najde: Lázně.geojson, Solné jeskyně.geojson, Letní koupání.geojson
```

## 📊 Mapování: Co uživatel řekne → Co se hledá

| Uživatel říká | LLM pošle | MongoDB hledá | Najde soubor |
|---------------|-----------|---------------|--------------|
| "lázně" | `kategorie="Lázně"` | `source_file: /Lázně/` | Lázně.geojson |
| "koupaliště" | `kategorie="Letní koupání"` | `source_file: /Letní koupání/` | Letní koupání.geojson |
| "hrady" | `kategorie="Hrady"` | `source_file: /Hrady/` | Hrady.geojson |
| "pivovary" | `kategorie="Pivovary"` | `source_file: /Pivovary/` | Pivovary.geojson |
| "zoo" | `kategorie="Zoo"` | `source_file: /Zoo/` | Zoo a zooparky.geojson |

## 🧠 Jak LLM ví co hledat?

### 1. System Prompt obsahuje všechny kategorie
```python
SYSTEMOVA_INSTRUKCE = """
Máš přístup k databázi více než 1000 míst v kraji, ve 22 kategoriích:
- 🏰 Hrady a zámky
- 💆 Lázně - wellness, relaxace pro dva
- 🏊 Letní koupání - koupaliště, aquaparky
...
"""
```

### 2. Tool Description vysvětluje kategorii
```python
funkce_hledani_mist = genai.protos.FunctionDeclaration(
    description="""
    Dostupné kategorie (22):
    - Lázně, Solné jeskyně, Letní koupání - wellness a relaxace
    - Hrady, Zámky - romantické památky
    ...
    """,
    parameters={
        "kategorie": "Kategorie míst: Hrady, Zámky, Lázně, Letní koupání..."
    }
)
```

### 3. LLM mapuje přirozenou řeč na kategorie

```
Uživatel: "Najdi lázně"
    ↓
LLM: "Lázně" zmíněno v system promptu ✓
    ↓
LLM: Zavolám funkci s kategorie="Lázně"
    ↓
Databáze: Hledám source_file obsahující "Lázně"
    ↓
Výsledek: 5 lázní nalezeno
```

## 🔧 Technické detaily

### REGEX operátor v MongoDB
```javascript
// $regex = hledá pattern v textu
{ "source_file": { "$regex": "Lázně", "$options": "i" } }

// Najde:
✅ "data_hk_rande/Lázně.geojson"
✅ "data_hk_rande/LÁZNĚ.geojson"  (case-insensitive)
✅ "...něco...Lázně...něco..."

// Nenajde:
❌ "data_hk_rande/Hrady.geojson"
❌ "data_hk_rande/Muzea.geojson"
```

### Kombinované dotazy s |
```python
"Hrady|Zámky|Rozhledny"  # OR operátor

# Najde VŠECHNY soubory které obsahují:
# - "Hrady" NEBO
# - "Zámky" NEBO  
# - "Rozhledny"
```

## 🎯 Shrnutí

**Celý systém funguje na jednom poli: `source_file`**

1. **Import**: Název souboru → `source_file` v databázi
2. **LLM**: Mapuje přirozenou řeč → název kategorie
3. **MongoDB**: REGEX vyhledávání v `source_file`
4. **Výsledek**: Vrátí všechna místa z daného souboru

**Výhody:**
✅ Jednoduché - stačí název souboru
✅ Rychlé - MongoDB regex je optimalizovaný
✅ Flexibilní - LLM se učí z popisu kategorií
✅ Přesné - každý soubor = jedna kategorie

**Omezení:**
⚠️ Závislé na názvech souborů (musí být konzistentní)
⚠️ Nelze snadno měnit kategorie bez přejmenovávání souborů
