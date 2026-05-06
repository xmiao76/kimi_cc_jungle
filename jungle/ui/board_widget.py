from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QFont
from PyQt6.QtWidgets import QWidget, QSizePolicy

from jungle.model.board import ROWS, COLS, get_terrain, Terrain
from jungle.model.pieces import Piece, Side
from jungle.model.game_state import GameState
from jungle.model.rules import Rules
from .piece_renderer import PieceRenderer

# Terrain colors
LAND_COLOR = QColor(245, 222, 179)      # Wheat
RIVER_COLOR = QColor(100, 149, 237)     # CornflowerBlue
TRAP_COLOR_BLUE = QColor(173, 216, 230) # LightBlue
TRAP_COLOR_RED = QColor(240, 128, 128)  # LightCoral
DEN_COLOR_BLUE = QColor(70, 130, 180)   # SteelBlue
DEN_COLOR_RED = QColor(205, 92, 92)     # IndianRed
GRID_COLOR = QColor(60, 40, 20)
HIGHLIGHT_MOVE = QColor(50, 205, 50, 180)   # LimeGreen semi-transparent
HIGHLIGHT_SELECT = QColor(255, 215, 0, 150) # Gold semi-transparent

class BoardWidget(QWidget):
    square_clicked = pyqtSignal(int, int)  # row, col

    def __init__(self, parent=None):
        super().__init__(parent)
        self._game_state: GameState | None = None
        self._selected_square: tuple[int, int] | None = None
        self._legal_dests: set[tuple[int, int]] = set()
        self._flipped = False
        self._last_move: tuple[int, int, int, int] | None = None
        self._capture_flash: tuple[int, int] | None = None
        self._flash_timer: QTimer | None = None
        self.setMinimumSize(350, 450)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

    def set_game_state(self, state: GameState):
        self._game_state = state
        self._selected_square = None
        self._legal_dests = set()
        self._last_move = None
        self._capture_flash = None
        if self._flash_timer is not None:
            self._flash_timer.stop()
        self.update()

    def set_selected(self, row: int | None, col: int | None):
        if row is None or col is None:
            self._selected_square = None
            self._legal_dests = set()
        else:
            self._selected_square = (row, col)
            if self._game_state:
                self._legal_dests = set(self._game_state.legal_moves_for(row, col))
            else:
                self._legal_dests = set()
        self.update()

    def set_flipped(self, flipped: bool):
        self._flipped = flipped
        self.update()

    def set_last_move(self, fr: int, fc: int, tr: int, tc: int):
        self._last_move = (fr, fc, tr, tc)
        self.update()

    def set_capture_flash(self, row: int, col: int):
        self._capture_flash = (row, col)
        self.update()
        if self._flash_timer is not None:
            self._flash_timer.stop()
        self._flash_timer = QTimer(self)
        self._flash_timer.setSingleShot(True)
        self._flash_timer.timeout.connect(self._clear_flash)
        self._flash_timer.start(400)

    def _clear_flash(self):
        self._capture_flash = None
        self.update()

    def _to_draw_coords(self, row: int, col: int) -> tuple[int, int]:
        if self._flipped:
            return ROWS - 1 - row, COLS - 1 - col
        return row, col

    def _from_draw_coords(self, drow: int, dcol: int) -> tuple[int, int]:
        if self._flipped:
            return ROWS - 1 - drow, COLS - 1 - dcol
        return drow, dcol

    def _square_rect(self, drow: int, dcol: int, cell_w: float, cell_h: float) -> QRectF:
        x = dcol * cell_w
        y = drow * cell_h
        return QRectF(x, y, cell_w, cell_h)

    def paintEvent(self, event):
        if not self._game_state:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        cell_w = w / COLS
        cell_h = h / ROWS

        # Draw terrain
        for r in range(ROWS):
            for c in range(COLS):
                dr, dc = self._to_draw_coords(r, c)
                rect = self._square_rect(dr, dc, cell_w, cell_h)
                terrain = get_terrain(r, c)
                color = LAND_COLOR
                if terrain is Terrain.RIVER:
                    color = RIVER_COLOR
                elif terrain is Terrain.BLUE_TRAP:
                    color = TRAP_COLOR_BLUE
                elif terrain is Terrain.RED_TRAP:
                    color = TRAP_COLOR_RED
                elif terrain is Terrain.BLUE_DEN:
                    color = DEN_COLOR_BLUE
                elif terrain is Terrain.RED_DEN:
                    color = DEN_COLOR_RED
                painter.fillRect(rect, QBrush(color))

        # Draw terrain icons
        for r in range(ROWS):
            for c in range(COLS):
                dr, dc = self._to_draw_coords(r, c)
                rect = self._square_rect(dr, dc, cell_w, cell_h)
                terrain = get_terrain(r, c)
                cx = rect.x() + rect.width() / 2
                cy = rect.y() + rect.height() / 2
                if terrain is Terrain.RIVER:
                    pen = QPen(QColor(70, 110, 200), 2)
                    painter.setPen(pen)
                    for offset in [-cell_h * 0.12, 0, cell_h * 0.12]:
                        y = cy + offset
                        painter.drawLine(int(cx - cell_w * 0.25), int(y), int(cx + cell_w * 0.25), int(y))
                elif terrain in (Terrain.BLUE_TRAP, Terrain.RED_TRAP):
                    pen = QPen(QColor(100, 100, 100), 2)
                    painter.setPen(pen)
                    margin = min(cell_w, cell_h) * 0.2
                    painter.drawLine(int(rect.x() + margin), int(rect.y() + margin),
                                     int(rect.x() + rect.width() - margin), int(rect.y() + rect.height() - margin))
                    painter.drawLine(int(rect.x() + rect.width() - margin), int(rect.y() + margin),
                                     int(rect.x() + margin), int(rect.y() + rect.height() - margin))
                elif terrain in (Terrain.BLUE_DEN, Terrain.RED_DEN):
                    pen = QPen(QColor(255, 255, 255, 180), 2)
                    painter.setPen(pen)
                    w_icon = min(cell_w, cell_h) * 0.3
                    h_peak = min(cell_w, cell_h) * 0.2
                    painter.drawLine(int(cx - w_icon), int(cy + h_peak * 0.5), int(cx - w_icon * 0.33), int(cy - h_peak))
                    painter.drawLine(int(cx - w_icon * 0.33), int(cy - h_peak), int(cx + w_icon * 0.33), int(cy - h_peak))
                    painter.drawLine(int(cx + w_icon * 0.33), int(cy - h_peak), int(cx + w_icon), int(cy + h_peak * 0.5))

        # Draw grid lines
        pen = QPen(GRID_COLOR)
        pen.setWidth(2)
        painter.setPen(pen)
        for r in range(ROWS + 1):
            y = r * cell_h
            painter.drawLine(0, int(y), w, int(y))
        for c in range(COLS + 1):
            x = c * cell_w
            painter.drawLine(int(x), 0, int(x), h)

        # Draw highlight for legal moves
        if self._selected_square and self._legal_dests:
            sel_r, sel_c = self._selected_square
            dr, dc = self._to_draw_coords(sel_r, sel_c)
            sel_rect = self._square_rect(dr, dc, cell_w, cell_h)
            painter.fillRect(sel_rect, QBrush(HIGHLIGHT_SELECT))
            for tr, tc in self._legal_dests:
                dr, dc = self._to_draw_coords(tr, tc)
                rect = self._square_rect(dr, dc, cell_w, cell_h)
                painter.fillRect(rect, QBrush(HIGHLIGHT_MOVE))

        # Draw pieces
        for r in range(ROWS):
            for c in range(COLS):
                piece = self._game_state.board[r][c]
                if piece is not None:
                    dr, dc = self._to_draw_coords(r, c)
                    rect = self._square_rect(dr, dc, cell_w, cell_h)
                    is_selected = (self._selected_square == (r, c))
                    PieceRenderer.render(painter, piece, rect, is_selected)

        # Draw last move highlight
        if self._last_move:
            fr, fc, tr, tc = self._last_move
            for r, c in ((fr, fc), (tr, tc)):
                dr, dc = self._to_draw_coords(r, c)
                rect = self._square_rect(dr, dc, cell_w, cell_h)
                pen = QPen(QColor(255, 215, 0, 180), 3)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(pen)
                painter.drawRect(rect.adjusted(2, 2, -2, -2))

        # Draw capture flash
        if self._capture_flash:
            r, c = self._capture_flash
            dr, dc = self._to_draw_coords(r, c)
            rect = self._square_rect(dr, dc, cell_w, cell_h)
            painter.fillRect(rect, QBrush(QColor(255, 100, 0, 120)))

        painter.end()

    def mousePressEvent(self, event):
        if not self._game_state:
            return
        w = self.width()
        h = self.height()
        cell_w = w / COLS
        cell_h = h / ROWS
        x = event.position().x()
        y = event.position().y()
        dcol = int(x // cell_w)
        drow = int(y // cell_h)
        if 0 <= drow < ROWS and 0 <= dcol < COLS:
            row, col = self._from_draw_coords(drow, dcol)
            self.square_clicked.emit(row, col)
