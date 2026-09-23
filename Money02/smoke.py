"""End-to-end smoke test on an isolated small universe (no touching real dirs).

Downloads 150 stocks (2022+), builds cache, runs 2 walk-forward folds with a
tiny GA, generates report + signals, and verifies determinism + basic sanity.
All executable logic is inside main() - mandatory for Windows spawn workers.
"""
import os
import shutil
import time
from pathlib import Path

import config as C


def _fresh_root(base: Path) -> Path:
    try:
        if base.exists():
            shutil.rmtree(base)
        return base
    except Exception:
        return base.parent / f"_smoke_{int(time.time())}"


def main():
    root = _fresh_root(Path(__file__).resolve().parent / "_smoke")
    for name in ("bars", "index", "cache", "results"):
        (root / name).mkdir(parents=True, exist_ok=True)
    # main-process overrides + env propagation for spawn workers
    C.BARS_DIR = root / "bars"
    C.IDX_DIR = root / "index"
    C.CACHE_DIR = root / "cache"
    C.RESULTS_DIR = root / "results"
    os.environ["MONEY_CACHE_DIR"] = str(root / "cache")
    C.HIST_START = "20220101"
    C.TRAIN_DAYS = 160
    C.TEST_DAYS = 40
    C.START_OFFSET = 70
    C.POP = 8
    C.GENS_MAX = 2
    C.WF_BUDGET_MIN = 8

    import data as D
    import evolve as EV
    import report as RP
    import backtest as BT

    t0 = time.time()
    spot = D.get_spot()
    codes = list(spot["code"])[:150]
    print(f"smoke universe: {len(codes)} codes (root={root.name})")
    D.update_index()
    for c in codes:
        df = D.fetch_hist(c, C.HIST_START)
        if df is not None and len(df):
            df.to_parquet(D._bar_path(c), index=False)
    meta = D.build_cache()
    assert meta["T"] > 500, f"bad calendar T={meta}"

    res = EV.run_walkforward(tag="smoke", n_folds=2, n_proc=4)
    assert len(res["records"]) == 2
    for r in res["records"]:
        eq = r["eq"]
        assert len(eq) == C.TEST_DAYS
        assert all(v > 0 for v in eq), "equity must stay positive"
        assert all(v == v for v in eq), "equity NaN"
    print("folds ok")

    m = RP.make_report(res)
    assert "sharpe" in m
    sig = RP.write_signals(res["cache"], res["live"], res["regime"], res["out_dir"])
    assert isinstance(sig["buys"], list)
    assert RP.signals_path().exists()

    # determinism: same seed -> same fitness
    import multiprocessing as mp
    with mp.get_context("spawn").Pool(2, initializer=EV._init_worker) as pool:
        _, f1, _, _ = EV.run_ga(pool, 100, 260, pop=6, gens=1, seed=7)
        _, f2, _, _ = EV.run_ga(pool, 100, 260, pop=6, gens=1, seed=7)
    assert abs(f1 - f2) < 1e-9, "GA must be deterministic per seed"
    print(f"SMOKE PASS ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
