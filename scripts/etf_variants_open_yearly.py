"""ETF composite factor book -- the two surviving sleeve subsets, on an honest fill base,
with a per-year table (r1247 bm-c).

Why this module exists
----------------------
r1243 decomposed the published 9.04%/yr book by asset class; r1244 re-ran four sleeve
subsets and found that the survivors are `bond_removed` (OOS 20.81%) and `equity_gold_only`
(OOS 16.02%), i.e. the mechanism is a switch between equity ETFs and gold, not a
cross-asset rotation. Both notes carried the same two open items:

  1. every subset number was close-to-close from the decision close (no open-fill model),
     while r1245 showed that for the all-class book the next-open base takes 8.57% out of
     9.04%/yr -- so the subset headline could be a close-basis artefact too;
  2. 2024+ is 2.8 years of one regime (equity up, gold up). If a variant's OOS excess is
     one year, the book is a regime bet, not a factor.

This module answers both in one pass: it re-runs the variants on the next-open base and
prints a per-year book-vs-own-equal-weight table.

Basis: signal at close t -> filled at the open of t+1; overnight leg to the OLD book,
weight change charged at the fill open, NEW book earns open->close on the fill day.
Cost 8bp/side on turnover. Universe: on-disk panel (survivorship applies). Exploratory,
not a preregistered judgement -- no verdict, no ledger booking.

Usage:
  python scripts/etf_variants_open_yearly.py
  python scripts/etf_variants_open_yearly.py --selftest
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd

from config import PATHS
from scripts import etf_composite_pf as F
from scripts.etf_asset_class import classify

# Variant name -> asset classes kept (None = whole panel, the published book).
VARIANTS = {
    "all_classes": None,
    "bond_removed": ("equity", "commodity", "crossborder"),
    "equity_gold_only": ("equity", "commodity"),
    "crossborder_removed": ("equity", "bond", "commodity"),
}
REBAL = 20                     # the published cadence
FULL_YEAR_BARS = 235           # a full A-share year is ~242 bars; below this = partial cell
IS_END = pd.Timestamp("2023-12-31")
OOS = pd.Timestamp("2024-01-01")


def yearly(ser):
    """Level-based calendar-year returns: last level of the year / first of the year - 1.

    A cell with fewer than FULL_YEAR_BARS bars is flagged `partial` -- on both ends of the
    span (the current year is still running, and the first year can start late). A partial
    cell is kept, never dropped: it is exactly the kind of cell that flatters a short OOS
    window, so it must stay visible with its bar count.
    """
    ser = ser.dropna()
    out = {}
    for yr, grp in ser.groupby(ser.index.year):
        if len(grp) < 2:
            continue
        lvl = float(grp.iloc[-1]) / float(grp.iloc[0]) - 1.0
        row = {"ret_pct": round(lvl * 100, 2), "bars": int(len(grp))}
        if row["bars"] < FULL_YEAR_BARS:
            row["partial"] = True
        out[int(yr)] = row
    return out


def window_metrics(ser, label):
    rows = []
    for lbl, sl in (("full", ser),
                    ("is_2020_2023", ser[ser.index <= IS_END]),
                    ("oos_2024_plus", ser[ser.index >= OOS])):
        m = F.metrics(sl, "%s_%s" % (label, lbl))
        rows.append(m)
    return rows


def run_variant(close, openp, amt, feats, cols):
    sub_close = close[cols]
    ser, turn, gapfill = F.run_next_open(
        sub_close, openp[cols], amt[cols], feats, REBAL, start="2020-01-01")
    ew = F.run_ew(sub_close, amt[cols], REBAL, start="2020-01-01")
    book_rows = window_metrics(ser, "book")
    ew_rows = window_metrics(ew, "ew")
    wins = {}
    for b, e in zip(book_rows, ew_rows):
        win = b["label"].split("book_", 1)[-1]
        assert win == e["label"].split("ew_", 1)[-1], "window pairing drift: %r/%r" % (
            b["label"], e["label"])
        if "cagr" not in b or "cagr" not in e:
            wins[win] = {"note": "too short", "bars": b.get("bars")}
            continue
        wins[win] = {
            "book_cagr_pct": round(b["cagr"] * 100, 2),
            "ew_cagr_pct": round(e["cagr"] * 100, 2),
            "cagr_pp": round((b["cagr"] - e["cagr"]) * 100, 2),
            "book_sharpe": b["sharpe"],
            "book_maxdd_pct": round(b["maxdd"] * 100, 2),
        }
    yb, ye = yearly(ser), yearly(ew)
    years = {}
    for yr in sorted(set(yb) | set(ye)):
        if yr not in yb or yr not in ye:
            continue
        years[yr] = {
            "book_pct": yb[yr]["ret_pct"],
            "ew_pct": ye[yr]["ret_pct"],
            "excess_pp": round(yb[yr]["ret_pct"] - ye[yr]["ret_pct"], 2),
            "partial": bool(yb[yr].get("partial")),
        }
    pos_years = sum(1 for y in years.values() if y["excess_pp"] > 0)
    return {
        "universe": len(cols),
        "rebalances": None,
        "turnover_per_rebal": round(turn, 3),
        "open_gapfill_cells": int(gapfill),
        "book": book_rows,
        "control": ew_rows,
        "vs_own_ew": wins,
        "by_year": years,
        "years_beating_own_ew": "%d/%d" % (pos_years, len(years)),
    }


def sweep(close, openp, amt, feats, cols, tag):
    """Parameter grid on one subset: is the headline a plateau or a spike?

    Each cell is the next-open book at (N, R) against the equal-weight control rebalanced
    at the same R -- the control moves with R, so a cell is never credited for a cadence
    the control did not have.
    """
    rows = {}
    for rebal in (10, 20, 60):
        ew = F.run_ew(close[cols], amt[cols], rebal, start="2020-01-01")
        ew_full = F.metrics(ew, "ew_full")
        ew_oos = F.metrics(ew[ew.index >= OOS], "ew_oos")
        for n_hold in (3, 5, 8, 10):
            ser, turn, _ = F.run_next_open(close[cols], openp[cols], amt[cols], feats,
                                           rebal, n_hold=n_hold, start="2020-01-01")
            mf = F.metrics(ser, "book_full")
            mo = F.metrics(ser[ser.index >= OOS], "book_oos")
            key = "N%d_R%d" % (n_hold, rebal)
            rows[key] = {
                "n_hold": n_hold, "rebal": rebal,
                "full_cagr_pct": round(mf["cagr"] * 100, 2),
                "full_sharpe": mf["sharpe"],
                "full_maxdd_pct": round(mf["maxdd"] * 100, 2),
                "oos_cagr_pct": round(mo["cagr"] * 100, 2),
                "oos_sharpe": mo["sharpe"],
                "turnover_per_rebal": round(turn, 3),
                "full_excess_pp": round((mf["cagr"] - ew_full["cagr"]) * 100, 2),
                "oos_excess_pp": round((mo["cagr"] - ew_oos["cagr"]) * 100, 2),
            }
            print(tag, key, rows[key])
    return rows


def main():
    close, openp, amt, feats = F.build_panel()
    # classify() must be handed the panel columns explicitly: the decomp module's lookup
    # table is populated inside ITS main(), so importing asset_class alone would silently
    # tag the whole universe "equity" (r1247 first run: four variants byte-identical).
    classes = pd.Series(classify(list(close.columns)))
    print("universe classes:", classes.value_counts().to_dict())

    out = {
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "basis": "next-open fill: decision at close t, fill at open t+1; overnight leg to "
                 "the OLD book, weight change charged at the fill open, NEW book earns "
                 "open->close on the fill day; 8bp/side on turnover",
        "cost_bp_per_side": 8,
        "n_hold": F.N_HOLD,
        "rebal": REBAL,
        "caveats": [
            "survivorship: the on-disk panel holds ETFs that still exist",
            "exploratory analysis, not a preregistered judgement",
            "each subset is ranked and controlled on the SAME columns",
            "subsets are static: the book cannot rotate INTO a removed sleeve",
            "control is equal-weight on the same subset, close basis",
        ],
        "variants": {},
    }

    for name, keep in VARIANTS.items():
        if keep is None:
            cols = list(close.columns)
        else:
            cols = [c for c in close.columns if classes[c] in keep]
        if len(cols) < F.N_HOLD * 4:
            out["variants"][name] = {"skipped": True, "universe": len(cols)}
            print(name, "SKIPPED universe", len(cols))
            continue
        v = run_variant(close, openp, amt, feats, cols)
        out["variants"][name] = v
        print("--- %s (universe %d)" % (name, len(cols)))
        for r in v["book"]:
            print("   ", r)
        print("    vs own EW:", v["vs_own_ew"])
        print("    by year:", v["by_year"], "beat", v["years_beating_own_ew"])

    p = os.path.join(PATHS.results_dir, "etf_variants_open_yearly.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved", p)

    # --- parameter platform test on the only subset that survives every window --------
    if "--sweep" in sys.argv:
        keep = VARIANTS["bond_removed"]
        cols = [c for c in close.columns if classes[c] in keep]
        rows = sweep(close, openp, amt, feats, cols, "bond_removed")
        pos = [k for k, v in rows.items() if v["full_excess_pp"] > 0 and v["oos_excess_pp"] > 0]
        sw = {
            "evidence_cutoff": out["evidence_cutoff"],
            "basis": out["basis"],
            "subset": "bond_removed (equity + commodity + crossborder)",
            "universe": len(cols),
            "caveats": out["caveats"] + [
                "control rebalanced at the same R as the cell it is compared with",
                "single panel start 2020-01-01; no walk-forward, no rolling origin",
            ],
            "cells": rows,
            "cells_beating_control_in_both_windows": "%d/%d" % (len(pos), len(rows)),
            "platform": {
                "full_cagr_pct_min": min(v["full_cagr_pct"] for v in rows.values()),
                "full_cagr_pct_max": max(v["full_cagr_pct"] for v in rows.values()),
                "full_cagr_pct_median": sorted(v["full_cagr_pct"] for v in rows.values())[len(rows) // 2],
                "oos_excess_pp_min": min(v["oos_excess_pp"] for v in rows.values()),
                "oos_excess_pp_max": max(v["oos_excess_pp"] for v in rows.values()),
            },
        }
        sp = os.path.join(PATHS.results_dir, "etf_variants_sweep.json")
        with open(sp, "w", encoding="utf-8") as f:
            json.dump(sw, f, ensure_ascii=False, indent=1)
        print("saved", sp)
        print("platform:", sw["platform"], "both-window winners:", sw["cells_beating_control_in_both_windows"])





def selftest():
    """Yearly aggregation and window pairing, on a hand-built series (no panel needed)."""
    idx = pd.bdate_range("2020-07-01", "2021-12-31")
    ser = pd.Series(1.0, index=idx)
    ser.iloc[:] = np.linspace(1.0, 2.0, len(idx))
    y = yearly(ser)
    assert set(y) == {2020, 2021}, y
    # 2020 is a half year -> partial must be flagged; 2021 is a full year -> must not be
    assert 0.0 < y[2020]["ret_pct"] < 100.0, y[2020]
    assert y[2020].get("partial") is True, "a late-start year must be flagged partial"
    assert "partial" not in y[2021], "full year must not be flagged"
    # levels chain is NOT exact across a year boundary (the last bar of a year and the first
    # bar of the next are different bars, so one bar of growth falls between the cells);
    # what must hold is: single-year cell == that year's own level ratio, exactly.
    one = ser[ser.index.year == 2021]
    assert len(one) > 1
    exact = (float(one.iloc[-1]) / float(one.iloc[0]) - 1.0) * 100.0
    assert abs(y[2021]["ret_pct"] - exact) < 0.01, (y[2021]["ret_pct"], exact)
    # and the chain may only under-count the boundary bar, never over-count the total
    tot = float(ser.iloc[-1]) / float(ser.iloc[0]) - 1
    chained = (1 + y[2020]["ret_pct"] / 100.0) * (1 + y[2021]["ret_pct"] / 100.0) - 1
    assert chained <= tot + 1e-9, (chained, tot)
    assert tot - chained < 0.02, (chained, tot)
    rows = window_metrics(ser, "book")
    assert [r["label"] for r in rows] == [
        "book_full", "book_is_2020_2023", "book_oos_2024_plus"], rows
    assert rows[2].get("note") == "too short", "empty OOS slice must degrade honestly"
    print("selftest OK (4/4)")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        main()