# -*- coding: utf-8 -*-
"""r162 bm-c YANG-gate probe (TRIAL_LABOR_W5 prereg sec.2 frozen facts).

Deterministic, zero-network, read-only. Facts face, NOT results.
Mirrors _r396bma_volgate_probe.py pattern (W4) for the wave-5 entry-confirm axis:
  YANG gate = signal-day close(d) > open(d)  (first-yang confirm, REFINE-BENCH-P1)
Causality: judged on signal-day d close info-set; entry d+1 open (T+1), grammar layer.
"""
import json
import pandas as pd

CUTOFF = "2026-09-22"  # P-5C frozen binding, same anchor as W4

def yang(s):
    return (s["close"] > s["open"]).astype(int)

def main():
    df = pd.read_csv("data/daily/sh510300.csv")
    df["date"] = df["date"].astype(str)
    df = df[df["date"] <= CUTOFF].reset_index(drop=True)
    n = len(df)
    assert n == 3483, f"row count {n} != 3483 (W4 probe anchor)"
    assert df["date"].iloc[-1] == CUTOFF, "last row != cutoff"

    y = yang(df)
    # GATE face (W3 frozen def): close vs MA200, min_periods=200
    ma200 = df["close"].rolling(200, min_periods=200).mean()
    gate = (df["close"] > ma200).map({True: "bull", False: "bear"})
    gate_known = gate.notna()
    # VOL face (W4 frozen def): vol20 vs med500
    ret = df["close"] / df["close"].shift(1) - 1
    vol20 = ret.rolling(20, min_periods=20).std(ddof=1)
    med500 = vol20.rolling(500, min_periods=500).median()
    vol = (vol20 <= med500).map({True: "calm", False: "wild"})
    vol_known = vol.notna()

    facts = {
        "panel": "data/daily/sh510300.csv",
        "rows": int(n),
        "first_date": df["date"].iloc[0],
        "cutoff": CUTOFF,
        "yang_total": int(y.sum()),
        "yang_rate": round(float(y.mean()), 4),
        "yang_nan_window_bars": 0,  # close/open available from bar 0 -> no warmup (vs VOL 519)
        "yang_by_gate": {},
        "yang_by_vol": {},
        "cross_gate": {},
        "cross_vol": {},
        "cross_gate_vol_yang": {},
    }
    # conditional rates
    for g in ("bull", "bear"):
        m = gate_known & (gate == g)
        facts["yang_by_gate"][g] = {"days": int(m.sum()), "yang": int(y[m].sum()),
                                    "rate": round(float(y[m].mean()), 4) if m.any() else None}
    for v in ("calm", "wild"):
        m = vol_known & (vol == v)
        facts["yang_by_vol"][v] = {"days": int(m.sum()), "yang": int(y[m].sum()),
                                   "rate": round(float(y[m].mean()), 4) if m.any() else None}
    # non-isomorphism cross counts (YANG x GATE)
    for g in ("bull", "bear"):
        for yy in (1, 0):
            m = gate_known & (gate == g) & (y == yy)
            facts["cross_gate"][f"{'yang' if yy else 'red'}_and_{g}"] = int(m.sum())
    # non-isomorphism cross counts (YANG x VOL, open-window only)
    for v in ("calm", "wild"):
        for yy in (1, 0):
            m = vol_known & (vol == v) & (y == yy)
            facts["cross_vol"][f"{'yang' if yy else 'red'}_and_{v}"] = int(m.sum())
    # triple face (open-window): gate x vol x yang
    mvo = vol_known & gate_known
    for g in ("bull", "bear"):
        for v in ("calm", "wild"):
            for yy in (1, 0):
                m = mvo & (gate == g) & (vol == v) & (y == yy)
                facts["cross_gate_vol_yang"][f"{g}_{v}_{'yang' if yy else 'red'}"] = int(m.sum())

    # extreme days (W4 seven) yang status
    extremes = ["2015-07-27", "2016-01-04", "2024-02-28", "2024-09-24",
                "2024-09-30", "2025-04-07", "2026-01-19"]
    facts["extreme_days"] = {}
    idx = df.set_index("date")
    for d in extremes:
        row = idx.loc[d]
        facts["extreme_days"][d] = {"yang": int(row["close"] > row["open"])}
    # policy-pulse non-isomorphism exemplars
    for d in ("2024-09-24", "2024-09-30"):
        facts[f"exemplar_{d}"] = {"yang": int(idx.loc[d, "close"] > idx.loc[d, "open"]),
                                  "gate": gate.iloc[list(idx.index).index(d)],
                                  "vol": vol.iloc[list(idx.index).index(d)] if vol.iloc[list(idx.index).index(d)] == vol.iloc[list(idx.index).index(d)] else "NaN"}

    # core48 member-level yang rate spread (brief)
    import glob, os
    rates = {}
    members = []
    for f in sorted(glob.glob("data/daily/*.csv")):
        sym = os.path.basename(f)[2:8]
        members.append(sym)
    c48 = [m for m in members][:48]
    for f in sorted(glob.glob("data/daily/*.csv"))[:48]:
        d2 = pd.read_csv(f)
        d2["date"] = d2["date"].astype(str)
        d2 = d2[d2["date"] <= CUTOFF]
        if len(d2) >= 60:
            r = float((d2["close"] > d2["open"]).mean())
            rates[os.path.basename(f)] = round(r, 4)
    vals = list(rates.values())
    facts["core48_yang_rate"] = {"n": len(vals),
                                 "min": round(min(vals), 4), "median": round(sorted(vals)[len(vals)//2], 4),
                                 "max": round(max(vals), 4)}

    out = "results/_r162bmc_yanggate_probe_facts.json"
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1)
    print(json.dumps(facts, ensure_ascii=False, indent=1))
    print("PROBE OK ->", out)

if __name__ == "__main__":
    main()
