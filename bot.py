import os
import requests

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text
        # On retire temporairement "parse_mode" pour éviter les plantages de balises
    }
    response = requests.post(url, json=payload)
    print("STATUT HTTP :", response.status_code, flush=True)
    print("REPONSE COMPLETE :", response.text, flush=True)
    return response.json()

if __name__ == "__main__":
    # Ton message de prono ici
    message = "⚽ Pronostic du jour\nMatch : Équipe A vs Équipe B\nCote : 1.85"
    send_telegram_message(message)