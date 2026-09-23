"""Backtest Celery task.

Each task runs one parameter combination against the shared price panel.
Result is written to results/<combo_hash>.json and returned as dict.
"""
import json
import os
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS, combo_hash
from engine import run_backtest

try:
    from .celery_app import app
except ImportError:
    app = None


def _load_prices(min_listing_days: int = 60) -> dict:
    """Load price panels from data/daily/*.csv.

    Returns dict[symbol] -> DataFrame with open/close/high/low.
    Filters out symbols listed less than min_listing_days days.
    """
    import pandas as pd
    out = {}
    daily_dir = PATHS.daily_dir
    if not os.path.isdir(daily_dir):
        return out
    for f in os.listdir(daily_dir):
        if not f.endswith(".csv"):
            continue
        sym = f[:-4]
        df = pd.read_csv(os.path.join(daily_dir, f), parse_dates=["date"])
        df = df.set_index("date").sort_index()
        if len(df) < min_listing_days:
            continue
        if "open" not in df.columns:
            df["open"] = df["close"]
        out[sym] = df[["open", "high", "low", "close", "volume"]].copy()
    return out


def run_one(params: dict) -> dict:
    """Execute one backtest. Shared by Celery and local runner."""
    h = combo_hash(params)
    t0 = time.time()
    try:
        prices = _load_prices()
        if not prices:
            return {"hash": h, "status": "no_data", "metrics": {}, "error": ""}
        res = run_backtest(prices, params)
        out = {
            "hash": h,
            "status": "ok",
            "params": {k: (list(v) if isinstance(v, tuple) else v)
                       for k, v in params.items()},
            "metrics": {k: float(v) if hasattr(v, "item") else v
                        for k, v in res["metrics"].items()},
            "n_trades": len(res["trades"]),
            "equity_curve": res["equity_curve"],
            "elapsed_sec": round(time.time() - t0, 2),
        }
        out_path = os.path.join(PATHS.results_dir, f"{h}.json")
        with open(out_path, "w") as f:
            json.dump(out, f, indent=2, default=str)
        return out
    except Exception as e:
        return {"hash": h, "status": "error",
                "error": f"{type(e).__name__}: {e}",
                "trace": traceback.format_exc()}


if app is not None:
    @app.task(name="tasks.backtest_task.run_one")
    def celery_run_one(params: dict):
        return run_one(params)
