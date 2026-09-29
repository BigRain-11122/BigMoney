# -*- coding: utf-8 -*-
"""r417 bm-b AMP-gate probe (TRIAL_LABOR_W7 prereg draft sec.2 facts).

Deterministic, zero-network, read-only. Facts face, NOT results.
Mirrors _r410bma_volconf_probe.py pattern (W6) for the wave-7 amplitude axis:
  AMP gate = signal-day amplitude(d) vs rolling-20 median of amplitude (incl d)
    amp_wide  : amp(d) >  med20amp(d)   (wide-range spectacle day)
    amp_narrow: amp(d) <= med20amp(d)   (narrow-range quiet day)
  amp(d) = (high - low) / close  -- EXACT registered formula
  engine/factors.py::intraday_range (A-row FACTORS_CENSUS_REGISTRY face,
  zero-invention law); med20 mirror = VCONF face (volume vs its own
  rolling-20 median, W6 frozen def) applied to the amplitude series.
Causality: judged on signal-day d close info-set; entry d+1 open (T+1),
grammar layer.  Warmup: first 19 bars med20amp NaN -> gate-closed honest
(same middle position as VCONF 19-bar; vs YANG 0-bar / VOL 519-bar).
Member roster face = tl1.load_core() import-reuse (real core48, NOT
first-48-alphabetical).
"""
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join("scripts"))
import trial_labor_w1 as tl1  # import-face reuse law (loader T-22/T-34 lineage)

CUTOFF = "2026-09-22"  # P-5C frozen binding, same anchor as W4/W5/W6
OUT = "results/_r417bmb_ampgate_probe_facts.json"


def amp_faces(df):
    """(high-low)/close + rolling-20 median (min_periods=20, incl d);
    wide=1/narrow=0.  Registered formula engine/factors.py::intraday_range."""
    amp = (df["high"] - df["low"]) / df["close"]
    med = amp.rolling(20, min_periods=20).median()
    wide = (amp > med).astype("float")  # NaN window stays NaN
    wide[med.isna()] = float("nan")
    return amp, med, wide


def main():
    # ---- 510300 raw full-history face (probe basis, W4/W5/W6 same anchor) ----
    df = pd.read_csv(os.path.join("data", "daily", "sh510300.csv"))
    df["date"] = df["date"].astype(str)
    df = df[df["date"] <= CUTOFF].reset_index(drop=True)
    n = len(df)
    assert n == 3483, f"row count {n} != 3483 (W4/W5/W6 probe anchor)"
    assert df["date"].iloc[-1] == CUTOFF, "last row != cutoff"
    zero_amp = int((df["high"] == df["low"]).sum())  # flat-line day (halt face)

    amp, med, wide = amp_faces(df)
    known = wide.notna()
    first_valid = int(wide.first_valid_index())  # 19 -> 19-bar gate-closed window

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
    # VCONF face (W6 frozen def): volume vs med20(volume)
    vol_med = df["volume"].rolling(20, min_periods=20).median()
    surge = (df["volume"] > vol_med).astype("float")
    surge[vol_med.isna()] = float("nan")
    vconf_known = surge.notna()

    facts = {
        "panel": "data/daily/sh510300.csv",
        "rows": int(n),
        "first_date": df["date"].iloc[0],
        "cutoff": CUTOFF,
        "zero_range_rows": zero_amp,
        "warmup_gate_closed_bars": first_valid,  # 19 (same as VCONF; YANG 0 / VOL 519)
        "wide_total": int((wide[known] == 1).sum()),
        "wide_days_known": int(known.sum()),
        "wide_rate": round(float(wide[known].mean()), 4),
        "narrow_total": int((wide[known] == 0).sum()),
        "amp_by_gate": {},
        "amp_by_vol": {},
        "amp_by_yang": {},
        "amp_by_vconf": {},
        "cross_gate": {},
        "cross_vol": {},
        "cross_yang": {},
        "cross_vconf": {},
        "five_gate_open_window": {},
    }
    for g in ("bull", "bear"):
        m = gate_known & known & (gate == g)
        facts["amp_by_gate"][g] = {
            "days": int(m.sum()), "wide": int(wide[m].sum()),
            "rate": round(float(wide[m].mean()), 4) if m.any() else None}
    for v in ("calm", "wild"):
        m = vol_known & known & (vol == v)
        facts["amp_by_vol"][v] = {
            "days": int(m.sum()), "wide": int(wide[m].sum()),
            "rate": round(float(wide[m].mean()), 4) if m.any() else None}
    for yy in (1, 0):
        m = known & (yang == yy)
        facts["amp_by_yang"]["yang" if yy else "red"] = {
            "days": int(m.sum()), "wide": int(wide[m].sum()),
            "rate": round(float(wide[m].mean()), 4) if m.any() else None}
    for s in (1, 0):
        m = vconf_known & known & (surge == s)
        facts["amp_by_vconf"]["surge" if s else "dry"] = {
            "days": int(m.sum()), "wide": int(wide[m].sum()),
            "rate": round(float(wide[m].mean()), 4) if m.any() else None}
    # non-isomorphism cross counts (AMP x GATE / x VOL / x YANG / x VCONF)
    for g in ("bull", "bear"):
        for w in (1, 0):
            m = gate_known & known & (gate == g) & (wide == w)
            facts["cross_gate"][f"{'wide' if w else 'narrow'}_and_{g}"] = int(m.sum())
    for v in ("calm", "wild"):
        for w in (1, 0):
            m = vol_known & known & (vol == v) & (wide == w)
            facts["cross_vol"][f"{'wide' if w else 'narrow'}_and_{v}"] = int(m.sum())
    for yy in (1, 0):
        for w in (1, 0):
            m = known & (yang == yy) & (wide == w)
            facts["cross_yang"][f"{'yang' if yy else 'red'}_and_{'wide' if w else 'narrow'}"] = int(m.sum())
    for s in (1, 0):
        for w in (1, 0):
            m = vconf_known & known & (surge == s) & (wide == w)
            facts["cross_vconf"][f"{'surge' if s else 'dry'}_and_{'wide' if w else 'narrow'}"] = int(m.sum())
    # five-gate interaction (open window = all five known): 32 cells
    mvo = vol_known & gate_known & vconf_known & known
    for g in ("bull", "bear"):
        for v in ("calm", "wild"):
            for yy in (1, 0):
                for s in (1, 0):
                    for w in (1, 0):
                        m = (mvo & (gate == g) & (vol == v) & (yang == yy)
                             & (surge == s) & (wide == w))
                        key = (f"{g}_{v}_{'yang' if yy else 'red'}_"
                               f"{'surge' if s else 'dry'}_"
                               f"{'wide' if w else 'narrow'}")
                        facts["five_gate_open_window"][key] = int(m.sum())

    # extreme days (W4/W5/W6 seven) amplitude status + ratio
    extremes = ["2015-07-27", "2016-01-04", "2024-02-28", "2024-09-24",
                "2024-09-30", "2025-04-07", "2026-01-19"]
    idx = df.set_index("date")
    facts["extreme_days"] = {}
    for d in extremes:
        row = idx.loc[d]
        i = list(idx.index).index(d)
        m = med.iloc[i]
        facts["extreme_days"][d] = {
            "amp": ("wide" if row["high"] - row["low"] > 0 and (row["high"] - row["low"]) / row["close"] > m else "narrow"),
            "amp_over_med20": round(float(((row["high"] - row["low"]) / row["close"]) / m), 3)}

    # ---- core48 member-level spread (real roster via load_core import-reuse) ----
    prices = tl1.load_core()
    cut = pd.Timestamp(CUTOFF)
    rates = {}
    for sym, d2 in sorted(prices.items()):
        d2 = d2[d2.index <= cut]
        if len(d2) >= 60:
            _, _, w2 = amp_faces(d2)
            k2 = w2.notna()
            if k2.any():
                rates[str(sym)] = round(float(w2[k2].mean()), 4)
    vals = sorted(rates.values())
    facts["core48_wide_rate"] = {
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
