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
        search = Search(time_limit_ms=500)
        move = search.best_move(state)
        assert move is not None
        (fr, fc), (tr, tc) = move
        assert state.board[fr][fc] is not None
        assert state.board[fr][fc].side is Side.BLUE

    def test_ai_vs_random_wins(self):
        import random
        ai_side = Side.BLUE
        ai = AIPlayer(time_limit_ms=1000)
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
        ai = AIPlayer(time_limit_ms=500)
        move = ai.choose_move(state)
        assert move == ((7, 3), (8, 3))

    def test_tt_speedup(self):
        state = GameState()
        search = Search(time_limit_ms=200)
        # First call clears TT internally, so test _negamax directly
        search.start_time = __import__('time').time()
        search._current_depth = 3
        nodes_before = search.nodes
        score1 = search._negamax(state, 2, -999999, 999999)
        nodes_after_first = search.nodes - nodes_before
        score2 = search._negamax(state, 2, -999999, 999999)
        nodes_after_second = search.nodes - nodes_after_first
        assert score1 == score2
        # Second search should use fewer nodes due to TT hits
        assert nodes_after_second < nodes_after_first

    def test_search_respects_time_limit(self):
        import time
        state = GameState()
        search = Search(time_limit_ms=200)
        start = time.time()
        move = search.best_move(state)
        elapsed = (time.time() - start) * 1000
        assert move is not None
        # Allow 20% buffer plus overhead
        assert elapsed < 300

    def test_iterative_deepening_reaches_depth_two(self):
        state = GameState()
        search = Search(time_limit_ms=500)
        search.best_move(state)
        # With 500ms, the search should easily reach depth >= 2
        assert search._current_depth >= 2

    def test_beginner_eval_noise(self):
        state = GameState()
        scores = set()
        for _ in range(10):
            from jungle.ai.evaluation import evaluate
            scores.add(evaluate(state, noise=10))
        # With noise, not all evaluations are identical
        assert len(scores) > 1

    def test_beginner_disabled_tt(self):
        state = GameState()
        search_no_tt = Search(time_limit_ms=200, max_depth=3, use_tt=False)
        search_tt = Search(time_limit_ms=200, max_depth=3, use_tt=True)
        move_no_tt = search_no_tt.best_move(state)
        move_tt = search_tt.best_move(state)
        # Both should produce legal moves
        assert move_no_tt is not None
        assert move_tt is not None
        # TT-enabled search should use the transposition table
        assert search_tt.tt.stats()["stores"] > 0

    def test_beginner_max_depth_capped(self):
        state = GameState()
        search = Search(time_limit_ms=200, max_depth=2)
        search.best_move(state)
        assert search._current_depth <= 2

    def test_beginner_beats_random(self):
        import random
        from jungle.ai.ai_player import AIPlayer
        ai_side = Side.BLUE
        ai = AIPlayer(
            time_limit_ms=200,
            strength_config={
                "max_depth": 3,
                "quiescence_depth": 0,
                "use_tt": False,
                "use_killers": False,
                "eval_noise": 10,
            },
        )
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
