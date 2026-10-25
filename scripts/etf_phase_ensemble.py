"""Phase-ensemble book: split the capital across all twenty decision-grid phases.

r1248 measured the phase lottery on the bond-removed composite book: from 2020 all twenty
decision phases beat their own equal weight, but the winner (+12.04pp) sat at the edge of a
17.21pp spread and the 2024 anchor left only 11/20 phases positive (median +1.11pp). The
published number was therefore "best of twenty", not a central tendency.

The honest remedy is not a better phase -- it is to stop choosing one. This module holds all
twenty staggered sub-books at once (1/20 of capital each, sub-books that have not started yet
sit in cash at level 1.0) and reports the resulting single curve against (a) its equal-weight
control and (b) the dispersion of the individual phases.

Leg chain is imported, not re-implemented: `etf_variants_null_rolling.fast_next_open` is the
numpy mirror of `etf_composite_pf.run_next_open` (pinned to 1e-12 on the real panel by that
module's own runtime assertion), so every sub-book pays its own 8bp/side turnover cost at its
own fill open. The ensemble adds no trading of its own -- it is a buy-and-hold package of the
twenty NAV paths, so the aggregate cost is exactly the average of the parts.

Not a verdict: exploratory, no ledger booking, no preregistration.
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
from scripts.etf_asset_class import classify  # noqa: E402

SPAN = 20
ANCHOR = "2020-01-01"
OOS = pd.Timestamp("2024-01-01")
EW_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "results", "etf_phase_ensemble.json")


def mean_curve(curves):
    """Equal-capital package of NAV paths.

    Sub-books start on different bars (that is the point of a phase shift), so a missing
    leading value means "not yet funded", i.e. that slice of the capital is in cash at 1.0.
    Averaging over the *funded* curve set (fillna(1.0) before the mean) keeps every bar's
    weights summing to one instead of silently re-weighting into the books that started early.
    """
    if not curves:
        return pd.Series(dtype=float)
    df = pd.concat(curves, axis=1)
    df = df.sort_index().ffill().fillna(1.0)
    return df.mean(axis=1)


def per_year(ser):
    r = ser.pct_change().dropna()
    out = {}
    for y in sorted(set(r.index.year)):
        sub = r[r.index.year == y]
        out[str(y)] = round(float((1.0 + sub).prod() - 1.0) * 100.0, 2)
    return out


def build(score, close, openp, amt, cols, span=SPAN, anchor=ANCHOR):
    idx = pd.to_datetime(close.index)
    pos = [i for i, d in enumerate(idx) if d >= pd.Timestamp(anchor)]
    curves, cells = [], []
    for k in range(min(span, max(0, len(pos) - 300))):
        start = idx[pos[k]]
        ser, turn, _gap = V.fast_next_open(score, close[cols], openp[cols], V.REBAL,
                                           start=str(start.date()))
        if ser is None or len(ser) < 30:
            continue
        curves.append(ser)
        m = F.metrics(ser, "phase-%02d" % k)
        cells.append({"phase": k, "start": str(start.date()), "cagr_pct": round(m["cagr"] * 100, 2),
                      "sharpe": m["sharpe"], "maxdd_pct": round(m["maxdd"] * 100, 2),
                      "turnover_per_rebal": round(turn, 3)})
    return mean_curve(curves), cells


def _dispersion(cells, key):
    v = np.array([c[key] for c in cells if key in c], dtype=float)
    if not v.size:
        return None
    return {"min": round(float(v.min()), 2), "median": round(float(np.median(v)), 2),
            "max": round(float(v.max()), 2), "spread": round(float(v.max() - v.min()), 2),
            "n": int(v.size)}


def _row(label, ser, ew, cells):
    m = F.metrics(ser, label)
    oos = ser[ser.index >= OOS]
    mo = F.metrics(oos, label + ":oos")
    eo = ew[ew.index >= OOS] if ew is not None else None
    meo = F.metrics(eo, label + ":oos:ew") if eo is not None else None
    row = {
        "full": {"book": m, "ew": F.metrics(ew, label + ":ew") if ew is not None else None},
        "oos_2024": {"book": mo, "ew": meo},
        "per_year_pct": per_year(ser),
        "turnover_note": "each sub-book pays its own cost; the package trades nothing itself",
    }
    if ew is not None:
        row["full"]["excess_pp"] = round((m["cagr"] - F.metrics(ew, "x")["cagr"]) * 100, 2)
    if meo is not None and "cagr" in meo:
        row["oos_2024"]["excess_pp"] = round((mo["cagr"] - meo["cagr"]) * 100, 2)
    return row


def selftest():
    ok = 0
    total = 0

    def chk(name, cond):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("SELFTEST FAIL:", name)

    a = pd.Series({pd.Timestamp("2020-01-01"): 1.0, pd.Timestamp("2020-01-02"): 1.10,
                   pd.Timestamp("2020-01-03"): 1.20})
    b = pd.Series({pd.Timestamp("2020-01-02"): 1.0, pd.Timestamp("2020-01-03"): 1.05})
    ens = mean_curve([a, b])
    chk("staggered-start cash fill: day1 = 1.0",
        abs(ens.loc[pd.Timestamp("2020-01-01")] - 1.0) < 1e-12)
    chk("staggered-start cash fill: day2 = 1.05",
        abs(ens.loc[pd.Timestamp("2020-01-02")] - 1.05) < 1e-12)
    chk("staggered-start cash fill: day3 = 1.125",
        abs(ens.loc[pd.Timestamp("2020-01-03")] - 1.125) < 1e-12)
    chk("single sub-book reproduces itself", np.max(np.abs(mean_curve([a]) - a)) < 1e-12)
    chk("identical sub-books average to themselves",
        np.max(np.abs(mean_curve([a, a]) - a)) < 1e-12)
    # a package can never leave the envelope of its parts
    c = pd.Series({pd.Timestamp("2020-01-01"): 1.0, pd.Timestamp("2020-01-02"): 0.90,
                   pd.Timestamp("2020-01-03"): 0.95})
    mix = mean_curve([a, c])
    lo = pd.concat([a, c], axis=1).min(axis=1)
    hi = pd.concat([a, c], axis=1).max(axis=1)
    chk("package stays inside the min/max envelope",
        bool(((mix >= lo - 1e-12) & (mix <= hi + 1e-12)).all()))
    py = per_year(pd.Series({pd.Timestamp("2021-12-31"): 1.0, pd.Timestamp("2022-01-03"): 1.10,
                            pd.Timestamp("2022-12-30"): 1.21}))
    chk("per_year compounds within the year", py.get("2022") == 21.0)
    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()

    t0 = time.time()
    close, openp, amt, feats = F.build_panel()
    classes = pd.Series(classify(list(close.columns)))
    bond_removed = [c for c in close.columns if classes[c] in V.KEEP]
    print("panel %s bars=%d cols=%d bond_removed=%d (%.1fs)"
          % (close.index[0].date(), close.shape[0], close.shape[1], len(bond_removed),
             time.time() - t0))

    out = {
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "generated": pd.Timestamp.now().isoformat(timespec="seconds"),
        "basis": "next-open fill per sub-book (decision at close t, fill at open t+1), 8bp/side "
                 "on each sub-book's own turnover; the ensemble is a buy-and-hold package of "
                 "the twenty NAV paths (unfunded sub-books sit in cash at 1.0)",
        "anchor": ANCHOR, "span_phases": SPAN, "rebal": V.REBAL, "n_hold": F.N_HOLD,
        "universes": {},
        "question": "does holding all twenty decision phases at once remove the phase lottery "
                    "without killing the excess?",
        "caveats": [
            "survivorship: the on-disk panel holds ETFs that still exist",
            "the control is equal-weight on the same subset (close basis, as published)",
            "exploratory: no preregistration, no verdict, no ledger booking",
            "sub-books are equally funded and never rebalanced back to 1/20 -- drift is left in",
        ],
    }

    for name, cols in (("bond_removed", bond_removed), ("all_classes", list(close.columns))):
        t1 = time.time()
        score = F.build_score(close[cols], amt[cols], feats)
        ens, cells = build(score, close, openp, amt, cols)
        ew = F.run_ew(close[cols], amt[cols], V.REBAL, start=ANCHOR)
        row = _row(name, ens, ew, cells)
        row["phases"] = cells
        row["phase_dispersion"] = {
            "cagr_pct": _dispersion(cells, "cagr_pct"),
            "sharpe": _dispersion(cells, "sharpe"),
            "maxdd_pct": _dispersion(cells, "maxdd_pct"),
        }
        # where does the package land inside its own parts?
        book_cagr = row["full"]["book"]["cagr"] * 100
        beats = sum(1 for c in cells if c["cagr_pct"] < book_cagr)
        row["ensemble_rank_among_phases"] = "%d/%d better than" % (beats, len(cells))
        med = row["phase_dispersion"]["cagr_pct"]["median"] if cells else None
        row["ensemble_minus_median_phase_pp"] = (
            round(book_cagr - med, 2) if med is not None else None)
        row["secs"] = round(time.time() - t1, 1)
        out["universes"][name] = row
        print("%s: package full %.2f%% (ew %.2f%%) | oos %.2f%% (ew %s) | phase median %.2f%% "
              "spread %.2f | rank %s | %.0fs"
              % (name, book_cagr, row["full"]["ew"]["cagr"] * 100,
                 row["oos_2024"]["book"]["cagr"] * 100,
                 row["oos_2024"]["ew"]["cagr"] * 100 if row["oos_2024"]["ew"] else "n/a",
                 med if med is not None else float("nan"),
                 row["phase_dispersion"]["cagr_pct"]["spread"] if cells else float("nan"),
                 row["ensemble_rank_among_phases"], row["secs"]))

    with open(EW_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("wrote", EW_PATH, "(%.0fs total)" % (time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())