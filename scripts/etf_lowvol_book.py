#!/usr/bin/env python
"""E228 -- the only quotable directions, priced as a book instead of a sentence.

E227 (r1340) closed with a consequence rather than a table: of the six factor
directions behind the published ETF headline, only `vol_60-` and
`intraday_range-` kept their sign across the three declared cells; the other four
moved by 1-3pp and one (`price_position`) flipped outright. So the card may say
"the edge is a low-volatility tilt" and may not say "factor X pays in direction Y".

That leaves an operational question the three-corner table never asked: if only
two directions are quotable, what does the book that uses ONLY those two look
like -- and does dropping the four unquotable factors cost anything?

Two arms per cell, nothing else:
  PROD = the published six-sign vector (what the card runs today)
  LV2  = vol_60 -1, intraday_range -1, everything else zero (score_from drops a
         zero factor and re-normalises by the number of active factors)

Cells: the FULL 9-cell walk-forward grid (N 3/5/8 x R 10/20/40), not three
corners -- E227's own honest limit was "unstable across THESE cells", and the
low-vol pair is the claim that survives it, so the claim gets the full grid.

Verdict rule is frozen here, echoed into the payload, and recomputed by the gate
from the per-cell numbers; a typed verdict cannot outlive a panel move.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import etf_sign_enum as E  # noqa: E402
import etf_sign_pit as P  # noqa: E402
import etf_variants_null_rolling as V  # noqa: E402

OUT_JSON = ROOT / "results" / "etf_lowvol_book.json"

COST = E.COST
START = E.START
MIN_TRADED_BARS = E.MIN_TRADED_BARS
OOS_START = "2024-01-01"
FACTOR_KEYS = list(E.FACTOR_KEYS)

LV2_KEYS = ("vol_60", "intraday_range")
LV2_SIGNS = {k: (-1.0 if k in LV2_KEYS else 0.0) for k in FACTOR_KEYS}

CELLS = tuple(("R%d_N%d" % (r, n), r, n) for n in (3, 5, 8) for r in (10, 20, 40))

TOL = 0.01          # 1pp/yr: below this LV2 is "no material loss"
MIN_CELLS_WITHIN = 7    # of the 9 declared cells
REPLACE_FRAC = 2.0 / 3.0
WORSE_FRAC = 1.0 / 3.0

DECLARED = {
    "cells": [{"tag": t, "rebal": r, "n_hold": n} for t, r, n in CELLS],
    "arms": {"PROD": "published six-sign vector",
             "LV2": ", ".join(sorted(LV2_KEYS)) + " negative, others zero"},
    "cost_per_side": COST,
    "start": START,
    "oos_start": OOS_START,
    "min_traded_bars": MIN_TRADED_BARS,
    "tol_cagr": TOL,
    "min_cells_within": MIN_CELLS_WITHIN,
    "replace_frac": REPLACE_FRAC,
    "worse_frac": WORSE_FRAC,
    "secondary_oos": "the OOS block is reported, never used by the verdict",
}


# --- arm arithmetic ------------------------------------------------------------------
def agg_pair(ser: pd.Series) -> dict:
    """Full window plus a declared IS/OOS split of the same series."""
    out = {"full": E.agg(ser)}
    s = ser.copy()
    s.index = pd.to_datetime(s.index)
    for tag, mask in (("is", s.index < pd.Timestamp(OOS_START)),
                      ("oos", s.index >= pd.Timestamp(OOS_START))):
        part = s[mask]
        out[tag] = E.agg(part) if len(part) >= 2 else {"cagr": None, "sharpe": None,
                                                      "maxdd": None, "bars": int(len(part))}
    return out


def run_arm(zs, signs, close, openp, elig, rebal, n_hold) -> dict:
    sc = E.score_from(zs, signs, close, elig)
    ser, turn, _gap = V.fast_next_open(sc, close, openp, rebal, n_hold=n_hold,
                                       cost=COST, start=START)
    a = agg_pair(ser)
    a["turnover_per_rebal"] = round(float(turn), 4)
    a["traded"] = bool(float(turn) > 0.0 and len(ser) >= MIN_TRADED_BARS)
    a["signs"] = {k: float(signs[k]) for k in FACTOR_KEYS}
    return a


def cell_row(prod: dict, lv2: dict) -> dict:
    pc, lc = prod["full"].get("cagr"), lv2["full"].get("cagr")
    ps, ls = prod["full"].get("sharpe"), lv2["full"].get("sharpe")
    active = bool(prod.get("traded") and lv2.get("traded") and isinstance(pc, (int, float))
                  and isinstance(lc, (int, float)))
    return {
        "PROD": prod, "LV2": lv2, "active": active,
        "d_cagr": (round(float(lc) - float(pc), 6) if active else None),
        "d_sharpe": (round(float(ls) - float(ps), 6)
                     if active and isinstance(ps, (int, float)) and isinstance(ls, (int, float)) else None),
        "d_maxdd": (round(float(lv2["full"]["maxdd"]) - float(prod["full"]["maxdd"]), 6)
                    if active and isinstance(prod["full"].get("maxdd"), (int, float))
                    and isinstance(lv2["full"].get("maxdd"), (int, float)) else None),
        "d_oos_cagr": (round(float(lv2["oos"]["cagr"]) - float(prod["oos"]["cagr"]), 6)
                       if isinstance(prod["oos"].get("cagr"), (int, float))
                       and isinstance(lv2["oos"].get("cagr"), (int, float)) else None),
    }


def decide(cells: dict) -> dict:
    """Frozen rule; recomputed from per-cell d_cagr/d_sharpe only."""
    act = [t for t, c in cells.items() if c.get("active")]
    n = len(act)
    if n == 0:
        return {"verdict": "degenerate_grid", "n_active": 0, "n_within_tol": 0,
                "n_beat": 0, "n_sharpe_ge": 0, "median_d_cagr": None}
    d = [cells[t]["d_cagr"] for t in act]
    within = sum(1 for x in d if x >= -TOL)
    beat = sum(1 for x in d if x > 0)
    # 0.0 is a legitimate delta here (identical Sharpe), so never use `or` as a null test
    sh = sum(1 for t in act
             if cells[t].get("d_sharpe") is not None and cells[t]["d_sharpe"] >= 0.0)
    need_rep = int(np.ceil(REPLACE_FRAC * n))
    if within == n and beat >= need_rep and sh >= need_rep:
        v = "lowvol_replaces_production"
    elif within >= MIN_CELLS_WITHIN:
        v = "lowvol_no_material_loss"
    elif beat <= int(np.floor(WORSE_FRAC * n)):
        v = "lowvol_worse"
    else:
        v = "cell_dependent"
    return {"verdict": v, "n_active": n, "n_within_tol": within, "n_beat": beat,
            "n_sharpe_ge": sh, "median_d_cagr": round(float(np.median(d)), 6)}


def gate(payload: dict) -> dict:
    """Re-derive every published number from the per-cell tables."""
    checks = []
    decl = payload.get("declared") or {}
    cells = payload.get("cells") or {}
    tags = [c["tag"] for c in (decl.get("cells") or [])]
    checks.append({"check": "declared cells echoed", "ok": sorted(tags) == sorted(cells),
                   "n_declared": len(tags), "n_payload": len(cells)})
    recomputed = {}
    for t in tags:
        c = cells.get(t) or {}
        p, l = c.get("PROD") or {}, c.get("LV2") or {}
        pc, lc = (p.get("full") or {}).get("cagr"), (l.get("full") or {}).get("cagr")
        ok_num = isinstance(pc, (int, float)) and isinstance(lc, (int, float))
        d = (round(float(lc) - float(pc), 6) if ok_num else None)
        if c.get("d_cagr") is None or d is None:
            ok_d = True
        else:
            ok_d = abs(c["d_cagr"] - d) < 5e-6
        ps, ls = (p.get("full") or {}).get("sharpe"), (l.get("full") or {}).get("sharpe")
        ok_s = True
        if isinstance(ps, (int, float)) and isinstance(ls, (int, float)) and c.get("d_sharpe") is not None:
            ok_s = abs(c["d_sharpe"] - round(float(ls) - float(ps), 6)) < 5e-6
        checks.append({"check": "cell %s recomputed" % t, "ok": bool(ok_d and ok_s),
                       "d_cagr": d})
        recomputed[t] = c
    dec = decide(recomputed)
    stored = payload.get("verdict")
    checks.append({"check": "verdict recomputed from cells", "ok": dec["verdict"] == stored,
                   "stored": stored, "recomputed": dec["verdict"]})
    echo = payload.get("summary") or {}
    checks.append({"check": "summary agrees with recomputation",
                   "ok": (echo.get("n_active") == dec["n_active"]
                          and echo.get("n_within_tol") == dec["n_within_tol"]
                          and echo.get("n_beat") == dec["n_beat"])})
    checks.append({"check": "at least one active cell", "ok": dec["n_active"] > 0,
                   "n_active": dec["n_active"]})
    return {"verdict": dec["verdict"], "detail": dec, "checks": checks,
            "all_ok": all(c["ok"] for c in checks)}


# --- run -----------------------------------------------------------------------------
def run() -> dict:
    t0 = time.time()
    close, openp, amt, feats = P.load_panel()
    elig = P.eligibility(close, amt)
    zs = E.z_mats(close, feats)
    print("panel %d bars x %d symbols in %.1fs" % (len(close.index), close.shape[1],
                                                   time.time() - t0), flush=True)
    cells, rows = {}, []
    for tag, rebal, n_hold in CELLS:
        tc = time.time()
        prod = run_arm(zs, E.SIGNS, close, openp, elig, rebal, n_hold)
        lv2 = run_arm(zs, LV2_SIGNS, close, openp, elig, rebal, n_hold)
        row = cell_row(prod, lv2)
        row["rebal"], row["n_hold"] = rebal, n_hold
        cells[tag] = row
        rows.append({"tag": tag, "rebal": rebal, "n_hold": n_hold,
                     "prod_cagr": prod["full"]["cagr"], "lv2_cagr": lv2["full"]["cagr"],
                     "d_cagr": row["d_cagr"], "d_sharpe": row["d_sharpe"],
                     "d_oos_cagr": row["d_oos_cagr"]})
        print("  cell %-8s PROD=%.4f LV2=%.4f d=%+.4f dSharpe=%s oos=%s (%.1fs)"
              % (tag, prod["full"]["cagr"] or 0.0, lv2["full"]["cagr"] or 0.0,
                 row["d_cagr"] or 0.0, row["d_sharpe"], row["d_oos_cagr"],
                 time.time() - tc), flush=True)
    dec = decide(cells)
    payload = {
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "universe": int(close.shape[1]),
        "question": "E227 left two directions quotable and four not. Priced as a book: does a "
                    "vol_60-/intraday_range- only vector lose anything against the published "
                    "six-sign vector, across the FULL 9-cell grid?",
        "declared": DECLARED,
        "prod_signs": {k: float(E.SIGNS[k]) for k in FACTOR_KEYS},
        "lv2_signs": dict(LV2_SIGNS),
        "cells": cells,
        "summary": {"rows": rows, **dec, "elapsed_s": None},
        "caveats": [
            "Both arms are in-sample by construction (the six published signs were chosen on "
            "this panel, E219/r1335); this compares two sign vectors, it does not estimate a live return.",
            "LV2 is not a fresh optimisation: it is the subset E227 already certified as "
            "sign-stable, so its win is not a new in-sample draw -- but it was still selected "
            "on the same panel, so the honest reading is 'fewer knobs, no measured loss', "
            "not 'better strategy'.",
            "The OOS block (>= 2024-01-01) is reported and never used by the verdict: the "
            "verdict rule was frozen over the full window.",
            "ETF pool is today's listed set (survivorship), unchanged caveat.",
            "Engine is the reference one (no impact cost, no gap risk).",
        ],
    }
    g = gate(payload)
    payload["verdict"] = g["verdict"]
    payload["summary"]["elapsed_s"] = round(time.time() - t0, 1)
    payload["gate"] = {"all_ok": g["all_ok"], "checks": g["checks"]}
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"verdict": g["verdict"], "detail": g["detail"],
                      "elapsed_s": payload["summary"]["elapsed_s"]},
                     ensure_ascii=False, indent=1))
    return payload


def check() -> int:
    if not OUT_JSON.exists():
        print("MISSING %s" % OUT_JSON)
        return 2
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    g = gate(payload)
    bad = [c for c in g["checks"] if not c["ok"]]
    print(json.dumps({"verdict": g["verdict"], "all_ok": g["all_ok"], "failed": bad},
                     ensure_ascii=False, indent=1))
    return 0 if g["all_ok"] else 1


# --- selftest ------------------------------------------------------------------------
def _cell(pc, lc, ps=1.0, ls=1.0, traded=True):
    return {"PROD": {"full": {"cagr": pc, "sharpe": ps}, "traded": traded},
            "LV2": {"full": {"cagr": lc, "sharpe": ls}, "traded": traded},
            "active": traded, "d_cagr": round(lc - pc, 6), "d_sharpe": round(ls - ps, 6)}


def selftest() -> int:
    n_ok = 0
    total = 0

    def leg(name, cond):
        nonlocal n_ok, total
        total += 1
        if cond:
            n_ok += 1
            print("  ok   %s" % name)
        else:
            print("  FAIL %s" % name)

    tags = [c["tag"] for c in DECLARED["cells"]]

    # 1 LV2 better everywhere -> replaces
    cells = {t: _cell(0.10, 0.13, 1.0, 1.2) for t in tags}
    leg("lv2 strictly better -> lowvol_replaces_production",
        decide(cells)["verdict"] == "lowvol_replaces_production")

    # 2 LV2 materially worse everywhere -> worse
    cells = {t: _cell(0.10, 0.06) for t in tags}
    leg("lv2 4pp worse everywhere -> lowvol_worse", decide(cells)["verdict"] == "lowvol_worse")

    # 3 mixed (4 beat, 5 lose 2pp) -> cell_dependent
    cells = {}
    for i, t in enumerate(tags):
        cells[t] = _cell(0.10, 0.12) if i < 4 else _cell(0.10, 0.08)
    leg("split grid -> cell_dependent", decide(cells)["verdict"] == "cell_dependent")

    # 4 within tolerance but never better -> no material loss, not replaces
    cells = {t: _cell(0.10, 0.095) for t in tags}
    leg("lv2 -0.5pp flat -> lowvol_no_material_loss",
        decide(cells)["verdict"] == "lowvol_no_material_loss")

    # 5 untraded grid is refused, not called stable
    cells = {t: _cell(0.10, 0.12, traded=False) for t in tags}
    leg("untraded grid -> degenerate_grid", decide(cells)["verdict"] == "degenerate_grid")

    # 6 gate refuses a typed verdict that the cells no longer support
    payload = {"declared": {"cells": [{"tag": t, "rebal": 20, "n_hold": 12} for t in tags]},
               "cells": {t: _cell(0.10, 0.13) for t in tags},
               "verdict": "lowvol_worse",
               "summary": {"n_active": 9, "n_within_tol": 9, "n_beat": 9}}
    leg("gate refuses a stale typed verdict", not gate(payload)["all_ok"])

    # 7 gate accepts a truthful payload
    payload["verdict"] = "lowvol_replaces_production"
    leg("gate accepts a consistent payload", gate(payload)["all_ok"])

    # 8 a cell whose d_cagr was hand-edited is caught
    payload2 = json.loads(json.dumps(payload))
    first = tags[0]
    payload2["cells"][first]["d_cagr"] = 0.5
    leg("gate catches a tampered d_cagr", not gate(payload2)["all_ok"])

    # 9 a missing declared cell is caught
    payload3 = json.loads(json.dumps(payload))
    payload3["cells"].pop(tags[0])
    leg("gate catches a dropped cell", not gate(payload3)["all_ok"])

    print("selftest %d/%d" % (n_ok, total))
    return 0 if n_ok == total else 1


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        run()
        return 0
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    print("usage: etf_lowvol_book.py [run|check|selftest]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())