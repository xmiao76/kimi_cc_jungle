# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Jungle / Dou Shou Qi — a Windows desktop board game with PyQt6 GUI and built-in AI (negamax alpha-beta). Written in Python 3.10+. Packaged as a single `.exe` via PyInstaller.

## Common Commands

```bash
# Run the GUI application (development)
python -m jungle

# Run all tests
python -m pytest tests/ -v

# Run a single test file
python -m pytest tests/test_rules.py -v

# Run a specific test
python -m pytest tests/test_rules.py::TestRankCapture::test_rat_kills_elephant_on_land -v

# Coverage report
python -m pytest tests/ --cov=jungle --cov-report=term-missing

# Build release executable
pyinstaller JungleGame.spec --noconfirm
# Then copy to release/:
cp dist/JungleGame.exe release/JungleGame.exe
cp README.md release/README.md
```

## Architecture

### Three-layer separation

| Layer | Directory | Responsibility |
|---|---|---|
| Model | `jungle/model/` | Game rules, board geometry, piece types, move generation, win detection. No UI or I/O. |
| AI | `jungle/ai/` | Static evaluation, negamax alpha-beta search, move ordering. Depends only on model. |
| UI | `jungle/ui/` | PyQt6 widgets, rendering, input handling, AI turn scheduling. Depends on model and AI. |

### Key architectural patterns

**Immutable-ish game state**: `GameState` stores the board, turn, and move history. `Rules.apply_move()` returns a *new* `GameState` via `deepcopy`; the original is never mutated. The AI relies on this for search tree expansion.

**Board flipping is a pure view transform**: `BoardWidget._to_draw_coords()` and `_from_draw_coords()` map logical board coordinates to screen coordinates. `_flipped` only affects painting and mouse-event translation; it never mutates `GameState` or swaps sides.

**Signal-driven UI updates**: `GameController` emits `state_changed`, `turn_changed`, `game_over`, and `message` signals. `MainWindow` connects these to UI updates. The controller schedules AI moves with `QTimer.singleShot` so the UI thread remains responsive.

**Capture rule ordering matters**: `Rules._can_capture()` evaluates conditions in this sequence:
1. Water immunity — land piece cannot capture rat in water.
2. Trap rank reduction — defender in *enemy* trap has rank 0.
3. Elephant→rat block — elephant cannot capture rat (chosen variant).
4. Rat→elephant special — rat on land can kill elephant.
5. Normal rank comparison.
Changing this order changes game behavior.

**River leaps are blocked by any rat**: Lion and Tiger leaps traverse every river square in the direction of the leap. If any square contains a rat (regardless of side), the leap is blocked. This is checked in `Rules._river_leaps()` before landing-square validation.

### Entry points

- `jungle/__main__.py` — launches the PyQt6 application.
- `jungle/ui/main_window.py` — `MainWindow` sets up menus, controls, and the `BoardWidget`.
- `jungle/ui/game_controller.py` — `GameController` translates square clicks into moves and triggers the AI.

### Testing structure

- `tests/test_board.py` — terrain geometry, river/trap/den positions.
- `tests/test_rules.py` — movement, capture, leaps, traps, win conditions. Uses `make_state_with()` helper to construct sparse board states.
- `tests/test_game_state.py` — turn alternation, apply_move, immutability, game over.
- `tests/test_ai.py` — evaluation symmetry, search finds moves, AI beats random player.
- `tests/test_ui.py` — MainWindow smoke tests using `pytest-qt` (`qtbot` fixture).

### Rule variant choices

The implementation uses these specific interpretations (document them if they change):
- **Elephant cannot capture rat** — even on land, even if rat is in enemy trap.
- **Rat kills elephant only from land** — rat in water cannot kill elephant on land.
- **Lion outranks Tiger** — standard hierarchy.
- **Only enemy traps reduce rank** — own trap is safe.
- **Leopards and Dogs do not leap rivers**.

### Release packaging

The release artifact is produced by PyInstaller using `JungleGame.spec`. The `release/` folder must contain:
- `JungleGame.exe`
- `README.md`
- `prompt.md`
