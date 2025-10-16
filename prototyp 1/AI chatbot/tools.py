"""
Definice nástrojů (tools) pro Gemini AI
"""
import google.generativeai as genai


# Definice funkce pro Gemini
funkce_hledani_mist = genai.protos.FunctionDeclaration(
    name="hledej_mista_na_rande",
    description="""Vyhledává místa vhodná na rande v Královéhradeckém kraji (Česká republika).
    
    Dostupné kategorie (22):
    - Hrady, Zámky - romantické památky
    - Muzea a galerie, Divadla a filharmonie, Kina - kultura
    - Pivovary, Restaurace - gastronomie
    - Lázně, Solné jeskyně, Letní koupání - wellness a relaxace
    - Zoo a zooparky, Zábavní centra - zábava
    - Přírodní zajímavosti, Botanické zahrady, Rozhledny a výhlídky - příroda
    - Letní sporty, Golfové hřiště, Rybaření - sport
    - Církevní památky, Národní kulturní památky, Technické památky - památky
    - Hudební kluby a festival parky, Festivaly - hudba a akce""",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "typ_dotazu": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="Typ dotazu k provedení - VŽDY použij 'category' pokud hledáš podle kategorie (např. Hrady, Lázně, Muzea)",
                enum=["text_search", "category", "geospatial", "romantic", "specific_place", "all"]
            ),
            "hledany_text": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="Text k vyhledání v názvech a popisech míst"
            ),
            "kategorie": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="JEDNA kategorie (ne seznam!): hrady, zámky, muzea, pivovary, restaurace, zoo, divadla, kina, lázně, koupaliště, příroda, rozhledny, galerie, atd. NEPOUŽÍVEJ čárky!"
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
            ),
            "wellness": genai.protos.Schema(
                type=genai.protos.Type.BOOLEAN,
                description="Hledat wellness a relaxaci (lázně, solné jeskyně, koupaliště)"
            )
        },
        required=["typ_dotazu"]
    )
)

# Vytvoření nástroje
nastroj = genai.protos.Tool(function_declarations=[funkce_hledani_mist])


def get_tool():
    """Vrací nástroj pro Gemini"""
    return nastroj
