import os
import requests
from datetime import datetime

# Récupération des secrets configurés sur GitHub
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
FOOTBALL_API_KEY = os.environ.get("FOOTBALL_API_KEY")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=payload)
    print("STATUT HTTP :", response.status_code)
    print("REPONSE COMPLETE :", response.text)
    return response.json()

def fetch_today_matches():
    """Interroge l'API Football pour récupérer les matchs du jour"""
    today = datetime.utcnow().strftime('%Y-%m-%d')
    url = f"https://api.football-data.org/v4/matches?dateFrom={today}&dateTo={today}"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY} if FOOTBALL_API_KEY else {}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            matches = data.get("matches", [])
            match_list = []
            for m in matches:
                home = m.get("homeTeam", {}).get("name", "")
                away = m.get("awayTeam", {}).get("name", "")
                if home and away:
                    match_list.append((home, away))
            return match_list
    except Exception as e:
        print("Erreur lors de la récupération des matchs :", e)
    
    return []

if __name__ == "__main__":
    if not TOKEN or not CHANNEL_ID:
        print("Erreur : Les secrets Telegram ne sont pas configurés.")
    else:
        # Récupération des vrais matchs du jour
        real_matches = fetch_today_matches()
        
        # Si on a assez de matchs via l'API, on les utilise, sinon liste de secours
        if len(real_matches) >= 5:
            m1_home, m1_away = real_matches[0]
            m2_home, m2_away = real_matches[1]
            m3_home, m3_away = real_matches[2]
            m4_home, m4_away = real_matches[3]
            m5_home, m5_away = real_matches[4]
        else:
            m1_home, m1_away = "Türkiye", "Belgium"
            m2_home, m2_away = "Italy", "France"
            m3_home, m3_away = "England", "Croatia"
            m4_home, m4_away = "Czech Republic", "Spain"
            m5_home, m5_away = "Albania", "Finland"

        # Génération dynamique d'options basées sur les équipes du jour
        safe_msg = (
            "<b>🔥 VIP PRONOS 225</b>\n\n"
            "<b>🛡️ TICKET SAFE</b>\n"
            f"{m1_home} vs {m1_away} – X2\n"
            f"{m2_home} vs {m2_away} – Moins de 3,5 buts\n"
            f"{m3_home} vs {m3_away} – Victoire {m3_home}\n\n"
            "<b>📌 BOOKMAKER : Paripesa</b>\n"
            "<b>🎁 CODE PROMO : POSSIBLE06</b>\n"
            "🔗 https://paripesa.bet/possible06\n\n"
            "⚠️ Jouez responsablement."
        )

        fun_msg = (
            "<b>🔥 VIP PRONOS 225</b>\n\n"
            "<b>🚀 TICKET FUN</b>\n"
            f"{m1_home} vs {m1_away} – Victoire {m1_away}\n"
            f"{m2_home} vs {m2_away} – Plus de 1,5 buts\n"
            f"{m4_home} vs {m4_away} – Victoire {m4_away}\n"
            f"{m5_home} vs {m5_away} – Victoire {m5_home}\n"
            f"{m3_away} vs {m3_home} – Plus de 1,5 buts\n\n"
            "<b>📌 BOOKMAKER : Paripesa</b>\n"
            "<b>🎁 CODE PROMO : POSSIBLE06</b>\n"
            "🔗 https://paripesa.bet/possible06\n\n"
            "⚠️ Jouez responsablement."
        )

        # Envoi des messages sur le canal
        send_telegram_message(safe_msg)
        send_telegram_message(fun_msg)
        print("Tickets dynamiques avec options adaptées envoyés avec succès !")