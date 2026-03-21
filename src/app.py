"""PokerTracker application shell."""

import atexit
import logging
import platform
import signal
import sys
from pathlib import Path
from typing import Optional

from src.config import ConfigManager
from src.database import DatabaseManager
from src.hud import HUDOverlay, TableRegistry
from src.tray import create_tray_manager, SystemTrayManager

logger = logging.getLogger(__name__)


class SettingsWindow:
    """Simple settings window for configuration."""

    def __init__(self, config: ConfigManager, parent=None):
        """Initialize settings window.

        Args:
            config: ConfigManager instance
            parent: Optional parent widget
        """
        self.config = config
        self._window = None
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI."""
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFormLayout
            from PyQt5.QtCore import Qt
        except ImportError:
            logger.warning("PyQt5 not available for settings window")
            return

        self._window = QDialog()
        self._window.setWindowTitle("PokerTracker Settings")
        self._window.setMinimumWidth(400)

        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self._hero_input = QLineEdit()
        self._hero_input.setText(self.config.get("hero_screen_name") or "")
        form_layout.addRow("Hero Screen Name:", self._hero_input)

        self._hh_dir_input = QLineEdit()
        self._hh_dir_input.setText(self.config.get("hand_history_directory") or "./hand-histories")
        form_layout.addRow("Hand History Directory:", self._hh_dir_input)

        layout.addLayout(form_layout)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save_settings)
        layout.addWidget(save_btn)

        self._window.setLayout(layout)

    def _save_settings(self):
        """Save settings to config."""
        self.config.set("hero_screen_name", self._hero_input.text() or None)
        self.config.set("hand_history_directory", self._hh_dir_input.text())
        self.config.save()
        logger.info("Settings saved")
        if self._window:
            self._window.close()

    def show(self):
        """Show the settings window."""
        if self._window:
            self._window.show()
            self._window.raise_()
            self._window.activateWindow()


class PokerTrackerApp:
    """Main application class for PokerTracker."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the application.

        Args:
            config_path: Optional path to config file
        """
        self._config = ConfigManager(config_path)
        self._db: Optional[DatabaseManager] = None
        self._stats = None
        self._parser = None
        self._hud: Optional[HUDOverlay] = None
        self._table_registry: Optional[TableRegistry] = None
        self._tray: Optional[SystemTrayManager] = None
        self._settings: Optional[SettingsWindow] = None
        self._qt_app = None
        self._running = False
        self._update_timer = None

        self._setup_logging()
        self._register_signal_handlers()

    def _setup_logging(self):
        """Configure logging."""
        log_level = self._config.get("log_level", "INFO")
        log_file = self._config.get("log_file", "poker_tracker.log")

        logging.basicConfig(
            level=getattr(logging, log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def _register_signal_handlers(self):
        """Register signal handlers for clean shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.shutdown()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def _init_qt(self) -> bool:
        """Initialize Qt application.

        Returns:
            True if successful, False otherwise
        """
        try:
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtCore import QTimer
        except ImportError:
            logger.warning("PyQt5 not available. GUI features disabled.")
            logger.info("Install with: pip install PyQt5")
            return False

        self._qt_app = QApplication(sys.argv)
        self._qt_app.setApplicationName("PokerTracker")
        self._qt_app.setQuitOnLastWindowClosed(False)

        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._update_loop)
        self._update_timer.start(1000)

        return True

    def _init_components(self) -> bool:
        """Initialize application components.

        Returns:
            True if successful
        """
        try:
            db_path = self._config.get("database_path", "poker_tracker.db")
            self._db = DatabaseManager(db_path)

            self._table_registry = TableRegistry()
            self._table_registry.initialize(self._db, self._config)

            self._hud = HUDOverlay(self._db, self._config)

            logger.info("Components initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            return False

    def _init_tray(self) -> bool:
        """Initialize system tray.

        Returns:
            True if successful
        """
        if platform.system() == "Windows":
            self._tray = create_tray_manager(
                on_show_hud=self._on_show_hud,
                on_hide_hud=self._on_hide_hud,
                on_show_settings=self._on_show_settings,
                on_quit=self._on_quit
            )
            if self._tray:
                return self._tray.initialize(self._qt_app)
        return False

    def _on_show_hud(self):
        """Handle show HUD request."""
        if self._hud:
            self._hud.show()
        if self._table_registry:
            self._table_registry.show_all()

    def _on_hide_hud(self):
        """Handle hide HUD request."""
        if self._hud:
            self._hud.hide()
        if self._table_registry:
            self._table_registry.hide_all()

    def _on_show_settings(self):
        """Handle show settings request."""
        if not self._settings:
            self._settings = SettingsWindow(self._config)
        self._settings.show()

    def _on_quit(self):
        """Handle quit request."""
        self.shutdown()

    def _update_loop(self):
        """Periodic update loop."""
        if self._hud and self._hud._visible:
            self._hud.update()
        if self._table_registry:
            self._table_registry.update_all()

    def register_table(self, table_id: str, window_handle: Optional[int] = None) -> Optional[HUDOverlay]:
        """Register a new poker table.

        Args:
            table_id: Unique table identifier
            window_handle: Optional window handle

        Returns:
            HUDOverlay instance or None
        """
        if not self._table_registry:
            return None
        return self._table_registry.register_table(table_id, window_handle)

    def unregister_table(self, table_id: str):
        """Unregister a poker table.

        Args:
            table_id: Table identifier
        """
        if self._table_registry:
            self._table_registry.unregister_table(table_id)

    def run(self):
        """Run the application."""
        logger.info("Starting PokerTracker...")

        if platform.system() == "Windows":
            self._init_qt()

        if not self._init_components():
            logger.error("Failed to initialize components")
            return False

        if platform.system() == "Windows":
            self._init_tray()
            if self._hud:
                self._hud.show()

        atexit.register(self.shutdown)
        self._running = True

        logger.info("PokerTracker running")

        if platform.system() == "Windows" and self._qt_app:
            sys.exit(self._qt_app.exec_())
        else:
            import time
            while self._running:
                time.sleep(1)

        return True

    def shutdown(self):
        """Shutdown the application cleanly."""
        logger.info("Shutting down PokerTracker...")

        self._running = False

        if self._update_timer:
            self._update_timer.stop()

        if self._hud:
            self._hud.destroy()

        if self._table_registry:
            for table_id in list(self._table_registry._tables.keys()):
                self._table_registry.unregister_table(table_id)

        if self._tray:
            self._tray.destroy()

        if self._db:
            self._db.close()

        logger.info("PokerTracker shutdown complete")


def main(config_path: Optional[str] = None):
    """Main entry point.

    Args:
        config_path: Optional path to config file
    """
    app = PokerTrackerApp(config_path)
    app.run()
