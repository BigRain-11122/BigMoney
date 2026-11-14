#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""双低线分段体检：这条线是「死了」还是「有 regime」。

只做一件事：把同一套规则切到不同时间段，看它相对「全池等权」是加还是减。
判据（先写死，后看数）：
  * 若最近两段（2024 起）选券跑不赢等权，则整线判负、不投产；
  * 若只是某一年吃亏、其余段稳定加，则保留并标注为高风险 regime 依赖。
"""
from __future__ import annotations

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cb_dual_low as CB  # noqa: E402

SEGMENTS = [
    ("2018-2021", "2018-01-01", "2022-01-01"),
    ("2022-2023", "2022-01-01", "2024-01-01"),
    ("2024", "2024-01-01", "2025-01-01"),
    ("2025", "2025-01-01", "2026-01-01"),
    ("2026-ytd", "2026-01-01", "2026-12-31"),
    ("全期(2018起)", "2018-01-01", "2026-12-31"),
]


def main() -> int:
    panel = CB._load_panel()
    print(f"panel {panel['date'].min().date()} -> {panel['date'].max().date()} "
          f"codes={panel['code'].nunique()}")
    print(f"{'段':<14}{'选券年化':>10}{'选券夏普':>10}{'选券回撤':>10}"
          f"{'等权年化':>10}{'等权夏普':>10}{'超额pp':>9}{'池子均值':>9}")
    rows = []
    for name, a, b in SEGMENTS:
        sub = panel[(panel["date"] >= a) & (panel["date"] < b)]
        if sub.empty or sub["date"].nunique() < 40:
            print(f"{name:<14} 数据不足")
            continue
        m, _, dt = CB._backtest(sub, n_hold=20, rebal=20, cost_bp=10.0)
        bm, _, _ = CB._backtest(sub, bench=True, rebal=20)
        pool = sub.groupby("date")["code"].nunique().mean()
        ex = (m["cagr"] - bm["cagr"]) * 100
        rows.append({"seg": name, "cagr": m["cagr"], "sharpe": m["sharpe"],
                     "maxdd": m["maxdd"], "bench_cagr": bm["cagr"],
                     "bench_sharpe": bm["sharpe"], "excess_pp": ex,
                     "pool_avg": float(pool), "bars": int(sub["date"].nunique())})
        print(f"{name:<14}{m['cagr']*100:>9.2f}%{m['sharpe']:>10.3f}"
              f"{m['maxdd']*100:>9.1f}%{bm['cagr']*100:>9.2f}%{bm['sharpe']:>10.3f}"
              f"{ex:>9.2f}{pool:>9.0f}")

    # 判据执行
    recent = [r for r in rows if r["seg"] in ("2024", "2025", "2026-ytd")]
    wins = [r for r in recent if r["excess_pp"] > 0]
    verdict = ("SELECTION_DEAD_IN_CURRENT_REGIME" if len(wins) <= 1
               else "SELECTION_STILL_ADDS")
    print(f"\n判据：最近 3 段里选券跑赢等权 {len(wins)}/3 段 -> {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
