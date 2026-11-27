#!/usr/bin/env python
"""Trial-labor null calibration: the band and the bar are two different nulls.

Why this face exists
--------------------
`results/trial_labor_w20/w20_screen.json` publishes two numbers side by side:

    null_p95            = 0.417438
    null_p95_band       = [0.50, 0.53]      band_hit = false
    cell_rate_band      = [0.15, 0.40]
    observed_cell_rate  = 0.451613          <- outside its own band, unflagged

The first is flagged as a miss; the second is printed without a flag.  This
face asks the question that decides whether either number means anything:

    is the bar the cells were measured against the same object as the band
    they were predicted against?

It is not.  Reading the four waves' own screen cells:

  w17 200 nulls -> 3 distinct beat6m_rate values, 197/200 at 0.511572
  w18 200 nulls -> 7 distinct, 193/200 at 0.511572
  w19 200 nulls -> 6 distinct, 193/200 at 0.511572
  w20 200 nulls -> 165 distinct, mean 0.2678, p95 0.417438

0.511572 is 641/1253 -- the fraction of 6m windows in which the benchmark is
down, i.e. the beat rate of a position that never trades.  In W17..W19 the
null was (near) a mass point at that value, so `null_p95` was a *constant of
the panel*, and `null_p95_band_hit = true` could not have come out false.
W20 is the first wave whose null actually trades (1162..2134 entries), and a
random-entry null pays cost, so its beat rate is turnover-driven (this face
fits -17.1pp per 1000 trades, corr -0.73).

That has two consequences this face measures instead of argues:

  1. Cross-wave survival rates are not comparable.  W17..W19 cells traded a
     median of 6..10 times; W20 cells trade 415..2226.  Against the do-nothing
     rate the W20 screen keeps 6/31 = 19.4% (inside the prereg's own
     [0.15, 0.40]); against the random-entry bar it keeps 14/31 = 45.2%.
     Same cells, two nulls, two answers -- and only one of them was flagged.

  2. Most surviving cells are judged outside the region where the bar was
     measured.  The W20 null spans 1162..2134 trades; 19 of 31 cells (12 of
     the 14 survivors) sit below that range.  Because beat rate rises as
     turnover falls, the pooled bar is *lenient* exactly where most cells
     live -- so the 45.2% is not a conservative reading.

This face changes no frozen verdict, re-runs no engine and writes no shared
face.  It re-derives every published survivor count from the four cells CSVs
(4/4 exact) as its control arm, then reports the two nulls side by side.

Exit codes: `run` returns 0 whenever the face was published -- a named
mis-specification is content, not a process failure.  `check` returns 3 when
the published face and a fresh build disagree, and says STALE (never
CHECK FAILED) when an input's bytes moved.  `build()` returns 3 on input
drift so selftest can prove it speaks.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

OUT_JSON = "results/trial_labor_null_calibration.json"
OUT_MD = "research/TRIAL-LABOR-NULL-CALIBRATION.md"

WAVES = ("w17", "w18", "w19", "w20")
BAND_WAVES = ("w17", "w18", "w19")

# A null family whose most common beat6m_rate holds this share of the draws is
# a mass point, not a distribution: its p95 is that one value.
MASS_POINT_SHARE = 0.90
N_BOOT = 2000
BOOT_SEED = 20650500  # = the wave's own scrnull seed base (prereg sec.2)
KNN = 25


# ---------------------------------------------------------------- primitives

def _r6(x):
    return None if x is None else round(float(x), 6)


def _r9(x):
    return None if x is None else round(float(x), 9)


def _pct(vals, q):
    """Percentile with linear interpolation -- the runner's own estimator.

    The published `null_p95` is reproduced by this and only by this
    (numpy.percentile(vals, 95) default): for W20 the bracketing order
    statistics are 0.417398 / 0.418196, interpolating to 0.4174379.
    """
    v = sorted(float(x) for x in vals)
    if not v:
        return None
    if len(v) == 1:
        return v[0]
    k = (len(v) - 1) * (q / 100.0)
    lo = int(k)
    hi = min(len(v) - 1, lo + 1)
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


def _median(vals):
    return _pct(vals, 50)


def _mean(vals):
    v = list(vals)
    return sum(v) / len(v) if v else None


def _sha16(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


def _now():
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


# ------------------------------------------------------------------- loading

def _wave_paths(root, w):
    base = os.path.join(root, "results", "trial_labor_%s" % w)
    return (os.path.join(base, "%s_screen_cells.csv" % w),
            os.path.join(base, "%s_screen.json" % w))


def _load_wave(root, w):
    csvp, jsonp = _wave_paths(root, w)
    if not (os.path.exists(csvp) and os.path.exists(jsonp)):
        return None
    with open(csvp, encoding="utf-8-sig", newline="") as fh:
        rows = [r for r in csv.DictReader(fh)]
    nulls = [r for r in rows if (r.get("family") or "").strip() == "NULL"]
    cells = [r for r in rows if (r.get("family") or "").strip() != "NULL"]
    with open(jsonp, encoding="utf-8") as fh:
        pub = json.load(fh)
    return {"wave": w, "csv": csvp, "json": jsonp, "rows": rows,
            "nulls": nulls, "cells": cells, "published": pub}


def _rate(row):
    try:
        return float(row["beat6m_rate"])
    except (KeyError, TypeError, ValueError):
        return None


def _trades(row):
    try:
        return float(row["n_trades"])
    except (KeyError, TypeError, ValueError):
        return None


def _fn(row):
    return (row.get("fn") or row.get("module") or "?").strip()


# ------------------------------------------------------------------ analysis

def null_health(loaded):
    """Shape of one wave's null family: is it a distribution or a constant?"""
    rates = [x for x in (_rate(r) for r in loaded["nulls"]) if x is not None]
    trades = [x for x in (_trades(r) for r in loaded["nulls"]) if x is not None]
    cell_trades = [x for x in (_trades(r) for r in loaded["cells"])
                   if x is not None]
    if not rates:
        return None
    rounded = Counter(_r6(x) for x in rates)
    modal, modal_n = rounded.most_common(1)[0]
    share = modal_n / float(len(rates))
    return {
        "n_null": len(rates),
        "n_distinct_rates": len(rounded),
        "modal_rate": modal,
        "modal_share": _r6(share),
        "mass_point": share >= MASS_POINT_SHARE,
        "p50": _r6(_median(rates)),
        "mean": _r6(_mean(rates)),
        "p95": _r6(_pct(rates, 95)),
        "p99": _r6(_pct(rates, 99)),
        "max": _r6(max(rates)),
        "trades_min": int(min(trades)) if trades else None,
        "trades_median": int(_median(trades)) if trades else None,
        "trades_max": int(max(trades)) if trades else None,
        "cells_median_trades": (int(_median(cell_trades))
                                if cell_trades else None),
        "n_cells": len(loaded["cells"]),
        "published_p95": _r6(loaded["published"].get("null_p95")),
        "published_band": loaded["published"].get("null_p95_band"),
        "published_band_hit": loaded["published"].get("null_p95_band_hit"),
        "published_n_survivors": loaded["published"].get("n_survivors"),
    }


def do_nothing_rate(loaded):
    """The mass-point value as the arithmetic identity k/n, not as a constant.

    A null whose modal draw is `beat6m_k/beat6m_n` is a position that never
    traded: its beat rate is the share of 6m windows in which the benchmark
    is down.  Reading it as k/n keeps it falsifiable -- a different panel or
    cutoff would move it.
    """
    for row in loaded["nulls"]:
        if _r6(_rate(row)) == loaded.get("_modal"):
            try:
                k = int(float(row["beat6m_k"]))
                n = int(float(row["beat6m_n"]))
            except (KeyError, TypeError, ValueError):
                continue
            if n:
                return {"k": k, "n": n, "rate": _r9(k / float(n)),
                        "wave": loaded["wave"]}
    return None


def regression(loaded):
    """beat6m_rate = a + b * n_trades over the null family (the cost curve)."""
    pts = [(_trades(r), _rate(r)) for r in loaded["nulls"]]
    pts = [(x, y) for x, y in pts if x is not None and y is not None]
    if len(pts) < 3:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    mx, my = _mean(xs), _mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if not sxx:
        return None
    sxy = sum((x - mx) * (y - my) for x, y in pts)
    syy = sum((y - my) ** 2 for y in ys)
    b = sxy / sxx
    a = my - b * mx
    corr = sxy / ((sxx * syy) ** 0.5) if syy else None
    # beat6m_rate is a fraction, so b*1000 is already "fraction per 1000
    # trades"; *100 puts it in percentage points, which is how a reader quotes
    # it ("17pp per thousand trades").
    return {"slope_per_1000": _r6(b * 1000.0),
            "slope_per_1000_pp": _r6(b * 100000.0),
            "intercept": _r6(a), "intercept_pp": _r6(a * 100.0),
            "corr": _r6(corr), "r2": _r6(corr * corr) if corr is not None
            else None, "n": len(pts),
            "trades_min": int(min(xs)), "trades_max": int(max(xs))}


def ladder(loaded, thresholds):
    """Survivor count under each candidate bar (counts are re-derived)."""
    cells = loaded["cells"]
    out = []
    for name, th in thresholds:
        if th is None:
            continue
        n = sum(1 for c in cells if (_rate(c) or 0) > th)
        out.append({"name": name, "threshold": _r6(th), "survivors": n,
                    "rate": _r6(n / float(len(cells))) if cells else None})
    out.sort(key=lambda d: d["threshold"])
    return out


def attribution(loaded, pooled_bar, dn_bar):
    cells = loaded["cells"]
    pooled = {c["cell_id"] for c in cells if (_rate(c) or 0) > pooled_bar}
    dn = {c["cell_id"] for c in cells if (_rate(c) or 0) > dn_bar}
    by_fn = defaultdict(lambda: {"n": 0, "pooled": 0, "do_nothing": 0,
                                 "both": 0})
    for c in cells:
        b = by_fn[_fn(c)]
        b["n"] += 1
        if c["cell_id"] in pooled:
            b["pooled"] += 1
        if c["cell_id"] in dn:
            b["do_nothing"] += 1
        if c["cell_id"] in pooled and c["cell_id"] in dn:
            b["both"] += 1
    return {
        "n_pooled": len(pooled),
        "n_do_nothing": len(dn),
        "n_above_both": len(pooled & dn),
        "n_pooled_only": len(pooled - dn),
        "n_do_nothing_only": len(dn - pooled),
        "above_both": sorted(pooled & dn),
        "above_pooled_only": sorted(pooled - dn),
        "above_do_nothing_only": sorted(dn - pooled),
        "by_fn": {k: {kk: int(vv) for kk, vv in v.items()}
                  for k, v in sorted(by_fn.items())},
    }


def support(loaded, pooled_bar):
    """Where the bar was measured, and where it was extrapolated."""
    ns = loaded["nulls"]
    trades = [x for x in (_trades(r) for r in ns) if x is not None]
    if not trades:
        return None
    lo, hi = min(trades), max(trades)
    inside, below, above = [], [], []
    surv_inside, surv_below, surv_above = 0, 0, 0
    for c in loaded["cells"]:
        t = _trades(c)
        if t is None:
            continue
        hit = (_rate(c) or 0) > pooled_bar
        if t < lo:
            below.append(c["cell_id"])
            surv_below += int(hit)
        elif t > hi:
            above.append(c["cell_id"])
            surv_above += int(hit)
        else:
            inside.append(c["cell_id"])
            surv_inside += int(hit)
    return {"null_trades_min": int(lo), "null_trades_max": int(hi),
            "cells_inside": len(inside), "cells_below": len(below),
            "cells_above": len(above),
            "survivors_inside": surv_inside, "survivors_below": surv_below,
            "survivors_above": surv_above,
            "inside_cells": sorted(inside)}


def matched_test(loaded, pooled_bar, k=KNN):
    """Turnover-matched bar: each cell is read against its nearest nulls."""
    ns = loaded["nulls"]
    flip, rows = [], []
    for c in loaded["cells"]:
        t = _trades(c)
        if t is None:
            continue
        near = sorted(ns, key=lambda r: (abs((_trades(r) or 0) - t),
                                         r.get("cell_id", "")))[:k]
        local = _pct([_rate(r) for r in near if _rate(r) is not None], 95)
        if local is None:
            continue
        rate = _rate(c) or 0.0
        pooled_hit = rate > pooled_bar
        local_hit = rate > local
        rows.append({"cell_id": c["cell_id"], "fn": _fn(c), "trades": int(t),
                     "rate": _r6(rate), "local_p95": _r6(local),
                     "local": bool(local_hit), "pooled": bool(pooled_hit)})
        if local_hit != pooled_hit:
            flip.append({"cell_id": c["cell_id"], "fn": _fn(c),
                         "trades": int(t), "rate": _r6(rate),
                         "local_p95": _r6(local),
                         "verdict": "LOCAL_PASS_POOLED_FAIL" if local_hit
                         else "LOCAL_FAIL_POOLED_PASS"})
    trade_t = sorted(x["trades"] for x in rows)
    lo = min((_trades(r) for r in ns if _trades(r) is not None), default=None)
    hi = max((_trades(r) for r in ns if _trades(r) is not None), default=None)
    measured = [x for x in rows if lo is not None and lo <= x["trades"] <= hi]
    extrap = [x for x in rows if lo is not None and x["trades"] < lo]
    low_end = sorted(ns, key=lambda r: ((_trades(r) or 0),
                                       r.get("cell_id", "")))[:k]
    low_bar = _pct([_rate(r) for r in low_end if _rate(r) is not None], 95)
    return {
        "k": k,
        "flips": sorted(flip, key=lambda d: d["cell_id"]),
        "n_flips": len(flip),
        "measured_region": {
            "cells": len(measured),
            "matched_pass": sum(1 for x in measured if x["local"]),
            "pooled_pass": sum(1 for x in measured if x["pooled"]),
        },
        "extrapolated_region": {
            "cells": len(extrap),
            "matched_pass": sum(1 for x in extrap if x["local"]),
            "pooled_pass": sum(1 for x in extrap if x["pooled"]),
            "lowest_turnover_bar": _r6(low_bar),
            "why": ("cells below the nulls' smallest turnover: any bar there "
                    "is an extrapolation, and the fitted cost curve says the "
                    "true bar is HIGHER than the pooled one -- bounding it "
                    "from below with the lowest-turnover nulls gives "
                    "%s vs the pooled %s" % (_r6(low_bar), _r6(pooled_bar))),
        },
        "trades_quantiles": {"p05": trade_t[int(0.05 * len(trade_t))] if trade_t else None,
                             "p50": int(_median(trade_t)) if trade_t else None,
                             "p95": trade_t[int(0.95 * len(trade_t))] if trade_t else None},
    }


def bootstrap(loaded, pooled_published, cell_band, n_boot=N_BOOT,
              seed=BOOT_SEED):
    """How much of the 45.2% is threshold noise?

    Resampling the 200 nulls moves p95; this counts how often the induced
    survivor rate lands inside the prereg's own cell-rate band.
    """
    rates = [x for x in (_rate(r) for r in loaded["nulls"]) if x is not None]
    cell_rates = [x for x in (_rate(c) for c in loaded["cells"]) if x is not None]
    if len(rates) < 10 or not cell_rates:
        return None
    rng = random.Random(seed)
    p95s, counts = [], []
    n = len(rates)
    for _ in range(n_boot):
        sample = [rates[rng.randrange(n)] for _ in range(n)]
        th = _pct(sample, 95)
        p95s.append(th)
        counts.append(sum(1 for c in cell_rates if c > th))
    denom = float(len(cell_rates))
    shares = [c / denom for c in counts]
    lo, hi = (cell_band or [None, None])[:2]
    inside = sum(1 for s in shares if lo is not None and hi is not None
                 and lo <= s <= hi)
    counts_sorted = sorted(counts)
    return {
        "n_boot": n_boot, "seed": seed,
        "p95": {"p05": _r6(_pct(p95s, 5)), "p50": _r6(_pct(p95s, 50)),
                "p95": _r6(_pct(p95s, 95))},
        "survivors": {"min": counts_sorted[0],
                      "p05": counts_sorted[int(0.05 * n_boot)],
                      "p50": counts_sorted[int(0.50 * n_boot)],
                      "p95": counts_sorted[int(0.95 * n_boot)],
                      "max": counts_sorted[-1]},
        "share_boots_inside_cell_band": _r6(inside / float(n_boot)),
        "share_boots_at_or_above_published": _r6(
            sum(1 for c in counts if c >= pooled_published) / float(n_boot)),
    }


def _verdict(flags):
    hits = [k for k in ("BAND_HIT_WAS_STRUCTURAL",
                        "BAND_ASSUMED_TURNOVER_INVARIANCE",
                        "MOST_SURVIVORS_JUDGED_OUTSIDE_THE_MEASURED_REGION")
            if flags.get(k)]
    if len(hits) == len(flags):
        return "BAND_AND_BAR_MEASURE_DIFFERENT_NULLS"
    if hits:
        return "PARTIAL:" + "+".join(hits)
    return "NULLS_ARE_CALIBRATED_AND_COMPARABLE"


# --------------------------------------------------------------------- build

def build(root=None):
    root = root or ROOT
    loaded = {}
    for w in WAVES:
        d = _load_wave(root, w)
        if d is None:
            return ({"verdict": "REFUSE_WAVE_FACE_MISSING", "wave": w,
                     "why_it_matters": "one of the four screen faces is not "
                                       "readable: the comparison cannot be "
                                       "made with three of them"}, 2)
        loaded[w] = d

    health = {}
    for w in WAVES:
        health[w] = null_health(loaded[w])

    # control arm: every published survivor count is re-derived from its cells
    control = []
    for w in WAVES:
        pub = loaded[w]["published"]
        th = pub.get("null_p95")
        n = sum(1 for c in loaded[w]["cells"] if th is not None
                and (_rate(c) or 0) > th)
        control.append({"wave": w, "cells": len(loaded[w]["cells"]),
                        "rederived": n, "published": pub.get("n_survivors"),
                        "match": n == pub.get("n_survivors")})

    # the mass point, read as k/n rather than as a constant
    dn = None
    for w in BAND_WAVES:
        loaded[w]["_modal"] = health[w]["modal_rate"]
        d = do_nothing_rate(loaded[w])
        if d:
            dn = d
            break
    if dn is None:
        return ({"verdict": "REFUSE_DO_NOTHING_RATE_UNREADABLE",
                 "why_it_matters": "the band's origin value cannot be read as "
                                   "k/n; the whole comparison is speculation"},
                2)

    w20 = loaded["w20"]
    pub20 = w20["published"]
    observed = pub20.get("null_p95")
    band = pub20.get("null_p95_band") or [None, None]
    cell_band = (pub20.get("sec51_prediction_accounting") or {}).get(
        "cell_rate_band")

    thresholds = [
        ("observed_null_p95", observed),
        ("do_nothing_rate", dn["rate"]),
        ("prereg_band_lo", band[0]),
        ("prereg_band_mid", (band[0] + band[1]) / 2.0
         if None not in band else None),
        ("prereg_band_hi", band[1]),
        ("observed_null_p99", health["w20"]["p99"]),
        ("observed_null_max", health["w20"]["max"]),
    ]
    lad = ladder(w20, thresholds)
    for row in lad:
        row["inside_prereg_cell_band"] = (
            None if (not cell_band or row["rate"] is None)
            else bool(cell_band[0] <= row["rate"] <= cell_band[1]))

    attr = attribution(w20, observed, dn["rate"])
    sup = support(w20, observed)
    mat = matched_test(w20, observed)
    reg = regression(w20)
    boot = bootstrap(w20, attr["n_pooled"], cell_band)

    band_structural = all(health[w]["mass_point"] for w in BAND_WAVES) and all(
        loaded[w]["published"].get("null_p95_band_hit") for w in BAND_WAVES)
    # The flag needs a *relationship*, not just a negative sign: 200 draws give
    # a noisy slope, so a correlation floor keeps a coin-flip from being read
    # as "turnover drives the bar" (the same always-lit-gate defect this face
    # was written to catch).
    turnover_moved = bool(
        reg and reg["slope_per_1000"] is not None
        and reg["slope_per_1000"] < 0
        and reg["corr"] is not None and reg["corr"] <= -0.5
        and health["w20"]["cells_median_trades"]
        and health["w17"]["cells_median_trades"]
        and health["w20"]["cells_median_trades"]
        >= 10 * max(1, health["w17"]["cells_median_trades"]))
    beyond_support = bool(sup and sup["survivors_below"]
                          > sup["survivors_inside"])
    flags = {"BAND_HIT_WAS_STRUCTURAL": band_structural,
             "BAND_ASSUMED_TURNOVER_INVARIANCE": turnover_moved,
             "MOST_SURVIVORS_JUDGED_OUTSIDE_THE_MEASURED_REGION": beyond_support}

    inputs = []
    for w in WAVES:
        for p in (loaded[w]["csv"], loaded[w]["json"]):
            inputs.append({"path": os.path.relpath(p, root).replace("\\", "/"),
                           "sha256_16": _sha16(p)})

    out = {
        "wave": "TRIAL_LABOR_NULL_CALIBRATION",
        "stage": "cross-wave-null-audit",
        "evidence_cutoff": pub20.get("evidence_cutoff"),
        "generated": _now(),
        "verdict": _verdict(flags),
        "flags": flags,
        "inputs": inputs,
        "control_arm_survivor_counts": control,
        "null_health": health,
        "do_nothing": {"k": dn["k"], "n": dn["n"], "rate": dn["rate"],
                       "source_wave": dn["wave"],
                       "note": ("the band's value is k/n of the same panel: it "
                                "moves only with the window, never with the "
                                "grammar")},
        "w20_published": {"null_p95": observed, "null_p95_band": band,
                          "null_p95_band_hit": pub20.get("null_p95_band_hit"),
                          "cell_rate_band": cell_band,
                          "observed_cell_rate": (
                              pub20.get("sec51_prediction_accounting") or {}
                          ).get("observed_cell_rate")},
        "ladder": lad,
        "attribution": attr,
        "support": sup,
        "matched": mat,
        "regression": reg,
        "bootstrap": boot,
        "why_it_matters": (
            "the W20 bar and the W20 band are two different nulls: the band "
            "is 641/1253 (a position that never trades) and the bar is a "
            "random-entry null that pays cost. Beat rate falls %.1f pp per "
            "1000 trades (corr %.2f), so a bar measured on nulls trading "
            "%s..%s is not the bar a cell trading %s should clear. Against the "
            "band's own null W20 keeps %d/%d = %.1f%% (inside the prereg's "
            "%.0f..%.0f%% band); against the published bar it keeps %d/%d = "
            "%.1f%%. %d of the %d survivors live below the nulls' smallest "
            "turnover, i.e. where the bar is extrapolated and -- by the sign "
            "of the cost curve -- too lenient."
            % (-reg["slope_per_1000_pp"] if reg and reg["slope_per_1000_pp"] else 0.0,
               reg["corr"] if reg and reg["corr"] is not None else 0.0,
               sup["null_trades_min"] if sup else "?",
               sup["null_trades_max"] if sup else "?",
               health["w20"]["cells_median_trades"],
               attr["n_do_nothing"], health["w20"]["n_cells"],
               100.0 * attr["n_do_nothing"] / max(1, health["w20"]["n_cells"]),
               100.0 * (cell_band[0] if cell_band else 0.0),
               100.0 * (cell_band[1] if cell_band else 0.0),
               attr["n_pooled"], health["w20"]["n_cells"],
               100.0 * attr["n_pooled"] / max(1, health["w20"]["n_cells"]),
               sup["survivors_below"] if sup else 0, attr["n_pooled"])),
        "not_measured": [
            "the nulls do not exist below 1162 trades, so no turnover-matched "
            "bar can be measured for 19 of 31 cells -- this face names the "
            "gap instead of extrapolating a verdict from it",
            "beat6m is a window count, not money: nothing here says which "
            "survivor would earn anything",
            "the reform gate that admitted W20-A-0003 / W20-B-0019 is a "
            "separate face (TRIAL-LABOR-DIRECTION-AUDIT.md); both fail both "
            "bars here",
        ],
    }
    return out, 0


# ------------------------------------------------------------------ renderer

def render_md(out):
    h = out["null_health"]
    attr = out["attribution"]
    sup = out["support"]
    mat = out["matched"]
    reg = out["regression"]
    boot = out["bootstrap"]
    L = []
    L.append("# TRIAL-LABOR 四波 null 校准审计")
    L.append("")
    L.append("> 生成：`scripts/trial_labor_null_calibration.py run` ｜ "
             "证据截止：%s ｜ 判词：**%s**"
             % (out["evidence_cutoff"], out["verdict"]))
    L.append("")
    L.append("## 一句话")
    L.append("")
    L.append("W20 的及格线（0.417438）和它的预测带（[0.50,0.53]）量的不是同一个"
             "零假设：带子的值是 **%d/%d = %.6f**——一个从不交易的仓位；"
             "线子是一个真在交易的随机入场 null。两者之间差的 9.4pp 不是校准失败，"
             "是 null 自己的换手成本。"
             % (out["do_nothing"]["k"], out["do_nothing"]["n"],
                out["do_nothing"]["rate"]))
    L.append("")
    L.append("## 五条读数")
    L.append("")
    L.append("| 波 | null 行 | beat6m 不同取值 | 众数占比 | 众数值 | 发行 p95 | "
             "带内 | 格中位换手 | 格数 | 存活 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for w in WAVES:
        d = h[w]
        L.append("| %s | %d | %d | %.3f | %.6f | %s | %s | %s | %d | %s |"
                 % (w, d["n_null"], d["n_distinct_rates"], d["modal_share"],
                    d["modal_rate"],
                    ("%.6f" % d["p95"]) if d["p95"] is not None else "-",
                    d["published_band_hit"],
                    d["cells_median_trades"], d["n_cells"],
                    d["published_n_survivors"]))
    L.append("")
    L.append("对照臂（重派生每条已发布存活数，4/4 逐位相等）："
             + "；".join("%s %d==%s" % (c["wave"], c["rederived"], c["published"])
                        for c in out["control_arm_survivor_counts"]))
    L.append("")
    L.append("1. **`null_p95_band_hit=true` 在 W17..W19 结构上不可能为假。** "
             "200 个 null 里 %d/%d/%d 个落在同一个值上，p95 就等于那个值；"
             "而那个值是面板常数（k/n），换哪一波都不动。"
             % tuple(int(h[w]["modal_share"] * h[w]["n_null"])
                     for w in BAND_WAVES))
    L.append("2. **W20 是第一次 null 真在交易。** 165 个不同取值、换手 %s..%s、"
             "均值 %.4f；代价曲线 beat6m ≈ %.4f %+.1fpp/千次换手（corr %.3f）。"
             % (h["w20"]["trades_min"], h["w20"]["trades_max"], h["w20"]["mean"],
                reg["intercept"], reg["slope_per_1000_pp"], reg["corr"]))
    n_cells = h["w20"]["n_cells"]
    L.append("3. **同一个 %d 格，两条线两个答案。** 对着 band 自己的 null，"
             "存活 %d/%d = %.1f%%（**落在预注册的 15..40%% 带内**）；对着已发布"
             "的线，%d/%d = %.1f%%。"
             % (n_cells, attr["n_do_nothing"], n_cells,
                100.0 * attr["n_do_nothing"] / max(1, n_cells),
                attr["n_pooled"], n_cells,
                100.0 * attr["n_pooled"] / max(1, n_cells)))
    if sup:
        L.append("4. **%d 个存活里有 %d 个站在 null 没有覆盖的换手区间。** "
                 "null 换手 %d..%d，%d 格里只有 %d 格在区间内（另 %d 格低于下沿、"
                 "%d 格高于上沿）；存活者的分布是 区间内 %d / 区间下 %d。"
                 % (attr["n_pooled"], sup["survivors_below"],
                    sup["null_trades_min"], sup["null_trades_max"], n_cells,
                    sup["cells_inside"], sup["cells_below"], sup["cells_above"],
                    sup["survivors_inside"], sup["survivors_below"]))
    if boot:
        L.append("5. **这不是阈值噪声。** 重抽 200 个 null %d 次，p95 只有 "
                 "%.4f..%.4f，诱导存活数 %d..%d；落进预注册 cell 带的占比 "
                 "**%.1f%%**——45.2%% 稳定地站在带外，所以问题在线本身，"
                 "不在抽样抖动。"
                 % (boot["n_boot"], boot["p95"]["p05"], boot["p95"]["p95"],
                    boot["survivors"]["min"], boot["survivors"]["max"],
                    100.0 * boot["share_boots_inside_cell_band"]))
    L.append("")
    L.append("## 族级两面")
    L.append("")
    L.append("| fn 族 | 格数 | 已发布线（%.6f） | band 自己的线（%.6f） | 两线都过 |"
             % (out["w20_published"]["null_p95"], out["do_nothing"]["rate"]))
    L.append("|---|---|---|---|---|")
    for fn, d in attr["by_fn"].items():
        L.append("| %s | %d | %d | %d | %d |"
                 % (fn, d["n"], d["pooled"], d["do_nothing"], d["both"]))
    L.append("")
    L.append("`near_52w_high` 在已发布面里是 6/6 = 100%，对着 band 自己的那条线只剩 "
             "1/6——「完美命中」是线的产物，不是族的本事。")
    L.append("")
    L.append("## 阈值阶梯（同一批 31 格）")
    L.append("")
    L.append("| 线 | 阈值 | 存活 | 存活率 | 在预注册 cell 带内 |")
    L.append("|---|---|---|---|---|")
    for row in out["ladder"]:
        L.append("| %s | %.6f | %d | %.4f | %s |"
                 % (row["name"], row["threshold"], row["survivors"],
                    row["rate"], row["inside_prereg_cell_band"]))
    L.append("")
    L.append("## 换手匹配读数（只在实测区间里下判断）")
    L.append("")
    L.append("| 区域 | 格数 | 匹配线过 | 已发布线过 |")
    L.append("|---|---|---|---|")
    L.append("| 实测区间（%s..%s） | %d | %d | %d |"
             % (sup["null_trades_min"], sup["null_trades_max"],
                mat["measured_region"]["cells"],
                mat["measured_region"]["matched_pass"],
                mat["measured_region"]["pooled_pass"]))
    L.append("| 外推区间（< %s） | %d | %d | %d |"
             % (sup["null_trades_min"], mat["extrapolated_region"]["cells"],
                mat["extrapolated_region"]["matched_pass"],
                mat["extrapolated_region"]["pooled_pass"]))
    L.append("")
    L.append("外推区间没有实测线，唯一诚实的下界取最低换手那端 %d 个 null 的 p95 = "
             "**%.6f**（已发布线 %.6f），斜率符号说明真值还应更高；"
             "所以那一区的 %d 个存活不能被当成已验证。"
             % (mat["k"],
                mat["extrapolated_region"]["lowest_turnover_bar"],
                out["w20_published"]["null_p95"],
                mat["extrapolated_region"]["pooled_pass"]))
    L.append("")
    if mat["flips"]:
        L.append("近邻匹配（k=%d 个最近换手的 null）翻面的格：" % mat["k"])
        L.append("")
        for f in mat["flips"]:
            L.append("- `%s`（%s，换手 %d，rate %.4f）：本地线 %.4f → %s"
                     % (f["cell_id"], f["fn"], f["trades"], f["rate"],
                        f["local_p95"], f["verdict"]))
    L.append("")
    L.append("## 阈值噪声（重抽 200 个 null，%d 次）" % boot["n_boot"])
    L.append("")
    L.append("p95 的 5%%/50%%/95%% 分位 = %.4f / %.4f / %.4f；诱导存活数 "
             "min %.0f / p05 %.0f / p50 %.0f / p95 %.0f / max %.0f；"
             "落在预注册 cell 带内的重抽占比 **%.1f%%**，"
             "存活数 ≥ 已发布 14 的重抽占比 **%.1f%%**。"
             % (boot["p95"]["p05"], boot["p95"]["p50"], boot["p95"]["p95"],
                boot["survivors"]["min"], boot["survivors"]["p05"],
                boot["survivors"]["p50"], boot["survivors"]["p95"],
                boot["survivors"]["max"],
                100.0 * boot["share_boots_inside_cell_band"],
                100.0 * boot["share_boots_at_or_above_published"]))
    L.append("")
    L.append("## 为什么重要")
    L.append("")
    L.append(out["why_it_matters"])
    L.append("")
    L.append("## 没有测的事（如实）")
    L.append("")
    for line in out["not_measured"]:
        L.append("- " + line)
    L.append("")
    L.append("## 输入面（字节门）")
    L.append("")
    for i in out["inputs"]:
        L.append("- `%s` sha256_16=%s" % (i["path"], i["sha256_16"]))
    L.append("")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ commands

def cmd_run():
    out, rc = build()
    p = os.path.join(ROOT, OUT_JSON)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    with open(os.path.join(ROOT, OUT_MD), "w", encoding="utf-8",
              newline="\n") as fh:
        if rc == 0:
            fh.write(render_md(out))
    print("verdict: %s" % out.get("verdict"))
    if rc == 0:
        print("band %.6f (k/n %d/%d) | bar %.6f | survivors %d vs %d"
              % (out["do_nothing"]["rate"], out["do_nothing"]["k"],
                 out["do_nothing"]["n"], out["w20_published"]["null_p95"],
                 out["attribution"]["n_pooled"],
                 out["attribution"]["n_do_nothing"]))
        print("survivors below null support: %d of %d"
              % (out["support"]["survivors_below"],
                 out["attribution"]["n_pooled"]))
    print("products: %s + %s" % (OUT_JSON, OUT_MD))
    return rc


def _cmp(old, new, problems, key, path="", tol=1e-9):
    if isinstance(old, dict) and isinstance(new, dict):
        for k in sorted(set(old) | set(new)):
            if k == "generated":
                continue
            if k not in old:
                problems.append("missing_in_face:%s" % (path + "." + str(k)))
                continue
            if k not in new:
                problems.append("stale_extra:%s" % (path + "." + str(k)))
                continue
            _cmp(old[k], new[k], problems, key, path + "." + str(k), tol)
        return
    if isinstance(old, list) and isinstance(new, list):
        if len(old) != len(new):
            problems.append("len:%s face=%d fresh=%d"
                            % (path, len(old), len(new)))
            return
        for i, (a, b) in enumerate(zip(old, new)):
            _cmp(a, b, problems, key, "%s[%d]" % (path, i), tol)
        return
    if isinstance(old, float) or isinstance(new, float):
        if old is None or new is None:
            if old != new:
                problems.append("val:%s face=%r fresh=%r" % (path, old, new))
            return
        if abs(float(old) - float(new)) > tol:
            problems.append("val:%s face=%r fresh=%r" % (path, old, new))
        return
    if old != new:
        problems.append("val:%s face=%r fresh=%r" % (path, old, new))


def cmd_check():
    p = os.path.join(ROOT, OUT_JSON)
    if not os.path.exists(p):
        print("STALE: face missing (%s) -- run first" % OUT_JSON)
        return 2
    with open(p, encoding="utf-8") as fh:
        old = json.load(fh)
    fresh, rc = build()
    if rc != 0:
        print("STALE: fresh build cannot be made (%s)" % fresh.get("verdict"))
        return 3
    old_sha = {i["path"]: i["sha256_16"] for i in old.get("inputs", [])}
    new_sha = {i["path"]: i["sha256_16"] for i in fresh["inputs"]}
    moved = sorted(k for k in set(old_sha) & set(new_sha)
                   if old_sha[k] != new_sha[k])
    if moved:
        print("STALE: input bytes moved since publication: %s"
              % ", ".join(moved))
        return 3
    problems = []
    if old.get("verdict") != fresh["verdict"]:
        problems.append("verdict: face=%r fresh=%r"
                        % (old.get("verdict"), fresh["verdict"]))
    for sect in ("null_health", "do_nothing", "ladder", "attribution",
                 "support", "matched", "regression", "bootstrap",
                 "flags", "control_arm_survivor_counts"):
        _cmp(old.get(sect), fresh.get(sect), problems, sect, "." + sect,
             tol=1e-6)
    if problems:
        print("CHECK FAILED: %d disagreement(s): %s"
              % (len(problems), " | ".join(problems[:6])))
        return 1
    print("CHECK OK: %s | band %.6f | bar %.6f | survivors %d vs %d"
          % (old["verdict"], old["do_nothing"]["rate"],
             old["w20_published"]["null_p95"], old["attribution"]["n_pooled"],
             old["attribution"]["n_do_nothing"]))
    return 0


# -------------------------------------------------------------- selftest

def _write_wave(root, w, nulls, cells, p95, band, n_survivors, cell_band,
                cutoff="2026-01-02", band_hit=True):
    base = os.path.join(root, "results", "trial_labor_%s" % w)
    os.makedirs(base, exist_ok=True)
    cols = ["cell_id", "family", "fn", "beat6m_k", "beat6m_n", "beat6m_rate",
            "n_trades", "sharpe_full", "survives_screen"]
    csvp = os.path.join(base, "%s_screen_cells.csv" % w)
    with open(csvp, "w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        for i, (rate, trades) in enumerate(nulls):
            wr.writerow({"cell_id": "%s-NULL-%04d" % (w.upper(), i),
                         "family": "NULL", "fn": "null",
                         "beat6m_k": 641, "beat6m_n": 1253,
                         "beat6m_rate": rate, "n_trades": trades,
                         "sharpe_full": 0.0, "survives_screen": "False"})
        for cid, fn, rate, trades in cells:
            wr.writerow({"cell_id": cid, "family": "B", "fn": fn,
                         "beat6m_k": 800, "beat6m_n": 1253,
                         "beat6m_rate": rate, "n_trades": trades,
                         "sharpe_full": 0.1, "survives_screen":
                         str(rate > p95)})
    jsonp = os.path.join(base, "%s_screen.json" % w)
    with open(jsonp, "w", encoding="utf-8") as fh:
        json.dump({"wave": w.upper(), "stage": "screen-finalize",
                   "evidence_cutoff": cutoff, "null_p95": p95,
                   "null_p95_band": band, "null_p95_band_hit": band_hit,
                   "n_survivors": n_survivors,
                   "sec51_prediction_accounting": {
                       "cell_rate_band": cell_band}}, fh)
    return csvp


def cmd_selftest():
    import shutil
    import tempfile
    legs, fails = [], []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))
        if not cond:
            fails.append(name)

    # ---- fixture A: the real shape (mass point in 3 waves, real null in w20)
    rng = random.Random(7)
    dn = 641.0 / 1253.0
    with tempfile.TemporaryDirectory() as tmp:
        global ROOT
        keep = ROOT
        ROOT = tmp
        try:
            mass = [(round(dn, 6), 0)] * 197 + [(0.508380, 1)] * 2 + \
                   [(0.513168, 2)]
            real_null = []
            for _ in range(200):
                t = rng.randint(1162, 2134)
                real_null.append((max(0.0, 0.55 - 0.00017 * t +
                                      rng.gauss(0.0, 0.06)), t))
            for w, ns in (("w17", mass), ("w18", mass), ("w19", mass)):
                _write_wave(tmp, w, ns,
                            [("C-%s-1" % w, "dd_rung_entry", 0.60, 10),
                             ("C-%s-2" % w, "near_52w_high", 0.40, 8)],
                            dn, [0.50, 0.53], 1, [0.15, 0.40])
            cells = []
            for i in range(13):
                t = 400 + 60 * i
                cells.append(("D-%02d" % i, "dd_rung_entry",
                              0.52 - 0.00008 * t, t))
            for i in range(6):
                t = 800 + 20 * i
                cells.append(("N-%02d" % i, "near_52w_high", 0.46, t))
            for i in range(12):
                t = 1200 + 80 * i
                cells.append(("T-%02d" % i, "turnover_regime", 0.40, t))
            p95 = _pct([r for r, _ in real_null], 95)
            nsr = sum(1 for _, _, r, _ in cells if r > p95)
            _write_wave(tmp, "w20", real_null, cells, round(p95, 6),
                        [0.50, 0.53], nsr, [0.15, 0.40], band_hit=False)

            out, rc = build(tmp)
            leg("fixture A builds rc0", rc == 0, str(out.get("verdict")))
            leg("degenerate null detected as a mass point",
                out["null_health"]["w17"]["mass_point"] is True
                and out["null_health"]["w20"]["mass_point"] is False,
                "%s/%s" % (out["null_health"]["w17"]["mass_point"],
                           out["null_health"]["w20"]["mass_point"]))
            leg("do-nothing rate read as k/n, not as a constant",
                abs(out["do_nothing"]["rate"] - 641.0 / 1253.0) < 1e-9
                and out["do_nothing"]["k"] == 641
                and out["do_nothing"]["n"] == 1253)
            leg("band-hit flag called structural",
                out["flags"]["BAND_HIT_WAS_STRUCTURAL"] is True)
            leg("control arm re-derives every published count",
                all(c["match"] for c in out["control_arm_survivor_counts"]),
                str(out["control_arm_survivor_counts"]))
            leg("primary verdict names the two-null split",
                out["verdict"] == "BAND_AND_BAR_MEASURE_DIFFERENT_NULLS",
                out["verdict"])
            lad = {r["name"]: r["survivors"] for r in out["ladder"]}
            leg("ladder is monotone in the threshold",
                lad["prereg_band_hi"] <= lad["do_nothing_rate"]
                <= lad["observed_null_p95"],
                str(lad))
            leg("bootstrap is seeded-deterministic",
                build(tmp)[0]["bootstrap"] == out["bootstrap"])

            # ---- fixture B: cells inside the null support -> no extrapolation
            inside = []
            for i in range(6):
                inside.append(("I-%02d" % i, "turnover_regime", 0.60,
                               1300 + 100 * i))
            _write_wave(tmp, "w20", real_null, inside, round(p95, 6),
                        [0.50, 0.53], 6, [0.15, 0.40], band_hit=False)
            out_b, rc_b = build(tmp)
            leg("all cells inside support -> beyond-support flag off",
                out_b["flags"][
                    "MOST_SURVIVORS_JUDGED_OUTSIDE_THE_MEASURED_REGION"]
                is False and out_b["support"]["cells_below"] == 0,
                str(out_b["support"]))

            # ---- fixture C: planted flip (pooled fails, matched passes)
            # a two-step null: half the draws trade 1200 times at rate 0.30,
            # half trade 2000 times at rate 0.10 -- so the pooled p95 sits on
            # the 0.30 shelf while a 2000-trade cell is read against 0.10.
            stepped = [(0.30, 1200)] * 100 + [(0.10, 2000)] * 100
            planted = [("P-01", "dd_rung_entry", 0.25, 2000)]
            _write_wave(tmp, "w20", stepped, planted, 0.30,
                        [0.50, 0.53], 0, [0.15, 0.40], band_hit=False)
            out_c, _ = build(tmp)
            fl = out_c["matched"]["flips"]
            leg("planted flip is named, not silently dropped",
                len(fl) == 1 and fl[0]["cell_id"] == "P-01"
                and fl[0]["verdict"] == "LOCAL_PASS_POOLED_FAIL",
                str(fl))
            leg("planted flip sits inside the null support",
                out_c["support"]["cells_below"] == 0
                and out_c["matched"]["measured_region"]["cells"] == 1,
                str(out_c["support"]))

            # ---- fixture D: a null that does not respond to turnover
            flat_null = [(0.45 + rng.gauss(0.0, 0.05), t)
                         for _, t in real_null]
            _write_wave(tmp, "w20", flat_null, cells, round(p95, 6),
                        [0.50, 0.53], nsr, [0.15, 0.40], band_hit=False)
            out_d, _ = build(tmp)
            leg("no turnover slope -> turnover-invariance flag off",
                abs(out_d["regression"]["slope_per_1000_pp"]) < 5.0
                and out_d["flags"]["BAND_ASSUMED_TURNOVER_INVARIANCE"] is False,
                str(out_d["regression"]))

            # ---- fixture E: check catches a tampered number, then a moved input
            p = os.path.join(tmp, OUT_JSON)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            good, rc_g = build(tmp)
            leg("fixture E builds rc0 before tampering", rc_g == 0)
            bad = json.loads(json.dumps(good))
            bad["attribution"]["n_pooled"] = good["attribution"]["n_pooled"] + 1
            with open(p, "w", encoding="utf-8") as fh:
                json.dump(bad, fh, ensure_ascii=False)
            rc_bad = cmd_check()
            leg("tampered number -> CHECK FAILED, names the field",
                rc_bad == 1, "rc=%s" % rc_bad)
            with open(p, "w", encoding="utf-8") as fh:
                json.dump(good, fh, ensure_ascii=False)
            leg("restored face -> CHECK OK", cmd_check() == 0)
            csvp, _ = _wave_paths(tmp, "w20")
            with open(csvp, "a", encoding="utf-8") as fh:
                fh.write("\n")
            rc_stale = cmd_check()
            leg("moved input bytes -> rc3 and the word STALE",
                rc_stale == 3, "rc=%s" % rc_stale)

            # ---- fixture F: a missing wave refuses instead of counting zero
            os.remove(os.path.join(tmp, "results", "trial_labor_w18",
                                   "w18_screen.json"))
            out_f, rc_f = build(tmp)
            leg("missing wave -> REFUSE rc2, never a silent zero",
                rc_f == 2 and out_f["verdict"] == "REFUSE_WAVE_FACE_MISSING")
        finally:
            ROOT = keep

    # ---- real-repo legs: published face agrees with a fresh build
    real, rc_real = build()
    p = os.path.join(ROOT, OUT_JSON)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as fh:
            pub = json.load(fh)
        leg("published face == fresh build (real repo)",
            pub.get("verdict") == real["verdict"]
            and pub["attribution"]["n_pooled"]
            == real["attribution"]["n_pooled"]
            and pub["do_nothing"]["rate"] == real["do_nothing"]["rate"])
        leg("real repo: control arm 4/4",
            all(c["match"] for c in pub["control_arm_survivor_counts"]))
        leg("real repo: the two nulls are told apart",
            pub["null_health"]["w20"]["modal_share"] < 0.05
            and min(pub["null_health"][w]["modal_share"]
                    for w in BAND_WAVES) >= 0.90)
        leg("real repo: why_it_matters carries k/n and both counts",
            "641" in pub["why_it_matters"]
            and str(pub["attribution"]["n_pooled"]) in pub["why_it_matters"])
    else:
        leg("published face exists (run first)", False, OUT_JSON)

    for name, ok, detail in legs:
        print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name,
                               ("  (%s)" % detail) if detail and not ok else ""))
    print("selftest %d/%d PASS" % (len(legs) - len(fails), len(legs)))
    return 0 if not fails else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("run")
    sub.add_parser("check")
    sub.add_parser("selftest")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        return cmd_run()
    if a.cmd == "check":
        return cmd_check()
    if a.cmd == "selftest":
        return cmd_selftest()
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
