#!/usr/bin/env python3
"""
Hlavní entry point pro chatbot
"""
from database import Database
from chat import ChatBot


def main():
    """Hlavní funkce aplikace"""
    
    # Inicializace databáze
    db = Database()
    
    # Úvodní zpráva
    print("="*60)
    print("🌹 ASISTENT PRO RANDE V KRÁLOVÉHRADECKÉM KRAJI 🌹")
    print("="*60)
    print(f"\n✓ Připojeno k databázi s {db.count_documents()} místy")
    print("\nPomůžu vám najít perfektní místa na rande, výlety pro dva")
    print("nebo romantické zážitky v Královéhradeckém kraji!")
    print("\nNapište 'konec' pro ukončení\n")
    print("="*60)
    
    # Inicializace chatbota
    chatbot = ChatBot(db.get_collection())
    
    # Příklady dotazů
    print("\n💡 Příklady konverzace:")
    print("  - Ahoj, chci naplánovat rande")
    print("  - Hledám místo na výlet pro dva")
    print("  - Ukaž mi hrady v kraji")
    print("  - Najdi pivovary které můžeme navštívit")
    print("  - Kam na romantický večer?")
    print("")
    
    # Hlavní smyčka
    try:
        while True:
            try:
                vstup_uzivatele = input("Vy: ").strip()
                
                if vstup_uzivatele.lower() in ['konec', 'quit', 'exit', 'q']:
                    print("👋 Přeji hezké rande! Nashledanou!")
                    break
                
                if vstup_uzivatele:
                    chatbot.send_message(vstup_uzivatele)
                    
            except KeyboardInterrupt:
                print("\n👋 Přeji hezké rande! Nashledanou!")
                break
            except Exception as e:
                print(f"❌ Chyba: {e}")
    finally:
        # Uzavření databázového připojení
        db.close()


if __name__ == "__main__":
    main()
