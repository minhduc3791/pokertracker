"""Tests for FileWatcher."""

import pytest
import tempfile
import time
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from src.file_watcher import FileWatcher, HandHistoryHandler
from src.natural8_parser import Natural8Parser
from src.database import DatabaseManager
from src.stats_engine import StatsEngine
from src.config import ConfigManager


class TestFileWatcher:
    """Test suite for FileWatcher."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = ConfigManager()
        self.config.set("hand_history_directory", self.temp_dir)
        self.config.set("poll_interval", 0.5)
        
        self.db = DatabaseManager(":memory:")
        self.parser = Natural8Parser()
        self.stats = StatsEngine(self.db, self.config)

    def teardown_method(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.db.close()

    def test_watcher_initializes(self):
        """Test that FileWatcher initializes correctly."""
        watcher = FileWatcher(self.config, self.parser, self.db, self.stats)
        assert watcher is not None

    def test_handler_initializes(self):
        """Test that HandHistoryHandler initializes correctly."""
        handler = HandHistoryHandler(self.parser, self.db, self.stats)
        assert handler is not None
        assert handler.debouncer == {}

    @patch('src.file_watcher.PollingObserver')
    def test_watcher_starts(self, mock_observer):
        """Test that watcher can start watching."""
        mock_instance = MagicMock()
        mock_observer.return_value = mock_instance
        
        watcher = FileWatcher(self.config, self.parser, self.db, self.stats)
        watcher.start_watching()
        
        mock_instance.schedule.assert_called_once()
        mock_instance.start.assert_called_once()

    @patch('src.file_watcher.PollingObserver')
    def test_watcher_stops(self, mock_observer):
        """Test that watcher can stop watching."""
        mock_instance = MagicMock()
        mock_observer.return_value = mock_instance
        
        watcher = FileWatcher(self.config, self.parser, self.db, self.stats)
        watcher.observer = mock_instance
        watcher.stop_watching()
        
        mock_instance.stop.assert_called_once()
