from enum import Enum, auto
from dataclasses import dataclass

class Side(Enum):
    BLUE = auto()
    RED = auto()

    def opposite(self) -> 'Side':
        return Side.RED if self is Side.BLUE else Side.BLUE

class PieceType(Enum):
    RAT = 1
    CAT = 2
    DOG = 3
    WOLF = 4
    LEOPARD = 5
    TIGER = 6
    LION = 7
    ELEPHANT = 8

    @property
    def rank(self) -> int:
        return self.value

@dataclass(frozen=True)
class Piece:
    piece_type: PieceType
    side: Side

    @property
    def rank(self) -> int:
        return self.piece_type.rank

    def __repr__(self) -> str:
        return f"{self.side.name}_{self.piece_type.name}"

# Pre-create all pieces for convenience
BLUE_RAT = Piece(PieceType.RAT, Side.BLUE)
BLUE_CAT = Piece(PieceType.CAT, Side.BLUE)
BLUE_DOG = Piece(PieceType.DOG, Side.BLUE)
BLUE_WOLF = Piece(PieceType.WOLF, Side.BLUE)
BLUE_LEOPARD = Piece(PieceType.LEOPARD, Side.BLUE)
BLUE_TIGER = Piece(PieceType.TIGER, Side.BLUE)
BLUE_LION = Piece(PieceType.LION, Side.BLUE)
BLUE_ELEPHANT = Piece(PieceType.ELEPHANT, Side.BLUE)

RED_RAT = Piece(PieceType.RAT, Side.RED)
RED_CAT = Piece(PieceType.CAT, Side.RED)
RED_DOG = Piece(PieceType.DOG, Side.RED)
RED_WOLF = Piece(PieceType.WOLF, Side.RED)
RED_LEOPARD = Piece(PieceType.LEOPARD, Side.RED)
RED_TIGER = Piece(PieceType.TIGER, Side.RED)
RED_LION = Piece(PieceType.LION, Side.RED)
RED_ELEPHANT = Piece(PieceType.ELEPHANT, Side.RED)


PIECE_NAME_MAP = {
    'LION': PieceType.LION,
    'TIGER': PieceType.TIGER,
    'LEOPARD': PieceType.LEOPARD,
    'WOLF': PieceType.WOLF,
    'DOG': PieceType.DOG,
    'CAT': PieceType.CAT,
    'RAT': PieceType.RAT,
    'ELEPHANT': PieceType.ELEPHANT,
}
