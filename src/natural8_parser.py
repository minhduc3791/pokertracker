"""Natural8 (GGPoker) hand history parser."""

import re
from datetime import datetime
from typing import List, Optional, Dict
from src.parser_base import HandHistoryParser, ParsedHand, Player, Action, ActionType


class Natural8Parser(HandHistoryParser):
    """Parser for GGPoker/Natural8 hand history files."""

    HAND_ID_PATTERN = re.compile(r'Poker Hand #(\w+):')
    TABLE_PATTERN = re.compile(r"Table '(\d+)'")
    SEAT_PATTERN = re.compile(r'Seat (\d+): (\S+) \(([\d,]+) in chips\)')
    BUTTON_PATTERN = re.compile(r"Seat #(\d+) is the button")
    HOLE_CARDS_START = re.compile(r'\*\*\* HOLE CARDS \*\*\*')
    FLOP_START = re.compile(r'\*\*\* FLOP \*\*\* \[([^\]]+)\]')
    TURN_START = re.compile(r'\*\*\* TURN \*\*\* \[[^\]]+\] \[([^\]]+)\]')
    RIVER_START = re.compile(r'\*\*\* RIVER \*\*\* \[[^\]]+\] \[([^\]]+)\]')
    ACTION_PATTERN = re.compile(r'(\S+): (posts (?:small blind|big blind|ante|straddle)|folds|checks|calls|bets|raises [\d,]+(?: to [\d,]+)?|is all-in|collected [\d,]+)')
    SHOWDOWN_START = re.compile(r'\*\*\* SHOWDOWN \*\*\*')
    SUMMARY_START = re.compile(r'\*\*\* SUMMARY \*\*\*')
    POT_PATTERN = re.compile(r'Total pot ([\d,]+)')
    DEALT_PATTERN = re.compile(r'Dealt to (\S+)')
    CARDS_PATTERN = re.compile(r'\[([A-Za-z0-9]{2}(?: [A-Za-z0-9]{2})*)\]')
    SHOW_PATTERN = re.compile(r'(\S+) (?:shows|wins|collected|folded)')
    BLIND_PATTERN = re.compile(r'(\S+): posts (small blind|big blind|ante|straddle) ([\d,]+)')

    def can_parse(self, content: str) -> bool:
        """Check if this parser can handle the given content.
        
        GG format contains 'Poker Hand #' and typically 'Tournament #' or table info.
        """
        return "Poker Hand #" in content and "Hold'em No Limit" in content

    def parse_hand(self, content: str) -> Optional[ParsedHand]:
        """Parse GGPoker hand history content."""
        if not self.can_parse(content):
            return None

        lines = content.strip().split('\n')
        
        hand_id = self._extract_hand_id(content)
        table_name = self._extract_table_name(content)
        hand_datetime = self._extract_datetime(content)
        players = self._extract_players(content)
        actions = self._extract_actions(content, players)
        board = self._extract_board(content)
        pot_total = self._extract_pot_total(content)

        return ParsedHand(
            hand_id=hand_id,
            table_name=table_name,
            datetime=hand_datetime,
            players=players,
            actions=actions,
            board=board,
            pot_total=pot_total,
            raw_text=content
        )

    def _extract_hand_id(self, content: str) -> str:
        """Extract hand ID from content."""
        match = self.HAND_ID_PATTERN.search(content)
        return match.group(1) if match else ""

    def _extract_table_name(self, content: str) -> str:
        """Extract table name from content."""
        match = self.TABLE_PATTERN.search(content)
        return match.group(1) if match else ""

    def _extract_datetime(self, content: str) -> datetime:
        """Extract datetime from content."""
        date_pattern = re.compile(r'(\d{4})/(\d{2})/(\d{2}) (\d{2}):(\d{2}):(\d{2})')
        match = date_pattern.search(content)
        if match:
            return datetime(
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3)),
                int(match.group(4)),
                int(match.group(5)),
                int(match.group(6))
            )
        return datetime.now()

    def _extract_players(self, content: str) -> List[Player]:
        """Extract all players from content."""
        players = []
        button_seat = 0
        button_match = self.BUTTON_PATTERN.search(content)
        if button_match:
            button_seat = int(button_match.group(1))

        for match in self.SEAT_PATTERN.finditer(content):
            seat = int(match.group(1))
            screen_name = match.group(2)
            stack_str = match.group(3).replace(',', '')
            stack = float(stack_str)
            players.append(Player(
                screen_name=screen_name,
                seat=seat,
                stack=stack,
                is_hero=False
            ))
        return players

    def _extract_actions(self, content: str, players: List[Player]) -> List[Action]:
        """Extract all actions from the hand."""
        actions = []
        lines = content.split('\n')
        
        hero_name = None
        for p in players:
            if p.is_hero:
                hero_name = p.screen_name
                break
        
        current_street = "preflop"
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if self.HOLE_CARDS_START.search(line):
                current_street = "preflop"
            elif self.FLOP_START.search(line):
                current_street = "flop"
            elif self.TURN_START.search(line):
                current_street = "turn"
            elif self.RIVER_START.search(line):
                current_street = "river"
            elif self.SHOWDOWN_START.search(line):
                break
            elif self.SUMMARY_START.search(line):
                break
            else:
                action = self._parse_action_line(line, current_street)
                if action:
                    actions.append(action)
            
            i += 1
        
        return actions

    def _parse_action_line(self, line: str, street: str) -> Optional[Action]:
        """Parse a single action line."""
        blind_match = re.match(r'(\S+): (posts small blind) ([\d,]+)', line)
        if blind_match:
            return Action(
                player=blind_match.group(1),
                action_type=ActionType.BET,
                amount=float(blind_match.group(3).replace(',', '')),
                street=street
            )
        
        blind_match = re.match(r'(\S+): (posts big blind) ([\d,]+)', line)
        if blind_match:
            return Action(
                player=blind_match.group(1),
                action_type=ActionType.BET,
                amount=float(blind_match.group(3).replace(',', '')),
                street=street
            )
        
        ante_match = re.match(r'(\S+): (posts ante) ([\d,]+)', line)
        if ante_match:
            return Action(
                player=ante_match.group(1),
                action_type=ActionType.BET,
                amount=float(ante_match.group(3).replace(',', '')),
                street=street
            )
        
        straddle_match = re.match(r'(\S+): (posts straddle) ([\d,]+)', line)
        if straddle_match:
            return Action(
                player=straddle_match.group(1),
                action_type=ActionType.BET,
                amount=float(straddle_match.group(3).replace(',', '')),
                street=street
            )
        
        if ': folds' in line:
            player = line.split(':')[0].strip()
            return Action(player=player, action_type=ActionType.FOLD, street=street)
        
        if ': checks' in line:
            player = line.split(':')[0].strip()
            return Action(player=player, action_type=ActionType.CHECK, street=street)
        
        if ': calls' in line:
            parts = line.split(': calls ')
            player = parts[0].strip()
            amount = float(parts[1].replace(',', '')) if len(parts) > 1 else 0
            return Action(player=player, action_type=ActionType.CALL, amount=amount, street=street)
        
        if 'and is all-in' in line:
            parts = line.split(': ')
            player = parts[0].strip()
            amount = 0
            nums = re.findall(r'[\d,]+', line)
            if nums:
                amount = float(nums[-1].replace(',', ''))
            return Action(player=player, action_type=ActionType.ALLIN, amount=amount, street=street)
        
        if ': bets' in line:
            parts = line.split(': bets ')
            player = parts[0].strip()
            amount = 0
            if len(parts) > 1:
                amount_str = parts[1].replace(' and is all-in', '')
                amount = float(amount_str.replace(',', ''))
            return Action(player=player, action_type=ActionType.BET, amount=amount, street=street)
        
        if ': raises' in line:
            parts = line.split(': raises ')
            player = parts[0].strip()
            amount = 0
            nums = re.findall(r'[\d,]+', line)
            if nums:
                amount = float(nums[-1].replace(',', ''))
            return Action(player=player, action_type=ActionType.RAISE, amount=amount, street=street)
        
        if 'and is all-in' in line:
            parts = line.split(': ')
            player = parts[0].strip()
            amount = 0
            if 'raises' in line:
                nums = re.findall(r'[\d,]+', line)
                if nums:
                    amount = float(nums[-1].replace(',', ''))
            return Action(player=player, action_type=ActionType.ALLIN, amount=amount, street=street)
        
        if ': collected' in line:
            return None
        
        if 'shows [' in line or 'won' in line.lower():
            return None
        
        if 'folded' in line and 'on ' in line:
            return None
        
        if 'is the button' in line or 'Seat' in line and 'in chips' in line:
            return None
        
        if self.HOLE_CARDS_START.search(line) or self.FLOP_START.search(line):
            return None
        if self.TURN_START.search(line) or self.RIVER_START.search(line):
            return None
        if self.SHOWDOWN_START.search(line) or self.SUMMARY_START.search(line):
            return None
        
        return None

    def _extract_board(self, content: str) -> List[str]:
        """Extract board cards from content."""
        board = []
        flop_match = self.FLOP_START.search(content)
        if flop_match:
            cards = flop_match.group(1).split()
            board.extend(cards)
        
        turn_match = self.TURN_START.search(content)
        if turn_match:
            board.append(turn_match.group(1))
        
        river_match = self.RIVER_START.search(content)
        if river_match:
            board.append(river_match.group(1))
        
        return board

    def _extract_pot_total(self, content: str) -> float:
        """Extract total pot from summary."""
        match = self.POT_PATTERN.search(content)
        if match:
            return float(match.group(1).replace(',', ''))
        return 0.0
