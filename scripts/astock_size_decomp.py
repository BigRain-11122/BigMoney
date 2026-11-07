#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""is the equal-weight breadth premium just the small-cap factor in disguise?

WHY THIS FILE EXISTS
--------------------
r1411 priced the width axis of the liquid A-share pool and refused it on a
phase spread, but left one question untouched: equal weighting every liquid
name IS a size bet -- it hands the smallest names the same capital as the
largest.  The pool's +10.11%/yr against 510300's +3.35%/yr could therefore be
(a) a real participation premium, (b) the size factor in costume, or (c) simply
the price of re-weighting away from cap weights.  Those three have completely
different consequences: (a) is investable, (b) means the book is a small-cap
fund the client could buy elsewhere for 15bp, (c) means the premium is a
mechanical re-weighting that ANY cap-agnostic rule earns.

The answer costs no new data: the archive carries `outstanding_share` per bar,
so cap = close x shares at the decision bar is computable for the same names
the r1411 control already holds.

CONSTRUCTION (frozen; changing any line changes the answer)
-----------------------------------------------------------
  panel       data/astock_daily/per/<sym>.csv via zoo93.load_panel(with_shares=True)
              -- single loader, never re-implemented (import)
  eligible    at decision bar t: bb.eligibility (20-bar median amount >= 20M CNY,
              finite close) -- imported from the r1411 control, same rule
  cohorts     bb.cohorts at R = 60 bars, non-overlapping, next-open entry,
              sell R bars later (r = open[t+1+R]/open[t+1] - 1) -- imported
  cap         close[t, member] * shares[t, member]; a member with a non-finite
              or non-positive cap is DROPPED from all cap-weighted arms AND from
              the tercile split, and that dropping is counted, never patched
  arms        EW_ALL  = mean of member returns, equal weight (the r1411 control,
                       re-run here and required to reproduce its reading)
              CW_ALL  = cap-weighted mean over the same members
              SML/MID/LRG = equal weight inside each cap tercile (equal counts,
                       cut on the day's own cap ranking -- no fixed thresholds,
                       so the terciles mean the same thing in every era)
              CW_SML  = cap-weighted inside the small tercile (does size still
                       pay when the small names are held in their own weights?)
  cost        2 x 13.041bp per cohort per arm (bb.COST_PER_SIDE)
  annualise   bb.chained over cohorts (252/60 periods per year)
  phases      decision offsets 0, 5, ..., R-5 (12 readings) on EW_ALL, CW_ALL
              and the three terciles; the spread across phases is the error bar

VERDICT RULE (frozen BEFORE the numbers were seen; re-emitted in the receipt)
  Let P = EW_ALL CAGR - CW_ALL CAGR (the "equal-weight premium") and
      S = SML CAGR - LRG CAGR (the size spread).
    REWEIGHTING_ONLY   iff every one of SML, MID, LRG beats CW_ALL, i.e. the
                       premium is available at every size and re-weighting is
                       what pays
    SIZE_IS_THE_PREMIUM iff S >= 0.60 * |P| and MID, LRG do NOT both beat CW_ALL
    MIXED              otherwise
  No arm here is a candidate: nothing is proposed for registration.  The output
  is an attribution of a control the desk already quotes.

self  python scripts/astock_size_decomp.py selftest   # synthetic, seconds
run   python scripts/astock_size_decomp.py run        # full panel, ~4 min
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import astock_breadth_book as bb          # eligibility/cohorts/chained/cost, one copy
import zoo93_disposition_cgo_probe as z93  # panel loader, one copy

OUT = os.path.join(ROOT, "results", "size_decomp", "astock_size_decomp.json")
COST = bb.COST_PER_SIDE
R = bb.R
PHASE_STEP = 5
TERCILES = 3


def caps_at(panel: dict, t: int, members: np.ndarray) -> np.ndarray:
    """Cap of each member at the decision bar, or NaN where it is unknowable."""
    cl = np.asarray(panel["close"], dtype=np.float64)
    sh = panel.get("shares")
    if sh is None:
        raise ValueError("panel has no shares column: load with with_shares=True")
    sh = np.asarray(sh, dtype=np.float64)
    cap = cl[t, members] * sh[t, members]
    cap = np.where(np.isfinite(cap) & (cap > 0), cap, np.nan)
    return cap


def tercile_bounds(cap: np.ndarray) -> list[tuple[int, int]]:
    """Equal-count splits of the stock-index array sorted by cap (NaN excluded).

    Returns half-open index ranges into the cap-sorted order, so a tercile holds
    the same NUMBER of names in every era -- fixed cap thresholds would empty
    the small bucket as the market grows.
    """
    n = cap.size
    edges = [int(round(k * n / TERCILES)) for k in range(TERCILES + 1)]
    return [(edges[k], edges[k + 1]) for k in range(TERCILES)]


def arm_readings(members: np.ndarray, rs: np.ndarray, cap: np.ndarray) -> dict:
    """Every arm's NET return for one cohort; NaN arms are refused, not filled."""
    ok = np.isfinite(cap) & (cap > 0)
    out = {"n_members": int(members.size), "n_capped": int(ok.sum())}
    out["ew_all"] = float(rs.mean()) - 2.0 * COST
    if ok.sum() < TERCILES * 2:
        for k in ("cw_all", "sml", "mid", "lrg", "cw_sml"):
            out[k] = float("nan")
        return out
    order = np.flatnonzero(ok)
    order = order[np.argsort(cap[order], kind="mergesort")]
    sub_cap = cap[order]
    sub_rs = rs[order]
    w = sub_cap / sub_cap.sum()
    out["cw_all"] = float(np.dot(w, sub_rs)) - 2.0 * COST
    names = ("sml", "mid", "lrg")
    for (lo, hi), nm in zip(tercile_bounds(sub_cap), names):
        if hi <= lo:
            out[nm] = float("nan")
        else:
            out[nm] = float(sub_rs[lo:hi].mean()) - 2.0 * COST
    lo, hi = tercile_bounds(sub_cap)[0]
    if hi > lo:
        w_s = sub_cap[lo:hi] / sub_cap[lo:hi].sum()
        out["cw_sml"] = float(np.dot(w_s, sub_rs[lo:hi])) - 2.0 * COST
    else:
        out["cw_sml"] = float("nan")
    return out


def cohort_arms(panel: dict, r: int = R, offset: int = 0) -> list[dict]:
    cs, _skipped = bb.cohorts(panel, r=r, offset=offset)
    rows = []
    for t, members, rs in cs:
        cap = caps_at(panel, t, members)
        row = arm_readings(members, rs, cap)
        row["date"] = panel["dates"][t]
        rows.append(row)
    return rows


ARMS = ("ew_all", "cw_all", "sml", "mid", "lrg", "cw_sml")


def chain_arms(rows: list[dict]) -> dict:
    out = {}
    for a in ARMS:
        seq = [row[a] for row in rows if np.isfinite(row.get(a, float("nan")))]
        cagr, dd, curve = bb.chained(seq, r=R)
        out[a] = {"cagr": cagr, "maxdd": dd, "cohorts": len(seq),
                  "skipped": len(rows) - len(seq)}
    return out


def verdict_block(chained: dict) -> dict:
    def c(a):
        return chained[a]["cagr"]

    def beat(a):
        """Arm a beats CW_ALL by strictly more than zero, on finite readings."""
        x, y = c(a), c("cw_all")
        return bool(np.isfinite(x) and np.isfinite(y) and x > y)

    fails = []
    P = S = None
    if np.isfinite(c("ew_all")) and np.isfinite(c("cw_all")):
        P = c("ew_all") - c("cw_all")
    if np.isfinite(c("sml")) and np.isfinite(c("lrg")):
        S = c("sml") - c("lrg")
    arms_beat = {a: beat(a) for a in ("sml", "mid", "lrg")}
    if P is None or S is None:
        v = "UNDECISIVE"
        fails.append("ew_all/cw_all or sml/lrg unreadable")
    elif all(arms_beat.values()):
        v = "REWEIGHTING_ONLY"
    elif S >= 0.60 * abs(P):
        v = "SIZE_IS_THE_PREMIUM"
    else:
        v = "MIXED"
    if v == "SIZE_IS_THE_PREMIUM" and arms_beat["mid"] and arms_beat["lrg"]:
        v = "MIXED"
        fails.append("size_spread_passes but every tercile beats cap weights")
    return {
        "verdict": v,
        "equal_weight_premium_pp": None if P is None else round(P * 100.0, 3),
        "size_spread_pp": None if S is None else round(S * 100.0, 3),
        "tercile_beats_cap_weight": arms_beat,
        "failing_conditions": fails,
        "rule": "REWEIGHTING_ONLY iff sml,mid,lrg all beat cw_all; "
                "SIZE_IS_THE_PREMIUM iff sml-lrg >= 0.60*|ew_all-cw_all| "
                "and not both mid,lrg beating cw_all; MIXED otherwise",
        "candidate": False,
        "note": "attribution of a control the desk already quotes; nothing is "
                "proposed for registration",
    }


def phase_readings(panel: dict, r: int = R) -> dict:
    phases = []
    for off in range(0, r, PHASE_STEP):
        rows = cohort_arms(panel, r=r, offset=off)
        ch = chain_arms(rows)
        phases.append({
            "offset": off,
            "cohorts": len(rows),
            **{a: (None if ch[a]["cagr"] is None else round(ch[a]["cagr"] * 100.0, 3))
               for a in ("ew_all", "cw_all", "sml", "mid", "lrg")},
        })
    vals = {}
    for a in ("ew_all", "cw_all", "sml", "mid", "lrg"):
        v = np.array([p[a] for p in phases if p[a] is not None], dtype=np.float64)
        vals[a] = {
            "min": float(v.min()) if v.size else None,
            "max": float(v.max()) if v.size else None,
            "spread": float(v.max() - v.min()) if v.size else None,
        }
    return {"phases": phases, "spread_pp": vals}


def run() -> dict:
    t0 = time.time()
    panel = z93.load_panel(with_shares=True)
    if "shares" not in panel:
        raise SystemExit("panel loader did not return shares")
    rows = cohort_arms(panel)
    chained = chain_arms(rows)
    vb = verdict_block(chained)
    ph = phase_readings(panel)
    cap_missing = int(sum(r["n_members"] - r["n_capped"] for r in rows))
    receipt = {
        "face": "astock_size_decomp",
        "asof": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": panel["dates"][-1] if panel["dates"] else None,
        "construct": {
            "panel": "data/astock_daily/per (qfq, with outstanding_share)",
            "names": len(panel["symbols"]),
            "bars": len(panel["dates"]),
            "first_date": panel["dates"][0], "last_date": panel["dates"][-1],
            "hold_bars": int(R), "cost_per_side": COST,
            "cohort_count": len(rows),
            "cap_missing_name_cohorts": cap_missing,
            "terciles": TERCILES,
        },
        "chained": chained,
        "verdict_block": vb,
        "phases": ph,
        "series": rows,
        "elapsed_sec": round(time.time() - t0, 1),
        "honest": [
            "pool = names liquid enough for a 20M CNY 20-bar median amount; both "
            "the pool and the archive are survivors of listing",
            "cap = close x outstanding_share is a TOTAL-market-cap proxy, not free "
            "float; state holders and cross-holdings are inside it",
            "equal weight is not an investable book at 4,000 names: capacity was "
            "already priced by r1411 (cost is not the wall, calendar phase is)",
            "cohort drawdown is 60-bar granularity, coarser than a daily curve",
        ],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    return receipt


# --------------------------------------------------------------------------- #
def _synth(nT=400, nS=150, seed=11, size_link=0.0):
    """Synthetic panel: optional return/size link so the arms have something to find."""
    rng = np.random.default_rng(seed)
    cap_rank = np.arange(nS, dtype=np.float64) + 1.0                       # 1 = smallest
    shares = np.repeat((cap_rank * 1e8)[None, :], nT, axis=0)
    base = 10.0
    rets = rng.normal(0.0, 0.02, size=(nT, nS))
    if size_link:
        rets = rets + size_link * (1.0 / np.sqrt(cap_rank))[None, :]
    close = base * np.cumprod(1.0 + rets, axis=0)
    op = close * 1.001
    return {"dates": [f"2020-{1 + d // 28:02d}-{1 + d % 28:02d}" for d in range(nT)],
            "symbols": [f"S{i:04d}" for i in range(nS)],
            "open": op, "close": close,
            "amount": np.full((nT, nS), 5e7), "volume": np.zeros((nT, nS)),
            "turn": np.full((nT, nS), 0.01), "shares": shares}


def selftest() -> int:
    fails = []
    if bb.MIN_POOL > 150:
        fails.append("L0 synthetic panel too small for the imported pool floor")
    # L1 arm_readings: a flat tape makes every arm equal to the cost.
    zero = np.zeros(50)
    cap = np.arange(1, 51, dtype=np.float64) * 1e8
    r0 = arm_readings(np.arange(50), zero, cap)
    for a in ARMS:
        if abs(r0[a] + 2.0 * COST) > 1e-12:
            fails.append(f"L1 flat tape arm {a} != -2*cost ({r0[a]})")
    # L2 cap weights sum to one and only capped members enter
    p2 = _synth(size_link=0.0)
    cap2 = caps_at(p2, 10, np.arange(60))
    ok = np.isfinite(cap2)
    w = cap2[ok] / cap2[ok].sum()
    if abs(w.sum() - 1.0) > 1e-12:
        fails.append("L2 cap weights do not sum to 1")
    # L3 terciles: equal counts, monotone caps, disjoint
    order = np.argsort(cap2, kind="mergesort")
    bounds = tercile_bounds(cap2[order])
    sizes = [hi - lo for lo, hi in bounds]
    if max(sizes) - min(sizes) > 1:
        fails.append(f"L3 terciles uneven: {sizes}")
    if not (cap2[order][bounds[0][0]:bounds[0][1]].max()
            <= cap2[order][bounds[1][0]:bounds[1][1]].min()):
        fails.append("L3 caps not monotone across terciles")
    # L4 size link: small names outperforming must lift EW_ALL above CW_ALL
    p3 = _synth(size_link=0.004)
    rows3 = cohort_arms(p3)
    ch3 = chain_arms(rows3)
    if not (ch3["ew_all"]["cagr"] > ch3["cw_all"]["cagr"]):
        fails.append("L4 size-linked tape did not lift EW_ALL above CW_ALL")
    if not (ch3["sml"]["cagr"] > ch3["lrg"]["cagr"]):
        fails.append("L4 small tercile did not beat large on a size-linked tape")
    v = verdict_block(ch3)["verdict"]
    if v not in ("SIZE_IS_THE_PREMIUM", "MIXED", "REWEIGHTING_ONLY"):
        fails.append(f"L4 verdict unreadable: {v}")
    # L5 no size link -> the plain tape should not manufacture a size spread
    ch0 = chain_arms(cohort_arms(_synth(size_link=0.0)))
    spread0 = ch0["sml"]["cagr"] - ch0["lrg"]["cagr"]
    if abs(spread0) > 0.10:
        fails.append(f"L5 flat tape produced a size spread of {spread0:.4f}")
    # L6 chain reproducibility against bb.chained on the same numbers
    seq = [0.01, -0.02, 0.03]
    cagr_a, dd_a, _ = bb.chained(seq)
    curve = np.concatenate(([1.0], np.cumprod(1.0 + np.asarray(seq))))
    yrs = 3 * R / 252.0
    cagr_b = curve[-1] ** (1.0 / yrs) - 1.0
    if abs(cagr_a - cagr_b) > 1e-12:
        fails.append("L6 chained disagrees with its own closed form")
    # L7 NaN cap members are refused, not treated as zero-size (which would be
    #   silently promoted to the largest weight by a naive sort)
    cap_bad = cap2.copy()
    cap_bad[3] = np.nan
    r1 = arm_readings(np.arange(60), np.full(60, 0.01), cap_bad)
    if r1["n_capped"] != 59:
        fails.append(f"L7 NaN cap not refused: n_capped={r1['n_capped']}")
    # L8 receiving a panel without shares must raise, not read zeros
    try:
        caps_at({"close": np.ones((3, 3))}, 0, np.arange(3))
        fails.append("L8 caps_at accepted a panel without shares")
    except ValueError:
        pass
    if fails:
        for f in fails:
            print("FAIL", f)
        return 1
    print("selftest 8/8 OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "selftest"])
    a = ap.parse_args()
    if a.mode == "selftest":
        return selftest()
    r = run()
    ch = r["chained"]
    print("names", r["construct"]["names"], "bars", r["construct"]["bars"],
          "cohorts", r["construct"]["cohort_count"], "elapsed", r["elapsed_sec"])
    for arm in ARMS:
        print(f"  {arm:7s} cagr={ch[arm]['cagr']} maxdd={ch[arm]['maxdd']} "
              f"cohorts={ch[arm]['cohorts']}")
    print("verdict", r["verdict_block"]["verdict"],
          "premium_pp", r["verdict_block"]["equal_weight_premium_pp"],
          "size_spread_pp", r["verdict_block"]["size_spread_pp"])
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())