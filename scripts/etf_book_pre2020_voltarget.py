"""Does the 8% vol overlay carry the pre-2020 book, or is the weakness in the picks?

r1233 published the pre-boom window (2015-01-01..2019-12-31, U_pre 193 names) for the
shipped rule and read 5.12%/yr, Sharpe 0.70, dd -16.71% against 9.60% in 2020+. The reader
left with one open question the page could not answer: the book is *de-levered* by an 8%
volatility target, and 2015-2019 was a much choppier tape -- so is the lower number the
overlay paying for its own insurance, or do the picks themselves simply earn less there?

The answer was already being computed and thrown away. etf_book_pre2020_wf builds both
curves per cell (`raw` no overlay / `vtc` at 8%) and publishes only `cells_vt`; the raw
legs never reach the payload. This script prices the comparison and nothing else:

  (a) per cell, raw vs the shipped overlay (target 8%, window 60 bars -- the production
      default in etf_book_production.backtest, so the pre-2020 test did NOT use a 10-day
      window; that claim in the r1233 hand-off is a transcription error and is corrected
      here by reading the constant out of the engine)
  (b) the overlay's own contribution, delta = vt - raw, per cell and in aggregate
  (c) how often the overlay actually de-levered (share of decisions with scale < 1) so a
      zero delta can be read as "never fired" rather than "fired and did nothing"
  (d) vol-window sensitivity 20 / 60 / 120 on the fixed N12_R20 cell, because a window
      choice that flips the sign would make every number above a knob reading

Verdict is frozen in code and recomputed by --selftest from this file's own summary keys;
no threshold is read back from the payload.

Control before any quotation: this script's vt(60) cells must reproduce the published
etf_book_pre2020_wf.cells_vt cagr within CONTROL_TOL_PP, else it is pricing a different
book and exits 3 instead of quoting.

Usage (cwd = repo root):
    python scripts/etf_book_pre2020_voltarget.py run
    python scripts/etf_book_pre2020_voltarget.py --selftest
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

OUT = os.path.join(E.PATHS.results_dir, "etf_book_pre2020_voltarget.json")
PUB_WF = os.path.join(E.PATHS.results_dir, "etf_book_pre2020_wf.json")

START = "2015-01-01"
END = "2019-12-31"
COST = 0.0010
TARGET = 0.08
SHIPPED_WINDOW = 60          # etf_book_production.backtest default; read back below
WINDOWS = [20, 60, 120]
CELLS = [(3, 10), (3, 20), (3, 40), (5, 10), (5, 20), (5, 40), (8, 10), (8, 20), (8, 40)]
FIXED = (12, 20)
CONTROL_TOL_PP = 0.5
ADOPT_PP = 0.5
WINDOW_SPREAD_PP = 1.0
DELEVER_EPS = 0.999


def _key(n, r):
    return "N%d_R%d" % (n, r)


def _stats(ser):
    m = E.metrics(ser, "arm")
    return {k: m.get(k) for k in ("cagr", "sharpe", "maxdd", "vol", "bars")}


def _delever_share(diag):
    """Share of decisions where the overlay actually shrank the book."""
    if not diag:
        return None
    scales = [float(row["scale"]) for row in diag if row.get("scale") is not None]
    if not scales:
        return None
    return round(sum(1 for s in scales if s < DELEVER_EPS) / len(scales), 4)


def verdict_from_summary(summary):
    """Frozen decision rule. Only the published summary keys are consulted."""
    delta = summary["delta_mean_pp"]
    pos = summary["cells_better"]
    n = summary["cells"]
    if delta >= ADOPT_PP and pos >= n - 2:
        return "OVERLAY_PAYS_PRE_2020"
    if delta <= -ADOPT_PP and pos <= 2:
        return "OVERLAY_DRAINS_PRE_2020"
    return "OVERLAY_IS_NOT_THE_STORY"


def window_verdict(spread_pp):
    return "WINDOW_INSENSITIVE" if spread_pp <= WINDOW_SPREAD_PP else "WINDOW_MATTERS"


def _summarise(cell_rows):
    deltas = [row["delta_pp"] for row in cell_rows if row.get("delta_pp") is not None]
    if not deltas:
        return {"cells": 0, "delta_mean_pp": None, "cells_better": 0, "cells_worse": 0}
    return {
        "cells": len(deltas),
        "delta_mean_pp": round(float(np.mean(deltas)), 4),
        "delta_min_pp": round(float(np.min(deltas)), 4),
        "delta_max_pp": round(float(np.max(deltas)), 4),
        "cells_better": int(sum(1 for d in deltas if d > 0)),
        "cells_worse": int(sum(1 for d in deltas if d < 0)),
    }


def build_panel():
    """The published pre-2020 panel path, copied call-for-call from pre2020_wf.run()."""
    close, openp, amt, _score, _cls, n_flip = P.prep_panel()
    _c0, _o0, _a0, feats = E.build_panel()
    pre = W.universe_pre(close)
    cols = [c for c in close.columns if c in set(pre)]
    c, o, a, f = W.truncate(
        [close[cols], openp[cols], amt[cols],
         {k: v.reindex(columns=cols) for k, v in feats.items() if hasattr(v, "columns")}],
        None, END)
    score = E.build_score(c, a, f)
    return c, o, a, f, score, len(pre), len(cols), n_flip


def run():
    c, o, a, f, score, n_pre, n_cols, n_flip = build_panel()
    print("universe U_pre=%d cols=%d panel=%s last=%s flips=%d window=%d"
          % (n_pre, n_cols, c.shape, c.index[-1].date(), n_flip, SHIPPED_WINDOW), flush=True)

    curves = {}
    diagnostics = {}
    cell_rows = []
    for (n, r) in CELLS + [FIXED]:
        k = _key(n, r)
        raw_ser, _t, _g = E.run_next_open(c, o, a, f, rebal=r, n_hold=n, cost=COST,
                                          start=START, score=score)
        curves[(k, "raw")] = raw_ser
        rows = {"cell": k, "raw": _stats(raw_ser)}
        for w in WINDOWS:
            diag = []
            ser, _turn = R.open_to_open_equity(c, o, a, score, r, n, COST,
                                               vol_target=TARGET, start=START,
                                               vol_window=w, diag=diag)
            curves[(k, "vt%d" % w)] = ser
            rows["vt%d" % w] = _stats(ser)
            rows["delever_share%d" % w] = _delever_share(diag)
            if w == SHIPPED_WINDOW:
                diagnostics[k] = diag
        raw_cagr = rows["raw"]["cagr"]
        ship = rows["vt%d" % SHIPPED_WINDOW]["cagr"]
        rows["delta_pp"] = (None if raw_cagr is None or ship is None
                            else round((ship - raw_cagr) * 100, 4))
        cell_rows.append(rows)
        print("%-8s raw %7.2f%% vt60 %7.2f%% delta %+6.2fpp delever %.2f"
              % (k, (raw_cagr or 0) * 100, (ship or 0) * 100,
                 rows["delta_pp"] or 0.0,
                 rows["delever_share%d" % SHIPPED_WINDOW] or 0.0), flush=True)

    summary = _summarise(cell_rows)
    summary["verdict"] = verdict_from_summary(summary)

    # window sensitivity on the fixed production cell
    fixed_rows = [row for row in cell_rows if row["cell"] == _key(*FIXED)][0]
    win_cagrs = [fixed_rows["vt%d" % w]["cagr"] for w in WINDOWS]
    win_cagrs = [x for x in win_cagrs if x is not None]
    spread_pp = round((max(win_cagrs) - min(win_cagrs)) * 100, 4) if win_cagrs else None
    sensitivity = {
        "cell": _key(*FIXED),
        "cagr_by_window": {"vt%d" % w: fixed_rows["vt%d" % w]["cagr"] for w in WINDOWS},
        "spread_pp": spread_pp,
        "verdict": window_verdict(spread_pp) if spread_pp is not None else None,
    }

    # control: reproduce the published cells_vt before quoting anything
    control = {"tol_pp": CONTROL_TOL_PP, "cells": {}, "ok": True}
    published = {}
    if os.path.exists(PUB_WF):
        with open(PUB_WF, encoding="utf-8") as fh:
            published = (json.load(fh) or {}).get("cells_vt") or {}
    for row in cell_rows:
        k = row["cell"]
        pub = (published.get(k) or {}).get("cagr")
        got = row["vt%d" % SHIPPED_WINDOW]["cagr"]
        if pub is None or got is None:
            control["cells"][k] = {"published": pub, "recomputed": got, "ok": False,
                                   "note": "missing side"}
            control["ok"] = False
            continue
        diff_pp = abs(got - pub) * 100
        control["cells"][k] = {"published": pub, "recomputed": got,
                               "diff_pp": round(diff_pp, 4), "ok": diff_pp <= CONTROL_TOL_PP}
        if diff_pp > CONTROL_TOL_PP:
            control["ok"] = False

    out = {
        "schema": "etf_book_pre2020_voltarget/v1",
        "question": "is the pre-2020 shortfall the 8% overlay de-levering, or the picks?",
        "window": [START, END],
        "universe": {"U_pre": n_pre, "cols": n_cols, "flips_repaired": n_flip},
        "cost_bp_per_side": COST * 1e4,
        "vol_target": TARGET,
        "shipped_vol_window": SHIPPED_WINDOW,
        "windows": WINDOWS,
        "cells": cell_rows,
        "summary": summary,
        "window_sensitivity": sensitivity,
        "control": control,
        "evidence_cutoff": str(c.index[-1].date()),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print("control ok=%s | summary=%s | window=%s"
          % (control["ok"], json.dumps(summary, sort_keys=True),
             json.dumps(sensitivity["verdict"])), flush=True)
    print("wrote", OUT, flush=True)
    return out if control["ok"] else 3


# ----------------------------------------------------------------------------- selftest

def _fixture(n=400, seed=7):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2015-01-01", periods=n)
    cols = ["A", "B", "C"]
    rets = rng.normal(0.0004, 0.01, size=(n, len(cols)))
    close = pd.DataFrame(np.cumprod(1 + rets, axis=0) * 10, index=idx, columns=cols)
    openp = close * (1 + rng.normal(0, 0.001, size=close.shape))
    amt = pd.DataFrame(1e9, index=idx, columns=cols)
    return close, openp, amt


def _selftest():
    legs = []

    def leg(name, cond, detail=""):
        legs.append({"leg": name, "ok": bool(cond), "detail": detail})

    # L1 summary aggregation
    rows = [{"delta_pp": 1.0}, {"delta_pp": -0.5}, {"delta_pp": 2.0}]
    s = _summarise(rows)
    leg("summary means the deltas", abs(s["delta_mean_pp"] - 0.8333) < 1e-3, str(s))
    leg("summary counts direction", s["cells_better"] == 2 and s["cells_worse"] == 1, str(s))

    # L2 frozen verdict, three branches
    leg("overlay pays", verdict_from_summary({"delta_mean_pp": 1.2, "cells_better": 10, "cells": 10})
        == "OVERLAY_PAYS_PRE_2020")
    leg("overlay drains", verdict_from_summary({"delta_mean_pp": -1.2, "cells_better": 0,
                                                "cells": 10}) == "OVERLAY_DRAINS_PRE_2020")
    leg("overlay not the story", verdict_from_summary({"delta_mean_pp": 0.1, "cells_better": 6,
                                                      "cells": 10}) == "OVERLAY_IS_NOT_THE_STORY")
    leg("sub-threshold mean is not adoption", verdict_from_summary(
        {"delta_mean_pp": 0.4, "cells_better": 10, "cells": 10}) == "OVERLAY_IS_NOT_THE_STORY")

    # L3 window verdict
    leg("window insensitive", window_verdict(0.9) == "WINDOW_INSENSITIVE")
    leg("window matters", window_verdict(1.01) == "WINDOW_MATTERS")

    # L4 delever share: only scale<1 counts, and an all-in book reads 0
    leg("delever share ignores full size",
        _delever_share([{"scale": 1.0}, {"scale": 1.0}]) == 0.0)
    leg("delever share counts partial size",
        _delever_share([{"scale": 1.0}, {"scale": 0.5}]) == 0.5)
    leg("no diag is None not zero", _delever_share([]) is None)

    # L5 the engine default really is the window this script calls shipped
    leg("engine default vol window is the shipped one",
        R.open_to_open_equity.__defaults__ is not None and
        SHIPPED_WINDOW in R.open_to_open_equity.__defaults__, str(R.open_to_open_equity.__defaults__))
    import inspect
    sig = inspect.signature(R.open_to_open_equity)
    leg("engine parameter is named vol_window", "vol_window" in sig.parameters,
        str(list(sig.parameters)))
    leg("engine vol_window default equals shipped",
        sig.parameters["vol_window"].default == SHIPPED_WINDOW,
        str(sig.parameters["vol_window"].default))

    # L6 production backtest passes the same default (so the pre-2020 test was not a 10d run)
    psig = inspect.signature(P.backtest)
    leg("production backtest default window", psig.parameters["vol_window"].default == SHIPPED_WINDOW,
        str(psig.parameters["vol_window"].default))

    # L7 a real engine call on a fixture: raw and vt must both produce a curve, and a
    # de-lever of a 10%-vol book to an 8% target must leave it under 1.0 scale at least once
    close, openp, amt = _fixture()
    score = pd.DataFrame(np.tile(np.linspace(0.5, 1.5, len(close))[:, None], (1, close.shape[1])),
                         index=close.index, columns=close.columns)
    raw, _t, _g = E.run_next_open(close, openp, amt, {}, rebal=20, n_hold=2, cost=COST,
                                  start="2015-01-01", score=score)
    diag = []
    vt, _turn = R.open_to_open_equity(close, openp, amt, score, 20, 2, COST,
                                      vol_target=TARGET, start="2015-01-01",
                                      vol_window=SHIPPED_WINDOW, diag=diag)
    leg("fixture raw curve produced", raw is not None and len(raw.dropna()) > 100,
        "bars=%s" % (0 if raw is None else len(raw.dropna())))
    leg("fixture vt curve produced", vt is not None and len(vt.dropna()) > 100,
        "bars=%s" % (0 if vt is None else len(vt.dropna())))
    leg("fixture overlay de-levers a 1%-daily book", (_delever_share(diag) or 0) > 0,
        "share=%s" % _delever_share(diag))
    leg("fixture overlay never levers above 1",
        all(float(r["scale"]) <= 1.0 + 1e-9 for r in diag if r.get("scale") is not None))

    # L8 the knob has to move risk inside ONE engine (raw and vt are different engines, so
    # their vols are not comparable). A target of 0 is the engine's "off" branch -- it must
    # reproduce the no-overlay curve bit for bit; a live target must cut realised vol.
    base, _t3 = R.open_to_open_equity(close, openp, amt, score, 20, 2, COST,
                                      vol_target=None, start="2015-01-01",
                                      vol_window=SHIPPED_WINDOW)
    diag0 = []
    zed, _t2 = R.open_to_open_equity(close, openp, amt, score, 20, 2, COST,
                                     vol_target=0.0, start="2015-01-01",
                                     vol_window=SHIPPED_WINDOW, diag=diag0)
    both = pd.concat([base.dropna(), zed.dropna()], axis=1, join="inner")
    same = bool(len(both) > 100 and np.allclose(both.iloc[:, 0], both.iloc[:, 1], rtol=0,
                                                atol=1e-12))
    leg("a zero target is the engine's off branch", same, "bars=%d" % len(both))
    leg("a live target cuts realised vol inside one engine",
        (_stats(vt).get("vol") or 1.0) < (_stats(base).get("vol") or 0.0),
        "vt08_vol=%s base_vol=%s" % (_stats(vt).get("vol"), _stats(base).get("vol")))

    # L9 the published payload, when present, must still agree with the frozen rule -- a
    # hand-edited verdict has to fail here rather than read as a finished round.
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as fh:
            pay = json.load(fh) or {}
        s = pay.get("summary") or {}
        leg("published verdict recomputes from its own summary",
            s.get("verdict") == verdict_from_summary(s) if s.get("cells") else False,
            "verdict=%s rule=%s" % (s.get("verdict"),
                                    verdict_from_summary(s) if s.get("cells") else None))
        ctl = pay.get("control") or {}
        leg("published control reproduces the shipped cells",
            bool(ctl.get("ok")) and all(v.get("ok") for v in (ctl.get("cells") or {}).values()),
            "cells=%d" % len(ctl.get("cells") or {}))
        leg("published window verdict matches its spread",
            (pay.get("window_sensitivity") or {}).get("verdict")
            == window_verdict((pay.get("window_sensitivity") or {}).get("spread_pp") or 0.0),
            str((pay.get("window_sensitivity") or {}).get("verdict")))

    n_pass = sum(1 for x in legs if x["ok"])
    for x in legs:
        print(("PASS " if x["ok"] else "FAIL ") + x["leg"] + (" | " + x["detail"] if x["detail"] else ""))
    print("%d/%d PASS" % (n_pass, len(legs)))
    return 0 if n_pass == len(legs) else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    if "run" in sys.argv:
        rc = run()
        sys.exit(3 if rc == 3 else 0)
    print(__doc__)
    sys.exit(0)