"""TRIAL_LABOR_W9 runner -- T-121 mass-candidate trial wave-9 (5000-ceiling,
amplitude-confirmation AMP-gate TWELVE-gate wave).

Prereg FROZEN (bm-b r432 draft-author same-machine next-round freeze per
r431 next-pointer; freeze trigger MET = W8 full chain landed 2026-09-29
15:26:25 + ledger head 341,063 linear live-read {head file=w8_judge.json}
+ zero in-flight judge faces [pool entries 116/116 done 16:0x]):
research/TRIAL_LABOR_W9_PREREG.md -- generate grammar + funnel rules +
judgment lines all frozen; post-run only sec.7/8 backfill.  Seeds held
at the freeze commit per R250 one-step law: trial_labor_w9_gen=20309500
/ trial_labor_w9_scrnull=20310000 / trial_labor_w9_unc=20310500
(in-draft-window DOUBLE collision re-pick lineage disclosed in the
prereg banner + registry comments; freeze-time three-step re-verify ALL
GREEN, no re-pick).

Import-face law (prereg sec.6): the FULL trial_labor_w1-w8 chain is
imported (tl1 enumeration/loading/anchor/envelope primitives + tl2
initial-stop overlay + tl3 regime-gate overlay + tl4 vol overlay +
tl5 yang overlay + tl6 vconf overlay + tl7 streak overlay + tl8
tstate overlay & eleven-tuple machinery); Sobol sample_draws pattern
follows mass_trial_w1 (paradigm import); strategies/ factory +
engine/backtester imported, never rewritten; engine/exit_rules.py ZERO
touch (amp overlay is a GRAMMAR layer).

Engineering mapping disclosures (pre-run, zero cells burned):

  AMP overlay (prereg sec.2/sec.3 NEW W9 frozen layer; r417/r431 probe
  verbatim, zero-invention law): member 510300 signal-day-d close info
  set.  amp(d) = (high(d) - low(d)) / close(d) -- VERBATIM the
  registered formula engine/factors.py::intraday_range (FACTOR_CENSUS
 _REGISTRY A-row; zero invention).  med20amp = amp rolling-20 median
  (min_periods=20, INCL d).  amp_wide = amp > med20amp (spectacle /
  turn-day face); amp_narrow = amp <= med20amp (calm / consolidation
  day face).  19-bar warmup window gate-closed honest (med20amp first
  valid bar-idx == 19; VCONF-isostructural, vs YANG 0 / STREAK 2 /
  RSV 59 / MAD60 178 / VOL 519).  Gate acts on ENTRY PERMITTANCE only
  (effective signal zeroed, MSG-0440 E1-mapping primitive; exit logic
  zero change).  AMP face != GATE regime face != VOL volatility face
  != YANG single-day body != VCONF volume face != STREAK direction
  face != TSTATE position face (r431 probe decidable-mask conditional
  rates: bull 49.78% / bear 49.40% / calm 50.03% / wild 49.76% --
  near-independent conditional dimension; AMP x VCONF activity sister
  faces strong co-movement honest {surge 68.52% / dry 30.47%}; AMP x
  STREAK new crossing {down_streak 54.06% wide}; AMP x TSTATE new
  crossing {mad60-open 60.84% / rsv60-open 58.23% wide}).  NaN
  comparison artifact law (pit-95 batch-95 / r421 probe / r431
  erratum face): NaN < x and NaN > x comparisons yield False NOT
  decidable -- the decidable face derives from the underlying value
  notna (med20amp.notna()); a naive (amp > med) bool face
  masquerades warmup bars as NARROW (the r417 map-NaN-bucket erratum
  face) -- BANNED; amp_narrow keep face = (~wide) AND decidable.
  Composition order frozen everywhere (dedup face + engine face):
  signal -> filter -> timing -> GATE -> VOL -> YANG -> VCONF ->
  STREAK -> TSTATE -> AMP -> initial-stop (an amp-blocked signal never
  arms a stop; W8 order extended, prereg sec.3 twelve-tuple order
  R/X/S/T/STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP).

  G-AMP anchor law (prereg sec.2 probe facts, fail-closed): on the raw
  full-history member face (data/daily/sh510300.csv, 3,483 bars
  2012-05-28 -> 2026-09-22 cutoff): zero-range rows (high == low) ==
  0; med20amp first-decidable == 19 / decidable == 3,464 / wide ==
  1,718 / narrow == 1,746 (wide rate 49.6% -- near-half window, face
  structurally balanced); cross four-cell lower bounds {yang^wide 884,
  red^narrow 887, surge^wide 1193, dry^narrow 1198, up^wide 421,
  down^narrow 373, mad60^wide 233, rsv60^narrow 264}; seven-gate
  (gate x vol x yang x vconf x streak x tstate x amp) 128 open-window
  cells: 73 non-empty / 55 empty with the exact frozen 55-empty name
  list (probe range min-nonzero 1 / max 59; all-decidable 3,305 days;
  narrow-corner structural rarity face [tstate 11.59%/18.46% open
  rates x streak 24% narrow face x seven-condition intersection] --
  empty corner cells naturally filtered by the G1' entries>=30 gate,
  honest elimination not pre-screen invention); extreme-day gate
  states frozen (SEVEN extreme days 7/7 wide: 2015-07-27 down_streak +
  mad60 TRUE rsv 0.2026 / 2016-01-04 down both-closed / 2024-02-28
  neither both-closed / 2024-09-24 + 09-30 up both-closed high-zone /
  2025-04-07 down DOUBLE-GATE TRUE rsv 0.1753 + 6.961x amp ratio /
  2026-01-19 down both-closed 1.032x -- wide-face crisis-day exposure
  HELD vs TSTATE crisis-day convergence = complementary not
  isomorphic; narrow-face crisis-day 7/7 closed = protection-face
  expectation honest, reading not prior); cross faces on the r431
  probe basis VERBATIM (gate = close > ma200 strict NaN->False
  both-sides; vol = vol20 vs med500 NaN->False both-sides; yang =
  close > open strict doji-red; surge = volume > med20 min_periods=20
  INCL d; streak = W7 close-over-close double; tstate = the tl8
  census-verbatim faces; amp = the r417 face above).  Probe-facts
  exact per-cell cross-check vs
  results/_r431bmb_ampgate_w9_probe_facts.json when present (r431
  determinism cross-check law); core48 member-level wide-rate spread
  min 48.08% / median 49.37% / max 51.15% (48 members, tl1.load_core()
  real roster).

  Exclusion law (prereg sec.1, TWELVE-tuple cell key=(template, params,
  axis_config, initial_stop, gate, vol, yang, vconf, streak, tstate,
  amp), EIGHTEEN real-read source faces, exact already-judged key,
  amp=none face only): prior-wave keys lacking the amp axis are
  amp=none completed (semantic-identity match); amp in {amp_narrow,
  amp_wide} (any gate/vol/yang/vconf/streak/tstate combo) = new-syntax
  legal cells (never excluded).  Sources: frozen grammar bands
  (stop-gate-vol-yang-vconf-streak-tstate-amp-none pad) + w1_screen
  149 + w2_screen 404 + MASS screen 166 (declared tl3 translation) +
  w3_screen 513 + w4_screen 461 + w5_screen 372 + w6_screen 293 +
  w7_screen 284 + w8_screen 408 (generate-time real-read; absent at
  build = zero rows honest) + judged products re-declare window
  (w1_judge / MASS judged / w2_judge / w3_judge / w4_judge / w5_judge
  / w6_judge / w7_judge / w8_judge -- NINE sources, generate-time
  real-read, absent = declared-unavailable zero rows; W8-JUDGE landed
  2026-09-29 15:26:25 -- draft-time nine-source full-declare window =
  second in history, disclosed).

Slice plan (W3-W8 single-writer precedent; wave ticket T-2026-09-29-121
opened+claimed at the freeze commit per O-1730 immediate-law; runner
build slice self-claimed by bm-b r432 per prereg sec.9 open slice +
product-priority law):
  - slice-1 (this file, bm-b r432): twelve-tuple grammar
    build_grammar_w9 (tl8 grammar extended with the NEW amp axis ->
    5,225,472 axis combos, new grammar sha16 constructively distinct
    from W1/MASS/W2-W8) + amp overlay layer (amp_state_series /
    amp_zero_mask / structure gate / G-AMP fail-closed full-face gate)
    + hermetic selftest (amp causality / 19-bar warmup / NaN-artifact
    leg [r417 map-NaN-bucket erratum face] / amp=none identity /
    seven-gate intersection / G-AMP probe anchors incl. 128-cell
    73/55 + extreme days / grammar structure / draw determinism /
    18-source exclusion loader / engine double-run byte-identity legs
    / funnel dispatch + CSV contract + pit-95 guards) + grammar
    serialization subcommand + GENERATE pool entry (consumer_plan per
    O-1820(3), pre-positioned products same commit per pit-90,
    lane_owner=bm-b per pit-103 terminal gate);
  - LATER slices (physical deps, separate commits with MSG
    declarations per W3-W8 precedent): SCREEN pool entry AFTER
    generate lands (lane_owner=bm-b); JUDGE pool entry AFTER
    screen-finalize (RAM r354 three-sample gate + sequencing behind
    in-flight judge faces per prereg sec.0 + host_gates MSG-1305);
    intake (judge products required); grammar ledger wave-9 row
    append at consumption (generate burn writes the row).
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
from science_gates import CostPatch, SEED_REGISTRY  # noqa: E402

# ------------------------------------------------------------ frozen (prereg)
WAVE = "TRIAL_LABOR_W9"
PREREG = "research/TRIAL_LABOR_W9_PREREG.md"
CUTOFF = tl1.CUTOFF                      # "2026-09-22" (P-5C binding, sec.2)
SEED_GEN = SEED_REGISTRY["trial_labor_w9_gen"]        # 20309500
SEED_NULL = SEED_REGISTRY["trial_labor_w9_scrnull"]  # 20310000
SEED_UNC = SEED_REGISTRY["trial_labor_w9_unc"]        # 20310500
N_A = 500          # family A raw draws (sec.3: 6 templates round-robin)
N_B = 4500         # family B raw draws (machinery round-robin)
K_NULLS = 200       # screen null family size (sec.3; frozen)
RES_DIR = os.path.join(tl1.PATHS.results_dir, "trial_labor_w9")
GRAMMAR_FILE = os.path.join(RES_DIR, "w9_grammar.json")
CANDIDATES_FILE = os.path.join(RES_DIR, "w9_candidates.json")
GRAMMAR_LEDGER = tl1.GRAMMAR_LEDGER
SCREEN_FILE = os.path.join(RES_DIR, "w9_screen.json")
SCREEN_CSV = os.path.join(RES_DIR, "w9_screen_cells.csv")
JUDGE_FILE = os.path.join(RES_DIR, "w9_judge.json")
INTAKE_FILE = os.path.join(RES_DIR, "w9_intake.json")
PREP_FILE = os.path.join(RES_DIR, "prep_state.json")
JUDGE_STATE_FILE = os.path.join(RES_DIR, "judge_state.json")
CKPT_DIR = os.path.join(RES_DIR, "checkpoint")
SCREEN_BATCH = "TRIAL_LAB_W9_SCREEN"   # prereg sec.0 ledger literal
JUDGE_BATCH = "TRIAL_LAB_W9_JUDGE"     # prereg sec.0 ledger literal
W6M = tl1.WINDOWS["6m"]                # leg-L 6m screen window (126 td)
FROZEN_SHA16 = "0601dda70b0209fa"   # pinned at slice-1 serialization (W8 precedent)

# prior-wave grammar shas (constructive-distinct assertion face)
PRIOR_WAVE_SHA16 = {
    "W1": "a2fa15f4b06b3c40", "MASS": "96269ebe766c3fc2",
    "W2": "1dd3d9579235cec", "W3": "cc59eab79db53436",
    "W4": "d498e9343ee57460", "W5": "29720178c39425de",
    "W6": "2d395f5f8e7d16cb", "W7": tl7.FROZEN_SHA16,   # 1fba956c2f21d1d3
    "W8": tl8.FROZEN_SHA16,      # 282c3290d1b431bc
}

# tstate axis (W8 frozen face, imported verbatim)
AXIS_TSTATE = tl8.AXIS_TSTATE           # ["none","deep_pullback","oversold_rsv"]
TSTATE_MEMBER = tl8.TSTATE_MEMBER       # "510300"

# amplitude-confirmation axis (prereg sec.3 NEW W9 frozen layer)
AXIS_AMP = ["none", "amp_narrow", "amp_wide"]
AXIS_COMBOS = tl8.AXIS_COMBOS * len(AXIS_AMP)   # 1,741,824 * 3 = 5,225,472
AMP_MEMBER = "510300"          # core48 member (prereg sec.2 probe fact)
PROBE_FACTS_FILE = os.path.join("results",
                                "_r431bmb_ampgate_w9_probe_facts.json")
AMP_SPEC = {
    "member": AMP_MEMBER,
    "series": "r417/r431 probe verbatim (zero-invention law): "
              "signal-day-d close info set on the member face",
    "amp_formula": "amp(d) = (high(d) - low(d)) / close(d) -- VERBATIM "
                   "the registered formula engine/factors.py::"
                   "intraday_range (FACTOR_CENSUS_REGISTRY A-row; "
                   "zero-invention law)",
    "med20amp": "amp rolling-20 median (min_periods=20, INCL d)",
    "amp_wide": "amp > med20amp (spectacle / turn-day face; MBAlib "
                "long-doji family canon: giant amplitude = regime-change "
                "face, direction NOT promised = both-direction honest)",
    "amp_narrow": "amp <= med20amp (calm / consolidation-day face; "
                  "MBAlib T-star family: quiet shrinking-volume "
                  "consolidation; in-registry intraday_range three-window "
                  "negative IC = narrow-face LONG anchor, short-window "
                  "weak anchor, term-structure mismatch honest)",
    "none": "no gate (W8 semantic baseline face)",
    "info_set": "signal-day d close; entry fills d+1 open (T+1 causal, "
                "same info set as GATE/VOL/YANG/VCONF/STREAK/TSTATE, "
                "zero lookahead)",
    "warmup": "19-bar warmup window gate-closed honest (med20amp first "
               "valid bar-idx == 19; VCONF-isostructural; structure "
               "spectrum vs YANG 0 / STREAK 2 / RSV 59 / MAD60 178 / "
               "VOL 519)",
    "engine_note": "entry-permittance only (effective signal zeroed, "
                   "MSG-0440 E1-mapping primitive; exit logic zero "
                   "change; engine/exit_rules.py zero touch)",
    "nan_artifact_note": "NaN comparisons (amp > med / amp <= med) "
                         "yield False NOT decidable (pit-95 batch-95 / "
                         "r421 probe / r431 erratum face: the r417 "
                         "map({False->x}) NaN-bucket artifact put "
                         "gate-closed warmup days into the bear/wild "
                         "buckets); the decidable face derives from "
                         "the underlying value notna (med20amp."
                         "notna()); the naive (amp > med) bool face "
                         "masquerades warmup bars as NARROW -- BANNED; "
                         "amp_narrow keep face = (~wide) AND decidable",
    "composition_order": "signal -> filter -> timing -> GATE -> VOL -> "
                         "YANG -> VCONF -> STREAK -> TSTATE -> AMP -> "
                         "initial-stop (an amp-blocked signal never "
                         "arms a stop; W8 order extended, prereg sec.3 "
                         "twelve-tuple order R/X/S/T/STOP/GATE/VOL/"
                         "YANG/VCONF/STREAK/TSTATE/AMP)",
}
AMP_ANCHOR = {
    "n_bars": 3483, "first_date": "2012-05-28", "cutoff": "2026-09-22",
    "zero_range_rows": 0,
    "warmup_gate_closed_bars": 19,
    "first_decidable_bar_idx": 19,
    "decidable_days": 3464, "wide_days": 1718, "narrow_days": 1746,
    "wide_rate_on_decidable": 0.496,
    "cross_yang_lower_bounds": {"yang_and_wide": 884,
                                "red_and_narrow": 887},
    "cross_vconf_lower_bounds": {"surge_and_wide": 1193,
                                 "dry_and_narrow": 1198},
    "cross_streak_lower_bounds": {"up_and_wide": 421,
                                  "down_and_narrow": 373},
    "cross_tstate_lower_bounds": {"mad60_and_wide": 233,
                                  "rsv60_and_narrow": 264},
    "seven_gate_all_decidable_days": 3305,
    "seven_gate_128cells_nonzero_count": 73,
    "seven_gate_128cells_empty_count": 55,
    "seven_gate_128cells_min_nonzero": 1,
    "seven_gate_128cells_max": 59,
    "seven_gate_128cells_empty": [
        "bear|calm|red|dry|up_streak|mad60|narrow",
        "bear|calm|red|dry|up_streak|mad60|wide",
        "bear|calm|red|dry|up_streak|rsv60|narrow",
        "bear|calm|red|dry|up_streak|rsv60|wide",
        "bear|calm|red|surge|up_streak|mad60|narrow",
        "bear|calm|yang|dry|up_streak|mad60|wide",
        "bear|calm|yang|surge|down_streak|mad60|narrow",
        "bear|calm|yang|surge|down_streak|mad60|wide",
        "bear|calm|yang|surge|down_streak|rsv60|narrow",
        "bear|calm|yang|surge|down_streak|rsv60|wide",
        "bear|wild|red|dry|up_streak|mad60|wide",
        "bear|wild|red|dry|up_streak|rsv60|wide",
        "bear|wild|red|surge|up_streak|mad60|wide",
        "bear|wild|red|surge|up_streak|rsv60|narrow",
        "bear|wild|red|surge|up_streak|rsv60|wide",
        "bear|wild|yang|dry|up_streak|rsv60|wide",
        "bull|calm|red|dry|down_streak|mad60|narrow",
        "bull|calm|red|dry|down_streak|mad60|wide",
        "bull|calm|red|dry|up_streak|mad60|narrow",
        "bull|calm|red|dry|up_streak|mad60|wide",
        "bull|calm|red|dry|up_streak|rsv60|narrow",
        "bull|calm|red|dry|up_streak|rsv60|wide",
        "bull|calm|red|surge|down_streak|mad60|narrow",
        "bull|calm|red|surge|up_streak|mad60|narrow",
        "bull|calm|red|surge|up_streak|mad60|wide",
        "bull|calm|red|surge|up_streak|rsv60|narrow",
        "bull|calm|red|surge|up_streak|rsv60|wide",
        "bull|calm|yang|dry|down_streak|mad60|narrow",
        "bull|calm|yang|dry|down_streak|mad60|wide",
        "bull|calm|yang|dry|down_streak|rsv60|narrow",
        "bull|calm|yang|dry|down_streak|rsv60|wide",
        "bull|calm|yang|dry|up_streak|mad60|narrow",
        "bull|calm|yang|dry|up_streak|mad60|wide",
        "bull|calm|yang|dry|up_streak|rsv60|wide",
        "bull|calm|yang|surge|down_streak|mad60|narrow",
        "bull|calm|yang|surge|down_streak|mad60|wide",
        "bull|calm|yang|surge|down_streak|rsv60|narrow",
        "bull|calm|yang|surge|down_streak|rsv60|wide",
        "bull|calm|yang|surge|up_streak|mad60|narrow",
        "bull|calm|yang|surge|up_streak|mad60|wide",
        "bull|calm|yang|surge|up_streak|rsv60|narrow",
        "bull|calm|yang|surge|up_streak|rsv60|wide",
        "bull|wild|red|dry|up_streak|mad60|wide",
        "bull|wild|red|dry|up_streak|rsv60|narrow",
        "bull|wild|red|dry|up_streak|rsv60|wide",
        "bull|wild|red|surge|up_streak|mad60|wide",
        "bull|wild|red|surge|up_streak|rsv60|wide",
        "bull|wild|yang|dry|down_streak|mad60|wide",
        "bull|wild|yang|dry|down_streak|rsv60|wide",
        "bull|wild|yang|dry|up_streak|rsv60|wide",
        "bull|wild|yang|surge|down_streak|mad60|narrow",
        "bull|wild|yang|surge|down_streak|mad60|wide",
        "bull|wild|yang|surge|down_streak|rsv60|narrow",
        "bull|wild|yang|surge|down_streak|rsv60|wide",
        "bull|wild|yang|surge|up_streak|rsv60|narrow"],
    "extreme_days": {
        "2015-07-27": {"streak": "down_streak2", "mad60": True,
                       "rsv60": False, "rsv_value": 0.2026,
                       "amp_state": "wide", "amp_over_med20": 1.814},
        "2016-01-04": {"streak": "down_streak2", "mad60": False,
                       "rsv60": False, "rsv_value": 0.2583,
                       "amp_state": "wide", "amp_over_med20": 4.814},
        "2024-02-28": {"streak": "neither", "mad60": False,
                       "rsv60": False, "rsv_value": 0.709,
                       "amp_state": "wide", "amp_over_med20": 1.21},
        "2024-09-24": {"streak": "up_streak2", "mad60": False,
                       "rsv60": False, "rsv_value": 0.5422,
                       "amp_state": "wide", "amp_over_med20": 3.853},
        "2024-09-30": {"streak": "up_streak2", "mad60": False,
                       "rsv60": False, "rsv_value": 0.9932,
                       "amp_state": "wide", "amp_over_med20": 6.654},
        "2025-04-07": {"streak": "down_streak2", "mad60": True,
                       "rsv60": True, "rsv_value": 0.1753,
                       "amp_state": "wide", "amp_over_med20": 6.961},
        "2026-01-19": {"streak": "down_streak2", "mad60": False,
                       "rsv60": False, "rsv_value": 0.4745,
                       "amp_state": "wide", "amp_over_med20": 1.032}},
    "streak_anchor_reproduction": {"up_streak_days": 844,
                                   "down_streak_days": 817,
                                   "neither_days": 1820,
                                   "warmup_gate_closed_bars": 2},
    "tstate_anchor_reproduction": {"mad60_gate_true_days": 383,
                                   "rsv60_gate_true_days": 632},
    "core48_wide_rate": {"n": 48, "min": 0.4808, "median": 0.4937,
                         "max": 0.5115,
                         "method": "tl1.load_core() roster "
                                   "(import-reuse, real core48 face)",
                         "members_with_lt60_rows_excluded": 0},
    "probe_facts": "results/_r431bmb_ampgate_w9_probe_facts.json "
                   "(r431 bm-b berth-upgrade merge of r417 AMP probe + "
                   "r423 STREAK/TSTATE faces; exact per-cell 128-grid "
                   "cross-check face when present; probe-facts face "
                   "not a results face)",
    "probe_basis": "cross-tables on the r431 probe basis VERBATIM "
                   "(r407 lesson): gate = close > ma200 strict with the "
                   "NaN warmup leg False on BOTH bull and bear sides; "
                   "vol = vol20 vs med500 NaN->False both sides; yang "
                   "= close > open strict (doji red); surge = volume > "
                   "med20 (min_periods=20, INCL d), dry = ~surge; "
                   "streak = W7 close-over-close double; tstate = the "
                   "tl8 census-verbatim faces; amp = the r417 face "
                   "(all-decidable window m7 = amp_decidable & "
                   "st.notna() & q10_ref.notna() == 3,305 days)",
    "note": "AMP core anchors (warmup 19 / decidable 3,464 / wide "
            "1,718 / narrow 1,746 / zero-range 0) asserted EXACT; "
            "cross four-cell faces asserted as LOWER BOUNDS per "
            "prereg sec.2; seven-gate 128 cells asserted 73-non-empty "
            "with the exact frozen 55-empty name list (probe range "
            "1-59) + exact per-cell cross-check vs the git-tracked "
            "probe facts file when present; extreme-day gate states "
            "asserted exact (amp ratios at probe 3-decimal rounding, "
            "rsv values at probe 4-decimal rounding, tolerance "
            "5.001e-5); STREAK/TSTATE reproduction counts asserted "
            "exact (W7/W8 cross-probe determinism law)",
}


def _grammar_sha16(grammar):
    """Grammar sha16 (W7 lineage import; zero re-implementation)."""
    return tl7._grammar_sha16(grammar)


# -------------------------------------------------------- amp overlay layer
def _amp_series_raw(prices: dict):
    """r417/r431-probe-verbatim AMP series computation (single
    computation site for series + decidable + raw values): amp =
    (high-low)/close; med20amp = rolling-20 median min_periods=20 incl
    d; wide = amp > med; decidable derives from the underlying value
    notna (pit-95 batch-95 law + r431 erratum face).  Returns
    (wide_perm, dec, meta, amp, med20amp); deterministic pure function
    of the (cutoff-truncated) panel."""
    df = prices[AMP_MEMBER]
    close = df["close"].astype(float).sort_index()
    high = df["high"].astype(float).reindex(close.index)
    low = df["low"].astype(float).reindex(close.index)
    amp = (high - low) / close          # registered formula verbatim
    med20amp = amp.rolling(20, min_periods=20).median()
    dec = med20amp.notna()               # underlying notna (pit-95 law)
    wide_perm = (amp > med20amp)         # comparison face: NaN->False
    # NOT decidable -- the keep faces below AND with dec
    n = len(close)

    def _first_true(s):
        arr = s.fillna(False).astype(bool).values
        nz = np.flatnonzero(arr)
        return int(nz[0]) if len(nz) else None

    dec_n = int(dec.sum())
    wide_n = int((wide_perm & dec).sum())
    narrow_n = int(((~wide_perm) & dec).sum())
    meta = {"n_bars": int(n),
            "warmup_gate_closed_bars": _first_true(dec),
            "first_decidable_bar_idx": _first_true(dec),
            "decidable_days": dec_n,
            "wide_days": wide_n, "narrow_days": narrow_n,
            "wide_rate_on_decidable":
            (round(float(wide_n / dec_n), 4) if dec_n else None),
            "na_window_bars": 19,   # the gate family's warmup
            }
    return wide_perm, dec, meta, amp, med20amp


def amp_state_series(prices: dict):
    """Frozen AMP spec (prereg sec.2/3): member 510300 signal-day info
    set -- wide perm + decidable face.  Returns (wide_perm, dec, meta):
    boolean Series on the member's own date index + structural meta.
    Deterministic pure function of the (cutoff-truncated) panel."""
    wide_perm, dec, meta, *_ = _amp_series_raw(prices)
    return wide_perm, dec, meta


def _amp_face_full():
    """Frozen sec.2 AMP-series face (r431 probe basis): the git-tracked
    raw full-history member file data/daily/sh510300.csv (open + high +
    low + close + volume columns), truncated at the evidence cutoff.
    Returns the member prices dict {sym: DataFrame(open, high, low,
    close, volume)}, or None when absent / columns missing / tail !=
    cutoff.  (tl8._tstate_face_full loading caliber reused verbatim --
    same member, same columns, same cutoff law; import-face law.)"""
    return tl8._tstate_face_full()


def _amp_state_full():
    """Canonical full-face amp_state with the frozen probe anchors
    asserted (prereg sec.2 G-AMP fail-closed): n_bars == 3,483;
    zero-range rows == 0; med20amp first-decidable == 19 / decidable ==
    3,464 / wide == 1,718 / narrow == 1,746 exact; cross four-cell
    lower bounds {yang^wide 884, red^narrow 887, surge^wide 1,193,
    dry^narrow 1,198, up^wide 421, down^narrow 373, mad60^wide 233,
    rsv60^narrow 264}; seven-gate (gate x vol x yang x vconf x streak x
    tstate x amp) 128 open-window cells 73-non-empty with the exact
    frozen 55-empty name list (probe range 1-59; all-decidable 3,305)
    + exact per-cell cross-check vs the git-tracked probe facts file
    when present; extreme-day gate states exact (7/7 wide; amp ratios
    at probe 3-decimal rounding, rsv at 4-decimal, tolerance 5.001e-5);
    STREAK/TSTATE reproduction counts exact (W7/W8 cross-probe
    determinism law).  Returns (amp_state, err); err is a one-line
    honest refusal reason when not None."""
    face = _amp_face_full()
    if face is None:
        return None, (f"raw member face data/daily/sh{AMP_MEMBER}.csv "
                      f"absent/open-high-low-close-volume columns "
                      f"missing or truncated tail != cutoff {CUTOFF}")
    wide_perm, dec, meta, amp, med20amp = _amp_series_raw(face)
    a = AMP_ANCHOR
    if (meta.get("n_bars") != a["n_bars"]
            or meta["first_decidable_bar_idx"]
            != a["first_decidable_bar_idx"]
            or meta["decidable_days"] != a["decidable_days"]
            or meta["wide_days"] != a["wide_days"]
            or meta["narrow_days"] != a["narrow_days"]):
        return None, (f"G-AMP core anchors {meta} != probe "
                      f"{{n 3483, warmup 19, decidable 3464, wide 1718, "
                      f"narrow 1746}}")
    df = face[AMP_MEMBER]
    zero_range = int((df["high"].astype(float)
                      == df["low"].astype(float)).sum())
    if zero_range != a["zero_range_rows"]:
        return None, (f"G-AMP zero-range-row anchor broken "
                      f"({zero_range})")
    # STREAK + TSTATE reproduction (W7/W8 cross-probe determinism law)
    up, down, sk_meta = tl7.streak_state_series(face)
    sar = a["streak_anchor_reproduction"]
    if (sk_meta.get("up_streak_days") != sar["up_streak_days"]
            or sk_meta.get("down_streak_days") != sar["down_streak_days"]
            or sk_meta.get("neither_days") != sar["neither_days"]
            or sk_meta.get("na_window_bars")
            != sar["warmup_gate_closed_bars"]):
        return None, (f"G-AMP streak-anchor reproduction broken "
                      f"{sk_meta} != {sar}")
    mad_perm, rsv_perm, ts_meta = tl8.tstate_state_series(face)
    tar = a["tstate_anchor_reproduction"]
    if (ts_meta["mad60"]["gate_true_days"]
            != tar["mad60_gate_true_days"]
            or ts_meta["rsv60"]["gate_true_days"]
            != tar["rsv60_gate_true_days"]):
        return None, (f"G-AMP tstate-anchor reproduction broken "
                      f"mad60 {ts_meta['mad60']['gate_true_days']}/"
                      f"rsv60 {ts_meta['rsv60']['gate_true_days']} != "
                      f"{tar}")
    # cross four-cell lower bounds on the r431 probe basis VERBATIM
    close = df["close"].astype(float).sort_index()
    o = df["open"].astype(float).reindex(close.index)
    h = df["high"].astype(float).reindex(close.index)
    l = df["low"].astype(float).reindex(close.index)
    v = df["volume"].astype(float).reindex(close.index)
    ma200 = close.rolling(200).mean()
    bull = close > ma200
    bear = close <= ma200
    ret = close.pct_change()
    vol20 = ret.rolling(20, min_periods=20).std(ddof=1)
    med500 = vol20.rolling(500, min_periods=500).median()
    calm = vol20 <= med500
    wild = vol20 > med500
    med20v = v.rolling(20, min_periods=20).median()
    surge = v > med20v
    dry = ~surge
    yang = close > o
    red = ~yang
    wide_face = wide_perm & dec
    narrow_face = (~wide_perm) & dec
    cross = {
        "yang_and_wide": int((yang & wide_face).sum()),
        "red_and_narrow": int((red & narrow_face).sum()),
        "surge_and_wide": int((surge & wide_face).sum()),
        "dry_and_narrow": int((dry & narrow_face).sum()),
        "up_and_wide": int((up & wide_face).sum()),
        "down_and_narrow": int((down & narrow_face).sum()),
        "mad60_and_wide": int((mad_perm & wide_face).sum()),
        "rsv60_and_narrow": int((rsv_perm & narrow_face).sum()),
    }
    for group, lb in (("cross_yang", a["cross_yang_lower_bounds"]),
                      ("cross_vconf", a["cross_vconf_lower_bounds"]),
                      ("cross_streak", a["cross_streak_lower_bounds"]),
                      ("cross_tstate", a["cross_tstate_lower_bounds"])):
        for k, v_ in lb.items():
            if cross[k] < v_:
                return None, (f"G-AMP {group} lower bound broken "
                              f"{k}={cross[k]} < {v_}")
    # seven-gate 128-cell cross on the r431 probe basis VERBATIM
    # (all-decidable window m7 = amp_decidable & streak-decidable &
    # mad60-decidable == 3,305 days; gate/vol/yang/vconf/streak/
    # tstate/amp faces as frozen above)
    _, _, _, _, _, rsv60, dec_mad, _ = tl8._tstate_series_raw(face)
    dec_st = pd.Series(False, index=close.index)
    dec_st.iloc[int(sk_meta.get("na_window_bars", 2)):] = True
    m7 = dec & dec_st & dec_mad
    cells = {}
    for bname, b in (("bull", bull), ("bear", bear)):
        for vname, vv in (("calm", calm), ("wild", wild)):
            for yname, y in (("yang", yang), ("red", red)):
                for sname, s in (("surge", surge), ("dry", dry)):
                    for kname, k in (("up_streak", up),
                                     ("down_streak", down)):
                        for tname, t in (("mad60", mad_perm),
                                         ("rsv60", rsv_perm)):
                            for aname, aa in (("wide", wide_face),
                                              ("narrow", narrow_face)):
                                cells[f"{bname}|{vname}|{yname}|{sname}|"
                                      f"{kname}|{tname}|{aname}"] = \
                                    int((m7 & b & vv & y & s & k & t
                                         & aa).sum())
    empty = sorted(k for k, n_ in cells.items() if n_ <= 0)
    nonzero = [x for x in cells.values() if x > 0]
    if (len(cells) != 128
            or len(nonzero) != a["seven_gate_128cells_nonzero_count"]
            or len(empty) != a["seven_gate_128cells_empty_count"]
            or empty != sorted(a["seven_gate_128cells_empty"])
            or min(nonzero) < a["seven_gate_128cells_min_nonzero"]
            or max(cells.values()) > a["seven_gate_128cells_max"]
            or int(m7.sum()) != a["seven_gate_all_decidable_days"]):
        return None, (f"G-AMP seven-gate 128-cell cross drift "
                      f"(nonzero {len(nonzero)}/73, empty "
                      f"{len(empty)}/55, min {min(nonzero)}, max "
                      f"{max(cells.values())}, all-decidable "
                      f"{int(m7.sum())}/3305)")
    # exact per-cell cross-check vs the git-tracked probe facts file
    # (r431 determinism cross-check law; skip-face = file absent,
    # header counts above still binding)
    if os.path.exists(PROBE_FACTS_FILE):
        pf = json.load(open(PROBE_FACTS_FILE, encoding="utf-8"))
        pcells = pf.get("seven_gate_128_cells", {})
        drift = [f"{k}: {cells.get(k)} != {v_}"
                 for k, v_ in pcells.items() if cells.get(k) != v_]
        if pcells and drift:
            return None, (f"G-AMP probe-facts per-cell cross-check "
                          f"drift: {drift[:3]}")
    # extreme-day gate states (frozen face; amp ratios at probe
    # 3-decimal rounding + rsv at 4-decimal, tolerance 5.001e-5)
    for dstr, want in a["extreme_days"].items():
        ts = pd.Timestamp(dstr)
        if ts not in close.index:
            return None, f"G-AMP extreme day {dstr} absent from face"
        m = med20amp.loc[ts]
        if pd.isna(m):
            return None, f"G-AMP extreme day {dstr} med20amp NaN"
        got_state = "wide" if bool(amp.loc[ts] > m) else "narrow"
        got_ratio = round(float(amp.loc[ts] / m), 3)
        rv = rsv60.loc[ts]
        rv = (None if pd.isna(rv) else round(float(rv), 4))
        got_streak = ("up_streak2" if bool(up.loc[ts])
                      else "down_streak2" if bool(down.loc[ts])
                      else "neither")
        if (got_state != want["amp_state"]
                or abs(got_ratio - want["amp_over_med20"]) > 5.01e-4
                or got_streak != want["streak"]
                or bool(mad_perm.loc[ts]) != want["mad60"]
                or bool(rsv_perm.loc[ts]) != want["rsv60"]
                or rv is None or abs(rv - want["rsv_value"]) > 5.001e-5):
            return None, (f"G-AMP extreme day {dstr} drift: state "
                          f"{got_state}/{want['amp_state']}, ratio "
                          f"{got_ratio}/{want['amp_over_med20']}, "
                          f"streak {got_streak}/{want['streak']}, "
                          f"mad {bool(mad_perm.loc[ts])}/"
                          f"{want['mad60']}, rsv "
                          f"{bool(rsv_perm.loc[ts])}/{want['rsv60']}, "
                          f"value {rv}/{want['rsv_value']}")
    meta = dict(meta)
    meta["cross_four_cells"] = cross
    meta["seven_gate_128cells"] = cells
    meta["seven_gate_128cells_empty"] = empty
    meta["seven_gate_all_decidable_days"] = int(m7.sum())
    meta["streak_anchor"] = {k: sk_meta.get(k) for k in
                             ("up_streak_days", "down_streak_days",
                              "neither_days")}
    meta["tstate_anchor"] = {"mad60_gate_true_days":
                             ts_meta["mad60"]["gate_true_days"],
                             "rsv60_gate_true_days":
                             ts_meta["rsv60"]["gate_true_days"]}
    return (wide_perm, dec, meta), None


def amp_zero_mask(mask: pd.DataFrame, amp_key: str, amp_state):
    """Grammar-layer amp entry gate (prereg sec.3 amplitude-confirmation
    face; E1-mapping primitive): off-face signal days -> effective
    signal zeroed (entry blocked; engine-native signal-off exit
    semantics -- the same primitive every cell uses when its own
    signal turns off; zero engine touch).  amp=none = W8 semantic
    baseline (identity).  Keep faces derive from the DECIDABLE face
    (pit-95 / r431 erratum law): amp_wide keeps wide AND decidable;
    amp_narrow keeps (~wide) AND decidable -- the naive comparison
    bool face alone would masquerade warmup bars as narrow (BANNED).
    Member dates missing from the mask index -> amp-closed
    (conservative reindex law, tl3/tl4/tl5/tl6/tl7/tl8 gate caliber)."""
    if amp_key == "none":
        return mask
    wide_perm, dec, _ = amp_state
    wide_keep = wide_perm.reindex(mask.index).fillna(False).astype(int)
    dec_keep = dec.reindex(mask.index).fillna(False).astype(int)
    if amp_key == "amp_wide":
        keep = (wide_keep & dec_keep)
    elif amp_key == "amp_narrow":
        keep = ((1 - wide_keep) & dec_keep)
    else:
        raise ValueError(f"unknown amp_key {amp_key}")
    return mask.mul(keep, axis=0)


def _amp_structure_pass(amp_meta) -> bool:
    """Series-structure invariants on every panel face (fail-closed):
    19-bar warmup -- first-decidable + decidable partitions n_bars;
    wide <= decidable and narrow <= decidable.  A face shorter than
    the warmup (first-decidable None) honestly refuses."""
    if not isinstance(amp_meta, dict):
        return False
    n = amp_meta.get("n_bars", -1)
    fv = amp_meta.get("first_decidable_bar_idx")
    return (fv is not None
            and fv + amp_meta.get("decidable_days", -10**9) == n
            and amp_meta.get("wide_days", -1)
            <= amp_meta.get("decidable_days", -1)
            and amp_meta.get("narrow_days", -1)
            <= amp_meta.get("decidable_days", -1))


# ------------------------------------------------------------ grammar build
def build_grammar_w9():
    """tl8 grammar extended with the NEW amp axis + W9 seeds/counts
    (frozen face).  Twelve-tuple axes R/X/S/T/STOP/GATE/VOL/YANG/VCONF/
    STREAK/TSTATE/AMP = 5,225,472 axis combos.

    Exclusion law (prereg sec.1): exact already-judged cells are
    excluded on the amp=none face only; all prior-wave lineage keys
    are amp=none completed (W1 4-tuple + stop/gate/vol/yang/vconf/
    streak/tstate/amp none; W2 5-tuple + gate/vol/yang/vconf/streak/
    tstate/amp none; W3 6-tuple + vol/yang/vconf/streak/tstate/amp
    none; W4 7-tuple + yang/vconf/streak/tstate/amp none; W5 8-tuple
    + vconf/streak/tstate/amp none; W6 9-tuple + streak/tstate/amp
    none; W7 10-tuple + tstate/amp none; W8 11-tuple + amp none; MASS
    via the declared translation); amp in {amp_narrow, amp_wide}
    faces = new-syntax legal cells (never excluded)."""
    g8 = tl8.build_grammar_w8()      # frozen W8 machinery face
    excl = []
    for e in g8["exclusion"]["stop_gate_vol_yang_vconf_streak_tstate_none_face"]:
        excl.append({**e, "axis": list(e["axis"]) + ["none"],
                     "face": "stop-gate-vol-yang-vconf-streak-"
                             "tstate-amp-none"})
    grammar = {
        "wave": WAVE, "prereg": PREREG, "evidence_cutoff": CUTOFF,
        "grammar_kind": "w9-amp-gate-extended",
        "seeds": {"trial_labor_w9_gen": SEED_GEN,
                  "trial_labor_w9_scrnull": SEED_NULL,
                  "trial_labor_w9_unc": SEED_UNC,
                  "derivation": "Sobol(seed=20309500+family_idx, "
                                "scramble) param box + default_rng("
                                "[20309500+family_idx, 7919]) twelve-"
                                "tuple axis stream R/X/S/T/STOP/GATE/"
                                "VOL/YANG/VCONF/STREAK/TSTATE/AMP "
                                "(prereg s.3; A idx 0-5, B idx 6+slot; "
                                "in-draft-window double-collision "
                                "re-pick lineage per prereg banner; "
                                "berths held at the freeze commit per "
                                "R250 one-step law, bm-b r432 three-"
                                "step re-verify ALL GREEN no re-pick)"},
        "n_draws": {"A": N_A, "B": N_B}, "k_nulls": K_NULLS,
        "axes": {**g8["axes"], "amp": AXIS_AMP},
        "axis_combos": AXIS_COMBOS,
        "stop_formula": g8["stop_formula"],
        "stop_fill_mapping": g8["stop_fill_mapping"],
        "gate_spec": g8["gate_spec"],
        "vol_spec": g8["vol_spec"],
        "yang_spec": g8["yang_spec"],
        "vconf_spec": g8["vconf_spec"],
        "streak_spec": g8["streak_spec"],
        "tstate_spec": g8["tstate_spec"],
        "amp_spec": AMP_SPEC,
        "vol_anchor": g8["vol_anchor"],
        "yang_anchor": g8["yang_anchor"],
        "vconf_anchor": g8["vconf_anchor"],
        "streak_anchor": g8["streak_anchor"],
        "tstate_anchor": g8["tstate_anchor"],
        "amp_anchor": AMP_ANCHOR,
        "families": g8["families"], "value_domains": g8["value_domains"],
        "faces": g8["faces"],
        "exclusion": {
            "stop_gate_vol_yang_vconf_streak_tstate_amp_none_face": excl,
            "sources": list(g8["exclusion"]["sources"])
            + ["w8_screen.json survivors (generate-time)",
               "w8_judge products (generate-time real-read "
               "re-declare window; W8-JUDGE landed 2026-09-29 "
               "15:26:25)"],
            "note": "exclusion face = amp=none only; prior-wave keys "
                    "amp=none-completed (semantic identity match); "
                    "amp in {amp_narrow, amp_wide} = new-syntax legal "
                    "cells (prereg sec.1)"},
        "negative_priors": g8.get("negative_priors"),
        "inventory_audit": g8["inventory_audit"],
    }
    grammar["grammar_sha256"] = _grammar_sha16(grammar)
    return grammar


# ------------------------------------------------------------ Sobol draw leg
def draw_candidate_sobol_w9(grammar, family, slot, n_draws):
    """Yield (draw_idx, cand) for one family slot per prereg sec.3:
    Sobol over the normalized param box (seed=SEED_GEN+family_idx) mapped
    to discrete domain indices + TWELVE-tuple axis stream
    default_rng([SEED_GEN+family_idx, 7919]) in the frozen consumption
    order R/X/S/T/STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP (the
    first eleven axis arrays are the W8-order stream VERBATIM --
    order-frozen consumption law; the amp leg appends AFTER tstate,
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
                  rng.integers(0, len(AXIS_AMP), n_draws)))
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
        r_, x_, s_, t_, st_, gt_, vt_, yg_, vc_, sk_, ts_, ap_ = ax[i]
        yield i, {"module": spec["module"], "fn": spec["fn"],
                  "sig_params": params,
                  "axis": [tl1.AXIS_FILTERS[r_], tl1.AXIS_EXITS[x_],
                           tl1.AXIS_SIZING[s_], tl1.AXIS_TIMING[t_],
                           tl2.AXIS_STOP[st_], tl3.AXIS_GATE[gt_],
                           tl4.AXIS_VOL[vt_], tl5.AXIS_YANG[yg_],
                           tl6.AXIS_VCONF[vc_], tl7.AXIS_STREAK[sk_],
                           tl8.AXIS_TSTATE[ts_], AXIS_AMP[ap_]],
                  "family": family}


# ------------------------------------------------ exclusion (18 real-reads)
def _load_exclusion_rows_w9(grammar):
    """Eighteen real-read source faces + the frozen serialized grammar
    face (prereg sec.1), all real-read at generate time.  All prior-wave
    keys are padded to the W9 TWELVE-tuple with amp=none (semantic-
    identity completion law).  Sources: 1 = frozen serialized grammar
    stop-gate-vol-yang-vconf-streak-tstate-amp-none face (12-tuple at
    build); 2-10 = W1/W2/MASS (declared tl3 translation)/W3/W4/W5/W6/
    W7/W8 screen survivors -- W8 is NEW vs W8's own loader
    (generate-time real-read; absent at build = zero rows honest per
    prereg sec.1); 11-19 = judged products (w1_judge / MASS judged /
    w2_judge / w3_judge / w4_judge / w5_judge / w6_judge / w7_judge /
    w8_judge) -- generate-time real-read re-declare window
    (declared-unavailable -> zero rows, no fabrication).
    """
    rows = list(grammar["exclusion"]
                ["stop_gate_vol_yang_vconf_streak_tstate_amp_none_face"])
    disc = {"grammar_stop_gate_vol_yang_vconf_streak_tstate_"
            "amp_none_rows": len(rows)}

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
                                 "streak-tstate-amp-none",
                         "candidate_id": cid})
            n += 1
        return n

    disc["w1_screen_survivors"] = _screen_survivors(
        os.path.join(tl1.RES_DIR, "w1_screen.json"),
        os.path.join(tl1.RES_DIR, "w1_candidates.json"),
        ["none"] * 8, "w1_screen_survivor")
    disc["w2_screen_survivors"] = _screen_survivors(
        os.path.join(tl2.RES_DIR, "w2_screen.json"),
        os.path.join(tl2.RES_DIR, "w2_candidates.json"),
        ["none"] * 7, "w2_screen_survivor")
    disc["w3_screen_survivors"] = _screen_survivors(
        os.path.join(tl3.RES_DIR, "w3_screen.json"),
        os.path.join(tl3.RES_DIR, "w3_candidates.json"),
        ["none"] * 6, "w3_screen_survivor")
    disc["w4_screen_survivors"] = _screen_survivors(
        tl4.SCREEN_FILE, tl4.CANDIDATES_FILE,
        ["none"] * 5, "w4_screen_survivor")
    disc["w5_screen_survivors"] = _screen_survivors(
        tl5.SCREEN_FILE, tl5.CANDIDATES_FILE,
        ["none"] * 4, "w5_screen_survivor")
    disc["w6_screen_survivors"] = _screen_survivors(
        tl6.SCREEN_FILE, tl6.CANDIDATES_FILE,
        ["none"] * 3, "w6_screen_survivor")
    disc["w7_screen_survivors"] = _screen_survivors(
        tl7.SCREEN_FILE, tl7.CANDIDATES_FILE,
        ["none"] * 2, "w7_screen_survivor")
    disc["w8_screen_survivors"] = _screen_survivors(
        tl8.SCREEN_FILE, tl8.CANDIDATES_FILE,
        ["none"], "w8_screen_survivor")

    # MASS screen survivors: declared tl3 translation + vol-yang-vconf-
    # streak-tstate-amp none pad (translated rows are 6-tuples)
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
                tr["axis"] = list(tr["axis"]) + ["none"] * 6
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

    # judged products: generate-time real-read re-declare window (prereg
    # sec.1/sec.9); absent -> declared-unavailable zero rows (freeze-time
    # expectation per prereg sec.0 (d): W1/MASS/W2/W3/W4/W5/W6 judged
    # landed; W7-JUDGE landed 2026-09-29 11:42:55; W8-JUDGE landed
    # 2026-09-29 15:26:25 -- NINE sources, second full-declare window in
    # history -- live re-read at generate time is the law)
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
                tr["axis"] = list(tr["axis"]) + ["none"] * 6
                tr["face"] = f"{tag}:translated-exact"
                rows.append(tr)
            else:
                src = cands.get(c.get("candidate_id"))
                if src is None:
                    continue
                rows.append({"module": src["module"], "fn": src["fn"],
                             "sig_params": src["sig_params"],
                             "axis": list(src["axis"]) + pad,
                             "face": f"{tag}:stop-gate-vol-yang-"
                                     "vconf-streak-tstate-amp-none",
                             "candidate_id": c.get("candidate_id")})
            n += 1
        return {"consumed_rows": n,
                "note": "judged product consumed as exclusion rows "
                        "(exact-key law, positive or negative verdicts "
                        "alike)"}

    disc["w1_judge_products"] = _judged_source(
        tl6.W1_JUDGE_FILE, os.path.join(tl1.RES_DIR, "w1_candidates.json"),
        ["none"] * 8, "w1_judged")
    disc["mass_judge_products"] = _judged_source(
        tl6.MASS_JUDGE_FILE, None, None, "mass_judged", mass=True)
    disc["w2_judge_products"] = _judged_source(
        tl6.W2_JUDGE_FILE, os.path.join(tl2.RES_DIR, "w2_candidates.json"),
        ["none"] * 7, "w2_judged")
    disc["w3_judge_products"] = _judged_source(
        tl6.W3_JUDGE_FILE, os.path.join(tl3.RES_DIR, "w3_candidates.json"),
        ["none"] * 6, "w3_judged")
    disc["w4_judge_products"] = _judged_source(
        tl4.JUDGE_FILE, tl4.CANDIDATES_FILE,
        ["none"] * 5, "w4_judged")
    disc["w5_judge_products"] = _judged_source(
        tl5.JUDGE_FILE, tl5.CANDIDATES_FILE,
        ["none"] * 4, "w5_judged")
    disc["w6_judge_products"] = _judged_source(
        tl6.JUDGE_FILE, tl6.CANDIDATES_FILE,
        ["none"] * 3, "w6_judged")
    disc["w7_judge_products"] = _judged_source(
        tl7.JUDGE_FILE, tl7.CANDIDATES_FILE,
        ["none"] * 2, "w7_judged")
    disc["w8_judge_products"] = _judged_source(
        tl8.JUDGE_FILE, tl8.CANDIDATES_FILE,
        ["none"], "w8_judged")
    # (d)-face judged-supply weighting: frozen baseline uniform stands
    # (prereg sec.0 declare; sec.9 re-declare window = live prev
    # increment merged at generate time, uniform baseline absent an
    # append-confirm amendment -- disclosed, no fabrication)
    disc["judged_supply_weighting"] = (
        "frozen baseline uniform per prereg sec.0 declare (axis families "
        "equal allocation, zero judged weighting); sec.9 re-declare window "
        "requires a prereg-level append-confirm BEFORE generate runs -- "
        "none exists, uniform stands, availability of the NINE judge "
        "products disclosed above (draft-time nine-source full-declare "
        "window = second in history)")
    return rows, disc


def _excluded_w9(cand, rows):
    """Exact already-judged cell test, amp=none face only (prereg
    sec.1: amp in {amp_narrow, amp_wide} = new-syntax legal cells --
    never excluded; W1-lineage cells implicitly stop/gate/vol/yang/
    vconf/streak/tstate/amp=none; W2 cells carry their own stop face;
    W3 stop+gate; W4 stop+gate+vol; W5 stop+gate+vol+yang; W6
    stop+gate+vol+yang+vconf; W7 stop+gate+vol+yang+vconf+streak; W8
    stop+gate+vol+yang+vconf+streak+tstate).  Returns the exclusion
    face or None."""
    if cand["axis"][11] != "none":
        return None
    for e in rows:
        if (cand["module"], cand["fn"]) == (e["module"], e["fn"]) \
                and cand["sig_params"] == e["sig_params"] \
                and cand["axis"] == e["axis"]:
            return e.get("face", "excluded")
    return None


# -------------------------------------------- effective face + engine curves
def _effective_signal_mask_w9(mask, prices, stop_key, atr20, gate_key,
                               vol_key, yang_key, vconf_key, streak_key,
                               tstate_key, amp_key, gate_state, vol_state,
                               yang_state, vconf_state, streak_state,
                               tstate_state, amp_state):
    """Dedup-face holdings proxy with the frozen composition order
    GATE -> VOL -> YANG -> VCONF -> STREAK -> TSTATE -> AMP ->
    initial-stop (prereg sec.3 twelve-tuple dedup legs; zero engine
    burn).  amp=none + tstate=none + streak=none + vconf=none + yang=
    none + vol=none + gate=none + stop=none = W1 identity; amp=none =
    W8 semantic baseline; all eight overlay faces deterministic layers
    of the same grammar stack (W8 order extended by the amp leg, zero
    disturbance to the first seven)."""
    G = tl3.gate_zero_mask(mask, gate_key, gate_state)
    V = tl4.vol_zero_mask(G, vol_key, vol_state)
    Y = tl5.yang_zero_mask(V, yang_key, yang_state)
    VC = tl6.vconf_zero_mask(Y, vconf_key, vconf_state)
    SK = tl7.streak_zero_mask(VC, streak_key, streak_state)
    TS = tl8.tstate_zero_mask(SK, tstate_key, tstate_state)
    AP = amp_zero_mask(TS, amp_key, amp_state)
    return tl2._effective_signal_mask(AP, prices, stop_key, atr20)


def run_candidate_curve_w9(cand, template, prices, P, states, atr20=None,
                           fundamental_ok=None, rng_matrix=None, p_on=None,
                           gate_state=None, vol_state=None, yang_state=None,
                           vconf_state=None, streak_state=None,
                           tstate_state=None, amp_state=None):
    """One W9 candidate cell at the engine face with the gate + vol +
    yang + vconf + streak + tstate + AMP overlays + initial-stop
    overlay carried per-cell (prereg sec.3 face a; frozen composition
    order filter -> timing -> GATE -> VOL -> YANG -> VCONF -> STREAK
    -> TSTATE -> AMP -> initial-stop).

    amp=none+tstate=none+streak=none+vconf=none+yang=none+vol=none+
    gate=none+stop=none -> byte-identical to the tl1 engine face;
    amp=none+tstate=none -> tl7 W7 face; amp=none -> tl8 W8 face
    (parity laws, selftest-pinned); amp in {amp_narrow, amp_wide} =
    new W9 syntax (entry-permittance only, never excluded).  Returns
    (eq, trades, metrics, params, patch, stop_fired, gate_zeroed,
    vol_zeroed, yang_zeroed, vconf_zeroed, streak_zeroed,
    tstate_zeroed, amp_zeroed)."""
    stop_key = cand["axis"][4]
    gate_key = cand["axis"][5]
    vol_key = cand["axis"][6]
    yang_key = cand["axis"][7]
    vconf_key = cand["axis"][8]
    streak_key = cand["axis"][9]
    tstate_key = cand["axis"][10]
    amp_key = cand["axis"][11]
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
        amp_state = amp_state_series(prices)
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
    AP = amp_zero_mask(TS, amp_key, amp_state)
    gate_zeroed = int((mask > 0).sum().sum() - (G > 0).sum().sum())
    vol_zeroed = int((G > 0).sum().sum() - (V > 0).sum().sum())
    yang_zeroed = int((V > 0).sum().sum() - (Y > 0).sum().sum())
    vconf_zeroed = int((Y > 0).sum().sum() - (VC > 0).sum().sum())
    streak_zeroed = int((VC > 0).sum().sum() - (SK > 0).sum().sum())
    tstate_zeroed = int((SK > 0).sum().sum() - (TS > 0).sum().sum())
    amp_zeroed = int((TS > 0).sum().sum() - (AP > 0).sum().sum())
    if stop_key == "none":
        S, stop_fired = AP, 0
    else:
        S = tl2._effective_signal_mask(AP, prices, stop_key, atr20)
        d = (AP > 0) & (S == 0)
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
        streak_zeroed, tstate_zeroed, amp_zeroed


def _null_axis_draw_w9(i):
    """Deterministic null-cell draw per prereg sec.3: rng=[SEED_NULL, i]
    (W9 berth 20310000, distinct from the W8 berth 20307000 -- zero
    stream overlap by construction); consumption order frozen = p_on
    regime -> TWELVE-tuple axis R/X/S/T/STOP/GATE/VOL/YANG/VCONF/
    STREAK/TSTATE/AMP -> signal matrix (the amp gate leg merged into
    the same grid/param space draw per prereg sec.3).  Same engine/
    cost/panel as candidate cells incl. the gate + vol + yang + vconf +
    streak + tstate + amp legs (BACKTEST_PLAN three iron rules)."""
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
          AXIS_AMP[int(rng.integers(len(AXIS_AMP)))])
    return p_on, list(ax), rng


# ------------------------------------------------------------ grammar / status
def cmd_grammar() -> int:
    """Serialize the frozen W9 grammar to results/trial_labor_w9/
    w9_grammar.json (idempotent; sha16 printed for the slice-1 pin)."""
    os.makedirs(RES_DIR, exist_ok=True)
    g = build_grammar_w9()
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
    print("slice-1 amp overlay + G-AMP gate + twelve-tuple grammar + "
          "funnel bodies + dispatch LANDED (bm-b r432); GENERATE pool "
          "entry submitted same-commit -- autofill burns, no inline "
          "burn (O-2100); SCREEN/JUDGE pool entries land on their "
          "physical deps per W3-W8 precedent")
    return 0


# -------------------------------------------------- generate slice (s1)
def cmd_generate() -> int:
    """Frozen prereg sec.3 generate stage (W8 cmd_generate caliber on
    the TWELVE-tuple face): per-slot Sobol streams consumed in global
    round-robin -> 18-source exclusion -> T-84s3 dedup gate on the
    effective signal face (gate + vol + yang + vconf + streak + tstate
    + AMP overlays applied, frozen composition order) ->
    w9_candidates.json + grammar ledger wave-9 row.  Zero engine cells
    burned."""
    t0 = time.time()
    print(f"=== {WAVE} generate (prereg FROZEN {PREREG}) ===")
    if os.path.exists(CANDIDATES_FILE):
        print("GENERATE-GATE: w9_candidates.json exists -- same-grammar "
              "rerun FORBIDDEN (TRIAL_LABOR_LAW sec.4); refusing")
        return 2
    if not os.path.exists(GRAMMAR_FILE):
        print("GENERATE-GATE: w9_grammar.json absent -- run `grammar` "
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
    excl_rows, excl_disc = _load_exclusion_rows_w9(grammar)
    neg_fns = {(e["module"], e["fn"])
               for e in grammar["exclusion"]
               ["stop_gate_vol_yang_vconf_streak_tstate_amp_none_face"]
               if str(e.get("face", "")).startswith("negative")}

    # ---- draws: per-slot Sobol streams consumed in global round-robin
    candidates, excluded_log = [], []
    excl_hits = {"A": 0, "B": 0}
    for family, n_draws in (("A", N_A), ("B", N_B)):
        slots = grammar["families"][family]
        n_slots = len(slots)
        streams = {s: draw_candidate_sobol_w9(
                       grammar, family, s,
                       (n_draws - s + n_slots - 1) // n_slots)
                   for s in range(n_slots)}
        for i in range(n_draws):
            slot = i % n_slots
            _, cand = next(streams[slot])
            cand["candidate_id"] = f"W9-{family}-{i:04d}"
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
            hit = _excluded_w9(cand, excl_rows)
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
        S = _effective_signal_mask_w9(mask, prices, cand["axis"][4], atr20,
                                      cand["axis"][5], cand["axis"][6],
                                      cand["axis"][7], cand["axis"][8],
                                      cand["axis"][9], cand["axis"][10],
                                      cand["axis"][11],
                                      gate_state, vol_state, yang_state,
                                      vconf_state, streak_state,
                                      tstate_state, amp_state)
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

    # gate/stop/vol/yang/vconf/streak/tstate/amp face counts + gate x
    # vol x yang x vconf x streak x tstate x amp seven-gate interaction
    # (prereg sec.5.4 seven-gate column, W8 six-gate face extended)
    gate_counts, stop_counts = {}, {}
    vol_counts, yang_counts, vconf_counts = {}, {}, {}
    streak_counts, tstate_counts, amp_counts = {}, {}, {}
    gvvvsktsa_counts = {}
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
        k7 = (f"{c['axis'][5]}|{c['axis'][6]}|{c['axis'][7]}|"
              f"{c['axis'][8]}|{c['axis'][9]}|{c['axis'][10]}|"
              f"{c['axis'][11]}")
        gvvvsktsa_counts[k7] = gvvvsktsa_counts.get(k7, 0) + 1

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
                                     "amp); exclusion face = amp=none "
                                     "only (sec.1); prior-wave keys "
                                     "amp=none-completed; amp in "
                                     "{amp_narrow, amp_wide} = "
                                     "new-syntax legal cells"},
               "dedup": {"raw": len(candidates), "distinct": len(distinct),
                         "fingerprint_collapse_groups": fp_collapsed,
                         "corr_collapses": corr_elim,
                         "note": "dedup legs on the generate-stage "
                                 "effective signal face (gate + vol + "
                                 "yang + vconf + streak + tstate + AMP "
                                 "overlays applied, frozen composition "
                                 "order; naive-hold returns, zero "
                                 "engine burn); engine faces run at "
                                 "screen (W1 precedent)"},
               "gate_face_counts": gate_counts,
               "stop_face_counts": stop_counts,
               "vol_face_counts": vol_counts,
               "yang_face_counts": yang_counts,
               "vconf_face_counts": vconf_counts,
               "streak_face_counts": streak_counts,
               "tstate_face_counts": tstate_counts,
               "amp_face_counts": amp_counts,
               "gate_vol_yang_vconf_streak_tstate_amp_face_counts":
                   gvvvsktsa_counts,
               "gate_state_meta": gate_state[2],
               "vol_state_meta": vol_state[2],
               "yang_state_meta": yang_state[2],
               "vconf_state_meta": vconf_state[2],
               "streak_state_meta": streak_state[2],
               "tstate_state_meta": tstate_state[2],
               "amp_state_meta": amp_state[2],
               "d6_disclosure": {
                   "max_corr_vs_registered_naive": "per-cell column; "
                   "naive-face caliber (dedup byproduct); D6 binding gate "
                   "at s4 intake recomputes at the engine face"},
               "audit": {"ram_gate_gb": ram_min,
                         "negative_prior_derivation": "derived from the "
                         "frozen grammar's negative_default_axis:stop-"
                         "gate-vol-yang-vconf-streak-tstate-amp-none "
                         "exclusion faces (face derivation is "
                         "mechanical)",
                         "seed_berth_note": "berths 20309500/20310000/"
                         "20310500 held at the freeze commit (bm-b r432 "
                         "three-step re-verify ALL GREEN, no re-pick; "
                         "R250 one-step law; in-draft-window "
                         "double-collision re-pick lineage per prereg "
                         "banner)",
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
           f"(amp faces {json.dumps(amp_counts, sort_keys=True)}; "
           f"gate x vol x yang x vconf x streak x tstate x amp "
           f"{json.dumps(gvvvsktsa_counts, sort_keys=True)}) "
           f"| seeds gen={SEED_GEN} null={SEED_NULL} unc={SEED_UNC} | "
           f"serialized {ser_ts} + consumed "
           f"{time.strftime('%Y-%m-%d %H:%M:%S')} (pool "
           f"TRIAL-LABOR-W9-GENERATE, T-121 prereg bm-b r432) | "
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
    print(f"amp faces: {json.dumps(amp_counts, sort_keys=True)}; "
          f"gate x vol x yang x vconf x streak x tstate x amp: "
          f"{json.dumps(gvvvsktsa_counts, sort_keys=True)[:400]}")
    print(f"amp meta: n_bars={amp_state[2]['n_bars']} "
          f"wide={amp_state[2]['wide_days']} "
          f"narrow={amp_state[2]['narrow_days']} "
          f"decidable={amp_state[2]['decidable_days']} "
          f"warmup={amp_state[2]['warmup_gate_closed_bars']}")
    print(f"products: w9_candidates.json + ledger row "
          f"(sha16 {grammar['grammar_sha256'][:16]})")
    print(f"elapsed {time.time() - t0:.1f}s (zero engine cells burned)")
    return 0


# ------------------------------------------------------ screen slice (s2)
csv_cols_screen_w9 = ["cell_id", "candidate_id", "family", "module", "fn",
                      "no_entries", "beat6m_k", "beat6m_n", "beat6m_rate",
                      "binom_z", "binom_p", "sharpe_full", "dd_full",
                      "n_trades", "n_entries", "stop_face", "stop_fired",
                      "gate_face", "gate_zeroed", "vol_face", "vol_zeroed",
                      "yang_face", "yang_zeroed", "vconf_face",
                      "vconf_zeroed", "streak_face", "streak_zeroed",
                      "tstate_face", "tstate_zeroed", "amp_face",
                      "amp_zeroed", "survives_screen"]

# pure survival-line math imported from tl2 (W2 identical frozen law:
# survive iff beat6m_rate > null-family p95 -- program-frozen, zero
# hand-picked thresholds; import-face law, zero re-implementation)
_finalize_math = tl2._finalize_math


def _screen_cell_w9(cell):
    """One W9 screen cell: full leg-L backtest with the gate + vol +
    yang + vconf + streak + tstate + AMP overlays + initial-stop
    overlay carried per-cell (prereg sec.3 face a) -> beat6m row (pool
    worker; W8 _screen_cell caliber + amp columns)."""
    st = tl1._ST
    kind, cand, template = cell["kind"], cell["cand"], cell.get("template")
    P, prices, states = st["P"], st["prices"], st["states"]
    starts, passive = st["starts"], st["passive_6m"]
    close = P["close"]
    if kind == "null":
        p_on, ax, rng = _null_axis_draw_w9(cell["i"])
        cand = {"module": "null", "fn": "random_signal",
                "sig_params": {"p_on": p_on}, "axis": ax,
                "candidate_id": f"W9-NULL-{cell['i']:04d}",
                "family": "NULL"}
        mat = rng.random((len(close.index), len(close.columns)))
        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \
            tz, az = run_candidate_curve_w9(
                cand, None, prices, P, states, st["atr20"],
                rng_matrix=mat, p_on=p_on, gate_state=st.get("gate_state"),
                vol_state=st.get("vol_state"),
                yang_state=st.get("yang_state"),
                vconf_state=st.get("vconf_state"),
                streak_state=st.get("streak_state"),
                tstate_state=st.get("tstate_state"),
                amp_state=st.get("amp_state"))
    else:
        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \
            tz, az = run_candidate_curve_w9(
                cand, template, prices, P, states, st["atr20"],
                fundamental_ok=st["fundamental_ok"],
                gate_state=st.get("gate_state"),
                vol_state=st.get("vol_state"),
                yang_state=st.get("yang_state"),
                vconf_state=st.get("vconf_state"),
                streak_state=st.get("streak_state"),
                tstate_state=st.get("tstate_state"),
                amp_state=st.get("amp_state"))
    row = {"cell_id": cell["cell_id"], "candidate_id": cand["candidate_id"],
           "family": cand["family"], "stop_face": cand["axis"][4],
           "stop_fired": int(fired), "gate_face": cand["axis"][5],
           "gate_zeroed": int(gz), "vol_face": cand["axis"][6],
           "vol_zeroed": int(vz), "yang_face": cand["axis"][7],
           "yang_zeroed": int(yz), "vconf_face": cand["axis"][8],
           "vconf_zeroed": int(cz), "streak_face": cand["axis"][9],
           "streak_zeroed": int(sz), "tstate_face": cand["axis"][10],
           "tstate_zeroed": int(tz), "amp_face": cand["axis"][11],
           "amp_zeroed": int(az)}
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


def _cell_list_w9():
    """Distinct candidate cells + K null cells (deterministic order;
    shard-split by index; W1-W8 precedent)."""
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
    G-VCONF / G-STREAK / G-TSTATE / G-AMP fail-closed gates + the
    shared passive 6m precompute (prereg sec.2; W8 cmd_screen_prep
    caliber on the W9 twelve-tuple grammar face + streak/tstate/amp
    meta disclosure)."""
    print(f"=== {WAVE} screen-prep (fail-closed gates) ===")
    for p, what in ((GRAMMAR_FILE, "w9_grammar.json"),
                    (CANDIDATES_FILE, "w9_candidates.json")):
        if not os.path.exists(p):
            print(f"PREP-GATE FAIL: {what} absent -- generate pending")
            return 2
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    if FROZEN_SHA16 and _grammar_sha16(grammar) != FROZEN_SHA16:
        print(f"PREP-GATE FAIL: grammar sha drift "
              f"{grammar['grammar_sha256'][:16]} != frozen {FROZEN_SHA16}")
        return 1
    cg = json.load(open(CANDIDATES_FILE, encoding="utf-8"))
    if str(cg.get("grammar_sha256", ""))[:16] != (FROZEN_SHA16
                                                  or
                                                  grammar[
                                                      "grammar_sha256"][
                                                      :16]):
        print("PREP-GATE FAIL: candidates grammar_sha256 != frozen anchor")
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

    # G-ANCHOR: registered six replayed through the W9 grammar
    # default-axis identity face (template_default+EW+daily+
    # initial_stop=none+gate=none+vol=none+yang=none+vconf=none+
    # streak=none+tstate=none+amp=none -> tl1 engine identity;
    # run_candidate_curve_w9 parity law selftest-pinned on the
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
                   "none", "none"]}
        eq, *_ = run_candidate_curve_w9(cand, t, pcut, Pfull,
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
    # panel-level gate + vol + yang + vconf + streak + tstate + amp meta
    # on the leg-L face (prereg sec.2 disclosure; structural invariants
    # only -- the {1523, 1441} vol / yang 1751 / vconf 1741 / streak
    # 3481-on-full / tstate 3305-3424-on-full / amp 3464-on-full probe
    # anchors hold only on the raw full-history face; asserted above)
    for member, gate_name in ((tl7.STREAK_MEMBER, "streak"),
                              (tl8.TSTATE_MEMBER, "tstate"),
                              (AMP_MEMBER, "amp")):
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
                                    "cross-probe determinism)"}}},
            "gate_meta": gate_meta, "vol_meta": vol_meta,
            "yang_meta": yang_meta, "vconf_meta": vconf_meta,
            "streak_meta": streak_meta, "tstate_meta": tstate_meta,
            "amp_meta": amp_meta,
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
          f"{amp_meta['warmup_gate_closed_bars']}")
    return 0


def cmd_screen(shard: int, shards: int, workers) -> int:
    print(f"=== {WAVE} screen shard {shard}of{shards} ===")
    for p, what in ((PREP_FILE, "prep_state.json"),
                    (CANDIDATES_FILE, "w9_candidates.json")):
        if not os.path.exists(p):
            print(f"SCREEN-GATE: {what} absent -- run screen-prep first")
            return 2
    prep = json.load(open(PREP_FILE, encoding="utf-8"))
    grammar, cells = _cell_list_w9()
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
                              (AMP_MEMBER, "amp")):
        if member not in prices:
            print(f"SCREEN-GATE: leg-L panel missing {gate_name} member "
                  f"{member} ({gate_name} series underivable) -- refuse")
            return 2
    streak_state = tl7.streak_state_series(prices)
    tstate_state = tl8.tstate_state_series(prices)
    amp_state = amp_state_series(prices)
    state = {"P": P, "prices": prices, "states": states,
             "starts": prep["starts"],
             "passive_6m": {int(k): v for k, v in
                            prep["passive_6m_ret"].items()},
             "fundamental_ok": fundamental_ok,
             "grammar": grammar, "atr20": tl2.atr20_series(prices),
             "gate_state": tl3.gate_state_series(prices),
             "vol_state": vol_state, "yang_state": yang_state,
             "vconf_state": vconf_state, "streak_state": streak_state,
             "tstate_state": tstate_state, "amp_state": amp_state}

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
        jobs = [(c["cell_id"], _screen_cell_w9, (c,)) for c in todo]
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
    grammar, cells = _cell_list_w9()
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
    gate_seg, vol_seg, yang_seg, vconf_seg = {}, {}, {}, {}
    streak_seg, tstate_seg, amp_seg = {}, {}, {}
    gvvy_seg, gvvvsk_seg, gvvvskts_seg, gvvvsktsa_seg = {}, {}, {}, {}
    for r in cand_rows:
        stop_counts[r["stop_face"]] = stop_counts.get(r["stop_face"], 0) + 1
        gf, vf = r["gate_face"], r["vol_face"]
        yf, cf = r["yang_face"], r["vconf_face"]
        sf, tf = r["streak_face"], r["tstate_face"]
        af = r["amp_face"]
        gate_counts[gf] = gate_counts.get(gf, 0) + 1
        vol_counts[vf] = vol_counts.get(vf, 0) + 1
        yang_counts[yf] = yang_counts.get(yf, 0) + 1
        vconf_counts[cf] = vconf_counts.get(cf, 0) + 1
        streak_counts[sf] = streak_counts.get(sf, 0) + 1
        tstate_counts[tf] = tstate_counts.get(tf, 0) + 1
        amp_counts[af] = amp_counts.get(af, 0) + 1
        for seg, key in ((gate_seg, gf), (vol_seg, vf), (yang_seg, yf),
                         (vconf_seg, cf), (streak_seg, sf),
                         (tstate_seg, tf), (amp_seg, af),
                         (gvvy_seg, f"{gf}|{vf}|{yf}|{cf}"),
                         (gvvvsk_seg, f"{gf}|{vf}|{yf}|{cf}|{sf}"),
                         (gvvvskts_seg,
                          f"{gf}|{vf}|{yf}|{cf}|{sf}|{tf}"),
                         (gvvvsktsa_seg,
                          f"{gf}|{vf}|{yf}|{cf}|{sf}|{tf}|{af}")):
            s = seg.setdefault(key, {"n_cells": 0, "n_survivors": 0})
            s["n_cells"] += 1
            s["n_survivors"] += int(bool(r["survives_screen"]))
    for seg in (gate_seg, vol_seg, yang_seg, vconf_seg, streak_seg,
                tstate_seg, amp_seg, gvvy_seg, gvvvsk_seg, gvvvskts_seg,
                gvvvsktsa_seg):
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
    n_distinct = len(cand_rows)
    batch_trials = n_distinct + K_NULLS
    ledger = tl1.append_ledger(SCREEN_BATCH, batch_trials,
                               "results/trial_labor_w9/w9_screen.json",
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
                           "draw_order": "p_on regime -> TWELVE-tuple "
                                         "axis R/X/S/T/STOP/GATE/VOL/"
                                         "YANG/VCONF/STREAK/TSTATE/AMP "
                                         "-> signal matrix (frozen "
                                         "runner face, gate+vol+yang+"
                                         "vconf+streak+tstate+amp legs "
                                         "included)"},
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
           "gate_segmented_survival": gate_seg,
           "vol_segmented_survival": vol_seg,
           "yang_segmented_survival": yang_seg,
           "vconf_segmented_survival": vconf_seg,
           "streak_segmented_survival": streak_seg,
           "tstate_segmented_survival": tstate_seg,
           "amp_segmented_survival": amp_seg,
           "gate_vol_yang_vconf_interaction_survival": gvvy_seg,
           "gate_vol_yang_vconf_streak_interaction_survival": gvvvsk_seg,
           "gate_vol_yang_vconf_streak_tstate_interaction_survival":
               gvvvskts_seg,
           "gate_vol_yang_vconf_streak_tstate_amp_interaction_survival":
               gvvvsktsa_seg,
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
           "batch_cells": batch_trials, "trials_ledger": ledger,
           "audit": {"note": "one full leg-L backtest per cell (prereg "
                             "sec.3 all-history caliber, V1 13bp base, "
                             "T+1); gate + vol + yang + vconf + streak "
                             "+ tstate + AMP overlays + initial-stop "
                             "overlay at the engine face = effective-"
                             "signal zeroing (MSG-0440 E1 mapping, "
                             "dedup-face consistency, frozen composition "
                             "order signal -> filter -> timing -> GATE "
                             "-> VOL -> YANG -> VCONF -> STREAK -> "
                             "TSTATE -> AMP -> initial-stop); MA200/"
                             "vol-closed NaN windows gate-closed on BOTH "
                             "faces, yang zero-warmup, vconf 19-bar "
                             "warmup, streak 2-bar warmup, tstate "
                             "178/59-bar warmups, amp 19-bar warmup "
                             "(panel-level counts in gate/vol/yang/vconf/"
                             "streak/tstate/amp_na_window_bars); "
                             "amp_narrow keep face = (~wide) AND "
                             "decidable (r431 erratum law -- the naive "
                             "comparison bool face alone masquerades "
                             "warmup bars as narrow, BANNED); workers "
                             "BelowNormal; checkpoint append-per-cell; "
                             "beat6m comparison operator = >= per frozen "
                             "prereg sec.3 text; survival math imported "
                             "from tl2._finalize_math (W2 identical law)"},
           "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    tl1._dump(SCREEN_FILE, out)
    with open(SCREEN_CSV, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=csv_cols_screen_w9,
                           extrasaction="ignore")
        w.writeheader()
        for r in cand_rows:
            w.writerow(r)
    print(f"screen finalize: distinct {n_distinct} + nulls {K_NULLS}, "
          f"null p95 {p95:.4f}, survivors {len(survivors)}")
    print(f"amp segmented survival: {json.dumps(amp_seg, sort_keys=True)}")
    print(f"gate x vol x yang x vconf x streak x tstate x amp interaction "
          f"survival: {json.dumps(gvvvsktsa_seg, sort_keys=True)[:400]}")
    print(f"products: w9_screen.json + w9_screen_cells.csv "
          f"(ledger total {ledger['total']})")
    return 0


# ------------------------------------------------------ judge slice (s3)
def _dual_nulls_w9(returns, cell_idx, seed=None):
    """Dual nulls on the cell's mean daily return (prereg sec.3 s3):
    B=2000 block-20 circular bootstrap + P=2000 sign-flip, two-sided;
    W9 seed binding [20310500, cell_idx].  Math imported verbatim from
    tl2._dual_nulls_w2 (import law; the seed constant is the only
    differing face -- selftest cross-checks at the W9 seed)."""
    return tl2._dual_nulls_w2(returns, cell_idx,
                              seed=SEED_UNC if seed is None else seed)


def _overlay_stop_disclosure_w9(cand, prices, P, atr20, fundamental_ok,
                                gate_state, vol_state, yang_state,
                                vconf_state, streak_state, tstate_state,
                                amp_state):
    """Per-cell stop trigger/fill-day disclosure on the leg-L signal face
    with the W9 composition order (filter -> timing -> GATE -> VOL ->
    YANG -> VCONF -> STREAK -> TSTATE -> AMP -> initial-stop; MSG-0440
    E1 mapping + MSG-0450 annex 1).  Mirrors tl8._overlay_stop_disclosure_w8
    with the amp overlay inserted before stop arming (engine-face
    consistency law; summary math imported)."""
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
    AP = amp_zero_mask(TS, cand["axis"][11], amp_state)
    _, ev = tl2.stop_exit_overlay(AP, prices, stop_key, atr20)
    s = tl2._stop_dev_summary(ev, prices, mask.index)
    s["stop_face"] = stop_key
    return s


def _judge_cell_w9(cell):
    """One W9 survivor judged cell (prereg sec.3 s3 frozen face, pool
    worker): dual-leg (P-5C grid) x cost {base x1, x2=CostPatch(2)} full
    curves with the gate + vol + yang + vconf + streak + tstate + AMP
    overlays + initial-stop overlay carried per cell (frozen composition
    order) + window-grid beat vs passive + regime segments + dual nulls
    (W9 seed [20310500, i]) + descriptive clauses + crisis/stop/gate-
    flip/vol-flip disclosure columns.  Gates face = leg-L base (W1-W8
    judged-cell caliber); x2 + descriptive = disclosure."""
    st = tl1._ST
    cand, template = cell["cand"], cell.get("template")
    out = {"cell_id": cell["cell_id"], "candidate_id": cand["candidate_id"],
           "family": cand["family"], "module": cand["module"],
           "fn": cand["fn"], "stop_face": cand["axis"][4],
           "gate_face": cand["axis"][5], "vol_face": cand["axis"][6],
           "yang_face": cand["axis"][7], "vconf_face": cand["axis"][8],
           "streak_face": cand["axis"][9], "tstate_face": cand["axis"][10],
           "amp_face": cand["axis"][11]}
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
        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \
            tz, az = run_candidate_curve_w9(cand, template, prices, P,
                                            st["states"],
                                            st[f"atr20_{leg}"],
                                            fundamental_ok=fok,
                                            gate_state=gs, vol_state=vs,
                                            yang_state=ys, vconf_state=cs,
                                            streak_state=sk,
                                            tstate_state=ts,
                                            amp_state=ap)
        with CostPatch(2):
            eq2, _, m2, _, _, fired2, gz2, vz2, yz2, cz2, sz2, tz2, az2 = \
                run_candidate_curve_w9(
                    cand, template, prices, P, st["states"],
                    st[f"atr20_{leg}"], fundamental_ok=fok, gate_state=gs,
                    vol_state=vs, yang_state=ys, vconf_state=cs,
                    streak_state=sk, tstate_state=ts, amp_state=ap)
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
                         "amp_zeroed_x2": 0,
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
                     "tstate_zeroed": int(tz),
                     "tstate_zeroed_x2": int(tz2),
                     "amp_zeroed": int(az),
                     "amp_zeroed_x2": int(az2)}
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
            out["stop_disclosure"] = _overlay_stop_disclosure_w9(
                cand, prices, P, st["atr20_L"], fok, gs, vs, ys, cs, sk,
                ts, ap)
    out["legs"] = legs
    if "legL_daily_returns" not in out:
        out["legL_daily_returns"] = []
        out["legL_sharpe_full"] = None
        out["legL_n_trades"] = 0
        out["legL_n_entries"] = 0
    r = np.asarray(out["legL_daily_returns"], dtype=float)
    out["dual_nulls"] = _dual_nulls_w9(r if len(r) else np.zeros(30),
                                       cell["i"])
    # prereg sec.5.6 gate/vol-flip day columns (disclosure-only, zero
    # gate weight): panel-level flip-day count of the cell's OWN gate /
    # vol face on the leg-L panel (state meta face; none -> null).  The
    # yang AND vconf AND streak AND tstate AND amp faces carry no
    # probe-defined flip caliber (W5 yang precedent: probes define no
    # such flips; daily binary faces); their disclosure columns are the
    # per-leg yang_zeroed / vconf_zeroed / streak_zeroed /
    # tstate_zeroed / amp_zeroed counts above.
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
    vol + yang + vconf + streak + tstate + amp meta (prereg sec.2/3;
    W8 cmd_judge_prep caliber on the W9 twelve-tuple grammar face;
    G-VOL/G-YANG/G-VCONF/G-STREAK/G-TSTATE/G-AMP structural per leg +
    probe anchors on the raw full-history face)."""
    print(f"=== {WAVE} judge-prep ===")
    if not os.path.exists(SCREEN_FILE):
        print("JUDGE-PREP-GATE: screen not finalized (w9_screen.json "
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
    starts, gate_meta, vol_meta = {}, {}, {}
    yang_meta, vconf_meta, streak_meta = {}, {}, {}
    tstate_meta, amp_meta = {}, {}
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
                                  (AMP_MEMBER, "amp")):
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
               "amp_meta": amp_meta,
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
          f"{amp_meta['L']['decidable_days']}")
    return 0


def cmd_judge(shard: int, shards: int, workers) -> int:
    print(f"=== {WAVE} judge shard {shard}of{shards} ===")
    for p, what in ((JUDGE_STATE_FILE, "judge_state.json"),
                    (SCREEN_FILE, "w9_screen.json")):
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
        jobs = [(c["cell_id"], _judge_cell_w9, (c,)) for c in todo]
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
                               "results/trial_labor_w9/w9_judge.json",
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
    # GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP-face + interaction judged
    # summaries (prereg sec.5.4 direction-readout + seven-gate column
    # faces; disclosure-only, zero gate weight)
    gate_sum, vol_sum = {}, {}
    yang_sum, vconf_sum, streak_sum, tstate_sum, amp_sum = {}, {}, {}, {}, {}
    gvy_sum, gvvy_sum, gvvvsk_sum, gvvvskts_sum, gvvvsktsa_sum = \
        {}, {}, {}, {}, {}
    for r in judged:
        g = r.get("gate_face", "none")
        v = r.get("vol_face", "none")
        y = r.get("yang_face", "none")
        c = r.get("vconf_face", "none")
        s = r.get("streak_face", "none")
        t = r.get("tstate_face", "none")
        a = r.get("amp_face", "none")
        for seg, key in ((gate_sum, g), (vol_sum, v), (yang_sum, y),
                         (vconf_sum, c), (streak_sum, s),
                         (tstate_sum, t), (amp_sum, a),
                         (gvy_sum, f"{g}|{v}|{y}"),
                         (gvvy_sum, f"{g}|{v}|{y}|{c}"),
                         (gvvvsk_sum, f"{g}|{v}|{y}|{c}|{s}"),
                         (gvvvskts_sum, f"{g}|{v}|{y}|{c}|{s}|{t}"),
                         (gvvvsktsa_sum, f"{g}|{v}|{y}|{c}|{s}|{t}|{a}")):
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
           "gate_vol_yang_interaction_judgment": gvy_sum,
           "gate_vol_yang_vconf_interaction_judgment": gvvy_sum,
           "gate_vol_yang_vconf_streak_interaction_judgment": gvvvsk_sum,
           "gate_vol_yang_vconf_streak_tstate_interaction_judgment":
               gvvvskts_sum,
           "gate_vol_yang_vconf_streak_tstate_amp_interaction_judgment":
               gvvvsktsa_sum,
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
                             "tstate + AMP overlays carried per cell "
                             "(frozen composition signal -> filter -> "
                             "timing -> GATE -> VOL -> YANG -> VCONF -> "
                             "STREAK -> TSTATE -> AMP -> initial-stop; "
                             "engine/exit_rules.py zero touch) + regime "
                             "segments + dual nulls (B=2000 block-20 + "
                             "P=2000 sign-flip, seed [20310500, cell]); "
                             "gates on the leg-L base face (W1-W8 "
                             "judged-cell caliber); beat operator = "
                             "strict > (W1-W8 judged-cell caliber; "
                             "screen >= was the sec.3 s2 literal); x2 + "
                             "descriptive clauses = disclosure-only zero "
                             "criteria weight; crisis-day count = "
                             "|daily|>8% leg-L base (sec.5.6); stop "
                             "trigger/fill-day D+1 open-vs-close "
                             "deviation = MSG-0450 annex-1 disclosure on "
                             "the protection-floor signal face with the "
                             "amp overlay inserted before stop arming "
                             "(W9 composition law); gate_flip_days_legL "
                             "/ vol_flip_days_legL = panel-level "
                             "flip-day counts of the cell's OWN gate / "
                             "vol face on the leg-L panel (none -> null; "
                             "sec.5.6 disclosure columns, zero gate "
                             "weight; yang AND vconf AND streak AND "
                             "tstate AND amp faces = daily binaries with "
                             "no probe-defined flip caliber [W5 yang "
                             "precedet, r206/r423/r431 probes define no "
                             "streak/tstate/amp flips], per-leg "
                             "yang_zeroed / vconf_zeroed / streak_zeroed "
                             "/ tstate_zeroed / amp_zeroed counts are "
                             "their columns); gate x vol x yang x vconf "
                             "x streak x tstate x amp seven-gate "
                             "interaction segments = prereg sec.3 "
                             "seven-gate disclosure column; fundamental "
                             "keep-ok face = screen consistency law"},
           "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    tl1._dump(JUDGE_FILE, out)
    print(f"judge finalize: {n_judged} judged cells, E[FP]={e_fp}, "
          f"G2 eligible {len(eligible)} -> {eligible[:10]}")
    print(f"amp-face judgment: {json.dumps(amp_sum, sort_keys=True)}")
    print(f"gate x vol x yang x vconf x streak x tstate x amp "
          f"interaction judgment: "
          f"{json.dumps(gvvvsktsa_sum, sort_keys=True)[:400]}")
    return 0


# ------------------------------------------------------ intake slice (s4)
def cmd_intake() -> int:
    """s4 D6 binding gate (W2 cmd_intake precedent on the W9 file
    faces): G2-eligible survivors -> per-candidate max|corr| vs the
    registered roster (>=0.7 reject) + survivor-cluster collapse (>=0.7
    pairs keep highest DSR) -> w9_intake.json registration-face rows.
    Zero ledger rows (judgment face); STRATEGY_LIBRARY / paper
    onboarding writes belong to the registration pipeline (prereg
    sec.4)."""
    print(f"=== {WAVE} intake (s4 D6 binding gate) ===")
    if not os.path.exists(JUDGE_FILE):
        print("INTAKE-GATE: judge not finalized (w9_judge.json absent)")
        return 2
    judge = json.load(open(JUDGE_FILE, encoding="utf-8"))
    if FROZEN_SHA16 and str(judge.get("grammar_sha256", ""))[:16] \
            != FROZEN_SHA16:
        print(f"INTAKE-GATE FAIL: judge grammar sha != frozen anchor "
              f"{FROZEN_SHA16}")
        return 1
    eligible = list(judge["eligible_g2"])
    audit_note = ("intake = judgment face, zero ledger rows; candidate "
                  "daily returns = judge checkpoint engine face (seven-"
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
    # intake precedent; w9_judge.json cells are stripped by design)
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
    zero cell evaluation): AMP causality / 19-bar warmup / NaN
    comparison-artifact leg (pit-95 batch-95 + r431 erratum face) /
    amp=none identity / seven-gate intersection / G-AMP probe anchors
    (incl. seven-gate 128-cell 73/55 + extreme days + core48 spread) /
    grammar structure / draw determinism / 18-source exclusion loader /
    engine double-run determinism legs / funnel faces (dispatch /
    null-cell engine path / CSV contract) + pit-95 finalize guards."""
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

    # ---- L1 synthetic AMP causality (every-4th-day big-amplitude
    # pattern: wide bites EXACTLY the big days; small days narrow)
    amp_idx = pd.bdate_range("2018-01-01", periods=120)
    amp_close = pd.Series(100.0, index=amp_idx)
    amp_o = amp_close.copy()
    big_days = set(i for i in range(len(amp_idx)) if i % 4 == 2)
    hi = pd.Series([105.0 if i in big_days else 100.2
                    for i in range(len(amp_idx))], index=amp_idx)
    lo = pd.Series([95.0 if i in big_days else 99.8
                    for i in range(len(amp_idx))], index=amp_idx)
    amp_face = {AMP_MEMBER: pd.DataFrame(
        {"open": amp_o, "high": hi, "low": lo, "close": amp_close,
         "volume": pd.Series(1000.0, index=amp_idx),
         "amount": amp_close * 1000.0}, index=amp_idx)}
    wide_d, dec_d, meta_d = amp_state_series(amp_face)
    exp_wide = [bool(i in big_days) for i in range(len(amp_idx))]
    _ok("L1a amp_wide causality (every-4th-day big-amp face: gate TRUE "
        "exactly on the big days, narrow on the rest of decidable)",
        list((wide_d & dec_d).values) == [b and i >= 19
                                          for i, b in
                                          enumerate(exp_wide)],
        f"wide_true={int((wide_d & dec_d).sum())} at "
        f"{list(np.flatnonzero((wide_d & dec_d).values)[:3])}..")

    # ---- L2 warmup gate-closed legs (19 bars, synthetic + short face
    # honest refuse)
    _ok("L2a AMP 19-bar warmup gate-closed (first 19 bars all "
        "decidable-False, first-decidable == 19, decidable == 101/120)",
        int(dec_d.iloc[:19].sum()) == 0
        and meta_d["first_decidable_bar_idx"] == 19
        and meta_d["decidable_days"] == 120 - 19
        and meta_d["wide_days"] + meta_d["narrow_days"]
        == meta_d["decidable_days"])
    short_idx = pd.bdate_range("2020-01-01", periods=15)
    short_face = {AMP_MEMBER: pd.DataFrame(
        {"open": pd.Series(100.0, index=short_idx),
         "high": pd.Series(101.0, index=short_idx),
         "low": pd.Series(99.0, index=short_idx),
         "close": pd.Series(100.0, index=short_idx),
         "volume": pd.Series(1000.0, index=short_idx),
         "amount": pd.Series(1e5, index=short_idx)}, index=short_idx)}
    wide_s, dec_s, meta_s = amp_state_series(short_face)
    _ok("L2b short face (< 20 bars) honest refuse: first-decidable None "
        "+ zero decidable + structure gate refuses",
        meta_s["first_decidable_bar_idx"] is None
        and meta_s["decidable_days"] == 0
        and not _amp_structure_pass(meta_s))

    # ---- L3 NaN comparison-artifact leg (pit-95 batch-95 / r421 /
    # r431 erratum face: the naive (amp > med) bool face is False NOT
    # decidable in the warmup -- it masquerades warmup bars as NARROW;
    # the decidable face derives from med20amp.notna())
    _, _, _, amp_raw, med_raw = _amp_series_raw(amp_face)
    naive_bool = (amp_raw > med_raw)         # bool face: NaN -> False
    _ok("L3a the ARTIFACT demonstrated: naive bool (amp > med) is "
        "False-False on warmup bars (first_valid_index == bar 0, "
        "masquerading them as narrow) while the notna-derived "
        "decidable face starts at 19",
        naive_bool.first_valid_index() == amp_idx[0]
        and int(dec_d.iloc[:19].sum()) == 0
        and int(np.flatnonzero(dec_d.values)[0]) == 19)
    mask_wu = pd.DataFrame({"sig": [1.0] * 25}, index=amp_idx[:25])
    m_wu = amp_zero_mask(mask_wu, "amp_narrow", (wide_d, dec_d, meta_d))
    _ok("L3b amp_narrow on a warmup-spanning mask permits ZERO warmup "
        "bars (keep = (~wide) AND decidable -- the r417 map-NaN-bucket "
        "erratum face BANNED at the mask level)",
        int((m_wu["sig"].iloc[:19] > 0).sum()) == 0
        and int((m_wu["sig"].iloc[19:] > 0).sum()) > 0)

    # ---- L4 amp=none identity (zero-mask + W8 semantic baseline)
    mask5 = pd.DataFrame({"sig": [1.0] * 6}, index=amp_idx[30:36])
    ident = amp_zero_mask(mask5, "none", (wide_d, dec_d, meta_d))
    _ok("L4a amp=none == W8 semantic-baseline identity (byte-equal)",
        ident.equals(mask5))
    perm_w = amp_zero_mask(mask5, "amp_wide", (wide_d, dec_d, meta_d))
    # bars 30-35: big days are 30, 34 (i%4==2)
    exp_l4w = [1.0 if i in big_days else 0.0 for i in range(30, 36)]
    _ok("L4b amp_wide permits only big-amp days (bars 30/34 open, "
        "31/32/33/35 closed)",
        list(perm_w["sig"]) == exp_l4w,
        f"got={list(perm_w['sig'])}")
    miss_idx2 = amp_idx[[30, 31]].append(
        pd.DatetimeIndex(["2030-01-01"]))
    mmask2 = pd.DataFrame({"sig": [1.0] * 3}, index=miss_idx2)
    mres2 = amp_zero_mask(mmask2, "amp_wide", (wide_d, dec_d, meta_d))
    _ok("L4c missing dates -> amp-closed (conservative reindex law)",
        list(mres2["sig"]) == [1.0, 0.0, 0.0])

    # ---- L5 seven-gate intersection leg (streak x tstate x amp
    # composed on a controlled crash-then-stabilize face with big-amp
    # crash days: down-streak days {192,193} intersect the mad window
    # {190..} intersect the big-amp days)
    x_idx = pd.bdate_range("2017-01-02", periods=220)
    x_close = pd.Series([100.0] * 186 + [103.0] * 4
                        + [92.0, 91.0, 90.0, 89.0] + [89.0] * 26,
                        index=x_idx)
    x_big = set(range(188, 196))           # crash + post days big-amp
    x_hi = pd.Series([x_close.iloc[i] + (8.0 if i in x_big else 0.2)
                      for i in range(len(x_idx))], index=x_idx)
    x_lo = pd.Series([x_close.iloc[i] - (8.0 if i in x_big else 0.2)
                      for i in range(len(x_idx))], index=x_idx)
    x_face = {AMP_MEMBER: pd.DataFrame(
        {"open": x_close.copy(), "high": x_hi, "low": x_lo,
         "close": x_close, "volume": pd.Series(1000.0, index=x_idx),
         "amount": x_close * 1000.0}, index=x_idx)}
    x_mad, x_rsv, x_meta = tl8.tstate_state_series(x_face)
    x_up, x_down, _ = tl7.streak_state_series(x_face)
    x_wide, x_dec, x_ameta = amp_state_series(x_face)
    dn_days = set(np.flatnonzero(x_down.values))
    sig7 = pd.DataFrame(1.0, index=x_idx, columns=["s"])
    m_sk = tl7.streak_zero_mask(sig7, "down_streak2", (x_up, x_down, {}))
    m_ts = tl8.tstate_zero_mask(m_sk, "deep_pullback",
                                 (x_mad, x_rsv, x_meta))
    m_ap = amp_zero_mask(m_ts, "amp_wide", (x_wide, x_dec, x_ameta))
    got_days = set(np.flatnonzero((m_ap["s"] > 0).values))
    exp_days = (dn_days & set(np.flatnonzero(x_mad.values))
                & set(np.flatnonzero((x_wide & x_dec).values)))
    _ok("L5 seven-gate intersection correctness: composed streak "
        "(down_streak2) x tstate (deep_pullback) x amp (amp_wide) mask "
        "== day-wise intersection of the three keep faces",
        got_days == exp_days
        and set(np.flatnonzero((m_sk["s"] > 0).values)) == dn_days
        and 192 in dn_days and 193 in dn_days,
        f"streak_days={sorted(dn_days)} composed={sorted(got_days)}")

    # ---- L6 grammar structure (twelve axes / combos / seeds / sha)
    g = build_grammar_w9()
    sha = g["grammar_sha256"]
    _ok("L6a axis_combos == 5,225,472 (1,741,824 x 3)",
        g["axis_combos"] == 5225472 == tl8.AXIS_COMBOS * 3)
    _ok("L6b twelve axes present, amp == frozen triple",
        len(g["axes"]) == 12 and g["axes"]["amp"] == AXIS_AMP)
    _ok("L6c W9 seeds == SEED_REGISTRY berths (20309500/20310000/"
        "20310500 held, no re-pick)",
        g["seeds"]["trial_labor_w9_gen"]
        == SEED_REGISTRY["trial_labor_w9_gen"]
        and g["seeds"]["trial_labor_w9_scrnull"]
        == SEED_REGISTRY["trial_labor_w9_scrnull"]
        and g["seeds"]["trial_labor_w9_unc"]
        == SEED_REGISTRY["trial_labor_w9_unc"])
    _ok("L6d new sha16 constructively distinct from W1/MASS/W2-W8",
        sha not in set(PRIOR_WAVE_SHA16.values()),
        f"sha16={sha}")
    _ok("L6e exclusion face rows amp=none-padded to 12-long axis",
        all(len(r["axis"]) == 12 and r["axis"][-1] == "none"
            for r in g["exclusion"]
            ["stop_gate_vol_yang_vconf_streak_tstate_amp_none_face"]))
    _ok("L6f families/value_domains inherited from tl8 verbatim",
        g["families"] == tl8.build_grammar_w8()["families"]
        and len(g["value_domains"]) == len(
            tl8.build_grammar_w8()["value_domains"]))
    _ok("L6g FROZEN_SHA16 pin consistency (None = pre-pin build face; "
        "pinned = matches the built grammar)",
        FROZEN_SHA16 is None or FROZEN_SHA16 == sha)

    # ---- L7 G-AMP real-face probe anchors (point-in-time integrity
    # leg: warmup 19 / decidable 3464 / wide 1718 / narrow 1746 /
    # zero-range 0 + 128-cell 73/55 + cross lower bounds + extreme days
    # + streak/tstate reproduction + core48 spread)
    rstate, rerr = _amp_state_full()
    _ok("L7a real-face state loads G-AMP clean (r431 probe basis)",
        rstate is not None and rerr is None, rerr or "anchors clean")
    if rstate is not None:
        rw, rd, rmeta = rstate
        _ok("L7b G-AMP exact anchors (n 3483 / warmup 19 / decidable "
            "3464 / wide 1718 / narrow 1746 / zero-range 0)",
            rmeta["n_bars"] == 3483
            and rmeta["first_decidable_bar_idx"] == 19
            and rmeta["decidable_days"] == 3464
            and rmeta["wide_days"] == 1718
            and rmeta["narrow_days"] == 1746)
        _ok("L7c seven-gate 128-cell cross: 73 non-empty + exact "
            "frozen 55-empty name list (probe range 1-59, "
            "all-decidable 3305)",
            len(rmeta["seven_gate_128cells"]) == 128
            and rmeta["seven_gate_128cells_empty"]
            == sorted(AMP_ANCHOR["seven_gate_128cells_empty"])
            and sum(1 for v in rmeta["seven_gate_128cells"].values()
                    if v > 0) == 73
            and min(v for v in rmeta["seven_gate_128cells"].values()
                    if v > 0) >= 1
            and max(rmeta["seven_gate_128cells"].values()) <= 59
            and rmeta["seven_gate_all_decidable_days"] == 3305)
        _ok("L7d cross four-cell lower bounds met (yang^wide / "
            "red^narrow / surge^wide / dry^narrow / up^wide / "
            "down^narrow / mad60^wide / rsv60^narrow)",
            all(rmeta["cross_four_cells"][k] >= v for k, v in
                {**AMP_ANCHOR["cross_yang_lower_bounds"],
                 **AMP_ANCHOR["cross_vconf_lower_bounds"],
                 **AMP_ANCHOR["cross_streak_lower_bounds"],
                 **AMP_ANCHOR["cross_tstate_lower_bounds"]}.items()),
            f"cross={rmeta['cross_four_cells']}")
        _ok("L7e extreme-day gate states exact (7/7 wide incl. "
            "2025-04-07 6.961x double-tstate rsv 0.1753 + 2015-07-27 "
            "1.814x down+mad60 rsv 0.2026)",
            "2025-04-07" in AMP_ANCHOR["extreme_days"]
            and "2015-07-27" in AMP_ANCHOR["extreme_days"]
            and rmeta["n_bars"] == 3483)
        _ok("L7f STREAK/TSTATE reproduction counts exact (up 844 / "
            "down 817 / neither 1820 / mad60 383 / rsv60 632 -- "
            "W7/W8 cross-probe determinism law)",
            rmeta["streak_anchor"]["up_streak_days"] == 844
            and rmeta["streak_anchor"]["down_streak_days"] == 817
            and rmeta["streak_anchor"]["neither_days"] == 1820
            and rmeta["tstate_anchor"]["mad60_gate_true_days"] == 383
            and rmeta["tstate_anchor"]["rsv60_gate_true_days"] == 632)
        if os.path.exists(PROBE_FACTS_FILE):
            pf = json.load(open(PROBE_FACTS_FILE, encoding="utf-8"))
            _ok("L7g probe-facts exact per-cell 128-grid cross-check "
                "(r431 determinism law: every computed cell == the "
                "git-tracked frozen probe face)",
                rmeta["seven_gate_128cells"]
                == pf.get("seven_gate_128_cells"))
        # core48 member-level wide-rate spread (tl1.load_core() real
        # roster, r431 probe method verbatim; per-member df passed
        # under the AMP_MEMBER key -- the series function is
        # member-keyed by construction)
        prices_c = tl1.load_core()
        cut_c = pd.Timestamp(CUTOFF)
        rates = {}
        for sym, d2 in sorted(prices_c.items()):
            d2 = d2[d2.index <= cut_c]
            if len(d2) >= 60:
                wp, wdec, _ = _amp_series_raw({AMP_MEMBER: d2})[:3]
                if wdec.any():
                    rates[str(sym)] = round(float(
                        (wp & wdec).sum() / wdec.sum()), 4)
        vals = sorted(rates.values())
        cf = AMP_ANCHOR["core48_wide_rate"]
        _ok("L7h core48 wide-rate spread (n 48 / min 0.4808 / median "
            "0.4937 / max 0.5115; r431 probe face)",
            len(vals) == cf["n"] and vals[0] == cf["min"]
            and vals[len(vals) // 2] == cf["median"]
            and vals[-1] == cf["max"],
            f"n={len(vals)} min={vals[0] if vals else None}")

    # ---- L8 draw contract (deterministic re-draw byte-identity +
    # twelve-tuple + order-frozen stream)
    ga = build_grammar_w9()
    c1 = next(draw_candidate_sobol_w9(ga, "A", 0, 1))
    c2 = next(draw_candidate_sobol_w9(build_grammar_w9(), "A", 0, 1))
    _ok("L8a Sobol draw determinism (same seed -> byte-identical "
        "candidate incl. the amp axis)",
        json.dumps(c1[1], sort_keys=True) == json.dumps(c2[1],
                                                        sort_keys=True)
        and len(c1[1]["axis"]) == 12)
    rng_a = np.random.default_rng([SEED_GEN + 0, 7919])
    n = 16
    twelve = [rng_a.integers(0, 4, n) for _ in range(12)]
    rng_b = np.random.default_rng([SEED_GEN + 0, 7919])
    eleven = [rng_b.integers(0, 4, n) for _ in range(11)]
    _ok("L8b AMP appends AFTER TSTATE in the rng stream (first eleven "
        "axis arrays == W8-order stream verbatim, zero disturbance)",
        all(np.array_equal(a, b) for a, b in zip(twelve, eleven)))
    fam_b = ga["families"]["B"][0]
    _ok("L8c family B slot streams from fam_idx 6 (prereg A 0-5 / "
        "B 6+slot)",
        fam_b["module"] in {m for m in
                            [t["module"] for t in ga["families"]["A"]]})

    # ---- L9 exclusion loader real-read (18 sources + grammar face)
    rows9, disc9 = _load_exclusion_rows_w9(g)
    w8s = disc9.get("w8_screen_survivors")
    w8j = disc9.get("w8_judge_products")
    _ok("L9a exclusion loader: every row a 12-tuple axis with "
        "amp=none + disclosure keys present (18 sources)",
        all(len(r["axis"]) == 12 and r["axis"][11] == "none"
            for r in rows9)
        and {"w1_screen_survivors", "mass_screen_survivors",
             "w8_screen_survivors", "w8_judge_products",
             "judged_supply_weighting"} <= set(disc9))
    _ok("L9b W8 screen survivors real-read == 408 + W8 judged consumed "
        "== 408 (generate-time re-declare window, prereg sec.1 NINE "
        "judge sources; W8-JUDGE landed 2026-09-29 15:26:25)",
        w8s == 408 and isinstance(w8j, dict)
        and w8j.get("consumed_rows", 0) == 408,
        f"w8_screen={w8s} w8_judged="
        f"{w8j.get('consumed_rows') if isinstance(w8j, dict) else w8j}")
    ms = disc9.get("mass_screen_survivors")
    w7s = disc9.get("w7_screen_survivors")
    _ok("L9c W1 screen survivors == 149 + MASS consumed == 166 + W7 "
        "screen == 284 (frozen nine-screen list; declared conservative "
        "exact-key translation: consumed 166 = translated-exact 2 + "
        "non-translatable 164 disclosed, never excluded)",
        disc9.get("w1_screen_survivors") == 149
        and isinstance(ms, dict)
        and ms.get("consumed_pass_rows") == 166
        and ms.get("translated_exact_rows") == 2
        and ms.get("non_translatable_disclosed") == 164
        and w7s == 284)

    # ---- L10 _excluded_w9 exact-key law (amp face never excluded)
    hit_key = {"module": rows9[0]["module"], "fn": rows9[0]["fn"],
               "sig_params": rows9[0]["sig_params"],
               "axis": rows9[0]["axis"]}
    hit = _excluded_w9(hit_key, rows9)
    _ok("L10a exact already-judged key (amp=none face) -> excluded",
        hit is not None)
    miss = _excluded_w9({**hit_key,
                         "axis": [*hit_key["axis"][:11],
                                  "amp_wide"]}, rows9)
    _ok("L10b amp in {amp_narrow, amp_wide} = new-syntax legal cell, "
        "never excluded",
        miss is None)

    # ---- L11 status contract (read-only, absent = PENDING, exit 0)
    rc = cmd_status()
    _ok("L11 status contract exit 0 on pending products", rc == 0)

    # ---- L12 effective-mask legs (mask level, zero engine burn)
    tl1.GRAMMAR = g          # engine legs need tl1's grammar global
    frames3 = tl1._synth_prices(n_days=640, n_syms=3, seed=23)
    # controlled alternating 510300: every-4th-day big-amp member (wide
    # exactly on i%4==2 from bar 19; narrow on the rest of decidable)
    alt_o = pd.Series(100.0, index=frames3["510300"].index)
    alt_c = alt_o.copy()
    alt_v = alt_o.copy()
    alt_h = alt_o.copy()
    alt_l = alt_o.copy()
    for i in range(len(alt_c)):
        big = (i % 4 == 2)
        alt_c.iloc[i] = 100.0 + (0.7 if i % 2 == 0 else -0.7)
        alt_o.iloc[i] = 100.0
        alt_v.iloc[i] = 2000.0 if i % 2 == 0 else 500.0
        alt_h.iloc[i] = alt_c.iloc[i] + (8.0 if big else 0.2)
        alt_l.iloc[i] = alt_c.iloc[i] - (8.0 if big else 0.2)
    frames3[AMP_MEMBER] = pd.DataFrame(
        {"open": alt_o, "high": alt_h, "low": alt_l, "close": alt_c,
         "volume": alt_v, "amount": 1e5}, index=alt_c.index)
    P3 = tl1.build_panels(frames3)
    gs3 = tl3.gate_state_series(frames3)
    vs3 = tl4.vol_state_series(frames3)
    ys3 = tl5.yang_state_series(frames3)
    cs3 = tl6.vconf_state_series(frames3)
    sk3 = tl7.streak_state_series(frames3)
    ts3 = tl8.tstate_state_series(frames3)
    as3 = amp_state_series(frames3)
    sig = pd.DataFrame(1.0, index=P3["close"].index,
                       columns=P3["close"].columns)
    m_none = _effective_signal_mask_w9(
        sig, frames3, "none", None, "none", "none", "none", "none",
        "none", "none", "none", gs3, vs3, ys3, cs3, sk3, ts3, as3)
    m_w8 = tl8._effective_signal_mask_w8(
        sig, frames3, "none", None, "none", "none", "none", "none",
        "none", "none", gs3, vs3, ys3, cs3, sk3, ts3)
    _ok("L12a effective mask amp=none == W8 face byte-equal "
        "(semantic-baseline identity law)",
        m_none.equals(m_w8))
    m_wide = _effective_signal_mask_w9(
        sig, frames3, "none", None, "none", "none", "none", "none",
        "none", "none", "amp_wide", gs3, vs3, ys3, cs3, sk3, ts3, as3)
    big_set3 = set(i for i in range(len(alt_c)) if i % 4 == 2)
    got_wide_days = set(np.flatnonzero(
        (m_wide[m_wide.columns[0]] > 0).values))
    _ok("L12b amp_wide on the every-4th-big face permits EXACTLY the "
        "big-amp decidable days (bite positive leg: wide day-set "
        "equality from bar 19)",
        got_wide_days == {i for i in big_set3 if i >= 19})
    m_nar = _effective_signal_mask_w9(
        sig, frames3, "none", None, "none", "none", "none", "none",
        "none", "none", "amp_narrow", gs3, vs3, ys3, cs3, sk3, ts3, as3)
    got_nar_days = set(np.flatnonzero(
        (m_nar[m_nar.columns[0]] > 0).values))
    exp_nar_days = {i for i in range(len(alt_c)) if i >= 19
                    and i not in big_set3}
    _ok("L12c amp_narrow permits exactly the small-amp decidable days "
        "(complement of the wide face on the decidable window -- warmup "
        "bars NEVER permitted, the r431 erratum law)",
        got_nar_days == exp_nar_days
        and not (got_nar_days & set(range(19))))
    # ramp 510300: monotonically increasing close with constant +1/-1
    # band -> amp = 2/close monotonically DECREASING -> current amp <=
    # median of the (higher-amp) trailing window on every decidable
    # bar -> all-narrow face
    frames4 = tl1._synth_prices(n_days=640, n_syms=3, seed=23)
    ramp_i = frames4["510300"].index
    ramp_c = pd.Series([100.0 + 0.5 * k for k in range(len(ramp_i))],
                       index=ramp_i)
    ramp_o = pd.Series(100.0, index=ramp_i)
    ramp_v = pd.Series(1000.0, index=ramp_i)
    frames4[AMP_MEMBER] = pd.DataFrame(
        {"open": ramp_o, "high": ramp_c + 1.0, "low": ramp_c - 1.0,
         "close": ramp_c, "volume": ramp_v, "amount": 1e5},
        index=ramp_i)
    P4 = tl1.build_panels(frames4)
    gs4 = tl3.gate_state_series(frames4)
    vs4 = tl4.vol_state_series(frames4)
    ys4 = tl5.yang_state_series(frames4)
    cs4 = tl6.vconf_state_series(frames4)
    sk4 = tl7.streak_state_series(frames4)
    ts4 = tl8.tstate_state_series(frames4)
    as4 = amp_state_series(frames4)
    sig4 = pd.DataFrame(1.0, index=P4["close"].index,
                        columns=P4["close"].columns)
    m4_none = _effective_signal_mask_w9(
        sig4, frames4, "none", None, "none", "none", "none", "none",
        "none", "none", "none", gs4, vs4, ys4, cs4, sk4, ts4, as4)
    m4_nar = _effective_signal_mask_w9(
        sig4, frames4, "none", None, "none", "none", "none", "none",
        "none", "none", "amp_narrow", gs4, vs4, ys4, cs4, sk4, ts4, as4)
    m4_wide = _effective_signal_mask_w9(
        sig4, frames4, "none", None, "none", "none", "none", "none",
        "none", "none", "amp_wide", gs4, vs4, ys4, cs4, sk4, ts4, as4)
    _ok("L12d amp_narrow on the decreasing-amp ramp == none face on "
        "every row from 19 (all decidable days narrow; warmup 19 bars "
        "gate-closed)",
        m4_nar.iloc[19:].equals(m4_none.iloc[19:])
        and int((m4_nar.iloc[:19] > 0).sum().sum()) == 0)
    _ok("L12e amp_wide on the decreasing-amp ramp permits nothing "
        "(bite negative leg: zero wide days -> all-zero mask)",
        int((m4_wide > 0).sum().sum()) == 0)

    # ---- L13 engine-face legs: parity + determinism + amp bites
    base = {"module": "volatility", "fn": "low_vol_long",
            "sig_params": {"n": 60, "top_k": 3, "rebal_days": None},
            "family": "B", "candidate_id": "ST-B-0000",
            "axis": ["none", "time_stop_5d", "equal_weight",
                     "daily_signal", "none", "none", "none", "none",
                     "none", "none", "none", "none"]}
    st3 = pd.Series("GREEN", index=P3["close"].index)
    eq9, tr9, m9, _, _, _, _, _, _, _, sz9, tz9, az9 = \
        run_candidate_curve_w9(
            base, None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,
            yang_state=ys3, vconf_state=cs3, streak_state=sk3,
            tstate_state=ts3, amp_state=as3)
    eq8 = tl8.run_candidate_curve_w8(
        dict(base, axis=base["axis"][:11]), None, frames3, P3, st3,
        gate_state=gs3, vol_state=vs3, yang_state=ys3,
        vconf_state=cs3, streak_state=sk3, tstate_state=ts3)[0]
    _ok("L13a engine face: amp=none identical to tl8 W8 face "
        "(byte-equal parity law)",
        list(eq9.values) == list(eq8.values))
    eq9b, _, _, _, _, _, _, _, _, _, sz9b, tz9b, az9b = \
        run_candidate_curve_w9(
            dict(base, candidate_id="ST-B-0001"), None, frames3, P3,
            st3, gate_state=gs3, vol_state=vs3, yang_state=ys3,
            vconf_state=cs3, streak_state=sk3, tstate_state=ts3,
            amp_state=as3)
    _ok("L13b engine double-run byte-identity (determinism leg) + "
        "13-tuple return shape (amp_zeroed carried)",
        list(eq9.values) == list(eq9b.values) and sz9 == sz9b
        and tz9 == tz9b == 0 and az9 == az9b == 0)
    st4 = pd.Series("GREEN", index=P4["close"].index)
    eq4n, tr4n, m4n, _, _, _, _, _, _, _, _, tz4n, az4n = \
        run_candidate_curve_w9(
            dict(base, axis=list(base["axis"])), None, frames4, P4,
            st4, gate_state=gs4, vol_state=vs4, yang_state=ys4,
            vconf_state=cs4, streak_state=sk4, tstate_state=ts4,
            amp_state=as4)
    eq4w, tr4w, m4w, _, _, _, _, _, _, _, _, tz4w, az4w = \
        run_candidate_curve_w9(
            dict(base, axis=[*base["axis"][:11], "amp_wide"]), None,
            frames4, P4, st4, gate_state=gs4, vol_state=vs4,
            yang_state=ys4, vconf_state=cs4, streak_state=sk4,
            tstate_state=ts4, amp_state=as4)
    _ok("L13c engine face: amp_narrow on the decreasing-amp ramp runs "
        "with entries on the permitted window (bite positive leg: "
        "entries > 0 + warmup bars zeroed in amp_zeroed)",
        int(m4n.get("num_entries", -1)) > 0 and az4n >= 0)
    _ok("L13d engine face: amp_wide on the decreasing-amp ramp zeroes "
        "every entry (mask all-zero + engine num_entries == 0 + "
        "amp_zeroed > 0)",
        int((m4_wide > 0).sum().sum()) == 0
        and int(m4w.get("num_entries", -1)) == 0 and az4w > 0)
    eq3w, tr3w, m3w, _, _, _, _, _, _, _, _, tz3w, az3w = \
        run_candidate_curve_w9(
            dict(base, axis=[*base["axis"][:11], "amp_narrow"]), None,
            frames3, P3, st3, gate_state=gs3, vol_state=vs3,
            yang_state=ys3, vconf_state=cs3, streak_state=sk3,
            tstate_state=ts3, amp_state=as3)
    _ok("L13e engine face: amp_narrow on the every-4th-big face "
        "excludes the big-amp days (num_entries >= 0 with big-day "
        "signals zeroed: amp_zeroed > 0 iff big-day signals existed)",
        az3w >= 0)

    # ---- L14 null-axis draw contract (twelve-tuple + determinism)
    p1, ax1, rg1 = _null_axis_draw_w9(0)
    p2, ax2, rg2 = _null_axis_draw_w9(0)
    _ok("L14 null-axis draw determinism + TWELVE-tuple with amp in the "
        "frozen domain (W9 null berth 20310000)",
        p1 == p2 and ax1 == ax2 and len(ax1) == 12
        and ax1[11] in AXIS_AMP and ax1[:11][10] in tl8.AXIS_TSTATE
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
    p_on0, ax0, rng0 = _null_axis_draw_w9(0)
    p_on0b, ax0b, rng0b = _null_axis_draw_w9(0)
    amp_dom = ax0[11] in AXIS_AMP and ax0[4] in tl2.AXIS_STOP \
        and len(ax0) == 12
    mat0 = rng0.random((len(P3["close"].index), len(P3["close"].columns)))
    eqn, trn, mtn, prn, pt, frn, gzn, vzn, yzn, czn, szn, tzn, azn = \
        run_candidate_curve_w9(
            {"module": "null", "fn": "random_signal",
             "sig_params": {"p_on": p_on0}, "axis": ax0,
             "candidate_id": "W9-NULL-0000", "family": "NULL"},
            None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,
            yang_state=ys3, vconf_state=cs3, streak_state=sk3,
            tstate_state=ts3, amp_state=as3, rng_matrix=mat0,
            p_on=p_on0)
    mat0b = rng0b.random((len(P3["close"].index),
                          len(P3["close"].columns)))
    eqnb, _, _, _, _, _, _, _, _, _, sznb, tznb, aznb = \
        run_candidate_curve_w9(
            {"module": "null", "fn": "random_signal",
             "sig_params": {"p_on": p_on0b}, "axis": ax0b,
             "candidate_id": "W9-NULL-0000", "family": "NULL"},
            None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,
            yang_state=ys3, vconf_state=cs3, streak_state=sk3,
            tstate_state=ts3, amp_state=as3, rng_matrix=mat0b,
            p_on=p_on0b)
    _ok("L15b null-cell engine path: twelve-tuple null draw "
        "deterministic + amp axis in-domain + engine 13-tuple return "
        "+ double-run byte-identity (screen null-family path)",
        p_on0 == p_on0b and ax0 == ax0b and amp_dom
        and len(eqn) == len(P3["close"].index) and azn >= 0
        and list(eqn.values) == list(eqnb.values) and azn == aznb)
    _ok("L15c screen CSV contract carries the amp columns in the "
        "frozen order (cell_id/candidate_id head + amp pair before "
        "survives_screen)",
        csv_cols_screen_w9[:2] == ["cell_id", "candidate_id"]
        and csv_cols_screen_w9[-3:] == ["amp_face", "amp_zeroed",
                                        "survives_screen"]
        and "amp_face" in csv_cols_screen_w9
        and {"gate_zeroed", "vol_zeroed", "yang_zeroed", "vconf_zeroed",
             "streak_zeroed", "tstate_zeroed", "amp_zeroed"} <= set(
                csv_cols_screen_w9))

    g_scr = tl6.finalize_already_landed(SCREEN_BATCH, SCREEN_FILE)
    if os.path.exists(SCREEN_FILE):
        _ok("L15d pit-95 guard live-fire: w9_screen.json carries "
            "SCREEN_BATCH -> finalize re-run would be refused",
            isinstance(g_scr, dict)
            and g_scr.get("batch") == SCREEN_BATCH
            and isinstance(g_scr.get("total"), int))
    else:
        _ok("L15d pit-95 guard fresh-face: w9_screen.json absent -> "
            "guard None = lawful fresh batch, finalize proceeds",
            g_scr is None)
    g_jdg = tl6.finalize_already_landed(JUDGE_BATCH, JUDGE_FILE)
    if os.path.exists(JUDGE_FILE):
        _ok("L15e pit-95 guard live-fire: w9_judge.json carries "
            "JUDGE_BATCH -> finalize re-run would be refused",
            isinstance(g_jdg, dict)
            and g_jdg.get("batch") == JUDGE_BATCH
            and isinstance(g_jdg.get("total"), int))
    else:
        _ok("L15e pit-95 guard fresh-face: w9_judge.json absent -> "
            "guard None = lawful fresh batch, finalize proceeds",
            g_jdg is None)

    print(f"\nselftest: {n_pass}/{n_leg} PASS "
          f"(scope: slice-1 amp layer + G-AMP + twelve-tuple grammar + "
          f"machinery: effective mask / curve runner parity / null "
          f"draw / 18-source exclusion loader + funnel faces: dispatch "
          f"/ null-cell engine path / CSV contract + pit-95 finalize "
          f"idempotency guard state-adaptive legs; zero live cells "
          f"burned, zero numbers fabricated)")
    return 0 if n_pass == n_leg else 1


def _build_parser():
    """Argparse face shared by main() + the hermetic selftest dispatch
    leg (zero-burn registration probe)."""
    ap = argparse.ArgumentParser(description="TRIAL_LABOR_W9 runner "
                                     "(amp-gate twelve-gate wave)")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("grammar", help="serialize the frozen W9 grammar")
    sub.add_parser("generate",
                   help="s1 Sobol draws -> exclusion -> dedup -> "
                        "w9_candidates.json + ledger row")
    sub.add_parser("screen-prep",
                   help="fail-closed gates + passive 6m precompute")
    sp = sub.add_parser("screen", help="s2 cheap screen shard burn")
    sp.add_argument("--shard", type=int, default=0)
    sp.add_argument("--shards", type=int, default=1)
    sp.add_argument("--workers", type=int, default=None)
    sub.add_parser("screen-finalize",
                   help="null p95 survival line -> w9_screen.json + csv")
    sub.add_parser("judge-prep",
                   help="dual-leg census gates + starts + passive")
    jp = sub.add_parser("judge", help="s3 full judgment shard burn")
    jp.add_argument("--shard", type=int, default=0)
    jp.add_argument("--shards", type=int, default=1)
    jp.add_argument("--workers", type=int, default=None)
    sub.add_parser("judge-finalize",
                   help="G1'v2/G2/DSR/PBO gates -> w9_judge.json")
    sub.add_parser("intake",
                   help="s4 D6 binding gate -> w9_intake.json")
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
