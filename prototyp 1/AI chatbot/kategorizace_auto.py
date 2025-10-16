#!/usr/bin/env python3
"""
Automatická kategorizace - bez interaktivních otázek
Kategorizuje pouze místa která nemají pole 'kategorie'
"""

import google.generativeai as genai
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json
import time
from tqdm import tqdm

# Načtení konfigurace
env_path = os.path.join(os.path.dirname(__file__), '..', 'databaze', '.env')
load_dotenv(env_path)

GEMINI_API_KEY = "AIzaSyCYnOrldYfeGFVp2Bepa2qyxFmy46NpMm4"
MONGODB_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'hackathon_hk')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'places')

# Inicializace Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash-lite')

DOSTUPNE_KATEGORIE = [
    "romantické", "hrad", "zámek", "museum", "galerie", "pivovar", "restaurace",
    "wellness", "lázně", "relaxace", "koupání", "aquapark", "bazén",
    "příroda", "park", "zahrada", "rozhledna", "výhled",
    "sport", "aktivní", "turistika", "golf",
    "kulturní", "historické", "památka", "církevní",
    "zábava", "zoo", "festival", "hudba",
    "letní", "klidné", "rodinné", "pro páry", "venkovní"
]


def kategorizuj_misto(doc):
    """Kategorizuje místo pomocí Gemini"""
    
    prompt = f"""Kategorizuj toto turistické místo a vrať JSON array kategorií.

Místo:
Název: {doc.get('nazev', 'Neznámé')}
Typ: {doc.get('source_file', '').split('/')[-1].replace('.geojson', '')}
Obec: {doc.get('nazev_obce', '')}"""
    
    if doc.get('typ_muzea'):
        prompt += f"\nTyp muzea: {doc.get('typ_muzea')}"
    if doc.get('popis'):
        prompt += f"\nPopis: {doc.get('popis')[:150]}"
    
    prompt += f"\n\nVyber 3-6 kategorií ze seznamu:\n{', '.join(DOSTUPNE_KATEGORIE)}\n\nVrať POUZE JSON array."
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip().replace('```json', '').replace('```', '').strip()
        kategorie = json.loads(text)
        return [k for k in kategorie if k in DOSTUPNE_KATEGORIE][:6]
    except Exception as e:
        # Fallback podle source_file
        source = doc.get('source_file', '')
        if 'Hrady' in source: return ['hrad', 'historické']
        elif 'Zámky' in source: return ['zámek', 'historické']
        elif 'Lázně' in source: return ['lázně', 'wellness']
        elif 'Koupání' in source: return ['koupání', 'letní']
        else: return ['kulturní']


# Připojení k MongoDB
print("🚀 Automatická kategorizace míst")
print("="*60)
client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Najdi místa bez kategorií
query = {"$or": [{"kategorie": {"$exists": False}}, {"kategorie": []}]}
count = collection.count_documents(query)

print(f"📊 Míst bez kategorií: {count}")
print(f"⏱️  Odhadovaný čas: ~{count * 2 // 60} minut")
print("🤖 Model: gemini-2.5-flash-lite")
print("\nSpouštím...\n")

updated = 0
errors = 0

with tqdm(total=count, desc="Kategorizace", unit="místo") as pbar:
    cursor = collection.find(query)
    
    for doc in cursor:
        try:
            kategorie = kategorizuj_misto(doc)
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"kategorie": kategorie}}
            )
            updated += 1
            pbar.set_postfix({"✅": updated, "❌": errors})
            time.sleep(0.5)
        except Exception as e:
            errors += 1
            pbar.set_postfix({"✅": updated, "❌": errors})
        
        pbar.update(1)

print(f"\n✅ HOTOVO!")
print(f"Aktualizováno: {updated}")
print(f"Chyby: {errors}")

client.close()
