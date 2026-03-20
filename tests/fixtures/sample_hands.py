"""GGPoker (Natural8) hand history samples for testing."""

import os
from pathlib import Path

SAMPLE_DIR = Path(__file__).parent.parent.parent / "hand-histories"

def _load_sample(filename: str) -> str:
    """Load a hand sample from the hand-histories directory."""
    for subdir in SAMPLE_DIR.iterdir():
        if subdir.is_dir():
            filepath = subdir / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
    raise FileNotFoundError(f"Could not find {filename} in hand-histories")

CASH_GAME_HAND = """Poker Hand #TM5646842611: Tournament #266809695, Bounty Hunters Mini Big Game $10.80 Hold'em No Limit - Level5(800/1,600(250)) - 2026/03/01 12:34:10
Table '5' 8-max Seat #2 is the button
Seat 1: 742d0fa7 (583,567 in chips)
Seat 2: 8b1e4ffd (98,200 in chips)
Seat 3: 25f485e1 (842,751 in chips)
Seat 4: Hero (42,480 in chips)
Seat 5: 9a330436 (96,720 in chips)
Seat 6: 758258a1 (83,634 in chips)
Seat 7: 175808c2 (100,000 in chips)
Seat 8: a8a349 (325,292 in chips)
8b1e4ffd: posts the ante 250
742d0fa7: posts the ante 250
758258a1: posts the ante 250
Hero: posts the ante 250
9a330436: posts the ante 250
25f485e1: posts the ante 250
a8a349: posts the ante 250
175808c2: posts the ante 250
25f485e1: posts small blind 800
Hero: posts big blind 1,600
*** HOLE CARDS ***
Dealt to 742d0fa7 
Dealt to 8b1e4ffd 
Dealt to 25f485e1 
Dealt to Hero [5d 4d]
Dealt to 9a330436 
Dealt to 758258a1 
Dealt to 175808c2 
Dealt to a8a349 
9a330436: folds
758258a1: raises 3,200 to 4,800
175808c2: calls 4,800
a8a349: folds
742d0fa7: folds
8b1e4ffd: folds
25f485e1: calls 4,000
Hero: calls 3,200
*** FLOP *** [2h 8s 6c]
25f485e1: checks
Hero: checks
758258a1: checks
175808c2: checks
*** TURN *** [2h 8s 6c] [6s]
25f485e1: bets 9,600
Hero: calls 9,600
758258a1: folds
175808c2: raises 25,000 to 34,600
25f485e1: folds
Hero: raises 2,830 to 37,430 and is all-in
175808c2: calls 2,830
Hero: shows [5d 4d] (a pair of Sixes)
175808c2: shows [3s As] (a pair of Sixes)
*** RIVER *** [2h 8s 6c 6s] [Ah]
*** SHOWDOWN ***
175808c2 collected 105,660 from pot
*** SUMMARY ***
Total pot 105,660 | Rake 0 | Jackpot 0 | Bingo 0 | Fortune 0 | Tax 0
Board [2h 8s 6c 6s Ah]
Seat 1: 742d0fa7 folded before Flop
Seat 2: 8b1e4ffd (button) folded before Flop
Seat 3: 25f485e1 (small blind) folded on the Turn
Seat 4: Hero (big blind) showed [5d 4d] and lost with a pair of Sixes
Seat 5: 9a330436 folded before Flop
Seat 6: 758258a1 folded on the Turn
Seat 7: 175808c2 showed [3s As] and won (105,660) with two pair, Aces and Sixes
Seat 8: a8a349 folded before Flop"""

TOURNAMENT_HAND = """Poker Hand #TM5646842600: Tournament #266809695, Bounty Hunters Mini Big Game $10.80 Hold'em No Limit - Level5(800/1,600(250)) - 2026/03/01 12:33:20
Table '5' 8-max Seat #1 is the button
Seat 1: 742d0fa7 (590,217 in chips)
Seat 2: 8b1e4ffd (99,250 in chips)
Seat 3: 25f485e1 (849,401 in chips)
Seat 4: Hero (42,730 in chips)
Seat 5: 9a330436 (96,970 in chips)
Seat 6: 758258a1 (68,534 in chips)
Seat 8: a8a349 (325,542 in chips)
8b1e4ffd: posts the ante 250
742d0fa7: posts the ante 250
758258a1: posts the ante 250
Hero: posts the ante 250
9a330436: posts the ante 250
25f485e1: posts the ante 250
a8a349: posts the ante 250
8b1e4ffd: posts small blind 800
25f485e1: posts big blind 1,600
*** HOLE CARDS ***
Dealt to 742d0fa7 
Dealt to 8b1e4ffd 
Dealt to 25f485e1 
Dealt to Hero [6s Qd]
Dealt to 9a330436 
Dealt to 758258a1 
Dealt to a8a349 
Hero: folds
9a330436: folds
758258a1: raises 1,600 to 3,200
a8a349: folds
742d0fa7: calls 3,200
8b1e4ffd: folds
25f485e1: calls 1,600
*** FLOP *** [2c 3d Tc]
25f485e1: bets 3,200
758258a1: calls 3,200
742d0fa7: calls 3,200
*** TURN *** [2c 3d Tc] [8c]
25f485e1: checks
758258a1: checks
742d0fa7: checks
*** RIVER *** [2c 3d Tc 8c] [Kc]
25f485e1: checks
758258a1: bets 7,178
742d0fa7: folds
25f485e1: folds
Uncalled bet (7,178) returned to 758258a1
*** SHOWDOWN ***
758258a1 collected 21,750 from pot
*** SUMMARY ***
Total pot 21,750 | Rake 0 | Jackpot 0 | Bingo 0 | Fortune 0 | Tax 0
Board [2c 3d Tc 8c Kc]
Seat 1: 742d0fa7 (button) folded on the River
Seat 2: 8b1e4ffd (small blind) folded before Flop
Seat 3: 25f485e1 (big blind) folded on the River
Seat 4: Hero folded before Flop
Seat 5: 9a330436 folded before Flop
Seat 6: 758258a1 won (21,750)
Seat 8: a8a349 folded before Flop"""

ALL_IN_HAND = """Poker Hand #TM5646842575: Tournament #266809695, Bounty Hunters Mini Big Game $10.80 Hold'em No Limit - Level5(800/1,600(250)) - 2026/03/01 12:32:05
Table '5' 8-max Seat #7 is the button
Seat 1: 742d0fa7 (592,067 in chips)
Seat 2: 8b1e4ffd (99,500 in chips)
Seat 3: 25f485e1 (693,717 in chips)
Seat 4: Hero (42,980 in chips)
Seat 5: 9a330436 (97,220 in chips)
Seat 6: 758258a1 (68,784 in chips)
Seat 7: 537383d6 (121,795 in chips)
Seat 8: 666a79db (31,039 in chips)
8b1e4ffd: posts the ante 250
742d0fa7: posts the ante 250
758258a1: posts the ante 250
Hero: posts the ante 250
9a330436: posts the ante 250
25f485e1: posts the ante 250
537383d6: posts the ante 250
666a79db: posts the ante 250
666a79db: posts small blind 800
742d0fa7: posts big blind 1,600
*** HOLE CARDS ***
Dealt to 742d0fa7 
Dealt to 8b1e4ffd 
Dealt to 25f485e1 
Dealt to Hero [As Ks]
Dealt to 9a330436 
Dealt to 758258a1 
Dealt to 537383d6 
Dealt to 666a79db 
9a330436: folds
758258a1: raises 3,200 to 4,800
537383d6: calls 4,800
666a79db: calls 4,000
742d0fa7: folds
8b1e4ffd: folds
25f485e1: calls 4,800
Hero: raises 37,430 to 42,230 and is all-in
9a330436: folds
758258a1: calls 37,430
537383d6: calls 37,430
25f485e1: folds
*** FLOP *** [Ah Kh Qh]
*** TURN *** [Ah Kh Qh] [Jc]
*** RIVER *** [Ah Kh Qh Jc] [2d]
*** SHOWDOWN ***
Hero: shows [As Ks] (a flush, Ace-high)
758258a1: shows [Ac Ad] (two pair, Aces and Kings)
537383d6: shows [Kc Kd] (three of a kind, Kings)
666a79db: shows [Qh Qd] (three of a kind, Queens)
Hero: wins 186,940"""

SPLIT_POT_HAND = """Poker Hand #TM5646842601: Tournament #266809695, Hold'em No Limit - Level5(800/1,600(250)) - 2026/03/01 12:33:30
Table '6' 6-max Seat #3 is the button
Seat 1: player1 (100,000 in chips)
Seat 2: player2 (80,000 in chips)
Seat 3: Hero (60,000 in chips)
Seat 4: player3 (120,000 in chips)
Seat 5: player4 (90,000 in chips)
Seat 6: player5 (110,000 in chips)
player1: posts the ante 250
player2: posts the ante 250
Hero: posts the ante 250
player3: posts the ante 250
player4: posts the ante 250
player5: posts the ante 250
player1: posts small blind 800
player2: posts big blind 1,600
*** HOLE CARDS ***
Dealt to player1 
Dealt to player2 
Dealt to Hero [7h 7d]
Dealt to player3 
Dealt to player4 
Dealt to player5 
Hero: raises 3,200 to 4,800
player3: calls 4,800
player4: calls 4,800
player5: calls 4,800
player1: calls 4,000
player2: calls 3,200
*** FLOP *** [7s 8c 9c]
player1: checks
player2: checks
Hero: bets 9,600
player3: calls 9,600
player4: calls 9,600
player5: calls 9,600
player1: folds
player2: folds
*** TURN *** [7s 8c 9c] [2c]
Hero: bets 24,000
player3: calls 24,000
player4: calls 24,000
player5: calls 24,000
*** RIVER *** [7s 8c 9c 2c] [7c]
Hero: bets 51,600 and is all-in
player3: calls 51,600
player4: calls 51,600
player5: calls 51,600
*** SHOWDOWN ***
Hero: shows [7h 7d] (full house, Sevens full of Sevens)
player3: shows [9h 9s] (full house, Nines full of Sevens)
player4: shows [Ac Ah] (two pair, Aces and Sevens)
player5: shows [Kc Ks] (two pair, Kings and Sevens)
*** SUMMARY ***
Total pot 320,000 | Rake 0 | Jackpot 0 | Bingo 0 | Fortune 0 | Tax 0
Board [7s 8c 9c 2c 7c]
Seat 1: player1 (small blind) folded before Flop
Seat 2: player2 (big blind) folded before Flop
Seat 3: Hero (button) showed [7h 7d] and won (160,000) with full house, Sevens full of Sevens
Seat 4: player3 showed [9h 9s] and won (160,000) with full house, Nines full of Sevens
Seat 5: player4 folded on the River
Seat 6: player5 folded on the River"""

STRADDLE_HAND = """Poker Hand #TM5646842602: Tournament #266809695, Hold'em No Limit - Level5(800/1,600(250)) - 2026/03/01 12:34:00
Table '6' 6-max Seat #2 is the button
Seat 1: player1 (100,000 in chips)
Seat 2: Hero (80,000 in chips)
Seat 3: player2 (120,000 in chips)
Seat 4: player3 (90,000 in chips)
Seat 5: player4 (110,000 in chips)
Seat 6: player5 (60,000 in chips)
player1: posts the ante 250
Hero: posts the ante 250
player2: posts the ante 250
player3: posts the ante 250
player4: posts the ante 250
player5: posts the ante 250
player1: posts small blind 800
player2: posts big blind 1,600
Hero: posts straddle 3,200
player3: calls 3,200
player4: folds
player5: raises 12,800 to 16,000
player1: folds
player2: calls 14,400
Hero: calls 12,800
player3: calls 12,800
*** FLOP *** [Ah Kd Qc]
player2: checks
Hero: checks
player3: checks
player5: bets 32,000
player2: folds
Hero: folds
player3: folds
Uncalled bet (32,000) returned to player5
*** SUMMARY ***
Total pot 68,400 | Rake 0 | Jackpot 0 | Bingo 0 | Fortune 0 | Tax 0
Board [Ah Kd Qc]
Seat 1: player1 (small blind) folded before Flop
Seat 2: Hero (button) folded on the Flop
Seat 3: player2 (big blind) folded before Flop
Seat 4: player3 folded on the Flop
Seat 5: player4 folded before Flop
Seat 6: player5 won (68,400)"""

def get_all_samples() -> dict:
    """Return all sample hands as a dictionary."""
    return {
        'cash_game': CASH_GAME_HAND,
        'tournament': TOURNAMENT_HAND,
        'all_in': ALL_IN_HAND,
        'split_pot': SPLIT_POT_HAND,
        'straddle': STRADDLE_HAND,
    }
