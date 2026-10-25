"""Phase-ensemble across rebalance cadences: does "hold all phases" survive R=10/20/40?

r1249 showed the twenty-phase package removes the phase lottery at R=20 (package 9.03%/yr vs
equal weight 2.26%, OOS 13.20% vs 9.04%) but the open question declared there was whether the
package is an artefact of one cadence. This module holds *R* staggered sub-books (one per bar of
the decision grid, 1/R capital each) for R in {10, 20, 40} and reports each package against
(a) its own equal-weight control at the same cadence and (b) the dispersion of its own phases.

Construction notes:
  - span == R. For cadence R the decision grid has exactly R phases (start bar k = 0..R-1),
    so a full-cycle package needs R offsets; using a fixed 20 offsets at R=40 would cover only
    half the grid and quietly reintroduce a phase choice.
  - every sub-book pays its own 8bp/side turnover at its own fill open (engine imported from
    etf_variants_null_rolling.fast_next_open, pinned to the reference implementation 1e-12);
    the package itself never trades, so its cost is the average of the parts.
  - bc the package trades nothing, a faster cadence shows up as higher per-sub-book turnover,
    not as package churn -- the turnover column is per-sub-book, not per-package.

Exploratory: no preregistration, no verdict, no ledger booking.
"""

import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import etf_composite_pf as F  # noqa: E402
from scripts import etf_variants_null_rolling as V  # noqa: E402
from scripts import etf_phase_ensemble as P  # noqa: E402
from scripts.etf_asset_class import classify  # noqa: E402

ANCHOR = "2020-01-01"
OOS = pd.Timestamp("2024-01-01")
CADENCES = (10, 20, 40)
OUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "results", "etf_phase_cadence.json")


def phase_starts(idx, anchor=ANCHOR, span=20):
    """The `span` decision-grid phases of a cadence-`span` book, as ISO dates."""
    pos = [i for i, d in enumerate(idx) if d >= pd.Timestamp(anchor)]
    return [pd.Timestamp(idx[pos[k]]) for k in range(min(span, len(pos)))]


def build(score, close, openp, cols, rebal, anchor=ANCHOR):
    idx = pd.to_datetime(close.index)
    starts = phase_starts(idx, anchor, rebal)
    curves, cells = [], []
    for k, start in enumerate(starts):
        ser, turn, _gap = V.fast_next_open(score, close[cols], openp[cols], rebal,
                                           start=str(start.date()))
        if ser is None or len(ser) < 30:
            continue
        curves.append(ser)
        m = F.metrics(ser, "phase-%02d" % k)
        cells.append({"phase": k, "start": str(start.date()),
                      "cagr_pct": round(m["cagr"] * 100, 2), "sharpe": m["sharpe"],
                      "maxdd_pct": round(m["maxdd"] * 100, 2),
                      "turnover_per_rebal": round(turn, 3)})
    return P.mean_curve(curves), cells, starts


def _dispersion(cells, key):
    v = np.array([c[key] for c in cells if key in c], dtype=float)
    if not v.size:
        return None
    return {"min": round(float(v.min()), 2), "median": round(float(np.median(v)), 2),
            "max": round(float(v.max()), 2), "spread": round(float(v.max() - v.min()), 2),
            "n": int(v.size)}


def _block(ser, ew=None):
    m = F.metrics(ser, "book")
    oos = ser[ser.index >= OOS] if ser is not None and len(ser) else None
    out = {"book": m, "per_year_pct": P.per_year(ser) if ser is not None else {}}
    if oos is not None and len(oos) > 20:
        out["oos_2024"] = F.metrics(oos, "book:oos")
    if ew is not None and len(ew):
        out["ew"] = F.metrics(ew, "ew")
        out["excess_pp"] = round((m["cagr"] - out["ew"]["cagr"]) * 100, 2)
        eo = ew[ew.index >= OOS]
        if len(eo) > 20:
            out["oos_2024_ew"] = F.metrics(eo, "ew:oos")
            out["oos_excess_pp"] = round((out["oos_2024"]["cagr"] -
                                          out["oos_2024_ew"]["cagr"]) * 100, 2)
    return out


def selftest():
    ok = total = 0

    def chk(name, cond):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("SELFTEST FAIL:", name)

    idx = pd.bdate_range("2020-01-01", periods=200)
    for r in CADENCES:
        st = phase_starts(idx, ANCHOR, r)
        chk("R=%d yields %d distinct phases" % (r, r), len(st) == r and len(set(st)) == r)
        gaps = {(st[i + 1] - st[i]).days for i in range(len(st) - 1)}
        chk("R=%d phases are one bar apart" % r, gaps <= {1, 3})  # weekend tolerance
        chk("R=%d last phase < R bars after first" % r,
            (st[-1] - st[0]).days <= 3 * r)
    # the cash-fill package law is inherited, not re-implemented: re-pin it here
    a = pd.Series({pd.Timestamp("2020-01-01"): 1.0, pd.Timestamp("2020-01-02"): 1.10})
    b = pd.Series({pd.Timestamp("2020-01-02"): 1.0, pd.Timestamp("2020-01-03"): 1.05})
    ens = P.mean_curve([a, b])
    chk("staggered start sits in cash at 1.0", abs(ens.iloc[0] - 1.0) < 1e-12)
    chk("package averages funded books", abs(ens.iloc[-1] - (1.10 + 1.05) / 2) < 1e-12)
    chk("empty package is empty", P.mean_curve([]).empty)
    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()

    t0 = time.time()
    close, openp, amt, feats = F.build_panel()
    classes = pd.Series(classify(list(close.columns)))
    cols = [c for c in close.columns if classes[c] in V.KEEP]
    print("panel %s bars=%d cols=%d bond_removed=%d (%.1fs)"
          % (close.index[0].date(), close.shape[0], close.shape[1], len(cols),
             time.time() - t0), flush=True)

    out = {
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "generated": pd.Timestamp.now().isoformat(timespec="seconds"),
        "anchor": ANCHOR,
        "universe": "bond_removed (equity/commodity/crossborder), %d instruments" % len(cols),
        "basis": "next-open fill (decide at close t, fill at open t+1), 8bp/side per sub-book "
                 "on its own turnover; package = buy-and-hold mean of the R phase NAVs, "
                 "unfunded sub-books in cash at 1.0",
        "question": "is the R=20 phase-ensemble excess a cadence artefact?",
        "caveats": [
            "survivorship: on-disk panel holds ETFs that still exist",
            "control = equal weight on the same subset (close basis, as published)",
            "exploratory: no preregistration, no verdict, no ledger booking",
            "R=10 sub-books trade twice as often as R=40 -- turnover is per sub-book",
        ],
        "cadences": {},
    }

    score = F.build_score(close[cols], amt[cols], feats)
    for r in CADENCES:
        t1 = time.time()
        ens, cells, starts = build(score, close, openp, cols, r)
        ew = F.run_ew(close[cols], amt[cols], r, start=ANCHOR)
        row = _block(ens, ew)
        row["phases"] = cells
        row["phase_dispersion"] = {k: _dispersion(cells, k) for k in
                                  ("cagr_pct", "sharpe", "maxdd_pct")}
        book = row["book"]["cagr"] * 100
        med = row["phase_dispersion"]["cagr_pct"]["median"] if cells else None
        row["beats_phases"] = "%d/%d" % (sum(1 for c in cells if c["cagr_pct"] < book),
                                         len(cells))
        row["ensemble_minus_median_phase_pp"] = round(book - med, 2) if med is not None else None
        row["mean_turnover_per_rebal"] = (round(float(np.mean([c["turnover_per_rebal"]
                                                               for c in cells])), 3)
                                          if cells else None)
        row["secs"] = round(time.time() - t1, 1)
        out["cadences"]["R%d" % r] = row
        print("R%-3d package full %.2f%% (ew %.2f%%) | oos %.2f%% (ew %s) | phases %d "
              "median %.2f%% spread %.2f | beats %s | turn %.3f | %.0fs"
              % (r, book, row["ew"]["cagr"] * 100,
                 row["oos_2024"]["cagr"] * 100,
                 round(row["oos_2024_ew"]["cagr"] * 100, 2) if "oos_2024_ew" in row else "n/a",
                 len(cells), med if med is not None else float("nan"),
                 row["phase_dispersion"]["cagr_pct"]["spread"] if cells else float("nan"),
                 row["beats_phases"], row["mean_turnover_per_rebal"] or float("nan"),
                 row["secs"]), flush=True)

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("wrote", OUT_PATH, "(%.0fs total)" % (time.time() - t0), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())