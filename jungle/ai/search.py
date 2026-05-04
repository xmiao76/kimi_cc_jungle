import random
import time
from typing import Optional, List
from jungle.model.game_state import GameState
from jungle.model.pieces import Side
from jungle.model.board import ROWS, get_terrain, Terrain
from jungle.model.rules import Rules, Move
from .evaluation import evaluate
from .transposition import TranspositionTable, EXACT, LOWERBOUND, UPPERBOUND


class Search:
    def __init__(
        self,
        time_limit_ms: int = 1000,
        max_depth: int = 20,
        quiescence_depth: int = 4,
        use_tt: bool = True,
        use_killers: bool = True,
        eval_noise: int = 0,
    ):
        self.time_limit_ms = time_limit_ms
        self.max_depth = max_depth
        self.quiescence_depth = quiescence_depth
        self.use_tt = use_tt
        self.use_killers = use_killers
        self.eval_noise = eval_noise
        self.nodes = 0
        self.tt = TranspositionTable()
        self.killer_moves: dict[int, list] = {}
        self.start_time: float = 0.0
        self._current_depth: int = 0
        self._current_best_move: Optional[Move] = None

    def time_exceeded(self) -> bool:
        elapsed = (time.time() - self.start_time) * 1000
        return elapsed > self.time_limit_ms

    def best_move(self, state: GameState) -> Optional[tuple]:
        self.nodes = 0
        self.tt.clear()
        self.killer_moves.clear()
        self.start_time = time.time()
        self._current_best_move = None

        moves = state.all_legal_moves()
        if not moves:
            return None

        # Iterative deepening
        depth = 1
        while True:
            elapsed = (time.time() - self.start_time) * 1000
            if elapsed > self.time_limit_ms * 0.8:
                break

            self._current_depth = depth
            best_score = -999999
            best_moves_at_depth = []

            ordered_moves = self._order_moves(state, moves, 0)

            for move in ordered_moves:
                if self.time_exceeded():
                    break
                new_state = state.apply_move(move)
                score = -self._negamax(new_state, depth - 1, -999999, 999999)
                if score > best_score:
                    best_score = score
                    best_moves_at_depth = [move]
                elif score == best_score:
                    best_moves_at_depth.append(move)

            if not self.time_exceeded() and best_moves_at_depth:
                self._current_best_move = best_moves_at_depth[0]

            depth += 1
            if depth > self.max_depth:  # safety cap
                break

        return self._current_best_move

    def _order_moves(self, state: GameState, moves: List[Move], ply: int) -> List[Move]:
        def move_priority(m):
            (fr, fc), (tr, tc) = m
            target = state.board[tr][tc]
            attacker = state.board[fr][fc]
            priority = 0

            if target is not None:
                # MVV-LVA: capture priority
                priority += 1000 + target.rank * 10 - (attacker.rank if attacker else 0)
            else:
                # Killer move bonus
                if self.use_killers:
                    killers = self.killer_moves.get(ply, [])
                    if m in killers:
                        priority += 500

                # Forward move priority
                if state.turn is Side.BLUE:
                    priority += tr
                else:
                    priority += (ROWS - 1 - tr)

            return priority

        return sorted(moves, key=move_priority, reverse=True)

    def _negamax(self, state: GameState, depth: int, alpha: int, beta: int) -> int:
        self.nodes += 1

        if self.time_exceeded():
            return evaluate(state, self.eval_noise)

        if state.is_game_over():
            return evaluate(state, self.eval_noise)

        # Transposition table lookup
        state_hash = hash(state)
        if self.use_tt:
            tt_entry = self.tt.lookup(state_hash, depth)
            if tt_entry is not None:
                if tt_entry.flag == EXACT:
                    return tt_entry.score
                elif tt_entry.flag == LOWERBOUND and tt_entry.score >= beta:
                    return tt_entry.score
                elif tt_entry.flag == UPPERBOUND and tt_entry.score <= alpha:
                    return tt_entry.score
        tt_entry = None

        moves = state.all_legal_moves()
        if not moves:
            return -50000

        # At leaf nodes, use quiescence search
        if depth <= 0:
            return self._quiescence(state, alpha, beta)

        ply = self._current_depth - depth
        ordered_moves = self._order_moves(state, moves, ply)

        alpha_orig = alpha
        best_move_at_node = None

        for move in ordered_moves:
            if self.time_exceeded():
                break
            new_state = state.apply_move(move)
            score = -self._negamax(new_state, depth - 1, -beta, -alpha)
            if score >= beta:
                # Beta cutoff — store killer move if not a capture
                if self.use_killers:
                    target = state.board[move[1][0]][move[1][1]]
                    if target is None:
                        killers = self.killer_moves.setdefault(ply, [])
                        if move not in killers:
                            killers.insert(0, move)
                            if len(killers) > 2:
                                killers.pop()
                if self.use_tt:
                    self.tt.store(state_hash, depth, score, LOWERBOUND, move)
                return beta
            if score > alpha:
                alpha = score
                best_move_at_node = move

        flag = EXACT
        if alpha <= alpha_orig:
            flag = UPPERBOUND
        elif alpha >= beta:
            flag = LOWERBOUND
        if self.use_tt:
            self.tt.store(state_hash, depth, alpha, flag, best_move_at_node)

        return alpha

    def _quiescence(self, state: GameState, alpha: int, beta: int, qdepth: int = 0) -> int:
        self.nodes += 1

        if state.is_game_over():
            return evaluate(state, self.eval_noise)

        stand_pat = evaluate(state, self.eval_noise)
        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat

        if qdepth >= self.quiescence_depth:
            return alpha

        tactical_moves = []
        from jungle.model.board import COLS
        for r in range(ROWS):
            for c in range(COLS):
                piece = state.board[r][c]
                if piece is not None and piece.side == state.turn:
                    for tr, tc in Rules.get_legal_moves(state, r, c):
                        target = state.board[tr][tc]
                        terrain = get_terrain(tr, tc)
                        is_capture = target is not None
                        is_den_entry = terrain in (Terrain.RED_DEN, Terrain.BLUE_DEN)
                        if is_capture or is_den_entry:
                            tactical_moves.append(((r, c), (tr, tc)))

        if not tactical_moves:
            return alpha

        def capture_priority(m):
            (fr, fc), (tr, tc) = m
            target = state.board[tr][tc]
            attacker = state.board[fr][fc]
            if target is not None:
                return 1000 + target.rank * 10 - (attacker.rank if attacker else 0)
            return 0

        tactical_moves.sort(key=capture_priority, reverse=True)

        for move in tactical_moves:
            new_state = state.apply_move(move)
            score = -self._quiescence(new_state, -beta, -alpha, qdepth + 1)
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

        return alpha
