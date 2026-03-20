"""Main entry point for poker tracker application."""

import logging
import signal
import sys
from pathlib import Path
from src.config import ConfigManager
from src.database import DatabaseManager
from src.natural8_parser import Natural8Parser
from src.stats_engine import StatsEngine
from src.process_detector import ProcessDetector
from src.file_watcher import FileWatcher


logger = logging.getLogger(__name__)

watcher_instance = None
detector_instance = None
db_instance = None


def setup_logging(config: ConfigManager):
    """Set up logging configuration.
    
    Args:
        config: Configuration manager
    """
    log_level = config.get("log_level", "INFO")
    log_file = config.get("log_file", "poker_tracker.log")
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def on_natural8_start():
    """Callback when Natural8 process starts."""
    global watcher_instance
    logger.info("Natural8 detected - starting file watcher")
    if watcher_instance:
        watcher_instance.start_watching()


def on_natural8_stop():
    """Callback when Natural8 process stops."""
    global watcher_instance
    logger.info("Natural8 stopped - pausing file watcher")
    if watcher_instance:
        watcher_instance.stop_watching()


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info("Received shutdown signal, cleaning up...")
    
    global watcher_instance, detector_instance, db_instance
    
    if watcher_instance:
        watcher_instance.stop_watching()
    
    if detector_instance:
        detector_instance.stop_monitoring()
    
    if db_instance:
        db_instance.close()
    
    sys.exit(0)


def main():
    """Main application entry point."""
    global watcher_instance, detector_instance, db_instance
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    config = ConfigManager()
    setup_logging(config)
    
    logger.info("Starting Poker Tracker")
    
    watch_dir = config.get("hand_history_directory")
    if not Path(watch_dir).exists():
        logger.warning(f"Hand history directory does not exist: {watch_dir}")
        logger.info("Creating directory...")
        Path(watch_dir).mkdir(parents=True, exist_ok=True)
    
    db_path = config.get("database_path", "poker_tracker.db")
    db_instance = DatabaseManager(db_path)
    logger.info(f"Database initialized: {db_path}")
    
    parser = Natural8Parser()
    stats = StatsEngine(db_instance, config)
    
    detector_instance = ProcessDetector(config)
    watcher_instance = FileWatcher(config, parser, db_instance, stats)
    
    detector_instance.start_monitoring(on_natural8_start, on_natural8_stop)
    
    if detector_instance.is_running():
        logger.info("Natural8 already running, starting watcher...")
        on_natural8_start()
    
    logger.info("Poker Tracker is running. Press Ctrl+C to stop.")
    
    try:
        while True:
            signal.pause()
    except AttributeError:
        pass


if __name__ == "__main__":
    main()
