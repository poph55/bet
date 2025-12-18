# Sports Betting Types Guide

## What We're Currently Using

Right now, we're only fetching **"h2h" (Head-to-Head)** bets, which are also called **"Moneyline"** bets.

### Moneyline (h2h) - What We're Using Now

**What it is:** A bet on which team will **win the game** (no point spread, no totals).

**Example from our data:**
```
Game: Radford Highlanders vs William & Mary Tribe

DraftKings odds:
- Radford Highlanders: +330
- William & Mary Tribe: -425

BetMGM odds:
- Radford Highlanders: +300
- William & Mary Tribe: -375
```

**How to read the odds:**
- **Negative odds (e.g., -425)**: The favorite. You need to bet $425 to win $100
  - If you bet $100 on -425, you'd win $23.53 (100/425 * 100)
- **Positive odds (e.g., +330)**: The underdog. You bet $100 to win $330
  - If you bet $100 on +330, you'd win $330 (plus your $100 back = $430 total)

**Why we use this:**
- It's the simplest bet type
- Directly comparable to Kalshi's "Winner?" markets
- Both ask: "Who will win?"

---

## Other Bet Types Available (Not Currently Used)

The Odds API supports these other market types, but we're **not using them yet**:

### 1. Spreads (Point Spread)

**What it is:** A bet on whether a team will win by a certain number of points.

**Example:**
```
Game: Alabama vs Oklahoma
Spread: Alabama -7.5

- Betting "Alabama -7.5" means: Alabama must win by 8+ points
- Betting "Oklahoma +7.5" means: Oklahoma can lose by up to 7 points and you still win
```

**Why we don't use it:**
- Kalshi doesn't have equivalent spread markets for most games
- Harder to compare directly

### 2. Totals (Over/Under)

**What it is:** A bet on whether the total combined score will be over or under a number.

**Example:**
```
Game: Alabama vs Oklahoma
Total: 55.5 points

- Betting "Over 55.5" means: Combined score must be 56+ points
- Betting "Under 55.5" means: Combined score must be 55 or less
```

**Why we don't use it:**
- Kalshi has some total markets, but not for all games
- Would need to match specific totals

### 3. Outrights (Futures)

**What it is:** Long-term bets like "Who will win the championship?"

**Example:**
- "Alabama to win National Championship: +250"
- "Kansas to win March Madness: +800"

**Why we don't use it:**
- These are season-long bets, not game-specific
- Not comparable to individual game markets

---

## What The Odds API Returns

When we fetch odds, we get data from multiple sportsbooks (DraftKings, BetMGM, FanDuel, etc.):

```json
{
  "bookmakers": [
    {
      "key": "draftkings",
      "title": "DraftKings",
      "markets": [
        {
          "key": "h2h",  // This is moneyline
          "outcomes": [
            {
              "name": "Radford Highlanders",
              "price": 330  // This is +330 in American odds
            },
            {
              "name": "William & Mary Tribe",
              "price": -425  // This is -425 in American odds
            }
          ]
        }
      ]
    }
  ]
}
```

**We compare odds across all sportsbooks** and pick the best one for each team.

---

## How Our System Works

1. **Kalshi**: We get "Winner?" markets
   - Example: "Jackson St. at Hampton Winner?"
   - Price in cents: 23 cents = 23% chance

2. **Sportsbooks**: We get moneyline odds
   - Example: "Jackson State +330" vs "Hampton -425"
   - Convert to probabilities: +330 = 23.3% chance, -425 = 80.9% chance

3. **Comparison**: We find where Kalshi and sportsbooks disagree
   - If Kalshi says 30% but sportsbooks say 25%, there might be an opportunity

---

## Why Moneyline is Perfect for Our Use Case

✅ **Direct comparison**: Both ask "Who wins?"
✅ **Simple**: No need to worry about point spreads or totals
✅ **Available**: Almost every game has moneyline odds
✅ **Clear**: Easy to understand and calculate expected value

---

## Could We Add Other Bet Types?

**Yes, but it would be more complex:**

1. **Spreads**: Would need to find matching Kalshi spread markets
2. **Totals**: Would need to find matching Kalshi total markets
3. **More opportunities**: But also more complexity

For now, **moneyline is the best starting point** because:
- It's the most common bet type
- Directly comparable to Kalshi's winner markets
- Easier to understand and calculate

---

## Example: Reading a Real Bet

From our data:
```
Game: Alabama vs Oklahoma

DraftKings:
- Alabama: -105 (favorite)
- Oklahoma: -115 (also favorite, but slightly less)

This means:
- Bet $105 on Alabama → Win $100 if Alabama wins
- Bet $115 on Oklahoma → Win $100 if Oklahoma wins

Both teams are favorites (negative odds), which means the sportsbook thinks it's a close game.
```

**Note:** When both teams have negative odds, it means the sportsbook takes a "vig" (commission). The probabilities don't add up to 100% - that's how sportsbooks make money.

---

## Summary

- **We use**: Moneyline (h2h) bets - "Who will win?"
- **We don't use**: Spreads, totals, or other bet types (yet)
- **Why**: Moneyline is simplest and directly comparable to Kalshi
- **Future**: Could add spreads/totals if we find matching Kalshi markets

