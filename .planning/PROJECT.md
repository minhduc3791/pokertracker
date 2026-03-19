# PokerTracker

## What This Is

A Windows desktop application for tracking poker statistics from Natural8 sessions. Users configure a hand history directory and process name, then the app displays live HUD stats per table for all players.

## Core Value

Accurate poker statistics on every player at every table, updated in real-time from hand history.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Import hand histories from Natural8 (extensible parser architecture)
- [ ] Detect running Natural8 instances by process name
- [ ] HUD panel per table showing player stats
- [ ] Track stats: VPIP, 3bet%, Fold to bet, Call to cbet, Raise to cbet, Cbet turn, Fold cbet turn, Call cbet turn, Raise cbet turn, Went to SD, Won at SD

### Out of Scope

- Inject into poker client window — external overlay only
- Mobile platforms
- Cloud sync / account system
- Support for other poker platforms until explicitly added

## Context

- Hand histories stored locally by Natural8
- Multiple tables can be open simultaneously
- User plays as "Hero" — their stats tracked separately
- Stats derived from parsed hand history, not live reads

## Constraints

- **Platform**: Windows only
- **Language**: Python
- **Distribution**: Standalone .exe via PyInstaller
- **Release delivery**: Download link for each release

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| External HUD overlay | Non-blocking, simpler than window injection | — Pending |
| Configurable process name | Natural8 may update process name | Flexibility |
| Configurable hand history directory | User controls where Natural8 stores histories | Flexibility |
| Extensible parser architecture | Other platforms can be added later | Future-proofing |

---
*Last updated: 2026-03-19 after initialization*
