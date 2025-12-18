import requests
import json
import time
import os
import sys
from datetime import datetime, timedelta, timezone

# Get the project root directory (parent of scripts folder)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

# Sport configuration
SPORT_CONFIG = {
    "nfl": {
        "series_ticker": "KXNFLGAME",
        "sport_name": "NFL",
        "content_type": "nfl_winner_markets",
        "keywords": ["nfl", "football"],
    },
    "mlb": {
        "series_ticker": "KXMLBGAME",
        "sport_name": "MLB",
        "content_type": "mlb_winner_markets",
        "keywords": ["mlb", "baseball"],
    },
    "nba": {
        "series_ticker": "KXNBAGAME",
        "sport_name": "NBA",
        "content_type": "nba_winner_markets",
        "keywords": ["nba", "basketball"],
    },
    "ncaab": {
        "series_ticker": "KXNCAAMBGAME",
        "sport_name": "NCAAB",
        "content_type": "ncaab_winner_markets",
        "keywords": ["ncaab", "college basketball", "college-basketball"],
    },
    "ncaaf": {
        "series_ticker": "KXNCAAFGAME",
        "sport_name": "NCAAF",
        "content_type": "ncaaf_winner_markets",
        "keywords": ["ncaaf", "college football", "college-football"],
    },
    "ufc": {
        "series_ticker": "KXUFCFIGHT",
        "sport_name": "UFC",
        "content_type": "ufc_winner_markets",
        "keywords": ["ufc", "mma"],
    },
    "nhl": {
        "series_ticker": "KXNHLGAME",
        "sport_name": "NHL",
        "content_type": "nhl_winner_markets",
        "keywords": ["nhl", "hockey", "ice hockey"],
    },
    "mls": {
        "series_ticker": "KXMLSGAME",
        "sport_name": "MLS",
        "content_type": "mls_winner_markets",
        "keywords": ["mls", "soccer", "football"],
    },
    "ncaabw": {
        "series_ticker": "KXNCAAWBGAME",
        "sport_name": "NCAABW",
        "content_type": "ncaabw_winner_markets",
        "keywords": ["ncaaw", "women's college basketball", "womens basketball", "college basketball women"],
    },
}

def get_paginated(path, params=None, list_key=None, limit=200):
    """
    Cursor-paginates Kalshi list endpoints.
    """
    params = dict(params or {})
    params["limit"] = min(limit, 200)
    out = []
    cursor = None

    while True:
        p = dict(params)
        if cursor:
            p["cursor"] = cursor
        try:
            r = requests.get(f"{BASE_URL}{path}", params=p, timeout=30)
            r.raise_for_status()
            data = r.json()

            items = data.get(list_key) or []
            if not isinstance(items, list):
                items = []
            out.extend(items)

            cursor = data.get("cursor")
            if not cursor:
                break
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {path}: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

    return out

def parse_iso8601(ts: str) -> datetime:
    # Kalshi returns timestamps like "2023-11-07T05:31:56Z"
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts)

def find_sport_series(sport: str):
    """
    Find the game series for the specified sport.
    """
    if sport not in SPORT_CONFIG:
        raise ValueError(f"Unsupported sport: {sport}. Supported: {list(SPORT_CONFIG.keys())}")
    
    config = SPORT_CONFIG[sport]
    series_ticker = config["series_ticker"]
    keywords = config["keywords"]
    
    # Get all Sports series
    series = get_paginated("/series", params={"category": "Sports"}, list_key="series", limit=200)
    
    print(f"Found {len(series)} total Sports series")

    # Filter to sport-specific series
    sport_series = []
    for s in series:
        title = (s.get("title") or "").lower()
        ticker = (s.get("ticker") or "").lower()
        tags = [t.lower() for t in (s.get("tags") or [])]
        
        # Check if matches sport keywords
        if any(keyword in title or keyword in ticker or any(keyword in t for t in tags) for keyword in keywords):
            sport_series.append(s)

    print(f"Found {len(sport_series)} {config['sport_name']}-related series")
    
    # Filter to the game series (winner markets)
    game_series = [s for s in sport_series if s.get("ticker", "").upper() == series_ticker]
    if game_series:
        print(f"Found {series_ticker} series - focusing on winner markets only")
        return game_series
    
    # Fallback to all sport series if game series not found
    return sport_series

def get_markets_for_series(series_ticker: str, status: str):
    try:
        result = get_paginated(
            "/markets",
            params={"series_ticker": series_ticker, "status": status},
            list_key="markets",
            limit=200,
        )
        return result or []
    except Exception as e:
        print(f"  Warning: Failed to get {status} markets for {series_ticker}: {e}")
        return []

def has_upcoming_markets(series_ticker: str, now: datetime, week_end: datetime):
    """
    Quickly check if a series has any markets closing in the next week.
    """
    try:
        for status in ("open", "unopened"):
            markets = get_markets_for_series(series_ticker, status)
            for m in markets:
                exp_time = m.get("expected_expiration_time") or m.get("expiration_time") or m.get("close_time")
                if exp_time:
                    try:
                        et = parse_iso8601(exp_time)
                        if now <= et <= week_end:
                            return True
                    except:
                        continue
        return False
    except:
        return False

def is_winner_market(market, sport: str):
    """
    Check if a market is exclusively about which team will win/lose a game.
    """
    title = market.get("title") or ""
    title_lower = title.lower()
    event_ticker = (market.get("event_ticker") or "").upper()
    
    config = SPORT_CONFIG[sport]
    series_ticker = config["series_ticker"]
    
    # Must be from the game series
    if not event_ticker.startswith(series_ticker):
        return False
    
    # Must be a winner market (ends with "Winner?")
    if not title.endswith("Winner?") or "winner" not in title_lower:
        return False
    
    # Exclude player-related keywords
    player_keywords = [
        "player", "scorer", "touchdown", "reception", "passing", "rushing",
        "receiving", "yards", "completion", "interception", "fumble", "sack",
        "home run", "rbi", "strikeout", "hits", "points", "rebounds", "assists"
    ]
    if any(keyword in title_lower for keyword in player_keywords):
        return False
    
    # Exclude score/total markets
    score_keywords = [
        "total", "over", "under", "points", "score", "combined", "sum", "runs"
    ]
    if any(keyword in title_lower for keyword in score_keywords):
        return False
    
    # Must have team names (indicated by "at" or "vs")
    if " at " not in title and " vs " not in title and " @ " not in title:
        return False
    
    return True

def main():
    # Get sport from command line argument
    if len(sys.argv) < 2:
        print("Usage: python fetch_kalshi_sports.py <sport>")
        print(f"Supported sports: {', '.join(SPORT_CONFIG.keys())}")
        sys.exit(1)
    
    sport = sys.argv[1].lower()
    if sport not in SPORT_CONFIG:
        print(f"Error: Unsupported sport '{sport}'")
        print(f"Supported sports: {', '.join(SPORT_CONFIG.keys())}")
        sys.exit(1)
    
    config = SPORT_CONFIG[sport]
    
    now = datetime.now(timezone.utc)
    # Fetch data for the next 7 days (aligned with The Odds API's typical 24-48 hour window)
    week_end = now + timedelta(days=7)

    sport_series = find_sport_series(sport)
    if not sport_series:
        print(f"No {config['sport_name']} series found.")
        return

    # Filter to only series with upcoming markets in the next 7 days
    print(f"\nFiltering {len(sport_series)} {config['sport_name']} series to those with games in the next 7 days...")
    upcoming_series = []
    for idx, s in enumerate(sport_series, 1):
        st = s.get("ticker")
        series_title = s.get("title", "Unknown")
        if not st:
            continue
        
        print(f"  [{idx}/{len(sport_series)}] Checking: {series_title[:50]}...", end=" ", flush=True)
        if has_upcoming_markets(st, now, week_end):
            upcoming_series.append(s)
            print("Has upcoming markets")
        else:
            print("No upcoming markets")
        
        time.sleep(0.1)
    
    print(f"\nFound {len(upcoming_series)} {config['sport_name']} series with games in the next 7 days")
    
    if not upcoming_series:
        print(f"No {config['sport_name']} series found with games closing in the next 7 days.")
        output_data = {
            "source": "kalshi",
            "content_type": config["content_type"],
            "query_time": now.isoformat(),
            "query_window_end": week_end.isoformat(),
            "total_markets_found": 0,
            "markets": []
        }
        output_file = os.path.join(DATA_DIR, f"kalshi_{config['content_type']}.json")
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"Empty output saved to {output_file}")
        return

    all_markets = []
    seen = set()

    print(f"\nFetching markets for {len(upcoming_series)} relevant {config['sport_name']} series...")
    for idx, s in enumerate(upcoming_series, 1):
        st = s.get("ticker")
        series_title = s.get("title", "Unknown")
        if not st:
            continue
        
        print(f"  [{idx}/{len(upcoming_series)}] Processing: {series_title[:50]}...", end=" ", flush=True)
        markets_count = 0
        
        for status in ("open", "unopened"):
            markets = get_markets_for_series(st, status=status)
            if not markets:
                continue
            for m in markets:
                tkr = m.get("ticker")
                if tkr and tkr not in seen:
                    seen.add(tkr)
                    all_markets.append(m)
                    markets_count += 1
        
        print(f"Found {markets_count} new markets (total: {len(all_markets)})")
        time.sleep(0.1)
    
    print(f"\nTotal unique markets collected: {len(all_markets)}")

    # Filter to markets expiring in next 7 days AND are winner markets only
    upcoming = []
    for m in all_markets:
        exp_time = m.get("expected_expiration_time") or m.get("expiration_time") or m.get("close_time")
        if not exp_time:
            continue
        try:
            et = parse_iso8601(exp_time)
            if now <= et <= week_end:
                if is_winner_market(m, sport):
                    upcoming.append((et, m))
        except Exception as e:
            continue

    upcoming.sort(key=lambda x: x[0])

    print(f"Found {len(upcoming)} {config['sport_name']} winner markets (team win/lose only) expiring between {now.isoformat()} and {week_end.isoformat()}:\n")
    for et, m in upcoming:
        print(f"{et.isoformat()}  {m.get('ticker')}  |  {m.get('title')}")

    # Prepare JSON output
    output_data = {
        "source": "kalshi",
        "content_type": config["content_type"],
        "sport": sport,
        "query_time": now.isoformat(),
        "query_window_end": week_end.isoformat(),
        "total_markets_found": len(upcoming),
        "markets": [
            {
                "expiration_time": et.isoformat(),
                "ticker": m.get("ticker"),
                "title": m.get("title"),
                "event_ticker": m.get("event_ticker"),
                "market_data": m
            }
            for et, m in upcoming
        ]
    }

    # Write to JSON file
    output_file = os.path.join(DATA_DIR, f"kalshi_{config['content_type']}.json")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nOutput saved to {output_file}")

if __name__ == "__main__":
    main()

