import os
import requests

# Récupération propre des secrets GitHub
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    print("REPONSE TELEGRAM :", response.text, flush=True)
    return response.json()

if __name__ == "__main__":
    send_telegram_message("🤖 *Test du bot pronos réussi !* Prêt pour @vipprono_225.")
