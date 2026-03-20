"""Configuration management for poker tracker."""

import json
from pathlib import Path
from typing import Any, Optional


class ConfigManager:
    """Manages application configuration from JSON files."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to config.json, defaults to project root
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.json"
        
        self.config_path = Path(config_path)
        self._config = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from JSON file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self._config = json.load(f)
        else:
            self._config = self._get_defaults()

    def _get_defaults(self) -> dict:
        """Get default configuration values."""
        return {
            "natural8_process_name": "Natural8.exe",
            "hand_history_directory": "./hand-histories",
            "poll_interval": 2,
            "hero_screen_name": None,
            "database_path": "poker_tracker.db",
            "log_level": "INFO",
            "log_file": "poker_tracker.log"
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation for nested)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.
        
        Args:
            key: Configuration key (supports dot notation for nested)
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value

    def save(self) -> None:
        """Save configuration to file."""
        with open(self.config_path, 'w') as f:
            json.dump(self._config, f, indent=2)

    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()
