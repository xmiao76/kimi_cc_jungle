from typing import Optional
from jungle.model.game_state import GameState
from jungle.model.rules import Rules
from .search import Search

class AIPlayer:
    def __init__(self, depth: int = 3):
        self.search = Search(depth)

    def choose_move(self, state: GameState) -> Optional[tuple]:
        return self.search.best_move(state)
