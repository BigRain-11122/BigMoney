# -*- coding: utf-8 -*-
"""Verify ignition detection on dropped expansion proxies (honesty probe)."""
import os
import sys

import pandas as pd

sys.path.insert(0, "scripts")
import theme_ignition_census as tic

for code in ("sh512400", "sh515210", "sh512980", "sz159992", "sh512800"):
    df = pd.read_csv(os.path.join("data/daily", f"{code}.csv"))
    print(code, "cols:", list(df.columns)[:8], "rows:", len(df))
    try:
        igns = tic._detect_ignitions(df)
    except Exception as e:
        print("  DETECT FAIL:", e)
        continue
    dates = [str(df["date"].iloc[i]) for i in igns]
    print("  n_ignitions:", len(igns), "| first 12:", dates[:12])
    # 20td max return within the narrative windows (diagnostic, not verdict)
    close = df["close"]
    r20 = close.pct_change(20)
    for lo, hi, tag in (("2021-01-01", "2021-12-31", "2021"),
                        ("2021-08-01", "2022-06-30", "meta"),
                        ("2025-01-01", "2026-06-30", "2025"),
                        ("2024-01-01", "2026-06-30", "bank")):
        m = (df["date"] >= lo) & (df["date"] <= hi)
        if m.any():
            print(f"  {tag}: max r20 in window = {r20[m].max():.3f}")
