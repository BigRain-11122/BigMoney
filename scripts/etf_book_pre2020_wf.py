"""Walk-forward cell selection on the pre-2020 window.

r1308 reconciled the two readings of 2015-2019 and closed the ladder, but every rung of
that ladder was a FIXED cell chosen with hindsight.  The shipped deployment rule is not a
fixed cell: r1256 re-picks (N, R) every year on trailing Sharpe.  So the open question the
ladder cannot answer is whether the rule -- not the cell -- would have survived the window
in which the published cell loses.

Three arms, one universe, one window, one execution rule (decision at close t, fill at
open t+1, 10bp/side on the weight turned over, `start` passed to the engine so the 120-bar
history counter is not reset):

  wf        pick the cell with the best trailing Sharpe before each year, earn that year
            on the 8%-target overlay curve of the picked cell
  fixed12   the production width (N12) with the same overlay -- r1308 rung 4
  ew        equal weight of the same universe

Selection is made on the RAW curve (the shipped rule, etf_walkforward_capacity.py) and
earned on the overlay curve, because the overlay is a sizing rule applied to whatever
book you hold, not a property of the cell.

Reuse, not re-implementation: panel from etf_book_production.prep_panel, U_pre mask and
truncate from etf_book_pre2020, engines from etf_composite_pf / etf_robust_pf.

  python scripts/etf_book_pre2020_wf.py run
  python scripts/etf_book_pre2020_wf.py --selftest
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_book_pre2020 as W
import etf_book_production as P
import etf_robust_pf as R

OUT = os.path.join(E.PATHS.results_dir, "etf_book_pre2020_wf.json")
DEC = os.path.join(E.PATHS.results_dir, "etf_book_window_decomp.json")
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTROL_TOL_PP = 0.5
START = "2015-01-01"
END = "2019-12-31"
REBAL = 20
COST = 0.0010
VT = 0.08
CELLS = [(3, 10), (3, 20), (3, 40), (5, 10), (5, 20), (5, 40), (8, 10), (8, 20), (8, 40)]
FIXED = (12, 20)
MIN_TRAIL = 120


def _sharpe(ser):
    r = ser.pct_change().dropna()
    if len(r) < 20:
        return np.nan
    sd = r.std()
    return float(r.mean() / sd * np.sqrt(252)) if sd > 0 else np.nan


def pick_cell(curves, year):
    """Best trailing Sharpe strictly before Jan 1 of `year`; FIXED when nothing qualifies."""
    edge = pd.Timestamp("%d-01-01" % year)
    best, sel = -9e9, None
    for cfg, ser in curves.items():
        trail = ser[ser.index < edge]
        if len(trail) < MIN_TRAIL:
            continue
        s = _sharpe(trail)
        if np.isfinite(s) and s > best:
            best, sel = s, cfg
    if sel is None:
        return FIXED, None
    return sel, round(best, 3)


def _year_bounds(ser, year):
    """Return (i0, i1): first bar on/after Jan 1 Y, first bar on/after Jan 1 Y+1 (or last).

    Year returns must share their boundary bar, otherwise compounding the years drops the
    move between the last bar of December and the first bar of January and the chain does
    not equal the same curve's window return.
    """
    a = pd.Timestamp("%d-01-01" % year)
    b = pd.Timestamp("%d-01-01" % (year + 1))
    i0 = int(ser.index.searchsorted(a))
    i1 = int(ser.index.searchsorted(b))
    if i0 >= len(ser) - 1:
        return None, None
    i1 = min(i1, len(ser) - 1)
    if i1 <= i0:
        return None, None
    return i0, i1


def year_return(ser, year):
    i0, i1 = _year_bounds(ser, year)
    if i0 is None:
        return None
    return float(ser.iloc[i1] / ser.iloc[i0] - 1.0)


def wf_chain(sel_curves, earn_curves, years):
    """Chain yearly returns; each year's cell chosen from sel_curves, earned from earn_curves."""
    rows, level = [], 1.0
    for y in years:
        cfg, trail_sr = pick_cell(sel_curves, y)
        ret = year_return(earn_curves.get(cfg) if cfg in earn_curves else sel_curves[cfg], y)
        if ret is None:
            rows.append({"year": y, "picked": "N%d_R%d" % cfg, "trailing_sharpe": trail_sr,
                         "return": None})
            continue
        level *= (1.0 + ret)
        rows.append({"year": y, "picked": "N%d_R%d" % cfg, "trailing_sharpe": trail_sr,
                     "return": round(ret, 4)})
    return rows, level


def window_stats(ser, start, end):
    sl = ser[(ser.index >= pd.Timestamp(start)) & (ser.index <= pd.Timestamp(end))]
    m = E.metrics(sl, "arm")
    return {k: m.get(k) for k in ("cagr", "sharpe", "maxdd", "vol", "years")}


def run():
    # panel from the production gate (repair + class filter); factor frames from the raw
    # panel, reindexed to the pre-2020 universe exactly as r1308's price_arm does -- the
    # score must be rebuilt on the 193 names, not subset after ranking 1,499.
    close, openp, amt, _score, cls, n_flip = P.prep_panel()
    _c0, _o0, _a0, feats = E.build_panel()
    pre = W.universe_pre(close)
    cols = [c for c in close.columns if c in set(pre)]
    c, o, a, f = W.truncate(
        [close[cols], openp[cols], amt[cols],
         {k: v.reindex(columns=cols) for k, v in feats.items() if hasattr(v, "columns")}],
        None, END)
    score = E.build_score(c, a, f)
    print("universe U_pre=%d cols=%d panel=%s last=%s flips=%d"
          % (len(pre), len(cols), c.shape, c.index[-1].date(), n_flip), flush=True)

    raw, vtc, cell_stats = {}, {}, {}
    for (n, r) in CELLS + [FIXED]:
        ser, _t, _g = E.run_next_open(c, o, a, f, rebal=r, n_hold=n, cost=COST,
                                      start=START, score=score)
        raw[(n, r)] = ser
        vser, _turn = R.open_to_open_equity(c, o, a, score, r, n, COST,
                                            vol_target=VT, start=START)
        vtc[(n, r)] = vser
        m = E.metrics(vser, "N%d_R%d" % (n, r))
        cell_stats["N%d_R%d" % (n, r)] = {k: m.get(k) for k in
                                          ("cagr", "sharpe", "maxdd", "vol")}
        print("cell N%2d R%2d raw %7.2f%%  vt %7.2f%% SR %.3f dd %6.2f%%"
              % (n, r, (E.metrics(ser, "x").get("cagr") or 0) * 100,
                 (m.get("cagr") or 0) * 100, m.get("sharpe") or 0,
                 (m.get("maxdd") or 0) * 100), flush=True)

    ew = E.run_ew(c, a, REBAL, start=START)

    years = list(range(2016, 2020))
    wf_rows, wf_level = wf_chain(raw, vtc, years)
    fixed_rows, fixed_level = wf_chain({FIXED: raw[FIXED]}, vtc, years)
    ew_rows, ew_level = wf_chain({FIXED: ew}, {FIXED: ew}, years)
    n = len([r for r in wf_rows if r["return"] is not None])
    to_cagr = (lambda lv: lv ** (1.0 / n) - 1.0 if n else None)
    print("years %d  WF %.2f%%  fixed N12 %.2f%%  EW %.2f%%"
          % (n, to_cagr(wf_level) * 100, to_cagr(fixed_level) * 100,
             to_cagr(ew_level) * 100), flush=True)
    for row in wf_rows:
        print("WF %d picked %s (trail SR %s) -> %s"
              % (row["year"], row["picked"], row["trailing_sharpe"], row["return"]), flush=True)

    out = {
        "schema": "etf_book_pre2020_wf/v1",
        "question": ("the shipped deployment rule re-picks (N,R) every year on trailing "
                     "Sharpe -- does the RULE survive 2016-2019, or only the hindsight cell?"),
        "engine": ("etf_composite_pf.run_next_open (selection curve) / "
                   "etf_robust_pf.open_to_open_equity (earned curve, 8% de-lever-only overlay)"),
        "window": [START, END],
        "earn_years": years,
        "universe": {"U_pre": len(pre), "cols": len(cols), "flips_repaired": n_flip},
        "cost_bp_per_side": COST * 1e4,
        "rebal": REBAL,
        "vol_target": VT,
        "cells": ["N%d_R%d" % k for k in CELLS],
        "cells_vt": {k: cell_stats[k] for k in sorted(cell_stats)},
        "cell_dispersion": _dispersion([cell_stats["N%d_R%d" % k].get("cagr")
                                        for k in CELLS]),
        "wf": {"rows": wf_rows, "chained_cagr": to_cagr(wf_level),
               "picks": [r["picked"] for r in wf_rows]},
        "fixed_n12": {"chained_cagr": to_cagr(fixed_level)},
        "ew": {"chained_cagr": to_cagr(ew_level)},
        "chained_returns": {
            "wf": round(wf_level - 1.0, 4),
            "fixed_n12": round(fixed_level - 1.0, 4),
            "ew": round(ew_level - 1.0, 4),
        },
        "full_window_arm_stats": {
            "wf_rule_full_window": window_stats(_stitch(vtc, wf_rows, years), START, END),
            "fixed_n12_vt": window_stats(vtc[FIXED], "2016-01-01", END),
            "ew": window_stats(ew, "2016-01-01", END),
            "fixed_n12_raw": window_stats(raw[FIXED], "2016-01-01", END),
        },
        "round": "r1309",
        "generated": pd.Timestamp.now("UTC").isoformat(),
    }
    out["control"] = _control(raw[FIXED], vtc[FIXED])
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print("control:", json.dumps(out["control"], sort_keys=True), flush=True)
    print("wrote", OUT, flush=True)
    return out


def _dispersion(vals):
    """Spread of the nine overlay cells: a selector cannot beat a draw it cannot separate."""
    v = np.array([x for x in vals if x is not None and np.isfinite(x)], dtype=float)
    if len(v) == 0:
        return {}
    return {"n": int(len(v)), "mean": round(float(v.mean()), 4),
            "sd": round(float(v.std(ddof=0)), 4), "min": round(float(v.min()), 4),
            "max": round(float(v.max()), 4), "positive": int((v > 0).sum())}


def _control(raw_ser, vt_ser):
    """Re-price r1308's rungs 3 and 4 through this script's own call path.

    The delta must be ~0 before any walk-forward number is quotable: if the fixed N12 arms
    do not reproduce the published ladder, the comparison arm is not the published arm and
    every delta below is a code difference rather than a selection result.
    """
    out = {"published": os.path.relpath(DEC, _REPO_ROOT) if os.path.exists(DEC) else None}
    try:
        with open(DEC, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        rungs = doc.get("rungs") or []
        pub_raw = next((r for r in rungs
                        if r.get("n_hold") == FIXED[0] and not r.get("vol_target")), None)
        pub_vt = next((r for r in rungs
                       if r.get("n_hold") == FIXED[0] and r.get("vol_target")), None)
        got_raw = E.metrics(raw_ser, "ctrl_raw").get("cagr")
        got_vt = E.metrics(vt_ser, "ctrl_vt").get("cagr")
        out["r3_n12_raw"] = {"published": pub_raw.get("book_cagr") if pub_raw else None,
                             "recomputed": got_raw}
        out["r4_n12_vt"] = {"published": pub_vt.get("book_cagr") if pub_vt else None,
                            "recomputed": got_vt}
        for k in ("r3_n12_raw", "r4_n12_vt"):
            p, g = out[k]["published"], out[k]["recomputed"]
            out[k]["delta_pp"] = (round((g - p) * 100, 2)
                                  if p is not None and g is not None else None)
            out[k]["ok"] = (out[k]["delta_pp"] is not None
                            and abs(out[k]["delta_pp"]) <= CONTROL_TOL_PP)
        out["tolerance_pp"] = CONTROL_TOL_PP
        out["verdict"] = ("control arms reproduce the published ladder"
                          if all(out[k]["ok"] for k in ("r3_n12_raw", "r4_n12_vt"))
                          else "CONTROL MISMATCH -- deltas below are not quotable")
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        out["error"] = "%s: %s" % (type(exc).__name__, exc)
        out["verdict"] = "control unavailable"
    return out


def _stitch(earn_curves, rows, years):
    """Build one continuous curve from the yearly picks (for window stats)."""
    parts, level = [], 1.0
    for row in rows:
        if row["return"] is None:
            continue
        cfg = tuple(int(x) for x in row["picked"].replace("N", "").split("_R"))
        ser = earn_curves[cfg]
        i0, i1 = _year_bounds(ser, row["year"])
        if i0 is None:
            continue
        seg = ser.iloc[i0:i1 + 1]
        scaled = seg / seg.iloc[0] * level
        parts.append(scaled if not parts else scaled.iloc[1:])
        level = scaled.iloc[-1]
    if not parts:
        return pd.Series(dtype=float)
    return pd.concat(parts)


def fixture():
    idx = pd.date_range("2015-01-02", periods=1100, freq="B")
    curves = {}
    for (n, r) in [(3, 10), (3, 20), (5, 10), (5, 20), (12, 20)]:
        # every cell drifts up with deterministic wobble -- a constant return has zero
        # dispersion and therefore an undefined Sharpe
        step = 0.0002 * (13 - n) * (30 - r) / 30.0
        wob = 0.004 * (n / 12.0) * np.sin(np.arange(len(idx)) * 0.37 + n)
        rates = np.full(len(idx), step) + wob
        rates[idx >= pd.Timestamp("2017-01-01")] *= 1.5
        curves[(n, r)] = pd.Series(np.cumprod(1.0 + rates), index=idx)
    return idx, curves


def chk(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ((" :: " + detail) if detail else ""),
          flush=True)
    return bool(cond)


def selftest():
    idx, curves = fixture()
    ok = []

    # L1 the pick is the highest trailing Sharpe, not the highest level
    sel, sr = pick_cell(curves, 2017)
    trailing = {k: round(_sharpe(v[v.index < pd.Timestamp("2017-01-01")]), 6)
                for k, v in curves.items()}
    best = max(trailing, key=lambda k: trailing[k])
    ok.append(chk("L1 pick = best trailing Sharpe", sel == best,
                  "pick=%s best=%s sr=%s" % (sel, best, sr)))

    # L2 no lookahead: the pick for year Y is unchanged when data on/after Jan 1 Y is removed
    cut = {k: v[v.index < pd.Timestamp("2018-01-01")] for k, v in curves.items()}
    ok.append(chk("L2 no lookahead in selection", pick_cell(curves, 2018)[0] == pick_cell(cut, 2018)[0]))

    # L3 too little history = FIXED fallback, not a crash
    short = {k: v[v.index < pd.Timestamp("2015-04-01")] for k, v in curves.items()}
    ok.append(chk("L3 fallback to FIXED when no cell has %d trailing bars" % MIN_TRAIL,
                  pick_cell(short, 2016)[0] == FIXED))

    # L4 chained level == product of the yearly returns it reports
    rows, lvl = wf_chain(curves, curves, [2016, 2017, 2018, 2019])
    prod = 1.0
    for r in rows:
        if r["return"] is not None:
            prod *= 1.0 + r["return"]
    ok.append(chk("L4 chained level equals the product of reported years",
                  abs(lvl - prod) < 1e-4, "lvl=%.10f prod=%.10f" % (lvl, prod)))

    # L5 a constant pick chains to exactly that curve's window return
    single = {(5, 20): curves[(5, 20)]}
    rows2, lvl2 = wf_chain(single, single, [2016, 2017, 2018, 2019])
    ser = curves[(5, 20)]
    whole = float(ser[ser.index < pd.Timestamp("2020-01-01")].iloc[-1] /
                  ser[ser.index >= pd.Timestamp("2016-01-01")].iloc[0] - 1.0)
    ok.append(chk("L5 constant-pick chain reproduces the curve window return",
                  abs(lvl2 - 1.0 - whole) < 1e-9,
                  "chain=%.8f curve=%.8f" % (lvl2 - 1.0, whole)))

    # L6 the earn curve is honoured: same picks, different earn curves -> different chain
    flipped = {k: v.iloc[::-1].set_axis(v.index) for k, v in curves.items()}
    _r3, lvl3 = wf_chain(curves, flipped, [2016, 2017, 2018, 2019])
    ok.append(chk("L6 earns from the earn curve, not the selection curve",
                  abs(lvl3 - lvl) > 1e-6, "sel-chain=%.6f alt=%.6f" % (lvl, lvl3)))

    # L7 year_return boundary is [Jan1 Y, Jan1 Y+1] -- both boundaries inclusive so that
    # compounding consecutive years reproduces the curve
    s = pd.Series([1.0, 1.1, 1.2, 1.3], index=pd.to_datetime(
        ["2017-01-03", "2017-12-29", "2018-01-02", "2018-06-01"]))
    ok.append(chk("L7 year slice shares its boundary bar", abs(year_return(s, 2017) - 0.2) < 1e-12,
                  "got=%s" % year_return(s, 2017)))

    # L8 the stitch reproduces the chain level at the last bar
    stitched = _stitch(curves, rows, [2016, 2017, 2018, 2019])
    ok.append(chk("L8 stitched curve ends at the chained level",
                  len(stitched) > 0 and abs(stitched.iloc[-1] - lvl) < 1e-6,
                  "end=%s chain=%s" % (stitched.iloc[-1] if len(stitched) else None, lvl)))

    print("%d/%d PASS" % (sum(1 for x in ok if x), len(ok)))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    run()