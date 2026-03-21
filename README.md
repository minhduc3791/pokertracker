# PokerTracker

Real-time poker statistics HUD overlay with cross-platform GUI.

## Features

- **Desktop GUI** - Single exe with menu-based interface
- **Hand History Import** - Import from Natural8/GGPoker, PokerStars, and more
- **Player Statistics** - Track VPIP, 3Bet, CBet, WTSD, W$SD and more
- **Player Search** - Search and view detailed stats for any player
- **HUD Overlay** - Real-time stats display on poker tables (Windows)
- **Multi-Platform** - Works on Windows, Mac, Linux

## Quick Start

### Run the GUI

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python -m src.gui
```

### Build Executable (Windows)

```bash
# Install PyInstaller
pip install pyinstaller

# Build single executable
pyinstaller PokerTracker.spec

# Output: dist/PokerTracker.exe
```

## GUI Menu

| Menu | Options |
|------|---------|
| **File** | Import Hand Histories, Exit |
| **Tracker** | Start/Stop HUD, Start/Stop Tracking |
| **View** | Player Statistics, Dashboard |
| **Settings** | Configure |
| **Help** | About |

## Configuration

Click **Settings > Configure** or edit `config.json`:

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
| VPIP | Voluntarily Put In Pot |
| 3BET | 3-Bet Percentage |
| F_TB | Fold to Bet |
| CALL_CB | Call Continuation Bet |
| RAISE_CB | Raise Continuation Bet |
| CB_TURN | Turn Barrel |
| WTSD | Went to Showdown |
| W$SD | Won Money at Showdown |

## Project Structure

```
pokertracker/
├── src/
│   ├── gui.py              # Main GUI application
│   ├── main.py             # CLI entry point
│   ├── config.py           # Configuration
│   ├── database.py         # SQLite database
│   ├── natural8_parser.py   # Hand history parser
│   ├── stats_engine.py     # Statistics calculation
│   ├── process_detector.py # Process detection
│   └── file_watcher.py    # File monitoring
├── tests/                  # Test suite
├── config.json.example     # Configuration template
├── requirements.txt        # Dependencies
├── PokerTracker.spec       # PyInstaller spec
└── README.md
```

## Development

```bash
# Run tests
pytest tests/ -v

# Run GUI
python -m src.gui

# Run CLI tracker
python -m src.main
```

## License

MIT License
