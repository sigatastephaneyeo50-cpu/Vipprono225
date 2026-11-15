import os
import requests

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
    """Interroge l'API Football pour récupérer les matchs du jour en cours"""
    url = "https://api.football-data.org/v4/matches"
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
        # Récupération des vrais matchs du jour via l'API
        real_matches = fetch_today_matches()
        
        if len(real_matches) >= 5:
            m1_home, m1_away = real_matches[0]
            m2_home, m2_away = real_matches[1]
            m3_home, m3_away = real_matches[2]
            m4_home, m4_away = real_matches[3]
            m5_home, m5_away = real_matches[4]
        elif len(real_matches) > 0:
            matches_pool = real_matches * 5
            m1_home, m1_away = matches_pool[0]
            m2_home, m2_away = matches_pool[1]
            m3_home, m3_away = matches_pool[2]
            m4_home, m4_away = matches_pool[3]
            m5_home, m5_away = matches_pool[4]
        else:
            # Matchs de secours si l'API est vide
            m1_home, m1_away = "France", "Turquie"
            m2_home, m2_away = "Belgique", "Italie"
            m3_home, m3_away = "Espagne", "Angleterre"
            m4_home, m4_away = "Croatie", "Tchéquie"
            m5_home, m5_away = "Albanie", "Finlande"

        # Construction du Ticket Safe avec mini-analyses
        safe_msg = (
            "<b>🔥 VIP PRONOS 225</b>\n\n"
            "<b>🛡️ TICKET SAFE & ANALYSES</b>\n\n"
            f"📌 <b>{m1_home} vs {m1_away}</b>\n"
            "• Option : X2\n"
            "💡 <i>Analyse : Solide à l'extérieur, l'équipe visiteuse a les armes pour ne pas perdre ce choc.</i>\n\n"
            f"📌 <b>{m2_home} vs {m2_away}</b>\n"
            "• Option : Moins de 3,5 buts\n"
            "💡 <i>Analyse : Tactique fermée attendue, les deux blocs défensifs battront rarement en retraite.</i>\n\n"
            f"📌 <b>{m3_home} vs {m3_away}</b>\n"
            "• Option : Victoire " + m3_home + "\n"
            "💡 <i>Analyse : Supériorité technique évidente à domicile, grosse dynamique à maintenir.</i>\n\n"
            "<b>📌 BOOKMAKER : Paripesa</b>\n"
            "<b>🎁 CODE PROMO : POSSIBLE06</b>\n"
            "🔗 https://paripesa.bet/possible06\n\n"
            "⚠️ Jouez responsablement."
        )

        # Construction du Ticket Fun avec mini-analyses
        fun_msg = (
            "<b>🔥 VIP PRONOS 225</b>\n\n"
            "<b>🚀 TICKET FUN (COTE DE FOLIE) & ANALYSES</b>\n\n"
            f"📌 <b>{m1_home} vs {m1_away}</b>\n"
            "• Option : Victoire " + m1_away + "\n"
            "💡 <i>Analyse : Coup à tenter, l'outsider a montré de belles fulgurances en contre.</i>\n\n"
            f"📌 <b>{m2_home} vs {m2_away}</b>\n"
            "• Option : Plus de 1,5 buts\n"
            "💡 <i>Analyse : Gros potentiel offensif des deux côtés, le premier but libérera des espaces.</i>\n\n"
            f"📌 <b>{m4_home} vs {m4_away}</b>\n"
            "• Option : Victoire " + m4_away + "\n"
            "💡 <i>Analyse : Envie de rachat affichée pour les visiteurs qui alignent leur équipe type.</i>\n\n"
            f"📌 <b>{m5_home} vs {m5_away}</b>\n"
            "• Option : Victoire " + m5_home + "\n"
            "💡 <i>Analyse : Forteresse à domicile, l'adversaire souffre traditionnellement sur cette pelouse.</i>\n\n"
            "<b>📌 BOOKMAKER : Paripesa</b>\n"
            "<b>🎁 CODE PROMO : POSSIBLE06</b>\n"
            "🔗 https://paripesa.bet/possible06\n\n"
            "⚠️ Jouez responsablement."
        )

        # Envoi des messages sur le canal
        send_telegram_message(safe_msg)
        send_telegram_message(fun_msg)
        print("Tickets avec analyses envoyés avec succès !")