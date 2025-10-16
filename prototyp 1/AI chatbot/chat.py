"""
Chat logika a zpracování zpráv
"""
import json
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL
from tools import get_tool
from prompts import SYSTEMOVA_INSTRUKCE
from database import hledej_mista_na_rande

# Konfigurace Gemini API
genai.configure(api_key=GEMINI_API_KEY)


class ChatBot:
    """Chatbot pro doporučování míst na rande"""
    
    def __init__(self, places_collection):
        self.places_collection = places_collection
        self.model = None
        self.chat = None
        self._init_model()
    
    def _init_model(self):
        """Inicializace Gemini modelu"""
        self.model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            tools=[get_tool()],
            system_instruction=SYSTEMOVA_INSTRUKCE
        )
        self.chat = self.model.start_chat()
    
    def _execute_function(self, function_name, function_args):
        """Provedení databázové funkce"""
        if function_name == "hledej_mista_na_rande":
            return hledej_mista_na_rande(self.places_collection, **function_args)
        return {"uspech": False, "chyba": "Neznámá funkce", "mista": []}
    
    def send_message(self, user_message):
        """
        Odeslání zprávy a zpracování odpovědi
        
        Args:
            user_message: Zpráva od uživatele
            
        Returns:
            None (výstup je vytištěn)
        """
        # Odeslání zprávy
        response = self.chat.send_message(user_message)
        
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
                        
                        # Provedení funkce
                        function_result = self._execute_function(function_name, function_args)
                        print(f"✅ Nalezeno {function_result.get('pocet', 0)} míst\n")
                        
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
                    response = self.chat.send_message(genai.protos.Content(parts=function_responses))
                else:
                    # Textová odpověď
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'text'):
                            print(f"\n💬 ASISTENT: {part.text}\n")
                    break
            else:
                break
