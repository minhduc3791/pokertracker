import pytest
from abc import ABC

def test_parser_interface():
    """Test HandHistoryParser interface"""
    from src.parser_base import HandHistoryParser
    
    # Should be abstract and cannot be instantiated
    with pytest.raises(TypeError):
        HandHistoryParser()

def test_can_parse_method():
    """Test can_parse method contract"""
    from src.parser_base import HandHistoryParser
    
    # Create a test parser that implements required methods
    class TestParser(HandHistoryParser):
        def can_parse(self, content: str) -> bool:
            return True
        
        def parse_hand(self, content: str):
            return None
    
    # Should be able to instantiate subclass
    parser = TestParser()
    assert parser.can_parse("test") == True

def test_data_models():
    """Test data model definitions"""
    from src.parser_base import ParsedHand, Player, Action, ActionType
    from datetime import datetime
    
    # Test Player dataclass
    player = Player("TestPlayer", 1, 100.0, False)
    assert player.screen_name == "TestPlayer"
    assert player.seat == 1
    assert player.stack == 100.0
    assert player.is_hero == False
    
    # Test Action dataclass
    action = Action("TestPlayer", ActionType.BET, 10.0, "preflop")
    assert action.player == "TestPlayer"
    assert action.action_type == ActionType.BET
    assert action.amount == 10.0
    assert action.street == "preflop"
    
    # Test ParsedHand dataclass
    hand = ParsedHand(
        hand_id="TEST123",
        table_name="Test Table",
        datetime=datetime.now(),
        players=[player],
        actions=[action],
        board=["As", "Ks"],
        pot_total=20.0,
        raw_text="test hand"
    )
    assert hand.hand_id == "TEST123"
    assert len(hand.players) == 1
    assert len(hand.actions) == 1