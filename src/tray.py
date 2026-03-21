"""System tray manager for PokerTracker."""

import logging
import platform
import sys
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class SystemTrayManager:
    """Manages system tray icon and menu."""

    def __init__(self, on_show_hud: Optional[Callable] = None,
                 on_hide_hud: Optional[Callable] = None,
                 on_show_settings: Optional[Callable] = None,
                 on_quit: Optional[Callable] = None):
        """Initialize system tray manager.

        Args:
            on_show_hud: Callback when Show HUD is clicked
            on_hide_hud: Callback when Hide HUD is clicked
            on_show_settings: Callback when Settings is clicked
            on_quit: Callback when Quit is clicked
        """
        self.on_show_hud = on_show_hud
        self.on_hide_hud = on_hide_hud
        self.on_show_settings = on_show_settings
        self.on_quit = on_quit

        self._app = None
        self._tray = None
        self._menu = None
        self._hud_visible = True

    def _get_icon_path(self) -> str:
        """Get the icon path, handling PyInstaller bundling."""
        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(__file__).parent.parent

        icon = base_path / "icon.png"
        if icon.exists():
            return str(icon)

        if platform.system() == "Windows":
            ico = base_path / "icon.ico"
            if ico.exists():
                return str(ico)

        return ""

    def initialize(self, app) -> bool:
        """Initialize the system tray.

        Args:
            app: QApplication instance

        Returns:
            True if successful, False otherwise
        """
        if platform.system() == "Darwin":
            logger.info("System tray not available on macOS - using dock icon")
            return False

        try:
            from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
            from PyQt5.QtGui import QIcon
        except ImportError:
            logger.warning("PyQt5 not installed. System tray unavailable.")
            logger.info("Install with: pip install PyQt5")
            return False

        self._app = app
        app.setQuitOnLastWindowClosed(False)

        icon_path = self._get_icon_path()
        if icon_path:
            icon = QIcon(icon_path)
        else:
            icon = QIcon()

        self._tray = QSystemTrayIcon(icon)
        self._tray.setToolTip("PokerTracker - Running")

        self._menu = QMenu()

        show_hud_action = QAction("Show HUD", self._menu)
        show_hud_action.triggered.connect(self._handle_show_hud)
        self._menu.addAction(show_hud_action)

        hide_hud_action = QAction("Hide HUD", self._menu)
        hide_hud_action.triggered.connect(self._handle_hide_hud)
        self._menu.addAction(hide_hud_action)

        self._menu.addSeparator()

        settings_action = QAction("Settings", self._menu)
        settings_action.triggered.connect(self._handle_show_settings)
        self._menu.addAction(settings_action)

        self._menu.addSeparator()

        quit_action = QAction("Quit", self._menu)
        quit_action.triggered.connect(self._handle_quit)
        self._menu.addAction(quit_action)

        self._tray.setContextMenu(self._menu)
        self._tray.activated.connect(self._on_tray_activated)

        self._tray.show()
        logger.info("System tray initialized")
        return True

    def _on_tray_activated(self, reason):
        """Handle tray icon activation (double-click)."""
        if reason == QSystemTrayIcon.DoubleClick:
            if self._hud_visible:
                self._handle_hide_hud()
            else:
                self._handle_show_hud()

    def _handle_show_hud(self):
        """Handle Show HUD menu action."""
        self._hud_visible = True
        if self.on_show_hud:
            self.on_show_hud()
        logger.info("HUD shown from tray")

    def _handle_hide_hud(self):
        """Handle Hide HUD menu action."""
        self._hud_visible = False
        if self.on_hide_hud:
            self.on_hide_hud()
        logger.info("HUD hidden from tray")

    def _handle_show_settings(self):
        """Handle Settings menu action."""
        if self.on_show_settings:
            self.on_show_settings()
        logger.info("Settings opened from tray")

    def _handle_quit(self):
        """Handle Quit menu action."""
        if self.on_quit:
            self.on_quit()
        if self._app:
            self._app.quit()
        logger.info("Quit from tray")

    def set_hud_visible(self, visible: bool):
        """Set HUD visibility state.

        Args:
            visible: True if HUD is visible
        """
        self._hud_visible = visible

    def is_hud_visible(self) -> bool:
        """Check if HUD is visible.

        Returns:
            True if HUD is visible
        """
        return self._hud_visible

    def destroy(self):
        """Destroy the system tray."""
        if self._tray:
            self._tray.hide()
            self._tray = None
        logger.info("System tray destroyed")


class macOSDockManager:
    """Manages macOS dock icon as alternative to system tray."""

    def __init__(self, on_show_hud: Optional[Callable] = None,
                 on_hide_hud: Optional[Callable] = None,
                 on_show_settings: Optional[Callable] = None,
                 on_quit: Optional[Callable] = None):
        """Initialize macOS dock manager.

        Args:
            on_show_hud: Callback when Show HUD is clicked
            on_hide_hud: Callback when Hide HUD is clicked
            on_show_settings: Callback when Settings is clicked
            on_quit: Callback when Quit is clicked
        """
        self.on_show_hud = on_show_hud
        self.on_hide_hud = on_hide_hud
        self.on_show_settings = on_show_settings
        self.on_quit = on_quit
        self._hud_visible = True

    def initialize(self, app) -> bool:
        """Initialize the dock manager.

        Args:
            app: QApplication instance

        Returns:
            True if successful
        """
        try:
            from PyQt5.QtWidgets import QMenuBar, QMenu
            from PyQt5.QtMacExtras import QtMac
        except ImportError:
            logger.warning("PyQt5 not installed. Dock menu unavailable.")
            return False

        logger.info("macOS dock manager initialized (menu bar approach)")
        return True

    def set_hud_visible(self, visible: bool):
        """Set HUD visibility state."""
        self._hud_visible = visible

    def is_hud_visible(self) -> bool:
        """Check if HUD is visible."""
        return self._hud_visible

    def destroy(self):
        """Destroy the dock manager."""
        logger.info("macOS dock manager destroyed")


def create_tray_manager(**kwargs) -> Optional[SystemTrayManager]:
    """Factory function to create appropriate tray manager.

    Returns:
        SystemTrayManager on Windows, None on other platforms
    """
    if platform.system() == "Windows":
        return SystemTrayManager(**kwargs)
    else:
        return None
