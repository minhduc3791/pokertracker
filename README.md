# PokerTracker

Real-time poker statistics HUD overlay for Natural8 with a detailed statistics viewer.

## Features

- **Real-time HUD Overlay** - Displays player statistics on top of your poker tables
- **Hand History Parsing** - Automatically parses Natural8 hand history files
- **Player Statistics** - Tracks VPIP, 3Bet, CBet, WTSD, W$SD and more
- **Multi-Table Support** - Separate HUD for each table
- **Statistics Viewer** - Detailed view with player selection and filtering
- **System Tray Integration** - Runs in background with tray icon
- **Background Operation** - Starts minimized, runs when Natural8 is active

## Requirements

- Windows 10/11 (for HUD overlay)
- Python 3.8+
- Natural8 poker client

## Installation

```bash
# Clone the repository
git clone https://github.com/minhduc3791/pokertracker.git
cd pokertracker

# Install dependencies
pip install -r requirements.txt
```

## Windows Installation (with GUI)

```bash
pip install transparent-overlay pywin32 PyQt5
```

## Usage

### Running the Tracker

```bash
python -m src.main
```

### Configuration

Edit `config.json` in the project root:

```json
{
    "natural8_process_name": "Natural8.exe",
    "hand_history_directory": "./hand-histories",
    "hero_screen_name": "YourScreenName",
    "database_path": "poker_tracker.db"
}
```

### Statistics Viewer

Run the viewer to see detailed player statistics:

```bash
python -m src.viewer
```

The viewer allows you to:
- View all players with summary statistics
- Select a player to see detailed breakdown
- Filter by table name
- Sort by any statistic
- See hand history samples

## Project Structure

```
pokertracker/
├── src/
│   ├── main.py           # Main entry point
│   ├── config.py         # Configuration management
│   ├── database.py       # SQLite database manager
│   ├── natural8_parser.py # Hand history parser
│   ├── stats_engine.py   # Statistics calculation
│   ├── process_detector.py # Natural8 process detection
│   ├── file_watcher.py    # Hand history file watcher
│   ├── hud.py             # HUD overlay
│   ├── tray.py            # System tray manager
│   ├── app.py             # Application shell
│   └── viewer.py          # Statistics viewer
├── tests/                # Test suite
├── hand-histories/       # Hand history files
├── config.json           # Configuration
├── requirements.txt      # Python dependencies
└── README.md
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
