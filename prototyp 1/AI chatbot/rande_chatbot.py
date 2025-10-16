"""
Chatbot pro doporučování míst na rande v Královéhradeckém kraji
Asistent pro hledání romantických a zajímavých míst pro dvojice
"""

import google.generativeai as genai
from google.generativeai import protos
import json
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Načtení prostředí z databáze
env_path = os.path.join(os.path.dirname(__file__), '..', 'databaze', '.env')
load_dotenv(env_path)

# Konfigurace Gemini API
API_KEY = "AIzaSyCYnOrldYfeGFVp2Bepa2qyxFmy46NpMm4"
genai.configure(api_key=API_KEY)

# MongoDB připojení
mongodb_uri = os.getenv('MONGODB_URI')
database_name = os.getenv('DATABASE_NAME', 'hackathon_hk')
collection_name = os.getenv('COLLECTION_NAME', 'places')

if not mongodb_uri:
    print("CHYBA: MONGODB_URI nenalezeno v .env souboru!")
    print(f"Zkontrolujte prosím: {env_path}")
    sys.exit(1)

# Připojení k MongoDB
try:
    mongo_client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
    mongo_client.admin.command('ping')
    db = mongo_client[database_name]
    places_collection = db[collection_name]
    print("✓ Připojeno k MongoDB Atlas")
except Exception as e:
    print(f"✗ Připojení k MongoDB selhalo: {e}")
    sys.exit(1)


# Funkce pro dotazování databáze míst
def hledej_mista_na_rande(
    typ_dotazu: str,
    hledany_text: str = None,
    kategorie: str = None,
    region: str = None,
    sirka: float = None,
    delka: float = None,
    max_vzdalenost_km: float = None,
    pocet_vysledku: int = 5,
    romanticky: bool = False,
    venkovni: bool = False,
    kulturni: bool = False
):
    """
    Hledá místa vhodná na rande v Královéhradeckém kraji.
    
    Args:
        typ_dotazu: Typ dotazu - "text_search", "category", "geospatial", "romantic", "all"
        hledany_text: Text k vyhledání v názvech a popisech míst
        kategorie: Filtr podle kategorie (Restaurace, Hrady, Pivovary, Muzea, atd.)
        region: Filtr podle regionu (okres, obec)
        sirka: Zeměpisná šířka pro vyhledávání podle polohy
        delka: Zeměpisná délka pro vyhledávání podle polohy
        max_vzdalenost_km: Maximální vzdálenost v kilometrech
        pocet_vysledku: Maximální počet výsledků (výchozí 5, max 20)
        romanticky: Hledat romantická místa (restaurace, hrady, rozhledny, příroda)
        venkovni: Hledat venkovní aktivity
        kulturni: Hledat kulturní místa (muzea, divadla, galerie)
    
    Returns:
        Seznam míst vhodných na rande s detaily
    """
    
    try:
        pocet_vysledku = min(pocet_vysledku, 20)
        query = {}
        
        # Romantická místa - kombinace vhodných kategorií
        if romanticky or typ_dotazu == "romantic":
            romantic_categories = [
                "Zámky", "Hrady", "Rozhledny", "Přírodní", 
                "Botanické", "Lázně", "Pivovary", "Divadla",
                "Muzea", "Galerie", "Kina"
            ]
            query["source_file"] = {
                "$regex": "|".join(romantic_categories), 
                "$options": "i"
            }
        
        # Venkovní aktivity
        elif venkovni:
            outdoor_categories = [
                "Přírodní", "Rozhledny", "Botanické", 
                "Koupání", "sport", "Golf"
            ]
            query["source_file"] = {
                "$regex": "|".join(outdoor_categories),
                "$options": "i"
            }
        
        # Kulturní místa
        elif kulturni:
            cultural_categories = [
                "Muzea", "Galerie", "Divadla", "Kina",
                "Hrady", "Zámky", "Církevní", "Kulturní"
            ]
            query["source_file"] = {
                "$regex": "|".join(cultural_categories),
                "$options": "i"
            }
        
        # Textové vyhledávání
        elif typ_dotazu == "text_search" and hledany_text:
            query["$text"] = {"$search": hledany_text}
        
        # Vyhledávání podle kategorie
        elif typ_dotazu == "category" and kategorie:
            query["source_file"] = {"$regex": kategorie, "$options": "i"}
        
        # Geolokační vyhledávání
        elif typ_dotazu == "geospatial" and sirka and delka:
            if not max_vzdalenost_km:
                max_vzdalenost_km = 20  # Výchozí 20km pro rande
            
            query["geometry"] = {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [delka, sirka]
                    },
                    "$maxDistance": max_vzdalenost_km * 1000
                }
            }
        
        # Specifické místo
        elif typ_dotazu == "specific_place" and hledany_text:
            query["$or"] = [
                {"nazev": {"$regex": hledany_text, "$options": "i"}},
                {"dp_id": hledany_text}
            ]
        
        # Filtr podle regionu
        if region and "source_file" in query:
            # Combine with existing query
            query = {
                "$and": [
                    query,
                    {
                        "$or": [
                            {"nazev_okresu": {"$regex": region, "$options": "i"}},
                            {"nazev_obce": {"$regex": region, "$options": "i"}},
                            {"nazev_orp": {"$regex": region, "$options": "i"}}
                        ]
                    }
                ]
            }
        elif region:
            query["$or"] = [
                {"nazev_okresu": {"$regex": region, "$options": "i"}},
                {"nazev_obce": {"$regex": region, "$options": "i"}},
                {"nazev_orp": {"$regex": region, "$options": "i"}}
            ]
        
        # Provedení dotazu
        vysledky = list(places_collection.find(query).limit(pocet_vysledku))
        
        # Formátování výsledků
        formatovana_mista = []
        for doc in vysledky:
            misto = {
                "nazev": doc.get("nazev", "Neznámé"),
                "id": doc.get("dp_id", "N/A"),
                "kategorie": doc.get("source_file", "N/A").split("/")[-1].replace(".geojson", ""),
                "okres": doc.get("nazev_okresu", "N/A"),
                "obec": doc.get("nazev_obce", "N/A"),
                "adresa": f"{doc.get('nazev_ulice', '')}, {doc.get('nazev_obce', '')}".strip(", "),
                "souradnice": doc.get("geometry", {}).get("coordinates", []),
                "web": doc.get("www", "Není k dispozici"),
                "pristupnost": doc.get("bezbarierovost", "Neuvedeno"),
            }
            
            # Přidání specifických polí
            if "typ_muzea" in doc:
                misto["typ_muzea"] = doc.get("typ_muzea")
                misto["zamereni"] = doc.get("zamereni_muzea", "")
            
            if "popis" in doc:
                misto["popis"] = doc.get("popis", "")[:300]
            
            formatovana_mista.append(misto)
        
        return {
            "uspech": True,
            "pocet": len(formatovana_mista),
            "dotaz": str(query),
            "mista": formatovana_mista
        }
        
    except Exception as e:
        return {
            "uspech": False,
            "chyba": str(e),
            "mista": []
        }


# Definice funkce pro Gemini
funkce_hledani_mist = genai.protos.FunctionDeclaration(
    name="hledej_mista_na_rande",
    description="""Vyhledává místa vhodná na rande v Královéhradeckém kraji (Česká republika).
    Databáze obsahuje romantická místa, hrady, zámky, muzea, pivovary, restaurace, přírodní 
    zajímavosti, rozhledny a další místa ideální pro rande nebo společné zážitky.
    
    Kategorie: Muzea a galerie, Hrady, Zámky, Pivovary, Zoo, Divadla, Kina, Přírodní zajímavosti,
    Rozhledny a výhlídky, Botanické zahrady, Lázně, a další.""",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "typ_dotazu": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="Typ dotazu k provedení",
                enum=["text_search", "category", "geospatial", "romantic", "specific_place", "all"]
            ),
            "hledany_text": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="Text k vyhledání v názvech a popisech míst"
            ),
            "kategorie": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="Kategorie míst (Muzea, Hrady, Zámky, Pivovary, Zoo, Divadla, Kina, Přírodní zajímavosti, atd.)"
            ),
            "region": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="Název regionu/okresu/obce pro filtrování"
            ),
            "sirka": genai.protos.Schema(
                type=genai.protos.Type.NUMBER,
                description="Zeměpisná šířka pro vyhledávání podle polohy (Hradec Králové ~50.2)"
            ),
            "delka": genai.protos.Schema(
                type=genai.protos.Type.NUMBER,
                description="Zeměpisná délka pro vyhledávání podle polohy (Hradec Králové ~15.8)"
            ),
            "max_vzdalenost_km": genai.protos.Schema(
                type=genai.protos.Type.NUMBER,
                description="Maximální vzdálenost v kilometrech (výchozí 20km)"
            ),
            "pocet_vysledku": genai.protos.Schema(
                type=genai.protos.Type.INTEGER,
                description="Maximální počet výsledků (výchozí 5, max 20)"
            ),
            "romanticky": genai.protos.Schema(
                type=genai.protos.Type.BOOLEAN,
                description="Hledat specificky romantická místa (hrady, zámky, rozhledny, příroda)"
            ),
            "venkovni": genai.protos.Schema(
                type=genai.protos.Type.BOOLEAN,
                description="Hledat venkovní aktivity"
            ),
            "kulturni": genai.protos.Schema(
                type=genai.protos.Type.BOOLEAN,
                description="Hledat kulturní místa (muzea, divadla, galerie)"
            )
        },
        required=["typ_dotazu"]
    )
)

# Vytvoření nástroje
nastroj = genai.protos.Tool(function_declarations=[funkce_hledani_mist])

# Mapování funkcí
dostupne_funkce = {
    "hledej_mista_na_rande": hledej_mista_na_rande
}

# Systémová instrukce pro LLM v češtině
SYSTEMOVA_INSTRUKCE = """Jsi přátelský a nápomocný asistent pro doporučování míst na rande v Královéhradeckém kraji.

Tvůj hlavní účel je pomáhat lidem najít perfektní místa pro rande, romantické výlety a společné zážitky.

Máš přístup k databázi více než 1000 míst v kraji, včetně:
- 🏰 Hrady a zámky - romantické, historické prostředí
- 🎨 Muzea a galerie - kulturní zážitky
- 🍺 Pivovary - posezení při dobré svarepě
- 🦁 Zoo a zooparky - zábava pro páry i rodiny
- 🎭 Divadla a kina - kulturní večery
- 🌳 Přírodní zajímavosti - procházky v přírodě
- 👁️ Rozhledny a výhlídky - romantické výhledy
- 🌸 Botanické zahrady - klidné prostředí
- 💆 Lázně - relaxace pro dva
- 🎡 Zábavní centra - aktivní zábava

PRAVIDLA PRO VOLÁNÍ FUNKCE:
🚫 NEvolej funkci hledej_mista_na_rande pokud:
   - Uživatel jen pozdraví nebo zahajuje konverzaci
   - Ptá se obecně bez konkrétní žádosti o místa
   - Ještě si není jistý co chce
   - Odpovídá na tvé upřesňující otázky

✅ Volej funkci hledej_mista_na_rande POUZE pokud:
   - Uživatel EXPLICITNĚ žádá konkrétní místa ("ukaž mi", "najdi", "kde jsou", "chci vidět")
   - Rozhodl se a chce konkrétní doporučení
   - Má jasnou představu (hrady, pivovary, muzea, atd.)

POSTUP KONVERZACE:
1. První kontakt: Buď přátelský, ptej se na preference
2. Zjisti co hledá: Romantické? Kulturní? Aktivní? Venkovní?
3. Upřesni požadavky: Kde? Vzdálenost? Specifické přání?
4. AŽ PAK: Zavolej funkci a najdi konkrétní místa

Tvoje odpovědi by měly být:
✅ V češtině
✅ Přátelské a konverzační
✅ Nejdřív se ptej, pak hledej
✅ Zaměřené na zážitek pro dvojice
✅ S informacemi o přístupnosti když zobrazuješ místa

Typy randí k doporučení:
- 🏰 Romantické (hrady, zámky, rozhledny, příroda)
- 🎨 Kulturní (muzea, divadla, galerie)
- 🍺 Relaxační (pivovary, lázně, kavárny)
- 🏃 Aktivní (sporty, zoo, příroda)

Pamatuj si kontext předchozích dotazů v konverzaci."""


def chat_s_databazi(zprava_uzivatele: str, chat_session):
    """Odeslání zprávy a zpracování dotazů do databáze"""
    
    # Použití existující konverzace
    chat = chat_session
    
    # Odeslání zprávy
    response = chat.send_message(zprava_uzivatele)
    
    # Zpracování volání funkcí
    while True:
        if response.candidates[0].content.parts:
            function_responses = []
            has_function_calls = False
            
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    has_function_calls = True
                    function_call = part.function_call
                    function_name = function_call.name
                    function_args = dict(function_call.args)
                    
                    print(f"🔍 HLEDÁNÍ V DATABÁZI: {function_name}")
                    print(f"📝 Parametry: {json.dumps(function_args, indent=2, ensure_ascii=False)}")
                    
                    if function_name in dostupne_funkce:
                        function_result = dostupne_funkce[function_name](**function_args)
                        print(f"✅ Nalezeno {function_result.get('pocet', 0)} míst\n")
                        
                        function_responses.append(
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=function_name,
                                    response={'result': function_result}
                                )
                            )
                        )
            
            if has_function_calls and function_responses:
                response = chat.send_message(genai.protos.Content(parts=function_responses))
            else:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'text'):
                        print(f"\n💬 ASISTENT: {part.text}\n")
                break
        else:
            break
    
    return chat


def main():
    """Hlavní funkce chatbota"""
    
    print("="*60)
    print("🌹 ASISTENT PRO RANDE V KRÁLOVÉHRADECKÉM KRAJI 🌹")
    print("="*60)
    print(f"\n✓ Připojeno k databázi s {places_collection.count_documents({})} místy")
    print("\nPomůžu vám najít perfektní místa na rande, výlety pro dva")
    print("nebo romantické zážitky v Královéhradeckém kraji!")
    print("\nNapište 'konec' pro ukončení\n")
    print("="*60)
    
    # Inicializace trvalé konverzace
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash-exp',
        tools=[nastroj],
        system_instruction=SYSTEMOVA_INSTRUKCE
    )
    chat = model.start_chat()
    
    # Příklady dotazů
    print("\n💡 Příklady konverzace:")
    print("  - Ahoj, chci naplánovat rande")
    print("  - Hledám místo na výlet pro dva")
    print("  - Ukaž mi hrady v kraji")
    print("  - Najdi pivovary které můžeme navštívit")
    print("  - Kam na romantický večer?")
    print("")
    
    while True:
        try:
            vstup_uzivatele = input("Vy: ").strip()
            if vstup_uzivatele.lower() in ['konec', 'quit', 'exit', 'q']:
                print("👋 Přeji hezké rande! Nashledanou!")
                break
            if vstup_uzivatele:
                chat = chat_s_databazi(vstup_uzivatele, chat)
        except KeyboardInterrupt:
            print("\n👋 Přeji hezké rande! Nashledanou!")
            break
        except Exception as e:
            print(f"❌ Chyba: {e}")


if __name__ == "__main__":
    main()
