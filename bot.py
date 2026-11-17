import html
import os
import sys
from datetime import datetime, timezone

import requests

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
FOOTBALL_API_KEY = os.environ.get("FOOTBALL_API_KEY")

API_URL = "https://api.football-data.org/v4/matches"
TIMEOUT = 15
EXCLUDED_STATUS = {"POSTPONED", "CANCELLED", "SUSPENDED"}

FOOTER = (
    "<b>📌 BOOKMAKER : Paripesa</b>\n"
    "<b>🎁 CODE PROMO : POSSIBLE06</b>\n"
    "🔗 https://paripesa.bet/possible06\n"
    "<i>(lien d'affiliation)</i>\n\n"
    "🔞 Réservé aux majeurs. Les paris comportent des risques : "
    "ne jouez que ce que vous pouvez perdre."
)

# Chaque sélection : (ticket, libellé, test).
# Le test reçoit (buts domicile, buts extérieur) et renvoie
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
    """Matchs du jour (UTC), triés par id pour un ordre identique matin/soir."""
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    headers = {"X-Auth-Token": FOOTBALL_API_KEY} if FOOTBALL_API_KEY else {}
    params = {"dateFrom": today_str, "dateTo": today_str}

    try:
        response = requests.get(API_URL, headers=headers, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        matches = response.json().get("matches", [])
    except (requests.RequestException, ValueError) as e:
        print("Erreur lors de la récupération des matchs :", e)
        return []

    today_matches = [
        m for m in matches
        if m.get("utcDate", "").startswith(today_str)
        and m.get("status") not in EXCLUDED_STATUS
        and m.get("homeTeam", {}).get("name")
        and m.get("awayTeam", {}).get("name")
    ]
    today_matches.sort(key=lambda m: m.get("id", 0))
    print(f"Matchs trouvés pour {today_str} : {len(today_matches)}")
    return today_matches


def assign_picks(matches):
    """Un match distinct par sélection. Même résultat le matin et le soir."""
    assigned = []
    for match, (ticket, label, test) in zip(matches, PICKS):
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]
        assigned.append({
            "ticket": ticket,
            "match": match,
            "home": home,
            "away": away,
            "label": label.format(home=home, away=away),
            "test": test,
        })
    return assigned


def format_ticket(title, legs):
    msg = f"<b>🔥 VIP PRONOS 225</b>\n\n<b>{title}</b>\n\n"
    for leg in legs:
        msg += (
            f"📌 <b>{esc(leg['home'])} vs {esc(leg['away'])}</b>\n"
            f"• Option : {esc(leg['label'])}\n\n"
        )
    return msg + FOOTER


def run_morning_predictions():
    matches = fetch_today_matches()
    if not matches:
        print("Aucun match aujourd'hui : rien n'est envoyé.")
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
    matches = fetch_today_matches()
    legs = assign_picks(matches)
    if not legs:
        print("Aucun pronostic à vérifier aujourd'hui : rien n'est envoyé.")
        return

    summary = "<b>📊 BILAN DES RÉSULTATS DU JOUR</b>\n\n"
    won = lost = 0

    for leg in legs:
        m = leg["match"]
        score = m.get("score", {}).get("fullTime", {})
        h, a = score.get("home"), score.get("away")
        line = f"⚽ <b>{esc(leg['home'])} vs {esc(leg['away'])}</b>\n• {esc(leg['label'])} : "

        if m.get("status") == "FINISHED" and h is not None and a is not None:
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