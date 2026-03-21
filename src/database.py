import sqlite3
import json
from typing import Optional, List, Dict
from datetime import datetime


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
    
    def check_duplicate(self, hand_id: str, table_name: str, datetime_str: str) -> bool:
        """Check if a hand already exists in the database.
        
        Args:
            hand_id: Unique hand identifier
            table_name: Table name
            datetime_str: Hand datetime string
            
        Returns:
            True if duplicate exists, False otherwise
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT 1 FROM hands WHERE hand_id=? AND table_name=? AND datetime=?",
            (hand_id, table_name, datetime_str)
        )
        return cursor.fetchone() is not None
    
    def insert_hand(self, parsed_hand) -> bool:
        """Insert a parsed hand into the database.
        
        Args:
            parsed_hand: ParsedHand object from parser
            
        Returns:
            True if inserted, False if duplicate
        """
        if self.check_duplicate(
            parsed_hand.hand_id,
            parsed_hand.table_name,
            parsed_hand.datetime.isoformat()
        ):
            return False
        
        cursor = self.connection.cursor()
        cursor.execute(
            """INSERT INTO hands (hand_id, table_name, datetime, raw_text, parsed_data)
               VALUES (?, ?, ?, ?, ?)""",
            (
                parsed_hand.hand_id,
                parsed_hand.table_name,
                parsed_hand.datetime.isoformat(),
                parsed_hand.raw_text,
                json.dumps({
                    'players': [(p.screen_name, p.seat, p.stack, p.is_hero) for p in parsed_hand.players],
                    'actions': [(a.player, a.action_type.value, a.amount, a.street) for a in parsed_hand.actions],
                    'board': parsed_hand.board,
                    'pot_total': parsed_hand.pot_total
                })
            )
        )
        self.connection.commit()
        return True
    
    def get_or_create_player(self, screen_name: str, is_hero: bool = False) -> int:
        """Get or create a player by screen name.
        
        Args:
            screen_name: Player's screen name
            is_hero: Whether this is the hero player
            
        Returns:
            Player ID
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM players WHERE screen_name=?", (screen_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        cursor.execute(
            "INSERT INTO players (screen_name, is_hero) VALUES (?, ?)",
            (screen_name, is_hero)
        )
        self.connection.commit()
        return cursor.lastrowid
    
    def increment_stat(self, player_id: int, table_name: str, stat_name: str,
                       incr_num: int = 0, incr_denom: int = 0):
        """Increment a player's stat with proper numerator/denominator.
        
        Args:
            player_id: Player ID
            table_name: Table name
            stat_name: Stat name (e.g., 'VPIP', 'THREE_BET')
            incr_num: Amount to increment numerator
            incr_denom: Amount to increment denominator
        """
        cursor = self.connection.cursor()
        cursor.execute(
            """INSERT INTO player_stats (player_id, table_name, stat_name, numerator, denominator)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(player_id, table_name, stat_name) DO UPDATE SET
               numerator = numerator + ?,
               denominator = denominator + ?""",
            (player_id, table_name, stat_name, incr_num, incr_denom,
             incr_num, incr_denom)
        )
        self.connection.commit()
    
    def get_player_stats(self, player_id: int, table_name: str) -> Dict[str, tuple]:
        """Get all stats for a player at a table.
        
        Args:
            player_id: Player ID
            table_name: Table name
            
        Returns:
            Dict of stat_name: (numerator, denominator)
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT stat_name, numerator, denominator FROM player_stats WHERE player_id=? AND table_name=?",
            (player_id, table_name)
        )
        return {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
    
    def get_hand_count(self) -> int:
        """Get total number of hands in database."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM hands")
        return cursor.fetchone()[0]
    
    def get_player_count(self) -> int:
        """Get total number of unique players."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM players")
        return cursor.fetchone()[0]
    
    def get_all_players(self) -> List[tuple]:
        """Get all players.
        
        Returns:
            List of (player_id, screen_name, is_hero) tuples
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, screen_name, is_hero FROM players ORDER BY screen_name")
        return cursor.fetchall()
    
    def get_player_by_id(self, player_id: int) -> Optional[tuple]:
        """Get player by ID.
        
        Args:
            player_id: Player ID
            
        Returns:
            (player_id, screen_name, is_hero) or None
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, screen_name, is_hero FROM players WHERE id=?", (player_id,))
        return cursor.fetchone()
    
    def get_player_stats_all_tables(self, player_id: int) -> Dict[str, tuple]:
        """Get all stats for a player aggregated across all tables.
        
        Args:
            player_id: Player ID
            
        Returns:
            Dict of stat_name: (numerator, denominator)
        """
        cursor = self.connection.cursor()
        cursor.execute(
            """SELECT stat_name, SUM(numerator), SUM(denominator) 
               FROM player_stats 
               WHERE player_id=? 
               GROUP BY stat_name""",
            (player_id,)
        )
        return {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
    
    def get_tables_for_player(self, player_id: int) -> List[str]:
        """Get all table names a player has played at.
        
        Args:
            player_id: Player ID
            
        Returns:
            List of table names
        """
        cursor = self.connection.cursor()
        cursor.execute(
            """SELECT DISTINCT table_name FROM player_stats WHERE player_id=?""",
            (player_id,)
        )
        return [row[0] for row in cursor.fetchall()]
    
    def get_player_hand_ids(self, player_id: int, table_name: Optional[str] = None, limit: int = 100) -> List[str]:
        """Get hand IDs that contain this player.
        
        Args:
            player_id: Player ID
            table_name: Optional table filter
            limit: Max number of hands
            
        Returns:
            List of hand IDs
        """
        cursor = self.connection.cursor()
        if table_name:
            cursor.execute(
                """SELECT hand_id FROM hands 
                   WHERE parsed_data LIKE ? 
                   ORDER BY datetime DESC 
                   LIMIT ?""",
                (f'%"{player_id}"%', limit)
            )
        else:
            cursor.execute(
                """SELECT hand_id FROM hands 
                   WHERE parsed_data LIKE ? 
                   ORDER BY datetime DESC 
                   LIMIT ?""",
                (f'%"{player_id}"%', limit)
            )
        return [row[0] for row in cursor.fetchall()]
    
    def get_hand_by_id(self, hand_id: str) -> Optional[Dict]:
        """Get a hand by its ID.
        
        Args:
            hand_id: Hand ID
            
        Returns:
            Dict with hand data or None
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT hand_id, table_name, datetime, raw_text, parsed_data FROM hands WHERE hand_id=?",
            (hand_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            'hand_id': row[0],
            'table_name': row[1],
            'datetime': row[2],
            'raw_text': row[3],
            'parsed_data': json.loads(row[4])
        }
    
    def get_player_summary(self) -> List[Dict]:
        """Get summary statistics for all players.
        
        Returns:
            List of player summaries with aggregated stats
        """
        cursor = self.connection.cursor()
        cursor.execute(
            """SELECT 
                   p.id,
                   p.screen_name,
                   p.is_hero,
                   COUNT(DISTINCT ps.table_name) as tables_played,
                   SUM(CASE WHEN ps.stat_name = 'VPIP' THEN ps.denominator ELSE 0 END) as hands_played
               FROM players p
               LEFT JOIN player_stats ps ON p.id = ps.player_id
               GROUP BY p.id
               ORDER BY hands_played DESC"""
        )
        results = []
        for row in cursor.fetchall():
            player_id = row[0]
            stats = self.get_player_stats_all_tables(player_id)
            results.append({
                'id': player_id,
                'screen_name': row[1],
                'is_hero': row[2],
                'tables_played': row[3],
                'hands_played': row[4],
                'stats': stats
            })
        return results
    
    def get_recent_hands_for_player(self, player_id: int, limit: int = 50) -> List[Dict]:
        """Get recent hands involving this player.
        
        Args:
            player_id: Player ID
            limit: Max hands to return
            
        Returns:
            List of hand dicts
        """
        cursor = self.connection.cursor()
        cursor.execute(
            """SELECT hand_id, table_name, datetime, raw_text, parsed_data 
               FROM hands 
               WHERE parsed_data LIKE ?
               ORDER BY datetime DESC 
               LIMIT ?""",
            (f'%"screen_name",%', limit)
        )
        hands = []
        for row in cursor.fetchall():
            parsed = json.loads(row[4])
            player_names = [p[0] for p in parsed.get('players', [])]
            if str(player_id) in str(parsed) or any(p[1] for p in parsed.get('players', []) if str(player_id) in str(p)):
                hands.append({
                    'hand_id': row[0],
                    'table_name': row[1],
                    'datetime': row[2],
                    'raw_text': row[3],
                    'parsed_data': parsed
                })
        return hands
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None