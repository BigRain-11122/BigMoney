"""Parameter grid: 3 * 3 * 4 * 3 * 2 * 2 = 432 combos."""
import itertools
from dataclasses import dataclass
from typing import List, Dict


GRID = {
    "take_profit_levels": [(0.05, 0.10, 0.20),
                            (0.08, 0.15, 0.30),
                            (0.03, 0.07, 0.15)],
    "trailing_stop_activate": [0.03, 0.05, 0.08],
    "time_decay_period": [10, 20, 30, 40],
    "time_decay_threshold": [0.01, 0.02, 0.03],
    "position_size_pct": [0.05, 0.10],
    "max_positions": [5, 10],
}


def all_combinations() -> List[Dict]:
    keys = list(GRID.keys())
    values = [GRID[k] for k in keys]
    combos = []
    for v in itertools.product(*values):
        d = dict(zip(keys, v))
        # tuple fields must stay tuple for take_profit_levels
        combos.append(d)
    return combos


def combo_hash(params: dict) -> str:
    """Short deterministic hash of a parameter combination."""
    import hashlib, json
    s = json.dumps(params, sort_keys=True, default=str)
    return hashlib.md5(s.encode()).hexdigest()[:8]


if __name__ == "__main__":
    combos = all_combinations()
    print(f"total combos: {len(combos)}")
    print("sample:", combos[0])
    print("hash:", combo_hash(combos[0]))
