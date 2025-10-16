"""
Databázové funkce pro MongoDB
"""
import sys
from pymongo import MongoClient
from config import MONGODB_URI, DATABASE_NAME, COLLECTION_NAME, MONGODB_TIMEOUT


class Database:
    """Správce MongoDB připojení"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self._connect()
    
    def _connect(self):
        """Připojení k MongoDB"""
        if not MONGODB_URI:
            print("CHYBA: MONGODB_URI nenalezeno v .env souboru!")
            sys.exit(1)
        
        try:
            self.client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=MONGODB_TIMEOUT)
            self.client.admin.command('ping')
            self.db = self.client[DATABASE_NAME]
            self.collection = self.db[COLLECTION_NAME]
            print("✓ Připojeno k MongoDB Atlas")
        except Exception as e:
            print(f"✗ Připojení k MongoDB selhalo: {e}")
            sys.exit(1)
    
    def get_collection(self):
        """Vrací MongoDB kolekci"""
        return self.collection
    
    def count_documents(self):
        """Počet dokumentů v databázi"""
        return self.collection.count_documents({})
    
    def close(self):
        """Uzavření připojení"""
        if self.client:
            self.client.close()


def hledej_mista_na_rande(
    places_collection,
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
    kulturni: bool = False,
    wellness: bool = False
):
    """
    Hledá místa vhodná na rande v Královéhradeckém kraji.
    
    Args:
        places_collection: MongoDB kolekce s místy
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
                "romantické", "hrad", "zámek", "rozhledna", "výhled",
                "příroda", "park", "zahrada", "lázně", "wellness",
                "pivovar", "restaurace", "galerie", "museum", "klidné"
            ]
            query["kategorie"] = {"$in": romantic_categories}
        
        # Venkovní aktivity
        elif venkovni:
            outdoor_categories = [
                "venkovní", "příroda", "park", "rozhledna",
                "koupání", "sport", "aktivní", "turistika", "golf"
            ]
            query["kategorie"] = {"$in": outdoor_categories}
        
        # Kulturní místa
        elif kulturni:
            cultural_categories = [
                "kulturní", "museum", "galerie", "divadlo", "kino",
                "hrad", "zámek", "církevní", "historické", "památka"
            ]
            query["kategorie"] = {"$in": cultural_categories}
        
        # Wellness a relaxace
        elif wellness:
            wellness_categories = [
                "lázně", "wellness", "relaxace", "klidné", "koupání"
            ]
            query["kategorie"] = {"$in": wellness_categories}
        
        # Textové vyhledávání
        elif typ_dotazu == "text_search" and hledany_text:
            query["$text"] = {"$search": hledany_text}
        
        # Vyhledávání podle kategorie
        elif typ_dotazu == "category" and kategorie:
            # Mapování uživatelských dotazů na AI kategorie
            kategorie_lower = kategorie.lower()
            
            kategorie_mapping = {
                "hrady": ["hrad"],
                "hrad": ["hrad"],
                "zámky": ["zámek"],
                "zámek": ["zámek"],
                "lázně": ["lázně", "wellness"],
                "koupaliště": ["koupání", "aquapark", "bazén"],
                "koupání": ["koupání", "aquapark", "bazén"],
                "letní koupání": ["koupání", "aquapark", "bazén"],
                "muzea": ["museum"],
                "museum": ["museum"],
                "pivovary": ["pivovar"],
                "pivovar": ["pivovar"],
                "restaurace": ["restaurace"],
                "zoo": ["zoo"],
                "příroda": ["příroda"],
                "rozhledny": ["rozhledna"],
                "rozhledna": ["rozhledna"],
                "divadla": ["divadlo"],
                "divadlo": ["divadlo"],
                "galerie": ["galerie"],
                "kina": ["kino"]
            }
            
            # Pokud je kategorie v mappingu, použij seznam
            if kategorie_lower in kategorie_mapping:
                query["kategorie"] = {"$in": kategorie_mapping[kategorie_lower]}
            else:
                # Jinak hledej přímou shodu v kategoriích
                query["kategorie"] = kategorie_lower
        
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
        
        # FALLBACK: Pokud najdeme málo výsledků (< 3) a byl to category search,
        # zkus regex search v source_file jako backup
        if len(vysledky) < 3 and typ_dotazu == "category" and kategorie:
            fallback_query = {"source_file": {"$regex": kategorie, "$options": "i"}}
            
            # Přidej region filtr pokud existuje
            if region:
                fallback_query = {
                    "$and": [
                        fallback_query,
                        {
                            "$or": [
                                {"nazev_okresu": {"$regex": region, "$options": "i"}},
                                {"nazev_obce": {"$regex": region, "$options": "i"}},
                                {"nazev_orp": {"$regex": region, "$options": "i"}}
                            ]
                        }
                    ]
                }
            
            fallback_vysledky = list(places_collection.find(fallback_query).limit(pocet_vysledku))
            
            # Pokud fallback našel více, použij ty výsledky
            if len(fallback_vysledky) > len(vysledky):
                vysledky = fallback_vysledky
        
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
