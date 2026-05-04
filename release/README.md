# Jungle / Dou Shou Qi

A polished Windows desktop board game application with built-in AI. Play the classic Chinese strategy game Jungle (Dou Shou Qi) against the computer or watch two AIs battle it out.

## Launch

Double-click `JungleGame.exe` in this folder. No installation required.

## Gameplay

Jungle is a two-player strategy board game played on a 7x9 grid. Each player controls 8 animal pieces ranked from Elephant (8) down to Rat (1).

### Objective
- Move any piece into the opponent's den, OR
- Capture all opposing pieces.

### Movement
- Click a piece to select it. Legal moves are highlighted in green.
- Click a highlighted destination square to move.
- Pieces move one square orthogonally (up, down, left, right).

### Special Rules
- **River**: Only the Rat may enter the water. Tigers and Lions can leap over the river vertically; Lions may also leap horizontally.
- **Traps**: A piece in an enemy trap has its rank reduced to zero and can be captured by any enemy piece.
- **Rat vs Elephant**:
  - A Rat on land **can** kill an Elephant (special exception to normal ranking).
  - An Elephant **cannot** capture a Rat in any case (special exception).
  - A Rat in water **cannot** kill an Elephant on land.
  - An Elephant on land **cannot** capture a Rat in water.
- **Rat in Water**: A Rat in water is immune to all land pieces. Only another Rat in water can capture it.

## Controls

- **New Game**: Start a fresh game.
- **Flip Board**: Rotate the board 180 degrees for viewing (does not change game state).
- **vs AI / Hotseat (2P) / AI vs AI**: Choose game mode.
- **Play as Blue / Red**: Choose your side (visible in vs AI mode).
- **Difficulty**: Choose AI strength — Beginner, Intermediate, Advanced, or Expert.
- **AI Think Time**: Fine-tune how long the AI thinks per move (200-5000 ms).

## Notes

- Standard Dou Shou Qi rules are used.
- Ambiguities resolved: Lion outranks Tiger; Elephant cannot capture Rat (chosen variant); Rat can capture Elephant on land (special exception); only enemy traps reduce rank; Leopards and Dogs do not leap rivers.
- Variant: Elephant cannot capture Rat — this is a chosen rule variant differing from some standard rulesets.
- The AI uses minimax search with alpha-beta pruning.

## Credits

Completed by **Kimi** (model: kimi-k2.6) via Claude Code agent.
