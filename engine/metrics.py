"""Performance metrics."""
import numpy as np
import pandas as pd
from math import sqrt


def annual_return(equity: pd.Series, periods_per_year: int = 252) -> float:
    if len(equity) < 2 or equity.iloc[0] <= 0:
        return 0.0
    total = equity.iloc[-1] / equity.iloc[0]
    years = len(equity) / periods_per_year
    return total ** (1 / years) - 1 if years > 0 else 0.0


def sharpe(equity: pd.Series, periods_per_year: int = 252,
           risk_free: float = 0.0) -> float:
    rets = equity.pct_change().dropna()
    if len(rets) < 2:
        return 0.0
    excess = rets - risk_free / periods_per_year
    sd = excess.std(ddof=1)
    if sd == 0:
        return 0.0
    return excess.mean() / sd * sqrt(periods_per_year)


def max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    dd = (equity - peak) / peak
    return float(dd.min())


def win_rate(pnls: list) -> float:
    if not pnls:
        return 0.0
    return sum(1 for p in pnls if p > 0) / len(pnls)


def profit_factor(pnls: list) -> float:
    gains = sum(p for p in pnls if p > 0)
    losses = -sum(p for p in pnls if p < 0)
    if losses == 0:
        return float("inf") if gains > 0 else 0.0
    return gains / losses


def summarize(equity: pd.Series, trades: list) -> dict:
    pnls = [t["pnl"] for t in trades]
    return {
        "annual_return": round(annual_return(equity), 4),
        "sharpe": round(sharpe(equity), 4),
        "max_drawdown": round(max_drawdown(equity), 4),
        "win_rate": round(win_rate(pnls), 4),
        "profit_factor": round(profit_factor(pnls), 4),
        "num_trades": len(trades),
        "avg_hold_days": round(
            float(np.mean([t["hold_days"] for t in trades])) if trades else 0.0, 2),
    }
