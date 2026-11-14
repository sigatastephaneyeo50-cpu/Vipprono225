import os
import requests
from datetime import datetime

# ==========================================
# CONFIGURATION (Récupérées depuis GitHub)
# ==========================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

def envoyer_pronostic():
    print(f"[{datetime.now()}] Envoi du pronostic automatique en cours...")
    
    # Données de ton prono (tu pourras les modifier plus tard)
    match = "Oklahoma City Thunder vs San Antonio Spurs"
    selection = "Thunder -5.5"
    cote = "1.87"
    analyse = "Avantage net sur le plan défensif et la régularité à l'extérieur."
    mise = "2%"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    message = f"""
🤖 **AUTOMATIC PREDICTION // BOT BET** 🤖

🏆 **ANALYSE STATISTIQUE DU JOUR**
📌 **Match :** {match}
🎯 **Sélection :** {selection}
📊 **Cote estimée :** @{cote}

📝 **Analyse rapide :**
_{analyse}_

💡 *Mise conseillée : {mise} de la bankroll*

⚡️ *Pari responsable. Bon gain à tous !*
"""

    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message.strip(),
        "parse_mode": "Markdown"
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("✅ Pronostic envoyé avec succès sur le canal !")
    else:
        print(f"❌ Erreur Telegram : {response.text}")

if __name__ == "__main__":
    envoyer_pronostic()
