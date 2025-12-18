# Arbitrage Opportunities Finder

Compare Kalshi prediction market odds with sportsbook odds to find positive expected value betting opportunities.

## Project Structure

```
Arbitrage/
├── scripts/
│   ├── fetch_kalshi_sports.py      # Fetch winner markets from Kalshi
│   ├── fetch_odds_api_sports.py    # Fetch moneyline odds from The Odds API
│   └── compare_odds.py              # Compare odds and find EV opportunities
└── data/                            # JSON data files (gitignored)
    ├── kalshi_*_winner_markets.json
    ├── the_odds_api_*_moneyline_odds.json
    └── odds_comparison_*.json

## Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set The Odds API Key

```bash
# Windows PowerShell
$env:ODDS_API_KEY='your_api_key_here'

# Windows CMD
set ODDS_API_KEY=your_api_key_here

# Linux/Mac
export ODDS_API_KEY='your_api_key_here'
```

## Usage

### Data Collection

1. **Fetch Kalshi markets:**
   ```bash
   python scripts/fetch_kalshi_sports.py nfl
   python scripts/fetch_kalshi_sports.py nba
   python scripts/fetch_kalshi_sports.py mlb
   ```

2. **Fetch sportsbook odds:**
   ```bash
   python scripts/fetch_odds_api_sports.py nfl
   python scripts/fetch_odds_api_sports.py nba
   python scripts/fetch_odds_api_sports.py mlb
   ```

3. **Compare odds and find opportunities:**
   ```bash
   python scripts/compare_odds.py          # All sports
   python scripts/compare_odds.py nfl      # Specific sport
   ```

   Results are saved to `data/odds_comparison_*.json` files and displayed in the terminal.

## How It Works

The comparison script evaluates two betting strategies for each game:

1. **Strategy 1**: Bet Away team on Kalshi, Bet Home team on Sportsbook
2. **Strategy 2**: Bet Away team on Sportsbook, Bet Home team on Kalshi

For each strategy, it calculates:
- Payouts if each team wins
- Expected value using normalized sportsbook probabilities (vig removed)
- Selects the strategy with highest positive EV

The script accounts for:
- Kalshi's 1% fee on winning contracts
- Sportsbook vig (removed for probability calculations)
- Best odds across all bookmakers

## Supported Sports

### Currently Supported:
- **NFL**: American Football
- **NBA**: Basketball
- **MLB**: Baseball
- **NCAAB**: College Basketball (HIGH OPPORTUNITY - large gap between public perception and reality)
- **NCAAF**: College Football (HIGH OPPORTUNITY - large gap between public perception and reality)
- **UFC**: Mixed Martial Arts (HIGH OPPORTUNITY - growing market with less efficient pricing)

### Why These Sports?

Sports with larger gaps between public perception and reality tend to show more arbitrage opportunities:
- **College Sports**: Public bets on brand names/rankings, but reality is more nuanced with upsets
- **UFC**: Public bets on big names, but technical matchups matter more
- **Professional Sports (NFL/NBA/MLB)**: More efficient markets, but still opportunities exist

## Data Files

All data files are stored in the `data/` directory and are gitignored:
- `kalshi_*_winner_markets.json`: Kalshi market data
- `the_odds_api_*_moneyline_odds.json`: Sportsbook odds data
- `odds_comparison_*.json`: Analyzed opportunities

## Notes

- Kalshi typically has markets for games up to a week in advance
- The Odds API usually only has odds for games in the next 24-48 hours
- Some games may not have matching odds from both sources
