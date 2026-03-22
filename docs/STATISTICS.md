# Poker Statistics Reference Guide

This document explains how each poker statistic is calculated in PokerTracker.

---

## 1. VPIP (Voluntarily Put In Pot)

### Definition
The percentage of hands a player voluntarily puts money into the pot preflop, excluding forced bets like blinds and antes.

### Formula
```
VPIP = (Times Voluntarily Put In Pot) / (Hands Played - Walks) × 100
```

### Calculation Rules
- **Numerator**: Count when player calls, raises, or bets preflop (voluntary action)
- **Denominator**: All hands minus "walks"
- **Excludes**: 
  - Small blind posts
  - Big blind posts
  - Ante posts
  - Straddle posts
- **Walk**: When all players fold to the big blind, and BB wins - this hand is NOT counted in denominator

### Typical Ranges
| Range | Interpretation |
|-------|---------------|
| 15-20% | Tight |
| 20-28% | Standard (6-max) |
| 25-35% | Loose |
| 35%+ | Very Loose |

---

## 2. PFR (Pre-Flop Raise)

### Definition
The percentage of hands a player raises preflop (open-raises).

### Formula
```
PFR = (Times Raised Preflop) / (Hands Played - Walks) × 100
```

### Calculation Rules
- **Numerator**: Count when player raises preflop
- **Denominator**: Same as VPIP

---

## 3. 3-Bet

### Definition
The percentage of times a player re-raises (3-bets) when faced with an open-raise.

### Formula
```
3-Bet = (Times 3-Bet) / (3-Bet Opportunities) × 100
```

### Calculation Rules
- **Numerator**: Count when player makes the 2nd raise preflop
- **Denominator**: Count when there's an open-raise and player has opportunity to 3-bet
- **Opportunity conditions**:
  - Someone raised before the player
  - Player is not all-in
  - Player hasn't already folded

### Typical Ranges
| Range | Interpretation |
|-------|---------------|
| 4-6% | Tight |
| 6-10% | Standard |
| 10%+ | Aggressive |

---

## 4. CBet (Continuation Bet)

### Definition
The percentage of times a player bets on the flop after being the preflop aggressor.

### Formula
```
CBet = (Times CBet) / (CBet Opportunities) × 100
```

### Calculation Rules
- **Numerator**: Count when preflop aggressor bets on flop
- **Denominator**: Count when preflop aggressor has opportunity to CBet
- **Opportunity conditions**:
  - Player was the preflop aggressor (last raise preflop)
  - Flop was dealt
  - Player is not all-in

### Typical Ranges
| Range | Interpretation |
|-------|---------------|
| 50-70% | Standard |
| 70%+ | Aggressive |
| <50% | Weak/Explploitable |

---

## 5. CBet Turn (Double Barrel)

### Definition
The percentage of times a player bets on the turn after CBeting the flop.

### Formula
```
CBet Turn = (Times Barrel Turn) / (Turn Barrel Opportunities) × 100
```

### Calculation Rules
- **Numerator**: Count when player bets on turn after CBeting flop
- **Denominator**: Count when player CBet flop and has opportunity to barrel turn
- **Opportunity conditions**:
  - Player CBet flop
  - Turn was dealt
  - Player is not all-in

---

## 6. Fold to CBet

### Definition
The percentage of times a player folds to a CBet when facing one.

### Formula
```
Fold to CBet = (Times Folded to CBet) / (Times Faced CBet) × 100
```

### Calculation Rules
- **Numerator**: Count when player faces CBet and folds
- **Denominator**: Count when player faces CBet (can call, raise, or fold)
- **Excludes**: When player raised before flop

---

## 7. WTSD (Went to Showdown)

### Definition
The percentage of hands the player reaches showdown out of all hands they saw the flop.

### Formula
```
WTSD = (Times Went to Showdown) / (Times Saw Flop) × 100
```

### Calculation Rules
- **Numerator**: Count when player shows cards at showdown
- **Denominator**: Count when player saw the flop

### Typical Ranges
| Range | Interpretation |
|-------|---------------|
| 20-25% | Tight |
| 25-30% | Standard |
| 30%+ | Calling Station |

---

## 8. W$SD (Won $ at Showdown)

### Definition
The percentage of showdowns the player wins.

### Formula
```
W$SD = (Times Won at Showdown) / (Times Went to Showdown) × 100
```

### Calculation Rules
- **Numerator**: Count when player wins at showdown
- **Denominator**: Count when player goes to showdown

### Typical Ranges
| Range | Interpretation |
|-------|---------------|
| 45-50% | Standard |
| 50-55% | Strong |
| 55%+ | Very Strong / Nit |
| <45% | Weak / Calling Station |

---

## 9. Fold to Bet (Any Street)

### Definition
The percentage of times a player folds when facing a bet.

### Formula
```
Fold to Bet = (Times Folded to Bet) / (Times Faced Bet) × 100
```

### Calculation Rules
- **Numerator**: Count when player faces bet and folds
- **Denominator**: Count when player faces bet

---

## Implementation Notes

### For Natural8 Hand Histories

When parsing Natural8 hand history files, the following patterns are used:

1. **Showdown Detection**: Look for "showed" in summary lines
   ```
   Seat 4: Hero showed [5d 4d] and won (105,660) with two pair
   ```

2. **Won Detection**: Check for "won" in showdown lines
   ```
   175808c2 showed [3s As] and won (105,660) with two pair
   ```

3. **Preflop Aggressor**: The last raiser preflop (excluding blinds/antes)
   - Look for ": raises" actions in preflop section
   - If no raise, check for ": calls" actions

### Important Exclusions

1. **Walks**: When everyone folds to BB - VPIP denominator should NOT include this
2. **All-in Hands**: Some stats exclude all-in situations
3. **Uncalled Bets**: When a bet is returned, don't count as action

---

## Summary Table

| Stat | Numerator | Denominator |
|------|-----------|------------|
| VPIP | Voluntary preflop actions | Hands - Walks |
| PFR | Preflop raises | Hands - Walks |
| 3-Bet | 2nd raise preflop | Raised opportunity |
| CBet | Flop bet as PFR | PFR + saw flop |
| WTSD | Showed cards | Saw flop |
| W$SD | Won at showdown | Went to showdown |
| Fold to Bet | Faced bet + folded | Faced bet |

---

## References

- PokerTracker Statistical Reference Guide
- VPIP definition: percentage of hands voluntarily put money in pot
- 3-Bet definition: percentage of re-raises when faced with open-raise
- CBet definition: percentage of continuation bets after being preflop aggressor
