# -*- coding: utf-8 -*-
"""INNOVATION_QUOTA_W9 runner -- CROWD-VOTE-P1 crowding four-vote
composite judged batch (INNOVATION-QUOTA-SLOT-9, zoo #84
crowding_vote, prereg research/INNOVATION_QUOTA_W9_PREREG.md FROZEN
bm-c r260; berth probe facts results/_r259bmc_w9_crowding_probe_facts.json
+ freeze-window facts results/_r260bmc_w9_d6_cells_probe_facts.json;
seed 20326000 three-step law ALL GREEN
results/_r260bmc_w9_seed_law_facts.json).

Laws (all construction faces verbatim-import from the two probes --
r456 single-source zero-drift paradigm; state machine + return
booking defined in the freeze probe = the runner's construction face):

  panel   core48 bare-code close panel via _r259bmc_w9_crowding_probe.
          load_core48 (data/daily/*.csv 6-digit names, union date
          index), truncated to evidence cutoff 2026-09-29 (P-5C
          frozen binding, prereg s2). G-PANEL: 48 symbols (47
          non-guard members + guard 510300) / 2020-01-02..2026-09-29
          / 1,635 dates. G-ANCHOR battery (fail-closed, one-face-off
          = config mismatch VOID, not data corruption), per the
          prereg s2 frozen list: n_decidable 1,616 / first decidable
          2020-02-06 / vote occupancy v1 1,525 v2 1,599 v3 715 v4
          824 / crowd_ge3 860 / crowd_eq4 571 / recover_ge3 660 /
          vote_count_mean 2.8855 / quantile faces / guard_score_neg
          824 + threshold constants (author-verbatim zero
          calibration) + state face (asym flips 71 / sym flips 77 +
          first-flip dates + defensive/decidable days) + decidable
          contiguity mechanism check.
  engine  Score_i = annualized 20d OLS log-trend x R^2 (x252) per
          member; votes on 47 non-guard members (ETF-domain
          adaptation: industries-vs-guard-object separation mirror):
          V1 mean(Top3)>0.20 / V2 mean(Top3)-median>0.25 / V3
          share(score<0)>55% / V4 guard score<0; >=3/4 votes = crowd
          risk day (3/4 not 4/4 = author tolerance verbatim).
          ASYM (author-verbatim): crowd CONFIRM_OUT(2) consecutive
          days -> OFF (defense); recover CONFIRM_IN(3) consecutive
          days -> ON; recover face = hysteresis-carrying four-dim
          >=3/4 (guard score>0 / guard rank>40% / spread<0.25*0.75
          =0.1875 / weak share<55%). SYM (ablation): same vote face,
          recover 2 consecutive days, r3 = spread<0.25 no-hysteresis
          -- isolates the asymmetric-confirm + 75pct-hysteresis
          design contribution. INITIAL STATE = long at the first
          decidable day (frozen r260 convention; the first decidable
          day's triggers still apply that same day -- probe
          semantics, selftest pins the face). Signal decided at
          close t, effective t+1 (T+1 onset, W1-W7 house caliber):
          pos[t] = pos_end[t-1]; batch window lo = first_decidable+1
          (W5 law), four-cell shared window for cross-cell PBO/CSCV
          date alignment. Judged x1 net = freeze-probe cell_returns
          verbatim (parity-asserted against the local mult-face
          helper at run time); costs = COST_X1_RATE on |dpos| booked
          to the following day, window-start entry booked against
          the pre-window flat face; x2 = CostPatch(2.0) = 26.082bp/
          side stress disclosure column. Hold-period >=3 trading
          days constraint EXEMPT per prereg s3 (state-gate holds =
          signal continuous segments; defense segments at 0 =
          cash-leg legal state, disclosed).
  cells   4 cells = 2 signal variants x 2 cost faces (prereg s0:
          every cell pays into N_eff, W6/W7 isomorphic):
          CROWD-ASYM-X1 (judged face, author-verbatim), CROWD-
          ASYM-X2, CROWD-SYM-X1 (judged face, ablation), CROWD-
          SYM-X2. Traded instrument = 510300 single-asset exposure
          gate (W1-W7 same harness face; signal source = core48
          cross-section, information/instrument separation = the
          family's structural-distinction argument). n_entries berth
          reading ~36 asym exits vs F6 gate 30 = marginal honest
          carry per prereg s0; live run <30 = trade_gate honest
          refusal, not a mechanism fault.
  passive PASSIVE-510300-BH buy-and-hold over the same batch window,
          live-computed Sharpe fed to g1_prime_v2 passive_override
          (W5 door). Reference columns (prereg s4 line-reading face):
          SG.passive_baseline("core48") + shared-collector null
          coverage, live-read, disclosed only.
  nulls   K=2000 uniform random-day-placement nulls per VARIANT
          (prereg s0 compute budget + s4 seed k-allocation "nulls
          k<2000", W3/W4/W5/W7 semantics): each draw preserves the
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
          convention, disclosed); beat = cell window cum ret (own
          cost face) > passive window cum ret. 100 random split
          windows (k in [3000, 3100), law s3 >= 100): split point in
          [0.2n, 0.8n], half-window Sharpe same-sign rate >= 80% =
          segment-stable.
  gates   G1'v2 per cell via science_gates.g1_prime_v2 (batch_cells
          = 2004 = 4 judged cells + 2000 null draws, the s0 counting
          law; prereg s4's "batch_cells=4" is the judged-cell
          shorthand exactly as W5's "batch_cells=3" -> 2003 family
          reconciliation, disclosed here and in judgment_note),
          pool='core48', null_pool = batch-own per-cell null family
          (the s0/s4-seed k-allocation face: "nulls k<2000,
          semantics same W3/W4/W5/W7" governs over s4's W6-template
          "shared collector n=120" phrase -- three-signal weight:
          s0 budget + seed k-band + W5-skeleton-mirror pointer; the
          shared collector stays a live-read reference column),
          passive_override = this batch's 510300-BH window Sharpe;
          n_trades = n_entries = derived position-face episode count
          (F6 dual trade gate folded, prereg s4 lists both counts;
          NaN-safe nan-aware runner stats, r442 pit law); DSR via
          deflated_sharpe_ratio on the raw cell series; family PBO
          via screening.pbo cscv_pbo CSCV-8 over the 4-cell matrix;
          G2 via g2_registration_v2. No hand-copied lines (O-2250).
  d6      frozen at the r260 probe window verbatim (W6/W7 paradigm:
          the admission record = the freeze-window artifact, no
          re-computation): batch internal asym-vs-sym |corr| 0.9169
          (variant face, both cells burn); vs T33 four in-book
          rotation cells max 0.4561 (rs_rotation_20, sym) -- ALL <
          0.7 reject line, merge clause ZERO triggers; vs registered
          six max 0.1767 (COMPOSITE-CE-01) disclose-only;
          REGIME_GUARD = in-production non-cell (signal face
          adjudicated at berth pearson +0.7728 width-leg / +0.5965
          composite, no cells pair exists -- honest boundary, T0
          authority untouched).
  turnover budget 50 entries/year (prereg s3); breach = red honest
          row. Ledger append_ledger("CROWD_VOTE_P1", 2004,
          "results/innovation_quota/CROWD-VOTE-P1.json",
          evidence_cutoff="2026-09-29"); out["trials_ledger"] carries
          the return value (r434 pit law); gate_attrition measurement
          row to the EXECUTING machine's lane file (prereg s6, W6
          law: gate_attrition.<machine_id>.json, shared-file
          fallback).
Products (prereg s6): results/innovation_quota/CROWD-VOTE-P1.json
(top evidence_cutoff + cutoff_meta + panel/anchor faces + passive +
4 cells + per-cell nulls + virtual starts + splits + frozen d6 +
funnel + gates + ledger) + nulls shard npy checkpoints.

Usage: run | verify | selftest   (exit 0 ok; 2 = fail-closed gate
refusal, including the r450 landed-state guard: a judged product
(trials_ledger present, read from CONTENT not existence/timestamps)
refuses re-run rc=2 unless INNOVATION_QUOTA_W9_REFINALIZE=1; a
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
from _r259bmc_w9_crowding_probe import (
    load_core48, build_faces, GUARD, TH_TOP3, TH_SPREAD, TH_WEAK,
    TH_GUARD, CONFIRM_OUT, CONFIRM_IN, HYST, TH_RANK, W, ANNUAL)
from _r260bmc_w9_d6_cells_probe import crowd_positions, cell_returns

OUT_DIR = os.path.join(ROOT, "results", "innovation_quota")
NULL_DIR = os.path.join(OUT_DIR, "nulls_w9")
OUT_JSON = os.path.join(OUT_DIR, "CROWD-VOTE-P1.json")
OUT_DIR_RESULTS = os.path.dirname(OUT_DIR)      # results root for lib faces
MACHINE_JSON = os.path.join(ROOT, "fleet", "machine.json")
ATT_JSON_SHARED = os.path.join(ROOT, "results", "gate_attrition.json")
D6_FACTS_PATH = os.path.join(
    ROOT, "results", "_r260bmc_w9_d6_cells_probe_facts.json")

BATCH_NAME = "CROWD_VOTE_P1"
BATCH_CELLS = 2004                # 4 judged cells + 2000 null draws (s0 law)
EVIDENCE_CUTOFF = "2026-09-29"
SEED_KEY = "innovation_quota_w9_crowd"
PBP = SG.PERIODS_PER_YEAR         # 252 gate-chain single-source
K_NULLS = 2000
NULL_SHARDS = 8
K_STARTS = 1000
K_SPLITS = 100
WIN_DAYS = {"6m": 126, "12m": 252, "24m": 504}
D6_REJECT = 0.7
TURNOVER_BUDGET = 50              # prereg s3: 50 entries/year budget line
TARGET = GUARD                    # 510300 traded object
SEED = None                       # filled from SG.SEED_REGISTRY at run

# 4 cells = 2 variants x 2 cost faces (prereg s0); key = (variant, face)
VARIANTS = ["asym", "sym"]
CELL_FACES = [("asym", "x1"), ("asym", "x2"),
              ("sym", "x1"), ("sym", "x2")]
CELL_NAME = {("asym", "x1"): "CROWD-ASYM-X1",
             ("asym", "x2"): "CROWD-ASYM-X2",
             ("sym", "x1"): "CROWD-SYM-X1",
             ("sym", "x2"): "CROWD-SYM-X2"}
CELL_MULT = {"x1": 1.0, "x2": 2.0}

# ---- frozen probe faces (G-PANEL / G-ANCHOR; r259 berth + r260 freeze
# facts verbatim; extreme_day_sample stays pinned in the facts files,
# tie-order-fragile by design, not a runner anchor per prereg s2 list)
PANEL_ANCHOR = {"n_symbols": 48, "n_members_non_guard": 47,
                "guard": "510300", "first_date": "2020-01-02",
                "last_date": "2026-09-29", "n_dates": 1635}
VOTE_ANCHOR = {"n_decidable_days": 1616,
               "first_decidable_date": "2020-02-06",
               "vote_occupancy": {"v1_days": 1525, "v2_days": 1599,
                                  "v3_days": 715, "v4_days": 824},
               "crowd_days_ge3": 860, "crowd_days_eq4": 571,
               "recover_days_ge3": 660, "vote_count_mean": 2.8855,
               "weak_share_q10": 0.125, "weak_share_q90": 0.8279,
               "top3_mean_q10": 0.3191, "top3_mean_q90": 2.3734,
               "spread_q10": 0.5736, "spread_q90": 2.1252,
               "guard_score_neg_days": 824}
TH_ANCHOR = {"v1_top3_gt": 0.20, "v2_spread_gt": 0.25,
             "v3_weak_share_gt": 0.55, "v4_guard_score_lt": 0.0,
             "confirm_out_days": 2, "confirm_in_days": 3,
             "hysteresis_pct": 0.75, "recovery_diff_lt": 0.1875,
             "recovery_rank_gt": 0.40}
STATE_ANCHOR = {
    "asym": {"n_flips": 71,
             "first_flip_dates": ["2020-02-07", "2020-02-28",
                                  "2020-03-17", "2020-04-14",
                                  "2020-05-28", "2020-06-10"],
             "defensive_days": 980, "decidable_days": 1616},
    "sym": {"n_flips": 77,
            "first_flip_dates": ["2020-02-07", "2020-02-27",
                                 "2020-03-17", "2020-04-13",
                                 "2020-05-28", "2020-06-09"],
            "defensive_days": 930, "decidable_days": 1616}}

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
    (window indices, half-open spans) + entry count (0->1 edges; the
    window-start long face counts as one deployment entry = the
    pre-window flat booking face, consistent with cost law)."""
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
    """O-1524 KPI dual disclosure (W5/W7 mirror). Trade-level faces (the
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
    """core48 close panel, truncated to the frozen evidence cutoff
    (P-5C binding; new bars beyond 2026-09-29 must not move anchors)."""
    if _DAILY_OVERRIDE is not None:
        # hermetic selftest path still exercises the real loader chain
        import _r259bmc_w9_crowding_probe as _p259
        saved = _p259.DAILY
        _p259.DAILY = _DAILY_OVERRIDE
        try:
            panel, syms = load_core48()
        finally:
            _p259.DAILY = saved
    else:
        panel, syms = load_core48()
    cut = pd.Timestamp(EVIDENCE_CUTOFF)
    panel = panel[panel.index <= cut]
    return panel, syms


def derive_faces(closes):
    """G-PANEL + G-ANCHOR derivation (vote occupancy + threshold
    constants + state machine + contiguity mechanism check). All
    comparisons rounded exactly like the frozen probe facts (4dp)."""
    faces, votes, rec_votes, decidable = build_faces(closes)
    dec_days = faces[decidable]
    n_dec = int(len(dec_days))
    derived_votes = {
        "n_decidable_days": n_dec,
        "first_decidable_date": str(dec_days.index[0].date()) if n_dec
        else None,
        "vote_occupancy": {
            "v1_days": int(votes["v1"].sum()),
            "v2_days": int(votes["v2"].sum()),
            "v3_days": int(votes["v3"].sum()),
            "v4_days": int(votes["v4"].sum()),
        },
        "crowd_days_ge3": int(dec_days["crowd"].sum()),
        "crowd_days_eq4": int((dec_days["vote_count"] == 4).sum()),
        "recover_days_ge3": int(dec_days["recover"].sum()),
        "vote_count_mean": round(float(dec_days["vote_count"].mean()), 4)
        if n_dec else None,
        "weak_share_q10": round(
            float(dec_days["weak_share"].quantile(0.10)), 4) if n_dec
        else None,
        "weak_share_q90": round(
            float(dec_days["weak_share"].quantile(0.90)), 4) if n_dec
        else None,
        "top3_mean_q10": round(
            float(dec_days["top3"].quantile(0.10)), 4) if n_dec
        else None,
        "top3_mean_q90": round(
            float(dec_days["top3"].quantile(0.90)), 4) if n_dec
        else None,
        "spread_q10": round(
            float(dec_days["spread"].quantile(0.10)), 4) if n_dec
        else None,
        "spread_q90": round(
            float(dec_days["spread"].quantile(0.90)), 4) if n_dec
        else None,
        "guard_score_neg_days": int((dec_days["guard_score"] < 0).sum()),
    }
    pos = {}
    state_face = {}
    for v in VARIANTS:
        p, nf, ff = crowd_positions(faces, rec_votes, decidable, v)
        pos[v] = p
        state_face[v] = {"n_flips": nf, "first_flip_dates": ff,
                         "defensive_days": int((p == 0.0).sum()),
                         "decidable_days": int(p.notna().sum())}
    th_face = {
        "v1_top3_gt": TH_TOP3, "v2_spread_gt": TH_SPREAD,
        "v3_weak_share_gt": TH_WEAK, "v4_guard_score_lt": TH_GUARD,
        "confirm_out_days": CONFIRM_OUT, "confirm_in_days": CONFIRM_IN,
        "hysteresis_pct": HYST,
        "recovery_diff_lt": round(TH_SPREAD * HYST, 4),
        "recovery_rank_gt": TH_RANK,
    }
    panel_face = {"n_symbols": int(closes.shape[1]),
                  "n_members_non_guard": int(closes.shape[1] - 1),
                  "guard": GUARD,
                  "first_date": str(closes.index[0].date()),
                  "last_date": str(closes.index[-1].date()),
                  "n_dates": int(len(closes.index))}
    # ---- decidable contiguity (mechanism hazard guard: a NaN pos_end
    # inside [first_dec, n) would silently propagate through the
    # window face; the frozen probe formula assumes contiguity)
    if n_dec:
        first_dec = closes.index.get_loc(dec_days.index[0])
        contiguous = bool(decidable.iloc[first_dec:].all())
    else:
        contiguous = False
    lo = first_dec + 1 if n_dec else None
    return {"faces": faces, "votes": votes, "rec_votes": rec_votes,
            "decidable": decidable, "pos": pos, "lo": lo,
            "panel": panel_face, "vote_face": derived_votes,
            "threshold_face": th_face, "state_face": state_face,
            "decidable_contiguous": contiguous}


def anchor_drift(P):
    """Fail-closed reconcile: derived faces vs the frozen probe
    constants (one-face-off = config mismatch VOID, not data
    corruption). Returns list of drift strings (empty = bit-exact)."""
    bad = []

    def _cmp(family, got, exp):
        for k, v in exp.items():
            g = got.get(k)
            if g != v:
                bad.append(f"{family}.{k}: {g!r} != frozen {v!r}")

    _cmp("panel", P["panel"], PANEL_ANCHOR)
    _cmp("g_anchor", P["vote_face"], VOTE_ANCHOR)
    _cmp("thresholds", P["threshold_face"], TH_ANCHOR)
    for v in VARIANTS:
        _cmp(f"state.{v}", P["state_face"][v], STATE_ANCHOR[v])
    if not P["decidable_contiguous"]:
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
    """One uniform random-day-placement draw (prereg s0, W4/W5/W7 null
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
    """Verbatim copy of the freeze-window D6 record (W6/W7 paradigm:
    the admission record = the freeze-window artifact, no
    re-computation)."""
    path = _D6_FACTS_OVERRIDE or D6_FACTS_PATH
    with open(path, encoding="utf-8") as fh:
        facts = json.load(fh)
    d6 = dict(facts["d6_cells_face"])
    d6["freeze_artifact"] = ("results/_r260bmc_w9_d6_cells_probe_facts.json "
                             "(frozen r260 bm-c, no re-computation, W6 "
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
                                        "CROWD-VOTE-P1.json",
                              evidence_cutoff=EVIDENCE_CUTOFF,
                              prev_total=prev_total)
    product["gates"] = gates
    product["family_pbo"] = pbo
    product["passive_override_fed"] = passive_override
    # prereg s4 live-read reference columns (judgment-line reading
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
                    "at burn window (live-calculation law, no "
                    "hand-copying)'",
        }
    except Exception as ex:
        product["line_reading_reference"] = {"error": str(ex)}
    n_pass = sum(1 for g in gates.values()
                 if g["g1_prime_v2"]["pass_v2"])
    n_g2 = sum(1 for g in gates.values() if g["g2"]["eligible_v2"])
    product["funnel"] = {
        "harvest_column": 1,
        "harvest_note": "zoo #84 crowding_vote four-vote composite "
                        "family (A-layer last unburned quota family, "
                        "r258 eligibility scan verdict PRIMARY; berth "
                        "r259 -> freeze r260 bm-c; five negative-prior "
                        "burden preregistered, judged-negative = "
                        "predicted mainline)",
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
        "k-allocation 'nulls k<2000, W3/W4/W5/W7 semantics' (s4's "
        "'shared collector n=120' phrase = W6-template carryover, "
        "reconciled at build time zero-run, disclosed; the shared "
        "collector stays a live-read reference column); passive_"
        "override = 510300-BH batch-window live Sharpe (W1-W7 harness "
        "face); n_trades = n_entries = position-face episode count (F6 "
        "dual trade gate folded; berth reading ~36 asym exits vs "
        "min 30 = marginal honest carry per prereg s0, live <30 = "
        "trade_gate honest refusal not a mechanism fault); judged-"
        "negative family = slot closed + new-evidence reopen note "
        "(law s5); G2-eligible cell = T-34 fastline candidate pool "
        "registration face, intake walks the CE admission harness "
        "separately; T0 brake authority stays with REGIME_GUARD "
        "(in-production non-cell, berth signal face +0.7728 width-leg "
        "disclosed, zero touch)")
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
    passive_ser, passive_stats, pos_cache)."""
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
    print(f"panel ok: {P['panel']['n_dates']} dates x "
          f"{P['panel']['n_symbols']} syms, lo={lo} "
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
        "prereg": "research/INNOVATION_QUOTA_W9_PREREG.md (r259 bm-c "
                  "berth + r260 bm-c freeze, seed 20326000)",
        "prereg_sha256_16": _sha256_file(os.path.join(
            ROOT, "research", "INNOVATION_QUOTA_W9_PREREG.md"))[:16],
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "seed": {"base": SEED, "k_nulls": K_NULLS,
                 "k_substreams": "nulls k<2000; starts k in "
                                 "[2000,3000); splits k in [3000,3100) "
                                 "-- rng([SEED, k]) one k-stream shared "
                                 "across variants/cost faces (W5 law)"},
        "panel": P["panel"],
        "anchor_faces": {"g_anchor": P["vote_face"],
                         "thresholds": P["threshold_face"],
                         "state": {v: P["state_face"][v]
                                   for v in VARIANTS}},
        "state_face": {f"{v}_defensive_days":
                       P["state_face"][v]["defensive_days"]
                       for v in VARIANTS},
        "construction": "verbatim-import results/_r259bmc_w9_crowding_"
                        "probe.py (load_core48 + build_faces + author-"
                        "verbatim threshold constants) + results/"
                        "_r260bmc_w9_d6_cells_probe.py (crowd_positions "
                        "+ cell_returns) -- r456 single-source "
                        "paradigm, parity-asserted every run",
        "engine_law": "Score_i = annualized 20d OLS log-trend x R^2 "
                      "(x252); votes on 47 non-guard members: V1 "
                      "mean(Top3)>0.20 / V2 mean(Top3)-median>0.25 / V3 "
                      "weak share>55% / V4 guard score<0; >=3/4 votes "
                      "= crowd day (3/4 author tolerance verbatim, zero "
                      "calibration); ASYM: crowd 2 consecutive days -> "
                      "OFF, recover 3 consecutive days -> ON, recover "
                      "face = four-dim >=3/4 with 75pct hysteresis "
                      "(r3 spread<0.1875); SYM ablation: same votes, "
                      "recover 2 consecutive days, r3 spread<0.25 "
                      "no-hysteresis; INITIAL = long at first decidable "
                      "day (frozen r260, first-day triggers apply); "
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
                                 "pre-lo days = score warmup, "
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
          f"(panel {P['panel']['first_date']}.."
          f"{P['panel']['last_date']}, "
          f"{P['panel']['n_dates']} dates x "
          f"{P['panel']['n_symbols']} syms; decidable "
          f"{P['vote_face']['n_decidable_days']}; votes "
          f"{P['vote_face']['vote_occupancy']['v1_days']}/"
          f"{P['vote_face']['vote_occupancy']['v2_days']}/"
          f"{P['vote_face']['vote_occupancy']['v3_days']}/"
          f"{P['vote_face']['vote_occupancy']['v4_days']}; crowd_ge3 "
          f"{P['vote_face']['crowd_days_ge3']}; asym/sym flips "
          f"{P['state_face']['asym']['n_flips']}/"
          f"{P['state_face']['sym']['n_flips']})")
    return 0


# ------------------------------------------------------------------ selftest
def _mk_core48_fixture(tmp):
    """Synthetic core48-like panel: 48 members x ~1200 bdays with
    planted crowding regimes -- in crowd windows 3 leader members
    rally hard while the other 44 non-guard members bleed and the
    guard declines softly (all four votes fire: V1 top3 mean, V2
    leader-vs-median spread, V3 weak share, V4 guard score); in
    recovery windows a broad uniform rally with the guard slightly
    ahead (r1/r2/r3/r4 recovery votes fire, spread narrows below the
    hysteresis band). Two full crowd->recover cycles exercise both
    variants' state machines (asym 2d-out/3d-in vs sym 2d-out/2d-in
    flip counts differ)."""
    rng = np.random.default_rng(11)
    n = 1200
    dates = pd.bdate_range("2020-01-02", periods=n)
    codes = ["510300"] + [f"{510400 + i}" for i in range(47)]
    leaders = codes[1:4]                  # 3 hard-rally leaders
    crowd_segs = [(100, 140), (500, 540)]
    recover_segs = [(160, 200), (560, 600)]
    frames = {}
    for j, code in enumerate(codes):
        r = rng.normal(0.0, 0.004, n)
        for (a, b) in crowd_segs:
            if code == "510300":
                r[a:b] -= 0.003          # guard soft decline (V4)
            elif code in leaders:
                r[a:b] += 0.010           # leaders hard rally (V1/V2)
            else:
                r[a:b] -= 0.004           # members bleed (V3)
        for (a, b) in recover_segs:
            if code == "510300":
                r[a:b] += 0.008          # guard slightly ahead (r2)
            else:
                r[a:b] += 0.006           # broad uniform rally (r1/r3/r4)
        s = pd.Series(1.0 + np.cumsum(r), index=dates)
        s = s.clip(lower=0.05)
        df = pd.DataFrame({
            "date": dates.strftime("%Y-%m-%d"),
            "open": s, "high": s * 1.01, "low": s * 0.99,
            "close": s, "volume": 1e6, "amount": s * 1e6,
        })
        df.to_csv(os.path.join(tmp, f"{code}.csv"), index=False)
    return codes


def cmd_selftest():
    global OUT_DIR, NULL_DIR, OUT_JSON, OUT_DIR_RESULTS, ATT_JSON_SHARED, \
        SEED, K_NULLS, NULL_SHARDS, K_STARTS, K_SPLITS, PANEL_ANCHOR, \
        VOTE_ANCHOR, TH_ANCHOR, STATE_ANCHOR, _DAILY_OVERRIDE, \
        _D6_FACTS_OVERRIDE, _ATT_OVERRIDE, EVIDENCE_CUTOFF
    tmp = tempfile.mkdtemp(prefix="innovation_quota_w9_selftest_")
    K_NULLS, NULL_SHARDS = 40, 2     # >= 30: skill_line_v2 thin-pool floor
    K_STARTS, K_SPLITS = 12, 6
    SEED = 20326000
    # tmp-path reassignment FIRST: every face (nulls included) must
    # stay hermetic -- a late reassignment poisons the real nulls_w9
    # dir with selftest-sized shards (W3 resume-broadcast lineage)
    OUT_DIR = os.path.join(tmp, "results", "innovation_quota")
    NULL_DIR = os.path.join(OUT_DIR, "nulls_w9")
    OUT_JSON = os.path.join(OUT_DIR, "CROWD-VOTE-P1.json")
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
        "batch_internal_asym_vs_sym": 0.9,
        "vs_t33_cells": {"stub_cell": {"asym": 0.1, "sym": 0.2}},
        "merge_clause_applied": [],
        "vs_registered_six": {"max_abs_corr": 0.2,
                               "argmax": "STUB-CE-01"}}},
        open(d6_tmp, "w"))
    _D6_FACTS_OVERRIDE = d6_tmp
    ok = []
    try:
        # ---- state-machine hand-checks (frozen probe semantics):
        # crowd CONFIRM_OUT(2) -> OFF; asym recover CONFIRM_IN(3) vs
        # sym CONFIRM_OUT(2) symmetric; initial = long at first
        # decidable day; first-day triggers apply the same day
        idx = pd.bdate_range("2022-01-03", periods=10)
        faces_h = pd.DataFrame({
            "crowd": [False, True, True, False, False, False, False,
                      False, False, False],
            "recover": [False, False, False, False, True, True, True,
                        False, False, False],
            "spread": [0.1] * 10}, index=idx)
        rec_h = pd.DataFrame({"r1": [False] * 4 + [True] * 3 + [False] * 3,
                              "r2": [False] * 4 + [True] * 3 + [False] * 3,
                              "r4": [False] * 10}, index=idx)
        dec_h = pd.Series(True, index=idx)
        pa, nfa, _ = crowd_positions(faces_h, rec_h, dec_h, "asym")
        ok.append(("asym gate: 2d-out / 3d-in zones",
                   list(pa.to_numpy()) ==
                   [1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0]
                   and nfa == 2))
        ps, nfs, _ = crowd_positions(faces_h, rec_h, dec_h, "sym")
        ok.append(("sym gate: 2d-out / 2d-in symmetric ablation",
                   list(ps.to_numpy()) ==
                   [1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0]
                   and nfs == 2))
        # first-day trigger still applies (probe semantics): crowd on
        # days 0-1 -> OFF already at day 1
        faces_2d = pd.DataFrame({
            "crowd": [True, True, False, False, False, False, False,
                      False, False, False],
            "recover": [False] * 10, "spread": [0.1] * 10}, index=idx)
        rec_2d = pd.DataFrame({"r1": [False] * 10, "r2": [False] * 10,
                               "r4": [False] * 10}, index=idx)
        p2, nf2, _ = crowd_positions(faces_2d, rec_2d, dec_h, "asym")
        ok.append(("first-decidable trigger applies same day",
                   list(p2.to_numpy()) ==
                   [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                   and nf2 == 1))

        # ---- T+1 onset + cost booking via cell_faces
        idx4 = pd.bdate_range("2020-01-02", periods=10)
        pe = pd.Series([np.nan, np.nan, 1.0, 1.0, 0.0, 0.0, 1.0,
                        np.nan, np.nan, np.nan], index=idx4)
        tgt_vals = np.array([0.01, 0.02, 0.03, -0.04, 0.05, 0.06,
                             0.0, 0.0, 0.0, 0.0])
        tgt = pd.Series(tgt_vals, index=idx4)
        pos, gross, flips, net = cell_faces(pe, tgt, 1.0)
        # window lo = first_valid(2)+1 = 3; pos[3]=pe[2]=1, pos[4]=pe[3]
        # =1, pos[5]=pe[4]=0, pos[6]=pe[5]=0, pos[7]=pe[6]=1
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

        # ---- fixture derive-then-freeze (W5/W7 pattern): anchors are
        # derived from the CSV-READ frame via the REAL probe loader
        closes, syms = load_closes()
        ok.append(("fixture loads via real probe loader",
                   closes.shape[1] == 48 and "510300" in closes.columns))
        cut = str(closes.index[-1].date())
        EVIDENCE_CUTOFF = cut
        P = derive_faces(closes)
        ok.append(("fixture exercises both variants' state machines",
                   P["state_face"]["asym"]["n_flips"] >= 2
                   and P["state_face"]["sym"]["n_flips"] >= 2
                   and P["vote_face"]["crowd_days_ge3"] > 0
                   and P["vote_face"]["recover_days_ge3"] > 0))
        ok.append(("fixture crowd votes all four fire",
                   P["vote_face"]["vote_occupancy"]["v1_days"] > 0
                   and P["vote_face"]["vote_occupancy"]["v2_days"] > 0
                   and P["vote_face"]["vote_occupancy"]["v3_days"] > 0
                   and P["vote_face"]["vote_occupancy"]["v4_days"] > 0))
        PANEL_ANCHOR = dict(P["panel"])
        VOTE_ANCHOR = dict(P["vote_face"])
        TH_ANCHOR = dict(P["threshold_face"])
        STATE_ANCHOR = {v: dict(P["state_face"][v]) for v in VARIANTS}
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
                   cells[("asym", "x2")]["stats"]["sharpe_full"] <=
                   cells[("asym", "x1")]["stats"]["sharpe_full"] + 1e-9
                   and cells[("sym", "x2")]["stats"]["sharpe_full"] <=
                   cells[("sym", "x1")]["stats"]["sharpe_full"] + 1e-9))
        n1 = run_nulls("asym", pos_cache["asym"]["held"],
                       closes[TARGET].astype(float).pct_change()
                       .to_numpy(dtype=float), P["lo"])
        n2 = run_nulls("asym", pos_cache["asym"]["held"],
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
            "panel": P["panel"],
            "anchor_faces": {"g_anchor": P["vote_face"],
                             "thresholds": P["threshold_face"],
                             "state": {v: P["state_face"][v]
                                       for v in VARIANTS}},
            "state_face": {f"{v}_defensive_days":
                           P["state_face"][v]["defensive_days"]
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
        real_v1 = VOTE_ANCHOR["vote_occupancy"]["v1_days"]
        VOTE_ANCHOR = dict(VOTE_ANCHOR)
        VOTE_ANCHOR["vote_occupancy"] = dict(VOTE_ANCHOR["vote_occupancy"],
                                             v1_days=real_v1 + 1)
        ok.append(("g-anchor vote-face drift refusal",
                   anchor_drift(P2) != []))
        VOTE_ANCHOR["vote_occupancy"] = dict(
            VOTE_ANCHOR["vote_occupancy"], v1_days=real_v1)
        real_fl = STATE_ANCHOR["asym"]["n_flips"]
        STATE_ANCHOR["asym"] = dict(STATE_ANCHOR["asym"],
                                    n_flips=real_fl + 1)
        ok.append(("state-face drift refusal", anchor_drift(P2) != []))
        STATE_ANCHOR["asym"] = dict(STATE_ANCHOR["asym"],
                                    n_flips=real_fl)
        real_h = TH_ANCHOR["confirm_out_days"]
        TH_ANCHOR = dict(TH_ANCHOR, confirm_out_days=real_h + 1)
        ok.append(("threshold-constant drift refusal",
                   anchor_drift(P2) != []))
        TH_ANCHOR = dict(TH_ANCHOR, confirm_out_days=real_h)
        ok.append(("anchor restored -> gates pass again",
                   anchor_drift(P2) == []))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n_ok = sum(1 for _, v in ok if v)
    print(f"innovation_quota_w9 selftest: {n_ok}/{len(ok)} PASS")
    for name, v in ok:
        if not v:
            print(f"  FAIL: {name}")
    return 0 if n_ok == len(ok) else 1


# ------------------------------------------------------------------ guard
def _refuse_if_judged():
    """r450 landed-state guard: read CONTENT (trials_ledger block), not
    existence/timestamps. Judged product refuses re-run (rc=2) unless
    INNOVATION_QUOTA_W9_REFINALIZE=1; phase-1-only product resumes."""
    if not os.path.exists(OUT_JSON):
        return 0
    try:
        with open(OUT_JSON, encoding="utf-8") as fh:
            old = json.load(fh)
    except Exception:
        return 0        # unreadable partial write -> resume path
    if (old.get("trials_ledger") or {}).get("total") is not None and \
            os.environ.get("INNOVATION_QUOTA_W9_REFINALIZE") != "1":
        print("GATE-REFUSE(exit2): CROWD-VOTE-P1.json already "
              "judged (trials_ledger present, content-read per r450); "
              "INNOVATION_QUOTA_W9_REFINALIZE=1 = only redo")
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
