# -*- coding: utf-8 -*-
"""is the R20 -> R10 cadence gap driven by the START DATE or by the CALENDAR SEGMENT?

WHY THIS FILE EXISTS
--------------------
r2129 (scripts/etf_book_cadence_start_dates.py) moved the start date out of the 2020 winter and
found the paired cadence gap flips sign (to-cutoff median -2.64pp). It then named the one thing
it could not separate, in its own honest block:

    "the earlier a book starts the more of 2020-2021 it contains, so for the earliest anchors
     'start date' and 'which regime you lived through' are the same knob -- this face does not
     separate them"

This face separates them. Every book is cut into the SAME calendar quarters, and the per-quarter
cadence delta is measured inside each quarter. A quarter that four start dates all live through
gives four observations of the SAME market with only the entry date differing -- that is the
start-date (path) channel. The same book read across quarters gives one observation per market
with only the market differing -- that is the regime channel. A two-way median polish then asks
which channel moves the delta more.

WHAT IT IS NOT
--------------
No verdict on the production ticket (that stays with results/etf_book_rebal_adoption.json,
PHASE_DEPENDENT). No new engine: it consumes scripts/etf_book_cadence_start_dates.build_inputs
(panel + score, bond-removed universe) and scripts/etf_variants_null_rolling.fast_next_open
(the pinned next-open fill chain), both imported, neither copied.

Two channels are NOT statistically independent: the path channel is a portfolio-sort difference,
the regime channel is a market difference, and a quarter with only two live books gives a very
thin path reading. Cells that cannot be read are NAMED in `holes`, never zeroed.

self  python scripts/etf_book_cadence_regime_split.py selftest
run   python scripts/etf_book_cadence_regime_split.py run
check python scripts/etf_book_cadence_regime_split.py check
"""

import hashlib
import json
import os
import statistics as st
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "results", "etf_book_cadence_regime_split.json")
FACE = "results/etf_book_cadence_regime_split.json"
SCHEMA = "etf-book-cadence-regime-split/v1"

BASE_MONEY = 1_000_000.0
N_HOLD = 5
CADENCE_FAST, CADENCE_SLOW = 10, 20
COSTS = {"8bp": 0.0008, "1bp": 0.0001}
MIN_BARS = 40                 # a quarter slice shorter than this is a named hole, not a zero

# start dates chosen to give overlapping coverage from 2022Q1 on, and to stay OUT of the
# 2020-01..2020-03 winter that r2128/r2129 both found dominate the family's phase grid
STARTS = ["2021-09-01", "2022-03-01", "2022-09-01", "2023-03-01", "2023-09-01", "2024-03-01"]

# calendar quarters, as [lo, hi) date strings
SEGMENTS = []
for _y in range(2022, 2026):
    for _q, (_m0, _m1) in enumerate(((1, 4), (4, 7), (7, 10), (10, 13)), start=1):
        SEGMENTS.append({"label": "%dQ%d" % (_y, _q),
                         "lo": "%04d-%02d-01" % (_y, _m0),
                         "hi": "%04d-%02d-01" % (_y + (1 if _m1 > 12 else 0),
                                                 (1 if _m1 > 12 else _m1))})

# frozen before the first run of this round
PATH_DOMINATES_RATIO = 2.0    # path spread >= 2x regime spread -> the entry date is the knob
REGIME_DOMINATES_RATIO = 2.0  # regime spread >= 2x path spread -> the market segment is the knob
MIN_BOOKS_PER_SEGMENT = 2     # a quarter with one book cannot separate path from itself
MIN_SEGMENTS_PER_BOOK = 3     # a book read on two quarters cannot show a regime spread

RULE = {
    "R1_starts": "six quarterly start dates 2021-09-01..2024-03-01, deliberately outside the "
                 "2020 winter; a book shorter than 2 quarters is named, never zeroed",
    "R2_same_grid": "every book is cut on the same calendar quarters, so two books differ only "
                    "in entry date inside a quarter and one book differs only in market across "
                    "quarters -- that is what makes the two channels separable at all",
    "R3_pair": "inside a quarter a delta pairs the SAME bar grid, cost, n_hold and start; only "
               "the cadence differs",
    "R4_polish": "two-way median polish, 9 sweeps, on the (start x segment) delta grid; row "
                 "effect = start-date channel, column effect = regime channel, residual = the "
                 "interaction neither explains",
    "R5_verdict": "compare the interquartile spread of the row effects with that of the column "
                  "effects; a ratio >= %.1f names a winner, anything less is MIXED"
                  % PATH_DOMINATES_RATIO,
    "R6_thin": "a quarter needs >= %d live books to be used for the path channel, and a book "
               "needs >= %d readable quarters to be used for the regime channel; every excluded "
               "cell is named in holes" % (MIN_BOOKS_PER_SEGMENT, MIN_SEGMENTS_PER_BOOK),
    "R7_money": "money lines use a %d reference account" % BASE_MONEY,
    "frozen": "thresholds written before the first read of these panels in this round",
}


# --------------------------------------------------------------------------------------
# pure functions (selftest drives these without a panel)
# --------------------------------------------------------------------------------------
def slice_ret(series, lo, hi, min_bars=MIN_BARS):
    """total return of one leg inside [lo, hi); None when the slice is too thin to speak."""
    import pandas as pd
    idx = pd.to_datetime(list(series.index))
    lo_ts, hi_ts = pd.Timestamp(lo), pd.Timestamp(hi)
    sel = (idx >= lo_ts) & (idx < hi_ts)
    if int(sel.sum()) < min_bars:
        return None, int(sel.sum())
    vals = [series.iloc[i] for i, keep in enumerate(sel) if keep]
    first, last = float(vals[0]), float(vals[-1])
    if first <= 0:
        return None, int(sel.sum())
    return last / first - 1.0, int(sel.sum())


def quartiles(vals):
    v = sorted(vals)
    if len(v) < 4:
        return None, None
    n = len(v)

    def at(p):
        pos = p * (n - 1)
        lo = int(pos)
        hi = min(lo + 1, n - 1)
        return v[lo] + (v[hi] - v[lo]) * (pos - lo)

    return at(0.25), at(0.75)


def spread(vals):
    if not vals:
        return None
    q1, q3 = quartiles(vals)
    return (q3 - q1) if q1 is not None else None


def polish(grid, sweeps=9):
    """two-way median polish on {(row, col): value}; returns effects and the residual grid."""
    rows = sorted({r for r, _ in grid})
    cols = sorted({c for _, c in grid})
    row_eff = {r: 0.0 for r in rows}
    col_eff = {c: 0.0 for c in cols}
    grand = st.median(list(grid.values())) if grid else 0.0
    resid = {k: v - grand for k, v in grid.items()}
    for _ in range(sweeps):
        for r in rows:
            vals = [resid[(r, c)] for c in cols if (r, c) in resid]
            if not vals:
                continue
            m = st.median(vals)
            row_eff[r] += m
            for c in cols:
                if (r, c) in resid:
                    resid[(r, c)] -= m
        for c in cols:
            vals = [resid[(r, c)] for r in rows if (r, c) in resid]
            if not vals:
                continue
            m = st.median(vals)
            col_eff[c] += m
            for r in rows:
                if (r, c) in resid:
                    resid[(r, c)] -= m
    return {"grand": grand, "row": row_eff, "col": col_eff, "resid": resid,
            "rows": rows, "cols": cols}


def channels(cells, min_books=MIN_BOOKS_PER_SEGMENT, min_segs=MIN_SEGMENTS_PER_BOOK):
    """split the delta grid into a start-date spread and a regime spread."""
    by_seg, by_start = {}, {}
    for c in cells:
        d = c.get("delta_pp")
        if d is None:
            continue
        by_seg.setdefault(c["segment"], []).append(d)
        by_start.setdefault(c["start"], []).append(d)

    path_cells = {g: v for g, v in by_seg.items() if len(v) >= min_books}
    regime_cells = {s: v for s, v in by_start.items() if len(v) >= min_segs}

    path_spreads = [spread(v) for v in path_cells.values() if len(v) >= min_books]
    regime_spreads = [spread(v) for v in regime_cells.values() if len(v) >= min_segs]
    path_spreads = [x for x in path_spreads if x is not None]
    regime_spreads = [x for x in regime_spreads if x is not None]

    return {
        "by_segment": {g: {"n_books": len(v), "median_pp": st.median(v),
                           "spread_pp": spread(v), "min_pp": min(v), "max_pp": max(v)}
                       for g, v in sorted(by_seg.items())},
        "by_start": {s: {"n_segments": len(v), "median_pp": st.median(v),
                         "spread_pp": spread(v), "min_pp": min(v), "max_pp": max(v)}
                     for s, v in sorted(by_start.items())},
        "path_spread_median_pp": st.median(path_spreads) if path_spreads else None,
        "path_spread_n": len(path_spreads),
        "regime_spread_median_pp": st.median(regime_spreads) if regime_spreads else None,
        "regime_spread_n": len(regime_spreads),
        "excluded_thin_segments": sorted(g for g, v in by_seg.items() if len(v) < min_books),
        "excluded_thin_starts": sorted(s for s, v in by_start.items() if len(v) < min_segs),
    }


def words(ch):
    """frozen reading of the two channel spreads."""
    out = []
    p, r = ch["path_spread_median_pp"], ch["regime_spread_median_pp"]
    if p is None or r is None:
        return ["CHANNELS_NOT_SEPARABLE"]
    if p <= 0 and r <= 0:
        out.append("BOTH_CHANNELS_FLAT")
    elif p >= PATH_DOMINATES_RATIO * r:
        out.append("START_DATE_DOMINATES")
    elif r >= REGIME_DOMINATES_RATIO * p:
        out.append("REGIME_DOMINATES")
    else:
        out.append("MIXED_CHANNELS")
    if ch["path_spread_n"] and ch["regime_spread_n"]:
        out.append("BOTH_CHANNELS_READ")
    else:
        out.append("CHANNEL_COVERAGE_INCOMPLETE")
    return out


# --------------------------------------------------------------------------------------
# inputs (read-only, imported from the family -- zero re-implementation)
# --------------------------------------------------------------------------------------
def build_inputs():
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from scripts import etf_book_cadence_start_dates as SD
    return SD.build_inputs()


def fingerprint(close, cols):
    import pandas as pd
    idx = pd.to_datetime(close.index)
    tail = [str(d.date()) for d in idx[-3:]]
    h = hashlib.sha1()
    h.update(("|".join(tail) + "|%d|%d" % (len(idx), len(cols))).encode("utf-8"))
    last = close[cols].iloc[-1].fillna(0.0).round(6)
    h.update(("|".join("%s=%.6f" % (k, float(v)) for k, v in last.items())).encode("utf-8"))
    return {"cutoff": tail[-1], "bars": int(len(idx)), "cols": int(len(cols)),
            "sha1": h.hexdigest()}


def compute():
    F, V, close, openp, cols, score = build_inputs()
    fp = fingerprint(close, cols)

    cells, holes = [], []
    for start in STARTS:
        for cost_key, cost in COSTS.items():
            runs = {}
            for cad in (CADENCE_FAST, CADENCE_SLOW):
                ser, turn, _gap = V.fast_next_open(score, close[cols], openp[cols], cad,
                                                   n_hold=N_HOLD, cost=cost, start=start)
                if ser is None or len(ser) < MIN_BARS:
                    runs[cad] = None
                    holes.append({"start": start, "cost": cost_key, "cadence": cad,
                                  "why": "run came back empty or shorter than %d bars" % MIN_BARS})
                    continue
                runs[cad] = {"ser": ser, "turn": float(turn)}
            if runs.get(CADENCE_FAST) is None or runs.get(CADENCE_SLOW) is None:
                continue
            for seg in SEGMENTS:
                rf, nf = slice_ret(runs[CADENCE_FAST]["ser"], seg["lo"], seg["hi"])
                rs, ns = slice_ret(runs[CADENCE_SLOW]["ser"], seg["lo"], seg["hi"])
                if rf is None or rs is None:
                    holes.append({"start": start, "cost": cost_key, "segment": seg["label"],
                                  "why": "slice too thin (%d/%d bars < %d)"
                                         % (nf, ns, MIN_BARS)})
                    continue
                cells.append({
                    "start": start, "cost": cost_key, "segment": seg["label"],
                    "bars": min(nf, ns),
                    "ret_fast_pct": rf * 100.0, "ret_slow_pct": rs * 100.0,
                    "delta_pp": (rf - rs) * 100.0,
                })

    by_cost = {}
    for cost_key in COSTS:
        sub = [c for c in cells if c["cost"] == cost_key]
        grid = {(c["start"], c["segment"]): c["delta_pp"] for c in sub}
        pol = polish(grid) if grid else None
        ch = channels(sub)
        entry = {
            "channels": ch,
            "words": " | ".join(words(ch)),
            "n_cells": len(sub),
            "both_positive_share": (sum(1 for c in sub if c["delta_pp"] > 0) / float(len(sub))
                                    if sub else None),
            "median_delta_pp": st.median([c["delta_pp"] for c in sub]) if sub else None,
        }
        if pol:
            entry["polish"] = {
                "grand_pp": pol["grand"],
                "row_effect_pp": {k: round(v, 6) for k, v in sorted(pol["row"].items())},
                "col_effect_pp": {k: round(v, 6) for k, v in sorted(pol["col"].items())},
                "row_spread_pp": spread(list(pol["row"].values())),
                "col_spread_pp": spread(list(pol["col"].values())),
                "residual_spread_pp": spread(list(pol["resid"].values())),
            }
        by_cost[cost_key] = entry

    main = by_cost.get("8bp", {})
    ch8 = main.get("channels") or {}
    w8 = main.get("words")
    pol8 = main.get("polish") or {}

    money = {
        "reference_account_cny": BASE_MONEY,
        "path_spread_cny": ((ch8.get("path_spread_median_pp") or 0.0) / 100.0 * BASE_MONEY
                            if ch8.get("path_spread_median_pp") is not None else None),
        "regime_spread_cny": ((ch8.get("regime_spread_median_pp") or 0.0) / 100.0 * BASE_MONEY
                              if ch8.get("regime_spread_median_pp") is not None else None),
        "note": "the two spreads are per-quarter total-return gaps, not annualised; they size "
                "how much the quarter's answer moves, they do not add up to an annual return",
    }

    sentence = (
        "把 6 个起跑日（2021-09..2024-03，全在 2020 冬天之外）切成同一批日历季度后："
        "同一季度里换起跑日，节奏差的中位四分位极差 %s pp（%d 个可用季度）；"
        "同一本书换季度，极差 %s pp（%d 本可用书）→ %s。"
        "双因素中位抛光后行（起跑日）效应极差 %s pp、列（行情段）效应极差 %s pp、残差 %s pp。"
        % (("%.2f" % ch8["path_spread_median_pp"]) if ch8.get("path_spread_median_pp") is not None
           else "n/a", ch8.get("path_spread_n") or 0,
           ("%.2f" % ch8["regime_spread_median_pp"]) if ch8.get("regime_spread_median_pp")
           is not None else "n/a", ch8.get("regime_spread_n") or 0,
           w8, ("%.2f" % pol8["row_spread_pp"]) if pol8.get("row_spread_pp") is not None
           else "n/a",
           ("%.2f" % pol8["col_spread_pp"]) if pol8.get("col_spread_pp") is not None else "n/a",
           ("%.2f" % pol8["residual_spread_pp"]) if pol8.get("residual_spread_pp")
           is not None else "n/a")
    )

    return {
        "schema": SCHEMA, "face": FACE,
        "question": "the R20->R10 cadence gap was measured on books that all start in one "
                    "winter; once start dates spread out, is the gap a property of the entry "
                    "date or of the market segment the book happens to live in?",
        "rule": RULE,
        "evidence_cutoff": fp["cutoff"],
        "panel_fingerprint": fp,
        "starts": STARTS, "segments": [s["label"] for s in SEGMENTS],
        "segment_bounds": {s["label"]: [s["lo"], s["hi"]] for s in SEGMENTS},
        "costs": {k: round(v, 6) for k, v in COSTS.items()},
        "n_hold": N_HOLD,
        "cadence": {"fast": CADENCE_FAST, "slow": CADENCE_SLOW},
        "cells": cells,
        "holes": holes,
        "by_cost": by_cost,
        "money": money,
        "headline": {
            "words_8bp": w8,
            "path_spread_median_pp": ch8.get("path_spread_median_pp"),
            "regime_spread_median_pp": ch8.get("regime_spread_median_pp"),
            "path_spread_n": ch8.get("path_spread_n"),
            "regime_spread_n": ch8.get("regime_spread_n"),
            "median_delta_pp": main.get("median_delta_pp"),
            "both_positive_share": main.get("both_positive_share"),
            "row_spread_pp": pol8.get("row_spread_pp"),
            "col_spread_pp": pol8.get("col_spread_pp"),
            "residual_spread_pp": pol8.get("residual_spread_pp"),
        },
        "desk_sentence": sentence,
        "honest": [
            "survivorship: the on-disk panel holds ETFs that still exist (family caveat)",
            "no vol target: fast_next_open has none, so these are un-targeted books",
            "a quarter with only two live books gives a thin path reading; quarters with one "
            "book are named in channels.excluded_thin_segments and never read as zero spread",
            "path and regime channels are not independent samples: the path channel is a "
            "portfolio-sort difference inside one market, the regime channel is a market "
            "difference for one sort; the polish residual is the part neither explains",
            "start dates were chosen to leave the 2020 winter out, so this face says nothing "
            "about how that winter's reading behaves",
            "quarter returns are total returns inside a quarter, not annualised; they size the "
            "movement of the answer, they do not sum to an annual number",
        ],
    }


def write_face(doc):
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


# --------------------------------------------------------------------------------------
# check: cheap invariants + an external anchor (never the re-run)
# --------------------------------------------------------------------------------------
TOL = 1e-9


def check():
    if not os.path.exists(OUT_PATH):
        print("STALE face missing: %s" % FACE)
        return 3
    with open(OUT_PATH, "r", encoding="utf-8") as fh:
        old = json.load(fh)

    try:
        F, V, close, openp, cols, score = build_inputs()
        live = fingerprint(close, cols)
    except Exception as exc:                                    # noqa: BLE001
        print("STALE panel could not be rebuilt: %r" % (exc,))
        return 3
    oldfp = old.get("panel_fingerprint") or {}
    if live["sha1"] != oldfp.get("sha1"):
        print("STALE input panel moved: cutoff %s -> %s, bars %s -> %s"
              % (oldfp.get("cutoff"), live["cutoff"], oldfp.get("bars"), live["bars"]))
        return 3

    bad = []
    cells = old.get("cells") or []
    if not cells:
        print("CHECK FAILED no cells stored")
        return 1
    for c in cells:
        d = c["ret_fast_pct"] - c["ret_slow_pct"]
        if abs(d - c["delta_pp"]) > TOL:
            bad.append("cell %s/%s/%s delta %.6f != fast-slow %.6f"
                       % (c["start"], c["cost"], c["segment"], c["delta_pp"], d))
        if c["bars"] < MIN_BARS:
            bad.append("cell %s/%s/%s kept %d bars (< min %d)"
                       % (c["start"], c["cost"], c["segment"], c["bars"], MIN_BARS))

    for cost_key in COSTS:
        sub = [c for c in cells if c["cost"] == cost_key]
        if not sub:
            continue
        ch = channels(sub)
        stored = (old.get("by_cost") or {}).get(cost_key) or {}
        st_ch = stored.get("channels") or {}
        for k in ("path_spread_median_pp", "regime_spread_median_pp"):
            a, b = ch.get(k), st_ch.get(k)
            if a is None or b is None:
                if a != b:
                    bad.append("%s %s: recomputed %r != stored %r" % (cost_key, k, a, b))
                continue
            if abs(a - b) > 1e-6:
                bad.append("%s %s: recomputed %.6f != stored %.6f" % (cost_key, k, a, b))
        w = " | ".join(words(ch))
        if w != (stored.get("words") or ""):
            bad.append("%s words: recomputed %r != stored %r" % (cost_key, w, stored.get("words")))

    if bad:
        print("CHECK FAILED")
        for b in bad[:12]:
            print("  " + b)
        return 1
    print("CHECK_OK REGIME_SPLIT_CONSISTENT cells=%d holes=%d" % (len(cells),
                                                                  len(old.get("holes") or [])))
    return 0


# --------------------------------------------------------------------------------------
# selftest: the frozen readings, on synthetic grids
# --------------------------------------------------------------------------------------
def selftest():
    legs = []

    def ok(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    import pandas as pd

    # 1) slice_ret reads the same book, and refuses a thin slice
    ser = pd.Series({pd.Timestamp("2022-01-%02d" % d): 1.0 + 0.01 * i
                     for i, d in enumerate(range(2, 30))})
    r, n = slice_ret(ser, "2022-01-01", "2022-02-01", min_bars=10)
    ok("slice_ret reads a fat slice", r is not None and n >= 10, "ret=%r n=%s" % (r, n))
    r2, n2 = slice_ret(ser, "2022-01-01", "2022-01-10", min_bars=10)
    ok("slice_ret refuses a thin slice", r2 is None and n2 < 10, "ret=%r n=%s" % (r2, n2))
    ok("slice_ret never returns a zero for a hole", r2 is None, "None not 0.0")

    # 2) polish recovers a pure row effect
    grid = {}
    for r_ in ("a", "b", "c"):
        for c_ in ("q1", "q2", "q3", "q4"):
            grid[(r_, c_)] = {"a": 2.0, "b": 0.0, "c": -2.0}[r_]
    pol = polish(grid)
    row_sp = max(pol["row"].values()) - min(pol["row"].values())
    col_sp = max(pol["col"].values()) - min(pol["col"].values())
    res_sp = max(pol["resid"].values()) - min(pol["resid"].values())
    ok("polish recovers a pure row effect", abs(row_sp - 4.0) < 1e-6, "row_spread=%.6f" % row_sp)
    ok("polish leaves a pure row grid with no column effect", abs(col_sp) < 1e-6,
       "col_spread=%.6f" % col_sp)
    ok("polish leaves no residual on a rank-1 grid", abs(res_sp) < 1e-6, "resid=%.6f" % res_sp)

    # 3) polish recovers a pure column effect
    grid2 = {}
    for r_ in ("a", "b", "c"):
        for i, c_ in enumerate(("q1", "q2", "q3", "q4")):
            grid2[(r_, c_)] = i * 1.5
    pol2 = polish(grid2)
    row2 = max(pol2["row"].values()) - min(pol2["row"].values())
    col2 = max(pol2["col"].values()) - min(pol2["col"].values())
    ok("polish recovers a pure column effect", abs(col2 - 4.5) < 1e-6, "col_spread=%.6f" % col2)
    ok("polish leaves a pure column grid with no row effect", abs(row2) < 1e-6,
       "row_spread=%.6f" % row2)

    # 4) channels + words on a path-dominated synthetic sheet (4 books x 4 quarters, so a
    #    quartile spread exists on both axes -- three points is a number, not a spread)
    cells_path = []
    for s_i, s_ in enumerate(("s1", "s2", "s3", "s4")):
        for g in ("q1", "q2", "q3", "q4"):
            cells_path.append({"start": s_, "segment": g, "delta_pp": 2.0 * s_i})
    ch = channels(cells_path)
    ok("path-dominated sheet names START_DATE_DOMINATES",
       "START_DATE_DOMINATES" in words(ch), "words=%s" % words(ch))
    ok("path-dominated sheet still keeps >=2 books per quarter",
       not ch["excluded_thin_segments"], "excluded=%s" % ch["excluded_thin_segments"])
    ok("path-dominated sheet reads both channels", "BOTH_CHANNELS_READ" in words(ch),
       "path_n=%s regime_n=%s" % (ch["path_spread_n"], ch["regime_spread_n"]))

    # 5) regime-dominated sheet (same geometry, effects transposed)
    cells_reg = []
    for s_ in ("s1", "s2", "s3", "s4"):
        for g_i, g in enumerate(("q1", "q2", "q3", "q4")):
            cells_reg.append({"start": s_, "segment": g, "delta_pp": 2.0 * g_i})
    ch2 = channels(cells_reg)
    ok("regime-dominated sheet names REGIME_DOMINATES",
       "REGIME_DOMINATES" in words(ch2), "words=%s" % words(ch2))

    # 6) thin quarters are named, not zeroed
    thin = [{"start": "s1", "segment": "q1", "delta_pp": 3.0},
            {"start": "s2", "segment": "q2", "delta_pp": 0.5},
            {"start": "s3", "segment": "q2", "delta_pp": 0.6},
            {"start": "s4", "segment": "q2", "delta_pp": 0.7}]
    ch3 = channels(thin)
    ok("a one-book quarter is excluded, not read as zero spread", "q1" in ch3["excluded_thin_segments"],
       "excluded=%s" % ch3["excluded_thin_segments"])

    # 7) a book with too few quarters is excluded from the regime channel
    ok("a two-quarter book is excluded from the regime channel",
       "s1" in ch3["excluded_thin_starts"], "excluded=%s" % ch3["excluded_thin_starts"])

    # 8) not separable when a channel is missing entirely
    one = [{"start": "s1", "segment": "q1", "delta_pp": 1.0}]
    ok("missing both channels says NOT_SEPARABLE",
       words(channels(one)) == ["CHANNELS_NOT_SEPARABLE"], "words=%s" % words(channels(one)))

    # 9) spread refuses fewer than four points (a quartile of three is a number, not a spread)
    ok("spread is None for three points", spread([1.0, 2.0, 3.0]) is None)
    ok("spread is a number for four points", spread([1.0, 2.0, 3.0, 4.0]) is not None)

    # 10) a face written and re-read keeps its arithmetic (cells path in memory)
    doc = {"schema": SCHEMA, "panel_fingerprint": {"sha1": "x"}, "cells": [
        {"start": "s1", "cost": "8bp", "segment": "q1", "bars": 60,
         "ret_fast_pct": 3.0, "ret_slow_pct": 1.0, "delta_pp": 2.0}], "holes": []}
    ok("delta equals fast minus slow on a written cell",
       abs((doc["cells"][0]["ret_fast_pct"] - doc["cells"][0]["ret_slow_pct"])
           - doc["cells"][0]["delta_pp"]) < TOL)

    npass = sum(1 for _, good, _ in legs if good)
    for name, good, detail in legs:
        print("%s %s%s" % ("PASS" if good else "FAIL", name, (" | " + detail) if detail else ""))
    print("selftest %d/%d %s" % (npass, len(legs), "PASS" if npass == len(legs) else "FAIL"))
    return 0 if npass == len(legs) else 1


def run():
    doc = compute()
    write_face(doc)
    print("wrote %s" % FACE)
    print("words 8bp: %s" % doc["headline"]["words_8bp"])
    print("path spread %.3f pp (%s quarters) / regime spread %.3f pp (%s books)"
          % (doc["headline"]["path_spread_median_pp"] or 0.0,
             doc["headline"]["path_spread_n"],
             doc["headline"]["regime_spread_median_pp"] or 0.0,
             doc["headline"]["regime_spread_n"]))
    print(doc["desk_sentence"])
    return 0


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:                                            # noqa: BLE001
        pass
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        return run()
    if cmd == "check":
        return check()
    print("unknown command: %s" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
