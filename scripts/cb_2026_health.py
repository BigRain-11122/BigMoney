#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026 转债市场体检：-7.75%/-16.04% 是市场真的跌，还是数据脏。

分三问：
 1) 2026 年逐券首末收益分布（中位数/分位/跌幅>30% 的只数）
 2) 双低持仓在 2026 是不是被少数违约券拖死（看末价<60 的券）
 3) 转债市场的「消失」方式：多少券以低价终结（违约）vs 高价终结（强赎）
"""
from __future__ import annotations

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cb_dual_low as CB  # noqa: E402


def main() -> int:
    p = CB._load_panel()
    y26 = p[p["date"] >= "2026-01-01"]
    print(f"2026 bars={y26['date'].nunique()} codes={y26['code'].nunique()}")

    g = y26.sort_values("date").groupby("code")
    first = g["close"].first()
    last = g["close"].last()
    r = (last / first - 1).dropna()
    print("\n[1] 2026 逐券首末收益")
    print(f"  只数={len(r)} 中位={r.median()*100:.1f}% 均值={r.mean()*100:.1f}%")
    for q in (0.1, 0.25, 0.5, 0.75, 0.9):
        print(f"  p{int(q*100):>2} = {r.quantile(q)*100:>7.1f}%")
    print(f"  跌超30%的券: {(r < -0.30).sum()} 只（{(r < -0.30).mean()*100:.1f}%）")
    print(f"  跌破 60 元的券: {(y26.groupby('code')['close'].min() < 60).sum()} 只")

    print("\n[2] 各年「消失方式」（全样本最后可得收盘价）")
    tail = p.sort_values("date").groupby("code").tail(1)[["code", "date", "close"]]
    tail = tail.assign(year=pd.to_datetime(tail["date"]).dt.year)
    for yr in sorted(tail["year"].unique()):
        t = tail[tail["year"] == yr]
        if len(t) < 5:
            continue
        low = (t["close"] < 80).sum()
        print(f"  {yr}: 终止 {len(t):>3} 只 | 末价<80（违约/退市）{low:>3} 只 "
              f"| 末价中位 {t['close'].median():.0f}")

    print("\n[3] 双低 20 只持仓在 2026 的最差 6 只（按年内跌幅）")
    sub = y26.copy()
    # 复刻一次调仓的选券：取 2026 第一根 bar
    d0 = sub["date"].min()
    day = sub[sub["date"] == d0]
    pool = CB._eligible(day, 80.0, 200.0, None, 130.0, 1.0)
    pool = pool.assign(score=pool["close"] + pool["conv_premium"].fillna(50.0))
    picks = pool.nsmallest(20, "score")["code"].tolist()
    sel = sub[sub["code"].isin(picks)].sort_values("date").groupby("code")["close"]
    rr = (sel.last() / sel.first() - 1).sort_values()
    for code, v in rr.head(6).items():
        print(f"  {code}: {v*100:>7.1f}%  首价 {sel.first()[code]:.1f} 末价 {sel.last()[code]:.1f}")
    print(f"  这 20 只等权年内 = {rr.mean()*100:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
