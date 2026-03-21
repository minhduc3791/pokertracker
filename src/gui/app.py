"""Flask-based web GUI for PokerTracker statistics viewer."""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, jsonify, request

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database import DatabaseManager
from src.config import ConfigManager

app = Flask(__name__)

db_path = None


def get_db():
    """Get database instance."""
    global db_path
    if db_path is None:
        config = ConfigManager()
        db_path = config.get('database_path', 'poker_tracker.db')
    return DatabaseManager(db_path)


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')


@app.route('/api/players')
def get_players():
    """Get all players with summary stats."""
    db = get_db()
    players = db.get_player_summary()
    
    result = []
    for p in players:
        stats = p.get('stats', {})
        vpip = stats.get('VPIP', (0, 0))
        three_bet = stats.get('3BET', (0, 0))
        wtsd = stats.get('WTSD', (0, 0))
        w_sd = stats.get('W$SD', (0, 0))
        
        result.append({
            'id': p['id'],
            'screen_name': p['screen_name'],
            'is_hero': p.get('is_hero', False),
            'hands_played': p.get('hands_played') or 0,
            'tables_played': p.get('tables_played') or 0,
            'vpip': {
                'numerator': vpip[0],
                'denominator': vpip[1],
                'percent': round(vpip[0] / vpip[1] * 100) if vpip[1] else 0
            },
            'three_bet': {
                'numerator': three_bet[0],
                'denominator': three_bet[1],
                'percent': round(three_bet[0] / three_bet[1] * 100) if three_bet[1] else 0
            },
            'wtsd': {
                'numerator': wtsd[0],
                'denominator': wtsd[1],
                'percent': round(wtsd[0] / wtsd[1] * 100) if wtsd[1] else 0
            },
            'w_sd': {
                'numerator': w_sd[0],
                'denominator': w_sd[1],
                'percent': round(w_sd[0] / w_sd[1] * 100) if w_sd[1] else 0
            }
        })
    
    return jsonify(result)


@app.route('/api/players/<int:player_id>')
def get_player_detail(player_id):
    """Get detailed stats for a player."""
    db = get_db()
    
    player = db.get_player_by_id(player_id)
    if not player:
        return jsonify({'error': 'Player not found'}), 404
    
    stats = db.get_player_stats_all_tables(player_id)
    tables = db.get_tables_for_player(player_id)
    
    all_stats = {}
    for stat_name, (num, den) in stats.items():
        all_stats[stat_name] = {
            'numerator': num,
            'denominator': den,
            'percent': round(num / den * 100) if den else 0
        }
    
    return jsonify({
        'id': player[0],
        'screen_name': player[1],
        'is_hero': player[2],
        'tables': tables,
        'stats': all_stats
    })


@app.route('/api/summary')
def get_summary():
    """Get overall statistics."""
    db = get_db()
    return jsonify({
        'total_hands': db.get_hand_count(),
        'total_players': db.get_player_count()
    })


def run_server(host='127.0.0.1', port=5000):
    """Run the GUI server."""
    app.run(host=host, port=port, debug=True)


if __name__ == '__main__':
    run_server()
