# PokerTracker

Real-time poker statistics HUD overlay for Natural8 with a web-based statistics dashboard.

## Features

- **Real-time HUD Overlay** - Displays player statistics on top of your poker tables (Windows only)
- **Web Dashboard** - Beautiful web-based GUI for viewing player statistics
- **Hand History Parsing** - Automatically parses Natural8 hand history files
- **Player Statistics** - Tracks VPIP, 3Bet, CBet, WTSD, W$SD and more
- **Multi-Table Support** - Separate HUD for each table
- **System Tray Integration** - Runs in background with tray icon (Windows)
- **Background Operation** - Starts minimized, runs when Natural8 is active

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard

```bash
python -m src.gui.app
```

Then open your browser to: **http://localhost:5000**

### 3. Run the Console Viewer (alternative)

```bash
python -m src.viewer
```

### 4. Run the Tracker

```bash
python -m src.main
```

## Dashboard Features

- **Player List** - Scrollable list with VPIP, 3B, W$SD stats
- **Player Selection** - Click any player to view detailed stats
- **Stat Classifications** - Tight/Normal/Loose, Weak/Strong indicators
- **Progress Bars** - Visual representation of percentages
- **All Stats View** - Complete breakdown of all tracked statistics
- **Auto-refresh** - Click Refresh button to reload data

## Project Structure

```
pokertracker/
├── src/
│   ├── main.py              # Main tracker entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # SQLite database manager
│   ├── natural8_parser.py   # Hand history parser
│   ├── stats_engine.py      # Statistics calculation
│   ├── process_detector.py  # Natural8 process detection
│   ├── file_watcher.py      # Hand history file watcher
│   ├── hud.py               # HUD overlay (Windows)
│   ├── tray.py              # System tray manager
│   ├── app.py               # Application shell (Windows)
│   ├── viewer.py             # Console statistics viewer
│   └── gui/
│       ├── app.py           # Web dashboard server
│       └── templates/
│           └── index.html   # Dashboard UI
├── tests/                   # Test suite
├── hand-histories/          # Hand history files
├── config.json              # Configuration
├── requirements.txt          # Python dependencies
└── README.md
```

## Configuration

Edit `config.json` in the project root:

```json
{
    "natural8_process_name": "Natural8.exe",
    "hand_history_directory": "./hand-histories",
    "hero_screen_name": "YourScreenName",
    "database_path": "poker_tracker.db"
}
```

## Statistics Tracked

| Stat | Description |
|------|-------------|
| VPIP | Voluntarily Put In Pot - % of hands played pre-flop |
| 3B | 3-Bet - % of hands 3-bet pre-flop |
| F_TB | Fold to Bet - % of bets faced that were folded |
| CBet | Continuation Bet - % of continuation bets on flop |
| CBet Turn | Barrel - % of turn barrels after CBet |
| WTSD | Went to Showdown - % of hands reaching showdown |
| W$SD | Won Money at Showdown - % of showdowns won |

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Building for Windows

```bash
# Install build dependencies
pip install pyinstaller transparent-overlay pywin32 PyQt5

# Build executable
./build.bat
```

Output: `dist/PokerTracker/PokerTracker.exe`

## License

MIT License

## Support

Report issues at: https://github.com/minhduc3791/pokertracker/issues
