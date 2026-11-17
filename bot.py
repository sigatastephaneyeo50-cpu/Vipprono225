import html
import os
import sys
from datetime import datetime, timezone

import requests

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
# Clé API-Football (api-sports.io)
API_KEY = os.environ.get("API_FOOTBALL_KEY") or os.environ.get("FOOTBALL_API_KEY")

API_URL = "https://v3.football.api-sports.io/fixtures"
TIMEOUT = 15

# Championnats suivis, par ordre de priorité (ids API-Football).
# Modifiable sans toucher au code : LEAGUES="2,39,140" python bot.py
DEFAULT_LEAGUES = [
    2,    # Ligue des champions
    39,   # Premier League
    140,  # Liga
    135,  # Serie A
    78,   # Bundesliga
    61,   # Ligue 1
    94,   # Primeira Liga
    88,   # Eredivisie
    1,    # Coupe du monde
    4,    # Championnat d'Europe
    6,    # Coupe d'Afrique des nations
    5,    # Ligue des nations UEFA
    29,   # Qualifications Coupe du monde - Afrique
    32,   # Qualifications Coupe du monde - Europe
    36,   # Qualifications CAN
    960,  # Qualifications Euro
    10,   # Matchs amicaux internationaux
]
_env_leagues = os.environ.get("LEAGUES", "")
LEAGUES = (
    [int(x) for x in _env_leagues.split(",") if x.strip().isdigit()]
    if _env_leagues else DEFAULT_LEAGUES
)

NOT_PLAYED = {"PST", "CANC", "SUSP", "INT", "ABD", "AWD", "WO"}
FINISHED = {"FT", "AET", "PEN"}

FOOTER = (
    "<b>📌 BOOKMAKER : Paripesa</b>\n"
    "<b>🎁 CODE PROMO : POSSIBLE06</b>\n"
    "🔗 https://paripesa.bet/possible06\n"
    "<i>(lien d'affiliation)</i>\n\n"
    "🔞 Réservé aux majeurs. Les paris comportent des risques : "
    "ne jouez que ce que vous pouvez perdre."
)

# Chaque sélection : (ticket, libellé, test).
# Le test reçoit (buts domicile, buts extérieur) sur 90 minutes et renvoie
# True (gagné), False (perdu) ou None (remboursé).
PICKS = [
    ("safe", "Handicap (+1) {away}",
     lambda h, a: True if a + 1 > h else (None if a + 1 == h else False)),
    ("safe", "Plus de 1,5 buts dans le match",
     lambda h, a: h + a >= 2),
    ("fun", "Les deux équipes marquent & plus de 2,5 buts",
     lambda h, a: h > 0 and a > 0 and h + a >= 3),
    ("fun", "Handicap (-1,5) {home}",
     lambda h, a: h - a >= 2),
]


def esc(text):
    return html.escape(str(text))


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text, "parse_mode": "HTML"}
    try:
        response = requests.post(url, json=payload, timeout=TIMEOUT)
        print("STATUT HTTP :", response.status_code)
        if not response.ok:
            print("Erreur Telegram :", response.text)
        return response.ok
    except requests.RequestException as e:
        print("Erreur d'envoi Telegram :", e)
        return False


def fetch_today_matches():
    """Matchs du jour (UTC) dans les compétitions suivies, classés par
    priorité de compétition puis par heure de coup d'envoi.
    Un seul appel API par exécution."""
    if not API_KEY:
        print("Erreur : API_FOOTBALL_KEY n'est pas configurée.")
        return []

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    headers = {"x-apisports-key": API_KEY}
    params = {"date": today_str, "timezone": "UTC"}

    try:
        response = requests.get(API_URL, headers=headers, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as e:
        print("Erreur lors de la récupération des matchs :", e)
        return []

    # L'API peut répondre 200 avec une erreur (quota, plan, clé invalide...)
    if data.get("errors"):
        print("Erreur API-Football :", data["errors"])
        return []

    matches = []
    for item in data.get("response", []):
        league_id = item.get("league", {}).get("id")
        status = item.get("fixture", {}).get("status", {}).get("short", "")
        home = item.get("teams", {}).get("home", {}).get("name")
        away = item.get("teams", {}).get("away", {}).get("name")
        if league_id not in LEAGUES or status in NOT_PLAYED or not home or not away:
            continue
        full = item.get("score", {}).get("fulltime", {})
        matches.append({
            "id": item["fixture"]["id"],
            "utc": item["fixture"].get("date", ""),
            "status": status,
            "home": home,
            "away": away,
            "league_id": league_id,
            "competition": item["league"].get("name", ""),
            "goals_home": full.get("home"),
            "goals_away": full.get("away"),
        })

    matches.sort(key=lambda m: (LEAGUES.index(m["league_id"]), m["utc"], m["id"]))

    print(f"Matchs trouvés pour {today_str} : {len(matches)}")
    for m in matches:
        print(" -", m["competition"], ":", m["home"], "vs", m["away"])
    return matches


def assign_picks(matches):
    """Un match distinct par sélection. Même résultat le matin et le soir."""
    assigned = []
    for m, (ticket, label, test) in zip(matches, PICKS):
        assigned.append({
            **m,
            "ticket": ticket,
            "kickoff": m["utc"][11:16],
            "label": label.format(home=m["home"], away=m["away"]),
            "test": test,
        })
    return assigned


def format_ticket(title, legs):
    msg = f"<b>🔥 VIP PRONOS 225</b>\n\n<b>{title}</b>\n\n"
    for leg in legs:
        msg += (
            f"🏆 <i>{esc(leg['competition'])}</i> • ⏰ {esc(leg['kickoff'])} GMT\n"
            f"📌 <b>{esc(leg['home'])} vs {esc(leg['away'])}</b>\n"
            f"• Option : {esc(leg['label'])}\n\n"
        )
    return msg + FOOTER


def run_morning_predictions():
    matches = fetch_today_matches()
    if not matches:
        print("Aucun match dans les compétitions suivies aujourd'hui : rien n'est envoyé.")
        return

    legs = assign_picks(matches)
    safe = [l for l in legs if l["ticket"] == "safe"]
    fun = [l for l in legs if l["ticket"] == "fun"]

    if safe:
        send_telegram_message(format_ticket("🛡️ TICKET SAFE DU JOUR", safe))
    if fun:
        send_telegram_message(format_ticket("🚀 TICKET FUN DU JOUR", fun))
    print("Tickets du jour envoyés.")


def run_evening_results():
    legs = assign_picks(fetch_today_matches())
    if not legs:
        print("Aucun pronostic à vérifier aujourd'hui : rien n'est envoyé.")
        return

    summary = "<b>📊 BILAN DES RÉSULTATS DU JOUR</b>\n\n"
    won = lost = 0

    for leg in legs:
        h, a = leg["goals_home"], leg["goals_away"]
        line = (
            f"🏆 <i>{esc(leg['competition'])}</i>\n"
            f"⚽ <b>{esc(leg['home'])} vs {esc(leg['away'])}</b>\n"
            f"• {esc(leg['label'])} : "
        )

        if leg["status"] in FINISHED and h is not None and a is not None:
            result = leg["test"](h, a)
            if result is True:
                icon, won = "✅ Gagné", won + 1
            elif result is False:
                icon, lost = "❌ Perdu", lost + 1
            else:
                icon = "↩️ Remboursé"
            summary += f"{line}{h} - {a} ➡️ {icon}\n\n"
        else:
            summary += f"{line}en attente ⏳\n\n"

    summary += f"<b>Total : {won} gagné(s), {lost} perdu(s)</b>"
    send_telegram_message(summary)
    print("Bilan du soir envoyé.")


if __name__ == "__main__":
    if not TOKEN or not CHANNEL_ID:
        print("Erreur : les secrets Telegram ne sont pas configurés.")
        sys.exit(1)

    mode = sys.argv[1] if len(sys.argv) > 1 else "morning"
    if mode == "evening":
        run_evening_results()
    else:
        run_morning_predictions()