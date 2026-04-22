from enum import Enum, auto
from typing import Set, Tuple, Optional
from .pieces import Side

class Terrain(Enum):
    LAND = auto()
    RIVER = auto()
    BLUE_TRAP = auto()
    RED_TRAP = auto()
    BLUE_DEN = auto()
    RED_DEN = auto()

# Board dimensions
ROWS = 9
COLS = 7

# Terrain definitions
BLUE_TRAPS: Set[Tuple[int, int]] = {(0, 2), (0, 4), (1, 3)}
RED_TRAPS: Set[Tuple[int, int]] = {(8, 2), (8, 4), (7, 3)}

BLUE_DEN: Tuple[int, int] = (0, 3)
RED_DEN: Tuple[int, int] = (8, 3)

# River: two 3x2 blocks (3 rows x 2 cols) in the center, separated by land bridge at col 3
# Cols 0 and 6 are land (edges), col 3 is land bridge
RIVER: Set[Tuple[int, int]] = set()
for r in range(3, 6):
    for c in range(1, 3):
        RIVER.add((r, c))
    for c in range(4, 6):
        RIVER.add((r, c))

def get_terrain(row: int, col: int) -> Terrain:
    coord = (row, col)
    if coord == BLUE_DEN:
        return Terrain.BLUE_DEN
    if coord == RED_DEN:
        return Terrain.RED_DEN
    if coord in BLUE_TRAPS:
        return Terrain.BLUE_TRAP
    if coord in RED_TRAPS:
        return Terrain.RED_TRAP
    if coord in RIVER:
        return Terrain.RIVER
    return Terrain.LAND

def is_river(row: int, col: int) -> bool:
    return (row, col) in RIVER

def is_trap(row: int, col: int, side: Side) -> bool:
    """Return True if (row,col) is a trap belonging to the given side."""
    coord = (row, col)
    if side is Side.BLUE:
        return coord in BLUE_TRAPS
    return coord in RED_TRAPS

def is_enemy_trap(row: int, col: int, side: Side) -> bool:
    """Return True if (row,col) is an enemy trap for the given side."""
    coord = (row, col)
    if side is Side.BLUE:
        return coord in RED_TRAPS
    return coord in BLUE_TRAPS

def is_den(row: int, col: int, side: Side) -> bool:
    if side is Side.BLUE:
        return (row, col) == RED_DEN
    return (row, col) == BLUE_DEN

def is_own_den(row: int, col: int, side: Side) -> bool:
    if side is Side.BLUE:
        return (row, col) == BLUE_DEN
    return (row, col) == RED_DEN

def in_bounds(row: int, col: int) -> bool:
    return 0 <= row < ROWS and 0 <= col < COLS
