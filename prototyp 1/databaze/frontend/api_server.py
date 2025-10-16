#!/usr/bin/env python3
"""
Flask API Server pro Hackathon HK
Poskytuje REST API pro přístup k MongoDB databázi míst
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Načti environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Povol CORS pro frontend

# MongoDB připojení
MONGODB_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'hackathon_hk')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'places')

if not MONGODB_URI:
    print("ERROR: MONGODB_URI not found in .env file!")
    exit(1)

try:
    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    # Test připojení
    client.server_info()
    print(f"✓ Připojeno k MongoDB: {DATABASE_NAME}.{COLLECTION_NAME}")
except Exception as e:
    print(f"✗ Chyba připojení k MongoDB: {e}")
    exit(1)


@app.route('/')
def index():
    """Základní info o API"""
    return jsonify({
        'status': 'online',
        'message': 'Hackathon HK - Map API',
        'endpoints': {
            '/api/place/<dp_id>': 'Získat místo podle dp_id',
            '/api/places': 'Získat všechna místa',
            '/api/health': 'Health check'
        }
    })


@app.route('/api/health')
def health():
    """Health check endpoint"""
    try:
        # Otestuj databázové připojení
        collection.find_one()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


@app.route('/api/place/<dp_id>')
def get_place(dp_id):
    """
    Získá místo podle dp_id

    Example:
        GET /api/place/HRAD1

    Returns:
        JSON s detaily místa nebo 404 pokud neexistuje
    """
    try:
        place = collection.find_one({'dp_id': dp_id}, {'_id': 0})

        if not place:
            return jsonify({
                'error': 'Place not found',
                'dp_id': dp_id
            }), 404

        return jsonify(place)

    except Exception as e:
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500


@app.route('/api/places')
def get_all_places():
    """
    Získá všechna místa (s limitem 100)

    Query parameters:
        ?limit=N - Počet výsledků (default 100, max 1000)

    Returns:
        JSON array s místy
    """
    try:
        limit = request.args.get('limit', default=100, type=int)
        limit = min(limit, 1000)  # Max 1000

        places = list(collection.find({}, {'_id': 0}).limit(limit))

        return jsonify({
            'count': len(places),
            'places': places
        })

    except Exception as e:
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500


@app.route('/api/search')
def search_places():
    """
    Vyhledá místa podle názvu

    Query parameters:
        ?q=text - Hledaný text v názvu

    Example:
        GET /api/search?q=hrad

    Returns:
        JSON array s nalezenými místy
    """
    try:
        query = request.args.get('q', '')

        if not query:
            return jsonify({
                'error': 'Missing query parameter',
                'message': 'Use ?q=search_term'
            }), 400

        # Case-insensitive regex search
        places = list(collection.find(
            {'nazev': {'$regex': query, '$options': 'i'}},
            {'_id': 0}
        ).limit(50))

        return jsonify({
            'query': query,
            'count': len(places),
            'places': places
        })

    except Exception as e:
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Spouštím API server...")
    print("="*50)
    print(f"📍 URL: http://localhost:5000")
    print(f"📊 Database: {DATABASE_NAME}.{COLLECTION_NAME}")
    print("\nDostupné endpointy:")
    print("  • GET /")
    print("  • GET /api/health")
    print("  • GET /api/place/<dp_id>")
    print("  • GET /api/places")
    print("  • GET /api/search?q=text")
    print("\n" + "="*50 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
