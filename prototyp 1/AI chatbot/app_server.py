#!/usr/bin/env python3
"""
Hlavní Flask server pro aplikaci - propojuje AI chatbot s frontendem
"""
import json
import os
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import google.generativeai as genai

from config import GEMINI_API_KEY, GEMINI_MODEL
from database import Database, hledej_mista_na_rande
from tools import get_tool
from prompts import SYSTEMOVA_INSTRUKCE

# Konfigurace
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__, static_folder='../databaze/frontend')
CORS(app)

# Globální databáze
db = Database()
places_collection = db.get_collection()

# Úložiště chat sessions (v produkci použít Redis nebo databázi)
chat_sessions = {}


class ChatSession:
    """Reprezentuje chat session s uživatelem"""
    
    def __init__(self, session_id):
        self.session_id = session_id
        
        self.model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            tools=[get_tool()],
            system_instruction=SYSTEMOVA_INSTRUKCE
        )
        
        self.chat = self.model.start_chat()
        self.history = []
        self.last_locations = []
    
    def send_message(self, user_message):
        """
        Odeslání zprávy do chatu
        
        Returns:
            dict: {
                'response': str,
                'locations': list,
                'tool_calls': list
            }
        """
        locations = []
        tool_calls_info = []
        response_text = ""
        
        try:
            # Uložení user zprávy do historie
            self.history.append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat()
            })
            
            # Odeslání zprávy do Gemini
            print(f"💬 Odesílám do AI: {user_message}")
            response = self.chat.send_message(user_message)
            print(f"🤖 AI odpověděla, zpracovávám...")
            
            # Zpracování volání funkcí
            while True:
                if response.candidates[0].content.parts:
                    function_responses = []
                    has_function_calls = False
                    
                    print(f"🔍 Počet parts v odpovědi: {len(response.candidates[0].content.parts)}")
                    
                    for part in response.candidates[0].content.parts:
                        print(f"  📦 Part type: {type(part)}")
                        print(f"  📦 Has function_call: {hasattr(part, 'function_call')}")
                        print(f"  📦 Has text: {hasattr(part, 'text')}")
                        if hasattr(part, 'text'):
                            print(f"  📝 Text preview: {part.text[:100]}...")
                        if hasattr(part, 'function_call') and part.function_call:
                            has_function_calls = True
                            function_call = part.function_call
                            function_name = function_call.name
                            function_args = dict(function_call.args)
                            
                            print(f"🔍 Tool call: {function_name}")
                            print(f"📝 Args: {json.dumps(function_args, ensure_ascii=False, indent=2)}")
                            
                            # Záznam tool callu
                            tool_calls_info.append({
                                'function': function_name,
                                'arguments': function_args
                            })
                            
                            # Provedení funkce
                            if function_name == "hledej_mista_na_rande":
                                function_result = hledej_mista_na_rande(
                                    places_collection, 
                                    **function_args
                                )
                                
                                # Uložení nalezených míst
                                if function_result.get('uspech') and function_result.get('mista'):
                                    locations.extend(function_result['mista'])
                                
                                print(f"✅ Nalezeno {function_result.get('pocet', 0)} míst")
                            else:
                                function_result = {"uspech": False, "chyba": "Neznámá funkce"}
                            
                            # Přidání odpovědi funkce
                            function_responses.append(
                                genai.protos.Part(
                                    function_response=genai.protos.FunctionResponse(
                                        name=function_name,
                                        response={'result': function_result}
                                    )
                                )
                            )
                    
                    if has_function_calls and function_responses:
                        # Odeslání výsledků funkcí zpět do LLM
                        response = self.chat.send_message(
                            genai.protos.Content(parts=function_responses)
                        )
                    else:
                        # Textová odpověď
                        for part in response.candidates[0].content.parts:
                            if hasattr(part, 'text'):
                                response_text = part.text
                                
                                # FALLBACK: Detekuj jestli AI omylem poslala kód
                                if 'print(' in response_text or 'hledej_mista_na_rande(' in response_text or 'default_api' in response_text:
                                    print("⚠️ AI poslala kód místo volání funkce! Opravuji...")
                                    response_text = "Omlouvám se, momentálně nemůžu vyhledat. Můžeš zkusit zadat konkrétnější dotaz, například: 'najdi hrady' nebo 'ukaž pivovary'."
                        break
                else:
                    break
            
            # Uložení odpovědi AI do historie
            self.history.append({
                'role': 'assistant',
                'content': response_text,
                'timestamp': datetime.now().isoformat(),
                'locations': locations,
                'tool_calls': tool_calls_info
            })
            
            # Aktualizace posledních lokací
            if locations:
                self.last_locations = locations
            
            result = {
                'response': response_text,
                'locations': locations,
                'tool_calls': tool_calls_info
            }
            
            # Debug log
            print(f"📤 Odpověď pro frontend:")
            print(f"   - Response: {response_text[:100]}...")
            print(f"   - Locations count: {len(locations)}")
            if locations:
                print(f"   - First location: {locations[0].get('nazev')} (ID: {locations[0].get('dp_id')})")
            
            return result
            
        except Exception as e:
            print(f"❌ Chyba v chat session: {e}")
            import traceback
            traceback.print_exc()
            
            error_msg = f"Omlouvám se, vyskytla se chyba: {str(e)}"
            self.history.append({
                'role': 'assistant',
                'content': error_msg,
                'timestamp': datetime.now().isoformat(),
                'error': True
            })
            
            return {
                'response': error_msg,
                'locations': [],
                'tool_calls': [],
                'error': str(e)
            }


def get_or_create_session(session_id):
    """Získá nebo vytvoří chat session"""
    if session_id not in chat_sessions:
        chat_sessions[session_id] = ChatSession(session_id)
    return chat_sessions[session_id]


# === API ENDPOINTY ===

@app.route('/')
def index():
    """Servíruj frontend"""
    return send_from_directory(app.static_folder, 'app_production.html')


@app.route('/<path:path>')
def static_files(path):
    """Servíruj statické soubory"""
    return send_from_directory(app.static_folder, path)


@app.route('/api/health')
def health():
    """Health check"""
    try:
        # Test databáze
        count = db.count_documents()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'places_count': count,
            'active_sessions': len(chat_sessions)
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@app.route('/api/chat/message', methods=['POST'])
def chat_message():
    """
    Endpoint pro posílání zpráv do chatu
    
    Body:
        {
            "session_id": "unique-session-id",
            "message": "Hledám romantickou restauraci"
        }
    
    Response:
        {
            "response": "Našel jsem pro vás...",
            "locations": [...],
            "tool_calls": [...]
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message in request'}), 400
        
        session_id = data.get('session_id', 'default')
        user_message = data.get('message')
        
        # Získat nebo vytvořit session
        session = get_or_create_session(session_id)
        
        # Poslat zprávu
        result = session.send_message(user_message)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error in /api/chat/message: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'error': str(e),
            'response': 'Omlouvám se, došlo k chybě při zpracování vaší zprávy.',
            'locations': []
        }), 500


@app.route('/api/chat/history', methods=['GET'])
def chat_history():
    """
    Získá historii chatu
    
    Query params:
        session_id: ID session
    """
    session_id = request.args.get('session_id', 'default')
    
    if session_id in chat_sessions:
        session = chat_sessions[session_id]
        return jsonify({
            'history': session.history,
            'last_locations': session.last_locations
        })
    else:
        return jsonify({
            'history': [],
            'last_locations': []
        })


@app.route('/api/chat/reset', methods=['POST'])
def chat_reset():
    """Resetuje chat session"""
    data = request.get_json()
    session_id = data.get('session_id', 'default')
    
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    
    return jsonify({'success': True, 'message': 'Chat reset'})


@app.route('/api/place/<dp_id>')
def get_place(dp_id):
    """Získá místo podle dp_id z databáze"""
    try:
        place = places_collection.find_one({'dp_id': dp_id}, {'_id': 0})
        
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


@app.route('/api/test/search')
def test_search():
    """Test endpoint - vyhledá hrady pro testování"""
    try:
        result = hledej_mista_na_rande(
            places_collection,
            typ_dotazu="category",
            kategorie="Hrady",
            pocet_vysledku=3
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SPOUŠTÍM APLIKACI - Rande v Hradci Králové")
    print("="*60)
    print(f"✓ Připojeno k databázi: {db.count_documents()} míst")
    print(f"✓ AI Model: {GEMINI_MODEL}")
    print(f"\n📍 Frontend URL: http://localhost:5000")
    print(f"📍 API URL: http://localhost:5000/api")
    print("\nDostupné endpointy:")
    print("  • GET  /                     - Frontend aplikace")
    print("  • GET  /api/health           - Health check")
    print("  • POST /api/chat/message     - Poslat zprávu do chatu")
    print("  • GET  /api/chat/history     - Historie chatu")
    print("  • POST /api/chat/reset       - Reset chatu")
    print("  • GET  /api/place/<dp_id>    - Detail místa")
    print("\n" + "="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
