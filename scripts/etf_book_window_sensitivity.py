"""Does the calendar refusal come from the book, or from where the window starts?

The supply ladder has been red on one sentence: the candidate books are refused by
years_for_half at a median of 2 years against a line of 3. r1428 measured how many years of
NEW data would heal it (7-14). Nobody asked the opposite question, which needs no new data at
all: the panel in this repo starts in 2005-02-23, but every published book is priced from
2020-01-01 onward, so "half the calendar's return arrives in 2 years" may be a statement about
a 7-year window rather than about the book.

EXPLORATORY receipt (no prereg, no verdict, no ledger entry). It re-prices the same published
plain arm through the same published engine at five window starts, each through the frozen
five-phase set (so a single phase cannot answer it -- r1261/r1425), and prints per start the
median caliber values, their phase spread, the CAGR/sharpe/drawdown and the width of the
universe actually available then. Two identity legs protect it:

  L1  start 2020-01-01, phase 0 reproduces the published plain-arm row
      (cagr 11.46 / top2 0.7108 / maxdd -0.1056)
  L2  the caliber function and the engine are imported, never retyped

If years_for_half lands at >= 3 on the earlier windows while CAGR/drawdown stay respectable,
the refusal is a window artefact and the honest next step is an admission-rule round on the
window, not seven more years of waiting. If it stays at 2, the book really is front-loaded and
the ETA stands.

    python scripts/etf_book_window_sensitivity.py run
    python scripts/etf_book_window_sensitivity.py selftest
"""
from __future__ import annotations

import json
import os
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import pandas as pd  # noqa: E402

import candidate_year_gate as G  # noqa: E402
import etf_book_scale_floor as S  # noqa: E402
import etf_book_year_caliber as K  # noqa: E402
import etf_book_year_gate as Y  # noqa: E402
import etf_equity_alpha as A  # noqa: E402

OUT = os.path.join(ROOT, "results", "etf_book_window_sensitivity.json")
PHASE_RECEIPT = os.path.join(ROOT, "results", "etf_book_sleeve_cap_phases.json")

STARTS = ("2013-01-01", "2015-01-01", "2017-01-01", "2019-01-01", "2020-01-01")
PHASE_OFFSETS = (0, 7, 14, 21, 28)      # the frozen weekly phase set from candidate_year_gate_phases
PUBLISHED_START = "2020-01-01"
TOL = 5e-5   # the published reference row is rounded to 4 decimals, so the identity leg
             # compares at the reference's own precision (4.5e-5 is rounding, not drift)

RULE = {
    "kind": "exploratory",
    "prereg": None,
    "verdict": None,
    "ledger": None,
    "why": ("re-prices one already-published arm at other window starts; it decides nothing "
            "and admits nothing -- it only says whether the refusal sentence is a property of "
            "the book or of the window it was measured in"),
    "frozen": {
        "starts": list(STARTS),
        "phase_offsets_days": list(PHASE_OFFSETS),
        "tolerance_identity": TOL,
        "engine": "etf_book_year_caliber.run_arm (imported, never retyped)",
        "calibers": "etf_book_year_caliber.calibers (imported, never retyped)",
    },
}


def _start_plus(start: str, days: int) -> str:
    return (pd.Timestamp(start) + pd.Timedelta(days=days)).strftime("%Y-%m-%d")


def _width(close: pd.DataFrame, start: str) -> dict:
    win = close.loc[close.index >= pd.Timestamp(start)]
    if win.empty:
        return {"first_bar_names": 0, "last_bar_names": 0, "bars": 0}
    return {"first_bar_names": int(win.iloc[0].notna().sum()),
            "last_bar_names": int(win.iloc[-1].notna().sum()),
            "bars": int(len(win))}


def _phase_cell(close, openp, amt, sc, cls, s: str) -> dict:
    ser, turn = K.run_arm(close, openp, amt, sc, cls, K.ARMS[0][1], s)
    rows = G._year_rows(Y.yearly_returns(ser))
    st = A.stats2(ser, "win_" + s)
    return {
        "start": s,
        "bars": int(len(ser)),
        "years": len(rows),
        "year_net_pct": {r["year"]: round(r["net_pct"], 4) for r in rows},
        "cagr_pct": None if st.get("cagr") is None else round(st["cagr"] * 100, 4),
        "sharpe": None if st.get("sharpe") is None else round(float(st["sharpe"]), 4),
        "maxdd_pct": None if st.get("maxdd") is None else round(st["maxdd"] * 100, 4),
        "turnover": None if turn is None else round(float(turn), 4),
        "calibers": K.calibers(rows),
    }


def _med(vals):
    vals = [v for v in vals if v is not None]
    return None if not vals else round(float(statistics.median(vals)), 6)


def _spread(vals):
    vals = [v for v in vals if v is not None]
    return None if len(vals) < 2 else round(float(max(vals) - min(vals)), 6)


def measure(close, openp, amt, sc, cls, start: str) -> dict:
    cells = [_phase_cell(close, openp, amt, sc, cls, _start_plus(start, d)) for d in PHASE_OFFSETS]
    keys = ("years_for_half", "effective_years", "net_top2_share", "gross_top2_share")
    # the S test is imported from the published ruler: a hand-rolled median/spread here would
    # be a second implementation of the very thing r1425 was about
    adj = {k: K.adjudicate_caliber(k, cells) for k in keys}
    return {
        "start": start,
        "phases": len(cells),
        "adjudication": adj,
        "median": {k: adj[k].get("median") for k in keys},
        "median_cagr_pct": _med([c["cagr_pct"] for c in cells]),
        "median_sharpe": _med([c["sharpe"] for c in cells]),
        "median_maxdd_pct": _med([c["maxdd_pct"] for c in cells]),
        "median_years": _med([c["years"] for c in cells]),
        "universe": _width(close, start),
        "cells": cells,
    }


def _published_plain_phase0() -> dict | None:
    if not os.path.exists(PHASE_RECEIPT):
        return None
    with open(PHASE_RECEIPT, encoding="utf-8") as f:
        prev = json.load(f)
    for b in prev.get("books", []):
        if b.get("book") == "plain":
            rows = b.get("phase_rows") or []
            return rows[0] if rows else None
    return None


def run() -> int:
    t0 = time.time()
    close, openp, amt, sc, n_flip = S.nobond_universe()
    cls = A.classify(close.columns, A.load_class_map(), close)
    cut = close.index[-1]
    print("panel", close.index[0].date(), "->", cut.date(), "cols", close.shape[1], flush=True)

    windows = []
    for s in STARTS:
        w = measure(close, openp, amt, sc, cls, s)
        windows.append(w)
        m = w["median"]
        print("%s done  yfh %s  ey %s  cagr %s" % (s, m["years_for_half"],
                                                   m["effective_years"], w["median_cagr_pct"]),
              flush=True)

    ident = {"checked": False}
    ref = _published_plain_phase0()
    pub = next((w for w in windows if w["start"] == PUBLISHED_START), None)
    if ref and pub:
        c0 = pub["cells"][0]
        pairs = {"cagr_pct": (c0["cagr_pct"], ref.get("cagr_pct")),
                 "top2_share": (c0["calibers"].get("net_top2_share"), ref.get("top2_share")),
                 "maxdd": (c0["maxdd_pct"] / 100.0 if c0["maxdd_pct"] is not None else None,
                           ref.get("maxdd"))}
        deltas = {k: (None if a is None or b is None else abs(a - b)) for k, (a, b) in pairs.items()}
        worst = max(d for d in deltas.values() if d is not None)
        ident = {"checked": True, "worst_abs_delta": round(worst, 12),
                 "per_field": {k: round(v, 12) for k, v in deltas.items() if v is not None},
                 "ok": worst <= TOL, "reference": {k: ref.get(k) for k in ref}}
        print("identity", PUBLISHED_START, "worst|d|", worst, "ok", ident["ok"], flush=True)

    print("elapsed %.1fs" % (time.time() - t0), flush=True)
    doc = {
        "evidence_cutoff": str(cut.date()),
        "as_of": str(cut.date()),
        "generated": pd.Timestamp.now().isoformat(timespec="seconds"),
        "rule": RULE,
        "panel": {"first": str(close.index[0].date()), "last": str(cut.date()),
                  "cols": int(close.shape[1]), "flip_cells_repaired": int(n_flip)},
        "arm": {"label": K.ARMS[0][0], "n_hold": K.N_HOLD, "rebalance": K.REBAL,
                "cost": K.COST, "vol_target": K.VT,
                "note": "the same published engine, only the window start moves"},
        "windows": windows,
        "identity": ident,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)

    for w in windows:
        m = w["median"]
        a = w["adjudication"]["years_for_half"]
        print("%s phases %d years %s cagr %s sharpe %s dd %s | yfh %s spread %s margin %s -> %s"
              " | ey %s top2 %s"
              % (w["start"], w["phases"], w["median_years"], w["median_cagr_pct"],
                 w["median_sharpe"], w["median_maxdd_pct"], m["years_for_half"],
                 a.get("spread"), a.get("margin"), a.get("state"),
                 m["effective_years"], m["net_top2_share"]), flush=True)
    print("wrote", os.path.relpath(OUT, ROOT), flush=True)
    return 0 if ident.get("ok", False) else 3


def selftest() -> int:
    ok = 0
    tot = 0

    def chk(cond, msg):
        nonlocal ok, tot
        tot += 1
        if cond:
            ok += 1
        else:
            print("FAIL", msg)

    chk(len(STARTS) >= 3 and STARTS[0] < PUBLISHED_START,
        "L1 earlier windows exist and are earlier than the published one")
    chk(PUBLISHED_START in STARTS, "L2 the published start is present for the identity leg")
    chk(len(PHASE_OFFSETS) == 5, "L3 the frozen five-phase set is used")
    rows = [{"year": 2020 + i, "net_pct": 10.0} for i in range(7)]
    cal = K.calibers(rows)
    chk(cal["years_for_half"] == 4, "L4 seven equal years reach half at 4 (%s)" % cal["years_for_half"])
    chk(abs(cal["effective_years"] - 7.0) < 1e-6, "L5 an even book counts 7 years")
    rows2 = [{"year": 2020, "net_pct": 90.0}] + [{"year": 2021 + i, "net_pct": 1.0} for i in range(6)]
    cal2 = K.calibers(rows2)
    chk(cal2["years_for_half"] == 1 and cal2["effective_years"] < cal["effective_years"],
        "L6 a front-loaded book reaches half in one year and counts fewer")
    chk(_med([None, None]) is None and _spread([1.0]) is None,
        "L7 medians/spreads refuse to invent a number from one reading")
    chk(_start_plus("2020-01-01", 7) == "2020-01-08", "L8 phase offsets are calendar days")
    chk(RULE["verdict"] is None and RULE["prereg"] is None, "L9 the rule admits it decides nothing")
    print("selftest %d/%d" % (ok, tot))
    return 0 if ok == tot else 1


def main(argv) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        return run()
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))