# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Jungle / Dou Shou Qi — a Windows desktop board game with PyQt6 GUI and built-in AI. Written in Python 3.10+. Packaged as a single `.exe` via PyInstaller.

The AI engine uses iterative deepening negamax with alpha-beta pruning, quiescence search, transposition tables (Zobrist hashing), piece-square tables, and killer move heuristics. It searches to depth 5-7+ within a configurable time limit (default 1000ms).

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

# Coverage report (target: >= 80%)
python -m pytest tests/ --cov=jungle --cov-report=term-missing

# Build release executable
pyinstaller JungleGame.spec --noconfirm
# Then copy to release/:
cp dist/JungleGame.exe release/JungleGame.exe
cp README.md release/README.md
```

**Note**: No linting or type-checking tools are configured (no ruff, black, mypy, or flake8 in `pyproject.toml`). The project relies on pytest for validation.

## Architecture

### Three-layer separation

| Layer | Directory | Responsibility |
|---|---|---|
| Model | `jungle/model/` | Game rules, board geometry, piece types, move generation, win detection. No UI or I/O. |
| AI | `jungle/ai/` | Static evaluation, search, transposition tables, move ordering. Depends only on model. |
| UI | `jungle/ui/` | PyQt6 widgets, rendering, input handling, AI turn scheduling. Depends on model and AI. |

### Key architectural patterns

**Immutable-ish game state with Zobrist hashing**: `GameState` stores the board, turn, move history, and a cached Zobrist hash. `Rules.apply_move()` returns a *new* `GameState` via `fast_copy` (shallow board list copy, immutable pieces shared) and incrementally updates the Zobrist hash via XOR operations. The original is never mutated. The AI relies on this for search tree expansion and transposition table lookups.

**Board flipping is a pure view transform**: `BoardWidget._to_draw_coords()` and `_from_draw_coords()` map logical board coordinates to screen coordinates. `_flipped` only affects painting and mouse-event translation; it never mutates `GameState` or swaps sides.

**Signal-driven UI updates**: `GameController` emits `state_changed`, `turn_changed`, `game_over`, `message`, and `capture_made` signals. `MainWindow` connects these to UI updates. The controller schedules AI moves with `QTimer.singleShot` so the UI thread remains responsive.

**Capture rule ordering matters**: `Rules._can_capture()` evaluates conditions in this sequence:
1. Water immunity — land piece cannot capture rat in water.
2. Trap rank reduction — defender in *enemy* trap has rank 0.
3. Elephant→rat block — elephant cannot capture rat (chosen variant).
4. Rat→elephant special — rat on land can kill elephant.
5. Normal rank comparison.
Changing this order changes game behavior.

**River leaps are blocked by any rat**: Lion and Tiger leaps traverse every river square in the direction of the leap. If any square contains a rat (regardless of side), the leap is blocked. This is checked in `Rules._river_leaps()` before landing-square validation.

**AI search architecture** (`jungle/ai/search.py`):
- `Search.best_move()` drives **iterative deepening**: searches depth 1, 2, 3... until `time_limit_ms * 0.8` is exceeded, returning the best move from the last *completed* depth.
- `_negamax()` performs alpha-beta search with **transposition table** lookups/stores (EXACT/LOWERBOUND/UPPERBOUND flags), **killer move** storage on beta cutoffs (up to 2 per ply), and **MVV-LVA** + forward-move ordering.
- At leaf nodes (`depth <= 0`), `_quiescence()` resolves tactical sequences (captures and den entries) up to a depth limit of 4 to mitigate the horizon effect.
- `AIPlayer` and `Search` take `time_limit_ms` (not a fixed depth).

**Evaluation** (`jungle/ai/evaluation.py`):
- Material values + piece-square tables (9×7 grids, vertically mirrored for Red).
- Positional bonuses: rat-in-water (+15), trap adjacency (+10), den proximity (+200 adjacent, +50 two squares away, +500 on den).
- Endgame detection scales rat advancement when total material drops below a threshold.
- Returns a positive score from the perspective of `state.turn`.

### Entry points

- `jungle/__main__.py` — launches the PyQt6 application.
- `jungle/ui/main_window.py` — `MainWindow` sets up menus, controls, and the `BoardWidget`.
- `jungle/ui/game_controller.py` — `GameController` translates square clicks into moves and triggers the AI.

### Key files

| File | Purpose |
|---|---|
| `jungle/ai/search.py` | Iterative deepening negamax, quiescence, TT, killer moves |
| `jungle/ai/evaluation.py` | Static evaluation with piece-square tables |
| `jungle/ai/transposition.py` | Zobrist hashing constants and `TranspositionTable` class |
| `jungle/ai/ai_player.py` | Thin wrapper around `Search` |
| `jungle/model/rules.py` | Move generation, capture logic, state application, win detection |
| `jungle/model/game_state.py` | Board state, turn, history, Zobrist hash, `fast_copy` |
| `jungle/model/board.py` | Terrain geometry, river/trap/den positions |
| `jungle/model/pieces.py` | Piece dataclasses, ranks, sides |
| `jungle/ui/board_widget.py` | PyQt6 board rendering, mouse input, flip transform |
| `jungle/ui/game_controller.py` | Turn logic, AI scheduling, move execution |
| `jungle/ui/main_window.py` | Top-level window, controls, AI think-time slider |

### Testing structure

- `tests/test_board.py` — terrain geometry, river/trap/den positions.
- `tests/test_rules.py` — movement, capture, leaps, traps, win conditions. Uses `make_state_with()` helper to construct sparse board states.
- `tests/test_game_state.py` — turn alternation, apply_move, immutability, game over.
- `tests/test_ai.py` — evaluation symmetry, search finds moves, AI beats random player, prefers winning moves, TT speedup, respects time limits, iterative deepening reaches depth >= 2.
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

**Note**: The in-repo `release/README.md` still refers to the old "AI Delay" slider. When cutting a release, update it to "AI Think Time" to match the current UI.
