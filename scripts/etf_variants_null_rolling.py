"""Permutation null and rolling-origin pass on the surviving ETF composite sleeve subset
(r1248 bm-c).

Why this module exists
----------------------
r1247 re-ran the sleeve subsets on the honest next-open base and left two open items:

  1. the "bond_removed beats its own equal weight in 6/7 years" headline had no null --
     the only permutation null in the tree (etf_composite_pf.null_test) was written on the
     CLOSE basis and only for the all-class book, and r1245 showed the basis matters;
  2. every number came from one fixed origin (2020-01-01), so the excess could be a
     start-date artefact of a single regime.

This module answers both, on the same next-open leg engine (never a re-implementation --
`fast_next_open` is pinned to `etf_composite_pf.run_next_open` in --selftest):

  * null: shuffle each factor's cross-section date by date (killing the factor->return
    link, keeping the per-date rank distribution), rebuild the composite, re-pick the
    top-N book and re-run the FILL engine. The statistic under test is the excess the
    product actually claims -- OOS CAGR minus the same-subset equal-weight control's OOS
    CAGR -- not a Sharpe on a different question.
  * rolling origin: restart the same book at every January from 2020 to 2025 and report
    book-vs-control per origin.

Basis and cost are inherited verbatim from the engine (decision at close t, fill at open
t+1, overnight gap to the OLD book, weight change charged at the fill open, new book earns
open->close, 8bp/side). Exploratory, not a preregistered judgement.

Usage:
  python scripts/etf_variants_null_rolling.py --selftest
  python scripts/etf_variants_null_rolling.py [--iter 300] [--only-null]
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd

from config import PATHS
from scripts import etf_composite_pf as F
from scripts.etf_asset_class import classify

KEEP = ("equity", "commodity", "crossborder")   # the bond_removed subset (r1247 survivor)
REBAL = 20
OOS = pd.Timestamp("2024-01-01")
ORIGINS = ("2020-01-01", "2021-01-01", "2022-01-01", "2023-01-01", "2024-01-01", "2025-01-01")


def _leg(a, b, ix):
    """Mean simple return over the held book between two price faces (engine-identical)."""
    if ix.size == 0:
        return None
    av, bv = a[ix], b[ix]
    v = bv / av - 1.0
    v = v[np.isfinite(v) & np.isfinite(av) & (av > 0)]
    return float(v.mean()) if v.size else None


def fast_next_open(score, close, openp, rebal, n_hold=None, cost=None, start="2020-01-01"):
    """Same leg chain as etf_composite_pf.run_next_open, on numpy arrays.

    `score` is supplied directly (a DataFrame of the same columns; NaN = not eligible), so a
    permutation null can drive the fill engine without rebuilding pandas rankings. The loop
    mirrors the reference implementation bar for bar, including its convention of stopping
    at the second-to-last decision date. --selftest pins the two to 1e-12.
    """
    n_hold = F.N_HOLD if n_hold is None else n_hold
    cost = F.COST if cost is None else cost
    idx = pd.to_datetime(close.index)
    cols = close.columns
    P = close.reindex(columns=cols).ffill().to_numpy(dtype=float)
    Oraw = openp.reindex(columns=cols).to_numpy(dtype=float)
    O = np.where(np.isfinite(Oraw), Oraw, P)
    S = score.reindex(index=idx, columns=cols).to_numpy(dtype=float)

    pos = [i for i, d in enumerate(idx) if d >= pd.Timestamp(start)]
    if len(pos) < 3:
        return pd.Series(dtype=float), 0.0, 0
    rebal_pos = set(pos[::rebal])

    equity = 1.0
    curve = [(idx[pos[0]], equity)]
    held = np.empty(0, dtype=int)
    pending = None
    turn_sum = 0.0
    n_r = 0
    gapfill = 0

    for j, i in enumerate(pos):
        if j > 0:
            prev = pos[j - 1]
            if held.size:
                gapfill += int(np.count_nonzero(~np.isfinite(Oraw[i, held])))
            if pending is not None:
                if held.size:
                    r = _leg(P[prev], O[i], held)
                    if r is not None:
                        equity *= (1.0 + r)
                new, turn = pending
                equity *= (1.0 - cost * turn)
                turn_sum += turn
                n_r += 1
                held = new
                pending = None
                r = _leg(O[i], P[i], held)
                if r is not None:
                    equity *= (1.0 + r)
            elif held.size:
                r = _leg(P[prev], P[i], held)
                if r is not None:
                    equity *= (1.0 + r)
            curve.append((idx[i], equity))

        if i in rebal_pos:
            row = S[i]
            m = np.isfinite(row)
            if int(m.sum()) >= n_hold:
                cand = np.flatnonzero(m)
                picks = cand[np.argsort(-row[cand], kind="stable")][:n_hold]
                turn = len(set(picks.tolist()) ^ set(held.tolist())) / float(n_hold)
                pending = (picks.astype(int), turn)

    ser = pd.Series(dict(curve))
    return ser, (turn_sum / n_r if n_r else 0.0), gapfill


def _excess(ser, ew):
    mf, me = F.metrics(ser, "book"), F.metrics(ew, "ew")
    if "cagr" not in mf or "cagr" not in me:
        return None
    return (mf["cagr"] - me["cagr"]) * 100.0, mf, me


def rolling_origins(score, close, openp, amt, cols):
    rows = {}
    for start in ORIGINS:
        if close.index[close.index >= pd.Timestamp(start)].shape[0] < 260:
            rows[start] = {"skipped": True, "reason": "fewer than 260 bars from this origin"}
            continue
        ser, turn, gap = fast_next_open(score, close[cols], openp[cols], REBAL, start=start)
        ew = F.run_ew(close[cols], amt[cols], REBAL, start=start)
        ex = _excess(ser, ew)
        if ex is None:
            rows[start] = {"skipped": True, "reason": "too short for a CAGR"}
            continue
        ex_pp, mf, me = ex
        oos_ser = ser[ser.index >= OOS]
        oos = F.metrics(oos_ser, "oos") if len(oos_ser) > 2 else {}
        rows[start] = {
            "bars": int(mf["bars"]),
            "book_cagr_pct": round(mf["cagr"] * 100, 2),
            "ew_cagr_pct": round(me["cagr"] * 100, 2),
            "excess_pp": round(ex_pp, 2),
            "book_sharpe": mf["sharpe"],
            "book_maxdd_pct": round(mf["maxdd"] * 100, 2),
            "turnover_per_rebal": round(turn, 3),
            "oos_cagr_pct": round(oos["cagr"] * 100, 2) if oos.get("cagr") is not None else None,
        }
        print("origin", start, rows[start])
    return rows


def phase_sweep(score, close, openp, amt, cols, anchor="2020-01-01", span=20):
    """Walk the decision grid over `span` consecutive trading days from `anchor`.

    The rebalance grid is `dates[::REBAL]` measured from the run's own first bar, so moving the
    origin by one day re-times every fill for the whole run. If the headline excess barely
    moves, the cadence claim is phase-robust; if it swings by more than the excess itself, the
    headline is a phase draw and must be published with its dispersion, never as a point.
    """
    idx = pd.to_datetime(close.index)
    pos = [i for i, d in enumerate(idx) if d >= pd.Timestamp(anchor)]
    rows = []
    for k in range(min(span, max(0, len(pos) - 300))):
        start = idx[pos[k]]
        ser, turn, _ = fast_next_open(score, close[cols], openp[cols], REBAL,
                                      start=str(start.date()))
        ew = F.run_ew(close[cols], amt[cols], REBAL, start=str(start.date()))
        ex = _excess(ser, ew)
        if ex is None:
            continue
        ex_pp, mf, me = ex
        rows.append({"start": str(start.date()), "book_cagr_pct": round(mf["cagr"] * 100, 2),
                     "ew_cagr_pct": round(me["cagr"] * 100, 2), "excess_pp": round(ex_pp, 2),
                     "turnover_per_rebal": round(turn, 3)})
    if not rows:
        return {"cells": [], "note": "no cell produced a CAGR"}
    vals = np.array([r["excess_pp"] for r in rows], dtype=float)
    books = np.array([r["book_cagr_pct"] for r in rows], dtype=float)
    return {
        "anchor": anchor, "span_bars": len(rows),
        "cells": rows,
        "excess_pp_min": round(float(vals.min()), 2),
        "excess_pp_median": round(float(np.median(vals)), 2),
        "excess_pp_max": round(float(vals.max()), 2),
        "excess_pp_spread": round(float(vals.max() - vals.min()), 2),
        "cells_positive": "%d/%d" % (int((vals > 0).sum()), vals.size),
        "book_cagr_pct_min": round(float(books.min()), 2),
        "book_cagr_pct_max": round(float(books.max()), 2),
    }


def selftest():
    """Pin the fast engine to the reference one, and pin the score-injection hook."""
    rng = np.random.default_rng(11)
    n_bar, n_col = 90, 12
    idx = pd.bdate_range("2021-01-04", periods=n_bar)
    px = np.cumprod(1.0 + rng.normal(0.0005, 0.012, size=(n_bar, n_col)), axis=0) * 10.0
    close = pd.DataFrame(px, index=idx, columns=["c%02d" % k for k in range(n_col)])
    openp = close * (1.0 + rng.normal(0.0, 0.004, size=(n_bar, n_col)))
    openp.iloc[5, 2] = np.nan          # a missing open must fall back to the close
    openp.iloc[40, [1, 3]] = np.nan

    score = pd.DataFrame(rng.normal(size=(n_bar, n_col)), index=idx, columns=close.columns)
    score.iloc[::7, 9] = np.nan        # sparse eligibility, never below n_hold on a decision bar
    amt = pd.DataFrame(1e9, index=idx, columns=close.columns)

    ref, ref_turn, ref_gap = F.run_next_open(close, openp, amt, {}, 5, start="2021-01-04",
                                             score=score)
    got, got_turn, got_gap = fast_next_open(score, close, openp, 5, start="2021-01-04")
    assert ref.index.equals(got.index), "date grid drift"
    d = float(np.max(np.abs(ref.to_numpy() / got.to_numpy() - 1.0)))
    assert d < 1e-12, ("level drift", d)
    assert abs(ref_turn - got_turn) < 1e-12, (ref_turn, got_turn)
    assert ref_gap == got_gap, ("gapfill drift", ref_gap, got_gap)

    # the injected-score hook must be a pure pass-through: identical to building it inside
    feats = {"mom_12_1": score}
    built = F.build_score(close, amt, feats, min_amt=0, min_hist=0)
    a, _, _ = F.run_next_open(close, openp, amt, feats, 5, start="2021-01-04",
                              min_amt=0, min_hist=0, score=built)
    b, _, _ = F.run_next_open(close, openp, amt, feats, 5, start="2021-01-04",
                              min_amt=0, min_hist=0)
    assert np.allclose(a.to_numpy(), b.to_numpy(), rtol=0, atol=1e-15), "hook is not a pass-through"

    # an origin with too little history must degrade, never raise
    short, _, _ = fast_next_open(score, close, openp, 5, start="2099-01-01")
    assert len(short) == 0, "a future origin must return an empty series"
    print("selftest OK (4/4): engine pinned 1e-12, hook pass-through, gapfill/date grid agree, "
          "short origin degrades")


def main():
    n_iter = 300
    if "--iter" in sys.argv:
        n_iter = int(sys.argv[sys.argv.index("--iter") + 1])
    seed = 7
    only_null = "--only-null" in sys.argv

    t0 = time.time()
    close, openp, amt, feats = F.build_panel()
    classes = pd.Series(classify(list(close.columns)))
    cols = [c for c in close.columns if classes[c] in KEEP]
    print("panel %s bars=%d cols=%d bond_removed=%d (%.1fs)"
          % (close.index[0].date(), close.shape[0], close.shape[1], len(cols), time.time() - t0))

    score = F.build_score(close[cols], amt[cols], feats)
    t0 = time.time()
    ser, turn, gap = fast_next_open(score, close[cols], openp[cols], REBAL)
    fast_secs = time.time() - t0

    # one-time pin against the reference engine on the real panel (the synthetic selftest
    # already covers the maths; this catches any panel-shaped surprise such as duplicate dates)
    ref, ref_turn, _ = F.run_next_open(close[cols], openp[cols], amt[cols], feats, REBAL)
    common = ref.index.intersection(ser.index)
    pin = float(np.max(np.abs(ref.reindex(common).to_numpy() / ser.reindex(common).to_numpy() - 1.0)))
    assert pin < 1e-12, ("real-panel pin drift", pin)
    print("real-panel pin ok (max rel dev %.2e), fast engine %.2fs/run" % (pin, fast_secs))

    ew = F.run_ew(close[cols], amt[cols], REBAL)
    ex_full, mf, me = _excess(ser, ew)
    oos_ser, oos_ew = ser[ser.index >= OOS], ew[ew.index >= OOS]
    ex_oos, mfo, meo = _excess(oos_ser, oos_ew)
    print("real: full %.2f%% vs ew %.2f%% (%.2fpp) | oos %.2f%% vs ew %.2f%% (%.2fpp) | turn %.3f"
          % (mf["cagr"] * 100, me["cagr"] * 100, ex_full,
             mfo["cagr"] * 100, meo["cagr"] * 100, ex_oos, turn))

    out = {
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "basis": "next-open fill (decision at close t, fill at open t+1; overnight gap to the "
                 "OLD book, weight change charged at the fill open, NEW book earns open->close "
                 "on the fill day); 8bp/side on turnover",
        "cost_bp_per_side": round(F.COST * 1e4, 3),
        "n_hold": F.N_HOLD,
        "rebal": REBAL,
        "subset": "bond_removed = equity + commodity + crossborder (%d of %d panel columns)"
                  % (len(cols), close.shape[1]),
        "real": {
            "book": mf, "control_ew": me, "full_excess_pp": round(ex_full, 2),
            "book_oos": mfo, "control_ew_oos": meo, "oos_excess_pp": round(ex_oos, 2),
            "turnover_per_rebal": round(turn, 3), "open_gapfill_cells": int(gap),
            "engine_pin_max_rel_dev": pin,
        },
        "null": {
            "n_iter": n_iter, "seed": seed,
            "shuffle": "each factor cross-section permuted date by date; composite rebuilt, "
                       "top-N re-picked, FILL ENGINE re-run per iteration",
            "statistics": ["full_excess_pp", "oos_excess_pp"],
        },
        "rolling_origin": {},
        "caveats": [
            "survivorship: the on-disk panel holds ETFs that still exist",
            "exploratory analysis, not a preregistered judgement -- no verdict, no ledger booking",
            "the control is equal-weight on the same subset, close basis (as published)",
            "the null shuffles factor ranks, so it tests the ranking skill, not the sleeve choice",
        ],
    }

    # --- rolling origin ---------------------------------------------------------------
    if not only_null:
        out["rolling_origin"] = rolling_origins(score, close, openp, amt, cols)
        ok = [v for v in out["rolling_origin"].values() if not v.get("skipped")]
        out["rolling_origin_beat"] = "%d/%d" % (sum(1 for v in ok if v["excess_pp"] > 0), len(ok))
        print("rolling origin beat:", out["rolling_origin_beat"])

        # The published headline rests on one decision-grid phase. Walk it.
        out["phase_sweep"] = {
            "from_2020": phase_sweep(score, close, openp, amt, cols, "2020-01-01"),
            "from_2024": phase_sweep(score, close, openp, amt, cols, "2024-01-01"),
        }
        for tag, sw in out["phase_sweep"].items():
            print("phase sweep", tag, {k: v for k, v in sw.items() if k != "cells"})

    # --- permutation null -------------------------------------------------------------
    idx = pd.to_datetime(close.index)
    hist = close[cols].notna().cumsum()
    elig = ((amt[cols] >= F.MIN_AMT) & (hist >= F.MIN_HIST)).to_numpy()
    base = []
    for c in F.SIGNS:
        f = feats.get(c)
        if f is None:
            continue
        r = f.reindex(index=idx, columns=cols).rank(axis=1, pct=True).to_numpy(dtype=np.float32)
        base.append((F.SIGNS[c], r))
    print("null base factors:", [c for c, _ in [(c, None) for c in F.SIGNS if feats.get(c) is not None]])

    rng = np.random.default_rng(seed)
    t0 = time.time()
    full_null, oos_null = [], []
    for it in range(n_iter):
        parts = []
        for sgn, arr in base:
            a = arr.copy()
            for i in range(a.shape[0]):
                rng.shuffle(a[i])
            parts.append(sgn * a)
        comp = sum(parts) / len(parts)
        sc = pd.DataFrame(np.where(elig, comp, np.nan), index=idx, columns=cols)
        s2, _, _ = fast_next_open(sc, close[cols], openp[cols], REBAL)
        if len(s2) < 50:
            continue
        ef, _, _ = _excess(s2, ew)
        eo, _, _ = _excess(s2[s2.index >= OOS], oos_ew)
        if ef is not None:
            full_null.append(ef)
        if eo is not None:
            oos_null.append(eo)
        if (it + 1) % 25 == 0:
            print("  null %d/%d  %.0fs" % (it + 1, n_iter, time.time() - t0), flush=True)

    def pvalue(arr, real):
        arr = np.asarray(arr, dtype=float)
        return float((1 + int(np.sum(arr >= real))) / (1 + len(arr)))

    full_null = np.array(full_null)
    oos_null = np.array(oos_null)
    out["null"].update({
        "full_excess_null": {
            "n": int(full_null.size), "mean_pp": round(float(full_null.mean()), 2),
            "p95_pp": round(float(np.percentile(full_null, 95)), 2),
            "max_pp": round(float(full_null.max()), 2),
            "real_pp": round(ex_full, 2), "p_value": round(pvalue(full_null, ex_full), 4),
        },
        "oos_excess_null": {
            "n": int(oos_null.size), "mean_pp": round(float(oos_null.mean()), 2),
            "p95_pp": round(float(np.percentile(oos_null, 95)), 2),
            "max_pp": round(float(oos_null.max()), 2),
            "real_pp": round(ex_oos, 2), "p_value": round(pvalue(oos_null, ex_oos), 4),
        },
    })
    print("null:", out["null"]["full_excess_null"], out["null"]["oos_excess_null"])

    p = os.path.join(PATHS.results_dir, "etf_variants_null_rolling.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved", p)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        main()