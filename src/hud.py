"""HUD overlay for displaying player statistics."""

import logging
import platform
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class PlayerStats:
    """Container for player statistics."""
    screen_name: str
    vpip: Tuple[int, int] = (0, 0)
    three_bet: Tuple[int, int] = (0, 0)
    fold_to_bet: Tuple[int, int] = (0, 0)
    call_cbet: Tuple[int, int] = (0, 0)
    raise_cbet: Tuple[int, int] = (0, 0)
    cbet_turn: Tuple[int, int] = (0, 0)
    fold_cbet_turn: Tuple[int, int] = (0, 0)
    call_cbet_turn: Tuple[int, int] = (0, 0)
    raise_cbet_turn: Tuple[int, int] = (0, 0)
    wtsd: Tuple[int, int] = (0, 0)
    w_sd: Tuple[int, int] = (0, 0)

    def get_vpip_pct(self) -> str:
        if self.vpip[1] == 0:
            return "—"
        return f"{round(self.vpip[0] / self.vpip[1] * 100)}%"

    def get_three_bet_pct(self) -> str:
        if self.three_bet[1] == 0:
            return "—"
        return f"{round(self.three_bet[0] / self.three_bet[1] * 100)}%"

    def get_wtsd_pct(self) -> str:
        if self.wtsd[1] == 0:
            return "—"
        return f"{round(self.wtsd[0] / self.wtsd[1] * 100)}%"

    def get_w_sd_pct(self) -> str:
        if self.w_sd[1] == 0:
            return "—"
        return f"{round(self.w_sd[0] / self.w_sd[1] * 100)}%"

    def to_display_list(self) -> List[Tuple[str, str]]:
        return [
            ("VPIP", self.get_vpip_pct()),
            ("3B", self.get_three_bet_pct()),
            ("WTSD", self.get_wtsd_pct()),
            ("W$SD", self.get_w_sd_pct()),
        ]


class OverlayBackend(ABC):
    """Abstract base class for overlay backends."""

    @abstractmethod
    def create_overlay(self, x: int, y: int, width: int, height: int, transparent: bool = True) -> None:
        """Create overlay window."""
        pass

    @abstractmethod
    def destroy(self) -> None:
        """Destroy overlay window."""
        pass

    @abstractmethod
    def draw_rect(self, x: int, y: int, width: int, height: int, color: Tuple[int, int, int, int]) -> None:
        """Draw a rectangle."""
        pass

    @abstractmethod
    def draw_text(self, x: int, y: int, text: str, color: Tuple[int, int, int, int], size: int = 12) -> None:
        """Draw text."""
        pass

    @abstractmethod
    def show(self) -> None:
        """Show the overlay."""
        pass

    @abstractmethod
    def hide(self) -> None:
        """Hide the overlay."""
        pass

    @abstractmethod
    def refresh(self) -> None:
        """Refresh the overlay."""
        pass


class WindowsOverlayBackend(OverlayBackend):
    """Windows-specific overlay using transparent-overlay and pywin32."""

    def __init__(self):
        try:
            from transparent_overlay import Overlay
            self._overlay = Overlay()
            self._visible = False
        except ImportError:
            logger.error("transparent-overlay not installed. Run: pip install transparent-overlay")
            raise

    def create_overlay(self, x: int, y: int, width: int, height: int, transparent: bool = True) -> None:
        self._overlay.create_window(x, y, width, height)
        if transparent:
            self._overlay.set_click_through(True)

    def destroy(self) -> None:
        self._overlay.destroy()

    def draw_rect(self, x: int, y: int, width: int, height: int, color: Tuple[int, int, int, int]) -> None:
        self._overlay.draw_rect(x, y, width, height, color)

    def draw_text(self, x: int, y: int, text: str, color: Tuple[int, int, int, int], size: int = 12) -> None:
        self._overlay.draw_text(x, y, text, color, size)

    def show(self) -> None:
        self._overlay.show()
        self._visible = True

    def hide(self) -> None:
        self._overlay.hide()
        self._visible = False

    def refresh(self) -> None:
        self._overlay.refresh()


class MacOSOverlayBackend(OverlayBackend):
    """macOS overlay stub - displays info via console logging."""

    def __init__(self):
        self._visible = False
        self._x = self._y = self._width = self._height = 0

    def create_overlay(self, x: int, y: int, width: int, height: int, transparent: bool = True) -> None:
        self._x, self._y, self._width, self._height = x, y, width, height
        logger.info(f"[HUD] Creating overlay at ({x}, {y}) size {width}x{height}")

    def destroy(self) -> None:
        logger.info("[HUD] Destroying overlay")

    def draw_rect(self, x: int, y: int, width: int, height: int, color: Tuple[int, int, int, int]) -> None:
        pass

    def draw_text(self, x: int, y: int, text: str, color: Tuple[int, int, int, int], size: int = 12) -> None:
        pass

    def show(self) -> None:
        self._visible = True
        logger.info("[HUD] Overlay shown (macOS stub)")

    def hide(self) -> None:
        self._visible = False
        logger.info("[HUD] Overlay hidden (macOS stub)")

    def refresh(self) -> None:
        pass


def create_overlay_backend() -> OverlayBackend:
    """Factory function to create appropriate overlay backend."""
    if platform.system() == "Windows":
        return WindowsOverlayBackend()
    else:
        return MacOSOverlayBackend()


class HUDOverlay:
    """Transparent HUD overlay for displaying player statistics."""

    PANEL_WIDTH = 180
    PANEL_HEIGHT_PER_PLAYER = 24
    PANEL_PADDING = 2
    ROW_HEIGHT = 24
    ROW_SPACING = 2
    BG_COLOR = (0, 0, 0, 200)
    TEXT_COLOR = (255, 255, 255, 255)
    ROW_BG_COLOR = (30, 30, 30, 180)
    HEADER_BG_COLOR = (0, 100, 0, 220)

    def __init__(self, db, config):
        """Initialize HUD overlay.

        Args:
            db: DatabaseManager instance
            config: ConfigManager instance
        """
        self.db = db
        self.config = config
        self._backend = create_overlay_backend()
        self._visible = False
        self._position = self._load_position()
        self._panel_height = 0

    def _load_position(self) -> Tuple[int, int]:
        """Load HUD position from config."""
        x = self.config.get("hud.position_x", -1)
        y = self.config.get("hud.position_y", 100)
        if x == -1:
            x = self._get_default_x()
        return (x, y)

    def _get_default_x(self) -> int:
        """Get default X position (right side of screen)."""
        try:
            import subprocess
            if platform.system() == "Windows":
                import ctypes
                user32 = ctypes.windll.user32
                return user32.GetSystemMetrics(0) - self.PANEL_WIDTH - 10
            else:
                result = subprocess.run(
                    ["system_profiler", "SPDisplaysDataType", "-json"],
                    capture_output=True, text=True
                )
                import json
                data = json.loads(result.stdout)
                displays = data.get("SPDisplaysDataType", [])
                if displays and "spdisplays_ndrs" in displays[0]:
                    width = displays[0]["spdisplays_ndrs"].get(
                        "spdisplays_resolution", "1920x1080"
                    ).split("x")[0]
                    return int(width) - self.PANEL_WIDTH - 10
        except Exception:
            pass
        return 800

    def _get_players_at_table(self, table_name: Optional[str] = None) -> List[PlayerStats]:
        """Get players with stats from database.

        Args:
            table_name: Optional table name filter

        Returns:
            List of PlayerStats objects
        """
        if self.db is None:
            return []

        try:
            players = self.db.get_all_players()
            result = []
            for player_id, screen_name, is_hero in players:
                stats = PlayerStats(screen_name=screen_name)
                if is_hero:
                    stats.screen_name = f"{screen_name} (Hero)"

                stat_types = ["VPIP", "3BET", "F_TB", "CALL_CB", "RAISE_CB",
                             "CB_TURN", "F_CB_T", "C_CB_T", "R_CB_T", "WTSD", "W$SD"]
                attrs = ["vpip", "three_bet", "fold_to_bet", "call_cbet", "raise_cbet",
                        "cbet_turn", "fold_cbet_turn", "call_cbet_turn", "raise_cbet_turn",
                        "wtsd", "w_sd"]

                for stat_type, attr in zip(stat_types, attrs):
                    value = self.db.get_stat(player_id, table_name, stat_type)
                    if value:
                        setattr(stats, attr, (value[0], value[1]))

                result.append(stats)
            return result
        except Exception as e:
            logger.error(f"Error getting players: {e}")
            return []

    def _draw_player_panel(self, players: List[PlayerStats]) -> None:
        """Draw the player panel with all stats.

        Args:
            players: List of PlayerStats to display
        """
        x, y = self._position
        y_offset = y

        self._backend.draw_rect(x, y_offset, self.PANEL_WIDTH, 28, self.HEADER_BG_COLOR)
        self._backend.draw_text(x + 5, y_offset + 5, "PokerTracker HUD", self.TEXT_COLOR, 14)
        y_offset += 28

        for player in players:
            row_height = self.ROW_HEIGHT

            self._backend.draw_rect(x, y_offset, self.PANEL_WIDTH, row_height, self.ROW_BG_COLOR)

            self._backend.draw_text(
                x + self.PANEL_PADDING,
                y_offset + 5,
                player.screen_name[:18],
                self.TEXT_COLOR,
                11
            )
            y_offset += row_height

            stats = player.to_display_list()
            for stat_name, stat_value in stats:
                if stat_name == "VPIP":
                    x_offset = x + self.PANEL_PADDING
                elif stat_name == "3B":
                    x_offset = x + 55
                elif stat_name == "WTSD":
                    x_offset = x + self.PANEL_PADDING
                    y_offset += 4
                elif stat_name == "W$SD":
                    x_offset = x + 55
                    y_offset += 4
                else:
                    x_offset = x + self.PANEL_PADDING

                self._backend.draw_text(
                    x_offset,
                    y_offset,
                    f"{stat_name}: {stat_value}",
                    (200, 200, 200, 255),
                    10
                )
                if stat_name == "W$SD":
                    y_offset -= 4

            y_offset += self.ROW_SPACING

        panel_end = y_offset
        self._panel_height = panel_end - y

    def _format_stat(self, stat_name: str, value: str) -> str:
        """Format a stat for display.

        Args:
            stat_name: Stat name
            value: Stat value

        Returns:
            Formatted stat string
        """
        if value == "—":
            return f"{stat_name}: —"
        return f"{stat_name}: {value}"

    def update(self) -> None:
        """Update the HUD display with current player stats."""
        if not self._visible:
            return

        players = self._get_players_at_table()
        if players:
            self._draw_player_panel(players)
        self._backend.refresh()

    def show(self) -> None:
        """Show the HUD overlay."""
        if not self._visible:
            x, y = self._position
            self._backend.create_overlay(x, y, self.PANEL_WIDTH, 400, transparent=True)
            self._backend.show()
            self._visible = True

    def hide(self) -> None:
        """Hide the HUD overlay."""
        if self._visible:
            self._backend.hide()
            self._visible = False

    def toggle(self) -> None:
        """Toggle HUD visibility."""
        if self._visible:
            self.hide()
        else:
            self.show()

    def destroy(self) -> None:
        """Destroy the HUD overlay."""
        self._backend.destroy()


class TableRegistry:
    """Registry for managing multiple table overlays."""

    def __init__(self):
        self._tables: Dict[str, HUDOverlay] = {}
        self._db = None
        self._config = None

    def initialize(self, db, config) -> None:
        """Initialize the registry with database and config.

        Args:
            db: DatabaseManager instance
            config: ConfigManager instance
        """
        self._db = db
        self._config = config

    def register_table(self, table_id: str, window_handle: Optional[int] = None) -> HUDOverlay:
        """Register a new table with HUD overlay.

        Args:
            table_id: Unique table identifier
            window_handle: Optional window handle for positioning

        Returns:
            HUDOverlay instance for the table
        """
        if table_id in self._tables:
            return self._tables[table_id]

        hud = HUDOverlay(self._db, self._config)

        if window_handle:
            x = self._calculate_table_position(window_handle)
            hud._position = (x, hud._position[1])

        self._tables[table_id] = hud
        logger.info(f"Registered table: {table_id}")
        return hud

    def unregister_table(self, table_id: str) -> None:
        """Unregister a table.

        Args:
            table_id: Table identifier to remove
        """
        if table_id in self._tables:
            self._tables[table_id].destroy()
            del self._tables[table_id]
            logger.info(f"Unregistered table: {table_id}")

    def get_overlay_for_table(self, table_id: str) -> Optional[HUDOverlay]:
        """Get HUD overlay for a specific table.

        Args:
            table_id: Table identifier

        Returns:
            HUDOverlay instance or None
        """
        return self._tables.get(table_id)

    def update_all(self) -> None:
        """Update all table overlays."""
        for hud in self._tables.values():
            hud.update()

    def show_all(self) -> None:
        """Show all table overlays."""
        for hud in self._tables.values():
            hud.show()

    def hide_all(self) -> None:
        """Hide all table overlays."""
        for hud in self._tables.values():
            hud.hide()

    def _calculate_table_position(self, window_handle: int) -> int:
        """Calculate HUD position relative to table window.

        Args:
            window_handle: Window handle

        Returns:
            X position for HUD
        """
        return self._config.get("hud.position_x", 800)

    def get_table_count(self) -> int:
        """Get number of registered tables."""
        return len(self._tables)
