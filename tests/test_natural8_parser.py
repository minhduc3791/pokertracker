"""Tests for Natural8Parser."""

import pytest
from datetime import datetime
from src.natural8_parser import Natural8Parser
from src.parser_base import ParsedHand, Player, Action, ActionType
from tests.fixtures.sample_hands import (
    CASH_GAME_HAND,
    TOURNAMENT_HAND,
    ALL_IN_HAND,
    SPLIT_POT_HAND,
    STRADDLE_HAND,
)


class TestNatural8Parser:
    """Test suite for Natural8Parser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = Natural8Parser()

    def test_can_parse_returns_true_for_gg_format(self):
        """Test that can_parse returns True for GG format hands."""
        assert self.parser.can_parse(CASH_GAME_HAND) is True
        assert self.parser.can_parse(TOURNAMENT_HAND) is True
        assert self.parser.can_parse(ALL_IN_HAND) is True

    def test_can_parse_returns_false_for_other_formats(self):
        """Test that can_parse returns False for non-GG formats."""
        other_format = "PokerStars Hand #123: Hold'em No Limit"
        assert self.parser.can_parse(other_format) is False

    def test_parse_hand_extracts_hand_id(self):
        """Test that parse_hand correctly extracts hand ID."""
        result = self.parser.parse_hand(CASH_GAME_HAND)
        assert result is not None
        assert "TM5646842611" in result.hand_id

    def test_parse_hand_extracts_table_name(self):
        """Test that parse_hand extracts table name."""
        result = self.parser.parse_hand(CASH_GAME_HAND)
        assert result is not None
        assert result.table_name == "5"

    def test_parse_hand_extracts_datetime(self):
        """Test that parse_hand extracts datetime."""
        result = self.parser.parse_hand(CASH_GAME_HAND)
        assert result is not None
        assert isinstance(result.datetime, datetime)
        assert result.datetime.year == 2026
        assert result.datetime.month == 3
        assert result.datetime.day == 1

    def test_parse_hand_extracts_players(self):
        """Test that parse_hand extracts all players."""
        result = self.parser.parse_hand(CASH_GAME_HAND)
        assert result is not None
        assert len(result.players) == 8
        screen_names = [p.screen_name for p in result.players]
        assert "742d0fa7" in screen_names
        assert "Hero" in screen_names

    def test_parse_hand_extracts_hero_player_name(self):
        """Test that parse_hand extracts 'Hero' as a player name from hand history."""
        result = self.parser.parse_hand(CASH_GAME_HAND)
        assert result is not None
        hero = next((p for p in result.players if p.screen_name == "Hero"), None)
        assert hero is not None
        assert hero.is_hero is False

    def test_parse_hand_extracts_actions(self):
        """Test that parse_hand extracts actions by street."""
        result = self.parser.parse_hand(CASH_GAME_HAND)
        assert result is not None
        assert len(result.actions) > 0
        action_players = [a.player for a in result.actions]
        assert "9a330436" in action_players

    def test_parse_hand_extracts_board(self):
        """Test that parse_hand extracts board cards."""
        result = self.parser.parse_hand(CASH_GAME_HAND)
        assert result is not None
        assert len(result.board) == 5
        assert "2h" in result.board
        assert "8s" in result.board
        assert "6c" in result.board

    def test_parse_hand_handles_all_in_scenario(self):
        """Test that parse_hand handles all-in scenarios correctly."""
        result = self.parser.parse_hand(ALL_IN_HAND)
        assert result is not None
        all_in_actions = [a for a in result.actions if a.action_type == ActionType.ALLIN]
        assert len(all_in_actions) > 0

    def test_parse_hand_handles_split_pot(self):
        """Test that parse_hand handles split pot scenarios."""
        result = self.parser.parse_hand(SPLIT_POT_HAND)
        assert result is not None
        assert "wins" in result.raw_text.lower() or "won" in result.raw_text.lower()

    def test_parse_hand_calculates_pot_total(self):
        """Test that parse_hand calculates total pot."""
        result = self.parser.parse_hand(CASH_GAME_HAND)
        assert result is not None
        assert result.pot_total > 0

    def test_parse_tournament_hand(self):
        """Test parsing of tournament hands."""
        result = self.parser.parse_hand(TOURNAMENT_HAND)
        assert result is not None
        assert result.hand_id.startswith("TM")

    def test_parse_straddle_hand(self):
        """Test parsing of straddle hands."""
        result = self.parser.parse_hand(STRADDLE_HAND)
        assert result is not None
        assert len(result.players) == 6
