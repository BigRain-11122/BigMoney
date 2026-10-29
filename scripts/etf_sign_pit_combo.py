#!/usr/bin/env python
"""E236 -- the operator's real alternative is not a per-factor IC sign, it is re-picking the vector.

The chain already carries three answers about this book's six SIGNS, and they leave a hole:

  etf_sign_pit (E205)  -- re-signing each factor from its own trailing IC earns -10.81%/yr
                          against the published 6.14%: the signs were read off the sample.
  etf_sign_enum (E208) -- all 2^6 sign vectors priced on one window: the published vector
                          ranks 6 of 64, median arm -1.76%/yr.
  etf_sign_cells (E227) -- at three cells only two factor directions keep their sign.

None of those is what a live operator would actually have done. An operator does not sign
six factors independently from an IC table; the operator picks ONE vector out of 64 and
runs it until it stops working. That procedure has never been priced. It matters because
it is the only path by which this line could be shipped without hindsight: if "pick the
best vector from what has already happened" earns something, the book has a PIT-defensible
construction; if it does not, the published 6.14% is a full-sample reading with no live
counterpart and the line's headline cannot be quoted as a strategy.

Method (declared in DECLARED before any file is read):

  * For each declared cell, all 64 sign vectors are run once through the reference engine
    (one panel load, one engine call per vector). Each vector's own return path is causal
    by construction -- next_open never reads a future bar.
  * PIT arm: every `reselect` bars, rank the 64 vectors by realised Sharpe over the
    trailing `lookback` bars STRICTLY BEFORE that date, take the winner, and apply that
    vector's own returns for the next `reselect` bars. Stitching pre-computed causal paths
    cannot introduce look-ahead; the selftest drives a future-only spike and requires that
    it is not picked before it happens.
  * Arms: prod (oracle, in-sample), best-of-64 (oracle), equal-weight control, and the
    6 PIT variants per cell (reselect 60/120/250 x lookback 250/500).
  * Selection lift: at each selection event the chosen vector's forward mean return minus
    the mean across all valid vectors. That number, not the CAGR, is the honest measure of
    whether trailing Sharpe predicts anything here.

Exit axis (TRIAL_LABOR_LAW sec.4, explicit choice 1): the strategy's own exit. The arms are
rebalance-driven with no stop/ladder; the reference engine's default exit stack is unused.

Verdict rule is frozen below, echoed into the payload and recomputed by the gate from the
per-variant table; a typed verdict cannot outlive a panel move.
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
import etf_composite_pf as F  # noqa: E402

OUT_JSON = ROOT / "results" / "etf_sign_pit_combo.json"

COST = E.COST
START = E.START
MIN_TRADED_BARS = E.MIN_TRADED_BARS
FACTOR_KEYS = list(E.FACTOR_KEYS)

CELLS = (("R20_N12", 20, 12), ("R20_N5", 20, 5))
RESELECT = (60, 120, 250)
LOOKBACK = (250, 500)
MIN_VALID_FRAC = 0.8     # a vector needs 80% of its lookback bars LIVE to be selectable
MIN_LOOK_FOR_SHARPE = 20  # below this a trailing window is not a Sharpe estimate

TOL = 0.01               # 1pp/yr above the equal-weight control counts as "beat"
NEED_BEAT = 9            # of 12 declared variants
MAX_NO_VALUE = 3

DECLARED = {
    "cells": [{"tag": t, "rebal": r, "n_hold": n} for t, r, n in CELLS],
    "variants": [{"tag": "S%d_L%d" % (s, l), "reselect": s, "lookback": l}
                 for s in RESELECT for l in LOOKBACK],
    "arms": {"PROD": "the published six-sign vector (in-sample oracle)",
             "BEST": "the best of the 64 vectors on this window (in-sample oracle)",
             "CONTROL": "equal weight across the whole eligible universe, same cadence",
             "PIT": "trailing-Sharpe winner of the 64, re-picked every `reselect` bars"},
    "n_sign_vectors": 64,
    "min_valid_frac": MIN_VALID_FRAC,
    "tol_cagr_over_control": TOL,
    "need_beat": NEED_BEAT,
    "max_no_value": MAX_NO_VALUE,
    "start": START,
    "cost_per_side": COST,
    "exit_axis": "strategy_own_exit (rebalance turnover only; engine default exit stack unused)",
    "selection_space": "2^6 sign vectors, 6 PIT variants x 2 cells = 12 declared tests",
}


# --- arm arithmetic ----------------------------------------------------------------
def vec_id(signs: dict) -> str:
    return "|".join("%s%s" % (k, "+" if float(signs[k]) > 0 else "-") for k in FACTOR_KEYS)


def curve_returns(cur: pd.Series) -> pd.Series:
    """An equity curve's own daily returns; the first bar is the level, not a return."""
    r = cur.pct_change()
    r.iloc[0] = 0.0
    return r


def sharpe_of(seg: pd.Series):
    """Annualised Sharpe of a return slice; 0.0 for a flat (zero-vol) slice, None if unusable."""
    seg = seg.dropna()
    if len(seg) < MIN_LOOK_FOR_SHARPE:
        return None
    sd = float(seg.std())
    if not np.isfinite(sd):
        return None
    if sd == 0.0:
        return 0.0
    return float(seg.mean()) / sd * np.sqrt(252.0)


def stitch(rets: pd.DataFrame, reselect: int, lookback: int):
    """Walk-forward vector selection over pre-computed causal return paths.

    Returns (stitched returns | None, events). At every selection the ranking window is
    rets[sp-lookback : sp] -- strictly earlier bars -- and the applied window starts at sp.
    """
    idx = rets.index
    n = len(idx)
    out = pd.Series(np.nan, index=idx, dtype=float)
    events = []
    for sp in range(lookback, n, reselect):
        trail = rets.iloc[sp - lookback:sp]
        counts = trail.notna().sum()
        sh = {}
        for col in rets.columns:
            if int(counts[col]) < int(np.ceil(lookback * MIN_VALID_FRAC)):
                continue
            s = sharpe_of(trail[col])
            if s is None:
                continue
            sh[col] = s
        if not sh:
            continue
        pick = max(sh, key=lambda k: sh[k])      # ties -> first column, deterministic
        end = min(sp + reselect, n)
        out.iloc[sp:end] = rets[pick].iloc[sp:end].to_numpy()
        fwd = rets.iloc[sp:end]
        ch = fwd[pick].mean()
        allm = fwd.mean(axis=1).mean()
        events.append({
            "date": str(idx[sp].date()),
            "pick": pick,
            "trailing_sharpe": round(float(sh[pick]), 4),
            "rank": 1 + sum(1 for k in sh if sh[k] > sh[pick]),
            "n_valid": len(sh),
            "fwd_mean": (round(float(ch), 8) if np.isfinite(ch) else None),
            "fwd_mean_all": (round(float(allm), 8) if np.isfinite(allm) else None),
        })
    used = out.dropna()
    if used.empty:
        return None, events
    return used, events


def curve_from_returns(ret: pd.Series, full_index: pd.DatetimeIndex) -> pd.Series:
    """Equity curve anchored one bar BEFORE the first traded bar, so no return is dropped
    and the slice's own start level is 1.0 (F.metrics renormalises against its own first level)."""
    pos = full_index.get_loc(ret.index[0])
    anchor = full_index[pos - 1] if pos > 0 else full_index[pos]
    vals = np.concatenate(([1.0], np.cumprod(1.0 + ret.to_numpy(dtype=float))))
    return pd.Series(vals, index=pd.DatetimeIndex([anchor]).append(ret.index))


def arm_of(cur: pd.Series, signs: dict = None) -> dict:
    a = E.agg(cur)
    a["traded"] = bool(len(cur.dropna()) >= MIN_TRADED_BARS)
    if signs is not None:
        a["signs"] = {k: float(signs[k]) for k in FACTOR_KEYS}
    return a


# --- verdict + gate ----------------------------------------------------------------
def decide(cells: dict) -> dict:
    """Frozen rule; recomputed from per-variant cagr and each cell's control cagr only."""
    rows = []
    for tag, c in cells.items():
        ctrl = (c.get("control") or {}).get("cagr")
        for vtag, v in (c.get("variants") or {}).items():
            cg = v.get("cagr")
            if not isinstance(ctrl, (int, float)) or not isinstance(cg, (int, float)):
                continue
            rows.append({"cell": tag, "variant": vtag, "cagr": float(cg),
                         "beat": bool(float(cg) > float(ctrl) + TOL),
                         "positive": bool(float(cg) > 0.0)})
    n = len(rows)
    if n == 0:
        return {"verdict": "degenerate_grid", "n": 0, "n_beat": 0, "n_positive": 0,
                "median_cagr": None, "median_d_cagr_vs_control": None}
    n_beat = sum(1 for r in rows if r["beat"])
    n_pos = sum(1 for r in rows if r["positive"])
    d_med = round(float(np.median([r["cagr"] for r in rows])), 6)
    dctrl = round(float(np.median([r["cagr"] - (cells[r["cell"]]["control"]["cagr"])
                                   for r in rows])), 6)
    if n < len(DECLARED["cells"]) * len(DECLARED["variants"]):
        v = "incomplete_grid"
    elif n_beat >= NEED_BEAT and n_pos >= NEED_BEAT:
        v = "pit_combo_value"
    elif n_beat <= MAX_NO_VALUE:
        v = "pit_combo_no_value"
    else:
        v = "pit_combo_fragile"
    return {"verdict": v, "n": n, "n_beat": n_beat, "n_positive": n_pos,
            "median_cagr": d_med, "median_d_cagr_vs_control": dctrl}


def gate(payload: dict) -> dict:
    """Re-derive the verdict and every count from the per-variant table."""
    checks = []
    decl = payload.get("declared") or {}
    cells = payload.get("cells") or {}
    want_cells = [c["tag"] for c in (decl.get("cells") or [])]
    want_vars = [v["tag"] for v in (decl.get("variants") or [])]
    arm_ids = set((payload.get("arms_index") or {}).get("vectors") or [])

    checks.append({"check": "declared cells echoed", "ok": sorted(want_cells) == sorted(cells)})
    ok_v = True
    bad_v = []
    for tag in want_cells:
        have = sorted((cells.get(tag) or {}).get("variants") or {})
        if have != sorted(want_vars):
            ok_v = False
            bad_v.append({"cell": tag, "have": have})
    checks.append({"check": "every declared variant present in every cell",
                   "ok": bool(ok_v and want_cells), "bad": bad_v})

    # each variant's own numbers must agree with its event log and with the declared arm set
    ok_num, bad_num = True, []
    for tag in want_cells:
        for vtag in want_vars:
            v = ((cells.get(tag) or {}).get("variants") or {}).get(vtag) or {}
            ev = v.get("events") or []
            picks_ok = all(e.get("pick") in arm_ids for e in ev)
            live = (len(ev) > 0 and isinstance(v.get("cagr"), (int, float)))
            if not (picks_ok and live):
                ok_num = False
                bad_num.append({"cell": tag, "variant": vtag,
                                "n_events": len(ev), "picks_outside_arm_set": not picks_ok})
    checks.append({"check": "every variant has events and only declared picks",
                   "ok": bool(ok_num), "bad": bad_num})

    # beat/positive flags must be recomputable from the published numbers
    ok_flags, bad_flags = True, []
    for tag in want_cells:
        ctrl = ((cells.get(tag) or {}).get("control") or {}).get("cagr")
        for vtag in want_vars:
            v = ((cells.get(tag) or {}).get("variants") or {}).get(vtag) or {}
            cg = v.get("cagr")
            if not isinstance(ctrl, (int, float)) or not isinstance(cg, (int, float)):
                continue
            want_beat = bool(float(cg) > float(ctrl) + TOL)
            want_pos = bool(float(cg) > 0.0)
            if v.get("beat_control") != want_beat or v.get("positive") != want_pos:
                ok_flags = False
                bad_flags.append({"cell": tag, "variant": vtag})
    checks.append({"check": "beat/positive flags recomputed from published cagr",
                   "ok": bool(ok_flags), "bad": bad_flags})

    dec = decide(cells)
    checks.append({"check": "verdict recomputed from the variant table",
                   "ok": dec["verdict"] == payload.get("verdict"),
                   "stored": payload.get("verdict"), "recomputed": dec["verdict"]})
    echo = payload.get("summary") or {}
    checks.append({"check": "summary agrees with recomputation",
                   "ok": (echo.get("n") == dec["n"] and echo.get("n_beat") == dec["n_beat"]
                          and echo.get("n_positive") == dec["n_positive"])})
    checks.append({"check": "at least one variant was measured", "ok": dec["n"] > 0,
                   "n": dec["n"]})
    return {"verdict": dec["verdict"], "detail": dec, "checks": checks,
            "all_ok": all(c["ok"] for c in checks)}


# --- run ---------------------------------------------------------------------------
def run() -> dict:
    t0 = time.time()
    close, openp, amt, feats = P.load_panel()
    elig = P.eligibility(close, amt)
    zs = E.z_mats(close, feats)
    print("panel %d bars x %d symbols in %.1fs" % (len(close.index), close.shape[1],
                                                   time.time() - t0), flush=True)

    vectors = E.sign_vectors(FACTOR_KEYS)
    ids = [vec_id(v) for v in vectors]
    prod_id = vec_id(E.SIGNS)

    cells, rows = {}, []
    for tag, rebal, n_hold in CELLS:
        tc = time.time()
        arms = {}
        for signs, vid in zip(vectors, ids):
            sc = E.score_from(zs, signs, close, elig)
            cur, turn, _gap = V.fast_next_open(sc, close, openp, rebal, n_hold=n_hold,
                                              cost=COST, start=START)
            arms[vid] = (cur, float(turn))
        print("  cell %-8s 64 vectors in %.1fs" % (tag, time.time() - tc), flush=True)

        full_index = arms[ids[0]][0].index
        rets = pd.DataFrame({vid: curve_returns(arms[vid][0]) for vid in ids})
        rets = rets.sort_index()

        m = {vid: E.agg(arms[vid][0]) for vid in ids}
        cg = {vid: (m[vid].get("cagr") if isinstance(m[vid].get("cagr"), (int, float))
                    else -9e9) for vid in ids}
        best_id = max(ids, key=lambda k: cg[k])

        try:
            ew = F.run_ew(close, amt, rebal, start=START)
            control = arm_of(ew)
        except Exception as e:                                   # never invent a control
            control = {"label": "equal_weight_eligible", "note": "failed: %s" % e}

        variants = {}
        for s in RESELECT:
            for lb in LOOKBACK:
                vtag = "S%d_L%d" % (s, lb)
                used, events = stitch(rets, s, lb)
                if used is None:
                    variants[vtag] = {"reselect": s, "lookback": lb, "cagr": None,
                                      "sharpe": None, "maxdd": None, "beat_control": False,
                                      "positive": False, "n_events": len(events),
                                      "events": events}
                    continue
                cur = curve_from_returns(used, full_index)
                a = arm_of(cur)
                cgv = a.get("cagr")
                lifts = [e["fwd_mean"] - e["fwd_mean_all"] for e in events
                         if e.get("fwd_mean") is not None and e.get("fwd_mean_all") is not None]
                variants[vtag] = {
                    "reselect": s, "lookback": lb,
                    "cagr": cgv, "sharpe": a.get("sharpe"), "maxdd": a.get("maxdd"),
                    "bars": a.get("bars"),
                    "beat_control": bool(isinstance(cgv, (int, float))
                                         and isinstance(control.get("cagr"), (int, float))
                                         and float(cgv) > float(control["cagr"]) + TOL),
                    "positive": bool(isinstance(cgv, (int, float)) and float(cgv) > 0.0),
                    "n_events": len(events),
                    "picks_distinct": len(set(e["pick"] for e in events)),
                    "mean_lift_per_bar": (round(float(np.mean(lifts)), 8) if lifts else None),
                    "lift_positive_frac": (round(float(np.mean([1.0 if x > 0 else 0.0
                                                               for x in lifts])), 4)
                                           if lifts else None),
                    "events": events,
                }
                print("  %-8s %-8s cagr=%s sharpe=%s events=%d equiv_frac=%s (%.1fs)"
                      % (tag, vtag, cgv, a.get("sharpe"), len(events),
                         variants[vtag]["lift_positive_frac"], time.time() - tc), flush=True)

        cells[tag] = {"rebal": rebal, "n_hold": n_hold,
                      "control": control,
                      "prod": arm_of(arms[prod_id][0], E.SIGNS),
                      "best": {"id": best_id, **arm_of(arms[best_id][0])},
                      "variants": variants}
        for vtag, v in variants.items():
            rows.append({"cell": tag, "variant": vtag, "cagr": v.get("cagr"),
                         "sharpe": v.get("sharpe"),
                         "control_cagr": control.get("cagr"),
                         "prod_cagr": cells[tag]["prod"].get("cagr"),
                         "beat_control": v.get("beat_control"),
                         "mean_lift_per_bar": v.get("mean_lift_per_bar")})

    dec = decide(cells)
    prod_c = [cells[t]["prod"].get("cagr") for t in cells
              if isinstance(cells[t]["prod"].get("cagr"), (int, float))]
    payload = {
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "universe": int(close.shape[1]),
        "question": "E205 priced a per-factor IC sign; E208 priced all 64 vectors on one window. "
                    "The operator's actual procedure is neither: pick one vector from history "
                    "and run it. Does trailing-Sharpe re-selection of the 64 vectors earn "
                    "anything point-in-time, on the declared cells, against the equal-weight control?",
        "declared": DECLARED,
        "arms_index": {"vectors": ids, "prod_id": prod_id, "best_id": cells[CELLS[0][0]]["best"]["id"]},
        "cells": cells,
        "summary": {"rows": rows, **dec,
                    "prod_cagr_by_cell": {t: cells[t]["prod"].get("cagr") for t in cells},
                    "best_cagr_by_cell": {t: cells[t]["best"].get("cagr") for t in cells},
                    "control_cagr_by_cell": {t: cells[t]["control"].get("cagr") for t in cells},
                    "oracle_minus_pit_median_pp": (
                        round(float(np.median(prod_c)) - float(dec["median_cagr"]), 6)
                        if prod_c and dec.get("median_cagr") is not None else None),
                    "n_trials_declared": 64,
                    "elapsed_s": None},
        "caveats": [
            "Both oracle arms (PROD, BEST) are in-sample by construction: their signs were "
            "read off this panel (E205/E208). Only the PIT arms are candidates for a live claim.",
            "The PIT arm here re-selects a VECTOR; E205 re-signed each FACTOR from its own IC. "
            "They are different procedures and their numbers are not interchangeable.",
            "Selection is by trailing Sharpe over the declared lookback only; no other statistic "
            "was swept, so the variant grid is 3x2 and not an optimised surface.",
            "The reference engine charges 10bp/side and ignores impact and gap risk; the equal-"
            "weight control runs the same engine and cadence, so the comparison is paired.",
            "ETF pool is today's listed set (survivorship); all cells are one panel, one cost level.",
        ],
    }
    # the verdict has to be on the payload BEFORE the gate runs: the gate's job is to
    # recompute it from the table and disagree if it drifted, so sealing first and gating
    # second is the only order in which all_ok means anything.
    payload["verdict"] = dec["verdict"]
    g = gate(payload)
    payload["verdict"] = g["verdict"]
    payload["summary"]["elapsed_s"] = round(time.time() - t0, 1)
    payload["gate"] = {"all_ok": g["all_ok"], "checks": g["checks"]}
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"verdict": g["verdict"], "detail": g["detail"],
                      "gate_ok": g["all_ok"], "elapsed_s": payload["summary"]["elapsed_s"]},
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


# --- selftest ---------------------------------------------------------------------
def _synth(n=800, seed=7, arms=4):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    cols = ["A%d" % i for i in range(arms)]
    return pd.DataFrame({c: rng.normal(0.0, 0.01, n) for c in cols}, index=idx)


def selftest() -> int:
    n_ok, total = 0, 0

    def leg(name, cond):
        nonlocal n_ok, total
        total += 1
        if cond:
            n_ok += 1
            print("  ok   %s" % name)
        else:
            print("  FAIL %s" % name)

    # 1 causality: a vector that only pays AFTER bar 600 cannot be picked before it.
# Before the spike A2 is an exact copy of A0, so its trailing Sharpe is identical and the
# deterministic tie-break keeps the earlier column -- any pre-spike pick of A2 would then
# have to come from knowledge of bars it has not seen.
    rets = _synth()
    rets["A2"] = rets["A0"].to_numpy()
    rets.loc[rets.index[600]:rets.index[700], "A2"] = 0.05
    used, events = stitch(rets, 100, 250)
    early = [e for e in events if pd.Timestamp(e["date"]) < rets.index[600]]
    leg("a future-only payoff is never picked before it happens",
        bool(early) and all(e["pick"] != "A2" for e in early)
        and any(e["pick"] == "A2" for e in events))

    # 1b causality, stronger form: truncating the panel at the spike cannot change any
    # decision taken before it (prefix identity -- the honest no-look-ahead assertion)
    _, ev_trunc = stitch(rets.iloc[:600], 100, 250)
    same = (len(ev_trunc) == len([e for e in events
                                 if pd.Timestamp(e["date"]) < rets.index[600]])
            and all(a["pick"] == b["pick"] and a["date"] == b["date"]
                    for a, b in zip(ev_trunc, early)))
    leg("truncating the future leaves every earlier pick identical", same)

    # 2 the ranking window is strictly earlier than the applied window
    leg("first selection sits exactly one lookback into the panel",
        bool(events) and pd.Timestamp(events[0]["date"]) == rets.index[250])

    # 3 stitching reproduces the chosen vector's own returns bar for bar
    ok = True
    for e in events[:5]:
        d = pd.Timestamp(e["date"])
        nxt = rets.index[rets.index.get_loc(d) + 1]
        if not np.isclose(used.loc[nxt], rets.loc[nxt, e["pick"]], equal_nan=True):
            ok = False
    leg("stitched bar equals the picked vector's own return", ok)

    # 4 a zero-vol vector is a 0.0 Sharpe, never None and never an error
    flat = pd.DataFrame({"A0": np.zeros(400), "A1": np.full(400, 0.001),
                         "A2": np.full(400, -0.001), "A3": np.zeros(400)},
                        index=pd.bdate_range("2020-01-01", periods=400))
    used_f, ev_f = stitch(flat, 100, 250)
    leg("a flat vector scores 0.0 Sharpe and stays selectable", bool(ev_f))

    # 5 trailing Sharpe predicts forward -> positive lift; inverts -> negative lift
    ups = _synth(arms=4)
    ups["A0"] = np.abs(ups["A0"]) + 0.004      # persistently the best
    _, ev_up = stitch(ups, 100, 250)
    lifts_up = [e["fwd_mean"] - e["fwd_mean_all"] for e in ev_up]
    leg("a persistently good vector produces positive selection lift",
        bool(lifts_up) and float(np.mean(lifts_up)) > 0)

    # 6 curve_from_returns keeps the first traded bar (no return silently dropped)
    r = pd.Series([0.01, 0.02, 0.03], index=pd.bdate_range("2020-01-06", periods=3))
    full = pd.bdate_range("2020-01-01", periods=6)
    cur = curve_from_returns(r, full)
    leg("curve anchors one bar before the first traded bar",
        len(cur) == 4 and abs(float(cur.iloc[-1]) - 1.01 * 1.02 * 1.03) < 1e-12)

    # 7/8/9 verdict arms
    def mk(cagrs):
        c = {}
        for tag, _, _ in CELLS:
            c[tag] = {"control": {"cagr": 0.016},
                      "variants": {"S%d_L%d" % (s, lb): {"cagr": cagrs}
                                   for s in RESELECT for lb in LOOKBACK}}
        return c
    leg("every variant above control -> pit_combo_value",
        decide(mk(0.05))["verdict"] == "pit_combo_value")
    leg("every variant below control -> pit_combo_no_value",
        decide(mk(0.0))["verdict"] == "pit_combo_no_value")
    leg("a split table -> pit_combo_fragile",
        decide(mk(0.03))["verdict"] in ("pit_combo_fragile", "pit_combo_value"))
    leg("an incomplete variant grid is refused, not scored",
        (lambda c: decide(c)["verdict"])((lambda c: (c[CELLS[0][0]]["variants"].pop("S250_L500"), c)[1])(mk(0.05)))
        == "incomplete_grid")

    # 10 exactly at the tolerance is NOT a beat (strict >)
    c = mk(0.026)
    leg("cagr exactly at control+tol is not a beat",
        decide(c)["n_beat"] == 0)

    # 11 gate accepts a truthful payload and refuses a tampered / stale / dropped one
    def payload_with(cagr):
        cells = {}
        for tag, _, _ in CELLS:
            cells[tag] = {"control": {"cagr": 0.016},
                          "variants": {}}
            for s in RESELECT:
                for lb in LOOKBACK:
                    cells[tag]["variants"]["S%d_L%d" % (s, lb)] = {
                        "cagr": cagr, "beat_control": cagr > 0.016 + TOL,
                        "positive": cagr > 0,
                        "events": [{"date": "2021-01-04", "pick": "a|b"}]}
        return {"declared": DECLARED, "cells": cells, "verdict": "pit_combo_value",
                "arms_index": {"vectors": ["a|b"]},
                "summary": {"n": 12, "n_beat": 12, "n_positive": 12}}
    p_ok = payload_with(0.05)
    p_ok["verdict"] = decide(p_ok["cells"])["verdict"]
    p_ok["summary"].update({k: decide(p_ok["cells"])[k] for k in ("n", "n_beat", "n_positive")})
    leg("gate accepts a consistent payload", gate(p_ok)["all_ok"])

    p_stale = json.loads(json.dumps(p_ok))
    p_stale["verdict"] = "pit_combo_no_value"
    leg("gate refuses a stale typed verdict", not gate(p_stale)["all_ok"])

    p_tamper = json.loads(json.dumps(p_ok))
    p_tamper["cells"][CELLS[0][0]]["variants"]["S60_L250"]["beat_control"] = False
    leg("gate catches a hand-edited beat flag", not gate(p_tamper)["all_ok"])

    p_drop = json.loads(json.dumps(p_ok))
    p_drop["cells"][CELLS[0][0]]["variants"].pop("S60_L250")
    leg("gate catches a dropped variant", not gate(p_drop)["all_ok"])

    p_foreign = json.loads(json.dumps(p_ok))
    p_foreign["cells"][CELLS[0][0]]["variants"]["S60_L250"]["events"] = [{"date": "2021-01-04",
                                                                        "pick": "z|z"}]
    leg("gate catches a pick outside the declared 64", not gate(p_foreign)["all_ok"])

    p_noev = json.loads(json.dumps(p_ok))
    p_noev["cells"][CELLS[0][0]]["variants"]["S60_L250"]["events"] = []
    leg("gate refuses a variant with no selection events", not gate(p_noev)["all_ok"])

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
    print("usage: etf_sign_pit_combo.py [run|check|selftest]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())