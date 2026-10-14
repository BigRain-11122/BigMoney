"""TRIAL_LABOR_W19 runner -- wave-19 timing-axis complete-block PAIRED
isolation burn machinery (frozen prereg research/TRIAL_LABOR_W19_PREREG.md,
bm-b r927 freeze commit 6c09b1251 lineage; this build window = r928,
funnel 4/5).

Design (prereg sec.3, FROZEN): 173 W16 frozen candidate cells (entry
source results/trial_labor_w16/w16_candidates.json, sha256_16
22179881b7537193, n=173, A=6/B=167) x 2 timing faces (tl1.AXIS_TIMING
verbatim) = 346 paired cells + K=200 timing-mixed nulls = 546 screen
trials.  ZERO new entry generation (W19 gen seed 20640000 held, zero
consumption); the TIMING face is the ONLY variable (complete-block
paired design -- same entry mask shared by both arms per block = the
paired-control design body; T-84s3 fingerprint dedup is FORBIDDEN
across timing arms per prereg sec.3, it would collapse the pairing
to 173).

X-axis consumption (prereg sec.0 banner, W17 sec.0 consumer (3)
machine-consumed): X=template_default -- every W19 arm runs the
engine default exit stack as the tested baseline (A-family -> registered
exit face via tl1.candidate_engine_params; B-family -> engine default
P1-P6 full stack).  Basis: W17-JUDGE 344 cells all-negative + 7 exit
faces paired median delta all 0.0 (wilcoxon_p 0.966-1.0) = exit-axis
demotion canonical basis.

S-axis consumption (prereg sec.0 banner, W18 sec.0 consumer (2)
machine-consumed): S=as-burned cell native (axis[2] frozen W16
sampled constant, untouched) -- W18-JUDGE 188 cells lawful-zero + 4
sizing faces paired median delta all ~0 = S-axis non-discriminating
face; keeping the paired face native = the third link of the
three-wave determinism cross-door chain (W17 control == W18 as-burned
== W19 as-burned, 173 pairs dual-source).

Timing faces (prereg sec.3 table, tl1.AXIS_TIMING + tl1.apply_timing
L596-604 verbatim, ZERO new timing code; iron law: engine/exit_rules.py
priority + T+1/cost model untouched):
  daily_signal  mask native verbatim (zero gating; baseline)
  weekly_grid   mask AND ISO-week-first-trading-day gate (new entries
                only on the first trading day of each ISO week,
                isoweek!=shift(1) OR isoyear!=shift(1))
  control arm   = per-cell as-burned axis[3] frozen face (the W16
                  sampled constant, census daily_signal 128 /
                  weekly_grid 45); treatment = the other face.
  face          = mechanism whole bundle (W1-W16 sampling caliber).

Lineage (import-face reuse law): W19 re-derives ZERO entry/overlay/
curve/null/judge machinery -- tl16 imports tl1..tl14 verbatim, W17
imports tl16, W18 imports tl17, W19 imports tl18 (and through it
tl1/tl2/tl16/tl17/science_gates); the ONLY new faces are the
timing-face layer (axis[3] single-variable override -> apply_timing
verbatim path), the 18-source exclusion book, the paired-delta
informative-pairs + 2-as-burned-T-subgroup readout (prereg sec.4,
batch-unique w19_paired_deltas.json), the 173-pair as-burned
determinism cross-gate DUAL-SOURCE (three-column byte-identity vs
w17_screen_cells.csv control rows AND w18_screen_cells.csv as-burned
rows, prereg sec.2/sec.5.1) and the G-face assertion battery (timing
2-tuple identity + ExitConfig default table = A9 + entry source sha +
grammar lineage w14/w16/w17 three-face identity = A4).

Three-command closeout law (r446bmb/r467bma surgical pit law, prereg
sec.9): screen-prep / screen-finalize / judge-prep real-data
identity-face first-runs BEFORE the runner is declared landed.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import os
import sys
import time

import numpy as np
import pandas as pd

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
# GBK console swallow chain entry law (r236): reconfigure BEFORE any
# child-output print; idempotent, never rely on survivorship bias.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import trial_labor_w1 as tl1   # import-face reuse law (prereg sec.6)
import science_gates           # M1 t-face: t_from_sharpe + m1_t_value_gate
import trial_labor_w2 as tl2   # survival math + dual-nulls + D6 core
import trial_labor_w16 as tl16  # W16 runner: overlay states, exclusion
                                # book loader, curve-caliber lineage
import trial_labor_w17 as tl17  # W17 runner: exit-axis paired-block
                                # lineage + shared low-level helpers
import trial_labor_w18 as tl18  # W18 runner: sizing-axis paired-block
                                # lineage (three-wave chain source 2)
from science_gates import (CostPatch, SEED_REGISTRY,  # noqa: E402
                           REFORM_DIM_WEIGHTS, REFORM_SUB_WEIGHTS,
                           REFORM_TOPN_PER_WAVE, REFORM_Q_LEVEL,
                           reform_weight_freeze_integrity,
                           g2_reform_fdr4d)

# ------------------------------------------------------------- frozen (prereg)
WAVE = "TRIAL_LABOR_W19"
PREREG = "research/TRIAL_LABOR_W19_PREREG.md"
CUTOFF = tl1.CUTOFF                      # "2026-09-22" (P-5C binding, sec.2)
SEED_GEN = SEED_REGISTRY["trial_labor_w19_gen"]         # 20640000 (held)
SEED_NULL = SEED_REGISTRY["trial_labor_w19_scrnull"]    # 20640500
SEED_UNC = SEED_REGISTRY["trial_labor_w19_unc"]        # 20641000
K_NULLS = 200          # screen null family size (sec.3; frozen)
JUDGE_CAP_BLOCKS = 90  # sec.0 frozen deterministic block cap
RES_DIR = os.path.join(tl1.PATHS.results_dir, "trial_labor_w19")
GRAMMAR_FILE = os.path.join(RES_DIR, "w19_grammar.json")
CELLS_FILE = os.path.join(RES_DIR, "w19_cells.json")
ENTRY_FILE = os.path.join(tl1.PATHS.results_dir, "trial_labor_w16",
                         "w16_candidates.json")
ENTRY_SHA16 = "22179881b7537193"          # sec.2 entry-source anchor (A3)
SCREEN_FILE = os.path.join(RES_DIR, "w19_screen.json")
SCREEN_CSV = os.path.join(RES_DIR, "w19_screen_cells.csv")
JUDGE_FILE = os.path.join(RES_DIR, "w19_judge.json")
REFORM_FILE = os.path.join(RES_DIR, "w19_reform_face.json")
PAIRED_FILE = os.path.join(RES_DIR, "w19_paired_deltas.json")
INTAKE_FILE = os.path.join(RES_DIR, "w19_intake.json")
PREP_FILE = os.path.join(RES_DIR, "prep_state.json")
JUDGE_STATE_FILE = os.path.join(RES_DIR, "judge_state.json")
W17_SCREEN_CSV = os.path.join(tl1.PATHS.results_dir, "trial_labor_w17",
                              "w17_screen_cells.csv")
W17_SCREEN_FILE = os.path.join(tl1.PATHS.results_dir, "trial_labor_w17",
                               "w17_screen.json")
W17_CELLS_FILE = os.path.join(tl1.PATHS.results_dir, "trial_labor_w17",
                              "w17_cells.json")
W17_GRAMMAR_FILE = os.path.join(tl1.PATHS.results_dir, "trial_labor_w17",
                                "w17_grammar.json")
W18_SCREEN_CSV = os.path.join(tl1.PATHS.results_dir, "trial_labor_w18",
                              "w18_screen_cells.csv")
W18_SCREEN_FILE = os.path.join(tl1.PATHS.results_dir, "trial_labor_w18",
                               "w18_screen.json")
W18_CELLS_FILE = os.path.join(tl1.PATHS.results_dir, "trial_labor_w18",
                              "w18_cells.json")
W18_GRAMMAR_FILE = os.path.join(tl1.PATHS.results_dir, "trial_labor_w18",
                                "w18_grammar.json")
W16_GRAMMAR_FILE = os.path.join(tl1.PATHS.results_dir, "trial_labor_w16",
                                "w16_grammar.json")
W14_GRAMMAR_FILE = os.path.join(tl1.PATHS.results_dir, "trial_labor_w14",
                                "w14_grammar.json")
CKPT_DIR = os.path.join(RES_DIR, "checkpoint")
SCREEN_BATCH = "TRIAL_LAB_W19_SCREEN"   # prereg sec.0 ledger literal
JUDGE_BATCH = "TRIAL_LAB_W19_JUDGE"     # prereg sec.0 ledger literal
W6M = tl1.WINDOWS["6m"]                # leg-L 6m screen window (126 td)
FROZEN_SHA16 = "e15a4a7b3a3b2b36"  # Slice-B pin (== w19_grammar.json
# sha16; pinned at first build per W17 r789 / W16 r722 / W18 r880
# Slice-B precedent; selftest fail-closed verifies the pin == built
# sha once set)

# grammar lineage anchors (prereg sec.2 A4 / freeze facts; W18-runner
# verified lineage carried verbatim: w14 + w16 + w17 internal shas ==
# TRIAL_GRAMMAR_LEDGER rows)
W14_GRAMMAR_SHA16 = "a231bf10940e7878"   # w14_grammar internal sha ==
                                          # TRIAL_GRAMMAR_LEDGER W14 row
W16_GRAMMAR_SHA16 = "ebf15822d2c8472e"   # W16 runner Slice-B pin ==
                                          # ledger W16 row
W17_GRAMMAR_SHA16 = "09476ecc5beb2304"   # W17 runner Slice-B pin ==
                                          # ledger W17 row
W18_GRAMMAR_SHA16 = "724b6135a5fdb6ae"   # W18 runner Slice-B pin ==
                                          # ledger W18 row (frozen fact,
                                          # three-wave chain source 2)

# X-axis consumption face (prereg sec.0 banner: X=template_default per
# W17 sec.0 consumer (3); engine default exit stack = tested baseline)
X_CONSUMED = "template_default"

# sec.3 timing face set -- FROZEN verbatim = tl1.AXIS_TIMING import-face
# (ZERO reorder, ZERO new timing code; freeze facts timing_faces leg).
# G-TIMING gate asserts this tuple == the frozen pair at every
# prep/finalize (drift = face-mismatch fail-closed).
W19_FACE_ORDER = tuple(tl1.AXIS_TIMING)   # ("daily_signal","weekly_grid")
W19_FROZEN_TIMING = ("daily_signal", "weekly_grid")
W19_FACE_RULES = {
    "daily_signal": "mask native verbatim (zero gating; baseline)",
    "weekly_grid": "mask AND ISO-week-first-trading-day gate "
                   "(isoweek!=shift(1) OR isoyear!=shift(1), "
                   "tl1.apply_timing L596-604 verbatim)",
}

# ExitConfig engine default table (prereg sec.2 A9 face, engine/exit_rules.py
# verbatim; X=template_default consumed -> the default stack is the tested
# baseline, so the A9 drift gate stays load-bearing) -- inherited from the
# W17 runner verbatim (tl17.EXITCFG_DEFAULTS); the runner asserts
# field-by-field equality at every screen-prep/finalize (engine drift
# fail-closed gate).
EXITCFG_DEFAULTS = tl17.EXITCFG_DEFAULTS

# sec.5 frozen prediction faces (recorded for honest post-run accounting;
# sec.5.1 count is a PREDICTION -- the hard determinism gate is the
# 173-pair three-column byte-identity per sec.2/sec.3, prereg sec.9
# build-window reading, disclosed in sec.9 build note)
PRED_AS_BURNED_SURVIVORS = 43
NULL_P95_BAND = (0.50, 0.53)   # sec.4/sec.5.3 reference band
# registered roster for the D6 reform sub-item (paper six: O-1555 five
# + 511010 cash leg; engine-face daily-return caliber, reeval18 canon)
REGISTERED_D6_SYMBOLS = ("510300", "510050", "510500", "512100",
                        "588000", "511010")
# paired-delta Wilcoxon rng streams -- unc family band, indices above the
# judge-cell consumption range (<2*90=180) and below the declared band
# top 346 (prereg sec.3 unc band rng([20641000,cell_idx]) cell_idx<346)
PAIRED_RNG_BASE = 200

_grammar_sha16 = tl16._grammar_sha16
_j = tl1._j


def _dump(path, payload):
    tl17._dump(path, payload)


def _timing_identity_gate():
    """G-TIMING (prereg sec.2 timing-face anchor): tl1.AXIS_TIMING ==
    the frozen two-tuple, verbatim import, zero reorder."""
    live = tuple(tl1.AXIS_TIMING)
    return live == W19_FROZEN_TIMING, live


# ------------------------------------------------------------ timing face layer
def w19_arm_cand(cand, face):
    """Per-arm candidate (prereg sec.3): the W16 frozen cell with
    axis[1] consumed to template_default (X consumption, W17 sec.0
    consumer (3)) and axis[3] set to the timing face -- the SINGLE
    variable; axis[2] (sizing) stays the as-burned cell native
    (S consumption, W18 sec.0 consumer (2)).  Everything downstream
    (apply_timing + candidate_engine_params + sizing_pieces) is the
    tl1 verbatim import path: ZERO new timing code.  For face == the
    cell's as-burned axis[3] the returned dict is byte-path identical
    to the W17 control-arm AND W18 as-burned-arm constructions (the
    173-pair dual-source determinism cross-gate premise)."""
    c2 = dict(cand)
    ax = list(cand["axis"])
    ax[1] = X_CONSUMED
    ax[3] = face
    c2["axis"] = ax
    return c2


def w19_engine_params(cand, template, face):
    """Full engine params + ExitPatch overrides for one W19 cell at the
    given timing face (prereg sec.3 table, tl1.candidate_engine_params
    verbatim routing): A-family -> registered face/ovr; B-family ->
    engine defaults {}, None.  The as-burned sizing rides the arm cand
    through sizing_pieces (never the original)."""
    c2 = w19_arm_cand(cand, face)
    return tl1.candidate_engine_params(c2, template)


def _exitcfg_defaults_now():
    """Live ExitConfig defaults via importlib read-only import (prereg
    sec.2 A9 anchor; ZERO engine edit) -- tl17 verbatim reuse."""
    return tl17._exitcfg_defaults_now()


def _exitcfg_gate():
    """A9 fail-closed gate: live engine defaults == frozen table
    (tl17 verbatim reuse; X=template_default consumed face)."""
    return tl17._exitcfg_gate()


def run_candidate_curve_w19(cand, template, face, prices, P, states,
                            atr20=None, fundamental_ok=None,
                            rng_matrix=None, p_on=None,
                            gate_state=None, vol_state=None,
                            yang_state=None, vconf_state=None,
                            streak_state=None, tstate_state=None,
                            amp_state=None, mom_state=None,
                            std_state=None, rsqr_state=None,
                            sumn_state=None, resi_state=None,
                            cnt_state=None, max_state=None,
                            rank_state=None):
    """One W19 paired cell at the engine face: the W16 overlay pipeline
    (filter -> timing -> GATE -> VOL -> YANG -> VCONF -> STREAK ->
    TSTATE -> AMP -> MOM -> STD -> RSQR -> SUMN -> RESI -> CNT -> MAX ->
    RANK -> initial-stop) with the TIMING FACE as the only variable
    (prereg sec.3; entry mask + all 19 non-T axes verbatim = both arms
    share one entry mask per block, the paired-control design body;
    engine params from w19_engine_params, sizing from tl1.sizing_pieces
    on the ARM cand at the as-burned axis[2]; P1 signal reversal =
    runner-native exit_signal=(S<=0) identical across all faces).
    Curve/overlay machinery = tl16 import-face reuse, zero
    re-derivation."""
    stop_key = cand["axis"][4]
    gate_key = cand["axis"][5]
    vol_key = cand["axis"][6]
    yang_key = cand["axis"][7]
    vconf_key = cand["axis"][8]
    streak_key = cand["axis"][9]
    tstate_key = cand["axis"][10]
    amp_key = cand["axis"][11]
    mom_key = cand["axis"][12]
    std_key = cand["axis"][13]
    rsqr_key = cand["axis"][14]
    sumn_key = cand["axis"][15]
    resi_key = cand["axis"][16]
    cnt_key = cand["axis"][17]
    max_key = cand["axis"][18]
    rank_key = cand["axis"][19]
    if gate_state is None:
        gate_state = tl16.tl3.gate_state_series(prices)
    if vol_state is None:
        vol_state = tl16.tl4.vol_state_series(prices)
    if yang_state is None:
        yang_state = tl16.tl5.yang_state_series(prices)
    if vconf_state is None:
        vconf_state = tl16.tl6.vconf_state_series(prices)
    if streak_state is None:
        streak_state = tl16.tl7.streak_state_series(prices)
    if tstate_state is None:
        tstate_state = tl16.tl8.tstate_state_series(prices)
    if amp_state is None:
        amp_state = tl16.amp_state_series(prices)
    if mom_state is None:
        mom_state = tl16.mom_state_series(prices)
    if std_state is None:
        std_state = tl16.std_state_series(prices)
    if rsqr_state is None:
        rsqr_state = tl16.rsqr_state_series(prices)
    if sumn_state is None:
        sumn_state = tl16.sumn_state_series(prices)
    if resi_state is None:
        resi_state = tl16.resi_state_series(prices)
    if cnt_state is None:
        cnt_state = tl16.cnt_state_series(prices)
    if max_state is None:
        max_state = tl16.max_state_series(prices)
    if rank_state is None:
        rank_state = tl16.rank_state_series(prices)
    if stop_key != "none" and tl2.STOP_FORMULA[stop_key]["kind"] == "atr" \
            and atr20 is None:
        atr20 = tl2.atr20_series(prices)
    mk = f"{cand['module']}.{cand['fn']}"
    face_frame = "null" if rng_matrix is not None \
        else tl1.GRAMMAR["faces"][mk]
    if rng_matrix is not None:
        mask = tl1._signal_frame(None, P, face_frame, rng_matrix=rng_matrix,
                                 p_on=p_on)
    else:
        mask = tl1._signal_frame(cand, P, face_frame)
    mask = mask.reindex(index=P["close"].index,
                        columns=P["close"].columns).fillna(0)
    mask = tl1.apply_filter(mask, cand["axis"][0], P, fundamental_ok)
    # timing face layer: the FACE is the single variable (prereg sec.3
    # -- per-arm axis[3] single-variable overwrite, tl1.apply_timing
    # verbatim path, zero new timing code)
    mask = tl1.apply_timing(mask, face)
    G = tl16.tl3.gate_zero_mask(mask, gate_key, gate_state)
    V = tl16.tl4.vol_zero_mask(G, vol_key, vol_state)
    Y = tl16.tl5.yang_zero_mask(V, yang_key, yang_state)
    VC = tl16.tl6.vconf_zero_mask(Y, vconf_key, vconf_state)
    SK = tl16.tl7.streak_zero_mask(VC, streak_key, streak_state)
    TS = tl16.tl8.tstate_zero_mask(SK, tstate_key, tstate_state)
    AP = tl16.tl9.amp_zero_mask(TS, amp_key, amp_state)
    MO = tl16.mom_zero_mask(AP, mom_key, mom_state)
    SD = tl16.std_zero_mask(MO, std_key, std_state)
    RQ = tl16.rsqr_zero_mask(SD, rsqr_key, rsqr_state)
    NQ = tl16.sumn_zero_mask(RQ, sumn_key, sumn_state)
    RE = tl16.resi_zero_mask(NQ, resi_key, resi_state)
    CN = tl16.cnt_zero_mask(RE, cnt_key, cnt_state)
    MX = tl16.max_zero_mask(CN, max_key, max_state)
    RK = tl16.rank_zero_mask(MX, rank_key, rank_state)
    gate_zeroed = int((mask > 0).sum().sum() - (G > 0).sum().sum())
    vol_zeroed = int((G > 0).sum().sum() - (V > 0).sum().sum())
    yang_zeroed = int((V > 0).sum().sum() - (Y > 0).sum().sum())
    vconf_zeroed = int((Y > 0).sum().sum() - (VC > 0).sum().sum())
    streak_zeroed = int((VC > 0).sum().sum() - (SK > 0).sum().sum())
    tstate_zeroed = int((SK > 0).sum().sum() - (TS > 0).sum().sum())
    amp_zeroed = int((TS > 0).sum().sum() - (AP > 0).sum().sum())
    mom_zeroed = int((AP > 0).sum().sum() - (MO > 0).sum().sum())
    std_zeroed = int((MO > 0).sum().sum() - (SD > 0).sum().sum())
    rsqr_zeroed = int((SD > 0).sum().sum() - (RQ > 0).sum().sum())
    sumn_zeroed = int((RQ > 0).sum().sum() - (NQ > 0).sum().sum())
    resi_zeroed = int((NQ > 0).sum().sum() - (RE > 0).sum().sum())
    cnt_zeroed = int((RE > 0).sum().sum() - (CN > 0).sum().sum())
    max_zeroed = int((CN > 0).sum().sum() - (MX > 0).sum().sum())
    rank_zeroed = int((MX > 0).sum().sum() - (RK > 0).sum().sum())
    if stop_key == "none":
        S, stop_fired = CN, 0
    else:
        S = tl2._effective_signal_mask(CN, prices, stop_key, atr20)
        d = (CN > 0) & (S == 0)
        stop_fired = int(sum(int((d[c] & ~d[c].shift(1, fill_value=False)
                                 ).sum()) for c in d.columns))
    # timing face layer: the ARM cand (X consumed + face at axis[3],
    # sizing as-burned at axis[2]) feeds BOTH the engine params and
    # sizing_pieces -- the timing face is the single variable, tl1
    # verbatim path, zero new timing code.
    c2 = w19_arm_cand(cand, face)
    params, patch = tl1.candidate_engine_params(c2, template)
    params, scale = tl1.sizing_pieces(c2, P, states, params)
    params["report_num_entries"] = True
    dd_control = (template.get("registered_dd_control")
                  if template is not None else None)
    with tl1.ExitPatch(patch):
        res = tl1.run_backtest(prices, params, entry_signal=S,
                               exit_signal=(S <= 0),
                               entry_size_scale=scale, dd_control=dd_control)
    eq = pd.Series(res["equity_curve"],
                   index=P["close"].index[:len(res["equity_curve"])])
    return eq, res["trades"], res["metrics"], params, patch, stop_fired, \
        gate_zeroed, vol_zeroed, yang_zeroed, vconf_zeroed, \
        streak_zeroed, tstate_zeroed, amp_zeroed, mom_zeroed, \
        std_zeroed, rsqr_zeroed, sumn_zeroed, resi_zeroed, cnt_zeroed, \
        max_zeroed, rank_zeroed


def _null_axis_draw_w19(i):
    """Deterministic null-cell draw per prereg sec.3: rng=[SEED_NULL, i]
    (W19 berth 20640500, band [20640500,20640700)); consumption order
    frozen = p_on regime -> 19-tuple non-T axis (R/X-fixed/S-as-drawn/
    STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR/SUMN/RESI/
    CNT/MAX/RANK; position 1 = template_default X-consumed FIXED, zero
    draw; position 2 = sizing drawn uniformly from tl1.AXIS_SIZING
    mirroring the W18 timing-draw slot) -> timing face (uniform over
    the 2 tl1.AXIS_TIMING faces, drawn LAST mirroring the W17/W18
    face-draw-at-the-end structure -- same grid/param space draw as
    candidate cells, BACKTEST_PLAN three iron rules) -> signal matrix
    (returned rng consumed later by the caller)."""
    rng = np.random.default_rng([SEED_NULL, i])
    p_on = tl1.NULL_P_REGIMES[int(rng.integers(len(tl1.NULL_P_REGIMES)))]
    ax = [tl1.AXIS_FILTERS[int(rng.integers(len(tl1.AXIS_FILTERS)))],
          X_CONSUMED,   # position 1 = X consumed, fixed zero-draw
          tl1.AXIS_SIZING[int(rng.integers(len(tl1.AXIS_SIZING)))],
          None,         # position 3 = timing face, drawn below (LAST)
          tl2.AXIS_STOP[int(rng.integers(len(tl2.AXIS_STOP)))],
          tl16.tl3.AXIS_GATE[int(rng.integers(len(tl16.tl3.AXIS_GATE)))],
          tl16.tl4.AXIS_VOL[int(rng.integers(len(tl16.tl4.AXIS_VOL)))],
          tl16.tl5.AXIS_YANG[int(rng.integers(len(tl16.tl5.AXIS_YANG)))],
          tl16.tl6.AXIS_VCONF[int(rng.integers(len(tl16.tl6.AXIS_VCONF)))],
          tl16.tl7.AXIS_STREAK[int(rng.integers(len(tl16.tl7.AXIS_STREAK)))],
          tl16.tl8.AXIS_TSTATE[int(rng.integers(len(tl16.tl8.AXIS_TSTATE)))],
          tl16.tl9.AXIS_AMP[int(rng.integers(len(tl16.tl9.AXIS_AMP)))],
          tl16.AXIS_MOM[int(rng.integers(len(tl16.AXIS_MOM)))],
          tl16.AXIS_STD[int(rng.integers(len(tl16.AXIS_STD)))],
          tl16.AXIS_RSQR[int(rng.integers(len(tl16.AXIS_RSQR)))],
          tl16.AXIS_SUMN[int(rng.integers(len(tl16.AXIS_SUMN)))],
          tl16.AXIS_RESI[int(rng.integers(len(tl16.AXIS_RESI)))],
          tl16.AXIS_CNT[int(rng.integers(len(tl16.AXIS_CNT)))],
          tl16.AXIS_MAX[int(rng.integers(len(tl16.AXIS_MAX)))],
          tl16.AXIS_RANK[int(rng.integers(len(tl16.AXIS_RANK)))]]
    ax[3] = W19_FACE_ORDER[int(rng.integers(len(W19_FACE_ORDER)))]
    return p_on, ax, rng


# ------------------------------------------------------------ grammar / generate
def _entry_load():
    """Entry-source anchor gate (prereg sec.2 A3): frozen W16 candidates
    product, sha256_16 verbatim, zero re-derivation.  The anchor was
    pinned on a CRLF worktree face, so hash the CRLF-canonical face:
    LF-only checkouts of the identical blob must not false-mismatch
    (r890 bm-b crash-loop repair); any content drift still fails closed."""
    with open(ENTRY_FILE, "rb") as fh:
        raw = fh.read()
    canon = raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    sha16 = __import__("hashlib").sha256(canon).hexdigest()[:16]
    if sha16 != ENTRY_SHA16:
        raise SystemExit(f"ENTRY-GATE FAIL: w16_candidates.json sha "
                         f"{sha16} != frozen {ENTRY_SHA16}")
    d = json.loads(raw)
    if len(d["candidates"]) != 173:
        raise SystemExit(f"ENTRY-GATE FAIL: n={len(d['candidates'])} != 173")
    return d


def build_grammar_w19():
    """Serialize the W19 grammar face: the frozen timing-face table +
    the entry-source anchor + lineage anchors (w14/w16/w17) + null/judge
    constants (deterministic, zero random; sec.3 GENERATE leg)."""
    ok, live = _timing_identity_gate()
    if not ok:
        raise SystemExit(f"GRAMMAR-GATE FAIL: tl1.AXIS_TIMING drift "
                         f"{live} != frozen {W19_FROZEN_TIMING}")
    g = {"wave": WAVE, "grammar_kind": "w19_timing_axis_paired_block",
         "prereg": PREREG, "evidence_cutoff": CUTOFF,
         "grammar_sha256": None,
         "seeds": {"gen_held": SEED_GEN, "scrnull": SEED_NULL,
                   "unc": SEED_UNC,
                   "band": [SEED_GEN, SEED_GEN + 2500],
                   "note": "gen held zero-consumption this wave (entry "
                           "= W16 frozen cells reuse); scrnull rng("
                           "[20640500,i]) i<200; unc rng([20641000,"
                           "cell_idx]) cell_idx<346; paired-delta "
                           "Wilcoxon streams rng([20641000,200+f]) "
                           "f<2 (above judge consumption <180, below "
                           "declared band top 346)"},
         "face_order": list(W19_FACE_ORDER),
         "timing_faces": {"source": "tl1.AXIS_TIMING verbatim import",
                          "rules": dict(W19_FACE_RULES),
                          "control_arm": "per-cell as-burned axis[3] "
                                         "frozen face (W16 sampled "
                                         "constant)",
                          "apply_timing": "tl1.apply_timing L596-604 "
                                          "verbatim (zero new timing "
                                          "code)"},
         "x_consumed": {"face": X_CONSUMED,
                        "basis": "W17 prereg sec.0 consumer (3) "
                                 "grammar-efficiency conclusion: W17-"
                                 "JUDGE 344 cells all-negative + 7 exit "
                                 "faces paired median delta 0.0 "
                                 "(wilcoxon_p 0.966-1.0)"},
         "s_consumed": {"face": "as-burned cell native axis[2]",
                        "basis": "W18 prereg sec.0 consumer (2) "
                                 "grammar-efficiency conclusion: "
                                 "W18-JUDGE 188 cells lawful-zero + 4 "
                                 "sizing faces paired median delta "
                                 "all ~0 = S-axis non-discriminating"},
         "k_nulls": K_NULLS,
         "null_p95_band": list(NULL_P95_BAND),
         "judge_cap_blocks": JUDGE_CAP_BLOCKS,
         "entry_source": {"file": "results/trial_labor_w16/"
                          "w16_candidates.json",
                          "sha256_16": ENTRY_SHA16, "n": 173,
                          "family_split": {"A": 6, "B": 167},
                          "axis3_timing_census": {"daily_signal": 128,
                                                  "weekly_grid": 45}},
         "w16_grammar_ref": {"file": "results/trial_labor_w16/"
                          "w16_grammar.json",
                          "grammar_sha16": W16_GRAMMAR_SHA16},
         "w17_grammar_ref": {"file": "results/trial_labor_w17/"
                          "w17_grammar.json",
                          "grammar_sha16": W17_GRAMMAR_SHA16},
         "w18_grammar_ref": {"file": "results/trial_labor_w18/"
                          "w18_grammar.json",
                          "grammar_sha16": W18_GRAMMAR_SHA16},
         "w14_lineage": {"grammar_sha16": W14_GRAMMAR_SHA16,
                         "file": "results/trial_labor_w14/w14_grammar.json"},
         "cell_key": "candidate_id x timing_face",
         "n_pairs": 173 * 2,
         "screen_trials": 173 * 2 + K_NULLS,
         "determinism_cross_gate": {"pairs": 173,
                                    "keys": ["beat6m_rate", "binom_z",
                                             "binom_p"],
                                    "sources": ["results/trial_labor_"
                                                "w17/w17_screen_cells."
                                                "csv (exit_face=="
                                                "template_default rows)",
                                                "results/trial_labor_"
                                                "w18/w18_screen_cells."
                                                "csv (as-burned sizing "
                                                "rows)"],
                                    "source_control_survivors": 43,
                                    "chain": "three-wave third link: "
                                             "W17 control == W18 "
                                             "as-burned == W19 as-burned"}}
    g["grammar_sha256"] = _grammar_sha16(g)
    return g


def cmd_grammar() -> int:
    """Serialize the frozen W19 grammar (idempotent; sha16 printed for
    the Slice-B pin)."""
    os.makedirs(RES_DIR, exist_ok=True)
    g = build_grammar_w19()
    if FROZEN_SHA16 and g["grammar_sha256"][:16] != FROZEN_SHA16:
        print(f"GRAMMAR-GATE: sha drift -- frozen anchor {FROZEN_SHA16} "
              f"!= built {g['grammar_sha256'][:16]} (fail-closed)")
        return 1
    _dump(GRAMMAR_FILE, g)
    print(f"grammar serialized: {GRAMMAR_FILE}")
    print(f"sha16 = {g['grammar_sha256'][:16]} "
          f"(pin this in FROZEN_SHA16 at Slice-B)")
    return 0


def _excluded_w19(cand, face, rows):
    """Exact already-burned cell test on (module, fn, sig_params,
    20-tuple with X consumed at axis[1] and the timing face at
    axis[3]) -- sec.3 exclusion book, 18 sources.  Returns the
    exclusion face tag or None."""
    ax = list(cand["axis"])
    ax[1] = X_CONSUMED
    ax[3] = face
    for e in rows:
        if (cand["module"], cand["fn"]) == (e["module"], e["fn"]) \
                and cand["sig_params"] == e["sig_params"] \
                and ax == e["axis"]:
            return e.get("face", "excluded")
    return None


def cmd_generate() -> int:
    """GENERATE leg (sec.3, deterministic zero-random): W16 candidates
    verbatim load + 2-face full-cross expansion + exclusion-book
    18-source live-read (W1-W14 + N2-W15 via the W16 grammar face +
    W16 burned cells + W17 burned cells + W18 burned cells) +
    w19_cells.json + TRIAL_GRAMMAR_LEDGER wave-19 row (W11/W17
    practice precedent).  Same-grammar rerun forbidden
    (TRIAL_LABOR_LAW sec.4).  Rerun-face clause: exactly the 173
    as-burned pairs (face == the cell's frozen axis[3]) are re-burns
    of the W17 control arm == W18 as-burned arm (paired baseline +
    determinism cross-gate); ANY other exclusion hit contradicts the
    frozen "173 new-grid pairs" claim -> honest refuse."""
    t0 = time.time()
    print(f"=== {WAVE} generate ===")
    if os.path.exists(CELLS_FILE):
        print("GENERATE-GATE: w19_cells.json already landed -- "
              "same-grammar rerun FORBIDDEN (TRIAL_LABOR_LAW sec.4)")
        return 2
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    if FROZEN_SHA16 and _grammar_sha16(grammar) != FROZEN_SHA16:
        print(f"GENERATE-GATE FAIL: grammar sha drift != frozen "
              f"{FROZEN_SHA16}")
        return 1
    ed = _entry_load()
    cands = ed["candidates"]
    # exclusion book 18-source live read: sources 1-15 = W1-W14 +
    # N2-W15 (serialized in the W16 grammar exclusion face + live-read
    # judged/screen faces by tl16's loader); source 16 = W16 burned
    # cells (own axes, live read); source 17 = W17 burned cells (all 8
    # exit faces, live read from the frozen W17 products -- only the
    # template_default rows can match a W19 cell by construction);
    # source 18 = W18 burned cells (all 4 sizing faces, live read --
    # only the as-burned sizing rows can match a W19 cell by
    # construction).
    w16g = json.load(open(W16_GRAMMAR_FILE, encoding="utf-8"))
    if _grammar_sha16(w16g)[:16] != W16_GRAMMAR_SHA16:
        print(f"GENERATE-GATE FAIL: w16_grammar sha drift != "
              f"{W16_GRAMMAR_SHA16}")
        return 1
    w17g = json.load(open(W17_GRAMMAR_FILE, encoding="utf-8"))
    if _grammar_sha16(w17g)[:16] != W17_GRAMMAR_SHA16:
        print(f"GENERATE-GATE FAIL: w17_grammar sha drift != "
              f"{W17_GRAMMAR_SHA16}")
        return 1
    w18g = json.load(open(W18_GRAMMAR_FILE, encoding="utf-8"))
    if _grammar_sha16(w18g)[:16] != W18_GRAMMAR_SHA16:
        print(f"GENERATE-GATE FAIL: w18_grammar sha drift != "
              f"{W18_GRAMMAR_SHA16}")
        return 1
    w17prod = json.load(open(W17_CELLS_FILE, encoding="utf-8"))
    w17_cells = w17prod.get("cells", [])
    w17_faces = set(w17g.get("face_order", []))
    if len(w17_cells) != 173 * 8 or not all(
            c.get("exit_face") in w17_faces for c in w17_cells):
        print(f"GENERATE-GATE FAIL: w17_cells.json census drift "
              f"({len(w17_cells)} cells) -- honest refuse")
        return 1
    w18prod = json.load(open(W18_CELLS_FILE, encoding="utf-8"))
    w18_cells = w18prod.get("cells", [])
    w18_faces = set(w18g.get("face_order", []))
    if len(w18_cells) != 173 * 4 or not all(
            c.get("sizing_face") in w18_faces for c in w18_cells):
        print(f"GENERATE-GATE FAIL: w18_cells.json census drift "
              f"({len(w18_cells)} cells) -- honest refuse")
        return 1
    rows, _excl_disc = tl16._load_exclusion_rows_w16(w16g)
    n_prev_rows = len(rows)
    for c in cands:   # source 16: W16 burned cells (own axes)
        rows.append({"module": c["module"], "fn": c["fn"],
                     "sig_params": c["sig_params"],
                     "axis": list(c["axis"]),
                     "face": "w16_burned_cell", "candidate_id":
                     c["candidate_id"]})
    n_w17_rows = 0
    by_cid = {c["candidate_id"]: c for c in cands}
    for cell in w17_cells:   # source 17: W17 burned cells (all faces)
        c = by_cid[cell["candidate_id"]]
        ax = list(c["axis"])
        ax[1] = cell["exit_face"]
        rows.append({"module": c["module"], "fn": c["fn"],
                     "sig_params": c["sig_params"],
                     "axis": ax, "face": "w17_burned_cell",
                     "candidate_id": cell["candidate_id"]})
        n_w17_rows += 1
    n_w18_rows = 0
    for cell in w18_cells:   # source 18: W18 burned cells (all faces)
        c = by_cid[cell["candidate_id"]]
        ax = list(c["axis"])
        ax[1] = X_CONSUMED
        ax[2] = cell["sizing_face"]
        rows.append({"module": c["module"], "fn": c["fn"],
                     "sig_params": c["sig_params"],
                     "axis": ax, "face": "w18_burned_cell",
                     "candidate_id": cell["candidate_id"]})
        n_w18_rows += 1
    rerun_pairs, other_hits = [], []
    cells = []
    for c in cands:
        for face in W19_FACE_ORDER:
            tag = _excluded_w19(c, face, rows)
            if face == c["axis"][3] and tag:
                rerun_pairs.append({"candidate_id": c["candidate_id"],
                                    "face": face, "source": tag})
            elif tag:
                other_hits.append({"candidate_id": c["candidate_id"],
                                   "face": face, "source": tag})
            cells.append({"cell_id": f"{c['candidate_id']}|{face}",
                          "candidate_id": c["candidate_id"],
                          "timing_face": face, "kind": "cand",
                          "family": c["family"]})
    if len(cells) != 173 * 2:
        print(f"GENERATE-GATE FAIL: cells {len(cells)} != 346")
        return 1
    if len(set(c["cell_id"] for c in cells)) != len(cells):
        print("GENERATE-GATE FAIL: cell-key collision (dedup violation)")
        return 1
    # sec.3 rerun-face clause: exactly the 173 as-burned pairs (face ==
    # the cell's frozen axis[3]) are re-burns of the W17 control arm ==
    # W18 as-burned arm; ANY other exclusion hit contradicts the
    # frozen "173 new-grid pairs" claim -> honest refuse (GM
    # adjudication face, zero fabrication).
    if other_hits:
        print(f"GENERATE-GATE FAIL: {len(other_hits)} exclusion hits "
              f"beyond the 173 as-burned rerun pairs (frozen sec.3 "
              f"claim violated) -- honest refuse, sample "
              f"{other_hits[:3]}")
        return 1
    if len(rerun_pairs) != 173:
        print(f"GENERATE-GATE FAIL: rerun pairs {len(rerun_pairs)} != 173 "
              "(sec.3 rerun-face clause: every as-burned pair must hit "
              "the W17 control / W18 as-burned arms) -- honest refuse")
        return 1
    prod = {"wave": WAVE, "stage": "generate", "prereg": PREREG,
            "evidence_cutoff": CUTOFF, **tl1.cutoff_meta(CUTOFF),
            "grammar_sha256": grammar["grammar_sha256"],
            "entry_sha256_16": ENTRY_SHA16,
            "n_candidates": 173, "n_faces": 2, "n_cells": len(cells),
            "rerun_pairs": rerun_pairs,
            "exclusion": {"sources": "W1-W14 + N2-W15 (w16 grammar "
                          "face) + W16 burned cells + W17 burned cells "
                          "(8 faces, live read) + W18 burned cells "
                          "(4 faces, live read)",
                          "prev_rows": n_prev_rows,
                          "w17_rows": n_w17_rows,
                          "w18_rows": n_w18_rows, "other_hits": 0},
            "family_split": ed.get("family_split", {"A": 6, "B": 167}),
            "seeds": grammar["seeds"],
            "cells": cells}
    _dump(CELLS_FILE, prod)
    # grammar consumption ledger row (append-only; W16/W17 caliber)
    ser_ts = time.strftime("%Y-%m-%d %H:%M",
                           time.localtime(os.path.getmtime(GRAMMAR_FILE)))
    row = (f"| {WAVE} | {grammar['grammar_sha256'][:16]} | "
           f"entry 173 x 2 timing faces (sha {ENTRY_SHA16}, zero new "
           f"generation, gen seed {SEED_GEN} held; X=template_default "
           f"consumed per W17 sec.0 consumer (3); S=as-burned kept per "
           f"W18 sec.0 consumer (2)) | paired cells "
           f"{len(cells)} + nulls {K_NULLS} = {len(cells) + K_NULLS} "
           f"(rerun face 173 as-burned W17-control==W18-asburned "
           f"pairs) | seeds "
           f"gen={SEED_GEN} null={SEED_NULL} unc={SEED_UNC} | "
           f"serialized {ser_ts} + consumed "
           f"{time.strftime('%Y-%m-%d %H:%M:%S')} (prereg bm-b r927 "
           f"frozen / runner bm-b r928 timing-axis build) | "
           f"same-grammar rerun FORBIDDEN (TRIAL_LABOR_LAW sec.4) |\n")
    gl = tl1.GRAMMAR_LEDGER
    os.makedirs(os.path.dirname(gl), exist_ok=True)
    if not os.path.exists(gl):
        with open(gl, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# TRIAL_GRAMMAR_LEDGER (append-only; "
                     "TRIAL_LABOR_LAW sec.4 same-grammar-rerun ban)\n\n"
                     "| wave | grammar_sha16 | raw | dedup | seeds | "
                     "consumed | law |\n|---|---|---|---|---|---|---|\n")
    with open(gl, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(row)
    print(f"generate done: 173 x 2 = {len(cells)} paired cells "
          f"(rerun face {len(rerun_pairs)} as-burned W17-control=="
          f"W18-asburned pairs, other hits 0)")
    print(f"products: {CELLS_FILE} + ledger row (sha16 "
          f"{grammar['grammar_sha256'][:16]})")
    print(f"elapsed {time.time() - t0:.1f}s (zero engine cells burned)")
    return 0


def cmd_status() -> int:
    print(f"=== {WAVE} status ===")
    for p, name in ((GRAMMAR_FILE, "grammar"), (CELLS_FILE, "cells"),
                    (PREP_FILE, "prep_state"), (SCREEN_FILE, "screen"),
                    (JUDGE_STATE_FILE, "judge_state"),
                    (JUDGE_FILE, "judge"), (REFORM_FILE, "reform_face"),
                    (PAIRED_FILE, "paired_deltas"),
                    (INTAKE_FILE, "intake")):
        print(f"  {name:14s} "
              f"{'PRESENT' if os.path.exists(p) else 'absent'}")
    print(f"  frozen sha16 pin: {FROZEN_SHA16}")
    ok, drift = _exitcfg_gate()
    print(f"  exitcfg A9 gate: {'PASS' if ok else f'DRIFT {drift}'}")
    tok, live = _timing_identity_gate()
    print(f"  timing G-TIMING gate: {'PASS' if tok else f'DRIFT {live}'}"
          f" (faces {list(live)})")
    return 0


# ------------------------------------------------------------ screen slice (s2)
csv_cols_screen_w19 = ["cell_id", "candidate_id", "timing_face", "family",
                       "module", "fn", "no_entries", "beat6m_k",
                       "beat6m_n", "beat6m_rate", "binom_z", "binom_p",
                       "sharpe_full", "dd_full", "n_trades", "n_entries",
                       "stop_face", "stop_fired", "gate_face",
                       "gate_zeroed", "vol_face", "vol_zeroed",
                       "yang_face", "yang_zeroed", "vconf_face",
                       "vconf_zeroed", "streak_face", "streak_zeroed",
                       "tstate_face", "tstate_zeroed", "amp_face",
                       "amp_zeroed", "mom_face", "mom_zeroed",
                       "std_face", "std_zeroed", "rsqr_face",
                       "rsqr_zeroed", "sumn_face", "sumn_zeroed",
                       "resi_face", "resi_zeroed", "cnt_face",
                       "cnt_zeroed", "max_face", "max_zeroed",
                       "rank_face", "rank_zeroed", "survives_screen"]

# pure survival-line math imported from tl2 (W2 identical frozen law)
_finalize_math = tl2._finalize_math


def _screen_cell_w19(cell):
    """One W19 screen cell: full leg-L backtest at the cell's timing
    face -> beat6m row (pool worker; W16/W17/W18 _screen_cell caliber
    + the timing_face column)."""
    st = tl1._ST
    kind, face = cell["kind"], cell["timing_face"]
    P, prices, states = st["P"], st["prices"], st["states"]
    starts, passive = st["starts"], st["passive_6m"]
    close = P["close"]
    if kind == "null":
        p_on, ax, rng = _null_axis_draw_w19(cell["i"])
        cand = {"module": "null", "fn": "random_signal",
                "sig_params": {"p_on": p_on}, "axis": ax,
                "candidate_id": f"W19-NULL-{cell['i']:04d}",
                "family": "NULL"}
        mat = rng.random((len(close.index), len(close.columns)))
        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \
            tz, az, mz, dz, rz, nz, rz2, cnz, mxz, rkz = \
            run_candidate_curve_w19(
                cand, None, ax[3], prices, P, states, st["atr20"],
                rng_matrix=mat, p_on=p_on, gate_state=st.get("gate_state"),
                vol_state=st.get("vol_state"),
                yang_state=st.get("yang_state"),
                vconf_state=st.get("vconf_state"),
                streak_state=st.get("streak_state"),
                tstate_state=st.get("tstate_state"),
                amp_state=st.get("amp_state"),
                mom_state=st.get("mom_state"),
                std_state=st.get("std_state"),
                rsqr_state=st.get("rsqr_state"),
                sumn_state=st.get("sumn_state"),
                resi_state=st.get("resi_state"),
                cnt_state=st.get("cnt_state"),
                max_state=st.get("max_state"),
                rank_state=st.get("rank_state"))
        cid = cand["candidate_id"]
    else:
        cand, template = cell["cand"], cell.get("template")
        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \
            tz, az, mz, dz, rz, nz, rz2, cnz, mxz, rkz = \
            run_candidate_curve_w19(
                cand, template, face, prices, P, states, st["atr20"],
                fundamental_ok=st["fundamental_ok"],
                gate_state=st.get("gate_state"),
                vol_state=st.get("vol_state"),
                yang_state=st.get("yang_state"),
                vconf_state=st.get("vconf_state"),
                streak_state=st.get("streak_state"),
                tstate_state=st.get("tstate_state"),
                amp_state=st.get("amp_state"),
                mom_state=st.get("mom_state"),
                std_state=st.get("std_state"),
                rsqr_state=st.get("rsqr_state"),
                sumn_state=st.get("sumn_state"),
                resi_state=st.get("resi_state"),
                cnt_state=st.get("cnt_state"),
                max_state=st.get("max_state"),
                rank_state=st.get("rank_state"))
        cid = cand["candidate_id"]
    row = {"cell_id": cell["cell_id"], "candidate_id": cid,
           "timing_face": face, "family": cand["family"],
           "stop_face": cand["axis"][4], "stop_fired": int(fired),
           "gate_face": cand["axis"][5], "gate_zeroed": int(gz),
           "vol_face": cand["axis"][6], "vol_zeroed": int(vz),
           "yang_face": cand["axis"][7], "yang_zeroed": int(yz),
           "vconf_face": cand["axis"][8], "vconf_zeroed": int(cz),
           "streak_face": cand["axis"][9], "streak_zeroed": int(sz),
           "tstate_face": cand["axis"][10], "tstate_zeroed": int(tz),
           "amp_face": cand["axis"][11], "amp_zeroed": int(az),
           "mom_face": cand["axis"][12], "mom_zeroed": int(mz),
           "std_face": cand["axis"][13], "std_zeroed": int(dz),
           "rsqr_face": cand["axis"][14], "rsqr_zeroed": int(rz),
           "sumn_face": cand["axis"][15], "sumn_zeroed": int(nz),
           "resi_face": cand["axis"][16], "resi_zeroed": int(rz2),
           "cnt_face": cand["axis"][17], "cnt_zeroed": int(cnz),
           "max_face": cand["axis"][18], "max_zeroed": int(mxz),
           "rank_face": cand["axis"][19], "rank_zeroed": int(rkz)}
    if len(eq) < 30 or float(eq.iloc[0]) <= 0:
        row.update({"no_entries": True, "beat6m_k": 0,
                    "beat6m_n": len(starts), "beat6m_rate": 0.0,
                    "sharpe_full": None,
                    "n_trades": int(metrics.get("num_trades", 0)),
                    "n_entries": int(metrics.get("num_entries", 0))})
        return row
    k = n_win = 0
    for p in starts:
        if p + W6M - 1 >= len(eq):
            continue
        n_win += 1
        cret = float(eq.iloc[p + W6M - 1] / eq.iloc[p] - 1.0)
        if cret >= passive[p]:        # prereg sec.3 literal ">="
            k += 1
    rate = k / n_win if n_win else 0.0
    n = len(starts)
    z = (k - 0.5 * n) / math.sqrt(0.25 * n) if n else 0.0
    pval = 2 * (1 - tl1._norm_cdf(abs(z)))
    row.update({"no_entries": False, "module": cand.get("module"),
                "fn": cand.get("fn"), "beat6m_k": k, "beat6m_n": n_win,
                "beat6m_rate": round(rate, 6), "binom_z": round(z, 4),
                "binom_p": round(pval, 6),
                "sharpe_full": round(float(tl1.sharpe(eq)), 4),
                "dd_full": round(float(tl1.max_drawdown(eq)), 4),
                "n_trades": int(metrics.get("num_trades", 0)),
                "n_entries": int(metrics.get("num_entries", 0))})
    return row


def _cell_list_w19():
    """Paired cells + K null cells (deterministic order; shard-split by
    index; W16/W17/W18 precedent).  Block order = candidate-major,
    face-minor (the complete-block bookkeeping face)."""
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    prod = json.load(open(CELLS_FILE, encoding="utf-8"))
    a_by_trader = {t["trader_id"]: t for t in tl1.A_TEMPLATES}
    entry = {c["candidate_id"]: c for c in
             _entry_load()["candidates"]}
    cells = []
    for cell in prod["cells"]:
        c = entry[cell["candidate_id"]]
        template = (a_by_trader.get(c.get("template_trader"))
                    if c["family"] == "A" else None)
        cells.append({"cell_id": cell["cell_id"], "kind": "cand",
                      "cand": c, "template": template,
                      "timing_face": cell["timing_face"]})
    for i in range(K_NULLS):
        cells.append({"cell_id": f"SCREEN|NULL-{i:04d}", "kind": "null",
                      "i": i, "cand": None, "timing_face": None})
    return grammar, cells


def cmd_screen_prep() -> int:
    """G-PANEL / G-ENTRY / G-LINEAGE (w14+w16+w17) / G-EXITCFG /
    G-TIMING / G-CROSSSRC (dual-source) fail-closed gates (prereg
    sec.2 anchors) + the shared passive 6m precompute.  Identity-first-
    run law (r446bmb): every panel/anchor identity face runs BEFORE
    the cells-presence refusal so the full identity face exercises on
    real data pre-generate (rc=2 honest 'generate pending' lands at
    the TAIL)."""
    print(f"=== {WAVE} screen-prep (fail-closed gates) ===")
    # G-EXITCFG (A9): live engine defaults == frozen table (X=template_
    # default consumed -> the default stack is the tested baseline)
    ok, drift = _exitcfg_gate()
    if not ok:
        print(f"PREP-GATE FAIL: G-EXITCFG drift {drift} (engine "
              "exit_rules.py drifted vs prereg sec.2 A9 -- fail-closed)")
        return 1
    # G-TIMING: tl1.AXIS_TIMING == frozen two-tuple, verbatim import
    tok, live = _timing_identity_gate()
    if not tok:
        print(f"PREP-GATE FAIL: G-TIMING drift {live} != frozen "
              f"{W19_FROZEN_TIMING} (tl1.AXIS_TIMING face-mismatch -- "
              "fail-closed)")
        return 1
    # G-LINEAGE (A4): w14 + w16 + w17 pins == ledger rows
    w14g = json.load(open(W14_GRAMMAR_FILE, encoding="utf-8"))
    if str(w14g.get("grammar_sha256", ""))[:16] != W14_GRAMMAR_SHA16:
        print(f"PREP-GATE FAIL: w14_grammar internal sha != "
              f"{W14_GRAMMAR_SHA16}")
        return 1
    w16g = json.load(open(W16_GRAMMAR_FILE, encoding="utf-8"))
    if _grammar_sha16(w16g)[:16] != W16_GRAMMAR_SHA16:
        print(f"PREP-GATE FAIL: w16_grammar sha != {W16_GRAMMAR_SHA16}")
        return 1
    w17g = json.load(open(W17_GRAMMAR_FILE, encoding="utf-8"))
    if _grammar_sha16(w17g)[:16] != W17_GRAMMAR_SHA16:
        print(f"PREP-GATE FAIL: w17_grammar sha != {W17_GRAMMAR_SHA16}")
        return 1
    led_rows = {}
    if os.path.exists(tl1.GRAMMAR_LEDGER):
        for ln in open(tl1.GRAMMAR_LEDGER, encoding="utf-8"):
            parts = [p.strip() for p in ln.split("|")]
            if len(parts) > 3 and parts[1].startswith("TRIAL_LABOR"):
                led_rows[parts[1]] = parts[2]
    if led_rows.get("TRIAL_LABOR_W14") != W14_GRAMMAR_SHA16 \
            or led_rows.get("TRIAL_LABOR_W16") != W16_GRAMMAR_SHA16 \
            or led_rows.get("TRIAL_LABOR_W17") != W17_GRAMMAR_SHA16:
        print("PREP-GATE FAIL: ledger lineage mismatch w14="
              f"{led_rows.get('TRIAL_LABOR_W14')} w16="
              f"{led_rows.get('TRIAL_LABOR_W16')} w17="
              f"{led_rows.get('TRIAL_LABOR_W17')}")
        return 1
    # G-CROSSSRC (sec.2 determinism dual-source anchors, batch-unique):
    # the W17 control rows (exit_face==template_default) + the W18
    # as-burned rows (sizing_face==cell axis[2]) + both products' frozen
    # as-burned survivor counts (43 each, three-wave chain fact)
    w17_ctrl = _w17_control_rows()
    if len(w17_ctrl) != 173:
        print(f"PREP-GATE FAIL: G-CROSSSRC W17 control rows "
              f"{len(w17_ctrl)} != 173 (w17_screen_cells.csv "
              "exit_face==template_default census)")
        return 1
    w18_asb = _w18_asburned_rows()
    if len(w18_asb) != 173:
        print(f"PREP-GATE FAIL: G-CROSSSRC W18 as-burned rows "
              f"{len(w18_asb)} != 173 (w18_screen_cells.csv "
              "sizing_face==as-burned census)")
        return 1
    w17s = json.load(open(W17_SCREEN_FILE, encoding="utf-8"))
    n_ctrl_surv = sum(1 for s in w17s.get("survivors", [])
                      if s.endswith("|template_default"))
    if n_ctrl_surv != 43:
        print(f"PREP-GATE FAIL: G-CROSSSRC W17 control survivors "
              f"{n_ctrl_surv} != 43 (w17_screen.json frozen fact, "
              "prereg sec.2 anchor)")
        return 1
    w18s = json.load(open(W18_SCREEN_FILE, encoding="utf-8"))
    w18_ab_by = {c["candidate_id"]: c["axis"][2]
                 for c in _entry_load()["candidates"]}
    n_w18_asb_surv = sum(1 for s in w18s.get("survivors", [])
                         if s.split("|", 1)[0] in w18_ab_by
                         and s.split("|", 1)[1]
                         == w18_ab_by[s.split("|", 1)[0]])
    if n_w18_asb_surv != 43:
        print(f"PREP-GATE FAIL: G-CROSSSRC W18 as-burned survivors "
              f"{n_w18_asb_surv} != 43 (w18_screen.json frozen fact, "
              "three-wave chain second link)")
        return 1
    tl1.GRAMMAR = w16g   # signal faces for the 173 W16 candidates
    if not tl1.self_test_patches():
        print("PREP-GATE FAIL: patch self-test")
        return 1
    # G-PANEL (A1/A2): cutoff-frozen face
    prices_full = tl1.load_core()
    cut = pd.Timestamp(CUTOFF)
    prices_full = {s: df[df.index <= cut] for s, df in prices_full.items()}
    n_members = len(prices_full)
    bad = [s for s, df in prices_full.items()
           if len(df) < 60 or str(df.index[-1].date()) != CUTOFF
           or not {"open", "high", "low", "close", "volume"} <= set(
               df.columns)]
    gp = {"members": n_members, "bad": bad,
          "pass": bool(n_members == 48 and not bad)}
    if not gp["pass"]:
        print(f"PREP-GATE FAIL: G-PANEL {gp}")
        return 1
    # G-ENTRY (A3): frozen entry product sha + n (raises on drift)
    ed = _entry_load()
    # axis[3] timing-slot census (freeze banner: 128/45 mixed faces)
    census = {}
    for c in ed["candidates"]:
        census[c["axis"][3]] = census.get(c["axis"][3], 0) + 1
    if census != {"daily_signal": 128, "weekly_grid": 45}:
        print(f"PREP-GATE FAIL: axis[3] timing census drift {census}")
        return 1
    # G-GRAMMAR: W19 grammar pin
    grammar = None
    if os.path.exists(GRAMMAR_FILE):
        grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
        if FROZEN_SHA16 and _grammar_sha16(grammar) != FROZEN_SHA16:
            print(f"PREP-GATE FAIL: w19 grammar sha drift != frozen "
                  f"{FROZEN_SHA16}")
            return 1
        if grammar["entry_source"]["sha256_16"] != ENTRY_SHA16:
            print("PREP-GATE FAIL: grammar entry anchor drift")
            return 1
    # starts + passive 6m precompute (W16 caliber on the shared panel)
    prices, P, idx, listed, cen = tl1._load_leg("L")
    if cen != tl1.FROZEN_CENSUS["L"]:
        print(f"PREP-GATE FAIL: leg-L census drift {cen}")
        return 1
    close = P["close"]
    n = len(idx)
    starts = [p for p in range(n)
              if idx[p] >= tl1.LEG_L_FLOOR and p >= tl1.WARMUP_TD
              and p <= n - 1 - W6M and listed.iloc[p] >= tl1.MIN_LISTED]
    if len(starts) != tl1.FROZEN_CENSUS["L"]["6m"]:
        print(f"PREP-GATE FAIL: 6m starts {len(starts)} != "
              f"{tl1.FROZEN_CENSUS['L']['6m']}")
        return 1
    passive_6m = {}
    for p in starts:
        sdate = idx[p]
        edate = idx[p + W6M - 1]
        syms = close.columns[close.loc[sdate].notna()]
        rel = tl1.passive_rel(close, syms, sdate, edate)
        passive_6m[int(p)] = round(float(rel.iloc[-1] - 1.0), 6)
    # cells-presence gate at the TAIL (identity-first-run law)
    if not os.path.exists(CELLS_FILE):
        print("PREP-GATE FAIL: w19_cells.json absent -- generate "
              "pending (identity faces above ALL PASS on real data)")
        return 2
    prod = json.load(open(CELLS_FILE, encoding="utf-8"))
    if grammar is not None and str(prod.get("grammar_sha256", "")
                                   )[:16] != grammar["grammar_sha256"][:16]:
        print("PREP-GATE FAIL: cells grammar_sha256 != grammar anchor")
        return 1
    prep = {"wave": WAVE, "evidence_cutoff": CUTOFF,
            **tl1.cutoff_meta(CUTOFF),
            "grammar_sha256": (grammar or {}).get("grammar_sha256"),
            "gates": {"G-PANEL": gp,
                      "G-ENTRY": {"sha256_16": ENTRY_SHA16, "n": 173,
                                  "axis3_census": census, "pass": True},
                      "G-LINEAGE": {"w14": W14_GRAMMAR_SHA16,
                                    "w16": W16_GRAMMAR_SHA16,
                                    "w17": W17_GRAMMAR_SHA16,
                                    "ledger_match": True, "pass": True},
                      "G-EXITCFG": {"pass": True,
                                    "defaults": EXITCFG_DEFAULTS},
                      "G-TIMING": {"faces": list(W19_FACE_ORDER),
                                   "pass": True},
                      "G-CROSSSRC": {"w17_control_rows":
                                     len(w17_ctrl),
                                     "w17_control_survivors":
                                     n_ctrl_surv,
                                     "w18_asburned_rows": len(w18_asb),
                                     "w18_asburned_survivors":
                                     n_w18_asb_surv,
                                     "pass": True}},
            "starts": starts, "passive_6m_ret": passive_6m}
    _dump(PREP_FILE, prep)
    print(f"prep done: {len(starts)} starts, passive 6m precomputed -> "
          f"{PREP_FILE}")
    return 0


def _park_stamp():
    return tl17._park_stamp()


_BURN_STARTED = None


def _claim_machine_id() -> str:
    """Worker-claim identity (fleet/machine.json; honest fallback)."""
    return tl17._claim_machine_id()


def _worker_claim(entry_id: str, shard_key: str, result_ref: str) -> None:
    """r497 worker-side harvest handshake (tl17 verbatim reuse; only
    called from the real-burn completion paths -- the hermetic selftest
    never reaches here).  The worker NEVER writes runnable_pool.json
    (pool single-writer law)."""
    tl17._worker_claim(entry_id, shard_key, result_ref)


def cmd_screen(shard: int, shards: int, workers) -> int:
    global _BURN_STARTED
    import datetime
    _BURN_STARTED = datetime.datetime.now().astimezone().isoformat(
        timespec="seconds")
    print(f"=== {WAVE} screen shard {shard}of{shards} ===")
    for p, what in ((PREP_FILE, "prep_state.json"),
                    (CELLS_FILE, "w19_cells.json")):
        if not os.path.exists(p):
            print(f"SCREEN-GATE: {what} absent -- run screen-prep first")
            return 2
    prep = json.load(open(PREP_FILE, encoding="utf-8"))
    grammar, cells = _cell_list_w19()
    if FROZEN_SHA16 and _grammar_sha16(grammar) != FROZEN_SHA16:
        print(f"SCREEN-GATE: grammar sha drift != frozen {FROZEN_SHA16}")
        return 2
    ram_min, ram_ok = tl2._ram_gate_gb(wait_min=40)
    if not ram_ok:
        # flush=True mandatory (r691 four-piece law, r800 live case): the
        # crash-confirmer reads this marker from the launch log MINUTES
        # before interpreter shutdown would flush -- an unflushed marker
        # is invisible to exactly the tick that must park instead of
        # fuse-feeding.
        print(f"AUTOFILL-PARK: {_park_stamp()} screen RAM gate "
              f"{ram_min}GB < 4GB after bounded wait (r354/r379) -- "
              "honest zero-burn, NOT a crash (r491 park law); "
              "un-park = session flip when RAM frees", flush=True)
        print(f"SCREEN-GATE: free RAM {ram_min}GB < 4GB after bounded "
              f"wait (three-sample r354 law; r379 wait-law) -- honest "
              "refuse, pool retries when RAM frees", flush=True)
        return 2
    tl1.GRAMMAR = json.load(open(W16_GRAMMAR_FILE, encoding="utf-8"))
    mine = [c for i, c in enumerate(cells) if i % shards == shard]
    prices, P, idx, listed, cen = tl1._load_leg("L")
    states = tl1.v3_state_series()
    try:
        bl = pd.read_csv(tl1.B_LAYER_MASK)
        ok_codes = set(bl.loc[bl["ok_static"] == True, "code"].astype(str))
        overlap = sorted(s for s in P["close"].columns if s in ok_codes)
    except Exception:
        overlap = []
    if overlap:
        fundamental_ok = pd.DataFrame(False, index=P["close"].index,
                                      columns=P["close"].columns)
        for s in overlap:
            fundamental_ok[s] = True
    else:
        fundamental_ok = None
    vol_state, vol_err = tl16.tl4._vol_state_full()
    if vol_err:
        print(f"SCREEN-GATE: {vol_err} (prereg sec.2 fail-closed) -- "
              "refuse")
        return 2
    yang_state, yang_err = tl16.tl5._yang_state_full()
    if yang_err:
        print(f"SCREEN-GATE: {yang_err} -- refuse")
        return 2
    vconf_state, vconf_err = tl16.tl6._vconf_state_full()
    if vconf_err:
        print(f"SCREEN-GATE: {vconf_err} -- refuse")
        return 2
    state = {"P": P, "prices": prices, "states": states,
             "starts": prep["starts"],
             "passive_6m": {int(k): v for k, v in
                            prep["passive_6m_ret"].items()},
             "fundamental_ok": fundamental_ok,
             # r581/crash-fix: the pool worker's ONLY grammar consumer is
             # run_candidate_curve_w19 tl1.GRAMMAR["faces"][mk] -- the
             # W19 grammar has no faces table (faces live in W16 grammar,
             # 77 mk keys). spawn workers re-import tl1 so the parent's
             # tl1.GRAMMAR load never propagates; the faces table must
             # ride initargs (w1 _init_worker GRAMMAR law, r121).
             "grammar": tl1.GRAMMAR, "atr20": tl2.atr20_series(prices),
             "gate_state": tl16.tl3.gate_state_series(prices),
             "vol_state": vol_state, "yang_state": yang_state,
             "vconf_state": vconf_state,
             "streak_state": tl16.tl7.streak_state_series(prices),
             "tstate_state": tl16.tl8.tstate_state_series(prices),
             "amp_state": tl16.amp_state_series(prices),
             "mom_state": tl16.mom_state_series(prices),
             "std_state": tl16.std_state_series(prices),
             "rsqr_state": tl16.rsqr_state_series(prices),
             "sumn_state": tl16.sumn_state_series(prices),
             "resi_state": tl16.resi_state_series(prices),
             "cnt_state": tl16.cnt_state_series(prices),
             "max_state": tl16.max_state_series(prices),
             "rank_state": tl16.rank_state_series(prices)}
    ck = os.path.join(CKPT_DIR, f"screen_shard_{shard}of{shards}.jsonl")
    os.makedirs(CKPT_DIR, exist_ok=True)
    done = set()
    if os.path.exists(ck):
        with open(ck, encoding="utf-8") as fh:
            for ln in fh:
                try:
                    done.add(json.loads(ln)["cell_id"])
                except Exception:
                    pass
    todo = [c for c in mine if c["cell_id"] not in done]
    print(f"shard cells {len(mine)}, done {len(done)}, todo {len(todo)}")

    def on_result(key, payload):
        os.makedirs(CKPT_DIR, exist_ok=True)
        with open(ck, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(tl1._j(payload), ensure_ascii=False,
                                default=float) + "\n")

    if todo:
        jobs = [(c["cell_id"], _screen_cell_w19, (c,)) for c in todo]
        tl1.run_cells_parallel(jobs, workers=workers or tl1.worker_cap(),
                              desc="screen cells",
                              initializer=tl1._init_worker,
                              initargs=(state,), on_result=on_result)
    print(f"shard {shard}of{shards} complete -> {ck}")
    _worker_claim(f"TRIAL-LABOR-W19-SCREEN-SHARD-{shard}",
                  f"w19-screen-{shard}of{shards}",
                  os.path.relpath(ck, os.path.dirname(os.path.dirname(
                      os.path.abspath(__file__)))))
    return 0


def _w17_control_rows():
    """W17 screen control-arm rows keyed by candidate_id (frozen
    product read; exit_face==template_default rows only -- the sec.2
    determinism source anchor, three-wave chain link 1)."""
    rows = {}
    with open(W17_SCREEN_CSV, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r.get("exit_face") == X_CONSUMED:
                rows[r["candidate_id"]] = r
    return rows


def _w18_asburned_rows():
    """W18 screen as-burned-arm rows keyed by candidate_id (frozen
    product read; sizing_face==cell as-burned axis[2] rows only -- the
    sec.2 determinism source anchor, three-wave chain link 2)."""
    as_burned_by = {c["candidate_id"]: c["axis"][2]
                    for c in _entry_load()["candidates"]}
    rows = {}
    with open(W18_SCREEN_CSV, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r.get("sizing_face") == as_burned_by.get(
                    r.get("candidate_id")):
                rows[r["candidate_id"]] = r
    return rows


# byte-identity comparison keys for the 173-pair determinism cross-gate
# (prereg sec.2/sec.3 FROZEN: three columns exactly)
_XGATE_KEYS = ("beat6m_rate", "binom_z", "binom_p")


def _control_determinism_gate(ctrl_rows, ref_rows):
    """sec.3 rerun-face determinism cross-gate: the 173 as-burned arm
    screen readings must be BYTE-IDENTICAL to the reference arm's
    same-cell readings on the three frozen columns (deterministic
    engine + same cutoff; any mismatch = face-mismatch VOID).
    Source-agnostic comparator: called once per source (W17 control
    rows, then W18 as-burned rows).  Returns (n_checked, mismatches)."""
    mism = []
    n = 0
    for cid, mine in ctrl_rows.items():
        ref = ref_rows.get(cid)
        if ref is None:
            mism.append({"candidate_id": cid,
                         "key": "_absent_in_ref_csv"})
            continue
        n += 1
        for k in _XGATE_KEYS:
            a, b = mine.get(k), ref.get(k)
            if a is None and (b is None or b == ""):
                continue
            try:
                if float(a) != float(b):
                    mism.append({"candidate_id": cid, "key": k,
                                 "w19": a, "ref": b})
            except (TypeError, ValueError):
                if str(a) != str(b):
                    mism.append({"candidate_id": cid, "key": k,
                                 "w19": a, "ref": b})
    return n, mism


def cmd_screen_finalize() -> int:
    """Screen-finalize: survival line (null p95 via the frozen W2 math)
    + G-face assertion battery (entry sha / grammar pin / A9 ExitConfig
    / G-TIMING / 173-pair as-burned determinism cross-gate DUAL-SOURCE
    VOID face + sec.5.1 count prediction accounting) + ledger append +
    products."""
    print(f"=== {WAVE} screen-finalize ===")
    landed = tl16.tl6.finalize_already_landed(SCREEN_BATCH, SCREEN_FILE)
    if landed is not None:
        print(f"finalize: already landed (ledger total "
              f"{landed['total']}) -- idempotent no-op")
        return 0
    for p, what in ((GRAMMAR_FILE, "w19_grammar.json"),
                    (CELLS_FILE, "w19_cells.json"),
                    (PREP_FILE, "prep_state.json")):
        if not os.path.exists(p):
            print(f"FINALIZE-GATE: {what} absent -- honest refuse "
                  "(identity face: no products to finalize)")
            return 2
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    if FROZEN_SHA16 and _grammar_sha16(grammar) != FROZEN_SHA16:
        print(f"FINALIZE-GATE: grammar sha drift != {FROZEN_SHA16}")
        return 1
    ed = _entry_load()   # G-ENTRY re-assert (raises on drift)
    ok, drift = _exitcfg_gate()
    if not ok:
        print(f"FINALIZE-GATE: G-EXITCFG drift {drift} -- VOID refuse")
        return 1
    tok, live = _timing_identity_gate()
    if not tok:
        print(f"FINALIZE-GATE: G-TIMING drift {live} -- VOID refuse")
        return 1
    rows = []
    for f in sorted(os.listdir(CKPT_DIR)):
        if f.startswith("screen_shard_") and f.endswith(".jsonl"):
            with open(os.path.join(CKPT_DIR, f), encoding="utf-8") as fh:
                for ln in fh:
                    try:
                        rows.append(json.loads(ln))
                    except Exception:
                        pass
    cand_rows = [r for r in rows
                 if not str(r["candidate_id"]).startswith("W19-NULL")]
    null_rows = [r for r in rows
                 if str(r["candidate_id"]).startswith("W19-NULL")]
    expected = 173 * 2
    if len(cand_rows) != expected or len(null_rows) != K_NULLS:
        print(f"FINALIZE-GATE: incomplete checkpoint ({len(cand_rows)}/"
              f"{expected} cand, {len(null_rows)}/{K_NULLS} nulls) -- "
              "honest refuse (burn pending)")
        return 2
    # G-CONTROL-DETERMINISM (DUAL-SOURCE): 173-pair three-column
    # byte-identity vs BOTH the W17 control arm AND the W18 as-burned
    # arm (hard VOID gate; as-burned arm == the cell's frozen axis[3]
    # face; three-wave chain third link, prereg sec.2/sec.5.1)
    as_burned_by = {c["candidate_id"]: c["axis"][3]
                    for c in ed["candidates"]}
    ctrl_rows = {r["candidate_id"]: r for r in cand_rows
                 if r["timing_face"] == as_burned_by.get(r["candidate_id"])}
    n17, mism17 = _control_determinism_gate(ctrl_rows,
                                            _w17_control_rows())
    xgate17 = {"source": "w17_screen_cells.csv control rows",
               "n_pairs_expected": 173, "n_checked": n17,
               "keys": list(_XGATE_KEYS), "mismatches": mism17,
               "pass": bool(n17 == 173 and not mism17)}
    n18, mism18 = _control_determinism_gate(ctrl_rows,
                                            _w18_asburned_rows())
    xgate18 = {"source": "w18_screen_cells.csv as-burned rows",
               "n_pairs_expected": 173, "n_checked": n18,
               "keys": list(_XGATE_KEYS), "mismatches": mism18,
               "pass": bool(n18 == 173 and not mism18)}
    if not (xgate17["pass"] and xgate18["pass"]):
        print(f"FINALIZE-GATE: as-burned determinism cross-gate VOID "
              f"(W17 checked {n17} mism {mism17[:3]}; W18 checked "
              f"{n18} mism {mism18[:3]}) -- "
              "face-mismatch, NOT a scientific reading (prereg sec.2/"
              "sec.3; report face-misconfig per G-ANCHOR-FACE law)")
        return 3
    # survival line (frozen W2 math; survive iff beat6m > null p95).
    # Cell-key law: the trial unit is the CELL (entry x face), so the
    # finalize-math key = cell_id (unique); the entry id stays in the
    # candidate_id column for the cross-gate + csv faces.
    math_rows = [dict(r, candidate_id=r["cell_id"]) for r in cand_rows]
    p95, survivors = _finalize_math(math_rows, null_rows)
    surv_set = set(survivors)
    for r in cand_rows:
        r["survives_screen"] = r["cell_id"] in surv_set
    null_p95 = round(float(p95), 6)
    band_hit = bool(NULL_P95_BAND[0] <= null_p95 <= NULL_P95_BAND[1])
    # sec.5.1 count prediction accounting (honest, non-VOID: the hard
    # determinism gate is the 173-pair identity above; the count is a
    # frozen prediction -> sec.7 post-run accounting per sec.5 charter)
    ab_surv = [s for s in survivors
               if s.split("|", 1)[0] in as_burned_by
               and s.split("|", 1)[1] == as_burned_by[s.split("|", 1)[0]]]
    pred_51 = {"predicted": PRED_AS_BURNED_SURVIVORS,
               "observed_as_burned_survivors": len(ab_surv),
               "verdict": "HIT" if len(ab_surv) ==
               PRED_AS_BURNED_SURVIVORS else "MISS"}
    per_face = {}
    for f in W19_FACE_ORDER:
        face_rows = [r for r in cand_rows if r["timing_face"] == f]
        n_s = sum(1 for r in face_rows if r["survives_screen"])
        per_face[f] = {"n": len(face_rows), "n_survivors": n_s,
                       "survival_rate": round(n_s / max(1, len(face_rows)),
                                              6)}
    face_summary = {f: per_face[f]["n_survivors"] for f in W19_FACE_ORDER}
    ledger = tl1.append_ledger(SCREEN_BATCH, len(cand_rows) + len(null_rows),
                               "results/trial_labor_w19/w19_screen.json",
                               evidence_cutoff=CUTOFF)
    prod = {"wave": WAVE, "stage": "screen-finalize", "prereg": PREREG,
            "evidence_cutoff": CUTOFF, **tl1.cutoff_meta(CUTOFF),
            "grammar_sha256": grammar["grammar_sha256"],
            "n_paired_cells": expected, "k_nulls": len(null_rows),
            "survival_rule": "beat6m_rate > null_p95 (prereg sec.4, "
                             "frozen W2 math, zero hand-picked)",
            "null_p95": null_p95, "null_p95_band": list(NULL_P95_BAND),
            "null_p95_band_hit": band_hit,
            "n_survivors": len(survivors), "survivors": survivors,
            "g_face_battery": {"G-ENTRY": {"sha256_16": ENTRY_SHA16},
                               "G-EXITCFG": {"pass": True},
                               "G-TIMING": {"faces": list(W19_FACE_ORDER),
                                            "pass": True},
                               "G-CONTROL-DETERMINISM": {
                                   "w17_source": xgate17,
                                   "w18_source": xgate18},
                               "sec51_prediction_accounting": pred_51},
            "per_face_survival": per_face,
            "rerun_pairs_n": 173,
            "trials_ledger": ledger}
    _dump(SCREEN_FILE, prod)
    with open(SCREEN_CSV, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=csv_cols_screen_w19,
                           extrasaction="ignore")
        w.writeheader()
        for r in sorted(cand_rows + null_rows,
                        key=lambda r: r["cell_id"]):
            w.writerow({k: r.get(k) for k in csv_cols_screen_w19})
    print(f"screen-finalize done: null p95 {null_p95} "
          f"(band {'HIT' if band_hit else 'MISS'}), survivors "
          f"{len(survivors)}/{expected}")
    print(f"per-face survival: {json.dumps(face_summary, sort_keys=True)}")
    print(f"sec.5.1 prediction accounting: {json.dumps(pred_51)}")
    print("as-burned determinism cross-gate DUAL-SOURCE: 173/173 "
          "three-column byte-identity PASS (W17 control + W18 as-burned)")
    print(f"products: {SCREEN_FILE} + {SCREEN_CSV} "
          f"(ledger total {ledger['total']})")
    return 0


# ------------------------------------------------------ judge slice (s3)
def _dual_nulls_w19(returns, cell_idx, seed=None):
    """Dual nulls on the cell's mean daily return (prereg sec.3 s3):
    B=2000 block-20 circular bootstrap + P=2000 sign-flip, two-sided;
    W19 unc-berth seed binding [20641000, cell_idx].  Math imported
    verbatim from tl2._dual_nulls_w2 (import law)."""
    return tl2._dual_nulls_w2(returns, cell_idx,
                              seed=SEED_UNC if seed is None else seed)


def _rankdata_avg(a):
    """Average ranks with ties (tl17 verbatim reuse)."""
    return tl17._rankdata_avg(a)


def _wilcoxon_paired(diffs, face_idx, b=2000):
    """Per-face Wilcoxon signed-rank two-sided p via B=2000 sign-flip
    sampling on the |diff| ranks (prereg sec.4 paired-readout face;
    W19 unc berth: rng=[SEED_UNC, 200+face_idx] -- unc family band,
    indices above the judge-cell consumption range (<180) and below the
    declared band top 346).  Returns (p, median, iqr, n)."""
    d = np.asarray([x for x in diffs if x == x], dtype=float)
    n = len(d)
    if n < 5:
        return None, None, None, n
    ranks = _rankdata_avg(np.abs(d))
    w_obs = float(np.sum(ranks * (d > 0)))
    rng = np.random.default_rng([SEED_UNC, PAIRED_RNG_BASE + face_idx])
    signs = rng.choice([-1.0, 1.0], size=(b, n))
    w_null = (ranks[None, :] * signs).sum(axis=1)
    p_up = float((w_null >= w_obs).mean())
    p_dn = float((w_null <= w_obs).mean())
    p = 2.0 * min(p_up, p_dn)
    med = float(np.median(d))
    q1, q3 = np.percentile(d, [25, 75])
    return round(min(1.0, p), 6), round(med, 6), \
        round(float(q3 - q1), 6), n


def _judge_cell_w19(cell):
    """One W19 judged paired cell (prereg sec.3 s3 frozen face, pool
    worker): dual-leg (P-5C grid) x cost {base x1, x2=CostPatch(2)}
    full curves at the cell's timing face + window-grid beat vs passive
    + regime segments + dual nulls (W19 unc berth) + member-metrics raw
    materials (four-dim reform face, sec.4 canon)."""
    st = tl1._ST
    cand, template = cell["cand"], cell.get("template")
    face = cell["timing_face"]
    out = {"cell_id": cell["cell_id"], "candidate_id":
           cand["candidate_id"], "timing_face": face,
           "family": cand["family"], "module": cand["module"],
           "fn": cand["fn"], "block": cell["block"]}
    legs = {}
    for leg in ("L", "D"):
        prices, P, idx = (st[f"prices_{leg}"], st[f"P_{leg}"],
                          st[f"idx_{leg}"])
        fok = st[f"fundamental_ok_{leg}"]
        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \
            tz, az, mz, dz, rz, nz, rz2, cnz, mxz, rkz = \
            run_candidate_curve_w19(
                cand, template, face, prices, P, st["states"],
                st[f"atr20_{leg}"], fundamental_ok=fok,
                gate_state=st[f"gate_state_{leg}"],
                vol_state=st[f"vol_state_{leg}"],
                yang_state=st[f"yang_state_{leg}"],
                vconf_state=st[f"vconf_state_{leg}"],
                streak_state=st[f"streak_state_{leg}"],
                tstate_state=st[f"tstate_state_{leg}"],
                amp_state=st[f"amp_state_{leg}"],
                mom_state=st[f"mom_state_{leg}"],
                std_state=st[f"std_state_{leg}"],
                rsqr_state=st[f"rsqr_state_{leg}"],
                sumn_state=st[f"sumn_state_{leg}"],
                resi_state=st[f"resi_state_{leg}"],
                cnt_state=st[f"cnt_state_{leg}"],
                max_state=st[f"max_state_{leg}"],
                rank_state=st[f"rank_state_{leg}"])
        with CostPatch(2):
            eq2, _, m2, _, _, fired2, *_ = run_candidate_curve_w19(
                cand, template, face, prices, P, st["states"],
                st[f"atr20_{leg}"], fundamental_ok=fok,
                gate_state=st[f"gate_state_{leg}"],
                vol_state=st[f"vol_state_{leg}"],
                yang_state=st[f"yang_state_{leg}"],
                vconf_state=st[f"vconf_state_{leg}"],
                streak_state=st[f"streak_state_{leg}"],
                tstate_state=st[f"tstate_state_{leg}"],
                amp_state=st[f"amp_state_{leg}"],
                mom_state=st[f"mom_state_{leg}"],
                std_state=st[f"std_state_{leg}"],
                rsqr_state=st[f"rsqr_state_{leg}"],
                sumn_state=st[f"sumn_state_{leg}"],
                resi_state=st[f"resi_state_{leg}"],
                cnt_state=st[f"cnt_state_{leg}"],
                max_state=st[f"max_state_{leg}"],
                rank_state=st[f"rank_state_{leg}"])
        if len(eq) < 30 or float(eq.iloc[0]) <= 0:
            legs[leg] = {"beat": {}, "beat_x2": {}, "sharpe_full": None,
                         "sharpe_full_x2": None, "n_trades": 0,
                         "n_entries": 0, "regime_start_windows":
                         {"bear": 0, "bull": 0, "chop": 0, "na": 0},
                         "degenerate": True}
            continue
        daily = eq.pct_change().fillna(0.0)
        segs = {"bear": 0, "bull": 0, "chop": 0, "na": 0}
        s_series = st["states"].reindex(idx)
        beat, beat_x2 = {}, {}
        for wname, w in tl1.WINDOWS.items():
            starts = st["starts"][leg][wname]
            k = tot = k2 = 0
            for p in starts:
                if p + w - 1 >= len(eq):
                    continue
                tot += 1
                pret = st["passive"][leg][wname][str(p)]
                if float(eq.iloc[p + w - 1] / eq.iloc[p] - 1.0) > pret:
                    k += 1
                if float(eq2.iloc[p + w - 1] / eq2.iloc[p] - 1.0) > pret:
                    k2 += 1
                dd = s_series.iloc[p] if p < len(s_series) else None
                st_ = tl1.REGIME_MAP.get(dd, "na") if dd == dd else "na"
                segs[st_] += 1
            beat[wname] = {"k": k, "n": tot,
                           "rate": round(k / tot, 6) if tot else 0.0}
            beat_x2[wname] = {"k": k2, "n": tot,
                              "rate": round(k2 / tot, 6) if tot else 0.0}
        legs[leg] = {"beat": beat, "beat_x2": beat_x2,
                     "regime_start_windows": segs,
                     "sharpe_full": round(float(tl1.sharpe(eq)), 4),
                     "sharpe_full_x2": round(float(tl1.sharpe(eq2)), 4),
                     "n_trades": int(metrics.get("num_trades", 0)),
                     "n_entries": int(metrics.get("num_entries", 0)),
                     "degenerate": False}
        if leg == "L":
            out["legL_daily_returns"] = [round(float(x), 8)
                                         for x in daily.values]
            out["legL_sharpe_full"] = legs[leg]["sharpe_full"]
            out["legL_sharpe_full_x2"] = legs[leg]["sharpe_full_x2"]
            out["legL_n_trades"] = legs[leg]["n_trades"]
            out["legL_n_entries"] = legs[leg]["n_entries"]
            out["legL_beat6m_rate"] = legs[leg]["beat"].get(
                "6m", {}).get("rate")
            out["legL_beat12m_rate"] = legs[leg]["beat"].get(
                "12m", {}).get("rate")
            # geometric annualization of the leg-L equity curve
            # (within-batch consistent reform sub-item caliber)
            n_bars = max(2, len(eq))
            out["legL_annualized_ret"] = round(
                float((eq.iloc[-1] / eq.iloc[0]) ** (252.0 / n_bars)
                     - 1.0), 6)
            # per-regime segment Sharpe (reform robust sub-item:
            # worst-regime-segment Sharpe, reeval18 canon key)
            seg_sharpes = []
            for seg in ("bear", "bull", "chop"):
                mask = (tl1.REGIME_MAP.get(s_series.reindex(
                    eq.index).iloc[i], "na") == seg
                    for i in range(len(eq)))
                marr = np.fromiter((1.0 if x else 0.0 for x in mask),
                                   dtype=float, count=len(eq))
                if marr.sum() < 60:
                    continue
                dr = daily.values[marr > 0]
                if dr.std() > 0:
                    seg_sharpes.append(float(
                        dr.mean() / dr.std() * math.sqrt(252)))
            out["legL_regime_min_sharpe"] = (round(min(seg_sharpes), 4)
                                             if seg_sharpes else None)
            out["descriptive"] = tl2._descriptive_face(eq, eq2)
    out["legs"] = legs
    if "legL_daily_returns" not in out:
        out["legL_daily_returns"] = []
        out["legL_sharpe_full"] = None
        out["legL_sharpe_full_x2"] = None
        out["legL_n_trades"] = 0
        out["legL_n_entries"] = 0
        out["legL_beat6m_rate"] = None
        out["legL_beat12m_rate"] = None
        out["legL_annualized_ret"] = None
        out["legL_regime_min_sharpe"] = None
    r = np.asarray(out["legL_daily_returns"], dtype=float)
    out["dual_nulls"] = _dual_nulls_w19(
        r if len(r) else np.zeros(30), cell["i"])
    n_eff = sum(legs[lg]["regime_start_windows"][s]
                for lg in legs for s in ("bear", "bull", "chop"))
    out["n_eff_start_windows"] = n_eff
    out["sample_sufficient"] = bool(
        n_eff >= 500 and all(legs[lg]["regime_start_windows"][s] >= 100
                             for lg in legs
                             for s in ("bear", "bull", "chop")))
    return out


def _block_selection(screen):
    """sec.3 frozen deterministic block selection: any block with >=1
    arm surviving screen enters JUDGE with ALL 2 arms (block
    completeness law); >90 blocks -> top-90 by the block's 2-arm mean
    screen beat6m descending, ties by candidate_id lexicographic
    (pre-registered deterministic rule, never result-picked)."""
    per_block = {}
    for s in screen["survivors"]:
        cid, face = s.split("|", 1) if "|" in s else (s, None)
        per_block.setdefault(cid, set()).add(face)
    rows_by_cell = {}
    with open(SCREEN_CSV, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            rows_by_cell[(r["candidate_id"], r["timing_face"])] = r
    blocks = []
    for cid, faces in per_block.items():
        rates = []
        for f in W19_FACE_ORDER:
            rr = rows_by_cell.get((cid, f))
            if rr is not None:
                rates.append(float(rr["beat6m_rate"]))
        blocks.append({"candidate_id": cid,
                       "mean_beat6m": round(sum(rates) / len(rates), 6)
                       if rates else 0.0,
                       "n_surviving_arms": len(faces)})
    blocks.sort(key=lambda b: (-b["mean_beat6m"], b["candidate_id"]))
    capped = len(blocks) > JUDGE_CAP_BLOCKS
    if capped:
        blocks = blocks[:JUDGE_CAP_BLOCKS]
    return blocks, capped


def cmd_judge_prep() -> int:
    """Judge-prep: screen-finalize gate + T18 manifest + dual-leg
    census/member gates + per-(leg, window) starts/passive + block
    selection (sec.3 cap rule) + judge state serialization."""
    print(f"=== {WAVE} judge-prep ===")
    if not os.path.exists(SCREEN_FILE):
        print("JUDGE-PREP-GATE: screen not finalized (w19_screen.json "
              "absent) -- honest refuse (identity face)")
        return 2
    screen = json.load(open(SCREEN_FILE, encoding="utf-8"))
    if FROZEN_SHA16 and str(screen.get("grammar_sha256", ""))[:16] \
            != FROZEN_SHA16:
        print(f"JUDGE-PREP-GATE FAIL: screen grammar sha != frozen "
              f"{FROZEN_SHA16}")
        return 1
    man = json.load(open(tl1.T18_MANIFEST, encoding="utf-8"))
    if man.get("verdict") != "PASS":
        print("JUDGE-PREP-GATE FAIL: t18 manifest verdict != PASS")
        return 1
    blocks, capped = _block_selection(screen)
    if not blocks:
        print("JUDGE-PREP-GATE FAIL: zero surviving blocks (honest "
              "negative screen -- judge batch empty)")
        return 2
    starts, passive = {}, {}
    jstate = {"wave": WAVE, "prereg": PREREG,
              "evidence_cutoff": CUTOFF, **tl1.cutoff_meta(CUTOFF),
              "grammar_sha256": screen["grammar_sha256"],
              "blocks": blocks, "n_blocks": len(blocks),
              "block_cap_applied": capped, "cap": JUDGE_CAP_BLOCKS}
    reform_baseline = {}
    for leg in ("L", "D"):
        prices, P, idx, listed, cen = tl1._load_leg(leg)
        if cen != tl1.FROZEN_CENSUS[leg]:
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} census drift")
            return 1
        for member, gname in ((tl16.tl6.GATE_MEMBER, "gate"),
                              (tl16.tl6.VOL_MEMBER, "vol"),
                              (tl16.tl6.YANG_MEMBER, "yang"),
                              (tl16.tl6.VCONF_MEMBER, "vconf"),
                              (tl16.tl7.STREAK_MEMBER, "streak"),
                              (tl16.tl8.TSTATE_MEMBER, "tstate"),
                              (tl16.AMP_MEMBER, "amp"),
                              (tl16.MOM_MEMBER, "mom"),
                              (tl16.STD_MEMBER, "std"),
                              (tl16.RSQR_MEMBER, "rsqr"),
                              (tl16.SUMN_MEMBER, "sumn")):
            if member not in prices:
                print(f"JUDGE-PREP-GATE FAIL: leg-{leg} panel missing "
                      f"{gname} member {member}")
                return 1
        if leg == "L":
            # reform-baseline precompute (light face; sec.4 canon):
            # five-member EW annualized + registered-six daily returns
            five = [s for s in ("510300", "510050", "510500", "512100",
                                "588000") if s in P["close"].columns]
            cl = P["close"][five]
            ew = cl.pct_change().mean(axis=1).fillna(0.0).cumsum()
            reform_baseline["five_member_ew_ann"] = round(
                float((1.0 + ew.iloc[-1]) ** (252.0 / max(2, len(ew)))
                     - 1.0), 6)
            reform_baseline["reg_rets"] = {
                s: [round(float(x), 8)
                    for x in P["close"][s].pct_change().fillna(0.0).values]
                for s in REGISTERED_D6_SYMBOLS
                if s in P["close"].columns}
        starts[leg], passive[leg] = {}, {}
        close = P["close"]
        n = len(idx)
        for wname, w in tl1.WINDOWS.items():
            if leg == "L":
                st_ = [p for p in range(n)
                       if idx[p] >= tl1.LEG_L_FLOOR
                       and p >= tl1.WARMUP_TD
                       and p <= n - 1 - w
                       and listed.iloc[p] >= tl1.MIN_LISTED]
            else:
                # W16-caliber fix (judge-prep): FROZEN_CENSUS["D"] is the
                # eligible_without_min_listed face (p5c_grid_probe.json
                # freeze evidence) -- leg-D starts carry no MIN_LISTED
                # gate, matching trial_labor_w16 judge-prep.
                st_ = [p for p in range(n)
                       if idx[p] >= tl1.LEG_D_FLOOR
                       and p >= tl1.WARMUP_TD
                       and p <= n - 1 - w]
            if len(st_) != tl1.FROZEN_CENSUS[leg][wname]:
                print(f"JUDGE-PREP-GATE FAIL: leg-{leg} {wname} starts "
                      f"{len(st_)} != census "
                      f"{tl1.FROZEN_CENSUS[leg][wname]}")
                return 1
            pas = {}
            for p in st_:
                sdate, edate = idx[p], idx[p + w - 1]
                syms = close.columns[close.loc[sdate].notna()]
                rel = tl1.passive_rel(close, syms, sdate, edate)
                pas[str(p)] = round(float(rel.iloc[-1] - 1.0), 6)
            starts[leg][wname] = st_
            passive[leg][wname] = pas
    jstate["starts"] = starts
    jstate["passive"] = passive
    jstate["reform_baseline"] = reform_baseline
    # judged cell list: block-major, face-minor (cell_idx binding for
    # the unc seed streams; i < 2*90=180 < 346 declared band top)
    entry = {c["candidate_id"]: c for c in
             _entry_load()["candidates"]}
    a_by_trader = {t["trader_id"]: t for t in tl1.A_TEMPLATES}
    judged = []
    i = 0
    for b in blocks:
        c = entry[b["candidate_id"]]
        template = (a_by_trader.get(c.get("template_trader"))
                    if c["family"] == "A" else None)
        for f in W19_FACE_ORDER:
            judged.append({"cell_id": f"{b['candidate_id']}|{f}",
                           "candidate_id": b["candidate_id"],
                           "timing_face": f, "kind": "cand",
                           "cand": _j(c), "template":
                           _j(template) if template else None,
                           "block": b["candidate_id"], "i": i})
            i += 1
    jstate["judged_cells"] = judged
    _dump(JUDGE_STATE_FILE, jstate)
    print(f"judge-prep done: {len(blocks)} blocks (cap "
          f"{'APPLIED' if capped else 'not applied'}), "
          f"{len(judged)} judged cells -> {JUDGE_STATE_FILE}")
    return 0


def cmd_judge(shard: int, shards: int, workers) -> int:
    global _BURN_STARTED
    import datetime
    _BURN_STARTED = datetime.datetime.now().astimezone().isoformat(
        timespec="seconds")
    print(f"=== {WAVE} judge shard {shard}of{shards} ===")
    if not os.path.exists(JUDGE_STATE_FILE):
        print("JUDGE-GATE: judge_state.json absent -- run judge-prep")
        return 2
    jstate = json.load(open(JUDGE_STATE_FILE, encoding="utf-8"))
    ram_min, ram_ok = tl2._ram_gate_gb(wait_min=40)
    if not ram_ok:
        print(f"AUTOFILL-PARK: {_park_stamp()} judge RAM gate "
              f"{ram_min}GB < 4GB after bounded wait (r354/r379) -- "
              "honest zero-burn, NOT a crash (r491 park law); "
              "un-park = session flip when RAM frees", flush=True)
        print(f"JUDGE-GATE: free RAM {ram_min}GB < 4GB after bounded "
              f"wait -- honest refuse (RAM gate r354)", flush=True)
        return 2
    tl1.GRAMMAR = json.load(open(W16_GRAMMAR_FILE, encoding="utf-8"))
    # heavy worker state rebuilt live (jstate is the light metadata
    # face; W16/W17 cmd_judge caliber): legs + overlay states + starts
    # r581/crash-fix: judge workers run run_candidate_curve_w19 too (the
    # tl1.GRAMMAR["faces"][mk] lookup) -- grammar rides initargs.
    state = {"wave": WAVE, "starts": jstate["starts"],
             "grammar": tl1.GRAMMAR,
             "passive": jstate["passive"],
             "judged_cells": jstate["judged_cells"],
             "states": tl1.v3_state_series()}
    for leg in ("L", "D"):
        prices, P, idx, listed, cen = tl1._load_leg(leg)
        try:
            bl = pd.read_csv(tl1.B_LAYER_MASK)
            ok_codes = set(bl.loc[bl["ok_static"] == True,
                                  "code"].astype(str))
            overlap = sorted(s for s in P["close"].columns
                             if s in ok_codes)
        except Exception:
            overlap = []
        if overlap:
            fok = pd.DataFrame(False, index=P["close"].index,
                               columns=P["close"].columns)
            for s in overlap:
                fok[s] = True
        else:
            fok = None
        state[f"prices_{leg}"] = prices
        state[f"P_{leg}"] = P
        state[f"idx_{leg}"] = idx
        state[f"fundamental_ok_{leg}"] = fok
        state[f"gate_state_{leg}"] = tl16.tl3.gate_state_series(prices)
        state[f"vol_state_{leg}"] = tl16.tl4.vol_state_series(prices)
        state[f"yang_state_{leg}"] = tl16.tl5.yang_state_series(prices)
        state[f"vconf_state_{leg}"] = tl16.tl6.vconf_state_series(prices)
        state[f"streak_state_{leg}"] = tl16.tl7.streak_state_series(prices)
        state[f"tstate_state_{leg}"] = tl16.tl8.tstate_state_series(prices)
        state[f"amp_state_{leg}"] = tl16.amp_state_series(prices)
        state[f"mom_state_{leg}"] = tl16.mom_state_series(prices)
        state[f"std_state_{leg}"] = tl16.std_state_series(prices)
        state[f"rsqr_state_{leg}"] = tl16.rsqr_state_series(prices)
        state[f"sumn_state_{leg}"] = tl16.sumn_state_series(prices)
        state[f"resi_state_{leg}"] = tl16.resi_state_series(prices)
        state[f"cnt_state_{leg}"] = tl16.cnt_state_series(prices)
        state[f"max_state_{leg}"] = tl16.max_state_series(prices)
        state[f"rank_state_{leg}"] = tl16.rank_state_series(prices)
        state[f"atr20_{leg}"] = tl2.atr20_series(prices)
    mine = [c for i, c in enumerate(jstate["judged_cells"])
            if i % shards == shard]
    ck = os.path.join(CKPT_DIR, f"judge_shard_{shard}of{shards}.jsonl")
    os.makedirs(CKPT_DIR, exist_ok=True)
    done = set()
    if os.path.exists(ck):
        with open(ck, encoding="utf-8") as fh:
            for ln in fh:
                try:
                    done.add(json.loads(ln)["cell_id"])
                except Exception:
                    pass
    todo = [c for c in mine if c["cell_id"] not in done]
    print(f"shard cells {len(mine)}, done {len(done)}, todo {len(todo)}")

    def on_result(key, payload):
        os.makedirs(CKPT_DIR, exist_ok=True)
        with open(ck, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(tl1._j(payload), ensure_ascii=False,
                                default=float) + "\n")

    if todo:
        jobs = [(c["cell_id"], _judge_cell_w19, (c,)) for c in todo]
        tl1.run_cells_parallel(jobs, workers=workers or tl1.worker_cap(),
                              desc="judge cells",
                              initializer=tl1._init_worker,
                              initargs=(state,), on_result=on_result)
    print(f"judge shard {shard}of{shards} complete -> {ck}")
    _worker_claim("TRIAL-LABOR-W19-JUDGE",
                  f"w19-judge-{shard}of{shards}",
                  os.path.relpath(ck, os.path.dirname(os.path.dirname(
                      os.path.abspath(__file__)))))
    return 0


def _paired_deltas_w19(judged, jstate):
    """Paired-delta face (prereg sec.4, this batch's own design):
    per-face f, delta_f(cell) = legL_sharpe(cell@f) - legL_sharpe(
    cell@as-burned) over judged blocks; Wilcoxon signed-rank two-sided
    B=2000 on INFORMATIVE pairs only (cell-as-burned(f) subgroup
    excluded -- delta==0 by construction, degenerate-pairs exclusion
    law); + the 2-as-burned-T-subgroup secondary readings (the
    direction-asymmetry face: daily_asburned subgroup n<=128 with
    treatment=weekly [thinning direction] / weekly_asburned subgroup
    n<=45 with treatment=daily [thickening direction] = the
    granularity-migration asymmetry evidence, batch-unique deliverable
    w19_paired_deltas.json) + the full-cell degenerate census
    disclosure (live entry read, never hand-copied)."""
    as_burned = {c["candidate_id"]: c["cand"]["axis"][3]
                 for c in jstate["judged_cells"]}
    census = {}
    for c in _entry_load()["candidates"]:
        census[c["axis"][3]] = census.get(c["axis"][3], 0) + 1
    sharpe_by = {(r["candidate_id"], r["timing_face"]):
                 r.get("legL_sharpe_full") for r in judged}
    paired = {}
    for f_idx, f in enumerate(W19_FACE_ORDER):
        diffs, subgroups = [], {}
        degenerate = 0
        missing = 0
        for b in jstate["blocks"]:
            cid = b["candidate_id"]
            g = as_burned[cid]
            a = sharpe_by.get((cid, f))
            c = sharpe_by.get((cid, g))
            if a is None or c is None:
                missing += 1
                continue
            if g == f:
                degenerate += 1   # constructed delta==0, excluded
                continue
            d = a - c
            diffs.append(d)
            subgroups.setdefault(g, []).append(d)
        p, med, iqr, n = _wilcoxon_paired(diffs, f_idx)
        paired[f] = {"n_pairs_informative": n,
                     "n_degenerate_excluded": degenerate,
                     "n_missing_reading": missing,
                     "median_delta": med, "iqr": iqr,
                     "wilcoxon_p": p,
                     "rng": [SEED_UNC, PAIRED_RNG_BASE + f_idx],
                     "as_burned_subgroup_deltas": {
                         g: {"n": len(v),
                             "median": round(float(np.median(v)), 6),
                             "iqr": round(float(
                                 np.percentile(v, 75)
                                 - np.percentile(v, 25)), 6)}
                         for g, v in sorted(subgroups.items())}}
    return paired, census


def cmd_judge_finalize() -> int:
    """Judge-finalize: G1'v2 + G2-v2 verdicts + M1 t-face + family PBO
    + the REFORM FACE BLOCK (member_metrics four-dim + dual-nulls +
    g2_reform_fdr4d + D6 + top-3 -- W16 sec.8 gap lesson, prereg sec.4
    mandated) + paired-delta informative-pairs + 2-as-burned-T-subgroup
    face (sec.4, batch-unique w19_paired_deltas.json) + E[FP]
    disclosure + ledger append + products."""
    print(f"=== {WAVE} judge-finalize ===")
    landed = tl16.tl6.finalize_already_landed(JUDGE_BATCH, JUDGE_FILE)
    if landed is not None:
        print(f"finalize: already landed (ledger total "
              f"{landed['total']}) -- idempotent no-op")
        return 0
    for p, what in ((JUDGE_STATE_FILE, "judge_state.json"),):
        if not os.path.exists(p):
            print(f"FINALIZE-GATE: {what} absent -- honest refuse "
                  "(identity face: judge prep/burn pending)")
            return 2
    jstate = json.load(open(JUDGE_STATE_FILE, encoding="utf-8"))
    rows = []
    for f in sorted(os.listdir(CKPT_DIR)):
        if f.startswith("judge_shard_") and f.endswith(".jsonl"):
            with open(os.path.join(CKPT_DIR, f), encoding="utf-8") as fh:
                for ln in fh:
                    try:
                        rows.append(json.loads(ln))
                    except Exception:
                        pass
    expected = len(jstate["judged_cells"])
    if len(rows) != expected:
        print(f"FINALIZE-GATE: incomplete checkpoint ({len(rows)}/"
              f"{expected}) -- honest refuse (judge burn pending)")
        return 2
    by_id = {r["cell_id"]: r for r in rows}
    judged = [by_id[c["cell_id"]] for c in jstate["judged_cells"]]
    n_judged = len(judged)
    batch_cells = n_judged
    prev = tl1.ledger_head()
    n_trials = prev["total"]   # screen already landed in the chain
    e_fp = round(0.05 * n_judged, 2)
    # -- per-cell verdicts (G1'v2 + DSR + M1 t-face)
    for r in judged:
        rets = r.get("legL_daily_returns") or []
        # zero-variance face (batch-unique: weekly_grid treatment arm
        # with 0 entries -- prereg sec.5.5 "trade gate" branch): DSR is
        # UNDEFINED on constant returns (frozen lib raises); G1 keeps
        # the frozen entries>=30 trade-gate refuse, t-face stays
        # recorded, G2 refuses on the missing DSR input -- never waved
        # through
        r["zero_variance"] = bool(rets) and len(set(
            float(x) for x in rets)) == 1
        if r["legs"].get("L", {}).get("degenerate") or not rets:
            r["dsr"] = None
            r["g1_pass"] = False
            r["verdict"] = "fail-degenerate"
            r["t_face"] = None
            continue
        g1 = tl1.g1_prime_v2(r["legL_sharpe_full"], rets, batch_cells,
                             pool="core48", n_trades=r["legL_n_trades"],
                             n_entries=r["legL_n_entries"])
        if r["zero_variance"]:
            r["g1_prime_v2"] = g1
            r["dsr"] = None
        else:
            dsr = tl1.deflated_sharpe_ratio(rets, n_trials=n_trials)
            r["g1_prime_v2"] = g1
            r["dsr"] = {"dsr": round(float(dsr["dsr"]), 6),
                        "n_trials": n_trials}
        r["g1_pass"] = g1["pass_v2"]
        r["verdict"] = ("pass" if (g1["pass_v2"] and r["sample_sufficient"])
                        else "insufficient-sample" if not r[
                            "sample_sufficient"] else "fail")
        # M1 t-face law (prereg sec.4): derivation lives in
        # science_gates (frozen import)
        t_stat = science_gates.t_from_sharpe(r["legL_sharpe_full"], len(rets))
        r["t_face"] = science_gates.m1_t_value_gate(t_stat)
    # -- family PBO (CSCV 8 blocks; family = strategy module; <8 n/a)
    fam_map = {}
    for r in judged:
        fam_map.setdefault(r.get("module"), []).append(r)
    pbos = {}
    for fam, rs in fam_map.items():
        series = {r["cell_id"]: pd.Series(r["legL_daily_returns"])
                  for r in rs if r.get("legL_daily_returns")}
        if len(rs) < 8 or len(series) < 8:
            pbos[fam] = {"pbo": None, "n_cells": len(rs),
                         "note": "insufficient (<8) -- G2 cannot pass"}
            for r in rs:
                r["family_pbo"] = None
            continue
        mat = tl1.align_returns(series)
        pbo = tl1.cscv_pbo(mat)
        pbos[fam] = {"pbo": round(float(pbo["pbo"]) if isinstance(
            pbo, dict) else float(pbo), 4), "n_cells": len(rs)}
        for r in rs:
            r["family_pbo"] = pbos[fam]["pbo"]
    # -- G2 registration columns (historical caliber, sec.4(b))
    for r in judged:
        if r.get("g1_prime_v2") is None or r.get("dsr") is None:
            r["g2_registration_v2"] = None
            continue
        r["g2_registration_v2"] = tl1.g2_registration_v2(
            r["g1_pass"], r["dsr"], r.get("family_pbo"))
    # -- REFORM FACE BLOCK (sec.4(a) canon; W16 sec.8 gap lesson)
    rb = jstate.get("reform_baseline", {})
    base_ann = rb.get("five_member_ew_ann")
    reg_rets = {}
    for s, vals in (rb.get("reg_rets") or {}).items():
        if vals:
            reg_rets[s] = pd.Series(vals)
    member_metrics, batch_p, cand_rets = {}, {}, {}
    for r in judged:
        # zero-variance arm (0 entries) has no reform candidacy: the
        # four-dim composite is undefined on a never-traded arm --
        # excluded from the reform face, fully disclosed in the product
        if (r["legs"].get("L", {}).get("degenerate")
                or r.get("zero_variance")):
            continue
        mm = {
            "ret": {"sharpe_full_L": r["legL_sharpe_full"],
                    "annualized_ret_L": r["legL_annualized_ret"],
                    "return_ceiling_O1126": (
                        None if base_ann is None
                        else round(r["legL_annualized_ret"] - base_ann,
                                   6)),
                    "beat6m_rate_L": r["legL_beat6m_rate"],
                    "beat12m_rate_L": r["legL_beat12m_rate"]},
            "robust": {"cost_x2_sharpe_L": r["legL_sharpe_full_x2"],
                       "regime_min_sharpe_L": r[
                           "legL_regime_min_sharpe"],
                       "bootstrap_ci_low_L": r["dual_nulls"]
                       ["bootstrap_ci"][0]},
            "anti_overfit": {"family_pbo": r.get("family_pbo"),
                             "d6_max_abs_corr": None},
            "anti_luck": {"batch_dsr": (r["dsr"] or {}).get("dsr")},
        }
        member_metrics[r["cell_id"]] = mm
        batch_p[r["cell_id"]] = r["dual_nulls"]["signflip_p"]
        if r.get("legL_daily_returns"):
            cand_rets[r["cell_id"]] = pd.Series(
                r["legL_daily_returns"]).round(8)
    dsr_by_id = {cid: member_metrics[cid]["anti_luck"]["batch_dsr"]
                 for cid in member_metrics}
    eligible_pool = [cid for cid in member_metrics
                     if cid in cand_rets]
    admitted, rejected, d6 = tl2._d6_admit_core(
        sorted(eligible_pool), cand_rets, reg_rets, dsr_by_id)
    for cid, d in d6.items():
        member_metrics[cid]["anti_overfit"]["d6_max_abs_corr"] = \
            d["max_corr_vs_registered"]
    g2 = g2_reform_fdr4d(member_metrics, REFORM_DIM_WEIGHTS,
                         REFORM_SUB_WEIGHTS, batch_p, q=REFORM_Q_LEVEL)
    if g2.get("error"):
        print(f"FINALIZE-GATE FAIL: reform gate error {g2['error']}")
        return 2
    eligible_reform = [cid for cid, m in g2["members"].items()
                       if m["eligible_reform"] and cid in admitted]
    # L4 top-N per wave (one wave here) by composite, ties by cell_id
    eligible_reform.sort(key=lambda c: (
        -(g2["members"][c]["composite"] or 0.0), c))
    onboard = eligible_reform[:REFORM_TOPN_PER_WAVE]
    reform_prod = {"wave": WAVE, "stage": "reform-face",
                   "evidence_cutoff": CUTOFF,
                   **tl1.cutoff_meta(CUTOFF),
                   "member_metrics": _j(member_metrics),
                   "batch_p_values": batch_p,
                   "g2_reform": _j(g2),
                   "d6": {"admitted": admitted, "rejected": rejected},
                   "eligible_reform": eligible_reform,
                   "top_n_per_wave": REFORM_TOPN_PER_WAVE,
                   "onboard_list": [{"cell_id": c,
                                     "composite":
                                     g2["members"][c]["composite"]}
                                    for c in onboard],
                   "five_member_ew_baseline_ann": base_ann,
                   "zero_variance_arms_excluded": sorted(
                       [r["cell_id"] for r in judged
                        if r.get("zero_variance")]),
                   "constants": {"dim_weights": REFORM_DIM_WEIGHTS,
                                 "sub_weights": REFORM_SUB_WEIGHTS,
                                 "q": REFORM_Q_LEVEL,
                                 "topn": REFORM_TOPN_PER_WAVE,
                                 "ceiling_baseline":
                                 "five_member_ew (O-1555 five)"}}
    _dump(REFORM_FILE, reform_prod)
    # -- paired-delta face (sec.4, this batch's own design:
    # informative-pairs exclusion + 2 as-burned-T-subgroup readings)
    paired, degenerate_census = _paired_deltas_w19(judged, jstate)
    paired_prod = {"wave": WAVE, "stage": "paired-deltas",
                   "evidence_cutoff": CUTOFF,
                   **tl1.cutoff_meta(CUTOFF),
                   "reading": "legL_sharpe_full (face-vs-as-burned "
                              "leg-L Sharpe paired deltas across "
                              "complete blocks)",
                   "per_face": paired,
                   "degenerate_census_full_173": degenerate_census,
                   "exclusion_law": "informative pairs only per face f: "
                                    "the cell-as-burned(f) subgroup is "
                                    "excluded (constructed delta==0, "
                                    "zero information; prereg sec.4 "
                                    "frozen) -- degenerate pairs fully "
                                    "disclosed, retained for block-"
                                    "completeness + determinism-anchor "
                                    "dual duty",
                   "rng_streams": "unc family band rng([20641000,"
                                  "200+f]) f<2 (above judge "
                                  "consumption <180, below band top "
                                  "346)"}
    _dump(PAIRED_FILE, paired_prod)
    ledger = tl1.append_ledger(JUDGE_BATCH, n_judged,
                              "results/trial_labor_w19/w19_judge.json",
                              evidence_cutoff=CUTOFF)
    eligible_v2 = [r["cell_id"] for r in judged
                   if (r.get("g2_registration_v2") or {}).get(
                       "eligible_v2")]
    prod = {"wave": WAVE, "stage": "judge-finalize", "prereg": PREREG,
            "evidence_cutoff": CUTOFF, **tl1.cutoff_meta(CUTOFF),
            "grammar_sha256": jstate["grammar_sha256"],
            "n_blocks": jstate["n_blocks"],
            "block_cap_applied": jstate["block_cap_applied"],
            "n_judged": n_judged, "E_FP_nominal": e_fp,
            "g1_pass_n": sum(1 for r in judged if r.get("g1_pass")),
            "eligible_v2": eligible_v2,
            "eligible_reform": eligible_reform,
            "onboard_list": reform_prod["onboard_list"],
            "family_pbo": pbos,
            "verdicts": {r["cell_id"]: r["verdict"] for r in judged},
            "cells": _j(judged),
            "trials_ledger": ledger}
    _dump(JUDGE_FILE, prod)
    paired_p_summary = {f: paired[f]["wilcoxon_p"] for f in paired}
    print(f"judge-finalize done: {n_judged} cells, G1 "
          f"{prod['g1_pass_n']}, G2-v2 {len(eligible_v2)}, "
          f"eligible_reform {len(eligible_reform)}, onboard "
          f"{len(onboard)}; E[FP]={e_fp}")
    print(f"paired deltas: {json.dumps(paired_p_summary, sort_keys=True)}")
    print(f"products: {JUDGE_FILE} + {REFORM_FILE} + {PAIRED_FILE} "
          f"(ledger total {ledger['total']})")
    return 0


def cmd_intake() -> int:
    """s4 intake (prereg sec.6): D6 binding gate face -- eligible_reform
    -> TRIAL-TIMINGAXIS-* paper-probation listing (registration itself =
    separate GM face per law); lawful-zero when none."""
    print(f"=== {WAVE} intake ===")
    if not os.path.exists(REFORM_FILE):
        print("INTAKE-GATE: w19_reform_face.json absent -- judge "
              "finalize pending")
        return 2
    reform = json.load(open(REFORM_FILE, encoding="utf-8"))
    onboard = reform.get("onboard_list", [])
    prod = {"wave": WAVE, "stage": "intake",
            "evidence_cutoff": CUTOFF, **tl1.cutoff_meta(CUTOFF),
            "n_eligible": len(onboard),
            "accounts": [{"name": f"TRIAL-TIMINGAXIS-{i+1:02d}",
                          "cell_id": o["cell_id"],
                          "composite": o["composite"]}
                         for i, o in enumerate(onboard)],
            "lawful_zero": len(onboard) == 0,
            "note": "registration + paper-probation onboarding = "
                    "separate GM slice (D6 binding gate -> "
                    "STRATEGY_LIBRARY row); marks non-trial ledger +0"}
    _dump(INTAKE_FILE, prod)
    print(f"intake done: n_eligible {len(onboard)} "
          f"({'lawful-zero' if not onboard else 'listing'}) -> "
          f"{INTAKE_FILE}")
    return 0


# ------------------------------------------------------------ selftest (hermetic)
def cmd_selftest() -> int:
    """Hermetic selftest (zero panel load, zero network, zero engine
    burn; synthetic fixtures only).  The real-data identity faces run
    via the three-command first-run law (screen-prep / screen-finalize
    / judge-prep)."""
    import tempfile
    ok_n = 0
    fails = []

    def ok(name, cond, detail=""):
        nonlocal ok_n
        if cond:
            ok_n += 1
            print(f"[PASS] {name}")
        else:
            fails.append(name)
            print(f"[FAIL] {name} {detail}")

    # L1: GBK entry law (r236)
    ok("L1 gbk-reconfigure entry law",
       (sys.stdout.encoding or "").lower() == "utf-8")
    # L2: A9 ExitConfig default table == frozen prereg values (live
    # import, read-only; engine drift face; X=template_default consumed)
    ok("L2 exitcfg defaults == A9 frozen table", *_exitcfg_gate())
    # L3: timing face bite on the tl1 verbatim path (synthetic panel;
    # prereg sec.3 table -- ZERO new timing code, the runner only
    # re-routes axis[3]; daily_signal = mask verbatim, weekly_grid =
    # mask AND ISO-week-first-trading-day gate)
    idx = pd.date_range("2020-01-01", periods=80, freq="B")
    mask = pd.DataFrame({"SYM": [(i % 3) == 0
                                 for i in range(80)]},
                        index=idx)   # engine-mask bool dtype caliber
    daily = tl1.apply_timing(mask, "daily_signal")
    weekly = tl1.apply_timing(mask, "weekly_grid")
    iso = idx.isocalendar()
    first_of_week = ((iso.week != iso.week.shift(1))
                    | (iso.year != iso.year.shift(1))).values
    ok("L3a daily_signal mask verbatim",
       daily.equals(mask))
    ok("L3b weekly_grid week-first gate subset",
       weekly.equals(mask
                     & pd.DataFrame(np.tile(
                         first_of_week[:, None], (1, mask.shape[1])),
                         index=idx, columns=mask.columns))
       and int((mask > 0).sum().sum()) > int((weekly > 0).sum().sum()))
    # L4: as-burned byte-path identity vs the W17 control arm AND the
    # W18 as-burned arm (the 173-pair dual-source determinism
    # cross-gate premise, synthetic A/B cands -- three-wave chain)
    cand_b = {"axis": ["liquidity", "ce_machine", "cap20",
                       "weekly_grid"] + ["none"] * 16}
    r19 = w19_engine_params(cand_b, None, "weekly_grid")
    r17 = tl17.w17_engine_params(cand_b, None, "template_default")
    r18 = tl18.w18_engine_params(cand_b, None, "cap20")
    ok("L4a B-family as-burned == W17 control == W18 as-burned",
       r19 == r17 == r18 == ({}, None))
    cand_a = {"axis": ["liquidity", "time_stop_10d", "equal_weight",
                       "daily_signal"] + ["none"] * 16}
    tmpl = {"registered_params": {"position_size_pct": 0.12,
                                   "max_positions": 4,
                                   "take_profit_levels": [0.04]},
            "registered_ovr": {"loss_time_days": 6}}
    r19a = w19_engine_params(cand_a, tmpl, "daily_signal")
    r17a = tl17.w17_engine_params(cand_a, tmpl, "template_default")
    r18a = tl18.w18_engine_params(cand_a, tmpl, "equal_weight")
    ok("L4b A-family as-burned == W17 control == W18 as-burned",
       r19a == r17a == r18a
       and r19a[0].get("position_size_pct") == 0.12
       and r19a[1] == {"loss_time_days": 6})
    r19t = w19_engine_params(cand_a, tmpl, "weekly_grid")
    ok("L4c A-family treatment timing face byte-path (S untouched)",
       r19t == tl17.w17_engine_params(
           {"axis": ["liquidity", "time_stop_10d", "equal_weight",
                     "weekly_grid"] + ["none"] * 16}, tmpl,
           "template_default")
       and r19t[0].get("position_size_pct") == 0.12)
    # L5: null draw determinism + face vocabulary + X consumed fixed
    p1, ax1, r1 = _null_axis_draw_w19(7)
    p2, ax2, r2 = _null_axis_draw_w19(7)
    p3, ax3, r3 = _null_axis_draw_w19(8)
    ok("L5 null draw determinism + 2-face vocab + X fixed",
       p1 == p2 and ax1 == ax2 and (p1, ax1) != (p3, ax3)
       and ax1[1] == X_CONSUMED and ax1[3] in W19_FACE_ORDER
       and ax1[2] in tuple(tl1.AXIS_SIZING)
       and len(ax1) == 20 and (r1.random() != r3.random()))
    # L6: grammar serialization determinism + anchor constants
    g1s, g2s = build_grammar_w19(), build_grammar_w19()
    ok("L6 grammar deterministic + lineage anchors",
       g1s["grammar_sha256"] == g2s["grammar_sha256"]
       and g1s["entry_source"]["sha256_16"] == ENTRY_SHA16
       and g1s["w14_lineage"]["grammar_sha16"] == W14_GRAMMAR_SHA16
       and g1s["w16_grammar_ref"]["grammar_sha16"]
       == W16_GRAMMAR_SHA16
       and g1s["w17_grammar_ref"]["grammar_sha16"]
       == W17_GRAMMAR_SHA16
       and g1s["w18_grammar_ref"]["grammar_sha16"]
       == W18_GRAMMAR_SHA16
       and g1s["n_pairs"] == 346
       and g1s["screen_trials"] == 546
       and g1s["entry_source"]["axis3_timing_census"]
       == {"daily_signal": 128, "weekly_grid": 45})
    # L6b: FROZEN pin check (Slice-B face)
    if FROZEN_SHA16:
        ok("L6b frozen sha pin == built grammar",
           g1s["grammar_sha256"][:16] == FROZEN_SHA16)
    else:
        ok_n += 1
        print("[PASS] L6b frozen pin not yet set (pre-generate face)")
    # L7: block-cap deterministic rule (synthetic screen, 4-face arms)
    fake_blocks = [{"candidate_id": f"C{i:03d}",
                    "mean_beat6m": 0.5 + (i % 7) * 0.01,
                    "n_surviving_arms": 1} for i in range(93)]
    fake_blocks.sort(key=lambda b: (-b["mean_beat6m"],
                                    b["candidate_id"]))
    capped = fake_blocks[:JUDGE_CAP_BLOCKS]
    ok("L7 block cap 90 deterministic",
       len(capped) == 90 and capped == sorted(
           capped, key=lambda b: (-b["mean_beat6m"],
                                  b["candidate_id"])))
    # L8: Wilcoxon paired face -- determinism + signal ordering
    rng = np.random.default_rng(11)
    strong = list(0.01 + 0.02 * rng.random(60))
    noise = list((rng.random(60) - 0.5) * 0.002)
    p_s, m_s, iqr_s, n_s = _wilcoxon_paired(strong, 1)
    p_s2, _, _, _ = _wilcoxon_paired(strong, 1)
    p_n, _, _, n_n = _wilcoxon_paired(noise, 2)
    ok("L8 wilcoxon determinism + signal ordering",
       p_s == p_s2 and p_s < 0.05 and p_s < p_n and n_s == 60
       and n_n == 60 and m_s > 0)
    # L8b: informative-pairs exclusion law (degenerate delta==0
    # subgroup excluded per face; constructed-identity pairs must never
    # enter the Wilcoxon -- the median face is the hard proof: 30
    # appended zeros pull the batch median to exactly 0.0, the exact
    # distortion the exclusion law exists to prevent)
    rngd = np.random.default_rng(13)
    informative = list(0.02 * (rngd.random(30) - 0.5))
    with_degen = informative + [0.0] * 30
    p_inf, m_inf, _, n_inf = _wilcoxon_paired(informative, 3)
    p_all, m_all, _, n_all = _wilcoxon_paired(with_degen, 3)
    ok("L8b informative-pairs exclusion law (median distortion proof)",
       n_inf == 30 and n_all == 60 and p_inf is not None
       and p_all is not None and p_inf != p_all
       and m_inf != 0.0 and m_all == 0.0)
    # L9: reform constants import integrity (禁手抄律)
    ok("L9 reform constants integrity",
       reform_weight_freeze_integrity()
       and abs(sum(REFORM_DIM_WEIGHTS.values()) - 1.0) < 1e-9
       and REFORM_TOPN_PER_WAVE == 3 and REFORM_Q_LEVEL == 0.10
       and set(REFORM_DIM_WEIGHTS) == {"ret", "robust",
                                       "anti_overfit", "anti_luck"})
    # L10: g2_reform_fdr4d joint verdict on a synthetic batch
    mm = {f"C{i}": {"ret": {"sharpe_full_L": 1.0 + i * 0.1,
                            "annualized_ret_L": 0.1,
                            "return_ceiling_O1126": 0.01,
                            "beat6m_rate_L": 0.6,
                            "beat12m_rate_L": 0.55},
                    "robust": {"cost_x2_sharpe_L": 0.8,
                               "regime_min_sharpe_L": 0.3,
                               "bootstrap_ci_low_L": 0.001},
                    "anti_overfit": {"family_pbo": 0.1,
                                     "d6_max_abs_corr": 0.2},
                    "anti_luck": {"batch_dsr": 0.9}}
          for i in range(10)}
    bp = {f"C{i}": (0.001 if i < 2 else 0.5) for i in range(10)}
    g2t = g2_reform_fdr4d(mm, REFORM_DIM_WEIGHTS, REFORM_SUB_WEIGHTS,
                          bp, q=REFORM_Q_LEVEL)
    ok("L10 g2_reform_fdr4d synthetic joint verdict",
       not g2t.get("error") and g2t["members"]["C0"]["fdr_pass"]
       and not g2t["members"]["C5"]["fdr_pass"]
       and g2t["members"]["C0"]["composite"] is not None)
    # L11: dual-nulls W19 unc berth binding (determinism)
    r = np.random.default_rng(3).normal(0.0005, 0.01, 300)
    d1 = _dual_nulls_w19(r, 5)
    d2 = _dual_nulls_w19(r, 5)
    ok("L11 dual-nulls unc-berth determinism",
       d1 == d2 and d1["B"] == 2000 and d1["P"] == 2000
       and len(d1["bootstrap_ci"]) == 2)
    # L12: exclusion matcher (face-at-axis-3 + X-consumed-at-axis-1
    # semantics) + cross-gate 3-column comparator
    rows = [{"module": "m", "fn": "f", "sig_params": {"w": 1},
             "axis": ["liquidity", "template_default", "cap20",
                      "weekly_grid"] + ["none"] * 16,
             "face": "w17_burned_cell"}]
    cand_x = {"module": "m", "fn": "f", "sig_params": {"w": 1},
              "axis": ["liquidity", "ce_machine", "cap20",
                       "weekly_grid"] + ["none"] * 16}
    ok("L12 exclusion matcher (face-at-axis-3 semantics)",
       _excluded_w19(cand_x, "weekly_grid", rows) == "w17_burned_cell"
       and _excluded_w19(cand_x, "daily_signal", rows) is None)
    mine_rows = {"W16-B-0001": {k: 1 for k in _XGATE_KEYS}}
    ref_rows = {"W16-B-0001": {k: "1" for k in _XGATE_KEYS}}
    n_c, mism = _control_determinism_gate(mine_rows, ref_rows)
    ok("L12b cross-gate three-column byte-identity comparator",
       n_c == 1 and not mism)
    mine_rows["W16-B-0001"]["binom_z"] = 0.9
    n_c2, mism2 = _control_determinism_gate(mine_rows, ref_rows)
    ok("L12c cross-gate catches drift", n_c2 == 1
       and len(mism2) == 1 and mism2[0]["key"] == "binom_z")
    # L13: five-member/registered constants sanity
    ok("L13 registered D6 roster frozen",
       len(REGISTERED_D6_SYMBOLS) == 6 and "510300"
       in REGISTERED_D6_SYMBOLS)
    # L14: products writer idempotence + timing identity gate
    with tempfile.TemporaryDirectory() as td:
        fp = os.path.join(td, "x.json")
        _dump(fp, {"a": 1})
        _dump(fp, {"a": 1})
        ok("L14 dump idempotent + ascii-safe",
           json.load(open(fp, encoding="utf-8")) == {"a": 1})
    ok("L14b timing 2-tuple identity (G-TIMING)",
       *_timing_identity_gate())
    print(f"selftest: {ok_n} PASS, {len(fails)} FAIL"
          f"{'' if not fails else ' -- ' + ', '.join(fails)}")
    return 0 if not fails else 1


# ------------------------------------------------------------------ argparse
def _build_parser():
    p = argparse.ArgumentParser(description=WAVE + " runner "
                               "(timing-axis complete-block paired "
                               "isolation; frozen prereg "
                               + PREREG + ")")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("grammar", help="serialize w19_grammar.json")
    sub.add_parser("generate", help="173 x 2 cross expansion + "
                   "exclusion book + w19_cells.json + ledger row")
    sub.add_parser("status", help="product presence + A9/TIMING gates")
    sub.add_parser("screen-prep", help="fail-closed gates + passive 6m")
    sp = sub.add_parser("screen", help="screen shard burn")
    sp.add_argument("shard", type=int)
    sp.add_argument("shards", type=int)
    sp.add_argument("--workers", type=int, default=None)
    sub.add_parser("screen-finalize", help="survival line + G-face "
                   "battery + ledger append")
    sub.add_parser("judge-prep", help="blocks + dual-leg judge state")
    jp = sub.add_parser("judge", help="judge shard burn")
    jp.add_argument("shard", type=int)
    jp.add_argument("shards", type=int)
    jp.add_argument("--workers", type=int, default=None)
    sub.add_parser("judge-finalize", help="verdicts + reform face + "
                   "paired deltas + ledger append")
    sub.add_parser("intake", help="s4 intake face")
    sub.add_parser("selftest", help="hermetic selftest")
    return p


def main(argv=None):
    args = _build_parser().parse_args(argv)
    return {"grammar": cmd_grammar, "generate": cmd_generate,
            "status": cmd_status, "screen-prep": cmd_screen_prep,
            "screen": lambda: cmd_screen(args.shard, args.shards,
                                         args.workers),
            "screen-finalize": cmd_screen_finalize,
            "judge-prep": cmd_judge_prep,
            "judge": lambda: cmd_judge(args.shard, args.shards,
                                       args.workers),
            "judge-finalize": cmd_judge_finalize,
            "intake": cmd_intake,
            "selftest": cmd_selftest}[args.cmd]()


if __name__ == "__main__":
    raise SystemExit(main())
