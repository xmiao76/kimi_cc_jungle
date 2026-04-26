from typing import List, Tuple, Optional, Any
from .pieces import Piece, PieceType, Side
from .board import (
    in_bounds, is_river, is_own_den, Terrain, get_terrain,
    ROWS, COLS,
)

Move = Tuple[Tuple[int, int], Tuple[int, int]]  # ((from_row, from_col), (to_row, to_col))

ORTHOGONAL = [(-1, 0), (1, 0), (0, -1), (0, 1)]

class Rules:
    @staticmethod
    def get_legal_moves(state: Any, from_row: int, from_col: int) -> List[Tuple[int, int]]:
        piece = state.board[from_row][from_col]
        if piece is None or piece.side != state.turn:
            return []
        return Rules._legal_dests_for_piece(state, from_row, from_col, piece)

    @staticmethod
    def _legal_dests_for_piece(state: Any, row: int, col: int, piece: Piece) -> List[Tuple[int, int]]:
        legal = []
        # Normal orthogonal moves
        for dr, dc in ORTHOGONAL:
            nr, nc = row + dr, col + dc
            if not in_bounds(nr, nc):
                continue
            if Rules._can_move_to(state, row, col, nr, nc, piece):
                legal.append((nr, nc))

        # Lion/Tiger river leaps
        if piece.piece_type in (PieceType.LION, PieceType.TIGER):
            legal.extend(Rules._river_leaps(state, row, col, piece))
        return legal

    @staticmethod
    def _can_move_to(state: Any, fr: int, fc: int, tr: int, tc: int, piece: Piece) -> bool:
        # Cannot enter own den
        if is_own_den(tr, tc, piece.side):
            return False

        # River entry restriction: only rat may enter river
        if is_river(tr, tc) and piece.piece_type is not PieceType.RAT:
            return False

        target = state.board[tr][tc]
        if target is None:
            return True
        if target.side == piece.side:
            return False
        return Rules._can_capture(fr, fc, tr, tc, piece, target)

    @staticmethod
    def _can_capture(fr: int, fc: int, tr: int, tc: int, attacker: Piece, defender: Piece) -> bool:
        # Rat in water is immune to land pieces, only another rat in water can capture it
        attacker_in_water = is_river(fr, fc)
        defender_in_water = is_river(tr, tc)

        if defender_in_water and not attacker_in_water:
            return False  # land piece cannot capture rat in water

        # Determine effective ranks
        atk_rank = attacker.rank
        def_rank = defender.rank

        # Defender in enemy trap has rank 0
        terrain = get_terrain(tr, tc)
        if terrain is Terrain.BLUE_TRAP and defender.side is Side.RED:
            def_rank = 0
        if terrain is Terrain.RED_TRAP and defender.side is Side.BLUE:
            def_rank = 0

        # Elephant cannot capture rat (special rule)
        if attacker.piece_type is PieceType.ELEPHANT and defender.piece_type is PieceType.RAT:
            return False

        # Rat on land can kill elephant
        if attacker.piece_type is PieceType.RAT and defender.piece_type is PieceType.ELEPHANT and not attacker_in_water:
            return True

        # Normal rank-based capture
        return atk_rank >= def_rank

    @staticmethod
    def _river_leaps(state: Any, row: int, col: int, piece: Piece) -> List[Tuple[int, int]]:
        leaps = []
        # Tiger: vertically only
        # Lion: vertically or horizontally
        directions = []
        if piece.piece_type is PieceType.TIGER:
            directions = [(-1, 0), (1, 0)]
        else:  # LION
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if not in_bounds(nr, nc):
                continue
            if not is_river(nr, nc):
                continue
            # Traverse river squares in this direction; blocked by any rat in the water
            rat_blocks = False
            landing_r, landing_c = nr, nc
            while in_bounds(landing_r, landing_c) and is_river(landing_r, landing_c):
                water_piece = state.board[landing_r][landing_c]
                if water_piece is not None and water_piece.piece_type is PieceType.RAT:
                    rat_blocks = True
                    break
                landing_r += dr
                landing_c += dc

            if rat_blocks or not in_bounds(landing_r, landing_c):
                continue
            if is_river(landing_r, landing_c):
                continue

            # Check if landing is legal (can't be own den, etc.)
            if Rules._can_move_to(state, row, col, landing_r, landing_c, piece):
                leaps.append((landing_r, landing_c))

        return leaps

    @staticmethod
    def all_legal_moves(state: Any, side: Optional[Side] = None) -> List[Move]:
        side = side or state.turn
        moves = []
        for r in range(ROWS):
            for c in range(COLS):
                piece = state.board[r][c]
                if piece is not None and piece.side is side:
                    for tr, tc in Rules.get_legal_moves(state, r, c):
                        moves.append(((r, c), (tr, tc)))
        return moves

    @staticmethod
    def apply_move(state: Any, move: Move) -> Any:
        # Use fast copy for GameState to avoid deepcopy overhead
        if hasattr(state, 'fast_copy'):
            new_state = state.fast_copy()
        else:
            from copy import deepcopy
            new_state = deepcopy(state)
        (fr, fc), (tr, tc) = move
        piece = new_state.board[fr][fc]
        assert piece is not None

        # Incrementally update Zobrist hash
        from jungle.ai.transposition import ZOBRIST_KEYS, ZOBRIST_SIDE
        old_hash = new_state._zobrist_hash
        if old_hash is None:
            old_hash = new_state._compute_zobrist_hash()

        # XOR out piece from source square
        old_hash ^= ZOBRIST_KEYS[(piece.piece_type, piece.side, fr, fc)]

        # XOR out captured piece from target square (if any)
        captured = new_state.board[tr][tc]
        if captured is not None:
            old_hash ^= ZOBRIST_KEYS[(captured.piece_type, captured.side, tr, tc)]

        # XOR in piece at target square
        old_hash ^= ZOBRIST_KEYS[(piece.piece_type, piece.side, tr, tc)]

        # XOR side-to-move (turn flips)
        old_hash ^= ZOBRIST_SIDE

        new_state._zobrist_hash = old_hash

        new_state.board[tr][tc] = piece
        new_state.board[fr][fc] = None
        new_state.turn = piece.side.opposite()
        new_state.move_history.append(move)
        new_state._winner = None  # clear cache
        return new_state

    @staticmethod
    def check_winner(state: Any) -> Optional[Side]:
        for r in range(ROWS):
            for c in range(COLS):
                piece = state.board[r][c]
                if piece is None:
                    continue
                terrain = get_terrain(r, c)
                if terrain is Terrain.RED_DEN and piece.side is Side.BLUE:
                    return Side.BLUE
                if terrain is Terrain.BLUE_DEN and piece.side is Side.RED:
                    return Side.RED

        # Win by capturing all enemy pieces
        blue_pieces = sum(1 for r in range(ROWS) for c in range(COLS)
                          if state.board[r][c] is not None and state.board[r][c].side is Side.BLUE)
        red_pieces = sum(1 for r in range(ROWS) for c in range(COLS)
                         if state.board[r][c] is not None and state.board[r][c].side is Side.RED)
        if blue_pieces == 0:
            return Side.RED
        if red_pieces == 0:
            return Side.BLUE
        return None

    @staticmethod
    def is_game_over(state: Any) -> bool:
        return Rules.check_winner(state) is not None
