# -*- coding: utf-8 -*-
"""R261 bm-a: CN-CORE-SATELLITE-P1 pre-freeze probe (prereg s2 frozen
reference file builder). Reads ONLY in-repo corpus (data/daily twins,
prefixed long-history face, zero network). Reuses slice-E loaders
(t73_s2_style_rotation single source, anti-repeat law) for the union
panel + envelope-rule fund-event detector (r239 law family).
Output: results/core_sat_probe.json (prereg s2 cites this file; frozen)."""
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import t73_s2_style_rotation as SRP   # slice-E single source (frozen set)

CORE = "510880"
SAT = ("510050", "510300", "510500", "512100", "159915", "588000", "563300")
ALL_LEGS = (CORE,) + SAT
TIMELINE_FIRST_FLOOR = "2013-01-01"   # probe-cited floor (frozen candidate)
W = 252                                # slice-E alive law window
REBAL_STEP = 63                        # quarterly (law holding horizon h=63)
MIN_AVAIL = 3                          # portfolio-selection minimum (frozen
                                       # design rationale in prereg s3.1:
                                       # argmax selection face, NOT the
                                       # slice-E statistical cross-section;
                                       # event-poison of ONE leg must
                                       # neutralize that leg only, never
                                       # zero the CORE via artifact side
                                       # effect -- r239 family spirit)
OUT = os.path.join(ROOT, "results", "core_sat_probe.json")


def main():
    close, ret = SRP.load_panels()          # union calendar, 9 legs
    events = SRP.fund_events(ret)           # envelope rule (slice-E frozen)
    clean, flagged = SRP.clean_rets(ret, events)

    out = {"probe": "CN-CORE-SATELLITE-P1 s2 pre-freeze (R261 bm-a)",
           "legs": {}, "events_on_my_universe": {},
           "timeline": {}, "availability": {}, "adv": {},
           "phantom_ratios": {}}

    # -- per-leg corpus facts
    for sym in ALL_LEGS:
        df = pd.read_csv(os.path.join(ROOT, "data", "daily",
                                      f"sh{sym}.csv" if sym[0] == "5"
                                      else f"sz{sym}.csv"),
                         parse_dates=["date"]).set_index("date").sort_index()
        out["legs"][sym] = {
            "rows": int(len(df)), "first": str(df.index[0].date()),
            "last": str(df.index[-1].date()),
            "nan_open": int(df["open"].isna().sum()),
            "nan_close": int(df["close"].isna().sum()),
            "nan_volume": int(df["volume"].isna().sum()),
            "last_is_cutoff": bool(str(df.index[-1].date())
                                   == SRP.EVIDENCE_CUTOFF),
        }

    # -- events on my 8-leg universe (slice-E detector, frozen set assert)
    flat = {}
    for sym in ALL_LEGS:
        evs = events.get(sym, [])
        out["events_on_my_universe"][sym] = [
            {"date": e["date"], "ret": e["ret"]} for e in evs]
        for e in evs:
            flat[(sym, e["date"])] = e["ret"]
    my_events = sorted(flat.items())
    # phantom re-denomination ratios (post-segment adjustment factor basis)
    for (sym, d), r in my_events:
        c = close[sym]
        d0 = pd.Timestamp(d)
        i = c.index.get_loc(d0)
        rho = float(c.iloc[i] / c.iloc[i - 1])
        out["phantom_ratios"][f"{sym}@{d}"] = round(rho, 6)

    # -- timeline (union floor 2013-01-01, cutoff lockbox belt+braces)
    idx = close.index
    tl = idx[(idx >= pd.Timestamp(TIMELINE_FIRST_FLOOR))
             & (idx <= pd.Timestamp(SRP.EVIDENCE_CUTOFF))]
    out["timeline"] = {
        "first_floor": TIMELINE_FIRST_FLOOR,
        "T": int(len(tl)), "first": str(tl[0].date()),
        "last": str(tl[-1].date()),
        "cutoff": SRP.EVIDENCE_CUTOFF,
        "legs": len(ALL_LEGS),
        "core": CORE, "satellite": list(SAT),
    }

    # -- clean strict-window 252d trailing return per satellite leg,
    #    computed on the FULL union calendar (slice-E convention: rolling
    #    over full leg history; timeline floor truncates only the SIM
    #    window, never the signal history -- no lookahead either way)
    def sig252(sym):
        r = clean[sym]
        return (1.0 + r).rolling(W, min_periods=W).apply(
            lambda x: float(np.prod(x)), raw=True) - 1.0

    sigs = {s: sig252(s) for s in SAT}
    sigs_tl = {s: sigs[s].reindex(tl) for s in SAT}
    nvalid = pd.DataFrame({s: np.isfinite(sigs_tl[s]) for s in SAT}).sum(axis=1)

    # -- rebalance grid: anchor 62, step 63 (frozen candidate)
    T = len(tl)
    sched = list(range(62, T - 1, REBAL_STEP))
    rows = []
    first_active = None
    cash_spans = []
    for r in sched:
        d = tl[r]
        nv = int(nvalid.iloc[r])
        act = nv >= MIN_AVAIL
        if act and first_active is None:
            first_active = str(d.date())
        rows.append({"r": int(r), "date": str(d.date()),
                     "n_avail": nv, "active": bool(act)})
    # ALL inactive (warmup or <MIN_AVAIL) rebalances after first activation
    if first_active is not None:
        fa = pd.Timestamp(first_active)
        for row in rows:
            if pd.Timestamp(row["date"]) > fa and not row["active"]:
                cash_spans.append(row["date"])
    out["availability"] = {
        "W": W, "min_avail": MIN_AVAIL, "rebal_anchor": 62,
        "rebal_step": REBAL_STEP, "n_rebal_evals": len(sched),
        "first_active_rebal": first_active,
        "post_activation_cash_rebals": cash_spans,
        "evals_head": rows[:6], "evals_around_2015": [
            row for row in rows if "2015" in row["date"]],
        "n_valid_signal_days_by_leg": {
            s: int(np.isfinite(sigs_tl[s]).sum()) for s in SAT},
        "signal_face": "rolling 252 on FULL union calendar (slice-E "
                       "convention), evaluated at timeline rebalance dates",
    }

    # -- ADV20 (raw volume x raw close, CNY, fold-invariant) medians by year
    for sym in ALL_LEGS:
        df = pd.read_csv(os.path.join(ROOT, "data", "daily",
                                      f"sh{sym}.csv" if sym[0] == "5"
                                      else f"sz{sym}.csv"),
                         parse_dates=["date"]).set_index("date").sort_index()
        vc = (df["volume"] * df["close"]).reindex(tl)
        adv = vc.rolling(20).mean()
        yr = {}
        for y in (2013, 2015, 2016, 2020, 2021, 2022, 2024, 2026):
            seg = adv[adv.index.year == y].dropna()
            if len(seg):
                yr[str(y)] = float(round(seg.median(), 0))
        out["adv"][sym] = {"adv20_cny_median_by_year": yr,
                           "full_window_median_cny": float(
                               round(adv.dropna().median(), 0))}

    # -- core zero-event assert (slice-D face)
    out["core_zero_events"] = bool(not events.get(CORE))
    out["sliceE_frozen_event_set_all9"] = {
        f"{s}@{e['date']}": e["ret"] for s, evs in events.items()
        for e in evs}

    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("probe written", OUT)
    print("T =", out["timeline"]["T"], "first_active =",
          out["availability"]["first_active_rebal"])
    print("events:", json.dumps(out["events_on_my_universe"],
                                ensure_ascii=False))
    print("post-activation cash rebals:", cash_spans)
    return 0


if __name__ == "__main__":
    sys.exit(main())
