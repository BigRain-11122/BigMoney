"""End-to-end backtest demo: loss exits fast, profit runs to 15 days."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters import run_backtest
from config import HoldPeriodConfig


def main():
    # Entry on day 0 at price 100.
    # Scenario 1: stock grinds down 0.5%/day -> stop loss should hit around -8%
    # Scenario 2: stock grinds up 1%/day -> runs until day 15 hard limit
    # Scenario 3: stock oscillates at small loss -> forced out at day 8

    bars = []
    n = 30
    for i in range(n):
        bars.append((
            f"2026-01-{i+1:02d}" if i < 28 else f"2026-02-{i-27:02d}",
            {
                "LOSS_STOP": 100 * (1 - 0.012 * i),   # -1.2%/day -> stop by day 7
                "PROFIT_RUN": 100 * (1 + 0.01 * i),   # +1%/day -> exits day 15
                "LOSS_TIME": 100 * (1 - 0.002 * i),   # tiny loss -> exits day 8
            },
        ))

    entries = []
    d0 = bars[0][0]
    for sym in ("LOSS_STOP", "PROFIT_RUN", "LOSS_TIME"):
        entries.append((d0, sym, 100.0, "demo_strategy"))

    res = run_backtest(entries, bars, cfg=HoldPeriodConfig())

    print(f"{'date':<12}{'symbol':<12}{'reason':<28}{'pnl%':>8}{'hold_days':>10}")
    for t in sorted(res.trades, key=lambda x: (x.date, x.symbol)):
        print(f"{t.date:<12}{t.symbol:<12}{t.reason:<28}{t.pnl_rate*100:>7.2f}%{t.hold_days:>10}")

    print(f"\nOpen positions after {n} bars: {list(res.open_positions.keys())}")


if __name__ == "__main__":
    main()
