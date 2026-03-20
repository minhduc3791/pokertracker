"""Process detection for Natural8 poker client."""

import logging
import threading
import time
from typing import Callable, Optional, List
import psutil
from src.config import ConfigManager


logger = logging.getLogger(__name__)


class ProcessDetector:
    """Detects when Natural8 process is running."""

    def __init__(self, config: ConfigManager):
        """Initialize process detector.
        
        Args:
            config: Configuration manager
        """
        self.config = config
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._last_state = False

    def is_running(self) -> bool:
        """Check if Natural8 process is currently running.
        
        Returns:
            True if process is running, False otherwise
        """
        process_name = self.config.get("natural8_process_name", "Natural8.exe")
        
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] == process_name:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return False

    def start_monitoring(self, on_start: Optional[Callable] = None,
                        on_stop: Optional[Callable] = None) -> None:
        """Start monitoring for process state changes.
        
        Args:
            on_start: Callback when process starts
            on_stop: Callback when process stops
        """
        if self._monitoring:
            logger.warning("Already monitoring")
            return
        
        self._monitoring = True
        self._last_state = self.is_running()
        
        poll_interval = self.config.get("poll_interval", 2)
        
        def _monitor_loop():
            logger.info("Starting process monitoring")
            while self._monitoring:
                current_state = self.is_running()
                
                if current_state != self._last_state:
                    if current_state:
                        logger.info("Natural8 process started")
                        if on_start:
                            on_start()
                    else:
                        logger.info("Natural8 process stopped")
                        if on_stop:
                            on_stop()
                    
                    self._last_state = current_state
                
                time.sleep(poll_interval)
            
            logger.info("Process monitoring stopped")
        
        self._monitor_thread = threading.Thread(target=_monitor_loop, daemon=True)
        self._monitor_thread.start()

    def stop_monitoring(self) -> None:
        """Stop monitoring for process state changes."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
            self._monitor_thread = None

    def detect_process_name_change(self) -> List[str]:
        """Detect potential poker process names if configured name not found.
        
        Returns:
            List of potential process names
        """
        poker_keywords = ['poker', 'gg', 'natural', 'partypoker', 'pokerstars']
        candidates = []
        
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name'].lower()
                if any(keyword in name for keyword in poker_keywords):
                    candidates.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return candidates
