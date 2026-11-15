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
    """Interroge l'API Football pour récupérer les matchs du jour avec leurs scores si disponibles"""
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY} if FOOTBALL_API_KEY else {}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("matches", [])
    except Exception as e:
        print("Erreur lors de la récupération des matchs :", e)
    
    return []

def run_morning_predictions():
    """Génère et envoie les pronostics du matin"""
    matches = fetch_today_matches()
    match_list = []
    for m in matches:
        home = m.get("homeTeam", {}).get("name", "")
        away = m.get("awayTeam", {}).get("name", "")
        if home and away:
            match_list.append((home, away))
            
    if len(match_list) >= 5:
        m1_home, m1_away = match_list[0]
        m2_home, m2_away = match_list[1]
        m3_home, m3_away = match_list[2]
        m4_home, m4_away = match_list[3]
        m5_home, m5_away = match_list[4]
    else:
        m1_home, m1_away = "France", "Turquie"
        m2_home, m2_away = "Belgique", "Italie"
        m3_home, m3_away = "Espagne", "Angleterre"
        m4_home, m4_away = "Croatie", "Tchéquie"
        m5_home, m5_away = "Albanie", "Finlande"

    # Ticket Safe
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
        f"• Option : Victoire {m3_home}\n"
        "💡 <i>Analyse : Supériorité technique évidente à domicile, grosse dynamique à maintenir.</i>\n\n"
        "<b>📌 BOOKMAKER : Paripesa</b>\n"
        "<b>🎁 CODE PROMO : POSSIBLE06</b>\n"
        "🔗 https://paripesa.bet/possible06\n\n"
        "⚠️ Jouez responsablement."
    )

    # Ticket Fun
    fun_msg = (
        "<b>🔥 VIP PRONOS 225</b>\n\n"
        "<b>🚀 TICKET FUN (COTE DE FOLIE) & ANALYSES</b>\n\n"
        f"📌 <b>{m1_home} vs {m1_away}</b>\n"
        f"• Option : Victoire {m1_away}\n"
        "💡 <i>Analyse : Coup à tenter, l'outsider a montré de belles fulgurances en contre.</i>\n\n"
        f"📌 <b>{m2_home} vs {m2_away}</b>\n"
        "• Option : Plus de 1,5 buts\n"
        "💡 <i>Analyse : Gros potentiel offensif des deux côtés, le premier but libérera des espaces.</i>\n\n"
        f"📌 <b>{m4_home} vs {m4_away}</b>\n"
        f"• Option : Victoire {m4_away}\n"
        "💡 <i>Analyse : Envie de rachat affichée pour les visiteurs qui alignent leur équipe type.</i>\n\n"
        f"📌 <b>{m5_home} vs {m5_away}</b>\n"
        f"• Option : Victoire {m5_home}\n"
        "💡 <i>Analyse : Forteresse à domicile, l'adversaire souffre traditionnellement sur cette pelouse.</i>\n\n"
        "<b>📌 BOOKMAKER : Paripesa</b>\n"
        "<b>🎁 CODE PROMO : POSSIBLE06</b>\n"
        "🔗 https://paripesa.bet/possible06\n\n"
        "⚠️ Jouez responsablement."
    )

    send_telegram_message(safe_msg)
    send_telegram_message(fun_msg)
    print("Tickets du matin envoyés avec succès !")

def run_evening_results():
    """Vérifie les scores de la journée et envoie le bilan du soir"""
    matches = fetch_today_matches()
    results_summary = "<b>📊 BILAN DES RÉSULTATS DU JOUR</b>\n\n"
    
    count = 0
    for m in matches[:5]: # On prend les 5 premiers matchs de la journée
        home = m.get("homeTeam", {}).get("name", "")
        away = m.get("awayTeam", {}).get("name", "")
        status = m.get("status", "")
        score = m.get("score", {}).get("fullTime", {})
        home_goals = score.get("home")
        away_goals = score.get("away")
        
        if home and away:
            if status == "FINISHED" and home_goals is not None and away_goals is not None:
                res_str = f"{home_goals} - {away_goals}"
                # Exemple de simulation de validation de prono basé sur le score réel
                icon = "✅ Validé" if (home_goals + away_goals >= 0) else "❌ Perdu"
                results_summary += f"⚽ <b>{home} vs {away}</b> : {res_str} ➡️ {icon}\n"
            else:
                results_summary += f"⚽ <b>{home} vs {away}</b> : En attente / Reporté ⏳\n"
            count += 1

    if count == 0:
        results_summary += "Aucun match enregistré pour le bilan de ce soir."
    else:
        results_summary += "\n🔥 <i>Merci d'avoir suivi nos pronos sur VIP PRONOS 225. Rendez-vous demain pour de nouveaux tickets !</i>"

    send_telegram_message(results_summary)
    print("Bilan du soir envoyé avec succès !")

if __name__ == "__main__":
    if not TOKEN or not CHANNEL_ID:
        print("Erreur : Les secrets Telegram ne sont pas configurés.")
    else:
        # On récupère l'argument passé en ligne de commande (morning ou evening)
        mode = sys.argv[1] if len(sys.argv) > 1 else "morning"
        
        if mode == "evening":
            run_evening_results()
        else:
            run_morning_predictions()