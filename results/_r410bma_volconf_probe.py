# -*- coding: utf-8 -*-
"""r410 bm-a VCONF-gate probe (TRIAL_LABOR_W6 prereg draft sec.2 facts).

Deterministic, zero-network, read-only. Facts face, NOT results.
Mirrors _r162bmc_yanggate_probe.py pattern (W5) for the wave-6 volume-confirm axis:
  VCONF gate = signal-day volume(d) vs rolling-20 median of volume (incl d)
    volume_surge: volume(d) >  vol20med(d)   (fang-liang confirm, A-share folk canon)
    volume_dry  : volume(d) <= vol20med(d)   (suo-liang face)
Causality: judged on signal-day d close info-set; entry d+1 open (T+1), grammar layer.
Warmup: first 19 bars vol20med NaN -> gate-closed honest (vs YANG 0-bar / VOL 519-bar).
Member roster face = tl1.load_core() import-reuse (real core48, NOT first-48-alphabetical).
"""
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join("scripts"))
import trial_labor_w1 as tl1  # import-face reuse law (loader T-22/T-34 lineage)

CUTOFF = "2026-09-22"  # P-5C frozen binding, same anchor as W4/W5
OUT = "results/_r410bma_volconf_probe_facts.json"


def vconf_faces(df):
    """volume + rolling-20 median (min_periods=20, incl d); surge=1/dry=0."""
    med = df["volume"].rolling(20, min_periods=20).median()
    surge = (df["volume"] > med).astype("float")  # NaN window stays NaN
    surge[med.isna()] = float("nan")
    return med, surge


def main():
    # ---- 510300 raw full-history face (probe basis, W4/W5 same anchor) ----
    df = pd.read_csv(os.path.join("data", "daily", "sh510300.csv"))
    df["date"] = df["date"].astype(str)
    df = df[df["date"] <= CUTOFF].reset_index(drop=True)
    n = len(df)
    assert n == 3483, f"row count {n} != 3483 (W4/W5 probe anchor)"
    assert df["date"].iloc[-1] == CUTOFF, "last row != cutoff"
    zero_vol = int((df["volume"] <= 0).sum())

    med, surge = vconf_faces(df)
    known = surge.notna()
    first_valid = int(surge.first_valid_index())  # 19 -> 19-bar gate-closed window

    # GATE face (W3 frozen def): close vs MA200
    ma200 = df["close"].rolling(200, min_periods=200).mean()
    gate = (df["close"] > ma200).map({True: "bull", False: "bear"})
    gate_known = gate.notna()
    # VOL face (W4 frozen def): vol20 vs med500
    ret = df["close"] / df["close"].shift(1) - 1
    vol20 = ret.rolling(20, min_periods=20).std(ddof=1)
    med500 = vol20.rolling(500, min_periods=500).median()
    vol = (vol20 <= med500).map({True: "calm", False: "wild"})
    vol_known = vol.notna()
    # YANG face (W5 frozen def): close > open
    yang = (df["close"] > df["open"]).astype(int)

    facts = {
        "panel": "data/daily/sh510300.csv",
        "rows": int(n),
        "first_date": df["date"].iloc[0],
        "cutoff": CUTOFF,
        "zero_volume_rows": zero_vol,
        "warmup_gate_closed_bars": first_valid,  # 19 (vs YANG 0 / VOL 519)
        "surge_total": int(known.sum() - (surge[known] == 0).sum()),
        "surge_days_known": int(known.sum()),
        "surge_rate": round(float(surge[known].mean()), 4),
        "dry_total": int((surge[known] == 0).sum()),
        "vconf_by_gate": {},
        "vconf_by_vol": {},
        "vconf_by_yang": {},
        "cross_gate": {},
        "cross_vol": {},
        "cross_yang": {},
        "four_gate_open_window": {},
    }
    for g in ("bull", "bear"):
        m = gate_known & known & (gate == g)
        facts["vconf_by_gate"][g] = {
            "days": int(m.sum()), "surge": int(surge[m].sum()),
            "rate": round(float(surge[m].mean()), 4) if m.any() else None}
    for v in ("calm", "wild"):
        m = vol_known & known & (vol == v)
        facts["vconf_by_vol"][v] = {
            "days": int(m.sum()), "surge": int(surge[m].sum()),
            "rate": round(float(surge[m].mean()), 4) if m.any() else None}
    for yy in (1, 0):
        m = known & (yang == yy)
        facts["vconf_by_yang"]["yang" if yy else "red"] = {
            "days": int(m.sum()), "surge": int(surge[m].sum()),
            "rate": round(float(surge[m].mean()), 4) if m.any() else None}
    # non-isomorphism cross counts (VCONF x GATE / x VOL / x YANG)
    for g in ("bull", "bear"):
        for s in (1, 0):
            m = gate_known & known & (gate == g) & (surge == s)
            facts["cross_gate"][f"{'surge' if s else 'dry'}_and_{g}"] = int(m.sum())
    for v in ("calm", "wild"):
        for s in (1, 0):
            m = vol_known & known & (vol == v) & (surge == s)
            facts["cross_vol"][f"{'surge' if s else 'dry'}_and_{v}"] = int(m.sum())
    for yy in (1, 0):
        for s in (1, 0):
            m = known & (yang == yy) & (surge == s)
            facts["cross_yang"][f"{'yang' if yy else 'red'}_and_{'surge' if s else 'dry'}"] = int(m.sum())
    # four-gate interaction (open window = gate & vol & vconf known): 16 cells
    mvo = vol_known & gate_known & known
    for g in ("bull", "bear"):
        for v in ("calm", "wild"):
            for yy in (1, 0):
                for s in (1, 0):
                    m = mvo & (gate == g) & (vol == v) & (yang == yy) & (surge == s)
                    key = f"{g}_{v}_{'yang' if yy else 'red'}_{'surge' if s else 'dry'}"
                    facts["four_gate_open_window"][key] = int(m.sum())

    # extreme days (W4/W5 seven) volume status + ratio
    extremes = ["2015-07-27", "2016-01-04", "2024-02-28", "2024-09-24",
                "2024-09-30", "2025-04-07", "2026-01-19"]
    idx = df.set_index("date")
    facts["extreme_days"] = {}
    for d in extremes:
        row = idx.loc[d]
        m = med.iloc[list(idx.index).index(d)]
        facts["extreme_days"][d] = {
            "vconf": ("surge" if row["volume"] > m else "dry"),
            "vol_over_med20": round(float(row["volume"] / m), 3)}

    # ---- core48 member-level spread (real roster via load_core import-reuse) ----
    prices = tl1.load_core()
    cut = pd.Timestamp(CUTOFF)
    rates = {}
    for sym, d2 in sorted(prices.items()):
        d2 = d2[d2.index <= cut]
        if len(d2) >= 60:
            _, s2 = vconf_faces(d2)
            k2 = s2.notna()
            if k2.any():
                rates[str(sym)] = round(float(s2[k2].mean()), 4)
    vals = sorted(rates.values())
    facts["core48_surge_rate"] = {
        "n": len(vals),
        "min": round(vals[0], 4), "median": round(vals[len(vals) // 2], 4),
        "max": round(vals[-1], 4),
        "method": "tl1.load_core() roster (import-reuse, real core48 face)",
        "members_with_lt60_rows_excluded": len(prices) - len(vals)}

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1)
    print(json.dumps(facts, ensure_ascii=False, indent=1))
    print("PROBE OK ->", OUT)


if __name__ == "__main__":
    main()
