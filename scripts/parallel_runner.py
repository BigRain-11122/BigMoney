"""Parallel batch runner (CEO order O-20260923-2345: mobilize every CPU).

Policy-compliant ProcessPool runner for engine-cell batches. Backwards
COMPATIBLE: import `run_pool` or use the same call shape as serial loops.
Worker cap = floor(cores x 0.8) per BACKTEST_PLAN s6 (bm-a <=25, bm-b <=12;
20% reserved for system/interactive). RAM guard = min(cap, free_GB / 0.5).
Every batch JSON must record audit.workers (O-1810: no audit -> not
ledgered); parallelism speeds NOTHING up in judgment -- prereg / nulls /
ledger discipline unchanged.

Usage (inside a batch script):

    from parallel_runner import run_cells_parallel, worker_cap
    results = run_cells_parallel(jobs)   # jobs = list of dicts; each has
                                         # 'key' + 'fn' -> dict payload

Each job's fn must be a top-level picklable callable returning a plain
dict (no pandas objects across the wire unless small; engine results are
reduced to metrics/equity lists inside fn).
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psutil  # stdlib-adjacent (requirements: rich/pandas ship it via deps)

import config  # noqa: E402


def worker_cap() -> int:
    """floor(cores x 0.8) with RAM guard (BACKTEST_PLAN s6 policy)."""
    cores = os.cpu_count() or 2
    cap = max(1, int(cores * 0.8))
    free_gb = psutil.virtual_memory().available / (1024 ** 3)
    ram_cap = int(free_gb / 0.5)
    return max(1, min(cap, ram_cap))


def run_cells_parallel(jobs, workers=None, desc="cells"):
    """jobs: list of (key, fn) where fn() -> dict. Returns {key: payload}.

    Deterministic output order (keys preserved); worker count recorded for
    the batch audit section.
    """
    n = workers or worker_cap()
    out = {}
    with ProcessPoolExecutor(max_workers=n) as pool:
        futures = {pool.submit(fn): key for key, fn in jobs}
        done = 0
        for fut in futures:
            key = futures[fut]
            out[key] = fut.result()
            done += 1
            if desc and done % 20 == 0:
                print(f"  [pool] {done}/{len(jobs)} {desc}")
    out["__workers__"] = n
    return out
