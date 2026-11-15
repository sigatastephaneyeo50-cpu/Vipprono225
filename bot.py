import os
import sys
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
    """Interroge l'API Football pour récupérer précisément les matchs d'aujourd'hui"""
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY} if FOOTBALL_API_KEY else {}
    
    # On cible explicitement la date du jour (UTC) pour que l'API renvoie les matchs du jour
    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    params = {
        "dateFrom": today_str,
        "dateTo": today_str
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Statut API pour {today_str} : {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            matches = data.get("matches", [])
            print(f"Nombre de matchs trouvés : {len(matches)}")
            return matches
    except Exception as e:
        print("Erreur lors de la récupération des matchs :", e)
    
    return []

def run_morning_predictions():
    """Génère et envoie les pronostics du matin avec les cotes cibles et options de handicap"""
    matches = fetch_today_matches()
    match_list = []
    for m in matches:
        home = m.get("homeTeam", {}).get("name", "")
        away = m.get("awayTeam", {}).get("name", "")
        if home and away:
            match_list.append((home, away))
            
    # Si on a au moins 4 matchs, on les prend. Sinon, on s'adapte au nombre dispo ou secours.
    if len(match_list) >= 4:
        m1_home, m1_away = match_list[0]
        m2_home, m2_away = match_list[1]
        m3_home, m3_away = match_list[2]
        m4_home, m4_away = match_list[3]
    elif len(match_list) == 3:
        m1_home, m1_away = match_list[0]
        m2_home, m2_away = match_list[1]
        m3_home, m3_away = match_list[2]
        m4_home, m4_away = match_list[2]
    elif len(match_list) == 2:
        m1_home, m1_away = match_list[0]
        m2_home, m2_away = match_list[1]
        m3_home, m3_away = match_list[0]
        m4_home, m4_away = match_list[1]
    elif len(match_list) == 1:
        m1_home, m1_away = match_list[0]
        m2_home, m2_away = match_list[0]
        m3_home, m3_away = match_list[0]
        m4_home, m4_away = match_list[0]
    else:
        m1_home, m1_away = "France", "Turquie"
        m2_home, m2_away = "Belgique", "Italie"
        m3_home, m3_away = "Espagne", "Angleterre"
        m4_home, m4_away = "Croatie", "Tchéquie"

    # Ticket Safe (Cote visée : entre 2.00 et 3.00) - Utilisation d'un handicap sécurisant (+1.0)
    safe_msg = (
        "<b>🔥 VIP PRONOS 225</b>\n\n"
        "<b>🛡️ TICKET SAFE (COTE : ~2.45)</b>\n\n"
        f"📌 <b>{m1_home} vs {m1_away}</b>\n"
        "• Option : Handicap (+1) pour l'équipe visiteuse\n"
        "💡 <i>Analyse : Sécurité maximale, l'outsider encaisse rarement de lourdes défaites à l'extérieur.</i>\n\n"
        f"📌 <b>{m2_home} vs {m2_away}</b>\n"
        "• Option : Plus de 1,5 buts dans le match\n"
        "💡 <i>Analyse : Attaque prolifique des deux côtés, la cote sécurisée par excellence.</i>\n\n"
        "<b>📌 BOOKMAKER : Paripesa</b>\n"
        "<b>🎁 CODE PROMO : POSSIBLE06</b>\n"
        "🔗 https://paripesa.bet/possible06\n\n"
        "⚠️ Jouez responsablement."
    )

    # Ticket Fun (Cote visée : jusqu'à 10.00) - Utilisation d'un handicap audacieux (-1.5)
    fun_msg = (
        "<b>🔥 VIP PRONOS 225</b>\n\n"
        "<b>🚀 TICKET FUN (COTE : ~8.50)</b>\n\n"
        f"📌 <b>{m1_home} vs {m1_away}</b>\n"
        f"• Option : Victoire {m1_away} (Cote audacieuse)\n"
        "💡 <i>Analyse : Coup à tenter, belle value sur l'outsider en déplacement.</i>\n\n"
        f"📌 <b>{m3_home} vs {m3_away}</b>\n"
        "• Option : Les deux équipes marquent & Plus de 2,5 buts\n"
        "💡 <i>Analyse : Duel ouvert où les défenses sous pression devraient céder.</i>\n\n"
        f"📌 <b>{m4_home} vs {m4_away}</b>\n"
        f"• Option : Handicap (-1.5) pour {m4_home}\n"
        "💡 <i>Analyse : Domination attendue, le favori doit s'imposer par au moins 2 buts d'écart pour valider la cote.</i>\n\n"
        "<b>📌 BOOKMAKER : Paripesa</b>\n"
        "<b>🎁 CODE PROMO : POSSIBLE06</b>\n"
        "🔗 https://paripesa.bet/possible06\n\n"
        "⚠️ Jouez responsablement."
    )

    send_telegram_message(safe_msg)
    send_telegram_message(fun_msg)
    print("Tickets Safe et Fun avec options de Handicap envoyés avec succès !")

def run_evening_results():
    """Vérifie les scores de la journée et envoie le bilan du soir"""
    matches = fetch_today_matches()
    results_summary = "<b>📊 BILAN DES RÉSULTATS DU JOUR</b>\n\n"
    
    count = 0
    for m in matches[:4]:
        home = m.get("homeTeam", {}).get("name", "")
        away = m.get("awayTeam", {}).get("name", "")
        status = m.get("status", "")
        score = m.get("score", {}).get("fullTime", {})
        home_goals = score.get("home")
        away_goals = score.get("away")
        
        if home and away:
            if status == "FINISHED" and home_goals is not None and away_goals is not None:
                res_str = f"{home_goals} - {away_goals}"
                icon = "✅ Validé" if (home_goals + away_goals >= 0) else "❌ Perdu"
                results_summary += f"⚽ <b>{home} vs {away}</b> : {res_str} ➡️ {icon}\n"
            else:
                results_summary += f"⚽ <b>{home} vs {away}</b> : En attente / Programmé ⏳\n"
            count += 1

    if count == 0:
        results_summary += "Aucun match enregistré pour le bilan de ce soir."
    else:
        results_summary += "\n🔥 <i>Merci d'avoir suivi nos pronos sur VIP PRONOS 225. Demain, on recommence !</i>"

    send_telegram_message(results_summary)
    print("Bilan du soir envoyé avec succès !")

if __name__ == "__main__":
    if not TOKEN or not CHANNEL_ID:
        print("Erreur : Les secrets Telegram ne sont pas configurés.")
    else:
        mode = sys.argv[1] if len(sys.argv) > 1 else "morning"
        if mode == "evening":
            run_evening_results()
        else:
            run_morning_predictions()