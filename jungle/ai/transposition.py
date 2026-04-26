"""Zobrist hashing and transposition table for the Jungle AI engine."""

import random
from typing import Optional
from dataclasses import dataclass

from jungle.model.board import ROWS, COLS
from jungle.model.pieces import PieceType, Side

# Fixed seed for deterministic hashing across runs
_RNG = random.Random(42)

# Zobrist keys: one per (piece_type, side, row, col) combination
ZOBRIST_KEYS: dict[tuple[PieceType, Side, int, int], int] = {}
for pt in PieceType:
    for side in Side:
        for r in range(ROWS):
            for c in range(COLS):
                ZOBRIST_KEYS[(pt, side, r, c)] = _RNG.getrandbits(64)

# Side-to-move key
ZOBRIST_SIDE = _RNG.getrandbits(64)


EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2


@dataclass
class TTEntry:
    """Single transposition table entry."""
    hash_key: int
    depth: int
    score: int
    flag: int
    best_move: Optional[tuple] = None


class TranspositionTable:
    """Simple fixed-size transposition table with replacement scheme."""

    def __init__(self, size: int = 1_048_576):
        self.size = size
        self.table: list[Optional[TTEntry]] = [None] * size
        self.hits = 0
        self.misses = 0
        self.stores = 0

    def _index(self, hash_key: int) -> int:
        return hash_key % self.size

    def lookup(self, hash_key: int, depth: int) -> Optional[TTEntry]:
        idx = self._index(hash_key)
        entry = self.table[idx]
        if entry is not None and entry.hash_key == hash_key and entry.depth >= depth:
            self.hits += 1
            return entry
        self.misses += 1
        return None

    def store(self, hash_key: int, depth: int, score: int, flag: int,
              best_move: Optional[tuple] = None) -> None:
        idx = self._index(hash_key)
        existing = self.table[idx]
        # Replace if empty or if new entry is deeper
        if existing is None or existing.hash_key != hash_key or depth >= existing.depth:
            self.table[idx] = TTEntry(hash_key, depth, score, flag, best_move)
            self.stores += 1

    def clear(self) -> None:
        self.table = [None] * self.size
        self.hits = 0
        self.misses = 0
        self.stores = 0

    def stats(self) -> dict[str, int]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "stores": self.stores,
        }
