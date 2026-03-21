"""Statistics viewer for PokerTracker - detailed player statistics."""

import os
import sys
from typing import Dict, List, Optional

from src.database import DatabaseManager
from src.config import ConfigManager


STAT_DESCRIPTIONS = {
    'VPIP': ('Voluntarily Put In Pot', 'preflop'),
    '3BET': ('3-Bet', 'preflop'),
    'F_TB': ('Fold to Bet', 'postflop'),
    'CALL_CB': ('Call CBet', 'flop'),
    'RAISE_CB': ('Raise CBet', 'flop'),
    'CB_TURN': ('CBet Turn', 'turn'),
    'F_CB_T': ('Fold CBet Turn', 'turn'),
    'C_CB_T': ('Call CBet Turn', 'turn'),
    'R_CB_T': ('Raise CBet Turn', 'turn'),
    'WTSD': ('Went to Showdown', 'showdown'),
    'W$SD': ('Won $ at Showdown', 'showdown'),
}

HUD_STATS = ['VPIP', '3BET', 'WTSD', 'W$SD']


class StatsViewer:
    """Console-based statistics viewer for PokerTracker."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize viewer.
        
        Args:
            db_path: Path to database file
        """
        if db_path is None:
            config = ConfigManager()
            db_path = config.get('database_path', 'poker_tracker.db')
        
        self.db = DatabaseManager(db_path)
        self.current_player: Optional[Dict] = None
        self.players: List[Dict] = []
        self.sort_key = 'hands_played'
        self.sort_reverse = True

    def clear_screen(self):
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def format_stat(self, stat_name: str, num: int, den: int) -> str:
        """Format a stat for display.
        
        Args:
            stat_name: Stat name
            num: Numerator
            den: Denominator
            
        Returns:
            Formatted string like "25% (50/200)"
        """
        if den == 0:
            return "—"
        pct = round(num / den * 100)
        return f"{pct}% ({num}/{den})"

    def calculate_stat_class(self, stat_name: str, pct: float) -> str:
        """Determine stat classification (tight/optimal/loose).
        
        Args:
            stat_name: Stat name
            pct: Percentage value
            
        Returns:
            Classification string
        """
        if stat_name == 'VPIP':
            if pct < 20:
                return 'Tight'
            elif pct < 35:
                return 'Normal'
            else:
                return 'Loose'
        elif stat_name == '3BET':
            if pct < 5:
                return 'Tight'
            elif pct < 10:
                return 'Normal'
            else:
                return 'Loose'
        elif stat_name == 'WTSD':
            if pct < 25:
                return 'Tight'
            elif pct < 35:
                return 'Normal'
            else:
                return 'Loose'
        elif stat_name == 'W$SD':
            if pct < 45:
                return 'Weak'
            elif pct < 55:
                return 'Normal'
            else:
                return 'Strong'
        return ''

    def show_header(self):
        """Display the viewer header."""
        print("=" * 80)
        print("  POKERTRACKER - PLAYER STATISTICS VIEWER")
        print("=" * 80)
        total_hands = self.db.get_hand_count()
        total_players = self.db.get_player_count()
        print(f"  Total Hands: {total_hands}  |  Total Players: {total_players}")
        print("-" * 80)

    def show_player_list(self):
        """Display list of players with summary stats."""
        self.players = self.db.get_player_summary()
        
        if not self.players:
            print("\n  No players found in database.")
            print("  Start playing hands to see statistics!\n")
            return

        self.players.sort(
            key=lambda x: x.get(self.sort_key, 0) or 0,
            reverse=self.sort_reverse
        )

        print("\n  PLAYER LIST (type number to view details, q to quit)")
        print("  " + "-" * 76)
        print(f"  {'#':<4} {'Player':<20} {'Hands':<8} {'VPIP':<12} {'3B':<12} {'WTSD':<12} {'W$SD':<12}")
        print("  " + "-" * 76)

        for i, player in enumerate(self.players, 1):
            stats = player.get('stats', {})
            vpip_data = stats.get('VPIP', (0, 0))
            three_bet_data = stats.get('3BET', (0, 0))
            wtsd_data = stats.get('WTSD', (0, 0))
            w_sd_data = stats.get('W$SD', (0, 0))

            vpip = self.format_stat('VPIP', *vpip_data).split()[0]
            three_bet = self.format_stat('3BET', *three_bet_data).split()[0]
            wtsd = self.format_stat('WTSD', *wtsd_data).split()[0]
            w_sd = self.format_stat('W$SD', *w_sd_data).split()[0]

            hero_marker = " *" if player.get('is_hero') else ""
            hands = player.get('hands_played', 0) or 0
            
            print(f"  {i:<4} {player['screen_name'][:18]:<20} {hands:<8} {vpip:<12} {three_bet:<12} {wtsd:<12} {w_sd:<12}{hero_marker}")

        print("  " + "-" * 76)
        print(f"  * = Hero (your account)")
        print("\n  Commands: [n] Next page  [p] Previous page  [s] Sort options  [q] Quit")

    def show_player_detail(self, player: Dict):
        """Display detailed statistics for a player.
        
        Args:
            player: Player dict from get_player_summary
        """
        self.clear_screen()
        stats = player.get('stats', {})
        tables = self.db.get_tables_for_player(player['id'])
        
        print("=" * 80)
        print(f"  PLAYER: {player['screen_name']} {'(HERO)' if player.get('is_hero') else ''}")
        print("=" * 80)
        print(f"\n  Overview:")
        print(f"  {'Hands Played:':<20} {player.get('hands_played', 0) or 0}")
        print(f"  {'Tables:':<20} {len(tables)}")
        print(f"  {'Table Names:':<20} {', '.join(tables[:5])}{'...' if len(tables) > 5 else ''}")

        print("\n  " + "=" * 78)
        print("  PREFLOP STATISTICS")
        print("  " + "-" * 78)
        
        vpip_data = stats.get('VPIP', (0, 0))
        three_bet_data = stats.get('3BET', (0, 0))
        f_tb_data = stats.get('F_TB', (0, 0))

        vpip_pct = round(vpip_data[0] / vpip_data[1] * 100) if vpip_data[1] else 0
        print(f"  VPIP  - Voluntarily Put In Pot")
        print(f"         {self.format_stat('VPIP', *vpip_data):<15} [{self.calculate_stat_class('VPIP', vpip_pct):<8}]")
        
        three_bet_pct = round(three_bet_data[0] / three_bet_data[1] * 100) if three_bet_data[1] else 0
        print(f"  3BET  - 3-Bet Percentage")
        print(f"         {self.format_stat('3BET', *three_bet_data):<15} [{self.calculate_stat_class('3BET', three_bet_pct):<8}]")
        
        print(f"  F_TB  - Fold to Bet (facing bets)")
        print(f"         {self.format_stat('F_TB', *f_tb_data):<15}")

        print("\n  " + "=" * 78)
        print("  POSTFLOP STATISTICS")
        print("  " + "-" * 78)
        
        call_cbet_data = stats.get('CALL_CB', (0, 0))
        raise_cbet_data = stats.get('RAISE_CB', (0, 0))
        cbet_turn_data = stats.get('CB_TURN', (0, 0))
        
        print(f"  CBet Flop:")
        print(f"    Call    - {self.format_stat('CALL_CB', *call_cbet_data):<15}")
        print(f"    Raise   - {self.format_stat('RAISE_CB', *raise_cbet_data):<15}")
        
        print(f"\n  CBet Turn:")
        print(f"    Barrel  - {self.format_stat('CB_TURN', *cbet_turn_data):<15}")

        f_cb_t_data = stats.get('F_CB_T', (0, 0))
        c_cb_t_data = stats.get('C_CB_T', (0, 0))
        r_cb_t_data = stats.get('R_CB_T', (0, 0))
        
        print(f"\n  Facing Turn Bet:")
        print(f"    Fold    - {self.format_stat('F_CB_T', *f_cb_t_data):<15}")
        print(f"    Call    - {self.format_stat('C_CB_T', *c_cb_t_data):<15}")
        print(f"    Raise   - {self.format_stat('R_CB_T', *r_cb_t_data):<15}")

        print("\n  " + "=" * 78)
        print("  SHOWDOWN STATISTICS")
        print("  " + "-" * 78)
        
        wtsd_data = stats.get('WTSD', (0, 0))
        w_sd_data = stats.get('W$SD', (0, 0))
        
        wtsd_pct = round(wtsd_data[0] / wtsd_data[1] * 100) if wtsd_data[1] else 0
        w_sd_pct = round(w_sd_data[0] / w_sd_data[1] * 100) if w_sd_data[1] else 0
        
        print(f"  WTSD  - Went to Showdown")
        print(f"         {self.format_stat('WTSD', *wtsd_data):<15} [{self.calculate_stat_class('WTSD', wtsd_pct):<8}]")
        
        print(f"  W$SD  - Won Money at Showdown")
        print(f"         {self.format_stat('W$SD', *w_sd_data):<15} [{self.calculate_stat_class('W$SD', w_sd_pct):<8}]")

        print("\n  " + "=" * 78)
        print("\n  Commands: [b] Back to list  [h] View recent hands  [q] Quit")

    def show_recent_hands(self, player: Dict):
        """Show recent hands for a player.
        
        Args:
            player: Player dict
        """
        self.clear_screen()
        print("=" * 80)
        print(f"  RECENT HANDS - {player['screen_name']}")
        print("=" * 80)
        
        hands = self.db.get_recent_hands_for_player(player['id'], limit=20)
        
        if not hands:
            print("\n  No hands found.")
        else:
            print(f"\n  Showing last {len(hands)} hands:\n")
            for i, hand in enumerate(hands[:10], 1):
                datetime_str = hand.get('datetime', 'Unknown')[:19]
                table = hand.get('table_name', 'Unknown')
                print(f"  {i}. {datetime_str}")
                print(f"     Table: {table}")
                parsed = hand.get('parsed_data', {})
                players = parsed.get('players', [])
                print(f"     Players: {', '.join([p[0] for p in players[:6]])}...")
                pot = parsed.get('pot_total', 0)
                print(f"     Pot: ${pot}")
                print()

        print("  Commands: [b] Back to player  [q] Quit")

    def run(self):
        """Run the interactive viewer."""
        mode = 'list'
        
        while True:
            if mode == 'list':
                self.clear_screen()
                self.show_header()
                self.show_player_list()
                
                try:
                    choice = input("\n  Enter number to view player, 'q' to quit: ").strip().lower()
                    
                    if choice == 'q':
                        break
                    elif choice == 's':
                        print("\n  Sort by: [1] Hands  [2] VPIP  [3] Name")
                        sort_choice = input("  Choice: ").strip()
                        if sort_choice == '1':
                            self.sort_key = 'hands_played'
                        elif sort_choice == '2':
                            self.sort_key = 'vpip'
                        elif sort_choice == '3':
                            self.sort_key = 'screen_name'
                        mode = 'list'
                    else:
                        try:
                            idx = int(choice) - 1
                            if 0 <= idx < len(self.players):
                                self.current_player = self.players[idx]
                                mode = 'detail'
                        except ValueError:
                            pass
                except (EOFError, KeyboardInterrupt):
                    break
                    
            elif mode == 'detail':
                self.show_player_detail(self.current_player)
                
                try:
                    choice = input("\n  Command: ").strip().lower()
                    
                    if choice == 'q':
                        break
                    elif choice == 'b':
                        mode = 'list'
                    elif choice == 'h':
                        mode = 'hands'
                except (EOFError, KeyboardInterrupt):
                    break
                    
            elif mode == 'hands':
                self.show_recent_hands(self.current_player)
                
                try:
                    choice = input("\n  Command: ").strip().lower()
                    
                    if choice == 'q':
                        break
                    elif choice == 'b':
                        mode = 'detail'
                except (EOFError, KeyboardInterrupt):
                    break

        print("\n  Thanks for using PokerTracker!\n")
        self.db.close()


def main():
    """Main entry point for the viewer."""
    import argparse
    
    parser = argparse.ArgumentParser(description='PokerTracker Statistics Viewer')
    parser.add_argument('--db', '-d', help='Database path', default=None)
    args = parser.parse_args()
    
    viewer = StatsViewer(db_path=args.db)
    viewer.run()


if __name__ == '__main__':
    main()
