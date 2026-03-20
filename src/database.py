import sqlite3
from typing import Optional


class DatabaseManager:
    """Manages SQLite database connection and schema for poker hand tracking."""
    
    def __init__(self, db_path: str):
        """Initialize database manager and create schema.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.create_schema()
    
    def create_schema(self):
        """Create database schema with tables, indexes, and WAL mode."""
        cursor = self.connection.cursor()
        
        # Enable WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        
        # Create hands table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hands (
                id INTEGER PRIMARY KEY,
                hand_id TEXT NOT NULL,
                table_name TEXT NOT NULL,
                datetime TEXT NOT NULL,
                raw_text TEXT NOT NULL,
                parsed_data JSON NOT NULL,
                UNIQUE(hand_id, table_name, datetime)
            )
        """)
        
        # Create players table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY,
                screen_name TEXT UNIQUE NOT NULL,
                is_hero BOOLEAN DEFAULT 0
            )
        """)
        
        # Create player_stats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_stats (
                player_id INTEGER NOT NULL,
                table_name TEXT NOT NULL,
                stat_name TEXT NOT NULL,
                numerator INTEGER DEFAULT 0,
                denominator INTEGER DEFAULT 0,
                PRIMARY KEY (player_id, table_name, stat_name),
                FOREIGN KEY (player_id) REFERENCES players(id)
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_hands_datetime ON hands(datetime)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_hands_table ON hands(table_name)")
        
        self.connection.commit()
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None