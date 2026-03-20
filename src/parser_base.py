from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class ActionType(Enum):
    """Enum for poker action types."""
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALLIN = "allin"


@dataclass
class Player:
    """Represents a player at the poker table."""
    screen_name: str
    seat: int
    stack: float
    is_hero: bool = False


@dataclass  
class Action:
    """Represents a player action during a hand."""
    player: str
    action_type: ActionType
    amount: float = 0
    street: str = "preflop"


@dataclass
class ParsedHand:
    """Represents a fully parsed poker hand."""
    hand_id: str
    table_name: str
    datetime: datetime
    players: List[Player]
    actions: List[Action]
    board: List[str]
    pot_total: float
    raw_text: str


class HandHistoryParser(ABC):
    """Abstract base class for hand history parsers.
    
    This class defines the interface that all site-specific 
    parsers must implement.
    """
    
    @abstractmethod
    def can_parse(self, content: str) -> bool:
        """Check if this parser can handle the given content.
        
        Args:
            content: Raw hand history text
            
        Returns:
            True if this parser can handle the content
        """
        pass
    
    @abstractmethod
    def parse_hand(self, content: str) -> Optional[ParsedHand]:
        """Parse hand history content into structured data.
        
        Args:
            content: Raw hand history text
            
        Returns:
            ParsedHand object if parsing succeeded, None otherwise
        """
        pass