from typing import Dict, Any

AIStrength = {
    "BEGINNER": {
        "time_limit_ms": 200,
        "max_depth": 2,
        "quiescence_depth": 0,
        "use_tt": False,
        "use_killers": False,
        "eval_noise": 20,
    },
    "INTERMEDIATE": {
        "time_limit_ms": 800,
        "max_depth": 4,
        "quiescence_depth": 2,
        "use_tt": True,
        "use_killers": True,
        "eval_noise": 5,
    },
    "ADVANCED": {
        "time_limit_ms": 2000,
        "max_depth": 6,
        "quiescence_depth": 4,
        "use_tt": True,
        "use_killers": True,
        "eval_noise": 0,
    },
    "EXPERT": {
        "time_limit_ms": 5000,
        "max_depth": 20,
        "quiescence_depth": 4,
        "use_tt": True,
        "use_killers": True,
        "eval_noise": 0,
    },
}

def get_strength_config(name: str) -> Dict[str, Any]:
    return AIStrength.get(name, AIStrength["INTERMEDIATE"]).copy()
