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
  - An Elephant **can** capture a Rat by normal rank (8 ≥ 1).
  - A Rat in water **cannot** kill an Elephant on land.
  - An Elephant on land **cannot** capture a Rat in water.
- **Rat in Water**: A Rat in water is immune to all land pieces. Only another Rat in water can capture it.

## Controls

- **New Game**: Start a fresh game.
- **Flip Board**: Rotate the board 180 degrees for viewing (does not change game state).
- **Play as Blue / Red**: Choose your side.
- **vs AI / Hotseat (2P) / AI vs AI**: Choose game mode.
- **AI Delay**: Adjust the pause between AI moves in AI-vs-AI mode.

## Notes

- Standard Dou Shou Qi rules are used.
- Ambiguities resolved: Lion outranks Tiger; Elephant can capture Rat normally (standard rule); Rat can capture Elephant on land (special exception); only enemy traps reduce rank; Leopards and Dogs do not leap rivers.
- Variant NOT used: Some versions forbid Elephant from killing Rat. We follow the standard Wikipedia rule where Elephant may defeat Rat by rank.
- The AI uses minimax search with alpha-beta pruning.

## Credits

Completed by **Kimi** (model: kimi-k2.6) via Claude Code agent.
