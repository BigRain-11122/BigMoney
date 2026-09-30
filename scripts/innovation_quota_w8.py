# -*- coding: utf-8 -*-
"""INNOVATION_QUOTA_W8 runner -- COV-SHRINK-AB-P1 covariance-shrinkage
A/B paired judged batch (INNOVATION-QUOTA-SLOT-8, zoo #89
cov_shrinkage_lw adoption route: "sample cov vs shrunk cov fed to the
SAME pipeline, pre-registered A/B variant batch").

Laws frozen in research/INNOVATION_QUOTA_W8_PREREG.md (r448 bm-b berth +
r450 bm-b freeze; construction probe facts frozen
results/_r449bmb_w8_probe.json; D6 cells probe frozen
results/_r450bmb_w8_d6_probe_facts.json; seed 20325500 three-step law
ALL GREEN import view, results/_r450bmb_w8_seed_law_facts.json):

  panel   28-member t27 FROZEN_ROSTER x1/x2 sleeves via
          iv6_portfolio.member_run_iv6 (anchor-cum-sleeve reuse, t27
          verbatim; 56 engine member runs = non-search machinery faces,
          disclosed). G-PANEL: matrix 1630x28 / 2020-01-03..2026-09-22
          / cutoff 2026-09-22 (P-5C binding, registration-pinned).
  build   verbatim-import from results/_r449bmb_w8_probe.py (r456
          paradigm, single source zero re-implementation drift):
          A arm = t27 mdp_weights VERBATIM (sample cov, production
          recipe); B arm = mdp_weights_cov on hand-rolled Ledoit-Wolf
          2004 JMV shrunk cov (mu*I target, N=n-1 pandas ddof=1
          caliber, sklearn absent = zero new dep). Rolling 252d window
          @ 21td anchors over the x1 matrix; weights decided at anchor
          close, effective next bar (T+1 causality, W6/W7 same law);
          66 anchors, 16 singular sample-cov windows (the ill-conditioned
          inverse-defense target phenomenon, live-fired).
  degenerate-window policy (frozen sec.C1-5): A arm at singular anchors
          CARRIES the last computable weights (production recipe
          verbatim, pinv forbidden); paired-diff per-anchor faces
          exclude singular anchors (50 valid, count disclosed);
          accrual lo = first valid anchor's effective bar.
  cells   4 cells = 2 arms x 2 cost faces (every cell pays into N_eff,
          W6 counting law): COVSHRINK-A-X1 (production-recipe arm,
          judged), COVSHRINK-A-X2, COVSHRINK-B-X1 (shrunk arm, judged),
          COVSHRINK-B-X2. x2 face reuses the x1-estimated weights
          (T-27 precedent) on x2 sleeves; anchor transition cost =
          |dw|_1 x COST_X1_RATE (x1) / COST_X2_RATE (x2) booked on
          effective days, initial deployment included (cost-always-on
          iron law).
  paired  primary hypothesis face = paired-difference series
          D_x1 = B_x1_net - A_x1_net (deterministic paired diff, no
          random-baseline null family per prereg sec.4); J4-style 12m
          pooled beat rates per arm vs 510300 B&H passive (T-28
          caliber; canon production record 0.4854 = cross-batch
          disclosure only, non-gate) + paired B>A beat rate.
  starts  K=1000 virtual starts (rng([SEED, k]), windows 6m/12m/24m =
          126/252/504 td), 100 random split windows (k in [1000,1100),
          rng([SEED, 1000+k])), same-sign rate >= 80% = segment-stable.
  gates   per-cell: G1'v2 via science_gates.g1_prime_v2
          (batch_cells=4, default core48 pool, live-read passive);
          DSR via deflated_sharpe_ratio; family PBO via screening.pbo
          cscv_pbo CSCV-8 over the 4-cell matrix; G2 via
          g2_registration_v2. Primary methodology gate = G1' on the
          paired-diff series with passive_override=0.0 (spread face
          has no passive term; line = max(0.10, null extreme term),
          live-read, no hand-copied lines) + paired G2 (same family
          PBO) + x2-paired direction consistency (D_x2 sharpe > 0).
          METHODOLOGY-ADOPT-ELIGIBLE = all three; else judged-negative
          family closure (zoo #89 A/B route tested and closed).
  d6      frozen at the r450 probe window verbatim (prereg sec.1):
          batch-internal A-vs-B (variant face, both cells burn), vs
          T33 four rotation cells (merge clause at 0.7), vs registered
          six (disclose-only), vs B_MAXDIV production static assembly
          face (the upgrade target itself, same-assembly confirmation
          face by family design, merge clause N/A -- prereg sec.1).
Products (prereg sec.6): results/innovation_quota/COV-SHRINK-AB-P1.json
(top evidence_cutoff + cutoff_meta + panel/anchor faces + cells + paired
faces + virtual starts + splits + frozen d6 + gates + funnel + ledger).

Usage: run | verify | selftest   (exit 0 ok; 2 = fail-closed gate
refusal, incl. the r450 landed-state guard: a judged product
(trials_ledger present, read from CONTENT not existence/timestamps)
refuses re-run rc=2 unless INNOVATION_QUOTA_W8_REFINALIZE=1).
'verify' = real-panel G-ANCHOR reconcile only (read-only, no engine
member runs beyond the sleeve build, no product, no ledger).
"""
import argparse
import hashlib
import json
import math
import os
import shutil
import sys
import tempfile
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "results"))

import science_gates as SG                      # shared gate library (O-2250)
from ce_transfer import COST_X1_RATE            # x1 = 13.041bp/side
from science_gates import COST_X2_RATE          # x2 = 26.082bp/side
from screening.pbo import cscv_pbo              # family PBO CSCV-8

# frozen construction single source (r456 verbatim-import paradigm)
from _r449bmb_w8_probe import (ROLL, CADENCE, arm_face, lw_shrink_cov,
                               mdp_weights_cov, _selfcheck_lw)
from t27_blend_tournament import (FROZEN_ROSTER, mdp_weights,
                                  daily_ret_matrix)
from iv6_portfolio import _init_worker, member_run_iv6
from parallel_runner import run_cells_parallel, worker_cap

OUT_DIR = os.path.join(ROOT, "results", "innovation_quota")
OUT_JSON = os.path.join(OUT_DIR, "COV-SHRINK-AB-P1.json")
OUT_DIR_RESULTS = os.path.dirname(OUT_DIR)      # results root for lib faces
PROBE_FACTS = os.path.join(ROOT, "results", "_r449bmb_w8_probe.json")
D6_FACTS = os.path.join(ROOT, "results", "_r450bmb_w8_d6_probe_facts.json")
MACHINE_JSON = os.path.join(ROOT, "fleet", "machine.json")
ATT_JSON_SHARED = os.path.join(ROOT, "results", "gate_attrition.json")
PASSIVE_CSV = os.path.join(ROOT, "data", "daily", "510300.csv")

BATCH_NAME = "COV_SHRINK_AB_P1"
BATCH_CELLS = 4                    # s0 counting law: every cell pays
SEED_KEY = "innovation_quota_w8_covshrink"
PBP = SG.PERIODS_PER_YEAR          # 252 gate-chain single-source
K_STARTS = 1000
K_SPLITS = 100
WIN_DAYS = {"6m": 126, "12m": 252, "24m": 504}
D6_REJECT = 0.7                    # prereg sec.1 merge-clause line
TURNOVER_BUDGET = 50.0            # prereg sec.3 disclosure budget / year
FROZEN_ANCHOR_DAYS = ("2021-02-22", "2024-07-08", "2026-09-03")
# first valid / valid[24] of 50 (lower-middle) / last valid -- r449 probe
# facts verbatim, prereg sec.2 bitwise freeze
FROZEN_ACCRUAL_LO = "2021-02-23"
# prereg sec.2 frozen policy: batch accrual lo = first VALID (non-singular)
# anchor's effective bar -- ONE batch-level face for all 4 cells, passive and
# paired diffs. The B arm (LW-shrunk, always PD) re-weights at every anchor
# and would otherwise self-derive lo=first anchor (warmup singular anchor
# 2021-01-18), drifting off the frozen face; cmd_run anchors it explicitly.
J4_CANON_RECORD = 0.4854          # T-28 production B_MAXDIV 12m pooled
# beat-passive record -- cross-batch DISCLOSURE ONLY, non-gate
ARMS = ("A", "B")
CELL_FACES = [("A", "x1"), ("A", "x2"), ("B", "x1"), ("B", "x2")]
CELL_NAME = {("A", "x1"): "COVSHRINK-A-X1", ("A", "x2"): "COVSHRINK-A-X2",
             ("B", "x1"): "COVSHRINK-B-X1", ("B", "x2"): "COVSHRINK-B-X2"}
COST_RATE = {"x1": COST_X1_RATE, "x2": COST_X2_RATE}
MAX_WORKERS = 12                   # polite cap; worker_cap() RAM guard applies

_SLEEVES_OVERRIDE = None           # selftest synthetic-sleeve injection hook
_PASSIVE_OVERRIDE = None          # selftest synthetic-passive injection hook
_ATT_OVERRIDE = None               # selftest attrition-path override
_SELFTEST_FACTS = False            # selftest facts-snapshot flag


def gate_refuse(msg):
    print(f"GATE-REFUSE(exit2): {msg}")
    return 2


def sharpe_of(series):
    """NaN-safe nan-aware Sharpe (r442 pit law): non-finite dropped, a
    degenerate all-zero face returns 0.0, never NaN via raw mean/std."""
    r = np.asarray(series, dtype=float)
    r = r[np.isfinite(r)]
    if len(r) < 2:
        return 0.0
    sd = r.std(ddof=1)
    return float(r.mean() / sd * math.sqrt(PBP)) if sd > 0 else 0.0


def cum_ret(series, lo, hi):
    """Window cumulative return over indices [lo, hi)."""
    seg = np.asarray(series[lo:hi], dtype=float)
    seg = seg[np.isfinite(seg)]
    return float(np.prod(1.0 + seg) - 1.0) if len(seg) else 0.0


def _cell_stats(ser):
    r = np.asarray(ser, dtype=float)
    fin = r[np.isfinite(r)]
    n = len(fin)
    eq = np.cumprod(1.0 + fin)
    dd = float((eq / np.maximum.accumulate(eq) - 1.0).min()) if n else 0.0
    ann = float(eq[-1] ** (PBP / max(n, 1)) - 1.0) if n else 0.0
    return {"sharpe_full": round(sharpe_of(r), 4),
            "ann_ret": round(ann, 6),
            "max_dd": round(dd, 6), "n_days": int(len(r))}


def _sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# ------------------------------------------------------------ sleeves
def build_sleeves():
    """28-member x1/x2 sleeves, t27 verbatim (anchor-cum-sleeve reuse,
    56 engine member runs = non-search machinery faces, disclosed)."""
    if _SLEEVES_OVERRIDE is not None:
        return _SLEEVES_OVERRIDE
    jobs = [(f"{tid}|{mult}", member_run_iv6, (tid, mult))
            for tid in FROZEN_ROSTER for mult in (None, 2)]
    res = run_cells_parallel(jobs, workers=min(worker_cap(), MAX_WORKERS),
                             desc="w8-covshrink-sleeves",
                             initializer=_init_worker)
    res.pop("__workers__", None)
    sleeves = {}
    for tid in FROZEN_ROSTER:
        r1, r2 = res[f"{tid}|None"], res[f"{tid}|2"]
        for r in (r1, r2):
            r["eq_s"] = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
        sleeves[tid] = {"x1": r1, "x2": r2}
    return sleeves


def load_passive():
    """510300 B&H passive (T-28 J4 caliber), panel bare-code face,
    truncated to the evidence cutoff by index alignment downstream."""
    if _PASSIVE_OVERRIDE is not None:
        return _PASSIVE_OVERRIDE
    df = pd.read_csv(PASSIVE_CSV, parse_dates=["date"]).set_index("date")
    df = df.sort_index()
    return df["close"].astype(float)


# ------------------------------------------------- anchors + G-ANCHOR faces
def derive_anchors(R1):
    """Rolling-anchor schedule + probe-parity faces. Face dicts come from
    the r449 probe arm_face VERBATIM; weights re-derived on the same
    deterministic windows (parity by construction + bit-exact reconcile
    vs the frozen probe facts)."""
    rows = []
    for end in range(ROLL, len(R1), CADENCE):
        win = R1.iloc[end - ROLL:end]
        face = arm_face(win)
        anchor_ts = R1.index[end - 1]
        eff_ts = R1.index[end]
        try:
            wA = mdp_weights(win)["weights"]
            singular = False
        except np.linalg.LinAlgError:
            wA = None
            singular = True
        lw = lw_shrink_cov(win)
        wB = mdp_weights_cov(win, lw["cov"])["weights"]
        rows.append({**face,
                     "anchor_date": str(anchor_ts.date()),
                     "eff_date": str(eff_ts.date()),
                     "window": f"{str(R1.index[end - ROLL].date())}"
                               f"..{str(anchor_ts.date())}",
                     "wA": wA, "wB": wB, "singular_A": singular})
    return rows


def derive_faces(R1, rows, cutoff):
    """Full probe-facts structure on the live panel (reconcile face)."""
    lam = [r["lambda"] for r in rows]
    mw = [r["max_wdiff"] for r in rows if r["max_wdiff"] is not None]
    n_sing = sum(1 for r in rows if r["solver_A"] == "SINGULAR_SAMPLE_COV")
    if n_sing:
        first_sing = next(r["anchor_date"] for r in rows
                          if r["solver_A"] == "SINGULAR_SAMPLE_COV")
    else:
        first_sing = None
    is_R = R1[R1.index < pd.Timestamp(_oos_start())]
    return {
        "roster_n": len(FROZEN_ROSTER),
        "matrix_shape": list(R1.shape),
        "matrix_first": str(R1.index[0].date()),
        "matrix_last": str(R1.index[-1].date()),
        "cutoff": cutoff,
        "oos_start": _oos_start(),
        "roll_window": ROLL, "anchor_cadence_td": CADENCE,
        "n_anchors": len(rows),
        "n_singular_A_windows": n_sing,
        "first_singular_anchor": first_sing,
        "lambda_stats": {"min": round(min(lam), 6),
                         "median": round(float(np.median(lam)), 6),
                         "max": round(max(lam), 6)},
        "max_wdiff_stats": {"n_valid": len(mw),
                            "min": round(min(mw), 6),
                            "median": round(float(np.median(mw)), 6),
                            "max": round(max(mw), 6)} if mw else None,
        "solver_paths_A": {p: sum(1 for r in rows
                                  if r["solver_A"] == p)
                           for p in ("closed_form",
                                     "pg_fallback_local_optimum",
                                     "SINGULAR_SAMPLE_COV")},
        "solver_paths_B": {p: sum(1 for r in rows
                                  if r["solver_B"] == p)
                           for p in ("closed_form",
                                     "pg_fallback_local_optimum")},
        "static_IS_face": arm_face(is_R),
        "lw_selfcheck": [bool(x) for x in _selfcheck_lw()],
        "anchors": rows,
    }


_OOS_START = None


def _oos_start():
    """live.paper OOS_START, lazy import (keeps selftest light paths)."""
    global _OOS_START
    if _OOS_START is None:
        from live.paper import OOS_START
        _OOS_START = str(OOS_START)
    return _OOS_START


def anchor_drift(derived, facts):
    """Bit-exact face-by-face reconcile vs the frozen r449 probe facts.
    Returns a drift list (empty = all faces bit-exact)."""
    bad = []
    for k in ("roster_n", "matrix_shape", "matrix_first", "matrix_last",
              "cutoff", "oos_start", "roll_window", "anchor_cadence_td",
              "n_anchors", "n_singular_A_windows", "first_singular_anchor",
              "lambda_stats", "max_wdiff_stats", "solver_paths_A",
              "solver_paths_B", "static_IS_face", "lw_selfcheck"):
        if derived.get(k) != facts.get(k):
            bad.append(f"{k}: {json.dumps(derived.get(k))[:120]} != "
                       f"{json.dumps(facts.get(k))[:120]}")
    # 3 frozen anchor days: full probe-face dicts bit-exact (prereg
    # sec.2; weight fields excluded = runner-added accrual faces).
    # Enforced only against the REAL r449 probe facts (synthetic
    # selftest facts carry their own schedule, no frozen-day binding).
    if str(facts.get("probe", "")).startswith("W8"):
        by_date = {r["anchor_date"]: r for r in derived["anchors"]}
        probe_keys = None
        for day in FROZEN_ANCHOR_DAYS:
            if day not in by_date:
                bad.append(f"frozen anchor day {day} absent from live "
                           f"schedule")
                continue
            f_row = next(f for f in facts["anchors"]
                         if f["anchor_date"] == day)
            if probe_keys is None:
                probe_keys = set(f_row.keys()) - {"wA", "wB", "singular_A"}
            live_row = {k: by_date[day][k] for k in probe_keys
                        if k in by_date[day]}
            want_row = {k: f_row[k] for k in probe_keys if k in f_row}
            if live_row != want_row:
                bad.append(f"frozen anchor {day}: face drift")
                if len(bad) > 12:
                    return bad          # cap the flood, refusal is total
    return bad


def load_probe_facts(path=None):
    with open(path or PROBE_FACTS, encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------- accrual
def arm_series(R, rows, arm, rate, lo_ts=None):
    """Daily-rebalanced net return series for one arm on matrix R.

    Weight blocks: A arm changes weights only at non-singular anchors
    (frozen degenerate-window policy: singular anchor = carry last
    computable weights, pinv forbidden); B arm re-weights at every
    anchor. Transition cost = |dw|_1 * rate booked on each effective
    day, initial deployment |w-0|_1 included (cost-always-on).
    Accrual window = [first valid anchor's effective bar, panel end).
    lo_ts = batch-level accrual anchor (prereg sec.2 frozen policy):
    when given, blocks before it are warmup only -- no accrual, no
    cost booking (both arms share the one frozen accrual face; without
    it the B arm self-derives lo=first anchor, which drifts off the
    frozen face whenever the first anchor is singular -- first-burn
    GATE-REFUSE 'accrual lo drift A 2021-02-23 != B 2021-01-18').
    Returns (net series, faces dict).
    """
    blocks = []                       # (eff_pos, weights, changed)
    prev = None
    lo_pos = None
    if lo_ts is not None:
        lo_pos = int(R.index.get_loc(pd.Timestamp(lo_ts)))
    for r in rows:
        eff_pos = int(R.index.get_loc(pd.Timestamp(r["eff_date"])))
        if arm == "A":
            if r["singular_A"]:
                if prev is None:
                    continue          # pre-lo warmup singular: no accrual
                blocks.append((eff_pos, prev, False))
            else:
                blocks.append((eff_pos, r["wA"], True))
                prev = r["wA"]
                if lo_pos is None:
                    lo_pos = eff_pos
        else:
            blocks.append((eff_pos, r["wB"], True))
            if lo_pos is None:
                lo_pos = eff_pos
    if not blocks or lo_pos is None:
        raise ValueError(f"arm {arm}: no accrual blocks (no valid anchor)")
    cols = list(R.columns)
    n = len(R.index)
    wmat = np.zeros((n, len(cols)), dtype=float)
    cost = np.zeros(n, dtype=float)
    cur = None
    changes = 0
    l1_turnover = 0.0
    for eff_pos, w, _ch in blocks:
        if eff_pos < lo_pos:
            continue
        wv = np.array([w[c] for c in cols], dtype=float)
        if cur is None:
            dw = np.abs(wv).sum()          # initial deployment |w-0|_1
        else:
            dw = np.abs(wv - cur).sum()
        cost[eff_pos] += dw * rate
        l1_turnover += dw
        changes += 1
        wmat[eff_pos:] = wv               # active until next block
        cur = wv
    gross = (R.iloc[lo_pos:].to_numpy() * wmat[lo_pos:]).sum(axis=1)
    net = gross - cost[lo_pos:]
    net = pd.Series(net, index=R.index[lo_pos:])
    faces = {"lo_pos": lo_pos,
             "lo_date": str(R.index[lo_pos].date()),
             "n_weight_events": changes,
             "l1_turnover": round(l1_turnover, 6),
             "n_singular_carried": sum(
                 1 for r in rows
                 if r["singular_A"] and arm == "A"
                 and int(R.index.get_loc(pd.Timestamp(r["eff_date"])))
                 >= lo_pos)}
    return net, faces


# --------------------------------------------------------- starts / splits
def virtual_starts(series_by_face, passive):
    """K=1000 random virtual starts x 3 windows (law s1); one rng per k
    shared across faces (per-window identical start, nested windows
    honest overlap disclosed); beat = cell window cum (own cost face)
    > 510300 passive window cum (T-28 J4 caliber)."""
    out = {"n_starts": K_STARTS, "windows_days": WIN_DAYS, "cells": {}}
    n = len(passive)
    wmax = max(WIN_DAYS.values())
    los = []
    for k in range(K_STARTS):
        rng = np.random.default_rng([SG.SEED_REGISTRY[SEED_KEY], k])
        los.append(int(rng.integers(0, n - wmax)))
    for name, ser in series_by_face.items():
        s = np.asarray(ser, dtype=float)
        wins = {}
        for wname, w in WIN_DAYS.items():
            hits = 0
            for k in range(K_STARTS):
                lo = los[k]
                hits += int(cum_ret(s, lo, lo + w) >
                            cum_ret(passive, lo, lo + w))
            wins[wname] = {"beats": hits,
                           "beat_rate": round(hits / K_STARTS, 4)}
        out["cells"][name] = wins
    return out


def paired_beats(netA, netB, passive):
    """Paired-difference beat faces per window (prereg sec.4 primary):
    per identical virtual start, cum_B(window) - cum_A(window) > 0 =
    B beats A on that window (paired diff, deterministic face)."""
    a = np.asarray(netA, dtype=float)
    b = np.asarray(netB, dtype=float)
    n = len(passive)
    wmax = max(WIN_DAYS.values())
    los = []
    for k in range(K_STARTS):
        rng = np.random.default_rng([SG.SEED_REGISTRY[SEED_KEY], k])
        los.append(int(rng.integers(0, n - wmax)))
    out = {"n_starts": K_STARTS, "windows": {}}
    for wname, w in WIN_DAYS.items():
        b_gt_a = a_gt_b = 0
        for k in range(K_STARTS):
            lo = los[k]
            d = cum_ret(b, lo, lo + w) - cum_ret(a, lo, lo + w)
            b_gt_a += int(d > 0)
            a_gt_b += int(d < 0)
        out["windows"][wname] = {
            "b_beats_a": b_gt_a,
            "b_beat_rate": round(b_gt_a / K_STARTS, 4),
            "a_beats_b": a_gt_b,
            "a_beat_rate": round(a_gt_b / K_STARTS, 4),
            "ties": K_STARTS - b_gt_a - a_gt_b}
    return out


def worst_start_drawdowns(series_by_face):
    """Worst 12m virtual-start within-window max drawdown per cell
    (prereg sec.4 disclosure face, same K starts)."""
    n = max(len(np.asarray(s, dtype=float)) for s in series_by_face.values())
    w = WIN_DAYS["12m"]
    los = []
    for k in range(K_STARTS):
        rng = np.random.default_rng([SG.SEED_REGISTRY[SEED_KEY], k])
        los.append(int(rng.integers(0, max(n - w, 1))))
    out = {}
    for name, ser in series_by_face.items():
        s = np.asarray(ser, dtype=float)
        worst = 0.0
        for lo in los:
            seg = s[lo:lo + w]
            seg = seg[np.isfinite(seg)]
            if len(seg) < 20:
                continue
            eq = np.cumprod(1.0 + seg)
            dd = float((eq / np.maximum.accumulate(eq) - 1.0).min())
            worst = min(worst, dd)
        out[name] = round(worst, 6)
    return out


def split_windows(series_by_face):
    """100 random split windows (law s3): split point in [0.2n, 0.8n],
    half-window Sharpe same-sign rate >= 80% = segment-stable."""
    out = {}
    for name, ser in series_by_face.items():
        r = np.asarray(ser, dtype=float)
        n = len(r)
        agree = 0
        for k in range(K_SPLITS):
            rng = np.random.default_rng(
                [SG.SEED_REGISTRY[SEED_KEY], 1000 + k])
            cut = int(rng.integers(int(0.2 * n), int(0.8 * n)))
            a, b = sharpe_of(r[:cut]), sharpe_of(r[cut:])
            agree += int((a > 0) == (b > 0))
        rate = agree / K_SPLITS
        out[name] = {"same_sign_rate": round(rate, 4),
                     "segment_stable": bool(rate >= 0.80),
                     "n_splits": K_SPLITS}
    return out


# --------------------------------------------------------------- attrition
def _att_json_path():
    """prereg sec.6: the EXECUTING machine's lane file (gate_attrition
    .<id>.json); shared-file fallback when machine.json unreadable."""
    try:
        with open(MACHINE_JSON, encoding="utf-8") as fh:
            mid = json.load(fh).get("machine_id")
        if mid:
            return os.path.join(ROOT, "results",
                                f"gate_attrition.{mid}.json")
    except Exception:
        pass
    return ATT_JSON_SHARED


def _attr_row(batch, delta, total, gates, entries):
    path = _ATT_OVERRIDE or _att_json_path()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
    else:
        d = {"entries": []}
    row = {"batch": batch,
           "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
           "kind": "measurement", "cells_ledger_delta": delta,
           "ledger_total_after": total, "gates": gates,
           "entries": entries}
    own = [i for i, e in enumerate(d["entries"])
           if e.get("batch") == batch and e.get("kind") == "measurement"]
    if own:
        d["entries"][own[-1]] = row
    else:
        d["entries"].append(row)
    with open(path + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    os.replace(path + ".tmp", path)


# --------------------------------------------------------------- drivers
def _reconcile(facts, R1, rows, cutoff):
    derived = derive_faces(R1, rows, cutoff)
    bad = anchor_drift(derived, facts)
    return derived, bad


def cmd_verify(facts=None):
    """Real-panel G-ANCHOR reconcile (read-only; no product, no ledger).
    Builds sleeves + anchors and reconciles vs the frozen probe facts."""
    t0 = time.time()
    facts = facts or load_probe_facts()
    sleeves = build_sleeves()
    R1 = daily_ret_matrix(sleeves, "x1")
    cutoff = max(sleeves[t]["x1"]["cutoff"] for t in FROZEN_ROSTER)
    rows = derive_anchors(R1)
    derived, bad = _reconcile(facts, R1, rows, cutoff)
    if bad:
        for b in bad[:12]:
            print(f"  drift: {b}")
        print(f"GATE-REFUSE(exit2): G-ANCHOR drift {len(bad)} face(s) vs "
              f"frozen probe facts -- config mismatch VOID (one-face-off "
              f"law)")
        return 2
    print("G-ANCHOR verify: ALL faces bit-exact vs frozen r449 probe "
          f"facts ({derived['n_anchors']} anchors, "
          f"{derived['n_singular_A_windows']} singular-A, matrix "
          f"{derived['matrix_shape']} {derived['matrix_first']}.."
          f"{derived['matrix_last']}, cutoff {derived['cutoff']}) "
          f"({time.time() - t0:.0f}s)")
    return 0


def phase1_write(product):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(product, fh, ensure_ascii=False, indent=1)
    os.replace(OUT_JSON + ".tmp", OUT_JSON)
    return product


def finalize(product, cells, paired):
    prev_total = None
    if os.path.exists(OUT_JSON):
        try:
            with open(OUT_JSON, encoding="utf-8") as fh:
                old = json.load(fh)
            prev_total = (old.get("trials_ledger") or {}).get("prev_total")
        except Exception:
            prev_total = None
    gates = {}
    for (arm, face) in CELL_FACES:
        cname = CELL_NAME[(arm, face)]
        net = cells[(arm, face)]["net"]
        st = cells[(arm, face)]["stats"]
        g1 = SG.g1_prime_v2(st["sharpe_full"], net,
                            batch_cells=BATCH_CELLS, pool="core48",
                            results_dir=OUT_DIR_RESULTS,
                            n_trades=cells[(arm, face)]["n_weight_events"],
                            n_entries=cells[(arm, face)]["n_weight_events"])
        dsr = SG.deflated_sharpe_ratio(
            net, n_trials=g1["skill_line"]["n_eff"])
        gates[cname] = {"g1_prime_v2": g1, "dsr": dsr,
                        "cost_face_role": "judged" if face == "x1"
                        else "stress-disclosure"}
    mat = pd.DataFrame({CELL_NAME[k]: np.asarray(cells[k]["net"],
                                                 dtype=float)
                        for k in CELL_FACES})
    pbo = cscv_pbo(mat)
    for cname in gates:
        gates[cname]["g2"] = SG.g2_registration_v2(
            gates[cname]["g1_prime_v2"]["pass_v2"], gates[cname]["dsr"],
            float(pbo["pbo"]))
    # primary methodology gate: paired-diff series (passive_override=0.0,
    # spread face; line live-read from the shared collector, no
    # hand-copied constants)
    pg1 = SG.g1_prime_v2(paired["d_x1_stats"]["sharpe_full"],
                         paired["d_x1"], batch_cells=BATCH_CELLS,
                         pool="core48", results_dir=OUT_DIR_RESULTS,
                         passive_override=0.0,
                         n_trades=paired["n_weight_events_b"],
                         n_entries=paired["n_weight_events_b"])
    pdsr = SG.deflated_sharpe_ratio(paired["d_x1"],
                                    n_trials=pg1["skill_line"]["n_eff"])
    pg2 = SG.g2_registration_v2(pg1["pass_v2"], pdsr, float(pbo["pbo"]))
    x2_dir_ok = bool(paired["d_x2_stats"]["sharpe_full"] > 0)
    adopt_eligible = bool(pg1["pass_v2"] and pg2["eligible_v2"]
                          and x2_dir_ok)
    ledger = SG.append_ledger(BATCH_NAME, BATCH_CELLS,
                              file_name="results/innovation_quota/"
                                        "COV-SHRINK-AB-P1.json",
                              evidence_cutoff=product["evidence_cutoff"],
                              prev_total=prev_total,
                              note="4 judgment cells (2 cov arms x 2 cost "
                                   "faces, every cell pays per W6 s0 "
                                   "counting law); 56 member engine runs "
                                   "= anchor-cum-sleeve non-search "
                                   "machinery faces (t27 verbatim, "
                                   "disclosed); paired-diff D_x1 = primary "
                                   "methodology gate face "
                                   "(gates/disclosure, not a ledger "
                                   "cell, t27 readout precedent)")
    product["gates"] = gates
    product["family_pbo"] = pbo
    product["paired_gate"] = {"g1_prime_v2": pg1, "dsr": pdsr,
                             "g2": pg2,
                             "x2_paired_direction_ok": x2_dir_ok,
                             "d_x2_sharpe": paired["d_x2_stats"]
                             ["sharpe_full"]}
    product["verdict"] = {
        "methodology_adopt_eligible": adopt_eligible,
        "verdict_template": "prereg sec.4: adopt-eligible = paired G1' "
                            "pass (line live-read, passive_override=0.0 "
                            "spread face) AND paired G2 eligible AND x2 "
                            "paired direction consistent (D_x2 sharpe "
                            "> 0); else judged-negative family closure "
                            "(zoo #89 A/B route tested and closed, "
                            "RANDOM_LARGE_SAMPLE_LAW s5 reopen note)",
        "consumer_face": "adopt-eligible -> SPM B_MAXDIV methodology-"
                         "upgrade candidate at the 2026-10-01 monthly "
                         "boundary (PROFIT_MODEL_MAP constraint-2 "
                         "source) + STRATEGY_LIBRARY methodology row; "
                         "closure -> attrition row + 48h CEO report",
    }
    n_pass = sum(1 for g in gates.values()
                 if g["g1_prime_v2"]["pass_v2"])
    n_g2 = sum(1 for g in gates.values() if g["g2"]["eligible_v2"])
    adopt_str = ("ADOPT-ELIGIBLE" if adopt_eligible
                 else "JUDGED-NEGATIVE family closure")
    product["funnel"] = {
        "harvest_column": 1,
        "harvest_note": "zoo #89 cov_shrinkage_lw adoption route A/B "
                        "variant batch (first covariance-face family in "
                        "tree, r448 berth two-face audit: zero prior "
                        "judgment artifacts)",
        "gate_column": f"cells: {n_pass}/{BATCH_CELLS} g1_prime_v2 pass, "
                       f"{n_g2}/{BATCH_CELLS} G2-eligible; paired "
                       f"methodology gate: G1' "
                       f"{'PASS' if pg1['pass_v2'] else 'FAIL'} / G2 "
                       f"{'ELIGIBLE' if pg2['eligible_v2'] else 'NOT'} / "
                       f"x2-dir "
                       f"{'OK' if x2_dir_ok else 'INCONSISTENT'} -> "
                       f"{adopt_str}",
    }
    product["trials_ledger"] = ledger          # r434 pit law: value carried
    product["judgment_note"] = ("judged per prereg sec.4 via shared "
                                "library (batch_cells=4 s0 counting law); "
                                "the primary hypothesis face is the "
                                "deterministic paired diff B-A, no "
                                "random-baseline null family per prereg "
                                "(non-survivor A/B design); DSR/N_eff "
                                "accounting = both arms each counted via "
                                "the 4-cell family; T0 brake authority "
                                "stays with REGIME_GUARD, adoption walks "
                                "the monthly-boundary process")
    phase1_write(product)
    _attr_row(BATCH_NAME, BATCH_CELLS, int(ledger["total"]),
              {"g1_pass": {c: gates[c]["g1_prime_v2"]["pass_v2"]
                           for c in gates},
               "g2_eligible": {c: gates[c]["g2"]["eligible_v2"]
                               for c in gates},
               "family_pbo": pbo,
               "paired_g1_pass": pg1["pass_v2"],
               "paired_g2_eligible": pg2["eligible_v2"],
               "methodology_adopt_eligible": adopt_eligible},
              {"n_weight_events":
                   {CELL_NAME[k]: cells[k]["n_weight_events"]
                    for k in CELL_FACES},
               "singular_carried_A":
                   cells[("A", "x1")]["n_singular_carried"]})
    return product


def cmd_run():
    t0 = time.time()
    seed = SG.SEED_REGISTRY.get(SEED_KEY)
    if seed is None:
        return gate_refuse(f"SEED_REGISTRY key {SEED_KEY} missing "
                           f"(freeze-window registration absent)")
    facts = load_probe_facts()
    sleeves = build_sleeves()
    R1 = daily_ret_matrix(sleeves, "x1")
    R2 = daily_ret_matrix(sleeves, "x2")
    if not R1.index.equals(R2.index):
        return gate_refuse("x1/x2 matrix index drift (sleeve face "
                           "mismatch)")
    cutoff = max(sleeves[t]["x1"]["cutoff"] for t in FROZEN_ROSTER)
    rows = derive_anchors(R1)
    derived, bad = _reconcile(facts, R1, rows, cutoff)
    if bad:
        for b in bad[:12]:
            print(f"  drift: {b}")
        return gate_refuse(f"G-ANCHOR drift {len(bad)} face(s) vs frozen "
                           f"probe facts -- config mismatch VOID "
                           f"(one-face-off law)")
    if not _SELFTEST_FACTS and derived["cutoff"] != "2026-09-22":
        return gate_refuse(f"evidence cutoff drift {derived['cutoff']} != "
                          f"2026-09-22 (P-5C frozen binding)")
    print(f"G-ANCHOR reconcile: bit-exact ({time.time() - t0:.0f}s)",
          flush=True)

    # ---- cells: 2 arms x 2 cost faces
    # batch-level accrual anchor (prereg sec.2 frozen policy: accrual lo =
    # first VALID anchor's effective bar) -- shared by all 4 cells so the
    # paired-diff / passive / virtual-start faces stay length-aligned.
    lo_batch = next(r["eff_date"] for r in rows if not r["singular_A"])
    cells = {}
    for (arm, face) in CELL_FACES:
        R = R1 if face == "x1" else R2
        net, acc = arm_series(R, rows, arm, COST_RATE[face],
                             lo_ts=lo_batch)
        cells[(arm, face)] = {
            "net": net, "arm_faces": acc,
            "stats": _cell_stats(net.to_numpy()),
            "n_weight_events": acc["n_weight_events"],
            "n_singular_carried": acc["n_singular_carried"],
            "l1_turnover": acc["l1_turnover"],
        }
    lo_a = cells[("A", "x1")]["arm_faces"]["lo_date"]
    lo_b = cells[("B", "x1")]["arm_faces"]["lo_date"]
    if lo_a != lo_b:
        return gate_refuse(f"accrual lo drift A {lo_a} != B {lo_b}")
    if not _SELFTEST_FACTS and lo_a != FROZEN_ACCRUAL_LO:
        return gate_refuse(f"accrual lo {lo_a} != frozen "
                           f"{FROZEN_ACCRUAL_LO} (prereg sec.2 "
                           f"runner-derive assertion)")
    years = len(cells[("A", "x1")]["net"]) / float(PBP)

    # ---- passive (510300 B&H, T-28 J4 caliber), aligned to accrual
    passive_full = load_passive()
    passive_close = passive_full.reindex(R1.index).ffill()
    if passive_close[derived["matrix_last"]:].isna().all():
        return gate_refuse("passive 510300 face missing at panel end")
    lo_ts = pd.Timestamp(lo_a)
    passive_ser = passive_close.pct_change().fillna(0.0)
    passive_ser = passive_ser[passive_ser.index >= lo_ts].to_numpy()
    if len(passive_ser) != len(cells[("A", "x1")]["net"]):
        return gate_refuse("passive/accrual length mismatch")
    passive_stats = _cell_stats(passive_ser)

    # ---- paired-diff faces (primary hypothesis)
    d_x1 = (cells[("B", "x1")]["net"].to_numpy()
            - cells[("A", "x1")]["net"].to_numpy())
    d_x2 = (cells[("B", "x2")]["net"].to_numpy()
            - cells[("A", "x2")]["net"].to_numpy())
    paired = {"d_x1": d_x1, "d_x2": d_x2,
              "d_x1_stats": _cell_stats(d_x1),
              "d_x2_stats": _cell_stats(d_x2),
              "n_weight_events_b": cells[("B", "x1")]["n_weight_events"]}

    series_by_face = {CELL_NAME[k]: cells[k]["net"].to_numpy()
                      for k in CELL_FACES}
    vstarts = virtual_starts(series_by_face, passive_ser)
    pbeats = paired_beats(cells[("A", "x1")]["net"].to_numpy(),
                          cells[("B", "x1")]["net"].to_numpy(),
                          passive_ser)
    splits = split_windows({**series_by_face,
                            "PAIRED-DIFF-D-X1": d_x1,
                            "PASSIVE-510300-BH": passive_ser})
    worst_dd = worst_start_drawdowns(series_by_face)

    cells_out = {}
    for (arm, face) in CELL_FACES:
        cname = CELL_NAME[(arm, face)]
        c = cells[(arm, face)]
        tpy = c["l1_turnover"] / years
        cells_out[cname] = {
            "arm": arm, "cov_face": "sample" if arm == "A" else "lw_shrunk",
            "cost_face": face,
            "accrual_lo": c["arm_faces"]["lo_date"],
            "n_weight_events": c["n_weight_events"],
            "n_singular_carried": c["n_singular_carried"],
            **c["stats"],
            "l1_turnover_total": c["l1_turnover"],
            "turnover_per_year": round(tpy, 2),
            "turnover_budget_ok": bool(tpy <= TURNOVER_BUDGET),
            "worst_12m_vstart_dd": worst_dd[cname],
        }
    n_valid_anchors = sum(1 for r in rows if not r["singular_A"])
    product = {
        "batch": BATCH_NAME,
        "evidence_cutoff": derived["cutoff"],
        "cutoff_meta": SG.cutoff_meta(derived["cutoff"]),
        "prereg": "research/INNOVATION_QUOTA_W8_PREREG.md (r448 bm-b "
                  "berth + r450 bm-b freeze, seed 20325500)",
        "prereg_sha256_16": _sha256_file(os.path.join(
            ROOT, "research", "INNOVATION_QUOTA_W8_PREREG.md"))[:16],
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "seed": {"base": seed,
                 "k_substreams": "starts k in [0,1000); splits k in "
                                 "[1000,1100) -- rng([SEED, k]) one "
                                 "k-stream shared across cells/faces; "
                                 "no own-null family (deterministic "
                                 "paired-diff design, prereg sec.4)"},
        "panel": {"roster_n": derived["roster_n"],
                  "matrix_shape": derived["matrix_shape"],
                  "matrix_first": derived["matrix_first"],
                  "matrix_last": derived["matrix_last"],
                  "anchor_four_tuples": {
                      "member_sleeve_matrix": {
                          "path": "firm/traders/*.json + data/daily "
                                  "bare-code core48 (via "
                                  "iv6_portfolio.member_run_iv6, t27 "
                                  "anchor-cum-sleeve)",
                          "loader": "iv6_portfolio.member_run_iv6(tid, "
                                    "mult)",
                          "start_window": derived["matrix_first"],
                          "warmup_window": "engine per-member signal "
                                           "warmup (in sleeves, not the "
                                           "cov window)"},
                      "rolling_cov_window": {
                          "path": "member x1 eq curves pct-change matrix",
                          "loader": "t27.daily_ret_matrix(sleeves, 'x1')",
                          "start_window": str(R1.index[ROLL].date()),
                          "warmup_window": f"{ROLL} trailing trading "
                                           f"days"},
                  },
                  "cutoff_face": "registration-pinned P-5C binding "
                                 "(probe facts cutoff 2026-09-22)"},
        "construction": "verbatim-import results/_r449bmb_w8_probe.py "
                        "(r456 paradigm): A arm = t27 mdp_weights "
                        "VERBATIM (sample cov, production recipe); "
                        "B arm = mdp_weights_cov on hand-rolled "
                        "Ledoit-Wolf 2004 JMV shrunk cov (mu*I target, "
                        "N=n-1 pandas ddof=1); rolling "
                        f"{ROLL}d@{CADENCE}td anchors over the x1 matrix, "
                        "weights decided at anchor close effective next "
                        "bar (T+1 causality)",
        "anchor_faces": {
            "n_anchors": derived["n_anchors"],
            "n_singular_A_windows": derived["n_singular_A_windows"],
            "n_valid_paired_anchors": n_valid_anchors,
            "first_singular_anchor": derived["first_singular_anchor"],
            "lambda_stats": derived["lambda_stats"],
            "max_wdiff_stats": derived["max_wdiff_stats"],
            "solver_paths_A": derived["solver_paths_A"],
            "solver_paths_B": derived["solver_paths_B"],
            "static_IS_face": derived["static_IS_face"],
            "frozen_anchor_days": list(FROZEN_ANCHOR_DAYS),
        },
        "degenerate_window_policy": {
            "frozen_rule": "prereg sec.2/3: A arm at singular anchors "
                           "CARRIES last computable weights (production "
                           "recipe verbatim, pinv forbidden); paired "
                           "per-anchor diff faces exclude singular "
                           "anchors (count disclosed); accrual lo = "
                           "first valid anchor effective bar",
            "accrual_lo": lo_a,
            "singular_carried_in_window_A":
                cells[("A", "x1")]["n_singular_carried"],
            "pre_lo_warmup_anchors":
                derived["n_anchors"] - n_valid_anchors
                - cells[("A", "x1")]["n_singular_carried"]
                if derived["n_anchors"] - n_valid_anchors
                - cells[("A", "x1")]["n_singular_carried"] > 0 else 0,
        },
        "cost_face": {"x1_rate_per_side": COST_X1_RATE,
                      "x2_rate_per_side": COST_X2_RATE,
                      "transition_cost_rule": "|dw|_1 * rate on each "
                                               "weight-event day, "
                                               "initial deployment "
                                               "included; x2 face reuses "
                                               "x1-estimated weights "
                                               "(T-27 precedent)",
                      "turnover_budget_per_year": TURNOVER_BUDGET},
        "passive": {"face": "510300 B&H, data/daily/510300.csv bare-code "
                            "panel face, truncated to evidence cutoff "
                            "by index alignment (T-28 J4 caliber)",
                    "stats": passive_stats,
                    "j4_canon_record_disclosure": {
                        "value": J4_CANON_RECORD,
                        "note": "T-28 production B_MAXDIV static-assembly "
                                "12m pooled beat-passive record "
                                "(NOT-DEMONSTRATED vs 0.70 line); "
                                "cross-batch disclosure only, different "
                                "start-grid caliber, non-gate"}},
        "nulls": {"consumed": "shared core48 collector for skill_line_v2 "
                              "calibration (K=0 own nulls; deterministic "
                              "paired-diff primary face per prereg "
                              "sec.4)"},
        "cells": cells_out,
        "paired": {
            "d_x1_stats": paired["d_x1_stats"],
            "d_x2_stats": paired["d_x2_stats"],
            "n_weight_events_b": paired["n_weight_events_b"],
            "paired_beats": pbeats,
            "primary_readout": "12m B-beat-A rate "
                                f"{pbeats['windows']['12m']['b_beat_rate']}"
                                " (K=1000 paired virtual starts)"},
        "virtual_starts": vstarts,
        "splits": splits,
        "d6": {"provenance": "frozen at the r450 D6 probe window "
                             "verbatim (results/_r450bmb_w8_d6_probe_"
                             "facts.json); merge-clause adjudication is "
                             "the freeze-window admission record, not "
                             "re-computed at burn (W6 precedent)",
               "reject_line": D6_REJECT},
    }
    with open(D6_FACTS, encoding="utf-8") as fh:
        product["d6"].update(json.load(fh).get("d6_cells_face", {}))
    product = phase1_write(product)
    print(f"phase-1 product written ({time.time() - t0:.0f}s)", flush=True)
    product = finalize(product, cells, paired)
    pg = product["paired_gate"]
    print(f"finalize ok: cells={len(cells)} paired_g1="
          f"{'PASS' if pg['g1_prime_v2']['pass_v2'] else 'FAIL'} "
          f"paired_g2="
          f"{'ELIGIBLE' if pg['g2']['eligible_v2'] else 'NOT'} "
          f"verdict="
          f"{product['verdict']['methodology_adopt_eligible']} "
          f"ledger={product['trials_ledger']['total']} "
          f"elapsed={time.time() - t0:.0f}s")
    return 0


# --------------------------------------------------------------- selftest
def _mk_synthetic_sleeves(n_members=28, n_days=760):
    """Synthetic 28-member sleeves with planted covariance structure:
    a member cluster goes perfectly correlated over a mid window segment
    (sample cov singular -> A-arm carry policy fires there) while the
    LW-shrunk face stays PD; members cross OOS_START (J18 pitfall law).
    Deterministic rng, eq curves only (engine bypassed)."""
    dates = pd.bdate_range("2020-01-02", periods=n_days)
    rng = np.random.default_rng(20285500)
    base = 0.0004 + 0.0012 * np.sin(np.arange(n_days) / 53.0)
    rets = {}
    for i, tid in enumerate(FROZEN_ROSTER):
        r = base + rng.normal(0, 0.006, n_days)
        rets[tid] = r
    # planted singular window: one member goes exactly flat over a
    # segment >= ROLL (eq bit-constant, cumprod x*1.0 is exact) so
    # anchor windows sitting fully inside carry an exact zero-variance
    # column -> sample cov exactly singular (np.linalg.solve raises ->
    # A-arm carry policy fires) while the LW-shrunk face stays PD.
    # Duplicate-member planting through the eq->pct_change roundtrip
    # loses bit-exactness to prefix-scale rounding and never trips
    # the exact-singularity detector (numpy-level probe verified
    # before this fix: array_equal False, solve no-raise).
    seg = slice(280, 600)
    rets[FROZEN_ROSTER[4]][seg] = 0.0
    sleeves = {}
    for tid, r in rets.items():
        eq = pd.Series(1.5 * np.cumprod(1.0 + r), index=dates)
        for key, scale in (("x1", 1.0), ("x2", 1.0)):
            sleeves.setdefault(tid, {})[key] = {
                "eq_s": eq, "cutoff": str(dates[-1].date()),
                "full": {"sharpe": 0.5}, "n_trades": 40, "n_entries": 40}
    return sleeves, dates


def cmd_selftest():
    global PROBE_FACTS, OUT_DIR, OUT_JSON, _SLEEVES_OVERRIDE, \
        _PASSIVE_OVERRIDE, _ATT_OVERRIDE, _SELFTEST_FACTS, _OOS_START
    tmp = tempfile.mkdtemp(prefix="innovation_quota_w8_selftest_")
    ok = []
    try:
        sleeves, dates = _mk_synthetic_sleeves()
        R1 = daily_ret_matrix(sleeves, "x1")
        rows = derive_anchors(R1)
        n_sing = sum(1 for r in rows if r["singular_A"])
        ok.append(("planted singular anchors fire (A-arm carry path)",
                   n_sing > 0))
        # OOS_START stub for the synthetic face (module-level cache)
        _OOS_START = "2025-01-01"
        derived = derive_faces(R1, rows, str(dates[-1].date()))
        snap = json.loads(json.dumps(
            {k: v for k, v in derived.items() if k != "anchors"}))
        facts = {"probe": "synthetic selftest facts",
                 "anchors": json.loads(json.dumps(
                     [{k: v for k, v in r.items()
                       if k not in ("wA", "wB", "singular_A")}
                      for r in rows])),
                 **snap}
        facts_path = os.path.join(tmp, "facts.json")
        with open(facts_path, "w", encoding="utf-8") as fh:
            json.dump(facts, fh)
        PROBE_FACTS = facts_path
        _SELFTEST_FACTS = True
        _SLEEVES_OVERRIDE = sleeves
        # drift refusal: perturb one compared top-level face (the
        # per-anchor row compare is bound to the real r449 probe facts
        # only -- frozen 3-day binding keys on facts['probe'] starting
        # 'W8'; synthetic facts exercise the same aggregate-face
        # refusal path anchor_drift -> rc=2)
        good_med = facts["lambda_stats"]["median"]
        facts["lambda_stats"]["median"] = float(good_med) + 0.5
        with open(facts_path, "w", encoding="utf-8") as fh:
            json.dump(facts, fh)
        ok.append(("anchor drift refusal (rc=2)",
                   cmd_verify() == 2))
        facts["lambda_stats"]["median"] = good_med
        with open(facts_path, "w", encoding="utf-8") as fh:
            json.dump(facts, fh)
        ok.append(("anchor restored -> verify clean (rc=0)",
                   cmd_verify() == 0))

        # ---- full pipeline on synthetic sleeves, stateful faces stubbed
        OUT_DIR = os.path.join(tmp, "innovation_quota")
        OUT_JSON = os.path.join(OUT_DIR, "COV-SHRINK-AB-P1.json")
        _ATT_OVERRIDE = os.path.join(tmp, "gate_attrition.lane.json")
        lo_ts = pd.Timestamp(rows[0]["eff_date"])
        passive_syn = pd.Series(
            4.0 * np.cumprod(1.0 + 0.0005
                             + np.zeros(len(dates))
                             + np.random.default_rng(7).normal(
                                 0, 0.004, len(dates))),
            index=dates)
        _PASSIVE_OVERRIDE = passive_syn
        _ne, _al, _pb = (SG.n_eff, SG.append_ledger, SG.passive_baseline)
        _real_cscv = globals()["cscv_pbo"]
        SG.n_eff = lambda bc, rd=None: int(bc)
        SG.append_ledger = lambda *a, **k: {"prev_total": 0, "total": 100,
                                            "batch": BATCH_NAME}
        SG.passive_baseline = lambda *a, **k: 0.10
        globals()["cscv_pbo"] = lambda mat: {"pbo": 0.1}
        # d6 facts stub (frozen-block carry path)
        d6_stub = os.path.join(tmp, "d6_facts.json")
        with open(d6_stub, "w", encoding="utf-8") as fh:
            json.dump({"d6_cells_face": {
                "batch_internal_A_vs_B": 0.99,
                "vs_t33_cells": {}, "merge_clause_applied": [],
                "vs_registered_six": {"max_abs_corr": None,
                                      "argmax": None},
                "vs_b_maxdiv_production_face": None}}, fh)
        global D6_FACTS
        D6_FACTS = d6_stub
        try:
            rc = cmd_run()
            ok.append(("cmd_run on synthetic sleeves rc=0", rc == 0))
            if rc == 0:
                with open(OUT_JSON, encoding="utf-8") as fh:
                    prod = json.load(fh)
                ok.append(("product faces (cutoff_meta/4 cells/ledger)",
                           len(prod["cells"]) == 4
                           and set(prod["cells"])
                           == set(CELL_NAME.values())
                           and "cutoff_meta" in prod
                           and prod["trials_ledger"]["total"] == 100
                           and prod["d6"]["batch_internal_A_vs_B"]
                           == 0.99))
                ok.append(("paired gate + verdict faces present",
                           "paired_gate" in prod
                           and "methodology_adopt_eligible"
                           in prod["verdict"]
                           and prod["verdict"][
                               "methodology_adopt_eligible"] in
                           (True, False)
                           and "paired_beats" in prod["paired"]
                           and prod["virtual_starts"]["n_starts"]
                           == K_STARTS))
                ok.append(("singular carry faces disclosed",
                           prod["cells"]["COVSHRINK-A-X1"]
                           ["n_singular_carried"] > 0
                           and prod["degenerate_window_policy"]
                           ["accrual_lo"] == prod["cells"]
                           ["COVSHRINK-A-X1"]["accrual_lo"]))
                ok.append(("turnover budget flag face",
                           all("turnover_budget_ok" in c
                               for c in prod["cells"].values())))
                ok.append(("splits incl paired-diff leg",
                           "PAIRED-DIFF-D-X1" in prod["splits"]
                           and all(v["n_splits"] == K_SPLITS
                                   for v in prod["splits"].values())))
                ok.append(("attrition lane row landed",
                           os.path.exists(_ATT_OVERRIDE)
                           and json.load(open(_ATT_OVERRIDE))
                           ["entries"][-1]["batch"] == BATCH_NAME))
                # ---- r450 landed-state guard
                ok.append(("r450 guard: judged product refuses (rc=2)",
                           _refuse_if_judged() == 2))
                with open(OUT_JSON + ".t", "w", encoding="utf-8") as fh:
                    json.dump({"phase1": True}, fh)
                os.replace(OUT_JSON + ".t", OUT_JSON)
                ok.append(("r450 guard: phase-1-only resumes (rc=0)",
                           _refuse_if_judged() == 0))
        finally:
            SG.n_eff, SG.append_ledger, SG.passive_baseline = \
                _ne, _al, _pb
            globals()["cscv_pbo"] = _real_cscv
            _SLEEVES_OVERRIDE = None
            _PASSIVE_OVERRIDE = None
            _SELFTEST_FACTS = False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    n_okk = sum(1 for _, v in ok if v)
    print(f"innovation_quota_w8 selftest: {n_okk}/{len(ok)} PASS")
    for name, v in ok:
        if not v:
            print(f"  FAIL: {name}")
    return 0 if n_okk == len(ok) else 1


# ------------------------------------------------------------------ guard
def _refuse_if_judged():
    """r450 landed-state guard: read CONTENT (trials_ledger block), not
    existence/timestamps. Judged product refuses re-run (rc=2) unless
    INNOVATION_QUOTA_W8_REFINALIZE=1; phase-1-only product resumes."""
    if not os.path.exists(OUT_JSON):
        return 0
    try:
        with open(OUT_JSON, encoding="utf-8") as fh:
            old = json.load(fh)
    except Exception:
        return 0        # unreadable partial write -> resume path
    if (old.get("trials_ledger") or {}).get("total") is not None and \
            os.environ.get("INNOVATION_QUOTA_W8_REFINALIZE") != "1":
        print("GATE-REFUSE(exit2): COV-SHRINK-AB-P1.json already "
              "judged (trials_ledger present, content-read per r450); "
              "INNOVATION_QUOTA_W8_REFINALIZE=1 = only redo")
        return 2
    return 0


def main():
    try:
        # r236 GBK-console law: reconfigure at entry
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "verify", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return cmd_selftest()
    if a.cmd == "verify":
        return cmd_verify()
    guard = _refuse_if_judged()
    if guard:
        return guard
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
