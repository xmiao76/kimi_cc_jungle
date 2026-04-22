import pytest
from jungle.model.game_state import GameState
from jungle.model.pieces import Side, BLUE_RAT, BLUE_LION, RED_RAT, RED_LION
from jungle.model.rules import Rules

class TestGameState:
    def test_copy(self):
        state = GameState()
        copy = state.copy()
        assert copy.turn == state.turn
        assert copy.board == state.board
        # Mutate copy should not affect original
        copy.board[0][0] = None
        assert state.board[0][0] is not None

    def test_apply_move(self):
        state = GameState()
        # Move blue rat from (2,0) to (3,0)
        move = ((2, 0), (3, 0))
        new_state = state.apply_move(move)
        assert new_state.board[3][0] == BLUE_RAT
        assert new_state.board[2][0] is None
        assert new_state.turn is Side.RED
        assert len(new_state.move_history) == 1
        # Original state unchanged
        assert state.board[2][0] == BLUE_RAT

    def test_turn_alternation(self):
        state = GameState()
        assert state.turn is Side.BLUE
        state = state.apply_move(((2, 0), (3, 0)))
        assert state.turn is Side.RED
        state = state.apply_move(((6, 6), (5, 6)))
        assert state.turn is Side.BLUE

    def test_all_legal_moves_count(self):
        state = GameState()
        blue_moves = state.all_legal_moves(Side.BLUE)
        # At start, most pieces have limited mobility due to layout
        # We just check it's a non-empty list and all moves are valid
        assert len(blue_moves) > 0
        for move in blue_moves:
            (fr, fc), (tr, tc) = move
            assert state.board[fr][fc] is not None
            assert state.board[fr][fc].side is Side.BLUE
            assert (tr, tc) in state.legal_moves_for(fr, fc)

    def test_game_over_by_den(self):
        from jungle.model.board import COLS, ROWS
        board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        board[8][3] = BLUE_RAT
        state = GameState(board, Side.BLUE)
        assert state.is_game_over()
        assert state.winner() is Side.BLUE

    def test_game_over_by_annihilation(self):
        from jungle.model.board import COLS, ROWS
        board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        board[4][3] = BLUE_LION
        state = GameState(board, Side.BLUE)
        assert state.is_game_over()
        assert state.winner() is Side.BLUE

    def test_not_game_over_initial(self):
        state = GameState()
        assert not state.is_game_over()
        assert state.winner() is None
