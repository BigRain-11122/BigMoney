# -*- coding: utf-8 -*-
"""INNOVATION_QUOTA_W7 runner -- NNL-BREADTH-P1 net-new-high breadth
family judged batch (INNOVATION-QUOTA-SLOT-7, zoo #87 nh_nl_breadth,
prereg research/INNOVATION_QUOTA_W7_PREREG.md FROZEN bm-c r255; berth
probe facts results/_r254bmc_w7_nlnl_probe_facts.json + freeze-window
theta/D6/state facts results/_r255bmc_w7_nnl_d6_probe_facts.json).

Laws (all construction faces verbatim-import from the two probes --
r456 single-source zero-drift paradigm):

  panel   core48 bare-code close panel via _r254bmc_w7_nlnl_probe.
          load_core48 (data/daily/*.csv 6-digit names, union date
          index), D2-truncated to evidence cutoff 2026-09-29 (P-5C
          frozen binding, prereg s2). G-PANEL: 48 symbols /
          2020-01-02..2026-09-29 / 1,635 dates. G-ANCHOR battery
          (fail-closed, one-face-off = config mismatch VOID, not data
          corruption), four families:
          (a) W20 masked breadth face (r254 facts verbatim): valid>=30
              mask -> 1,616 b-days / first 2020-02-06 / valid_min 37 /
              valid_max 48 / b_mean 0.0194 / b_std 0.2561 / b_min
              -0.9211 / b_p5 -0.4468 / b_p50 0.0213 / b_p95 0.4792 /
              b_max 0.8125 / b_q10 -0.3111 / b_q90 0.3404 /
              days_nh>=10 329 / days_nl>=10 332 / all-member NH 0 /
              all-member NL 0;
          (b) theta face (r255 facts verbatim): trailing-500d rolling
              quantiles q10/q50/q90 of the UNMASKED b (min_periods=500,
              zero hand-copied constants) -> 1,117 decidable days,
              first 2022-02-24, order invariant lo<=re<=hi every day,
              strict-inequality live fractions 1.0/1.0, range faces,
              5 extreme-day samples incl. 2021-02-18 warmup;
          (c) state face (r255 facts verbatim): bottom defensive 259 /
              dual defensive 376 over 1,117 decidable days each;
          (d) decidable-contiguity mechanism check (NaN-position
              propagation hazard guard).
  engine  B_t(W20) = (NH_t - NL_t)/valid_t over core48 members with
          full 20-bar lookback (honest denominator, _r254bmc probe
          breadth_series); theta = trailing-500d rolling q10/q50/q90;
          state machine = _r255bmc probe variant_positions verbatim:
          bottom: B<=th_lo -> flat; B>=th_re -> long; else maintain.
          dual: B<=th_lo -> flat; B>=th_hi -> flat; B<=th_re -> long;
          else maintain (top-leg hysteresis: the (th_re, th_hi)
          maintain band IS the "defend until B<=th_re" carry).
          INITIAL STATE = long at the first decidable day (frozen r255
          convention; the first decidable day's triggers still apply
          that same day -- probe semantics, selftest pins both faces).
          Signal decided at close t, effective t+1 (T+1 onset,
          W1-W6 house caliber): pos[t] = pos_end[t-1]; batch window lo
          = first_decidable_idx + 1 (W5 max(first_decidable)+1 law),
          four-cell shared window for cross-cell PBO/CSCV date
          alignment; pre-lo days are breadth/theta construction
          warmup, disclosed. Judged x1 net = probe cell_returns
          verbatim (parity-asserted against the local mult-face helper
          at run time); costs = COST_X1_RATE on |dpos| booked to the
          following day, window-start entry booked against the
          pre-window flat face; x2 = CostPatch(2.0) = 26.082bp/side
          stress disclosure column. Hold-period >=3 trading days
          constraint EXEMPT per prereg s3 (state-gate holds = signal
          continuous segments; defense segments at 0 = cash-leg legal
          state, disclosed).
  cells   4 cells = 2 signal variants x 2 cost faces (prereg s0: every
          cell pays into N_eff, W6 isomorphic): NNL-BOTTOM-X1 (judged
          face), NNL-BOTTOM-X2, NNL-DUAL-X1 (judged face),
          NNL-DUAL-X2. Traded instrument = 510300 single-asset
          exposure gate (W1-W5 same harness face; signal source =
          core48 cross-section, information/instrument separation =
          the family's structural-distinction argument).
  passive PASSIVE-510300-BH buy-and-hold over the same batch window,
          live-computed Sharpe fed to g1_prime_v2 passive_override
          (W5 door). Reference columns (prereg s3 "510300 B&H + core48
          pool passive calibration live-read"): SG.passive_baseline
          ("core48") + shared-collector null coverage, live-read,
          disclosed only.
  nulls   K=2000 uniform random-day-placement nulls per VARIANT
          (prereg s0 compute budget + s4 seed k-allocation "nulls
          k<2000", W3/W4/W5 semantics): each draw preserves the
          variant's window position-day count (exposure preserved),
          placement uniform over the pos_end domain [lo-1, n); flip
          count NOT preserved (isolated days = 2 flips each, null
          cost drag higher than the real cell = frozen honest face);
          one draw -> both cost faces (x1/x2 sharpes from the same
          positions). rng = np.random.default_rng([SEED, k]), k <
          2000, one k-stream shared across variants (W5 seed law);
          shard npy checkpoints for idempotent resume.
  starts  K=1000 virtual starts (k in [2000, 3000), law s1 K>=1000):
          windows 6m/12m/24m = 126/252/504 trading days (252 ppy
          convention, disclosed); beat = cell window cum ret (own cost
          face) > passive window cum ret. 100 random split windows
          (k in [3000, 3100), law s3 >= 100): split point in
          [0.2n, 0.8n], half-window Sharpe same-sign rate >= 80% =
          segment-stable.
  gates   G1'v2 per cell via science_gates.g1_prime_v2 (batch_cells =
          2004 = 4 judged cells + 2000 null draws, the s0 counting
          law; prereg s4's "batch_cells=4" is the judged-cell
          shorthand exactly as W5's "batch_cells=3" -> 2003 family
          reconciliation, disclosed here and in judgment_note), pool=
          'core48', null_pool = batch-own per-cell null family (the
          s0/s4-seed k-allocation face: "nulls k<2000, semantics same
          W3/W4/W5" governs over s4's W6-template "shared collector
          n=120" phrase -- three-signal weight: s0 budget + seed
          k-band + r256 W5-skeleton-mirror pointer; the shared
          collector stays a live-read reference column), passive_
          override = this batch's 510300-BH window Sharpe; n_trades =
          n_entries = derived position-face episode count (F6 dual
          trade gate folded, prereg s4 lists both counts); NaN-safe
          nan-aware runner stats (r442 pit law); DSR via
          deflated_sharpe_ratio on the raw cell series; family PBO
          via screening.pbo cscv_pbo CSCV-8 over the 4-cell matrix; G2
          via g2_registration_v2. No hand-copied lines (O-2250).
  d6      frozen at the r255 probe window verbatim (W6 paradigm: the
          admission record = the freeze-window artifact, no
          re-computation): batch internal bottom-vs-dual |corr| 0.6511
          (variant face, both cells burn); vs T33 four in-book
          rotation cells max 0.4618 (bottom x dual_momentum) -- ALL <
          0.7 reject line, merge clause ZERO triggers; vs registered
          six max 0.351 (ENGULF-CE-01) disclose-only; REGIME_GUARD =
          in-production non-cell (signal face adjudicated at berth
          pearson -0.7757 W20 / -0.6369 W60, no cells pair exists --
          honest boundary, T0 authority untouched).
  turnover budget 50 entries/year (prereg s3); breach = red honest row.
  ledger  append_ledger("NNL_BREADTH_P1", 2004, "results/
          innovation_quota/NNL-BREADTH-P1.json", evidence_cutoff
          ="2026-09-29"); out["trials_ledger"] carries the return
          value (r434 pit law); gate_attrition measurement row to the
          EXECUTING machine's lane file (prereg s6, W6 law:
          gate_attrition.<machine_id>.json, shared-file fallback).
Products (prereg s6): results/innovation_quota/NNL-BREADTH-P1.json
(top evidence_cutoff + cutoff_meta + panel/anchor faces + passive +
4 cells + per-cell nulls + virtual starts + splits + frozen d6 +
funnel + gates + ledger) + nulls shard npy checkpoints.

Usage: run | verify | selftest   (exit 0 ok; 2 = fail-closed gate
refusal, including the r450 landed-state guard: a judged product
(trials_ledger present, read from CONTENT not existence/timestamps)
refuses re-run rc=2 unless INNOVATION_QUOTA_W7_REFINALIZE=1; a
phase-1-only product resumes via npy checkpoints). 'verify' =
real-panel G-ANCHOR reconcile only (read-only, no engine, no
product, no ledger -- build-time pre-verification face, burn stays
with the pool claim).
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
from screening.pbo import cscv_pbo              # family PBO CSCV-8

# frozen construction single source (r456 verbatim-import paradigm)
from _r254bmc_w7_nlnl_probe import load_core48, breadth_series
from _r255bmc_w7_nnl_d6_probe import variant_positions, cell_returns

OUT_DIR = os.path.join(ROOT, "results", "innovation_quota")
NULL_DIR = os.path.join(OUT_DIR, "nulls_w7")
OUT_JSON = os.path.join(OUT_DIR, "NNL-BREADTH-P1.json")
OUT_DIR_RESULTS = os.path.dirname(OUT_DIR)      # results root for lib faces
MACHINE_JSON = os.path.join(ROOT, "fleet", "machine.json")
ATT_JSON_SHARED = os.path.join(ROOT, "results", "gate_attrition.json")
D6_FACTS_PATH = os.path.join(
    ROOT, "results", "_r255bmc_w7_nnl_d6_probe_facts.json")

BATCH_NAME = "NNL_BREADTH_P1"
BATCH_CELLS = 2004                # 4 judged cells + 2000 null draws (s0 law)
EVIDENCE_CUTOFF = "2026-09-29"
SEED_KEY = "innovation_quota_w7_nlnl"
PBP = SG.PERIODS_PER_YEAR         # 252 gate-chain single-source
W_MAIN = 20
THETA_TRAIL = 500
K_NULLS = 2000
NULL_SHARDS = 8
K_STARTS = 1000
K_SPLITS = 100
WIN_DAYS = {"6m": 126, "12m": 252, "24m": 504}
D6_REJECT = 0.7
TURNOVER_BUDGET = 50              # prereg s3: 50 entries/year budget line
TARGET = "510300"
SEED = None                       # filled from SG.SEED_REGISTRY at run

# 4 cells = 2 variants x 2 cost faces (prereg s0); key = (variant, face)
VARIANTS = ["bottom", "dual"]
CELL_FACES = [("bottom", "x1"), ("bottom", "x2"),
              ("dual", "x1"), ("dual", "x2")]
CELL_NAME = {("bottom", "x1"): "NNL-BOTTOM-X1",
             ("bottom", "x2"): "NNL-BOTTOM-X2",
             ("dual", "x1"): "NNL-DUAL-X1",
             ("dual", "x2"): "NNL-DUAL-X2"}
CELL_MULT = {"x1": 1.0, "x2": 2.0}

# ---- frozen probe faces (G-PANEL / G-ANCHOR; r254 + r255 facts verbatim)
PANEL_ANCHOR = {"n_symbols": 48, "first_date": "2020-01-02",
                "last_date": "2026-09-29", "n_dates": 1635}
W20_ANCHOR = {"n_valid_days": 1616, "valid_min": 37, "valid_max": 48,
              "first_valid_date": "2020-02-06", "b_mean": 0.0194,
              "b_std": 0.2561, "b_min": -0.9211, "b_p5": -0.4468,
              "b_p50": 0.0213, "b_p95": 0.4792, "b_max": 0.8125,
              "b_q10": -0.3111, "b_q90": 0.3404, "days_nh_ge_10": 329,
              "days_nl_ge_10": 332, "days_all_member_nh": 0,
              "days_all_member_nl": 0}
THETA_ANCHOR = {"n_decidable_days": 1117,
                "first_decidable_date": "2022-02-24",
                "order_invariant": True,
                "strict_frac_lo_lt_re": 1.0, "strict_frac_re_lt_hi": 1.0,
                "th_lo_range": [-0.4176, -0.2054],
                "th_re_range": [-0.0213, 0.0455],
                "th_hi_range": [0.2297, 0.4167],
                "extreme_day_samples": {
                    "2021-02-18": "absent-or-warmup",
                    "2022-04-26": {"b": -0.587, "th_lo": -0.2402,
                                   "th_re": 0.0426, "th_hi": 0.3556},
                    "2024-02-05": {"b": -0.3125, "th_lo": -0.4167,
                                   "th_re": -0.0213, "th_hi": 0.234},
                    "2024-09-24": {"b": 0.4792, "th_lo": -0.3843,
                                   "th_re": -0.0208, "th_hi": 0.234},
                    "2025-01-14": {"b": 0.0625, "th_lo": -0.3542,
                                   "th_re": 0.0, "th_hi": 0.2708}}}
STATE_ANCHOR = {"bottom_defensive_days": 259,
                "bottom_decidable_days": 1117,
                "dual_defensive_days": 376,
                "dual_decidable_days": 1117}

_DAILY_OVERRIDE = None            # selftest synthetic-panel injection hook
_D6_FACTS_OVERRIDE = None         # selftest frozen-d6 stub hook
_ATT_OVERRIDE = None              # selftest attrition-path override


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
            "max_dd": round(dd, 6), "n_days": int(len(r)),
            "median_abs_r": round(float(np.median(np.abs(fin))), 8)
            if n else None}


def episodes_of(pos):
    """Contiguous True runs of the position face -> episode list
    (window indices, half-open spans) + entry count (0->1 edges)."""
    eps = []
    entries = 0
    t = 0
    w = len(pos)
    while t < w:
        if pos[t] > 0:
            entries += 1
            j = t
            while j < w and pos[j] > 0:
                j += 1
            eps.append((t, j))
            t = j
        else:
            t += 1
    return eps, entries


def episode_kpi(passive_ser, net_ser, episodes):
    """O-1524 KPI dual disclosure (W5 mirror). Trade-level faces (the
    law's primary reading) + the W1-lineage passive-same-days faces;
    for a long-flat timing face the vs-passive-same-days edge is
    -entry-cost by construction on intra-episode days (degenerate,
    kept for lineage comparability); the alpha question lives at the
    full-window / segment-mix level (G1/vstarts/splits)."""
    pas = np.asarray(passive_ser, dtype=float)
    cel = np.asarray(net_ser, dtype=float)
    wins_p, edges, ep_rets = 0, [], []
    for (a, b) in episodes:
        if b > len(pas):
            b = len(pas)
        if a >= b:
            continue
        e_cum = float(np.prod(1.0 + cel[a:b]) - 1.0)
        p_cum = float(np.prod(1.0 + pas[a:b]) - 1.0)
        if np.isfinite(e_cum) and np.isfinite(p_cum):
            wins_p += int(e_cum > p_cum)
            edges.append(e_cum - p_cum)
            ep_rets.append(e_cum)
    n_ep = len(ep_rets)
    win_rets = [r for r in ep_rets if r > 0]
    loss_rets = [r for r in ep_rets if r <= 0]
    payoff = None
    if win_rets and loss_rets:
        mw = float(np.mean(win_rets))
        ml = abs(float(np.mean(loss_rets)))
        payoff = round(mw / ml, 4) if ml > 0 else None
    return {
        "n_closed_episodes": n_ep,
        "win_rate_trade_level": round(
            len(win_rets) / n_ep, 4) if n_ep else None,
        "mean_episode_return": round(
            float(np.mean(ep_rets)), 8) if ep_rets else None,
        "payoff_ratio_win_over_loss": payoff,
        "win_rate_vs_passive_same_days": round(wins_p / n_ep, 4)
        if n_ep else None,
        "mean_episode_edge_vs_passive": round(float(np.mean(edges)), 8)
        if edges else None,
        "kpi_face_note": "trade-level faces are the O-1524 primary "
                         "reading; vs-passive-same-days faces are "
                         "structurally -entry-cost for long-flat timing "
                         "(degenerate, kept for W1 lineage)",
    }


# ------------------------------------------------------------------ panel
def load_closes():
    """core48 close panel, D2-truncated to the frozen evidence cutoff
    (P-5C binding; new bars beyond 2026-09-29 must not move anchors)."""
    if _DAILY_OVERRIDE is not None:
        # hermetic selftest path still exercises the real loader chain
        import _r254bmc_w7_nlnl_probe as _p254
        saved = _p254.DAILY
        _p254.DAILY = _DAILY_OVERRIDE
        try:
            panel, syms = load_core48()
        finally:
            _p254.DAILY = saved
    else:
        panel, syms = load_core48()
    cut = pd.Timestamp(EVIDENCE_CUTOFF)
    panel = panel[panel.index <= cut]
    return panel, syms


def derive_faces(closes):
    """G-PANEL + G-ANCHOR derivation (W20 masked face + theta face +
    state face + contiguity mechanism check). All comparisons rounded
    exactly like the frozen probe facts (4dp)."""
    n_syms = int(closes.shape[1])
    face = {"panel": {"n_symbols": n_syms,
                      "first_date": str(closes.index[0].date()),
                      "last_date": str(closes.index[-1].date()),
                      "n_dates": int(len(closes.index))},
            "w20": {}, "theta": {}, "state": {}}

    # ---- (a) W20 masked breadth face (r254 probe recipe verbatim)
    bd = breadth_series(closes, W_MAIN)
    m = bd["valid"] >= 30
    bdv = bd[m]
    b_masked = bdv["b"].dropna()
    face["w20"] = {
        "n_valid_days": int(len(b_masked)),
        "valid_min": int(bdv["valid"].min()),
        "valid_max": int(bdv["valid"].max()),
        "first_valid_date": str(b_masked.index[0].date()),
        "b_mean": round(float(b_masked.mean()), 4),
        "b_std": round(float(b_masked.std()), 4),
        "b_min": round(float(b_masked.min()), 4),
        "b_p5": round(float(b_masked.quantile(0.05)), 4),
        "b_p50": round(float(b_masked.quantile(0.50)), 4),
        "b_p95": round(float(b_masked.quantile(0.95)), 4),
        "b_max": round(float(b_masked.max()), 4),
        "b_q10": round(float(b_masked.quantile(0.10)), 4),
        "b_q90": round(float(b_masked.quantile(0.90)), 4),
        "days_nh_ge_10": int((bdv["nh"] >= 10).sum()),
        "days_nl_ge_10": int((bdv["nl"] >= 10).sum()),
        "days_all_member_nh": int((bdv["nh"] == bdv["valid"]).sum()),
        "days_all_member_nl": int((bdv["nl"] == bdv["valid"]).sum()),
    }

    # ---- (b) theta face (r255 probe recipe verbatim, unmasked b)
    b = bd["b"]
    th_lo = b.rolling(THETA_TRAIL, min_periods=THETA_TRAIL).quantile(0.10)
    th_hi = b.rolling(THETA_TRAIL, min_periods=THETA_TRAIL).quantile(0.90)
    th_re = b.rolling(THETA_TRAIL, min_periods=THETA_TRAIL).quantile(0.50)
    dec_mask = b.notna() & th_lo.notna()
    dec_idx = b.index[dec_mask]
    order_ok = bool((th_lo[dec_mask] <= th_re[dec_mask]).all()
                    and (th_re[dec_mask] <= th_hi[dec_mask]).all())
    face["theta"] = {
        "n_decidable_days": int(dec_mask.sum()),
        "first_decidable_date": str(dec_idx[0].date()) if len(dec_idx)
        else None,
        "order_invariant": order_ok,
        "strict_frac_lo_lt_re": round(
            float((th_lo[dec_mask] < th_re[dec_mask]).mean()), 6)
        if len(dec_idx) else None,
        "strict_frac_re_lt_hi": round(
            float((th_re[dec_mask] < th_hi[dec_mask]).mean()), 6)
        if len(dec_idx) else None,
        "th_lo_range": [round(float(th_lo[dec_mask].min()), 4),
                        round(float(th_lo[dec_mask].max()), 4)],
        "th_re_range": [round(float(th_re[dec_mask].min()), 4),
                        round(float(th_re[dec_mask].max()), 4)],
        "th_hi_range": [round(float(th_hi[dec_mask].min()), 4),
                        round(float(th_hi[dec_mask].max()), 4)],
        "extreme_day_samples": {},
    }
    for day, exp in THETA_ANCHOR["extreme_day_samples"].items():
        ts = pd.Timestamp(day)
        if ts in b.index and bool(dec_mask.loc[ts]):
            face["theta"]["extreme_day_samples"][day] = {
                "b": round(float(b.loc[ts]), 4),
                "th_lo": round(float(th_lo.loc[ts]), 4),
                "th_re": round(float(th_re.loc[ts]), 4),
                "th_hi": round(float(th_hi.loc[ts]), 4)}
        else:
            face["theta"]["extreme_day_samples"][day] = "absent-or-warmup"

    # ---- (c) state face (r255 probe variant_positions verbatim)
    pos = {v: variant_positions(b, th_lo, th_hi, th_re, v)
           for v in VARIANTS}
    for v in VARIANTS:
        face["state"][f"{v}_defensive_days"] = int((pos[v] == 0.0).sum())
        face["state"][f"{v}_decidable_days"] = int(pos[v].notna().sum())

    # ---- (d) decidable contiguity (mechanism hazard guard: a NaN
    # pos_end inside [first_dec, n) would silently propagate through
    # the window face; the frozen probe formula assumes contiguity)
    if len(dec_idx):
        first_dec = closes.index.get_loc(dec_idx[0])
        contiguous = bool(dec_mask.iloc[first_dec:].all())
    else:
        contiguous = False
    face["decidable_contiguous"] = contiguous
    lo = int(closes.index.get_loc(dec_idx[0])) + 1 if len(dec_idx) else None
    return {"faces": face, "bd": bd, "b": b, "th_lo": th_lo,
            "th_re": th_re, "th_hi": th_hi, "pos": pos, "lo": lo,
            "dec_mask": dec_mask}


def anchor_drift(derived):
    """Fail-closed reconcile: derived faces vs the frozen probe
    constants (one-face-off = config mismatch VOID, not data
    corruption). Returns list of drift strings (empty = bit-exact)."""
    bad = []
    f = derived["faces"]

    def _cmp(family, got, exp):
        for k, v in exp.items():
            g = got.get(k)
            if g != v:
                bad.append(f"{family}.{k}: {g!r} != frozen {v!r}")

    _cmp("panel", f["panel"], PANEL_ANCHOR)
    _cmp("w20", f["w20"], W20_ANCHOR)
    _cmp("theta", {k: v for k, v in f["theta"].items()
                   if k in THETA_ANCHOR}, THETA_ANCHOR)
    _cmp("state", f["state"], STATE_ANCHOR)
    if not f["decidable_contiguous"]:
        bad.append("decidable_contiguous: False (NaN-position hazard)")
    return bad


# ------------------------------------------------------------- engine leg
def cell_faces(pos_end, tgt_ret, mult):
    """Local mult-face mirror of the probe cell_returns formula
    (verbatim semantics: pos over the full index initialized 0.0,
    pos[lo:] = pos_end shifted one; gross = pos*ret; flips =
    pos.diff().abs(); net = gross - mult*COST*flips; window-sliced).
    The x1 face is parity-asserted against the imported probe
    cell_returns at run time (zero-drift proof)."""
    lo_idx = pos_end.first_valid_index()
    lo = pos_end.index.get_loc(lo_idx) + 1
    idx = pos_end.index
    n = len(idx)
    pos = pd.Series(0.0, index=idx, dtype=float)
    pos.iloc[lo:] = pos_end.iloc[lo - 1: n - 1].values
    gross = pos * tgt_ret
    flips = pos.diff().abs()
    net = gross - mult * COST_X1_RATE * flips
    return pos, gross, flips, net.iloc[lo:]


def window_pos(pos_end):
    """Window position face (numpy): pos_win[t] = pos_end[lo-1+t]."""
    lo_idx = pos_end.first_valid_index()
    lo = pos_end.index.get_loc(lo_idx) + 1
    return pos_end.iloc[lo - 1: len(pos_end) - 1].to_numpy(dtype=float), lo


# ------------------------------------------------------------------ nulls
def uniform_day_null(domain, held, n, rng):
    """One uniform random-day-placement draw (prereg s0, W4/W5 null
    family): preserve the variant's window position-day count
    (exposure), placement uniform over the pos_end domain [lo-1, n);
    flip count NOT preserved (isolated days = 2 flips each; null cost
    drag higher than the real cell = frozen honest face)."""
    npos = np.zeros(n, dtype=bool)
    if held > 0:
        idx = rng.choice(domain, size=held, replace=False)
        npos[idx] = True
    return npos


def null_net(npos, ret, lo, mult):
    """Null draw -> window net series at the given cost multiple
    (same booking law as the judged face: window-start flip booked
    against the pre-window flat face)."""
    n = len(ret)
    w = n - lo
    pos = np.zeros(w)
    for t in range(w):
        pos[t] = float(npos[lo - 1 + t])
    gross = pos * ret[lo:]
    flips = np.zeros(w)
    flips[0] = abs(pos[0] - 0.0)         # pre-window flat face
    for t in range(1, w):
        flips[t] = abs(pos[t] - pos[t - 1])
    return gross - mult * COST_X1_RATE * flips


def run_nulls(variant, held, ret, lo):
    """K=2000 null draws for one variant (shared k-stream seed law,
    rng([SEED, k]) k<2000; one draw feeds both cost faces); shard npy
    checkpoints (per, 2) for idempotent resume."""
    os.makedirs(NULL_DIR, exist_ok=True)
    n = len(ret)
    domain = np.arange(lo - 1, n)
    per = K_NULLS // NULL_SHARDS
    vals = np.empty((K_NULLS, 2))
    for s in range(NULL_SHARDS):
        path = os.path.join(NULL_DIR, f"{variant}_shard{s}.npy")
        if os.path.exists(path):
            vals[s * per:(s + 1) * per] = np.load(path)
            continue
        chunk = np.empty((per, 2))
        for i in range(per):
            k = s * per + i
            rng = np.random.default_rng([SEED, k])
            npos = uniform_day_null(domain, held, n, rng)
            n1 = null_net(npos, ret, lo, 1.0)
            n2 = null_net(npos, ret, lo, 2.0)
            chunk[i] = (sharpe_of(n1), sharpe_of(n2))
        np.save(path, chunk)
        vals[s * per:(s + 1) * per] = chunk
    out = {}
    for face_i, face in enumerate(("x1", "x2")):
        v = vals[:, face_i]
        out[face] = {
            "values": [round(float(x), 4) for x in v],
            "coverage": {"mu": round(float(v.mean()), 4),
                         "sigma": round(float(v.std(ddof=1)), 4),
                         "n_values": int(len(v))},
        }
    return out


# ------------------------------------------------- starts / splits
def virtual_starts(series_by_face, passive):
    """K=1000 random virtual starts x 3 windows (law s1); one rng per k
    shared across windows (nested windows honest overlap disclosed);
    beat = cell window cum (own cost face) > passive window cum."""
    out = {"n_starts": K_STARTS, "windows_days": WIN_DAYS, "cells": {}}
    n = len(passive)
    wmax = max(WIN_DAYS.values())
    los = []
    for k in range(K_STARTS):
        rng = np.random.default_rng([SEED, 2000 + k])
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


def split_windows(series_by_face):
    """100 random split windows (law s3): split point in [0.2n, 0.8n],
    half-window Sharpe same-sign rate >= 80% = segment-stable."""
    out = {}
    for name, ser in series_by_face.items():
        r = np.asarray(ser, dtype=float)
        n = len(r)
        agree = 0
        for k in range(K_SPLITS):
            rng = np.random.default_rng([SEED, 3000 + k])
            cut = int(rng.integers(int(0.2 * n), int(0.8 * n)))
            a, b = sharpe_of(r[:cut]), sharpe_of(r[cut:])
            agree += int((a > 0) == (b > 0))
        rate = agree / K_SPLITS
        out[name] = {"same_sign_rate": round(rate, 4),
                     "segment_stable": bool(rate >= 0.80),
                     "n_splits": K_SPLITS}
    return out


# ------------------------------------------------------------------ d6
def frozen_d6_block():
    """Verbatim copy of the freeze-window D6 record (W6 paradigm: the
    admission record = the freeze-window artifact, no re-computation)."""
    path = _D6_FACTS_OVERRIDE or D6_FACTS_PATH
    with open(path, encoding="utf-8") as fh:
        facts = json.load(fh)
    d6 = dict(facts["d6_cells_face"])
    d6["freeze_artifact"] = ("results/_r255bmc_w7_nnl_d6_probe_facts.json "
                             "(frozen r255 bm-c, no re-computation, W6 "
                             "admission-record paradigm)")
    d6["reject_line"] = D6_REJECT
    return d6


# --------------------------------------------------------------- attrition
def _att_json_path():
    """prereg s6: the EXECUTING machine's lane file (gate_attrition
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


# ------------------------------------------------------------------ product
def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 16), b""):
            h.update(blk)
    return h.hexdigest()


def phase1_write(product):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(product, fh, ensure_ascii=False, indent=1)
    os.replace(OUT_JSON + ".tmp", OUT_JSON)
    return product


def finalize(product, cells, passive_ser, passive_stats):
    prev_total = None
    if os.path.exists(OUT_JSON):
        try:
            with open(OUT_JSON, encoding="utf-8") as fh:
                old = json.load(fh)
            prev_total = (old.get("trials_ledger") or {}).get("prev_total")
        except Exception:
            prev_total = None
    passive_override = passive_stats["sharpe_full"]
    gates = {}
    for (variant, face) in CELL_FACES:
        cname = CELL_NAME[(variant, face)]
        net = cells[(variant, face)]["net"]
        st = cells[(variant, face)]["stats"]
        nulls_face = product["nulls"][variant][face]
        g1 = SG.g1_prime_v2(st["sharpe_full"], net,
                            batch_cells=BATCH_CELLS, pool="core48",
                            results_dir=OUT_DIR_RESULTS,
                            null_pool={"values": nulls_face["values"],
                                       "coverage": nulls_face["coverage"]},
                            n_trades=cells[(variant, face)]["entries"],
                            n_entries=cells[(variant, face)]["entries"],
                            passive_override=passive_override)
        dsr = SG.deflated_sharpe_ratio(
            net, n_trials=g1["skill_line"]["n_eff"])
        gates[cname] = {"g1_prime_v2": g1, "dsr": dsr,
                        "cost_face_role": "judged (V1 legacy base)"
                        if face == "x1" else "stress-disclosure"}
    mat = pd.DataFrame({CELL_NAME[vf]: np.asarray(
        cells[vf]["net"], dtype=float) for vf in CELL_FACES})
    pbo = cscv_pbo(mat)
    for cname in gates:
        gates[cname]["g2"] = SG.g2_registration_v2(
            gates[cname]["g1_prime_v2"]["pass_v2"], gates[cname]["dsr"],
            float(pbo["pbo"]))
    ledger = SG.append_ledger(BATCH_NAME, BATCH_CELLS,
                              file_name="results/innovation_quota/"
                                        "NNL-BREADTH-P1.json",
                              evidence_cutoff=EVIDENCE_CUTOFF,
                              prev_total=prev_total)
    product["gates"] = gates
    product["family_pbo"] = pbo
    product["passive_override_fed"] = passive_override
    # prereg s3/s4 live-read reference columns (judgment-line reading
    # face disclosure; NOT the judgment inputs -- passive_override +
    # batch-own null_pool above are the judgment face)
    try:
        product["line_reading_reference"] = {
            "core48_pool_passive_baseline": SG.passive_baseline("core48",
                                                                 OUT_DIR_RESULTS),
            "shared_null_collector": SG.null_sharpes(OUT_DIR_RESULTS)
            ["coverage"],
            "note": "reference columns live-read per prereg s4 "
                    "'judgment-line reading face: re-read current values "
                    "at freeze window (live-calculation law, no "
                    "hand-copying)'",
        }
    except Exception as ex:
        product["line_reading_reference"] = {"error": str(ex)}
    n_pass = sum(1 for g in gates.values()
                 if g["g1_prime_v2"]["pass_v2"])
    n_g2 = sum(1 for g in gates.values() if g["g2"]["eligible_v2"])
    product["funnel"] = {
        "harvest_column": 1,
        "harvest_note": "zoo #87 nh_nl_breadth param-frozen untried "
                        "family, r254/r255 probe facts (quota line: "
                        "first two-sided-extreme breadth state-gate "
                        "face; A-layer last unburned family)",
        "gate_column": f"{n_pass}/{len(CELL_FACES)} g1_prime_v2 pass, "
                       f"{n_g2}/{len(CELL_FACES)} G2-eligible (judged)",
    }
    product["episode_kpi"] = {
        CELL_NAME[vf]: episode_kpi(passive_ser, cells[vf]["net"],
                                  cells[vf]["episodes"])
        for vf in CELL_FACES}
    product["trials_ledger"] = ledger          # r434 pit law: value carried
    product["judgment_note"] = (
        "judged per prereg s4 via shared library; batch_cells=2004 s0 "
        "counting law (4 judged cells + 2000 null draws -- prereg s4's "
        "'batch_cells=4' is the judged-cell shorthand per the W5 "
        "'batch_cells=3'->2003 family reconciliation); null_pool = "
        "batch-own per-cell family per s0 compute budget + s4 seed "
        "k-allocation 'nulls k<2000, W3/W4/W5 semantics' (s4's "
        "'shared collector n=120' phrase = W6-template carryover, "
        "reconciled at build time zero-run, disclosed; the shared "
        "collector stays a live-read reference column); passive_"
        "override = 510300-BH batch-window live Sharpe (W1-W5 harness "
        "face); judged-negative family = slot closed + new-evidence "
        "reopen note (law s5); G2-eligible cell = T-34 fastline "
        "candidate pool registration face, intake walks the CE "
        "admission harness separately; T0 brake authority stays with "
        "REGIME_GUARD")
    phase1_write(product)
    _attr_row(BATCH_NAME, BATCH_CELLS, int(ledger["total"]),
              {"g1_pass": {c: gates[c]["g1_prime_v2"]["pass_v2"]
                           for c in gates},
               "g2_eligible": {c: gates[c]["g2"]["eligible_v2"]
                               for c in gates},
               "family_pbo": pbo},
              {"episodes": {CELL_NAME[vf]: cells[vf]["entries"]
                            for vf in CELL_FACES},
               "defensive_days": product["state_face"],
               "turnover_breaches": {CELL_NAME[vf]:
                                     cells[vf]["turnover_breach"]
                                     for vf in CELL_FACES}})
    return product


# ------------------------------------------------------------------ driver
def _build_batch(P):
    """Cells + passive from the derived faces. Returns (cells dict,
    passive_ser, passive_stats, lo)."""
    closes = P["closes"]
    lo = P["lo"]
    tgt_ret = closes[TARGET].astype(float).pct_change()
    passive_ser = tgt_ret.iloc[lo:].to_numpy(dtype=float)
    passive_stats = _cell_stats(passive_ser)
    cells = {}
    pos_cache = {}
    for variant in VARIANTS:
        pos_end = P["pos"][variant]
        pos_win, _ = window_pos(pos_end)
        eps, entries = episodes_of(pos_win)
        held = int((pos_win > 0).sum())
        pos_cache[variant] = {"pos_win": pos_win, "episodes": eps,
                              "entries": entries, "held": held}
        # parity assert: local mult-1 face == probe cell_returns (zero
        # re-implementation drift proof, every run)
        _, _, _, net_probe = cell_faces(pos_end, tgt_ret, 1.0)
        probe_ref = cell_returns(pos_end, tgt_ret)
        if not np.allclose(np.asarray(net_probe, dtype=float),
                           np.asarray(probe_ref, dtype=float),
                           equal_nan=True, rtol=0, atol=0):
            raise RuntimeError(
                f"parity drift {variant}: local mult-1 net != probe "
                f"cell_returns (verbatim-import broken)")
    years = len(passive_ser) / float(PBP)
    for (variant, face) in CELL_FACES:
        pos_end = P["pos"][variant]
        mult = CELL_MULT[face]
        _, _, _, net = cell_faces(pos_end, tgt_ret, mult)
        pc = pos_cache[variant]
        cells[(variant, face)] = {
            "net": np.asarray(net, dtype=float),
            "stats": _cell_stats(net), "episodes": pc["episodes"],
            "entries": pc["entries"], "held": pc["held"],
            "entries_per_year": round(pc["entries"] / years, 2)
            if years > 0 else None,
            "turnover_breach": bool(pc["entries"] / years
                                    > TURNOVER_BUDGET)
            if years > 0 else None,
        }
    return cells, passive_ser, passive_stats, pos_cache


def cmd_run():
    global SEED
    if SEED_KEY not in SG.SEED_REGISTRY:
        return gate_refuse(f"SEED_REGISTRY key {SEED_KEY} missing "
                           f"(freeze-window registration absent)")
    SEED = SG.SEED_REGISTRY[SEED_KEY]
    t0 = time.time()
    closes, syms = load_closes()
    P = derive_faces(closes)
    P["closes"] = closes
    bad = anchor_drift(P)
    if bad:
        for b in bad[:12]:
            print(f"  drift: {b}")
        return gate_refuse(f"G-ANCHOR drift {len(bad)} face(s) vs frozen "
                           f"probe facts -- config mismatch VOID "
                           f"(one-face-off law)")
    print(f"G-ANCHOR reconcile: bit-exact ({time.time() - t0:.0f}s)",
          flush=True)
    lo = P["lo"]
    n = len(closes.index)
    print(f"panel ok: {P['faces']['panel']['n_dates']} dates x "
          f"{P['faces']['panel']['n_symbols']} syms, lo={lo} "
          f"({time.time() - t0:.0f}s)", flush=True)

    cells, passive_ser, passive_stats, pos_cache = _build_batch(P)
    for vf in CELL_FACES:
        c = cells[vf]
        print(f"  cell {CELL_NAME[vf]}: sharpe="
              f"{c['stats']['sharpe_full']} entries={c['entries']} "
              f"epy={c['entries_per_year']} "
              f"({time.time() - t0:.0f}s)", flush=True)

    nulls = {}
    for variant in VARIANTS:
        nulls[variant] = run_nulls(variant, pos_cache[variant]["held"],
                                   P["closes"][TARGET].astype(float)
                                   .pct_change().to_numpy(dtype=float),
                                   lo)
        for face in ("x1", "x2"):
            cov = nulls[variant][face]["coverage"]
            print(f"  nulls {variant}-{face}: mu={cov['mu']} "
                  f"sigma={cov['sigma']} ({time.time() - t0:.0f}s)",
                  flush=True)

    series_by_face = {CELL_NAME[vf]: cells[vf]["net"] for vf in CELL_FACES}
    vstarts = virtual_starts(series_by_face, passive_ser)
    splits = split_windows({**series_by_face,
                            "PASSIVE-510300-BH": passive_ser})
    d6 = frozen_d6_block()
    product = {
        "batch": BATCH_NAME,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "cutoff_meta": SG.cutoff_meta(EVIDENCE_CUTOFF),
        "prereg": "research/INNOVATION_QUOTA_W7_PREREG.md (r254 bm-c "
                  "berth + r255 bm-c freeze, seed 20325000)",
        "prereg_sha256_16": _sha256_file(os.path.join(
            ROOT, "research", "INNOVATION_QUOTA_W7_PREREG.md"))[:16],
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "seed": {"base": SEED, "k_nulls": K_NULLS,
                 "k_substreams": "nulls k<2000; starts k in "
                                 "[2000,3000); splits k in [3000,3100) "
                                 "-- rng([SEED, k]) one k-stream shared "
                                 "across variants/cost faces (W5 law)"},
        "panel": P["faces"]["panel"],
        "anchor_faces": {"w20": P["faces"]["w20"],
                         "theta": P["faces"]["theta"],
                         "state": P["faces"]["state"]},
        "state_face": {f"{v}_defensive_days":
                       P["faces"]["state"][f"{v}_defensive_days"]
                       for v in VARIANTS},
        "construction": "verbatim-import results/_r254bmc_w7_nlnl_probe.py "
                        "(load_core48 + breadth_series) + results/"
                        "_r255bmc_w7_nnl_d6_probe.py (variant_positions + "
                        "cell_returns) -- r456 single-source paradigm, "
                        "parity-asserted every run",
        "engine_law": "B_t(W20) = (NH_t - NL_t)/valid_t over core48 "
                      "members with full 20-bar lookback (honest "
                      "denominator); theta = trailing-500d rolling "
                      "q10/q50/q90 (min_periods 500, zero hand-copied "
                      "constants); bottom: B<=th_lo flat / B>=th_re "
                      "long / else maintain; dual: + B>=th_hi flat, "
                      "(th_re,th_hi) maintain band = top-leg "
                      "hysteresis; INITIAL = long at first decidable "
                      "day (frozen r255, first-day triggers apply); "
                      "T+1 onset close-to-close (pos[t]=pos_end[t-1]); "
                      "batch lo = first_decidable+1 (W5 law); cost = "
                      "COST_X1_RATE on |dpos| booked next day, "
                      "window-start entry vs pre-window flat; x2 = "
                      "CostPatch(2.0) stress face; hold-period >=3d "
                      "constraint EXEMPT per prereg s3 (state-gate "
                      "holds = signal continuous segments, defense "
                      "segments at 0 = cash-leg legal state)",
        "batch_window": {"lo_bar_index": lo, "window_days": n - lo,
                          "law": "lo = first decidable day + 1; "
                                 "pre-lo days = breadth/theta warmup, "
                                 "disclosed; four-cell shared window "
                                 "(cross-cell PBO/CSCV alignment)"},
        "cost_face": {"x1_rate_per_side": COST_X1_RATE,
                      "judged_face": "x1 (V1 legacy base)",
                      "x2_disclosure": "CostPatch(2.0) = 26.082bp/side "
                                       "stress face",
                      "turnover_budget_per_year": TURNOVER_BUDGET},
        "passive": {"passive_510300_bh": {"full": passive_stats}},
        "cells": {CELL_NAME[vf]: {**cells[vf]["stats"],
                                  "variant": vf[0], "cost_face": vf[1],
                                  "n_entries": cells[vf]["entries"],
                                  "entries_per_year":
                                      cells[vf]["entries_per_year"],
                                  "turnover_budget_ok":
                                      not cells[vf]["turnover_breach"],
                                  "window_position_days":
                                      cells[vf]["held"]}
                  for vf in CELL_FACES},
        "nulls": nulls, "virtual_starts": vstarts, "splits": splits,
        "d6": d6,
        "funnel": {"harvest_column": 1,
                   "gate_column": "0/4 pending judgment (this batch)"},
    }
    phase1_write(product)
    print(f"phase-1 product written ({time.time() - t0:.0f}s)", flush=True)
    product = finalize(product, cells, passive_ser, passive_stats)
    print(f"finalize ok: cells={len(cells)} "
          f"ledger={product['trials_ledger']['total']} "
          f"elapsed={time.time() - t0:.0f}s")
    return 0


def cmd_verify():
    """Real-panel G-ANCHOR reconcile (read-only; no engine, no
    product, no ledger). Build-time pre-verification face."""
    closes, _syms = load_closes()
    P = derive_faces(closes)
    bad = anchor_drift(P)
    if bad:
        for b in bad[:12]:
            print(f"  drift: {b}")
        print(f"GATE-REFUSE(exit2): G-ANCHOR drift {len(bad)} face(s) "
              f"vs frozen probe facts -- config mismatch VOID "
              f"(one-face-off law)")
        return 2
    print("G-ANCHOR verify: ALL faces bit-exact vs frozen probe facts "
          f"(panel {P['faces']['panel']['first_date']}.."
          f"{P['faces']['panel']['last_date']}, "
          f"{P['faces']['panel']['n_dates']} dates x "
          f"{P['faces']['panel']['n_symbols']} syms; W20 "
          f"{P['faces']['w20']['n_valid_days']} days; theta "
          f"{P['faces']['theta']['n_decidable_days']} decidable; "
          f"bottom/dual defensive "
          f"{P['faces']['state']['bottom_defensive_days']}/"
          f"{P['faces']['state']['dual_defensive_days']})")
    return 0


# ------------------------------------------------------------------ selftest
def _mk_core48_fixture(tmp):
    """Synthetic core48-like panel: 48 members x ~1000 bdays with a
    common factor + planted broad rally/crash segments so B_t crosses
    the theta bands in both directions (bottom defense, top defense,
    mid maintain all exercised) plus staggered member maturity (valid
    ramp face). One member is code 510300 (the traded target)."""
    rng = np.random.default_rng(11)
    n = 1200                 # theta trail 500 + W20 warmup leaves a
                             # window > 504d (24m vstart face exercises)
    dates = pd.bdate_range("2020-01-02", periods=n)
    common = rng.normal(0.0, 0.006, n)
    common[800:860] += 0.010        # broad rally -> euphoria band
    common[860:900] -= 0.004
    common[950:1010] -= 0.011       # broad crash -> capitulation band
    common[1020:1060] += 0.006
    frames = {}
    codes = ["510300"] + [f"{510400 + i}" for i in range(47)]
    for j, code in enumerate(codes):
        load = rng.normal(0.0, 0.010, n) + common * \
            rng.uniform(0.6, 1.4)
        # staggered maturity: members j>=40 start later (valid ramp)
        if j >= 40:
            load[:30 + 3 * (j - 40)] = np.nan
        s = pd.Series(1.0 + np.cumsum(np.nan_to_num(load)),
                      index=dates)
        s = s.where(np.isfinite(load), np.nan)
        # forward-fill the price level for late-listed members (close
        # exists only from their first bar; union index carries NaN)
        first = int(np.argmax(np.isfinite(s.to_numpy())))
        vals = s.to_numpy(dtype=float).copy()   # CoW read-only view guard
        vals[:first] = np.nan
        close = pd.Series(vals, index=dates)
        close = close + 1.0        # positive price level
        df = pd.DataFrame({
            "date": dates.strftime("%Y-%m-%d"),
            "open": close, "high": close * 1.01, "low": close * 0.99,
            "close": close, "volume": 1e6, "amount": close * 1e6,
        })
        df = df.dropna(subset=["close"])
        df.to_csv(os.path.join(tmp, f"{code}.csv"), index=False)
    return codes


def cmd_selftest():
    global OUT_DIR, NULL_DIR, OUT_JSON, OUT_DIR_RESULTS, ATT_JSON_SHARED, \
        SEED, K_NULLS, NULL_SHARDS, K_STARTS, K_SPLITS, PANEL_ANCHOR, \
        W20_ANCHOR, THETA_ANCHOR, STATE_ANCHOR, _DAILY_OVERRIDE, \
        _D6_FACTS_OVERRIDE, _ATT_OVERRIDE, EVIDENCE_CUTOFF
    tmp = tempfile.mkdtemp(prefix="innovation_quota_w7_selftest_")
    K_NULLS, NULL_SHARDS = 40, 2     # >= 30: skill_line_v2 thin-pool floor
    K_STARTS, K_SPLITS = 12, 6
    SEED = 20325000
    # tmp-path reassignment FIRST: every face (nulls included) must
    # stay hermetic -- a late reassignment poisons the real nulls_w7
    # dir with selftest-sized shards (W3 resume-broadcast lineage)
    OUT_DIR = os.path.join(tmp, "results", "innovation_quota")
    NULL_DIR = os.path.join(OUT_DIR, "nulls_w7")
    OUT_JSON = os.path.join(OUT_DIR, "NNL-BREADTH-P1.json")
    OUT_DIR_RESULTS = os.path.dirname(OUT_DIR)
    os.makedirs(NULL_DIR, exist_ok=True)
    _ATT_OVERRIDE = os.path.join(tmp, "gate_attrition.lane.json")
    json.dump({"entries": []}, open(_ATT_OVERRIDE, "w"))
    daily = os.path.join(tmp, "daily")
    os.makedirs(daily)
    codes = _mk_core48_fixture(daily)
    _DAILY_OVERRIDE = daily
    # frozen-d6 stub (the real facts file is a burn artifact; selftest
    # must stay hermetic)
    d6_tmp = os.path.join(tmp, "d6_facts.json")
    json.dump({"d6_cells_face": {
        "batch_internal_bottom_vs_dual": 0.5,
        "vs_t33_cells": {"stub_cell": {"bottom": 0.1, "dual": 0.2}},
        "merge_clause_applied": [],
        "vs_registered_six": {"max_abs_corr": 0.2,
                               "argmax": "STUB-CE-01"}}},
        open(d6_tmp, "w"))
    _D6_FACTS_OVERRIDE = d6_tmp
    ok = []
    try:
        # ---- state-machine hand-checks (frozen probe semantics; the
        # dual re-entry zone is the LOWER band (lo, re] and the
        # maintain band (re, hi) is the top-leg hysteresis carry --
        # verbatim probe rule order, counts 259/376 pin it)
        idx = pd.bdate_range("2022-01-03", periods=8)
        b = pd.Series([0.5, 0.3, 0.1, -0.1, -0.5, -0.05, 0.05, 0.6],
                      index=idx)
        const = pd.Series(0.0, index=idx)
        th_lo = pd.Series(-0.4, index=idx)
        th_hi = pd.Series(0.4, index=idx)
        pos_b = variant_positions(b, th_lo, th_hi, const, "bottom")
        pos_d = variant_positions(b, th_lo, th_hi, const, "dual")
        # bottom: 0.5>=re long; 0.3/0.1 long; -0.1 mid maintain long;
        # -0.5<=lo flat; -0.05 mid maintain flat; 0.05>=re re-enter;
        # 0.6 long
        ok.append(("bottom gate: zones + maintain + re-entry",
                   list(pos_b.to_numpy()) ==
                   [1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0]))
        # dual: 0.5>=hi flat; 0.3/0.1 (re,hi) maintain flat (top-leg
        # hysteresis); -0.1<=re re-enter long; -0.5 flat; -0.05<=re
        # long; 0.05 (re,hi) maintain long; 0.6>=hi flat
        ok.append(("dual gate: top leg hysteresis via maintain band",
                   list(pos_d.to_numpy()) ==
                   [0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0]))
        # initial state: long at first decidable when NO trigger fires
        # (all three days strictly inside the mid band (lo, re))
        idx3 = pd.bdate_range("2022-01-03", periods=3)
        b2 = pd.Series([-0.05, -0.02, -0.01], index=idx3)
        p2 = variant_positions(b2, pd.Series(-0.9, index=idx3),
                               pd.Series(0.9, index=idx3),
                               pd.Series(0.0, index=idx3), "bottom")
        ok.append(("initial = long at first decidable (no trigger)",
                   list(p2.to_numpy()) == [1.0, 1.0, 1.0]))
        # first-day trigger still applies (probe semantics)
        b3 = pd.Series([-0.95, 0.1, 0.2], index=idx3)
        p3 = variant_positions(b3, pd.Series(-0.9, index=idx3),
                               pd.Series(0.9, index=idx3),
                               pd.Series(0.0, index=idx3), "bottom")
        ok.append(("first-decidable trigger applies same day",
                   list(p3.to_numpy()) == [0.0, 1.0, 1.0]))

        # ---- T+1 onset + cost booking via cell_faces
        idx4 = pd.bdate_range("2020-01-02", periods=10)
        pe = pd.Series([np.nan, np.nan, 1.0, 1.0, 0.0, 0.0, 1.0,
                        np.nan, np.nan, np.nan], index=idx4)
        tgt_vals = np.array([0.01, 0.02, 0.03, -0.04, 0.05, 0.06,
                             0.0, 0.0, 0.0, 0.0])
        tgt = pd.Series(tgt_vals, index=idx4)
        pos, gross, flips, net = cell_faces(pe, tgt, 1.0)
        # window lo = first_valid(2)+1 = 3; pos[3]=pe[2]=1, pos[4]=pe[3]
        # =1, pos[5]=pe[4]=0, pos[6]=pe[5]=0, pos[7]=pe[6]=1, pos[8]=
        # pe[7]=NaN -> NaN position (non-decidable tail, disclosed)
        ok.append(("cell_faces T+1 onset window",
                   list(pos.iloc[3:8].to_numpy()) ==
                   [1.0, 1.0, 0.0, 0.0, 1.0]))
        # entry flip at window start vs pre-window flat + exit flip
        f3 = flips.iloc[3:8].to_numpy()
        ok.append(("cost booking x1 on |dpos| next day",
                   abs(f3[0] - 1.0) < 1e-12 and abs(f3[2] - 1.0) < 1e-12
                   and abs(f3[4] - 1.0) < 1e-12))
        ok.append(("net = gross - x1*flips",
                   abs(float(net.iloc[0]) -
                       (tgt_vals[3] * 1.0 - COST_X1_RATE)) < 1e-12))

        # ---- null draw: exposure preserved, domain excludes pre-lo
        n_t = 10
        domain = np.arange(3, n_t)
        npos = uniform_day_null(domain, 3, n_t,
                                np.random.default_rng([SEED, 0]))
        ok.append(("null preserves position-day count",
                   int(npos.sum()) == 3 and not npos[0] and
                   not npos[1] and not npos[2]))

        # ---- fixture derive-then-freeze (W5 pattern): anchors are
        # derived from the CSV-READ frame via the REAL probe loader
        closes, syms = load_closes()
        ok.append(("fixture loads via real probe loader",
                   closes.shape[1] == 48 and "510300" in closes.columns))
        cut = str(closes.index[-1].date())
        EVIDENCE_CUTOFF = cut
        P = derive_faces(closes)
        ok.append(("fixture exercises all zones",
                   P["faces"]["state"]["bottom_defensive_days"] > 0
                   and P["faces"]["state"]["dual_defensive_days"] > 0
                   and P["faces"]["theta"]["n_decidable_days"] > 30))
        PANEL_ANCHOR = dict(P["faces"]["panel"])
        W20_ANCHOR = dict(P["faces"]["w20"])
        THETA_ANCHOR = {k: v for k, v in P["faces"]["theta"].items()
                        if k in ("n_decidable_days", "first_decidable_date",
                                 "order_invariant", "strict_frac_lo_lt_re",
                                 "strict_frac_re_lt_hi", "th_lo_range",
                                 "th_re_range", "th_hi_range",
                                 "extreme_day_samples")}
        THETA_ANCHOR["extreme_day_samples"] = \
            P["faces"]["theta"]["extreme_day_samples"]
        STATE_ANCHOR = dict(P["faces"]["state"])
        bad = anchor_drift(P)
        ok.append(("derive-then-freeze anchors pass", bad == []))
        P["closes"] = closes

        # ---- full pipeline on fixture
        cells, passive_ser, passive_stats, pos_cache = _build_batch(P)
        ok.append(("4 cells + passive derive finite",
                   all(np.isfinite(cells[vf]["stats"]["sharpe_full"])
                       for vf in CELL_FACES)
                   and np.isfinite(passive_stats["sharpe_full"])))
        ok.append(("both variants see real state traffic (episodes)",
                   all(cells[(v, "x1")]["entries"] >= 1
                       for v in VARIANTS)))
        ok.append(("x2 sharpe <= x1 sharpe (stress face)",
                   cells[("bottom", "x2")]["stats"]["sharpe_full"] <=
                   cells[("bottom", "x1")]["stats"]["sharpe_full"] + 1e-9
                   and cells[("dual", "x2")]["stats"]["sharpe_full"] <=
                   cells[("dual", "x1")]["stats"]["sharpe_full"] + 1e-9))
        n1 = run_nulls("bottom", pos_cache["bottom"]["held"],
                       closes[TARGET].astype(float).pct_change()
                       .to_numpy(dtype=float), P["lo"])
        n2 = run_nulls("bottom", pos_cache["bottom"]["held"],
                       closes[TARGET].astype(float).pct_change()
                       .to_numpy(dtype=float), P["lo"])
        ok.append(("nulls deterministic (npy resume) + dual-face size",
                   n1["x1"]["values"] == n2["x1"]["values"]
                   and len(n1["x1"]["values"]) == K_NULLS
                   and len(n1["x2"]["values"]) == K_NULLS))
        nulls = {v: run_nulls(v, pos_cache[v]["held"],
                              closes[TARGET].astype(float).pct_change()
                              .to_numpy(dtype=float), P["lo"])
                 for v in VARIANTS}
        series_by_face = {CELL_NAME[vf]: cells[vf]["net"]
                          for vf in CELL_FACES}
        vstarts = virtual_starts(series_by_face, passive_ser)
        splits = split_windows({**series_by_face,
                                "PASSIVE-510300-BH": passive_ser})
        d6 = frozen_d6_block()
        ok.append(("vstarts/splits/d6 shapes",
                   set(vstarts["cells"]) == set(CELL_NAME.values())
                   and all(set(vstarts["cells"][c]) == set(WIN_DAYS)
                           for c in vstarts["cells"])
                   and all("segment_stable" in splits[s]
                           for s in splits)
                   and d6["merge_clause_applied"] == []))
        product = {
            "batch": BATCH_NAME,
            "evidence_cutoff": EVIDENCE_CUTOFF,
            "cutoff_meta": SG.cutoff_meta(EVIDENCE_CUTOFF),
            "prereg": "selftest fixture",
            "seed": {"base": SEED},
            "panel": P["faces"]["panel"],
            "anchor_faces": {"w20": P["faces"]["w20"],
                             "theta": P["faces"]["theta"],
                             "state": P["faces"]["state"]},
            "state_face": {f"{v}_defensive_days":
                           P["faces"]["state"][f"{v}_defensive_days"]
                           for v in VARIANTS},
            "passive": {"passive_510300_bh": {"full": passive_stats}},
            "cells": {CELL_NAME[vf]: {**cells[vf]["stats"],
                                      "n_entries": cells[vf]["entries"],
                                      "entries_per_year":
                                          cells[vf]["entries_per_year"],
                                      "turnover_budget_ok":
                                          not cells[vf][
                                              "turnover_breach"],
                                      "window_position_days":
                                          cells[vf]["held"]}
                      for vf in CELL_FACES},
            "nulls": nulls, "virtual_starts": vstarts,
            "splits": splits, "d6": d6,
            "funnel": {"harvest_column": 1,
                       "gate_column": "0/4 pending judgment (fixture)"},
        }
        phase1_write(product)
        ok.append(("phase-1 product fields",
                   os.path.exists(OUT_JSON)
                   and product["cutoff_meta"]["evidence_cutoff"] ==
                   EVIDENCE_CUTOFF
                   and set(product["cells"]) == set(CELL_NAME.values())))

        # ---- r450 landed-state guard: judged product refuses re-run
        with open(OUT_JSON + ".tmp2", "w", encoding="utf-8") as fh:
            json.dump({"trials_ledger": {"prev_total": 1, "total": 2}},
                      fh)
        os.replace(OUT_JSON + ".tmp2", OUT_JSON)
        ok.append(("r450 guard: judged product refuses (rc=2 face)",
                   _refuse_if_judged() == 2))
        phase1_write(product)
        ok.append(("r450 guard: phase-1-only product resumes",
                   _refuse_if_judged() == 0))

        # shared-library stateful faces stubbed (hermetic isolation)
        _ne, _al, _lh = SG.n_eff, SG.append_ledger, SG.ledger_head
        SG.n_eff = lambda bc, rd=None: int(bc)
        SG.append_ledger = lambda *a, **k: {"prev_total": 0,
                                            "total": 100,
                                            "batch": BATCH_NAME}
        SG.ledger_head = lambda rd=None: {"total": 500, "file": None,
                                          "note": None}
        _real_cscv = globals()["cscv_pbo"]
        globals()["cscv_pbo"] = lambda mat: {"pbo": 0.1}
        try:
            product = finalize(product, cells, passive_ser, passive_stats)
            ok.append(("finalize product fields",
                       os.path.exists(OUT_JSON)
                       and len(product["gates"]) == 4
                       and all("g2" in g for g in product["gates"].values())
                       and product["trials_ledger"]["total"] == 100
                       and product["passive_override_fed"] ==
                       passive_stats["sharpe_full"]
                       and "batch_cells" in
                       product["judgment_note"]))
            ok.append(("episode kpi face (O-1524 trade-level + lineage)",
                       all("win_rate_vs_passive_same_days"
                           in product["episode_kpi"][c]
                           and "win_rate_trade_level"
                           in product["episode_kpi"][c]
                           for c in product["episode_kpi"])))
            att = json.load(open(_ATT_OVERRIDE, encoding="utf-8"))
            ok.append(("attrition lane row landed (executing-machine law)",
                       att["entries"][-1]["batch"] == BATCH_NAME
                       and att["entries"][-1]["cells_ledger_delta"]
                       == BATCH_CELLS))
        finally:
            SG.n_eff, SG.append_ledger, SG.ledger_head = _ne, _al, _lh
            globals()["cscv_pbo"] = _real_cscv

        # ---- gate-refusal paths (drift -> refuse, not corruption)
        real = PANEL_ANCHOR["n_dates"]
        PANEL_ANCHOR = dict(PANEL_ANCHOR, n_dates=real + 1)
        closes2, _s = load_closes()
        P2 = derive_faces(closes2)
        ok.append(("G-PANEL drift refusal", anchor_drift(P2) != []))
        PANEL_ANCHOR = dict(PANEL_ANCHOR, n_dates=real)
        real_def = STATE_ANCHOR["bottom_defensive_days"]
        STATE_ANCHOR = dict(STATE_ANCHOR,
                            bottom_defensive_days=real_def + 1)
        ok.append(("state-face drift refusal", anchor_drift(P2) != []))
        STATE_ANCHOR = dict(STATE_ANCHOR,
                            bottom_defensive_days=real_def)
        real_dec = THETA_ANCHOR["n_decidable_days"]
        THETA_ANCHOR = dict(THETA_ANCHOR, n_decidable_days=real_dec + 1)
        ok.append(("theta-face drift refusal", anchor_drift(P2) != []))
        THETA_ANCHOR = dict(THETA_ANCHOR, n_decidable_days=real_dec)
        real_b = W20_ANCHOR["b_q10"]
        W20_ANCHOR = dict(W20_ANCHOR, b_q10=real_b + 0.5)
        ok.append(("W20-face drift refusal", anchor_drift(P2) != []))
        W20_ANCHOR = dict(W20_ANCHOR, b_q10=real_b)
        ok.append(("anchor restored -> gates pass again",
                   anchor_drift(P2) == []))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n_ok = sum(1 for _, v in ok if v)
    print(f"innovation_quota_w7 selftest: {n_ok}/{len(ok)} PASS")
    for name, v in ok:
        if not v:
            print(f"  FAIL: {name}")
    return 0 if n_ok == len(ok) else 1


# ------------------------------------------------------------------ guard
def _refuse_if_judged():
    """r450 landed-state guard: read CONTENT (trials_ledger block), not
    existence/timestamps. Judged product refuses re-run (rc=2) unless
    INNOVATION_QUOTA_W7_REFINALIZE=1; phase-1-only product resumes."""
    if not os.path.exists(OUT_JSON):
        return 0
    try:
        with open(OUT_JSON, encoding="utf-8") as fh:
            old = json.load(fh)
    except Exception:
        return 0        # unreadable partial write -> resume path
    if (old.get("trials_ledger") or {}).get("total") is not None and \
            os.environ.get("INNOVATION_QUOTA_W7_REFINALIZE") != "1":
        print("GATE-REFUSE(exit2): NNL-BREADTH-P1.json already "
              "judged (trials_ledger present, content-read per r450); "
              "INNOVATION_QUOTA_W7_REFINALIZE=1 = only redo")
        return 2
    return 0


def main():
    try:
        # r236 GBK-console law: reconfigure at entry (idempotent, must
        # not depend on last round's output having no unencodable chars)
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
