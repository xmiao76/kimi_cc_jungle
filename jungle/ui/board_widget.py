from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
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
        self.setMinimumSize(350, 450)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

    def set_game_state(self, state: GameState):
        self._game_state = state
        self._selected_square = None
        self._legal_dests = set()
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

        # Draw coordinates (optional, small text)
        coord_font = QFont("Arial", max(8, int(min(cell_w, cell_h) * 0.15)))
        painter.setFont(coord_font)
        painter.setPen(QPen(QColor(0, 0, 0, 100)))
        for r in range(ROWS):
            for c in range(COLS):
                dr, dc = self._to_draw_coords(r, c)
                rect = self._square_rect(dr, dc, cell_w, cell_h)
                painter.drawText(rect.toRect(), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft, f"{r},{c}")

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
