import pytest
import sqlite3
import tempfile
import os
from pathlib import Path

def test_schema_creation():
    """Test that database schema is created properly"""
    # This test should fail initially
    from src.database import DatabaseManager
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp_file:
        db_path = tmp_file.name
    
    try:
        # Create database manager
        db = DatabaseManager(db_path)
        
        # Check WAL mode is enabled
        cursor = db.connection.cursor()
        cursor.execute("PRAGMA journal_mode")
        journal_mode = cursor.fetchone()[0]
        assert journal_mode == "wal", f"Expected WAL mode, got {journal_mode}"
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        assert "hands" in tables, "hands table should exist"
        assert "players" in tables, "players table should exist" 
        assert "player_stats" in tables, "player_stats table should exist"
        
        # Check indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]
        assert "idx_hands_datetime" in indexes, "hands datetime index should exist"
        assert "idx_hands_table" in indexes, "hands table index should exist"
        
        db.close()
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

@pytest.mark.skip("Not implemented") 
def test_hand_storage():
    """Test that hands can be stored"""
    pass

@pytest.mark.skip("Not implemented")
def test_duplicate_prevention():
    """Test that duplicate hands are prevented"""
    pass

@pytest.mark.skip("Not implemented") 
def test_stats_storage():
    """Test that stats can be stored"""
    pass