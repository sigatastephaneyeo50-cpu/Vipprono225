import os
import requests

# Récupération des secrets configurés sur GitHub
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML"  # Permet d'utiliser les balises <b> pour le gras
    }
    response = requests.post(url, json=payload)
    print("STATUT HTTP :", response.status_code)
    print("REPONSE COMPLETE :", response.text)
    return response.json()

def get_safe_prediction():
    return (
        "<b>🔥 VIP PRONOS 225</b>\n\n"
        "<b>🛡️ TICKET SAFE</b>\n"
        "Türkiye vs Belgium – X2\n"
        "Italy vs France – Moins de 3,5 buts\n"
        "England vs Croatia – Victoire England\n\n"
        "<b>📌 BOOKMAKER : Paripesa</b>\n"
        "<b>🎁 CODE PROMO : POSSIBLE06</b>\n"
        "🔗 https://paripesa.bet/possible06\n\n"
        "⚠️ Jouez responsablement."
    )

def get_fun_prediction():
    return (
        "<b>🔥 VIP PRONOS 225</b>\n\n"
        "<b>🚀 TICKET FUN</b>\n"
        "Türkiye vs Belgium – Victoire Belgium\n"
        "Italy vs France – Plus de 1,5 buts\n"
        "Czech Republic vs Spain – Victoire Spain\n"
        "Albania vs Finland – Victoire Finland\n"
        "Montenegro vs Latvia – Plus de 1,5 buts\n\n"
        "<b>📌 BOOKMAKER : Paripesa</b>\n"
        "<b>🎁 CODE PROMO : POSSIBLE06</b>\n"
        "🔗 https://paripesa.bet/possible06\n\n"
        "⚠️ Jouez responsablement."
    )

if __name__ == "__main__":
    if not TOKEN or not CHANNEL_ID:
        print("Erreur : Les secrets Telegram ne sont pas configurés.")
    else:
        # Envoie le ticket Safe
        safe_msg = get_safe_prediction()
        send_telegram_message(safe_msg)
        
        # Envoie le ticket Fun à la suite
        fun_msg = get_fun_prediction()
        send_telegram_message(fun_msg)
        
        print("Tous les tickets du jour ont été envoyés avec succès !")