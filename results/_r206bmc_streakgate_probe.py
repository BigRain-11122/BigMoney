# -*- coding: utf-8 -*-
"""r206 bm-c STREAK-gate probe (TRIAL_LABOR_W7 prereg draft sec.2 facts).

Deterministic, zero-network, read-only. Facts face, NOT results.
Mirrors _r410bma_volconf_probe.py pattern (W6) for the wave-7 streak axis:
  STREAK gate = close-over-close consecutive same-direction run at signal day d
    up_streak2  : close(d)>close(d-1) AND close(d-1)>close(d-2)   (lian-zhang, A-share folk canon)
    down_streak2: close(d)<close(d-1) AND close(d-1)<close(d-2)   (lian-die, fan-tan kou-juan)
    neither state (flat/alternating) = gate-closed for conditioned faces
Causality: judged on signal-day d close info-set; entry d+1 open (T+1), grammar layer.
Warmup: first 2 bars not judgeable -> first_valid bar-idx == 2 (vs YANG 0 / VCONF 19 / VOL 519).
Member roster face = tl1.load_core() import-reuse (real core48, NOT first-48-alphabetical).
"""
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join("scripts"))
import trial_labor_w1 as tl1  # import-face reuse law (loader T-22/T-34 lineage)

CUTOFF = "2026-09-22"  # P-5C frozen binding, same anchor as W4/W5/W6
OUT = "results/_r206bmc_streakgate_probe_facts.json"

EXTREME_DAYS = ["2015-07-27", "2016-01-04", "2024-02-28", "2024-09-24",
                "2024-09-30", "2025-04-07", "2026-01-19"]


def streak_faces(df):
    """up/down 2-day close-over-close run; -1=neither; NaN only first 2 bars."""
    up1 = df["close"] > df["close"].shift(1)
    up2 = df["close"].shift(1) > df["close"].shift(2)
    dn1 = df["close"] < df["close"].shift(1)
    dn2 = df["close"].shift(1) < df["close"].shift(2)
    state = pd.Series(float("nan"), index=df.index)
    judge = (df["close"].shift(2)).notna()  # bars 0-1 = warmup gate-closed
    state[judge & (up1 & up2).fillna(False)] = 1.0
    state[judge & (dn1 & dn2).fillna(False)] = 0.0
    state[judge & ~((up1 & up2).fillna(False) | (dn1 & dn2).fillna(False))] = -1.0
    return state


def main():
    # ---- 510300 raw full-history face (probe basis, W4/W5/W6 same anchor) ----
    df = pd.read_csv(os.path.join("data", "daily", "sh510300.csv"))
    df["date"] = df["date"].astype(str)
    df = df[df["date"] <= CUTOFF].reset_index(drop=True)
    n = len(df)
    assert n == 3483, f"row count {n} != 3483 (W4/W5/W6 probe anchor)"
    assert df["date"].iloc[-1] == CUTOFF, "last row != cutoff"
    zero_vol = int((df["volume"] <= 0).sum())

    st = streak_faces(df)
    known = st.notna()                     # judgeable (warmup bars 0-1 excluded)
    has_state = st.isin([1.0, 0.0])        # up/down run days (gate open)
    neither = st == -1.0                    # no-streak state = gate-closed face
    warmup = int(st.isna().sum())           # 2 -> 2-bar gate-closed window

    # GATE face (W3 frozen def): close vs MA200
    ma200 = df["close"].rolling(200, min_periods=200).mean()
    gate = (df["close"] > ma200).map({True: "bull", False: "bear"})
    # VOL face (W4 frozen def): vol20 vs med500
    ret = df["close"] / df["close"].shift(1) - 1
    vol20 = ret.rolling(20, min_periods=20).std(ddof=1)
    med500 = vol20.rolling(500, min_periods=500).median()
    vol = (vol20 <= med500).map({True: "calm", False: "wild"})
    # YANG face (W5 frozen def): close > open
    yang = (df["close"] > df["open"]).astype(int)
    # VCONF face (W6 frozen def): volume vs med20 (incl d)
    med20 = df["volume"].rolling(20, min_periods=20).median()
    surge = (df["volume"] > med20).astype("float")
    surge[med20.isna()] = float("nan")

    facts = {
        "probe": "r206 bm-c STREAK gate (TRIAL_LABOR_W7 draft sec.2)",
        "panel": "data/daily/sh510300.csv",
        "rows": int(n),
        "first_date": df["date"].iloc[0],
        "cutoff": CUTOFF,
        "zero_volume_rows": zero_vol,
        "warmup_gate_closed_bars": warmup,  # 2 (vs YANG 0 / VCONF 19 / VOL 519)
        "judgeable_days": int(known.sum()),
        "neither_total": int(neither.sum()),
        "up_streak_total": int((st == 1).sum()),
        "down_streak_total": int((st == 0).sum()),
        "streak_days_known": int(has_state.sum()),
        "up_streak_rate": round(float(st[has_state].mean()), 4),
        "up_open_rate_judgeable": round(float(has_state[known].sum()) / max(int(known.sum()), 1), 4),
        "streak_by_gate": {},
        "streak_by_vol": {},
        "streak_by_yang": {},
        "streak_by_vconf": {},
        "cross_gate": {},
        "cross_vol": {},
        "cross_yang": {},
        "cross_vconf": {},
        "five_gate_open_window": {},
        "extreme_days": {},
    }

    # conditional faces: up-rate within each conditioned state of the other four gates
    for label, series, states in (
            ("gate", gate, (("bull", "bull"), ("bear", "bear"))),
            ("vol", vol, (("calm", "calm"), ("wild", "wild"))),
            ("yang", yang, ((1, "yang"), (0, "red"))),
            ("vconf", surge, ((1.0, "surge"), (0.0, "dry")))):
        for s, name in states:
            m = has_state & (series == s).fillna(False)
            facts[f"streak_by_{label}"][name] = {
                "up": int((st[m] == 1).sum()), "down": int((st[m] == 0).sum()),
                "up_rate": round(float(st[m].mean()) if m.sum() else -1.0, 4),
            }

    # ---- five-gate open-window cell census (all-nonempty assertion face) ----
    cell = {}
    for i in df.index:
        if not has_state.iloc[i]:
            continue
        g, v, y, c = gate.iloc[i], vol.iloc[i], yang.iloc[i], surge.iloc[i]
        if pd.isna(g) or pd.isna(v) or pd.isna(c):
            continue
        k = f"{g}|{v}|{'yang' if y == 1 else 'red'}|{'surge' if c == 1.0 else 'dry'}|{'up' if st.iloc[i] == 1 else 'down'}"
        cell[k] = cell.get(k, 0) + 1
    facts["five_gate_open_window"] = dict(sorted(cell.items()))
    facts["five_gate_cells_total"] = len(cell)
    facts["five_gate_cells_min"] = min(cell.values()) if cell else 0
    facts["five_gate_cells_max"] = max(cell.values()) if cell else 0

    # ---- extreme-day streak states (7 days, W6 same roster) ----
    dset = df.set_index("date")
    for d in EXTREME_DAYS:
        if d in dset.index:
            i = dset.index.get_loc(d)
            sv = st.iloc[i]
            facts["extreme_days"][d] = {
                "state": ("up" if sv == 1 else ("down" if sv == 0 else
                          ("neither" if sv == -1 else "warmup"))),
                "ret_d": round(float(ret.iloc[i]), 4),
                "volx_med20": round(float(df['volume'].iloc[i] / med20.iloc[i]), 3)
                if pd.notna(med20.iloc[i]) else None,
            }

    # ---- core48 member-level streak rates (real roster via load_core import) ----
    members = tl1.load_core()
    rates = {}
    for sym in members:
        f = os.path.join("data", "daily", f"{sym}.csv")
        if not os.path.exists(f):
            continue
        m = pd.read_csv(f)
        m["date"] = m["date"].astype(str)
        m = m[m["date"] <= CUTOFF].reset_index(drop=True)
        s = streak_faces(m)
        kk = s.isin([1.0, 0.0])
        rates[sym] = round(float(s[kk].mean()), 4) if kk.sum() else None
    vals = [v for v in rates.values() if v is not None]
    facts["core48_members"] = len(rates)
    facts["core48_up_rate_min"] = min(vals)
    facts["core48_up_rate_median"] = sorted(vals)[len(vals) // 2]
    facts["core48_up_rate_max"] = max(vals)

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in facts.items()
                      if not isinstance(v, dict) or k == "extreme_days"},
                     ensure_ascii=False, indent=1)[:2600])


if __name__ == "__main__":
    main()
