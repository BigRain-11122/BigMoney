# -*- coding: utf-8 -*-
"""REEVAL18_DRILL runner -- T-126 s2 (drill harness, REEVAL18_DRILL_P1).

Prereg FROZEN: research/REEVAL18_DRILL_P1.md (T-126 s1; O-20260930-1058 +
O-20260930-1101 merged product line). Post-run only sec.7/8 backfill.

Import-face law (prereg sec.2/6): wave replay primitives are IMPORTED
verbatim from the wave runners (tl1/tl2/tl3/tl4/tl5 -- run_candidate_curve*
families, atr20/gate/vol/yang state series, _d6_admit_core), engine +
strategies factory + live.paper panel machinery imported, never rewritten;
engine/exit_rules.py ZERO touch. Scoring constants IMPORTED from
science_gates frozen canon (REFORM_* -- 禁手抄判线).

Drill semantics (prereg sec.3): 18 roster configs replayed on the
cutoff-truncated core48 panel; scoring face = 2026 YTD window slice
(first trading day >= 2026-01-01 -> evidence_cutoff 2026-09-22); dual
cost legs (x1 base + x2 CostPatch(2)); regime segments via v3_state_series
+ REGIME_MAP 3-way proxy; REGIME_GUARD v1.0 current-state pinned cap =
disclosure face (capped application, NOT a composite sub-metric);
batch-internal BH-FDR + four-dim composite via g2_reform_fdr4d; two-stage
ranking = 0.70*composite + 0.30*current-style-fit (frozen weights);
per-wave top-N (REFORM_TOPN_PER_WAVE) on-board list.

Subcommands (prereg sec.6):
  prep        fail-closed gates: roster sha16 pin + G-PANEL (truncated
              face) + grammar faces + anchor gate (registered six) +
              patch self-test -> drill_manifest.json
  run         the burn: 18 cells x dual-cost, per-cell window faces,
              checkpoint jsonl append-per-cell (kill-safe resume),
              DRILL-burn json at 18/18
  finalize    sentinel determinism replay gate + D6 registered replay +
              g2_reform_fdr4d + two-stage ranking + on-board list +
              cap pin (regime_state.json asof-stamped) -> DRILL-<cutoff>.json
  selftest    hermetic offline fixtures (r116 law; no repo data files)
  status      checkpoint progress readout

Exit codes: 0 = ok/no-op, 1 = gate fail (VOID, zero products), 2 =
machinery error / blocked dependency (honest report, never mask).

Marks: +0 accounts / +0 SEED / ledger +0 (re-evaluation face, prereg
sec.0 D-41 trial-gate disclosure: replay consumes zero generation trials).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

import trial_labor_w1 as tl1
import trial_labor_w2 as tl2
import trial_labor_w3 as tl3
import trial_labor_w4 as tl4
import trial_labor_w5 as tl5
from config import PATHS
from engine.metrics import max_drawdown, sharpe
from firm.hr import load_trader
from live.paper import (anchor_gate, build_panels, load_core,
                        self_test_patches, v3_state_series)
from p5_random_entry import passive_rel
from p5c_virtual_timepoint import EVIDENCE_CUTOFF_GRID, WINDOWS
from science_gates import (CostPatch, REFORM_DIM_WEIGHTS, REFORM_Q_LEVEL,
                           REFORM_SUB_WEIGHTS, REFORM_TOPN_PER_WAVE,
                           _norm_cdf, _pct_ranks, bh_batch_fdr,
                           bootstrap_ci_sharpe, cutoff_meta,
                           deflated_sharpe_ratio, g2_reform_fdr4d,
                           t_from_sharpe)

# ------------------------------------------------------------------ frozen
WAVE = "REEVAL18_DRILL"
PREREG = "research/REEVAL18_DRILL_P1.md"
CUTOFF = EVIDENCE_CUTOFF_GRID                    # "2026-09-22" (sec.9.3)
WINDOW_START = "2026-01-01"
RES_DIR = os.path.join(PATHS.results_dir, "reeval18")
ROSTER_PATH = os.path.join(RES_DIR, "ROSTER.json")
ROSTER_SHA16 = "7c5ac06b3a243450"                # s0 roster pin (r470)
GRAMMAR_PATH = os.path.join(PATHS.results_dir, "trial_labor_w1",
                            "w1_grammar.json")
MANIFEST = os.path.join(RES_DIR, "drill_manifest.json")
CKPT = os.path.join(RES_DIR, "checkpoint_drill.jsonl")
REGIME_STATE = os.path.join(PATHS.results_dir, "regime_state.json")
CI_SEED = 20260923                              # judgment CI seed family
BATCH_N_TRIALS = 18                             # batch-internal DSR n_trials
CAP_LADDER = {"GREEN": 0.80, "YELLOW": 0.65, "ORANGE": 0.50, "RED": 0.20}
TWO_STAGE_W = (0.70, 0.30)                      # composite / current-style fit
REGIME_MAP = tl1.REGIME_MAP                     # GREEN->bull YELLOW->chop
                                                # ORANGE|RED->bear (T-22 s3)
W6 = WINDOWS["6m"]
PPY = 252.0
MIN_SEG_DAYS = 20                               # segment Sharpe floor
MIN_WIN_TRADES = 10                             # sample-thin label line
D6_CEILING = tl2.D6_CEILING
DRILL_MODULES = {"volatility.low_vol_long",
                 "composite_rotation.top_n_rotation",
                 "patterns.box_breakout"}
FIVE_MEMBER_EW = ["510300", "510050", "510500", "512100", "588000"]  # O-1555


def _j(x):
    """JSON-safe converter (numpy -> python primitives)."""
    if isinstance(x, dict):
        return {str(k): _j(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_j(v) for v in x]
    if isinstance(x, (np.floating,)):
        return round(float(x), 6)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, float):
        return round(x, 6) if math.isfinite(x) else None
    return x


def _sha16(path):
    h = hashlib.sha256(open(path, "rb").read())
    return h.hexdigest()[:16]


def _payload_sha(payload):
    s = json.dumps(_j(payload), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _load_roster():
    if not os.path.exists(ROSTER_PATH):
        raise FileNotFoundError(f"roster absent: {ROSTER_PATH}")
    got = _sha16(ROSTER_PATH)
    if got != ROSTER_SHA16:
        raise ValueError(f"roster sha16 drift: {got} != {ROSTER_SHA16}")
    d = json.load(open(ROSTER_PATH, encoding="utf-8"))
    rows = d["rows"]
    if len(rows) != BATCH_N_TRIALS:
        raise ValueError(f"roster rows {len(rows)} != {BATCH_N_TRIALS}")
    for r in rows:
        if r["wave"] not in ("w1", "w2", "w3", "w5"):
            raise ValueError(f"unknown wave {r['wave']}")
        if f"{r['module']}.{r['fn']}" not in DRILL_MODULES:
            raise ValueError(f"off-grammar module face {r['module']}.{r['fn']}")
        need = {"w1": 4, "w2": 5, "w3": 6, "w5": 8}[r["wave"]]
        if len(r["axis"]) != need:
            raise ValueError(f"axis arity {len(r['axis'])} != {need} "
                             f"for {r['candidate_id']}")
        if r["template_trader"] is None and r["family"] != "B":
            raise ValueError(f"null template on non-B row {r['candidate_id']}")
    return d


# --------------------------------------------------------------- panel state
def _fundamental_ok(close):
    """keep-ok mask, tl1 cmd_generate caliber verbatim (consistency law)."""
    try:
        bl = pd.read_csv(tl1.B_LAYER_MASK)
        ok_codes = set(bl.loc[bl["ok_static"] == True, "code"].astype(str))
        overlap = sorted(s for s in close.columns if s in ok_codes)
    except Exception:
        return None
    if not overlap:
        return None
    m = pd.DataFrame(False, index=close.index, columns=close.columns)
    for s in overlap:
        m[s] = True
    return m


def _build_state():
    """Cutoff-truncated core48 panel + shared replay series (prereg sec.2).

    G-PANEL is asserted on the TRUNCATED face (48 members, last bar ==
    CUTOFF, OHLCV) -- the raw CSVs now extend past the frozen cutoff, the
    drill reconstructs the judgment-face panel by truncation (restatement
    drift disclosed in the manifest).
    """
    tl1.GRAMMAR = json.load(open(GRAMMAR_PATH, encoding="utf-8"))
    faces = set(tl1.GRAMMAR.get("faces", {}))
    missing = DRILL_MODULES - faces
    if missing:
        raise ValueError(f"grammar faces missing: {sorted(missing)}")
    prices_full = load_core()
    cut = pd.Timestamp(CUTOFF)
    prices = {s: df[df.index <= cut] for s, df in prices_full.items()}
    bad = [s for s, df in prices.items()
           if len(df) < 60 or str(df.index[-1].date()) != CUTOFF
           or not {"open", "high", "low", "close", "volume"} <= set(df.columns)]
    if len(prices) != 48 or bad:
        raise ValueError(f"G-PANEL fail: {len(prices)}/48, bad={bad[:5]}")
    P = build_panels(prices)
    close = P["close"]
    idx = list(close.index)
    states = v3_state_series()
    st = {
        "prices": prices, "P": P, "close": close, "idx": idx,
        "states": states,
        "fundamental_ok": _fundamental_ok(close),
        "atr20": tl2.atr20_series(prices),
        "gate_state": tl3.gate_state_series(prices),
        "vol_state": tl4.vol_state_series(prices),
        "yang_state": tl5.yang_state_series(prices),
        "grammar_sha16": _sha16(GRAMMAR_PATH),
    }
    w0 = next(p for p, d in enumerate(idx) if str(d.date()) >= WINDOW_START)
    if w0 < 1:
        raise ValueError("window base needs >=1 pre-window bar")
    st["w0"], st["wbase"], st["wend"] = w0, w0 - 1, len(idx) - 1
    st["n_win_days"] = st["wend"] - w0 + 1
    return st


def _wave_run(st, wave, cand, template):
    """Dispatch to the wave's verbatim curve fn; returns (eq, trades, metrics)."""
    a = dict(cand=cand, template=template, prices=st["prices"], P=st["P"],
             states=st["states"], fundamental_ok=st["fundamental_ok"])
    if wave == "w1":
        eq, trades, metrics, _params, _patch = tl1.run_candidate_curve(**a)
    elif wave == "w2":
        a["atr20"] = st["atr20"]
        eq, trades, metrics, _pa, _pt, _fired = tl2.run_candidate_curve_w2(**a)
    elif wave == "w3":
        a["atr20"] = st["atr20"]
        a["gate_state"] = st["gate_state"]
        (eq, trades, metrics, _pa, _pt, _fired,
         _gz) = tl3.run_candidate_curve_w3(**a)
    elif wave == "w5":
        a["atr20"] = st["atr20"]
        a["gate_state"] = st["gate_state"]
        a["vol_state"] = st["vol_state"]
        a["yang_state"] = st["yang_state"]
        (eq, trades, metrics, _pa, _pt, _fired, _gz, _vz,
         _yz) = tl5.run_candidate_curve_w5(**a)
    else:
        raise ValueError(f"unknown wave {wave}")
    return eq, trades, metrics


# ------------------------------------------------------------- window faces
def _seg_sharpe(rets):
    """Sharpe of a return subset, engine.metrics convention (ddof=1, x252)."""
    if len(rets) < 2:
        return None
    eq = pd.Series((1.0 + pd.Series(rets)).cumprod())
    return round(float(sharpe(eq)), 4)


def _window_faces(eq, eq2, st, cap):
    """Per-cell window metric faces (prereg sec.3; pure in (eq, eq2, st, cap))."""
    idx, w0, wbase, wend = st["idx"], st["w0"], st["wbase"], st["wend"]
    eq_w = eq.iloc[wbase:]
    r = eq_w.pct_change().dropna()
    n = int(len(r))
    if n < 20 or float(eq.iloc[wbase]) <= 0:
        return {"degenerate": True, "n_win_days": n}
    sharpe_win = float(sharpe(eq_w))
    total = float(eq.iloc[-1] / eq.iloc[wbase] - 1.0)
    ann = (1.0 + total) ** (PPY / n) - 1.0
    # rolling 6m beats vs passive (passive_rel caliber, window-restricted)
    k = tot = 0
    p = w0
    while p + W6 - 1 <= wend:
        sdate, edate = idx[p], idx[p + W6 - 1]
        syms = st["close"].columns[st["close"].loc[sdate].notna()]
        pret = float(passive_rel(st["close"], syms, sdate, edate).iloc[-1] - 1.0)
        cret = float(eq.iloc[p + W6 - 1] / eq.iloc[p] - 1.0)
        k += int(cret > pret)
        tot += 1
        p += 1
    beat6m = {"k": k, "n": tot, "rate": round(k / tot, 6) if tot else 0.0}
    # regime segments on the window (REGIME_MAP 3-way proxy)
    s_series = st["states"].reindex(idx[w0:wend + 1])
    seg_rets = {"bull": [], "chop": [], "bear": []}
    for pos, d in enumerate(idx[w0:wend + 1]):
        v = s_series.iloc[pos]
        seg = REGIME_MAP.get(v, "bear") if v == v else "bear"
        seg_rets[seg].append(float(r.iloc[pos]))
    segs = {}
    for seg, rets in seg_rets.items():
        segs[seg] = {"n_days": len(rets),
                     "sharpe": _seg_sharpe(rets) if len(rets) >= MIN_SEG_DAYS
                     else None}
    live_segs = [v["sharpe"] for v in segs.values() if v["sharpe"] is not None]
    seg_min = round(min(live_segs), 4) if live_segs else None
    ci = bootstrap_ci_sharpe([float(x) for x in r.values], seed=CI_SEED)
    dsr = deflated_sharpe_ratio([float(x) for x in r.values],
                                n_trials=BATCH_N_TRIALS)
    t = t_from_sharpe(sharpe_win, n)
    p_val = 1.0 - float(_norm_cdf(t))
    # x2 cost leg (disclosure + robust sub-metric)
    eq2_w = eq2.iloc[wbase:]
    sharpe_x2 = float(sharpe(eq2_w)) if len(eq2_w) > 21 else None
    # current-state pinned cap application (disclosure face)
    r_cap = pd.Series([cap * float(x) for x in r.values])
    eq_cap = (1.0 + r_cap).cumprod()
    ann_cap = float(eq_cap.iloc[-1] - 1.0)
    ann_cap = (1.0 + ann_cap) ** (PPY / n) - 1.0 if n else None
    sharpe_cap = float(sharpe(eq_cap))
    # window trade rows (exit-event caliber, disclosed)
    trades = st.get("_last_trades") or []
    n_trades_win = sum(1 for tr in trades
                       if str(idx[w0].date()) <= tr["date"]
                       <= str(idx[wend].date()))
    out = {
        "degenerate": False, "n_win_days": n,
        "sharpe_win": round(sharpe_win, 4),
        "annualized_ret": round(ann, 6),
        "beat6m": beat6m,
        "regime_segments": segs, "regime_min_sharpe": seg_min,
        "bootstrap_ci_low": round(float(ci["ci95_low"]), 4),
        "batch_dsr": round(float(dsr["dsr"]), 6),
        "t_stat": round(float(t), 4), "p_value": round(p_val, 6),
        "sharpe_win_x2": round(sharpe_x2, 4) if sharpe_x2 is not None else None,
        "cap_face": {"cap": cap, "annualized_ret_capped": round(ann_cap, 6),
                     "sharpe_capped": round(sharpe_cap, 4)},
        "n_trades_win": int(n_trades_win),
        "sample_thin": bool(n_trades_win < MIN_WIN_TRADES),
        "max_drawdown_win": round(float(max_drawdown(eq.iloc[wbase:])), 4),
    }
    return out


def _five_member_baseline_ann(st):
    """O-1126 ratified EW baseline (O-1555 frozen universe), window face."""
    idx, w0, wbase, wend = st["idx"], st["w0"], st["wbase"], st["wend"]
    sdate, edate = idx[w0], idx[wend]
    five = [c for c in FIVE_MEMBER_EW if c in st["close"].columns]
    if len(five) != 5:
        raise ValueError(f"five-member universe incomplete on panel: {five}")
    rel = passive_rel(st["close"], five, sdate, edate)
    n = wend - w0 + 1
    total = float(rel.iloc[-1] - 1.0)
    return {"annualized_ret": round((1.0 + total) ** (PPY / n) - 1.0, 6),
            "total_ret": round(total, 6), "n_days": n,
            "universe": FIVE_MEMBER_EW}


# ------------------------------------------------------------------ cells
def _roster_cand(row):
    return {"candidate_id": row["candidate_id"], "family": row["family"],
            "module": row["module"], "fn": row["fn"],
            "sig_params": row["sig_params"], "axis": list(row["axis"]),
            "wave": row["wave"]}


def _run_cell(st, row, cap):
    cand = _roster_cand(row)
    template = None
    if row["template_trader"]:
        template = load_trader(row["template_trader"])
    eq, trades, metrics = _wave_run(st, row["wave"], cand, template)
    st["_last_trades"] = trades
    with CostPatch(2):
        eq2, _t2, _m2 = _wave_run(st, row["wave"], cand, template)
    faces = _window_faces(eq, eq2, st, cap)
    faces["candidate_id"] = row["candidate_id"]
    faces["wave"] = row["wave"]
    faces["family"] = row["family"]
    faces["family_pbo"] = row.get("family_pbo")
    faces["dsr_archive"] = row.get("dsr")            # roster frozen face
    faces["cell_id"] = row.get("cell_id")
    return _j(faces)


# ------------------------------------------------------------------ prep
def cmd_prep() -> int:
    print(f"=== {WAVE} prep (prereg FROZEN {PREREG}) ===")
    try:
        roster = _load_roster()
    except Exception as e:
        print(f"PREP-GATE FAIL: roster -- {e}")
        return 1
    if not self_test_patches():
        print("PREP-GATE FAIL: patch self-test")
        return 1
    try:
        st = _build_state()
    except Exception as e:
        print(f"PREP-GATE FAIL: state build -- {e}")
        return 2
    # G-ANCHOR: registered six replay vs live anchors (W1 caliber)
    anchors = {}
    for t in tl1.A_TEMPLATES:
        trader = load_trader(t["trader_id"])
        a = anchor_gate(trader, st["prices"])
        if not a["ok"]:
            print(f"PREP-GATE FAIL: live anchor drift {t['trader_id']}")
            return 1
        anchors[t["trader_id"]] = {"ok": True}
    man = {
        "wave": WAVE, "prereg": PREREG, "evidence_cutoff": CUTOFF,
        **cutoff_meta(CUTOFF),
        "roster_sha16": ROSTER_SHA16,
        "grammar_sha16": st["grammar_sha16"],
        "window": {"start": str(st["idx"][st["w0"]].date()),
                   "end": str(st["idx"][st["wend"]].date()),
                   "base_date": str(st["idx"][st["wbase"]].date()),
                   "n_days": st["n_win_days"]},
        "panel": {"members": 48, "last_bar": CUTOFF,
                  "truncation_note": "raw CSVs extend past frozen cutoff; "
                  "judgment-face panel reconstructed by <=cutoff truncation "
                  "(qfq restatement drift disclosed, prereg sec.3)"},
        "anchors": {k: v for k, v in anchors.items()},
        "batch_n_trials": BATCH_N_TRIALS, "ci_seed": CI_SEED,
        "two_stage_w": {"composite": TWO_STAGE_W[0],
                        "fit": TWO_STAGE_W[1]},
        "cap_ladder": CAP_LADDER,
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    json.dump(_j(man), open(MANIFEST, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"prep PASS: panel 48/48, anchors {len(anchors)}/6, window "
          f"{man['window']['start']}..{man['window']['end']} "
          f"({st['n_win_days']}d), roster sha16 {ROSTER_SHA16}")
    return 0


# ------------------------------------------------------------------- run
def _ckpt_ids():
    if not os.path.exists(CKPT):
        return set()
    ids = set()
    for line in open(CKPT, encoding="utf-8"):
        line = line.strip()
        if line:
            ids.add(json.loads(line)["candidate_id"])
    return ids


def cmd_run() -> int:
    print(f"=== {WAVE} run (18 cells x dual-cost) ===")
    if not os.path.exists(MANIFEST):
        print("RUN-GATE FAIL: prep manifest absent (run prep first)")
        return 1
    roster = _load_roster()
    st = _build_state()
    # cap pin read at burn start (finalize re-stamps asof; prereg sec.3)
    reg = json.load(open(REGIME_STATE, encoding="utf-8"))
    cap = CAP_LADDER.get(reg.get("state"))
    if cap is None:
        print(f"RUN-GATE FAIL: regime state {reg.get('state')} off-ladder")
        return 1
    done = _ckpt_ids()
    t0 = time.time()
    n_new = 0
    for row in roster["rows"]:
        cid = row["candidate_id"]
        if cid in done:
            continue
        faces = _run_cell(st, row, cap)
        rec = {"candidate_id": cid, "sha256": _payload_sha(faces),
               "payload": faces}
        with open(CKPT, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        n_new += 1
        print(f"  cell {cid}: sharpe_win={faces.get('sharpe_win')} "
              f"p={faces.get('p_value')} dsr={faces.get('batch_dsr')} "
              f"[{time.time() - t0:.1f}s]")
    have = _ckpt_ids()
    if len(have) < BATCH_N_TRIALS:
        print(f"run PARTIAL: {len(have)}/{BATCH_N_TRIALS} cells on checkpoint "
              f"(resume-safe); rerun to complete")
        return 0
    # 18/18 -> burn product
    rows = {}
    for line in open(CKPT, encoding="utf-8"):
        line = line.strip()
        if line:
            r = json.loads(line)
            rows[r["candidate_id"]] = r
    burn = {
        "wave": WAVE, "prereg": PREREG, "evidence_cutoff": CUTOFF,
        **cutoff_meta(CUTOFF), "roster_sha16": ROSTER_SHA16,
        "cap_pin_at_burn": {"state": reg.get("state"), "cap": cap,
                            "asof": reg.get("asof")},
        "sentinel_candidate_id": roster["rows"][0]["candidate_id"],
        "sentinel_sha256": rows[roster["rows"][0]["candidate_id"]]["sha256"],
        "cells": {cid: r["payload"] for cid, r in rows.items()},
        "ledger_delta": 0, "marks": "+0",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    out = os.path.join(RES_DIR, f"DRILL-burn-{CUTOFF}.json")
    json.dump(_j(burn), open(out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"run DONE: 18/18 cells -> {out} ({time.time() - t0:.1f}s total)")
    return 0


# -------------------------------------------------------------- finalize
def _registered_window_rets(st, cap):
    """Registered six replayed via the grammar default-axis path (W1 face);
    returns {trader_id: window daily-return pd.Series}."""
    out = {}
    wbase = st["wbase"]
    for t in tl1.A_TEMPLATES:
        cand = {"module": t["module"], "fn": t["fn"],
                "sig_params": t["sig_params"],
                "axis": list(tl1.DEFAULT_AXIS)}
        eq, _tr, _mt = _wave_run(st, "w1", cand, t)
        r = eq.iloc[wbase:].pct_change().dropna()
        out[t["trader_id"]] = pd.Series(
            [round(float(x), 8) for x in r.values],
            index=list(r.index))
    return out


def cmd_finalize() -> int:
    print(f"=== {WAVE} finalize ===")
    burn_path = os.path.join(RES_DIR, f"DRILL-burn-{CUTOFF}.json")
    if not os.path.exists(burn_path):
        print("FINALIZE-GATE FAIL: burn product absent (run not complete)")
        return 1
    burn = json.load(open(burn_path, encoding="utf-8"))
    roster = _load_roster()
    st = _build_state()
    # -- determinism sentinel: full dual-cost replay of the first roster row
    reg = json.load(open(REGIME_STATE, encoding="utf-8"))
    cap = CAP_LADDER.get(reg.get("state"))
    if cap is None:
        print(f"FINALIZE-GATE FAIL: regime state off-ladder")
        return 1
    srow = roster["rows"][0]
    if srow["candidate_id"] != burn["sentinel_candidate_id"]:
        print("FINALIZE-GATE FAIL: sentinel id drift")
        return 1
    sfaces = _run_cell(st, srow, cap)
    s_sha = _payload_sha(sfaces)
    det_ok = s_sha == burn["sentinel_sha256"]
    if not det_ok:
        print(f"FINALIZE-GATE FAIL: sentinel determinism drift "
              f"{s_sha[:12]} != {burn['sentinel_sha256'][:12]}")
        return 2
    # -- member metrics + batch p-values
    cells = burn["cells"]
    base_ann = _five_member_baseline_ann(st)
    member_metrics, batch_p, cand_rets = {}, {}, {}
    for cid, c in cells.items():
        if c.get("degenerate"):
            continue
        member_metrics[cid] = {
            "ret": {
                "sharpe_full_L": c["sharpe_win"],
                "annualized_ret_L": c["annualized_ret"],
                "return_ceiling_O1126": round(
                    c["annualized_ret"] - base_ann["annualized_ret"], 6),
                "beat6m_rate_L": c["beat6m"]["rate"],
                "beat12m_rate_L": None,   # window < 12m (prereg sec.0)
            },
            "robust": {
                "cost_x2_sharpe_L": c["sharpe_win_x2"],
                "regime_min_sharpe_L": c["regime_min_sharpe"],
                "bootstrap_ci_low_L": c["bootstrap_ci_low"],
            },
            "anti_overfit": {
                "family_pbo": c["family_pbo"],
                "d6_max_abs_corr": None,  # filled by D6 pass
            },
            "anti_luck": {"batch_dsr": c["batch_dsr"]},
        }
        batch_p[cid] = c["p_value"]
    # -- D6: registered six window returns + candidate window returns
    # (candidate window rets re-derived from the checkpointed curves is not
    # possible without re-run; re-run all 18 is the honest D6 caliber -> the
    # burn already carries p/dsr; for D6 corr we re-run the 18 window curves)
    reg_rets = _registered_window_rets(st, cap)
    cand_rets = {}
    for row in roster["rows"]:
        cid = row["candidate_id"]
        if cid not in member_metrics:
            continue
        cand = _roster_cand(row)
        template = load_trader(row["template_trader"]) \
            if row["template_trader"] else None
        eq, _tr, _mt = _wave_run(st, row["wave"], cand, template)
        r = eq.iloc[st["wbase"]:].pct_change().dropna()
        cand_rets[cid] = pd.Series([round(float(x), 8) for x in r.values],
                                   index=list(r.index))
    dsr_by_id = {cid: member_metrics[cid]["anti_luck"]["batch_dsr"]
                 for cid in member_metrics}
    admitted, rejected, d6 = tl2._d6_admit_core(
        sorted(member_metrics), cand_rets, reg_rets, dsr_by_id)
    for cid, d in d6.items():
        member_metrics[cid]["anti_overfit"]["d6_max_abs_corr"] = \
            d["max_corr_vs_registered"]
    # -- L3 reform gate (frozen constants import, 禁手抄)
    g2 = g2_reform_fdr4d(member_metrics, REFORM_DIM_WEIGHTS,
                         REFORM_SUB_WEIGHTS, batch_p, q=REFORM_Q_LEVEL)
    if g2.get("error"):
        print(f"FINALIZE-GATE FAIL: reform gate error {g2['error']}")
        return 2
    # -- two-stage ranking (prereg sec.3 frozen weights)
    cur_state = reg.get("state")
    fit_seg = REGIME_MAP.get(cur_state, "bear")
    fit_raw = {}
    for cid in member_metrics:
        seg = cells[cid]["regime_segments"].get(fit_seg) or {}
        fit_raw[cid] = seg.get("sharpe")
    fit_pct = _pct_ranks({cid: fit_raw[cid] for cid in fit_raw})
    two_stage = {}
    for cid, sc in g2["members"].items():
        comp = sc["composite"]
        fp = fit_pct.get(cid)
        final = None
        if comp is not None and fp is not None:
            final = round(TWO_STAGE_W[0] * comp + TWO_STAGE_W[1] * fp, 6)
        two_stage[cid] = {"composite": comp, "fit_pct": round(fp, 6)
                          if fp is not None else None,
                          "final_score": final,
                          "fdr_pass": sc["fdr_pass"], "bh_q": sc["bh_q"],
                          "p": sc["p"], "eligible_reform": sc["eligible_reform"],
                          "d6_admitted": cid in admitted}
    eligible = [cid for cid, t in two_stage.items()
                if t["eligible_reform"] and t["d6_admitted"]
                and t["final_score"] is not None]
    eligible.sort(key=lambda c: (-two_stage[c]["final_score"], c))
    onboard, per_wave = [], {}
    for cid in eligible:
        w = cells[cid]["wave"]
        if per_wave.get(w, 0) >= REFORM_TOPN_PER_WAVE:
            continue
        per_wave[w] = per_wave.get(w, 0) + 1
        onboard.append(cid)
    prod = {
        "wave": WAVE, "prereg": PREREG, "evidence_cutoff": CUTOFF,
        **cutoff_meta(CUTOFF), "roster_sha16": ROSTER_SHA16,
        "window": {"start": str(st["idx"][st["w0"]].date()),
                   "end": str(st["idx"][st["wend"]].date()),
                   "n_days": st["n_win_days"]},
        "cap_pin": {"state": cur_state, "cap": cap,
                    "asof": reg.get("asof"),
                    "source": "results/regime_state.json",
                    "note": "GREEN x HOT 0.95 upgrade = live application "
                            "face, out of drill scope (prereg sec.3)"},
        "five_member_ew_baseline": base_ann,
        "sentinel_determinism": {"candidate_id": srow["candidate_id"],
                                 "sha256": s_sha, "match": det_ok},
        "cells": cells, "member_metrics": member_metrics,
        "batch_p_values": batch_p,
        "g2_reform": _j(g2), "d6": {"admitted": admitted,
                                    "rejected": rejected, "table": d6},
        "two_stage": two_stage,
        "fit_segment": {"state": cur_state, "segment": fit_seg},
        "onboard_list": [{"candidate_id": cid,
                          "wave": cells[cid]["wave"],
                          "final_score": two_stage[cid]["final_score"],
                          "composite": two_stage[cid]["composite"],
                          "fit_pct": two_stage[cid]["fit_pct"]}
                         for cid in onboard],
        "s4_note": "on-board list -> 48h CEO report + TRIAL-R18 paper "
                   "accounts = separate slice per prereg sec.3",
        "ledger_delta": 0, "marks": "+0",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    out = os.path.join(RES_DIR, f"DRILL-{CUTOFF}.json")
    json.dump(_j(prod), open(out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    n_fdr = sum(1 for c in g2["members"].values() if c["fdr_pass"])
    print(f"finalize DONE -> {out}")
    print(f"  fdr_pass {n_fdr}/18 | d6 admitted {len(admitted)} | "
          f"eligible {len(eligible)} | onboard {len(onboard)} "
          f"(fit_seg={fit_seg} cap={cap} @{cur_state})")
    return 0


# --------------------------------------------------------------- selftest
def _mk_series(vals, start="2025-06-02", freq="B"):
    return pd.Series(vals, index=pd.date_range(start, periods=len(vals),
                                               freq=freq))


def cmd_selftest() -> int:
    print(f"=== {WAVE} selftest (hermetic offline fixtures) ===")
    fails = []

    def chk(name, cond):
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            fails.append(name)

    # (a) window faces math on a synthetic equity curve
    idx = list(pd.date_range("2025-11-03", periods=130, freq="B"))
    eq = pd.Series(np.linspace(1.0, 1.30, 130), index=idx)
    close = pd.DataFrame({"510300": np.linspace(4.0, 4.3, 130),
                          "510050": np.linspace(3.0, 3.1, 130)}, index=idx)
    w0 = next(p for p, d in enumerate(idx) if str(d.date()) >= WINDOW_START)
    st_l = {"idx": idx, "w0": w0, "wbase": w0 - 1, "wend": len(idx) - 1,
            "close": close,
            "states": pd.Series(["GREEN"] * 40 + ["ORANGE"] * 90,
                                index=idx[:130])}
    # shrink W6 for the synthetic window so at least one 6m fits
    global W6
    W6_save = W6
    W6 = 20
    try:
        f = _window_faces(eq, eq * 0.98, st_l, cap=0.5)
        chk("window faces: non-degenerate", not f.get("degenerate"))
        chk("window faces: annualized > 0", f["annualized_ret"] > 0)
        chk("window faces: cap halves ann",
            abs(f["cap_face"]["annualized_ret_capped"]
                - ((1 + f["annualized_ret"]) ** 0.5 - 1)) < 0.05)
        chk("window faces: beat6m counted", f["beat6m"]["n"] >= 1)
        chk("window faces: segs live",
            f["regime_min_sharpe"] is not None)
        chk("window faces: dsr in (0,1)", 0.0 <= f["batch_dsr"] <= 1.0)
        chk("window faces: p in (0,1)", 0.0 <= f["p_value"] <= 1.0)
        chk("window faces: x2 sharpe carried",
            f["sharpe_win_x2"] is not None)
    finally:
        W6 = W6_save
    # (b) t + p-value direction (higher Sharpe -> lower p)
    rng_b = np.random.default_rng(11)
    noise = list(rng_b.normal(0.0, 0.01, 60))
    r_hi = [0.002 + x for x in noise]
    r_lo = [0.0002 + x for x in noise]
    t_hi = t_from_sharpe(float(sharpe(_mk_series(
        np.cumprod([1 + x for x in r_hi])))), 60)
    t_lo = t_from_sharpe(float(sharpe(_mk_series(
        np.cumprod([1 + x for x in r_lo])))), 60)
    chk("t face direction", t_hi > t_lo)
    chk("p = 1 - Phi(t) in (0,1)",
        0.0 < 1.0 - float(_norm_cdf(t_hi)) < 1.0)
    # (c) BH FDR fixture (known pass set)
    fdr = bh_batch_fdr({"a": 0.001, "b": 0.02, "c": 0.5, "d": None}, q=0.10)
    chk("bh fixture: a passes", fdr["items"]["a"]["fdr_pass"])
    chk("bh fixture: c fails", not fdr["items"]["c"]["fdr_pass"])
    chk("bh fixture: d refused honestly",
        fdr["items"]["d"]["bh_q"] is None and not fdr["items"]["d"]["fdr_pass"])
    # (d) composite + renormalization fixture (missing sub renorms)
    mm = {f"c{i}": {"ret": {"sharpe_full_L": float(i)},
                    "robust": {"cost_x2_sharpe_L": float(i)},
                    "anti_overfit": {"family_pbo": float(10 - i)},
                    "anti_luck": {"batch_dsr": float(i) / 10}}
         for i in range(1, 4)}
    g2 = g2_reform_fdr4d(mm, REFORM_DIM_WEIGHTS, REFORM_SUB_WEIGHTS,
                         {f"c{i}": 0.001 for i in range(1, 4)})
    chk("reform fixture: no error", not g2.get("error"))
    chk("reform fixture: monotone rank order",
        g2["members"]["c3"]["composite"]
        > g2["members"]["c1"]["composite"])
    chk("reform fixture: all eligible",
        all(m["eligible_reform"] for m in g2["members"].values()))
    # (e) two-stage final math
    fs = TWO_STAGE_W[0] * 0.8 + TWO_STAGE_W[1] * 0.4
    chk("two-stage math", abs(fs - 0.68) < 1e-12)
    # (f) D6 fixture: registered clone rejected, cluster collapse keeps best
    rng = np.random.default_rng(7)
    base = list(rng.normal(0.001, 0.01, 200))
    idx_d = list(pd.date_range("2026-01-05", periods=200, freq="B"))
    reg_r = {"REG": pd.Series(base, index=idx_d)}
    cand_r = {
        "CLONE": pd.Series(base, index=idx_d),
        "TWIN": pd.Series([x * 0.98 + 0.0002 for x in base], index=idx_d),
        "IND": pd.Series(list(rng.normal(0.0005, 0.008, 200)), index=idx_d)}
    adm, rej, d6t = tl2._d6_admit_core(
        ["CLONE", "TWIN", "IND"], cand_r, reg_r,
        {"CLONE": 0.5, "TWIN": 0.6, "IND": 0.4})
    chk("d6 fixture: clone rejected",
        "CLONE" in [r["candidate_id"] for r in rej])
    chk("d6 fixture: independent admitted", "IND" in adm)
    # (g) roster pin + wave arity validation (file-shape face, no data load)
    try:
        _load_roster()
        chk("roster sha16 + arity gate", True)
    except Exception as e:
        chk(f"roster gate: {e}", False)
    # (h) cap ladder completeness
    chk("cap ladder 4 states", set(CAP_LADDER) == {"GREEN", "YELLOW",
                                                   "ORANGE", "RED"})
    n = len(fails)
    print(f"selftest: {'ALL PASS' if not n else f'{n} FAIL'}")
    return 0 if not n else 1


# ------------------------------------------------------------------ status
def cmd_status() -> int:
    have = sorted(_ckpt_ids())
    print(f"{WAVE}: checkpoint {len(have)}/{BATCH_N_TRIALS} cells")
    burn = os.path.join(RES_DIR, f"DRILL-burn-{CUTOFF}.json")
    prod = os.path.join(RES_DIR, f"DRILL-{CUTOFF}.json")
    print(f"  burn product: {'present' if os.path.exists(burn) else 'absent'}")
    print(f"  final product: {'present' if os.path.exists(prod) else 'absent'}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=WAVE)
    ap.add_argument("cmd", choices=["prep", "run", "finalize", "selftest",
                                    "status"])
    a = ap.parse_args(argv)
    try:
        if a.cmd == "prep":
            return cmd_prep()
        if a.cmd == "run":
            return cmd_run()
        if a.cmd == "finalize":
            return cmd_finalize()
        if a.cmd == "selftest":
            return cmd_selftest()
        return cmd_status()
    except KeyboardInterrupt:
        print("interrupted (checkpoint preserved)")
        return 2
    except Exception as e:                       # machinery error, never mask
        import traceback
        traceback.print_exc()
        print(f"ERROR: {type(e).__name__}: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
