from jungle.model.board import ROWS, COLS, get_terrain, Terrain
from jungle.model.pieces import Piece, PieceType, Side
from jungle.model.game_state import GameState
from jungle.model.rules import Rules

# Piece values
PIECE_VALUES = {
    PieceType.ELEPHANT: 100,
    PieceType.LION: 80,
    PieceType.TIGER: 60,
    PieceType.LEOPARD: 40,
    PieceType.WOLF: 25,
    PieceType.DOG: 15,
    PieceType.CAT: 10,
    PieceType.RAT: 20,  # Elevated because of special powers
}

# Distance to enemy den bonus
BLUE_DEN_ROW = 8
RED_DEN_ROW = 0

def evaluate(state: GameState) -> int:
    if state.is_game_over():
        winner = state.winner()
        if winner is state.turn:
            return 100000
        elif winner is not None:
            return -100000
        return 0

    score = 0
    blue_mobility = 0
    red_mobility = 0

    for r in range(ROWS):
        for c in range(COLS):
            piece = state.board[r][c]
            if piece is None:
                continue
            val = PIECE_VALUES[piece.piece_type]

            # Advancement bonus
            if piece.side is Side.BLUE:
                progress = r  # further down = higher row number
                score += val + progress * 2
                blue_mobility += len(Rules.get_legal_moves(state, r, c))
            else:
                progress = (ROWS - 1 - r)
                score -= val + progress * 2
                red_mobility += len(Rules.get_legal_moves(state, r, c))

            # Trap penalty
            terrain = get_terrain(r, c)
            if terrain is Terrain.BLUE_TRAP and piece.side is Side.RED:
                score += 30  # red piece in blue trap = vulnerable = good for blue
            if terrain is Terrain.RED_TRAP and piece.side is Side.BLUE:
                score -= 30

            # Den threat bonus
            if piece.side is Side.BLUE and terrain is Terrain.RED_DEN:
                score += 500
            if piece.side is Side.RED and terrain is Terrain.BLUE_DEN:
                score -= 500

    score += (blue_mobility - red_mobility) * 2
    return score if state.turn is Side.BLUE else -score
