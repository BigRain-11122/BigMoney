#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""can the size premium be held with 20 names, or does it need 1,400?

WHY THIS FILE EXISTS
--------------------
r1412 decomposed the equal-weight breadth control and found the premium is the
size ladder: small tercile +14.98%/yr vs large +0.55%/yr, and the size spread
was positive in all 12 calendar phases (min 12.31pp) while the equal-weight
premium was not stable.  That makes the small end the first structure this desk
has that survives the phase test -- but a tercile of a 4,200-name pool is
~1,400 names, which nobody can hold, and the r1412 note left the real question
open: does the premium survive when the book is N names wide?

This is the same question r1408 asked of a decile and r1411 asked of breadth,
priced the same way: hold only what you can actually buy, pay for the trades,
and report how much money the book can take.

CONSTRUCTION (frozen; changing any line changes the answer)
-----------------------------------------------------------
  panel      data/astock_daily/per via z93.load_panel(with_shares=True)
  eligible   bb.eligibility at the decision bar (20-bar median amount >= 20M CNY)
  cohorts    bb.cohorts, R = 60 bars, non-overlapping, next-open entry, hold R
  cap        close[t] * shares[t]; non-finite/non-positive caps are dropped and
             counted, never patched
  arms       bottom-N by cap, equal weight, N in 20/50/100/200/500
             SML_ALL = every name in the bottom cap tercile, equal weight
                       (the r1412 reading, re-run here and required to reproduce)
  cost       2 x bb.COST_PER_SIDE per cohort per arm at x1; x3 = 3x that
  phases     decision offsets 0,5,...,55 -> the calendar error bar
  capacity   sum of the held names' 20-bar median amount x 5% participation =
             CNY that can be entered in one day; median over cohorts

VERDICT RULE (frozen BEFORE the numbers were seen; re-emitted in the receipt)
  A width N in {20, 50, 100} is ADOPTABLE iff
    (a) x1 net CAGR >= 8.0%/yr
    (b) all 12 phases net CAGR > 0
    (c) x3 net CAGR >= 5.0%/yr
    (d) median 5%-participation one-day capacity >= 20,000,000 CNY
  Verdict = ADOPT_AS_CANDIDATE if any width passes all four; CAPACITY_LIMITED
  if a width passes (a)(b)(c) but fails (d); REFUSE_AS_CANDIDATE otherwise.
  Only the narrowest passing width is reported as the candidate.  Nothing is
  registered here: registration is a separate act with its own prereg.

self  python scripts/astock_smallcap_book.py selftest   # synthetic, seconds
run   python scripts/astock_smallcap_book.py run        # full panel, ~2 min
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

OUT = os.path.join(ROOT, "results", "smallcap_book", "astock_smallcap_book.json")
COST = bb.COST_PER_SIDE
R = bb.R
PHASE_STEP = 5
WIDTHS = (20, 50, 100, 200, 500)
TERCILES = 3
X3 = 3.0
PARTICIPATION = 0.05
GATES = {"x1_cagr_min": 0.08, "x3_cagr_min": 0.05, "capacity_min_cny": 20_000_000.0}
LIQ_WINDOW = bb.LIQ_WINDOW


def caps_at(panel: dict, t: int, members: np.ndarray) -> np.ndarray:
    cl = np.asarray(panel["close"], dtype=np.float64)
    sh = panel.get("shares")
    if sh is None:
        raise ValueError("panel has no shares column: load with with_shares=True")
    sh = np.asarray(sh, dtype=np.float64)
    cap = cl[t, members] * sh[t, members]
    return np.where(np.isfinite(cap) & (cap > 0), cap, np.nan)


def amount_at(panel: dict, t: int, members: np.ndarray) -> np.ndarray:
    """Trailing LIQ_WINDOW median amount per member up to and including bar t."""
    am = np.asarray(panel["amount"], dtype=np.float64)
    lo = max(0, t - LIQ_WINDOW + 1)
    win = am[lo:t + 1][:, members]
    with np.errstate(invalid="ignore"):
        med = np.nanmedian(np.where(np.isfinite(win), win, np.nan), axis=0)
    return med


def cap_sorted(members: np.ndarray, cap: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    ok = np.isfinite(cap) & (cap > 0)
    idx = np.flatnonzero(ok)
    idx = idx[np.argsort(cap[idx], kind="mergesort")]   # smallest cap first
    return idx, cap[idx]


def arm_gross(members: np.ndarray, rs: np.ndarray, cap: np.ndarray, t: int,
              panel: dict) -> dict:
    """Gross return + capacity for one cohort, all widths.  NaN, never filled."""
    idx, sub_cap = cap_sorted(members, cap)
    out = {"n_members": int(members.size), "n_capped": int(idx.size)}
    if idx.size < TERCILES * 2:
        for w in WIDTHS:
            out[f"n{w}"] = float("nan")
            out[f"n{w}_cap_cny"] = None
        out["sml_all"] = float("nan")
        return out
    sub_rs = rs[idx]
    sub_amt = amount_at(panel, t, members[idx])
    lo, hi = 0, int(round(idx.size / TERCILES))
    out["sml_all"] = float(sub_rs[lo:hi].mean())
    for w in WIDTHS:
        k = min(w, idx.size)
        out[f"n{w}"] = float(sub_rs[:k].mean())
        a = sub_amt[:k]
        a = a[np.isfinite(a)]
        out[f"n{w}_cap_cny"] = float(a.sum() * PARTICIPATION) if a.size else None
    return out


def cohort_rows(panel: dict, r: int = R, offset: int = 0) -> list[dict]:
    cs, _skipped = bb.cohorts(panel, r=r, offset=offset)
    rows = []
    for t, members, rs in cs:
        cap = caps_at(panel, t, members)
        row = arm_gross(members, rs, cap, t, panel)
        row["date"] = panel["dates"][t]
        rows.append(row)
    return rows


def net_chain(rows: list[dict], arm: str, mult: float = 1.0) -> dict:
    """Chain gross cohort returns after 2*COST*mult per cohort."""
    seq = []
    for row in rows:
        g = row.get(arm, float("nan"))
        if g is not None and np.isfinite(g):
            seq.append(g - 2.0 * COST * mult)
    if not seq:
        return {"cagr": None, "maxdd": None, "cohorts": 0}
    cagr, dd, _curve = bb.chained(seq, r=R)
    return {"cagr": cagr, "maxdd": dd, "cohorts": len(seq)}


def capacity_median(rows: list[dict], w: int) -> float | None:
    vals = [row[f"n{w}_cap_cny"] for row in rows
            if row.get(f"n{w}_cap_cny") is not None]
    return float(np.median(vals)) if vals else None


def phase_table(panel: dict) -> dict:
    """Net x1 CAGR per width for each decision offset."""
    out = {}
    for w in WIDTHS:
        out[f"n{w}"] = []
    out["sml_all"] = []
    for off in range(0, R, PHASE_STEP):
        rows = cohort_rows(panel, offset=off)
        for key in list(out):
            ch = net_chain(rows, key)
            out[key].append(None if ch["cagr"] is None
                            else round(ch["cagr"] * 100.0, 3))
    summary = {}
    for key, vals in out.items():
        v = np.array([x for x in vals if x is not None], dtype=np.float64)
        summary[key] = {
            "min": float(v.min()) if v.size else None,
            "max": float(v.max()) if v.size else None,
            "spread": float(v.max() - v.min()) if v.size else None,
            "all_positive": bool(v.size and (v > 0).all()),
        }
    return {"by_offset": out, "summary": summary}


def verdict_block(chained_x1: dict, chained_x3: dict, caps: dict,
                  phases: dict) -> dict:
    widths = {}
    limited_only = False
    passing = []
    for w in WIDTHS:
        key = f"n{w}"
        c1 = chained_x1[key]["cagr"]
        c3 = chained_x3[key]["cagr"]
        cap = caps[key]
        ok = {
            "x1_cagr": bool(c1 is not None and c1 >= GATES["x1_cagr_min"]),
            "phases_all_positive": bool(phases["summary"][key]["all_positive"]),
            "x3_cagr": bool(c3 is not None and c3 >= GATES["x3_cagr_min"]),
            "capacity": bool(cap is not None and cap >= GATES["capacity_min_cny"]),
        }
        widths[key] = {"gates": ok, "passes_all": all(ok.values())}
        if ok["x1_cagr"] and ok["phases_all_positive"] and ok["x3_cagr"]:
            if ok["capacity"]:
                passing.append(w)
            else:
                limited_only = True
    candidate = min(passing) if passing else None
    if candidate is not None:
        v = "ADOPT_AS_CANDIDATE"
    elif limited_only:
        v = "CAPACITY_LIMITED"
    else:
        v = "REFUSE_AS_CANDIDATE"
    # The gate above grades the FLOOR (every phase positive).  The desk's own
    # r1411 rule grades the SPREAD and refused an equal-weight book at 4.03pp.
    # Emit both numbers so the two frozen rules can be seen disagreeing rather
    # than being quietly reconciled after the fact.
    spread = {f"n{w}": phases["summary"][f"n{w}"]["spread"] for w in WIDTHS}
    spread["sml_all"] = phases["summary"]["sml_all"]["spread"]
    flip = []
    for w in WIDTHS:
        key = f"n{w}"
        if widths[key]["gates"]["phases_all_positive"] and (spread[key] or 0.0) > 4.03:
            flip.append(key)
    return {
        "verdict": v,
        "candidate_width": candidate,
        "widths": widths,
        "gates": GATES,
        "phase_spread_pp": spread,
        "conflict_with_r1411_rule": {
            "r1411_rule": "phase spread across the 12 decision offsets must stay "
                          "within the tolerance that refused the equal-weight book "
                          "(4.03pp)",
            "widths_that_pass_this_gate_would_fail_that_one": flip,
            "note": "the two frozen rules grade different things: this gate asks "
                    "whether the WORST offset still pays, r1411 asks whether the "
                    "headline is knowable.  A width in this list has a high floor "
                    "and an unknowable point estimate -- quote the floor.",
        },
        "rule": "ADOPT_AS_CANDIDATE iff some N in {20,50,100} has x1 CAGR >= 8%/yr, "
                "all 12 phases positive, x3 CAGR >= 5%/yr and median 5%-participation "
                "one-day capacity >= 20M CNY; CAPACITY_LIMITED if the first three "
                "hold but capacity does not; REFUSE otherwise",
    }


def by_year(rows: list[dict], arms: list[str]) -> dict:
    """Chained net CAGR inside each calendar year, cohort order preserved.

    A year with a single cohort is one 60-bar holding period, not an annual
    reading; the cohorts count is printed next to every number so it cannot be
    read otherwise.
    """
    out = {}
    for arm in arms:
        per = {}
        for row in rows:
            g = row.get(arm, float("nan"))
            if g is None or not np.isfinite(g):
                continue
            y = str(row["date"])[:4]
            per.setdefault(y, []).append(g - 2.0 * COST)
        out[arm] = {
            y: {"net_pct": round(((np.prod(1.0 + np.array(v)) **
                                   (bb.BARS_PER_YEAR / (R * len(v)))) - 1.0) * 100.0, 3),
                "cohorts": len(v)}
            for y, v in sorted(per.items())
        }
    return out


def run() -> dict:
    t0 = time.time()
    panel = z93.load_panel(with_shares=True)
    if "shares" not in panel:
        raise SystemExit("panel loader did not return shares")
    rows = cohort_rows(panel)
    arms = [f"n{w}" for w in WIDTHS] + ["sml_all"]
    chained_x1 = {a: net_chain(rows, a, 1.0) for a in arms}
    chained_x3 = {a: net_chain(rows, a, X3) for a in arms}
    caps = {f"n{w}": capacity_median(rows, w) for w in WIDTHS}
    ph = phase_table(panel)
    vb = verdict_block(chained_x1, chained_x3, caps, ph)
    cap_missing = int(sum(r["n_members"] - r["n_capped"] for r in rows))
    receipt = {
        "face": "astock_smallcap_book",
        "asof": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": panel["dates"][-1] if panel["dates"] else None,
        "construct": {
            "panel": "data/astock_daily/per (qfq, outstanding_share)",
            "names": len(panel["symbols"]), "bars": len(panel["dates"]),
            "first_date": panel["dates"][0], "last_date": panel["dates"][-1],
            "hold_bars": int(R), "cost_per_side": COST, "x3_mult": X3,
            "cohort_count": len(rows), "widths": list(WIDTHS),
            "participation": PARTICIPATION,
            "cap_missing_name_cohorts": cap_missing,
        },
        "chained_x1": chained_x1,
        "chained_x3": chained_x3,
        "capacity_cny_5pct_1day": caps,
        "phases": ph,
        "by_year": by_year(rows, ["n20", "sml_all"]),
        "verdict_block": vb,
        "series": rows,
        "elapsed_sec": round(time.time() - t0, 1),
        "honest": [
            "bottom-N by cap is a total-market-cap sort, not free float; state "
            "holders sit inside it",
            "the pool and the archive are survivors of listing, so both the "
            "premium and the capacity are measured on names that lived",
            "capacity is one-day entry at 5% of trailing turnover; a 60-bar hold "
            "can spread entry, but exit on a limit-down day is worse than this",
            "cohort drawdown is 60-bar granularity",
        ],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    return receipt


# --------------------------------------------------------------------------- #
def _synth(nT=400, nS=150, seed=7, size_link=0.0, vol=0.02):
    rng = np.random.default_rng(seed)
    sizes = np.arange(1, nS + 1, dtype=np.float64)
    shares = np.repeat((sizes * 1e8)[None, :], nT, axis=0)
    rets = rng.normal(0.0, vol, size=(nT, nS))
    if size_link:
        # smallest names drift up; the bonus is bounded by size_link*2e-3 per bar
        # so 400 bars of compounding stays in a believable range
        bonus = size_link * 2e-3 * (1.0 - (sizes - 0.5) / nS)
        rets = rets + np.repeat(bonus[None, :], nT, axis=0)
    px = 10.0 * np.cumprod(1.0 + rets, axis=0)
    op = px * 1.001
    am = np.full((nT, nS), 5e7)
    return {"symbols": [f"S{i:04d}" for i in range(nS)], "dates": [f"d{i}" for i in range(nT)],
            "open": op, "close": px, "amount": am, "shares": shares}


def selftest() -> int:
    ok = 0
    total = 0

    def chk(cond, label):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print(f"FAIL {label}")

    p = _synth(nT=1600, size_link=0.0, vol=0.008)
    rows = cohort_rows(p)
    ch = net_chain(rows, "n20")
    chk(ch["cohorts"] > 3, "L1 flat panel still produces cohorts")
    # cost must bite: the gross book of a flat panel earns ~nothing, and the
    # net book must sit clearly below it by the cohort cost drag
    gross_seq = [row["n20"] for row in rows if np.isfinite(row["n20"])]
    g_cagr, _dd, _c = bb.chained(gross_seq, r=R)
    chk(-0.04 < g_cagr < 0.05, "L2a flat panel gross earns ~zero")
    chk(ch["cagr"] < g_cagr - 0.005, "L2b net sits below gross by the cost drag")

    p2 = _synth(size_link=0.4)
    rows2 = cohort_rows(p2)
    a20, a500 = net_chain(rows2, "n20"), net_chain(rows2, "n500")
    chk(a20["cagr"] > a500["cagr"], "L3 small names up -> n20 beats n500")

    # bottom-N must really be the smallest caps
    cap = caps_at(p2, 100, np.arange(150))
    idx, sub = cap_sorted(np.arange(150), cap)
    chk(sub[0] <= sub[-1] * 1e-6 + sub[0], "L4 cap sort is ascending")
    chk(idx.size == 150, "L5 no cap dropped on a complete panel")

    # capacity scales with width
    cap20 = capacity_median(rows2, 20)
    cap500 = capacity_median(rows2, 500)
    chk(cap20 is not None and cap500 is not None and cap500 > cap20,
        "L6 wider book carries more money")

    # verdict: gates must be able to refuse a flat panel
    ph = {"summary": {f"n{w}": {"all_positive": False, "min": None, "max": None,
                                "spread": None} for w in WIDTHS}}
    ph["summary"]["sml_all"] = {"all_positive": False, "min": None, "max": None,
                                "spread": None}
    vb = verdict_block({f"n{w}": {"cagr": -0.1} for w in WIDTHS} | {"sml_all": {"cagr": -0.1}},
                       {f"n{w}": {"cagr": -0.3} for w in WIDTHS} | {"sml_all": {"cagr": -0.3}},
                       {f"n{w}": 1e6 for w in WIDTHS}, ph)
    chk(vb["verdict"] == "REFUSE_AS_CANDIDATE", "L7 negative arms refused")
    chk(vb["candidate_width"] is None, "L8 no candidate on a negative book")

    good_ph = {"summary": {f"n{w}": {"all_positive": True, "min": 1.0, "max": 2.0,
                                     "spread": 1.0} for w in WIDTHS}}
    good_ph["summary"]["sml_all"] = good_ph["summary"]["n20"]
    vb2 = verdict_block({f"n{w}": {"cagr": 0.15} for w in WIDTHS} | {"sml_all": {"cagr": 0.15}},
                        {f"n{w}": {"cagr": 0.10} for w in WIDTHS} | {"sml_all": {"cagr": 0.10}},
                        {f"n{w}": 5e7 for w in WIDTHS}, good_ph)
    chk(vb2["verdict"] == "ADOPT_AS_CANDIDATE" and vb2["candidate_width"] == 20,
        "L9 narrowest passing width is the candidate")
    vb3 = verdict_block({f"n{w}": {"cagr": 0.15} for w in WIDTHS} | {"sml_all": {"cagr": 0.15}},
                        {f"n{w}": {"cagr": 0.10} for w in WIDTHS} | {"sml_all": {"cagr": 0.10}},
                        {f"n{w}": 1e6 for w in WIDTHS}, good_ph)
    chk(vb3["verdict"] == "CAPACITY_LIMITED", "L10 capacity gate separates the two")

    print(f"selftest {ok}/{total} PASS")
    return 0 if ok == total else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["run", "selftest"])
    a = ap.parse_args()
    if a.mode == "selftest":
        return selftest()
    r = run()
    vb = r["verdict_block"]
    print(json.dumps({"verdict": vb["verdict"], "candidate_width": vb["candidate_width"],
                      "x1": {k: (None if v["cagr"] is None else round(v["cagr"] * 100, 2))
                             for k, v in r["chained_x1"].items()},
                      "x3": {k: (None if v["cagr"] is None else round(v["cagr"] * 100, 2))
                             for k, v in r["chained_x3"].items()},
                      "capacity_cny": r["capacity_cny_5pct_1day"],
                      "phases": {k: v["min"] for k, v in r["phases"]["summary"].items()},
                      "elapsed_sec": r["elapsed_sec"]}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())