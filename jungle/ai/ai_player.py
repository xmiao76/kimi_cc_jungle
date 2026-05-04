from typing import Optional
from jungle.model.game_state import GameState
from jungle.model.rules import Rules
from .search import Search

class AIPlayer:
    def __init__(self, time_limit_ms: int = 1000, strength_config: dict | None = None):
        if strength_config is None:
            strength_config = {}
        self.search = Search(
            time_limit_ms=time_limit_ms,
            max_depth=strength_config.get("max_depth", 20),
            quiescence_depth=strength_config.get("quiescence_depth", 4),
            use_tt=strength_config.get("use_tt", True),
            use_killers=strength_config.get("use_killers", True),
            eval_noise=strength_config.get("eval_noise", 0),
        )

    def choose_move(self, state: GameState) -> Optional[tuple]:
        return self.search.best_move(state)
