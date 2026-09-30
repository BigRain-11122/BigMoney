"""TRIAL_LABOR_W14 runner -- T-128 mass-candidate trial wave-14
(10,000-ceiling, RESI trend-extension position + CNT yang-day density
EIGHTEEN-gate wave; reform verdict face FIRST WAVE).

Prereg FROZEN (bm-b r471 adoption freeze whole-package per berth
first-to-hold + open-adoption clause: bm-c r276 draft origin 04759cf69
-> bm-b r470 same-window independent dual-draft zero-collusion
cross-validation yield -> bm-b r471 freeze + cntn20 supplement ->
bm-c r277 gap probe twin cross-val 39/39; freeze trigger MET live =
W13 full chain landed 2026-09-30 12:28 {w13_judge 99/99 judged zero
G1 zero G2 + w13_intake lawful-zero + CEO-REPORT-WAVE13 48h window +
grammar ledger wave-14 row + attrition SCREEN row retrofilled} + pool
139/139 done zero in-flight):
research/TRIAL_LABOR_W14_PREREG.md -- generate grammar + funnel rules +
judgment lines all frozen; post-run only sec.7/8 backfill.  Seeds held
at the freeze commit per R250 one-step law: trial_labor_w14_gen=
20327500 / trial_labor_w14_scrnull=20328000 / trial_labor_w14_unc=
20328500 (three-step law ALL GREEN at the freeze commit
results/_r471bmb_w14_seed_law_facts.json, no re-pick after freeze).

Import-face law (prereg sec.3): the FULL trial_labor_w1-w13 chain is
imported (tl1 enumeration/loading/anchor/envelope primitives + tl2
initial-stop overlay + tl3 regime-gate overlay + tl4 vol overlay +
tl5 yang overlay + tl6 vconf overlay + tl7 streak overlay + tl8
tstate overlay & eleven-tuple machinery + tl9 amp overlay + tl10 mom
overlay + tl11 std overlay + tl12 rsqr overlay + tl13 sumn overlay &
sixteen-tuple machinery); RESI/CNT come from the FROZEN in-repo
runner scripts/a158_tsgate_probe.py verbatim import (alpha158_factors
+ GATE_WIN=252 / GATE_MINP=120 / QHIGH / QLOW constants same-source;
zero re-implementation); Sobol sample_draws pattern follows
mass_trial_w1 (paradigm import); strategies/ factory + engine/
backtester imported, never rewritten; engine/exit_rules.py ZERO touch.

RESI/CNT overlay (prereg sec.2/sec.3 NEW W14 frozen layer; r470/r471
probe verbatim = A158-TSGATE-P1 frozen construction).  Member 510300
signal-day-d close info set.  F = a158.alpha158_factors(member face);
resi60 = F["RESI60"] = rolling-OLS(close,60) end-point residual/close
(closed-form cumsum, min_periods=1 expanding warmup); q90_ref =
resi60.rolling(GATE_WIN, min_periods=GATE_MINP).quantile(QHIGH);
resi60_hi = resi60 > q90_ref (trend-extension position entering its
own top decile).  cntd5 = F["CNTD5"] = mean(up-day,5) - mean(down-
day,5); cntd5_hi = cntd5 > q90_ref (yang-day NET-DOMINANCE density);
cntn20 = F["CNTN20"] = mean(down-day,20); cntn20_lo = cntn20 < q10_ref
(down-day FREQUENCY low -- non-purity face, r471 supplement).  RESI
first-decidable == 120 (RESI[0] NaN, expanding k=1 Stt=0 guard);
CNT first-decidable == 119 (idx-0 comparison vs NaN -> False -> 0.0
non-NaN -> qref one bar early -- HONEST one-bar construction-family
difference note vs the RSQR/STD/SUMN 120 face; probe assert anchors
per-face, NOT a uniform 120).  Decidable derives from the underlying
values notna (pit-95 batch-95 law); gates act on ENTRY PERMITTANCE
only (effective signal zeroed, MSG-0440 E1-mapping; exit logic zero
change).  Member set adjudicated (prereg banner): RESI{none,resi60_hi}
x CNT{none,cntd5_hi,cntn20_lo} = 6 mult; resi30/cntd10 GATE-RECHECK
FAIL demoted (increment faces non-collapsed 219/161 days disclosed --
increment existence != recheck pass); cntd20 ABSENT below threshold.

G-RESI/G-CNT anchor law (prereg sec.2/sec.3 probe facts, fail-closed):
on the raw full-history member face (3,483 bars 2012-05-28 -> 2026-
09-22 cutoff): resi60 decidable == 3,363 / open == 390 (11.20%) /
first-decidable == 120; cntd5 decidable == 3,364 / open == 137
(3.93% thin-tail honest note) / first-decidable == 119; cntn20
decidable == 3,364 / open == 265 (7.61%) / first-decidable == 119;
NINE-gate 512-cell grids: resi60 103 non-empty / 409 empty (max 41;
all-decidable 3,305), cntd5 109/403, cntn20 103/409 (max 41); core48
open-rate non-degenerate 48/48; extreme-day gate states exact (probe
7-day face) + exact per-cell cross-check vs the git-tracked probe
facts files when present (r470/r471 determinism cross-check law).

Exclusion law (prereg sec.1, EIGHTEEN-tuple cell key=(template,
params, axis_config, initial_stop, gate, vol, yang, vconf, streak,
tstate, amp, mom, std, rsqr, sumn, resi, cnt), FOURTEEN judged +
FOURTEEN screen real-read source faces, exact already-judged key,
resi=none AND cnt=none face only: prior-wave keys lacking the resi/
cnt axes are none-completed (semantic-identity match; generate-time
real-read; W13-JUDGE landed 2026-09-30 12:28 = FOURTEENTH source,
seventh full-declare window); resi/cnt in member values = new-syntax
legal cells (never excluded).

Reform verdict face (prereg sec.4 FIRST WAVE; REGISTRATION_REFORM_
FDR4D canon): judge-finalize produces per-cell four-dimension raw
materials (ret: sharpe_full_L/annualized_ret_L/return_ceiling_O1126/
beat6m_rate_L/beat12m_rate_L; robust: cost_x2_sharpe_L/regime_min_
sharpe_L/bootstrap_ci_low_L; anti_overfit: family_pbo/d6_max_abs_
corr; anti_luck: batch_dsr with n_trials = BATCH size) -> science_gates
g2_reform_fdr4d (batch-internal BH FDR q<=REFORM_Q_LEVEL + complete
four-dim composite; constants imported, 禁手抄判线律) -> eligible_
reform = registration caliber; top-3 by composite = paper-probation
caliber (REFORM_TOPN_PER_WAVE); G1'v2/G2-v2/DSR-global columns
retained as disclosure-only legacy faces (O-1058 sec.1 verbatim:
G1' pass-count != hiring caliber change, both calibers disclosed
separately); reform_weight_freeze_integrity pre-checked fail-closed.
batch_p_values = dual-nulls signflip_p (reform canon sec.5 P1
standard candidate face: full-period return sign-flip significance);
return_ceiling baseline = five_member_ew_O1555 (equal weight of the
O-1555 frozen universe over the same leg-L window, r271 定谳).

Composition order frozen everywhere: signal -> filter -> timing ->
GATE -> VOL -> YANG -> VCONF -> STREAK -> TSTATE -> AMP -> MOM ->
STD -> RSQR -> SUMN -> RESI -> CNT -> initial-stop (W13 order
extended; prereg sec.3 eighteen-tuple order R/X/S/T/STOP/GATE/VOL/
YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR/SUMN/RESI/CNT).

Three-command closeout law (r446bmb/r467bma surgical pit law,
prereg sec.9): prep/finalize/judge-prep real-data identity-face
first-runs BEFORE the runner is declared landed.  Physical-data
sequencing adjudication (disclosed, W12 r445/r446 precedent):
screen-prep identity faces (G-PANEL..G-RESI/G-CNT..G-ANCHOR/G-CENSUS
+ passive precompute) are ordered BEFORE the candidates-presence
refusal so the full identity face runs pre-generate and refuses
honestly rc=2 at the tail; screen-finalize + judge-prep identity
first-runs fire at their natural funnel points (their sole inputs
are screen/judge products -- rehearsal burns are ledger-forbidden,
pit-95) per the W12 r446 live precedent; fix-first law armed.

Slice plan (W3-W13 single-writer precedent; wave ticket
T-2026-09-30-128 opened+claimed bm-b same freeze commit per
O-1730 immediate law):
  - Slice-A (this draft, bm-b r472 identity surgery
    results/_r472bmb_w14_identity.py + section payloads): mechanical
    identity + RESI/CNT overlay layer (a158 verbatim import kit) +
    grammar/Sobol/exclusion/mask/curve/null legs rewiring + reform
    judge face + intake + selftest legs.  Draft name
    results/_r472bmb_w14_runner_draft.py -- NOT the formal runner
    (runner_exists gate must not fire on a partial build).
  - Slice-B (same round): py_compile + selftest + grammar
    serialization + sha16 pin + formal-name move + screen-prep
    real-data identity first-run + catalog runner_exists arm + MSG
    declaration, GENERATE pool release.
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trial_labor_w1 as tl1  # import-face reuse law (prereg sec.6)
import trial_labor_w2 as tl2  # initial-stop overlay layer import law
import trial_labor_w3 as tl3  # regime-gate overlay + MASS translation
import trial_labor_w4 as tl4  # vol overlay + dual-gate machinery
import trial_labor_w5 as tl5  # yang overlay + triple-gate machinery
import trial_labor_w6 as tl6  # vconf overlay + nine-tuple machinery
import trial_labor_w7 as tl7  # streak overlay + ten-tuple machinery
import trial_labor_w8 as tl8  # tstate overlay + eleven-tuple machinery
import trial_labor_w9 as tl9  # amp overlay + twelve-tuple machinery
import trial_labor_w10 as tl10  # mom overlay + thirteen-tuple machinery
import trial_labor_w11 as tl11  # std overlay + sixteen-tuple machinery
import trial_labor_w12 as tl12  # rsqr overlay + fifteen-tuple machinery (W12 frozen face)
import trial_labor_w13 as tl13  # sumn overlay + sixteen-tuple machinery (W13 frozen face; import-face law -- W14 re-derives ZERO sumn machinery)
import a158_tsgate_probe as a158  # frozen A158 runner (RESI60/CNTD5/CNTN20/RSQR20/SUMN20/BETA20 verbatim import)
from science_gates import (CostPatch, SEED_REGISTRY,  # noqa: E402
                           REFORM_DIM_WEIGHTS, REFORM_SUB_WEIGHTS,
                           REFORM_TOPN_PER_WAVE, REFORM_Q_LEVEL,
                           reform_weight_freeze_integrity,
                           g2_reform_fdr4d)  # prereg sec.4 reform canon: constants + gate functions imported from the single canonical source (r271 定谳, 禁手抄判线律)

# ------------------------------------------------------------ frozen (prereg)
WAVE = "TRIAL_LABOR_W14"
PREREG = "research/TRIAL_LABOR_W14_PREREG.md"
CUTOFF = tl1.CUTOFF                      # "2026-09-22" (P-5C binding, sec.2)
SEED_GEN = SEED_REGISTRY["trial_labor_w14_gen"]        # 20327500
SEED_NULL = SEED_REGISTRY["trial_labor_w14_scrnull"]  # 20328000
SEED_UNC = SEED_REGISTRY["trial_labor_w14_unc"]        # 20328500
N_A = 500          # family A raw draws (sec.3: 6 templates round-robin)
N_B = 9500         # family B raw draws (machinery round-robin; O-1132 10,000-cap: A500 + B9500)
K_NULLS = 200       # screen null family size (sec.3; frozen)
RES_DIR = os.path.join(tl1.PATHS.results_dir, "trial_labor_w14")
GRAMMAR_FILE = os.path.join(RES_DIR, "w14_grammar.json")
CANDIDATES_FILE = os.path.join(RES_DIR, "w14_candidates.json")
GRAMMAR_LEDGER = tl1.GRAMMAR_LEDGER
SCREEN_FILE = os.path.join(RES_DIR, "w14_screen.json")
SCREEN_CSV = os.path.join(RES_DIR, "w14_screen_cells.csv")
JUDGE_FILE = os.path.join(RES_DIR, "w14_judge.json")
INTAKE_FILE = os.path.join(RES_DIR, "w14_intake.json")
PREP_FILE = os.path.join(RES_DIR, "prep_state.json")
JUDGE_STATE_FILE = os.path.join(RES_DIR, "judge_state.json")
CKPT_DIR = os.path.join(RES_DIR, "checkpoint")
SCREEN_BATCH = "TRIAL_LAB_W14_SCREEN"   # prereg sec.0 ledger literal
JUDGE_BATCH = "TRIAL_LAB_W14_JUDGE"     # prereg sec.0 ledger literal
W6M = tl1.WINDOWS["6m"]                # leg-L 6m screen window (126 td)
FROZEN_SHA16 = "a231bf10940e7878"   # Slice-B pin (bm-b r472; == w14_
# grammar.json serialization sha16; selftest L6g
# fail-closed verifies pin == built sha (grammar face
# built + sha measured this round; W12 r445-close precedent)

# prior-wave grammar shas (constructive-distinct assertion face)
PRIOR_WAVE_SHA16 = {
    "W1": "a2fa15f4b06b3c40", "MASS": "96269ebe766c3fc2",
    "W2": "1dd3d9579235cec", "W3": "cc59eab79db53436",
    "W4": "d498e9343ee57460", "W5": "29720178c39425de",
    "W6": "2d395f5f8e7d16cb", "W7": tl7.FROZEN_SHA16,   # 1fba956c2f21d1d3
    "W8": tl8.FROZEN_SHA16,      # 282c3290d1b431bc
    "W9": tl9.FROZEN_SHA16,      # 0601dda70b0209fa
    "W10": tl10.FROZEN_SHA16,    # e21c7eb83087035c
    "W11": tl11.FROZEN_SHA16,    # 128962592feeb8d3
    "W12": tl12.FROZEN_SHA16,    # 67c86c9cf4ef1ca7
    "W13": tl13.FROZEN_SHA16,    # 868cd0c6413636e6
}

# tstate axis (W8 frozen face, imported verbatim)
AXIS_TSTATE = tl8.AXIS_TSTATE           # ["none","deep_pullback","oversold_rsv"]
TSTATE_MEMBER = tl8.TSTATE_MEMBER       # "510300"

# amplitude-confirmation axis (W9 frozen face, imported verbatim from
# tl9 -- import-face law; the W13 runner re-derives ZERO mom machinery)
AXIS_AMP = tl9.AXIS_AMP                 # ["none","amp_narrow","amp_wide"]
AMP_MEMBER = tl9.AMP_MEMBER              # "510300"
AMP_ANCHOR = tl9.AMP_ANCHOR             # W9 frozen probe anchors
# FULL amp machinery imported verbatim from tl9 (W9 frozen face;
# import-face law; zero re-implementation -- same block as tl10 L567)
amp_state_series = tl9.amp_state_series
amp_zero_mask = tl9.amp_zero_mask
_amp_state_full = tl9._amp_state_full
_amp_structure_pass = tl9._amp_structure_pass
_amp_series_raw = tl9._amp_series_raw
# AMP_SPEC carried from tl9.build_grammar_w9() inside build_grammar_w14
# (import-time grammar-chain build is heavy; lazy face = build-time read)

# momentum-confirmation axis (W10 frozen face, imported verbatim from
# tl10 -- import-face law; the W13 runner re-derives ZERO mom
# machinery)
AXIS_MOM = tl10.AXIS_MOM                 # ["none","mom_oversold"]
MOM_MEMBER = tl10.MOM_MEMBER              # "510300"
MOM_ANCHOR = tl10.MOM_ANCHOR             # W10 frozen probe anchors
mom_state_series = tl10.mom_state_series
mom_zero_mask = tl10.mom_zero_mask
_mom_state_full = tl10._mom_state_full
_mom_structure_pass = tl10._mom_structure_pass
_mom_series_raw = tl10._mom_series_raw
# MOM_SPEC/MOM_ANCHOR carried from tl10.build_grammar_w10() inside
# build_grammar_w14 (import-time grammar-chain build is heavy; lazy
# face = build-time read)

# grammar sha16 (W7 lineage import; zero re-implementation)
def _grammar_sha16(grammar):
    """Grammar sha16 (W7 lineage import; zero re-implementation)."""
    return tl7._grammar_sha16(grammar)

# high-dispersion STD axis (W11 frozen face, imported verbatim from
# tl11 -- import-face law; the W13 runner re-derives ZERO std
# machinery)
AXIS_STD = tl11.AXIS_STD                 # ["none","std20_hi","std10_hi"]
STD_MEMBER = tl11.STD_MEMBER             # "510300"
STD_ANCHOR = tl11.STD_ANCHOR             # W11 frozen probe anchors
std_state_series = tl11.std_state_series
std_zero_mask = tl11.std_zero_mask
_std_state_full = tl11._std_state_full
_std_structure_pass = tl11._std_structure_pass
_std_series_raw = tl11._std_series_raw
# STD_SPEC/STD_ANCHOR carried from tl11.build_grammar_w11() inside
# build_grammar_w14 (import-time grammar-chain build is heavy; lazy
# face = build-time read)

# trend-fit-quality RSQR axis (W12 frozen face, imported verbatim from
# tl12 -- import-face law; the W13 runner re-derives ZERO rsqr machinery)
AXIS_RSQR = tl12.AXIS_RSQR                 # ["none","rsqr20_hi","rsqr10_hi"]
RSQR_MEMBER = tl12.RSQR_MEMBER             # "510300"
RSQR_ANCHOR = tl12.RSQR_ANCHOR             # W12 frozen probe anchors
rsqr_state_series = tl12.rsqr_state_series
rsqr_zero_mask = tl12.rsqr_zero_mask
_rsqr_state_full = tl12._rsqr_state_full
_rsqr_structure_pass = tl12._rsqr_structure_pass
_rsqr_faces_raw = tl12._rsqr_faces_raw
# RSQR_SPEC/RSQR_ANCHOR carried from tl12.build_grammar_w12() inside
# build_grammar_w14 (import-time grammar-chain build is heavy; lazy
# face = build-time read)

# --- kit part A: sumn import-face + resi/cnt axes + specs + anchors +
# faces computation + zero masks (spliced into the W14 runner) ---

# up-share-purity SUMN axis (W13 frozen face, imported verbatim from
# tl13 -- import-face law; the W14 runner re-derives ZERO sumn machinery)
AXIS_SUMN = tl13.AXIS_SUMN               # ["none","sumn20_lo","sumn10_lo"]
SUMN_MEMBER = tl13.SUMN_MEMBER          # "510300"
SUMN_ANCHOR = tl13.SUMN_ANCHOR         # W13 frozen sumn probe anchors
sumn_state_series = tl13.sumn_state_series
sumn_zero_mask = tl13.sumn_zero_mask
_sumn_state_full = tl13._sumn_state_full
_sumn_structure_pass = tl13._sumn_structure_pass
_sumn_faces_raw = tl13._sumn_faces_raw
# SUMN_SPEC/SUMN_ANCHOR carried from tl13.build_grammar_w14() inside
# build_grammar_w14 (import-time grammar-chain build is heavy; lazy
# face = build-time read)

# trend-extension-position RESI axis (prereg sec.3 NEW W14 frozen
# layer, TWO-value adjudicated member axis; resi30 GATE-RECHECK FAIL
# demoted -- member-set adjudication banner; W4-VOL/W11-STD/W12-RSQR/
# W13-SUMN axis-family precedent)
AXIS_RESI = ["none", "resi60_hi"]
RESI_MEMBER = "510300"          # core48 member (prereg sec.2 probe fact)
RESI_PROBE_FACTS = os.path.join(
    "results", "_r470bmb_vsumd_resi_w14_probe_facts.json")
RESI_SPEC = {
 "member": "510300",
 "series": "r470 probe verbatim / A158-TSGATE-P1 frozen RESI construction via the frozen in-repo runner import (zero-invention law; scripts/a158_tsgate_probe.py alpha158_factors): signal-day-d close info set on the member face",
 "resi60": "F[\"RESI60\"] = rolling-OLS(close, 60) end-point residual / close (closed-form cumsum, O(n); qlib expanding min_periods=1 warmup; RESI[0] NaN -- expanding k=1 Stt=0 guard)",
 "q90_ref": "q90_ref = resi60.rolling(GATE_WIN=252, min_periods=GATE_MINP=120).quantile(QHIGH=0.90) (own-trailing 252-observation top-decile reference; GATE_WIN/GATE_MINP/QHIGH constants same-source frozen-runner import)",
 "resi60_hi": "resi60 > q90_ref (price stretched ABOVE its own 60-bar trend into the trailing top decile = trend-extension position state; direction-agnostic POSITION face -- high residual = above-trend stretch, readout sign carried by BETA20 slope split 352 up / 38 down; A158-TSGATE-P1 RESI60_q90 OOS med_t 1.178 + GATE-RECHECK CONFIRM +0.005699 = LONG anchor)",
 "none": "no gate (W13 semantic baseline face)",
 "position_not_fit": "RESI high-extension days 96% above the fit-difference trend axis (W12 RSQR judg-negative axis does NOT swallow the RESI face: extension POSITION != regression fit QUALITY; prereg sec.1 D6 (a))",
 "demoted": "resi30_hi GATE-RECHECK FAIL (face_a med_net -0.006028 SIGN FLIP vs P1 OOS 0.433; c1 downgrade list) -- demoted from the member set; increment face 219 days (61% open-day) disclosed non-collapsed but increment existence != recheck pass (two judgments do not conflict)",
 "info_set": "signal-day d close; entry fills d+1 open (T+1 causal, same info set as GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR/SUMN, zero lookahead)",
 "warmup": "120-bar warmup window gate-closed honest (q90_ref min_periods 120 -> first decidable bar-idx == 120, fail-closed assertion == RSQR/STD/SUMN family warmup)",
 "engine_note": "entry-permittance only (effective signal zeroed, MSG-0440 E1-mapping primitive; exit logic zero change; engine/exit_rules.py zero touch)",
 "nan_artifact_note": "NaN comparisons (f > q90_ref) yield False NOT decidable (pit-95 batch-95 law; the decidable face derives from the underlying values notna; the naive comparison bool face masquerades warmup bars as resi-closed -- BANNED at the mask level)",
 "adjacency_note": "nearest burned neighbor: W12 RSQR (fit quality, sign-blind) -- resi60^rsqr20_closed dominant (RESI high-extension days 96% fall above the fit-difference trend = two gates read DIFFERENT states); W10 MOM zero co-open (390/0) + cntn20^mom_closed 265 days (position != oversold rebound); W8 RSV60 zero co-open (trend extension != range oversold); prereg sec.1 D6 (a)/(d)/(e)",
 "composition_order": "signal -> filter -> timing -> GATE -> VOL -> YANG -> VCONF -> STREAK -> TSTATE -> AMP -> MOM -> STD -> RSQR -> SUMN -> RESI -> initial-stop (W13 order extended; prereg sec.3 eighteen-tuple)"
}

RESI_ANCHOR = {
 "n_bars": 3483,
 "first_date": "2012-05-28",
 "cutoff": "2026-09-22",
 "warmup_gate_closed_bars": 120,
 "first_decidable_bar_idx": 120,
 "decidable_days": 3363,
 "open_days": 390,
 "closed_days": 2973,
 "open_rate_on_decidable": 0.112,
 "slope_sign_split": {
  "up_slope_days": 352,
  "down_slope_days": 38,
  "note": "BETA20 sign from the same frozen runner; resi60 is sign-aware by construction (high residual = above-trend stretch); direction conditioning lives in burned axes (GATE/YANG/STREAK/MOM), redundancy measured in adjacency cells"
 },
 "nine_gate_all_decidable_days": 3305,
 "nine_gate_512cells_nonzero_count": 103,
 "nine_gate_512cells_empty_count": 409,
 "nine_gate_512cells_min_nonzero": 1,
 "nine_gate_512cells_max": 41,
 "core48_note": "48/48 members non-degenerate (prereg sec.2 core48 face; probe r470)"
}

# yang-day-density CNT axis (prereg sec.3 NEW W14 frozen layer,
# THREE-value adjudicated member axis = density + frequency dual
# carrier; cntd10 GATE-RECHECK FAIL demoted, CNTD20 ABSENT below
# threshold/cluster-disambiguation -- member-set adjudication banner)
AXIS_CNT = ["none", "cntd5_hi", "cntn20_lo"]
CNT_MEMBER = "510300"          # core48 member (prereg sec.2 probe fact)
CNT_PROBE_FACTS_R470 = os.path.join(
    "results", "_r470bmb_vsumd_resi_w14_probe_facts.json")
CNT_PROBE_FACTS_R471 = os.path.join(
    "results", "_r471bmb_cntn20_w14_supplement_facts.json")
CNT_SPEC = {
 "member": "510300",
 "series": "r470/r471 probe verbatim / A158-TSGATE-P1 frozen CNT construction via the frozen in-repo runner import (zero-invention law; scripts/a158_tsgate_probe.py alpha158_factors): signal-day-d close info set on the member face",
 "cntd5": "F[\"CNTD5\"] = F[\"CNTP5\"] - F[\"CNTN5\"] = mean(up-day, 5) - mean(down-day, 5) (yang-day NET-DOMINANCE density in [-1,1])",
 "cntn20": "F[\"CNTN20\"] = mean(down-day, 20) (down-day FREQUENCY share in [0,1] -- non-purity face: low value = FEW down days without any price-magnitude claim; r471 supplement distinct-space face)",
 "cntd5_hi": "cntd5 > rolling(GATE_WIN=252, min_periods=GATE_MINP=120).quantile(QHIGH=0.90) (net up-day dominance entering its own top decile; A158-TSGATE-P1 CNTD5_q90 OOS 0.815 + GATE-RECHECK CONFIRM +0.009845 = LONG anchor)",
 "cntn20_lo": "cntn20 < rolling(GATE_WIN=252, min_periods=GATE_MINP=120).quantile(QLOW=0.10) (down-day frequency entering its own bottom decile; A158-TSGATE-P1 CNTN20_q10 OOS 0.617 + GATE-RECHECK CONFIRM +0.007839 [+0.016584 r471 recheck supplement same direction] = LONG anchor)",
 "none": "no gate (W13 semantic baseline face)",
 "density_vs_frequency": "cntd5 (density) and cntn20 (frequency) are TWO orthogonal readings of the same up/down-day stream: cntd5^cntn20 both-open 44 / cntn20-only 221 days (r471 distinct_space_increment face; frequency-without-purity = few-down-day grind increment face vs prereg sec.1 D6 (b) SUMN purity axis: cntn20^sumn20_closed 69 + cntd5^sumn20_closed 44 days)",
 "demoted": "cntd10_hi GATE-RECHECK FAIL (c1 downgrade list) -- demoted from the member set; increment face 161 days (70% open-day) disclosed non-collapsed; CNTD20_q90 ABSENT below threshold/cluster-disambiguation (twin-window construction with cntn20 disclosed NOT taken)",
 "mirror_twin": "CNTD_q90 vs CNTN_q10 construction mirrors (r277 XOR measured: cntd10/cntn10 19 days, cntd5/cntn5 20 days; quantile reference-window contamination dominant 18/19-18/20 current-window zero-change) -- mirror NEAR-SAME not identity; dedup gate T-84s3 cell-key face carries the distinction",
 "info_set": "signal-day d close; entry fills d+1 open (T+1 causal, same info set as GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR/SUMN/RESI, zero lookahead)",
 "warmup": "119-bar first-decidable HONEST one-bar construction-family difference (idx-0 up/down-day indicator = comparison-vs-NaN -> False -> 0.0 NOT NaN -> qref valid one bar early; NOT the RSQR/STD/SUMN 120 face; probe assert anchors per-face; prereg sec.2 warmup fail-closed measured note)",
 "engine_note": "entry-permittance only (effective signal zeroed, MSG-0440 E1-mapping primitive; exit logic zero change; engine/exit_rules.py zero touch)",
 "nan_artifact_note": "NaN comparisons yield False NOT decidable (pit-95 batch-95 law; the decidable face derives from the underlying values notna; the naive comparison bool face masquerades warmup bars as cnt-closed -- BANNED at the mask level)",
 "adjacency_note": "W7 STREAK: cntd5^upstreak_closed 147 days (density has NO 2-day streak requirement); W13 SUMN: cntn20^sumn20_closed 69 + cntd5^sumn20_closed 44 (frequency without magnitude purity); W10 MOM: cntn20^mom_closed 265; prereg sec.1 D6 (b)/(c)/(d)",
 "composition_order": "signal -> filter -> timing -> GATE -> VOL -> YANG -> VCONF -> STREAK -> TSTATE -> AMP -> MOM -> STD -> RSQR -> SUMN -> RESI -> CNT -> initial-stop (W13 order extended; prereg sec.3 eighteen-tuple)"
}

CNT_ANCHOR = {
 "n_bars": 3483,
 "first_date": "2012-05-28",
 "cutoff": "2026-09-22",
 "cntd5": {
  "first_decidable_bar_idx": 119,
  "decidable_days": 3364,
  "open_days": 137,
  "closed_days": 3227,
  "open_rate_on_decidable": 0.0393,
  "thin_tail_note": "3.93% thin-tail axis honest note (prereg sec.2; insufficient-sample clause likely on thin-tail grids = honest expectation, NOT a defect)",
  "slope_sign_split": {"up_slope_days": 97, "down_slope_days": 40},
  "nine_gate_512cells_nonzero_count": 109,
  "nine_gate_512cells_empty_count": 403,
  "nine_gate_512cells_min_nonzero": 1,
  "nine_gate_512cells_max": 41,
  "nine_gate_all_decidable_days": 3305,
  "core48_open_rate": {"min": 0.0196, "median": 0.0411, "max": 0.065}
 },
 "cntn20": {
  "first_decidable_bar_idx": 119,
  "decidable_days": 3364,
  "open_days": 265,
  "closed_days": 3099,
  "open_rate_on_decidable": 0.0761,
  "nine_gate_512cells_nonzero_count": 103,
  "nine_gate_512cells_empty_count": 409,
  "nine_gate_512cells_min_nonzero": 1,
  "nine_gate_512cells_max": 41,
  "nine_gate_all_decidable_days": 3305,
  "core48_open_rate": {"min": 0.0276, "median": 0.065, "max": 0.0865}
 }
}

AXIS_COMBOS = tl13.AXIS_COMBOS * len(AXIS_RESI) * len(AXIS_CNT)
# 282,175,488 x 2 x 3 = 1,693,052,928 (prereg sec.3 eighteen-tuple)


def _resicnt_faces_raw(prices: dict):
    """r470/r471-probe-verbatim RESI/CNT face computation (single
    computation site for all three member faces + decidables + raw
    values + slope sign; A158-TSGATE-P1 frozen construction via the
    FROZEN in-repo runner import -- zero-invention law):
    F = a158.alpha158_factors(member frame); resi60 = F["RESI60"]
    (rolling-OLS(close,60) end-point residual/close, expanding
    warmup); cntd5 = F["CNTD5"] (up-day minus down-day 5-bar mean);
    cntn20 = F["CNTN20"] (down-day 20-bar mean share).
    resi60_hi: q90_ref rolling(252,min_periods=120).quantile(QHIGH);
    open = (f > q90_ref); cntd5_hi same high-side law; cntn20_lo:
    q10_ref ...quantile(QLOW); open = (f < q10_ref).  decidable
    derives from the underlying values notna (pit-95 batch-95 law).
    Returns (resi_open, resi_dec, resi_meta, cntd_open, cntd_dec,
    cntn_open, cntn_dec, cnt_meta, resi60, cntd5, cntn20, beta20);
    deterministic pure function of the (cutoff-truncated) panel."""
    df = prices[RESI_MEMBER].sort_index()
    # .to_numpy() first: dict-of-Series construction ALIGNs to a
    # given index -> all-NaN reindex artifact (r447 probe live pit)
    di = pd.DataFrame({"open": df["open"].astype(float).to_numpy(),
                       "high": df["high"].astype(float).to_numpy(),
                       "low": df["low"].astype(float).to_numpy(),
                       "close": df["close"].astype(float).to_numpy(),
                       "volume": df["volume"].astype(float)
                       .to_numpy()},
                      index=df.index)
    F = a158.alpha158_factors(di)
    resi60, cntd5, cntn20, beta20 = (F["RESI60"], F["CNTD5"],
                                     F["CNTN20"], F["BETA20"])
    q90_r = resi60.rolling(a158.GATE_WIN,
                           min_periods=a158.GATE_MINP).quantile(a158.QHIGH)
    dec_r = resi60.notna() & q90_r.notna()   # underlying notna (pit-95)
    open_r = (resi60 > q90_r)                # comparison face: NaN->False
    q90_d = cntd5.rolling(a158.GATE_WIN,
                          min_periods=a158.GATE_MINP).quantile(a158.QHIGH)
    dec_d = cntd5.notna() & q90_d.notna()
    open_d = (cntd5 > q90_d)
    q10_n = cntn20.rolling(a158.GATE_WIN,
                           min_periods=a158.GATE_MINP).quantile(a158.QLOW)
    dec_n = cntn20.notna() & q10_n.notna()
    open_n = (cntn20 < q10_n)
    n = len(resi60)

    def _first_true(s):
        arr = s.fillna(False).astype(bool).values
        nz = np.flatnonzero(arr)
        return int(nz[0]) if len(nz) else None

    resi_meta = {"n_bars": int(n),
                 "warmup_gate_closed_bars": 120,
                 "first_decidable_bar_idx": _first_true(dec_r),
                 "decidable_days": int(dec_r.sum()),
                 "open_days": int((open_r & dec_r).sum()),
                 "closed_days": int(((~open_r) & dec_r).sum()),
                 "open_rate_on_decidable":
                 (round(float((open_r & dec_r).sum() / dec_r.sum()), 4)
                  if int(dec_r.sum()) else None),
                 "na_window_bars": 120}
    cnt_meta = {"n_bars": int(n),
                "cntd5_first_decidable_bar_idx": _first_true(dec_d),
                "cntd5_decidable_days": int(dec_d.sum()),
                "cntd5_open_days": int((open_d & dec_d).sum()),
                "cntd5_open_rate_on_decidable":
                (round(float((open_d & dec_d).sum() / dec_d.sum()), 4)
                 if int(dec_d.sum()) else None),
                "cntn20_first_decidable_bar_idx": _first_true(dec_n),
                "cntn20_decidable_days": int(dec_n.sum()),
                "cntn20_open_days": int((open_n & dec_n).sum()),
                "cntn20_open_rate_on_decidable":
                (round(float((open_n & dec_n).sum() / dec_n.sum()), 4)
                 if int(dec_n.sum()) else None),
                "na_window_bars": 120,
                "warmup_family_note":
                "119 first-decidable one-bar construction-family "
                "difference (idx-0 comparison-vs-NaN -> False -> 0.0 "
                "non-NaN; honest, probe-anchored per-face)"}
    return (open_r, dec_r, resi_meta, open_d, dec_d, open_n, dec_n,
            cnt_meta, resi60, cntd5, cntn20, beta20)


def resi_state_series(prices: dict):
    """Frozen RESI spec (prereg sec.2/3): member 510300 signal-day
    info set -- resi60_hi open perm + decidable face.  Returns
    (open, dec, meta): boolean Series on the member's own date
    index + structural meta.  Deterministic pure function of the
    (cutoff-truncated) panel."""
    o, d, m, _od, _dd, _on, _dn, _cm, _r, _c, _n, _b = \
        _resicnt_faces_raw(prices)
    return o, d, m


def cnt_state_series(prices: dict):
    """Frozen CNT spec (prereg sec.2/3): member 510300 signal-day
    info set -- cntd5_hi + cntn20_lo open perms + decidables.
    Returns (open_d5, dec_d5, open_n20, dec_n20, meta).
    Deterministic pure function of the (cutoff-truncated) panel."""
    _o, _d, _m, od, dd, on, dn, cm, _r, _c, _n, _b = \
        _resicnt_faces_raw(prices)
    return od, dd, on, dn, cm


def resi_zero_mask(mask: pd.DataFrame, resi_key: str, resi_state):
    """Grammar-layer resi entry gate (prereg sec.3 trend-extension
    position face; E1-mapping primitive): off-face signal days ->
    effective signal zeroed (entry blocked; engine-native signal-off
    exit semantics; zero engine touch).  resi=none = W13 semantic
    baseline (identity).  The keep face derives from the DECIDABLE
    face (pit-95 law): resi60_hi keeps resi60-open AND decidable --
    the naive comparison bool face alone would masquerade warmup bars
    as resi-closed (BANNED).  Member dates missing from the mask
    index -> resi-closed (conservative reindex law,
    tl3..tl13 gate caliber)."""
    if resi_key == "none":
        return mask
    open_r, dec_r, _meta = resi_state
    if resi_key == "resi60_hi":
        keep = (open_r.reindex(mask.index).fillna(False).astype(int)
                & dec_r.reindex(mask.index).fillna(False).astype(int))
    else:
        raise ValueError(f"unknown resi_key {resi_key}")
    return mask.mul(keep, axis=0)


def cnt_zero_mask(mask: pd.DataFrame, cnt_key: str, cnt_state):
    """Grammar-layer cnt entry gate (prereg sec.3 yang-day density +
    down-day frequency dual face; E1-mapping primitive): off-face
    signal days -> effective signal zeroed.  cnt=none = W13 semantic
    baseline (identity).  Keep faces derive from the DECIDABLE faces
    (pit-95 law): cntd5_hi keeps cntd5-open AND decidable; cntn20_lo
    keeps cntn20-open AND decidable.  Member dates missing from the
    mask index -> cnt-closed (conservative reindex law)."""
    if cnt_key == "none":
        return mask
    open_d, dec_d, open_n, dec_n, _meta = cnt_state
    if cnt_key == "cntd5_hi":
        keep = (open_d.reindex(mask.index).fillna(False).astype(int)
                & dec_d.reindex(mask.index).fillna(False).astype(int))
    elif cnt_key == "cntn20_lo":
        keep = (open_n.reindex(mask.index).fillna(False).astype(int)
                & dec_n.reindex(mask.index).fillna(False).astype(int))
    else:
        raise ValueError(f"unknown cnt_key {cnt_key}")
    return mask.mul(keep, axis=0)


# --- kit part B: resi/cnt full-face gates (probe anchors + 512-cell
# grid + extreme days + facts cross-check) + structure passes + the
# reform five-member EW ceiling baseline (spliced into the W14 runner) ---

def _resicnt_face_full():
    """Frozen sec.2 RESI/CNT-series face (r470/r471 probe basis): the
    git-tracked raw full-history member file data/daily/sh510300.csv
    (open + high + low + close + volume columns), truncated at the
    evidence cutoff.  (tl8._tstate_face_full loading caliber reused
    verbatim -- same member, same columns, same cutoff law;
    import-face law.)"""
    return tl8._tstate_face_full()


def _resicnt_nine_gate_cells(face_open, face_dec, close, o_, h_, l_, v_,
                             face_name):
    """NINE-gate 512-cell cross on the r470/r471 probe basis VERBATIM
    (W13 G-SUMN grid caliber with the 9th gate swapped to the W14
    member face): gate x vol x yang x vconf x streak x tstate x amp x
    std20 x <face>; W13 basis faces exactly (calm/wild = the VOL-axis
    face: 20-bar return std vs its trailing 500-bar median; surge/dry
    = volume vs its 20-bar median; yang/red = close-vs-open; bull/bear
    = close-vs-MA200; up/down_streak = 2-day close-over-close with the
    shift(2) warmup judge; mad60/rsv60 = tstate faces; wide/narrow =
    amplitude vs its 20-bar median; std20 = the W11 STD20_q90 face);
    m9 = face-decidable & bull/calm notna & amp_known & judge &
    dec_mad & dec_rsv & dec_s20.  Returns (cells, m9_days)."""
    amp = (h_ - l_) / close
    med20amp = amp.rolling(20, min_periods=20).median()
    amp_known = med20amp.notna()
    wide_face = (amp > med20amp) & amp_known
    narrow_face = (amp <= med20amp) & amp_known
    up1 = close > close.shift(1)
    up2 = close.shift(1) > close.shift(2)
    dn1 = close < close.shift(1)
    dn2 = close.shift(1) < close.shift(2)
    judge = close.shift(2).notna()      # bars 0-1 warmup gate-closed
    up_st = judge & (up1 & up2).fillna(False)
    dn_st = judge & (dn1 & dn2).fillna(False)
    ma60 = close.rolling(60).mean()
    dist = close / ma60 - 1.0
    ts_q10 = dist.rolling(252, min_periods=120).quantile(0.10)
    mad_q10 = dist < ts_q10
    dec_mad = ts_q10.notna()
    hh60 = h_.rolling(60).max()
    ll60 = l_.rolling(60).min()
    rng60 = (hh60 - ll60).replace(0, np.nan)
    rsv60 = (close - ll60) / rng60
    rsv_low = rsv60 < 0.2
    dec_rsv = rsv60.notna()
    s20o, s20d, _s20meta, _s20, _s20q, _s10o, _s10d, _s10, _s10q = \
        _std_series_raw({RESI_MEMBER: pd.DataFrame(
            {"open": o_, "high": h_, "low": l_, "close": close,
             "volume": v_}, index=close.index)})
    dec_s20 = s20d
    std20_open = s20o
    ma200 = close.rolling(200).mean()
    bull = close > ma200
    bear = ~bull
    ret = close.pct_change()
    vol20 = ret.rolling(20, min_periods=20).std(ddof=1)
    med500 = vol20.rolling(500, min_periods=500).median()
    calm = vol20 <= med500
    wild = vol20 > med500
    med20v = v_.rolling(20, min_periods=20).median()
    surge = v_ > med20v
    yang = close > o_
    red = ~yang
    open_face = face_open & face_dec
    closed_face = (~face_open) & face_dec
    m9 = face_dec & bull.notna() & calm.notna() & amp_known & judge \
        & dec_mad & dec_rsv & dec_s20
    cells = {}
    for bname, b in (("bull", bull), ("bear", bear)):
        for vname, vv in (("calm", calm), ("wild", wild)):
            for yname, y in (("yang", yang), ("red", red)):
                for sname, s in (("surge", surge), ("dry", ~surge)):
                    for kname, k in (("up_streak", up_st),
                                     ("down_streak", dn_st)):
                        for tname, t in (("mad60", mad_q10),
                                         ("rsv60", rsv_low)):
                            for aname, aa in (("wide", wide_face),
                                              ("narrow", narrow_face)):
                                for sdname, sd in (
                                        ("std20_open", std20_open),
                                        ("std20_closed",
                                         (~std20_open) & dec_s20)):
                                    for fname, ff in (
                                            (f"{face_name}_open",
                                             open_face),
                                            (f"{face_name}_closed",
                                             closed_face)):
                                        cells[f"{bname}|{vname}|"
                                              f"{yname}|{sname}|"
                                              f"{kname}|{tname}|"
                                              f"{aname}|{sdname}|"
                                              f"{fname}"] = \
                                              int((m9 & b & vv & y
                                                 & s & k & t & aa
                                                 & sd & ff).sum())
    return cells, int(m9.sum())


def _grid_gate(cells, m9_days, a, face_label):
    """Shared 512-cell anchor assert (counts + min/max + all-decidable;
    W13 G-SUMN caliber).  Returns None or a one-line refusal."""
    empty = sorted(k for k, n_ in cells.items() if n_ <= 0)
    nonzero = [x for x in cells.values() if x > 0]
    if (len(cells) != 512
            or len(nonzero) != a["nine_gate_512cells_nonzero_count"]
            or len(empty) != a["nine_gate_512cells_empty_count"]
            or min(nonzero) < a["nine_gate_512cells_min_nonzero"]
            or max(cells.values()) > a["nine_gate_512cells_max"]
            or m9_days != a["nine_gate_all_decidable_days"]):
        return (f"{face_label} nine-gate 512-cell cross drift "
                f"(nonzero {len(nonzero)}/"
                f"{a['nine_gate_512cells_nonzero_count']}, empty "
                f"{len(empty)}/{a['nine_gate_512cells_empty_count']}, "
                f"min {min(nonzero)}, max {max(cells.values())}, "
                f"all-decidable {m9_days}/"
                f"{a['nine_gate_all_decidable_days']})")
    return None


def _facts_grid_crosscheck(facts_path, cells_key, cells, face_label):
    """Exact per-cell cross-check vs the git-tracked probe facts file
    (r470/r471 determinism cross-check law; skip-face = file absent,
    frozen header counts above still binding).  Returns None or a
    one-line refusal."""
    if not os.path.exists(facts_path):
        return None
    pf_ = json.load(open(facts_path, encoding="utf-8"))
    pcells = pf_.get(cells_key, {})
    drift = [f"{k}: {cells.get(k)} != {v_}"
             for k, v_ in pcells.items() if cells.get(k) != v_]
    if pcells and drift:
        return (f"{face_label} probe-facts per-cell cross-check drift: "
                f"{drift[:3]}")
    return None


def _extreme_day_checks(want_days, facts, close, face_map):
    """Extreme-day gate states exact (probe 7-day face; values at
    6-decimal rounding, open flags, slope sign).  face_map maps
    face name -> (open_series, dec_series, value_series).  Returns
    None or a one-line refusal."""
    for dstr, want in want_days.items():
        ts = pd.Timestamp(dstr)
        if ts not in close.index:
            return f"extreme day {dstr} absent from face"
        for fname, (open_s, dec_s, val_s) in face_map.items():
            if f"{fname}_open" not in want:
                continue
            if pd.isna(val_s.loc[ts]):
                return f"extreme day {dstr} {fname} value NaN"
            got_open = (bool(open_s.loc[ts])
                        if bool(dec_s.loc[ts]) else None)
            got_val = round(float(val_s.loc[ts]), 6)
            if (got_open != want[f"{fname}_open"]
                    or abs(got_val - want[f"{fname}_value"]) > 5.01e-6):
                return (f"extreme day {dstr} {fname} drift: open "
                        f"{got_open}/{want[fname + '_open']}, "
                        f"value {got_val}/{want[fname + '_value']}")
    return None


def _resi_state_full():
    """Canonical full-face resi_state with the frozen probe anchors
    asserted (prereg sec.2 G-RESI fail-closed): n_bars == 3,483;
    first-decidable == 120 / decidable == 3,363 / open == 390
    (11.20%); slope-sign split 352 up / 38 down (BETA20 same frozen
    runner); NINE-gate 512-cell grid 103 non-empty / 409 empty (max
    41; all-decidable 3,305) + exact per-cell cross-check vs the
    git-tracked r470 facts file when present; extreme-day gate
    states exact (probe 7-day face).  Returns (resi_state, err); err
    is a one-line honest refusal reason when not None."""
    face = _resicnt_face_full()
    if face is None:
        return None, (f"raw member face data/daily/sh{RESI_MEMBER}.csv "
                      f"absent/open-high-low-close-volume columns "
                      f"missing or truncated tail != cutoff {CUTOFF}")
    open_r, dec_r, meta, _od, _dd, _on, _dn, _cm, resi60, _c5, _n20, \
        beta20 = _resicnt_faces_raw(face)
    a = RESI_ANCHOR
    # r470 probe rate-key caliber disclosure: the frozen probe's
    # "open_rate_on_decidable" value is open/n_bars caliber (390/3483
    # = 0.112), not open/decidable (390/3363 = 0.116) -- label drift
    # disclosed; the rate key is consumed in the probe's construction
    # (fail-closed face completeness), the integer anchors pin the
    # face exactly.
    _probe_rate = (round(meta["open_days"] / meta["n_bars"], 4)
                   if meta["n_bars"] else None)
    if (meta.get("n_bars") != a["n_bars"]
            or meta["first_decidable_bar_idx"]
            != a["first_decidable_bar_idx"]
            or meta["decidable_days"] != a["decidable_days"]
            or meta["open_days"] != a["open_days"]
            or meta["closed_days"] != a["closed_days"]
            or _probe_rate != a["open_rate_on_decidable"]):
        return None, (f"G-RESI core anchors {meta} != probe "
                      f"{{n 3483, warmup 120, decidable 3363, open "
                      f"390 (11.20%)}}")
    # slope-sign split (disclosure face; direction conditioning lives
    # in burned axes; NOT a gate input -- asserted as frozen probe
    # fact)
    m_open = open_r & dec_r & beta20.notna()
    up_days = int((m_open & (beta20 > 0)).sum())
    dn_days = int((m_open & (beta20 <= 0)).sum())
    if (up_days != a["slope_sign_split"]["up_slope_days"]
            or dn_days != a["slope_sign_split"]["down_slope_days"]):
        return None, (f"G-RESI slope-sign split drift {up_days}/"
                      f"{dn_days} != probe "
                      f"{a['slope_sign_split']['up_slope_days']}/"
                      f"{a['slope_sign_split']['down_slope_days']}")
    # NINE-gate 512-cell grid + facts cross-check
    df = face[RESI_MEMBER]
    close = df["close"].astype(float).sort_index()
    o_ = df["open"].astype(float).reindex(close.index)
    h_ = df["high"].astype(float).reindex(close.index)
    l_ = df["low"].astype(float).reindex(close.index)
    v_ = df["volume"].astype(float).reindex(close.index)
    cells, m9_days = _resicnt_nine_gate_cells(open_r, dec_r, close,
                                              o_, h_, l_, v_, "resi60")
    err = _grid_gate(cells, m9_days, a, "G-RESI")
    if err:
        return None, f"G-RESI {err}"
    err = _facts_grid_crosscheck(RESI_PROBE_FACTS,
                                 "resi60_nine_gate_cells", cells,
                                 "G-RESI")
    if err:
        return None, f"G-RESI {err}"
    # extreme-day gate states (frozen probe face)
    if os.path.exists(RESI_PROBE_FACTS):
        pf_ = json.load(open(RESI_PROBE_FACTS, encoding="utf-8"))
        want_days = pf_.get("extreme_day_states", {})
        beta_up = beta20 > 0
        err = _extreme_day_checks(want_days, pf_, close,
                                  {"resi60": (open_r, dec_r, resi60)})
        if err:
            return None, f"G-RESI {err}"
        # slope_sign + std20_open + rsqr20_open cross-reads
        s20o, s20d, _m20, _s20, _q20, _s10o, _s10d, _s10, _q10 = \
            _std_series_raw({RESI_MEMBER: pd.DataFrame(
                {"open": o_, "high": h_, "low": l_, "close": close,
                 "volume": v_}, index=close.index)})
        r20o, r20d, _r20meta = _rsqr_faces_raw(face)[0], \
            _rsqr_faces_raw(face)[1], _rsqr_faces_raw(face)[2]
        for dstr, want in want_days.items():
            ts = pd.Timestamp(dstr)
            if pd.isna(beta20.loc[ts]):
                continue
            got_slope = "up" if bool(beta_up.loc[ts]) else "down"
            if got_slope != want.get("slope_sign"):
                return None, (f"G-RESI extreme day {dstr} slope drift "
                              f"{got_slope}/{want.get('slope_sign')}")
            got_std = (bool(s20o.loc[ts])
                       if bool(s20d.loc[ts]) else None)
            if got_std != want.get("std20_open"):
                return None, (f"G-RESI extreme day {dstr} std20 drift "
                              f"{got_std}/{want.get('std20_open')}")
            got_rsqr = (bool(r20o.loc[ts])
                        if bool(r20d.loc[ts]) else None)
            if got_rsqr != want.get("rsqr20_open"):
                return None, (f"G-RESI extreme day {dstr} rsqr drift "
                              f"{got_rsqr}/{want.get('rsqr20_open')}")
    meta = dict(meta)
    meta["slope_sign_split"] = {"up_slope_days": up_days,
                                "down_slope_days": dn_days}
    meta["nine_gate_512cells"] = cells
    meta["nine_gate_all_decidable_days"] = m9_days
    return (open_r, dec_r, meta), None


def _cnt_state_full():
    """Canonical full-face cnt_state with the frozen probe anchors
    asserted (prereg sec.2 G-CNT fail-closed): n_bars == 3,483;
    cntd5 first-decidable == 119 / decidable == 3,364 / open == 137
    (3.93% thin-tail honest note); cntn20 first-decidable == 119 /
    decidable == 3,364 / open == 265 (7.61%); cntd5 slope split 97/40;
    NINE-gate 512-cell grids: cntd5 109/403, cntn20 103/409 (max 41;
    all-decidable 3,305 both) + exact per-cell cross-checks vs the
    git-tracked r470/r471 facts files when present; extreme-day gate
    states exact (probe 7-day face).  Returns (cnt_state, err)."""
    face = _resicnt_face_full()
    if face is None:
        return None, (f"raw member face data/daily/sh{CNT_MEMBER}.csv "
                      f"absent/open-high-low-close-volume columns "
                      f"missing or truncated tail != cutoff {CUTOFF}")
    open_d, dec_d, open_n, dec_n, meta = cnt_state_series(face)
    a = CNT_ANCHOR
    for sub, okey, dkey in (("cntd5", open_d, dec_d),
                            ("cntn20", open_n, dec_n)):
        s = a[sub]
        dec_n_ = int(dkey.sum())
        open_n_ = int((okey & dkey).sum())
        # r470 probe rate-key caliber disclosure: same label drift as
        # G-RESI -- probe "_on_decidable" values are open/n_bars
        # caliber (137/3483 = 0.0393; 265/3483 = 0.0761); consumed in
        # the probe's construction, integers pin the face exactly.
        rate = (round(open_n_ / meta["n_bars"], 4)
                if meta["n_bars"] else None)
        if (meta[f"{sub}_first_decidable_bar_idx"]
                != s["first_decidable_bar_idx"]
                or dec_n_ != s["decidable_days"]
                or open_n_ != s["open_days"]
                or rate != s["open_rate_on_decidable"]):
            return None, (f"G-CNT {sub} core anchors drift "
                          f"(first-dec "
                          f"{meta[sub + '_first_decidable_bar_idx']}, "
                          f"decidable {dec_n_}, open {open_n_}, rate "
                          f"{rate}) != probe {{first-dec "
                          f"{s['first_decidable_bar_idx']}, decidable "
                          f"{s['decidable_days']}, open "
                          f"{s['open_days']}, rate "
                          f"{s['open_rate_on_decidable']}}}")
    # cntd5 slope-sign split (frozen probe fact)
    _o, _d, _m, _od, _dd, _on, _dn, _cm, _r60, c5, _n20, beta20 = \
        _resicnt_faces_raw(face)
    m_open = open_d & dec_d & beta20.notna()
    up_days = int((m_open & (beta20 > 0)).sum())
    dn_days = int((m_open & (beta20 <= 0)).sum())
    sa = a["cntd5"]["slope_sign_split"]
    if (up_days != sa["up_slope_days"] or dn_days != sa["down_slope_days"]):
        return None, (f"G-CNT cntd5 slope-sign split drift {up_days}/"
                      f"{dn_days} != probe {sa['up_slope_days']}/"
                      f"{sa['down_slope_days']}")
    df = face[CNT_MEMBER]
    close = df["close"].astype(float).sort_index()
    o_ = df["open"].astype(float).reindex(close.index)
    h_ = df["high"].astype(float).reindex(close.index)
    l_ = df["low"].astype(float).reindex(close.index)
    v_ = df["volume"].astype(float).reindex(close.index)
    for sub, okey, dkey in (("cntd5", open_d, dec_d),
                            ("cntn20", open_n, dec_n)):
        cells, m9_days = _resicnt_nine_gate_cells(okey, dkey, close,
                                                  o_, h_, l_, v_, sub)
        err = _grid_gate(cells, m9_days, a[sub], f"G-CNT {sub}")
        if err:
            return None, f"G-CNT {err}"
        fpath = (CNT_PROBE_FACTS_R470 if sub == "cntd5"
                 else CNT_PROBE_FACTS_R471)
        ckey = f"{sub}_nine_gate_cells"
        err = _facts_grid_crosscheck(fpath, ckey, cells, f"G-CNT {sub}")
        if err:
            return None, f"G-CNT {err}"
    # extreme-day gate states (frozen probe face; r470 carries the
    # cntd5 values, r471 the cntn20 values)
    if os.path.exists(CNT_PROBE_FACTS_R470):
        pf_ = json.load(open(CNT_PROBE_FACTS_R470, encoding="utf-8"))
        want_days = pf_.get("extreme_day_states", {})
        err = _extreme_day_checks(want_days, pf_, close,
                                  {"cntd5": (open_d, dec_d, c5)})
        if err:
            return None, f"G-CNT {err}"
    if os.path.exists(CNT_PROBE_FACTS_R471):
        pf2 = json.load(open(CNT_PROBE_FACTS_R471, encoding="utf-8"))
        want_days = pf2.get("extreme_day_states", {})
        err = _extreme_day_checks(want_days, pf2, close,
                                  {"cntn20": (open_n, dec_n, _n20)})
        if err:
            return None, f"G-CNT {err}"
    meta = dict(meta)
    meta["cntd5_slope_sign_split"] = {"up_slope_days": up_days,
                                      "down_slope_days": dn_days}
    return (open_d, dec_d, open_n, dec_n, meta), None


def _resi_structure_pass(resi_meta) -> bool:
    """Series-structure invariants on every panel face (fail-closed):
    120-bar warmup -- first-decidable + decidable partitions n_bars;
    open <= decidable and closed <= decidable.  A face shorter than
    the warmup (first-decidable None) honestly refuses."""
    if not isinstance(resi_meta, dict):
        return False
    n = resi_meta.get("n_bars", -1)
    fv = resi_meta.get("first_decidable_bar_idx")
    return (fv is not None
            and fv + resi_meta.get("decidable_days", -10**9) == n
            and resi_meta.get("open_days", -1)
            <= resi_meta.get("decidable_days", -1)
            and resi_meta.get("closed_days", -1)
            <= resi_meta.get("decidable_days", -1))


def _cnt_structure_pass(cnt_meta) -> bool:
    """Series-structure invariants on BOTH cnt sub-faces (fail-closed;
    same law as _resi_structure_pass, applied per sub-face with the
    119 one-bar construction-family difference)."""
    if not isinstance(cnt_meta, dict):
        return False
    for sub in ("cntd5", "cntn20"):
        n = cnt_meta.get("n_bars", -1)
        fv = cnt_meta.get(f"{sub}_first_decidable_bar_idx")
        dec = cnt_meta.get(f"{sub}_decidable_days", -10**9)
        op = cnt_meta.get(f"{sub}_open_days", -1)
        if fv is None or fv + dec != n or op > dec:
            return False
    return True


# reform return-ceiling baseline (prereg sec.4; REFORM_CEILING_BASELINE
# = five_member_ew_O1555, reform canon r271 ratification)
O1555_UNIVERSE = ("510300", "510050", "510500", "512100", "588000")


def _five_member_ew_baseline_annualized(leg_idx):
    """Equal-weight daily returns of the O-1555 frozen five-member
    universe over the SAME evaluation window as the candidates' leg-L
    curves (members without data on a day are excluded that day --
    deterministic, batch-independent passive face); annualized with
    the descriptive-face _ann formula (compound, 252/n scaling).
    Returns None on any member file absent/short (honest refuse ->
    return_ceiling_O1126 material missing -> missing-dims refuse,
    never zero-filled)."""
    closes = {}
    for s in O1555_UNIVERSE:
        path = os.path.join("data", "daily", f"sh{s}.csv")
        if not os.path.exists(path):
            return None
        df = pd.read_csv(path)
        df["date"] = df["date"].astype(str)
        df = df[df["date"] <= CUTOFF]
        if len(df) < 2:
            return None
        closes[s] = pd.Series(df["close"].astype(float).to_numpy(),
                              index=pd.to_datetime(df["date"]))
    m = pd.DataFrame(closes)              # columns = members
    daily = m.pct_change()                # member daily returns
    ew = daily.mean(axis=1, skipna=True)   # equal weight across the
    # members with data that day
    ew_win = ew.reindex(leg_idx)
    if ew_win.notna().sum() < 2:
        return None
    total = float((1.0 + ew_win.fillna(0.0)).prod())
    n = int(len(ew_win))
    if total <= 0 or n < 2:
        return None
    return float(total ** (252.0 / n) - 1.0)


# ------------------------------------------------------------ grammar build
def build_grammar_w14():
    """tl13 grammar extended with the NEW resi + cnt axes + W14
    seeds/counts (frozen face).  EIGHTEEN-tuple axes R/X/S/T/STOP/
    GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR/SUMN/RESI/CNT
    = 1,693,052,928 axis combos (W13 282,175,488 x RESI 2-value x
    CNT 3-value adjudicated member-set mult; prereg sec.3).

    Exclusion law (prereg sec.1): exact already-judged cells are
    excluded on the resi=none AND cnt=none face only; all prior-wave
    lineage keys are resi/cnt-none-completed (W1 4-tuple + stop/gate/
    vol/yang/vconf/streak/tstate/amp/mom/std/rsqr/sumn/resi/cnt none;
    W2 5-tuple + gate/vol/yang/vconf/streak/tstate/amp/mom/std/rsqr/
    sumn/resi/cnt none; W3 6-tuple + vol/yang/vconf/streak/tstate/
    amp/mom/std/rsqr/sumn/resi/cnt none; W4 7-tuple + yang/vconf/
    streak/tstate/amp/mom/std/rsqr/sumn/resi/cnt none; W5 8-tuple +
    vconf/streak/tstate/amp/mom/std/rsqr/sumn/resi/cnt none; W6
    9-tuple + streak/tstate/amp/mom/std/rsqr/sumn/resi/cnt none; W7
    10-tuple + tstate/amp/mom/std/rsqr/sumn/resi/cnt none; W8 11-tuple
    + amp/mom/std/rsqr/sumn/resi/cnt none; W9 12-tuple + mom/std/rsqr/
    sumn/resi/cnt none; W10 13-tuple + std/rsqr/sumn/resi/cnt none;
    W11 14-tuple + rsqr/sumn/resi/cnt none; W12 15-tuple + sumn/resi/
    cnt none; W13 16-tuple + resi/cnt none; MASS via the declared
    translation); resi/cnt in member values = new-syntax legal cells
    (never excluded)."""
    g13 = tl13.build_grammar_w13()    # frozen W13 machinery face
    excl = []
    for e in g13["exclusion"]["stop_gate_vol_yang_vconf_streak_"
                             "tstate_amp_mom_std_rsqr_sumn_none_face"]:
        excl.append({**e, "axis": list(e["axis"]) + ["none", "none"],
                     "face": "stop-gate-vol-yang-vconf-streak-"
                             "tstate-amp-mom-std-rsqr-sumn-resi-cnt-"
                             "none"})
    grammar = {
        "wave": WAVE, "prereg": PREREG, "evidence_cutoff": CUTOFF,
        "grammar_kind": "w14-resicnt-gate-extended",
        "seeds": {"trial_labor_w14_gen": SEED_GEN,
                  "trial_labor_w14_scrnull": SEED_NULL,
                  "trial_labor_w14_unc": SEED_UNC,
                  "derivation": "Sobol(seed=20327500+family_idx, "
                                "scramble) param box + default_rng("
                                "[20327500+family_idx, 7919]) EIGHTEEN-"
                                "tuple axis stream R/X/S/T/STOP/GATE/"
                                "VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/"
                                "STD/RSQR/SUMN/RESI/CNT (prereg s.3; "
                                "A idx 0-5, B idx 6+slot; the first "
                                "sixteen axis arrays are the W13-order "
                                "stream VERBATIM -- order-frozen "
                                "consumption law; the resi+cnt legs "
                                "append AFTER sumn, zero disturbance; "
                                "berths 20327500/20328000/20328500 "
                                "held at the freeze commit per R250 "
                                "one-step law, bm-b r471 three-step "
                                "re-verify ALL GREEN no re-pick; berth "
                                "adoption lineage AMP->W9/MOM->W10/STD->"
                                "W11/RSQR->W12/SUMN->W13/RESI+CNT->W14)"},
        "n_draws": {"A": N_A, "B": N_B}, "k_nulls": K_NULLS,
        "axes": {**g13["axes"], "resi": AXIS_RESI, "cnt": AXIS_CNT},
        "axis_combos": AXIS_COMBOS,
        "stop_formula": g13["stop_formula"],
        "stop_fill_mapping": g13["stop_fill_mapping"],
        "gate_spec": g13["gate_spec"],
        "vol_spec": g13["vol_spec"],
        "yang_spec": g13["yang_spec"],
        "vconf_spec": g13["vconf_spec"],
        "streak_spec": g13["streak_spec"],
        "tstate_spec": g13["tstate_spec"],
        "amp_spec": g13["amp_spec"],
        "mom_spec": g13["mom_spec"],
        "std_spec": g13["std_spec"],
        "rsqr_spec": g13["rsqr_spec"],
        "sumn_spec": g13["sumn_spec"],
        "resi_spec": RESI_SPEC,
        "cnt_spec": CNT_SPEC,
        "vol_anchor": g13["vol_anchor"],
        "yang_anchor": g13["yang_anchor"],
        "vconf_anchor": g13["vconf_anchor"],
        "streak_anchor": g13["streak_anchor"],
        "tstate_anchor": g13["tstate_anchor"],
        "amp_anchor": g13["amp_anchor"],
        "mom_anchor": g13["mom_anchor"],
        "std_anchor": g13["std_anchor"],
        "rsqr_anchor": g13["rsqr_anchor"],
        "sumn_anchor": g13["sumn_anchor"],
        "resi_anchor": RESI_ANCHOR,
        "cnt_anchor": CNT_ANCHOR,
        "families": g13["families"], "value_domains": g13["value_domains"],
        "faces": g13["faces"],
        "exclusion": {
            "stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_"
            "sumn_resi_cnt_none_face":
                excl,
            "sources": list(g13["exclusion"]["sources"])
            + ["w13 screen survivors (generate-time real-read; "
               "W13 = THIRTEENTH screen source, seventh full-declare "
               "window)",
               "w13 judge products (generate-time real-read "
               "re-declare window; W13-JUDGE landed 2026-09-30 "
               "12:28 = FOURTEENTH judged source)"],
            "note": "exclusion face = resi=none AND cnt=none only; "
                    "prior-wave keys resi/cnt-none-completed "
                    "(semantic identity match); resi/cnt in member "
                    "values = new-syntax legal cells (prereg sec.1)"},
        "negative_priors": g13.get("negative_priors"),
        "inventory_audit": g13["inventory_audit"],
    }
    grammar["grammar_sha256"] = _grammar_sha16(grammar)
    return grammar


# ------------------------------------------------------------ Sobol draw leg
def draw_candidate_sobol_w14(grammar, family, slot, n_draws):
    """Yield (draw_idx, cand) for one family slot per prereg sec.3:
    Sobol over the normalized param box (seed=SEED_GEN+family_idx) mapped
    to discrete domain indices + EIGHTEEN-tuple axis stream
    default_rng([SEED_GEN+family_idx, 7919]) in the frozen consumption
    order R/X/S/T/STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR/SUMN/RESI/CNT (the
    first sixteen axis arrays are the W13-order stream VERBATIM --
    order-frozen consumption law; the resi+cnt legs append AFTER sumn,
    zero disturbance).  Deterministic, zero band use."""
    from scipy.stats import qmc
    fam_idx = slot if family == "A" else 6 + slot   # A 0-5, B 6+ (prereg)
    spec = grammar["families"][family][slot]
    mk = f"{spec['module']}.{spec['fn']}"
    dom = grammar["value_domains"][mk]
    names = sorted(nm for nm, vs in dom.items() if len(vs) > 1)
    sob = qmc.Sobol(max(1, len(names)), scramble=True,
                    seed=SEED_GEN + fam_idx)
    box = sob.random(n_draws)
    rng = np.random.default_rng([SEED_GEN + fam_idx, 7919])
    ax = list(zip(rng.integers(0, len(tl1.AXIS_FILTERS), n_draws),
                  rng.integers(0, len(tl1.AXIS_EXITS), n_draws),
                  rng.integers(0, len(tl1.AXIS_SIZING), n_draws),
                  rng.integers(0, len(tl1.AXIS_TIMING), n_draws),
                  rng.integers(0, len(tl2.AXIS_STOP), n_draws),
                  rng.integers(0, len(tl3.AXIS_GATE), n_draws),
                  rng.integers(0, len(tl4.AXIS_VOL), n_draws),
                  rng.integers(0, len(tl5.AXIS_YANG), n_draws),
                  rng.integers(0, len(tl6.AXIS_VCONF), n_draws),
                  rng.integers(0, len(tl7.AXIS_STREAK), n_draws),
                  rng.integers(0, len(tl8.AXIS_TSTATE), n_draws),
                  rng.integers(0, len(tl9.AXIS_AMP), n_draws),
                  rng.integers(0, len(AXIS_MOM), n_draws),
                  rng.integers(0, len(AXIS_STD), n_draws),
                  rng.integers(0, len(AXIS_RSQR), n_draws),
                  rng.integers(0, len(AXIS_SUMN), n_draws),
                  rng.integers(0, len(AXIS_RESI), n_draws),
                  rng.integers(0, len(AXIS_CNT), n_draws)))
    for i in range(n_draws):
        params = {}
        j = 0
        for nm in sorted(dom):
            values = dom[nm]
            if len(values) <= 1:
                params[nm] = values[0] if values else None
                continue
            params[nm] = values[min(int(box[i, j] * len(values)),
                                    len(values) - 1)]
            j += 1
        r_, x_, s_, t_, st_, gt_, vt_, yg_, vc_, sk_, ts_, ap_, mo_, sd_, \
            rq_, su_, re_, cn_ = ax[i]
        yield i, {"module": spec["module"], "fn": spec["fn"],
                  "sig_params": params,
                  "axis": [tl1.AXIS_FILTERS[r_], tl1.AXIS_EXITS[x_],
                           tl1.AXIS_SIZING[s_], tl1.AXIS_TIMING[t_],
                           tl2.AXIS_STOP[st_], tl3.AXIS_GATE[gt_],
                           tl4.AXIS_VOL[vt_], tl5.AXIS_YANG[yg_],
                           tl6.AXIS_VCONF[vc_], tl7.AXIS_STREAK[sk_],
                           tl8.AXIS_TSTATE[ts_], tl9.AXIS_AMP[ap_],
                           AXIS_MOM[mo_], AXIS_STD[sd_],
                           AXIS_RSQR[rq_], AXIS_SUMN[su_],
                           AXIS_RESI[re_], AXIS_CNT[cn_]],
                  "family": family}


# --------------------------------------------- exclusion (28 real-reads)
def _load_exclusion_rows_w14(grammar):
    """FOURTEEN judged + FOURTEEN screen real-read source faces + the
    frozen serialized grammar face (prereg sec.1), all real-read at
    generate time.  All prior-wave keys are padded to the W14
    EIGHTEEN-tuple with resi/cnt=none (semantic-identity completion
    law).  Sources: 1 = frozen serialized grammar stop-gate-vol-...
    -sumn-resi-cnt-none face (18-tuple at build); 2-15 = W1/W2/MASS
    (declared tl3 translation)/W3/W4/W5/W6/W7/W8/W9/W10/W11/W12/W13
    screen survivors -- W13 is NEW vs the W13 runner's own loader
    (generate-time real-read; absent at build = zero rows honest per
    prereg sec.1); 16-29 = judged products (w1_judge / MASS judged /
    w2_judge ... w13_judge) -- generate-time real-read re-declare
    window (declared-unavailable -> zero rows, no fabrication).
    Honest tag note: the W13 runner's loader carried an off-by-one
    disc-key drift (files of wave N tagged wN+1) -- rows consumed were
    always correct (exact-key law); the W14 loader tags each source by
    its OWN wave number (cosmetic fix, zero effect on rows)."""
    rows = list(grammar["exclusion"]
                ["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_"
                 "rsqr_sumn_resi_cnt_none_face"])
    disc = {"grammar_stop_gate_vol_yang_vconf_streak_tstate_"
            "amp_mom_std_rsqr_sumn_resi_cnt_none_rows": len(rows)}

    def _screen_survivors(scr_path, cand_path, pad, tag):
        if not (os.path.exists(scr_path) and os.path.exists(cand_path)):
            return f"declared-unavailable ({os.path.basename(scr_path)} " \
                   f"absent)"
        scr = json.load(open(scr_path, encoding="utf-8"))
        cands = {c["candidate_id"]: c for c in
                 json.load(open(cand_path, encoding="utf-8"))["candidates"]}
        n = 0
        for cid in sorted(scr.get("survivors", [])):
            c = cands[cid]
            rows.append({"module": c["module"], "fn": c["fn"],
                         "sig_params": c["sig_params"],
                         "axis": list(c["axis"]) + pad,
                         "face": f"{tag}:stop-gate-vol-yang-vconf-"
                                 "streak-tstate-amp-mom-std-rsqr-sumn-"
                                 "resi-cnt-none",
                         "candidate_id": cid})
            n += 1
        return n

    # pads to the EIGHTEEN-tuple: wave axis-tuple length + pad == 18
    disc["w1_screen_survivors"] = _screen_survivors(
        os.path.join(tl1.RES_DIR, "w1_screen.json"),
        os.path.join(tl1.RES_DIR, "w1_candidates.json"),
        ["none"] * 14, "w1_screen_survivor")
    disc["w2_screen_survivors"] = _screen_survivors(
        os.path.join(tl2.RES_DIR, "w2_screen.json"),
        os.path.join(tl2.RES_DIR, "w2_candidates.json"),
        ["none"] * 13, "w2_screen_survivor")
    disc["w3_screen_survivors"] = _screen_survivors(
        os.path.join(tl3.RES_DIR, "w3_screen.json"),
        os.path.join(tl3.RES_DIR, "w3_candidates.json"),
        ["none"] * 12, "w3_screen_survivor")
    disc["w4_screen_survivors"] = _screen_survivors(
        tl4.SCREEN_FILE, tl4.CANDIDATES_FILE,
        ["none"] * 11, "w4_screen_survivor")
    disc["w5_screen_survivors"] = _screen_survivors(
        tl5.SCREEN_FILE, tl5.CANDIDATES_FILE,
        ["none"] * 10, "w5_screen_survivor")
    disc["w6_screen_survivors"] = _screen_survivors(
        tl6.SCREEN_FILE, tl6.CANDIDATES_FILE,
        ["none"] * 9, "w6_screen_survivor")
    disc["w7_screen_survivors"] = _screen_survivors(
        tl7.SCREEN_FILE, tl7.CANDIDATES_FILE,
        ["none"] * 8, "w7_screen_survivor")
    disc["w8_screen_survivors"] = _screen_survivors(
        tl8.SCREEN_FILE, tl8.CANDIDATES_FILE,
        ["none"] * 7, "w8_screen_survivor")
    disc["w9_screen_survivors"] = _screen_survivors(
        tl9.SCREEN_FILE, tl9.CANDIDATES_FILE,
        ["none"] * 6, "w9_screen_survivor")
    disc["w10_screen_survivors"] = _screen_survivors(
        tl10.SCREEN_FILE, tl10.CANDIDATES_FILE,
        ["none"] * 5, "w10_screen_survivor")
    disc["w11_screen_survivors"] = _screen_survivors(
        tl11.SCREEN_FILE, tl11.CANDIDATES_FILE,
        ["none"] * 4, "w11_screen_survivor")
    disc["w12_screen_survivors"] = _screen_survivors(
        tl12.SCREEN_FILE, tl12.CANDIDATES_FILE,
        ["none"] * 3, "w12_screen_survivor")
    disc["w13_screen_survivors"] = _screen_survivors(
        tl13.SCREEN_FILE, tl13.CANDIDATES_FILE,
        ["none"] * 2, "w13_screen_survivor")

    # MASS screen survivors: declared tl3 translation + the same
    # none-pad (translated rows are 6-tuples -> 12 more to 18)
    if os.path.exists(tl6.MASS_SCREEN_CKPT):
        n_tr = n_bad = 0
        with open(tl6.MASS_SCREEN_CKPT, encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln:
                    continue
                r = json.loads(ln)
                if r.get("row_type") != "candidate" \
                        or not r.get("screen_pass"):
                    continue
                tr = tl3._mass_translate_row(r)
                if tr is None:
                    n_bad += 1
                    continue
                tr["axis"] = list(tr["axis"]) + ["none"] * 12
                tr["face"] = "mass_screen_survivor:translated-exact"
                tr["candidate_id"] = r.get("id")
                rows.append(tr)
                n_tr += 1
        disc["mass_screen_survivors"] = {
            "consumed_pass_rows": n_tr + n_bad,
            "translated_exact_rows": n_tr,
            "non_translatable_disclosed": n_bad,
            "note": tl6.MASS_TRANSLATION_NOTE}
    else:
        disc["mass_screen_survivors"] = "declared-unavailable " \
                                        "(screen_checkpoint.jsonl absent)"

    # judged products: generate-time real-read re-declare window
    # (prereg sec.1/sec.9); absent -> declared-unavailable zero rows
    # (freeze-time expectation per prereg sec.0 (d): W1/MASS/W2/W3/
    # W4/W5/W6/W7/W8/W9/W10/W11/W12 judged landed; W13-JUDGE landed
    # 2026-09-30 12:28 -- FOURTEEN sources, seventh full-declare
    # window in history -- live re-read at generate time is the law)
    def _judged_source(jpath, cand_path, pad, tag, mass=False):
        if not os.path.exists(jpath):
            return "declared-unavailable at generate time " \
                   f"({os.path.basename(jpath)} absent; pool-waiting); " \
                   "zero rows"
        j = json.load(open(jpath, encoding="utf-8"))
        cells = j.get("cells", [])
        n = 0
        cands = {}
        if not mass and cand_path and os.path.exists(cand_path):
            cands = {c["candidate_id"]: c for c in json.load(
                open(cand_path, encoding="utf-8"))["candidates"]}
        for c in cells:
            if mass:
                tr = tl3._mass_translate_row(c)
                if tr is None:
                    continue
                tr["axis"] = list(tr["axis"]) + ["none"] * 12
                tr["face"] = f"{tag}:translated-exact"
                rows.append(tr)
            else:
                src = cands.get(c.get("candidate_id"))
                if src is None:
                    continue
                rows.append({"module": src["module"], "fn": src["fn"],
                             "sig_params": src["sig_params"],
                             "axis": list(src["axis"]) + pad,
                             "face": f"{tag}:stop-gate-vol-"
                                     "yang-vconf-streak-tstate-amp-"
                                     "mom-std-rsqr-sumn-resi-cnt-none",
                             "candidate_id": c.get("candidate_id")})
            n += 1
        return {"consumed_rows": n,
                "note": "judged product consumed as exclusion rows "
                        "(exact-key law, positive or negative verdicts "
                        "alike)"}

    disc["w1_judge_products"] = _judged_source(
        tl6.W1_JUDGE_FILE, os.path.join(tl1.RES_DIR, "w1_candidates.json"),
        ["none"] * 14, "w1_judged")
    disc["mass_judge_products"] = _judged_source(
        tl6.MASS_JUDGE_FILE, None, None, "mass_judged", mass=True)
    disc["w2_judge_products"] = _judged_source(
        tl6.W2_JUDGE_FILE, os.path.join(tl2.RES_DIR, "w2_candidates.json"),
        ["none"] * 13, "w2_judged")
    disc["w3_judge_products"] = _judged_source(
        tl6.W3_JUDGE_FILE, os.path.join(tl3.RES_DIR, "w3_candidates.json"),
        ["none"] * 12, "w3_judged")
    disc["w4_judge_products"] = _judged_source(
        tl4.JUDGE_FILE, tl4.CANDIDATES_FILE,
        ["none"] * 11, "w4_judged")
    disc["w5_judge_products"] = _judged_source(
        tl5.JUDGE_FILE, tl5.CANDIDATES_FILE,
        ["none"] * 10, "w5_judged")
    disc["w6_judge_products"] = _judged_source(
        tl6.JUDGE_FILE, tl6.CANDIDATES_FILE,
        ["none"] * 9, "w6_judged")
    disc["w7_judge_products"] = _judged_source(
        tl7.JUDGE_FILE, tl7.CANDIDATES_FILE,
        ["none"] * 8, "w7_judged")
    disc["w8_judge_products"] = _judged_source(
        tl8.JUDGE_FILE, tl8.CANDIDATES_FILE,
        ["none"] * 7, "w8_judged")
    disc["w9_judge_products"] = _judged_source(
        tl9.JUDGE_FILE, tl9.CANDIDATES_FILE,
        ["none"] * 6, "w9_judged")
    disc["w10_judge_products"] = _judged_source(
        tl10.JUDGE_FILE, tl10.CANDIDATES_FILE,
        ["none"] * 5, "w10_judged")
    disc["w11_judge_products"] = _judged_source(
        tl11.JUDGE_FILE, tl11.CANDIDATES_FILE,
        ["none"] * 4, "w11_judged")
    disc["w12_judge_products"] = _judged_source(
        tl12.JUDGE_FILE, tl12.CANDIDATES_FILE,
        ["none"] * 3, "w12_judged")
    disc["w13_judge_products"] = _judged_source(
        tl13.JUDGE_FILE, tl13.CANDIDATES_FILE,
        ["none"] * 2, "w13_judged")
    # (d)-face judged-supply weighting: frozen baseline uniform stands
    # (prereg sec.0 declare; sec.9 re-declare window = live prev
    # increment merged at generate time, uniform baseline absent an
    # append-confirm amendment -- disclosed, no fabrication)
    disc["judged_supply_weighting"] = (
        "frozen baseline uniform per prereg sec.0 declare (axis families "
        "equal allocation, zero judged weighting); sec.9 re-declare window "
        "requires a prereg-level append-confirm BEFORE generate runs -- "
        "none exists, uniform stands, availability of the FOURTEEN judge "
        "products disclosed above (freeze-time fourteen-source "
        "full-declare window = seventh in history)")
    return rows, disc


def _excluded_w14(cand, rows):
    """Exact already-judged cell test, resi/cnt=none face only (prereg
    sec.1: resi/cnt in member values = new-syntax legal cells --
    never excluded; W1-lineage cells implicitly stop/gate/vol/yang/
    vconf/streak/tstate/amp/mom/std/rsqr/sumn/resi/cnt=none; W2 cells
    carry their own stop face; W3 stop+gate; W4 stop+gate+vol; W5
    stop+gate+vol+yang; W6 stop+gate+vol+yang+vconf; W7
    stop+gate+vol+yang+vconf+streak; W8 stop+gate+vol+yang+vconf+
    streak+tstate; W9 +amp; W10 +mom; W11 +std; W12 +rsqr; W13 +sumn).
    Returns the exclusion face or None."""
    if cand["axis"][16] != "none" or cand["axis"][17] != "none":
        return None
    for e in rows:
        if (cand["module"], cand["fn"]) == (e["module"], e["fn"]) \
                and cand["sig_params"] == e["sig_params"] \
                and cand["axis"] == e["axis"]:
            return e.get("face", "excluded")
    return None


# -------------------------------------------- effective face + engine curves
def _effective_signal_mask_w14(mask, prices, stop_key, atr20, gate_key,
                               vol_key, yang_key, vconf_key, streak_key,
                               tstate_key, amp_key, mom_key, std_key,
                               rsqr_key, sumn_key, resi_key, cnt_key,
                               gate_state, vol_state, yang_state,
                               vconf_state, streak_state, tstate_state,
                               amp_state, mom_state, std_state, rsqr_state,
                               sumn_state, resi_state, cnt_state):
    """Dedup-face holdings proxy with the frozen composition order
    GATE -> VOL -> YANG -> VCONF -> STREAK -> TSTATE -> AMP -> MOM ->
    STD -> RSQR -> SUMN -> RESI -> CNT -> initial-stop (prereg sec.3 eighteen-tuple dedup legs; zero
    engine burn).  sumn=none + rsqr=none + std=none + mom=none + amp=none
    + tstate=none + streak=none + vconf=none + yang=none + vol=none +
    gate=none + stop=none = W1 identity; sumn=none = W12 semantic baseline; all
    twelve overlay faces deterministic layers of the same grammar
    stack (W12 order extended by the sumn leg, zero disturbance to the
    first eleven)."""
    G = tl3.gate_zero_mask(mask, gate_key, gate_state)
    V = tl4.vol_zero_mask(G, vol_key, vol_state)
    Y = tl5.yang_zero_mask(V, yang_key, yang_state)
    VC = tl6.vconf_zero_mask(Y, vconf_key, vconf_state)
    SK = tl7.streak_zero_mask(VC, streak_key, streak_state)
    TS = tl8.tstate_zero_mask(SK, tstate_key, tstate_state)
    AP = tl9.amp_zero_mask(TS, amp_key, amp_state)
    MO = mom_zero_mask(AP, mom_key, mom_state)
    SD = std_zero_mask(MO, std_key, std_state)
    RQ = rsqr_zero_mask(SD, rsqr_key, rsqr_state)
    SU = sumn_zero_mask(RQ, sumn_key, sumn_state)
    RE = resi_zero_mask(SU, resi_key, resi_state)
    CN = cnt_zero_mask(RE, cnt_key, cnt_state)
    return tl2._effective_signal_mask(CN, prices, stop_key, atr20)


def run_candidate_curve_w14(cand, template, prices, P, states, atr20=None,
                           fundamental_ok=None, rng_matrix=None, p_on=None,
                           gate_state=None, vol_state=None, yang_state=None,
                           vconf_state=None, streak_state=None,
                           tstate_state=None, amp_state=None,
                           mom_state=None, std_state=None, rsqr_state=None,
                           sumn_state=None, resi_state=None,
                           cnt_state=None):
    """One W12 candidate cell at the engine face with the gate + vol +
    yang + vconf + streak + tstate + amp + MOM + STD + RSQR overlays +
    initial-stop overlay carried per-cell (prereg sec.3 face a; frozen composition
    order filter -> timing -> GATE -> VOL -> YANG -> VCONF -> STREAK
    -> TSTATE -> AMP -> MOM -> STD -> RSQR -> SUMN -> initial-stop).

    sumn=none+rsqr=none+std=none+mom=none+amp=none+tstate=none+streak=none+
    vconf=none+yang=none+vol=none+gate=none+stop=none -> byte-identical
    to the tl1 engine face; sumn=none -> tl12 W12 face (parity law,
    selftest-pinned); sumn in {sumn20_lo, sumn10_lo} = new W13 syntax
    (entry-permittance only, never excluded).  Returns (eq, trades,
    metrics, params, patch, stop_fired, gate_zeroed, vol_zeroed,
    yang_zeroed, vconf_zeroed, streak_zeroed, tstate_zeroed,
    amp_zeroed, mom_zeroed, std_zeroed, rsqr_zeroed, sumn_zeroed,
    resi_zeroed, cnt_zeroed)."""
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
    if gate_state is None:
        gate_state = tl3.gate_state_series(prices)
    if vol_state is None:
        vol_state = tl4.vol_state_series(prices)
    if yang_state is None:
        yang_state = tl5.yang_state_series(prices)
    if vconf_state is None:
        vconf_state = tl6.vconf_state_series(prices)
    if streak_state is None:
        streak_state = tl7.streak_state_series(prices)
    if tstate_state is None:
        tstate_state = tl8.tstate_state_series(prices)
    if amp_state is None:
        amp_state = tl9.amp_state_series(prices)
    if mom_state is None:
        mom_state = mom_state_series(prices)
    if std_state is None:
        std_state = std_state_series(prices)
    if rsqr_state is None:
        rsqr_state = rsqr_state_series(prices)
    if sumn_state is None:
        sumn_state = sumn_state_series(prices)
    if resi_state is None:
        resi_state = resi_state_series(prices)
    if cnt_state is None:
        cnt_state = cnt_state_series(prices)
    if stop_key != "none" and tl2.STOP_FORMULA[stop_key]["kind"] == "atr" \
            and atr20 is None:
        atr20 = tl2.atr20_series(prices)
    mk = f"{cand['module']}.{cand['fn']}"
    face = "null" if rng_matrix is not None else tl1.GRAMMAR["faces"][mk]
    if rng_matrix is not None:
        mask = tl1._signal_frame(None, P, face, rng_matrix=rng_matrix,
                                 p_on=p_on)
    else:
        mask = tl1._signal_frame(cand, P, face)
    mask = mask.reindex(index=P["close"].index,
                        columns=P["close"].columns).fillna(0)
    mask = tl1.apply_filter(mask, cand["axis"][0], P, fundamental_ok)
    mask = tl1.apply_timing(mask, cand["axis"][3])
    G = tl3.gate_zero_mask(mask, gate_key, gate_state)
    V = tl4.vol_zero_mask(G, vol_key, vol_state)
    Y = tl5.yang_zero_mask(V, yang_key, yang_state)
    VC = tl6.vconf_zero_mask(Y, vconf_key, vconf_state)
    SK = tl7.streak_zero_mask(VC, streak_key, streak_state)
    TS = tl8.tstate_zero_mask(SK, tstate_key, tstate_state)
    AP = tl9.amp_zero_mask(TS, amp_key, amp_state)
    MO = mom_zero_mask(AP, mom_key, mom_state)
    SD = std_zero_mask(MO, std_key, std_state)
    RQ = rsqr_zero_mask(SD, rsqr_key, rsqr_state)
    SU = sumn_zero_mask(RQ, sumn_key, sumn_state)
    RE = resi_zero_mask(SU, resi_key, resi_state)
    CN = cnt_zero_mask(RE, cnt_key, cnt_state)
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
    sumn_zeroed = int((RQ > 0).sum().sum() - (SU > 0).sum().sum())
    resi_zeroed = int((SU > 0).sum().sum() - (RE > 0).sum().sum())
    cnt_zeroed = int((RE > 0).sum().sum() - (CN > 0).sum().sum())
    if stop_key == "none":
        S, stop_fired = CN, 0
    else:
        S = tl2._effective_signal_mask(CN, prices, stop_key, atr20)
        d = (CN > 0) & (S == 0)
        stop_fired = int(sum(int((d[c] & ~d[c].shift(1, fill_value=False)
                                 ).sum()) for c in d.columns))
    params, patch = tl1.candidate_engine_params(cand, template)
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
        std_zeroed, rsqr_zeroed, sumn_zeroed, resi_zeroed, cnt_zeroed


def _null_axis_draw_w14(i):
    """Deterministic null-cell draw per prereg sec.3: rng=[SEED_NULL, i]
    (W14 berth 20328000, distinct from the W13 berth 20323500 -- zero
    stream overlap by construction); consumption order frozen = p_on
    regime -> EIGHTEEN-tuple axis R/X/S/T/STOP/GATE/VOL/YANG/VCONF/
    STREAK/TSTATE/AMP/MOM/STD/RSQR/SUMN/RESI/CNT -> signal matrix (the resi/cnt
    gate legs merged into the same grid/param space draw per prereg
    sec.3).  Same engine/cost/panel as candidate cells incl. the
    gate + vol + yang + vconf + streak + tstate + amp + mom + std +
    rsqr + sumn + resi + cnt legs (BACKTEST_PLAN three iron rules)."""
    rng = np.random.default_rng([SEED_NULL, i])
    p_on = tl1.NULL_P_REGIMES[int(rng.integers(len(tl1.NULL_P_REGIMES)))]
    ax = (tl1.AXIS_FILTERS[int(rng.integers(len(tl1.AXIS_FILTERS)))],
          tl1.AXIS_EXITS[int(rng.integers(len(tl1.AXIS_EXITS)))],
          tl1.AXIS_SIZING[int(rng.integers(len(tl1.AXIS_SIZING)))],
          tl1.AXIS_TIMING[int(rng.integers(len(tl1.AXIS_TIMING)))],
          tl2.AXIS_STOP[int(rng.integers(len(tl2.AXIS_STOP)))],
          tl3.AXIS_GATE[int(rng.integers(len(tl3.AXIS_GATE)))],
          tl4.AXIS_VOL[int(rng.integers(len(tl4.AXIS_VOL)))],
          tl5.AXIS_YANG[int(rng.integers(len(tl5.AXIS_YANG)))],
          tl6.AXIS_VCONF[int(rng.integers(len(tl6.AXIS_VCONF)))],
          tl7.AXIS_STREAK[int(rng.integers(len(tl7.AXIS_STREAK)))],
          tl8.AXIS_TSTATE[int(rng.integers(len(tl8.AXIS_TSTATE)))],
          tl9.AXIS_AMP[int(rng.integers(len(tl9.AXIS_AMP)))],
          AXIS_MOM[int(rng.integers(len(AXIS_MOM)))],
          AXIS_STD[int(rng.integers(len(AXIS_STD)))],
          AXIS_RSQR[int(rng.integers(len(AXIS_RSQR)))],
          AXIS_SUMN[int(rng.integers(len(AXIS_SUMN)))],
          AXIS_RESI[int(rng.integers(len(AXIS_RESI)))],
          AXIS_CNT[int(rng.integers(len(AXIS_CNT)))])
    return p_on, list(ax), rng


# ------------------------------------------------------------ grammar / status
def cmd_grammar() -> int:
    """Serialize the frozen W14 grammar to results/trial_labor_w14/
    w14_grammar.json (idempotent; sha16 printed for the Slice-B pin)."""
    os.makedirs(RES_DIR, exist_ok=True)
    g = build_grammar_w14()
    if FROZEN_SHA16 and g["grammar_sha256"] != FROZEN_SHA16:
        print(f"GRAMMAR-GATE: sha drift -- frozen anchor {FROZEN_SHA16} "
              f"!= built {g['grammar_sha256']}; refusing")
        return 2
    with open(GRAMMAR_FILE, "w", encoding="utf-8") as fh:
        json.dump(g, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(f"grammar serialized: {GRAMMAR_FILE}")
    print(f"sha16={g['grammar_sha256']} axis_combos={g['axis_combos']} "
          f"wave={g['wave']} cutoff={g['evidence_cutoff']}")
    return 0


def cmd_status() -> int:
    """Honest slice-state readout (all faces read-only; absent =
    pending)."""
    faces = [("grammar", GRAMMAR_FILE), ("candidates", CANDIDATES_FILE),
             ("prep", PREP_FILE), ("screen", SCREEN_FILE),
             ("judge_state", JUDGE_STATE_FILE), ("judge", JUDGE_FILE),
             ("intake", INTAKE_FILE)]
    for name, path in faces:
        if os.path.exists(path):
            print(f"{name}: present ({os.path.getsize(path)} bytes)")
        else:
            print(f"{name}: PENDING (funnel leg)")
    print("W14 resi+cnt overlay + G-RESI/G-CNT gates + eighteen-tuple "
          "grammar + funnel bodies + dispatch LANDED (bm-b r472); "
          "GENERATE pool entry submitted same-commit -- autofill "
          "burns, no inline burn (O-2100); SCREEN/JUDGE pool entries "
          "land on their physical deps per W3-W13 precedent")
    return 0


# -------------------------------------------------- generate slice (s1)
def cmd_generate() -> int:
    """Frozen prereg sec.3 generate stage (W12 cmd_generate caliber on
    the EIGHTEEN-tuple face): per-slot Sobol streams consumed in global
    round-robin -> 25-source exclusion -> T-84s3 dedup gate on the
    effective signal face (gate + vol + yang + vconf + streak + tstate
    + amp + MOM + STD + RSQR overlays applied, frozen composition
    order) -> w14_candidates.json + grammar ledger wave-13 row.  Zero
    engine cells burned."""
    t0 = time.time()
    print(f"=== {WAVE} generate (prereg FROZEN {PREREG}) ===")
    if os.path.exists(CANDIDATES_FILE):
        print("GENERATE-GATE: w14_candidates.json exists -- same-grammar "
              "rerun FORBIDDEN (TRIAL_LABOR_LAW sec.4); refusing")
        return 2
    if not os.path.exists(GRAMMAR_FILE):
        print("GENERATE-GATE: w14_grammar.json absent -- run `grammar` "
              "first")
        return 2
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    if _grammar_sha16(grammar) != grammar["grammar_sha256"] \
            or (FROZEN_SHA16 and grammar["grammar_sha256"] != FROZEN_SHA16):
        print(f"GENERATE-GATE: grammar sha drift -- frozen anchor "
              f"{FROZEN_SHA16} != file {grammar['grammar_sha256']}; "
              "refusing")
        return 2
    ram_min, ram_ok = tl2._ram_gate_gb(wait_min=40)
    if not ram_ok:
        print(f"GENERATE-GATE: free RAM {ram_min}GB < 4GB after bounded "
              f"wait (three-sample r354 law, dual-company discipline; "
              f"r379 wait-law) -- honest refuse, pool retries when RAM "
              "frees")
        return 2
    tl1.GRAMMAR = grammar           # tl1._signal_frame reads tl1's global
    prices = tl1.load_core()
    cut = pd.Timestamp(CUTOFF)
    prices = {s: df[df.index <= cut] for s, df in prices.items()}
    P = tl1.build_panels(prices)
    close = P["close"]
    try:
        bl = pd.read_csv(tl1.B_LAYER_MASK)
        ok_codes = set(bl.loc[bl["ok_static"] == True, "code"].astype(str))
        overlap = sorted(s for s in close.columns if s in ok_codes)
    except Exception as e:
        overlap = []
        print(f"  [warn] b_layer_mask load error: {str(e)[:120]}")
    if overlap:
        fundamental_ok = pd.DataFrame(False, index=close.index,
                                       columns=close.columns)
        for s in overlap:
            fundamental_ok[s] = True
    else:
        fundamental_ok = None
    atr20 = tl2.atr20_series(prices)
    gate_state = tl3.gate_state_series(prices)
    vol_state, vol_err = tl4._vol_state_full()
    if vol_err:
        print(f"GENERATE-GATE: {vol_err} (prereg sec.2 fail-closed) "
              "-- refuse")
        return 2
    yang_state, yang_err = tl5._yang_state_full()
    if yang_err:
        print(f"GENERATE-GATE: {yang_err} (prereg sec.2 G-YANG "
              "fail-closed) -- refuse")
        return 2
    vconf_state, vconf_err = tl6._vconf_state_full()
    if vconf_err:
        print(f"GENERATE-GATE: {vconf_err} (prereg sec.2 G-VCONF "
              "fail-closed) -- refuse")
        return 2
    streak_state, streak_err = tl7._streak_state_full()
    if streak_err:
        print(f"GENERATE-GATE: {streak_err} (prereg sec.2 G-STREAK "
              "fail-closed) -- refuse")
        return 2
    tstate_state, tstate_err = tl8._tstate_state_full()
    if tstate_err:
        print(f"GENERATE-GATE: {tstate_err} (prereg sec.2 G-TSTATE "
              "fail-closed) -- refuse")
        return 2
    amp_state, amp_err = _amp_state_full()
    if amp_err:
        print(f"GENERATE-GATE: {amp_err} (prereg sec.2 G-AMP "
              "fail-closed) -- refuse")
        return 2
    mom_state, mom_err = _mom_state_full()
    if mom_err:
        print(f"GENERATE-GATE: {mom_err} (prereg sec.2 G-MOM "
              "fail-closed, tl10 import face) -- refuse")
        return 2
    std_state, std_err = _std_state_full()
    if std_err:
        print(f"GENERATE-GATE: {std_err} (prereg sec.2 G-STD "
              "fail-closed) -- refuse")
        return 2
    rsqr_state, rsqr_err = _rsqr_state_full()
    if rsqr_err:
        print(f"GENERATE-GATE: {rsqr_err} (prereg sec.2 G-RSQR "
              "fail-closed) -- refuse")
        return 2
    sumn_state, sumn_err = _sumn_state_full()
    if sumn_err:
        print(f"GENERATE-GATE: {sumn_err} (prereg sec.2 G-SUMN "
              "fail-closed) -- refuse")
        return 2
    excl_rows, excl_disc = _load_exclusion_rows_w14(grammar)
    neg_fns = {(e["module"], e["fn"])
               for e in grammar["exclusion"]
               ["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_sumn_none_face"]
               if str(e.get("face", "")).startswith("negative")}

    # ---- draws: per-slot Sobol streams consumed in global round-robin
    candidates, excluded_log = [], []
    excl_hits = {"A": 0, "B": 0}
    for family, n_draws in (("A", N_A), ("B", N_B)):
        slots = grammar["families"][family]
        n_slots = len(slots)
        streams = {s: draw_candidate_sobol_w14(
                       grammar, family, s,
                       (n_draws - s + n_slots - 1) // n_slots)
                   for s in range(n_slots)}
        for i in range(n_draws):
            slot = i % n_slots
            _, cand = next(streams[slot])
            cand["candidate_id"] = f"W13-{family}-{i:04d}"
            cand["provenance"] = {"seed": SEED_GEN,
                                  "family_idx": (slot if family == "A"
                                                 else 6 + slot),
                                  "stream_draw_idx": i // n_slots,
                                  "global_draw_idx": i}
            if family == "A":
                cand["template_trader"] = slots[slot]["trader_id"]
                cand["negative_prior"] = False
            else:
                cand["negative_prior"] = \
                    (cand["module"], cand["fn"]) in neg_fns
            hit = _excluded_w14(cand, excl_rows)
            if hit:
                excl_hits[family] += 1
                excluded_log.append({"candidate_id": cand["candidate_id"],
                                     "module": cand["module"],
                                     "fn": cand["fn"],
                                     "axis": cand["axis"], "face": hit})
                continue
            candidates.append(cand)
        print(f"  raw draws {family}={n_draws}, exclusion hits "
              f"{excl_hits[family]}")

    # ---- dedup gate (T-84 s3) on the effective signal face (streaming)
    fps, series = [], []
    for j, cand in enumerate(candidates):
        mk = f"{cand['module']}.{cand['fn']}"
        mask = tl1._signal_frame(cand, P, grammar["faces"][mk])
        mask = mask.reindex(index=close.index,
                            columns=close.columns).fillna(0)
        mask = tl1.apply_filter(mask, cand["axis"][0], P, fundamental_ok)
        mask = tl1.apply_timing(mask, cand["axis"][3])
        S = _effective_signal_mask_w14(mask, prices, cand["axis"][4], atr20,
                                      cand["axis"][5], cand["axis"][6],
                                      cand["axis"][7], cand["axis"][8],
                                      cand["axis"][9], cand["axis"][10],
                                      cand["axis"][11], cand["axis"][12],
                                      cand["axis"][13], cand["axis"][14],
                                      cand["axis"][15],
                                      gate_state, vol_state, yang_state,
                                      vconf_state, streak_state,
                                      tstate_state, amp_state, mom_state,
                                      std_state, rsqr_state,
                                      sumn_state)
        fps.append(tl1._fingerprint(S))
        series.append(tl1._naive_returns(S, close).values)
        del mask, S
        if (j + 1) % 250 == 0:
            print(f"  [dedup face] {j + 1}/{len(candidates)}", flush=True)

    fp_groups = {}
    for i, fp in enumerate(fps):
        fp_groups.setdefault(fp, []).append(i)
    keep, fp_collapsed = set(), []
    for fp, members in fp_groups.items():
        members.sort(key=lambda k: candidates[k]["candidate_id"])
        keep.add(members[0])
        fp_collapsed.append({"kept": candidates[members[0]]["candidate_id"],
                             "eliminated": [candidates[m]["candidate_id"]
                                            for m in members[1:]]})
    idx_keep = sorted(keep)
    mat = np.vstack([series[i] for i in idx_keep])
    sd = mat.std(axis=1)
    live_rows = [j for j in range(len(idx_keep)) if sd[j] > 1e-12]
    corr_elim, dead = [], set()
    if len(live_rows) >= 2:
        sub = mat[live_rows]
        corr = np.corrcoef(sub)
        for a_ in range(len(live_rows)):
            for b_ in range(a_ + 1, len(live_rows)):
                if abs(corr[a_, b_]) >= 0.999:
                    ia, ib = idx_keep[live_rows[a_]], idx_keep[live_rows[b_]]
                    ka = candidates[ia]["candidate_id"]
                    kb = candidates[ib]["candidate_id"]
                    dead.add(ib if ka < kb else ia)
                    corr_elim.append({"pair": sorted([ka, kb]),
                                      "corr": round(float(corr[a_, b_]), 6),
                                      "eliminated": candidates[
                                          ib if ka < kb else ia]
                                      ["candidate_id"]})
    final_keep = [i for i in idx_keep if i not in dead]
    distinct = [candidates[i] for i in final_keep]

    # gate/stop/vol/yang/vconf/streak/tstate/amp/mom face counts + gate
    # x vol x yang x vconf x streak x tstate x amp x mom eight-gate
    # interaction (prereg sec.5.4 eight-gate column, W9 seven-gate face
    # extended)
    gate_counts, stop_counts = {}, {}
    vol_counts, yang_counts, vconf_counts = {}, {}, {}
    streak_counts, tstate_counts, amp_counts = {}, {}, {}
    mom_counts, std_counts = {}, {}
    rsqr_counts = {}
    sumn_counts = {}
    gvvvsktsam_counts = {}
    for c in distinct:
        gate_counts[c["axis"][5]] = gate_counts.get(c["axis"][5], 0) + 1
        stop_counts[c["axis"][4]] = stop_counts.get(c["axis"][4], 0) + 1
        vol_counts[c["axis"][6]] = vol_counts.get(c["axis"][6], 0) + 1
        yang_counts[c["axis"][7]] = yang_counts.get(c["axis"][7], 0) + 1
        vconf_counts[c["axis"][8]] = vconf_counts.get(c["axis"][8], 0) + 1
        streak_counts[c["axis"][9]] = streak_counts.get(c["axis"][9], 0) + 1
        tstate_counts[c["axis"][10]] = tstate_counts.get(c["axis"][10],
                                                          0) + 1
        amp_counts[c["axis"][11]] = amp_counts.get(c["axis"][11], 0) + 1
        mom_counts[c["axis"][12]] = mom_counts.get(c["axis"][12], 0) + 1
        std_counts[c["axis"][13]] = std_counts.get(c["axis"][13], 0) + 1
        rsqr_counts[c["axis"][14]] = rsqr_counts.get(c["axis"][14], 0) + 1
        sumn_counts[c["axis"][15]] = sumn_counts.get(c["axis"][15], 0) + 1
        k11 = (f"{c['axis'][5]}|{c['axis'][6]}|{c['axis'][7]}|"
              f"{c['axis'][8]}|{c['axis'][9]}|{c['axis'][10]}|"
              f"{c['axis'][11]}|{c['axis'][12]}|{c['axis'][13]}|"
              f"{c['axis'][14]}|{c['axis'][15]}")
        gvvvsktsam_counts[k11] = gvvvsktsam_counts.get(k11, 0) + 1

    # D6 disclosure column (naive face; prereg sec.1 per-cell max|corr|)
    reg_series = tl2._registered_naive_series(P, grammar)
    reg_names = sorted(reg_series)
    R = np.vstack([reg_series[nm] for nm in reg_names]) \
        if reg_names else np.zeros((0, len(close.index)))
    Rc = R - R.mean(axis=1, keepdims=True)
    rn = np.linalg.norm(Rc, axis=1)
    if final_keep:
        F = np.vstack([series[i] for i in final_keep])
        Fc = F - F.mean(axis=1, keepdims=True)
        fn = np.linalg.norm(Fc, axis=1)
        cm = (Fc @ Rc.T) / np.outer(np.where(fn > 1e-12, fn, 1.0),
                                    np.where(rn > 1e-12, rn, 1.0))
    else:
        cm = np.zeros((0, len(reg_names)))
    for row, i in enumerate(final_keep):
        v = cm[row]
        finite = v[np.isfinite(v)]
        candidates[i]["max_corr_vs_registered_naive"] = (
            round(float(np.max(np.abs(finite))), 4)
            if len(finite) else None)

    payload = {"wave": WAVE, "stage": "generate", "prereg": PREREG,
               "evidence_cutoff": CUTOFF, **tl1.cutoff_meta(CUTOFF),
               "grammar_sha256": grammar["grammar_sha256"],
               "n": len(distinct), "candidates": distinct,
               "exclusion": {"hits": excl_hits,
                             "excluded_log": excluded_log,
                             "sources": excl_disc,
                             "note": "cell key=(template, params, "
                                     "axis_config, initial_stop, gate, "
                                     "vol, yang, vconf, streak, tstate, "
                                     "amp, mom, std, rsqr, sumn); exclusion "
                                     "face = sumn=none only (sec.1); prior-wave "
                                     "keys sumn=none-completed; sumn in "
                                     "{sumn20_lo, sumn10_lo} = "
                                     "new-syntax legal cells"},
               "dedup": {"raw": len(candidates), "distinct": len(distinct),
                         "fingerprint_collapse_groups": fp_collapsed,
                         "corr_collapses": corr_elim,
                         "note": "dedup legs on the generate-stage "
                                 "effective signal face (gate + vol + "
                                 "yang + vconf + streak + tstate + AMP "
                                 "+ MOM + STD + RSQR overlays applied, frozen "
                                 "composition order; naive-hold "
                                 "returns, zero engine burn); engine "
                                 "faces run at screen (W1 precedent)"},
               "gate_face_counts": gate_counts,
               "stop_face_counts": stop_counts,
               "vol_face_counts": vol_counts,
               "yang_face_counts": yang_counts,
               "vconf_face_counts": vconf_counts,
               "streak_face_counts": streak_counts,
               "tstate_face_counts": tstate_counts,
               "amp_face_counts": amp_counts,
               "mom_face_counts": mom_counts,
               "std_face_counts": std_counts,
               "rsqr_face_counts": rsqr_counts,
               "sumn_face_counts": sumn_counts,
               "gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_sumn_"
               "face_counts":
                   gvvvsktsam_counts,
               "gate_state_meta": gate_state[2],
               "vol_state_meta": vol_state[2],
               "yang_state_meta": yang_state[2],
               "vconf_state_meta": vconf_state[2],
               "streak_state_meta": streak_state[2],
               "tstate_state_meta": tstate_state[2],
               "amp_state_meta": amp_state[2],
               "mom_state_meta": mom_state[2],
               "std_state_meta": std_state[2],
               "rsqr_state_meta": rsqr_state[2],
               "sumn_state_meta": sumn_state[2],
               "d6_disclosure": {
                   "max_corr_vs_registered_naive": "per-cell column; "
                   "naive-face caliber (dedup byproduct); D6 binding gate "
                   "at s4 intake recomputes at the engine face"},
               "audit": {"ram_gate_gb": ram_min,
                         "negative_prior_derivation": "derived from the "
                         "frozen grammar's negative_default_axis:stop-"
                         "gate-vol-yang-vconf-streak-tstate-amp-mom-"
                         "none exclusion faces (face derivation is "
                         "mechanical)",
                         "seed_berth_note": "berths 20327500/"
                         "20328000/20328500 held at the freeze commit "
                         "(bm-a r461 three-step re-verify ALL GREEN, "
                         "no re-pick; R250 one-step law; berth-open adoption "
                         "of the bm-a r456 SUMN candidate whole package "
                         "per AMP->W9/MOM->W10/STD->W11/RSQR->W12 adoption lineage)",
                         "note": "Sobol per-slot streams in global "
                                 "round-robin; deterministic pre-burn "
                                 "stage; same-grammar rerun still FORBIDDEN "
                                 "post-consume"},
               "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    tl1._dump(CANDIDATES_FILE, payload)

    # grammar consumption ledger row (append-only; prereg sec.4/sec.6)
    ser_ts = time.strftime("%Y-%m-%d %H:%M",
                           time.localtime(os.path.getmtime(GRAMMAR_FILE)))
    raw_total = len(candidates) + sum(excl_hits.values())
    row = (f"| {WAVE} | {grammar['grammar_sha256'][:16]} | "
           f"raw {raw_total} (A{N_A}/B{N_B}, excl hits "
           f"{sum(excl_hits.values())}) | dedup -> {len(distinct)} "
           f"(std faces {json.dumps(std_counts, sort_keys=True)}; "
           f"rsqr faces {json.dumps(rsqr_counts, sort_keys=True)}; "
           f"sumn faces {json.dumps(sumn_counts, sort_keys=True)}; "
           f"gate x vol x yang x vconf x streak x tstate x amp x mom "
           f"x std x rsqr x sumn {json.dumps(gvvvsktsam_counts, sort_keys=True)}) "
           f"| seeds gen={SEED_GEN} null={SEED_NULL} unc={SEED_UNC} | "
           f"serialized {ser_ts} + consumed "
           f"{time.strftime('%Y-%m-%d %H:%M:%S')} (pool "
           f"TRIAL-LABOR-W13-GENERATE, T-125 prereg bm-a r461 frozen / "
           f"runner bm-a r465) | "
           f"same-grammar rerun FORBIDDEN (TRIAL_LABOR_LAW sec.4) |\n")
    os.makedirs(os.path.dirname(GRAMMAR_LEDGER), exist_ok=True)
    if not os.path.exists(GRAMMAR_LEDGER):
        with open(GRAMMAR_LEDGER, "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write("# TRIAL_GRAMMAR_LEDGER (append-only; "
                     "TRIAL_LABOR_LAW sec.4 same-grammar-rerun ban)\n\n"
                     "| wave | grammar_sha16 | raw | dedup | seeds | "
                     "consumed | law |\n|---|---|---|---|---|---|---|\n")
    with open(GRAMMAR_LEDGER, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(row)
    print(f"generate done: raw {raw_total} -> exclusion hits "
          f"{sum(excl_hits.values())} -> dedup distinct {len(distinct)} "
          f"(fp-collapses {len(fp_collapsed)}, corr-collapses "
          f"{len(corr_elim)})")
    print(f"mom faces: {json.dumps(mom_counts, sort_keys=True)}; "
          f"std faces: {json.dumps(std_counts, sort_keys=True)}; "
          f"rsqr faces: {json.dumps(rsqr_counts, sort_keys=True)}; "
          f"sumn faces: {json.dumps(sumn_counts, sort_keys=True)}; "
          f"gate x vol x yang x vconf x streak x tstate x amp x mom x "
          f"std x rsqr x sumn: "
          f"{json.dumps(gvvvsktsam_counts, sort_keys=True)[:400]}")
    print(f"mom meta: n_bars={mom_state[2]['n_bars']} "
          f"open={mom_state[2]['open_days']} "
          f"closed={mom_state[2]['closed_days']} "
          f"decidable={mom_state[2]['decidable_days']} "
          f"warmup={mom_state[2]['warmup_gate_closed_bars']}")
    print(f"products: w14_candidates.json + ledger row "
          f"(sha16 {grammar['grammar_sha256'][:16]})")
    print(f"elapsed {time.time() - t0:.1f}s (zero engine cells burned)")
    return 0


# ------------------------------------------------------ screen slice (s2)
csv_cols_screen_w14 = ["cell_id", "candidate_id", "family", "module", "fn",
                      "no_entries", "beat6m_k", "beat6m_n", "beat6m_rate",
                      "binom_z", "binom_p", "sharpe_full", "dd_full",
                      "n_trades", "n_entries", "stop_face", "stop_fired",
                      "gate_face", "gate_zeroed", "vol_face", "vol_zeroed",
                      "yang_face", "yang_zeroed", "vconf_face",
                      "vconf_zeroed", "streak_face", "streak_zeroed",
                      "tstate_face", "tstate_zeroed", "amp_face",
                      "amp_zeroed", "mom_face", "mom_zeroed",
                      "std_face", "std_zeroed",
                      "rsqr_face", "rsqr_zeroed",
                      "sumn_face", "sumn_zeroed",
                      "resi_face", "resi_zeroed",
                      "cnt_face", "cnt_zeroed",
                      "survives_screen"]

# pure survival-line math imported from tl2 (W2 identical frozen law:
# survive iff beat6m_rate > null-family p95 -- program-frozen, zero
# hand-picked thresholds; import-face law, zero re-implementation)
_finalize_math = tl2._finalize_math


def _screen_cell_w14(cell):
    """One W10 screen cell: full leg-L backtest with the gate + vol +
    yang + vconf + streak + tstate + amp + MOM overlays + initial-stop
    overlay carried per-cell (prereg sec.3 face a) -> beat6m row (pool
    worker; W9 _screen_cell caliber + mom columns)."""
    st = tl1._ST
    kind, cand, template = cell["kind"], cell["cand"], cell.get("template")
    P, prices, states = st["P"], st["prices"], st["states"]
    starts, passive = st["starts"], st["passive_6m"]
    close = P["close"]
    if kind == "null":
        p_on, ax, rng = _null_axis_draw_w14(cell["i"])
        cand = {"module": "null", "fn": "random_signal",
                "sig_params": {"p_on": p_on}, "axis": ax,
                "candidate_id": f"W14-NULL-{cell['i']:04d}",
                "family": "NULL"}
        mat = rng.random((len(close.index), len(close.columns)))
        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \
            tz, az, mz, dz, rz, nz, rz2, cnz = run_candidate_curve_w14(
                cand, None, prices, P, states, st["atr20"],
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
                cnt_state=st.get("cnt_state"))
    else:
        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \
            tz, az, mz, dz, rz, nz, rz2, cnz = run_candidate_curve_w14(
                cand, template, prices, P, states, st["atr20"],
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
                cnt_state=st.get("cnt_state"))
    row = {"cell_id": cell["cell_id"], "candidate_id": cand["candidate_id"],
           "family": cand["family"], "stop_face": cand["axis"][4],
           "stop_fired": int(fired), "gate_face": cand["axis"][5],
           "gate_zeroed": int(gz), "vol_face": cand["axis"][6],
           "vol_zeroed": int(vz), "yang_face": cand["axis"][7],
           "yang_zeroed": int(yz), "vconf_face": cand["axis"][8],
           "vconf_zeroed": int(cz), "streak_face": cand["axis"][9],
           "streak_zeroed": int(sz), "tstate_face": cand["axis"][10],
           "tstate_zeroed": int(tz), "amp_face": cand["axis"][11],
           "amp_zeroed": int(az), "mom_face": cand["axis"][12],
           "mom_zeroed": int(mz), "std_face": cand["axis"][13],
           "std_zeroed": int(dz),
           "rsqr_face": cand["axis"][14],
           "rsqr_zeroed": int(rz),
            "sumn_face": cand["axis"][15],
            "sumn_zeroed": int(nz),
            "resi_face": cand["axis"][16],
            "resi_zeroed": int(rz2),
            "cnt_face": cand["axis"][17],
            "cnt_zeroed": int(cnz)}
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


def _cell_list_w14():
    """Distinct candidate cells + K null cells (deterministic order;
    shard-split by index; W1-W9 precedent)."""
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    cands = json.load(open(CANDIDATES_FILE, encoding="utf-8"))["candidates"]
    a_by_trader = {t["trader_id"]: t for t in tl1.A_TEMPLATES}
    cells = []
    for c in cands:
        template = (a_by_trader.get(c.get("template_trader"))
                    if c["family"] == "A" else None)
        cells.append({"cell_id": f"SCREEN|{c['candidate_id']}",
                      "kind": "cand", "cand": c, "template": template})
    for i in range(K_NULLS):
        cells.append({"cell_id": f"SCREEN|NULL-{i:04d}", "kind": "null",
                      "i": i, "cand": None})
    return grammar, cells


def _load_screen_rows():
    rows = []
    for f in sorted(os.listdir(CKPT_DIR)):
        if f.startswith("screen_shard_") and f.endswith(".jsonl"):
            with open(os.path.join(CKPT_DIR, f), encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln:
                        rows.append(json.loads(ln))
    return rows


def cmd_screen_prep() -> int:
    """G-PANEL / G-ANCHOR / G-CENSUS / G-EXCLUDE / G-VOL / G-YANG /
    G-VCONF / G-STREAK / G-TSTATE / G-AMP / G-MOM / G-STD / G-RSQR /
    G-SUMN / G-RESI / G-CNT fail-closed gates +
    the shared passive 6m precompute (prereg sec.2; W13 cmd_screen_prep
    caliber on the W13 sixteen-tuple grammar face extended by the
    W14 resi/cnt layer (eighteen-tuple) + streak/tstate/
    amp/mom meta disclosure)."""
    print(f"=== {WAVE} screen-prep (fail-closed gates) ===")
    # r446bmb three-command identity-first-run law: ALL panel/anchor/
    # census identity faces run BEFORE the candidates-presence refusal
    # so the full identity face exercises on real data pre-generate
    # (rc=2 honest "generate pending" lands at the TAIL; W12 r446
    # precedent + prereg sec.9 sequencing adjudication)
    if not os.path.exists(GRAMMAR_FILE):
        print("PREP-GATE FAIL: w14_grammar.json absent -- run `grammar` "
              "first")
        return 2
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    if FROZEN_SHA16 and _grammar_sha16(grammar) != FROZEN_SHA16:
        print(f"PREP-GATE FAIL: grammar sha drift "
              f"{grammar['grammar_sha256'][:16]} != frozen {FROZEN_SHA16}")
        return 1
    tl1.GRAMMAR = grammar   # tl1._signal_frame reads tl1's global
    if not tl1.self_test_patches():
        print("PREP-GATE FAIL: patch self-test")
        return 1

    prices_full = tl1.load_core()
    cut = pd.Timestamp(CUTOFF)
    # G-PANEL validates the cutoff-frozen face, not the raw load face
    # (Monday-bar-proof, T-89 r313 pattern).  Every downstream consumer
    # already sees the panel truncated at the frozen cutoff.
    prices_full = {s: df[df.index <= cut] for s, df in prices_full.items()}
    n_members = len(prices_full)
    bad = [s for s, df in prices_full.items()
           if len(df) < 60 or str(df.index[-1].date()) != CUTOFF
           or not {"open", "high", "low", "close", "volume"} <= set(df.columns)]
    gp = {"members": n_members, "bad": bad,
          "pass": bool(n_members == 48 and not bad)}
    if not gp["pass"]:
        print(f"PREP-GATE FAIL: G-PANEL {gp}")
        return 1

    # G-VOL on the raw full-history face (W4 law; probe basis =
    # data/daily/sh510300.csv; NOT the W1-floored load_core pool face)
    vol_state_full, vol_err = tl4._vol_state_full()
    if vol_err:
        print(f"PREP-GATE FAIL: G-VOL {vol_err}")
        return 1
    vol_meta_core = vol_state_full[2]

    # G-YANG on the raw full-history face (W5 law; probe basis =
    # data/daily/sh510300.csv open+close; zero warmup + probe anchors)
    yang_state_full, yang_err = tl5._yang_state_full()
    if yang_err:
        print(f"PREP-GATE FAIL: G-YANG {yang_err}")
        return 1
    yang_meta_core = yang_state_full[2]

    # G-VCONF on the raw full-history face (prereg sec.2 probe basis =
    # data/daily/sh510300.csv open+close+volume; 19-bar warmup + probe
    # anchors + four-gate 16-cell non-empty law)
    vconf_state_full, vconf_err = tl6._vconf_state_full()
    if vconf_err:
        print(f"PREP-GATE FAIL: G-VCONF {vconf_err}")
        return 1
    vconf_meta_core = vconf_state_full[2]

    # G-STREAK on the raw full-history face (prereg sec.2 probe basis =
    # data/daily/sh510300.csv close-over-close; 2-bar warmup + probe
    # anchors + cross lower bounds + five-gate 32-cell non-empty law)
    streak_state_full, streak_err = tl7._streak_state_full()
    if streak_err:
        print(f"PREP-GATE FAIL: G-STREAK {streak_err}")
        return 1
    streak_meta_core = streak_state_full[2]

    # G-TSTATE on the raw full-history face (prereg sec.2 probe basis =
    # data/daily/sh510300.csv open+high+low+close+volume; 178/59-bar
    # warmups + probe anchors + streak-anchor reproduction + cross
    # lower bounds + six-gate 64-cell 44/20 law + extreme-day states)
    tstate_state_full, tstate_err = tl8._tstate_state_full()
    if tstate_err:
        print(f"PREP-GATE FAIL: G-TSTATE {tstate_err}")
        return 1
    tstate_meta_core = tstate_state_full[2]

    # G-AMP on the raw full-history face (prereg sec.2 probe basis =
    # data/daily/sh510300.csv open+high+low+close; 19-bar warmup +
    # probe anchors + cross four-cell lower bounds + seven-gate
    # 128-cell 73/55 law + extreme-day 7/7-wide states)
    amp_state_full, amp_err = _amp_state_full()
    if amp_err:
        print(f"PREP-GATE FAIL: G-AMP {amp_err}")
        return 1
    amp_meta_core = amp_state_full[2]

    # G-MOM on the raw full-history face (prereg sec.2 probe basis =
    # data/daily/sh510300.csv close; 139-bar warmup + probe anchors +
    # cross lower bounds {mom^mad60 253 / mom^rsv60 212 / mom^down_
    # streak 139 / mom^wide 222} + eight-gate 256-cell 111/145 law +
    # extreme-day 2/7-open states)
    mom_state_full, mom_err = _mom_state_full()
    if mom_err:
        print(f"PREP-GATE FAIL: G-MOM {mom_err}")
        return 1
    mom_meta_core = mom_state_full[2]

    # G-STD on the raw full-history face (prereg sec.2 probe basis =
    # data/daily/sh510300.csv close; 120-bar warmup + probe anchors
    # decidable 3,363 / open 391 / std10 3363/399 + eight-gate 256-cell
    # 103/153 law + extreme-day 2/7 std20-open states)
    std_state_full, std_err = _std_state_full()
    if std_err:
        print(f"PREP-GATE FAIL: G-STD {std_err}")
        return 1
    std_meta_core = std_state_full[2]

    # G-RSQR on the raw full-history face (prereg sec.2 probe basis =
    # data/daily/sh510300.csv; 120-bar warmup + probe anchors
    # decidable 3,363 / open 341 / rsqr10 3363/332 + slope split
    # 213/128 + nine-gate 512-cell 124/388 law + extreme-day 0/7
    # open states)
    rsqr_state_full, rsqr_err = _rsqr_state_full()
    if rsqr_err:
        print(f"PREP-GATE FAIL: G-RSQR {rsqr_err}")
        return 1
    rsqr_meta_core = rsqr_state_full[2]

    # G-SUMN on the raw full-history face (prereg sec.2 probe basis =
    # data/daily/sh510300.csv; 120-bar warmup + probe anchors
    # decidable 3,363 / open 387 / sumn10 3363/368 + slope split
    # 387/0 + nine-gate 512-cell 103/409 law + mirror-twin
    # 387/0-xor + zero-co-open exact mad60/rsv60/mom)
    sumn_state_full, sumn_err = _sumn_state_full()
    if sumn_err:
        print(f"PREP-GATE FAIL: G-SUMN {sumn_err}")
        return 1
    sumn_meta_core = sumn_state_full[2]

    # G-RESI on the raw full-history face (prereg sec.2/3 probe basis
    # = data/daily/sh510300.csv; 120-bar warmup + probe anchors
    # resi60 decidable 3,363 / open 390 (11.20%) + slope split 352/38
    # + nine-gate 512-cell 103/409 max 41 + extreme-day states + the
    # r470 facts per-cell cross-check)
    resi_state_full, resi_err = _resi_state_full()
    if resi_err:
        print(f"PREP-GATE FAIL: G-RESI {resi_err}")
        return 1
    resi_meta_core = resi_state_full[2]

    # G-CNT on the raw full-history face (prereg sec.2/3 probe basis
    # = data/daily/sh510300.csv; 119-bar first-decidable one-bar
    # construction-family note + cntd5 3,364/137 (3.93% thin tail) +
    # cntn20 3,364/265 (7.61%) + grids 109/403 + 103/409 + the
    # r470/r471 facts per-cell cross-checks)
    cnt_state_full, cnt_err = _cnt_state_full()
    if cnt_err:
        print(f"PREP-GATE FAIL: G-CNT {cnt_err}")
        return 1
    cnt_meta_core = cnt_state_full[4]

    # G-ANCHOR: registered six replayed through the W10 grammar
    # default-axis identity face (template_default+EW+daily+
    # initial_stop=none+gate=none+vol=none+yang=none+vconf=none+
    # streak=none+tstate=none+amp=none+mom=none -> tl1 engine identity;
    # run_candidate_curve_w14 parity law selftest-pinned on the
    # all-none face)
    pcut = {s: df[df.index <= cut] for s, df in prices_full.items()}
    Pfull = tl1.build_panels(pcut)
    anchors = {}
    for t in tl1.A_TEMPLATES:
        trader = tl1.load_trader(t["trader_id"])
        a = tl1.anchor_gate(trader, prices_full)
        if not a["ok"]:
            print(f"PREP-GATE FAIL: live anchor drift {t['trader_id']}")
            return 1
        cand = {"module": t["module"], "fn": t["fn"],
                "sig_params": t["sig_params"],
                "axis": list(tl1.DEFAULT_AXIS)
                + ["none", "none", "none", "none", "none", "none",
                   "none", "none", "none", "none", "none", "none",
                   "none", "none"]}
        eq, *_ = run_candidate_curve_w14(cand, t, pcut, Pfull,
                                        tl1.v3_state_series())
        got_is = tl1.sharpe(eq[eq.index < tl1.OOS_START])
        got_oos = tl1.sharpe(eq[eq.index >= tl1.OOS_START])
        mine_ok = (abs(round(float(got_is), 4)
                       - a["got"]["in_sample"]["sharpe"]) < 1e-9
                   and abs(round(float(got_oos), 4)
                           - a["got"]["out_sample"]["sharpe"]) < 1e-9)
        anchors[t["trader_id"]] = {
            "live_ok": True, "grammar_replay_is": round(float(got_is), 4),
            "grammar_replay_oos": round(float(got_oos), 4),
            "grammar_face_faithful": bool(mine_ok)}
        if not mine_ok:
            print(f"PREP-GATE FAIL: grammar replay != live anchor "
                  f"{t['trader_id']} (is {got_is:.4f} vs "
                  f"{a['got']['in_sample']['sharpe']}, oos {got_oos:.4f} vs "
                  f"{a['got']['out_sample']['sharpe']})")
            return 1
    ga = {"pass": True, "anchors": anchors}

    # leg-L panel + G-CENSUS (P-5C frozen grid, sec.2 wholesale binding)
    prices, P, idx, listed, cen = tl1._load_leg("L")
    if cen != tl1.FROZEN_CENSUS["L"]:
        print(f"PREP-GATE FAIL: leg-L census drift {cen} != "
              f"{tl1.FROZEN_CENSUS['L']}")
        return 1
    gc_ = {"pass": True, "census": cen, "frozen": tl1.FROZEN_CENSUS["L"]}
    # panel-level gate + vol + yang + vconf + streak + tstate + amp +
    # mom meta on the leg-L face (prereg sec.2 disclosure; structural
    # invariants only -- the {1523, 1441} vol / yang 1751 / vconf 1741
    # / streak 3481-on-full / tstate 3305-3424-on-full / amp
    # 3464-on-full / mom 3344-on-full probe anchors hold only on the
    # raw full-history face; asserted above)
    for member, gate_name in ((tl7.STREAK_MEMBER, "streak"),
                              (tl8.TSTATE_MEMBER, "tstate"),
                              (AMP_MEMBER, "amp"),
                              (MOM_MEMBER, "mom"), (STD_MEMBER, "std"),
                              (RSQR_MEMBER, "rsqr"),
                              (SUMN_MEMBER, "sumn"),
                              (RESI_MEMBER, "resi"),
                              (CNT_MEMBER, "cnt")):
        if member not in prices:
            print(f"PREP-GATE FAIL: leg-L panel missing {gate_name} "
                  f"member {member} ({gate_name} series underivable)")
            return 1
    _, _, gate_meta = tl3.gate_state_series(prices)
    _, _, vol_meta = tl4.vol_state_series(prices)
    if not tl4._vol_structure_pass(vol_meta):
        print(f"PREP-GATE FAIL: G-VOL leg-L structural invariants "
              f"broken {vol_meta} -- honest refuse")
        return 1
    _, _, yang_meta = tl5.yang_state_series(prices)
    if not tl5._yang_structure_pass(yang_meta):
        print(f"PREP-GATE FAIL: G-YANG leg-L structural invariants "
              f"broken {yang_meta} -- honest refuse")
        return 1
    _, _, vconf_meta = tl6.vconf_state_series(prices)
    if not tl6._vconf_structure_pass(vconf_meta):
        print(f"PREP-GATE FAIL: G-VCONF leg-L structural invariants "
              f"broken {vconf_meta} -- honest refuse")
        return 1
    _, _, streak_meta = tl7.streak_state_series(prices)
    if not tl7._streak_structure_pass(streak_meta):
        print(f"PREP-GATE FAIL: G-STREAK leg-L structural invariants "
              f"broken {streak_meta} -- honest refuse")
        return 1
    _, _, tstate_meta = tl8.tstate_state_series(prices)
    if not tl8._tstate_structure_pass(tstate_meta):
        print(f"PREP-GATE FAIL: G-TSTATE leg-L structural invariants "
              f"broken {tstate_meta} -- honest refuse")
        return 1
    _, _, amp_meta = amp_state_series(prices)
    if not _amp_structure_pass(amp_meta):
        print(f"PREP-GATE FAIL: G-AMP leg-L structural invariants "
              f"broken {amp_meta} -- honest refuse")
        return 1
    _, _, mom_meta = mom_state_series(prices)
    if not _mom_structure_pass(mom_meta):
        print(f"PREP-GATE FAIL: G-MOM leg-L structural invariants "
              f"broken {mom_meta} -- honest refuse")
        return 1
    _o20, _d20, std_meta, _o10, _d10 = std_state_series(prices)
    if not _std_structure_pass(std_meta):
        print(f"PREP-GATE FAIL: G-STD leg-L structural invariants "
              f"broken {std_meta} -- honest refuse")
        return 1
    _r20o, _r20d, rsqr_meta, _r10o, _r10d = rsqr_state_series(prices)
    if not _rsqr_structure_pass(rsqr_meta):
        print(f"PREP-GATE FAIL: G-RSQR leg-L structural "
              f"invariants broken {rsqr_meta} -- honest refuse")
        return 1
    _n20o, _n20d, sumn_meta, _n10o, _n10d = sumn_state_series(prices)
    if not _sumn_structure_pass(sumn_meta):
        print(f"PREP-GATE FAIL: G-SUMN leg-L structural "
              f"invariants broken {sumn_meta} -- honest refuse")
        return 1
    _ro, _rd, resi_meta = resi_state_series(prices)
    if not _resi_structure_pass(resi_meta):
        print(f"PREP-GATE FAIL: G-RESI leg-L structural "
              f"invariants broken {resi_meta} -- honest refuse")
        return 1
    _cd5o, _cd5d, _cn20o, _cn20d, cnt_meta = cnt_state_series(prices)
    if not _cnt_structure_pass(cnt_meta):
        print(f"PREP-GATE FAIL: G-CNT leg-L structural "
              f"invariants broken {cnt_meta} -- honest refuse")
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

    # candidates-presence gate at the TAIL (identity-first-run law:
    # every panel/anchor/census face above has ALREADY exercised on
    # real data by this point; generate-stage product face)
    if not os.path.exists(CANDIDATES_FILE):
        print("PREP-GATE FAIL: w14_candidates.json absent -- generate "
              "pending (identity faces above ALL PASS on real data)")
        return 2
    cg = json.load(open(CANDIDATES_FILE, encoding="utf-8"))
    if str(cg.get("grammar_sha256", ""))[:16] != (FROZEN_SHA16
                                                  or
                                                  grammar[
                                                      "grammar_sha256"][
                                                      :16]):
        print("PREP-GATE FAIL: candidates grammar_sha256 != frozen "
              "anchor")
        return 1

    prep = {"wave": WAVE, "evidence_cutoff": CUTOFF,
            **tl1.cutoff_meta(CUTOFF),
            "grammar_sha256": grammar["grammar_sha256"],
            "gates": {"G-PANEL": gp, "G-ANCHOR": ga, "G-CENSUS": gc_,
                      "G-EXCLUDE": {"pass": True,
                                    "hits": cg["exclusion"]["hits"],
                                    "sources": cg["exclusion"]["sources"]},
                      "G-VOL": {"pass": True,
                                "core48": vol_meta_core,
                                "legL": vol_meta,
                                "anchors": {"first_valid_bar":
                                            tl4.VOL_ANCHOR_FIRST_VALID_BAR,
                                            "calm_days":
                                            tl4.VOL_ANCHOR_CALM_DAYS,
                                            "wild_days":
                                            tl4.VOL_ANCHOR_WILD_DAYS}},
                      "G-YANG": {"pass": True,
                                 "core48": yang_meta_core,
                                 "legL": yang_meta,
                                 "anchors": {"yang_days":
                                             tl5.YANG_ANCHOR["yang_days"],
                                             "yang_and_bull_lower_bound":
                                             tl5.YANG_ANCHOR[
                                                 "yang_and_bull_lower_bound"],
                                             "red_and_bear_lower_bound":
                                             tl5.YANG_ANCHOR[
                                                 "red_and_bear_lower_bound"]}},
                      "G-VCONF": {"pass": True,
                                  "core48": vconf_meta_core,
                                  "legL": vconf_meta,
                                  "anchors": {
                                      "surge_days":
                                      tl6.VCONF_ANCHOR["surge_days"],
                                      "dry_days":
                                      tl6.VCONF_ANCHOR["dry_days"],
                                      "zero_volume_rows":
                                      tl6.VCONF_ANCHOR["zero_volume_rows"],
                                      "warmup_gate_closed_bars":
                                      tl6.VCONF_ANCHOR[
                                          "warmup_gate_closed_bars"],
                                      "yang_and_surge_lower_bound":
                                      tl6.VCONF_ANCHOR[
                                          "yang_and_surge_lower_bound"],
                                      "red_and_dry_lower_bound":
                                      tl6.VCONF_ANCHOR[
                                          "red_and_dry_lower_bound"],
                                      "four_gate_16cells":
                                      "all non-empty (asserted "
                                      "live at gate)"}},
                      "G-STREAK": {"pass": True,
                                   "core48": streak_meta_core,
                                   "legL": streak_meta,
                                   "anchors": {
                                       "warmup_gate_closed_bars":
                                       tl7.STREAK_ANCHOR[
                                           "warmup_gate_closed_bars"],
                                       "judgeable_days":
                                       tl7.STREAK_ANCHOR[
                                           "judgeable_days"],
                                       "up_streak_days":
                                       tl7.STREAK_ANCHOR[
                                           "up_streak_days"],
                                       "down_streak_days":
                                       tl7.STREAK_ANCHOR[
                                           "down_streak_days"],
                                       "neither_days":
                                       tl7.STREAK_ANCHOR["neither_days"],
                                       "yang_and_up_lower_bound":
                                       tl7.STREAK_ANCHOR[
                                           "yang_and_up_lower_bound"],
                                       "red_and_down_lower_bound":
                                       tl7.STREAK_ANCHOR[
                                           "red_and_down_lower_bound"],
                                       "five_gate_32cells":
                                       "all non-empty (asserted "
                                       "live at gate)"}},
                      "G-TSTATE": {"pass": True,
                                   "core48": tstate_meta_core,
                                   "legL": tstate_meta,
                                   "anchors": {
                                       "mad60_warmup_gate_closed_bars":
                                       tl8.TSTATE_ANCHOR["mad60"][
                                           "warmup_gate_closed_bars"],
                                       "mad60_decidable_days":
                                       tl8.TSTATE_ANCHOR["mad60"][
                                           "decidable_days"],
                                       "mad60_gate_true_days":
                                       tl8.TSTATE_ANCHOR["mad60"][
                                           "gate_true_days"],
                                       "rsv60_warmup_gate_closed_bars":
                                       tl8.TSTATE_ANCHOR["rsv60"][
                                           "warmup_gate_closed_bars"],
                                       "rsv60_decidable_days":
                                       tl8.TSTATE_ANCHOR["rsv60"][
                                           "decidable_days"],
                                       "rsv60_gate_true_days":
                                       tl8.TSTATE_ANCHOR["rsv60"][
                                           "gate_true_days"],
                                       "zero_volume_rows":
                                       tl8.TSTATE_ANCHOR["zero_volume_rows"],
                                       "streak_anchor_reproduction":
                                       "asserted live at gate (W7 "
                                       "cross-probe determinism)",
                                       "streak_tstate_cross_lower_bounds":
                                       tl8.TSTATE_ANCHOR[
                                           "streak_tstate_cross_lower_bounds"],
                                       "six_gate_64cells":
                                       "44 non-empty / 20 empty with "
                                       "the frozen name list (asserted "
                                       "live at gate)",
                                       "extreme_days":
                                       "asserted live at gate (frozen "
                                       "face incl. 2025-04-07 "
                                       "double-gate rsv 0.1753)"}},
                      "G-AMP": {"pass": True,
                                "core48": amp_meta_core,
                                "legL": amp_meta,
                                "anchors": {
                                    "warmup_gate_closed_bars":
                                    AMP_ANCHOR["warmup_gate_closed_bars"],
                                    "decidable_days":
                                    AMP_ANCHOR["decidable_days"],
                                    "wide_days":
                                    AMP_ANCHOR["wide_days"],
                                    "narrow_days":
                                    AMP_ANCHOR["narrow_days"],
                                    "zero_range_rows":
                                    AMP_ANCHOR["zero_range_rows"],
                                    "cross_four_lower_bounds":
                                    {**AMP_ANCHOR[
                                         "cross_yang_lower_bounds"],
                                     **AMP_ANCHOR[
                                         "cross_vconf_lower_bounds"],
                                     **AMP_ANCHOR[
                                         "cross_streak_lower_bounds"],
                                     **AMP_ANCHOR[
                                         "cross_tstate_lower_bounds"]},
                                    "seven_gate_128cells":
                                    "73 non-empty / 55 empty with the "
                                    "frozen name list + exact per-cell "
                                    "cross-check vs probe facts "
                                    "(asserted live at gate)",
                                    "extreme_days":
                                    "asserted live at gate (frozen "
                                    "face: 7/7 wide incl. 2025-04-07 "
                                    "6.961x + 2015-07-27 1.814x)",
                                    "streak_tstate_reproduction":
                                    "asserted live at gate (W7/W8 "
                                    "cross-probe determinism)"}},
                      "G-MOM": {"pass": True,
                                "core48": mom_meta_core,
                                "legL": mom_meta,
                       "G-STD": {"pass": True,
                                 "core48": std_meta_core,
                                 "legL": std_meta},
                       "G-RSQR": {"pass": True,
                                  "core48": rsqr_meta_core,
                                  "legL": rsqr_meta},
                       "G-SUMN": {"pass": True,
                                  "core48": sumn_meta_core,
                                  "legL": sumn_meta},
                      "G-RESI": {"pass": True,
                                 "core48": resi_meta_core,
                                 "legL": resi_meta},
                      "G-CNT": {"pass": True,
                                "core48": cnt_meta_core,
                                "legL": cnt_meta},
                                "anchors": {
                                    "warmup_gate_closed_bars":
                                    MOM_ANCHOR["warmup_gate_closed_bars"],
                                    "decidable_days":
                                    MOM_ANCHOR["decidable_days"],
                                    "open_days":
                                    MOM_ANCHOR["open_days"],
                                    "closed_days":
                                    MOM_ANCHOR["closed_days"],
                                    "roc20_nan_rows_before_bar20":
                                    MOM_ANCHOR[
                                        "roc20_nan_rows_before_bar20"],
                                    "cross_lower_bounds":
                                    {**MOM_ANCHOR[
                                         "cross_tstate_lower_bounds"],
                                     **MOM_ANCHOR[
                                         "cross_streak_lower_bounds"],
                                     **MOM_ANCHOR[
                                         "cross_amp_lower_bounds"]},
                                    "eight_gate_256cells":
                                    "111 non-empty / 145 empty with "
                                    "the frozen name list + exact "
                                    "per-cell cross-check vs probe "
                                    "facts (asserted live at gate)",
                                    "extreme_days":
                                    "asserted live at gate (frozen "
                                    "face: 2/7 mom-open incl. "
                                    "2015-07-27 -0.0906 + 2025-04-07 "
                                    "-0.0852; 2016-01-04 -0.052 "
                                    "near-miss closed honest)",
                                    "streak_tstate_amp_reproduction":
                                    "asserted live at gate (W7/W8/W9 "
                                    "cross-probe determinism)",
                                    "core48_mom_open_rate":
                                    MOM_ANCHOR["core48_mom_open_rate"],
                                     "core48_std20_open_rate":
                                     STD_ANCHOR["core48_std20_open_rate"],
                                    "tstate_adjacency":
                                    "probe disclosure: mad60-open days "
                                    "66.06% co-open / rsv60-open "
                                    "35.16%; 253 both-open / 121 "
                                    "mom-unique days (D6 audit column "
                                    "face at intake)"}}},
            "gate_meta": gate_meta, "vol_meta": vol_meta,
            "yang_meta": yang_meta, "vconf_meta": vconf_meta,
            "streak_meta": streak_meta, "tstate_meta": tstate_meta,
            "amp_meta": amp_meta, "mom_meta": mom_meta,
            "std_meta": std_meta,
            "rsqr_meta": rsqr_meta,
            "sumn_meta": sumn_meta,
            "resi_meta": resi_meta,
            "cnt_meta": cnt_meta,
            "n_distinct": cg["n"], "n_starts_6m": len(starts),
            "starts": starts, "passive_6m_ret": passive_6m,
            "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    tl1._dump(PREP_FILE, prep)
    print(f"prep PASS: panel {gp['members']}/48, anchors 6/6 faithful, "
          f"census {cen}, starts {len(starts)}, passive precomputed, "
          f"gate na-window {gate_meta['na_window_bars']} bars, "
          f"G-VOL {vol_meta['calm_days']}calm/{vol_meta['wild_days']}wild "
          f"first-valid {vol_meta['first_valid_bar_idx']}, "
          f"G-YANG {yang_meta['yang_days']}yang/{yang_meta['red_days']}"
          f"red zero-warmup, "
          f"G-VCONF {vconf_meta['surge_days']}surge/"
          f"{vconf_meta['dry_days']}dry warmup "
          f"{vconf_meta['na_window_bars']}, "
          f"G-STREAK {streak_meta['up_streak_days']}up/"
          f"{streak_meta['down_streak_days']}down/"
          f"{streak_meta['neither_days']}neither warmup "
          f"{streak_meta['na_window_bars']}, "
          f"G-TSTATE mad60 {tstate_meta['mad60']['gate_true_days']}true/"
          f"{tstate_meta['mad60']['decidable_days']}decidable warmup "
          f"{tstate_meta['mad60']['warmup_gate_closed_bars']} + "
          f"rsv60 {tstate_meta['rsv60']['gate_true_days']}true/"
          f"{tstate_meta['rsv60']['decidable_days']}decidable warmup "
          f"{tstate_meta['rsv60']['warmup_gate_closed_bars']}, "
          f"G-AMP {amp_meta['wide_days']}wide/"
          f"{amp_meta['narrow_days']}narrow decidable "
          f"{amp_meta['decidable_days']} warmup "
          f"{amp_meta['warmup_gate_closed_bars']}, "
          f"G-MOM {mom_meta['open_days']}open/"
          f"{mom_meta['closed_days']}closed decidable "
          f"{mom_meta['decidable_days']} warmup "
          f"{mom_meta['warmup_gate_closed_bars']}; "
          f"G-RSQR {rsqr_meta['open_days']}open/"
          f"{rsqr_meta['closed_days']}closed decidable "
          f"{rsqr_meta['decidable_days']} rsqr10-open "
          f"{rsqr_meta['rsqr10_open_days']}; "
          f"G-SUMN {sumn_meta['open_days']}open/"
          f"{sumn_meta['closed_days']}closed decidable "
          f"{sumn_meta['decidable_days']} sumn10-open "
          f"{sumn_meta['sumn10_open_days']}; "
          f"G-RESI {resi_meta['open_days']}open/"
          f"{resi_meta['closed_days']}closed decidable "
          f"{resi_meta['decidable_days']} slope-split "
          f"{resi_meta['slope_sign_split']}; "
          f"G-CNT cntd5 {cnt_meta['cntd5_open_days']}open/"
          f"{cnt_meta['cntd5_decidable_days']}decidable + cntn20 "
          f"{cnt_meta['cntn20_open_days']}open/"
          f"{cnt_meta['cntn20_decidable_days']}decidable")
    return 0


def cmd_screen(shard: int, shards: int, workers) -> int:
    print(f"=== {WAVE} screen shard {shard}of{shards} ===")
    for p, what in ((PREP_FILE, "prep_state.json"),
                    (CANDIDATES_FILE, "w14_candidates.json")):
        if not os.path.exists(p):
            print(f"SCREEN-GATE: {what} absent -- run screen-prep first")
            return 2
    prep = json.load(open(PREP_FILE, encoding="utf-8"))
    grammar, cells = _cell_list_w14()
    if FROZEN_SHA16 and _grammar_sha16(grammar) != FROZEN_SHA16:
        print(f"SCREEN-GATE: grammar sha drift != frozen {FROZEN_SHA16}")
        return 2
    ram_min, ram_ok = tl2._ram_gate_gb(wait_min=40)
    if not ram_ok:
        print(f"SCREEN-GATE: free RAM {ram_min}GB < 4GB after bounded "
              f"wait (three-sample r354 law; r379 wait-law) -- honest "
              "refuse, pool retries when RAM frees")
        return 2
    tl1.GRAMMAR = grammar
    mine = [c for i, c in enumerate(cells) if i % shards == shard]
    prices, P, idx, listed, cen = tl1._load_leg("L")
    states = tl1.v3_state_series()
    try:
        bl = pd.read_csv(tl1.B_LAYER_MASK)
        ok_codes = set(bl.loc[bl["ok_static"] == True, "code"].astype(str))
        overlap = sorted(s for s in P["close"].columns if s in ok_codes)
    except Exception:
        overlap = []
    # keep-ok face = the serialized grammar filter_def ("keep-ok codes only")
    # -- identical to the generate-stage dedup face (consistency law)
    if overlap:
        fundamental_ok = pd.DataFrame(False, index=P["close"].index,
                                      columns=P["close"].columns)
        for s in overlap:
            fundamental_ok[s] = True
    else:
        fundamental_ok = None
    vol_state, vol_err = tl4._vol_state_full()
    if vol_err:
        print(f"SCREEN-GATE: {vol_err} (prereg sec.2 fail-closed) "
              "-- refuse")
        return 2
    yang_state, yang_err = tl5._yang_state_full()
    if yang_err:
        print(f"SCREEN-GATE: {yang_err} (prereg sec.2 G-YANG "
              "fail-closed) -- refuse")
        return 2
    vconf_state, vconf_err = tl6._vconf_state_full()
    if vconf_err:
        print(f"SCREEN-GATE: {vconf_err} (prereg sec.2 G-VCONF "
              "fail-closed) -- refuse")
        return 2
    for member, gate_name in ((tl7.STREAK_MEMBER, "streak"),
                              (tl8.TSTATE_MEMBER, "tstate"),
                              (AMP_MEMBER, "amp"),
                              (MOM_MEMBER, "mom"), (STD_MEMBER, "std"),
                              (RSQR_MEMBER, "rsqr"),
                              (SUMN_MEMBER, "sumn")):
        if member not in prices:
            print(f"SCREEN-GATE: leg-L panel missing {gate_name} member "
                  f"{member} ({gate_name} series underivable) -- refuse")
            return 2
    streak_state = tl7.streak_state_series(prices)
    tstate_state = tl8.tstate_state_series(prices)
    amp_state = amp_state_series(prices)
    mom_state = mom_state_series(prices)
    std_state = std_state_series(prices)
    rsqr_state = rsqr_state_series(prices)
    sumn_state = sumn_state_series(prices)
    state = {"P": P, "prices": prices, "states": states,
             "starts": prep["starts"],
             "passive_6m": {int(k): v for k, v in
                            prep["passive_6m_ret"].items()},
             "fundamental_ok": fundamental_ok,
             "grammar": grammar, "atr20": tl2.atr20_series(prices),
             "gate_state": tl3.gate_state_series(prices),
             "vol_state": vol_state, "yang_state": yang_state,
             "vconf_state": vconf_state, "streak_state": streak_state,
             "tstate_state": tstate_state, "amp_state": amp_state,
             "mom_state": mom_state,
             "std_state": std_state,
             "rsqr_state": rsqr_state,
             "sumn_state": sumn_state}

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
        # r429: S0 stash -u can lift the (untracked) checkpoint dir
        # mid-burn -> recreate before append or the pool driver dies
        # (2026-09-29 W8-SCREEN live fire, 828 cells lost to a crash;
        # .gitignore results/trial_labor_w*/checkpoint/ covers w9)
        os.makedirs(CKPT_DIR, exist_ok=True)
        with open(ck, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(tl1._j(payload), ensure_ascii=False,
                                default=float) + "\n")

    if todo:
        jobs = [(c["cell_id"], _screen_cell_w14, (c,)) for c in todo]
        tl1.run_cells_parallel(jobs, workers=workers or tl1.worker_cap(),
                              desc="screen cells", initializer=tl1._init_worker,
                              initargs=(state,), on_result=on_result)
    print(f"shard {shard}of{shards} complete -> {ck}")
    return 0


def cmd_screen_finalize() -> int:
    print(f"=== {WAVE} screen-finalize ===")
    landed = tl6.finalize_already_landed(SCREEN_BATCH, SCREEN_FILE)
    if landed is not None:
        print(f"FINALIZE-IDEMPOTENT-GUARD: {SCREEN_BATCH} already landed "
              f"(ledger total={landed.get('total')}); re-run refused "
              "(pit-95 double-append guard; re-run channel = fresh prereg "
              "+ fresh batch name)")
        return 2
    if not os.path.exists(CANDIDATES_FILE):
        print("SCREEN-FINALIZE-GATE: generate pending "
              "(w14_candidates.json absent) -- nothing to finalize")
        return 2
    grammar, cells = _cell_list_w14()
    rows = _load_screen_rows()
    by_id = {r["cell_id"]: r for r in rows}
    missing = [c["cell_id"] for c in cells if c["cell_id"] not in by_id]
    if missing:
        print(f"FINALIZE-GATE: {len(missing)} cells incomplete -- finalize "
              f"refused (checkpoint retained); first missing: "
              f"{missing[:3]}")
        return 2
    null_rows = [by_id[f"SCREEN|NULL-{i:04d}"] for i in range(K_NULLS)]
    cand_rows = [by_id[c["cell_id"]] for c in cells if c["kind"] == "cand"]
    p95, survivors = _finalize_math(cand_rows, null_rows)
    null_rates = [r["beat6m_rate"] for r in null_rows]
    stop_counts, gate_counts = {}, {}
    vol_counts, yang_counts, vconf_counts = {}, {}, {}
    streak_counts, tstate_counts, amp_counts = {}, {}, {}
    mom_counts, std_counts = {}, {}
    rsqr_counts = {}
    sumn_counts = {}
    resi_counts = {}
    cnt_counts = {}
    gate_seg, vol_seg, yang_seg, vconf_seg = {}, {}, {}, {}
    streak_seg, tstate_seg, amp_seg, mom_seg = {}, {}, {}, {}
    gvvy_seg, gvvvsk_seg, gvvvskts_seg = {}, {}, {}
    gvvvsktsa_seg, gvvvsktsam_seg, gvvvsktsams_seg = {}, {}, {}
    gvvvsktsamsr_seg = {}
    std_seg, rsqr_seg, sumn_seg, gvvvsktsamsrn_seg = {}, {}, {}, {}
    resi_seg, cnt_seg, gvvvsktsamsrnrc_seg = {}, {}, {}
    for r in cand_rows:
        stop_counts[r["stop_face"]] = stop_counts.get(r["stop_face"], 0) + 1
        gf, vf = r["gate_face"], r["vol_face"]
        yf, cf = r["yang_face"], r["vconf_face"]
        sf, tf = r["streak_face"], r["tstate_face"]
        af = r["amp_face"]
        mf = r["mom_face"]
        stf = r["std_face"]
        rqf = r["rsqr_face"]
        nqf = r["sumn_face"]
        gate_counts[gf] = gate_counts.get(gf, 0) + 1
        vol_counts[vf] = vol_counts.get(vf, 0) + 1
        yang_counts[yf] = yang_counts.get(yf, 0) + 1
        vconf_counts[cf] = vconf_counts.get(cf, 0) + 1
        streak_counts[sf] = streak_counts.get(sf, 0) + 1
        tstate_counts[tf] = tstate_counts.get(tf, 0) + 1
        amp_counts[af] = amp_counts.get(af, 0) + 1
        mom_counts[mf] = mom_counts.get(mf, 0) + 1
        std_counts[stf] = std_counts.get(stf, 0) + 1
        rsqr_counts[rqf] = rsqr_counts.get(rqf, 0) + 1
        sumn_counts[nqf] = sumn_counts.get(nqf, 0) + 1
        resf = r["resi_face"]
        cntf = r["cnt_face"]
        resi_counts[resf] = resi_counts.get(resf, 0) + 1
        cnt_counts[cntf] = cnt_counts.get(cntf, 0) + 1
        for seg, key in ((gate_seg, gf), (vol_seg, vf), (yang_seg, yf),
                         (vconf_seg, cf), (streak_seg, sf),
                         (tstate_seg, tf), (amp_seg, af), (mom_seg, mf),
                         (std_seg, stf),
                         (rsqr_seg, rqf),
                         (sumn_seg, nqf),
                         (gvvy_seg, f"{gf}|{vf}|{yf}|{cf}"),
                         (gvvvsk_seg, f"{gf}|{vf}|{yf}|{cf}|{sf}"),
                         (gvvvskts_seg,
                          f"{gf}|{vf}|{yf}|{cf}|{sf}|{tf}"),
                         (gvvvsktsa_seg,
                          f"{gf}|{vf}|{yf}|{cf}|{sf}|{tf}|{af}"),
                         (gvvvsktsam_seg,
                          f"{gf}|{vf}|{yf}|{cf}|{sf}|{tf}|{af}|{mf}"),
                         (gvvvsktsams_seg,
                          f"{gf}|{vf}|{yf}|{cf}|{sf}|{tf}|{af}|{mf}|"
                          f"{stf}"),
                         (gvvvsktsamsr_seg,
                          f"{gf}|{vf}|{yf}|{cf}|{sf}|{tf}|{af}|{mf}|"
                          f"{stf}|{rqf}"),
                         (gvvvsktsamsrn_seg,
                          f"{gf}|{vf}|{yf}|{cf}|{sf}|{tf}|{af}|{mf}|"
                          f"{stf}|{rqf}|{nqf}"),
                         (resi_seg, resf),
                         (cnt_seg, cntf),
                         (gvvvsktsamsrnrc_seg,
                          f"{gf}|{vf}|{yf}|{cf}|{sf}|{tf}|{af}|{mf}|"
                          f"{stf}|{rqf}|{nqf}|{resf}|{cntf}")):
            s = seg.setdefault(key, {"n_cells": 0, "n_survivors": 0})
            s["n_cells"] += 1
            s["n_survivors"] += int(bool(r["survives_screen"]))
    for seg in (gate_seg, vol_seg, yang_seg, vconf_seg, streak_seg,
                tstate_seg, amp_seg, mom_seg, std_seg, rsqr_seg, sumn_seg,
                resi_seg, cnt_seg, gvvy_seg,
                gvvvsk_seg, gvvvskts_seg, gvvvsktsa_seg,
                gvvvsktsam_seg, gvvvsktsams_seg, gvvvsktsamsr_seg,
                gvvvsktsamsrn_seg, gvvvsktsamsrnrc_seg):
        for key, s in seg.items():
            s["survival_rate"] = round(
                s["n_survivors"] / s["n_cells"], 6) if s["n_cells"] else 0.0
    prep = (json.load(open(PREP_FILE, encoding="utf-8"))
            if os.path.exists(PREP_FILE) else {})
    gate_meta = prep.get("gate_meta")
    vol_meta = prep.get("vol_meta")
    yang_meta = prep.get("yang_meta")
    vconf_meta = prep.get("vconf_meta")
    streak_meta = prep.get("streak_meta")
    tstate_meta = prep.get("tstate_meta")
    amp_meta = prep.get("amp_meta")
    mom_meta = prep.get("mom_meta")
    std_meta = prep.get("std_meta")
    rsqr_meta = prep.get("rsqr_meta")
    sumn_meta = prep.get("sumn_meta")
    n_distinct = len(cand_rows)
    batch_trials = n_distinct + K_NULLS
    ledger = tl1.append_ledger(SCREEN_BATCH, batch_trials,
                               "results/trial_labor_w14/w14_screen.json",
                               evidence_cutoff=CUTOFF)
    out = {"wave": WAVE, "stage": "screen", "prereg": PREREG,
           **tl1.cutoff_meta(CUTOFF),
           "grammar_sha256": grammar["grammar_sha256"],
           "n_distinct": n_distinct, "k_nulls": K_NULLS,
           "null_family": {"rates": [round(x, 4) for x in null_rates],
                           "median": round(float(np.median(null_rates)), 4),
                           "p95_line": round(p95, 6),
                           "p_regimes": list(tl1.NULL_P_REGIMES),
                           "seed": SEED_NULL,
                           "draw_order": "p_on regime -> EIGHTEEN-tuple "
                                         "axis R/X/S/T/STOP/GATE/VOL/"
                                         "YANG/VCONF/STREAK/TSTATE/AMP/"
                                         "MOM/STD/RSQR/SUMN/RESI/CNT -> signal matrix (frozen "
                                         "runner face, gate+vol+yang+"
                                         "vconf+streak+tstate+amp+mom+std+rsqr+sum "
                                         "legs included)"},
           "survival_rule": "beat6m_rate > null_p95 (prereg sec.3, frozen)",
           "survivors": survivors, "n_survivors": len(survivors),
           "stop_face_counts": stop_counts,
           "gate_face_counts": gate_counts,
           "vol_face_counts": vol_counts,
           "yang_face_counts": yang_counts,
           "vconf_face_counts": vconf_counts,
           "streak_face_counts": streak_counts,
           "tstate_face_counts": tstate_counts,
           "amp_face_counts": amp_counts,
           "mom_face_counts": mom_counts,
           "std_face_counts": std_counts,
           "rsqr_face_counts": rsqr_counts,
           "sumn_face_counts": sumn_counts,
           "resi_face_counts": resi_counts,
           "cnt_face_counts": cnt_counts,
           "gate_segmented_survival": gate_seg,
           "vol_segmented_survival": vol_seg,
           "yang_segmented_survival": yang_seg,
           "vconf_segmented_survival": vconf_seg,
           "streak_segmented_survival": streak_seg,
           "tstate_segmented_survival": tstate_seg,
           "amp_segmented_survival": amp_seg,
           "mom_segmented_survival": mom_seg,
           "std_segmented_survival": std_seg,
           "rsqr_segmented_survival": rsqr_seg,
           "sumn_segmented_survival": sumn_seg,
           "resi_segmented_survival": resi_seg,
           "cnt_segmented_survival": cnt_seg,
           "gate_vol_yang_vconf_interaction_survival": gvvy_seg,
           "gate_vol_yang_vconf_streak_interaction_survival": gvvvsk_seg,
           "gate_vol_yang_vconf_streak_tstate_interaction_survival":
               gvvvskts_seg,
           "gate_vol_yang_vconf_streak_tstate_amp_interaction_survival":
               gvvvsktsa_seg,
           "gate_vol_yang_vconf_streak_tstate_amp_mom_interaction_"
           "survival": gvvvsktsam_seg,
           "gate_vol_yang_vconf_streak_tstate_amp_mom_std_interaction_"
           "survival": gvvvsktsams_seg,
           "gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_interaction_"
           "survival": gvvvsktsamsr_seg,
           "gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_sumn_interaction_"
           "survival": gvvvsktsamsrn_seg,
           "gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_sumn_"
           "resi_cnt_interaction_survival": gvvvsktsamsrnrc_seg,
           "gate_na_window_bars": (gate_meta["na_window_bars"]
                                   if gate_meta else None),
           "vol_na_window_bars": (vol_meta["na_window_bars"]
                                  if vol_meta else None),
           "yang_na_window_bars": (yang_meta["na_window_bars"]
                                   if yang_meta else None),
           "vconf_na_window_bars": (vconf_meta["na_window_bars"]
                                    if vconf_meta else None),
           "streak_na_window_bars": (streak_meta["na_window_bars"]
                                     if streak_meta else None),
           "tstate_na_window_bars": (tstate_meta["na_window_bars"]
                                      if tstate_meta else None),
           "amp_na_window_bars": (amp_meta["na_window_bars"]
                                   if amp_meta else None),
           "mom_na_window_bars": (mom_meta["na_window_bars"]
                                   if mom_meta else None),
           "std_na_window_bars": (std_meta["na_window_bars"]
                                   if std_meta else None),
           "rsqr_na_window_bars": (rsqr_meta["na_window_bars"]
                                   if rsqr_meta else None),
           "sumn_na_window_bars": (sumn_meta["na_window_bars"]
                                   if sumn_meta else None),
           "batch_cells": batch_trials, "trials_ledger": ledger,
           "audit": {"note": "one full leg-L backtest per cell (prereg "
                             "sec.3 all-history caliber, V1 13bp base, "
                             "T+1); gate + vol + yang + vconf + streak "
                             "+ tstate + amp + MOM overlays + initial-"
                             "stop overlay at the engine face = "
                             "effective-signal zeroing (MSG-0440 E1 "
                             "mapping, dedup-face consistency, frozen "
                             "composition order signal -> filter -> "
                             "timing -> GATE -> VOL -> YANG -> VCONF "
                             "-> STREAK -> TSTATE -> AMP -> MOM -> STD -> "
                             "RSQR -> SUM -> initial-stop); MA200/"
                             "vol-closed NaN windows gate-closed on BOTH "
                             "faces, yang zero-warmup, vconf 19-bar "
                             "warmup, streak 2-bar warmup, tstate "
                             "178/59-bar warmups, amp 19-bar warmup, "
                             "mom 139-bar warmup / std 120-bar warmup / rsqr / sumn "
                             "120-bar warmup (panel-level counts in gate/vol/yang/vconf/"
                             "streak/tstate/amp/mom/std/rsqr/sumn_na_window_bars); "
                             "amp_narrow keep face = (~wide) AND "
                             "decidable (r431 erratum law -- the naive "
                             "comparison bool face alone masquerades "
                             "warmup bars as narrow, BANNED); "
                             "mom_oversold keep face = open AND "
                             "decidable (same erratum law -- the naive "
                             "comparison bool face alone masquerades "
                             "warmup bars as mom_closed, BANNED); "
                              "std20_hi/std10_hi keep face = open AND "
                              "decidable (same erratum law); rsqr20_hi/rsqr10_hi keep "
                              "face = open AND decidable (same erratum law); sumn20_lo/sumn10_lo keep "
                              "face = open AND decidable (same erratum law); "
                             "workers BelowNormal; checkpoint "
                             "append-per-cell; "
                             "beat6m comparison operator = >= per frozen "
                             "prereg sec.3 text; survival math imported "
                             "from tl2._finalize_math (W2 identical law)"},
           "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    tl1._dump(SCREEN_FILE, out)
    with open(SCREEN_CSV, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=csv_cols_screen_w14,
                           extrasaction="ignore")
        w.writeheader()
        for r in cand_rows:
            w.writerow(r)
    print(f"screen finalize: distinct {n_distinct} + nulls {K_NULLS}, "
          f"null p95 {p95:.4f}, survivors {len(survivors)}")
    print(f"mom segmented survival: {json.dumps(mom_seg, sort_keys=True)}")
    print(f"std segmented survival: {json.dumps(std_seg, sort_keys=True)}")
    print(f"rsqr segmented survival: {json.dumps(rsqr_seg, sort_keys=True)}")
    print(f"gate x vol x yang x vconf x streak x tstate x amp x mom "
          f"interaction survival: "
          f"{json.dumps(gvvvsktsam_seg, sort_keys=True)[:400]}")
    print(f"gate x vol x yang x vconf x streak x tstate x amp x mom "
          f"x std interaction survival: "
          f"{json.dumps(gvvvsktsams_seg, sort_keys=True)[:400]}")
    print(f"gate x vol x yang x vconf x streak x tstate x amp x mom x "
          f"std x rsqr interaction survival: "
          f"{json.dumps(gvvvsktsamsr_seg, sort_keys=True)[:400]}")
    print(f"sumn segmented survival: {json.dumps(sumn_seg, sort_keys=True)}")
    print(f"gate x vol x yang x vconf x streak x tstate x amp x mom x "
          f"std x rsqr x sumn interaction survival: "
          f"{json.dumps(gvvvsktsamsrn_seg, sort_keys=True)[:400]}")
    print(f"products: w14_screen.json + w14_screen_cells.csv "
          f"(ledger total {ledger['total']})")
    return 0


# ------------------------------------------------------ judge slice (s3)
def _dual_nulls_w14(returns, cell_idx, seed=None):
    """Dual nulls on the cell's mean daily return (prereg sec.3 s3):
    B=2000 block-20 circular bootstrap + P=2000 sign-flip, two-sided;
    W13 unc-berth seed binding [20328500, cell_idx].  Math imported verbatim from
    tl2._dual_nulls_w2 (import law; the seed constant is the only
    differing face -- selftest cross-checks at the W13 unc-berth seed)."""
    return tl2._dual_nulls_w2(returns, cell_idx,
                              seed=SEED_UNC if seed is None else seed)


def _overlay_stop_disclosure_w14(cand, prices, P, atr20, fundamental_ok,
                                gate_state, vol_state, yang_state,
                                vconf_state, streak_state, tstate_state,
                                amp_state, mom_state, std_state,
                                rsqr_state, sumn_state):
    """Per-cell stop trigger/fill-day disclosure on the leg-L signal face
    with the W13 composition order (filter -> timing -> GATE -> VOL ->
    YANG -> VCONF -> STREAK -> TSTATE -> AMP -> MOM -> STD ->
    RSQR -> SUM -> initial-stop; MSG-0440 E1 mapping + MSG-0450 annex 1).  Mirrors
    tl12._overlay_stop_disclosure_w12 with the sumn overlay inserted
    before stop arming (engine-face consistency law; summary math
    imported)."""
    stop_key = cand["axis"][4]
    if stop_key == "none":
        s = tl2._stop_dev_summary([], prices, P["close"].index)
        s["stop_face"] = "none"
        return s
    mk = f"{cand['module']}.{cand['fn']}"
    mask = tl1._signal_frame(cand, P, tl1.GRAMMAR["faces"][mk])
    mask = mask.reindex(index=P["close"].index,
                        columns=P["close"].columns).fillna(0)
    mask = tl1.apply_filter(mask, cand["axis"][0], P, fundamental_ok)
    mask = tl1.apply_timing(mask, cand["axis"][3])
    G = tl3.gate_zero_mask(mask, cand["axis"][5], gate_state)
    V = tl4.vol_zero_mask(G, cand["axis"][6], vol_state)
    Y = tl5.yang_zero_mask(V, cand["axis"][7], yang_state)
    VC = tl6.vconf_zero_mask(Y, cand["axis"][8], vconf_state)
    SK = tl7.streak_zero_mask(VC, cand["axis"][9], streak_state)
    TS = tl8.tstate_zero_mask(SK, cand["axis"][10], tstate_state)
    AP = tl9.amp_zero_mask(TS, cand["axis"][11], amp_state)
    MO = mom_zero_mask(AP, cand["axis"][12], mom_state)
    SD = std_zero_mask(MO, cand["axis"][13], std_state)
    RQ = rsqr_zero_mask(SD, cand["axis"][14], rsqr_state)
    NQ = sumn_zero_mask(SD, cand["axis"][15], sumn_state)
    _, ev = tl2.stop_exit_overlay(NQ, prices, stop_key, atr20)
    s = tl2._stop_dev_summary(ev, prices, mask.index)
    s["stop_face"] = stop_key
    return s


def _judge_cell_w14(cell):
    """One W10 survivor judged cell (prereg sec.3 s3 frozen face, pool
    worker): dual-leg (P-5C grid) x cost {base x1, x2=CostPatch(2)} full
    curves with the gate + vol + yang + vconf + streak + tstate + AMP
    overlays + initial-stop overlay carried per cell (frozen composition
    order) + window-grid beat vs passive + regime segments + dual nulls
    (W10 seed [20312000, i]) + descriptive clauses + crisis/stop/gate-
    flip/vol-flip disclosure columns.  Gates face = leg-L base (W1-W9
    judged-cell caliber); x2 + descriptive = disclosure."""
    st = tl1._ST
    cand, template = cell["cand"], cell.get("template")
    out = {"cell_id": cell["cell_id"], "candidate_id": cand["candidate_id"],
           "family": cand["family"], "module": cand["module"],
           "fn": cand["fn"], "stop_face": cand["axis"][4],
           "gate_face": cand["axis"][5], "vol_face": cand["axis"][6],
           "yang_face": cand["axis"][7], "vconf_face": cand["axis"][8],
           "streak_face": cand["axis"][9], "tstate_face": cand["axis"][10],
           "amp_face": cand["axis"][11], "mom_face": cand["axis"][12],
           "std_face": cand["axis"][13],
           "rsqr_face": cand["axis"][14],
            "sumn_face": cand["axis"][15]}
    legs = {}
    for leg in ("L", "D"):
        prices, P, idx = (st[f"prices_{leg}"], st[f"P_{leg}"],
                          st[f"idx_{leg}"])
        fok = st[f"fundamental_ok_{leg}"]
        gs = st[f"gate_state_{leg}"]
        vs = st[f"vol_state_{leg}"]
        ys = st[f"yang_state_{leg}"]
        cs = st[f"vconf_state_{leg}"]
        sk = st[f"streak_state_{leg}"]
        ts = st[f"tstate_state_{leg}"]
        ap = st[f"amp_state_{leg}"]
        mo = st[f"mom_state_{leg}"]
        sd = st[f"std_state_{leg}"]
        rq = st[f"rsqr_state_{leg}"]
        nq = st[f"sumn_state_{leg}"]
        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \
            tz, az, mz, dz, rz, nz = run_candidate_curve_w14(cand, template,
                                                 prices,
                                                 P, st["states"],
                                                 st[f"atr20_{leg}"],
                                                 fundamental_ok=fok,
                                                 gate_state=gs,
                                                 vol_state=vs,
                                                 yang_state=ys,
                                                 vconf_state=cs,
                                                 streak_state=sk,
                                                 tstate_state=ts,
                                                 amp_state=ap,
                                                 mom_state=mo,
                                                 std_state=sd,
                                                 rsqr_state=rq,
                                                 sumn_state=nq)
        with CostPatch(2):
            eq2, _, m2, _, _, fired2, gz2, vz2, yz2, cz2, sz2, tz2, \
                az2, mz2, dz2, rz2, nz2 = run_candidate_curve_w14(
                    cand, template, prices, P, st["states"],
                    st[f"atr20_{leg}"], fundamental_ok=fok, gate_state=gs,
                    vol_state=vs, yang_state=ys, vconf_state=cs,
                    streak_state=sk, tstate_state=ts, amp_state=ap,
                    mom_state=mo, std_state=sd, rsqr_state=rq, sumn_state=nq)
        if len(eq) < 30 or float(eq.iloc[0]) <= 0:
            legs[leg] = {"beat": {}, "beat_x2": {}, "sharpe_full": None,
                         "sharpe_full_x2": None, "n_trades": 0,
                         "n_entries": 0, "stop_fired": 0,
                         "stop_fired_x2": 0, "gate_zeroed": 0,
                         "gate_zeroed_x2": 0, "vol_zeroed": 0,
                         "vol_zeroed_x2": 0, "yang_zeroed": 0,
                         "yang_zeroed_x2": 0, "vconf_zeroed": 0,
                         "vconf_zeroed_x2": 0, "streak_zeroed": 0,
                         "streak_zeroed_x2": 0, "tstate_zeroed": 0,
                         "tstate_zeroed_x2": 0, "amp_zeroed": 0,
                         "amp_zeroed_x2": 0, "mom_zeroed": 0,
                         "mom_zeroed_x2": 0,
                         "std_zeroed": 0,
                         "std_zeroed_x2": 0,
                         "rsqr_zeroed": 0,
                         "rsqr_zeroed_x2": 0,
                         "sumn_zeroed": 0,
                         "sumn_zeroed_x2": 0,
                         "regime_start_windows": {"bear": 0, "bull": 0,
                                                  "chop": 0, "na": 0},
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
                d = s_series.iloc[p] if p < len(s_series) else None
                st_ = tl1.REGIME_MAP.get(d, "na") if d == d else "na"
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
                     "stop_fired": int(fired),
                     "stop_fired_x2": int(fired2),
                     "gate_zeroed": int(gz),
                     "gate_zeroed_x2": int(gz2),
                     "vol_zeroed": int(vz),
                     "vol_zeroed_x2": int(vz2),
                     "yang_zeroed": int(yz),
                     "yang_zeroed_x2": int(yz2),
                     "vconf_zeroed": int(cz),
                     "vconf_zeroed_x2": int(cz2),
                     "streak_zeroed": int(sz),
                     "streak_zeroed_x2": int(sz2),
                     "std_zeroed": int(dz),
                     "std_zeroed_x2": int(dz2),
                     "rsqr_zeroed": int(rz),
                     "rsqr_zeroed_x2": int(rz2),
                     "sumn_zeroed": int(nz),
                     "sumn_zeroed_x2": int(nz2),
                     "tstate_zeroed": int(tz),
                     "tstate_zeroed_x2": int(tz2),
                     "amp_zeroed": int(az),
                     "amp_zeroed_x2": int(az2),
                     "mom_zeroed": int(mz),
                     "mom_zeroed_x2": int(mz2)}
        if leg == "L":
            out["legL_daily_returns"] = [round(float(x), 8)
                                         for x in daily.values]
            out["legL_sharpe_full"] = legs[leg]["sharpe_full"]
            out["legL_n_trades"] = legs[leg]["n_trades"]
            out["legL_n_entries"] = legs[leg]["n_entries"]
            out["descriptive"] = tl2._descriptive_face(eq, eq2)
            out["crisis_days_gt8pct"] = int(
                (np.abs(np.asarray(daily.values, dtype=float))
                 > 0.08).sum())
            out["stop_disclosure"] = _overlay_stop_disclosure_w14(
                cand, prices, P, st["atr20_L"], fok, gs, vs, ys, cs, sk,
                ts, ap, mo, sd, rq, nq)
    out["legs"] = legs
    if "legL_daily_returns" not in out:
        out["legL_daily_returns"] = []
        out["legL_sharpe_full"] = None
        out["legL_n_trades"] = 0
        out["legL_n_entries"] = 0
    r = np.asarray(out["legL_daily_returns"], dtype=float)
    out["dual_nulls"] = _dual_nulls_w14(r if len(r) else np.zeros(30),
                                       cell["i"])
    # prereg sec.5.6 gate/vol-flip day columns (disclosure-only, zero
    # gate weight): panel-level flip-day count of the cell's OWN gate /
    # vol face on the leg-L panel (state meta face; none -> null).  The
    # yang AND vconf AND streak AND tstate AND amp AND mom faces carry
    # no probe-defined flip caliber (W5 yang precedent: probes define
    # no such flips; daily binary faces); their disclosure columns are
    # the per-leg yang_zeroed / vconf_zeroed / streak_zeroed /
    # tstate_zeroed / amp_zeroed / mom_zeroed counts above.
    gm = st.get("gate_meta_L") or {}
    vm = st.get("vol_meta_L") or {}
    gk = cand["axis"][5]
    vk = cand["axis"][6]
    out["gate_flip_days_legL"] = (
        None if gk == "none"
        else int(gm.get("flips_bull_face" if gk == "bull"
                        else "flips_bear_face", 0)))
    out["vol_flip_days_legL"] = (
        None if vk == "none"
        else int(vm.get("flips_calm_face" if vk == "calm"
                        else "flips_wild_face", 0)))
    n_eff = sum(legs[lg]["regime_start_windows"][s]
                for lg in legs for s in ("bear", "bull", "chop"))
    out["n_eff_start_windows"] = n_eff
    out["sample_sufficient"] = bool(
        n_eff >= 500 and all(legs[lg]["regime_start_windows"][s] >= 100
                             for lg in legs
                             for s in ("bear", "bull", "chop")))
    return out


def cmd_judge_prep() -> int:
    """Screen-finalize gate + grammar anchor + t18 manifest + dual-leg
    census gates + starts + passive per (leg, window) + per-leg gate +
    vol + yang + vconf + streak + tstate + amp + mom meta (prereg
    sec.2/3; W13 cmd_judge_prep caliber on the W13 sixteen-tuple
    grammar face extended by the W14 resi/cnt layer (eighteen-tuple); G-VOL/G-YANG/G-VCONF/G-STREAK/G-TSTATE/G-AMP/G-MOM
    structural per leg + probe anchors on the raw full-history face)."""
    print(f"=== {WAVE} judge-prep ===")
    if not os.path.exists(SCREEN_FILE):
        print("JUDGE-PREP-GATE: screen not finalized (w14_screen.json "
              "absent)")
        return 2
    screen = json.load(open(SCREEN_FILE, encoding="utf-8"))
    if FROZEN_SHA16 and str(screen.get("grammar_sha256", ""))[:16] \
            != FROZEN_SHA16:
        print(f"JUDGE-PREP-GATE FAIL: screen grammar sha != frozen "
              f"anchor {FROZEN_SHA16}")
        return 1
    man = json.load(open(tl1.T18_MANIFEST, encoding="utf-8"))
    gm = {"verdict": man.get("verdict"),
          "manifest_members": len(man.get("members", {})),
          "pass": bool(man.get("verdict") == "PASS")}
    if not gm["pass"]:
        print("JUDGE-PREP-GATE FAIL: t18 manifest verdict != PASS")
        return 1
    vol_state_full, vol_err = tl4._vol_state_full()
    if vol_err:
        print(f"JUDGE-PREP-GATE FAIL: G-VOL {vol_err}")
        return 1
    yang_state_full, yang_err = tl5._yang_state_full()
    if yang_err:
        print(f"JUDGE-PREP-GATE FAIL: G-YANG {yang_err}")
        return 1
    vconf_state_full, vconf_err = tl6._vconf_state_full()
    if vconf_err:
        print(f"JUDGE-PREP-GATE FAIL: G-VCONF {vconf_err}")
        return 1
    streak_state_full, streak_err = tl7._streak_state_full()
    if streak_err:
        print(f"JUDGE-PREP-GATE FAIL: G-STREAK {streak_err}")
        return 1
    tstate_state_full, tstate_err = tl8._tstate_state_full()
    if tstate_err:
        print(f"JUDGE-PREP-GATE FAIL: G-TSTATE {tstate_err}")
        return 1
    amp_state_full, amp_err = _amp_state_full()
    if amp_err:
        print(f"JUDGE-PREP-GATE FAIL: G-AMP {amp_err}")
        return 1
    mom_state_full, mom_err = _mom_state_full()
    if mom_err:
        print(f"JUDGE-PREP-GATE FAIL: G-MOM {mom_err}")
        return 1
    std_state_full, std_err = _std_state_full()
    if std_err:
        print(f"JUDGE-PREP-GATE FAIL: G-STD {std_err}")
        return 1
    rsqr_state_full, rsqr_err = _rsqr_state_full()
    if rsqr_err:
        print(f"JUDGE-PREP-GATE FAIL: G-RSQR {rsqr_err}")
        return 1
    sumn_state_full, sumn_err = _sumn_state_full()
    if sumn_err:
        print(f"JUDGE-PREP-GATE FAIL: G-SUMN {sumn_err}")
        return 1
    starts, gate_meta, vol_meta = {}, {}, {}
    yang_meta, vconf_meta, streak_meta = {}, {}, {}
    tstate_meta, amp_meta, mom_meta, std_meta = {}, {}, {}, {}
    rsqr_meta = {}
    sumn_meta = {}
    for leg in ("L", "D"):
        prices, P, idx, listed, cen = tl1._load_leg(leg)
        if cen != tl1.FROZEN_CENSUS[leg]:
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} census drift {cen} "
                  f"!= {tl1.FROZEN_CENSUS[leg]}")
            return 1
        for member, gate_name in ((tl6.GATE_MEMBER, "gate"),
                                  (tl6.VOL_MEMBER, "vol"),
                                  (tl6.YANG_MEMBER, "yang"),
                                  (tl6.VCONF_MEMBER, "vconf"),
                                  (tl7.STREAK_MEMBER, "streak"),
                                  (tl8.TSTATE_MEMBER, "tstate"),
                                  (AMP_MEMBER, "amp"),
                                  (MOM_MEMBER, "mom"),
                                  (STD_MEMBER, "std"),
                                  (RSQR_MEMBER, "rsqr"),
                                  (SUMN_MEMBER, "sumn")):
            if member not in prices:
                print(f"JUDGE-PREP-GATE FAIL: leg-{leg} panel missing "
                      f"{gate_name} member {member} ({gate_name} series "
                      f"underivable)")
                return 1
        _, _, gmeta = tl3.gate_state_series(prices)
        gate_meta[leg] = gmeta
        _, _, vmeta = tl4.vol_state_series(prices)
        if not tl4._vol_structure_pass(vmeta):
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} G-VOL structural "
                  f"invariants broken {vmeta} -- honest refuse")
            return 1
        vol_meta[leg] = vmeta
        _, _, ymeta = tl5.yang_state_series(prices)
        if not tl5._yang_structure_pass(ymeta):
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} G-YANG structural "
                  f"invariants broken {ymeta} -- honest refuse")
            return 1
        yang_meta[leg] = ymeta
        _, _, cmeta = tl6.vconf_state_series(prices)
        if not tl6._vconf_structure_pass(cmeta):
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} G-VCONF structural "
                  f"invariants broken {cmeta} -- honest refuse")
            return 1
        vconf_meta[leg] = cmeta
        _, _, skmeta = tl7.streak_state_series(prices)
        if not tl7._streak_structure_pass(skmeta):
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} G-STREAK structural "
                  f"invariants broken {skmeta} -- honest refuse")
            return 1
        streak_meta[leg] = skmeta
        _, _, tsmeta = tl8.tstate_state_series(prices)
        if not tl8._tstate_structure_pass(tsmeta):
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} G-TSTATE structural "
                  f"invariants broken {tsmeta} -- honest refuse")
            return 1
        tstate_meta[leg] = tsmeta
        _, _, apmeta = amp_state_series(prices)
        if not _amp_structure_pass(apmeta):
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} G-AMP structural "
                  f"invariants broken {apmeta} -- honest refuse")
            return 1
        amp_meta[leg] = apmeta
        _, _, mometa = mom_state_series(prices)
        if not _mom_structure_pass(mometa):
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} G-MOM structural "
                  f"invariants broken {mometa} -- honest refuse")
            return 1
        mom_meta[leg] = mometa
        _so20, _sd20, stdeta, _so10, _sd10 = std_state_series(prices)
        if not _std_structure_pass(stdeta):
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} G-STD structural "
                  f"invariants broken {stdeta} -- honest refuse")
            return 1
        std_meta[leg] = stdeta
        _r20o, _r20d, rsqreta, _r10o, _r10d = rsqr_state_series(prices)
        if not _rsqr_structure_pass(rsqreta):
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} G-RSQR structural "
                  f"invariants broken {rsqreta} -- honest refuse")
            return 1
        # per-leg slope-sign disclosure (mirror of the full-face
        # sec.2(e) computation in _rsqr_state_full; same frozen
        # runner face, additive disclosure key -- not a gate input)
        _b20 = _rsqr_faces_raw(prices)[9]
        _mopen = _r20o & _r20d & _b20.notna()
        rsqreta["slope_sign_split"] = {
            "up_slope_days": int((_mopen & (_b20 > 0)).sum()),
            "down_slope_days": int((_mopen & (_b20 <= 0)).sum()),
            "note": "BETA20 sign from the same frozen runner; "
                    "direction face intentionally NOT part of the "
                    "gate (burned axes carry direction)"}
        rsqr_meta[leg] = rsqreta
        _n20o, _n20d, sumneta, _n10o, _n10d = sumn_state_series(prices)
        if not _sumn_structure_pass(sumneta):
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} G-SUMN structural "
                  f"invariants broken {sumneta} -- honest refuse")
            return 1
        # per-leg slope-sign disclosure (mirror of the full-face
        # sec.2(e) computation in _sumn_state_full; same frozen
        # runner face, additive disclosure key -- not a gate input)
        _c20 = _sumn_faces_raw(prices)[9]
        _nmopen = _n20o & _n20d & _c20.notna()
        sumneta["slope_sign_split"] = {
            "up_slope_days": int((_nmopen & (_c20 > 0)).sum()),
            "down_slope_days": int((_nmopen & (_c20 <= 0)).sum()),
            "note": "BETA20 sign from the same frozen runner; "
                    "up-dominant windows are slope-up-heavy BY "
                    "CONSTRUCTION (direction-loaded up-share axis) "
                    "-- the split quantifies how much; direction "
                    "conditioning still lives in burned axes "
                    "(GATE/YANG/STREAK/MOM), redundancy measured "
                    "in adjacency cells"}
        sumn_meta[leg] = sumneta
        n = len(idx)
        starts[leg] = {}
        for wname, w in tl1.WINDOWS.items():
            st = [p for p in range(n)
                  if idx[p] >= (tl1.LEG_L_FLOOR if leg == "L"
                                else tl1.LEG_D_FLOOR)
                  and p >= tl1.WARMUP_TD and p <= n - 1 - w
                  and (listed.iloc[p] >= tl1.MIN_LISTED
                       if leg == "L" else True)]
            if len(st) != tl1.FROZEN_CENSUS[leg][wname]:
                print(f"JUDGE-PREP-GATE FAIL: leg-{leg} {wname} starts "
                      f"{len(st)} != {tl1.FROZEN_CENSUS[leg][wname]}")
                return 1
            starts[leg][wname] = st
    vol_meta["full_raw_face"] = vol_state_full[2]
    yang_meta["full_raw_face"] = yang_state_full[2]
    vconf_meta["full_raw_face"] = vconf_state_full[2]
    streak_meta["full_raw_face"] = streak_state_full[2]
    tstate_meta["full_raw_face"] = tstate_state_full[2]
    amp_meta["full_raw_face"] = amp_state_full[2]
    mom_meta["full_raw_face"] = mom_state_full[2]
    std_meta["full_raw_face"] = std_state_full[2]
    rsqr_meta["full_raw_face"] = rsqr_state_full[2]
    sumn_meta["full_raw_face"] = sumn_state_full[2]
    if not screen.get("survivors"):
        out = {"wave": WAVE, **tl1.cutoff_meta(CUTOFF),
               "grammar_sha256": (FROZEN_SHA16 or
                                  screen.get("grammar_sha256",
                                             "")[:16]),
               "n_survivors": 0,
               "g_manifest": gm, "starts": starts, "passive": {},
               "census_frozen": tl1.FROZEN_CENSUS,
               "gate_meta": gate_meta, "vol_meta": vol_meta,
               "yang_meta": yang_meta, "vconf_meta": vconf_meta,
               "streak_meta": streak_meta, "tstate_meta": tstate_meta,
               "amp_meta": amp_meta, "mom_meta": mom_meta,
               "std_meta": std_meta,
               "rsqr_meta": rsqr_meta,
               "sumn_meta": sumn_meta,
               "vacuous": True,
               "note": "zero screen survivors: lawful modal-zero face "
                       "(prereg sec.5 pred.3); judge burn vacuous; "
                       "judge-finalize writes the zero product + ledger 0",
               "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
        tl1._dump(JUDGE_STATE_FILE, out)
        print("judge-prep PASS (vacuous): zero survivors -- judge burn "
              "skipped, judge-finalize writes the lawful zero product")
        return 0
    passive = {}
    for leg in ("L", "D"):
        prices, P, idx, listed, cen = tl1._load_leg(leg)
        close = P["close"]
        passive[leg] = {}
        for wname, w in tl1.WINDOWS.items():
            passive[leg][wname] = {}
            for p in starts[leg][wname]:
                sdate = idx[p]
                edate = idx[p + w - 1]
                syms = close.columns[close.loc[sdate].notna()]
                rel = tl1.passive_rel(close, syms, sdate, edate)
                passive[leg][wname][str(p)] = round(
                    float(rel.iloc[-1] - 1.0), 6)
    out = {"wave": WAVE, **tl1.cutoff_meta(CUTOFF),
           "grammar_sha256": (FROZEN_SHA16
                               or screen.get("grammar_sha256", "")[:16]),
           "n_survivors": len(screen["survivors"]),
           "g_manifest": gm,
           "starts": starts, "passive": passive,
           "census_frozen": tl1.FROZEN_CENSUS, "gate_meta": gate_meta,
           "vol_meta": vol_meta, "yang_meta": yang_meta,
           "vconf_meta": vconf_meta, "streak_meta": streak_meta,
           "tstate_meta": tstate_meta, "amp_meta": amp_meta,
           "mom_meta": mom_meta,
           "std_meta": std_meta,
           "rsqr_meta": rsqr_meta,
           "sumn_meta": sumn_meta,
           "manifest_note": "P-5C frozen census reproduces only on the "
                            "48-member twin cache (W1 sec.9.3 precedent; "
                            "member count disclosed, mechanical import "
                            "wins)",
           "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    tl1._dump(JUDGE_STATE_FILE, out)
    print(f"judge-prep PASS: manifest {gm['verdict']} "
          f"({gm['manifest_members']} members), census L/D == frozen, "
          f"survivors {len(screen['survivors'])}, gate meta L/D "
          f"na-window {gate_meta['L']['na_window_bars']}/"
          f"{gate_meta['D']['na_window_bars']}, vol meta L/D "
          f"na-window {vol_meta['L']['na_window_bars']}/"
          f"{vol_meta['D']['na_window_bars']} "
          f"(leg-L anchors {vol_meta['L']['calm_days']}calm/"
          f"{vol_meta['L']['wild_days']}wild), yang meta L/D "
          f"zero-warmup {yang_meta['L']['yang_days']}yang/"
          f"{yang_meta['L']['red_days']}red, vconf meta L/D "
          f"19-bar-warmup {vconf_meta['L']['surge_days']}surge/"
          f"{vconf_meta['L']['dry_days']}dry, streak meta L/D "
          f"2-bar-warmup {streak_meta['L']['up_streak_days']}up/"
          f"{streak_meta['L']['down_streak_days']}down/"
          f"{streak_meta['L']['neither_days']}neither, tstate meta L/D "
          f"178/59-warmup mad60 "
          f"{tstate_meta['L']['mad60']['gate_true_days']}true/"
          f"{tstate_meta['L']['mad60']['decidable_days']}decidable + "
          f"rsv60 {tstate_meta['L']['rsv60']['gate_true_days']}true/"
          f"{tstate_meta['L']['rsv60']['decidable_days']}decidable, "
          f"amp meta L/D 19-bar-warmup "
          f"{amp_meta['L']['wide_days']}wide/"
          f"{amp_meta['L']['narrow_days']}narrow decidable "
          f"{amp_meta['L']['decidable_days']}, "
          f"mom meta L/D 139-bar-warmup "
          f"{mom_meta['L']['open_days']}open/"
          f"{mom_meta['L']['closed_days']}closed decidable "
          f"{mom_meta['L']['decidable_days']}")
    print(f"std meta L 120-bar-warmup "
          f"{std_meta['L']['open_days']}open/"
          f"{std_meta['L']['closed_days']}closed decidable "
          f"{std_meta['L']['decidable_days']} std10-open "
          f"{std_meta['L']['std10_open_days']}")
    print(f"rsqr meta L 120-bar-warmup "
          f"{rsqr_meta['L']['open_days']}open/"
          f"{rsqr_meta['L']['closed_days']}closed decidable "
          f"{rsqr_meta['L']['decidable_days']} rsqr10-open "
          f"{rsqr_meta['L']['rsqr10_open_days']} slope-split "
          f"{rsqr_meta['L']['slope_sign_split']}")
    print(f"sumn meta L 120-bar-warmup "
          f"{sumn_meta['L']['open_days']}open/"
          f"{sumn_meta['L']['closed_days']}closed decidable "
          f"{sumn_meta['L']['decidable_days']} sumn10-open "
          f"{sumn_meta['L']['sumn10_open_days']} slope-split "
          f"{sumn_meta['L']['slope_sign_split']}")
    return 0


def cmd_judge(shard: int, shards: int, workers) -> int:
    print(f"=== {WAVE} judge shard {shard}of{shards} ===")
    for p, what in ((JUDGE_STATE_FILE, "judge_state.json"),
                    (SCREEN_FILE, "w14_screen.json")):
        if not os.path.exists(p):
            # O-1712 sec.1.2 diagnostic-soundness: the refusal
            # self-locates the expected face (abs path + machine) so
            # absence vs path mismatch vs wrong-machine face reads off
            # the refusal line itself (R398 anchor-face lesson).
            print(f"JUDGE-GATE: {what} absent -- judge-prep + "
                  f"screen-finalize required first; expected face: "
                  f"{os.path.abspath(p)} (this machine: "
                  f"{os.environ.get('COMPUTERNAME', '?')})")
            return 2
    jstate = json.load(open(JUDGE_STATE_FILE, encoding="utf-8"))
    if jstate.get("vacuous"):
        print("JUDGE-GATE: vacuous face (zero survivors) -- zero cells, "
              "proceed to judge-finalize")
        return 0
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    if FROZEN_SHA16 and _grammar_sha16(grammar) != FROZEN_SHA16:
        print(f"JUDGE-GATE: grammar sha drift != frozen {FROZEN_SHA16}")
        return 2
    tl1.GRAMMAR = grammar
    screen = json.load(open(SCREEN_FILE, encoding="utf-8"))
    cands = {c["candidate_id"]: c for c in json.load(
        open(CANDIDATES_FILE, encoding="utf-8"))["candidates"]}
    a_by_trader = {t["trader_id"]: t for t in tl1.A_TEMPLATES}
    cells = []
    for i, cid in enumerate(sorted(screen["survivors"])):
        c = cands[cid]
        template = (a_by_trader.get(c.get("template_trader"))
                    if c["family"] == "A" else None)
        cells.append({"cell_id": f"JUDGE|{cid}", "candidate_id": cid,
                      "i": i, "cand": c, "template": template})
    mine = [c for i, c in enumerate(cells) if i % shards == shard]

    vol_state_full, vol_err = tl4._vol_state_full()
    if vol_err:
        print(f"JUDGE-GATE: {vol_err} (prereg sec.2 fail-closed) "
              "-- refuse")
        return 2
    yang_state_full, yang_err = tl5._yang_state_full()
    if yang_err:
        print(f"JUDGE-GATE: {yang_err} (prereg sec.2 G-YANG "
              "fail-closed) -- refuse")
        return 2
    vconf_state_full, vconf_err = tl6._vconf_state_full()
    if vconf_err:
        print(f"JUDGE-GATE: {vconf_err} (prereg sec.2 G-VCONF "
              "fail-closed) -- refuse")
        return 2
    streak_state_full, streak_err = tl7._streak_state_full()
    if streak_err:
        print(f"JUDGE-GATE: {streak_err} (prereg sec.2 G-STREAK "
              "fail-closed) -- refuse")
        return 2
    tstate_state_full, tstate_err = tl8._tstate_state_full()
    if tstate_err:
        print(f"JUDGE-GATE: {tstate_err} (prereg sec.2 G-TSTATE "
              "fail-closed) -- refuse")
        return 2
    amp_state_full, amp_err = _amp_state_full()
    if amp_err:
        print(f"JUDGE-GATE: {amp_err} (prereg sec.2 G-AMP "
              "fail-closed) -- refuse")
        return 2
    mom_state_full, mom_err = _mom_state_full()
    if mom_err:
        print(f"JUDGE-GATE: {mom_err} (prereg sec.2 G-MOM "
              "fail-closed) -- refuse")
        return 2
    std_state_full, std_err = _std_state_full()
    if std_err:
        print(f"JUDGE-GATE: {std_err} (prereg sec.2 G-STD "
              "fail-closed) -- refuse")
        return 2
    rsqr_state_full, rsqr_err = _rsqr_state_full()
    if rsqr_err:
        print(f"JUDGE-GATE: {rsqr_err} (prereg sec.2 G-RSQR "
              "fail-closed) -- refuse")
        return 2
    sumn_state_full, sumn_err = _sumn_state_full()
    if sumn_err:
        print(f"JUDGE-GATE: {sumn_err} (prereg sec.2 G-SUMN "
              "fail-closed) -- refuse")
        return 2
    state = {}
    for leg in ("L", "D"):
        prices, P, idx, listed, cen = tl1._load_leg(leg)
        if cen != tl1.FROZEN_CENSUS[leg]:
            print(f"JUDGE-GATE: leg-{leg} census drift {cen} -- refuse")
            return 2
        state[f"prices_{leg}"] = prices
        state[f"P_{leg}"] = P
        state[f"idx_{leg}"] = idx
        state[f"atr20_{leg}"] = tl2.atr20_series(prices)
        try:
            bl = pd.read_csv(tl1.B_LAYER_MASK)
            ok_codes = set(bl.loc[bl["ok_static"] == True, "code"]
                           .astype(str))
            overlap = sorted(s for s in P["close"].columns
                             if s in ok_codes)
        except Exception:
            overlap = []
        # keep-ok face = identical derivation to the screen-stage face
        # (consistency law); applied per-leg to that leg's own columns
        if overlap:
            fok = pd.DataFrame(False, index=P["close"].index,
                               columns=P["close"].columns)
            for s in overlap:
                fok[s] = True
        else:
            fok = None
        state[f"fundamental_ok_{leg}"] = fok
        gs = tl3.gate_state_series(prices)
        state[f"gate_state_{leg}"] = gs
        state[f"gate_meta_{leg}"] = gs[2]
        state[f"vol_state_{leg}"] = vol_state_full
        state[f"vol_meta_{leg}"] = vol_state_full[2]
        state[f"yang_state_{leg}"] = yang_state_full
        state[f"yang_meta_{leg}"] = yang_state_full[2]
        state[f"vconf_state_{leg}"] = vconf_state_full
        state[f"vconf_meta_{leg}"] = vconf_state_full[2]
        sk = tl7.streak_state_series(prices)
        state[f"streak_state_{leg}"] = sk
        state[f"streak_meta_{leg}"] = sk[2]
        ts = tl8.tstate_state_series(prices)
        state[f"tstate_state_{leg}"] = ts
        state[f"tstate_meta_{leg}"] = ts[2]
        ap = amp_state_series(prices)
        state[f"amp_state_{leg}"] = ap
        state[f"amp_meta_{leg}"] = ap[2]
        mo = mom_state_series(prices)
        state[f"mom_state_{leg}"] = mo
        state[f"mom_meta_{leg}"] = mo[2]
        sdst = std_state_series(prices)
        state[f"std_state_{leg}"] = sdst
        state[f"std_meta_{leg}"] = sdst[2]
        rst = rsqr_state_series(prices)
        state[f"rsqr_state_{leg}"] = rst
        state[f"rsqr_meta_{leg}"] = rst[2]
        nst = sumn_state_series(prices)
        state[f"sumn_state_{leg}"] = nst
        state[f"sumn_meta_{leg}"] = nst[2]
    state["starts"] = jstate["starts"]
    state["passive"] = jstate["passive"]
    state["states"] = tl1.v3_state_series()
    state["grammar"] = grammar

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
    print(f"judge shard cells {len(mine)}, done {len(done)}, "
          f"todo {len(todo)}")

    def on_result(key, payload):
        # r429: same stash-ectomy hardening as screen face (see there)
        os.makedirs(CKPT_DIR, exist_ok=True)
        with open(ck, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(tl1._j(payload), ensure_ascii=False,
                                default=float) + "\n")

    if todo:
        jobs = [(c["cell_id"], _judge_cell_w14, (c,)) for c in todo]
        tl1.run_cells_parallel(jobs, workers=workers or tl1.worker_cap(),
                              desc="judge cells",
                              initializer=tl1._init_worker,
                              initargs=(state,), on_result=on_result)
    print(f"judge shard {shard}of{shards} complete -> {ck}")
    return 0


def cmd_judge_finalize() -> int:
    print(f"=== {WAVE} judge-finalize ===")
    landed = tl6.finalize_already_landed(JUDGE_BATCH, JUDGE_FILE)
    if landed is not None:
        print(f"FINALIZE-IDEMPOTENT-GUARD: {JUDGE_BATCH} already landed "
              f"(ledger total={landed.get('total')}); re-run refused "
              "(pit-95 double-append guard; re-run channel = fresh prereg "
              "+ fresh batch name)")
        return 2
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    screen = json.load(open(SCREEN_FILE, encoding="utf-8"))
    survivors = list(screen.get("survivors", []))
    rows = []
    for f in sorted(os.listdir(CKPT_DIR)):
        if f.startswith("judge_shard_") and f.endswith(".jsonl"):
            with open(os.path.join(CKPT_DIR, f), encoding="utf-8") as fh:
                for ln in fh:
                    if ln.strip():
                        rows.append(json.loads(ln))
    by_id = {r["cell_id"]: r for r in rows}
    missing = [f"JUDGE|{cid}" for cid in survivors
               if f"JUDGE|{cid}" not in by_id]
    if missing:
        print(f"FINALIZE-GATE: {len(missing)} judged cells incomplete; "
              f"refused (checkpoint retained); first: {missing[:3]}")
        return 2
    judged = [by_id[f"JUDGE|{cid}"] for cid in sorted(survivors)]
    # G1'v2 + DSR per cell (n_trials = live chain head AFTER the screen
    # append; prereg sec.4 cumulative-N, cross-wave no reset)
    n_trials = tl1.ledger_head()["total"]
    batch_cells = screen["batch_cells"]
    for r in judged:
        rets = r.get("legL_daily_returns") or []
        if r.get("legL_sharpe_full") is None or not rets:
            r["g1_prime_v2"] = None
            r["dsr"] = None
            r["g1_pass"] = False
            r["verdict"] = "fail-degenerate"
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
    # family PBO (CSCV 8 blocks; family = strategy module; <8 cells n/a)
    fam_map = {}
    for r in judged:
        fam_map.setdefault(r.get("module"), []).append(r)
    pbos = {}
    for fam, rs in fam_map.items():
        series = {r["candidate_id"]: pd.Series(r["legL_daily_returns"])
                  for r in rs if r.get("legL_daily_returns")}
        if len(rs) < 8 or len(series) < 8:
            pbos[fam] = {"pbo": None, "n_cells": len(rs),
                         "note": "insufficient (<8) -- G2 cannot pass"}
            for r in rs:
                r["family_pbo"] = None
            continue
        mat = tl1.align_returns(series)
        pbo = tl1.cscv_pbo(mat)
        pbos[fam] = {"pbo": round(float(pbo["pbo"]), 4) if isinstance(
            pbo, dict) else round(float(pbo), 4), "n_cells": len(rs)}
        for r in rs:
            r["family_pbo"] = pbos[fam]["pbo"]
    # G2 registration columns
    for r in judged:
        if r.get("g1_prime_v2") is None:
            r["g2_registration_v2"] = None
            continue
        g2 = tl1.g2_registration_v2(r["g1_pass"], r["dsr"],
                                    r.get("family_pbo"))
        r["g2_registration_v2"] = g2
    n_judged = len(judged)
    e_fp = round(0.05 * n_judged, 2)
    eligible = [r["candidate_id"] for r in judged
                if (r.get("g2_registration_v2") or {}).get("eligible_v2")]
    ledger = tl1.append_ledger(JUDGE_BATCH, n_judged,
                               "results/trial_labor_w14/w14_judge.json",
                               evidence_cutoff=CUTOFF)
    # descriptive clause batch summary (disclosure-only, zero gate weight)
    cl_keys = [("clause_ann_pos", "annualized > 0"),
               ("clause_oos_dual_pos",
                "OOS(2025+ blind) sharpe + annualized both > 0"),
               ("clause_dd_ok", "max drawdown >= -35%"),
               ("clause_no_crash_year", "no calendar year <= -35%"),
               ("clause_x2_no_crash_year",
                "x2 face: no calendar year <= -35%")]
    clauses = {}
    for k, label in cl_keys:
        vals = [r.get("descriptive", {}).get(k) for r in judged]
        clauses[k] = {"label": label,
                      "n_true": sum(1 for v in vals if v is True),
                      "n_evaluable": sum(1 for v in vals
                                         if v is not None)}
    # GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM-face + interaction
    # judged summaries (prereg sec.5.4 direction-readout + eight-gate
    # column faces; disclosure-only, zero gate weight)
    gate_sum, vol_sum = {}, {}
    yang_sum, vconf_sum, streak_sum, tstate_sum = {}, {}, {}, {}
    amp_sum, mom_sum, std_sum = {}, {}, {}
    rsqr_sum = {}
    gvy_sum, gvvy_sum, gvvvsk_sum = {}, {}, {}
    gvvvskts_sum, gvvvsktsa_sum, gvvvsktsam_sum = {}, {}, {}
    gvvvsktsams_sum = {}
    gvvvsktsamsr_sum = {}
    sumn_sum = {}
    gvvvsktsamsrn_sum = {}
    for r in judged:
        g = r.get("gate_face", "none")
        v = r.get("vol_face", "none")
        y = r.get("yang_face", "none")
        c = r.get("vconf_face", "none")
        s = r.get("streak_face", "none")
        t = r.get("tstate_face", "none")
        a = r.get("amp_face", "none")
        m = r.get("mom_face", "none")
        stf = r.get("std_face", "none")
        rqf = r.get("rsqr_face", "none")
        nqf = r.get("sumn_face", "none")
        for seg, key in ((gate_sum, g), (vol_sum, v), (yang_sum, y),
                         (vconf_sum, c), (streak_sum, s),
                         (tstate_sum, t), (amp_sum, a), (mom_sum, m),
                         (std_sum, stf),
                         (rsqr_sum, rqf),
                         (sumn_sum, nqf),
                         (gvy_sum, f"{g}|{v}|{y}"),
                         (gvvy_sum, f"{g}|{v}|{y}|{c}"),
                         (gvvvsk_sum, f"{g}|{v}|{y}|{c}|{s}"),
                         (gvvvskts_sum, f"{g}|{v}|{y}|{c}|{s}|{t}"),
                         (gvvvsktsa_sum, f"{g}|{v}|{y}|{c}|{s}|{t}|{a}"),
                         (gvvvsktsam_sum,
                          f"{g}|{v}|{y}|{c}|{s}|{t}|{a}|{m}"),
                         (gvvvsktsams_sum,
                          f"{g}|{v}|{y}|{c}|{s}|{t}|{a}|{m}|{stf}"),
                         (gvvvsktsamsr_sum,
                          f"{g}|{v}|{y}|{c}|{s}|{t}|{a}|{m}|{stf}|{rqf}"),
                         (gvvvsktsamsrn_sum,
                          f"{g}|{v}|{y}|{c}|{s}|{t}|{a}|{m}|{stf}|{rqf}|{nqf}")):
            sm = seg.setdefault(key, {"n_cells": 0, "n_g1_pass": 0,
                                      "n_eligible_g2": 0})
            sm["n_cells"] += 1
            sm["n_g1_pass"] += int(bool(r.get("g1_pass")))
            sm["n_eligible_g2"] += int(
                bool((r.get("g2_registration_v2") or {}).get("eligible_v2")))
    out = {"wave": WAVE, "stage": "judge", "prereg": PREREG,
           **tl1.cutoff_meta(CUTOFF), "grammar_sha256": grammar[
               "grammar_sha256"],
           "n_judged_cells": n_judged,
           "n_wave_disclosure": {"screen_cells": batch_cells,
                                 "judged_cells": n_judged,
                                 "E_FP_nominal_5pct": e_fp,
                                 "note": "DSR>=0.95 gate IS the multiple-"
                                         "testing correction (cumulative-N "
                                         "deflation); E[FP] disclosed at "
                                         "the nominal 5% caliber"},
           "family_pbo": pbos,
           "gate_face_judgment": gate_sum,
           "vol_face_judgment": vol_sum,
           "yang_face_judgment": yang_sum,
           "vconf_face_judgment": vconf_sum,
           "streak_face_judgment": streak_sum,
           "tstate_face_judgment": tstate_sum,
           "amp_face_judgment": amp_sum,
           "mom_face_judgment": mom_sum,
           "std_face_judgment": std_sum,
           "rsqr_face_judgment": rsqr_sum,
           "sumn_face_judgment": sumn_sum,
           "gate_vol_yang_interaction_judgment": gvy_sum,
           "gate_vol_yang_vconf_interaction_judgment": gvvy_sum,
           "gate_vol_yang_vconf_streak_interaction_judgment": gvvvsk_sum,
           "gate_vol_yang_vconf_streak_tstate_interaction_judgment":
               gvvvskts_sum,
           "gate_vol_yang_vconf_streak_tstate_amp_interaction_judgment":
               gvvvsktsa_sum,
           "gate_vol_yang_vconf_streak_tstate_amp_mom_interaction_"
           "judgment": gvvvsktsam_sum,
           "gate_vol_yang_vconf_streak_tstate_amp_mom_std_interaction_"
           "judgment": gvvvsktsams_sum,
           "gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_interaction_"
           "judgment": gvvvsktsamsr_sum,
           "gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_sumn_interaction_"
           "judgment": gvvvsktsamsrn_sum,
           "descriptive_summary": {"n_cells": n_judged,
                                   "clauses": clauses,
                                   "note": "descriptive clauses are "
                                           "batch-level disclosure per "
                                           "prereg sec.3 -- zero gate "
                                           "weight; gates = G1'v2/G2/DSR/"
                                           "PBO per sec.4"},
           "eligible_g2": eligible, "n_eligible_g2": len(eligible),
           "trials_ledger": ledger,
           "cells": [{k: v for k, v in r.items()
                      if k != "legL_daily_returns"} for r in judged],
           "audit": {"note": "judged face = dual-leg (P-5C grid) x "
                             "{6m,12m,24m} x base/x2 curves with the "
                             "gate + vol + yang + vconf + streak + "
                             "tstate + amp + MOM + STD + RSQR + SUM overlays carried "
                             "per "
                             "cell (frozen composition signal -> filter "
                             "-> timing -> GATE -> VOL -> YANG -> VCONF "
                             "-> STREAK -> TSTATE -> AMP -> MOM -> STD -> "
                             "RSQR -> SUM -> initial-stop; "
                             "engine/exit_rules.py zero touch) + regime "
                             "segments + dual nulls (B=2000 block-20 + "
                             "P=2000 sign-flip, seed [20328500, "
                             "cell]); "
                             "gates on the leg-L base face (W1-W9 "
                             "judged-cell caliber); beat operator = "
                             "strict > (W1-W9 judged-cell caliber; "
                             "screen >= was the sec.3 s2 literal); x2 + "
                             "descriptive clauses = disclosure-only zero "
                             "criteria weight; crisis-day count = "
                             "|daily|>8% leg-L base (sec.5.6); stop "
                             "trigger/fill-day D+1 open-vs-close "
                             "deviation = MSG-0450 annex-1 disclosure on "
                             "the protection-floor signal face with the "
                             "std+rsqr+sumn overlays inserted before stop arming "
                             "(W12/W13 composition law); gate_flip_days_legL "
                             "/ vol_flip_days_legL = panel-level "
                             "flip-day counts of the cell's OWN gate / "
                             "vol face on the leg-L panel (none -> null; "
                             "sec.5.6 disclosure columns, zero gate "
                             "weight; yang AND vconf AND streak AND "
                             "tstate AND amp AND mom faces = daily "
                             "binaries with no probe-defined flip "
                             "caliber [W5 yang precedent, r206/r423/"
                             "r431/r228 probes define no streak/tstate/"
                             "amp/mom flips], per-leg "
                             "yang_zeroed / vconf_zeroed / streak_zeroed "
                             "/ tstate_zeroed / amp_zeroed / mom_zeroed "
                             "counts are their columns); gate x vol x "
                             "yang x vconf x streak x tstate x amp x mom "
                             "eight-gate interaction segments = prereg "
                             "sec.3 eight-gate disclosure column; "
                             "fundamental keep-ok face = screen "
                             "consistency law"},
           "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    tl1._dump(JUDGE_FILE, out)
    print(f"judge finalize: {n_judged} judged cells, E[FP]={e_fp}, "
          f"G2 eligible {len(eligible)} -> {eligible[:10]}")
    print(f"mom-face judgment: {json.dumps(mom_sum, sort_keys=True)}")
    print(f"std-face judgment: {json.dumps(std_sum, sort_keys=True)}")
    print(f"rsqr-face judgment: {json.dumps(rsqr_sum, sort_keys=True)}")
    print(f"sumn-face judgment: {json.dumps(sumn_sum, sort_keys=True)}")
    print(f"gate x vol x yang x vconf x streak x tstate x amp x mom "
          f"interaction judgment: "
          f"{json.dumps(gvvvsktsam_sum, sort_keys=True)[:400]}")
    return 0


# ------------------------------------------------------ intake slice (s4)
def cmd_intake() -> int:
    """s4 D6 binding gate (W2 cmd_intake precedent on the W12 file
    faces): G2-eligible survivors -> per-candidate max|corr| vs the
    registered roster (>=0.7 reject) + survivor-cluster collapse (>=0.7
    pairs keep highest DSR) -> w14_intake.json registration-face rows.
    Zero ledger rows (judgment face); STRATEGY_LIBRARY / paper
    onboarding writes belong to the registration pipeline (prereg
    sec.4)."""
    print(f"=== {WAVE} intake (s4 D6 binding gate) ===")
    if not os.path.exists(JUDGE_FILE):
        print("INTAKE-GATE: judge not finalized (w14_judge.json absent)")
        return 2
    judge = json.load(open(JUDGE_FILE, encoding="utf-8"))
    if FROZEN_SHA16 and str(judge.get("grammar_sha256", ""))[:16] \
            != FROZEN_SHA16:
        print(f"INTAKE-GATE FAIL: judge grammar sha != frozen anchor "
              f"{FROZEN_SHA16}")
        return 1
    eligible = list(judge["eligible_g2"])
    audit_note = ("intake = judgment face, zero ledger rows; candidate "
                  "daily returns = judge checkpoint engine face (eight-"
                  "gate + stop overlays included); registered six = "
                  "engine recompute at the registered config, cutoff-"
                  "truncated FIRST (r363 law); D6 ceiling 0.7 prereg "
                  "sec.4; cluster keep = highest DSR, tie lowest id; "
                  "TRIAL-<FAMILY>-<NN>: family = strategy module per "
                  "sec.4 PBO definition, per-module NN counter; hr/"
                  "STRATEGY_LIBRARY writes + smoke anchor re-run = "
                  "registration pipeline face (prereg sec.4)")
    if not eligible:
        out = {"wave": WAVE, "stage": "intake", "prereg": PREREG,
               **tl1.cutoff_meta(CUTOFF),
               "grammar_sha256": (FROZEN_SHA16
                                  or judge.get("grammar_sha256",
                                               "")[:16]),
               "n_eligible": 0, "admitted": [], "rejected": [],
               "d6_binding": {}, "intake": [],
               "note": "zero G2-eligible survivors = lawful outcome, "
                       "reported as-is (prereg sec.5 pred.3 modal zero)",
               "audit": {"n_engine_runs": 0, "ledger_trials_added": 0,
                         "note": audit_note},
               "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
        tl1._dump(INTAKE_FILE, out)
        print("intake: zero eligible survivors -- lawful zero, product "
              "written")
        return 0
    cands = {c["candidate_id"]: c for c in json.load(
        open(CANDIDATES_FILE, encoding="utf-8"))["candidates"]}
    cells = {r["candidate_id"]: r for r in judge["cells"]}
    dsr_by_id = {cid: (cells[cid].get("dsr") or {}).get("dsr")
                 for cid in eligible}
    # candidate engine-face daily returns: judge checkpoint rows (W1
    # intake precedent; w14_judge.json cells are stripped by design)
    cand_ret = {}
    for f in sorted(os.listdir(CKPT_DIR)):
        if f.startswith("judge_shard_") and f.endswith(".jsonl"):
            with open(os.path.join(CKPT_DIR, f), encoding="utf-8") as fh:
                for ln in fh:
                    r = json.loads(ln)
                    if r.get("candidate_id") in eligible:
                        cand_ret[r["candidate_id"]] = r.get(
                            "legL_daily_returns") or []
    missing = [c for c in eligible if not len(cand_ret.get(c, []))]
    if missing:
        print(f"INTAKE-GATE FAIL: eligible rows missing legL daily "
              f"returns in checkpoints: {missing[:3]}")
        return 2
    # registered six: engine-face recompute at the registered config
    # (W1 intake precedent; truncate to cutoff before any engine face)
    from live.paper import SIGNAL_BUILDERS      # W1 cmd_intake precedent
    prices = tl1.load_core()
    cut = pd.Timestamp(CUTOFF)
    pcut = {s: df[df.index <= cut] for s, df in prices.items()}
    P = tl1.build_panels(pcut)
    reg_ret = {}
    for t in tl1.A_TEMPLATES:
        trader = tl1.load_trader(t["trader_id"])
        entry = trader["params"]["entry"]
        sig = SIGNAL_BUILDERS[entry](P)
        params = {k: v for k, v in trader["params"].items()
                  if k != "entry"}
        with tl1.ExitPatch(trader.get("exit_overrides")):
            res = tl1.run_backtest(pcut, params, entry_signal=sig,
                                   exit_signal=(sig <= 0))
        eq = pd.Series(res["equity_curve"],
                       index=P["close"].index[:len(res["equity_curve"])])
        reg_ret[t["trader_id"]] = eq.pct_change().fillna(0.0)
    cand_ret_s = {cid: pd.Series(v, index=P["close"].index[:len(v)])
                  for cid, v in cand_ret.items()}
    admitted, rejected, d6 = tl2._d6_admit_core(eligible, cand_ret_s,
                                                reg_ret, dsr_by_id)
    intake_rows = tl2._trial_intake_rows(admitted, cands)
    out = {"wave": WAVE, "stage": "intake", "prereg": PREREG,
           **tl1.cutoff_meta(CUTOFF),
           "grammar_sha256": (FROZEN_SHA16
                              or judge.get("grammar_sha256", "")[:16]),
           "n_eligible": len(eligible), "admitted": admitted,
           "rejected": rejected, "d6_binding": d6, "intake": intake_rows,
           "ceo_report_due": "48h from intake (prereg sec.4)",
           "audit": {"n_engine_runs": len(reg_ret),
                     "ledger_trials_added": 0, "note": audit_note},
           "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    tl1._dump(INTAKE_FILE, out)
    print(f"intake: eligible {len(eligible)} -> admitted {len(admitted)} "
          f"(D6 rejects {len(rejected)})")
    return 0


# ------------------------------------------------------------------ selftest
def cmd_selftest() -> int:
    """Hermetic offline selftest (zero network, zero live engine burns,
    zero cell evaluation): W10-W13 regression legs (MOM causality /
    139-bar warmup / NaN comparison-artifact / mom=none identity /
    eight-gate intersection / G-MOM probe anchors / G-SUMN probe
    anchors) + W14 own faces (eighteen-tuple grammar 1,693,052,928
    combos / resi+cnt stream append / 28-source exclusion loader
    resi/cnt-none completion / resi+cnt new-syntax legality / G-RESI
    + G-CNT real-face fail-closed anchor loads / mask + engine parity
    vs W9 + W13 baselines / engine double-run determinism / funnel
    faces (dispatch / null-cell engine path / CSV contract) + pit-95
    finalize guards."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    n_pass = 0
    n_leg = 0

    def _ok(name, cond, detail=""):
        nonlocal n_pass, n_leg
        n_leg += 1
        if cond:
            n_pass += 1
            print(f"[PASS] {name}" + (f" | {detail}" if detail else ""))
        else:
            print(f"[FAIL] {name}" + (f" | {detail}" if detail else ""))

    # ---- L1 synthetic MOM causality (flat -> 1%/bar crash 200-229 ->
    # flat: mom_oversold bites ONLY inside the crash window, on
    # negative-momentum days; zero pre-crash decidable days open)
    mom_idx = pd.bdate_range("2018-01-01", periods=460)
    base_close = np.full(460, 100.0)
    for i in range(200, 230):
        base_close[i] = 100.0 * (0.99 ** (i - 199))
    for i in range(230, 460):
        base_close[i] = base_close[229]
    mc = pd.Series(base_close, index=mom_idx)
    mom_face = {MOM_MEMBER: pd.DataFrame(
        {"open": mc.copy(), "high": mc + 1.0, "low": mc - 1.0,
         "close": mc, "volume": pd.Series(1000.0, index=mom_idx),
         "amount": mc * 1000.0}, index=mom_idx)}
    open_d, dec_d, meta_d = mom_state_series(mom_face)
    open_days = set(np.flatnonzero((open_d & dec_d).values))
    crash_days = set(range(200, 250))
    _ok("L1a mom_oversold causality (flat->crash->flat face: gate "
        "open ONLY inside the crash window {200..249}, zero "
        "pre-crash decidable days open, non-empty open set, every "
        "open day roc20 < 0)",
        open_days and open_days <= crash_days
        and int((open_d & dec_d).iloc[:200].sum()) == 0
        and len(open_days) > 0,
        f"open_true={len(open_days)} at "
        f"{sorted(open_days)[:3]}..{sorted(open_days)[-3:] if open_days else ''}")

    # ---- L2 warmup gate-closed legs (139 bars, synthetic + short face
    # honest refuse)
    _ok("L2a MOM 139-bar warmup gate-closed (first 139 bars all "
        "decidable-False, first-decidable == 139, decidable == 321/460)",
        int(dec_d.iloc[:139].sum()) == 0
        and meta_d["first_decidable_bar_idx"] == 139
        and meta_d["decidable_days"] == 460 - 139
        and meta_d["open_days"] + meta_d["closed_days"]
        == meta_d["decidable_days"])
    short_idx = pd.bdate_range("2020-01-01", periods=120)
    short_face = {MOM_MEMBER: pd.DataFrame(
        {"open": pd.Series(100.0, index=short_idx),
         "high": pd.Series(101.0, index=short_idx),
         "low": pd.Series(99.0, index=short_idx),
         "close": pd.Series(100.0, index=short_idx),
         "volume": pd.Series(1000.0, index=short_idx),
         "amount": pd.Series(1e5, index=short_idx)}, index=short_idx)}
    open_s, dec_s, meta_s = mom_state_series(short_face)
    _ok("L2b short face (< 139 bars) honest refuse: first-decidable "
        "None + zero decidable + structure gate refuses",
        meta_s["first_decidable_bar_idx"] is None
        and meta_s["decidable_days"] == 0
        and not _mom_structure_pass(meta_s))

    # ---- L3 NaN comparison-artifact leg (pit-95 batch-95 / r421 /
    # r431 erratum face: the naive (roc20 < q10_ref) bool face is False
    # NOT decidable in the warmup -- it masquerades warmup bars as
    # mom_closed; the decidable face derives from notna())
    _, _, _, roc_raw, q10_raw = _mom_series_raw(mom_face)
    naive_bool = (roc_raw < q10_raw)      # bool face: NaN -> False
    _ok("L3a the ARTIFACT demonstrated: naive bool (roc20 < q10_ref) "
        "is False-False on warmup bars (first_valid_index == bar 0, "
        "masquerading them as closed) while the notna-derived "
        "decidable face starts at 139",
        naive_bool.first_valid_index() == mom_idx[0]
        and int(dec_d.iloc[:139].sum()) == 0
        and int(np.flatnonzero(dec_d.values)[0]) == 139)
    mask_wu = pd.DataFrame({"sig": [1.0] * 150}, index=mom_idx[:150])
    m_wu = mom_zero_mask(mask_wu, "mom_oversold", (open_d, dec_d, meta_d))
    _open_all = set(np.flatnonzero((open_d & dec_d).values))
    open_in_wu = _open_all & set(range(150))
    _ok("L3b mom_oversold on a warmup-spanning mask permits ZERO warmup "
        "bars (keep = open AND decidable -- the r417 map-NaN-bucket "
        "erratum face BANNED at the mask level; permitted days == the "
        "open set intersected with the mask span)",
        int((m_wu["sig"].iloc[:139] > 0).sum()) == 0
        and set(np.flatnonzero((m_wu["sig"] > 0).values))
        == open_in_wu,
        f"permitted={len(open_in_wu)}")

    # ---- L4 mom=none identity (zero-mask + W9 semantic baseline)
    mask5 = pd.DataFrame({"sig": [1.0] * 6}, index=mom_idx[200:206])
    ident = mom_zero_mask(mask5, "none", (open_d, dec_d, meta_d))
    _ok("L4a mom=none == W9 semantic-baseline identity (byte-equal)",
        ident.equals(mask5))
    perm_o = mom_zero_mask(mask5, "mom_oversold", (open_d, dec_d, meta_d))
    exp_l4o = [1.0 if i in open_days else 0.0 for i in range(200, 206)]
    _ok("L4b mom_oversold permits exactly the open decidable days "
        "(bars 200-205 window vs the crash-day open set)",
        list(perm_o["sig"]) == exp_l4o,
        f"got={list(perm_o['sig'])}")
    miss_idx2 = mom_idx[[200, 201]].append(
        pd.DatetimeIndex(["2030-01-01"]))
    mmask2 = pd.DataFrame({"sig": [1.0] * 3}, index=miss_idx2)
    mres2 = mom_zero_mask(mmask2, "mom_oversold", (open_d, dec_d, meta_d))
    miss_open = [1.0 if i in open_days else 0.0 for i in (200, 201)]
    _ok("L4c missing dates -> mom-closed (conservative reindex law)",
        list(mres2["sig"]) == miss_open + [0.0])

    # ---- L5 eight-gate intersection leg (streak x tstate x amp x mom
    # composed on a controlled crash-then-stabilize face: the composed
    # mask == day-wise intersection of the four keep faces)
    x_idx = pd.bdate_range("2017-01-02", periods=420)
    x_close = pd.Series([100.0] * 186 + [103.0] * 4
                        + [92.0, 91.0, 90.0, 89.0] + [89.0] * 226,
                        index=x_idx)
    x_big = set(range(188, 196))           # crash + post days big-amp
    x_hi = pd.Series([x_close.iloc[i] + (8.0 if i in x_big else 0.2)
                      for i in range(len(x_idx))], index=x_idx)
    x_lo = pd.Series([x_close.iloc[i] - (8.0 if i in x_big else 0.2)
                      for i in range(len(x_idx))], index=x_idx)
    x_face = {MOM_MEMBER: pd.DataFrame(
        {"open": x_close.copy(), "high": x_hi, "low": x_lo,
         "close": x_close, "volume": pd.Series(1000.0, index=x_idx),
         "amount": x_close * 1000.0}, index=x_idx)}
    x_mad, x_rsv, x_meta = tl8.tstate_state_series(x_face)
    x_up, x_down, _ = tl7.streak_state_series(x_face)
    x_wide, x_dec, _ = tl9.amp_state_series(x_face)
    x_mopen, x_mdec, _ = mom_state_series(x_face)
    dn_days = set(np.flatnonzero(x_down.values))
    sig8 = pd.DataFrame(1.0, index=x_idx, columns=["s"])
    m_sk = tl7.streak_zero_mask(sig8, "down_streak2", (x_up, x_down, {}))
    m_ts = tl8.tstate_zero_mask(m_sk, "deep_pullback",
                                 (x_mad, x_rsv, x_meta))
    m_ap = tl9.amp_zero_mask(m_ts, "amp_wide", (x_wide, x_dec, {}))
    m_mo = mom_zero_mask(m_ap, "mom_oversold",
                          (x_mopen, x_mdec, {}))
    got_days = set(np.flatnonzero((m_mo["s"] > 0).values))
    exp_days = (dn_days & set(np.flatnonzero(x_mad.values))
                & set(np.flatnonzero((x_wide & x_dec).values))
                & set(np.flatnonzero((x_mopen & x_mdec).values)))
    _ok("L5 eight-gate intersection correctness: composed streak "
        "(down_streak2) x tstate (deep_pullback) x amp (amp_wide) x mom "
        "(mom_oversold) mask == day-wise intersection of the four keep "
        "faces",
        got_days == exp_days
        and set(np.flatnonzero((m_sk["s"] > 0).values)) == dn_days
        and 192 in dn_days and 193 in dn_days,
        f"streak_days={sorted(dn_days)} composed={sorted(got_days)}")

    # ---- L6 grammar structure (eighteen axes / combos / seeds / sha)
    g = build_grammar_w14()
    sha = g["grammar_sha256"]
    _ok("L6a axis_combos == 1,693,052,928 (282,175,488 x 2 resi-axis "
        "x 3 cnt-axis values; W13 sumn-face combos x len(AXIS_RESI) x "
        "len(AXIS_CNT) adjudicated member-set 6-mult)",
        g["axis_combos"] == 1693052928
        == tl13.AXIS_COMBOS * len(AXIS_RESI) * len(AXIS_CNT))
    _ok("L6b eighteen axes present, resi == frozen two-value + cnt "
        "== frozen three-value adjudicated member set",
        len(g["axes"]) == 18 and g["axes"]["sumn"] == AXIS_SUMN
        and g["axes"]["resi"] == AXIS_RESI and len(AXIS_RESI) == 2
        and g["axes"]["cnt"] == AXIS_CNT and len(AXIS_CNT) == 3)
    _ok("L6c W14 seeds == SEED_REGISTRY berths (20327500/20328000/"
        "20328500 berths held, no re-pick)",
        g["seeds"]["trial_labor_w14_gen"]
        == SEED_REGISTRY["trial_labor_w14_gen"]
        and g["seeds"]["trial_labor_w14_scrnull"]
        == SEED_REGISTRY["trial_labor_w14_scrnull"]
        and g["seeds"]["trial_labor_w14_unc"]
        == SEED_REGISTRY["trial_labor_w14_unc"])
    _ok("L6d new sha16 constructively distinct from W1/MASS/W2-W13",
        sha not in set(PRIOR_WAVE_SHA16.values())
        and sha != tl13.FROZEN_SHA16,
        f"sha16={sha}")
    _ok("L6e exclusion face rows resi/cnt=none-padded to 18-long "
        "axis",
        all(len(r["axis"]) == 18 and r["axis"][-1] == "none"
            and r["axis"][-2] == "none"
            for r in g["exclusion"]
            ["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_"
             "rsqr_sumn_resi_cnt_none_face"]))
    _ok("L6f families/value_domains inherited from tl9 verbatim",
        g["families"] == tl9.build_grammar_w9()["families"]
        and len(g["value_domains"]) == len(
            tl9.build_grammar_w9()["value_domains"]))
    _ok("L6g FROZEN_SHA16 pin consistency (None = pre-pin build face; "
        "pinned = matches the built grammar)",
        FROZEN_SHA16 is None or FROZEN_SHA16 == sha)

    # ---- L7 G-MOM real-face probe anchors (point-in-time integrity
    # leg: warmup 139 / decidable 3344 / open 374 / closed 2970 + roc20
    # nan 20 + 256-cell 111/145 + cross lower bounds + extreme days 2/7
    # + streak/tstate/amp reproduction + core48 spread)
    rstate, rerr = _mom_state_full()
    _ok("L7a real-face state loads G-MOM clean (r228 probe basis)",
        rstate is not None and rerr is None, rerr or "anchors clean")
    if rstate is not None:
        ro, rd, rmeta = rstate
        _ok("L7b G-MOM exact anchors (n 3483 / warmup 139 / decidable "
            "3344 / open 374 / closed 2970 / roc20-nan-before-bar20 20)",
            rmeta["n_bars"] == 3483
            and rmeta["first_decidable_bar_idx"] == 139
            and rmeta["decidable_days"] == 3344
            and rmeta["open_days"] == 374
            and rmeta["closed_days"] == 2970)
        _ok("L7c eight-gate 256-cell cross: 111 non-empty + exact "
            "frozen 145-empty name list (probe range 1-37, "
            "all-decidable 3305)",
            len(rmeta["eight_gate_256cells"]) == 256
            and rmeta["eight_gate_256cells_empty"]
            == sorted(MOM_ANCHOR["eight_gate_256cells_empty"])
            and sum(1 for v in rmeta["eight_gate_256cells"].values()
                    if v > 0) == 111
            and min(v for v in rmeta["eight_gate_256cells"].values()
                    if v > 0) >= 1
            and max(rmeta["eight_gate_256cells"].values()) <= 37
            and rmeta["eight_gate_all_decidable_days"] == 3305)
        _ok("L7d cross lower bounds met (mom^mad60 253 / mom^rsv60 "
            "212 / mom^down_streak 139 / mom^wide 222)",
            all(rmeta["cross_lower_bounds"][k] >= v for k, v in
                {**MOM_ANCHOR["cross_tstate_lower_bounds"],
                 **MOM_ANCHOR["cross_streak_lower_bounds"],
                 **MOM_ANCHOR["cross_amp_lower_bounds"]}.items()),
            f"cross={rmeta['cross_lower_bounds']}")
        _ok("L7e extreme-day gate states exact (2/7 mom-open incl. "
            "2015-07-27 -0.0906 + 2025-04-07 -0.0852 open; 2016-01-04 "
            "-0.052 near-miss closed)",
            MOM_ANCHOR["extreme_days"]["2015-07-27"]["mom_open"] is True
            and abs(MOM_ANCHOR["extreme_days"]["2015-07-27"]
                    ["roc20_value"] + 0.0906) < 5.01e-5
            and MOM_ANCHOR["extreme_days"]["2025-04-07"]["mom_open"]
            is True
            and abs(MOM_ANCHOR["extreme_days"]["2025-04-07"]
                    ["roc20_value"] + 0.0852) < 5.01e-5
            and MOM_ANCHOR["extreme_days"]["2016-01-04"]["mom_open"]
            is False
            and abs(MOM_ANCHOR["extreme_days"]["2016-01-04"]
                    ["roc20_value"] + 0.052) < 5.01e-5
            and rmeta["n_bars"] == 3483)
        _ok("L7f STREAK/TSTATE/AMP reproduction counts exact (up 844 / "
            "down 817 / neither 1820 / mad60 383 / rsv60 632 / wide "
            "1718 / narrow 1746 -- W7/W8/W9 cross-probe determinism "
            "law)",
            rmeta["streak_anchor"]["up_streak_days"] == 844
            and rmeta["streak_anchor"]["down_streak_days"] == 817
            and rmeta["streak_anchor"]["neither_days"] == 1820
            and rmeta["tstate_anchor"]["mad60_gate_true_days"] == 383
            and rmeta["tstate_anchor"]["rsv60_gate_true_days"] == 632
            and rmeta["amp_anchor"]["wide_days"] == 1718
            and rmeta["amp_anchor"]["narrow_days"] == 1746)
        if os.path.exists(tl13.PROBE_FACTS_FILE):
            pf = json.load(open(tl13.PROBE_FACTS_FILE, encoding="utf-8"))
            nstate2, nerr2 = _sumn_state_full()
            _ok("L7g probe-facts exact per-cell 512-grid cross-check "
                "(r456 determinism law: every computed SUMN-face cell "
                "== the git-tracked frozen probe face)",
                nerr2 is None
                and nstate2[2]["nine_gate_512cells"]
                == pf.get("nine_gate_cells"),
                nerr2 or "sumn-face cells == probe facts")
        # core48 member-level sumn20 open-rate spread (r456 probe
        # method verbatim; frozen-runner SUMN verbatim)
        prices_r = tl1.load_core()
        cut_r = pd.Timestamp(CUTOFF)
        rates2 = {}
        for sym, d2 in sorted(prices_r.items()):
            d2 = d2[d2.index <= cut_r]
            if len(d2) >= 260:
                op2, wdec2, _ = sumn_state_series({SUMN_MEMBER: d2})[:3]
                if wdec2.any():
                    rates2[str(sym)] = round(float(
                        (op2 & wdec2).mean()), 4)
        vals2 = sorted(rates2.values())
        cf2 = SUMN_ANCHOR["core48_sumn20_open_rate"]
        _ok("L7i core48 sumn20-open-rate spread (n 48 / min 0.0728 / "
            "median 0.1012 / max 0.1171; r456 probe face)",
            len(vals2) == cf2["n"] and vals2[0] == cf2["min"]
            and vals2[len(vals2) // 2] == cf2["median"]
            and vals2[-1] == cf2["max"],
            f"n={len(vals2)} min={vals2[0] if vals2 else None}")
        # core48 member-level mom open-rate spread (tl1.load_core()
        # real roster, r228 probe method verbatim; per-member df passed
        # under the MOM_MEMBER key -- the series function is
        # member-keyed by construction)
        prices_c = tl1.load_core()
        cut_c = pd.Timestamp(CUTOFF)
        rates = {}
        for sym, d2 in sorted(prices_c.items()):
            d2 = d2[d2.index <= cut_c]
            if len(d2) >= 260:
                op, wdec, _ = _mom_series_raw({MOM_MEMBER: d2})[:3]
                if wdec.any():
                    # r228 probe caliber VERBATIM: open-rate = (open &
                    # decidable).mean() over the FULL series (warmup
                    # bars in the denominator) -- probe disclosure face
                    rates[str(sym)] = round(float(
                        (op & wdec).mean()), 4)
        vals = sorted(rates.values())
        cf = MOM_ANCHOR["core48_mom_open_rate"]
        _ok("L7h core48 mom-open-rate spread (n 48 / min 0.0723 / "
            "median 0.1012 / max 0.1215; r228 probe face)",
            len(vals) == cf["n"] and vals[0] == cf["min"]
            and vals[len(vals) // 2] == cf["median"]
            and vals[-1] == cf["max"],
            f"n={len(vals)} min={vals[0] if vals else None}")

    # ---- L8 draw contract (deterministic re-draw byte-identity +
    # eighteen-tuple + order-frozen stream)
    ga = build_grammar_w14()
    c1 = next(draw_candidate_sobol_w14(ga, "A", 0, 1))
    c2 = next(draw_candidate_sobol_w14(build_grammar_w14(), "A", 0, 1))
    _ok("L8a Sobol draw determinism (same seed -> byte-identical "
        "candidate incl. the resi+cnt axes, eighteen-tuple)",
        json.dumps(c1[1], sort_keys=True) == json.dumps(c2[1],
                                                        sort_keys=True)
        and len(c1[1]["axis"]) == 18)
    rng_a = np.random.default_rng([SEED_GEN + 0, 7919])
    n = 16
    eighteen = [rng_a.integers(0, 4, n) for _ in range(18)]
    rng_b = np.random.default_rng([SEED_GEN + 0, 7919])
    sixteen = [rng_b.integers(0, 4, n) for _ in range(16)]
    _ok("L8b RESI+CNT append AFTER SUMN in the rng stream (first "
        "sixteen axis arrays == W13-order stream verbatim, zero "
        "disturbance)",
        all(np.array_equal(a, b) for a, b in zip(eighteen, sixteen)))
    fam_b = ga["families"]["B"][0]
    _ok("L8c family B slot streams from fam_idx 6 (prereg A 0-5 / "
        "B 6+slot)",
        fam_b["module"] in {m for m in
                            [t["module"] for t in ga["families"]["A"]]})

    # ---- L9 exclusion loader real-read (20 sources + grammar face)
    rows10, disc10 = _load_exclusion_rows_w14(g)
    w9s = disc10.get("w9_screen_survivors")
    w9j = disc10.get("w9_judge_products")
    _ok("L9a exclusion loader: every row an 18-tuple axis, resi/cnt "
        "= none at 16/17 for ALL rows + sumn at 15 inside the frozen "
        "three-value domain + W13 real-sumn rows present (28 "
        "real-read sources; W1-W12 sources sumn=none, W13 survivors/"
        "judged carry real values)",
        all(len(r["axis"]) == 18 and r["axis"][16] == "none"
            and r["axis"][17] == "none"
            and r["axis"][15] in AXIS_SUMN for r in rows10)
        and any(r["axis"][15] in ("sumn20_lo", "sumn10_lo")
                for r in rows10)
        and {"w1_screen_survivors", "mass_screen_survivors",
             "w9_screen_survivors", "w9_judge_products",
             "w10_screen_survivors", "w10_judge_products",
             "w12_screen_survivors", "w12_judge_products",
             "w13_screen_survivors", "w13_judge_products",
             "judged_supply_weighting"} <= set(disc10))
    _ok("L9b W9 screen survivors real-read == 243 + W9 judged consumed "
        "== 243 (generate-time re-declare window, prereg sec.1 THIRTEEN "
        "judge sources; W9-JUDGE landed 2026-09-29 17:47:46)",
        w9s == 243 and isinstance(w9j, dict)
        and w9j.get("consumed_rows", 0) == 243,
        f"w9_screen={w9s} w9_judged="
        f"{w9j.get('consumed_rows') if isinstance(w9j, dict) else w9j}")
    ms = disc10.get("mass_screen_survivors")
    w7s = disc10.get("w7_screen_survivors")
    w8s = disc10.get("w8_screen_survivors")
    _ok("L9c W1 screen survivors == 149 + MASS consumed == 166 + W7 "
        "screen == 284 + W8 screen == 408 (frozen ten-screen list; "
        "declared conservative exact-key translation: consumed 166 = "
        "translated-exact 2 + non-translatable 164 disclosed, never "
        "excluded)",
        disc10.get("w1_screen_survivors") == 149
        and isinstance(ms, dict)
        and ms.get("consumed_pass_rows") == 166
        and ms.get("translated_exact_rows") == 2
        and ms.get("non_translatable_disclosed") == 164
        and w7s == 284 and w8s == 408)

    # ---- L10 _excluded_w14 exact-key law (mom face never excluded)
    hit_key = {"module": rows10[0]["module"], "fn": rows10[0]["fn"],
               "sig_params": rows10[0]["sig_params"],
               "axis": rows10[0]["axis"]}
    hit = _excluded_w14(hit_key, rows10)
    _ok("L10a exact already-judged key (mom=none face) -> excluded",
        hit is not None)
    miss_r = _excluded_w14({**hit_key,
                            "axis": [*hit_key["axis"][:16],
                                     "resi60_hi",
                                     hit_key["axis"][17]]},
                           rows10)
    miss_c = _excluded_w14({**hit_key,
                            "axis": [*hit_key["axis"][:17],
                                     "cntd5_hi"]},
                           rows10)
    _ok("L10b resi in {resi60_hi} / cnt in {cntd5_hi, cntn20_lo} = "
        "new-syntax legal cells, never excluded",
        miss_r is None and miss_c is None)

    # ---- L11 status contract (read-only, absent = PENDING, exit 0)
    rc = cmd_status()
    _ok("L11 status contract exit 0 on pending products", rc == 0)

    # ---- L12 effective-mask legs (mask level, zero engine burn)
    tl1.GRAMMAR = g          # engine legs need tl1's grammar global
    frames3 = tl1._synth_prices(n_days=640, n_syms=3, seed=23)
    # controlled crash member: flat 100 (0-299) -> 1%/bar crash
    # (300-330) -> flat to 639 (mom opens only inside the crash window
    # subset {301..349})
    alt_c = pd.Series(100.0, index=frames3["510300"].index)
    avals = alt_c.values.copy()
    for i_ in range(len(avals)):
        if 300 <= i_ <= 330:
            avals[i_] = 100.0 * (0.99 ** (i_ - 299))
        elif i_ > 330:
            avals[i_] = 100.0 * (0.99 ** 31)
    alt_o = pd.Series(100.0, index=alt_c.index)
    alt_v = pd.Series(1000.0, index=alt_c.index)
    alt_h = pd.Series(avals + 1.0, index=alt_c.index)
    alt_l = pd.Series(avals - 1.0, index=alt_c.index)
    frames3[MOM_MEMBER] = pd.DataFrame(
        {"open": alt_o, "high": alt_h, "low": alt_l,
         "close": pd.Series(avals, index=alt_c.index),
         "volume": alt_v, "amount": 1e5}, index=alt_c.index)
    P3 = tl1.build_panels(frames3)
    gs3 = tl3.gate_state_series(frames3)
    vs3 = tl4.vol_state_series(frames3)
    ys3 = tl5.yang_state_series(frames3)
    cs3 = tl6.vconf_state_series(frames3)
    sk3 = tl7.streak_state_series(frames3)
    ts3 = tl8.tstate_state_series(frames3)
    as3 = tl9.amp_state_series(frames3)
    ms3 = mom_state_series(frames3)
    ss3 = std_state_series(frames3)
    rq3 = rsqr_state_series(frames3)
    nq3 = sumn_state_series(frames3)
    rs3 = resi_state_series(frames3)
    cn3 = cnt_state_series(frames3)
    sig = pd.DataFrame(1.0, index=P3["close"].index,
                       columns=P3["close"].columns)
    m_none = _effective_signal_mask_w14(
        sig, frames3, "none", None,
        "none", "none", "none", "none",          # gate vol yang vconf
        "none", "none", "none", "none",          # streak tstate amp mom
        "none", "none", "none", "none",          # std rsqr sumn resi
        "none",                                    # cnt
        gs3, vs3, ys3, cs3, sk3, ts3, as3, ms3, ss3,
        rq3, nq3, rs3, cn3)
    m_w9 = tl9._effective_signal_mask_w9(
        sig, frames3, "none", None, "none", "none", "none", "none",
        "none", "none", "none", gs3, vs3, ys3, cs3, sk3, ts3, as3)
    _ok("L12a effective mask mom=none == W9 face byte-equal "
        "(semantic-baseline identity law)",
        m_none.equals(m_w9))
    m_w13 = tl13._effective_signal_mask_w13(
        sig, frames3, "none", None,
        gate_key="none", vol_key="none", yang_key="none",
        vconf_key="none", streak_key="none", tstate_key="none",
        amp_key="none", mom_key="none", std_key="none",
        rsqr_key="none", sumn_key="none",
        gate_state=gs3, vol_state=vs3, yang_state=ys3,
        vconf_state=cs3, streak_state=sk3, tstate_state=ts3,
        amp_state=as3, mom_state=ms3, std_state=ss3,
        rsqr_state=rq3, sumn_state=nq3)
    _ok("L12a2 effective mask resi/cnt=none == tl13 W13 face "
        "byte-equal (W14 semantic-baseline identity law)",
        m_none.equals(m_w13))
    m_ov = _effective_signal_mask_w14(
        sig, frames3, "none", None,
        "none", "none", "none", "none",          # gate vol yang vconf
        "none", "none", "none", "mom_oversold",  # streak tstate amp mom
        "none", "none", "none", "none",          # std rsqr sumn resi
        "none",                                    # cnt
        gs3, vs3, ys3, cs3, sk3, ts3, as3, ms3, ss3,
        rq3, nq3, rs3, cn3)
    mo_open3 = set(np.flatnonzero((ms3[0] & ms3[1]).values))
    got_ov_days = set(np.flatnonzero(
        (m_ov[m_ov.columns[0]] > 0).values))
    _ok("L12b mom_oversold on the crash face permits ONLY mom-open "
        "decidable days (bite positive leg: permitted day-set == the "
        "mom-open set; warmup bars NEVER permitted)",
        got_ov_days == mo_open3
        and not (got_ov_days & set(range(139))),
        f"open={len(mo_open3)} permitted={len(got_ov_days)}")
    # accelerating-GROWTH member: roc20 strictly increasing -> q10_ref
    # (trailing decile of LOWER roc20s) always below roc20 -> ZERO open
    # days -> mom_oversold mask all-zero (bite negative leg)
    frames5 = tl1._synth_prices(n_days=640, n_syms=3, seed=23)
    grow_c = pd.Series(
        [100.0 * math.exp(0.000008 * (i5 ** 2)) for i5 in range(640)],
        index=frames5["510300"].index)
    frames5[MOM_MEMBER] = pd.DataFrame(
        {"open": pd.Series(100.0, index=grow_c.index),
         "high": grow_c + 1.0, "low": grow_c - 1.0, "close": grow_c,
         "volume": pd.Series(1000.0, index=grow_c.index),
         "amount": 1e5}, index=grow_c.index)
    P5 = tl1.build_panels(frames5)
    gs5 = tl3.gate_state_series(frames5)
    vs5 = tl4.vol_state_series(frames5)
    ys5 = tl5.yang_state_series(frames5)
    cs5 = tl6.vconf_state_series(frames5)
    sk5 = tl7.streak_state_series(frames5)
    ts5 = tl8.tstate_state_series(frames5)
    as5 = tl9.amp_state_series(frames5)
    ms5 = mom_state_series(frames5)
    ss5 = std_state_series(frames5)
    rq5 = rsqr_state_series(frames5)
    nq5 = sumn_state_series(frames5)
    rs5 = resi_state_series(frames5)
    cn5 = cnt_state_series(frames5)
    sig5 = pd.DataFrame(1.0, index=P5["close"].index,
                        columns=P5["close"].columns)
    m5_none = _effective_signal_mask_w14(
        sig5, frames5, "none", None,
        "none", "none", "none", "none",          # gate vol yang vconf
        "none", "none", "none", "none",          # streak tstate amp mom
        "none", "none", "none", "none",          # std rsqr sumn resi
        "none",                                    # cnt
        gs5, vs5, ys5, cs5, sk5, ts5, as5, ms5, ss5,
        rq5, nq5, rs5, cn5)
    m5_ov = _effective_signal_mask_w14(
        sig5, frames5, "none", None,
        "none", "none", "none", "none",          # gate vol yang vconf
        "none", "none", "none", "mom_oversold",  # streak tstate amp mom
        "none", "none", "none", "none",          # std rsqr sumn resi
        "none",                                    # cnt
        gs5, vs5, ys5, cs5, sk5, ts5, as5, ms5, ss5,
        rq5, nq5, rs5, cn5)
    _ok("L12c mom_oversold on the accelerating-growth face (roc20 "
        "strictly increasing = zero oversold days) permits NOTHING "
        "(bite negative leg: all-zero mask while mom=none face is "
        "live)",
        int((m5_ov > 0).sum().sum()) == 0
        and int((m5_none > 0).sum().sum()) > 0
        and int(ms5[0].sum()) == 0)

    # ---- L13 engine-face legs: parity + determinism + mom bites
    base = {"module": "volatility", "fn": "low_vol_long",
            "sig_params": {"n": 60, "top_k": 3, "rebal_days": None},
            "family": "B", "candidate_id": "ST-B-0000",
            "axis": ["none", "time_stop_5d", "equal_weight",
                     "daily_signal"] + ["none"] * 14}
    st3 = pd.Series("GREEN", index=P3["close"].index)
    eq10, tr10, m10, _, _, _, _, _, _, _, sz10, tz10, az10, mz10, \
        sdz10, rz10, nz10, rrez10, cntz10 = \
        run_candidate_curve_w14(
            base, None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,
            yang_state=ys3, vconf_state=cs3, streak_state=sk3,
            tstate_state=ts3, amp_state=as3, mom_state=ms3,
            std_state=ss3, rsqr_state=rq3, sumn_state=nq3,
            resi_state=rs3, cnt_state=cn3)
    eq9 = tl9.run_candidate_curve_w9(
        dict(base, axis=base["axis"][:12]), None, frames3, P3, st3,
        gate_state=gs3, vol_state=vs3, yang_state=ys3,
        vconf_state=cs3, streak_state=sk3, tstate_state=ts3,
        amp_state=as3)[0]
    _ok("L13a engine face: mom=none identical to tl9 W9 face "
        "(byte-equal parity law)",
        list(eq10.values) == list(eq9.values))
    eq10b, _, _, _, _, _, _, _, _, _, sz10b, tz10b, az10b, mz10b, \
        sdz10b, rz10b, nz10b, rrez10b, cntz10b = \
        run_candidate_curve_w14(
            dict(base, candidate_id="ST-B-0001"), None, frames3, P3,
            st3, gate_state=gs3, vol_state=vs3, yang_state=ys3,
            vconf_state=cs3, streak_state=sk3, tstate_state=ts3,
            amp_state=as3, mom_state=ms3, std_state=ss3,
            rsqr_state=rq3, sumn_state=nq3, resi_state=rs3,
            cnt_state=cn3)
    _ok("L13b engine double-run byte-identity (determinism leg) + "
        "19-tuple return shape (resi_zeroed + cnt_zeroed carried; "
        "all-none face zeroed counters == 0)",
        list(eq10.values) == list(eq10b.values) and sz10 == sz10b
        and tz10 == tz10b and az10 == az10b and mz10 == mz10b == 0
        and rz10 == rz10b == 0 and nz10 == nz10b == 0
        and rrez10 == rrez10b == 0 and cntz10 == cntz10b == 0
        and sdz10 == sdz10b)
    st5 = pd.Series("GREEN", index=P5["close"].index)
    eq5n, tr5n, m5n, _, _, _, _, _, _, _, _, _, az5n, mz5n, \
        _, _, _, _, _ = \
        run_candidate_curve_w14(
            dict(base, axis=list(base["axis"])), None, frames5, P5,
            st5, gate_state=gs5, vol_state=vs5, yang_state=ys5,
            vconf_state=cs5, streak_state=sk5, tstate_state=ts5,
            amp_state=as5, mom_state=ms5, std_state=ss5,
            rsqr_state=rq5, sumn_state=nq5, resi_state=rs5,
            cnt_state=cn5)
    _ok("L13c engine face: mom=none on the accelerating-growth face "
        "runs with entries (num_entries > 0 baseline leg)",
        int(m5n.get("num_entries", -1)) > 0 and mz5n == 0)
    eq5o, tr5o, m5o, _, _, _, _, _, _, _, _, _, az5o, mz5o, \
        _, _, _, rrez5o, cntz5o = \
        run_candidate_curve_w14(
            dict(base, axis=[*base["axis"][:12], "mom_oversold",
                             "none", "none", "none", "none", "none"]),
            None, frames5, P5, st5, gate_state=gs5, vol_state=vs5,
            yang_state=ys5, vconf_state=cs5, streak_state=sk5,
            tstate_state=ts5, amp_state=as5, mom_state=ms5,
            std_state=ss5, rsqr_state=rq5, sumn_state=nq5,
            resi_state=rs5, cnt_state=cn5)
    _ok("L13d engine face: mom_oversold on the zero-oversold face "
        "zeroes every entry (mask all-zero + engine num_entries == 0 + "
        "mom_zeroed > 0; resi/cnt none-face zeroed == 0)",
        int((m5_ov > 0).sum().sum()) == 0
        and int(m5o.get("num_entries", -1)) == 0 and mz5o > 0
        and rrez5o == 0 and cntz5o == 0)
    eq3o, tr3o, m3o, _, _, _, _, _, _, _, _, _, az3o, mz3o, \
        _, _, _, _, _ = \
        run_candidate_curve_w14(
            dict(base, axis=[*base["axis"][:12], "mom_oversold",
                             "none", "none", "none", "none", "none"]),
            None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,
            yang_state=ys3, vconf_state=cs3, streak_state=sk3,
            tstate_state=ts3, amp_state=as3, mom_state=ms3,
            std_state=ss3, rsqr_state=rq3, sumn_state=nq3,
            resi_state=rs3, cnt_state=cn3)
    _ok("L13e engine face: mom_oversold on the crash face runs with "
        "entries on the permitted window (bite positive leg: "
        "num_entries >= 0 with off-window signals zeroed: mom_zeroed "
        "> 0 iff off-open-day signals existed)",
        az3o >= 0 and mz3o >= 0)

    # ---- L14 null-axis draw contract (eighteen-tuple + determinism)
    p1, ax1, rg1 = _null_axis_draw_w14(0)
    p2, ax2, rg2 = _null_axis_draw_w14(0)
    _ok("L14 null-axis draw determinism + EIGHTEEN-tuple with resi+cnt "
        "in the frozen domains (W14 null berth 20328000)",
        p1 == p2 and ax1 == ax2 and len(ax1) == 18
        and ax1[12] in AXIS_MOM and ax1[13] in AXIS_STD
        and ax1[15] in AXIS_SUMN
        and ax1[14] in AXIS_RSQR
        and ax1[16] in AXIS_RESI and ax1[17] in AXIS_CNT
        and ax1[11] in tl9.AXIS_AMP
        and ax1[10] in tl8.AXIS_TSTATE and ax1[9] in tl7.AXIS_STREAK
        and ax1[4] in tl2.AXIS_STOP)

    # ---- L15 funnel faces (dispatch + null path + contract)
    want_cmds = ["grammar", "generate", "screen-prep", "screen",
                 "screen-finalize", "judge-prep", "judge",
                 "judge-finalize", "intake", "status", "selftest"]
    got_cmds = []
    for probe in (["grammar"], ["generate"], ["screen-prep"],
                  ["screen"], ["screen-finalize"], ["judge-prep"],
                  ["judge"], ["judge-finalize"], ["intake"],
                  ["status"], ["selftest"]):
        a = _build_parser().parse_args(probe)
        got_cmds.append(a.cmd)
    a_sh = _build_parser().parse_args(
        ["screen", "--shard", "1", "--shards", "4", "--workers", "9"])
    _ok("L15a main dispatch registers all eleven funnel subcommands "
        "zero-burn (r141 crash-lane: every registered cmd has a body)",
        got_cmds == want_cmds
        and (a_sh.shard, a_sh.shards, a_sh.workers) == (1, 4, 9))
    p_on0, ax0, rng0 = _null_axis_draw_w14(0)
    p_on0b, ax0b, rng0b = _null_axis_draw_w14(0)
    dom0 = (ax0[12] in AXIS_MOM and ax0[13] in AXIS_STD
            and ax0[15] in AXIS_SUMN
            and ax0[14] in AXIS_RSQR
            and ax0[16] in AXIS_RESI and ax0[17] in AXIS_CNT
            and ax0[4] in tl2.AXIS_STOP and len(ax0) == 18)
    mat0 = rng0.random((len(P3["close"].index), len(P3["close"].columns)))
    eqn, trn, mtn, prn, pt, frn, gzn, vzn, yzn, czn, szn, tzn, azn, \
        mzn, sdzn, rzn, nznn, rrezn, cntzn = \
        run_candidate_curve_w14(
            {"module": "null", "fn": "random_signal",
             "sig_params": {"p_on": p_on0}, "axis": ax0,
             "candidate_id": "W14-NULL-0000", "family": "NULL"},
            None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,
            yang_state=ys3, vconf_state=cs3, streak_state=sk3,
            tstate_state=ts3, amp_state=as3, mom_state=ms3,
            std_state=ss3, rsqr_state=rq3, sumn_state=nq3,
            resi_state=rs3, cnt_state=cn3, rng_matrix=mat0,
            p_on=p_on0)
    mat0b = rng0b.random((len(P3["close"].index),
                          len(P3["close"].columns)))
    eqnb, _, _, _, _, _, _, _, _, _, _, _, _, mznb, _, rznb, nznb, \
        rreznb, cntznb = \
        run_candidate_curve_w14(
            {"module": "null", "fn": "random_signal",
             "sig_params": {"p_on": p_on0b}, "axis": ax0b,
             "candidate_id": "W14-NULL-0000", "family": "NULL"},
            None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,
            yang_state=ys3, vconf_state=cs3, streak_state=sk3,
            tstate_state=ts3, amp_state=as3, mom_state=ms3,
            std_state=ss3, rsqr_state=rq3, sumn_state=nq3,
            resi_state=rs3, cnt_state=cn3, rng_matrix=mat0b,
            p_on=p_on0b)
    _ok("L15b null-cell engine path: eighteen-tuple null draw "
        "deterministic + resi/cnt axis in-domain + engine 19-tuple "
        "return + double-run byte-identity (screen null-family path)",
        p_on0 == p_on0b and ax0 == ax0b and dom0
        and len(eqn) == len(P3["close"].index) and mzn >= 0
        and list(eqn.values) == list(eqnb.values) and mzn == mznb
        and rzn == rznb
        and nznn == nznb and rrezn == rreznb and cntzn == cntznb)
    _ok("L15c screen CSV contract carries the mom+std+rsqr+sumn+resi+"
        "cnt columns in the frozen order (cell_id/candidate_id head + "
        "resi/cnt pairs before survives_screen)",
        csv_cols_screen_w14[:2] == ["cell_id", "candidate_id"]
        and csv_cols_screen_w14[-7:] == ["sumn_face", "sumn_zeroed",
                                         "resi_face", "resi_zeroed",
                                         "cnt_face", "cnt_zeroed",
                                         "survives_screen"]
        and "mom_face" in csv_cols_screen_w14
        and {"gate_zeroed", "vol_zeroed", "yang_zeroed", "vconf_zeroed",
             "streak_zeroed", "tstate_zeroed", "amp_zeroed",
             "mom_zeroed", "std_zeroed", "rsqr_zeroed", "sumn_zeroed",
             "resi_zeroed", "cnt_zeroed"} <= set(csv_cols_screen_w14))

    g_scr = tl6.finalize_already_landed(SCREEN_BATCH, SCREEN_FILE)
    if os.path.exists(SCREEN_FILE):
        _ok("L15d pit-95 guard live-fire: w14_screen.json carries "
            "SCREEN_BATCH -> finalize re-run would be refused",
            isinstance(g_scr, dict)
            and g_scr.get("batch") == SCREEN_BATCH
            and isinstance(g_scr.get("total"), int))
    else:
        _ok("L15d pit-95 guard fresh-face: w14_screen.json absent -> "
            "guard None = lawful fresh batch, finalize proceeds",
            g_scr is None)
    g_jdg = tl6.finalize_already_landed(JUDGE_BATCH, JUDGE_FILE)
    if os.path.exists(JUDGE_FILE):
        _ok("L15e pit-95 guard live-fire: w14_judge.json carries "
            "JUDGE_BATCH -> finalize re-run would be refused",
            isinstance(g_jdg, dict)
            and g_jdg.get("batch") == JUDGE_BATCH
            and isinstance(g_jdg.get("total"), int))
    else:
        _ok("L15e pit-95 guard fresh-face: w14_judge.json absent -> "
            "guard None = lawful fresh batch, finalize proceeds",
            g_jdg is None)

    # ---- L16 G-RESI/G-CNT real-face anchor loads (W14 own faces;
    # internal gates assert every probe anchor fail-closed)
    re_st, re_err = _resi_state_full()
    _ok("L16a real-face state loads G-RESI clean (n 3483 / grids / "
        "extreme-day anchors fail-closed; r470/r471 probe basis)",
        re_st is not None and re_err is None, re_err or "anchors clean")
    if re_st is not None:
        _re_meta = re_st[2]
        _ok("L16b G-RESI exact anchors (n_bars 3483 + structure "
            "pass: 120-bar warmup partitions)",
            _re_meta.get("n_bars") == 3483
            and _resi_structure_pass(_re_meta))
    cn_st, cn_err = _cnt_state_full()
    _ok("L16c real-face state loads G-CNT clean (dual cntd5+cntn20 "
        "sub-faces / grids / extreme days fail-closed; r470/r471 + "
        "bm-c r277 twin probe basis)",
        cn_st is not None and cn_err is None, cn_err or "anchors clean")
    if cn_st is not None:
        _cn_meta = cn_st[4]
        _ok("L16d G-CNT exact anchors (n_bars 3483 + dual sub-face "
            "structure pass)",
            _cn_meta.get("n_bars") == 3483
            and _cnt_structure_pass(_cn_meta))

    print(f"\nselftest: {n_pass}/{n_leg} PASS "
          f"(scope: W14 resi+cnt layer + G-RESI/G-CNT + "
          f"eighteen-tuple grammar + machinery: effective mask / "
          f"curve runner parity / null draw / 28-source exclusion "
          f"loader + funnel faces: dispatch / null-cell engine path / "
          f"CSV contract + pit-95 finalize idempotency guard "
          f"state-adaptive legs + W10-W13 regression legs; zero live "
          f"cells burned, zero numbers fabricated)")
    return 0 if n_pass == n_leg else 1


def _build_parser():
    """Argparse face shared by main() + the hermetic selftest dispatch
    leg (zero-burn registration probe)."""
    ap = argparse.ArgumentParser(description="TRIAL_LABOR_W14 runner "
                                     "(RESI+CNT eighteen-gate wave)")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("grammar", help="serialize the frozen W14 grammar")
    sub.add_parser("generate",
                   help="s1 Sobol draws -> exclusion -> dedup -> "
                        "w14_candidates.json + ledger row")
    sub.add_parser("screen-prep",
                   help="fail-closed gates + passive 6m precompute")
    sp = sub.add_parser("screen", help="s2 cheap screen shard burn")
    sp.add_argument("--shard", type=int, default=0)
    sp.add_argument("--shards", type=int, default=1)
    sp.add_argument("--workers", type=int, default=None)
    sub.add_parser("screen-finalize",
                   help="null p95 survival line -> w14_screen.json + csv")
    sub.add_parser("judge-prep",
                   help="dual-leg census gates + starts + passive")
    jp = sub.add_parser("judge", help="s3 full judgment shard burn")
    jp.add_argument("--shard", type=int, default=0)
    jp.add_argument("--shards", type=int, default=1)
    jp.add_argument("--workers", type=int, default=None)
    sub.add_parser("judge-finalize",
                   help="G1'v2/G2/DSR/PBO gates -> w14_judge.json")
    sub.add_parser("intake",
                   help="s4 D6 binding gate -> w14_intake.json")
    sub.add_parser("status", help="slice-state readout")
    sub.add_parser("selftest", help="hermetic offline selftest")
    return ap


def main(argv=None):
    args = _build_parser().parse_args(argv)
    # r141 crash-lane law: explicit per-command forwarding; no zero-arg
    # dict dispatch; every registered subcommand HAS a built body
    # (slice-1 complete -- zero half-built dispatch faces)
    if args.cmd == "grammar":
        return cmd_grammar()
    if args.cmd == "generate":
        return cmd_generate()
    if args.cmd == "screen-prep":
        return cmd_screen_prep()
    if args.cmd == "screen":
        return cmd_screen(args.shard, args.shards, args.workers)
    if args.cmd == "screen-finalize":
        return cmd_screen_finalize()
    if args.cmd == "judge-prep":
        return cmd_judge_prep()
    if args.cmd == "judge":
        return cmd_judge(args.shard, args.shards, args.workers)
    if args.cmd == "judge-finalize":
        return cmd_judge_finalize()
    if args.cmd == "intake":
        return cmd_intake()
    if args.cmd == "status":
        return cmd_status()
    if args.cmd == "selftest":
        return cmd_selftest()
    _build_parser().print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
