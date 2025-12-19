import requests
import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

# Get the project root directory (parent of scripts folder)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# The Odds API configuration
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"
# TODO: Remove hardcoded API key before production/deployment
ODDS_API_KEY = os.getenv("ODDS_API_KEY") or "d77d2e63a1e5fb8832317d1058c996a1"

# Sport configuration
SPORT_CONFIG = {
    "nfl": {
        "odds_api_key": "americanfootball_nfl",
        "sport_name": "NFL",
        "content_type": "nfl_moneyline_odds",
        "kalshi_file": "kalshi_nfl_winner_markets.json",
    },
    "mlb": {
        "odds_api_key": "baseball_mlb",
        "sport_name": "MLB",
        "content_type": "mlb_moneyline_odds",
        "kalshi_file": "kalshi_mlb_winner_markets.json",
    },
    "nba": {
        "odds_api_key": "basketball_nba",
        "sport_name": "NBA",
        "content_type": "nba_moneyline_odds",
        "kalshi_file": "kalshi_nba_winner_markets.json",
    },
    "ncaab": {
        "odds_api_key": "basketball_ncaab",
        "sport_name": "NCAAB",
        "content_type": "ncaab_moneyline_odds",
        "kalshi_file": "kalshi_ncaab_winner_markets.json",
    },
    "ncaaf": {
        "odds_api_key": "americanfootball_ncaaf",
        "sport_name": "NCAAF",
        "content_type": "ncaaf_moneyline_odds",
        "kalshi_file": "kalshi_ncaaf_winner_markets.json",
    },
    "ufc": {
        "odds_api_key": "mma_ufc",
        "sport_name": "UFC",
        "content_type": "ufc_moneyline_odds",
        "kalshi_file": "kalshi_ufc_winner_markets.json",
    },
    "nhl": {
        "odds_api_key": "icehockey_nhl",
        "sport_name": "NHL",
        "content_type": "nhl_moneyline_odds",
        "kalshi_file": "kalshi_nhl_winner_markets.json",
    },
    "mls": {
        "odds_api_key": "soccer_usa_mls",
        "sport_name": "MLS",
        "content_type": "mls_moneyline_odds",
        "kalshi_file": "kalshi_mls_winner_markets.json",
    },
    "ncaabw": {
        "odds_api_key": "basketball_ncaaw",
        "sport_name": "NCAABW",
        "content_type": "ncaabw_moneyline_odds",
        "kalshi_file": "kalshi_ncaabw_winner_markets.json",
    },
}

# Team name mappings (will need to expand for MLB and NBA)
TEAM_NAME_MAPPING = {
    # NFL teams (existing)
    "Arizona": "Arizona Cardinals",
    "Atlanta": "Atlanta Falcons",
    "Baltimore": "Baltimore Ravens",
    "Buffalo": "Buffalo Bills",
    "Carolina": "Carolina Panthers",
    "Chicago": "Chicago Bears",
    "Cincinnati": "Cincinnati Bengals",
    "Cleveland": "Cleveland Browns",
    "Dallas": "Dallas Cowboys",
    "Denver": "Denver Broncos",
    "Detroit": "Detroit Lions",
    "Green Bay": "Green Bay Packers",
    "Houston": "Houston Texans",
    "Indianapolis": "Indianapolis Colts",
    "Jacksonville": "Jacksonville Jaguars",
    "Kansas City": "Kansas City Chiefs",
    "Las Vegas": "Las Vegas Raiders",
    "Los Angeles C": "Los Angeles Chargers",
    "Los Angeles R": "Los Angeles Rams",
    "Miami": "Miami Dolphins",
    "Minnesota": "Minnesota Vikings",
    "New England": "New England Patriots",
    "New Orleans": "New Orleans Saints",
    "New York G": "New York Giants",
    "New York J": "New York Jets",
    "Philadelphia": "Philadelphia Eagles",
    "Pittsburgh": "Pittsburgh Steelers",
    "San Francisco": "San Francisco 49ers",
    "Seattle": "Seattle Seahawks",
    "Tampa Bay": "Tampa Bay Buccaneers",
    "Tennessee": "Tennessee Titans",
    "Washington": "Washington Commanders",
    # MLB teams (basic - will need expansion)
    "Arizona D": "Arizona Diamondbacks",
    "Atlanta B": "Atlanta Braves",
    "Baltimore O": "Baltimore Orioles",
    "Boston": "Boston Red Sox",
    "Chicago C": "Chicago Cubs",
    "Chicago W": "Chicago White Sox",
    "Cincinnati": "Cincinnati Reds",
    "Cleveland": "Cleveland Guardians",
    "Colorado": "Colorado Rockies",
    "Detroit": "Detroit Tigers",
    "Houston": "Houston Astros",
    "Kansas City": "Kansas City Royals",
    "Los Angeles A": "Los Angeles Angels",
    "Los Angeles D": "Los Angeles Dodgers",
    "Miami": "Miami Marlins",
    "Milwaukee": "Milwaukee Brewers",
    "Minnesota": "Minnesota Twins",
    "New York M": "New York Mets",
    "New York Y": "New York Yankees",
    "Oakland": "Oakland Athletics",
    "Philadelphia": "Philadelphia Phillies",
    "Pittsburgh": "Pittsburgh Pirates",
    "San Diego": "San Diego Padres",
    "San Francisco": "San Francisco Giants",
    "Seattle": "Seattle Mariners",
    "St. Louis": "St. Louis Cardinals",
    "Tampa Bay": "Tampa Bay Rays",
    "Texas": "Texas Rangers",
    "Toronto": "Toronto Blue Jays",
    "Washington": "Washington Nationals",
    # NBA teams (verified from actual Kalshi data)
    "Atlanta": "Atlanta Hawks",
    "Boston": "Boston Celtics",
    "Brooklyn": "Brooklyn Nets",
    "Charlotte": "Charlotte Hornets",
    "Chicago": "Chicago Bulls",
    "Cleveland": "Cleveland Cavaliers",
    "Dallas": "Dallas Mavericks",
    "Denver": "Denver Nuggets",
    "Detroit": "Detroit Pistons",
    "Golden State": "Golden State Warriors",
    "Houston": "Houston Rockets",
    "Indiana": "Indiana Pacers",
    "Los Angeles C": "LA Clippers",  # Note: Kalshi uses "Los Angeles C" for Clippers
    "Los Angeles L": "Los Angeles Lakers",
    "Memphis": "Memphis Grizzlies",
    "Miami": "Miami Heat",
    "Milwaukee": "Milwaukee Bucks",
    "Minnesota": "Minnesota Timberwolves",
    "New Orleans": "New Orleans Pelicans",
    "New York": "New York Knicks",  # Note: Kalshi uses "New York" (not "New York K")
    "Oklahoma City": "Oklahoma City Thunder",
    "Orlando": "Orlando Magic",
    "Philadelphia": "Philadelphia 76ers",
    "Phoenix": "Phoenix Suns",
    "Portland": "Portland Trail Blazers",
    "Sacramento": "Sacramento Kings",
    "San Antonio": "San Antonio Spurs",
    "Toronto": "Toronto Raptors",
    "Utah": "Utah Jazz",
    "Washington": "Washington Wizards",
}

def parse_kalshi_team_name(title: str, sport: str = None) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse Kalshi title format like "Los Angeles R at Seattle Winner?"
    Returns (away_team, home_team) or (None, None) if parsing fails.
    
    Args:
        title: Market title from Kalshi
        sport: Sport key (nfl, nba, mlb, ncaab, ncaaf, ufc) - if None, uses mapping
    """
    if not title.endswith("Winner?"):
        return None, None
    
    game_part = title.replace(" Winner?", "").strip()
    
    if " at " in game_part:
        parts = game_part.split(" at ", 1)
    elif " @ " in game_part:
        parts = game_part.split(" @ ", 1)
    elif " vs " in game_part:
        parts = game_part.split(" vs ", 1)
    else:
        return None, None
    
    if len(parts) != 2:
        return None, None
    
    away_team_kalshi = parts[0].strip()
    home_team_kalshi = parts[1].strip()
    
    # For college sports and UFC, don't use pro team mappings
    # They should match directly or with normalization
    if sport in ["ncaab", "ncaaf", "ufc"]:
        away_team = away_team_kalshi
        home_team = home_team_kalshi
    else:
        # For pro sports, use mapping
        away_team = TEAM_NAME_MAPPING.get(away_team_kalshi, away_team_kalshi)
        home_team = TEAM_NAME_MAPPING.get(home_team_kalshi, home_team_kalshi)
    
    return away_team, home_team

def load_kalshi_games(sport: str) -> List[Dict]:
    """
    Load Kalshi games from the JSON file.
    """
    config = SPORT_CONFIG[sport]
    kalshi_file = os.path.join(DATA_DIR, config["kalshi_file"])
    
    if not os.path.exists(kalshi_file):
        print(f"Warning: Kalshi data file not found at {kalshi_file}")
        return []
    
    with open(kalshi_file, "r", encoding="utf-8") as f:
        kalshi_data = json.load(f)
    
    games = {}
    
    for market in kalshi_data.get("markets", []):
        title = market.get("title", "")
        expiration_time = market.get("expiration_time")
        event_ticker = market.get("event_ticker", "")
        
        away_team, home_team = parse_kalshi_team_name(title, sport)
        
        if away_team and home_team:
            if event_ticker not in games:
                games[event_ticker] = {
                    "away_team": away_team,
                    "home_team": home_team,
                    "kalshi_title": title,
                    "event_ticker": event_ticker,
                    "expiration_time": expiration_time,
                }
    
    return list(games.values())

def fetch_odds_api_sports(sport: str, api_key: str) -> List[Dict]:
    """
    Fetch odds from The Odds API for the specified sport.
    """
    if not api_key:
        raise ValueError("ODDS_API_KEY environment variable not set. Please set it before running.")
    
    config = SPORT_CONFIG[sport]
    sport_key = config["odds_api_key"]
    
    url = f"{ODDS_API_BASE_URL}/sports/{sport_key}/odds"
    params = {
        "apiKey": api_key,
        "regions": "us",
        "markets": "h2h",
        "oddsFormat": "american",
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching odds from The Odds API: {e}")
        if hasattr(response, 'text'):
            print(f"Response: {response.text}")
        raise

def normalize_team_name(name: str) -> str:
    """Normalize team name for better matching (case-insensitive, remove common suffixes)."""
    name = name.strip()
    # Remove common suffixes that might differ
    suffixes = [" University", " Univ", " State", " St", " College", " Col"]
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    return name

def extract_team_names_from_odds(odds_game: Dict) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract team names from an Odds API game object.
    Tries direct fields first, then bookmaker outcomes.
    """
    # Method 1: Check direct fields
    home_team = odds_game.get("home_team")
    away_team = odds_game.get("away_team")
    if home_team and away_team:
        return away_team, home_team
    
    # Method 2: Extract from bookmaker outcomes
    bookmakers = odds_game.get("bookmakers", [])
    if not bookmakers:
        return None, None
    
    # Look through bookmakers for h2h market
    team_names = []
    for bookmaker in bookmakers:
        markets = bookmaker.get("markets", [])
        for market in markets:
            if market.get("key") == "h2h":
                outcomes = market.get("outcomes", [])
                for outcome in outcomes:
                    team_name = outcome.get("name")
                    if team_name and team_name not in team_names:
                        team_names.append(team_name)
                # If we found 2 teams, return them
                if len(team_names) >= 2:
                    return team_names[0], team_names[1]
    
    return None, None

def match_games_with_odds(kalshi_games: List[Dict], odds_data: List[Dict]) -> List[Dict]:
    """
    Match Kalshi games with The Odds API data.
    Uses flexible matching for college sports and UFC.
    """
    matched_games = []
    
    for kalshi_game in kalshi_games:
        away_team_kalshi = kalshi_game["away_team"]
        home_team_kalshi = kalshi_game["home_team"]
        
        # Normalize for matching
        away_kalshi_norm = normalize_team_name(away_team_kalshi).lower()
        home_kalshi_norm = normalize_team_name(home_team_kalshi).lower()
        
        matched_odds = None
        for odds_game in odds_data:
            # Extract team names (from direct fields or outcomes)
            away_team_odds, home_team_odds = extract_team_names_from_odds(odds_game)
            
            if not away_team_odds or not home_team_odds:
                continue
            
            # Normalize odds API names
            home_odds_norm = normalize_team_name(home_team_odds).lower()
            away_odds_norm = normalize_team_name(away_team_odds).lower()
            
            # Try exact match first
            if ((home_odds_norm == home_kalshi_norm and away_odds_norm == away_kalshi_norm) or
                (home_odds_norm == away_kalshi_norm and away_odds_norm == home_kalshi_norm)):
                matched_odds = odds_game
                break
            
            # Try partial match (for college teams with varying formats)
            if ((home_odds_norm in home_kalshi_norm or home_kalshi_norm in home_odds_norm) and
                (away_odds_norm in away_kalshi_norm or away_kalshi_norm in away_odds_norm)):
                matched_odds = odds_game
                break
            if ((home_odds_norm in away_kalshi_norm or away_kalshi_norm in home_odds_norm) and
                (away_odds_norm in home_kalshi_norm or home_kalshi_norm in away_odds_norm)):
                matched_odds = odds_game
                break
        
        if matched_odds:
            # Ensure team names are in the odds_data for later use
            away_team, home_team = extract_team_names_from_odds(matched_odds)
            if away_team and home_team:
                if not matched_odds.get("away_team"):
                    matched_odds["away_team"] = away_team
                if not matched_odds.get("home_team"):
                    matched_odds["home_team"] = home_team
            
            matched_games.append({
                "kalshi_data": kalshi_game,
                "odds_data": matched_odds,
                "matched": True,
            })
        else:
            matched_games.append({
                "kalshi_data": kalshi_game,
                "odds_data": None,
                "matched": False,
            })
    
    return matched_games

def main():
    """
    Main function to fetch sportsbook odds and match with Kalshi games.
    """
    if len(sys.argv) < 2:
        print("Usage: python fetch_odds_api_sports.py <sport>")
        print(f"Supported sports: {', '.join(SPORT_CONFIG.keys())}")
        sys.exit(1)
    
    sport = sys.argv[1].lower()
    if sport not in SPORT_CONFIG:
        print(f"Error: Unsupported sport '{sport}'")
        print(f"Supported sports: {', '.join(SPORT_CONFIG.keys())}")
        sys.exit(1)
    
    config = SPORT_CONFIG[sport]
    
    if not ODDS_API_KEY:
        print("ERROR: ODDS_API_KEY environment variable not set.")
        print("Please set it before running:")
        print("  Windows PowerShell: $env:ODDS_API_KEY='your_api_key_here'")
        print("  Windows CMD: set ODDS_API_KEY=your_api_key_here")
        print("  Linux/Mac: export ODDS_API_KEY='your_api_key_here'")
        print("\nGet your API key from: https://the-odds-api.com/")
        return
    
    print(f"Loading {config['sport_name']} games from Kalshi...")
    kalshi_games = load_kalshi_games(sport)
    print(f"Found {len(kalshi_games)} unique games from Kalshi data")
    
    if not kalshi_games:
        print(f"No {config['sport_name']} games found. Please run fetch_kalshi_sports.py {sport} first.")
        return
    
    print(f"\nFetching {config['sport_name']} odds from The Odds API...")
    try:
        raw_odds_data = fetch_odds_api_sports(sport, ODDS_API_KEY)
        print(f"Retrieved {len(raw_odds_data)} games from The Odds API")
        
        # Extract team names for games that don't have them at top level
        games_with_teams = 0
        for odds_game in raw_odds_data:
            away_team, home_team = extract_team_names_from_odds(odds_game)
            if away_team and home_team:
                # Add team names if they weren't at top level
                if not odds_game.get("away_team"):
                    odds_game["away_team"] = away_team
                if not odds_game.get("home_team"):
                    odds_game["home_team"] = home_team
                games_with_teams += 1
        
        print(f"Games with team data: {games_with_teams} out of {len(raw_odds_data)}")
        odds_data = raw_odds_data
    except Exception as e:
        print(f"Failed to fetch odds: {e}")
        return
    
    print("\nMatching games...")
    matched_games = match_games_with_odds(kalshi_games, odds_data)
    
    matched_count = sum(1 for g in matched_games if g["matched"])
    print(f"Matched {matched_count} out of {len(matched_games)} games")
    
    # Prepare output data
    output_data = {
        "source": "the_odds_api",
        "content_type": config["content_type"],
        "sport": sport,
        "query_time": datetime.now(timezone.utc).isoformat(),
        "kalshi_query_window_end": kalshi_games[0]["expiration_time"] if kalshi_games else None,
        "total_games": len(matched_games),
        "matched_games": matched_count,
        "games": matched_games,
    }
    
    # Write to JSON file
    output_file = os.path.join(DATA_DIR, f"the_odds_api_{config['content_type']}.json")
    os.makedirs(DATA_DIR, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nOutput saved to {output_file}")
    
    # Print summary
    if matched_count < len(matched_games):
        print("\nUnmatched games:")
        for game in matched_games:
            if not game["matched"]:
                kalshi = game["kalshi_data"]
                print(f"  {kalshi['away_team']} at {kalshi['home_team']}")

if __name__ == "__main__":
    main()

