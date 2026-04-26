from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from jungle.model.game_state import GameState
from jungle.model.pieces import Side
from jungle.model.rules import Rules

class GameController(QObject):
    state_changed = pyqtSignal()
    turn_changed = pyqtSignal(Side)
    game_over = pyqtSignal(Side)  # winner
    message = pyqtSignal(str)
    capture_made = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._state: GameState = GameState()
        self._selected: tuple[int, int] | None = None
        self._human_side: Side = Side.BLUE
        self._ai_enabled: bool = True
        self._ai_vs_ai: bool = False
        self._ai_thinking: bool = False
        self._ai_delay_ms: int = 300

    @property
    def state(self) -> GameState:
        return self._state

    @property
    def human_side(self) -> Side:
        return self._human_side

    def set_human_side(self, side: Side):
        self._human_side = side

    def set_ai_enabled(self, enabled: bool):
        self._ai_enabled = enabled
        if not enabled:
            self._ai_vs_ai = False

    def set_ai_vs_ai(self, enabled: bool):
        self._ai_vs_ai = enabled
        if enabled:
            self._ai_enabled = True

    def set_ai_delay(self, ms: int):
        self._ai_delay_ms = max(0, ms)

    def new_game(self):
        self._state = GameState()
        self._selected = None
        self._ai_thinking = False
        self.state_changed.emit()
        self.turn_changed.emit(self._state.turn)
        if self._ai_vs_ai:
            self.message.emit("AI vs AI mode. Watching...")
            self._check_ai_turn()
        elif self._ai_enabled:
            self.message.emit(f"New game. You play as {self._human_side.name}. Blue moves first.")
        else:
            self.message.emit("New game. Hotseat mode. Blue moves first.")
        self._check_ai_turn()

    def handle_square_click(self, row: int, col: int):
        if self._state.is_game_over() or self._ai_thinking or self._ai_vs_ai:
            return
        if self._ai_enabled and self._state.turn != self._human_side:
            return

        piece = self._state.board[row][col]
        if self._selected is not None:
            sr, sc = self._selected
            if (row, col) == self._selected:
                self._selected = None
                self.state_changed.emit()
                return
            if (row, col) in self._state.legal_moves_for(sr, sc):
                self._execute_move((sr, sc), (row, col))
                self._selected = None
                return
            if piece is not None and piece.side == self._state.turn:
                self._selected = (row, col)
                self.state_changed.emit()
                return
            self._selected = None
            self.state_changed.emit()
            return
        else:
            if piece is not None and piece.side == self._state.turn:
                self._selected = (row, col)
                self.state_changed.emit()
            return

    def _execute_move(self, fr: tuple[int, int], tr: tuple[int, int]):
        move = (fr, tr)
        attacker = self._state.board[fr[0]][fr[1]]
        target = self._state.board[tr[0]][tr[1]]
        self._state = self._state.apply_move(move)
        self.state_changed.emit()
        self.turn_changed.emit(self._state.turn)
        if target is not None and attacker is not None:
            msg = f"{attacker.side.name} {attacker.piece_type.name} captured {target.side.name} {target.piece_type.name}!"
            self.capture_made.emit(msg)
        if self._state.is_game_over():
            winner = self._state.winner()
            if winner:
                self.game_over.emit(winner)
                self.message.emit(f"Game over! {winner.name} wins!")
            return
        self._check_ai_turn()

    def _check_ai_turn(self):
        if self._state.is_game_over():
            return
        if self._ai_vs_ai or (self._ai_enabled and self._state.turn != self._human_side):
            self._ai_thinking = True
            if not self._ai_vs_ai:
                self.message.emit("AI is thinking...")
            QTimer.singleShot(self._ai_delay_ms, self._make_ai_move)

    def _make_ai_move(self):
        from jungle.ai.ai_player import AIPlayer
        if self._ai_vs_ai:
            ai = AIPlayer(depth=3)
        else:
            ai = AIPlayer(depth=3)
        move = ai.choose_move(self._state)
        self._ai_thinking = False
        if move:
            self._execute_move(move[0], move[1])
        else:
            self.message.emit("AI has no legal moves.")

    def get_selected(self) -> tuple[int, int] | None:
        return self._selected

    def get_legal_dests(self) -> set[tuple[int, int]]:
        if self._selected is None or self._state is None:
            return set()
        return set(self._state.legal_moves_for(*self._selected))
