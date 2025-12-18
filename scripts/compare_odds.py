import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)  # Auto-reset colors after each print
    COLORAMA_AVAILABLE = True
except ImportError:
    # Fallback if colorama not installed
    class Fore:
        GREEN = ''
        YELLOW = ''
        CYAN = ''
        MAGENTA = ''
        RED = ''
        BLUE = ''
        WHITE = ''
        RESET = ''
    class Style:
        BRIGHT = ''
        RESET_ALL = ''
    COLORAMA_AVAILABLE = False

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# Sport configuration
SPORT_CONFIG = {
    "nfl": {
        "sport_name": "NFL",
        "kalshi_file": "kalshi_nfl_winner_markets.json",
        "odds_file": "the_odds_api_nfl_moneyline_odds.json",
        "output_file": "odds_comparison_nfl.json",
    },
    "mlb": {
        "sport_name": "MLB",
        "kalshi_file": "kalshi_mlb_winner_markets.json",
        "odds_file": "the_odds_api_mlb_moneyline_odds.json",
        "output_file": "odds_comparison_mlb.json",
    },
    "nba": {
        "sport_name": "NBA",
        "kalshi_file": "kalshi_nba_winner_markets.json",
        "odds_file": "the_odds_api_nba_moneyline_odds.json",
        "output_file": "odds_comparison_nba.json",
    },
    "ncaab": {
        "sport_name": "NCAAB",
        "kalshi_file": "kalshi_ncaab_winner_markets.json",
        "odds_file": "the_odds_api_ncaab_moneyline_odds.json",
        "output_file": "odds_comparison_ncaab.json",
    },
    "ncaaf": {
        "sport_name": "NCAAF",
        "kalshi_file": "kalshi_ncaaf_winner_markets.json",
        "odds_file": "the_odds_api_ncaaf_moneyline_odds.json",
        "output_file": "odds_comparison_ncaaf.json",
    },
    "ufc": {
        "sport_name": "UFC",
        "kalshi_file": "kalshi_ufc_winner_markets.json",
        "odds_file": "the_odds_api_ufc_moneyline_odds.json",
        "output_file": "odds_comparison_ufc.json",
    },
    "nhl": {
        "sport_name": "NHL",
        "kalshi_file": "kalshi_nhl_winner_markets.json",
        "odds_file": "the_odds_api_nhl_moneyline_odds.json",
        "output_file": "odds_comparison_nhl.json",
    },
    "mls": {
        "sport_name": "MLS",
        "kalshi_file": "kalshi_mls_winner_markets.json",
        "odds_file": "the_odds_api_mls_moneyline_odds.json",
        "output_file": "odds_comparison_mls.json",
    },
    "ncaabw": {
        "sport_name": "NCAABW",
        "kalshi_file": "kalshi_ncaabw_winner_markets.json",
        "odds_file": "the_odds_api_ncaabw_moneyline_odds.json",
        "output_file": "odds_comparison_ncaabw.json",
    },
}

# Team name mapping from Kalshi format to full team names
# Organized by sport to avoid conflicts (e.g., "Seattle" exists in NFL, MLB, NBA)
KALSHI_TO_FULL_TEAM = {
    "nfl": {
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
    },
    "mlb": {
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
    },
    "nba": {
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
    },
    "ncaab": {
        # College basketball teams - will be populated as we see data
        # Format: "Kalshi short name": "Full team name"
    },
    "ncaaf": {
        # College football teams - will be populated as we see data
        # Format: "Kalshi short name": "Full team name"
    },
    "ufc": {
        # UFC fighters - will be populated as we see data
        # Format: "Kalshi fighter name": "Full fighter name"
    },
    "nhl": {
        # NHL teams - will be populated as we see data
        # Format: "Kalshi short name": "Full team name"
    },
    "mls": {
        # MLS teams - will be populated as we see data
        # Format: "Kalshi short name": "Full team name"
    },
    "ncaabw": {
        # Women's college basketball teams - will be populated as we see data
        # Format: "Kalshi short name": "Full team name"
    },
}

def convert_american_odds_to_probability(odds: int) -> float:
    """
    Convert American odds to implied probability percentage.
    
    Negative odds (e.g., -125): probability = abs(odds) / (abs(odds) + 100) × 100
    Positive odds (e.g., +105): probability = 100 / (odds + 100) × 100
    
    Returns probability as a percentage (0-100).
    """
    if odds < 0:
        return abs(odds) / (abs(odds) + 100) * 100
    else:
        return 100 / (odds + 100) * 100

def normalize_probabilities(prob_a: float, prob_b: float) -> Tuple[float, float]:
    """
    Remove vig from probabilities by normalizing them to sum to 100%.
    Keeps the same ratio between the probabilities.
    
    Returns (normalized_prob_a, normalized_prob_b) as percentages.
    """
    total = prob_a + prob_b
    if total == 0:
        return 50.0, 50.0
    return (prob_a / total * 100, prob_b / total * 100)

def calculate_kalshi_payout(bet_amount: float, price_cents: int, fee_percent: float = 1.0) -> Dict:
    """
    Calculate Kalshi payout for a bet.
    Price is in cents (0-100), represents cost per $1 share.
    
    Kalshi takes a fee (default 1%) on winning contracts, so the payout
    is reduced by that percentage.
    
    Args:
        bet_amount: Amount bet in dollars
        price_cents: Price per share in cents (0-100)
        fee_percent: Kalshi's fee percentage on winning contracts (default 1.0%)
    
    Returns dict with profit_if_win and loss_if_lose.
    """
    price_dollars = price_cents / 100.0
    if price_dollars == 0:
        return {"profit_if_win": 0, "loss_if_lose": -bet_amount}
    
    shares = bet_amount / price_dollars
    # Each share pays $1, but Kalshi takes a fee on winning contracts
    payout_per_share = 1.0 * (1 - fee_percent / 100.0)
    payout_if_win = shares * payout_per_share
    profit_if_win = payout_if_win - bet_amount
    loss_if_lose = -bet_amount
    
    return {
        "profit_if_win": round(profit_if_win, 2),
        "loss_if_lose": round(loss_if_lose, 2),
    }

def calculate_sportsbook_payout(bet_amount: float, odds: int) -> Dict:
    """
    Calculate sportsbook payout for a bet using actual odds (with vig).
    
    Returns dict with profit_if_win and loss_if_lose.
    """
    if odds < 0:
        # Negative odds: bet $X to win $100
        # For $100 bet: profit = (bet_amount / abs(odds)) * 100
        profit_if_win = (bet_amount / abs(odds)) * 100
    else:
        # Positive odds: bet $100 to win $X
        profit_if_win = (bet_amount / 100.0) * odds
    
    loss_if_lose = -bet_amount
    
    return {
        "profit_if_win": round(profit_if_win, 2),
        "loss_if_lose": round(loss_if_lose, 2),
    }

def find_best_platform(team: str, kalshi_prob: float, sportsbook_prob: float) -> str:
    """
    Find the best platform for betting on a team.
    Lower probability = better odds (more profit if win).
    
    Returns "kalshi" or "sportsbook".
    """
    if kalshi_prob < sportsbook_prob:
        return "kalshi"
    else:
        return "sportsbook"

def calculate_expected_value(
    prob_team_a_wins: float,
    prob_team_b_wins: float,
    net_if_team_a_wins: float,
    net_if_team_b_wins: float
) -> float:
    """
    Calculate expected value using normalized probabilities (vig removed).
    
    EV = (prob_team_a × net_if_team_a_wins) + (prob_team_b × net_if_team_b_wins)
    
    Probabilities should be percentages (0-100).
    """
    prob_a = prob_team_a_wins / 100.0
    prob_b = prob_team_b_wins / 100.0
    
    return (prob_a * net_if_team_a_wins) + (prob_b * net_if_team_b_wins)

def parse_kalshi_team_name(title: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse Kalshi title format like "Los Angeles R at Seattle Winner?"
    Returns (away_team, home_team) or (None, None) if parsing fails.
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
    
    away_team = KALSHI_TO_FULL_TEAM.get(away_team_kalshi)
    home_team = KALSHI_TO_FULL_TEAM.get(home_team_kalshi)
    
    return away_team, home_team

def load_and_match_games(sport: str) -> List[Dict]:
    """
    Load data from both JSON files and match games.
    Returns list of matched games with all necessary data.
    """
    config = SPORT_CONFIG[sport]
    
    # Load Kalshi data
    kalshi_file = os.path.join(DATA_DIR, config["kalshi_file"])
    if not os.path.exists(kalshi_file):
        raise FileNotFoundError(f"Kalshi data file not found: {kalshi_file}")
    
    with open(kalshi_file, "r", encoding="utf-8") as f:
        kalshi_data = json.load(f)
    
    # Load odds data
    odds_file = os.path.join(DATA_DIR, config["odds_file"])
    if not os.path.exists(odds_file):
        raise FileNotFoundError(f"Odds data file not found: {odds_file}")
    
    with open(odds_file, "r", encoding="utf-8") as f:
        odds_data = json.load(f)
    
    # Group Kalshi markets by event_ticker
    kalshi_markets_by_event = {}
    for market in kalshi_data.get("markets", []):
        event_ticker = market.get("event_ticker", "")
        if event_ticker not in kalshi_markets_by_event:
            kalshi_markets_by_event[event_ticker] = []
        kalshi_markets_by_event[event_ticker].append(market)
    
    matched_games = []
    matched_event_ticks = set()  # Track matched events to avoid duplicates
    
    # Get sport-specific team mapping
    sport_mapping = KALSHI_TO_FULL_TEAM.get(sport, {})
    # For college sports, UFC, NHL, MLS, use flexible matching
    use_flexible_matching = sport in ["ncaab", "ncaaf", "ncaabw", "ufc", "nhl", "mls"]
    
    # Helper function to extract team names from Odds API game
    def extract_team_names(odds_game: Dict) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract team names from an Odds API game object.
        Tries multiple methods:
        1. Direct fields (home_team, away_team)
        2. From first bookmaker's h2h market outcomes
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
        team_names = set()
        for bookmaker in bookmakers:
            markets = bookmaker.get("markets", [])
            for market in markets:
                if market.get("key") == "h2h":
                    outcomes = market.get("outcomes", [])
                    for outcome in outcomes:
                        team_name = outcome.get("name")
                        if team_name:
                            team_names.add(team_name)
                    # If we found 2 teams, we can return them
                    if len(team_names) >= 2:
                        team_list = list(team_names)
                        # Try to determine which is home/away (usually first is away, second is home)
                        # But we'll return both and let matching figure it out
                        return team_list[0], team_list[1] if len(team_list) > 1 else None
        
        return None, None
    
    # Helper function to normalize team names for matching
    def normalize_for_match(name: str) -> str:
        """Normalize team name for better matching."""
        if not name:
            return ""
        name = name.strip().lower()
        # Remove common suffixes
        suffixes = [" university", " univ", " state", " st", " college", " col", " st.", " st "]
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
        return name.strip()
    
    # Helper function to check if teams match
    def teams_match(team1: str, team2: str) -> bool:
        """Check if two team names match (with normalization and flexible matching)."""
        if not team1 or not team2:
            return False
        norm1 = normalize_for_match(team1)
        norm2 = normalize_for_match(team2)
        
        # Exact match after normalization
        if norm1 == norm2:
            return True
        
        # For flexible matching sports, try substring matching
        if use_flexible_matching:
            if norm1 in norm2 or norm2 in norm1:
                return True
        
        return False
    
    # Collect all Odds API games (both matched and unmatched)
    # The Odds API data can be in nested format (odds_data) or direct format
    all_odds_games = []
    for game in odds_data.get("games", []):
        odds_info = game.get("odds_data")
        
        # Check nested structure first (from saved file format)
        if odds_info:
            # Try to extract team names (from direct fields or bookmaker outcomes)
            away_team, home_team = extract_team_names(odds_info)
            if away_team and home_team:
                # Add team names if they weren't at top level
                if not odds_info.get("away_team"):
                    odds_info["away_team"] = away_team
                if not odds_info.get("home_team"):
                    odds_info["home_team"] = home_team
                all_odds_games.append(odds_info)
        # Also check if team names are at the game level directly
        elif game.get("away_team") and game.get("home_team"):
            all_odds_games.append(game)
        # Try extracting from game level if it has bookmakers
        elif game.get("bookmakers"):
            away_team, home_team = extract_team_names(game)
            if away_team and home_team:
                game["away_team"] = away_team
                game["home_team"] = home_team
                all_odds_games.append(game)
    
    # Get all Kalshi markets
    all_kalshi_markets = []
    for markets_list in kalshi_markets_by_event.values():
        all_kalshi_markets.extend(markets_list)
    
    # Try to match each Odds API game with Kalshi markets
    for odds_info in all_odds_games:
        away_team_odds = odds_info.get("away_team", "")
        home_team_odds = odds_info.get("home_team", "")
        
        if not away_team_odds or not home_team_odds:
            continue
        
        away_kalshi_market = None
        home_kalshi_market = None
        matched_event_ticker = None
        
        # Search all Kalshi markets for team matches
        for market in all_kalshi_markets:
            market_data = market.get("market_data", {})
            yes_sub_title = market_data.get("yes_sub_title", "")
            title = market.get("title", "") or market_data.get("title", "")
            
            # Skip if not a winner market
            if not title or not title.endswith("Winner?"):
                continue
            
            event_ticker = market.get("event_ticker", "")
            
            # Try mapping first, then fall back to direct match
            kalshi_full_team = sport_mapping.get(yes_sub_title, yes_sub_title if use_flexible_matching else "")
            
            # Check if this market matches away team
            if teams_match(kalshi_full_team, away_team_odds) or (use_flexible_matching and teams_match(yes_sub_title, away_team_odds)):
                if not away_kalshi_market:
                    away_kalshi_market = market
                    matched_event_ticker = event_ticker
            # Check if this market matches home team
            elif teams_match(kalshi_full_team, home_team_odds) or (use_flexible_matching and teams_match(yes_sub_title, home_team_odds)):
                if not home_kalshi_market:
                    home_kalshi_market = market
                    if not matched_event_ticker:
                        matched_event_ticker = event_ticker
        
        # Only add if we found both markets and they're from the same event
        if away_kalshi_market and home_kalshi_market:
            away_event = away_kalshi_market.get("event_ticker", "")
            home_event = home_kalshi_market.get("event_ticker", "")
            
            # Both markets must be from the same event
            if away_event == home_event and away_event and away_event not in matched_event_ticks:
                matched_event_ticks.add(away_event)
                matched_games.append({
                    "event_ticker": away_event,
                    "away_team": away_team_odds,
                    "home_team": home_team_odds,
                    "commence_time": odds_info.get("commence_time"),
                    "away_kalshi_market": away_kalshi_market,
                    "home_kalshi_market": home_kalshi_market,
                    "odds_data": odds_info,
                })
    
    return matched_games

def get_average_sportsbook_odds(game: Dict, team_name: str) -> Tuple[Optional[float], int]:
    """
    Get the average sportsbook odds for a team across all bookmakers.
    Returns (average_odds, bookmaker_count).
    """
    odds_list = []
    
    for bookmaker in game["odds_data"].get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            if market.get("key") == "h2h":
                for outcome in market.get("outcomes", []):
                    if outcome.get("name", "") == team_name:
                        odds = outcome.get("price")
                        odds_list.append(odds)
                        break  # Only count once per bookmaker
                break  # Only check first h2h market per bookmaker
    
    if not odds_list:
        return None, 0
    
    avg_odds = sum(odds_list) / len(odds_list)
    return avg_odds, len(odds_list)

def analyze_game(game: Dict) -> Optional[Dict]:
    """
    Analyze a single game for positive EV opportunities on Kalshi.
    
    Uses average sportsbook odds (devigged) as the true probabilities,
    and compares Kalshi prices to find positive EV unhedged bets.
    
    Only evaluates unhedged Kalshi bets (no sportsbook bets, no hedging).
    
    Returns the best opportunity if positive EV found, None otherwise.
    """
    away_team = game["away_team"]
    home_team = game["home_team"]
    
    # Get Kalshi data
    away_kalshi_data = game["away_kalshi_market"]["market_data"]
    home_kalshi_data = game["home_kalshi_market"]["market_data"]
    
    away_kalshi_price = away_kalshi_data.get("yes_ask", 0)  # Price in cents
    home_kalshi_price = home_kalshi_data.get("yes_ask", 0)  # Price in cents
    
    # Get average sportsbook odds for each team
    avg_away_odds, away_bookmaker_count = get_average_sportsbook_odds(game, away_team)
    avg_home_odds, home_bookmaker_count = get_average_sportsbook_odds(game, home_team)
    
    if avg_away_odds is None or avg_home_odds is None:
        return None
    
    # Convert average sportsbook odds to probabilities (with vig)
    away_sportsbook_prob = convert_american_odds_to_probability(int(avg_away_odds))
    home_sportsbook_prob = convert_american_odds_to_probability(int(avg_home_odds))
    
    # Normalize sportsbook probabilities (remove vig) - these are our "true" probabilities
    away_prob_normalized, home_prob_normalized = normalize_probabilities(
        away_sportsbook_prob, home_sportsbook_prob
    )
    
    bet_amount = 100.0
    
    # ============================================================
    # UNHEDGED KALSHI STRATEGIES ONLY
    # ============================================================
    
    # Strategy 1: Bet on Away team via Kalshi (unhedged)
    away_kalshi_payout = calculate_kalshi_payout(bet_amount, int(away_kalshi_price))
    away_net_if_away_wins = away_kalshi_payout["profit_if_win"]
    away_net_if_home_wins = away_kalshi_payout["loss_if_lose"]
    
    away_ev = calculate_expected_value(
        away_prob_normalized,
        home_prob_normalized,
        away_net_if_away_wins,
        away_net_if_home_wins
    )
    
    # Strategy 2: Bet on Home team via Kalshi (unhedged)
    home_kalshi_payout = calculate_kalshi_payout(bet_amount, int(home_kalshi_price))
    home_net_if_away_wins = home_kalshi_payout["loss_if_lose"]
    home_net_if_home_wins = home_kalshi_payout["profit_if_win"]
    
    home_ev = calculate_expected_value(
        away_prob_normalized,
        home_prob_normalized,
        home_net_if_away_wins,
        home_net_if_home_wins
    )
    
    # ============================================================
    # CHOOSE BEST STRATEGY (highest EV, must be positive)
    # ============================================================
    
    strategies = [
        {
            "team": "away",
            "team_name": away_team,
            "ev": away_ev,
            "kalshi_price": away_kalshi_price,
            "payout": away_kalshi_payout,
            "net_if_away_wins": away_net_if_away_wins,
            "net_if_home_wins": away_net_if_home_wins,
        },
        {
            "team": "home",
            "team_name": home_team,
            "ev": home_ev,
            "kalshi_price": home_kalshi_price,
            "payout": home_kalshi_payout,
            "net_if_away_wins": home_net_if_away_wins,
            "net_if_home_wins": home_net_if_home_wins,
        },
    ]
    
    # Find strategy with highest positive EV
    best_strategy = max(strategies, key=lambda s: s["ev"])
    
    # Only return if positive EV
    if best_strategy["ev"] <= 0:
        return None
    
    # Build result dictionary
    result = {
        "event_ticker": game["event_ticker"],
        "away_team": away_team,
        "home_team": home_team,
        "commence_time": game["commence_time"],
        "strategy_type": "unhedged",
        "bet_team": best_strategy["team"],
        "bet_team_name": best_strategy["team_name"],
        "away_platform": "kalshi" if best_strategy["team"] == "away" else None,
        "away_platform_name": "Kalshi" if best_strategy["team"] == "away" else None,
        "home_platform": "kalshi" if best_strategy["team"] == "home" else None,
        "home_platform_name": "Kalshi" if best_strategy["team"] == "home" else None,
        "away_kalshi_prob": away_kalshi_price,
        "home_kalshi_prob": home_kalshi_price,
        "away_sportsbook_prob": away_sportsbook_prob,
        "home_sportsbook_prob": home_sportsbook_prob,
        "away_prob_normalized": away_prob_normalized,
        "home_prob_normalized": home_prob_normalized,
        "avg_away_odds": round(avg_away_odds, 2),
        "avg_home_odds": round(avg_home_odds, 2),
        "away_bookmaker_count": away_bookmaker_count,
        "home_bookmaker_count": home_bookmaker_count,
        "away_payout": best_strategy["payout"] if best_strategy["team"] == "away" else None,
        "home_payout": best_strategy["payout"] if best_strategy["team"] == "home" else None,
        "net_if_away_wins": best_strategy["net_if_away_wins"],
        "net_if_home_wins": best_strategy["net_if_home_wins"],
        "expected_value": round(best_strategy["ev"], 2),
        "total_investment": bet_amount,
    }
    
    return result

def generate_opportunity_table(opp: Dict) -> str:
    """
    Generate a detailed, colorized summary for a Kalshi betting opportunity.
    Uses average sportsbook devigged probabilities as true likelihood.
    """
    lines = []
    
    away_team = opp['away_team']
    home_team = opp['home_team']
    away_prob = opp['away_prob_normalized']  # Average sportsbook devigged probability
    home_prob = opp['home_prob_normalized']  # Average sportsbook devigged probability
    
    # Format: [TEAM1] xx.xx% @ [TEAM2] xx.xx%
    # These percentages are from average sportsbook devigged odds (true probabilities)
    team_line = f"{Fore.BLUE}Sportsbook Odds:{Style.RESET_ALL} {Fore.CYAN}[{away_team}]{Style.RESET_ALL} {Fore.YELLOW}{away_prob:.2f}%{Style.RESET_ALL} @ {Fore.CYAN}[{home_team}]{Style.RESET_ALL} {Fore.YELLOW}{home_prob:.2f}%{Style.RESET_ALL}"
    lines.append(team_line)
    
    # Kalshi odds (prices in cents, displayed as percentages)
    away_kalshi_price = opp.get('away_kalshi_prob', 0)
    home_kalshi_price = opp.get('home_kalshi_prob', 0)
    kalshi_line = f"{Fore.BLUE}Kalshi Odds:{Style.RESET_ALL} {Fore.CYAN}[{away_team}]{Style.RESET_ALL} {Fore.YELLOW}{away_kalshi_price:.0f}%{Style.RESET_ALL} @ {Fore.CYAN}[{home_team}]{Style.RESET_ALL} {Fore.YELLOW}{home_kalshi_price:.0f}%{Style.RESET_ALL}"
    lines.append(kalshi_line)
    lines.append("")  # Blank line for spacing
    
    # Strategy line - always Kalshi, always unhedged
    bet_team_name = opp.get('bet_team_name', away_team if opp.get('bet_team') == 'away' else home_team)
    strategy_text = f"{Fore.MAGENTA}Strategy:{Style.RESET_ALL} Bet ${100:.0f} on {Fore.GREEN}{bet_team_name}{Style.RESET_ALL} via {Fore.BLUE}Kalshi{Style.RESET_ALL} {Fore.RED}(NO HEDGE){Style.RESET_ALL}"
    lines.append(strategy_text)
    lines.append("")  # Blank line for spacing
    
    # Expected Value breakdown
    lines.append(f"{Fore.MAGENTA}{Style.BRIGHT}Expected Value:{Style.RESET_ALL}")
    lines.append("")  # Blank line for spacing
    
    # Calculate probability-weighted outcomes
    away_prob_decimal = away_prob / 100.0
    home_prob_decimal = home_prob / 100.0
    
    away_weighted = away_prob_decimal * opp['net_if_away_wins']
    home_weighted = home_prob_decimal * opp['net_if_home_wins']
    
    # Format outcomes
    away_outcome_str = f"+${opp['net_if_away_wins']:.2f}" if opp['net_if_away_wins'] >= 0 else f"${opp['net_if_away_wins']:.2f}"
    home_outcome_str = f"+${opp['net_if_home_wins']:.2f}" if opp['net_if_home_wins'] >= 0 else f"${opp['net_if_home_wins']:.2f}"
    
    # Format weighted outcomes with colors
    away_weighted_str = f"+${away_weighted:.2f}" if away_weighted >= 0 else f"${away_weighted:.2f}"
    home_weighted_str = f"+${home_weighted:.2f}" if home_weighted >= 0 else f"${home_weighted:.2f}"
    
    # Color code positive/negative values
    away_outcome_color = Fore.GREEN if opp['net_if_away_wins'] >= 0 else Fore.RED
    home_outcome_color = Fore.GREEN if opp['net_if_home_wins'] >= 0 else Fore.RED
    away_weighted_color = Fore.GREEN if away_weighted >= 0 else Fore.RED
    home_weighted_color = Fore.GREEN if home_weighted >= 0 else Fore.RED
    
    # [TEAM1] win: xx.xx% * odds = outcome
    # xx.xx% is the average sportsbook devigged probability (true likelihood)
    away_line = f"  {Fore.CYAN}{away_team}{Style.RESET_ALL} win: {Fore.YELLOW}{away_prob:.2f}%{Style.RESET_ALL} * {away_outcome_color}{away_outcome_str}{Style.RESET_ALL} = {away_weighted_color}{away_weighted_str}{Style.RESET_ALL}"
    home_line = f"  {Fore.CYAN}{home_team}{Style.RESET_ALL} win: {Fore.YELLOW}{home_prob:.2f}%{Style.RESET_ALL} * {home_outcome_color}{home_outcome_str}{Style.RESET_ALL} = {home_weighted_color}{home_weighted_str}{Style.RESET_ALL}"
    
    lines.append(away_line)
    lines.append(home_line)
    lines.append("")  # Blank line for spacing
    
    # TOTAL = outcome + outcome
    total_ev = away_weighted + home_weighted
    total_str = f"+${total_ev:.2f}" if total_ev >= 0 else f"${total_ev:.2f}"
    total_color = Fore.GREEN if total_ev >= 0 else Fore.RED
    
    # Format the addition properly (avoid double signs)
    away_formatted = away_weighted_str.replace("+", "") if away_weighted_str.startswith("+") else away_weighted_str
    home_formatted = home_weighted_str.replace("+", "") if home_weighted_str.startswith("+") else home_weighted_str
    
    total_line = f"  {Fore.MAGENTA}{Style.BRIGHT}TOTAL{Style.RESET_ALL} = {away_formatted} + {home_formatted} = {total_color}{Style.BRIGHT}{total_str}{Style.RESET_ALL}"
    lines.append(total_line)
    
    return "\n".join(lines)

def process_sport(sport: str) -> Optional[Dict]:
    """
    Process a single sport and return results.
    Returns None if data files don't exist or no games found.
    """
    if sport not in SPORT_CONFIG:
        return None
    
    config = SPORT_CONFIG[sport]
    
    # Check if data files exist
    kalshi_file = os.path.join(DATA_DIR, config["kalshi_file"])
    odds_file = os.path.join(DATA_DIR, config["odds_file"])
    
    if not os.path.exists(kalshi_file):
        return None
    
    if not os.path.exists(odds_file):
        return None
    try:
        matched_games = load_and_match_games(sport)
        
        # Load odds data to show how many games The Odds API had
        odds_file = os.path.join(DATA_DIR, config["odds_file"])
        with open(odds_file, "r", encoding="utf-8") as f:
            odds_data = json.load(f)
        total_odds_games = odds_data.get("total_games", 0)
        matched_odds_games = odds_data.get("matched_games", 0)
        
        # Load Kalshi data to show how many games Kalshi had
        kalshi_file = os.path.join(DATA_DIR, config["kalshi_file"])
        with open(kalshi_file, "r", encoding="utf-8") as f:
            kalshi_data = json.load(f)
        total_kalshi_games = kalshi_data.get("total_markets_found", 0)
        
    except FileNotFoundError as e:
        return None
    except Exception as e:
        return None
    
    if len(matched_games) == 0:
        return None
    
    opportunities = []
    
    # Minimum EV threshold: 2% of bet amount
    min_ev_threshold = 2.0  # 2% of $100 bet = $2.00
    
    for game in matched_games:
        opp = analyze_game(game)
        if opp and opp["expected_value"] > min_ev_threshold:
            opportunities.append(opp)
    
    # Sort by expected value (highest first)
    opportunities.sort(key=lambda x: x["expected_value"], reverse=True)
    
    # Save to JSON
    output_data = {
        "source": "odds_comparison",
        "content_type": "positive_ev_opportunities",
        "sport": sport,
        "query_time": datetime.now(timezone.utc).isoformat(),
        "total_opportunities": len(opportunities),
        "opportunities": opportunities,
    }
    
    output_file = os.path.join(DATA_DIR, config["output_file"])
    os.makedirs(DATA_DIR, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Count how many Odds API games actually had team data
    # Check both the nested structure (saved format) and direct structure (if games are at top level)
    def extract_team_names_for_count(odds_game: Dict) -> Tuple[Optional[str], Optional[str]]:
        """Extract team names for counting purposes."""
        home_team = odds_game.get("home_team")
        away_team = odds_game.get("away_team")
        if home_team and away_team:
            return away_team, home_team
        
        # Try extracting from bookmaker outcomes
        bookmakers = odds_game.get("bookmakers", [])
        for bookmaker in bookmakers:
            markets = bookmaker.get("markets", [])
            for market in markets:
                if market.get("key") == "h2h":
                    outcomes = market.get("outcomes", [])
                    team_names = [outcome.get("name") for outcome in outcomes if outcome.get("name")]
                    if len(team_names) >= 2:
                        return team_names[0], team_names[1]
        return None, None
    
    odds_games_with_teams = 0
    for game in odds_data.get("games", []):
        odds_info = game.get("odds_data")
        # Check nested structure (from saved file)
        if odds_info:
            away_team, home_team = extract_team_names_for_count(odds_info)
            if away_team and home_team:
                odds_games_with_teams += 1
        # Also check if team names are at the game level directly
        elif game.get("away_team") and game.get("home_team"):
            odds_games_with_teams += 1
        # Try extracting from bookmaker outcomes
        elif game.get("bookmakers"):
            away_team, home_team = extract_team_names_for_count(game)
            if away_team and home_team:
                odds_games_with_teams += 1
    
    return {
        "sport": sport,
        "sport_name": config["sport_name"],
        "matched_games": len(matched_games),
        "total_kalshi_games": total_kalshi_games,
        "total_odds_games": total_odds_games,
        "odds_games_with_teams": odds_games_with_teams,
        "opportunities": opportunities,
        "total_opportunities": len(opportunities),
    }

def main():
    """
    Main function to find positive EV opportunities.
    If no sport argument is provided, processes all sports.
    """
    # If sport argument provided, process only that sport
    if len(sys.argv) >= 2:
        sport = sys.argv[1].lower()
        if sport not in SPORT_CONFIG:
            print(f"Error: Unsupported sport '{sport}'")
            print(f"Supported sports: {', '.join(SPORT_CONFIG.keys())}")
            sys.exit(1)
        
        result = process_sport(sport)
        if result is None:
            sys.exit(1)
        
        # Display summary for single sport
        total_games = result['matched_games']
        total_opps = len(result['opportunities'])
        total_kalshi = result.get('total_kalshi_games', 0)
        total_odds = result.get('total_odds_games', 0)
        
        summary_border = f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}"
        print(f"\n{summary_border}")
        summary_text = f"{Fore.CYAN}{Style.BRIGHT}SUMMARY ({result['sport_name']}):{Style.RESET_ALL}"
        summary_text += f"\n  {Fore.YELLOW}Total Kalshi games:{Style.RESET_ALL} {total_kalshi}"
        summary_text += f"\n  {Fore.YELLOW}Total Sportsbook games:{Style.RESET_ALL} {total_odds}"
        summary_text += f"\n  {Fore.YELLOW}Matched & Analyzed:{Style.RESET_ALL} {total_games}"
        summary_text += f"\n  {Fore.GREEN}Positive EV opportunities:{Style.RESET_ALL} {total_opps}"
        if total_games > 0:
            percentage = (total_opps / total_games) * 100
            summary_text += f" ({Fore.YELLOW}{percentage:.1f}%{Style.RESET_ALL})"
        print(summary_text)
        print(f"{summary_border}\n")
        
        # Display opportunities if any
        if total_opps > 0:
            for i, opp in enumerate(result['opportunities'], 1):
                opp_header = f"{Fore.CYAN}{Style.BRIGHT}[{i}/{total_opps}]{Style.RESET_ALL} {Fore.MAGENTA}[{result['sport_name']}]{Style.RESET_ALL}"
                print(opp_header)
                print(f"{Fore.CYAN}{'-'*80}{Style.RESET_ALL}")
                table = generate_opportunity_table(opp)
                print(table)
                if i < total_opps:
                    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        else:
            print(f"{Fore.RED}No positive EV opportunities found for {result['sport_name']}.{Style.RESET_ALL}\n")
        
        return
    
    # No argument provided - process all sports
    all_results = []
    for sport in SPORT_CONFIG.keys():
        result = process_sport(sport)
        if result:
            all_results.append(result)
    
    if not all_results:
        print("No data available for any sport.")
        print("\nTo generate data, run:")
        print("  python scripts/fetch_kalshi_sports.py <sport>")
        print("  python scripts/fetch_odds_api_sports.py <sport>")
        return
    
    # Calculate totals
    total_games_analyzed = sum(result['matched_games'] for result in all_results)
    total_kalshi_games = sum(result.get('total_kalshi_games', 0) for result in all_results)
    total_odds_games = sum(result.get('total_odds_games', 0) for result in all_results)
    total_odds_with_teams = sum(result.get('odds_games_with_teams', 0) for result in all_results)
    
    # Collect all opportunities across all sports
    all_opps = []
    for result in all_results:
        for opp in result['opportunities']:
            opp['sport'] = result['sport_name']
            all_opps.append(opp)
    
    # Display summary at the top
    summary_border = f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}"
    print(f"\n{summary_border}")
    summary_text = f"{Fore.CYAN}{Style.BRIGHT}SUMMARY:{Style.RESET_ALL}"
    summary_text += f"\n  {Fore.YELLOW}Total Kalshi games:{Style.RESET_ALL} {total_kalshi_games}"
    summary_text += f"\n  {Fore.YELLOW}Total Sportsbook games:{Style.RESET_ALL} {total_odds_games}"
    if total_odds_with_teams != total_odds_games:
        summary_text += f" ({Fore.CYAN}{total_odds_with_teams} with team data{Style.RESET_ALL})"
    summary_text += f"\n  {Fore.YELLOW}Matched & Analyzed:{Style.RESET_ALL} {total_games_analyzed}"
    if total_odds_with_teams > 0:
        match_rate = (total_games_analyzed / total_odds_with_teams) * 100
        summary_text += f" ({Fore.CYAN}{match_rate:.1f}% of sportsbook games matched{Style.RESET_ALL})"
    summary_text += f"\n  {Fore.GREEN}Positive EV opportunities:{Style.RESET_ALL} {len(all_opps)}"
    if total_games_analyzed > 0:
        percentage = (len(all_opps) / total_games_analyzed) * 100
        summary_text += f" ({Fore.YELLOW}{percentage:.1f}%{Style.RESET_ALL})"
    print(summary_text)
    print(f"{summary_border}\n")
    
    if len(all_opps) > 0:
        all_opps.sort(key=lambda x: x["expected_value"], reverse=True)
        
        # Header with decoration
        header_border = f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}"
        header_text = f"{Fore.CYAN}{Style.BRIGHT}ALL {len(all_opps)} POSITIVE EV OPPORTUNITIES ACROSS ALL SPORTS{Style.RESET_ALL}"
        header_subtext = f"{Fore.YELLOW}(sorted by Expected Value){Style.RESET_ALL}"
        
        print(f"{header_border}")
        print(f"{header_text}")
        print(f"{header_subtext}")
        print(f"{header_border}\n")
        
        for i, opp in enumerate(all_opps, 1):
            # Opportunity header with number and sport
            opp_header = f"{Fore.CYAN}{Style.BRIGHT}[{i}/{len(all_opps)}]{Style.RESET_ALL} {Fore.MAGENTA}[{opp['sport']}]{Style.RESET_ALL}"
            print(opp_header)
            print(f"{Fore.CYAN}{'-'*80}{Style.RESET_ALL}")
            
            table = generate_opportunity_table(opp)
            print(table)
            
            # Add separator between opportunities (except last one)
            if i < len(all_opps):
                print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    else:
        print(f"\n{Fore.RED}No positive EV opportunities found across all sports.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
