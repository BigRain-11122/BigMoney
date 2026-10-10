"""TRIAL_LABOR_W17 runner -- wave-17 exit-axis complete-block PAIRED
isolation burn machinery (frozen prereg research/TRIAL_LABOR_W17_PREREG.md,
bm-c r788 freeze commit lineage; this build window = r789, funnel 4/5).

Design (prereg sec.3, FROZEN): 173 W16 frozen candidate cells (entry
source results/trial_labor_w16/w16_candidates.json, sha256_16
22179881b7537193, n=173, A=6/B=167) x 8 exit faces = 1,384 paired
cells + K=200 face-mixed nulls = 1,584 screen trials.  ZERO new entry
generation (W17 gen seed 20610000 held, zero consumption); the exit
face is the ONLY variable (complete-block paired design -- same entry
mask shared by all 8 arms per block = the paired-control design body;
T-84s3 fingerprint dedup is FORBIDDEN across exit arms per prereg
sec.3, it would collapse the pairing to 173).

Exit faces (prereg sec.3 table, engine-default verbatim + W1
never-true idiom, ZERO engine edit; iron law: engine/exit_rules.py
priority + T+1/cost model untouched):
  control   template_default  {} bridged / {} patch (X-axis semantics:
                   A-family -> registered exit face via
                   tl1.candidate_engine_params; B-family -> engine
                   default P1-P6 full stack -- the tested baseline,
                   prereg sec.3 arm-3)
  tiered_tp_only / hard_stop_only / trailing_only / time_decay_only /
  loss_time_only / hard_limit_only / hold_to_end -- single-rule
  isolation faces, frozen bridged(run_backtest kwargs) + patch
  (ExitPatch fields) per the sec.3 table.

Lineage (import-face reuse law): W17 re-derives ZERO entry/overlay/
curve/null/judge machinery -- tl16 imports tl1..tl14 + a158 verbatim
and W17 imports tl16; the ONLY new faces are the exit-face layer,
paired-block bookkeeping, the reform face block (member_metrics 4-dim
+ dual-nulls + g2_reform_fdr4d + top-3, REFORM constants import --
W16 sec.8 gap lesson prereg-sec.9 mandated), the paired-delta
Wilcoxon face (prereg sec.4) and the G-face assertion battery
(control-arm determinism cross-gate = the 25 same-face W16 pairs
byte-identity, prereg sec.3 rerun-face clause + sec.5.1 count
prediction accounting; ExitConfig default table = A9; entry source
sha; grammar lineage three-face identity = A4).

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
import science_gates           # M1 t-face: t_from_sharpe + m1_t_value_gate (frozen law import)
import trial_labor_w2 as tl2   # survival math + dual-nulls + D6 core
import trial_labor_w16 as tl16  # W16 runner: overlay states, exclusion
                                # book loader, curve-caliber lineage
from science_gates import (CostPatch, SEED_REGISTRY,  # noqa: E402
                           REFORM_DIM_WEIGHTS, REFORM_SUB_WEIGHTS,
                           REFORM_TOPN_PER_WAVE, REFORM_Q_LEVEL,
                           reform_weight_freeze_integrity,
                           g2_reform_fdr4d)

# ------------------------------------------------------------- frozen (prereg)
WAVE = "TRIAL_LABOR_W17"
PREREG = "research/TRIAL_LABOR_W17_PREREG.md"
CUTOFF = tl1.CUTOFF                      # "2026-09-22" (P-5C binding, sec.2)
SEED_GEN = SEED_REGISTRY["trial_labor_w17_gen"]        # 20610000 (held)
SEED_NULL = SEED_REGISTRY["trial_labor_w17_scrnull"]  # 20610500
SEED_UNC = SEED_REGISTRY["trial_labor_w17_unc"]       # 20611000
K_NULLS = 200          # screen null family size (sec.3; frozen)
JUDGE_CAP_BLOCKS = 90  # sec.0 frozen deterministic block cap
RES_DIR = os.path.join(tl1.PATHS.results_dir, "trial_labor_w17")
GRAMMAR_FILE = os.path.join(RES_DIR, "w17_grammar.json")
CELLS_FILE = os.path.join(RES_DIR, "w17_cells.json")
ENTRY_FILE = os.path.join(tl1.PATHS.results_dir, "trial_labor_w16",
                         "w16_candidates.json")
ENTRY_SHA16 = "22179881b7537193"          # sec.2 entry-source anchor (A3)
SCREEN_FILE = os.path.join(RES_DIR, "w17_screen.json")
SCREEN_CSV = os.path.join(RES_DIR, "w17_screen_cells.csv")
JUDGE_FILE = os.path.join(RES_DIR, "w17_judge.json")
REFORM_FILE = os.path.join(RES_DIR, "w17_reform_face.json")
PAIRED_FILE = os.path.join(RES_DIR, "w17_paired_deltas.json")
INTAKE_FILE = os.path.join(RES_DIR, "w17_intake.json")
PREP_FILE = os.path.join(RES_DIR, "prep_state.json")
JUDGE_STATE_FILE = os.path.join(RES_DIR, "judge_state.json")
W16_SCREEN_CSV = os.path.join(tl1.PATHS.results_dir, "trial_labor_w16",
                              "w16_screen_cells.csv")
W16_GRAMMAR_FILE = os.path.join(tl1.PATHS.results_dir, "trial_labor_w16",
                                "w16_grammar.json")
W14_GRAMMAR_FILE = os.path.join(tl1.PATHS.results_dir, "trial_labor_w14",
                                "w14_grammar.json")
CKPT_DIR = os.path.join(RES_DIR, "checkpoint")
SCREEN_BATCH = "TRIAL_LAB_W17_SCREEN"   # prereg sec.0 ledger literal
JUDGE_BATCH = "TRIAL_LAB_W17_JUDGE"     # prereg sec.0 ledger literal
W6M = tl1.WINDOWS["6m"]                # leg-L 6m screen window (126 td)
FROZEN_SHA16 = "09476ecc5beb2304"  # Slice-B pin (== w17_grammar.json
# serialization sha16, first build 2026-10-09 bm-c r789; selftest
# fail-closed verifies the pin == built sha; W16 r722 Slice-B precedent)

# grammar lineage three-face anchors (prereg sec.2 A4 / freeze facts)
W14_GRAMMAR_SHA16 = "a231bf10940e7878"   # w14_grammar internal sha ==
                                          # judge_state grammar_sha ==
                                          # TRIAL_GRAMMAR_LEDGER W14 row
W16_GRAMMAR_SHA16 = "ebf15822d2c8472e"   # W16 runner Slice-B pin ==
                                          # ledger W16 row

# ExitConfig engine default table (prereg sec.2 A9 face, engine/exit_rules.py
# verbatim; freeze facts A9) -- the runner asserts field-by-field equality
# at every screen-prep/finalize (engine drift fail-closed gate).
EXITCFG_DEFAULTS = {
    "take_profit_levels": [0.05, 0.10, 0.20],
    "take_profit_fractions": [1 / 3, 1 / 3, 1.0],
    "trailing_activate": 0.05,
    "trailing_lock": 0.01,
    "initial_stop": -0.08,
    "loss_time_days": 8,
    "time_decay_period": 12,
    "time_decay_threshold": 0.02,
    "global_hard_limit": 25,
    "position_size_pct": 0.10,
    "max_positions": 5,
}

# sec.3 exit face table -- FROZEN verbatim (bridged = run_backtest param
# kwargs, keys are the engine bridge names; patch = ExitPatch override
# fields).  never-true idiom: tp=[10.0] never take-profit, init=-1.0 stop
# price 0 never triggers, trail_act=10.0 never activates, period/loss_time/
# hard_limit=1000 beyond panel length (W1 EXIT_MACHINES idiom source).
W17_FACE_ORDER = ("template_default", "tiered_tp_only", "hard_stop_only",
                  "trailing_only", "time_decay_only", "loss_time_only",
                  "hard_limit_only", "hold_to_end")
W17_EXIT_FACES = {
    "template_default": {"bridged": {}, "patch": {},
                         "rule": "P1-P6 full stack (X-axis semantics: "
                                 "A->registered face / B->engine default)"},
    "tiered_tp_only": {
        "bridged": {"take_profit_levels": [0.05, 0.10, 0.20],
                    "initial_stop": -1.0, "trailing_stop_activate": 10.0,
                    "trailing_lock": 10.0, "time_decay_period": 1000},
        "patch": {"take_profit_fractions": [1 / 3, 1 / 3, 1.0],
                  "loss_time_days": 1000, "global_hard_limit": 1000},
        "rule": "P3 only"},
    "hard_stop_only": {
        "bridged": {"initial_stop": -0.08, "trailing_stop_activate": 0.05,
                    "trailing_lock": 0.01, "take_profit_levels": [10.0],
                    "time_decay_period": 1000},
        "patch": {"loss_time_days": 1000, "take_profit_fractions": [1.0],
                  "global_hard_limit": 1000},
        "rule": "P2 default bundle (initial -8% + 5%-trail)"},
    "trailing_only": {
        "bridged": {"initial_stop": -1.0, "trailing_stop_activate": 0.05,
                    "trailing_lock": 0.01, "take_profit_levels": [10.0],
                    "time_decay_period": 1000},
        "patch": {"loss_time_days": 1000, "take_profit_fractions": [1.0],
                  "global_hard_limit": 1000},
        "rule": "pure trailing, no initial stop (5%/1% defaults)"},
    "time_decay_only": {
        "bridged": {"time_decay_period": 12, "time_decay_threshold": 0.02,
                    "initial_stop": -1.0, "trailing_stop_activate": 10.0,
                    "trailing_lock": 10.0, "take_profit_levels": [10.0]},
        "patch": {"loss_time_days": 1000, "take_profit_fractions": [1.0],
                  "global_hard_limit": 1000},
        "rule": "P4 only (12d/2%)"},
    "loss_time_only": {
        "bridged": {"initial_stop": -1.0, "trailing_stop_activate": 10.0,
                    "trailing_lock": 10.0, "take_profit_levels": [10.0],
                    "time_decay_period": 1000},
        "patch": {"loss_time_days": 8, "take_profit_fractions": [1.0],
                  "global_hard_limit": 1000},
        "rule": "P5 only (8d losing force-exit)"},
    "hard_limit_only": {
        "bridged": {"initial_stop": -1.0, "trailing_stop_activate": 10.0,
                    "trailing_lock": 10.0, "take_profit_levels": [10.0],
                    "time_decay_period": 1000},
        "patch": {"loss_time_days": 1000, "take_profit_fractions": [1.0],
                  "global_hard_limit": 25},
        "rule": "P6 only (25d pure time ceiling)"},
    "hold_to_end": {
        "bridged": {"initial_stop": -1.0, "trailing_stop_activate": 10.0,
                    "trailing_lock": 10.0, "take_profit_levels": [10.0],
                    "time_decay_period": 1000},
        "patch": {"loss_time_days": 1000, "take_profit_fractions": [1.0],
                  "global_hard_limit": 1000},
        "rule": "P1 signal-native only (hold-to-end declaration, "
                "engine default exit stack explicitly disabled)"},
}
# sec.5 frozen prediction faces (recorded for honest post-run accounting;
# sec.5.1 count is a PREDICTION -- the hard determinism gate is the
# 25-pair byte-identity per sec.3 rerun-face clause, prereg sec.9
# build-window reading, disclosed in sec.9 build note)
PRED_CONTROL_SURVIVORS = 40
NULL_P95_BAND = (0.50, 0.53)   # sec.4/sec.5.3 reference band
# registered roster for the D6 reform sub-item (paper six: O-1555 five
# + 511010 cash leg; engine-face daily-return caliber, reeval18 canon)
REGISTERED_D6_SYMBOLS = ("510300", "510050", "510500", "512100",
                        "588000", "511010")
# paired-delta Wilcoxon rng streams -- unc family band, indices above the
# judge-cell consumption range (<720) and below the declared band top 1384
PAIRED_RNG_BASE = 1300

_grammar_sha16 = tl16._grammar_sha16
_j = tl1._j


def _dump(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(_j(payload), fh, ensure_ascii=False, indent=1,
                  default=float)


# ------------------------------------------------------------ exit face layer
def w17_engine_params(cand, template, face):
    """Full engine params + ExitPatch overrides for one W17 cell at the
    given exit face (prereg sec.3 table).  template_default routes
    through tl1.candidate_engine_params with axis[1]='template_default'
    (A-family -> registered exit face + registered_ovr; B-family ->
    engine defaults {}, None) -- byte-identity path for the 25 W16
    same-face pairs (sec.3 rerun-face determinism cross-gate).
    Treatment faces mirror the W1 machine-axes semantics: bridged exit
    fields win, registered sizing fields carried for equal_weight A."""
    sizing = cand["axis"][2]
    if face == "template_default":
        c2 = dict(cand)
        ax = list(cand["axis"])
        ax[1] = "template_default"
        c2["axis"] = ax
        return tl1.candidate_engine_params(c2, template)
    mach = W17_EXIT_FACES[face]
    base = dict(mach["bridged"])
    if template is not None and sizing == "equal_weight":
        reg = template["registered_params"]
        for k in ("position_size_pct", "max_positions"):
            if k in reg:
                base[k] = reg[k]
    return base, dict(mach["patch"])


def _exitcfg_defaults_now():
    """Live ExitConfig defaults via importlib read-only import (prereg
    sec.2 A9 anchor; ZERO engine edit)."""
    import importlib
    eb = importlib.import_module("engine.exit_rules")
    cfg = eb.ExitConfig()
    return {"take_profit_levels": list(cfg.take_profit_levels),
            "take_profit_fractions": list(cfg.take_profit_fractions),
            "trailing_activate": float(cfg.trailing_activate),
            "trailing_lock": float(cfg.trailing_lock),
            "initial_stop": float(cfg.initial_stop),
            "loss_time_days": int(cfg.loss_time_days),
            "time_decay_period": int(cfg.time_decay_period),
            "time_decay_threshold": float(cfg.time_decay_threshold),
            "global_hard_limit": int(cfg.global_hard_limit),
            "position_size_pct": float(cfg.position_size_pct),
            "max_positions": int(cfg.max_positions)}


def _exitcfg_gate():
    """A9 fail-closed gate: live engine defaults == frozen table."""
    live = _exitcfg_defaults_now()
    drift = {k: (live[k], EXITCFG_DEFAULTS[k]) for k in EXITCFG_DEFAULTS
             if live[k] != EXITCFG_DEFAULTS[k]}
    return (not drift), drift


def run_candidate_curve_w17(cand, template, face, prices, P, states,
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
    """One W17 paired cell at the engine face: the W16 overlay pipeline
    (filter -> timing -> GATE -> VOL -> YANG -> VCONF -> STREAK ->
    TSTATE -> AMP -> MOM -> STD -> RSQR -> SUMN -> RESI -> CNT -> MAX ->
    RANK -> initial-stop) with the EXIT FACE as the only variable
    (prereg sec.3; exit params from w17_engine_params; P1 signal
    reversal = runner-native exit_signal=(S<=0) identical across all
    faces).  Curve/overlay machinery = tl16 import-face reuse, zero
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
    mask = tl1.apply_timing(mask, cand["axis"][3])
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
    params, patch = w17_engine_params(cand, template, face)
    params, scale = tl1.sizing_pieces(cand, P, states, params)
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


def _null_axis_draw_w17(i):
    """Deterministic null-cell draw per prereg sec.3: rng=[SEED_NULL, i]
    (W17 berth 20610500, band [20610500,20610700)); consumption order
    frozen = p_on regime -> 19-tuple non-X axis (R/S/T/STOP/GATE/VOL/
    YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR/SUMN/RESI/CNT/MAX/RANK)
    -> exit face (uniform over the 8 W17 faces -- same grid/param space
    draw as candidate cells, BACKTEST_PLAN three iron rules) -> signal
    matrix (returned rng consumed later by the caller)."""
    rng = np.random.default_rng([SEED_NULL, i])
    p_on = tl1.NULL_P_REGIMES[int(rng.integers(len(tl1.NULL_P_REGIMES)))]
    ax = [tl1.AXIS_FILTERS[int(rng.integers(len(tl1.AXIS_FILTERS)))],
          None,   # position 1 = exit face, drawn below
          tl1.AXIS_SIZING[int(rng.integers(len(tl1.AXIS_SIZING)))],
          tl1.AXIS_TIMING[int(rng.integers(len(tl1.AXIS_TIMING)))],
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
    ax[1] = W17_FACE_ORDER[int(rng.integers(len(W17_FACE_ORDER)))]
    return p_on, ax, rng


# ------------------------------------------------------------ grammar / generate
def _entry_load():
    """Entry-source anchor gate (prereg sec.2 A3): frozen W16 candidates
    product, sha256_16 verbatim, zero re-derivation."""
    with open(ENTRY_FILE, "rb") as fh:
        raw = fh.read()
    sha16 = __import__("hashlib").sha256(raw).hexdigest()[:16]
    if sha16 != ENTRY_SHA16:
        raise SystemExit(f"ENTRY-GATE FAIL: w16_candidates.json sha "
                         f"{sha16} != frozen {ENTRY_SHA16}")
    d = json.loads(raw)
    if len(d["candidates"]) != 173:
        raise SystemExit(f"ENTRY-GATE FAIL: n={len(d['candidates'])} != 173")
    return d


def build_grammar_w17():
    """Serialize the W17 grammar face: the frozen exit-face table + the
    entry-source anchor + lineage anchors + null/judge constants
    (deterministic, zero random; sec.3 GENERATE leg)."""
    g = {"wave": WAVE, "grammar_kind": "w17_exit_axis_paired_block",
         "prereg": PREREG, "evidence_cutoff": CUTOFF,
         "grammar_sha256": None,
         "seeds": {"gen_held": SEED_GEN, "scrnull": SEED_NULL,
                   "unc": SEED_UNC,
                   "band": [SEED_GEN, SEED_GEN + 2500],
                   "note": "gen held zero-consumption this wave (entry "
                           "= W16 frozen cells reuse); scrnull rng("
                           "[20610500,i]) i<200; unc rng([20611000,"
                           "cell_idx]) cell_idx<1384; paired-delta "
                           "Wilcoxon streams rng([20611000,1300+f])"},
         "face_order": list(W17_FACE_ORDER),
         "exit_faces": _j(W17_EXIT_FACES),
         "k_nulls": K_NULLS,
         "null_p95_band": list(NULL_P95_BAND),
         "judge_cap_blocks": JUDGE_CAP_BLOCKS,
         "entry_source": {"file": "results/trial_labor_w16/"
                          "w16_candidates.json",
                          "sha256_16": ENTRY_SHA16, "n": 173,
                          "family_split": {"A": 6, "B": 167}},
         "w16_grammar_ref": {"file": "results/trial_labor_w16/"
                             "w16_grammar.json",
                             "grammar_sha16": W16_GRAMMAR_SHA16},
         "w14_lineage": {"grammar_sha16": W14_GRAMMAR_SHA16,
                         "file": "results/trial_labor_w14/w14_grammar.json"},
         "cell_key": "candidate_id x exit_face",
         "n_pairs": 173 * 8,
         "screen_trials": 173 * 8 + K_NULLS}
    g["grammar_sha256"] = _grammar_sha16(g)
    return g


def cmd_grammar() -> int:
    """Serialize the frozen W17 grammar (idempotent; sha16 printed for
    the Slice-B pin)."""
    os.makedirs(RES_DIR, exist_ok=True)
    g = build_grammar_w17()
    if FROZEN_SHA16 and g["grammar_sha256"][:16] != FROZEN_SHA16:
        print(f"GRAMMAR-GATE: sha drift -- frozen anchor {FROZEN_SHA16} "
              f"!= built {g['grammar_sha256'][:16]} (fail-closed)")
        return 1
    _dump(GRAMMAR_FILE, g)
    print(f"grammar serialized: {GRAMMAR_FILE}")
    print(f"sha16 = {g['grammar_sha256'][:16]} "
          f"(pin this in FROZEN_SHA16 at Slice-B)")
    return 0


def _excluded_w17(cand, face, rows):
    """Exact already-burned cell test on (module, fn, sig_params,
    20-tuple with the face at axis[1]) -- sec.3 exclusion book.
    Returns the exclusion face tag or None."""
    ax = list(cand["axis"])
    ax[1] = face
    for e in rows:
        if (cand["module"], cand["fn"]) == (e["module"], e["fn"]) \
                and cand["sig_params"] == e["sig_params"] \
                and ax == e["axis"]:
            return e.get("face", "excluded")
    return None


def cmd_generate() -> int:
    """GENERATE leg (sec.3, deterministic zero-random): W16 candidates
    verbatim load + 8-face full-cross expansion + exclusion-book
    live-read (16 sources: W1-W14 + N2-W15 via the W16 grammar face +
    W16 itself) + w17_cells.json + TRIAL_GRAMMAR_LEDGER wave-17 row
    (W11 practice precedent).  Same-grammar rerun forbidden
    (TRIAL_LABOR_LAW sec.4)."""
    t0 = time.time()
    print(f"=== {WAVE} generate ===")
    if os.path.exists(CELLS_FILE):
        print("GENERATE-GATE: w17_cells.json already landed -- "
              "same-grammar rerun FORBIDDEN (TRIAL_LABOR_LAW sec.4)")
        return 2
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    if FROZEN_SHA16 and _grammar_sha16(grammar) != FROZEN_SHA16:
        print(f"GENERATE-GATE FAIL: grammar sha drift != frozen "
              f"{FROZEN_SHA16}")
        return 1
    ed = _entry_load()
    cands = ed["candidates"]
    # exclusion book: 16-source live read (W1-W14 + N2-W15 rows are
    # serialized in the W16 grammar exclusion face + live-read judged/
    # screen faces by tl16's loader; the 16th source = W16 candidates
    # themselves, read live from the frozen entry product)
    w16g = json.load(open(W16_GRAMMAR_FILE, encoding="utf-8"))
    if _grammar_sha16(w16g)[:16] != W16_GRAMMAR_SHA16:
        print(f"GENERATE-GATE FAIL: w16_grammar sha drift != "
              f"{W16_GRAMMAR_SHA16}")
        return 1
    rows, _excl_disc = tl16._load_exclusion_rows_w16(w16g)
    n_prev_rows = len(rows)
    for c in cands:   # 16th source: W16 burned cells (own X faces)
        rows.append({"module": c["module"], "fn": c["fn"],
                     "sig_params": c["sig_params"],
                     "axis": list(c["axis"]),
                     "face": "w16_burned_cell", "candidate_id":
                     c["candidate_id"]})
    rerun_pairs, other_hits = [], []
    cells = []
    for c in cands:
        for face in W17_FACE_ORDER:
            tag = _excluded_w17(c, face, rows[:n_prev_rows])
            tag16 = _excluded_w17(c, face, rows[n_prev_rows:])
            if face == "template_default" and (tag or tag16):
                rerun_pairs.append({"candidate_id": c["candidate_id"],
                                    "source": tag or tag16})
            elif tag or tag16:
                other_hits.append({"candidate_id": c["candidate_id"],
                                   "face": face,
                                   "source": tag or tag16})
            cells.append({"cell_id": f"{c['candidate_id']}|{face}",
                          "candidate_id": c["candidate_id"],
                          "exit_face": face, "kind": "cand",
                          "family": c["family"]})
    if len(cells) != 173 * 8:
        print(f"GENERATE-GATE FAIL: cells {len(cells)} != 1384")
        return 1
    if len(set(c["cell_id"] for c in cells)) != len(cells):
        print("GENERATE-GATE FAIL: cell-key collision (dedup violation)")
        return 1
    # sec.3 rerun-face clause: exactly the 25 W16 template_default pairs
    # are re-burns (paired baseline + determinism cross-gate); ANY other
    # exclusion hit contradicts the frozen "1,359 new-grid" claim ->
    # honest refuse (GM adjudication face, zero fabrication).
    if other_hits:
        print(f"GENERATE-GATE FAIL: {len(other_hits)} exclusion hits "
              f"beyond the 25 rerun pairs (frozen sec.3 claim violated) "
              f"-- honest refuse, sample {other_hits[:3]}")
        return 1
    if len(rerun_pairs) != 25:
        print(f"GENERATE-GATE FAIL: rerun pairs {len(rerun_pairs)} != 25 "
              "(sec.3 rerun-face clause) -- honest refuse")
        return 1
    prod = {"wave": WAVE, "stage": "generate", "prereg": PREREG,
            "evidence_cutoff": CUTOFF, **tl1.cutoff_meta(CUTOFF),
            "grammar_sha256": grammar["grammar_sha256"],
            "entry_sha256_16": ENTRY_SHA16,
            "n_candidates": 173, "n_faces": 8, "n_cells": len(cells),
            "rerun_pairs": rerun_pairs,
            "exclusion": {"sources": "W1-W14 + N2-W15 (w16 grammar face)"
                          " + W16 burned cells (live read)",
                          "prev_rows": n_prev_rows, "other_hits": 0},
            "family_split": ed.get("family_split", {"A": 6, "B": 167}),
            "seeds": grammar["seeds"],
            "cells": cells}
    _dump(CELLS_FILE, prod)
    # grammar consumption ledger row (append-only; W16 generate caliber)
    ser_ts = time.strftime("%Y-%m-%d %H:%M",
                           time.localtime(os.path.getmtime(GRAMMAR_FILE)))
    row = (f"| {WAVE} | {grammar['grammar_sha256'][:16]} | "
           f"entry 173 x 8 faces (sha {ENTRY_SHA16}, zero new "
           f"generation, gen seed {SEED_GEN} held) | paired cells "
           f"{len(cells)} + nulls {K_NULLS} = {len(cells) + K_NULLS} "
           f"(rerun face 25 W16 pairs) | seeds gen={SEED_GEN} "
           f"null={SEED_NULL} unc={SEED_UNC} | serialized {ser_ts} + "
           f"consumed {time.strftime('%Y-%m-%d %H:%M:%S')} (prereg "
           f"bm-c r788 frozen / runner bm-c r789 exit-axis build) | "
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
    print(f"generate done: 173 x 8 = {len(cells)} paired cells "
          f"(rerun face {len(rerun_pairs)} W16 pairs, other hits 0)")
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
    return 0


# ------------------------------------------------------------ screen slice (s2)
csv_cols_screen_w17 = ["cell_id", "candidate_id", "exit_face", "family",
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


def _screen_cell_w17(cell):
    """One W17 screen cell: full leg-L backtest at the cell's exit face
    -> beat6m row (pool worker; W16 _screen_cell caliber + the
    exit_face column)."""
    st = tl1._ST
    kind, face = cell["kind"], cell["exit_face"]
    P, prices, states = st["P"], st["prices"], st["states"]
    starts, passive = st["starts"], st["passive_6m"]
    close = P["close"]
    if kind == "null":
        p_on, ax, rng = _null_axis_draw_w17(cell["i"])
        cand = {"module": "null", "fn": "random_signal",
                "sig_params": {"p_on": p_on}, "axis": ax,
                "candidate_id": f"W17-NULL-{cell['i']:04d}",
                "family": "NULL"}
        mat = rng.random((len(close.index), len(close.columns)))
        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \
            tz, az, mz, dz, rz, nz, rz2, cnz, mxz, rkz = \
            run_candidate_curve_w17(
                cand, None, ax[1], prices, P, states, st["atr20"],
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
            run_candidate_curve_w17(
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
           "exit_face": face, "family": cand["family"],
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


def _cell_list_w17():
    """Paired cells + K null cells (deterministic order; shard-split by
    index; W16 precedent).  Block order = candidate-major, face-minor
    (the complete-block bookkeeping face)."""
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
                      "exit_face": cell["exit_face"]})
    for i in range(K_NULLS):
        cells.append({"cell_id": f"SCREEN|NULL-{i:04d}", "kind": "null",
                      "i": i, "cand": None, "exit_face": None})
    return grammar, cells


def cmd_screen_prep() -> int:
    """G-PANEL / G-ENTRY / G-LINEAGE / G-EXITCFG fail-closed gates
    (prereg sec.2 anchors A1-A4/A9) + the shared passive 6m precompute.
    Identity-first-run law (r446bmb): every panel/anchor identity face
    runs BEFORE the cells-presence refusal so the full identity face
    exercises on real data pre-generate (rc=2 honest 'generate
    pending' lands at the TAIL)."""
    print(f"=== {WAVE} screen-prep (fail-closed gates) ===")
    # G-EXITCFG (A9): live engine defaults == frozen table
    ok, drift = _exitcfg_gate()
    if not ok:
        print(f"PREP-GATE FAIL: G-EXITCFG drift {drift} (engine "
              "exit_rules.py drifted vs prereg sec.2 A9 -- fail-closed)")
        return 1
    # G-LINEAGE (A4): w14 three-face + w16 pin == ledger rows
    w14g = json.load(open(W14_GRAMMAR_FILE, encoding="utf-8"))
    if str(w14g.get("grammar_sha256", ""))[:16] != W14_GRAMMAR_SHA16:
        print(f"PREP-GATE FAIL: w14_grammar internal sha != "
              f"{W14_GRAMMAR_SHA16}")
        return 1
    w16g = json.load(open(W16_GRAMMAR_FILE, encoding="utf-8"))
    if _grammar_sha16(w16g)[:16] != W16_GRAMMAR_SHA16:
        print(f"PREP-GATE FAIL: w16_grammar sha != {W16_GRAMMAR_SHA16}")
        return 1
    led_rows = {}
    if os.path.exists(tl1.GRAMMAR_LEDGER):
        for ln in open(tl1.GRAMMAR_LEDGER, encoding="utf-8"):
            parts = [p.strip() for p in ln.split("|")]
            if len(parts) > 3 and parts[1].startswith("TRIAL_LABOR"):
                led_rows[parts[1]] = parts[2]
    if led_rows.get("TRIAL_LABOR_W14") != W14_GRAMMAR_SHA16 \
            or led_rows.get("TRIAL_LABOR_W16") != W16_GRAMMAR_SHA16:
        print("PREP-GATE FAIL: ledger lineage mismatch w14="
              f"{led_rows.get('TRIAL_LABOR_W14')} w16="
              f"{led_rows.get('TRIAL_LABOR_W16')}")
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
    # G-GRAMMAR: W17 grammar pin
    grammar = None
    if os.path.exists(GRAMMAR_FILE):
        grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
        if FROZEN_SHA16 and _grammar_sha16(grammar) != FROZEN_SHA16:
            print(f"PREP-GATE FAIL: w17 grammar sha drift != frozen "
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
        print("PREP-GATE FAIL: w17_cells.json absent -- generate "
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
                                  "pass": True},
                      "G-LINEAGE": {"w14": W14_GRAMMAR_SHA16,
                                    "w16": W16_GRAMMAR_SHA16,
                                    "ledger_match": True, "pass": True},
                      "G-EXITCFG": {"pass": True,
                                    "defaults": EXITCFG_DEFAULTS}},
            "starts": starts, "passive_6m_ret": passive_6m}
    _dump(PREP_FILE, prep)
    print(f"prep done: {len(starts)} starts, passive 6m precomputed -> "
          f"{PREP_FILE}")
    return 0


def _park_stamp():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


_BURN_STARTED = None


def _claim_machine_id() -> str:
    """Worker-claim identity (fleet/machine.json; honest fallback)."""
    try:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return json.load(open(os.path.join(root, "fleet", "machine.json"),
                              encoding="utf-8"))["machine_id"]
    except Exception:
        return "unknown"


def _worker_claim(entry_id: str, shard_key: str, result_ref: str) -> None:
    """r497 worker-side harvest handshake (W17 lineage gap closed
    2026-10-10: the w14->w16->w17 clone chain lost this leg, r797
    lineage-copy-loss family -- live cost: completed burns read as
    crashes to the fuse and the campaign froze, r496/r860 families).
    On a completed burn write results/pool_claims/<entry>/<shard>.<mid>
    .json with state=closed+outcome=ok so the launcher's harvest flip
    lands the shard done. The worker NEVER writes runnable_pool.json
    (pool single-writer law). Only called from the real-burn
    completion paths -- the hermetic selftest never reaches here."""
    try:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        d = os.path.join(root, "results", "pool_claims", entry_id)
        os.makedirs(d, exist_ok=True)
        mid = _claim_machine_id()
        fp = os.path.join(d, f"{shard_key}.{mid}.json")
        import datetime
        now = datetime.datetime.now().astimezone().isoformat(
            timespec="seconds")
        with open(fp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"machine_id": mid, "state": "closed",
                       "outcome": "ok", "pid": os.getpid(),
                       "started": _BURN_STARTED, "closed_at": now,
                       "exit_code": 0, "result_ref": result_ref},
                      fh, indent=1, ensure_ascii=False)
        print(f"WORKER-CLAIM closed+ok -> "
              f"{os.path.relpath(fp, root)}", flush=True)
    except Exception as exc:
        # product already landed -- a failed handshake must not fail the
        # burn; the observation round can still write the claim by hand
        # (r860 trio), so disclose and exit clean.
        print(f"WORKER-CLAIM fault (non-fatal, hand-write per r860 "
              f"trio): {exc}", flush=True)


def cmd_screen(shard: int, shards: int, workers) -> int:
    global _BURN_STARTED
    import datetime
    _BURN_STARTED = datetime.datetime.now().astimezone().isoformat(
        timespec="seconds")
    print(f"=== {WAVE} screen shard {shard}of{shards} ===")
    for p, what in ((PREP_FILE, "prep_state.json"),
                    (CELLS_FILE, "w17_cells.json")):
        if not os.path.exists(p):
            print(f"SCREEN-GATE: {what} absent -- run screen-prep first")
            return 2
    prep = json.load(open(PREP_FILE, encoding="utf-8"))
    grammar, cells = _cell_list_w17()
    if FROZEN_SHA16 and _grammar_sha16(grammar) != FROZEN_SHA16:
        print(f"SCREEN-GATE: grammar sha drift != frozen {FROZEN_SHA16}")
        return 2
    ram_min, ram_ok = tl2._ram_gate_gb(wait_min=40)
    if not ram_ok:
        # flush=True mandatory (r691 four-piece law, r800 live case): the
        # crash-confirmer reads this marker from the launch log MINUTES
        # before interpreter shutdown would flush -- an unflushed marker
        # is invisible to exactly the tick that must park instead of
        # fuse-feeding (r800: marker printed 11:32:11, disk-landed only at
        # process exit ~3min later; benign by luck, race is real).
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
             # run_candidate_curve_w17 L350 tl1.GRAMMAR["faces"][mk] -- the
             # W17 grammar has no faces table (faces live in W16 grammar,
             # 77 mk keys). spawn workers re-import tl1 so the parent's
             # L963 tl1.GRAMMAR load never propagates; the faces table
             # must ride initargs (w1 _init_worker GRAMMAR law, r121).
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
        jobs = [(c["cell_id"], _screen_cell_w17, (c,)) for c in todo]
        tl1.run_cells_parallel(jobs, workers=workers or tl1.worker_cap(),
                              desc="screen cells",
                              initializer=tl1._init_worker,
                              initargs=(state,), on_result=on_result)
    print(f"shard {shard}of{shards} complete -> {ck}")
    _worker_claim(f"TRIAL-LABOR-W17-SCREEN-SHARD-{shard}",
                  f"w17-screen-{shard}of{shards}",
                  os.path.relpath(ck, os.path.dirname(os.path.dirname(
                      os.path.abspath(__file__)))))
    return 0


def _w16_screen_rows():
    """W16 screen rows keyed by candidate_id (frozen product read)."""
    rows = {}
    with open(W16_SCREEN_CSV, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            rows[r["candidate_id"]] = r
    return rows


# byte-identity comparison keys for the 25-pair determinism cross-gate
_XGATE_KEYS = ("no_entries", "beat6m_k", "beat6m_n", "beat6m_rate",
               "binom_z", "binom_p", "sharpe_full", "dd_full",
               "n_trades", "n_entries", "stop_fired")


def _control_determinism_gate(ctrl_rows, w16_rows):
    """sec.3 rerun-face determinism cross-gate: the 25 W16
    template_default cells' control-arm screen readings must be
    BYTE-IDENTICAL to the W16 screen same-cell readings (deterministic
    engine + same cutoff; any mismatch = face-mismatch VOID).
    Returns (n_checked, mismatches)."""
    mism = []
    n = 0
    for cid, mine in ctrl_rows.items():
        ref = w16_rows.get(cid)
        if ref is None:
            mism.append({"candidate_id": cid, "key": "_absent_in_w16_csv"})
            continue
        n += 1
        for k in _XGATE_KEYS:
            a, b = mine.get(k), ref.get(k)
            if a is None and (b is None or b == ""):
                continue
            try:
                if float(a) != float(b):
                    mism.append({"candidate_id": cid, "key": k,
                                 "w17": a, "w16": b})
            except (TypeError, ValueError):
                if str(a) != str(b):
                    mism.append({"candidate_id": cid, "key": k,
                                 "w17": a, "w16": b})
    return n, mism


def cmd_screen_finalize() -> int:
    """Screen-finalize: survival line (null p95 via the frozen W2 math)
    + G-face assertion battery (entry sha / grammar pin / A9 ExitConfig
    / 25-pair determinism cross-gate VOID face + sec.5.1 count
    prediction accounting) + ledger append + products."""
    print(f"=== {WAVE} screen-finalize ===")
    landed = tl16.tl6.finalize_already_landed(SCREEN_BATCH, SCREEN_FILE)
    if landed is not None:
        print(f"finalize: already landed (ledger total "
              f"{landed['total']}) -- idempotent no-op")
        return 0
    for p, what in ((GRAMMAR_FILE, "w17_grammar.json"),
                    (CELLS_FILE, "w17_cells.json"),
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
                 if not str(r["candidate_id"]).startswith("W17-NULL")]
    null_rows = [r for r in rows
                 if str(r["candidate_id"]).startswith("W17-NULL")]
    expected = 173 * 8
    if len(cand_rows) != expected or len(null_rows) != K_NULLS:
        print(f"FINALIZE-GATE: incomplete checkpoint ({len(cand_rows)}/"
              f"{expected} cand, {len(null_rows)}/{K_NULLS} nulls) -- "
              "honest refuse (burn pending)")
        return 2
    # G-CONTROL-DETERMINISM: 25-pair byte-identity (hard VOID gate)
    ctrl_rows = {r["candidate_id"]: r for r in cand_rows
                 if r["exit_face"] == "template_default"}
    same_face_ids = {c["candidate_id"] for c in ed["candidates"]
                     if c["axis"][1] == "template_default"}
    gate_rows = {cid: r for cid, r in ctrl_rows.items()
                 if cid in same_face_ids}
    w16_rows = _w16_screen_rows()
    n_checked, mism = _control_determinism_gate(gate_rows, w16_rows)
    xgate = {"n_pairs_expected": 25, "n_checked": n_checked,
             "mismatches": mism,
             "pass": bool(n_checked == 25 and not mism)}
    if not xgate["pass"]:
        print(f"FINALIZE-GATE: control determinism cross-gate VOID "
              f"(checked {n_checked}, mismatches {mism[:3]}) -- "
              "face-mismatch, NOT a scientific reading (prereg sec.3)")
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
    # determinism gate is the 25-pair identity above; the count is a
    # frozen prediction -> sec.7 post-run accounting per sec.5 charter)
    ctrl_surv = [s for s in survivors if s.endswith("|template_default")]
    pred_51 = {"predicted": PRED_CONTROL_SURVIVORS,
               "observed_control_survivors": len(ctrl_surv),
               "verdict": "HIT" if len(ctrl_surv) ==
               PRED_CONTROL_SURVIVORS else "MISS"}
    per_face = {}
    for f in W17_FACE_ORDER:
        face_rows = [r for r in cand_rows if r["exit_face"] == f]
        n_s = sum(1 for r in face_rows if r["survives_screen"])
        per_face[f] = {"n": len(face_rows), "n_survivors": n_s,
                       "survival_rate": round(n_s / max(1, len(face_rows)),
                                              6)}
    face_summary = {f: per_face[f]["n_survivors"] for f in W17_FACE_ORDER}
    ledger = tl1.append_ledger(SCREEN_BATCH, len(cand_rows) + len(null_rows),
                               "results/trial_labor_w17/w17_screen.json",
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
                               "G-CONTROL-DETERMINISM": xgate,
                               "sec51_prediction_accounting": pred_51},
            "per_face_survival": per_face,
            "rerun_pairs_n": 25,
            "trials_ledger": ledger}
    _dump(SCREEN_FILE, prod)
    with open(SCREEN_CSV, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=csv_cols_screen_w17,
                           extrasaction="ignore")
        w.writeheader()
        for r in sorted(cand_rows + null_rows,
                        key=lambda r: r["cell_id"]):
            w.writerow({k: r.get(k) for k in csv_cols_screen_w17})
    print(f"screen-finalize done: null p95 {null_p95} "
          f"(band {'HIT' if band_hit else 'MISS'}), survivors "
          f"{len(survivors)}/{expected}")
    print(f"per-face survival: {json.dumps(face_summary, sort_keys=True)}")
    print(f"sec.5.1 prediction accounting: {json.dumps(pred_51)}")
    print("control determinism cross-gate: 25/25 byte-identity PASS")
    print(f"products: {SCREEN_FILE} + {SCREEN_CSV} "
          f"(ledger total {ledger['total']})")
    return 0


# ------------------------------------------------------ judge slice (s3)
def _dual_nulls_w17(returns, cell_idx, seed=None):
    """Dual nulls on the cell's mean daily return (prereg sec.3 s3):
    B=2000 block-20 circular bootstrap + P=2000 sign-flip, two-sided;
    W17 unc-berth seed binding [20611000, cell_idx].  Math imported
    verbatim from tl2._dual_nulls_w2 (import law)."""
    return tl2._dual_nulls_w2(returns, cell_idx,
                              seed=SEED_UNC if seed is None else seed)


def _rankdata_avg(a):
    """Average ranks with ties (scipy.rankdata 'average' semantics,
    inlined -- zero new third-party dependency)."""
    a = np.asarray(a, dtype=float)
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), dtype=float)
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a[order[j + 1]] == a[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def _wilcoxon_paired(diffs, face_idx, b=2000):
    """Per-face Wilcoxon signed-rank two-sided p via B=2000 sign-flip
    sampling on the |diff| ranks (prereg sec.4 paired-readout face;
    rng=[SEED_UNC, 1300+face_idx] -- unc family band, indices above the
    judge-cell consumption range and below the declared band top 1384).
    Returns (p, median, iqr, n)."""
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


def _judge_cell_w17(cell):
    """One W17 judged paired cell (prereg sec.3 s3 frozen face, pool
    worker): dual-leg (P-5C grid) x cost {base x1, x2=CostPatch(2)}
    full curves at the cell's exit face + window-grid beat vs passive +
    regime segments + dual nulls (W17 unc berth) + member-metrics raw
    materials (four-dim reform face, sec.4 canon)."""
    st = tl1._ST
    cand, template = cell["cand"], cell.get("template")
    face = cell["exit_face"]
    out = {"cell_id": cell["cell_id"], "candidate_id":
           cand["candidate_id"], "exit_face": face,
           "family": cand["family"], "module": cand["module"],
           "fn": cand["fn"], "block": cell["block"]}
    legs = {}
    for leg in ("L", "D"):
        prices, P, idx = (st[f"prices_{leg}"], st[f"P_{leg}"],
                          st[f"idx_{leg}"])
        fok = st[f"fundamental_ok_{leg}"]
        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \
            tz, az, mz, dz, rz, nz, rz2, cnz, mxz, rkz = \
            run_candidate_curve_w17(
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
            eq2, _, m2, _, _, fired2, *_ = run_candidate_curve_w17(
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
    out["dual_nulls"] = _dual_nulls_w17(
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
    arm surviving screen enters JUDGE with ALL 8 arms (block
    completeness law); >90 blocks -> top-90 by the block's 8-arm mean
    screen beat6m descending, ties by candidate_id lexicographic
    (pre-registered deterministic rule, never result-picked)."""
    per_block = {}
    for s in screen["survivors"]:
        cid, face = s.split("|", 1) if "|" in s else (s, None)
        per_block.setdefault(cid, set()).add(face)
    rows_by_cell = {}
    with open(SCREEN_CSV, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            rows_by_cell[(r["candidate_id"], r["exit_face"])] = r
    blocks = []
    for cid, faces in per_block.items():
        rates = []
        for f in W17_FACE_ORDER:
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
        print("JUDGE-PREP-GATE: screen not finalized (w17_screen.json "
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
                # freeze evidence: 3104/2978/2726 vs 2079/1953/1701 gated)
                # -- leg-D starts carry no MIN_LISTED gate, matching
                # trial_labor_w16 judge-prep (`if leg == "L" else True`).
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
    # the unc seed streams; i < 8*90=720 < 1384 declared band top)
    entry = {c["candidate_id"]: c for c in
             _entry_load()["candidates"]}
    a_by_trader = {t["trader_id"]: t for t in tl1.A_TEMPLATES}
    judged = []
    i = 0
    for b in blocks:
        c = entry[b["candidate_id"]]
        template = (a_by_trader.get(c.get("template_trader"))
                    if c["family"] == "A" else None)
        for f in W17_FACE_ORDER:
            judged.append({"cell_id": f"{b['candidate_id']}|{f}",
                           "candidate_id": b["candidate_id"],
                           "exit_face": f, "kind": "cand",
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
    # face; W16 cmd_judge caliber): legs + overlay states + starts
    # r581/crash-fix: judge workers run run_candidate_curve_w17 too (the
    # L350 tl1.GRAMMAR["faces"][mk] lookup) -- grammar rides initargs.
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
        jobs = [(c["cell_id"], _judge_cell_w17, (c,)) for c in todo]
        tl1.run_cells_parallel(jobs, workers=workers or tl1.worker_cap(),
                              desc="judge cells",
                              initializer=tl1._init_worker,
                              initargs=(state,), on_result=on_result)
    print(f"judge shard {shard}of{shards} complete -> {ck}")
    _worker_claim("TRIAL-LABOR-W17-JUDGE",
                  f"w17-judge-{shard}of{shards}",
                  os.path.relpath(ck, os.path.dirname(os.path.dirname(
                      os.path.abspath(__file__)))))
    return 0


def cmd_judge_finalize() -> int:
    """Judge-finalize: G1'v2 + G2-v2 verdicts + M1 t-face + family PBO
    + the REFORM FACE BLOCK (member_metrics four-dim + dual-nulls +
    g2_reform_fdr4d + D6 + top-3 -- W16 sec.8 gap lesson, prereg sec.4
    mandated) + paired-delta Wilcoxon face (sec.4) + E[FP] disclosure
    + ledger append + products."""
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
        if r["legs"].get("L", {}).get("degenerate") or not rets:
            r["dsr"] = None
            r["g1_pass"] = False
            r["verdict"] = "fail-degenerate"
            r["t_face"] = None
            continue
        g1 = tl1.g1_prime_v2(r["legL_sharpe_full"], rets, batch_cells,
                             pool="core48", n_trades=r["legL_n_trades"],
                             n_entries=r["legL_n_entries"])
        dsr = tl1.deflated_sharpe_ratio(rets, n_trials=n_trials)
        r["g1_prime_v2"] = g1
        r["dsr"] = {"dsr": round(float(dsr["dsr"]), 6),
                    "n_trials": n_trials}
        r["g1_pass"] = g1["pass_v2"]
        r["verdict"] = ("pass" if (g1["pass_v2"] and r["sample_sufficient"])
                        else "insufficient-sample" if not r[
                            "sample_sufficient"] else "fail")
        # M1 t-face law (prereg sec.4): derivation lives in science_gates (frozen import)
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
        if r.get("g1_prime_v2") is None:
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
        if r["legs"].get("L", {}).get("degenerate"):
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
                   "constants": {"dim_weights": REFORM_DIM_WEIGHTS,
                                 "sub_weights": REFORM_SUB_WEIGHTS,
                                 "q": REFORM_Q_LEVEL,
                                 "topn": REFORM_TOPN_PER_WAVE,
                                 "ceiling_baseline":
                                 "five_member_ew (O-1555 five)"}}
    _dump(REFORM_FILE, reform_prod)
    # -- paired-delta Wilcoxon face (sec.4, this batch's own design)
    sharpe_by = {(r["candidate_id"], r["exit_face"]):
                 r.get("legL_sharpe_full") for r in judged}
    paired = {}
    for f_idx, f in enumerate([x for x in W17_FACE_ORDER
                               if x != "template_default"]):
        diffs = []
        for b in jstate["blocks"]:
            cid = b["candidate_id"]
            a = sharpe_by.get((cid, f))
            c = sharpe_by.get((cid, "template_default"))
            if a is not None and c is not None:
                diffs.append(a - c)
        p, med, iqr, n = _wilcoxon_paired(diffs, f_idx)
        paired[f] = {"n_pairs": n, "median_delta": med, "iqr": iqr,
                     "wilcoxon_p": p,
                     "rng": [SEED_UNC, PAIRED_RNG_BASE + f_idx]}
    paired_prod = {"wave": WAVE, "stage": "paired-deltas",
                   "evidence_cutoff": CUTOFF,
                   **tl1.cutoff_meta(CUTOFF),
                   "per_face": paired,
                   "note": "face-vs-control leg-L Sharpe paired deltas "
                           "across complete blocks; Wilcoxon signed-rank "
                           "two-sided via B=2000 sign-flip sampling on "
                           "|diff| ranks, unc-family rng streams"}
    _dump(PAIRED_FILE, paired_prod)
    ledger = tl1.append_ledger(JUDGE_BATCH, n_judged,
                              "results/trial_labor_w17/w17_judge.json",
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
    -> TRIAL-EXITAXIS-* paper-probation listing (registration itself =
    separate GM face per law); lawful-zero when none."""
    print(f"=== {WAVE} intake ===")
    if not os.path.exists(REFORM_FILE):
        print("INTAKE-GATE: w17_reform_face.json absent -- judge "
              "finalize pending")
        return 2
    reform = json.load(open(REFORM_FILE, encoding="utf-8"))
    onboard = reform.get("onboard_list", [])
    prod = {"wave": WAVE, "stage": "intake",
            "evidence_cutoff": CUTOFF, **tl1.cutoff_meta(CUTOFF),
            "n_eligible": len(onboard),
            "accounts": [{"name": f"TRIAL-EXITAXIS-{i+1:02d}",
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
    # import, read-only; engine drift face)
    ok("L2 exitcfg defaults == A9 frozen table", *_exitcfg_gate())
    # L3: face params bite + never-true idiom (ExitPatch + bridge
    # precedence: bridge kwargs WIN over patch, engine factory law --
    # the patch replaces engine.BACKTESTER's ExitConfig reference, so
    # the bite test must construct via backtester exactly like the
    # engine's run_backtest does)
    import importlib
    _ebb = importlib.import_module("engine.backtester")
    with tl1.ExitPatch(dict(W17_EXIT_FACES["hold_to_end"]["patch"])):
        cfg = _ebb.ExitConfig(
            take_profit_levels=tuple(
                W17_EXIT_FACES["hold_to_end"]["bridged"].get(
                    "take_profit_levels", (0.05, 0.10, 0.20))),
            trailing_activate=W17_EXIT_FACES["hold_to_end"][
                "bridged"].get("trailing_stop_activate", 0.05),
            trailing_lock=W17_EXIT_FACES["hold_to_end"]["bridged"].get(
                "trailing_lock", 0.01),
            initial_stop=W17_EXIT_FACES["hold_to_end"]["bridged"].get(
                "initial_stop", -0.08),
            time_decay_period=W17_EXIT_FACES["hold_to_end"][
                "bridged"].get("time_decay_period", 12),
            time_decay_threshold=W17_EXIT_FACES["hold_to_end"][
                "bridged"].get("time_decay_threshold", 0.02))
        ok("L3 hold_to_end never-true idiom",
           cfg.take_profit_levels[0] == 10.0 and cfg.initial_stop == -1.0
           and cfg.trailing_activate == 10.0 and cfg.time_decay_period
           == 1000 and cfg.loss_time_days == 1000
           and cfg.global_hard_limit == 1000)
    with tl1.ExitPatch(dict(W17_EXIT_FACES["hard_limit_only"]["patch"])):
        cfg = _ebb.ExitConfig(
            take_profit_levels=tuple(
                W17_EXIT_FACES["hard_limit_only"]["bridged"][
                    "take_profit_levels"]))
        ok("L3b hard_limit_only P6-only bite",
           cfg.global_hard_limit == 25 and cfg.loss_time_days == 1000)
    with tl1.ExitPatch(dict(W17_EXIT_FACES["loss_time_only"]["patch"])):
        cfg = _ebb.ExitConfig(
            initial_stop=W17_EXIT_FACES["loss_time_only"]["bridged"][
                "initial_stop"])
        ok("L3c loss_time_only P5-only bite",
           cfg.loss_time_days == 8 and cfg.initial_stop == -1.0)
    # L4: w17_engine_params routing (synthetic cand/template)
    cand_b = {"axis": ["liquidity", "ce_machine", "cap20",
                       "weekly_grid"] + ["none"] * 16}
    base, patch = w17_engine_params(cand_b, None, "template_default")
    ok("L4a B-family control -> engine defaults", base == {}
       and patch is None)
    cand_a = {"axis": ["liquidity", "time_stop_10d", "equal_weight",
                       "weekly_grid"] + ["none"] * 16}
    tmpl = {"registered_params": {"position_size_pct": 0.12,
                                   "max_positions": 4,
                                   "take_profit_levels": [0.04]},
            "registered_ovr": {"loss_time_days": 6}}
    base, patch = w17_engine_params(cand_a, tmpl, "template_default")
    ok("L4b A-family control -> registered face",
       base.get("position_size_pct") == 0.12 and patch == {
           "loss_time_days": 6})
    base, patch = w17_engine_params(cand_a, tmpl, "tiered_tp_only")
    ok("L4c treatment -> bridged verbatim + sizing carry",
       base.get("take_profit_levels") == [0.05, 0.10, 0.20]
       and base.get("position_size_pct") == 0.12
       and patch.get("take_profit_fractions") == [1 / 3, 1 / 3, 1.0]
       and "take_profit_levels" not in patch)
    # L5: null draw determinism + face vocabulary
    p1, ax1, r1 = _null_axis_draw_w17(7)
    p2, ax2, r2 = _null_axis_draw_w17(7)
    p3, ax3, r3 = _null_axis_draw_w17(8)
    ok("L5 null draw determinism + 8-face vocab",
       p1 == p2 and ax1 == ax2 and (p1, ax1) != (p3, ax3)
       and ax1[1] in W17_FACE_ORDER and len(ax1) == 20
       and (r1.random() != r3.random()))
    # L6: grammar serialization determinism + anchor constants
    g1s, g2s = build_grammar_w17(), build_grammar_w17()
    ok("L6 grammar deterministic + lineage anchors",
       g1s["grammar_sha256"] == g2s["grammar_sha256"]
       and g1s["entry_source"]["sha256_16"] == ENTRY_SHA16
       and g1s["w14_lineage"]["grammar_sha16"] == "a231bf10940e7878"
       and g1s["w16_grammar_ref"]["grammar_sha16"] == "ebf15822d2c8472e"
       and g1s["n_pairs"] == 1384
       and g1s["screen_trials"] == 1584)
    # L6b: FROZEN pin check (Slice-B face)
    if FROZEN_SHA16:
        ok("L6b frozen sha pin == built grammar",
           g1s["grammar_sha256"][:16] == FROZEN_SHA16)
    else:
        ok_n += 1
        print("[PASS] L6b frozen pin not yet set (pre-generate face)")
    # L7: block-cap deterministic rule (synthetic screen)
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
    # L11: dual-nulls W17 unc berth binding (determinism)
    r = np.random.default_rng(3).normal(0.0005, 0.01, 300)
    d1 = _dual_nulls_w17(r, 5)
    d2 = _dual_nulls_w17(r, 5)
    ok("L11 dual-nulls unc-berth determinism",
       d1 == d2 and d1["B"] == 2000 and d1["P"] == 2000
       and len(d1["bootstrap_ci"]) == 2)
    # L12: exclusion matcher + control determinism gate function
    rows = [{"module": "m", "fn": "f", "sig_params": {"w": 1},
             "axis": ["liquidity", "template_default", "cap20",
                      "weekly_grid"] + ["none"] * 16,
             "face": "w16_burned_cell"}]
    cand_x = {"module": "m", "fn": "f", "sig_params": {"w": 1},
              "axis": ["liquidity", "ce_machine", "cap20",
                       "weekly_grid"] + ["none"] * 16}
    ok("L12 exclusion matcher (face-at-axis-1 semantics)",
       _excluded_w17(cand_x, "template_default", rows)
       == "w16_burned_cell"
       and _excluded_w17(cand_x, "tiered_tp_only", rows) is None)
    mine_rows = {"W16-B-0001": {k: 1 for k in _XGATE_KEYS}}
    ref_rows = {"W16-B-0001": {k: "1" for k in _XGATE_KEYS}}
    n_c, mism = _control_determinism_gate(mine_rows, ref_rows)
    ok("L12b cross-gate byte-identity comparator",
       n_c == 1 and not mism)
    mine_rows["W16-B-0001"]["beat6m_rate"] = 0.9
    n_c2, mism2 = _control_determinism_gate(mine_rows, ref_rows)
    ok("L12c cross-gate catches drift", n_c2 == 1
       and len(mism2) == 1 and mism2[0]["key"] == "beat6m_rate")
    # L13: five-member/registered constants sanity
    ok("L13 registered D6 roster frozen",
       len(REGISTERED_D6_SYMBOLS) == 6 and "510300"
       in REGISTERED_D6_SYMBOLS)
    # L14: generate refuse-on-landed law + products writer idempotence
    with tempfile.TemporaryDirectory() as td:
        fp = os.path.join(td, "x.json")
        _dump(fp, {"a": 1})
        _dump(fp, {"a": 1})
        ok("L14 dump idempotent + ascii-safe",
           json.load(open(fp, encoding="utf-8")) == {"a": 1})
    print(f"selftest: {ok_n} PASS, {len(fails)} FAIL"
          f"{'' if not fails else ' -- ' + ', '.join(fails)}")
    return 0 if not fails else 1


# ------------------------------------------------------------------ argparse
def _build_parser():
    p = argparse.ArgumentParser(description=WAVE + " runner "
                               "(exit-axis complete-block paired "
                               "isolation; frozen prereg "
                               + PREREG + ")")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("grammar", help="serialize w17_grammar.json")
    sub.add_parser("generate", help="173 x 8 cross expansion + "
                   "exclusion book + w17_cells.json + ledger row")
    sub.add_parser("status", help="product presence + A9 gate")
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
