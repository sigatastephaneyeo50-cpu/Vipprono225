import os
import random
import requests

# Récupération des secrets configurés sur GitHub
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text
    }
    response = requests.post(url, json=payload)
    print("STATUT HTTP :", response.status_code)
    print("REPONSE COMPLETE :", response.text)
    return response.json()

def generate_prediction():
    # Choisi aléatoirement entre un ticket Safe et un ticket Fun avec les matchs du jour
    prediction_types = ["safe", "fun"]
    chosen_type = random.choice(prediction_types)
    
    if chosen_type == "safe":
        message = (
            "🔥 VIP PRONOS 225\n\n"
            "🛡️ TICKET SAFE\n"
            "Türkiye – Belgium – X2\n"
            "Italy – France – Moins de 3,5 buts\n"
            "England – Croatia – Victoire England\n\n"
            "📌 BOOKMAKER : Paripesa\n"
            "🎁 CODE PROMO : POSSIBLE06\n"
            "🔗 https://paripesa.bet/possible06\n\n"
            "⚠️ Jouez responsablement."
        )
    else:
        message = (
            "🔥 VIP PRONOS 225\n\n"
            "🚀 TICKET FUN\n"
            "Türkiye – Belgium – Victoire Belgium\n"
            "Italy – France – Plus de 1,5 buts\n"
            "Czech Republic – Spain – Victoire Spain\n"
            "Albania – Finland – Victoire Finland\n"
            "Montenegro – Latvia – Plus de 1,5 buts\n\n"
            "📌 BOOKMAKER : Paripesa\n"
            "🎁 CODE PROMO : POSSIBLE06\n"
            "🔗 https://paripesa.bet/possible06\n\n"
            "⚠️ Jouez responsablement."
        )
        
    return message

if __name__ == "__main__":
    if not TOKEN or not CHANNEL_ID:
        print("Erreur : Les secrets Telegram ne sont pas configurés.")
    else:
        forecast = generate_prediction()
        result = send_telegram_message(forecast)
        print("Exécution terminée.")