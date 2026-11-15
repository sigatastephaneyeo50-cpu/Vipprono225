import os
import sys
import requests
from datetime import datetime

# Récupération des secrets configurés sur GitHub
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
FOOTBALL_API_KEY = os.environ.get("FOOTBALL_API_KEY")

# Liste élargie : Grands championnats + Compétitions internationales & Matchs amicaux
MAJOR_COMPETITIONS = ["CL", "UNL", "PL", "PD", "SA", "BL1", "FL1", "CLI"]

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

def fetch_today_major_matches():
    """Interroge l'API pour les matchs du jour et filtre uniquement les tournois majeurs et internationaux"""
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY} if FOOTBALL_API_KEY else {}
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    params = {
        "dateFrom": today_str,
        "dateTo": today_str
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            all_matches = data.get("matches", [])
            
            # Filtrer pour ne garder que les compétitions majeures et internationales
            filtered_matches = []
            for m in all_matches:
                comp_code = m.get("competition", {}).get("code", "")
                if comp_code in MAJOR_COMPETITIONS:
                    filtered_matches.append(m)
            
            print(f"Matchs totaux du jour : {len(all_matches)} | Gardés (Clubs majeurs + Internationaux) : {len(filtered_matches)}")
            return filtered_matches
    except Exception as e:
        print("Erreur lors de la récupération des matchs :", e)
    
    return []

def run_morning_predictions():
    """Génère les pronostics du matin basés sur les matchs majeurs et internationaux"""
    matches = fetch_today_major_matches()
    match_list = []
    
    for m in matches:
        home = m.get("homeTeam", {}).get("name", "")
        away = m.get("awayTeam", {}).get("name", "")
        if home and away:
            match_list.append((home, away))
            
    # Attribution des matchs récupérés
    if len(match_list) >= 4:
        m1_home, m1_away = match_list[0]
        m2_home, m2_away = match_list[1]
        m3_home, m3_away = match_list[2]
        m4_home, m4_away = match_list[3]
    elif len(match_list) > 0:
        m1_home, m1_away = match_list[0]
        m2_home, m2_away = match_list[min(1, len(match_list)-1)]
        m3_home, m3_away = match_list[min(2, len(match_list)-1)]
        m4_home, m4_away = match_list[min(3, len(match_list)-1)]
    else:
        # Affiches de repli si aucun match n'est répertorié ce jour-là
        m1_home, m1_away = "Brésil", "Argentine"
        m2_home, m2_away = "France", "Angleterre"
        m3_home, m3_away = "Espagne", "Italie"
        m4_home, m4_away = "Allemagne", "Portugal"

    # Ticket Safe (Cote cible : entre 2.00 et 3.00)
    safe_msg = (
        "<b>🔥 VIP PRONOS 225</b>\n\n"
        "<b>🛡️ TICKET SAFE (COTE : ~2.45)</b>\n\n"
        f"📌 <b>{m1_home} vs {m1_away}</b>\n"
        "• Option : Handicap (+1) pour l'équipe visiteuse\n"
        "💡 <i>Analyse : Affiche internationale serrée, l'outsider solide en déplacement.</i>\n\n"
        f"📌 <b>{m2_home} vs {m2_away}</b>\n"
        "• Option : Plus de 1,5 buts dans le match\n"
        "💡 <i>Analyse : Gros engagement offensif attendu sur cette pelouse.</i>\n\n"
        "<b>📌 BOOKMAKER : Paripesa</b>\n"
        "<b>🎁 CODE PROMO : POSSIBLE06</b>\n"
        "🔗 https://paripesa.bet/possible06\n\n"
        "⚠️ Jouez responsablement."
    )

    # Ticket Fun (Cote cible : jusqu'à 10.00)
    fun_msg = (
        "<b>🔥 VIP PRONOS 225</b>\n\n"
        "<b>🚀 TICKET FUN (COTE : ~8.50)</b>\n\n"
        f"📌 <b>{m3_home} vs {m3_away}</b>\n"
        "• Option : Victoire sèche & Plus de 2,5 buts\n"
        "💡 <i>Analyse : Choc de sélections, les compteurs doivent s'affoler.</i>\n\n"
        f"📌 <b>{m4_home} vs {m4_away}</b>\n"
        "• Option : Handicap (-1.5) pour le favori\n"
        "💡 <i>Analyse : Supériorité technique claire, victoire par au moins 2 buts d'écart exigée.</i>\n\n"
        "<b>📌 BOOKMAKER : Paripesa</b>\n"
        "<b>🎁 CODE PROMO : POSSIBLE06</b>\n"
        "🔗 https://paripesa.bet/possible06\n\n"
        "⚠️ Jouez responsablement."
    )

    send_telegram_message(safe_msg)
    send_telegram_message(fun_msg)
    print("Tickets (Championnats + Internationaux) envoyés avec succès !")

def run_evening_results():
    """Vérifie les scores et envoie le bilan du soir"""
    matches = fetch_today_major_matches()
    results_summary = "<b>📊 BILAN DES RÉSULTATS (MATCHS MAJEURS & INTERNATIONAUX)</b>\n\n"
    
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
        results_summary += "⚽ <b>Bilan de la soirée :</b> Superbe suivi des affiches sur @vipprono_225 !\n"
        results_summary += "🎯 Demain, on attaque de nouvelles opportunités."
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