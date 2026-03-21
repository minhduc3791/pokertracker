"""Tests for StatsEngine."""

import pytest
from datetime import datetime
from src.stats_engine import StatsEngine, StatType
from src.parser_base import ParsedHand, Player, Action, ActionType
from src.database import DatabaseManager
from src.config import ConfigManager


class TestStatsEngine:
    """Test suite for StatsEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.db = DatabaseManager(":memory:")
        self.config = ConfigManager()
        self.config.set("hero_screen_name", "Hero")
        self.stats = StatsEngine(self.db, self.config)

    def teardown_method(self):
        """Clean up after tests."""
        self.db.close()

    def _create_parsed_hand(self, actions, players=None, board=None):
        """Helper to create a parsed hand for testing."""
        if players is None:
            players = [
                Player(screen_name="Hero", seat=1, stack=10000, is_hero=False),
                Player(screen_name="Villain", seat=2, stack=10000, is_hero=False),
            ]
        if board is None:
            board = ["2h", "3d", "4s"]
        
        return ParsedHand(
            hand_id="TM123456",
            table_name="1",
            datetime=datetime.now(),
            players=players,
            actions=actions,
            board=board,
            pot_total=100,
            raw_text="Test hand"
        )

    def test_vpip_increments_for_voluntary_action(self):
        """Test that VPIP increments when player puts money in voluntarily."""
        actions = [
            Action(player="Villain", action_type=ActionType.BET, amount=100, street="preflop"),
            Action(player="Hero", action_type=ActionType.CALL, amount=100, street="preflop"),
            Action(player="Villain", action_type=ActionType.CHECK, amount=0, street="flop"),
            Action(player="Hero", action_type=ActionType.CHECK, amount=0, street="flop"),
            Action(player="Villain", action_type=ActionType.BET, amount=200, street="flop"),
            Action(player="Hero", action_type=ActionType.FOLD, amount=0, street="flop"),
        ]
        hand = self._create_parsed_hand(actions)
        self.stats.process_hand(hand)
        
        hero_id = self.db.get_or_create_player("Hero", is_hero=True)
        stats = self.db.get_player_stats(hero_id, "1")
        
        assert StatType.VPIP.value in stats
        assert stats[StatType.VPIP.value][0] == 1
        assert stats[StatType.VPIP.value][1] == 1

    def test_vpip_increments_on_call(self):
        """Test that VPIP increments when player calls."""
        actions = [
            Action(player="Villain", action_type=ActionType.RAISE, amount=100, street="preflop"),
            Action(player="Hero", action_type=ActionType.CALL, amount=100, street="preflop"),
            Action(player="Villain", action_type=ActionType.CHECK, amount=0, street="flop"),
            Action(player="Hero", action_type=ActionType.CHECK, amount=0, street="flop"),
            Action(player="Villain", action_type=ActionType.CHECK, amount=0, street="turn"),
            Action(player="Hero", action_type=ActionType.CHECK, amount=0, street="turn"),
        ]
        hand = self._create_parsed_hand(actions, board=[])
        self.stats.process_hand(hand)
        
        hero_id = self.db.get_or_create_player("Hero", is_hero=True)
        stats = self.db.get_player_stats(hero_id, "1")
        
        assert StatType.VPIP.value in stats
        assert stats[StatType.VPIP.value][0] == 1

    def test_stats_are_stored_in_database(self):
        """Test that stats are properly stored in the database."""
        actions = [
            Action(player="Villain", action_type=ActionType.BET, amount=100, street="preflop"),
            Action(player="Hero", action_type=ActionType.CALL, amount=100, street="preflop"),
            Action(player="Villain", action_type=ActionType.CHECK, amount=0, street="flop"),
            Action(player="Hero", action_type=ActionType.CHECK, amount=0, street="flop"),
        ]
        hand = self._create_parsed_hand(actions)
        self.stats.process_hand(hand)
        
        hero_id = self.db.get_or_create_player("Hero", is_hero=True)
        stats = self.db.get_player_stats(hero_id, "1")
        
        assert len(stats) > 0

    def test_all_stat_types_defined(self):
        """Test that all expected stat types are defined."""
        expected_stats = [
            StatType.VPIP,
            StatType.THREE_BET,
            StatType.FOLD_TO_BET,
            StatType.CBET_TURN,
            StatType.WTSD,
            StatType.W_SD,
        ]
        for stat in expected_stats:
            assert stat.value is not None

    def test_hero_identification_from_hero_string(self):
        """Test that 'Hero' player is correctly identified."""
        assert self.stats._identify_hero("Hero") is True
        assert self.stats._identify_hero("OtherPlayer") is False

    def test_hero_identification_from_config(self):
        """Test that hero can be identified from config."""
        self.config.set("hero_screen_name", "MyScreenName")
        assert self.stats._identify_hero("MyScreenName") is True

    def test_hero_stored_with_is_hero_flag(self):
        """Test that hero is stored with is_hero=True in database."""
        actions = [
            Action(player="Villain", action_type=ActionType.FOLD, amount=0, street="preflop"),
        ]
        hand = self._create_parsed_hand(actions, board=[])
        self.stats.process_hand(hand)
        
        hero_id = self.db.get_or_create_player("Hero", is_hero=True)
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT is_hero FROM players WHERE id=?", (hero_id,))
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == 1
