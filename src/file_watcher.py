"""File watching for hand history files."""

import logging
import os
import time
from pathlib import Path
from typing import Dict
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver
from src.config import ConfigManager
from src.natural8_parser import Natural8Parser
from src.database import DatabaseManager
from src.stats_engine import StatsEngine


logger = logging.getLogger(__name__)


class HandHistoryHandler(FileSystemEventHandler):
    """Handles file system events for hand history files."""

    def __init__(self, parser: Natural8Parser, db: DatabaseManager, 
                 stats: StatsEngine, debounce_seconds: float = 1.0):
        """Initialize handler.
        
        Args:
            parser: Natural8 parser instance
            db: Database manager
            stats: Stats engine
            debounce_seconds: Seconds to wait before reprocessing
        """
        super().__init__()
        self.parser = parser
        self.db = db
        self.stats = stats
        self.debounce_seconds = debounce_seconds
        self.debouncer: Dict[str, float] = {}

    def on_modified(self, event):
        """Handle file modification events.
        
        Args:
            event: File system event
        """
        if event.is_directory:
            return
        
        filepath = event.src_path
        
        if not filepath.endswith('.txt'):
            return
        
        current_time = time.time()
        last_modified = self.debouncer.get(filepath, 0)
        
        if current_time - last_modified < self.debounce_seconds:
            logger.debug(f"Debouncing {filepath}")
            return
        
        self.debouncer[filepath] = current_time
        
        logger.info(f"Processing modified file: {filepath}")
        self._process_file(filepath)

    def _process_file(self, filepath: str):
        """Process a single hand history file.
        
        Args:
            filepath: Path to the file
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not self.parser.can_parse(content):
                logger.debug(f"Skipping non-GG file: {filepath}")
                return
            
            parsed_hand = self.parser.parse_hand(content)
            if parsed_hand is None:
                logger.warning(f"Failed to parse: {filepath}")
                return
            
            if self.db.check_duplicate(
                parsed_hand.hand_id,
                parsed_hand.table_name,
                parsed_hand.datetime.isoformat()
            ):
                logger.debug(f"Duplicate hand: {parsed_hand.hand_id}")
                return
            
            if self.db.insert_hand(parsed_hand):
                logger.info(f"Inserted hand: {parsed_hand.hand_id}")
                self.stats.process_hand(parsed_hand)
            else:
                logger.debug(f"Hand already exists: {parsed_hand.hand_id}")
                
        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")


class FileWatcher:
    """Watches hand history directory for new files."""

    def __init__(self, config: ConfigManager, parser: Natural8Parser,
                 db: DatabaseManager, stats: StatsEngine):
        """Initialize file watcher.
        
        Args:
            config: Configuration manager
            parser: Natural8 parser instance
            db: Database manager
            stats: Stats engine
        """
        self.config = config
        self.parser = parser
        self.db = db
        self.stats = stats
        self.observer = None
        self.debounce_seconds = config.get("debounce_seconds", 1.0)

    def start_watching(self):
        """Start watching the hand history directory."""
        watch_dir = self.config.get("hand_history_directory")
        
        if not os.path.exists(watch_dir):
            logger.error(f"Hand history directory does not exist: {watch_dir}")
            return
        
        poll_interval = self.config.get("poll_interval", 2)
        
        handler = HandHistoryHandler(
            self.parser, self.db, self.stats,
            debounce_seconds=self.debounce_seconds
        )
        
        self.observer = PollingObserver(timeout=poll_interval)
        self.observer.schedule(handler, watch_dir, recursive=True)
        self.observer.start()
        
        logger.info(f"Started watching {watch_dir}")

    def stop_watching(self):
        """Stop watching for file changes."""
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=10)
            logger.info("Stopped watching for file changes")
