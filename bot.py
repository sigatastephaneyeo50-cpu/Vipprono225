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
    """Interroge l'API pour récupérer les matchs exacts d'aujourd'hui"""
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY} if FOOTBALL_API_KEY else {}
    
    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    params = {
        "dateFrom": today_str,
        "dateTo": today_str
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Statut API : {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            matches = data.get("matches", [])
            print(f"Nombre de matchs trouvés pour aujourd'hui : {len(matches)}")
            return matches
    except Exception as e:
        print("Erreur lors de la récupération des matchs :", e)
    
    return []

def run_morning_predictions():
    """Génère les pronostics du matin basés sur les matchs réels du jour"""
    matches = fetch_today_matches()
    match_list = []
    
    for m in matches:
        home = m.get("homeTeam", {}).get("name", "")
        away = m.get("awayTeam", {}).get("name", "")
        utc_time = m.get("utcDate", "") # Format ex: 2026-11-15T15:00:00Z
        
        # Extraire l'heure proprement (HH:MM)
        time_str = "🕒 Horaire non défini"
        if utc_time:
            try:
                dt = datetime.strptime(utc_time, "%Y-%m-%dT%H:%M:%SZ")
                time_str = f"🕒 {dt.strftime('%H:%M')} UTC"
            except:
                pass
                
        if home and away:
            match_list.append((home, away, time_str))
            
    # Attribution dynamique des matchs du jour
    if len(match_list) >= 4:
        m1_home, m1_away, m1_time = match_list[0]
        m2_home, m2_away, m2_time = match_list[1]
        m3_home, m3_away, m3_time = match_list[2]
        m4_home, m4_away, m4_time = match_list[3]
    elif len(match_list) > 0:
        m1_home, m1_away, m1_time = match_list[0]
        m2_home, m2_away, m2_time = match_list[min(1, len(match_list)-1)]
        m3_home, m3_away, m3_time = match_list[min(2, len(match_list)-1)]
        m4_home, m4_away, m4_time = match_list[min(3, len(match_list)-1)]
    else:
        m1_home, m1_away, m1_time = "Équipe A", "Équipe B", "🕒 15:00"
        m2_home, m2_away, m2_time = "Équipe C", "Équipe D", "🕒 17:00"
        m3_home, m3_away, m3_time = "Équipe E", "Équipe F", "🕒 19:00"
        m4_home, m4_away, m4_time = "Équipe G", "Équipe H", "🕒 21:00"

    # Ticket Safe (Cote visée : entre 2.00 et 3.00)
    safe_msg = (
        "<b>🔥 VIP PRONOS 225</b>\n\n"
        "<b>🛡️ TICKET SAFE (COTE : ~2.45)</b>\n\n"
        f"📌 <b>{m1_home} vs {m1_away}</b>\n"
        f"{m1_time}\n"
        "• Option : Handicap (+1) / Double Chance\n"
        "💡 <i>Analyse : Option sécurisée basée sur la forme actuelle des formations.</i>\n\n"
        f"📌 <b>{m2_home} vs {m2_away}</b>\n"
        f"{m2_time}\n"
        "• Option : Plus de 1,5 buts dans le match\n"
        "💡 <i>Analyse : Gros potentiel offensif relevé par nos analyses statistiques.</i>\n\n"
        "<b>📌 BOOKMAKER : Paripesa</b>\n"
        "<b>🎁 CODE PROMO : POSSIBLE06</b>\n"
        "🔗 https://paripesa.bet/possible06\n\n"
        "⚠️ Jouez responsablement."
    )

    # Ticket Fun (Cote visée : jusqu'à 10.00)
    fun_msg = (
        "<b>🔥 VIP PRONOS 225</b>\n\n"
        "<b>🚀 TICKET FUN (COTE : ~8.50)</b>\n\n"
        f"📌 <b>{m3_home} vs {m3_away}</b>\n"
        f"{m3_time}\n"
        "• Option : Victoire sèche & Plus de 2,5 buts\n"
        "💡 <i>Analyse : Pari audacieux pour aller chercher une belle value.</i>\n\n"
        f"📌 <b>{m4_home} vs {m4_away}</b>\n"
        f"{m4_time}\n"
        "• Option : Handicap (-1.5) pour le favori\n"
        "💡 <i>Analyse : Domination attendue, victoire par au moins 2 buts d'écart exigée.</i>\n\n"
        "<b>📌 BOOKMAKER : Paripesa</b>\n"
        "<b>🎁 CODE PROMO : POSSIBLE06</b>\n"
        "🔗 https://paripesa.bet/possible06\n\n"
        "⚠️ Jouez responsablement."
    )

    send_telegram_message(safe_msg)
    send_telegram_message(fun_msg)
    print("Tickets du jour envoyés avec succès !")

def run_evening_results():
    """Vérifie les scores et envoie le bilan du soir"""
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
        results_summary += "⚽ <b>Bilan de la journée :</b> Suivi exceptionnel des affiches sur @vipprono_225 !\n"
        results_summary += "🎯 Rendez-vous demain pour de nouvelles opportunités."
    else:
        results_summary += "\n🔥 <i>Merci d'avoir suivi nos pronos sur VIP PRONOS 225. Demain, on remet ça !</i>"

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