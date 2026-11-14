def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    print("REPONSE TELEGRAM :", response.text)  # <--- Ajoute cette ligne pour voir l'erreur exacte
    return response.json()
