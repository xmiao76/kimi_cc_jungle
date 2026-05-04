import random
from jungle.model.board import ROWS, COLS, get_terrain, Terrain, is_river, in_bounds
from jungle.model.pieces import Piece, PieceType, Side
from jungle.model.game_state import GameState
from jungle.model.rules import Rules

# Piece values — refined to better reflect true strength
PIECE_VALUES = {
    PieceType.ELEPHANT: 110,
    PieceType.LION: 90,
    PieceType.TIGER: 70,
    PieceType.LEOPARD: 50,
    PieceType.WOLF: 35,
    PieceType.DOG: 20,
    PieceType.CAT: 12,
    PieceType.RAT: 25,
}

# Piece-square tables (from Blue's perspective; Red uses vertically mirrored tables)
# 9 rows x 7 cols. Positive = good for the piece.
_PST_RAT = [
    [0, 0, 5, 10, 5, 0, 0],
    [0, 2, 8, 12, 8, 2, 0],
    [2, 5, 10, 8, 10, 5, 2],
    [5, 10, 15, 5, 15, 10, 5],
    [5, 10, 15, 5, 15, 10, 5],
    [5, 10, 15, 5, 15, 10, 5],
    [2, 5, 10, 8, 10, 5, 2],
    [0, 2, 8, 12, 8, 2, 0],
    [0, 0, 5, 10, 5, 0, 0],
]

_PST_CAT = [
    [0, 0, 0, 2, 0, 0, 0],
    [0, 2, 4, 6, 4, 2, 0],
    [2, 4, 6, 8, 6, 4, 2],
    [2, 4, 8, 10, 8, 4, 2],
    [2, 4, 8, 10, 8, 4, 2],
    [2, 4, 8, 10, 8, 4, 2],
    [2, 4, 6, 8, 6, 4, 2],
    [0, 2, 4, 6, 4, 2, 0],
    [0, 0, 0, 2, 0, 0, 0],
]

_PST_DOG = [
    [0, 0, 2, 4, 2, 0, 0],
    [0, 2, 4, 6, 4, 2, 0],
    [2, 4, 6, 8, 6, 4, 2],
    [2, 4, 8, 10, 8, 4, 2],
    [2, 4, 8, 10, 8, 4, 2],
    [2, 4, 8, 10, 8, 4, 2],
    [2, 4, 6, 8, 6, 4, 2],
    [0, 2, 4, 6, 4, 2, 0],
    [0, 0, 2, 4, 2, 0, 0],
]

_PST_WOLF = [
    [0, 0, 2, 4, 2, 0, 0],
    [0, 2, 4, 6, 4, 2, 0],
    [2, 4, 6, 8, 6, 4, 2],
    [2, 6, 10, 12, 10, 6, 2],
    [2, 6, 10, 12, 10, 6, 2],
    [2, 6, 10, 12, 10, 6, 2],
    [2, 4, 6, 8, 6, 4, 2],
    [0, 2, 4, 6, 4, 2, 0],
    [0, 0, 2, 4, 2, 0, 0],
]

_PST_LEOPARD = [
    [0, 0, 2, 4, 2, 0, 0],
    [0, 2, 4, 8, 4, 2, 0],
    [2, 4, 8, 10, 8, 4, 2],
    [2, 6, 10, 14, 10, 6, 2],
    [2, 6, 10, 14, 10, 6, 2],
    [2, 6, 10, 14, 10, 6, 2],
    [2, 4, 8, 10, 8, 4, 2],
    [0, 2, 4, 8, 4, 2, 0],
    [0, 0, 2, 4, 2, 0, 0],
]

_PST_TIGER = [
    [0, 0, 0, 2, 0, 0, 0],
    [0, 0, 2, 4, 2, 0, 0],
    [0, 2, 4, 8, 4, 2, 0],
    [2, 4, 8, 12, 8, 4, 2],
    [2, 4, 8, 12, 8, 4, 2],
    [2, 4, 8, 12, 8, 4, 2],
    [0, 2, 4, 8, 4, 2, 0],
    [0, 0, 2, 4, 2, 0, 0],
    [0, 0, 0, 2, 0, 0, 0],
]

_PST_LION = [
    [0, 0, 0, 2, 0, 0, 0],
    [0, 0, 2, 4, 2, 0, 0],
    [0, 2, 4, 8, 4, 2, 0],
    [2, 4, 8, 12, 8, 4, 2],
    [2, 4, 8, 12, 8, 4, 2],
    [2, 4, 8, 12, 8, 4, 2],
    [0, 2, 4, 8, 4, 2, 0],
    [0, 0, 2, 4, 2, 0, 0],
    [0, 0, 0, 2, 0, 0, 0],
]

_PST_ELEPHANT = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 2, 4, 2, 0, 0],
    [0, 2, 4, 6, 4, 2, 0],
    [2, 4, 6, 8, 6, 4, 2],
    [2, 4, 6, 8, 6, 4, 2],
    [2, 4, 6, 8, 6, 4, 2],
    [0, 2, 4, 6, 4, 2, 0],
    [0, 0, 2, 4, 2, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
]

PIECE_SQUARE_TABLES_BLUE = {
    PieceType.RAT: _PST_RAT,
    PieceType.CAT: _PST_CAT,
    PieceType.DOG: _PST_DOG,
    PieceType.WOLF: _PST_WOLF,
    PieceType.LEOPARD: _PST_LEOPARD,
    PieceType.TIGER: _PST_TIGER,
    PieceType.LION: _PST_LION,
    PieceType.ELEPHANT: _PST_ELEPHANT,
}

# Red sees the board flipped vertically
PIECE_SQUARE_TABLES_RED = {
    pt: list(reversed(tbl)) for pt, tbl in PIECE_SQUARE_TABLES_BLUE.items()
}

# Endgame material threshold (sum of non-rat piece values)
ENDGAME_THRESHOLD = 200


def evaluate(state: GameState, noise: int = 0) -> int:
    if state.is_game_over():
        winner = state.winner()
        if winner is state.turn:
            return 100000
        elif winner is not None:
            return -100000
        return 0

    score = 0
    total_material = 0

    for r in range(ROWS):
        for c in range(COLS):
            piece = state.board[r][c]
            if piece is None:
                continue

            val = PIECE_VALUES[piece.piece_type]
            total_material += val

            # Material and advancement
            if piece.side is Side.BLUE:
                progress = r
                score += val + progress * 2
            else:
                progress = (ROWS - 1 - r)
                score -= val + progress * 2

            # Piece-square table bonus
            pst = PIECE_SQUARE_TABLES_BLUE if piece.side is Side.BLUE else PIECE_SQUARE_TABLES_RED
            pst_bonus = pst[piece.piece_type][r][c]
            if piece.side is Side.BLUE:
                score += pst_bonus
            else:
                score -= pst_bonus

            # Rat in water bonus
            if piece.piece_type is PieceType.RAT and is_river(r, c):
                if piece.side is Side.BLUE:
                    score += 15
                else:
                    score -= 15

            # Trap adjacency threat
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if in_bounds(nr, nc):
                    terrain = get_terrain(nr, nc)
                    if piece.side is Side.BLUE and terrain is Terrain.RED_TRAP:
                        score += 10
                    elif piece.side is Side.RED and terrain is Terrain.BLUE_TRAP:
                        score -= 10

            # Den proximity / threat
            terrain = get_terrain(r, c)
            if piece.side is Side.BLUE:
                if terrain is Terrain.RED_DEN:
                    score += 500
                elif terrain in (Terrain.RED_TRAP,):
                    pass  # already handled by trap adjacency
            else:
                if terrain is Terrain.BLUE_DEN:
                    score -= 500

            # Adjacent to enemy den
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if in_bounds(nr, nc):
                    adj_terrain = get_terrain(nr, nc)
                    if piece.side is Side.BLUE and adj_terrain is Terrain.RED_DEN:
                        score += 200
                    elif piece.side is Side.RED and adj_terrain is Terrain.BLUE_DEN:
                        score -= 200

            # Two squares away from enemy den
            for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                nr, nc = r + dr, c + dc
                if in_bounds(nr, nc):
                    adj_terrain = get_terrain(nr, nc)
                    if piece.side is Side.BLUE and adj_terrain is Terrain.RED_DEN:
                        score += 50
                    elif piece.side is Side.RED and adj_terrain is Terrain.BLUE_DEN:
                        score -= 50

            # Trap vulnerability (piece in enemy trap)
            terrain = get_terrain(r, c)
            if terrain is Terrain.BLUE_TRAP and piece.side is Side.RED:
                score += 30  # good for blue
            if terrain is Terrain.RED_TRAP and piece.side is Side.BLUE:
                score -= 30

    # Endgame scaling
    is_endgame = total_material < ENDGAME_THRESHOLD
    if is_endgame:
        # In endgame, rat advancement is more important
        for r in range(ROWS):
            for c in range(COLS):
                piece = state.board[r][c]
                if piece is not None and piece.piece_type is PieceType.RAT:
                    if piece.side is Side.BLUE:
                        score += r * 3
                    else:
                        score -= (ROWS - 1 - r) * 3

    if noise > 0:
        score += random.randint(-noise, noise)

    return score if state.turn is Side.BLUE else -score
