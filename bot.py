import os
import time
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

SPORT = "soccer_epl"
REGIONS = "eu"
MARKETS = "h2h,totals"
DROP_PERCENT = 10

previous_odds = {}

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_odds():
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": REGIONS,
        "markets": MARKETS,
        "oddsFormat": "decimal"
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

send("✅ Odds bot started successfully.")

while True:
    try:
        matches = get_odds()

        for match in matches:
            home = match["home_team"]
            away = match["away_team"]
            match_name = f"{home} vs {away}"

            for bookmaker in match.get("bookmakers", []):
                bookie = bookmaker["title"]

                for market in bookmaker.get("markets", []):
                    market_name = market["key"]

                    for outcome in market.get("outcomes", []):
                        pick = outcome["name"]
                        new_odd = float(outcome["price"])

                        key = f"{match_name}-{bookie}-{market_name}-{pick}"

                        if key in previous_odds:
                            old_odd = previous_odds[key]

                            if old_odd > new_odd:
                                drop = ((old_odd - new_odd) / old_odd) * 100

                                if drop >= DROP_PERCENT:
                                    msg = f"""🚨 ODDS DROP ALERT

⚽ {match_name}
🏦 {bookie}
🎯 Market: {market_name}
✅ Pick: {pick}

📉 Old Odds: {old_odd}
🔥 New Odds: {new_odd}
📊 Drop: {drop:.2f}%"""
                                    send(msg)

                        previous_odds[key] = new_odd

        time.sleep(60)

    except Exception as e:
        send(f"⚠️ Bot error: {e}")
        time.sleep(60)
