import pytest
from jungle.model.board import (
    get_terrain, is_river, is_trap, is_own_den, in_bounds,
    Terrain, RIVER, BLUE_TRAPS, RED_TRAPS, BLUE_DEN, RED_DEN, ROWS, COLS
)
from jungle.model.pieces import Side

def test_dimensions():
    assert ROWS == 9
    assert COLS == 7

def test_blue_den():
    assert get_terrain(0, 3) is Terrain.BLUE_DEN
    assert is_own_den(0, 3, Side.BLUE)
    assert not is_own_den(0, 3, Side.RED)

def test_red_den():
    assert get_terrain(8, 3) is Terrain.RED_DEN
    assert is_own_den(8, 3, Side.RED)
    assert not is_own_den(8, 3, Side.BLUE)

def test_blue_traps():
    for coord in BLUE_TRAPS:
        assert get_terrain(*coord) is Terrain.BLUE_TRAP
        assert is_trap(*coord, Side.BLUE)
        assert not is_trap(*coord, Side.RED)

def test_red_traps():
    for coord in RED_TRAPS:
        assert get_terrain(*coord) is Terrain.RED_TRAP
        assert is_trap(*coord, Side.RED)
        assert not is_trap(*coord, Side.BLUE)

def test_river_layout():
    # Two 3x2 river sections: rows 3-5, cols 1-2 and cols 4-5
    expected_river = set()
    for r in range(3, 6):
        for c in range(1, 3):
            expected_river.add((r, c))
        for c in range(4, 6):
            expected_river.add((r, c))
    assert RIVER == expected_river
    assert len(RIVER) == 12  # 2 sections * 3 rows * 2 cols = 12

def test_river_tiles():
    for r in range(ROWS):
        for c in range(COLS):
            if (r, c) in RIVER:
                assert get_terrain(r, c) is Terrain.RIVER
                assert is_river(r, c)
            else:
                assert not is_river(r, c)

def test_land_bridge():
    # Column 3, rows 3-5 should be land
    for r in range(3, 6):
        assert get_terrain(r, 3) is Terrain.LAND
        assert not is_river(r, 3)

def test_edges_are_land():
    # Col 0 and col 6, rows 3-5 should be land
    for r in range(3, 6):
        assert get_terrain(r, 0) is Terrain.LAND
        assert get_terrain(r, 6) is Terrain.LAND

def test_in_bounds():
    assert in_bounds(0, 0)
    assert in_bounds(8, 6)
    assert not in_bounds(-1, 0)
    assert not in_bounds(0, -1)
    assert not in_bounds(9, 0)
    assert not in_bounds(0, 7)
