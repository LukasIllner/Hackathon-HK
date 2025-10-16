"""
Konfigurace pro chatbot - API klíče a konstanty
"""
import os
from dotenv import load_dotenv

# Načtení prostředí z databáze
env_path = os.path.join(os.path.dirname(__file__), '..', 'databaze', '.env')
load_dotenv(env_path)

# API klíče
GEMINI_API_KEY = "AIzaSyCYnOrldYfeGFVp2Bepa2qyxFmy46NpMm4"

# MongoDB konfigurace
MONGODB_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'hackathon_hk')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'places')

# Model konfigurace
GEMINI_MODEL = 'gemini-2.0-flash'

# Timeout konfigurace
MONGODB_TIMEOUT = 10000  # ms
