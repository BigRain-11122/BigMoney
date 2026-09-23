"""Local multi-process runner (fallback when Redis is unavailable).

Splits the 432 combos across N worker processes and writes results.
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import all_combinations
from tasks.backtest_task import run_one


def run_local(n_workers: int = 4) -> list:
    combos = all_combinations()
    print(f"[local] running {len(combos)} combos with {n_workers} workers")
    results = []
    done = 0
    with ProcessPoolExecutor(max_workers=n_workers) as ex:
        futures = {ex.submit(run_one, c): c for c in combos}
        for fut in as_completed(futures):
            r = fut.result()
            results.append(r)
            done += 1
            if done % 20 == 0 or done == len(combos):
                print(f"  progress: {done}/{len(combos)}")
    return results


if __name__ == "__main__":
    run_local()
