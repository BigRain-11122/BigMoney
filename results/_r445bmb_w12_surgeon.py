# -*- coding: utf-8 -*-
"""_r445bmb_w12_surgeon.py -- W12 runner build surgery (Slice-A, bm-b r445).

TRIAL_LABOR_W12 runner draft generator: operates on the FROZEN W11
runner (scripts/trial_labor_w11.py, bm-b r442/r443 close-out face)
producing results/_r445bmb_w12_runner_draft.py per frozen
research/TRIAL_LABOR_W12_PREREG sec.3:
  - fifteen-tuple = fourteen-tuple + RSQR in {none, rsqr20_hi,
    rsqr10_hi} (three-value axis, W4-VOL/W11-STD precedent) ->
    31,352,832 * 3 = 94,058,496
  - RSQR gate construction VERBATIM from the frozen in-repo runner
    (scripts/a158_tsgate_probe.py::alpha158_factors import --
    zero-invention law; the r447 probe
    results/_r447bma_rsqr_w12_probe.py is the frozen authoritative
    definition; GATE_WIN=252 / GATE_MINP=120 constants same-source)
  - RSQR_ANCHOR generated PROGRAMMATICALLY from
    results/_r447bma_rsqr_w12_probe_facts.json (zero hand-copy;
    r445 declare-vs-disk law)
  - STD machinery imported verbatim from tl11 (W11 frozen face;
    import-face law; zero re-implementation)
  - seeds: trial_labor_w12_gen/scrnull/unc = 20320500/20321000/
    20321500 (freeze-commit berths, bm-b r444; three-step law ALL
    GREEN facts results/_r444bmb_w12_seed_law_facts.json)
Products: draft file + surgery report JSON.  Draft is NOT the formal
runner until Slice-B review (selftest anchor faces + grammar
serialization + sha16 pin) -- formal name scripts/trial_labor_w12.py
is the final move (runner_exists gate at Tools/fill_ladder_catalog.json
must not fire on a partial build).
"""
from __future__ import annotations
import json
import os
import re
import sys

ROOT = os.getcwd()
SRC = os.path.join("scripts", "trial_labor_w11.py")
DST = os.path.join("results", "_r445bmb_w12_runner_draft.py")
REPORT = os.path.join("results", "_r445bmb_w12_surgery_report.json")
FACTS = os.path.join("results", "_r447bma_rsqr_w12_probe_facts.json")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def die(msg):
    print("SURGEON-FAIL: " + msg)
    sys.exit(2)


def sub1(src, old, new, what):
    """Count-verified single replace (exactly one hit)."""
    if src.count(old) != 1:
        die("anchor not unique (%d hits): %r" % (src.count(old),
                                                 old[:70]) + " | " + what)
    return src.replace(old, new)


def subn(src, old, new, n, what):
    """Count-verified n-hit replace."""
    if src.count(old) != n:
        die("anchor count %d != %d: %r" % (src.count(old), n,
                                           old[:70]) + " | " + what)
    return src.replace(old, new)


def segment(src, start_marker, end_marker, include_start=True,
            include_end=False):
    """Cut [start_marker .. end_marker) by marker text (unique hit)."""
    i = src.find(start_marker)
    if i < 0:
        die("start marker not found: %r" % start_marker[:60])
    if src.find(start_marker, i + 1) >= 0:
        die("start marker not unique: %r" % start_marker[:60])
    j = src.find(end_marker, i + len(start_marker))
    if j < 0:
        die("end marker not found after start: %r" % end_marker[:60])
    a = i if include_start else i + len(start_marker)
    b = j + len(end_marker) if include_end else j
    return src[a:b], a, b


def build_rsqr_anchor():
    """RSQR_ANCHOR dict generated programmatically from probe facts
    (zero hand-copy; r445 declare-vs-disk law)."""
    pf = json.load(open(FACTS, encoding="utf-8"))
    cells = pf["nine_gate_cells"]
    empty = sorted(k for k, v in cells.items() if v <= 0)
    adj = pf["adjacency"]
    slope = pf["rsqr20_open_slope_sign_split"]
    anchor = {
        "n_bars": pf["rows"],
        "first_date": pf["first_date"],
        "cutoff": pf["last_date"],
        "rsqr20_first_valid_bar_idx": 1,  # k=2 two-point OLS fit
        "warmup_gate_closed_bars": 120,
        "first_decidable_bar_idx": 120,
        "decidable_days": pf["rsqr20_decidable_days"],
        "open_days": pf["rsqr20_open_days"],
        "closed_days": pf["rsqr20_decidable_days"]
                       - pf["rsqr20_open_days"],
        "rsqr20_open_rate_on_decidable":
            pf["rsqr20_open_rate_on_decidable"],
        "rsqr10_decidable_days": pf["rsqr10_decidable_days"],
        "rsqr10_open_days": pf["rsqr10_open_days"],
        "rsqr10_open_rate_on_decidable":
            pf["rsqr10_open_rate_on_decidable"],
        "slope_sign_split": {
            "up_slope_days": slope["up_slope_days"],
            "down_slope_days": slope["down_slope_days"],
            "note": "BETA20 sign from the same frozen runner; "
                    "direction face intentionally NOT part of the "
                    "gate (burned axes carry direction)",
        },
        "cross_lower_bounds": {
            "mad60_and_rsqr20": adj["rsqr20_vs_mad60"]["both_open"],
            "rsv60_and_rsqr20": adj["rsqr20_vs_rsv60"]["both_open"],
            "down_streak_and_rsqr20":
                adj["rsqr20_vs_downstreak"]["both_open"],
            "wide_and_rsqr20": adj["rsqr20_vs_wide"]["both_open"],
            "mom_and_rsqr20": adj["rsqr20_vs_mom"]["both_open"],
            "std20_and_rsqr20": adj["rsqr20_vs_std20"]["both_open"],
            "rsqr20_vs_rsqr10_both_open":
                adj["rsqr10_vs_rsqr20"]["both_open"],
        },
        "nine_gate_all_decidable_days":
            pf["nine_gate_all_decidable_days"],
        "nine_gate_512cells_nonzero_count":
            pf["nine_gate_512_cells_nonzero_count"],
        "nine_gate_512cells_empty_count":
            pf["nine_gate_512_cells_empty_count"],
        "nine_gate_512cells_min_nonzero":
            pf["nine_gate_512_cells_min_nonzero"],
        "nine_gate_512cells_max": pf["nine_gate_512_cells_max"],
        "nine_gate_512cells_empty": empty,
        "extreme_days": pf["extreme_day_states"],
        "streak_anchor_reproduction": {
            "up_streak_days": 844, "down_streak_days": 817,
            "neither_days": 1820},
        "tstate_anchor_reproduction": {
            "mad60_gate_true_days": 383, "rsv60_gate_true_days": 632},
        "amp_anchor_reproduction": {
            "wide_days": 1718, "narrow_days": 1746, "zero_range_rows": 0},
        "core48_rsqr20_open_rate": pf["core48_rsqr20_open_rate"],
        "probe_facts_note": "generated verbatim from "
                            "_r447bma_rsqr_w12_probe_facts.json "
                            "(r447 probe = frozen authoritative RSQR "
                            "definition via the a158 frozen-runner "
                            "import; nine-gate face = rsqr20 open/"
                            "closed states on the r447 probe basis; "
                            "W4-VOL/W11-STD three-value axis "
                            "precedent)",
    }
    assert anchor["nine_gate_512cells_nonzero_count"] == 124
    assert anchor["nine_gate_512cells_empty_count"] == 388
    assert len(empty) == 388
    assert anchor["decidable_days"] == 3363
    assert anchor["open_days"] == 341
    assert anchor["closed_days"] == 3022
    assert anchor["rsqr10_decidable_days"] == 3363
    assert anchor["rsqr10_open_days"] == 332
    assert anchor["first_decidable_bar_idx"] == 120
    assert anchor["slope_sign_split"]["up_slope_days"] == 213
    assert anchor["slope_sign_split"]["down_slope_days"] == 128
    return anchor


W12_DOCSTRING = '''"""TRIAL_LABOR_W12 runner -- T-124 mass-candidate trial wave-12
(5000-ceiling, RSQR trend-fit-quality FIFTEEN-gate wave).

Prereg FROZEN (bm-b r444 whole-package adoption of the bm-a r447 RSQR
candidate per the AMP->W9 / MOM->W10 / STD->W11 / RSQR->W12
four-straight adoption lineage; freeze trigger MET live = W11 full
chain landed 2026-09-30 01:47:40 {w11_judge.json 229/229 judged zero
G1 zero G2 + CEO-REPORT-WAVE11-20260930 + attrition CLEAN + TRIAL_
GRAMMAR_LEDGER wave-11 row + W11 prereg sec.7/sec.8 backfilled} +
pool entries drained {TRIAL-LABOR-W11-JUDGE flipped done; INNOVATION-
QUOTA-SLOT-4 = bm-c innovation-quota lane, non-trial-labor honest
disclosure}):
research/TRIAL_LABOR_W12_PREREG.md -- generate grammar + funnel rules +
judgment lines all frozen; post-run only sec.7/8 backfill.  Seeds held
at the freeze commit per R250 one-step law: trial_labor_w12_gen=
20320500 / trial_labor_w12_scrnull=20321000 / trial_labor_w12_unc=
20321500 (berth-open adoption of the bm-a r447 RSQR candidate whole
package; three-step law ALL GREEN at the freeze commit
results/_r444bmb_w12_seed_law_facts.json, no re-pick after freeze).

Import-face law (prereg sec.3): the FULL trial_labor_w1-w11 chain is
imported (tl1 enumeration/loading/anchor/envelope primitives + tl2
initial-stop overlay + tl3 regime-gate overlay + tl4 vol overlay +
tl5 yang overlay + tl6 vconf overlay + tl7 streak overlay + tl8
tstate overlay & eleven-tuple machinery + tl9 amp overlay & twelve-
tuple machinery + tl10 mom overlay & thirteen-tuple machinery + tl11
std overlay & fourteen-tuple machinery); RSQR comes from the FROZEN
in-repo runner scripts/a158_tsgate_probe.py verbatim import
(alpha158_factors + GATE_WIN=252 / GATE_MINP=120 constants same-
source; zero re-implementation); Sobol sample_draws pattern follows
mass_trial_w1 (paradigm import); strategies/ factory + engine/
backtester imported, never rewritten; engine/exit_rules.py ZERO touch.

RSQR overlay (prereg sec.2/sec.3 NEW W12 frozen layer; r447 probe
verbatim = A158-TSGATE-P1 frozen RSQR construction): member 510300
signal-day-d close info set.  F = a158.alpha158_factors(member face);
f = F["RSQR20"] = rolling OLS r^2 of close vs t=1..d, 20-day window
(qlib expanding-warmup semantics + flat-price guard std~0->NaN;
RSQR10 same construction); q90_ref = f.rolling(252, min_periods=120)
.quantile(0.90); rsqr_hi = f > q90_ref (trend-fit QUALITY entering
its own top decile = clean directional-trend state; fit quality is
DIRECTION-BLIND -- slope-sign split among rsqr20-open days 213 up /
128 down, direction conditioning lives in the burned axes GATE/
YANG/STREAK/MOM).  120-bar warmup window gate-closed honest (f valid
from bar-idx 1: k=2 two-point fit; q90_ref min_periods 120 -> first
decidable bar-idx == 120, fail-closed assertion == STD family warmup).
Gate acts on ENTRY PERMITTANCE only (effective signal zeroed,
MSG-0440 E1-mapping primitive; exit logic zero change).  Composition
order frozen everywhere: signal -> filter -> timing -> GATE -> VOL ->
YANG -> VCONF -> STREAK -> TSTATE -> AMP -> MOM -> STD -> RSQR ->
initial-stop (W11 order extended; prereg sec.3 fifteen-tuple order
R/X/S/T/STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR).

G-RSQR anchor law (prereg sec.2 probe facts, fail-closed): on the raw
full-history member face (3,483 bars 2012-05-28 -> 2026-09-22 cutoff):
first-decidable == 120 / decidable == 3,363 / rsqr20 open == 341
(9.79%) / rsqr10 open == 332 (9.53%); slope-sign split 213 up / 128
down; NINE-gate (gate x vol x yang x vconf x streak x tstate x amp x
std20 x rsqr20) 512 open-window cells: 124 non-empty / 388 empty
(probe range 1-41; all-decidable 3,305); extreme-day gate states
0/7 rsqr-open both windows (fit gate structurally closed on crisis
days) + exact per-cell cross-check vs
results/_r447bma_rsqr_w12_probe_facts.json when present (r447
determinism cross-check law).

Exclusion law (prereg sec.1, FIFTEEN-tuple cell key=(template,
params, axis_config, initial_stop, gate, vol, yang, vconf, streak,
tstate, amp, mom, std, rsqr), TWELVE judged + TWELVE screen
real-read source faces, exact already-judged key, rsqr=none face
only: prior-wave keys lacking the rsqr axis are rsqr=none completed
(semantic-identity match; generate-time real-read; W11-JUDGE landed
2026-09-30 01:47:40 = TWELFTH source, fifth full-declare window);
rsqr in {rsqr20_hi, rsqr10_hi} = new-syntax legal cells (never
excluded).

Slice plan (W3-W11 single-writer precedent; wave ticket
T-2026-09-30-124 opened+claimed bm-b r444 same freeze commit per
O-1730 immediate law):
  - Slice-A (this draft, bm-b r445 surgeon
    results/_r445bmb_w12_surgeon.py): mechanical identity surgery +
    rsqr overlay layer (a158 verbatim import) + RSQR_ANCHOR
    programmatic generation + grammar/Sobol/exclusion/mask/curve/
    null/generate/screen/judge legs rewiring + std import face from
    tl11 + py_compile gate.  Draft name
    results/_r445bmb_w12_runner_draft.py -- NOT the formal runner
    (runner_exists gate must not fire on a partial build).
  - Slice-B (next): selftest anchor review (W12 warmup 120/
    decidable 3,363/341/332 + slope 213/128 + 124/388 cell faces +
    core48 spread), grammar serialization + sha16 pin, formal-name
    move, catalog runner_exists arm, MSG declaration, GENERATE pool
    entry.
"""
'''


IDENTITY_CONSTANTS = '''WAVE = "TRIAL_LABOR_W12"
PREREG = "research/TRIAL_LABOR_W12_PREREG.md"
CUTOFF = tl1.CUTOFF                      # "2026-09-22" (P-5C binding, sec.2)
SEED_GEN = SEED_REGISTRY["trial_labor_w12_gen"]        # 20320500
SEED_NULL = SEED_REGISTRY["trial_labor_w12_scrnull"]  # 20321000
SEED_UNC = SEED_REGISTRY["trial_labor_w12_unc"]        # 20321500
N_A = 500          # family A raw draws (sec.3: 6 templates round-robin)
N_B = 4500         # family B raw draws (machinery round-robin)
K_NULLS = 200       # screen null family size (sec.3; frozen)
RES_DIR = os.path.join(tl1.PATHS.results_dir, "trial_labor_w12")
GRAMMAR_FILE = os.path.join(RES_DIR, "w12_grammar.json")
CANDIDATES_FILE = os.path.join(RES_DIR, "w12_candidates.json")
GRAMMAR_LEDGER = tl1.GRAMMAR_LEDGER
SCREEN_FILE = os.path.join(RES_DIR, "w12_screen.json")
SCREEN_CSV = os.path.join(RES_DIR, "w12_screen_cells.csv")
JUDGE_FILE = os.path.join(RES_DIR, "w12_judge.json")
INTAKE_FILE = os.path.join(RES_DIR, "w12_intake.json")
PREP_FILE = os.path.join(RES_DIR, "prep_state.json")
JUDGE_STATE_FILE = os.path.join(RES_DIR, "judge_state.json")
CKPT_DIR = os.path.join(RES_DIR, "checkpoint")
SCREEN_BATCH = "TRIAL_LAB_W12_SCREEN"   # prereg sec.0 ledger literal
JUDGE_BATCH = "TRIAL_LAB_W12_JUDGE"     # prereg sec.0 ledger literal
W6M = tl1.WINDOWS["6m"]                # leg-L 6m screen window (126 td)
FROZEN_SHA16 = None   # pinned at Slice-B serialization (W11 r442-close precedent; selftest L6g fail-closed verifies pin == built sha)

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
}

# tstate axis (W8 frozen face, imported verbatim)
AXIS_TSTATE = tl8.AXIS_TSTATE           # ["none","deep_pullback","oversold_rsv"]
TSTATE_MEMBER = tl8.TSTATE_MEMBER       # "510300"

# amplitude-confirmation axis (W9 frozen face, imported verbatim from
# tl9 -- import-face law; the W12 runner re-derives ZERO mom machinery)
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
# AMP_SPEC carried from tl9.build_grammar_w9() inside build_grammar_w12
# (import-time grammar-chain build is heavy; lazy face = build-time read)

# momentum-confirmation axis (W10 frozen face, imported verbatim from
# tl10 -- import-face law; the W12 runner re-derives ZERO mom
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
# build_grammar_w12 (import-time grammar-chain build is heavy; lazy
# face = build-time read)

# grammar sha16 (W7 lineage import; zero re-implementation)
def _grammar_sha16(grammar):
    """Grammar sha16 (W7 lineage import; zero re-implementation)."""
    return tl7._grammar_sha16(grammar)

# high-dispersion STD axis (W11 frozen face, imported verbatim from
# tl11 -- import-face law; the W12 runner re-derives ZERO std
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
# build_grammar_w12 (import-time grammar-chain build is heavy; lazy
# face = build-time read)

# trend-fit-quality RSQR axis (prereg sec.3 NEW W12 frozen layer,
# three-value axis, W4-VOL/W11-STD precedent)
AXIS_RSQR = ["none", "rsqr20_hi", "rsqr10_hi"]
AXIS_COMBOS = tl11.AXIS_COMBOS * len(AXIS_RSQR)  # 31,352,832 * 3 = 94,058,496
RSQR_MEMBER = "510300"          # core48 member (prereg sec.2 probe fact)
PROBE_FACTS_FILE = os.path.join("results",
                                "_r447bma_rsqr_w12_probe_facts.json")
RSQR_SPEC = {
    "member": RSQR_MEMBER,
    "series": "r447 probe verbatim / A158-TSGATE-P1 frozen RSQR "
              "construction via the frozen in-repo runner import "
              "(zero-invention law; scripts/a158_tsgate_probe.py "
              "alpha158_factors): signal-day-d close info set on "
              "the member face",
    "rsqr20": 'F["RSQR20"] = rolling OLS r^2 of close vs t=1..d, '
              "20-day window (qlib expanding-warmup semantics + "
              "flat-price guard std~0->NaN)",
    "rsqr10": 'F["RSQR10"] = same construction, 10-day window',
    "q90_ref": "q90_ref = f.rolling(GATE_WIN=252, "
               "min_periods=GATE_MINP=120).quantile(0.90) "
               "(own-trailing 252-observation top-decile reference; "
               "GATE_WIN/GATE_MINP constants same-source frozen-"
               "runner import)",
    "rsqr_hi": "f > q90_ref (trend-fit quality entering its own top "
               "decile = clean directional-trend state; time-series "
               "momentum / trend-continuation folklore + fitted-"
               "trend statistical basis; A158-TSGATE-P1 48-PASS pool "
               "STD-next top family RSQR20_q90 OOS med_t +1.520 / "
               "RSQR10_q90 +1.258 + GATE-RECHECK five-member net "
               "median +0.00838/+0.01156 CONFIRM = LONG anchor)",
    "none": "no gate (W11 semantic baseline face)",
    "direction_blind": "R^2 is sign-blind -- a clean DOWN-trend "
                       "fits as well as an UP-trend; slope-sign "
                       "split among rsqr20-open days 213 up / 128 "
                       "down (probe face); direction conditioning "
                       "lives in the burned axes GATE/YANG/STREAK/"
                       "MOM (prereg sec.2 honesty disclosure (e))",
    "grind_face": "rsqr-open-and-calm 186 days forward-20d +0.33% "
                  "vs rsqr-open-and-wild 122 days +3.19% (Welch "
                  "t=-3.98) -- clean-grind increment face is a drag "
                  "face (prereg sec.2 honesty disclosure (b)); the "
                  "VOL axis co-conditioning decomposes this inside "
                  "the cell grid",
    "info_set": "signal-day d close; entry fills d+1 open (T+1 "
                "causal, same info set as GATE/VOL/YANG/VCONF/"
                "STREAK/TSTATE/AMP/MOM/STD, zero lookahead)",
    "warmup": "120-bar warmup window gate-closed honest (k=1 "
              "undefined -> f valid from bar-idx 1: k=2 two-point "
              "fit; q90_ref min_periods 120 -> first decidable "
              "bar-idx == 120, fail-closed assertion == STD family "
              "warmup)",
    "engine_note": "entry-permittance only (effective signal "
                   "zeroed, MSG-0440 E1-mapping primitive; exit "
                   "logic zero change; engine/exit_rules.py zero "
                   "touch)",
    "nan_artifact_note": "NaN comparisons (f > q90_ref) yield "
                         "False NOT decidable (pit-95 batch-95 law; "
                         "the decidable face derives from the "
                         "underlying values notna; the naive "
                         "comparison bool face masquerades warmup "
                         "bars as rsqr_closed -- BANNED at the mask "
                         "level)",
    "adjacency_note": "nearest burned neighbor = W11 STD (both "
                      "trend-state family): rsqr-open-and-std-"
                      "closed 207 days = fit-quality-without-"
                      "dispersion divergence face (construction "
                      "distinct: fit QUALITY R^2 direction-blind "
                      "vs dispersion LEVEL std/close incl. drift; "
                      "39.3%/34.27% mutual-open, D6 max|corr| audit "
                      "column face at intake); W4 VOL 60.39% "
                      "overlap + 122 wild-side non-empty; W9 AMP "
                      "62.17% + 129 narrow-only; W10 MOM 19.7% "
                      "near-orthogonal; collapsed-neighbor precedent "
                      "VSTD20_q20 (98.5% + 11-day empty set, r234 "
                      "DEMOTE) is NOT this face (probe cross-check "
                      "law)",
    "composition_order": "signal -> filter -> timing -> GATE -> "
                         "VOL -> YANG -> VCONF -> STREAK -> TSTATE "
                         "-> AMP -> MOM -> STD -> RSQR -> "
                         "initial-stop (a rsqr-blocked signal "
                         "never arms a stop; W11 order extended, "
                         "prereg sec.3 fifteen-tuple order R/X/S/T/"
                         "STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/"
                         "AMP/MOM/STD/RSQR)",
}
'''


RSQR_LAYER = '''# ------------------------------------------------------------- rsqr overlay layer
def _rsqr_faces_raw(prices: dict):
    """r447-probe-verbatim RSQR face computation (single computation
    site for both window faces + decidable + raw values + slope sign;
    A158-TSGATE-P1 frozen RSQR20_q90/RSQR10_q90 construction via the
    FROZEN in-repo runner import -- import a158_tsgate_probe;
    zero-invention law): F = a158.alpha158_factors(member frame);
    rsqr20 = F["RSQR20"] (rolling OLS r^2 of close vs t=1..d, qlib
    expanding-warmup semantics + flat-price guard std~0->NaN);
    q90_ref = rsqr20.rolling(a158.GATE_WIN, min_periods=
    a158.GATE_MINP).quantile(0.90); open_perm = rsqr20 > q90_ref
    (comparison NaN->False); decidable derives from the underlying
    values notna (pit-95 batch-95 law).  rsqr10 same face on the
    10-bar window.  Returns (open20, dec20, meta, rsqr20, q90_ref,
    open10, dec10, rsqr10, q90_ref10, beta20); deterministic pure
    function of the (cutoff-truncated) panel."""
    df = prices[RSQR_MEMBER].sort_index()
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
    rsqr20, rsqr10, beta20 = F["RSQR20"], F["RSQR10"], F["BETA20"]
    q90_ref = rsqr20.rolling(a158.GATE_WIN,
                             min_periods=a158.GATE_MINP).quantile(0.90)
    dec = rsqr20.notna() & q90_ref.notna()  # underlying notna (pit-95)
    open_perm = (rsqr20 > q90_ref)           # comparison face: NaN->False
    q90_ref10 = rsqr10.rolling(a158.GATE_WIN,
                               min_periods=a158.GATE_MINP).quantile(0.90)
    dec10 = rsqr10.notna() & q90_ref10.notna()
    open10 = (rsqr10 > q90_ref10)
    n = len(rsqr20)

    def _first_true(s):
        arr = s.fillna(False).astype(bool).values
        nz = np.flatnonzero(arr)
        return int(nz[0]) if len(nz) else None

    dec_n = int(dec.sum())
    open_n = int((open_perm & dec).sum())
    closed_n = int(((~open_perm) & dec).sum())
    meta = {"n_bars": int(n),
            "warmup_gate_closed_bars": _first_true(dec),
            "first_decidable_bar_idx": _first_true(dec),
            "decidable_days": dec_n,
            "open_days": open_n, "closed_days": closed_n,
            "open_rate_on_decidable":
            (round(float(open_n / dec_n), 4) if dec_n else None),
            "rsqr10_decidable_days": int(dec10.sum()),
            "rsqr10_open_days": int((open10 & dec10).sum()),
            "na_window_bars": 120,   # the gate family's warmup
            }
    return open_perm, dec, meta, rsqr20, q90_ref, open10, dec10, \\
        rsqr10, q90_ref10, beta20


def rsqr_state_series(prices: dict):
    """Frozen RSQR spec (prereg sec.2/3): member 510300 signal-day
    info set -- rsqr20 open perm + decidable face + the rsqr10
    faces.  Returns (open20, dec20, meta, open10, dec10): boolean
    Series on the member's own date index + structural meta + the
    10-bar faces.  Deterministic pure function of the (cutoff-
    truncated) panel."""
    o20, d20, meta, _r20, _q20, o10, d10, _r10, _q10, _b20 = \\
        _rsqr_faces_raw(prices)
    return o20, d20, meta, o10, d10


def _rsqr_face_full():
    """Frozen sec.2 RSQR-series face (r447 probe basis): the
    git-tracked raw full-history member file data/daily/
    sh510300.csv (open + high + low + close + volume columns),
    truncated at the evidence cutoff.  (tl8._tstate_face_full
    loading caliber reused verbatim -- same member, same columns,
    same cutoff law; import-face law.)"""
    return tl8._tstate_face_full()


def _rsqr_state_full():
    """Canonical full-face rsqr_state with the frozen probe anchors
    asserted (prereg sec.2 G-RSQR fail-closed): n_bars == 3,483;
    first-decidable == 120 / decidable == 3,363 / open == 341 /
    closed == 3,022 / rsqr10 decidable == 3,363 / rsqr10 open ==
    332 exact; slope-sign split 213 up / 128 down (BETA20 same
    frozen runner); cross reproduction counts {streak up 844/down
    817/neither 1820, mad60 383, rsv60 632, wide 1718/narrow 1746/
    zero-range 0} + cross lower bounds {mad60 59, rsv60 89,
    down_streak 67, wide 212, mom 66, std20 134, rsqr10-both-open
    81}; NINE-gate (gate x vol x yang x vconf x streak x tstate x
    amp x std20 x rsqr20) 512 open-window cells 124-non-empty with
    the exact frozen 388-empty name list (probe range 1-41;
    all-decidable 3,305) + exact per-cell cross-check vs the
    git-tracked probe facts file when present; extreme-day gate
    states exact (0/7 rsqr-open both windows -- fit gate
    structurally closed on crisis days; rsqr20 values at probe
    6-decimal rounding, ratios at 3-decimal).  Returns
    (rsqr_state, err); err is a one-line honest refusal reason
    when not None."""
    face = _rsqr_face_full()
    if face is None:
        return None, (f"raw member face data/daily/sh{RSQR_MEMBER}.csv "
                      f"absent/open-high-low-close-volume columns "
                      f"missing or truncated tail != cutoff {CUTOFF}")
    open20, dec, meta, rsqr20, q90_ref, open10, dec10, rsqr10, \\
        q90_ref10, beta20 = _rsqr_faces_raw(face)
    a = RSQR_ANCHOR
    if (meta.get("n_bars") != a["n_bars"]
            or meta["first_decidable_bar_idx"]
            != a["first_decidable_bar_idx"]
            or meta["decidable_days"] != a["decidable_days"]
            or meta["open_days"] != a["open_days"]
            or meta["closed_days"] != a["closed_days"]
            or meta["rsqr10_decidable_days"]
            != a["rsqr10_decidable_days"]
            or meta["rsqr10_open_days"] != a["rsqr10_open_days"]):
        return None, (f"G-RSQR core anchors {meta} != probe "
                      f"{{n 3483, warmup 120, decidable 3363, open "
                      f"341, closed 3022, rsqr10 dec 3363 open "
                      f"332}}")
    # slope-sign split (direction-blind disclosure face; prereg
    # sec.2 (e))
    m_open = open20 & dec & beta20.notna()
    up_days = int((m_open & (beta20 > 0)).sum())
    dn_days = int((m_open & (beta20 <= 0)).sum())
    if (up_days != a["slope_sign_split"]["up_slope_days"]
            or dn_days != a["slope_sign_split"]["down_slope_days"]):
        return None, (f"G-RSQR slope-sign split drift {up_days}/"
                      f"{dn_days} != probe "
                      f"{a['slope_sign_split']['up_slope_days']}/"
                      f"{a['slope_sign_split']['down_slope_days']}")
    # ---- r447 probe basis faces VERBATIM (cross + nine-gate grid)
    df = face[RSQR_MEMBER]
    close = df["close"].astype(float).sort_index()
    o_ = df["open"].astype(float).reindex(close.index)
    h_ = df["high"].astype(float).reindex(close.index)
    l_ = df["low"].astype(float).reindex(close.index)
    v_ = df["volume"].astype(float).reindex(close.index)
    amp = (h_ - l_) / close
    med20amp = amp.rolling(20, min_periods=20).median()
    amp_known = med20amp.notna()
    wide_face = (amp > med20amp) & amp_known
    up1 = close > close.shift(1)
    up2 = close.shift(1) > close.shift(2)
    dn1 = close < close.shift(1)
    dn2 = close.shift(1) < close.shift(2)
    judge = close.shift(2).notna()      # bars 0-1 warmup gate-closed
    up_st = judge & (up1 & up2).fillna(False)
    dn_st = judge & (dn1 & dn2).fillna(False)
    neither_st = judge & ~((up1 & up2).fillna(False)
                           | (dn1 & dn2).fillna(False))
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
    # reproduction counts (W7/W8/W9 cross-probe determinism law)
    sar = a["streak_anchor_reproduction"]
    if (int(up_st.sum()) != sar["up_streak_days"]
            or int(dn_st.sum()) != sar["down_streak_days"]
            or int(neither_st.sum()) != sar["neither_days"]):
        return None, (f"G-RSQR streak-anchor reproduction broken "
                      f"up {int(up_st.sum())}/down {int(dn_st.sum())}/"
                      f"neither {int(neither_st.sum())} != {sar}")
    tar = a["tstate_anchor_reproduction"]
    if (int((mad_q10 & dec_mad).sum()) != tar["mad60_gate_true_days"]
            or int((rsv_low & dec_rsv).sum())
            != tar["rsv60_gate_true_days"]):
        return None, (f"G-RSQR tstate-anchor reproduction broken "
                      f"mad60 {int((mad_q10 & dec_mad).sum())}/"
                      f"rsv60 {int((rsv_low & dec_rsv).sum())} != "
                      f"{tar}")
    aar = a["amp_anchor_reproduction"]
    if (int(wide_face.sum()) != aar["wide_days"]
            or int((amp_known & ~wide_face).sum()) != aar["narrow_days"]
            or int((h_ == l_).sum()) != aar["zero_range_rows"]):
        return None, (f"G-RSQR amp-anchor reproduction broken "
                      f"wide {int(wide_face.sum())}/narrow "
                      f"{int((amp_known & ~wide_face).sum())}/"
                      f"zero-range {int((h_ == l_).sum())} != {aar}")
    # std faces VERBATIM from the W11 frozen machinery (tl11 import
    # face; A158 STD20_q90/STD10_q90 construction)
    s20o, s20d, _s20meta, _s20, _s20q, s10o, s10d, _s10, _s10q = \\
        _std_series_raw(face)
    dec_s20 = s20d
    std20_open = s20o
    # mom faces VERBATIM from the W10 frozen machinery (tl10 import
    # face) for the mom cross lower bound
    m_open_face, m_dec, _mmeta = _mom_series_raw(face)[:3]
    # cross lower bounds on the r447 probe basis VERBATIM
    cross = {
        "mad60_and_rsqr20":
            int((mad_q10 & open20 & (dec & dec_mad)).sum()),
        "rsv60_and_rsqr20":
            int((rsv_low & open20 & (dec & dec_rsv)).sum()),
        "down_streak_and_rsqr20":
            int((dn_st & open20 & (dec & judge)).sum()),
        "wide_and_rsqr20":
            int((wide_face & open20 & (dec & amp_known)).sum()),
        "mom_and_rsqr20":
            int((m_open_face & open20 & (dec & m_dec)).sum()),
        "std20_and_rsqr20":
            int((std20_open & open20 & (dec & dec_s20)).sum()),
        "rsqr20_vs_rsqr10_both_open":
            int((open10 & open20 & (dec & dec10)).sum()),
    }
    for k, lbv in a["cross_lower_bounds"].items():
        if k in cross and cross[k] < lbv:
            return None, (f"G-RSQR cross lower bound broken "
                          f"{k}={cross[k]} < {lbv}")
    # NINE-gate 512-cell cross on the r447 probe basis VERBATIM
    # (m9 = dec_rsqr20 & bull/calm notna & amp_known & streak-
    # decidable & dec_mad & dec_rsv & dec_s20 == 3,305 days;
    # gate/vol/yang/vconf faces are NaN->False comparison faces)
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
    narrow_face = (amp <= med20amp) & amp_known
    rsqr_open_face = open20 & dec
    rsqr_closed_face = (~open20) & dec
    m9 = dec & bull.notna() & calm.notna() & amp_known & judge \\
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
                                    for rname, rr in (
                                            ("rsqr20_open",
                                             rsqr_open_face),
                                            ("rsqr20_closed",
                                             rsqr_closed_face)):
                                        cells[f"{bname}|{vname}|"
                                              f"{yname}|{sname}|"
                                              f"{kname}|{tname}|"
                                              f"{aname}|{sdname}|"
                                              f"{rname}"] = \\
                                              int((m9 & b & vv & y
                                                 & s & k & t & aa
                                                 & sd & rr).sum())
    empty = sorted(k for k, n_ in cells.items() if n_ <= 0)
    nonzero = [x for x in cells.values() if x > 0]
    if (len(cells) != 512
            or len(nonzero)
            != a["nine_gate_512cells_nonzero_count"]
            or len(empty) != a["nine_gate_512cells_empty_count"]
            or empty != sorted(a["nine_gate_512cells_empty"])
            or min(nonzero) < a["nine_gate_512cells_min_nonzero"]
            or max(cells.values()) > a["nine_gate_512cells_max"]
            or int(m9.sum())
            != a["nine_gate_all_decidable_days"]):
        return None, (f"G-RSQR nine-gate 512-cell cross drift "
                      f"(nonzero {len(nonzero)}/124, empty "
                      f"{len(empty)}/388, min {min(nonzero)}, max "
                      f"{max(cells.values())}, all-decidable "
                      f"{int(m9.sum())}/3305)")
    # exact per-cell cross-check vs the git-tracked probe facts file
    # (r447 determinism cross-check law; skip-face = file absent,
    # header counts above still binding)
    if os.path.exists(PROBE_FACTS_FILE):
        pf_ = json.load(open(PROBE_FACTS_FILE, encoding="utf-8"))
        pcells = pf_.get("nine_gate_cells", {})
        drift = [f"{k}: {cells.get(k)} != {v_}"
                 for k, v_ in pcells.items() if cells.get(k) != v_]
        if pcells and drift:
            return None, (f"G-RSQR probe-facts per-cell cross-check "
                          f"drift: {drift[:3]}")
    # extreme-day gate states (frozen face; rsqr20 values at probe
    # 6-decimal rounding + ratios at 3-decimal; 0/7 rsqr-open both
    # windows = fit gate structurally closed on crisis days)
    for dstr, want in a["extreme_days"].items():
        ts = pd.Timestamp(dstr)
        if ts not in close.index:
            return None, f"G-RSQR extreme day {dstr} absent from face"
        rv20 = rsqr20.loc[ts]
        if pd.isna(rv20):
            return None, f"G-RSQR extreme day {dstr} rsqr20 NaN"
        got_open = bool(open20.loc[ts]) if bool(dec.loc[ts]) else None
        got_open10 = (bool(open10.loc[ts]) if bool(dec10.loc[ts])
                      else None)
        got_val = round(float(rv20), 6)
        qr = q90_ref.loc[ts]
        got_ratio = (None if pd.isna(qr) or qr == 0
                     else round(float(rv20 / qr), 3))
        got_std20 = (bool(std20_open.loc[ts])
                     if bool(dec_s20.loc[ts]) else None)
        got_slope = None
        if bool(dec.loc[ts]) and not pd.isna(beta20.loc[ts]):
            got_slope = "up" if beta20.loc[ts] > 0 else "down"
        if (got_open != want["rsqr20_open"]
                or got_open10 != want["rsqr10_open"]
                or abs(got_val - want["rsqr20_value"]) > 5.01e-6
                or got_slope != want["slope_sign"]
                or got_std20 != want["std20_open"]
                or got_ratio is None
                or abs(got_ratio - want["rsqr20_over_q90ref"])
                > 5.01e-4):
            return None, (f"G-RSQR extreme day {dstr} drift: open "
                          f"{got_open}/{want['rsqr20_open']}, "
                          f"open10 {got_open10}/"
                          f"{want['rsqr10_open']}, rsqr20 "
                          f"{got_val}/{want['rsqr20_value']}, "
                          f"ratio {got_ratio}/"
                          f"{want['rsqr20_over_q90ref']}, slope "
                          f"{got_slope}/{want['slope_sign']}, "
                          f"std20 {got_std20}/"
                          f"{want['std20_open']}")
    meta = dict(meta)
    meta["slope_sign_split"] = {"up_slope_days": up_days,
                                "down_slope_days": dn_days}
    meta["cross_lower_bounds"] = cross
    meta["nine_gate_512cells"] = cells
    meta["nine_gate_512cells_empty"] = empty
    meta["nine_gate_all_decidable_days"] = int(m9.sum())
    meta["streak_anchor"] = {k: sar[k] for k in
                             ("up_streak_days", "down_streak_days",
                              "neither_days")}
    meta["tstate_anchor"] = dict(tar)
    meta["amp_anchor"] = dict(aar)
    return (open20, dec, meta, open10, dec10), None


def rsqr_zero_mask(mask: pd.DataFrame, rsqr_key: str, rsqr_state):
    """Grammar-layer rsqr entry gate (prereg sec.3 trend-fit-quality
    face; E1-mapping primitive): off-face signal days -> effective
    signal zeroed (entry blocked; engine-native signal-off exit
    semantics -- the same primitive every cell uses when its own
    signal turns off; zero engine touch).  rsqr=none = W11
    semantic baseline (identity).  The keep face derives from the
    DECIDABLE face (pit-95 law): rsqr20_hi keeps rsqr20-open AND
    decidable; rsqr10_hi keeps rsqr10-open AND decidable -- the
    naive comparison bool face alone would masquerade warmup bars
    as rsqr_closed (BANNED).  Member dates missing from the mask
    index -> rsqr-closed (conservative reindex law,
    tl3/tl4/tl5/tl6/tl7/tl8/tl9/tl10/tl11 gate caliber)."""
    if rsqr_key == "none":
        return mask
    open20, dec20, _meta, open10, dec10 = rsqr_state
    if rsqr_key == "rsqr20_hi":
        keep = (open20.reindex(mask.index).fillna(False).astype(int)
                & dec20.reindex(mask.index).fillna(False).astype(int))
    elif rsqr_key == "rsqr10_hi":
        keep = (open10.reindex(mask.index).fillna(False).astype(int)
                & dec10.reindex(mask.index).fillna(False).astype(int))
    else:
        raise ValueError(f"unknown rsqr_key {rsqr_key}")
    return mask.mul(keep, axis=0)


def _rsqr_structure_pass(rsqr_meta) -> bool:
    """Series-structure invariants on every panel face (fail-closed):
    120-bar warmup -- first-decidable + decidable partitions n_bars;
    open <= decidable and closed <= decidable.  A face shorter than
    the warmup (first-decidable None) honestly refuses."""
    if not isinstance(rsqr_meta, dict):
        return False
    n = rsqr_meta.get("n_bars", -1)
    fv = rsqr_meta.get("first_decidable_bar_idx")
    return (fv is not None
            and fv + rsqr_meta.get("decidable_days", -10**9) == n
            and rsqr_meta.get("open_days", -1)
            <= rsqr_meta.get("decidable_days", -1)
            and rsqr_meta.get("closed_days", -1)
            <= rsqr_meta.get("decidable_days", -1))

'''


def main() -> int:
    src = open(SRC, encoding="utf-8").read()
    steps = []

    # ---- 1. docstring replacement (W12 identity)
    ds, a, b = segment(src, '"""TRIAL_LABOR_W11 runner', '\n"""\n',
                       include_start=True, include_end=True)
    src = src[:a] + W12_DOCSTRING + src[b:]
    steps.append("docstring: W12 identity")

    # ---- 2. imports: + tl11 + a158 frozen runner
    src = sub1(src,
               "import trial_labor_w10 as tl10  # mom overlay + "
               "thirteen-tuple machinery\nfrom science_gates import",
               "import trial_labor_w10 as tl10  # mom overlay + "
               "thirteen-tuple machinery\n"
               "import trial_labor_w11 as tl11  # std overlay + "
               "fourteen-tuple machinery\n"
               "import a158_tsgate_probe as a158  # frozen A158 "
               "runner (RSQR20/RSQR10/BETA20 verbatim import)\n"
               "from science_gates import",
               "imports")
    steps.append("imports: + tl11 + a158 (RSQR verbatim source)")

    # ---- 3. identity constants block (WAVE .. mom import face)
    _, a, b = segment(src, 'WAVE = "TRIAL_LABOR_W11"',
                      'AXIS_STD = ["none", "std20_hi", "std10_hi"]',
                      include_start=True, include_end=False)
    src = src[:a] + IDENTITY_CONSTANTS + src[b:]
    steps.append("constants: W12 identity + std import face (tl11) + "
                 "AXIS_RSQR + RSQR_SPEC")

    # ---- 4. RSQR_ANCHOR (programmatic; replaces STD_SPEC+STD_ANCHOR)
    _, a, b = segment(src, 'AXIS_STD = ["none", "std20_hi", "std10_hi"]',
                      'def _std_series_raw(prices: dict):',
                      include_start=False, include_end=False)
    anchor = build_rsqr_anchor()
    anchor_json = json.dumps(anchor, ensure_ascii=False, indent=1,
                             sort_keys=False)
    anchor_json = anchor_json.replace(": false", ": False")
    anchor_json = anchor_json.replace(": true", ": True")
    anchor_json = anchor_json.replace(": null", ": None")
    anchor_lit = "\nRSQR_ANCHOR = " + anchor_json + "\n\n\n"
    src = src[:a] + anchor_lit + src[b:]
    steps.append("RSQR_ANCHOR: programmatic from probe facts "
                 "(124/388 cells, 3363/341/332, slope 213/128)")

    # ---- 5. rsqr overlay layer (replaces the std overlay functions)
    _, a, b = segment(src, 'def _std_series_raw(prices: dict):',
                      '# ------------------------------------------------------------ grammar build',
                      include_start=True, include_end=False)
    src = src[:a] + RSQR_LAYER + src[b:]
    steps.append("rsqr overlay layer: a158-verbatim functions "
                 "(three-value axis) + std/mom import faces kept")

    # ---- 6. grammar build leg surgery
    gb, a, b = segment(src, 'def build_grammar_w11():',
                       '# ------------------------------------------------------------ Sobol draw leg',
                       include_start=True, include_end=False)
    gb = gb.replace("build_grammar_w11", "build_grammar_w12")
    gb = sub1(gb,
              "    \"\"\"tl10 grammar extended with the NEW std axis "
              "+ W11 seeds/counts\n    (frozen face).  FOURTEEN-tuple "
              "axes R/X/S/T/STOP/GATE/VOL/YANG/\n    VCONF/STREAK/"
              "TSTATE/AMP/MOM/STD = 31,352,832 axis combos.",
              "    \"\"\"tl11 grammar extended with the NEW rsqr "
              "axis + W12 seeds/counts\n    (frozen face).  "
              "FIFTEEN-tuple axes R/X/S/T/STOP/GATE/VOL/YANG/VCONF/"
              "STREAK/TSTATE/AMP/MOM/STD/RSQR = 94,058,496 axis "
              "combos.", "grammar docstring head")
    gb = sub1(gb,
              "    Exclusion law (prereg sec.1): exact already-judged "
              "cells are\n    excluded on the std=none face only; "
              "all prior-wave lineage keys\n    are std=none "
              "completed (W1 4-tuple + stop/gate/vol/yang/vconf/\n"
              "    streak/tstate/amp/mom/std none; W2 5-tuple + "
              "gate/vol/yang/vconf/\n    streak/tstate/amp/mom/std "
              "none; W3 6-tuple + vol/yang/vconf/\n    streak/tstate/"
              "amp/mom/std none; W4 7-tuple + yang/vconf/streak/\n"
              "    tstate/amp/mom/std none; W5 8-tuple + vconf/"
              "streak/tstate/amp/\n    mom/std none; W6 9-tuple + "
              "streak/tstate/amp/mom/std none; W7\n    10-tuple + "
              "tstate/amp/mom/std none; W8 11-tuple + amp/mom/std\n"
              "    none; W9 12-tuple + mom/std none; W10 13-tuple + "
              "std none; MASS\n    via the declared translation); "
              "std in {std20_hi, std10_hi}\n    faces = new-syntax "
              "legal cells (never excluded).\"\"\"",
              "    Exclusion law (prereg sec.1): exact already-judged "
              "cells are\n    excluded on the rsqr=none face only; "
              "all prior-wave lineage keys\n    are rsqr=none "
              "completed (W1 4-tuple + stop/gate/vol/yang/vconf/\n"
              "    streak/tstate/amp/mom/std/rsqr none; W2 5-tuple + "
              "gate/vol/yang/vconf/\n    streak/tstate/amp/mom/std/"
              "rsqr none; W3 6-tuple + vol/yang/vconf/\n    streak/"
              "tstate/amp/mom/std/rsqr none; W4 7-tuple + yang/vconf/"
              "streak/\n    tstate/amp/mom/std/rsqr none; W5 8-tuple "
              "+ vconf/streak/tstate/amp/\n    mom/std/rsqr none; "
              "W6 9-tuple + streak/tstate/amp/mom/std/rsqr none; "
              "W7\n    10-tuple + tstate/amp/mom/std/rsqr none; W8 "
              "11-tuple + amp/mom/std/\n    rsqr none; W9 12-tuple + "
              "mom/std/rsqr none; W10 13-tuple +\n    std/rsqr none; "
              "W11 14-tuple + rsqr none; MASS via the declared\n"
              "    translation); rsqr in {rsqr20_hi, rsqr10_hi} "
              "faces = new-syntax\n    legal cells (never "
              "excluded).\"\"\"", "grammar exclusion docstring")
    gb = sub1(gb,
              '    g10 = tl10.build_grammar_w10()      # frozen W10 '
              'machinery face',
              '    g11 = tl11.build_grammar_w11()    # frozen W11 '
              'machinery face', "g11 base")
    gb = sub1(gb,
              '    for e in g10["exclusion"]["stop_gate_vol_yang_'
              'vconf_streak_tstate_amp_mom_none_face"]:',
              '    for e in g11["exclusion"]["stop_gate_vol_yang_'
              'vconf_streak_tstate_amp_mom_std_none_face"]:',
              "exclusion face source")
    gb = sub1(gb,
              '                     "face": "stop-gate-vol-yang-'
              'vconf-streak-"\n                             "tstate-'
              'amp-mom-std-none"})',
              '                     "face": "stop-gate-vol-yang-'
              'vconf-streak-"\n                             "tstate-'
              'amp-mom-std-rsqr-none"})', "excl face label")
    gb = sub1(gb, '"grammar_kind": "w11-std-gate-extended",',
              '"grammar_kind": "w12-rsqr-gate-extended",', "kind")
    gb = sub1(gb,
              '        "seeds": {"trial_labor_w11_gen": SEED_GEN,\n'
              '                  "trial_labor_w11_scrnull": '
              'SEED_NULL,\n                  "trial_labor_w11_unc": '
              'SEED_UNC,\n                  "derivation": '
              '"Sobol(seed=20317000+family_idx, "\n'
              '                                "scramble) param box + '
              'default_rng("\n                                '
              '"[20317000+family_idx, 7919]) FOURTEEN-"\n'
              '                                "tuple axis stream '
              'R/X/S/T/STOP/GATE/"\n'
              '                                "VOL/YANG/VCONF/STREAK/'
              'TSTATE/AMP/MOM/"\n                                "STD '
              '(prereg s.3; A idx 0-5, B idx "\n'
              '                                "6+slot; berth re-take '
              '20317000/"\n                                "20317500/'
              '20318000 per the draft "\n'
              '                                "clause-5 collision '
              'clause (20316000/"\n'
              '                                "20316500 collided with '
              'bm-a r445 "\n'
              '                                "A12-PREDCOND), W9 '
              'two-collision "\n'
              '                                "precedent; berths held '
              'at the freeze "\n'
              '                                "commit per R250 '
              'one-step law, bm-b "\n'
              '                                "r441 three-step '
              're-verify ALL GREEN "\n'
              '                                "no re-pick)"},',
              '        "seeds": {"trial_labor_w12_gen": SEED_GEN,\n'
              '                  "trial_labor_w12_scrnull": '
              'SEED_NULL,\n                  "trial_labor_w12_unc": '
              'SEED_UNC,\n                  "derivation": '
              '"Sobol(seed=20320500+family_idx, "\n'
              '                                "scramble) param box + '
              'default_rng("\n                                '
              '"[20320500+family_idx, 7919]) FIFTEEN-"\n'
              '                                "tuple axis stream '
              'R/X/S/T/STOP/GATE/"\n'
              '                                "VOL/YANG/VCONF/STREAK/'
              'TSTATE/AMP/MOM/"\n                                "STD/'
              'RSQR (prereg s.3; A idx 0-5, B idx "\n'
              '                                "6+slot; berths '
              '20320500/20321000/20321500 "\n'
              '                                "held at the freeze '
              'commit per R250 "\n'
              '                                "one-step law, bm-b '
              'r444 three-step "\n'
              '                                "re-verify ALL GREEN '
              'no re-pick; berth-open "\n'
              '                                "adoption of the bm-a '
              'r447 RSQR candidate "\n'
              '                                "whole package per '
              'AMP->W9/MOM->W10/STD->"\n'
              '                                "W11 lineage)"},',
              "seeds derivation")
    gb = sub1(gb, '"axes": {**g10["axes"], "std": AXIS_STD},',
              '"axes": {**g11["axes"], "rsqr": AXIS_RSQR},', "axes")
    for k in ("stop_formula", "stop_fill_mapping", "gate_spec",
              "vol_spec", "yang_spec", "vconf_spec", "streak_spec",
              "tstate_spec", "amp_spec", "families", "value_domains",
              "faces", "inventory_audit",
              "vol_anchor", "yang_anchor", "vconf_anchor",
              "streak_anchor", "tstate_anchor", "amp_anchor"):
        gb = gb.replace(f'g10["{k}"]', f'g11["{k}"]')
    gb = sub1(gb,
              '        "mom_spec": g10["mom_spec"],\n'
              '        "std_spec": STD_SPEC,',
              '        "mom_spec": g11["mom_spec"],\n'
              '        "std_spec": g11["std_spec"],\n'
              '        "rsqr_spec": RSQR_SPEC,', "specs")
    gb = sub1(gb,
              '        "mom_anchor": g10["mom_anchor"],\n'
              '        "std_anchor": STD_ANCHOR,',
              '        "mom_anchor": g11["mom_anchor"],\n'
              '        "std_anchor": g11["std_anchor"],\n'
              '        "rsqr_anchor": RSQR_ANCHOR,', "anchors")
    gb = sub1(gb,
              '"negative_priors": g10.get("negative_priors"),',
              '"negative_priors": g11.get("negative_priors"),',
              "negative priors")
    gb = sub1(gb,
              '            "stop_gate_vol_yang_vconf_streak_tstate_'
              'amp_mom_std_none_face":\n                excl,',
              '            "stop_gate_vol_yang_vconf_streak_tstate_'
              'amp_mom_std_rsqr_none_face":\n                excl,',
              "exclusion payload key")
    gb = sub1(gb,
              '            "sources": list(g10["exclusion"]'
              '["sources"])\n            + ["w10_screen.json '
              'survivors (generate-time)",\n               "w10_judge '
              'products (generate-time real-read "\n               '
              '"re-declare window; W10-JUDGE landed 2026-09-29 "\n'
              '               "20:31:29)"],',
              '            "sources": list(g11["exclusion"]'
              '["sources"])\n            + ["@@W11SRC1@@",\n'
              '               "@@W11SRC2@@"],', "sources W11")
    gb = sub1(gb,
              '            "note": "exclusion face = std=none only; '
              'prior-wave keys "\n                    "std=none-'
              'completed (semantic identity match); "\n'
              '                    "std in {std20_hi, std10_hi} = '
              'new-syntax legal "\n                    "cells '
              '(prereg sec.1)"},',
              '            "note": "exclusion face = rsqr=none only; '
              'prior-wave keys "\n                    "rsqr=none-'
              'completed (semantic identity match); "\n'
              '                    "rsqr in {rsqr20_hi, rsqr10_hi} = '
              'new-syntax legal "\n                    "cells '
              '(prereg sec.1)"},', "exclusion note")
    src = src[:a] + gb + src[b:]
    steps.append("grammar build: fifteen-tuple + rsqr axis + W11 "
                 "lineage")

    # ---- 7. Sobol draw leg surgery (fifteen-tuple stream)
    sob, a, b = segment(src, 'def draw_candidate_sobol_w11(',
                        '# ------------------------------------------------ exclusion (22 real-reads)',
                        include_start=True, include_end=False)
    sob = sob.replace("draw_candidate_sobol_w11", "draw_candidate_sobol_w12")
    sob = sub1(sob,
               "    to discrete domain indices + FOURTEEN-tuple axis "
               "stream\n    default_rng([SEED_GEN+family_idx, 7919]) "
               "in the frozen consumption\n    order R/X/S/T/STOP/GATE/"
               "VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD (the\n    "
               "first thirteen axis arrays are the W10-order stream "
               "VERBATIM --\n    order-frozen consumption law; the "
               "std leg appends AFTER mom,\n    zero disturbance).  "
               "Deterministic, zero band use.\"\"\"",
               "    to discrete domain indices + FIFTEEN-tuple axis "
               "stream\n    default_rng([SEED_GEN+family_idx, 7919]) "
               "in the frozen consumption\n    order R/X/S/T/STOP/GATE/"
               "VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR (the\n"
               "    first fourteen axis arrays are the W11-order "
               "stream VERBATIM --\n    order-frozen consumption law; "
               "the rsqr leg appends AFTER std,\n    zero "
               "disturbance).  Deterministic, zero band use.\"\"\"",
               "sobol docstring")
    sob = sub1(sob,
               "                  rng.integers(0, len(AXIS_STD), "
               "n_draws)))",
               "                  rng.integers(0, len(AXIS_STD), "
               "n_draws),\n                  rng.integers(0, "
               "len(AXIS_RSQR), n_draws)))", "sobol rng leg")
    sob = sub1(sob,
               "        r_, x_, s_, t_, st_, gt_, vt_, yg_, vc_, sk_, "
               "ts_, ap_, mo_, sd_ \\\n            = ax[i]",
               "        r_, x_, s_, t_, st_, gt_, vt_, yg_, vc_, sk_, "
               "ts_, ap_, mo_, sd_, \\\n            rq_ = ax[i]",
               "sobol unpack")
    sob = sub1(sob,
               "                           AXIS_MOM[mo_], "
               "AXIS_STD[sd_]],",
               "                           AXIS_MOM[mo_], "
               "AXIS_STD[sd_],\n                           "
               "AXIS_RSQR[rq_]],", "sobol axis list")
    src = src[:a] + sob + src[b:]
    steps.append("Sobol: fifteen-tuple stream (rsqr leg appends "
                 "after std)")

    # ---- 8. exclusion loader surgery
    ex, a, b = segment(src, 'def _load_exclusion_rows_w11(grammar):',
                       'def _excluded_w11(',
                       include_start=True, include_end=False)
    ex = ex.replace("_load_exclusion_rows_w11", "_load_exclusion_rows_w12")
    ex = sub1(ex, "Twenty-two real-read source faces",
              "Twenty-four real-read source faces", "loader count")
    ex = sub1(ex,
              "    face (prereg sec.1), all real-read at generate "
              "time.  All prior-wave\n    keys are padded to the W10 "
              "FOURTEEN-tuple with mom=none (semantic-\n    identity "
              "completion law).",
              "    face (prereg sec.1), all real-read at generate "
              "time.  All prior-wave\n    keys are padded to the W12 "
              "FIFTEEN-tuple with rsqr=none (semantic-identity\n    "
              "completion law).",
              "loader pad law")
    ex = sub1(ex,
              "    face (prereg sec.1), all real-read at generate "
              "time.",
              "    face (prereg sec.1), all real-read at generate "
              "time.", "noop check")
    ex = sub1(ex,
              "stop-gate-vol-yang-vconf-streak-tstate-amp-mom-std-none "
              "face (14-tuple at\n    build); 2-12 = W1/W2/MASS "
              "(declared tl3 translation)/W3/W4/W5/W6/\n    W7/W8/W9/"
              "W10 screen survivors -- W10 is NEW vs W10's own loader\n"
              "    (generate-time real-read; absent at build = zero "
              "rows honest per\n    prereg sec.1); 13-23 = judged "
              "products (w1_judge / MASS judged /\n    w2_judge / "
              "w3_judge / w4_judge / w5_judge / w6_judge / w7_judge /\n"
              "    w8_judge / w9_judge / w10_judge) -- generate-time "
              "real-read\n    re-declare window (declared-unavailable "
              "-> zero rows, no\n    fabrication).",
              "stop-gate-vol-yang-vconf-streak-tstate-amp-mom-std-"
              "rsqr-none face (15-tuple at\n    build); 2-13 = W1/W2/"
              "MASS (declared tl3 translation)/W3/W4/W5/W6/\n    W7/W8/"
              "W9/W10/W11 screen survivors -- W11 is NEW vs W11's own "
              "loader\n    (generate-time real-read; absent at build = "
              "zero rows honest per\n    prereg sec.1); 14-25 = judged "
              "products (w1_judge / MASS judged /\n    w2_judge / "
              "w3_judge / w4_judge / w5_judge / w6_judge / w7_judge /\n"
              "    w8_judge / w9_judge / w10_judge / w11_judge) -- "
              "generate-time real-read\n    re-declare window "
              "(declared-unavailable -> zero rows, no\n    "
              "fabrication).", "loader sources docstring")
    ex = sub1(ex,
              '    rows = list(grammar["exclusion"]\n'
              '                ["stop_gate_vol_yang_vconf_streak_'
              'tstate_amp_mom_std_none_face"])',
              '    rows = list(grammar["exclusion"]\n'
              '                ["stop_gate_vol_yang_vconf_streak_'
              'tstate_amp_mom_std_rsqr_none_face"])', "rows key")
    ex = sub1(ex,
              '    disc = {"grammar_stop_gate_vol_yang_vconf_streak_'
              'tstate_"\n            "amp_mom_std_none_rows": '
              'len(rows)}',
              '    disc = {"grammar_stop_gate_vol_yang_vconf_streak_'
              'tstate_"\n            "amp_mom_std_rsqr_none_rows": '
              'len(rows)}', "disc key")
    # screen pads +1 rsqr-none
    ex = sub1(ex, '["none"] * 10, "w1_screen_survivor")',
              '["none"] * 11, "w1_screen_survivor")', "w1 pad")
    ex = sub1(ex, '["none"] * 9, "w2_screen_survivor")',
              '["none"] * 10, "w2_screen_survivor")', "w2 pad")
    ex = sub1(ex, '["none"] * 8, "w3_screen_survivor")',
              '["none"] * 9, "w3_screen_survivor")', "w3 pad")
    ex = sub1(ex, '["none"] * 7, "w4_screen_survivor")',
              '["none"] * 8, "w4_screen_survivor")', "w4 pad")
    ex = sub1(ex, '["none"] * 6, "w5_screen_survivor")',
              '["none"] * 7, "w5_screen_survivor")', "w5 pad")
    ex = sub1(ex, '["none"] * 5, "w6_screen_survivor")',
              '["none"] * 6, "w6_screen_survivor")', "w6 pad")
    ex = sub1(ex, '["none"] * 4, "w7_screen_survivor")',
              '["none"] * 5, "w7_screen_survivor")', "w7 pad")
    ex = sub1(ex, '["none"] * 3, "w8_screen_survivor")',
              '["none"] * 4, "w8_screen_survivor")', "w8 pad")
    ex = sub1(ex, '["none"] * 2, "w9_screen_survivor")',
              '["none"] * 3, "w9_screen_survivor")', "w9 pad")
    ex = sub1(ex, '["none"], "w10_screen_survivor")',
              '["none"] * 2, "w10_screen_survivor")', "w10 pad")
    ex = sub1(ex,
              '                         "face": f"{tag}:stop-gate-'
              'vol-yang-vconf-"\n                                 '
              '"streak-tstate-amp-mom-std-none",',
              '                         "face": f"{tag}:stop-gate-'
              'vol-yang-vconf-"\n                                 '
              '"streak-tstate-amp-mom-std-rsqr-none",',
              "screen face label")
    ex = sub1(ex,
              '    disc["w10_screen_survivors"] = _screen_survivors(\n'
              '        tl10.SCREEN_FILE, tl10.CANDIDATES_FILE,\n'
              '        ["none"] * 2, "w10_screen_survivor")',
              '    disc["w10_screen_survivors"] = _screen_survivors(\n'
              '        tl10.SCREEN_FILE, tl10.CANDIDATES_FILE,\n'
              '        ["none"] * 2, "w10_screen_survivor")\n'
              '    disc["w11_screen_survivors"] = _screen_survivors(\n'
              '        tl11.SCREEN_FILE, tl11.CANDIDATES_FILE,\n'
              '        ["none"], "@@W11TAG1@@")', "w11 screen source")
    ex = sub1(ex,
              '                tr["axis"] = list(tr["axis"]) + '
              '["none"] * 8\n                tr["face"] = '
              '"mass_screen_survivor:translated-exact"',
              '                tr["axis"] = list(tr["axis"]) + '
              '["none"] * 9\n                tr["face"] = '
              '"mass_screen_survivor:translated-exact"',
              "mass screen pad")
    ex = sub1(ex,
              "    # sec.1/sec.9); absent -> declared-unavailable zero "
              "rows (freeze-time\n    # expectation per prereg sec.0 "
              "(d): W1/MASS/W2/W3/W4/W5/W6 judged\n    # landed; "
              "W7-JUDGE landed 2026-09-29 11:42:55; W8-JUDGE landed\n"
              "    # 2026-09-29 15:26:25; W9-JUDGE landed 2026-09-29 "
              "17:47:46;\n    # W10-JUDGE landed 2026-09-29 20:31:29 "
              "-- ELEVEN sources, fourth\n    # full-declare window in "
              "history -- live re-read at generate time\n    # is the "
              "law)",
              "    # sec.1/sec.9); absent -> declared-unavailable zero "
              "rows (freeze-time\n    # expectation per prereg sec.0 "
              "(d): W1/MASS/W2/W3/W4/W5/W6 judged\n    # landed; "
              "W7-JUDGE landed 2026-09-29 11:42:55; W8-JUDGE landed\n"
              "    # 2026-09-29 15:26:25; W9-JUDGE landed 2026-09-29 "
              "17:47:46;\n    # W10-JUDGE landed 2026-09-29 20:31:29; "
              "W11-JUDGE landed 2026-09-30\n    # 01:47:40 -- TWELVE "
              "sources, fifth full-declare window in\n    # history -- "
              "live re-read at generate time is the law)",
              "judged sources note")
    # judged pads +1 rsqr-none
    ex = sub1(ex, '["none"] * 10, "w1_judged")',
              '["none"] * 11, "w1_judged")', "w1 judged pad")
    ex = sub1(ex, '["none"] * 9, "w2_judged")',
              '["none"] * 10, "w2_judged")', "w2 judged pad")
    ex = sub1(ex, '["none"] * 8, "w3_judged")',
              '["none"] * 9, "w3_judged")', "w3 judged pad")
    ex = sub1(ex, '["none"] * 7, "w4_judged")',
              '["none"] * 8, "w4_judged")', "w4 judged pad")
    ex = sub1(ex, '["none"] * 6, "w5_judged")',
              '["none"] * 7, "w5_judged")', "w5 judged pad")
    ex = sub1(ex, '["none"] * 5, "w6_judged")',
              '["none"] * 6, "w6_judged")', "w6 judged pad")
    ex = sub1(ex, '["none"] * 4, "w7_judged")',
              '["none"] * 5, "w7_judged")', "w7 judged pad")
    ex = sub1(ex, '["none"] * 3, "w8_judged")',
              '["none"] * 4, "w8_judged")', "w8 judged pad")
    ex = sub1(ex, '["none"] * 2, "w9_judged")',
              '["none"] * 3, "w9_judged")', "w9 judged pad")
    ex = sub1(ex,
              '                tr["axis"] = list(tr["axis"]) + '
              '["none"] * 8\n                tr["face"] = '
              'f"{tag}:translated-exact"',
              '                tr["axis"] = list(tr["axis"]) + '
              '["none"] * 9\n                tr["face"] = '
              'f"{tag}:translated-exact"', "mass judged pad")
    ex = sub1(ex,
              '                             "face": f"{tag}:stop-'
              'gate-vol-"\n                                     '
              '"yang-vconf-streak-tstate-amp-"\n'
              '                                     "mom-std-none",',
              '                             "face": f"{tag}:stop-'
              'gate-vol-"\n                                     '
              '"yang-vconf-streak-tstate-amp-"\n'
              '                                     "mom-std-rsqr-'
              'none",', "judged face label")
    ex = sub1(ex, '["none"], "w10_judged")',
              '["none"] * 2, "w10_judged")', "w10 judged pad")
    ex = sub1(ex,
              '    disc["w10_judge_products"] = _judged_source(\n'
              '        tl10.JUDGE_FILE, tl10.CANDIDATES_FILE,\n'
              '        ["none"] * 2, "w10_judged")',
              '    disc["w10_judge_products"] = _judged_source(\n'
              '        tl10.JUDGE_FILE, tl10.CANDIDATES_FILE,\n'
              '        ["none"] * 2, "w10_judged")\n'
              '    disc["w11_judge_products"] = _judged_source(\n'
              '        tl11.JUDGE_FILE, tl11.CANDIDATES_FILE,\n'
              '        ["none"], "@@W11TAG2@@")', "w11 judge source")
    ex = sub1(ex,
              '        "requires a prereg-level append-confirm BEFORE '
              'generate runs -- "\n        "none exists, uniform '
              'stands, availability of the ELEVEN judge "\n'
              '        "products disclosed above (freeze-time '
              'eleven-source "\n        "full-declare window = '
              'fourth in history)")',
              '        "requires a prereg-level append-confirm BEFORE '
              'generate runs -- "\n        "none exists, uniform '
              'stands, availability of the TWELVE judge "\n'
              '        "products disclosed above (freeze-time '
              'twelve-source "\n        "full-declare window = fifth '
              'in history)")', "weighting note")
    src = src[:a] + ex + src[b:]
    steps.append("exclusion: 24 real-read faces, w11 screen+judge "
                 "sources, pads+1")

    # ---- 9. _excluded test: index 14 + rsqr face
    exd, a, b = segment(src, 'def _excluded_w11(',
                        '# -------------------------------------------- '
                        'effective face + engine curves',
                        include_start=True, include_end=False)
    exd = exd.replace("_excluded_w11", "_excluded_w12")
    exd = sub1(exd, 'if cand["axis"][13] != "none":',
               'if cand["axis"][14] != "none":', "axis idx")
    exd = sub1(exd,
               "    \"\"\"Exact already-judged cell test, std=none "
               "face only (prereg\n    sec.1: std in {std20_hi, "
               "std10_hi} = new-syntax legal cells --\n    never "
               "excluded; W1-lineage cells implicitly stop/gate/vol/"
               "yang/\n    vconf/streak/tstate/amp/mom/std=none; W2 "
               "cells carry their own\n    stop face; W3 stop+gate; "
               "W4 stop+gate+vol; W5 stop+gate+vol+yang;\n    W6 stop+"
               "gate+vol+yang+vconf; W7 stop+gate+vol+yang+vconf+"
               "streak;\n    W8 stop+gate+vol+yang+vconf+streak+"
               "tstate; W9\n    stop+gate+vol+yang+vconf+streak+"
               "tstate+amp; W10 +mom).  Returns\n    the exclusion\n"
               "    face or None.\"\"\"",
               "    \"\"\"Exact already-judged cell test, rsqr=none "
               "face only (prereg\n    sec.1: rsqr in {rsqr20_hi, "
               "rsqr10_hi} = new-syntax legal cells --\n    never "
               "excluded; W1-lineage cells implicitly stop/gate/vol/"
               "yang/\n    vconf/streak/tstate/amp/mom/std/rsqr=none; "
               "W2 cells carry their own\n    stop face; W3 stop+gate; "
               "W4 stop+gate+vol; W5 stop+gate+vol+yang;\n    W6 stop+"
               "gate+vol+yang+vconf; W7 stop+gate+vol+yang+vconf+"
               "streak;\n    W8 stop+gate+vol+yang+vconf+streak+"
               "tstate; W9\n    stop+gate+vol+yang+vconf+streak+"
               "tstate+amp; W10 +mom; W11 +std).\n    Returns the "
               "exclusion face or None.\"\"\"", "excluded docstring")
    src = src[:a] + exd + src[b:]
    steps.append("_excluded: axis[14] rsqr=none face law")

    # ---- 10. mask + curve + null surgery
    mk, a, b = segment(src, 'def _effective_signal_mask_w11(',
                       '# ------------------------------------------------------------ grammar / status',
                       include_start=True, include_end=False)
    mk = mk.replace("_effective_signal_mask_w11", "_effective_signal_mask_w12")
    mk = sub1(mk,
              "                               tstate_key, amp_key, "
              "mom_key, std_key,\n                               "
              "gate_state, vol_state, yang_state,\n"
              "                               vconf_state, "
              "streak_state, tstate_state,\n"
              "                               amp_state, mom_state, "
              "std_state):",
              "                               tstate_key, amp_key, "
              "mom_key, std_key,\n                               "
              "rsqr_key, gate_state, vol_state, yang_state,\n"
              "                               vconf_state, "
              "streak_state, tstate_state,\n"
              "                               amp_state, mom_state, "
              "std_state, rsqr_state):", "mask signature")
    mk = sub1(mk,
              "    \"\"\"Dedup-face holdings proxy with the frozen "
              "composition order\n    GATE -> VOL -> YANG -> VCONF -> "
              "STREAK -> TSTATE -> AMP -> MOM ->\n    STD -> "
              "initial-stop (prereg sec.3 fourteen-tuple dedup legs; "
              "zero\n    engine burn).  std=none + mom=none + "
              "amp=none + tstate=none +\n    streak=none + vconf=none "
              "+ yang=none + vol=none + gate=none +\n    stop=none = "
              "W1 identity; std=none = W10 semantic baseline; all\n"
              "    ten overlay faces deterministic layers of the same "
              "grammar stack\n    (W10 order extended by the std leg, "
              "zero disturbance to the first\n    nine).\"\"\"",
              "    \"\"\"Dedup-face holdings proxy with the frozen "
              "composition order\n    GATE -> VOL -> YANG -> VCONF -> "
              "STREAK -> TSTATE -> AMP -> MOM ->\n    STD -> RSQR -> "
              "initial-stop (prereg sec.3 fifteen-tuple dedup legs; "
              "zero\n    engine burn).  rsqr=none + std=none + "
              "mom=none + amp=none + tstate=none\n    + streak=none + "
              "vconf=none + yang=none + vol=none + gate=none +\n"
              "    stop=none = W1 identity; rsqr=none = W11 semantic "
              "baseline; all\n    eleven overlay faces deterministic "
              "layers of the same grammar\n    stack (W11 order "
              "extended by the rsqr leg, zero disturbance to the\n"
              "    first ten).\"\"\"", "mask docstring")
    mk = sub1(mk,
              "    MO = mom_zero_mask(AP, mom_key, mom_state)\n"
              "    SD = std_zero_mask(MO, std_key, std_state)\n"
              "    return tl2._effective_signal_mask(SD, prices, "
              "stop_key, atr20)",
              "    MO = mom_zero_mask(AP, mom_key, mom_state)\n"
              "    SD = std_zero_mask(MO, std_key, std_state)\n"
              "    RQ = rsqr_zero_mask(SD, rsqr_key, rsqr_state)\n"
              "    return tl2._effective_signal_mask(RQ, prices, "
              "stop_key, atr20)", "mask chain")
    mk = mk.replace("run_candidate_curve_w11", "run_candidate_curve_w12")
    mk = sub1(mk,
              "                           mom_state=None, "
              "std_state=None):",
              "                           mom_state=None, "
              "std_state=None, rsqr_state=None):", "curve signature")
    mk = sub1(mk,
              "    \"\"\"One W10 candidate cell at the engine face "
              "with the gate + vol +\n    yang + vconf + streak + "
              "tstate + amp + MOM overlays + initial-stop\n    "
              "overlay carried per-cell (prereg sec.3 face a; frozen "
              "composition\n    order filter -> timing -> GATE -> VOL "
              "-> YANG -> VCONF -> STREAK\n    -> TSTATE -> AMP -> MOM "
              "-> initial-stop).\n\n    mom=none+amp=none+"
              "tstate=none+streak=none+vconf=none+yang=none+\n    "
              "vol=none+gate=none+stop=none -> byte-identical to the "
              "tl1 engine\n    face; mom=none+tstate=none -> tl7 W7 "
              "face; mom=none+amp=none ->\n    tl8 W8 face; mom=none "
              "-> tl9 W9 face (parity laws, selftest-\n    pinned); "
              "std=none -> tl10 W10 face (parity law, selftest-"
              "pinned);\n    std in {std20_hi, std10_hi} = new W11 "
              "syntax (entry-permittance\n    only, never excluded).  "
              "Returns (eq, trades, metrics, params,\n    patch, "
              "stop_fired, gate_zeroed, vol_zeroed, yang_zeroed,\n"
              "    vconf_zeroed, streak_zeroed, tstate_zeroed, "
              "amp_zeroed,\n    mom_zeroed, std_zeroed).\"\"\"",
              "    \"\"\"One W11 candidate cell at the engine face "
              "with the gate + vol +\n    yang + vconf + streak + "
              "tstate + amp + MOM + STD overlays +\n    initial-stop "
              "overlay carried per-cell (prereg sec.3 face a; frozen "
              "composition\n    order filter -> timing -> GATE -> VOL "
              "-> YANG -> VCONF -> STREAK\n    -> TSTATE -> AMP -> MOM "
              "-> STD -> RSQR -> initial-stop).\n\n    rsqr=none+std="
              "none+mom=none+amp=none+tstate=none+streak=none+\n    "
              "vconf=none+yang=none+vol=none+gate=none+stop=none -> "
              "byte-identical\n    to the tl1 engine face; rsqr=none -> "
              "tl11 W11 face (parity law,\n    selftest-pinned); rsqr "
              "in {rsqr20_hi, rsqr10_hi} = new W12 syntax\n    "
              "(entry-permittance only, never excluded).  Returns "
              "(eq, trades,\n    metrics, params, patch, stop_fired, "
              "gate_zeroed, vol_zeroed,\n    yang_zeroed, "
              "vconf_zeroed, streak_zeroed, tstate_zeroed,\n    "
              "amp_zeroed, mom_zeroed, std_zeroed, rsqr_zeroed).\"\"\"",
              "curve docstring")
    mk = sub1(mk,
              '    std_key = cand["axis"][13]\n',
              '    std_key = cand["axis"][13]\n'
              '    rsqr_key = cand["axis"][14]\n', "curve keys")
    mk = sub1(mk,
              "    if std_state is None:\n        std_state = "
              "std_state_series(prices)",
              "    if std_state is None:\n        std_state = "
              "std_state_series(prices)\n    if rsqr_state is None:\n"
              "        rsqr_state = rsqr_state_series(prices)",
              "curve state init")
    mk = sub1(mk,
              "    MO = mom_zero_mask(AP, mom_key, mom_state)\n"
              "    SD = std_zero_mask(MO, std_key, std_state)\n"
              "    gate_zeroed",
              "    MO = mom_zero_mask(AP, mom_key, mom_state)\n"
              "    SD = std_zero_mask(MO, std_key, std_state)\n"
              "    RQ = rsqr_zero_mask(SD, rsqr_key, rsqr_state)\n"
              "    gate_zeroed", "curve chain")
    mk = sub1(mk,
              "    std_zeroed = int((MO > 0).sum().sum() - (SD > 0)"
              ".sum().sum())\n    if stop_key",
              "    std_zeroed = int((MO > 0).sum().sum() - (SD > 0)"
              ".sum().sum())\n    rsqr_zeroed = int((SD > 0).sum().sum()"
              " - (RQ > 0).sum().sum())\n    if stop_key",
              "curve zeroed")
    mk = sub1(mk,
              "    if stop_key == \"none\":\n        S, stop_fired = "
              "SD, 0\n    else:\n        S = tl2._effective_signal_"
              "mask(SD, prices, stop_key, atr20)\n        d = (SD > 0) "
              "& (S == 0)",
              "    if stop_key == \"none\":\n        S, stop_fired = "
              "RQ, 0\n    else:\n        S = tl2._effective_signal_"
              "mask(RQ, prices, stop_key, atr20)\n        d = (RQ > 0) "
              "& (S == 0)", "curve stop")
    mk = sub1(mk,
              "    return eq, res[\"trades\"], res[\"metrics\"], "
              "params, patch, stop_fired, \\\n        gate_zeroed, "
              "vol_zeroed, yang_zeroed, vconf_zeroed, \\\n        "
              "streak_zeroed, tstate_zeroed, amp_zeroed, mom_zeroed, "
              "\\\n        std_zeroed",
              "    return eq, res[\"trades\"], res[\"metrics\"], "
              "params, patch, stop_fired, \\\n        gate_zeroed, "
              "vol_zeroed, yang_zeroed, vconf_zeroed, \\\n        "
              "streak_zeroed, tstate_zeroed, amp_zeroed, mom_zeroed, "
              "\\\n        std_zeroed, rsqr_zeroed", "curve return")
    mk = mk.replace("_null_axis_draw_w11", "_null_axis_draw_w12")
    mk = sub1(mk,
              "    \"\"\"Deterministic null-cell draw per prereg "
              "sec.3: rng=[SEED_NULL, i]\n    (W11 berth 20317500, "
              "distinct from the W10 berth 20311500 -- zero\n    "
              "stream overlap by construction); consumption order "
              "frozen = p_on\n    regime -> FOURTEEN-tuple axis R/X/S/"
              "T/STOP/GATE/VOL/YANG/VCONF/\n    STREAK/TSTATE/AMP/MOM "
              "-> signal matrix (the mom gate leg merged\n    into "
              "the same grid/param space draw per prereg sec.3).  Same"
              "\n    engine/cost/panel as candidate cells incl. the "
              "gate + vol + yang +\n    vconf + streak + tstate + amp + "
              "mom legs (BACKTEST_PLAN three\n    iron "
              "rules).\"\"\"",
              "    \"\"\"Deterministic null-cell draw per prereg "
              "sec.3: rng=[SEED_NULL, i]\n    (W12 berth 20321000, "
              "distinct from the W11 berth 20317500 -- zero\n    "
              "stream overlap by construction); consumption order "
              "frozen = p_on\n    regime -> FIFTEEN-tuple axis R/X/S/"
              "T/STOP/GATE/VOL/YANG/VCONF/\n    STREAK/TSTATE/AMP/MOM/"
              "STD/RSQR -> signal matrix (the rsqr gate leg merged\n"
              "    into the same grid/param space draw per prereg "
              "sec.3).  Same\n    engine/cost/panel as candidate cells "
              "incl. the gate + vol + yang +\n    vconf + streak + "
              "tstate + amp + mom + std + rsqr legs\n    "
              "(BACKTEST_PLAN three iron rules).\"\"\"",
              "null docstring")
    mk = sub1(mk,
              "          AXIS_STD[int(rng.integers(len(AXIS_STD)))])",
              "          AXIS_STD[int(rng.integers(len(AXIS_STD)))],"
              "\n          AXIS_RSQR[int(rng.integers"
              "(len(AXIS_RSQR)))])", "null axis leg")
    src = src[:a] + mk + src[b:]
    steps.append("mask/curve/null: rsqr leg wiring (axis[14], "
                 "three-value)")

    # ---- 11. generate-leg surgery
    gen, a, b = segment(src, 'def cmd_generate() -> int:',
                        '# ------------------------------------------------------ screen slice (s2)',
                        include_start=True, include_end=False)
    gen = sub1(gen,
               '    """Frozen prereg sec.3 generate stage (W9 '
               'cmd_generate caliber on\n    the FOURTEEN-tuple face): '
               'per-slot Sobol streams consumed in global\n    '
               'round-robin -> 20-source exclusion -> T-84s3 dedup '
               'gate on the\n    effective signal face (gate + vol + '
               'yang + vconf + streak + tstate\n    + amp + MOM '
               'overlays applied, frozen composition order) ->\n    '
               'w11_candidates.json + grammar ledger wave-10 row.  '
               'Zero engine cells\n    burned."""',
               '    """Frozen prereg sec.3 generate stage (W11 '
               'cmd_generate caliber on\n    the FIFTEEN-tuple face): '
               'per-slot Sobol streams consumed in global\n    '
               'round-robin -> 24-source exclusion -> T-84s3 dedup '
               'gate on the\n    effective signal face (gate + vol + '
               'yang + vconf + streak + tstate\n    + amp + MOM + STD '
               'overlays applied, frozen composition order) ->\n    '
               'w12_candidates.json + grammar ledger wave-12 row.  '
               'Zero engine cells\n    burned."""', "generate docstring")
    gen = sub1(gen,
               '    std_state, std_err = _std_state_full()\n'
               '    if std_err:\n        print(f"GENERATE-GATE: '
               '{std_err} (prereg sec.2 G-STD "\n              '
               '"fail-closed) -- refuse")\n        return 2',
               '    std_state, std_err = _std_state_full()\n'
               '    if std_err:\n        print(f"GENERATE-GATE: '
               '{std_err} (prereg sec.2 G-STD "\n              '
               '"fail-closed) -- refuse")\n        return 2\n'
               '    rsqr_state, rsqr_err = _rsqr_state_full()\n'
               '    if rsqr_err:\n        print(f"GENERATE-GATE: '
               '{rsqr_err} (prereg sec.2 G-RSQR "\n              '
               '"fail-closed) -- refuse")\n        return 2',
               "G-RSQR gate")
    gen = sub1(gen,
               '               ["stop_gate_vol_yang_vconf_streak_'
               'tstate_amp_mom_std_none_face"]',
               '               ["stop_gate_vol_yang_vconf_streak_'
               'tstate_amp_mom_std_rsqr_none_face"]',
               "neg_fns key")
    gen = sub1(gen,
               "        S = _effective_signal_mask_w11(mask, prices, "
               "cand[\"axis\"][4], atr20,\n                                      "
               "cand[\"axis\"][5], cand[\"axis\"][6],\n            "
               "                          cand[\"axis\"][7], "
               "cand[\"axis\"][8],\n                                      "
               "cand[\"axis\"][9], cand[\"axis\"][10],\n             "
               "                         cand[\"axis\"][11], "
               "cand[\"axis\"][12],\n                                      "
               "cand[\"axis\"][13],\n                                      "
               "gate_state, vol_state, yang_state,\n                "
               "                      vconf_state, streak_state,\n   "
               "                                   tstate_state, "
               "amp_state, mom_state,\n                                      "
               "std_state)",
               "        S = _effective_signal_mask_w12(mask, prices, "
               "cand[\"axis\"][4], atr20,\n                                      "
               "cand[\"axis\"][5], cand[\"axis\"][6],\n            "
               "                          cand[\"axis\"][7], "
               "cand[\"axis\"][8],\n                                      "
               "cand[\"axis\"][9], cand[\"axis\"][10],\n             "
               "                         cand[\"axis\"][11], "
               "cand[\"axis\"][12],\n                                      "
               "cand[\"axis\"][13], cand[\"axis\"][14],\n            "
               "                          gate_state, vol_state, "
               "yang_state,\n                                      "
               "vconf_state, streak_state,\n                        "
               "              tstate_state, amp_state, mom_state,\n  "
               "                                    std_state, "
               "rsqr_state)", "generate mask call")
    gen = sub1(gen,
               "    mom_counts, std_counts = {}, {}\n    "
               "gvvvsktsam_counts = {}",
               "    mom_counts, std_counts = {}, {}\n    "
               "rsqr_counts = {}\n    gvvvsktsam_counts = {}",
               "counts init")
    gen = sub1(gen,
               "        std_counts[c[\"axis\"][13]] = "
               "std_counts.get(c[\"axis\"][13], 0) + 1\n        k9 = "
               "(f\"{c['axis'][5]}|{c['axis'][6]}|{c['axis'][7]}|\"\n"
               "              f\"{c['axis'][8]}|{c['axis'][9]}|"
               "{c['axis'][10]}|\"\n              f\"{c['axis'][11]}|"
               "{c['axis'][12]}|{c['axis'][13]}\")\n        "
               "gvvvsktsam_counts[k9] = gvvvsktsam_counts.get(k9, 0) "
               "+ 1",
               "        std_counts[c[\"axis\"][13]] = "
               "std_counts.get(c[\"axis\"][13], 0) + 1\n        "
               "rsqr_counts[c[\"axis\"][14]] = "
               "rsqr_counts.get(c[\"axis\"][14], 0) + 1\n        k10 = "
               "(f\"{c['axis'][5]}|{c['axis'][6]}|{c['axis'][7]}|\"\n"
               "              f\"{c['axis'][8]}|{c['axis'][9]}|"
               "{c['axis'][10]}|\"\n              f\"{c['axis'][11]}|"
               "{c['axis'][12]}|{c['axis'][13]}|\"\n              "
               "f\"{c['axis'][14]}\")\n        "
               "gvvvsktsam_counts[k10] = gvvvsktsam_counts.get(k10, 0) "
               "+ 1", "counts loop")
    gen = sub1(gen,
               '                                     "amp, mom, std); '
               'exclusion face "\n                                     '
               '"= std=none only (sec.1); prior-wave "\n            '
               '                         "keys std=none-completed; '
               'std in "\n                                     '
               '"{std20_hi, std10_hi} = "\n                                     '
               '"new-syntax legal cells"},',
               '                                     "amp, mom, std, '
               'rsqr); exclusion face "\n                                     '
               '"= rsqr=none only (sec.1); prior-wave "\n            '
               '                         "keys rsqr=none-completed; '
               'rsqr in "\n                                     '
               '"{rsqr20_hi, rsqr10_hi} = "\n                                '
               '     "new-syntax legal cells"},', "excl note")
    gen = sub1(gen, '"+ MOM overlays applied, frozen "',
               '"+ MOM + STD overlays applied, frozen "', "dedup note")
    gen = sub1(gen,
               '               "std_face_counts": std_counts,\n'
               '               "gate_vol_yang_vconf_streak_tstate_'
               'amp_mom_std_face_"\n               "counts":\n'
               '                   gvvvsktsam_counts,',
               '               "std_face_counts": std_counts,\n'
               '               "rsqr_face_counts": rsqr_counts,\n'
               '               "gate_vol_yang_vconf_streak_tstate_'
               'amp_mom_std_rsqr_face_"\n               "counts":\n'
               '                   gvvvsktsam_counts,', "payload counts")
    gen = sub1(gen, '               "std_state_meta": std_state[2],',
               '               "std_state_meta": std_state[2],\n'
               '               "rsqr_state_meta": rsqr_state[2],',
               "payload metas")
    gen = sub1(gen,
               '                         "seed_berth_note": "berths '
               '20317000/"\n                         "20317500/'
               '20318000 held at the freeze commit "\n                '
               '         "(bm-b r441 three-step re-verify ALL GREEN, "\n'
               '                         "no re-pick after the '
               '20316000/20316500 "\n                         '
               '"collision re-take per draft clause-5; R250 "\n'
               '                         "one-step law; berth-open '
               'adoption of the "\n                         "bm-c '
               'r237 STD candidate whole package per "\n'
               '                         "AMP->W9->W10 adoption '
               'lineage)",',
               '                         "seed_berth_note": "berths '
               '20320500/"\n                         "20321000/20321500 '
               'held at the freeze commit "\n                         '
               '"(bm-b r444 three-step re-verify ALL GREEN, "\n'
               '                         "no re-pick; R250 one-step '
               'law; berth-open adoption "\n                         '
               '"of the bm-a r447 RSQR candidate whole package "\n'
               '                         "per AMP->W9/MOM->W10/STD->W11 '
               'adoption lineage)",', "berth note")
    gen = sub1(gen,
               '           f"(std faces {json.dumps(std_counts, '
               'sort_keys=True)}; "\n           f"gate x vol x yang x '
               'vconf x streak x tstate x amp x mom "\n           f"x '
               'std {json.dumps(gvvvsktsam_counts, sort_keys=True)}) "',
               '           f"(std faces {json.dumps(std_counts, '
               'sort_keys=True)}; "\n           f"rsqr faces '
               '{json.dumps(rsqr_counts, sort_keys=True)}; "\n'
               '           f"gate x vol x yang x vconf x streak x '
               'tstate x amp x mom "\n           f"x std x rsqr '
               '{json.dumps(gvvvsktsam_counts, sort_keys=True)}) "',
               "ledger row")
    gen = sub1(gen,
               '           f"TRIAL-LABOR-W11-GENERATE, T-123 prereg '
               'bm-b r441 frozen / "\n           f"runner bm-b r442) '
               '| "',
               '           f"TRIAL-LABOR-W12-GENERATE, T-124 prereg '
               'bm-b r444 frozen / "\n           f"runner bm-b r445) '
               '| "', "ledger pool row")
    gen = sub1(gen,
               '    print(f"mom faces: {json.dumps(mom_counts, '
               'sort_keys=True)}; "\n          f"gate x vol x yang x '
               'vconf x streak x tstate x amp x mom: "\n          '
               'f"{json.dumps(gvvvsktsam_counts, sort_keys=True)[:400]}")',
               '    print(f"mom faces: {json.dumps(mom_counts, '
               'sort_keys=True)}; "\n          f"std faces: '
               '{json.dumps(std_counts, sort_keys=True)}; "\n          '
               'f"rsqr faces: {json.dumps(rsqr_counts, '
               'sort_keys=True)}; "\n          f"gate x vol x yang x '
               'vconf x streak x tstate x amp x mom x "\n          '
               'f"std x rsqr: "\n          f"{json.dumps'
               '(gvvvsktsam_counts, sort_keys=True)[:400]}")',
               "generate print")
    src = src[:a] + gen + src[b:]
    steps.append("generate: G-RSQR gate + fifteen-tuple dedup + "
                 "counts")

    # ---- 12. screen-slice wiring (csv cols + cell + prep + shard +
    #         finalize) -- targeted count-verified replaces
    src = sub1(src,
              '                      "std_face", "std_zeroed",\n'
              '                      "survives_screen"]',
              '                      "std_face", "std_zeroed",\n'
              '                      "rsqr_face", "rsqr_zeroed",\n'
              '                      "survives_screen"]', "csv cols")
    src = subn(src,
               "        eq, trades, metrics, params, patch, fired, gz, "
               "vz, yz, cz, sz, \\\n            tz, az, mz, dz = "
               "run_candidate_curve_w11(",
               "        eq, trades, metrics, params, patch, fired, gz, "
               "vz, yz, cz, sz, \\\n            tz, az, mz, dz, rz = "
               "run_candidate_curve_w12(", 3, "screen+judge cell unpack")
    src = subn(src, '                std_state=st.get("std_state"))',
               '                std_state=st.get("std_state"),\n'
               '                rsqr_state=st.get("rsqr_state"))',
               2, "screen cell state args")
    src = sub1(src,
               '           "mom_zeroed": int(mz), "std_face": '
               'cand["axis"][13],\n           "std_zeroed": int(dz)}',
               '           "mom_zeroed": int(mz), "std_face": '
               'cand["axis"][13],\n           "std_zeroed": int(dz),\n'
               '           "rsqr_face": cand["axis"][14],\n'
               '           "rsqr_zeroed": int(rz)}', "screen row")
    src = sub1(src,
               "    std_meta_core = std_state_full[2]\n",
               "    std_meta_core = std_state_full[2]\n\n"
               "    # G-RSQR on the raw full-history face (prereg "
               "sec.2 probe basis =\n    # data/daily/sh510300.csv; "
               "120-bar warmup + probe anchors\n    # decidable "
               "3,363 / open 341 / rsqr10 3363/332 + slope split\n"
               "    # 213/128 + nine-gate 512-cell 124/388 law + "
               "extreme-day 0/7\n    # open states)\n    "
               "rsqr_state_full, rsqr_err = _rsqr_state_full()\n"
               "    if rsqr_err:\n        print(f\"PREP-GATE FAIL: "
               "G-RSQR {rsqr_err}\")\n        return 1\n    "
               "rsqr_meta_core = rsqr_state_full[2]\n",
               "prep G-RSQR gate")
    src = subn(src,
               '                              (MOM_MEMBER, "mom"), '
               '(STD_MEMBER, "std")):',
               '                              (MOM_MEMBER, "mom"), '
               '(STD_MEMBER, "std"),\n                              '
               '(RSQR_MEMBER, "rsqr")):', 2, "member loops")
    src = sub1(src,
               "    _o20, _d20, std_meta, _o10, _d10 = "
               "std_state_series(prices)\n    if not "
               "_std_structure_pass(std_meta):\n        print(f"
               "\"PREP-GATE FAIL: G-STD leg-L structural invariants "
               "\"\n              f\"broken {std_meta} -- honest "
               "refuse\")\n        return 1",
               "    _o20, _d20, std_meta, _o10, _d10 = "
               "std_state_series(prices)\n    if not "
               "_std_structure_pass(std_meta):\n        print(f"
               "\"PREP-GATE FAIL: G-STD leg-L structural invariants "
               "\"\n              f\"broken {std_meta} -- honest "
               "refuse\")\n        return 1\n    _r20o, _r20d, "
               "rsqr_meta, _r10o, _r10d = rsqr_state_series(prices)\n"
               "    if not _rsqr_structure_pass(rsqr_meta):\n        "
               "print(f\"PREP-GATE FAIL: G-RSQR leg-L structural \"\n"
               "              f\"invariants broken {rsqr_meta} -- "
               "honest refuse\")\n        return 1",
               "prep legL structure")
    src = sub1(src,
               '                       "G-STD": {"pass": True,\n'
               '                                 "core48": '
               'std_meta_core,\n                                 '
               '"legL": std_meta},',
               '                       "G-STD": {"pass": True,\n'
               '                                 "core48": '
               'std_meta_core,\n                                 '
               '"legL": std_meta},\n'
               '                       "G-RSQR": {"pass": True,\n'
               '                                  "core48": '
               'rsqr_meta_core,\n                                  '
               '"legL": rsqr_meta},', "prep payload G-RSQR")
    src = sub1(src,
               '            "amp_meta": amp_meta, "mom_meta": '
               'mom_meta,\n            "std_meta": std_meta,\n'
               '            "n_distinct": cg["n"], "n_starts_6m": '
               'len(starts),',
               '            "amp_meta": amp_meta, "mom_meta": '
               'mom_meta,\n            "std_meta": std_meta,\n'
               '            "rsqr_meta": rsqr_meta,\n'
               '            "n_distinct": cg["n"], "n_starts_6m": '
               'len(starts),', "prep payload meta")
    src = sub1(src,
               '          f"{mom_meta[\'decidable_days\']} warmup "\n'
               '          f"{mom_meta[\'warmup_gate_closed_bars\']}")'
               '\n    return 0',
               '          f"{mom_meta[\'decidable_days\']} warmup "\n'
               '          f"{mom_meta[\'warmup_gate_closed_bars\']}; "'
               '\n          f"G-RSQR {rsqr_meta[\'open_days\']}open/"'
               '\n          f"{rsqr_meta[\'closed_days\']}closed '
               'decidable "\n          f"{rsqr_meta'
               '[\'decidable_days\']} rsqr10-open "\n          '
               'f"{rsqr_meta[\'rsqr10_open_days\']}")\n    return 0',
               "prep print")
    src = sub1(src,
               '    mom_state = mom_state_series(prices)\n'
               '    std_state = std_state_series(prices)\n',
               '    mom_state = mom_state_series(prices)\n'
               '    std_state = std_state_series(prices)\n'
               '    rsqr_state = rsqr_state_series(prices)\n',
               "shard state init")
    src = sub1(src,
               '             "mom_state": mom_state,\n'
               '             "std_state": std_state}',
               '             "mom_state": mom_state,\n'
               '             "std_state": std_state,\n'
               '             "rsqr_state": rsqr_state}', "shard st")
    src = sub1(src,
               "    mom_counts, std_counts = {}, {}\n    gate_seg, "
               "vol_seg, yang_seg, vconf_seg = {}, {}, {}, {}",
               "    mom_counts, std_counts = {}, {}\n    rsqr_counts "
               "= {}\n    gate_seg, vol_seg, yang_seg, vconf_seg = "
               "{}, {}, {}, {}", "finalize counts init")
    src = sub1(src,
               "    std_seg, gvvvsktsams_seg = {}, {}",
               "    std_seg, rsqr_seg, gvvvsktsamsr_seg = {}, {}, {}",
               "finalize segs init")
    src = sub1(src,
               '        stf = r["std_face"]\n',
               '        stf = r["std_face"]\n        rqf = '
               'r["rsqr_face"]\n', "finalize face read")
    src = sub1(src,
               '        std_counts[stf] = std_counts.get(stf, 0) + 1',
               '        std_counts[stf] = std_counts.get(stf, 0) + 1\n'
               '        rsqr_counts[rqf] = rsqr_counts.get(rqf, 0) + 1',
               "finalize counts loop")
    src = sub1(src,
               "                         (std_seg, stf),\n"
               "                         (gvvy_seg, "
               'f"{gf}|{vf}|{yf}|{cf}"),',
               "                         (std_seg, stf),\n"
               "                         (rsqr_seg, rqf),\n"
               "                         (gvvy_seg, "
               'f"{gf}|{vf}|{yf}|{cf}"),', "finalize seg loop a")
    src = sub1(src,
               '                         (gvvvsktsams_seg,\n'
               '                          f"{gf}|{vf}|{yf}|{cf}|{sf}|'
               '{tf}|{af}|{mf}|"\n                          f"{stf}")):',
               '                         (gvvvsktsams_seg,\n'
               '                          f"{gf}|{vf}|{yf}|{cf}|{sf}|'
               '{tf}|{af}|{mf}|"\n                          f"{stf}"),'
               '\n                         (gvvvsktsamsr_seg,\n'
               '                          f"{gf}|{vf}|{yf}|{cf}|{sf}|'
               '{tf}|{af}|{mf}|"\n                          f"{stf}|'
               '{rqf}")):', "finalize seg loop b")
    src = sub1(src,
               "    for seg in (gate_seg, vol_seg, yang_seg, "
               "vconf_seg, streak_seg,\n                tstate_seg, "
               "amp_seg, mom_seg, std_seg, gvvy_seg,\n                "
               "gvvvsk_seg, gvvvskts_seg, gvvvsktsa_seg,\n                "
               "gvvvsktsam_seg, gvvvsktsams_seg):",
               "    for seg in (gate_seg, vol_seg, yang_seg, "
               "vconf_seg, streak_seg,\n                tstate_seg, "
               "amp_seg, mom_seg, std_seg, rsqr_seg, gvvy_seg,\n"
               "                gvvvsk_seg, gvvvskts_seg, "
               "gvvvsktsa_seg,\n                gvvvsktsam_seg, "
               "gvvvsktsams_seg, gvvvsktsamsr_seg):",
               "finalize rate loop")
    src = sub1(src, '    std_meta = prep.get("std_meta")\n',
               '    std_meta = prep.get("std_meta")\n'
               '    rsqr_meta = prep.get("rsqr_meta")\n',
               "finalize meta read")
    src = sub1(src,
               '           "std_face_counts": std_counts,\n'
               '           "gate_segmented_survival": gate_seg,',
               '           "std_face_counts": std_counts,\n'
               '           "rsqr_face_counts": rsqr_counts,\n'
               '           "gate_segmented_survival": gate_seg,',
               "finalize payload counts")
    src = sub1(src, '           "std_segmented_survival": std_seg,',
               '           "std_segmented_survival": std_seg,\n'
               '           "rsqr_segmented_survival": rsqr_seg,',
               "finalize payload segs")
    src = sub1(src,
               '           "gate_vol_yang_vconf_streak_tstate_amp_mom_'
               'std_interaction_"\n           "survival": '
               'gvvvsktsams_seg,',
               '           "gate_vol_yang_vconf_streak_tstate_amp_mom_'
               'std_interaction_"\n           "survival": '
               'gvvvsktsams_seg,\n           "gate_vol_yang_vconf_'
               'streak_tstate_amp_mom_std_rsqr_interaction_"\n'
               '           "survival": gvvvsktsamsr_seg,',
               "finalize payload interaction")
    src = sub1(src,
               '           "std_na_window_bars": (std_meta'
               '["na_window_bars"]\n                                   '
               'if std_meta else None),',
               '           "std_na_window_bars": (std_meta'
               '["na_window_bars"]\n                                   '
               'if std_meta else None),\n           '
               '"rsqr_na_window_bars": (rsqr_meta["na_window_bars"]\n'
               '                                   if rsqr_meta else '
               'None),', "finalize na bars")
    src = sub1(src, '"MOM -> signal matrix (frozen "',
               '"MOM/STD/RSQR -> signal matrix (frozen "',
               "finalize draw order a")
    src = sub1(src, '"vconf+streak+tstate+amp+mom "\n',
               '"vconf+streak+tstate+amp+mom+std+rsqr "\n',
               "finalize draw order b")
    src = sub1(src,
               '                             "-> STREAK -> TSTATE -> '
               'AMP -> MOM -> "\n                             '
               '"initial-stop); MA200/"',
               '                             "-> STREAK -> TSTATE -> '
               'AMP -> MOM -> STD -> "\n                             '
               '"RSQR -> initial-stop); MA200/"', "finalize audit order")
    src = sub1(src,
               '                             "mom 139-bar warmup / '
               'std 120-bar warmup "\n                             '
               '"(panel-level counts in gate/vol/yang/vconf/"\n'
               '                             "streak/tstate/amp/mom/'
               'std_na_window_bars); "',
               '                             "mom 139-bar warmup / '
               'std 120-bar warmup / rsqr "\n                             '
               '"120-bar warmup (panel-level counts in gate/vol/yang/'
               'vconf/"\n                             "streak/tstate/'
               'amp/mom/std/rsqr_na_window_bars); "', "audit warmups")
    src = sub1(src,
               '                             "std20_hi/std10_hi keep '
               'face = open AND "\n                              '
               '"decidable (same erratum law); "',
               '                             "std20_hi/std10_hi keep '
               'face = open AND "\n                              '
               '"decidable (same erratum law); rsqr20_hi/rsqr10_hi '
               'keep "\n                              "face = open AND '
               'decidable (same erratum law); "', "audit erratum")
    src = sub1(src,
               '    print(f"std segmented survival: {json.dumps'
               '(std_seg, sort_keys=True)}")\n    print(f"gate x vol x '
               'yang x vconf x streak x tstate x amp x mom "\n          '
               'f"interaction survival: "\n          f"{json.dumps'
               '(gvvvsktsam_seg, sort_keys=True)[:400]}")\n    print(f'
               '"gate x vol x yang x vconf x streak x tstate x amp x '
               'mom "\n          f"x std interaction survival: "\n'
               '          f"{json.dumps(gvvvsktsams_seg, '
               'sort_keys=True)[:400]}")',
               '    print(f"std segmented survival: {json.dumps'
               '(std_seg, sort_keys=True)}")\n    print(f"rsqr '
               'segmented survival: {json.dumps(rsqr_seg, '
               'sort_keys=True)}")\n    print(f"gate x vol x yang x '
               'vconf x streak x tstate x amp x mom "\n          f'
               '"interaction survival: "\n          f"{json.dumps'
               '(gvvvsktsam_seg, sort_keys=True)[:400]}")\n    print(f'
               '"gate x vol x yang x vconf x streak x tstate x amp x '
               'mom "\n          f"x std interaction survival: "\n'
               '          f"{json.dumps(gvvvsktsams_seg, '
               'sort_keys=True)[:400]}")\n    print(f"gate x vol x '
               'yang x vconf x streak x tstate x amp x mom x "\n'
               '          f"std x rsqr interaction survival: "\n'
               '          f"{json.dumps(gvvvsktsamsr_seg, '
               'sort_keys=True)[:400]}")',
               "finalize prints")
    steps.append("screen slice: csv/cell/prep/shard/finalize rsqr "
                 "wiring")

    # ---- 13. judge-slice wiring
    src = sub1(src,
               '    tl2._dual_nulls_w2 (import law; the seed constant '
               'is the only\n    differing face -- selftest '
               'cross-checks at the W10 seed)."""',
               '    tl2._dual_nulls_w2 (import law; the seed constant '
               'is the only\n    differing face -- selftest '
               'cross-checks at the W12 unc-berth seed)."""',
               "dual nulls docstring a")
    src = sub1(src,
               '    B=2000 block-20 circular bootstrap + P=2000 '
               'sign-flip, two-sided;\n    W10 seed binding '
               '[20312000, cell_idx].  Math imported verbatim from',
               '    B=2000 block-20 circular bootstrap + P=2000 '
               'sign-flip, two-sided;\n    W12 unc-berth seed binding '
               '[20321500, cell_idx].  Math imported verbatim from',
               "dual nulls docstring b")
    src = sub1(src,
               "def _overlay_stop_disclosure_w11(cand, prices, P, "
               "atr20, fundamental_ok,\n                                "
               "gate_state, vol_state, yang_state,\n"
               "                                vconf_state, "
               "streak_state, tstate_state,\n                                "
               "amp_state, mom_state, std_state):",
               "def _overlay_stop_disclosure_w12(cand, prices, P, "
               "atr20, fundamental_ok,\n                                "
               "gate_state, vol_state, yang_state,\n"
               "                                vconf_state, "
               "streak_state, tstate_state,\n                                "
               "amp_state, mom_state, std_state,\n                                "
               "rsqr_state):", "stop disclosure sig")
    src = sub1(src,
               "    with the W11 composition order (filter -> timing "
               "-> GATE -> VOL ->\n    YANG -> VCONF -> STREAK -> "
               "TSTATE -> AMP -> MOM -> STD ->\n    initial-stop; "
               "MSG-0440 E1 mapping + MSG-0450 annex 1).  Mirrors\n"
               "    tl10._overlay_stop_disclosure_w10 with the std "
               "overlay inserted\n    before stop arming (engine-face "
               "consistency law; summary math\n    imported).\"\"\"",
               "    with the W12 composition order (filter -> timing "
               "-> GATE -> VOL ->\n    YANG -> VCONF -> STREAK -> "
               "TSTATE -> AMP -> MOM -> STD ->\n    RSQR -> "
               "initial-stop; MSG-0440 E1 mapping + MSG-0450 annex "
               "1).  Mirrors\n    tl11._overlay_stop_disclosure_w11 "
               "with the rsqr overlay inserted\n    before stop "
               "arming (engine-face consistency law; summary math\n"
               "    imported).\"\"\"", "stop disclosure docstring")
    src = sub1(src,
               "    MO = mom_zero_mask(AP, cand[\"axis\"][12], "
               "mom_state)\n    SD = std_zero_mask(MO, "
               "cand[\"axis\"][13], std_state)\n    _, ev = "
               "tl2.stop_exit_overlay(SD, prices, stop_key, atr20)",
               "    MO = mom_zero_mask(AP, cand[\"axis\"][12], "
               "mom_state)\n    SD = std_zero_mask(MO, "
               "cand[\"axis\"][13], std_state)\n    RQ = "
               "rsqr_zero_mask(SD, cand[\"axis\"][14], rsqr_state)\n"
               "    _, ev = tl2.stop_exit_overlay(RQ, prices, "
               "stop_key, atr20)", "stop disclosure chain")
    src = sub1(src,
               '           "std_face": cand["axis"][13]}\n    legs = {}',
               '           "std_face": cand["axis"][13],\n'
               '           "rsqr_face": cand["axis"][14]}\n    legs '
               '= {}', "judge cell out face")
    src = sub1(src, '        sd = st[f"std_state_{leg}"]\n',
               '        sd = st[f"std_state_{leg}"]\n        rq = '
               'st[f"rsqr_state_{leg}"]\n', "judge cell state read")
    src = sub1(src,
               "            eq2, _, m2, _, _, fired2, gz2, vz2, yz2, "
               "cz2, sz2, tz2, \\\n                az2, mz2, dz2 = "
               "run_candidate_curve_w11(",
               "            eq2, _, m2, _, _, fired2, gz2, vz2, yz2, "
               "cz2, sz2, tz2, \\\n                az2, mz2, dz2, rz2 "
               "= run_candidate_curve_w12(", "judge cell unpack 2")
    src = sub1(src,
               "                                                 "
               "amp_state=ap,\n                                                 "
               "mom_state=mo,\n                                                 "
               "std_state=sd)",
               "                                                 "
               "amp_state=ap,\n                                                 "
               "mom_state=mo,\n                                                 "
               "std_state=sd,\n                                                 "
               "rsqr_state=rq)", "judge cell curve states 1")
    src = sub1(src,
               "                    streak_state=sk, tstate_state=ts, "
               "amp_state=ap,\n                    mom_state=mo, "
               "std_state=sd)",
               "                    streak_state=sk, tstate_state=ts, "
               "amp_state=ap,\n                    mom_state=mo, "
               "std_state=sd, rsqr_state=rq)",
               "judge cell curve states 2")
    src = sub1(src,
               '                         "std_zeroed": 0,\n'
               '                         "std_zeroed_x2": 0,',
               '                         "std_zeroed": 0,\n'
               '                         "std_zeroed_x2": 0,\n'
               '                         "rsqr_zeroed": 0,\n'
               '                         "rsqr_zeroed_x2": 0,',
               "judge degenerate legs")
    src = sub1(src,
               '                     "std_zeroed": int(dz),\n'
               '                     "std_zeroed_x2": int(dz2),',
               '                     "std_zeroed": int(dz),\n'
               '                     "std_zeroed_x2": int(dz2),\n'
               '                     "rsqr_zeroed": int(rz),\n'
               '                     "rsqr_zeroed_x2": int(rz2),',
               "judge legs dict")
    src = sub1(src,
               '            out["stop_disclosure"] = '
               '_overlay_stop_disclosure_w11(\n                cand, '
               'prices, P, st["atr20_L"], fok, gs, vs, ys, cs, sk,\n'
               '                ts, ap, mo, sd)',
               '            out["stop_disclosure"] = '
               '_overlay_stop_disclosure_w12(\n                cand, '
               'prices, P, st["atr20_L"], fok, gs, vs, ys, cs, sk,\n'
               '                ts, ap, mo, sd, rq)', "stop disc call")
    src = sub1(src,
               "    std_state_full, std_err = _std_state_full()\n"
               "    if std_err:\n        print(f\"JUDGE-GATE: "
               "{std_err} (prereg sec.2 G-STD \"\n              "
               "\"fail-closed) -- refuse\")\n        return 2",
               "    std_state_full, std_err = _std_state_full()\n"
               "    if std_err:\n        print(f\"JUDGE-GATE: "
               "{std_err} (prereg sec.2 G-STD \"\n              "
               "\"fail-closed) -- refuse\")\n        return 2\n"
               "    rsqr_state_full, rsqr_err = _rsqr_state_full()\n"
               "    if rsqr_err:\n        print(f\"JUDGE-GATE: "
               "{rsqr_err} (prereg sec.2 G-RSQR \"\n              "
               "\"fail-closed) -- refuse\")\n        return 2",
               "judge cmd G-RSQR gate")
    src = sub1(src,
               "        sdst = std_state_series(prices)\n        "
               "state[f\"std_state_{leg}\"] = sdst\n        "
               "state[f\"std_meta_{leg}\"] = sdst[2]",
               "        sdst = std_state_series(prices)\n        "
               "state[f\"std_state_{leg}\"] = sdst\n        "
               "state[f\"std_meta_{leg}\"] = sdst[2]\n        rst = "
               "rsqr_state_series(prices)\n        "
               "state[f\"rsqr_state_{leg}\"] = rst\n        "
               "state[f\"rsqr_meta_{leg}\"] = rst[2]",
               "judge cmd per-leg state")
    src = sub1(src,
               "    std_state_full, std_err = _std_state_full()\n"
               "    if std_err:\n        print(f\"JUDGE-PREP-GATE "
               "FAIL: G-STD {std_err}\")\n        return 1",
               "    std_state_full, std_err = _std_state_full()\n"
               "    if std_err:\n        print(f\"JUDGE-PREP-GATE "
               "FAIL: G-STD {std_err}\")\n        return 1\n"
               "    rsqr_state_full, rsqr_err = _rsqr_state_full()\n"
               "    if rsqr_err:\n        print(f\"JUDGE-PREP-GATE "
               "FAIL: G-RSQR {rsqr_err}\")\n        return 1",
               "judge prep G-RSQR gate")
    src = sub1(src,
               "    tstate_meta, amp_meta, mom_meta, std_meta = "
               "{}, {}, {}, {}",
               "    tstate_meta, amp_meta, mom_meta, std_meta = "
               "{}, {}, {}, {}\n    rsqr_meta = {}",
               "judge prep metas init")
    src = sub1(src,
               '                                  (STD_MEMBER, '
               '"std")):\n            if member not in prices:',
               '                                  (STD_MEMBER, '
               '"std"),\n                                  '
               '(RSQR_MEMBER, "rsqr")):\n            if member not '
               'in prices:', "judge prep member loop")
    src = sub1(src,
               "        _so20, _sd20, stdeta, _so10, _sd10 = "
               "std_state_series(prices)\n        if not "
               "_std_structure_pass(stdeta):\n            print(f"
               "\"JUDGE-PREP-GATE FAIL: leg-{leg} G-STD structural "
               "\"\n                  f\"invariants broken {stdeta} "
               "-- honest refuse\")\n            return 1\n        "
               "std_meta[leg] = stdeta",
               "        _so20, _sd20, stdeta, _so10, _sd10 = "
               "std_state_series(prices)\n        if not "
               "_std_structure_pass(stdeta):\n            print(f"
               "\"JUDGE-PREP-GATE FAIL: leg-{leg} G-STD structural "
               "\"\n                  f\"invariants broken {stdeta} "
               "-- honest refuse\")\n            return 1\n        "
               "std_meta[leg] = stdeta\n        _r20o, _r20d, "
               "rsqreta, _r10o, _r10d = rsqr_state_series(prices)\n"
               "        if not _rsqr_structure_pass(rsqreta):\n        "
               "    print(f\"JUDGE-PREP-GATE FAIL: leg-{leg} G-RSQR "
               "structural \"\n                  f\"invariants broken "
               "{rsqreta} -- honest refuse\")\n            return 1\n"
               "        rsqr_meta[leg] = rsqreta",
               "judge prep per-leg structure")
    src = sub1(src, '    std_meta["full_raw_face"] = std_state_full[2]',
               '    std_meta["full_raw_face"] = std_state_full[2]\n'
               '    rsqr_meta["full_raw_face"] = rsqr_state_full[2]',
               "judge prep full_raw_face")
    src = subn(src,
               '               "amp_meta": amp_meta, "mom_meta": '
               'mom_meta,\n               "std_meta": std_meta,\n'
               '               "vacuous": True,',
               '               "amp_meta": amp_meta, "mom_meta": '
               'mom_meta,\n               "std_meta": std_meta,\n'
               '               "rsqr_meta": rsqr_meta,\n'
               '               "vacuous": True,', 1, "prep vacuous payload")
    src = subn(src,
               '           "mom_meta": mom_meta,\n           "std_meta": '
               'std_meta,\n           "manifest_note":',
               '           "mom_meta": mom_meta,\n           "std_meta": '
               'std_meta,\n           "rsqr_meta": rsqr_meta,\n'
               '           "manifest_note":', 1, "prep main payload")
    src = sub1(src,
               '    print(f"std meta L 120-bar-warmup "\n'
               '          f"{std_meta[\'L\'][\'open_days\']}open/"\n'
               '          f"{std_meta[\'L\'][\'closed_days\']}closed '
               'decidable "\n          f"{std_meta[\'L\']'
               '[\'decidable_days\']} std10-open "\n          '
               'f"{std_meta[\'L\'][\'std10_open_days\']}")',
               '    print(f"std meta L 120-bar-warmup "\n'
               '          f"{std_meta[\'L\'][\'open_days\']}open/"\n'
               '          f"{std_meta[\'L\'][\'closed_days\']}closed '
               'decidable "\n          f"{std_meta[\'L\']'
               '[\'decidable_days\']} std10-open "\n          '
               'f"{std_meta[\'L\'][\'std10_open_days\']}")\n    '
               'print(f"rsqr meta L 120-bar-warmup "\n          '
               'f"{rsqr_meta[\'L\'][\'open_days\']}open/"\n          '
               'f"{rsqr_meta[\'L\'][\'closed_days\']}closed decidable '
               '"\n          f"{rsqr_meta[\'L\'][\'decidable_days\']} '
               'rsqr10-open "\n          f"{rsqr_meta[\'L\']'
               '[\'rsqr10_open_days\']} slope-split "\n          '
               'f"{rsqr_meta[\'L\'][\'slope_sign_split\']}")',
               "judge prep print")
    src = sub1(src,
               "    amp_sum, mom_sum, std_sum = {}, {}, {}\n    "
               "gvy_sum, gvvy_sum, gvvvsk_sum = {}, {}, {}\n    "
               "gvvvskts_sum, gvvvsktsa_sum, gvvvsktsam_sum = "
               "{}, {}, {}\n    gvvvsktsams_sum = {}",
               "    amp_sum, mom_sum, std_sum = {}, {}, {}\n    "
               "rsqr_sum = {}\n    gvy_sum, gvvy_sum, gvvvsk_sum = "
               "{}, {}, {}\n    gvvvskts_sum, gvvvsktsa_sum, "
               "gvvvsktsam_sum = {}, {}, {}\n    "
               "gvvvsktsams_sum = {}\n    gvvvsktsamsr_sum = {}",
               "judge final sums init")
    src = sub1(src,
               '        stf = r.get("std_face", "none")\n',
               '        stf = r.get("std_face", "none")\n        rqf '
               '= r.get("rsqr_face", "none")\n', "judge final face read")
    src = sub1(src,
               "                         (std_sum, stf),\n"
               "                         (gvy_sum, "
               'f"{g}|{v}|{y}"),',
               "                         (std_sum, stf),\n"
               "                         (rsqr_sum, rqf),\n"
               "                         (gvy_sum, "
               'f"{g}|{v}|{y}"),', "judge final seg loop a")
    src = sub1(src,
               '                         (gvvvsktsams_sum,\n'
               '                          f"{g}|{v}|{y}|{c}|{s}|{t}|'
               '{a}|{m}|{stf}")):',
               '                         (gvvvsktsams_sum,\n'
               '                          f"{g}|{v}|{y}|{c}|{s}|{t}|'
               '{a}|{m}|{stf}"),\n                         '
               '(gvvvsktsamsr_sum,\n                          '
               'f"{g}|{v}|{y}|{c}|{s}|{t}|{a}|{m}|{stf}|{rqf}")):',
               "judge final seg loop b")
    src = sub1(src, '           "std_face_judgment": std_sum,',
               '           "std_face_judgment": std_sum,\n'
               '           "rsqr_face_judgment": rsqr_sum,',
               "judge final payload sums")
    src = sub1(src,
               '           "gate_vol_yang_vconf_streak_tstate_amp_mom_'
               'std_interaction_"\n           "judgment": '
               'gvvvsktsams_sum,',
               '           "gate_vol_yang_vconf_streak_tstate_amp_mom_'
               'std_interaction_"\n           "judgment": '
               'gvvvsktsams_sum,\n           "gate_vol_yang_vconf_'
               'streak_tstate_amp_mom_std_rsqr_interaction_"\n'
               '           "judgment": gvvvsktsamsr_sum,',
               "judge final payload interaction")
    src = sub1(src,
               '                             "gate + vol + yang + '
               'vconf + streak + "\n                             '
               '"tstate + amp + MOM + STD overlays carried "\n'
               '                             "per "\n'
               '                             "cell (frozen composition '
               'signal -> filter "\n                             '
               '"-> timing -> GATE -> VOL -> YANG -> VCONF "\n'
               '                             "-> STREAK -> TSTATE -> '
               'AMP -> MOM -> STD "\n                             '
               '"-> initial-stop; "',
               '                             "gate + vol + yang + '
               'vconf + streak + "\n                             '
               '"tstate + amp + MOM + STD + RSQR overlays carried "\n'
               '                             "per "\n'
               '                             "cell (frozen composition '
               'signal -> filter "\n                             '
               '"-> timing -> GATE -> VOL -> YANG -> VCONF "\n'
               '                             "-> STREAK -> TSTATE -> '
               'AMP -> MOM -> STD -> "\n                             '
               '"RSQR -> initial-stop; "', "judge final audit")
    src = sub1(src,
               '    print(f"std-face judgment: {json.dumps(std_sum, '
               'sort_keys=True)}")\n    print(f"gate x vol x yang x '
               'vconf x streak x tstate x amp x mom "\n          '
               'f"interaction judgment: "\n          f"{json.dumps'
               '(gvvvsktsam_sum, sort_keys=True)[:400]}")',
               '    print(f"std-face judgment: {json.dumps(std_sum, '
               'sort_keys=True)}")\n    print(f"rsqr-face judgment: '
               '{json.dumps(rsqr_sum, sort_keys=True)}")\n    '
               'print(f"gate x vol x yang x vconf x streak x tstate x '
               'amp x mom "\n          f"interaction judgment: "\n'
               '          f"{json.dumps(gvvvsktsam_sum, '
               'sort_keys=True)[:400]}")', "judge final prints")
    src = sub1(src,
               '                             "the protection-floor '
               'signal face with the "\n                             '
               '"mom overlay inserted before stop arming "\n'
               '                             "(W10 composition law); '
               'gate_flip_days_legL "',
               '                             "the protection-floor '
               'signal face with the "\n                             '
               '"std+rsqr overlays inserted before stop arming "\n'
               '                             "(W11/W12 composition law); '
               'gate_flip_days_legL "', "judge final audit stop note")
    src = sub1(src,
               '    """s4 D6 binding gate (W2 cmd_intake precedent on '
               'the W10 file\n    faces):',
               '    """s4 D6 binding gate (W2 cmd_intake precedent on '
               'the W11 file\n    faces):', "intake docstring")
    steps.append("judge slice: prep/cell/finalize rsqr wiring")

    # ---- 14. selftest surgery
    st_, a, b = segment(src, "def cmd_selftest() -> int:",
                        "def _build_parser():",
                        include_start=True, include_end=False)
    st_ = sub1(st_,
               "    zero cell evaluation): MOM causality / 139-bar "
               "warmup / NaN\n    comparison-artifact leg (pit-95 "
               "batch-95 + r431 erratum face) /\n    mom=none "
               "identity / eight-gate intersection / G-MOM probe "
               "anchors\n    (incl. eight-gate 256-cell 111/145 + "
               "extreme days 2/7 + core48\n    spread) / grammar "
               "structure / draw determinism / 20-source\n    "
               "exclusion loader / engine double-run determinism legs "
               "/ funnel\n    faces (dispatch / null-cell engine path "
               "/ CSV contract) + pit-95\n    finalize guards.\"\"\"",
               "    zero cell evaluation): MOM causality / 139-bar "
               "warmup / NaN\n    comparison-artifact leg (pit-95 "
               "batch-95 + r431 erratum face) /\n    mom=none "
               "identity / eight-gate intersection / G-MOM probe "
               "anchors\n    (incl. eight-gate 256-cell 111/145 + "
               "extreme days 2/7 + core48\n    spread) / G-RSQR probe "
               "anchors (nine-gate 512-cell 124/388 +\n    slope split "
               "213/128 + core48 spread) / grammar structure / draw\n"
               "    determinism / 24-source exclusion loader / engine "
               "double-run\n    determinism legs / funnel faces "
               "(dispatch / null-cell engine path /\n    CSV "
               "contract) + pit-95 finalize guards.\"\"\"",
               "selftest docstring")
    st_ = sub1(st_,
               '    _ok("L6a axis_combos == 31,352,832 (10,450,944 x 3 '
               'std-axis "\n        "values; W10 mom-face combos x '
               'len(AXIS_STD))",\n        g["axis_combos"] == 31352832'
               '\n        == tl10.AXIS_COMBOS * len(AXIS_STD))',
               '    _ok("L6a axis_combos == 94,058,496 (31,352,832 x 3 '
               'rsqr-axis "\n        "values; W11 std-face combos x '
               'len(AXIS_RSQR))",\n        g["axis_combos"] == 94058496'
               '\n        == tl11.AXIS_COMBOS * len(AXIS_RSQR))',
               "L6a")
    st_ = sub1(st_,
               '    _ok("L6b fourteen axes present, mom == frozen '
               'binary",\n        len(g["axes"]) == 14 and '
               'g["axes"]["mom"] == AXIS_MOM)',
               '    _ok("L6b fifteen axes present, rsqr == frozen '
               'three-value",\n        len(g["axes"]) == 15 and '
               'g["axes"]["rsqr"] == AXIS_RSQR)', "L6b")
    st_ = sub1(st_,
               '    _ok("L6c W11 seeds == SEED_REGISTRY berths '
               '(20317000/20317500/"\n        "20318000 berth re-take '
               'held, no re-pick)",',
               '    _ok("L6c W12 seeds == SEED_REGISTRY berths '
               '(20320500/20321000/"\n        "20321500 berths held, '
               'no re-pick)",', "L6c text")
    st_ = sub1(st_,
               '    _ok("L6d new sha16 constructively distinct from '
               'W1/MASS/W2-W9",\n        sha not in '
               'set(PRIOR_WAVE_SHA16.values())\n        and sha != '
               'tl9.FROZEN_SHA16,',
               '    _ok("L6d new sha16 constructively distinct from '
               'W1/MASS/W2-W11",\n        sha not in '
               'set(PRIOR_WAVE_SHA16.values())\n        and sha != '
               'tl11.FROZEN_SHA16,', "L6d")
    st_ = sub1(st_,
               '    _ok("L6e exclusion face rows mom=none-padded to '
               '13-long axis",\n        all(len(r["axis"]) == 14 and '
               'r["axis"][-1] == "none"\n            for r in '
               'g["exclusion"]\n            '
               '["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_'
               'none_face"]))',
               '    _ok("L6e exclusion face rows rsqr=none-padded to '
               '15-long axis",\n        all(len(r["axis"]) == 15 and '
               'r["axis"][-1] == "none"\n            for r in '
               'g["exclusion"]\n            '
               '["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_'
               'rsqr_none_face"]))', "L6e")
    st_ = sub1(st_,
               '        if os.path.exists(PROBE_FACTS_FILE):\n'
               '            pf = json.load(open(PROBE_FACTS_FILE, '
               'encoding="utf-8"))\n            sstate, serr = '
               '_std_state_full()\n            _ok("L7g probe-facts '
               'exact per-cell 256-grid cross-check "\n                '
               '"(r237 determinism law: every computed STD-face cell '
               '"\n                "== the git-tracked frozen probe '
               'face)",\n                serr is None\n                '
               'and sstate[2]["eight_gate_256cells"]\n                '
               '== pf.get("eight_gate_cells"),\n                serr '
               'or "std-face cells == probe facts")',
               '        if os.path.exists(PROBE_FACTS_FILE):\n'
               '            pf = json.load(open(PROBE_FACTS_FILE, '
               'encoding="utf-8"))\n            rstate2, rerr2 = '
               '_rsqr_state_full()\n            _ok("L7g probe-facts '
               'exact per-cell 512-grid cross-check "\n                '
               '"(r447 determinism law: every computed RSQR-face cell '
               '"\n                "== the git-tracked frozen probe '
               'face)",\n                rerr2 is None\n                '
               'and rstate2[2]["nine_gate_512cells"]\n                '
               '== pf.get("nine_gate_cells"),\n                rerr2 '
               'or "rsqr-face cells == probe facts")\n        # '
               'core48 member-level rsqr20 open-rate spread (r447 '
               'probe\n        # method verbatim; frozen-runner RSQR '
               'verbatim)\n        prices_r = tl1.load_core()\n'
               '        cut_r = pd.Timestamp(CUTOFF)\n        rates2 = '
               '{}\n        for sym, d2 in sorted(prices_r.items()):\n'
               '            d2 = d2[d2.index <= cut_r]\n            '
               'if len(d2) >= 260:\n                op2, wdec2, _ = '
               'rsqr_state_series({RSQR_MEMBER: d2})[:3]\n                '
               'if wdec2.any():\n                    rates2[str(sym)] '
               '= round(float(\n                        (op2 & '
               'wdec2).mean()), 4)\n        vals2 = sorted'
               '(rates2.values())\n        cf2 = RSQR_ANCHOR'
               '["core48_rsqr20_open_rate"]\n        _ok("L7i core48 '
               'rsqr20-open-rate spread (n 48 / min 0.0891 / "\n            '
               '"median 0.1009 / max 0.1183; r447 probe face)",\n            '
               'len(vals2) == cf2["n"] and vals2[0] == cf2["min"]\n'
               '            and vals2[len(vals2) // 2] == cf2'
               '["median"]\n            and vals2[-1] == cf2["max"],\n'
               '            f"n={len(vals2)} min={vals2[0] if vals2 '
               'else None}")', "L7g+L7i")
    st_ = sub1(st_,
               '    _ok("L8a Sobol draw determinism (same seed -> '
               'byte-identical "\n        "candidate incl. the '
               'mom+std axes, fourteen-tuple)",\n        '
               'json.dumps(c1[1], sort_keys=True) == json.dumps(c2[1],'
               '\n                                                        '
               'sort_keys=True)\n        and len(c1[1]["axis"]) == 14)',
               '    _ok("L8a Sobol draw determinism (same seed -> '
               'byte-identical "\n        "candidate incl. the '
               'std+rsqr axes, fifteen-tuple)",\n        '
               'json.dumps(c1[1], sort_keys=True) == json.dumps(c2[1],'
               '\n                                                        '
               'sort_keys=True)\n        and len(c1[1]["axis"]) == 15)',
               "L8a")
    st_ = sub1(st_,
               "    fourteen = [rng_a.integers(0, 4, n) for _ in "
               "range(14)]\n    rng_b = np.random.default_rng([SEED_GEN "
               "+ 0, 7919])\n    twelve = [rng_b.integers(0, 4, n) "
               "for _ in range(12)]\n    _ok(\"L8b MOM+STD append "
               "AFTER AMP in the rng stream (first twelve \"\n        "
               "\"axis arrays == W9-order stream verbatim, zero "
               "disturbance)\",\n        all(np.array_equal(a, b) for "
               "a, b in zip(fourteen, twelve)))",
               "    fifteen = [rng_a.integers(0, 4, n) for _ in "
               "range(15)]\n    rng_b = np.random.default_rng([SEED_GEN "
               "+ 0, 7919])\n    thirteen = [rng_b.integers(0, 4, n) "
               "for _ in range(13)]\n    _ok(\"L8b STD+RSQR append "
               "AFTER AMP in the rng stream (first thirteen \"\n        "
               "\"axis arrays == W10-order stream verbatim, zero "
               "disturbance)\",\n        all(np.array_equal(a, b) for "
               "a, b in zip(fifteen, thirteen)))", "L8b")
    st_ = sub1(st_,
               '    _ok("L9a exclusion loader: every row a 14-tuple '
               'axis, std=none "\n        "at 13 for ALL rows + mom at '
               '12 inside the frozen binary "\n        "domain + W10 '
               'real-mom rows present (20 sources; W1-W9 "\n        '
               '"sources mom=none, W10 survivors/judged carry real '
               'values)",\n        all(len(r["axis"]) == 14 and '
               'r["axis"][13] == "none"\n            and r["axis"][12] '
               'in AXIS_MOM for r in rows10)\n        and '
               'any(r["axis"][12] == "mom_oversold"\n                '
               'for r in rows10)\n        and '
               '{"w1_screen_survivors", "mass_screen_survivors",\n'
               '             "w9_screen_survivors", '
               '"w9_judge_products",\n             '
               '"w10_screen_survivors", "w10_judge_products",\n'
               '             "judged_supply_weighting"} <= set(disc10))',
               '    _ok("L9a exclusion loader: every row a 15-tuple '
               'axis, rsqr=none "\n        "at 14 for ALL rows + std at '
               '13 inside the frozen three-value "\n        "domain + '
               'W11 real-std rows present (24 sources; W1-W10 "\n'
               '        "sources std=none, W11 survivors/judged carry '
               'real values)",\n        all(len(r["axis"]) == 15 and '
               'r["axis"][14] == "none"\n            and r["axis"][13] '
               'in AXIS_STD for r in rows10)\n        and '
               'any(r["axis"][13] in ("std20_hi", "std10_hi")\n'
               '                for r in rows10)\n        and '
               '{"w1_screen_survivors", "mass_screen_survivors",\n'
               '             "w9_screen_survivors", '
               '"w9_judge_products",\n             '
               '"w10_screen_survivors", "w10_judge_products",\n'
               '             "@@W11TAG3@@", "@@W11TAG4@@",\n'
               '             "judged_supply_weighting"} <= set(disc10))',
               "L9a")
    st_ = sub1(st_,
               '        "== 243 (generate-time re-declare window, '
               'prereg sec.1 TEN "\n        "judge sources; W9-JUDGE '
               'landed 2026-09-29 17:47:46)"',
               '        "== 243 (generate-time re-declare window, '
               'prereg sec.1 TWELVE "\n        "judge sources; W9-JUDGE '
               'landed 2026-09-29 17:47:46)"', "L9b text")
    st_ = sub1(st_,
               '    miss = _excluded_w11({**hit_key,\n                          '
               '"axis": [*hit_key["axis"][:12],\n                                   '
               '"mom_oversold", "none"]},\n                         '
               'rows10)\n    _ok("L10b mom in {mom_oversold} = '
               'new-syntax legal cell, "\n        "never excluded",\n'
               '        miss is None)',
               '    miss = _excluded_w12({**hit_key,\n                          '
               '"axis": [*hit_key["axis"][:14],\n                                   '
               '"rsqr20_hi"]},\n                         rows10)\n'
               '    _ok("L10b rsqr in {rsqr20_hi, rsqr10_hi} = '
               'new-syntax legal cell, "\n        "never excluded",\n'
               '        miss is None)', "L10b")
    st_ = sub1(st_, "    ss3 = std_state_series(frames3)\n",
               "    ss3 = std_state_series(frames3)\n    rq3 = "
               "rsqr_state_series(frames3)\n", "L12 rq3")
    st_ = sub1(st_, "    ss5 = std_state_series(frames5)\n",
               "    ss5 = std_state_series(frames5)\n    rq5 = "
               "rsqr_state_series(frames5)\n", "L12 rq5")
    st_ = sub1(st_,
               '            "axis": ["none", "time_stop_5d", '
               '"equal_weight",\n                     "daily_signal", '
               '"none", "none", "none", "none",\n                     '
               '"none", "none", "none", "none", "none",\n'
               '                     "none"]}',
               '            "axis": ["none", "time_stop_5d", '
               '"equal_weight",\n                     "daily_signal", '
               '"none", "none", "none", "none",\n                     '
               '"none", "none", "none", "none", "none",\n'
               '                     "none", "none"]}',
               "L13 base axis fifteen")
    st_ = sub1(st_,
               '        "none", "none", "none", "none", "none", gs3, '
               'vs3, ys3, cs3,\n        sk3, ts3, as3, ms3, ss3)',
               '        "none", "none", "none", "none", "none", '
               '"none", gs3,\n        vs3, ys3, cs3, sk3, ts3, as3, '
               'ms3, ss3, rq3)', "L12 mask calls gs3 none")
    st_ = sub1(st_,
               '        "none", "none", "none", "mom_oversold", '
               '"none", gs3, vs3,\n        ys3, cs3, sk3, ts3, as3, '
               'ms3, ss3)',
               '        "none", "none", "none", "mom_oversold", '
               '"none", "none", gs3,\n        vs3, ys3, cs3, sk3, ts3, '
               'as3, ms3, ss3, rq3)', "L12 mask calls gs3 mom")
    st_ = sub1(st_,
               '        "none", "none", "none", "none", "none", gs5, '
               'vs5, ys5, cs5,\n        sk5, ts5, as5, ms5, ss5)',
               '        "none", "none", "none", "none", "none", '
               '"none", gs5,\n        vs5, ys5, cs5, sk5, ts5, as5, '
               'ms5, ss5, rq5)', "L12 mask calls gs5 none")
    st_ = sub1(st_,
               '        "none", "none", "none", "mom_oversold", '
               '"none", gs5, vs5,\n        ys5, cs5, sk5, ts5, as5, '
               'ms5, ss5)',
               '        "none", "none", "none", "mom_oversold", '
               '"none", "none", gs5,\n        vs5, ys5, cs5, sk5, ts5, '
               'as5, ms5, ss5, rq5)', "L12 mask calls gs5 mom")
    st_ = sub1(st_,
               '    eq10, tr10, m10, _, _, _, _, _, _, _, sz10, tz10, '
               'az10, mz10, \\\n        sdz10 = \\\n        '
               'run_candidate_curve_w11(\n            base, None, '
               'frames3, P3, st3, gate_state=gs3, vol_state=vs3,\n'
               '            yang_state=ys3, vconf_state=cs3, '
               'streak_state=sk3,\n            tstate_state=ts3, '
               'amp_state=as3, mom_state=ms3,\n            '
               'std_state=ss3)',
               '    eq10, tr10, m10, _, _, _, _, _, _, _, sz10, tz10, '
               'az10, mz10, \\\n        sdz10, rz10 = \\\n        '
               'run_candidate_curve_w12(\n            base, None, '
               'frames3, P3, st3, gate_state=gs3, vol_state=vs3,\n'
               '            yang_state=ys3, vconf_state=cs3, '
               'streak_state=sk3,\n            tstate_state=ts3, '
               'amp_state=as3, mom_state=ms3,\n            '
               'std_state=ss3, rsqr_state=rq3)', "L13a")
    st_ = sub1(st_,
               '    _ok("L13b engine double-run byte-identity '
               '(determinism leg) + "\n        "15-tuple return shape '
               '(mom_zeroed carried)",\n        list(eq10.values) == '
               'list(eq10b.values) and sz10 == sz10b\n        and tz10 '
               '== tz10b and az10 == az10b and mz10 == mz10b == 0)',
               '    _ok("L13b engine double-run byte-identity '
               '(determinism leg) + "\n        "16-tuple return shape '
               '(rsqr_zeroed carried)",\n        list(eq10.values) == '
               'list(eq10b.values) and sz10 == sz10b\n        and tz10 '
               '== tz10b and az10 == az10b and mz10 == mz10b == 0\n'
               '        and rz10 == 0)', "L13b check")
    st_ = sub1(st_,
               '    eq10b, _, _, _, _, _, _, _, _, _, sz10b, tz10b, '
               'az10b, mz10b, \\\n        _ = \\\n        '
               'run_candidate_curve_w11(\n            dict(base, '
               'candidate_id="ST-B-0001"), None, frames3, P3,\n'
               '            st3, gate_state=gs3, vol_state=vs3, '
               'yang_state=ys3,\n            vconf_state=cs3, '
               'streak_state=sk3, tstate_state=ts3,\n            '
               'amp_state=as3, mom_state=ms3, std_state=ss3)',
               '    eq10b, _, _, _, _, _, _, _, _, _, sz10b, tz10b, '
               'az10b, mz10b, \\\n        _, _ = \\\n        '
               'run_candidate_curve_w12(\n            dict(base, '
               'candidate_id="ST-B-0001"), None, frames3, P3,\n'
               '            st3, gate_state=gs3, vol_state=vs3, '
               'yang_state=ys3,\n            vconf_state=cs3, '
               'streak_state=sk3, tstate_state=ts3,\n            '
               'amp_state=as3, mom_state=ms3, std_state=ss3,\n'
               '            rsqr_state=rq3)', "L13b call")
    st_ = sub1(st_,
               '    eq5n, tr5n, m5n, _, _, _, _, _, _, _, _, _, az5n, '
               'mz5n, _ = \\\n        run_candidate_curve_w11(\n'
               '            dict(base, axis=list(base["axis"])), None, '
               'frames5, P5,\n            st5, gate_state=gs5, '
               'vol_state=vs5, yang_state=ys5,\n            '
               'vconf_state=cs5, streak_state=sk5, tstate_state=ts5,\n'
               '            amp_state=as5, mom_state=ms5, '
               'std_state=ss5)',
               '    eq5n, tr5n, m5n, _, _, _, _, _, _, _, _, _, az5n, '
               'mz5n, _, _ = \\\n        run_candidate_curve_w12(\n'
               '            dict(base, axis=list(base["axis"])), None, '
               'frames5, P5,\n            st5, gate_state=gs5, '
               'vol_state=vs5, yang_state=ys5,\n            '
               'vconf_state=cs5, streak_state=sk5, tstate_state=ts5,\n'
               '            amp_state=as5, mom_state=ms5, '
               'std_state=ss5,\n            rsqr_state=rq5)', "L13c")
    st_ = sub1(st_,
               '    eq5o, tr5o, m5o, _, _, _, _, _, _, _, _, _, az5o, '
               'mz5o, _ = \\\n        run_candidate_curve_w11(\n'
               '            dict(base, axis=[*base["axis"][:12], '
               '"mom_oversold",\n                             "none"]), '
               'None,\n            frames5, P5, st5, gate_state=gs5, '
               'vol_state=vs5,\n            yang_state=ys5, '
               'vconf_state=cs5, streak_state=sk5,\n            '
               'tstate_state=ts5, amp_state=as5, mom_state=ms5,\n'
               '            std_state=ss5)',
               '    eq5o, tr5o, m5o, _, _, _, _, _, _, _, _, _, az5o, '
               'mz5o, _, _ = \\\n        run_candidate_curve_w12(\n'
               '            dict(base, axis=[*base["axis"][:12], '
               '"mom_oversold",\n                             "none", '
               '"none"]), None,\n            frames5, P5, st5, '
               'gate_state=gs5, vol_state=vs5,\n            '
               'yang_state=ys5, vconf_state=cs5, streak_state=sk5,\n'
               '            tstate_state=ts5, amp_state=as5, '
               'mom_state=ms5,\n            std_state=ss5, '
               'rsqr_state=rq5)', "L13d")
    st_ = sub1(st_,
               '    eq3o, tr3o, m3o, _, _, _, _, _, _, _, _, _, az3o, '
               'mz3o, _ = \\\n        run_candidate_curve_w11(\n'
               '            dict(base, axis=[*base["axis"][:12], '
               '"mom_oversold",\n                             "none"]), '
               'None,\n            frames3, P3, st3, gate_state=gs3, '
               'vol_state=vs3,\n            yang_state=ys3, '
               'vconf_state=cs3, streak_state=sk3,\n            '
               'tstate_state=ts3, amp_state=as3, mom_state=ms3,\n'
               '            std_state=ss3)',
               '    eq3o, tr3o, m3o, _, _, _, _, _, _, _, _, _, az3o, '
               'mz3o, _, _ = \\\n        run_candidate_curve_w12(\n'
               '            dict(base, axis=[*base["axis"][:12], '
               '"mom_oversold",\n                             "none", '
               '"none"]), None,\n            frames3, P3, st3, '
               'gate_state=gs3, vol_state=vs3,\n            '
               'yang_state=ys3, vconf_state=cs3, streak_state=sk3,\n'
               '            tstate_state=ts3, amp_state=as3, '
               'mom_state=ms3,\n            std_state=ss3, '
               'rsqr_state=rq3)', "L13e")
    st_ = sub1(st_,
               '    _ok("L14 null-axis draw determinism + '
               'FOURTEEN-tuple with mom+std "\n        "in the frozen '
               'domains (W11 null berth 20317500)",\n        p1 == p2 '
               'and ax1 == ax2 and len(ax1) == 14\n        and ax1[12] '
               'in AXIS_MOM and ax1[13] in AXIS_STD\n        and '
               'ax1[11] in tl9.AXIS_AMP\n        and ax1[10] in '
               'tl8.AXIS_TSTATE and ax1[9] in tl7.AXIS_STREAK\n'
               '        and ax1[4] in tl2.AXIS_STOP)',
               '    _ok("L14 null-axis draw determinism + '
               'FIFTEEN-tuple with std+rsqr "\n        "in the frozen '
               'domains (W12 null berth 20321000)",\n        p1 == p2 '
               'and ax1 == ax2 and len(ax1) == 15\n        and ax1[12] '
               'in AXIS_MOM and ax1[13] in AXIS_STD\n        and '
               'ax1[14] in AXIS_RSQR\n        and ax1[11] in '
               'tl9.AXIS_AMP\n        and ax1[10] in tl8.AXIS_TSTATE '
               'and ax1[9] in tl7.AXIS_STREAK\n        and ax1[4] in '
               'tl2.AXIS_STOP)', "L14")
    st_ = sub1(st_,
               "    mom_dom = (ax0[12] in AXIS_MOM and ax0[13] in "
               "AXIS_STD\n               and ax0[4] in tl2.AXIS_STOP "
               "and len(ax0) == 14)",
               "    mom_dom = (ax0[12] in AXIS_MOM and ax0[13] in "
               "AXIS_STD\n               and ax0[14] in AXIS_RSQR\n"
               "               and ax0[4] in tl2.AXIS_STOP and "
               "len(ax0) == 15)", "L15b dom")
    st_ = sub1(st_,
               "    eqn, trn, mtn, prn, pt, frn, gzn, vzn, yzn, czn, "
               "szn, tzn, azn, \\\n        mzn, _ = \\\n        "
               "run_candidate_curve_w11(\n            {\"module\": "
               "\"null\", \"fn\": \"random_signal\",\n             "
               "\"sig_params\": {\"p_on\": p_on0}, \"axis\": ax0,\n"
               "             \"candidate_id\": \"W11-NULL-0000\", "
               "\"family\": \"NULL\"},\n            None, frames3, P3, "
               "st3, gate_state=gs3, vol_state=vs3,\n            "
               "yang_state=ys3, vconf_state=cs3, streak_state=sk3,\n"
               "            tstate_state=ts3, amp_state=as3, "
               "mom_state=ms3,\n            std_state=ss3, "
               "rng_matrix=mat0, p_on=p_on0)",
               "    eqn, trn, mtn, prn, pt, frn, gzn, vzn, yzn, czn, "
               "szn, tzn, azn, \\\n        mzn, _, rzn = \\\n        "
               "run_candidate_curve_w12(\n            {\"module\": "
               "\"null\", \"fn\": \"random_signal\",\n             "
               "\"sig_params\": {\"p_on\": p_on0}, \"axis\": ax0,\n"
               "             \"candidate_id\": \"W12-NULL-0000\", "
               "\"family\": \"NULL\"},\n            None, frames3, P3, "
               "st3, gate_state=gs3, vol_state=vs3,\n            "
               "yang_state=ys3, vconf_state=cs3, streak_state=sk3,\n"
               "            tstate_state=ts3, amp_state=as3, "
               "mom_state=ms3,\n            std_state=ss3, "
               "rsqr_state=rq3, rng_matrix=mat0, p_on=p_on0)",
               "L15b call 1")
    st_ = sub1(st_,
               "    eqnb, _, _, _, _, _, _, _, _, _, _, _, _, mznb, _ "
               "= \\\n        run_candidate_curve_w11(\n            "
               "{\"module\": \"null\", \"fn\": \"random_signal\",\n"
               "             \"sig_params\": {\"p_on\": p_on0b}, "
               "\"axis\": ax0b,\n             \"candidate_id\": "
               "\"W11-NULL-0000\", \"family\": \"NULL\"},\n            "
               "None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,\n"
               "            yang_state=ys3, vconf_state=cs3, "
               "streak_state=sk3,\n            tstate_state=ts3, "
               "amp_state=as3, mom_state=ms3,\n            "
               "std_state=ss3, rng_matrix=mat0b, p_on=p_on0b)",
               "    eqnb, _, _, _, _, _, _, _, _, _, _, _, _, mznb, _, "
               "rznb = \\\n        run_candidate_curve_w12(\n        "
               "    {\"module\": \"null\", \"fn\": \"random_signal\",\n"
               "             \"sig_params\": {\"p_on\": p_on0b}, "
               "\"axis\": ax0b,\n             \"candidate_id\": "
               "\"W12-NULL-0000\", \"family\": \"NULL\"},\n            "
               "None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,\n"
               "            yang_state=ys3, vconf_state=cs3, "
               "streak_state=sk3,\n            tstate_state=ts3, "
               "amp_state=as3, mom_state=ms3,\n            "
               "std_state=ss3, rsqr_state=rq3, rng_matrix=mat0b, "
               "p_on=p_on0b)", "L15b call 2")
    st_ = sub1(st_,
               '    _ok("L15b null-cell engine path: fourteen-tuple '
               'null draw "\n        "deterministic + mom axis '
               'in-domain + engine 14-tuple return "\n        "+ '
               'double-run byte-identity (screen null-family path)",\n'
               '        p_on0 == p_on0b and ax0 == ax0b and mom_dom\n'
               '        and len(eqn) == len(P3["close"].index) and '
               'mzn >= 0\n        and list(eqn.values) == '
               'list(eqnb.values) and mzn == mznb)',
               '    _ok("L15b null-cell engine path: fifteen-tuple '
               'null draw "\n        "deterministic + rsqr axis '
               'in-domain + engine 16-tuple return "\n        "+ '
               'double-run byte-identity (screen null-family path)",\n'
               '        p_on0 == p_on0b and ax0 == ax0b and mom_dom\n'
               '        and len(eqn) == len(P3["close"].index) and '
               'mzn >= 0\n        and list(eqn.values) == '
               'list(eqnb.values) and mzn == mznb\n        and rzn == '
               'rznb)', "L15b check")
    st_ = sub1(st_,
               '    _ok("L15c screen CSV contract carries the mom+std '
               'columns in the "\n        "frozen order '
               '(cell_id/candidate_id head + std pair before "\n        '
               '"survives_screen)",\n        csv_cols_screen_w11[:2] '
               '== ["cell_id", "candidate_id"]\n        and '
               'csv_cols_screen_w11[-3:] == ["std_face", '
               '"std_zeroed",\n                                         '
               '"survives_screen"]\n        and "mom_face" in '
               'csv_cols_screen_w11\n        and {"gate_zeroed", '
               '"vol_zeroed", "yang_zeroed", "vconf_zeroed",\n'
               '             "streak_zeroed", "tstate_zeroed", '
               '"amp_zeroed",\n             "mom_zeroed", '
               '"std_zeroed"} <= set(csv_cols_screen_w11))',
               '    _ok("L15c screen CSV contract carries the '
               'mom+std+rsqr columns in the "\n        "frozen order '
               '(cell_id/candidate_id head + rsqr pair before "\n'
               '        "survives_screen)",\n        '
               'csv_cols_screen_w12[:2] == ["cell_id", '
               '"candidate_id"]\n        and csv_cols_screen_w12[-3:] '
               '== ["rsqr_face", "rsqr_zeroed",\n                                   '
               '      "survives_screen"]\n        and "mom_face" in '
               'csv_cols_screen_w12\n        and {"gate_zeroed", '
               '"vol_zeroed", "yang_zeroed", "vconf_zeroed",\n'
               '             "streak_zeroed", "tstate_zeroed", '
               '"amp_zeroed",\n             "mom_zeroed", '
               '"std_zeroed", "rsqr_zeroed"} <= set'
               '(csv_cols_screen_w12))', "L15c")
    st_ = sub1(st_,
               '    print(f"\\nselftest: {n_pass}/{n_leg} PASS "\n'
               '          f"(scope: slice-1 mom layer + G-MOM + '
               'fourteen-tuple grammar "\n          f"+ machinery: '
               'effective mask / curve runner parity / null "\n'
               '          f"draw / 20-source exclusion loader + funnel '
               'faces: dispatch "\n          f"/ null-cell engine '
               'path / CSV contract + pit-95 finalize "\n          '
               'f"idempotency guard state-adaptive legs; zero live '
               'cells "\n          f"burned, zero numbers '
               'fabricated)")',
               '    print(f"\\nselftest: {n_pass}/{n_leg} PASS "\n'
               '          f"(scope: W12 rsqr layer + G-RSQR + '
               'fifteen-tuple grammar "\n          f"+ machinery: '
               'effective mask / curve runner parity / null "\n'
               '          f"draw / 24-source exclusion loader + funnel '
               'faces: dispatch "\n          f"/ null-cell engine '
               'path / CSV contract + pit-95 finalize "\n          '
               'f"idempotency guard state-adaptive legs; zero live '
               'cells "\n          f"burned, zero numbers '
               'fabricated)")', "selftest scope print")
    src = src[:a] + st_ + src[b:]
    steps.append("selftest: L6/L7g/L7i/L8/L9/L10/L12/L13/L14/L15 "
                 "fifteen-tuple faces")

    # ---- 15. residual global mechanical pass
    # protect the W11-source literals + import from the renames
    src = src.replace(
        '"@@W11SRC1@@",',
        '"w11_screen.json survivors (generate-time)",')
    src = src.replace(
        '"@@W11SRC2@@"],',
        '"w11_judge products (generate-time real-read "\n'
        '               "re-declare window; W11-JUDGE landed '
        '2026-09-30 "\n               "01:47:40 = TWELFTH source)"],')
    src = src.replace('"@@W11TAG1@@"', '"w11_screen_survivor"')
    src = src.replace('"@@W11TAG2@@"', '"w11_judged"')
    src = src.replace('"@@W11TAG3@@"', '"w11_screen_survivors"')
    src = src.replace('"@@W11TAG4@@"', '"w11_judge_products"')
    src = src.replace("import trial_labor_w11 as tl11",
                      "import @@TL11IMPORT@@ as tl11")
    resid = [
        ("csv_cols_screen_w11", "csv_cols_screen_w12"),
        ("_screen_cell_w11", "_screen_cell_w12"),
        ("_cell_list_w11", "_cell_list_w12"),
        ("_overlay_stop_disclosure_w11", "_overlay_stop_disclosure_w12"),
        ("_judge_cell_w11", "_judge_cell_w12"),
        ("_dual_nulls_w11", "_dual_nulls_w12"),
        ("draw_candidate_sobol_w11", "draw_candidate_sobol_w12"),
        ("_load_exclusion_rows_w11", "_load_exclusion_rows_w12"),
        ("_excluded_w11", "_excluded_w12"),
        ("_effective_signal_mask_w11", "_effective_signal_mask_w12"),
        ("run_candidate_curve_w11", "run_candidate_curve_w12"),
        ("_null_axis_draw_w11", "_null_axis_draw_w12"),
        ("build_grammar_w11", "build_grammar_w12"),
        ("TRIAL_LABOR_W11", "TRIAL_LABOR_W12"),
        ("TRIAL_LAB_W11", "TRIAL_LAB_W12"),
        ("TRIAL-LABOR-W11", "TRIAL-LABOR-W12"),
        ("trial_labor_w11", "trial_labor_w12"),
        ('"W11-', '"W12-'),
        ("W11-NULL", "W12-NULL"),
        ("w11_", "w12_"),
        ("20317000", "20320500"),
        ("20317500", "20321000"),
        ("20318000", "20321500"),
        ("FOURTEEN-tuple", "FIFTEEN-tuple"),
        ("FOURTEEN-gate", "FIFTEEN-gate"),
        ("fourteen-tuple", "fifteen-tuple"),
        ("FOURTEEN-", "FIFTEEN-"),
        ("(MOM+STD fourteen-gate wave)", "(MOM+STD+RSQR fifteen-gate "
         "wave)"),
        ("20-source", "24-source"),
        ("22 real-reads", "24 real-reads"),
        ("T-123", "T-124"),
    ]
    for old, new in resid:
        src = src.replace(old, new)
    src = src.replace("@@TL11IMPORT@@", "trial_labor_w11")
    # residual-rename overreach guard: module-face calls into the FROZEN
    # tl11 must keep W11-side names (r445 fix-first: the global residual
    # renames hit tl11.build_grammar_w11 / tl11._overlay_stop_disclosure_w11)
    src = re.sub(r"tl11\.([A-Za-z_][A-Za-z0-9_]*)_w12\b",
                 r"tl11.\1_w11", src)
    steps.append("residual pass: identifiers/payloads "
                 "(screen/judge/intake/selftest legs)")

    # ---- 16. axis-length guards + report
    flags = []
    for pat in ('len(axis) == 14', 'axis"][13] != "none"',
                "fourteen-tuple", "FOURTEEN-tuple", "THIRTEEN-tuple"):
        hits = [m.start() for m in re.finditer(re.escape(pat), src)]
        if hits:
            flags.append(f"REVIEW-AT-SLICE-B {pat}: {len(hits)} hits")
    n_axis14 = len(re.findall(re.escape('cand["axis"][14]'), src))
    report = {
        "src": SRC, "dst": DST, "steps": steps,
        "axis14_refs": n_axis14, "review_flags": flags,
        "rsqr_anchor_checks": {
            "nonzero": 124, "empty": 388, "decidable": 3363,
            "rsqr20_open": 341, "rsqr10_open": 332,
            "first_decidable": 120, "all_decidable": 3305,
            "slope_split": "213/128"},
        "generated": os.path.getmtime(SRC),
    }
    with open(DST, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(src)
    with open(REPORT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print("SURGEON-OK: draft written %s (%d lines) -- %d steps" %
          (DST, src.count("\n"), len(steps)))
    for s in steps:
        print("  - " + s)
    for f in flags:
        print("  ! " + f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
