#!/usr/bin/env python3
"""
Flask API Server pro Hackathon HK - LOKÁLNÍ VERZE
Načítá data z lokálních GeoJSON souborů
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import glob

app = Flask(__name__)
CORS(app)  # Povol CORS pro frontend

# Cesta k GeoJSON souborům
GEOJSON_DIR = "../../data HK - rande geojson"

# Globální cache pro načtená data
places_cache = {}

def load_all_places():
    """Načte všechna místa z GeoJSON souborů"""
    global places_cache

    if places_cache:
        return places_cache

    print("📂 Načítám GeoJSON soubory...")

    geojson_path = os.path.join(os.path.dirname(__file__), GEOJSON_DIR)
    files = glob.glob(os.path.join(geojson_path, "*.geojson"))

    total = 0
    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            source_file = os.path.basename(filepath)

            for feature in data.get('features', []):
                props = feature.get('properties', {})
                dp_id = props.get('dp_id')

                if dp_id:
                    # Přidej geometry do properties pro jednodušší práci
                    place_data = {
                        **props,
                        'geometry': feature.get('geometry'),
                        'source_file': source_file
                    }
                    places_cache[dp_id] = place_data
                    total += 1

        except Exception as e:
            print(f"⚠️  Chyba při načítání {filepath}: {e}")

    print(f"✅ Načteno {total} míst z {len(files)} souborů")
    return places_cache


@app.route('/')
def index():
    """Základní info o API"""
    places = load_all_places()
    return jsonify({
        'status': 'online',
        'message': 'Hackathon HK - Map API (Local GeoJSON)',
        'total_places': len(places),
        'endpoints': {
            '/api/place/<dp_id>': 'Získat místo podle dp_id',
            '/api/places': 'Získat všechna místa',
            '/api/health': 'Health check'
        }
    })


@app.route('/api/health')
def health():
    """Health check endpoint"""
    places = load_all_places()
    return jsonify({
        'status': 'healthy',
        'source': 'local_geojson',
        'places_loaded': len(places)
    })


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
        places = load_all_places()

        place = places.get(dp_id)

        if not place:
            return jsonify({
                'error': 'Place not found',
                'dp_id': dp_id
            }), 404

        return jsonify(place)

    except Exception as e:
        return jsonify({
            'error': 'Server error',
            'message': str(e)
        }), 500


@app.route('/api/places')
def get_all_places():
    """
    Získá všechna místa (s limitem)

    Query parameters:
        ?limit=N - Počet výsledků (default 100, max 1000)

    Returns:
        JSON array s místy
    """
    try:
        limit = request.args.get('limit', default=100, type=int)
        limit = min(limit, 1000)  # Max 1000

        places = load_all_places()
        places_list = list(places.values())[:limit]

        return jsonify({
            'count': len(places_list),
            'total': len(places),
            'places': places_list
        })

    except Exception as e:
        return jsonify({
            'error': 'Server error',
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
        query = request.args.get('q', '').lower()

        if not query:
            return jsonify({
                'error': 'Missing query parameter',
                'message': 'Use ?q=search_term'
            }), 400

        places = load_all_places()

        # Vyhledej v názvech
        results = [
            place for place in places.values()
            if query in place.get('nazev', '').lower()
        ][:50]

        return jsonify({
            'query': query,
            'count': len(results),
            'places': results
        })

    except Exception as e:
        return jsonify({
            'error': 'Server error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Spouštím API server (Local GeoJSON)...")
    print("="*50)

    # Načti data při startu
    places = load_all_places()

    print(f"📍 URL: http://localhost:5000")
    print(f"📊 Načteno míst: {len(places)}")
    print("\nDostupné endpointy:")
    print("  • GET /")
    print("  • GET /api/health")
    print("  • GET /api/place/<dp_id>")
    print("  • GET /api/places")
    print("  • GET /api/search?q=text")
    print("\n" + "="*50 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=False)
