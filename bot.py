import os
import random
import requests

# Récupération des secrets configurés sur GitHub (correction du nom du token)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text
        # On retire "parse_mode" pour éviter tout conflit de caractères spéciaux
    }
    response = requests.post(url, json=payload)
    print("STATUT HTTP :", response.status_code)
    print("REPONSE COMPLETE :", response.text)
    return response.json()

def generate_prediction():
    # Liste de grands matchs et de sélections variées (Safe, Fun, Live FIFA)
    prediction_types = ["safe", "fun", "fifa"]
    chosen_type = random.choice(prediction_types)
    
    if chosen_type == "safe":
        matches_safe = [
            ("Real Madrid – FC Barcelona", "Les deux équipes marquent"),
            ("Manchester City – Arsenal", "Manchester City ou Nul & Moins de 4,5 buts"),
            ("Bayern Munich – Borussia Dortmund", "Victoire Bayern Munich"),
            ("Inter Milan – Juventus", "Moins de 3,5 buts dans le match")
        ]
        match, selection = random.choice(matches_safe)
        
        message = (
            "🔥 VIP PRONOS 225\n\n"
            "🛡️ TICKET SAFE (GRAND CHOC)\n"
            f"📌 Match : {match}\n"
            f"🎯 Sélection : {selection}\n\n"
            "📌 BOOKMAKER : Paripesa\n"
            "🎁 CODE PROMO : POSSIBLE06\n"
            "🔗 https://paripesa.bet/possible06\n\n"
            "⚠️ Jouez responsablement."
        )
    elif chosen_type == "fun":
        matches_fun = [
            ("Real Madrid – FC Barcelona", "Victoire Real Madrid & Plus de 2,5 buts"),
            ("Paris Saint-Germain – AC Milan", "Victoire PSG par 1 but d'écart ou plus"),
            ("Liverpool – Real Madrid", "Les deux équipes marquent en 1ère mi-temps"),
            ("Atletico Madrid – Manchester City", "Match nul à la mi-temps")
        ]
        match, selection = random.choice(matches_fun)
        
        message = (
            "🔥 VIP PRONOS 225\n\n"
            "🚀 TICKET FUN (COTE DE FOLIE)\n"
            f"📌 Match : {match}\n"
            f"🎯 Sélection : {selection}\n\n"
            "📌 BOOKMAKER : Paripesa\n"
            "🎁 CODE PROMO : POSSIBLE06\n"
            "🔗 https://paripesa.bet/possible06\n\n"
            "⚠️ Jouez responsablement."
        )
    else:
        fifa_matches = [
            ("France (Esport) vs Brazil (Esport)", "Plus de 3.5 buts", "@1.90"),
            ("Argentina (Esport) vs England (Esport)", "Victoire Argentina", "@1.75"),
            ("Portugal (Esport) vs Germany (Esport)", "Les deux équipes marquent", "@1.80")
        ]
        match, selection, cote = random.choice(fifa_matches)
        
        message = (
            "🔥 VIP PRONOS 225\n\n"
            "🎮 LIVE FIFA ESPORT (GROS MATCH)\n"
            f"📌 Match : {match}\n"
            f"🎯 Sélection : {selection}\n"
            f"📊 Cote : {cote}\n\n"
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