"""
Master script to refresh all data for all sports.
Fetches Kalshi data and sportsbook odds for all configured sports.
"""
import subprocess
import sys
import os

# Get the project root directory (parent of scripts folder)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")

# All supported sports
SPORTS = ["nfl", "mlb", "nba", "ncaab", "ncaabw", "ncaaf", "ufc", "nhl", "mls"]

def run_script(script_name: str, sport: str) -> bool:
    """
    Run a Python script with a sport argument.
    Returns True if successful, False otherwise.
    """
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    try:
        # Explicitly pass environment variables to ensure API key is available
        env = os.environ.copy()
        result = subprocess.run(
            [sys.executable, script_path, sport],
            cwd=PROJECT_ROOT,
            env=env,  # Pass environment explicitly
            capture_output=False,  # Show output in real-time
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {script_name} for {sport}: {e}")
        return False

def main():
    """
    Refresh all data for all sports.
    """
    print("=" * 80)
    print("REFRESHING ALL DATA FOR ALL SPORTS")
    print("=" * 80)
    
    # Check if API key is set
    api_key = os.getenv("ODDS_API_KEY")
    if not api_key:
        print("\n⚠ WARNING: ODDS_API_KEY environment variable is not set!")
        print("Sportsbook odds fetching will fail without the API key.")
        print("Please set it using:")
        print("  PowerShell: $env:ODDS_API_KEY='your_api_key_here'")
        print("  CMD: set ODDS_API_KEY=your_api_key_here")
        print("\nContinuing with Kalshi data fetch only...\n")
    else:
        print()
    
    total_sports = len(SPORTS)
    successful_kalshi = 0
    successful_odds = 0
    
    for idx, sport in enumerate(SPORTS, 1):
        print(f"\n[{idx}/{total_sports}] Processing {sport.upper()}...")
        print("-" * 80)
        
        # Step 1: Fetch Kalshi data
        print(f"\n1. Fetching Kalshi data for {sport.upper()}...")
        if run_script("fetch_kalshi_sports.py", sport):
            successful_kalshi += 1
            print(f"   ✓ Kalshi data fetched successfully for {sport.upper()}")
        else:
            print(f"   ✗ Failed to fetch Kalshi data for {sport.upper()}")
        
        # Step 2: Fetch sportsbook odds
        print(f"\n2. Fetching sportsbook odds for {sport.upper()}...")
        if run_script("fetch_odds_api_sports.py", sport):
            successful_odds += 1
            print(f"   ✓ Sportsbook odds fetched successfully for {sport.upper()}")
        else:
            print(f"   ✗ Failed to fetch sportsbook odds for {sport.upper()}")
        
        print()
    
    # Summary
    print("=" * 80)
    print("REFRESH SUMMARY")
    print("=" * 80)
    print(f"Kalshi data: {successful_kalshi}/{total_sports} sports successful")
    print(f"Sportsbook odds: {successful_odds}/{total_sports} sports successful")
    print()
    
    if successful_kalshi == total_sports and successful_odds == total_sports:
        print("✓ All data refreshed successfully!")
    else:
        print("⚠ Some data refresh operations failed. Check the output above for details.")
    
    print("\nTo analyze opportunities, run:")
    print("  python scripts/compare_odds.py")

if __name__ == "__main__":
    main()
