from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QFont
from jungle.model.pieces import Piece, PieceType, Side

# Color scheme
SIDE_BLUE_COLOR = QColor(30, 144, 255)    # DodgerBlue
SIDE_RED_COLOR = QColor(220, 20, 60)      # Crimson
PIECE_BG_BLUE = QColor(70, 180, 255)
PIECE_BG_RED = QColor(255, 80, 100)
OUTLINE_COLOR = QColor(20, 20, 20)
TEXT_COLOR = QColor(255, 255, 255)
SELECTED_OUTLINE = QColor(255, 215, 0)    # Gold

# Animal symbols (UTF characters for simplicity and crisp rendering)
ANIMAL_SYMBOLS = {
    PieceType.RAT: "\U0001F400",
    PieceType.CAT: "\U0001F408",
    PieceType.DOG: "\U0001F415",
    PieceType.WOLF: "\U0001F43A",
    PieceType.LEOPARD: "\U0001F406",
    PieceType.TIGER: "\U0001F405",
    PieceType.LION: "\U0001F981",
    PieceType.ELEPHANT: "\U0001F418",
}

ANIMAL_LABELS = {
    PieceType.RAT: "Rt",
    PieceType.CAT: "Ct",
    PieceType.DOG: "Dg",
    PieceType.WOLF: "Wf",
    PieceType.LEOPARD: "Lp",
    PieceType.TIGER: "Tg",
    PieceType.LION: "Ln",
    PieceType.ELEPHANT: "El",
}

class PieceRenderer:
    @staticmethod
    def render(painter: QPainter, piece: Piece, rect: QRectF, selected: bool = False):
        side_color = SIDE_BLUE_COLOR if piece.side is Side.BLUE else SIDE_RED_COLOR
        bg_color = PIECE_BG_BLUE if piece.side is Side.BLUE else PIECE_BG_RED

        # Draw piece background circle
        margin = rect.width() * 0.08
        circle_rect = rect.adjusted(margin, margin, -margin, -margin)

        # Shadow
        shadow_rect = circle_rect.translated(2, 2)
        painter.setBrush(QBrush(QColor(0, 0, 0, 80)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(shadow_rect)

        # Main circle
        painter.setBrush(QBrush(bg_color))
        outline = QPen(SELECTED_OUTLINE if selected else OUTLINE_COLOR)
        outline.setWidth(3 if selected else 2)
        painter.setPen(outline)
        painter.drawEllipse(circle_rect)

        # Inner gradient ring
        inner_margin = rect.width() * 0.18
        inner_rect = rect.adjusted(inner_margin, inner_margin, -inner_margin, -inner_margin)
        painter.setBrush(QBrush(side_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(inner_rect)

        # Draw animal emoji
        font = QFont("Segoe UI Emoji", int(rect.width() * 0.35))
        painter.setFont(font)
        painter.setPen(QPen(TEXT_COLOR))
        symbol = ANIMAL_SYMBOLS.get(piece.piece_type, "?")
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, symbol)

        # Draw short English abbreviation at bottom right
        label_font = QFont("Arial", int(rect.width() * 0.18))
        label_font.setBold(True)
        painter.setFont(label_font)
        painter.setPen(QPen(TEXT_COLOR))
        label_text = ANIMAL_LABELS.get(piece.piece_type, "?")
        painter.drawText(circle_rect.adjusted(0, 0, -4, -4).toRect(),
                         Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom,
                         label_text)
