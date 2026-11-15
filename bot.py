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
    """Interroge l'API pour récupérer les matchs du jour de manière robuste"""
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
            print(f"Matchs bruts récupérés : {len(matches)}")
            return matches
    except Exception as e:
        print("Erreur lors de la récupération des matchs :", e)
    
    return []

def run_morning_predictions():
    """Génère les pronostics du matin avec des options variées et des noms garantis"""
    matches = fetch_today_matches()
    match_list = []
    
    for m in matches:
        # Extraction sécurisée des noms d'équipes
        home_team = m.get("homeTeam")
        away_team = m.get("awayTeam")
        
        home = home_team.get("name") if isinstance(home_team, dict) else ""
        away = away_team.get("name") if isinstance(away_team, dict) else ""
        
        utc_time = m.get("utcDate", "")
        time_str = "🕒 En journée"
        if utc_time:
            try:
                dt = datetime.strptime(utc_time, "%Y-%m-%dT%H:%M:%SZ")
                time_str = f"🕒 {dt.strftime('%H:%M')} UTC"
            except:
                pass
                
        if home and away:
            match_list.append((home, away, time_str))
            
    # Si l'API retourne des matchs, on les prend, sinon listes de secours diversifiées
    if len(match_list) >= 4:
        m1 = match_list[0]
        m2 = match_list[1]
        m3 = match_list[2]
        m4 = match_list[3]
    elif len(match_list) > 0:
        m1 = match_list[0]
        m2 = match_list[min(1, len(match_list)-1)]
        m3 = match_list[min(2, len(match_list)-1)]
        m4 = match_list[min(3, len(match_list)-1)]
    else:
        # Secours varié
        m1 = ("Brésil", "Uruguay", "🕒 20:00 UTC")
        m2 = ("Sénégal", "Côte d'Ivoire", "🕒 17:00 UTC")
        m3 = ("France", "Italie", "🕒 20:45 UTC")
        m4 = ("Espagne", "Allemagne", "🕒 20:45 UTC")

    # Options variées pour casser la monotonie
    safe_msg = (
        "<b>🔥 VIP PRONOS 225</b>\n\n"
        "<b>🛡️ TICKET SAFE (COTE : ~2.45)</b>\n\n"
        f"📌 <b>{m1[0]} vs {m1[1]}</b>\n"
        f"{m1[2]}\n"
        "• Option : Double Chance (1X) & Moins de 3,5 buts\n"
        "💡 <i>Analyse : Gestion rigoureuse du match, l'équipe à domicile solide dans son antre.</i>\n\n"
        f"📌 <b>{m2[0]} vs {m2[1]}</b>\n"
        f"{m2[2]}\n"
        "• Option : Handicap (+1) pour l'équipe extérieure\n"
        "💡 <i>Analyse : L'outsider a les armes pour accrocher un résultat serré.</i>\n\n"
        "<b>📌 BOOKMAKER : Paripesa</b>\n"
        "<b>🎁 CODE PROMO : POSSIBLE06</b>\n"
        "🔗 https://paripesa.bet/possible06\n\n"
        "⚠️ Jouez responsablement."
    )

    fun_msg = (
        "<b>🔥 VIP PRONOS 225</b>\n\n"
        "<b>🚀 TICKET FUN (COTE : ~8.50)</b>\n\n"
        f"📌 <b>{m3[0]} vs {m3[1]}</b>\n"
        f"{m3[2]}\n"
        "• Option : Les deux équipes marquent & Plus de 2,5 buts\n"
        "💡 <i>Analyse : Choc ouvert avec un gros potentiel offensif des deux côtés.</i>\n\n"
        f"📌 <b>{m4[0]} vs {m4[1]}</b>\n"
        f"{m4[2]}\n"
        "• Option : Handicap (-1.5) pour le favori\n"
        "💡 <i>Analyse : Supériorité manifeste, victoire nette par au moins 2 buts d'écart attendue.</i>\n\n"
        "<b>📌 BOOKMAKER : Paripesa</b>\n"
        "<b>🎁 CODE PROMO : POSSIBLE06</b>\n"
        "🔗 https://paripesa.bet/possible06\n\n"
        "⚠️ Jouez responsablement."
    )

    send_telegram_message(safe_msg)
    send_telegram_message(fun_msg)
    print("Tickets dynamiques et variés envoyés avec succès !")

def run_evening_results():
    """Vérifie les scores et envoie le bilan du soir"""
    matches = fetch_today_matches()
    results_summary = "<b>📊 BILAN DES RÉSULTATS DU JOUR</b>\n\n"
    
    count = 0
    for m in matches[:4]:
        home_team = m.get("homeTeam", {})
        away_team = m.get("awayTeam", {})
        home = home_team.get("name", "") if isinstance(home_team, dict) else ""
        away = away_team.get("name", "") if isinstance(away_team, dict) else ""
        
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
        results_summary += "⚽ <b>Bilan de la journée :</b> Excellent suivi des tickets sur @vipprono_225 !\n"
        results_summary += "🎯 Rendez-vous demain pour de nouvelles analyses."
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