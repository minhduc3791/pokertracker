"""Tests for ProcessDetector."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.process_detector import ProcessDetector
from src.config import ConfigManager


class TestProcessDetector:
    """Test suite for ProcessDetector."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = ConfigManager()

    @patch('psutil.process_iter')
    def test_is_running_returns_true_when_process_found(self, mock_process_iter):
        """Test that is_running returns True when process is found."""
        mock_proc = MagicMock()
        mock_proc.info = {'name': 'Natural8.exe'}
        mock_process_iter.return_value = [mock_proc]
        
        detector = ProcessDetector(self.config)
        assert detector.is_running() is True

    @patch('psutil.process_iter')
    def test_is_running_returns_false_when_process_not_found(self, mock_process_iter):
        """Test that is_running returns False when process is not found."""
        mock_proc = MagicMock()
        mock_proc.info = {'name': 'OtherApp.exe'}
        mock_process_iter.return_value = [mock_proc]
        
        detector = ProcessDetector(self.config)
        assert detector.is_running() is False

    @patch('psutil.process_iter')
    def test_detects_custom_process_name(self, mock_process_iter):
        """Test that detector can find custom process names."""
        mock_proc = MagicMock()
        mock_proc.info = {'name': 'MyPokerApp.exe'}
        mock_process_iter.return_value = [mock_proc]
        
        self.config.set("natural8_process_name", "MyPokerApp.exe")
        detector = ProcessDetector(self.config)
        assert detector.is_running() is True

    @patch('psutil.process_iter')
    def test_empty_process_list(self, mock_process_iter):
        """Test handling of empty process list."""
        mock_process_iter.return_value = []
        detector = ProcessDetector(self.config)
        assert detector.is_running() is False
