from typing import Optional
from jungle.model.game_state import GameState
from jungle.model.rules import Rules
from .search import Search

class AIPlayer:
    def __init__(self, time_limit_ms: int = 1000):
        self.search = Search(time_limit_ms)

    def choose_move(self, state: GameState) -> Optional[tuple]:
        return self.search.best_move(state)
