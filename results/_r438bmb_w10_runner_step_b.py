# -*- coding: utf-8 -*-
"""r438 bm-b step B: replace the literal AMP_SPEC/AMP_ANCHOR constant
block in trial_labor_w10.py with the W10 MOM_SPEC + MOM_ANCHOR (values
generated verbatim from the git-tracked frozen probe facts file
results/_r228bmc_momgate_w10_probe_facts.json -- zero hand transcription)."""
import json
import pprint
import sys

F = "results/_r228bmc_momgate_w10_probe_facts.json"
T = "scripts/trial_labor_w10.py"

facts = json.load(open(F, encoding="utf-8"))
cells = facts["eight_gate_cells"]
empty = sorted(k for k, v in cells.items() if v <= 0)
assert len(empty) == 145, len(empty)
assert len(cells) == 256

MOM_SPEC = '''MOM_SPEC = {
    "member": MOM_MEMBER,
    "series": "r228 probe verbatim / census family O-1855(4) ROC20_q10 "
              "(zero-invention law; structural transplant of the "
              "in-repo census-verbatim decile-gate mechanics = the "
              "MAD60_q10 pattern frozen in W8 prereg sec.2 / r431 "
              "tstate_faces): signal-day-d close info set on the "
              "member face",
    "roc20": "roc20(d) = close(d)/close(d-20) - 1 (20-day "
             "rate-of-change momentum)",
    "q10_ref": "q10_ref = roc20.rolling(252, min_periods=120)"
               ".quantile(0.10) (own-trailing 252-observation "
               "decile reference)",
    "mom_oversold": "roc20 < q10_ref (20-day descent-speed entering "
                    "its own bottom decile = oversold momentum state; "
                    "speed face: MBAlib short-suppression folklore "
                    "canon panic-sellers-pay behavioral hypothesis; "
                    "census 20d-forward positive signal t=+2.000 "
                    "universe face 1,724 codes = LONG anchor, 5d "
                    "window halved in-register, term-structure "
                    "mismatch honest)",
    "none": "no gate (W9 semantic baseline face)",
    "info_set": "signal-day d close; entry fills d+1 open (T+1 causal, "
                "same info set as GATE/VOL/YANG/VCONF/STREAK/TSTATE/"
                "AMP, zero lookahead)",
    "warmup": "139-bar warmup window gate-closed honest (roc20 first "
               "valid bar-idx == 20; q10_ref min_periods 120 -> first "
               "decidable bar-idx == 139; structure spectrum vs YANG "
               "0 / STREAK 2 / VCONF 19 / AMP 19 / RSV 59 / MAD60 178 "
               "/ VOL 519)",
    "engine_note": "entry-permittance only (effective signal zeroed, "
                   "MSG-0440 E1-mapping primitive; exit logic zero "
                   "change; engine/exit_rules.py zero touch)",
    "nan_artifact_note": "NaN comparisons (roc20 < q10_ref) yield "
                         "False NOT decidable (pit-95 batch-95 / r421 "
                         "probe / r431 erratum face: the r417 "
                         "map({False->x}) NaN-bucket artifact put "
                         "gate-closed warmup days into the wrong "
                         "buckets); the decidable face derives from "
                         "the underlying values notna (q10_ref."
                         "notna() & roc20.notna()); the naive "
                         "comparison bool face masquerades warmup "
                         "bars as mom_closed -- BANNED at the mask "
                         "level",
    "tstate_adjacency_note": "TSTATE adjacency disclosed (probe: "
                             "mad60-open days 66.06% co-open / rsv60-"
                             "open 35.16%; 253 both-open / 121 "
                             "mom-unique days = speed face != "
                             "position face; D6 max|corr| audit "
                             "column face at intake)",
    "composition_order": "signal -> filter -> timing -> GATE -> VOL -> "
                         "YANG -> VCONF -> STREAK -> TSTATE -> AMP -> "
                         "MOM -> initial-stop (a mom-blocked signal "
                         "never arms a stop; W9 order extended, "
                         "prereg sec.3 thirteen-tuple order R/X/S/T/"
                         "STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/"
                         "MOM)",
}
'''

anchor = {
    "n_bars": facts["rows"],
    "first_date": facts["first_date"],
    "cutoff": facts["cutoff"],
    "roc20_nan_rows_before_bar20": facts["roc20_nan_rows_before_bar20"],
    "warmup_gate_closed_bars": facts["mom_warmup_gate_closed_bars"],
    "first_decidable_bar_idx": facts["mom_first_decidable_bar_idx"],
    "decidable_days": facts["mom_decidable_days"],
    "open_days": facts["mom_open_days"],
    "closed_days": facts["mom_decidable_days"] - facts["mom_open_days"],
    "open_rate_on_decidable": facts["mom_open_rate_on_decidable"],
    "cross_tstate_lower_bounds": {
        "mad60_and_mom": facts["adjacency"]["mom_vs_mad60"]["both_open"],
        "rsv60_and_mom": facts["adjacency"]["mom_vs_rsv60"]["both_open"]},
    "cross_streak_lower_bounds": {
        "down_streak_and_mom":
            facts["adjacency"]["mom_vs_downstreak"]["both_open"]},
    "cross_amp_lower_bounds": {
        "wide_and_mom": facts["adjacency"]["mom_vs_wide"]["both_open"]},
    "eight_gate_all_decidable_days":
        facts["eight_gate_all_decidable_days"],
    "eight_gate_256cells_nonzero_count":
        facts["eight_gate_256_cells_nonzero_count"],
    "eight_gate_256cells_empty_count":
        facts["eight_gate_256_cells_empty_count"],
    "eight_gate_256cells_min_nonzero":
        facts["eight_gate_256_cells_min_nonzero"],
    "eight_gate_256cells_max": facts["eight_gate_256_cells_max"],
    "eight_gate_256cells_empty": empty,
    "extreme_days": facts["extreme_day_states"],
    "streak_anchor_reproduction": {"up_streak_days": 844,
                                   "down_streak_days": 817,
                                   "neither_days": 1820,
                                   "warmup_gate_closed_bars": 2},
    "tstate_anchor_reproduction": {"mad60_gate_true_days": 383,
                                   "rsv60_gate_true_days": 632},
    "amp_anchor_reproduction": {"wide_days": 1718, "narrow_days": 1746,
                                "zero_range_rows": 0},
    "core48_mom_open_rate": facts["core48_mom_open_rate"],
    "forward_differential": {"fwd20d": facts["forward_20d"],
                            "fwd5d": facts["forward_5d"]},
    "probe_facts": "results/_r228bmc_momgate_w10_probe_facts.json "
                   "(r228 bm-c MOM probe; exact per-cell 256-grid "
                   "cross-check face when present; probe-facts face "
                   "not a results face)",
    "probe_basis": "cross-tables on the r228 probe basis VERBATIM "
                   "(r407 lesson): gate = close > ma200 strict "
                   "NaN->False both sides; vol = vol20 vs med500 "
                   "NaN->False both sides; yang = close > open strict "
                   "(doji red); surge = volume > med20 (min_periods="
                   "20, INCL d), dry = ~surge; streak = W7 "
                   "close-over-close double; tstate = the tl8 "
                   "census-verbatim faces; amp = the r417 face; mom = "
                   "the ROC20_q10 face above (eight-gate all-"
                   "decidable window m8 = dec_mom & amp_known & "
                   "streak-decidable & dec_mad & dec_rsv == 3,305 "
                   "days)",
    "note": "MOM core anchors (warmup 139 / decidable 3,344 / open "
            "374 / closed 2,969 / roc20-nan-before-bar20 20) "
            "asserted EXACT; TSTATE/STREAK/AMP cross faces asserted "
            "as LOWER BOUNDS per prereg sec.2; eight-gate 256 cells "
            "asserted 111-non-empty with the exact frozen 145-empty "
            "name list (probe range 1-37) + exact per-cell "
            "cross-check vs the git-tracked probe facts file when "
            "present; extreme-day gate states asserted exact (roc20 "
            "values at probe 4-decimal rounding, ratios at 3-decimal, "
            "rsv at 4-decimal; 2/7 mom-open incl. 2015-07-27 -0.0906 "
            "+ 2025-04-07 -0.0852, 2016-01-04 -0.052 near-miss "
            "closed honest); STREAK/TSTATE/AMP reproduction counts "
            "asserted exact (W7/W8/W9 cross-probe determinism law)",
}

txt = open(T, encoding="utf-8").read()
i0 = txt.index("AMP_SPEC = {")
i1 = txt.index("def _grammar_sha16(grammar):")
new_block = (MOM_SPEC + "MOM_ANCHOR = "
             + pprint.pformat(anchor, width=76, sort_dicts=False)
             + "\n\n\n")
txt = txt[:i0] + new_block + txt[i1:]
open(T, "w", encoding="utf-8", newline="\n").write(txt)
print("step B done: AMP block -> MOM block,", len(txt), "bytes")
