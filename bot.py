import html
import json
import os
import sys
from datetime import datetime, timezone

import requests

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
API_KEY = os.environ.get("API_FOOTBALL_KEY") or os.environ.get("FOOTBALL_API_KEY")

BASE_URL = "https://v3.football.api-sports.io"
TIMEOUT = 15
PREDICTIONS_FILE = "predictions.json"

# Cote totale minimale visée par ticket (modifiable via variables d'environnement)
SAFE_MIN_ODDS = float(os.environ.get("SAFE_MIN_ODDS", "2.0"))
FUN_MIN_ODDS = float(os.environ.get("FUN_MIN_ODDS", "5.0"))
MAX_LEGS = 4              # matchs maximum par ticket
MAX_MATCHES_FOR_ODDS = 8  # 1 appel API par match pour les cotes

# Championnats suivis, par ordre de priorité (ids API-Football).
# Modifiable : LEAGUES="2,39,140" python bot.py
DEFAULT_LEAGUES = [
    2, 39, 140, 135, 78, 61, 94, 88,   # LDC, PL, Liga, Serie A, Bundesliga, L1, Primeira, Eredivisie
    1, 4, 6, 5,                        # Coupe du monde, Euro, CAN, Ligue des nations
    29, 32, 36, 960,                   # Qualifications (CdM Afrique/Europe, CAN, Euro)
    10,                                # Amicaux internationaux
]
_env = os.environ.get("LEAGUES", "")
LEAGUES = [int(x) for x in _env.split(",") if x.strip().isdigit()] if _env else DEFAULT_LEAGUES

NOT_PLAYED = {"PST", "CANC", "SUSP", "INT", "ABD", "AWD", "WO"}
UPCOMING = {"NS", "TBD"}
FINISHED = {"FT", "AET", "PEN"}

# Marchés de cotes utilisés (ids des paris API-Football) -> code interne
BET_MAP = {
    1: {"Home": "1", "Away": "2"},                                   # Match Winner
    12: {"Home/Draw": "1X", "Draw/Away": "X2"},                      # Double Chance
    5: {"Over 1.5": "O1.5", "Over 2.5": "O2.5"},                     # Goals Over/Under
    8: {"Yes": "BTTS"},                                              # Both Teams Score
}

LABELS = {
    "1": "Victoire {home}",
    "2": "Victoire {away}",
    "1X": "{home} ou match nul",
    "X2": "{away} ou match nul",
    "O1.5": "Plus de 1,5 buts",
    "O2.5": "Plus de 2,5 buts",
    "BTTS": "Les deux équipes marquent",
}

# Test de réussite sur le score à 90 minutes (h = domicile, a = extérieur)
TESTS = {
    "1": lambda h, a: h > a,
    "2": lambda h, a: a > h,
    "1X": lambda h, a: h >= a,
    "X2": lambda h, a: a >= h,
    "O1.5": lambda h, a: h + a >= 2,
    "O2.5": lambda h, a: h + a >= 3,
    "BTTS": lambda h, a: h > 0 and a > 0,
}

# Profil des tickets : marchés autorisés, plage de cotes par match, cote cible par match
SAFE = {"codes": ["1X", "X2", "O1.5", "1", "2"], "lo": 1.15, "hi": 1.70, "target": 1.45}
FUN = {"codes": ["1", "2", "BTTS", "O2.5"], "lo": 1.60, "hi": 3.50, "target": 2.10}

FOOTER = (
    "<i>Cotes indicatives : elles peuvent varier selon le bookmaker.</i>\n\n"
    "<b>📌 BOOKMAKER : Paripesa</b>\n"
    "<b>🎁 CODE PROMO : POSSIBLE06</b>\n"
    "🔗 https://paripesa.bet/possible06\n"
    "<i>(lien d'affiliation)</i>\n\n"
    "🔞 Réservé aux majeurs. Les paris comportent des risques : "
    "ne jouez que ce que vous pouvez perdre."
)


def esc(text):
    return html.escape(str(text))


def today_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


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


def api_get(path, params):
    """Appel API-Football. Renvoie le JSON, ou None en cas d'erreur."""
    if not API_KEY:
        print("Erreur : API_FOOTBALL_KEY n'est pas configurée.")
        return None
    try:
        response = requests.get(
            f"{BASE_URL}/{path}", headers={"x-apisports-key": API_KEY},
            params=params, timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as e:
        print(f"Erreur API ({path}) :", e)
        return None
    if data.get("errors"):
        print(f"Erreur API-Football ({path}) :", data["errors"])
        return None
    return data


def fetch_today_matches():
    """Matchs du jour dans les compétitions suivies, par priorité puis heure."""
    data = api_get("fixtures", {"date": today_utc(), "timezone": "UTC"})
    if not data:
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
    print(f"Matchs trouvés pour {today_utc()} : {len(matches)}")
    return matches


def fetch_odds(fixture_id):
    """Cotes avant-match d'un match : {code_marché: cote}. Vide si indisponibles."""
    data = api_get("odds", {"fixture": fixture_id})
    if not data or not data.get("response"):
        return {}
    markets = {}
    for bookmaker in data["response"][0].get("bookmakers", []):
        for bet in bookmaker.get("bets", []):
            mapping = BET_MAP.get(bet.get("id"))
            if not mapping:
                continue
            for v in bet.get("values", []):
                code = mapping.get(v.get("value"))
                if code and code not in markets:
                    try:
                        markets[code] = float(v["odd"])
                    except (KeyError, TypeError, ValueError):
                        pass
    return markets


def build_ticket(pool, profile, min_total, used_ids):
    """Ajoute un match à la fois (un marché par match) jusqu'à atteindre la
    cote totale visée. Renvoie (legs, cote_totale) ou (None, 0)."""
    legs, total = [], 1.0
    for m in pool:
        if m["id"] in used_ids:
            continue
        options = [
            (code, odd) for code, odd in m["odds"].items()
            if code in profile["codes"] and profile["lo"] <= odd <= profile["hi"]
        ]
        if not options:
            continue
        code, odd = min(options, key=lambda o: abs(o[1] - profile["target"]))
        legs.append({
            "fixture_id": m["id"],
            "home": m["home"],
            "away": m["away"],
            "competition": m["competition"],
            "kickoff": m["utc"][11:16],
            "market": code,
            "label": LABELS[code].format(home=m["home"], away=m["away"]),
            "odd": odd,
        })
        total *= odd
        if total >= min_total:
            return legs, total
        if len(legs) >= MAX_LEGS:
            break
    return None, 0


def format_ticket(title, legs, total):
    msg = f"<b>🔥 VIP PRONOS 225</b>\n\n<b>{title}</b>\n\n"
    for leg in legs:
        msg += (
            f"🏆 <i>{esc(leg['competition'])}</i> • ⏰ {esc(leg['kickoff'])} GMT\n"
            f"📌 <b>{esc(leg['home'])} vs {esc(leg['away'])}</b>\n"
            f"• {esc(leg['label'])} (cote {leg['odd']:.2f})\n\n"
        )
    msg += f"💰 <b>Cote totale : {total:.2f}</b>\n\n"
    return msg + FOOTER


def save_predictions(tickets):
    with open(PREDICTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump({"date": today_utc(), "tickets": tickets}, f, ensure_ascii=False, indent=2)


def run_morning_predictions():
    matches = [m for m in fetch_today_matches() if m["status"] in UPCOMING]
    pool = matches[:MAX_MATCHES_FOR_ODDS]
    for m in pool:
        m["odds"] = fetch_odds(m["id"])
        print(f" - {m['home']} vs {m['away']} : cotes {m['odds'] or 'indisponibles'}")

    saved, used = [], set()
    for key, title, profile, min_total in [
        ("safe", "🛡️ TICKET SAFE DU JOUR", SAFE, SAFE_MIN_ODDS),
        ("fun", "🚀 TICKET FUN DU JOUR", FUN, FUN_MIN_ODDS),
    ]:
        legs, total = build_ticket(pool, profile, min_total, used)
        if not legs:
            print(f"Ticket {key} : impossible d'atteindre la cote {min_total} avec les matchs du jour.")
            continue
        used.update(l["fixture_id"] for l in legs)
        saved.append({"name": key, "title": title, "total": total, "legs": legs})
        send_telegram_message(format_ticket(title, legs, total))

    save_predictions(saved)
    print(f"{len(saved)} ticket(s) envoyé(s).")


def run_evening_results():
    try:
        with open(PREDICTIONS_FILE, encoding="utf-8") as f:
            saved = json.load(f)
    except (OSError, ValueError):
        print("Aucun fichier de pronostics trouvé : rien à vérifier.")
        return
    if saved.get("date") != today_utc() or not saved.get("tickets"):
        print("Pas de pronostics enregistrés pour aujourd'hui : rien n'est envoyé.")
        return

    results = {m["id"]: m for m in fetch_today_matches()}
    summary = "<b>📊 BILAN DES RÉSULTATS DU JOUR</b>\n\n"
    won_tickets = lost_tickets = 0

    for ticket in saved["tickets"]:
        summary += f"<b>{ticket['title']}</b> (cote {ticket['total']:.2f})\n"
        all_won, any_lost = True, False
        for leg in ticket["legs"]:
            m = results.get(leg["fixture_id"])
            line = f"⚽ {esc(leg['home'])} vs {esc(leg['away'])} • {esc(leg['label'])} : "
            h, a = (m["goals_home"], m["goals_away"]) if m else (None, None)
            if m and m["status"] in FINISHED and h is not None and a is not None:
                ok = TESTS[leg["market"]](h, a)
                summary += f"{line}{h}-{a} {'✅' if ok else '❌'}\n"
                all_won &= ok
                any_lost |= not ok
            else:
                summary += f"{line}en attente ⏳\n"
                all_won = False
        if any_lost:
            summary += "➡️ <b>Ticket perdu ❌</b>\n\n"
            lost_tickets += 1
        elif all_won:
            summary += "➡️ <b>Ticket gagné ✅</b>\n\n"
            won_tickets += 1
        else:
            summary += "➡️ <b>En cours ⏳</b>\n\n"

    summary += f"<b>Total : {won_tickets} ticket(s) gagné(s), {lost_tickets} perdu(s)</b>"
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