"""Overfitting detector: in-sample vs out-of-sample split.

For each strategy, split the equity curve 70/30. If OOS sharpe drops
more than 30% vs IS, mark overfitting risk HIGH.
"""
import numpy as np
import pandas as pd


def sharpe_of(returns: pd.Series) -> float:
    if len(returns) < 2:
        return 0.0
    sd = returns.std(ddof=1)
    if sd == 0:
        return 0.0
    return returns.mean() / sd * np.sqrt(252)


def detect_equity(equity: list[float], split: float = 0.7) -> dict:
    """equity: list of daily equity values. Returns risk level."""
    if len(equity) < 60:
        return {"risk": "LOW", "is_sharpe": 0, "oos_sharpe": 0,
                "drop_pct": 0}
    n = int(len(equity) * split)
    is_eq = pd.Series(equity[:n]).pct_change().dropna()
    oos_eq = pd.Series(equity[n:]).pct_change().dropna()
    is_sh = sharpe_of(is_eq)
    oos_sh = sharpe_of(oos_eq)
    if is_sh <= 0:
        return {"risk": "LOW", "is_sharpe": is_sh, "oos_sharpe": oos_sh,
                "drop_pct": 0}
    drop = (is_sh - oos_sh) / is_sh
    if drop > 0.30:
        risk = "HIGH"
    elif drop > 0.15:
        risk = "MEDIUM"
    else:
        risk = "LOW"
    return {"risk": risk,
            "is_sharpe": round(is_sh, 3),
            "oos_sharpe": round(oos_sh, 3),
            "drop_pct": round(drop, 3)}
