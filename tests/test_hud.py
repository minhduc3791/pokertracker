"""Tests for HUD overlay module."""

import pytest
from unittest.mock import Mock, MagicMock


class TestPlayerStats:
    """Tests for PlayerStats dataclass."""

    def test_player_stats_creation(self):
        """Test PlayerStats can be created."""
        from src.hud import PlayerStats
        ps = PlayerStats(screen_name="TestPlayer")
        assert ps.screen_name == "TestPlayer"

    def test_get_vpip_pct_with_data(self):
        """Test VPIP percentage calculation."""
        from src.hud import PlayerStats
        ps = PlayerStats(screen_name="Test", vpip=(25, 100))
        assert ps.get_vpip_pct() == "25%"

    def test_get_vpip_pct_no_data(self):
        """Test VPIP shows dash when no data."""
        from src.hud import PlayerStats
        ps = PlayerStats(screen_name="Test", vpip=(0, 0))
        assert ps.get_vpip_pct() == "—"

    def test_to_display_list(self):
        """Test converting stats to display list."""
        from src.hud import PlayerStats
        ps = PlayerStats(
            screen_name="Test",
            vpip=(25, 100),
            three_bet=(0, 0)
        )
        stats = ps.to_display_list()
        assert len(stats) == 4
        assert stats[0] == ("VPIP", "25%")
        assert stats[1] == ("3B", "—")


class TestHUDOverlay:
    """Tests for HUDOverlay class."""

    def test_hud_creation(self):
        """Test HUDOverlay can be created."""
        from src.hud import HUDOverlay
        mock_db = Mock()
        mock_config = Mock()
        hud = HUDOverlay(mock_db, mock_config)
        assert hud.db == mock_db
        assert hud.config == mock_config

    def test_format_stat(self):
        """Test stat formatting."""
        from src.hud import HUDOverlay
        mock_db = Mock()
        mock_config = Mock()
        hud = HUDOverlay(mock_db, mock_config)
        
        assert hud._format_stat("VPIP", "25%") == "VPIP: 25%"
        assert hud._format_stat("VPIP", "—") == "VPIP: —"


class TestTableRegistry:
    """Tests for TableRegistry class."""

    def test_registry_creation(self):
        """Test TableRegistry can be created."""
        from src.hud import TableRegistry
        registry = TableRegistry()
        assert registry.get_table_count() == 0

    def test_register_table(self):
        """Test table registration."""
        from src.hud import TableRegistry
        mock_db = Mock()
        mock_config = Mock()
        registry = TableRegistry()
        registry.initialize(mock_db, mock_config)
        
        hud = registry.register_table("table_1")
        assert hud is not None
        assert registry.get_table_count() == 1

    def test_unregister_table(self):
        """Test table unregistration."""
        from src.hud import TableRegistry
        mock_db = Mock()
        mock_config = Mock()
        registry = TableRegistry()
        registry.initialize(mock_db, mock_config)
        
        registry.register_table("table_1")
        assert registry.get_table_count() == 1
        
        registry.unregister_table("table_1")
        assert registry.get_table_count() == 0

    def test_get_overlay_for_table(self):
        """Test getting overlay for specific table."""
        from src.hud import TableRegistry
        mock_db = Mock()
        mock_config = Mock()
        registry = TableRegistry()
        registry.initialize(mock_db, mock_config)
        
        registry.register_table("table_1")
        hud = registry.get_overlay_for_table("table_1")
        assert hud is not None
        
        not_found = registry.get_overlay_for_table("nonexistent")
        assert not_found is None
