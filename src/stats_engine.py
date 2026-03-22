"""Poker statistics calculation engine."""

import logging
from enum import Enum
from typing import List
from src.parser_base import ParsedHand, Action, ActionType
from src.database import DatabaseManager
from src.config import ConfigManager


logger = logging.getLogger(__name__)


class StatType(Enum):
    """Enum for all tracked poker statistics."""
    VPIP = "VPIP"
    THREE_BET = "3BET"
    FOLD_TO_BET = "FOLD_TO_BET"
    CALL_CBET = "CALL_CBET"
    RAISE_CBET = "RAISE_CBET"
    CBET_TURN = "CBET_TURN"
    FOLD_CBET_TURN = "FOLD_CBET_TURN"
    CALL_CBET_TURN = "CALL_CBET_TURN"
    RAISE_CBET_TURN = "RAISE_CBET_TURN"
    WTSD = "WTSD"
    W_SD = "W$SD"


class StatsEngine:
    """Calculates and tracks poker statistics from parsed hands."""

    def __init__(self, db: DatabaseManager, config: ConfigManager):
        """Initialize stats engine.
        
        Args:
            db: Database manager for storing stats
            config: Configuration manager
        """
        self.db = db
        self.config = config

    def process_hand(self, parsed_hand: ParsedHand) -> None:
        """Process a parsed hand and update statistics.
        
        Args:
            parsed_hand: ParsedHand from the parser
        """
        preflop_actions = [a for a in parsed_hand.actions if a.street == "preflop"]
        flop_actions = [a for a in parsed_hand.actions if a.street == "flop"]
        turn_actions = [a for a in parsed_hand.actions if a.street == "turn"]
        showdown_players = self._get_showdown_players(parsed_hand)
        hero = next((p for p in parsed_hand.players if p.is_hero), None)

        for player in parsed_hand.players:
            is_hero = self._identify_hero(player.screen_name)
            player_id = self.db.get_or_create_player(player.screen_name, is_hero=is_hero)
            
            self._update_vpip(player_id, parsed_hand.table_name, player, preflop_actions)
            self._update_three_bet(player_id, parsed_hand.table_name, player, preflop_actions)
            self._update_fold_to_bet(player_id, parsed_hand.table_name, player, preflop_actions)
            self._update_cbet(player_id, parsed_hand.table_name, player, flop_actions, preflop_actions)
            self._update_cbet_turn(player_id, parsed_hand.table_name, player, turn_actions, flop_actions)
            
            if player.screen_name in showdown_players:
                self.db.increment_stat(player_id, parsed_hand.table_name, StatType.WTSD.value, 0, 1)
                if self._player_won(parsed_hand, player.screen_name):
                    self.db.increment_stat(player_id, parsed_hand.table_name, StatType.W_SD.value, 1, 1)
                else:
                    self.db.increment_stat(player_id, parsed_hand.table_name, StatType.W_SD.value, 0, 1)

    def _identify_hero(self, player_name: str) -> bool:
        """Identify if a player is the hero.
        
        In GGPoker/Natural8 hand histories, "Hero" is the screen name of the
        current player. Other players are shown as hex strings.
        
        Args:
            player_name: Player's screen name
            
        Returns:
            True if this is the hero player
        """
        if player_name == "Hero":
            return True
        
        hero_screen_name = self.config.get("hero_screen_name")
        if hero_screen_name and player_name == hero_screen_name:
            return True
        
        return False

    def _is_voluntary_action(self, action: Action) -> bool:
        """Check if an action is voluntary (counts toward VPIP).
        
        Args:
            action: The action to check
            
        Returns:
            True if voluntary
        """
        if action.action_type in [ActionType.CALL, ActionType.RAISE, ActionType.BET]:
            if action.amount > 0:
                return True
        return False

    def _get_preflop_aggressor(self, actions: List[Action]) -> str:
        """Get the preflop aggressor (last raiser).
        
        Args:
            actions: Preflop actions
            
        Returns:
            Player name of aggressor, or empty string
        """
        raisers = [a.player for a in actions if a.action_type == ActionType.RAISE]
        if raisers:
            return raisers[-1]
        callers = [a.player for a in actions if a.action_type == ActionType.CALL]
        if callers:
            return callers[-1]
        return ""

    def _get_showdown_players(self, parsed_hand: ParsedHand) -> List[str]:
        """Get list of players who reached showdown.
        
        Args:
            parsed_hand: Parsed hand
            
        Returns:
            List of player names
        """
        showdown_players = []
        lines = parsed_hand.raw_text.split('\n')
        
        for line in lines:
            if 'showed' in line.lower():
                if ':' in line:
                    player = line.split(':')[0].strip()
                    if 'Seat' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            player = parts[1].strip().split()[0]
                    if player:
                        showdown_players.append(player)
        
        return list(set(showdown_players))

    def _player_won(self, parsed_hand: ParsedHand, player_name: str) -> bool:
        """Check if a player won the hand.
        
        Args:
            parsed_hand: Parsed hand
            player_name: Player name
            
        Returns:
            True if player won
        """
        for line in parsed_hand.raw_text.split('\n'):
            if 'showed' in line.lower() and player_name in line:
                if 'won' in line.lower():
                    return True
        return False

    def _update_vpip(self, player_id: int, table_name: str, player, actions: List[Action]) -> None:
        """Update VPIP (Voluntarily Put In Pot) stat.
        
        Args:
            player_id: Player ID
            table_name: Table name
            player: Player object
            actions: Hand actions
        """
        for action in actions:
            if action.player == player.screen_name and self._is_voluntary_action(action):
                self.db.increment_stat(player_id, table_name, StatType.VPIP.value, 1, 1)
                return
        self.db.increment_stat(player_id, table_name, StatType.VPIP.value, 0, 1)

    def _update_three_bet(self, player_id: int, table_name: str, player, actions: List[Action]) -> None:
        """Update 3-bet stat.
        
        A 3-bet is when a player makes the second raise preflop.
        Only counts for players who had the opportunity (entered pot voluntarily).
        
        Args:
            player_id: Player ID
            table_name: Table name
            player: Player object
            actions: Hand actions
        """
        if not actions:
            return
        
        player_raised = False
        raise_count = 0
        first_raiser = None
        
        for action in actions:
            if action.action_type == ActionType.RAISE:
                raise_count += 1
                if raise_count == 1:
                    first_raiser = action.player
                elif raise_count == 2 and action.player == player.screen_name:
                    player_raised = True
        
        if player_raised:
            self.db.increment_stat(player_id, table_name, StatType.THREE_BET.value, 1, 1)

    def _update_fold_to_bet(self, player_id: int, table_name: str, player, actions: List[Action]) -> None:
        """Update fold to bet stat (any street).
        
        Tracks when a player faces a bet and folds.
        
        Args:
            player_id: Player ID
            table_name: Table name
            player: Player object
            actions: Hand actions
        """
        facing_bet = False
        folded = False
        
        for action in actions:
            if action.player == player.screen_name:
                if action.action_type == ActionType.BET:
                    facing_bet = True
                elif action.action_type == ActionType.FOLD and facing_bet:
                    folded = True
                    break
        
        if facing_bet:
            if folded:
                self.db.increment_stat(player_id, table_name, StatType.FOLD_TO_BET.value, 1, 1)
            else:
                self.db.increment_stat(player_id, table_name, StatType.FOLD_TO_BET.value, 0, 1)

    def _update_cbet(self, player_id: int, table_name: str, player, flop_actions: List[Action],
                     preflop_actions: List[Action]) -> None:
        """Update continuation bet stat.
        
        Only the preflop aggressor can make a CBet.
        Only counts if there were flop actions and player was aggressor.
        
        Args:
            player_id: Player ID
            table_name: Table name
            player: Player object
            flop_actions: Flop actions
            preflop_actions: Preflop actions
        """
        preflop_aggressor = self._get_preflop_aggressor(preflop_actions)
        
        if not flop_actions or preflop_aggressor != player.screen_name:
            return
        
        for action in flop_actions:
            if action.player == player.screen_name and action.action_type == ActionType.BET:
                self.db.increment_stat(player_id, table_name, StatType.CBET_TURN.value, 1, 1)
                return
        
        self.db.increment_stat(player_id, table_name, StatType.CBET_TURN.value, 0, 1)

    def _update_cbet_turn(self, player_id: int, table_name: str, player, turn_actions: List[Action],
                          flop_actions: List[Action]) -> None:
        """Update turn barrel stat.
        
        Args:
            player_id: Player ID
            table_name: Table name
            player: Player object
            turn_actions: Turn actions
            flop_actions: Flop actions
        """
        if not turn_actions:
            return
        
        flop_bettor = None
        for action in flop_actions:
            if action.action_type == ActionType.BET:
                flop_bettor = action.player
                break
        
        if flop_bettor and flop_bettor == player.screen_name:
            for action in turn_actions:
                if action.player == player.screen_name and action.action_type == ActionType.BET:
                    self.db.increment_stat(player_id, table_name, StatType.RAISE_CBET_TURN.value, 1, 1)
                    return
        
        if flop_bettor and flop_bettor != player.screen_name:
            for action in turn_actions:
                if action.player == player.screen_name and action.action_type == ActionType.BET:
                    self.db.increment_stat(player_id, table_name, StatType.CALL_CBET_TURN.value, 1, 1)
                    return
                if action.player == player.screen_name and action.action_type == ActionType.FOLD:
                    self.db.increment_stat(player_id, table_name, StatType.FOLD_CBET_TURN.value, 1, 1)
                    return
