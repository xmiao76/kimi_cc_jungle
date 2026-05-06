import pytest
from jungle.model.board import Terrain, get_terrain
from jungle.model.pieces import Piece, PieceType, Side, BLUE_RAT, BLUE_CAT, BLUE_DOG, BLUE_WOLF, BLUE_LEOPARD, BLUE_TIGER, BLUE_LION, BLUE_ELEPHANT, RED_RAT, RED_CAT, RED_DOG, RED_WOLF, RED_LEOPARD, RED_TIGER, RED_LION, RED_ELEPHANT
from jungle.model.game_state import GameState
from jungle.model.rules import Rules

def make_state_with(board_dict: dict, turn: Side = Side.BLUE) -> GameState:
    """Helper to create a GameState from a sparse dict of (r,c): Piece."""
    from jungle.model.board import COLS, ROWS
    board = [[None for _ in range(COLS)] for _ in range(ROWS)]
    for (r, c), piece in board_dict.items():
        board[r][c] = piece
    return GameState(board, turn)

class TestBasicMovement:
    def test_orthogonal_moves(self):
        # Blue rat at (4,3) on land bridge
        state = make_state_with({(4, 3): BLUE_RAT})
        moves = state.legal_moves_for(4, 3)
        assert sorted(moves) == [(3, 3), (4, 2), (4, 4), (5, 3)]

    def test_no_diagonal(self):
        state = make_state_with({(4, 3): BLUE_RAT})
        moves = state.legal_moves_for(4, 3)
        assert (3, 2) not in moves
        assert (3, 4) not in moves

    def test_blocked_by_edge(self):
        state = make_state_with({(0, 0): BLUE_RAT})
        moves = state.legal_moves_for(0, 0)
        assert sorted(moves) == [(0, 1), (1, 0)]

    def test_blocked_by_own_piece(self):
        state = make_state_with({(4, 3): BLUE_RAT, (4, 4): BLUE_CAT})
        moves = state.legal_moves_for(4, 3)
        assert (4, 4) not in moves

class TestRiverRules:
    def test_only_rat_enters_river(self):
        # Blue cat adjacent to river at (3,1)
        state = make_state_with({(2, 1): BLUE_CAT})
        moves = state.legal_moves_for(2, 1)
        assert (3, 1) not in moves  # river, cat cannot enter
        assert (2, 0) in moves
        assert (2, 2) in moves
        assert (1, 1) in moves

    def test_rat_enters_river(self):
        state = make_state_with({(2, 1): BLUE_RAT})
        moves = state.legal_moves_for(2, 1)
        assert (3, 1) in moves  # rat can enter river

    def test_rat_moves_in_river(self):
        state = make_state_with({(3, 1): BLUE_RAT})
        moves = state.legal_moves_for(3, 1)
        # Adjacent river squares
        assert (4, 1) in moves
        assert (3, 2) in moves
        # Can exit to land
        assert (2, 1) in moves
        assert (3, 0) in moves  # land at col 0
        # Cannot enter land bridge col 3 from col 2? Wait, (3,2) is river, (3,3) is land.
        # From (3,1), adjacent squares are (2,1), (4,1), (3,0), (3,2). (3,2) is river.
        assert (3, 2) in moves

    def test_land_piece_cannot_capture_rat_in_water(self):
        state = make_state_with({(2, 1): BLUE_CAT, (3, 1): RED_RAT})
        moves = state.legal_moves_for(2, 1)
        assert (3, 1) not in moves

    def test_rat_in_water_can_be_captured_by_rat_in_water(self):
        state = make_state_with({(3, 1): BLUE_RAT, (3, 2): RED_RAT})
        moves = state.legal_moves_for(3, 1)
        assert (3, 2) in moves

    def test_rat_in_water_cannot_capture_land_elephant(self):
        # Rat in water vs elephant on land — special power requires rat on land
        state = make_state_with({(3, 1): BLUE_RAT, (2, 1): RED_ELEPHANT})
        moves = state.legal_moves_for(3, 1)
        assert (2, 1) not in moves

class TestRiverLeaps:
    def test_tiger_horizontal_leap_right(self):
        # Blue tiger at (4, 0) leaps right across river cols 1,2 to (4, 3)
        state = make_state_with({(4, 0): BLUE_TIGER})
        moves = state.legal_moves_for(4, 0)
        assert (4, 3) in moves

    def test_tiger_horizontal_leap_left(self):
        # Red tiger at (4, 6) leaps left across river cols 5,4 to (4, 3)
        state = make_state_with({(4, 6): RED_TIGER}, turn=Side.RED)
        moves = state.legal_moves_for(4, 6)
        assert (4, 3) in moves

    def test_lion_horizontal_leap_from_bridge(self):
        # Blue lion at (4, 3) leaps left across cols 2,1 (river) to col 0
        state = make_state_with({(4, 3): BLUE_LION})
        moves = state.legal_moves_for(4, 3)
        assert (4, 0) in moves
        assert (4, 6) in moves  # right leap across cols 4,5

    def test_lion_horizontal_leap_to_bridge(self):
        state = make_state_with({(4, 0): BLUE_LION})
        moves = state.legal_moves_for(4, 0)
        assert (4, 3) in moves

    def test_lion_vertical_leap_down(self):
        # Blue lion at (2, 1) leaps down across river rows 3-5 to (6, 1)
        state = make_state_with({(2, 1): BLUE_LION})
        moves = state.legal_moves_for(2, 1)
        assert (6, 1) in moves

    def test_lion_vertical_leap_up(self):
        # Red lion at (6, 1) leaps up across river rows 5-3 to (2, 1)
        state = make_state_with({(6, 1): RED_LION}, turn=Side.RED)
        moves = state.legal_moves_for(6, 1)
        assert (2, 1) in moves

    def test_leap_blocked_by_rat(self):
        # Tiger leap from (4,0) to (4,3) blocked by rat at (4,1)
        state = make_state_with({(4, 0): BLUE_TIGER, (4, 1): RED_RAT})
        moves = state.legal_moves_for(4, 0)
        assert (4, 3) not in moves

    def test_lion_leap_blocked_by_rat(self):
        # Lion vertical leap from (2,1) to (6,1) blocked by rat at (4,1)
        state = make_state_with({(2, 1): BLUE_LION, (4, 1): RED_RAT})
        moves = state.legal_moves_for(2, 1)
        assert (6, 1) not in moves

    def test_tiger_no_vertical_leap(self):
        # Tiger can only leap horizontally (3 cols), not vertically (4 rows)
        state = make_state_with({(2, 1): BLUE_TIGER})
        moves = state.legal_moves_for(2, 1)
        assert (6, 1) not in moves

    def test_leap_captures_on_landing(self):
        # Lion leaps and lands on enemy piece
        state = make_state_with({(4, 0): BLUE_LION, (4, 3): RED_CAT})
        moves = state.legal_moves_for(4, 0)
        assert (4, 3) in moves  # can capture

class TestTraps:
    def test_trap_reduces_defender_rank(self):
        # Blue lion attacks red rat in blue trap (0,2)
        state = make_state_with({(0, 1): BLUE_LION, (0, 2): RED_RAT})
        moves = state.legal_moves_for(0, 1)
        # Blue lion can capture red rat in blue trap because rat's rank is 0 in enemy trap
        assert (0, 2) in moves

    def test_own_trap_is_safe(self):
        # Red lion attacks blue rat in red trap (7,3)
        state = make_state_with({(7, 3): BLUE_RAT, (6, 3): RED_LION}, turn=Side.RED)
        moves = state.legal_moves_for(6, 3)
        # Blue rat is in RED trap (enemy trap for blue), so blue rat rank = 0
        # Red lion can capture
        assert (7, 3) in moves

    def test_any_piece_can_capture_in_enemy_trap(self):
        # Blue cat captures red lion in blue trap
        state = make_state_with({(0, 2): RED_LION, (0, 1): BLUE_CAT})
        moves = state.legal_moves_for(0, 1)
        assert (0, 2) in moves  # cat can capture lion because lion rank is 0 in enemy trap

class TestRankCapture:
    def test_higher_rank_wins(self):
        # Place on land squares, not river
        state = make_state_with({(2, 3): BLUE_ELEPHANT, (2, 4): RED_LION})
        moves = state.legal_moves_for(2, 3)
        assert (2, 4) in moves  # Elephant (8) >= Lion (7)

    def test_lower_rank_cannot_capture(self):
        state = make_state_with({(4, 3): RED_CAT, (4, 4): BLUE_DOG})
        # Red cat (2) cannot capture blue dog (3)
        moves = state.legal_moves_for(4, 3)
        assert (4, 4) not in moves

    def test_equal_rank_can_capture(self):
        state = make_state_with({(2, 3): BLUE_DOG, (2, 4): RED_DOG})
        moves = state.legal_moves_for(2, 3)
        assert (2, 4) in moves

    def test_rat_kills_elephant_on_land(self):
        # Standard rule: rat on land can kill elephant (special exception to ranking)
        state = make_state_with({(2, 3): BLUE_RAT, (2, 4): RED_ELEPHANT})
        moves = state.legal_moves_for(2, 3)
        assert (2, 4) in moves

    def test_elephant_cannot_capture_rat_on_land(self):
        # Elephant cannot capture rat (special rule exception to normal ranking)
        state = make_state_with({(2, 3): BLUE_ELEPHANT, (2, 4): RED_RAT})
        moves = state.legal_moves_for(2, 3)
        assert (2, 4) not in moves

    def test_elephant_cannot_capture_rat_in_water(self):
        # "A rat in the water is invulnerable to capture by any piece on land"
        # Elephant on land cannot capture rat in river
        state = make_state_with({(2, 1): BLUE_ELEPHANT, (3, 1): RED_RAT})
        moves = state.legal_moves_for(2, 1)
        assert (3, 1) not in moves

class TestDenRules:
    def test_cannot_enter_own_den(self):
        state = make_state_with({(1, 3): BLUE_RAT})
        moves = state.legal_moves_for(1, 3)
        assert (0, 3) not in moves  # own den

    def test_can_enter_enemy_den_and_wins(self):
        # Blue rat next to red den
        state = make_state_with({(7, 3): BLUE_RAT})
        moves = state.legal_moves_for(7, 3)
        assert (8, 3) in moves  # can enter enemy den

class TestWinConditions:
    def test_win_by_den_entry(self):
        state = make_state_with({(8, 3): BLUE_RAT})
        assert state.winner() is Side.BLUE

    def test_win_by_annihilation(self):
        state = make_state_with({(4, 3): BLUE_RAT})
        assert state.winner() is Side.BLUE

    def test_no_winner_at_start(self):
        state = GameState()
        assert state.winner() is None

class TestInitialBoard:
    def test_initial_pieces(self):
        state = GameState()
        # Blue
        assert state.board[0][0] == BLUE_LION
        assert state.board[0][6] == BLUE_TIGER
        assert state.board[1][1] == BLUE_DOG
        assert state.board[1][5] == BLUE_CAT
        assert state.board[2][0] == BLUE_RAT
        assert state.board[2][2] == BLUE_LEOPARD
        assert state.board[2][4] == BLUE_WOLF
        assert state.board[2][6] == BLUE_ELEPHANT
        # Red (rotational)
        assert state.board[8][6] == RED_LION
        assert state.board[8][0] == RED_TIGER
        assert state.board[7][5] == RED_DOG
        assert state.board[7][1] == RED_CAT
        assert state.board[6][6] == RED_RAT
        assert state.board[6][4] == RED_LEOPARD
        assert state.board[6][2] == RED_WOLF
        assert state.board[6][0] == RED_ELEPHANT

    def test_blue_opens(self):
        state = GameState()
        assert state.turn is Side.BLUE
