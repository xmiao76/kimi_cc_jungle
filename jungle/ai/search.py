import random
from typing import Optional
from jungle.model.game_state import GameState
from jungle.model.pieces import Side
from jungle.model.rules import Rules
from .evaluation import evaluate

class Search:
    def __init__(self, depth: int = 3):
        self.max_depth = depth
        self.nodes = 0

    def best_move(self, state: GameState) -> Optional[tuple]:
        self.nodes = 0
        moves = state.all_legal_moves()
        if not moves:
            return None

        best_score = -999999
        best_moves = []

        # Move ordering: captures first, then forward moves
        def move_priority(m):
            (fr, fc), (tr, tc) = m
            target = state.board[tr][tc]
            if target is not None:
                return 1000 + target.rank * 10 - state.board[fr][fc].rank
            # Forward move priority based on side
            if state.turn is Side.BLUE:
                return tr
            return (ROWS - 1 - tr)

        moves.sort(key=move_priority, reverse=True)

        for move in moves:
            new_state = state.apply_move(move)
            score = -self._negamax(new_state, self.max_depth - 1, -999999, 999999)
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)

        return random.choice(best_moves) if best_moves else None

    def _negamax(self, state: GameState, depth: int, alpha: int, beta: int) -> int:
        self.nodes += 1
        if depth == 0 or state.is_game_over():
            return evaluate(state)

        moves = state.all_legal_moves()
        if not moves:
            # No legal moves = loss
            return -50000

        # Simple move ordering
        def move_priority(m):
            (fr, fc), (tr, tc) = m
            target = state.board[tr][tc]
            if target is not None:
                return 1000 + target.rank * 10 - state.board[fr][fc].rank
            if state.turn is Side.BLUE:
                return tr
            return (ROWS - 1 - tr)

        moves.sort(key=move_priority, reverse=True)

        for move in moves:
            new_state = state.apply_move(move)
            score = -self._negamax(new_state, depth - 1, -beta, -alpha)
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha

# Import here to avoid circular reference at top level
from jungle.model.board import ROWS
