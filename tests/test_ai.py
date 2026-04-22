import pytest
from jungle.model.pieces import Side, BLUE_RAT, BLUE_LION, RED_RAT, RED_LION
from jungle.model.game_state import GameState
from jungle.model.board import COLS, ROWS
from jungle.ai.ai_player import AIPlayer
from jungle.ai.evaluation import evaluate
from jungle.ai.search import Search

def make_state_with(board_dict: dict, turn: Side = Side.BLUE) -> GameState:
    from jungle.model.board import COLS, ROWS
    board = [[None for _ in range(COLS)] for _ in range(ROWS)]
    for (r, c), piece in board_dict.items():
        board[r][c] = piece
    return GameState(board, turn)

class TestEvaluation:
    def test_blue_advantage(self):
        state = GameState()
        score = evaluate(state)
        # Initial position should be roughly balanced, not a huge swing
        assert -200 < score < 200

    def test_blue_win_is_high(self):
        board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        board[8][3] = BLUE_RAT
        state = GameState(board, Side.BLUE)
        assert evaluate(state) > 90000

    def test_red_win_is_high_for_red_turn(self):
        # When it's Red's turn and Red has won, evaluate is strongly positive
        board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        board[0][3] = RED_RAT
        state = GameState(board, Side.RED)
        assert evaluate(state) > 90000

class TestSearch:
    def test_finds_move(self):
        state = GameState()
        search = Search(depth=2)
        move = search.best_move(state)
        assert move is not None
        (fr, fc), (tr, tc) = move
        assert state.board[fr][fc] is not None
        assert state.board[fr][fc].side is Side.BLUE

    def test_ai_vs_random_wins(self):
        import random
        ai_side = Side.BLUE
        ai = AIPlayer(depth=3)
        state = GameState()
        moves = 0
        while not state.is_game_over() and moves < 500:
            if state.turn is ai_side:
                move = ai.choose_move(state)
            else:
                legal = state.all_legal_moves()
                move = random.choice(legal) if legal else None
            if move is None:
                break
            state = state.apply_move(move)
            moves += 1
        assert state.is_game_over()
        assert state.winner() is ai_side

    def test_ai_prefers_winning_move(self):
        # Blue rat one step from enemy den, red has a piece so no annihilation
        board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        board[7][3] = BLUE_RAT
        board[0][0] = RED_LION
        state = GameState(board, Side.BLUE)
        ai = AIPlayer(depth=1)
        move = ai.choose_move(state)
        assert move == ((7, 3), (8, 3))
