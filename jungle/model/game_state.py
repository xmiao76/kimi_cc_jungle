from typing import Optional, List, Tuple
from copy import deepcopy
from .pieces import (
    Piece, Side,
    BLUE_LION, BLUE_TIGER, BLUE_LEOPARD, BLUE_WOLF, BLUE_DOG, BLUE_CAT, BLUE_RAT, BLUE_ELEPHANT,
    RED_LION, RED_TIGER, RED_LEOPARD, RED_WOLF, RED_DOG, RED_CAT, RED_RAT, RED_ELEPHANT,
)
from .board import ROWS, COLS, Terrain, get_terrain
from .rules import Rules, Move

class GameState:
    def __init__(self, board: Optional[List[List[Optional[Piece]]]] = None, turn: Side = Side.BLUE):
        if board is None:
            board = self._initial_board()
        self.board: List[List[Optional[Piece]]] = board
        self.turn: Side = turn
        self.move_history: List[Move] = []
        self._winner: Optional[Side] = None

    @staticmethod
    def _initial_board() -> List[List[Optional[Piece]]]:
        b: List[List[Optional[Piece]]] = [[None for _ in range(COLS)] for _ in range(ROWS)]
        # Blue side (top)
        b[0][0] = BLUE_LION
        b[0][6] = BLUE_TIGER
        b[1][1] = BLUE_DOG
        b[1][5] = BLUE_CAT
        b[2][0] = BLUE_RAT
        b[2][2] = BLUE_LEOPARD
        b[2][4] = BLUE_WOLF
        b[2][6] = BLUE_ELEPHANT

        # Red side (bottom) - 180° rotation of blue
        b[8][6] = RED_LION
        b[8][0] = RED_TIGER
        b[7][5] = RED_DOG
        b[7][1] = RED_CAT
        b[6][6] = RED_RAT
        b[6][4] = RED_LEOPARD
        b[6][2] = RED_WOLF
        b[6][0] = RED_ELEPHANT
        return b

    def copy(self) -> 'GameState':
        new = GameState(deepcopy(self.board), self.turn)
        new.move_history = list(self.move_history)
        new._winner = self._winner
        return new

    def winner(self) -> Optional[Side]:
        if self._winner is None:
            self._winner = Rules.check_winner(self)
        return self._winner

    def is_game_over(self) -> bool:
        return self.winner() is not None

    def apply_move(self, move: Move) -> 'GameState':
        return Rules.apply_move(self, move)

    def legal_moves_for(self, row: int, col: int) -> List[Tuple[int, int]]:
        return Rules.get_legal_moves(self, row, col)

    def all_legal_moves(self, side: Optional[Side] = None) -> List[Move]:
        return Rules.all_legal_moves(self, side)

    def __repr__(self) -> str:
        lines = []
        for r in range(ROWS):
            row_strs = []
            for c in range(COLS):
                p = self.board[r][c]
                if p is None:
                    terrain = get_terrain(r, c)
                    if terrain is Terrain.RIVER:
                        row_strs.append('~~')
                    elif terrain in (Terrain.BLUE_TRAP, Terrain.RED_TRAP):
                        row_strs.append('TP')
                    elif terrain in (Terrain.BLUE_DEN, Terrain.RED_DEN):
                        row_strs.append('DN')
                    else:
                        row_strs.append('  ')
                else:
                    abbr = p.piece_type.name[:2]
                    if p.side is Side.BLUE:
                        row_strs.append(abbr.lower())
                    else:
                        row_strs.append(abbr.upper())
            lines.append(' '.join(row_strs))
        return '\n'.join(lines)
