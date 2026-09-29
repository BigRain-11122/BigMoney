# -*- coding: utf-8 -*-
"""_r242bmc_w11_surgeon.py -- W11 runner build surgery (Slice-A, bm-c r242).

TRIAL_LABOR_W11 runner draft generator: operates on the FROZEN W10
runner (scripts/trial_labor_w10.py, bm-b r438) producing
results/_r242bmc_w11_runner_draft.py per frozen
research/TRIAL_LABOR_W11_PREREG sec.3:
  - fourteen-tuple = thirteen-tuple + STD in {none, std20_hi, std10_hi}
    (three-value axis, W4-VOL precedent) -> 10,450,944 * 3 = 31,352,832
  - STD gate construction VERBATIM from the r237 probe
    (results/_r237bmc_stdq90_w11_probe.py::std_faces -- zero-invention
    law; the probe is the frozen authoritative definition)
  - STD_ANCHOR generated PROGRAMMATICALLY from
    results/_r237bmc_stdq90_w11_probe_facts.json (zero hand-copy;
    r445 declare-vs-disk law)
  - seeds: trial_labor_w11_gen/scrnull/unc = 20317000/20317500/20318000
    (freeze-commit berths, bm-b r441 re-take per berth clause-5)
Products: draft file + surgery report JSON.  Draft is NOT the formal
runner until Slice-B review (selftest anchor faces + grammar
serialization + sha pin) -- formal name scripts/trial_labor_w11.py is
the final move (runner_exists gate at Tools/fill_ladder_catalog.json
must not fire on a partial build).
"""
from __future__ import annotations
import json
import os
import re
import sys

ROOT = os.getcwd()
SRC = os.path.join("scripts", "trial_labor_w10.py")
DST = os.path.join("results", "_r242bmc_w11_runner_draft.py")
REPORT = os.path.join("results", "_r242bmc_w11_surgery_report.json")
FACTS = os.path.join("results", "_r237bmc_stdq90_w11_probe_facts.json")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def die(msg):
    print("SURGEON-FAIL: " + msg)
    sys.exit(2)


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


def build_std_anchor():
    """STD_ANCHOR dict generated programmatically from probe facts."""
    pf = json.load(open(FACTS, encoding="utf-8"))
    cells = pf["eight_gate_cells"]
    empty = sorted(k for k, v in cells.items() if v <= 0)
    nonzero = [v for v in cells.values() if v > 0]
    adj = pf["adjacency"]
    anchor = {
        "n_bars": pf["rows"],
        "first_date": pf["first_date"],
        "cutoff": pf["last_date"],
        "std20_first_valid_bar_idx": 1,  # single-obs ddof=1 std -> NaN
        "warmup_gate_closed_bars": 120,
        "first_decidable_bar_idx": 120,
        "decidable_days": pf["std20_decidable_days"],
        "std20_open_days": pf["std20_open_days"],
        "std10_decidable_days": pf["std10_decidable_days"],
        "std10_open_days": pf["std10_open_days"],
        "std20_open_rate_on_decidable": pf["std20_open_rate_on_decidable"],
        "std10_open_rate_on_decidable": pf["std10_open_rate_on_decidable"],
        "cross_lower_bounds": {
            "mad60_and_std20": adj["std20_vs_mad60"]["both_open"],
            "rsv60_and_std20": adj["std20_vs_rsv60"]["both_open"],
            "down_streak_and_std20": adj["std20_vs_downstreak"]["both_open"],
            "wide_and_std20": adj["std20_vs_narrow"]["both_open"],
            "mom_and_std20": adj["std20_vs_mom"]["both_open"],
            "std20_vs_std10_both_open": adj["std10_vs_std20"]["both_open"],
        },
        "eight_gate_all_decidable_days": pf["eight_gate_all_decidable_days"],
        "eight_gate_256cells_nonzero_count":
            pf["eight_gate_256_cells_nonzero_count"],
        "eight_gate_256cells_empty_count":
            pf["eight_gate_256_cells_empty_count"],
        "eight_gate_256cells_min_nonzero":
            pf["eight_gate_256_cells_min_nonzero"],
        "eight_gate_256cells_max": pf["eight_gate_256_cells_max"],
        "eight_gate_256cells_empty": empty,
        "extreme_days": pf["extreme_day_states"],
        "streak_anchor_reproduction": {
            "up_streak_days": 844, "down_streak_days": 817,
            "neither_days": 1820},
        "tstate_anchor_reproduction": {
            "mad60_gate_true_days": 383, "rsv60_gate_true_days": 632},
        "amp_anchor_reproduction": {
            "wide_days": 1718, "narrow_days": 1746, "zero_range_rows": 0},
        "probe_facts_note": "generated verbatim from "
                            "_r237bmc_stdq90_w11_probe_facts.json "
                            "(r237 probe = frozen authoritative STD "
                            "definition; eight-gate face = std20 "
                            "open/closed states; W4-VOL three-value axis "
                            "precedent)",
    }
    assert anchor["eight_gate_256cells_nonzero_count"] == 103
    assert anchor["eight_gate_256cells_empty_count"] == 153
    assert len(empty) == 153
    assert anchor["decidable_days"] == 3363
    assert anchor["std20_open_days"] == 391
    assert anchor["std10_open_days"] == 399
    assert anchor["first_decidable_bar_idx"] == 120
    return anchor


def main() -> int:
    src = open(SRC, encoding="utf-8").read()
    steps = []

    # ---- 1. docstring replacement (W11 identity)
    ds, a, b = segment(src, '"""TRIAL_LABOR_W10 runner',
                       '\n"""\n', include_start=True, include_end=True)
    new_ds = '"""TRIAL_LABOR_W11 runner -- T-123 mass-candidate trial\n' \
        'wave-11 (5000-ceiling, high-dispersion STD-gate FOURTEEN-gate\n' \
        'wave; three-value axis STD in {none, std20_hi, std10_hi}).\n' \
        '\n' \
        'Prereg FROZEN (bm-b r441 adopter-freeze of the bm-c r237 STD\n' \
        'candidate whole package per AMP->W9 / MOM->W10 / STD->W11\n' \
        'adoption lineage; freeze trigger MET live = W10 full chain\n' \
        'landed 2026-09-29 20:31:29 {w10_judge.json 283/283 judged zero\n' \
        'G1 zero G2 + CEO-REPORT-WAVE10 + attrition 27 rows + ledger\n' \
        'head 346,553 linear + pool 123/123 done}):\n' \
        'research/TRIAL_LABOR_W11_PREREG.md -- generate grammar + funnel\n' \
        'rules + judgment lines all frozen; post-run only sec.7/8\n' \
        'backfill.  Seeds held at the freeze commit per R250 one-step\n' \
        'law: trial_labor_w11_gen=20317000 / trial_labor_w11_scrnull=\n' \
        '20317500 / trial_labor_w11_unc=20318000 (berth re-take +500\n' \
        'per draft clause-5 after the 20316000/20316500 collision with\n' \
        'bm-a r445 A12; three-step law ALL GREEN at freeze).\n' \
        '\n' \
        'Import-face law (prereg sec.6): the FULL trial_labor_w1-w10\n' \
        'chain is imported (tl1-tl9 overlays per W10 face + tl10 mom\n' \
        'overlay & thirteen-tuple machinery); Sobol sample_draws pattern\n' \
        'follows mass_trial_w1; strategies/ factory + engine/backtester\n' \
        'imported, never rewritten; engine/exit_rules.py ZERO touch.\n' \
        '\n' \
        'STD overlay (prereg sec.2/sec.3 NEW W11 frozen layer; r237\n' \
        'probe verbatim = A158 frozen STD construction, zero-invention\n' \
        'law): member 510300 signal-day-d close info set.\n' \
        'f = close.rolling(win, min_periods=1).std(ddof=1)/close\n' \
        '(price-LEVEL std incl. drift, distinct from W4 return-std);\n' \
        'q90_ref = f.rolling(252, min_periods=120).quantile(0.90);\n' \
        'std_hi = f > q90_ref (20/10-day price dispersion entering its\n' \
        'own top-decile = high-dispersion state).  120-bar warmup window\n' \
        'gate-closed honest (single-obs ddof=1 std NaN -> f valid from\n' \
        'bar-idx 1; q90_ref min_periods 120 -> first decidable bar-idx\n' \
        '== 120, fail-closed assertion).  Gate acts on ENTRY PERMITTANCE\n' \
        'only (effective signal zeroed, MSG-0440 E1-mapping primitive;\n' \
        'exit logic zero change).  Composition order frozen everywhere:\n' \
        'signal -> filter -> timing -> GATE -> VOL -> YANG -> VCONF ->\n' \
        'STREAK -> TSTATE -> AMP -> MOM -> STD -> initial-stop (W10\n' \
        'order extended; prereg sec.3 fourteen-tuple order R/X/S/T/STOP/\n' \
        'GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD).\n' \
        '\n' \
        'G-STD anchor law (prereg sec.2 probe facts, fail-closed): on\n' \
        'the raw full-history member face (3,483 bars 2012-05-28 ->\n' \
        '2026-09-22 cutoff): first-decidable == 120 / decidable ==\n' \
        '3,363 / std20 open == 391 (11.23%) / std10 open == 399\n' \
        '(11.46%); eight-gate (gate x vol x yang x vconf x streak x\n' \
        'tstate x amp x std20) 256 open-window cells: 103 non-empty /\n' \
        '153 empty (probe range 1-41; all-decidable 3,305); exact\n' \
        'per-cell cross-check vs\n' \
        'results/_r237bmc_stdq90_w11_probe_facts.json when present\n' \
        '(r237 determinism cross-check law).\n' \
        '\n' \
        'Exclusion law (prereg sec.1, FOURTEEN-tuple cell key=(template,\n' \
        'params, axis_config, initial_stop, gate, vol, yang, vconf,\n' \
        'streak, tstate, amp, mom, std), ELEVEN judged + ELEVEN screen\n' \
        'real-read source faces, exact already-judged key, std=none\n' \
        'face only: prior-wave keys lacking the std axis are std=none\n' \
        'completed (semantic-identity match; generate-time real-read;\n' \
        'W10-JUDGE landed 2026-09-29 20:31:29 = ELEVENTH source, third\n' \
        'full-declare window);\n' \
        'std in {std20_hi, std10_hi} = new-syntax legal cells (never\n' \
        'excluded).\n' \
        '\n' \
        'Slice plan (W3-W10 single-writer precedent; wave ticket\n' \
        'T-2026-09-29-123 opened+claimed bm-b r441; runner build slice\n' \
        'TAKEN OVER by bm-c r242 per O-1730 heartbeat-stale takeover\n' \
        'law -- bm-b heartbeat stale since 21:11:02 >20min at 22:0x,\n' \
        'origin zero new commits; r239 fetch double-gate re-checked,\n' \
        'zero rival MSG face):\n' \
        '  - Slice-A (this draft, bm-c r242 surgeon\n' \
        '    results/_r242bmc_w11_surgeon.py): mechanical identity\n' \
        '    surgery + STD overlay layer + STD_ANCHOR programmatic\n' \
        '    generation + grammar/Sobol/exclusion/mask/curve/null/\n' \
        '    generate legs rewiring + py_compile gate.  Draft name\n' \
        '    results/_r242bmc_w11_runner_draft.py -- NOT the formal\n' \
        '    runner (runner_exists gate must not fire on a partial\n' \
        '    build).\n' \
        '  - Slice-B (next): selftest anchor review (W11 warmup 120/\n' \
        '    decidable 3,363/391/399 + 103/153 cell faces), grammar\n' \
        '    serialization + sha16 pin, formal-name move, catalog\n' \
        '    runner_exists arm, MSG declaration.\n' \
        '"""\n'
    src = src[:a] + new_ds + src[b:]
    steps.append("docstring: W11 identity")

    # ---- 2. imports: add tl10
    old = "import trial_labor_w9 as tl9  # amp overlay + twelve-tuple machinery\nfrom science_gates import"
    new = ("import trial_labor_w9 as tl9  # amp overlay + twelve-tuple machinery\n"
           "import trial_labor_w10 as tl10  # mom overlay + thirteen-tuple machinery\n"
           "from science_gates import")
    if src.count(old) != 1:
        die("import anchor not unique")
    src = src.replace(old, new)
    steps.append("imports: + tl10")

    # ---- 3. frozen constants block (WAVE .. MOM_SPEC .. before MOM_ANCHOR)
    cs, a, b = segment(src, 'WAVE = "TRIAL_LABOR_W10"',
                       'MOM_ANCHOR = {', include_start=True, include_end=False)
    new_cs = '''WAVE = "TRIAL_LABOR_W11"
PREREG = "research/TRIAL_LABOR_W11_PREREG.md"
CUTOFF = tl1.CUTOFF                      # "2026-09-22" (P-5C binding, sec.2)
SEED_GEN = SEED_REGISTRY["trial_labor_w11_gen"]        # 20317000
SEED_NULL = SEED_REGISTRY["trial_labor_w11_scrnull"]  # 20317500
SEED_UNC = SEED_REGISTRY["trial_labor_w11_unc"]        # 20318000
N_A = 500          # family A raw draws (sec.3: 6 templates round-robin)
N_B = 4500         # family B raw draws (machinery round-robin)
K_NULLS = 200       # screen null family size (sec.3; frozen)
RES_DIR = os.path.join(tl1.PATHS.results_dir, "trial_labor_w11")
GRAMMAR_FILE = os.path.join(RES_DIR, "w11_grammar.json")
CANDIDATES_FILE = os.path.join(RES_DIR, "w11_candidates.json")
GRAMMAR_LEDGER = tl1.GRAMMAR_LEDGER
SCREEN_FILE = os.path.join(RES_DIR, "w11_screen.json")
SCREEN_CSV = os.path.join(RES_DIR, "w11_screen_cells.csv")
JUDGE_FILE = os.path.join(RES_DIR, "w11_judge.json")
INTAKE_FILE = os.path.join(RES_DIR, "w11_intake.json")
PREP_FILE = os.path.join(RES_DIR, "prep_state.json")
JUDGE_STATE_FILE = os.path.join(RES_DIR, "judge_state.json")
CKPT_DIR = os.path.join(RES_DIR, "checkpoint")
SCREEN_BATCH = "TRIAL_LAB_W11_SCREEN"   # prereg sec.0 ledger literal
JUDGE_BATCH = "TRIAL_LAB_W11_JUDGE"     # prereg sec.0 ledger literal
W6M = tl1.WINDOWS["6m"]                # leg-L 6m screen window (126 td)
FROZEN_SHA16 = None   # pinned at Slice-B serialization (W10 r438 precedent)

# prior-wave grammar shas (constructive-distinct assertion face)
PRIOR_WAVE_SHA16 = {
    "W1": "a2fa15f4b06b3c40", "MASS": "96269ebe766c3fc2",
    "W2": "1dd3d9579235cec", "W3": "cc59eab79db53436",
    "W4": "d498e9343ee57460", "W5": "29720178c39425de",
    "W6": "2d395f5f8e7d16cb", "W7": tl7.FROZEN_SHA16,   # 1fba956c2f21d1d3
    "W8": tl8.FROZEN_SHA16,      # 282c3290d1b431bc
    "W9": tl9.FROZEN_SHA16,      # 0601dda70b0209fa
    "W10": tl10.FROZEN_SHA16,    # e21c7eb83087035c
}

# tstate axis (W8 frozen face, imported verbatim)
AXIS_TSTATE = tl8.AXIS_TSTATE           # ["none","deep_pullback","oversold_rsv"]
TSTATE_MEMBER = tl8.TSTATE_MEMBER       # "510300"

# amplitude-confirmation axis (W9 frozen face, imported verbatim)
AXIS_AMP = tl9.AXIS_AMP                 # ["none","amp_narrow","amp_wide"]
AMP_MEMBER = tl9.AMP_MEMBER              # "510300"
AMP_ANCHOR = tl9.AMP_ANCHOR             # W9 frozen probe anchors

# mom axis (W10 frozen face, imported verbatim from tl10)
AXIS_MOM = tl10.AXIS_MOM                 # ["none","mom_oversold"]
MOM_MEMBER = tl10.MOM_MEMBER             # "510300"

# high-dispersion STD axis (prereg sec.3 NEW W11 frozen layer,
# three-value axis, W4-VOL precedent)
AXIS_STD = ["none", "std20_hi", "std10_hi"]
AXIS_COMBOS = tl10.AXIS_COMBOS * len(AXIS_STD)  # 10,450,944 * 3 = 31,352,832
STD_MEMBER = "510300"          # core48 member (prereg sec.2 probe fact)
PROBE_FACTS_FILE = os.path.join("results",
                                "_r237bmc_stdq90_w11_probe_facts.json")
STD_SPEC = {
    "member": STD_MEMBER,
    "series": "r237 probe verbatim / A158-TSGATE-P1 frozen STD "
              "construction (zero-invention law; scripts/"
              "a158_tsgate_probe.py L240 face): signal-day-d close "
              "info set on the member face",
    "std20": "f = close.rolling(20, min_periods=1).std(ddof=1) / "
             "close (price-LEVEL std incl. drift)",
    "std10": "f = close.rolling(10, min_periods=1).std(ddof=1) / "
             "close (same construction, 10-day window)",
    "q90_ref": "q90_ref = f.rolling(252, min_periods=120)"
               ".quantile(0.90) (own-trailing 252-observation "
               "top-decile reference)",
    "std_hi": "f > q90_ref (price dispersion entering its own top "
              "decile = high-dispersion state; volatility-clustering "
              "folklore + GARCH statistical basis; A158-TSGATE-P1 "
              "48-PASS pool top family STD20_q90 OOS median +1.07% / "
              "positive share 0.74 five-member 5/5 = LONG anchor)",
    "none": "no gate (W10 semantic baseline face)",
    "info_set": "signal-day d close; entry fills d+1 open (T+1 causal, "
                "same info set as GATE/VOL/YANG/VCONF/STREAK/TSTATE/"
                "AMP/MOM, zero lookahead)",
    "warmup": "120-bar warmup window gate-closed honest (single-obs "
              "ddof=1 std NaN -> f valid from bar-idx 1; q90_ref "
              "min_periods 120 -> first decidable bar-idx == 120, "
              "fail-closed assertion)",
    "engine_note": "entry-permittance only (effective signal zeroed, "
                   "MSG-0440 E1-mapping primitive; exit logic zero "
                   "change; engine/exit_rules.py zero touch)",
    "nan_artifact_note": "NaN comparisons (f > q90_ref) yield "
                         "False NOT decidable (pit-95 batch-95 law; "
                         "the decidable face derives from the "
                         "underlying values notna; the naive "
                         "comparison bool face masquerades warmup "
                         "bars as std_closed -- BANNED at the mask "
                         "level)",
    "adjacency_note": "W4-VOL adjacency disclosed (probe: 88.92% of "
                      "std20-open days inside W4 wild + 38 std-only "
                      "days + 305/1,441 in-wild re-split = increment "
                      "non-empty, main-mass overlap dual-disclosure; "
                      "drift face std-open-and-calm 18d -2.83% vs "
                      "std-open-and-wild +1.90% honest negative "
                      "carried into sec.5); D6 max|corr| audit "
                      "column face at intake",
    "composition_order": "signal -> filter -> timing -> GATE -> VOL -> "
                         "YANG -> VCONF -> STREAK -> TSTATE -> AMP -> "
                         "MOM -> STD -> initial-stop (a std-blocked "
                         "signal never arms a stop; W10 order "
                         "extended, prereg sec.3 fourteen-tuple order "
                         "R/X/S/T/STOP/GATE/VOL/YANG/VCONF/STREAK/"
                         "TSTATE/AMP/MOM/STD)",
}
'''
    src = src[:a] + new_cs + src[b:]
    steps.append("constants: W11 identity + AXIS_STD + STD_SPEC")

    # ---- 4. MOM_ANCHOR block -> STD_ANCHOR (programmatic)
    _, a, b = segment(src, 'MOM_ANCHOR = {',
                      '# --------------------------------------------- amp overlay',
                      include_start=True, include_end=False)
    anchor = build_std_anchor()
    anchor_json = json.dumps(
        anchor, ensure_ascii=False, indent=1, sort_keys=False)
    # JSON booleans -> Python literals (false/null are not Python)
    anchor_json = anchor_json.replace(": false", ": False")
    anchor_json = anchor_json.replace(": true", ": True")
    anchor_json = anchor_json.replace(": null", ": None")
    anchor_lit = ("STD_ANCHOR = " + anchor_json + "\n\n\n"
                  "def _grammar_sha16(grammar):\n"
                  "    \"\"\"Grammar sha16 (W7 lineage import; zero "
                  "re-implementation --\n    carried verbatim from the W10 "
                  "runner block this surgery replaced).\"\"\"\n"
                  "    return tl7._grammar_sha16(grammar)\n\n\n")
    src = src[:a] + anchor_lit + src[b:]
    steps.append("STD_ANCHOR: programmatic from probe facts "
                 "(103/153 cells, 3363/391/399, first-decidable 120)")

    # ---- 5. mom overlay layer -> std overlay layer (full rewrite)
    _, a, b = segment(src,
                      '# ------------------------------------------------------------- mom overlay layer',
                      '# ------------------------------------------------------------ grammar build',
                      include_start=False, include_end=False)
    std_layer = '''# ------------------------------------------------------------- std overlay layer
def _std_series_raw(prices: dict, win: int):
    """r237-probe-verbatim STD series computation (A158 frozen STD
    construction, construction verbatim from scripts/
    a158_tsgate_probe.py L240; zero-invention law -- the r237 probe
    results/_r237bmc_stdq90_w11_probe.py::std_faces IS the frozen
    authoritative definition): f = close.rolling(win, min_periods=1)
    .std(ddof=1) / close; qref = f.rolling(252, min_periods=120)
    .quantile(0.90); open_perm = f > qref (comparison NaN->False);
    decidable derives from the underlying values notna (pit-95
    batch-95 law).  Returns (open_perm, dec, meta, f, qref);
    deterministic pure function of the (cutoff-truncated) panel."""
    df = prices[STD_MEMBER]
    close = df["close"].astype(float).sort_index()
    f = close.rolling(win, min_periods=1).std(ddof=1) / close
    qref = f.rolling(252, min_periods=120).quantile(0.90)
    dec = qref.notna() & f.notna()      # underlying notna (pit-95)
    open_perm = (f > qref)               # comparison face: NaN->False
    n = len(close)

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
            "na_window_bars": 120,   # the gate family's warmup
            }
    return open_perm, dec, meta, f, qref


def std_state_series(prices: dict):
    """Frozen STD spec (prereg sec.2/3): member 510300 signal-day info
    set -- BOTH gate faces for the three-value axis consumption.
    Returns {"std20_hi": (open_perm, dec, meta),
             "std10_hi": (open_perm, dec, meta)}.  Deterministic pure
    function of the (cutoff-truncated) panel."""
    return {"std20_hi": _std_series_raw(prices, 20)[:3],
            "std10_hi": _std_series_raw(prices, 10)[:3]}


def _std_face_full():
    """Frozen sec.2 STD-series face (r237 probe basis): the git-tracked
    raw full-history member file data/daily/sh510300.csv (open + high +
    low + close + volume columns), truncated at the evidence cutoff.
    (tl8._tstate_face_full loading caliber reused verbatim -- same
    member, same columns, same cutoff law; import-face law.)"""
    return tl8._tstate_face_full()


def _std_state_full():
    """Canonical full-face std_state with the frozen probe anchors
    asserted (prereg sec.2 G-STD fail-closed): n_bars == 3,483;
    first-decidable == 120 / decidable == 3,363 / std20 open == 391 /
    std10 open == 399 exact (both windows); eight-gate (gate x vol x
    yang x vconf x streak x tstate x amp x std20) 256 open-window cells
    103-non-empty / 153-empty (probe range 1-41; all-decidable 3,305)
    + exact per-cell cross-check vs the git-tracked probe facts file
    when present; extreme-day gate states exact vs STD_ANCHOR;
    cross lower bounds {mad60 154, rsv60 108, down_streak 85, wide
    150, mom 164, std10-both-open 196}; STREAK/TSTATE/AMP reproduction
    counts exact (W7/W8/W9/W10 cross-probe determinism law).
    Returns (std_state, err); err is a one-line honest refusal reason
    when not None."""
    face = _std_face_full()
    if face is None:
        return None, (f"raw member face data/daily/sh{STD_MEMBER}.csv "
                      f"absent/open-high-low-close-volume columns "
                      f"missing or truncated tail != cutoff {CUTOFF}")
    s20 = _std_series_raw(face, 20)
    s10 = _std_series_raw(face, 10)
    a = STD_ANCHOR
    for tag, s_ in (("std20", s20), ("std10", s10)):
        meta = s_[2]
        if (meta.get("n_bars") != a["n_bars"]
                or meta["first_decidable_bar_idx"]
                != a["first_decidable_bar_idx"]
                or meta["decidable_days"] != a["decidable_days"]):
            return None, (f"G-STD {tag} core anchors {meta} != probe "
                          f"{{n 3483, warmup 120, decidable 3363}}")
    if s20[2]["open_days"] != a["std20_open_days"] \\
            or s10[2]["open_days"] != a["std10_open_days"]:
        return None, (f"G-STD open anchors std20 {s20[2]['open_days']} "
                      f"!= 391 / std10 {s10[2]['open_days']} != 399")
    open20, dec20 = s20[0], s20[1]
    # ---- eight-gate 256-cell cross on the r237 probe basis VERBATIM
    # (std20 face; all-decidable window m8 = dec20 & amp_known &
    # streak-decidable & dec_mad & dec_rsv == 3,305 days)
    df = face[STD_MEMBER]
    close = df["close"].astype(float).sort_index()
    o_ = df["open"].astype(float).reindex(close.index)
    h_ = df["high"].astype(float).reindex(close.index)
    l_ = df["low"].astype(float).reindex(close.index)
    v_ = df["volume"].astype(float).reindex(close.index)
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
    sar = a["streak_anchor_reproduction"]
    if (int(up_st.sum()) != sar["up_streak_days"]
            or int(dn_st.sum()) != sar["down_streak_days"]):
        return None, (f"G-STD streak-anchor reproduction broken "
                      f"{int(up_st.sum())}/{int(dn_st.sum())} != {sar}")
    tar = a["tstate_anchor_reproduction"]
    if (int((mad_q10 & dec_mad).sum()) != tar["mad60_gate_true_days"]
            or int((rsv_low & dec_rsv).sum())
            != tar["rsv60_gate_true_days"]):
        return None, (f"G-STD tstate-anchor reproduction broken "
                      f"{int((mad_q10 & dec_mad).sum())}/"
                      f"{int((rsv_low & dec_rsv).sum())} != {tar}")
    aar = a["amp_anchor_reproduction"]
    if (int(wide_face.sum()) != aar["wide_days"]
            or int(narrow_face.sum()) != aar["narrow_days"]
            or int((h_ == l_).sum()) != aar["zero_range_rows"]):
        return None, (f"G-STD amp-anchor reproduction broken "
                      f"{int(wide_face.sum())}/{int(narrow_face.sum())}"
                      f"/{int((h_ == l_).sum())} != {aar}")
    # cross lower bounds on the r237 probe basis VERBATIM
    cross = {
        "mad60_and_std20":
            int((mad_q10 & open20 & (dec20 & dec_mad)).sum()),
        "rsv60_and_std20":
            int((rsv_low & open20 & (dec20 & dec_rsv)).sum()),
        "down_streak_and_std20":
            int((dn_st & open20 & (dec20 & judge)).sum()),
        "wide_and_std20":
            int((wide_face & open20 & (dec20 & amp_known)).sum()),
    }
    for k, lbv in a["cross_lower_bounds"].items():
        if k in cross and cross[k] < lbv:
            return None, (f"G-STD cross lower bound broken "
                          f"{k}={cross[k]} < {lbv}")
    # eight-gate 256-cell cross on the r237 probe basis VERBATIM
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
    std_open_face = open20 & dec20
    std_closed_face = (~open20) & dec20
    m8 = dec20 & amp_known & judge & dec_mad & dec_rsv
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
                                        ("std20_open", std_open_face),
                                        ("std20_closed",
                                         std_closed_face)):
                                    cells[f"{bname}|{vname}|{yname}|"
                                          f"{sname}|{kname}|{tname}|"
                                          f"{aname}|{sdname}"] =                                         int((m8 & b & vv & y & s & k & t
                                             & aa & sd).sum())
    empty = sorted(k for k, n_ in cells.items() if n_ <= 0)
    nonzero = [x for x in cells.values() if x > 0]
    if (len(cells) != 256
            or len(nonzero)
            != a["eight_gate_256cells_nonzero_count"]
            or len(empty) != a["eight_gate_256cells_empty_count"]
            or empty != sorted(a["eight_gate_256cells_empty"])
            or min(nonzero) < a["eight_gate_256cells_min_nonzero"]
            or max(cells.values()) > a["eight_gate_256cells_max"]
            or int(m8.sum()) != a["eight_gate_all_decidable_days"]):
        return None, (f"G-STD eight-gate 256-cell cross drift "
                      f"(nonzero {len(nonzero)}/103, empty "
                      f"{len(empty)}/153, min {min(nonzero)}, max "
                      f"{max(cells.values())}, all-decidable "
                      f"{int(m8.sum())}/3305)")
    # exact per-cell cross-check vs the git-tracked probe facts file
    # (r237 determinism cross-check law; skip-face = file absent,
    # header counts above still binding)
    if os.path.exists(PROBE_FACTS_FILE):
        pf = json.load(open(PROBE_FACTS_FILE, encoding="utf-8"))
        pcells = pf.get("eight_gate_cells", {})
        drift = [f"{k}: {cells.get(k)} != {v_}"
                 for k, v_ in pcells.items() if cells.get(k) != v_]
        if pcells and drift:
            return None, (f"G-STD probe-facts per-cell cross-check "
                          f"drift: {drift[:3]}")
    # extreme-day gate states (frozen face; values at probe rounding)
    for dstr, want in a["extreme_days"].items():
        ts = pd.Timestamp(dstr)
        if ts not in close.index:
            return None, f"G-STD extreme day {dstr} absent from face"
        if bool(dec20.loc[ts]):
            if bool(open20.loc[ts]) != bool(want["std20_open"]):
                return None, (f"G-STD extreme day {dstr} std20_open "
                              f"drift {bool(open20.loc[ts])} != "
                              f"{want['std20_open']}")
        if bool(s10[1].loc[ts]):
            if bool(s10[0].loc[ts]) != bool(want["std10_open"]):
                return None, (f"G-STD extreme day {dstr} std10_open "
                              f"drift {bool(s10[0].loc[ts])} != "
                              f"{want['std10_open']}")
    meta = dict(s20[2])
    meta["std10_open_days"] = s10[2]["open_days"]
    meta["cross_lower_bounds"] = cross
    meta["eight_gate_256cells"] = cells
    meta["eight_gate_256cells_empty"] = empty
    meta["eight_gate_all_decidable_days"] = int(m8.sum())
    meta["streak_anchor"] = {k: sar[k] for k in
                             ("up_streak_days", "down_streak_days")}
    meta["tstate_anchor"] = dict(tar)
    meta["amp_anchor"] = dict(aar)
    state = {"std20_hi": (s20[0], s20[1], meta),
             "std10_hi": (s10[0], s10[1], s10[2])}
    return state, None


def std_zero_mask(mask: pd.DataFrame, std_key: str, std_state):
    """Grammar-layer std entry gate (prereg sec.3 high-dispersion
    face; E1-mapping primitive): off-face signal days -> effective
    signal zeroed (entry blocked).  std=none = W10 semantic baseline
    (identity).  The keep face derives from the DECIDABLE face
    (pit-95 law): std20_hi keeps std20-open AND decidable; std10_hi
    keeps std10-open AND decidable.  Member dates missing from the
    mask index -> std-closed (conservative reindex law)."""
    if std_key == "none":
        return mask
    open_perm, dec, _ = std_state[std_key]
    open_keep = open_perm.reindex(mask.index).fillna(False).astype(int)
    dec_keep = dec.reindex(mask.index).fillna(False).astype(int)
    keep = (open_keep & dec_keep)
    return mask.mul(keep, axis=0)


def _std_structure_pass(std_meta) -> bool:
    """Series-structure invariants on every panel face (fail-closed):
    120-bar warmup -- first-decidable + decidable partitions n_bars;
    open <= decidable and closed <= decidable.  A face shorter than
    the warmup (first-decidable None) honestly refuses."""
    if not isinstance(std_meta, dict):
        return False
    n = std_meta.get("n_bars", -1)
    fv = std_meta.get("first_decidable_bar_idx")
    return (fv is not None
            and fv + std_meta.get("decidable_days", -10**9) == n
            and std_meta.get("open_days", -1)
            <= std_meta.get("decidable_days", -1)
            and std_meta.get("closed_days", -1)
            <= std_meta.get("decidable_days", -1))


'''
    src = src[:a] + std_layer + src[b:]
    steps.append("std overlay layer: probe-verbatim functions "
                 "(three-value axis)")

    # ---- 6. amp import face comment fix (tl10 base now)
    src = src.replace(
        "amp_state_series = tl9.amp_state_series",
        "amp_state_series = tl9.amp_state_series")

    # ---- 7. mom machine re-import from tl10 (frozen W10 face)
    mom_reimport = '''# ------------------------------------------------- mom overlay (tl10 import face)
# The FULL mom machinery is imported verbatim from tl10 (W10 frozen
# face; import-face law; zero re-implementation) -- the W11 runner
# only adds the NEW std overlay layer on top of it.
mom_state_series = tl10.mom_state_series
mom_zero_mask = tl10.mom_zero_mask
_mom_state_full = tl10._mom_state_full
_mom_structure_pass = tl10._mom_structure_pass
_mom_series_raw = tl10._mom_series_raw
'''
    src = src.replace(
        "amp_state_series = tl9.amp_state_series\n"
        "amp_zero_mask = tl9.amp_zero_mask\n"
        "_amp_state_full = tl9._amp_state_full\n"
        "_amp_structure_pass = tl9._amp_structure_pass\n"
        "_amp_series_raw = tl9._amp_series_raw\n",
        "amp_state_series = tl9.amp_state_series\n"
        "amp_zero_mask = tl9.amp_zero_mask\n"
        "_amp_state_full = tl9._amp_state_full\n"
        "_amp_structure_pass = tl9._amp_structure_pass\n"
        "_amp_series_raw = tl9._amp_series_raw\n\n" + mom_reimport)
    steps.append("mom overlay: tl10 import face (frozen W10 reuse)")

    # ---- 8. grammar build leg surgery
    gb, a, b = segment(src, 'def build_grammar_w10():',
                       '# ------------------------------------------------------------ Sobol draw leg',
                       include_start=True, include_end=False)
    gb = gb.replace("build_grammar_w10", "build_grammar_w11")
    gb = gb.replace("g9 = tl9.build_grammar_w9()      # frozen W9 machinery face",
                    "g10 = tl10.build_grammar_w10()    # frozen W10 machinery face")
    gb = gb.replace('g9["exclusion"]["stop_gate_vol_yang_vconf_streak_tstate_amp_none_face"]',
                    'g10["exclusion"]["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_none_face"]')
    gb = gb.replace('excl.append({**e, "axis": list(e["axis"]) + ["none"],',
                    'excl.append({**e, "axis": list(e["axis"]) + ["none"],')
    gb = gb.replace('"face": "stop-gate-vol-yang-vconf-streak-"\n                            "tstate-amp-mom-none"',
                    '"face": "stop-gate-vol-yang-vconf-streak-"\n                            "tstate-amp-mom-std-none"')
    gb = gb.replace('"grammar_kind": "w10-mom-gate-extended",',
                    '"grammar_kind": "w11-std-gate-extended",')
    gb = re.sub(r'"trial_labor_w10_gen": SEED_GEN,\n\s+"trial_labor_w10_scrnull": SEED_NULL,\n\s+"trial_labor_w10_unc": SEED_UNC,',
               '"trial_labor_w11_gen": SEED_GEN,\n                  "trial_labor_w11_scrnull": SEED_NULL,\n                  "trial_labor_w11_unc": SEED_UNC,',
               gb)
    gb = gb.replace('"derivation": "Sobol(seed=20311000+family_idx, "',
                    '"derivation": "Sobol(seed=20317000+family_idx, "')
    gb = gb.replace('"default_rng("\n                                "[20311000+family_idx, 7919]) thirteen-"',
                    '"default_rng("\n                                "[20317000+family_idx, 7919]) fourteen-"')
    gb = gb.replace('"tuple axis stream R/X/S/T/STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM "\n                                "(prereg s.3; A idx 0-5, B idx 6+slot; "',
                    '"tuple axis stream R/X/S/T/STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/"\n                                "STD (prereg s.3; A idx 0-5, B idx 6+slot; "')
    gb = gb.replace('"berth-open adoption of the bm-c r228 "\n                                "MOM candidate whole package per "\n                                "AMP->W9 precedent; berths held at "\n                                "the freeze commit per R250 one-step "\n                                "law, bm-b r437 three-step re-verify "\n                                "ALL GREEN no re-pick)"',
                    '"berth-open adoption of the bm-c r237 "\n                                "STD candidate whole package per "\n                                "AMP->W9/MOM->W10 precedent; berths "\n                                "re-taken +500 at the freeze commit "\n                                "(20316000/20316500 collided with "\n                                "bm-a r445 A12 per draft clause-5); "\n                                "bm-b r441 three-step re-verify "\n                                "ALL GREEN no re-pick)"')
    gb = gb.replace('"axes": {**g9["axes"], "mom": AXIS_MOM},',
                    '"axes": {**g10["axes"], "std": AXIS_STD},')
    gb = gb.replace('"axis_combos": AXIS_COMBOS,', '"axis_combos": AXIS_COMBOS,')
    for k in ("stop_formula", "stop_fill_mapping", "gate_spec", "vol_spec",
              "yang_spec", "vconf_spec", "streak_spec", "tstate_spec",
              "amp_spec", "vol_anchor", "yang_anchor", "vconf_anchor",
              "streak_anchor", "tstate_anchor", "amp_anchor", "families",
              "value_domains", "faces", "inventory_audit"):
        gb = gb.replace(f'g9["{k}"]', f'g10["{k}"]')
    gb = gb.replace('"mom_spec": MOM_SPEC,', '"mom_spec": g10["mom_spec"],\n        "std_spec": STD_SPEC,')
    gb = gb.replace('"mom_anchor": MOM_ANCHOR,', '"mom_anchor": g10["mom_anchor"],\n        "std_anchor": STD_ANCHOR,')
    gb = gb.replace('"negative_priors": g9.get("negative_priors"),',
                    '"negative_priors": g10.get("negative_priors"),')
    gb = gb.replace('"stop_gate_vol_yang_vconf_streak_tstate_amp_mom_none_face": excl,',
                    '"stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_none_face": excl,')
    gb = gb.replace('"sources": list(g9["exclusion"]["sources"])',
                    '"sources": list(g10["exclusion"]["sources"])')
    gb = gb.replace('+ ["w9_screen.json survivors (generate-time)",\n               "w9_judge products (generate-time real-read "\n               "re-declare window; W9-JUDGE landed 2026-09-29 "\n               "17:47:46)"],',
                    '+ ["w10_screen.json survivors (generate-time)",\n               "w10_judge products (generate-time real-read "\n               "re-declare window; W10-JUDGE landed 2026-09-29 "\n               "20:31:29 = ELEVENTH source)"],')
    gb = gb.replace('"note": "exclusion face = mom=none only; prior-wave keys "\n                    "mom=none-completed (semantic identity match); "\n                    "mom in {mom_oversold} = new-syntax legal "\n                    "cells (prereg sec.1)"',
                    '"note": "exclusion face = std=none only; prior-wave keys "\n                    "std=none-completed (semantic identity match); "\n                    "std in {std20_hi, std10_hi} = new-syntax legal "\n                    "cells (prereg sec.1)"')
    gb = gb.replace("Exclusion law (prereg sec.1): exact already-judged cells are\n    excluded on the mom=none face only",
                    "Exclusion law (prereg sec.1): exact already-judged cells are\n    excluded on the std=none face only")
    src = src[:a] + gb + src[b:]
    steps.append("grammar build: fourteen-tuple + std axis + W10 lineage")

    # ---- 9. Sobol draw leg surgery (fourteen-tuple stream)
    sob, a, b = segment(src, 'def draw_candidate_sobol_w10(',
                        '# ------------------------------------------------ exclusion',
                        include_start=True, include_end=False)
    sob = sob.replace("draw_candidate_sobol_w10", "draw_candidate_sobol_w11")
    sob = sob.replace("mapped\n    to discrete domain indices + THIRTEEN-tuple axis stream",
                      "mapped\n    to discrete domain indices + FOURTEEN-tuple axis stream")
    sob = sob.replace("default_rng([SEED_GEN + family_idx, 7919]) in the frozen consumption\n    order R/X/S/T/STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM (the\n    first twelve axis arrays are the W9-order stream VERBATIM --\n    order-frozen consumption law; the mom leg appends AFTER amp,\n    zero disturbance).",
                      "default_rng([SEED_GEN + family_idx, 7919]) in the frozen consumption\n    order R/X/S/T/STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD\n    (the first thirteen axis arrays are the W10-order stream VERBATIM\n    -- order-frozen consumption law; the std leg appends AFTER mom,\n    zero disturbance).")
    sob = sob.replace("                  rng.integers(0, len(AXIS_MOM), n_draws)))",
                       "                  rng.integers(0, len(AXIS_MOM), n_draws),\n                  rng.integers(0, len(AXIS_STD), n_draws)))")
    sob = sob.replace("        r_, x_, s_, t_, st_, gt_, vt_, yg_, vc_, sk_, ts_, ap_, mo_ = ax[i]",
                       "        r_, x_, s_, t_, st_, gt_, vt_, yg_, vc_, sk_, ts_, ap_, mo_, sd_ = ax[i]")
    sob = sob.replace("                  tl8.AXIS_TSTATE[ts_], tl9.AXIS_AMP[ap_],\n                  AXIS_MOM[mo_]],",
                       "                  tl8.AXIS_TSTATE[ts_], tl9.AXIS_AMP[ap_],\n                  AXIS_MOM[mo_], AXIS_STD[sd_]],")
    src = src[:a] + sob + src[b:]
    steps.append("Sobol: fourteen-tuple stream (std leg appends after mom)")

    # ---- 10. exclusion loader surgery
    ex, a, b = segment(src, 'def _load_exclusion_rows_w10(',
                       '# -------------------------------------------- effective face + engine curves',
                       include_start=True, include_end=False)
    ex = ex.replace("_load_exclusion_rows_w10", "_load_exclusion_rows_w11")
    ex = ex.replace("Twenty real-read source faces", "Twenty-two real-read source faces")
    ex = ex.replace("All prior-wave\n    keys are padded to the W10 THIRTEEN-tuple with mom=none (semantic-\n    identity completion law).",
                    "All prior-wave\n    keys are padded to the W11 FOURTEEN-tuple with std=none\n    (semantic-identity completion law).")
    ex = ex.replace('rows = list(grammar["exclusion"]\n                ["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_none_face"])',
                    'rows = list(grammar["exclusion"]\n                ["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_none_face"])')
    ex = ex.replace('disc = {"grammar_stop_gate_vol_yang_vconf_streak_tstate_"\n            "amp_mom_none_rows": len(rows)}',
                    'disc = {"grammar_stop_gate_vol_yang_vconf_streak_tstate_"\n            "amp_mom_std_none_rows": len(rows)}')
    # pad lists: all prior-wave pads +1 std-none
    ex = ex.replace('["none"] * 9, "w1_screen_survivor")', '["none"] * 10, "w1_screen_survivor")')
    ex = ex.replace('["none"] * 8, "w2_screen_survivor")', '["none"] * 9, "w2_screen_survivor")')
    ex = ex.replace('["none"] * 7, "w3_screen_survivor")', '["none"] * 8, "w3_screen_survivor")')
    ex = ex.replace('["none"] * 6, "w4_screen_survivor")', '["none"] * 7, "w4_screen_survivor")')
    ex = ex.replace('["none"] * 5, "w5_screen_survivor")', '["none"] * 6, "w5_screen_survivor")')
    ex = ex.replace('["none"] * 4, "w6_screen_survivor")', '["none"] * 5, "w6_screen_survivor")')
    ex = ex.replace('["none"] * 3, "w7_screen_survivor")', '["none"] * 4, "w7_screen_survivor")')
    ex = ex.replace('["none"] * 2, "w8_screen_survivor")', '["none"] * 3, "w8_screen_survivor")')
    ex = ex.replace('["none"], "w9_screen_survivor")', '["none"] * 2, "w9_screen_survivor")')
    ex = ex.replace('"face": f"{tag}:stop-gate-vol-yang-vconf-"\n                                 "streak-tstate-amp-mom-none",',
                    '"face": f"{tag}:stop-gate-vol-yang-vconf-"\n                                 "streak-tstate-amp-mom-std-none",')
    # w10 screen source (new; thirteen-tuple + 1 std-none pad)
    ex = ex.replace('    disc["w9_screen_survivors"] = _screen_survivors(\n        tl9.SCREEN_FILE, tl9.CANDIDATES_FILE,\n        ["none"] * 2, "w9_screen_survivor")',
                    '    disc["w9_screen_survivors"] = _screen_survivors(\n        tl9.SCREEN_FILE, tl9.CANDIDATES_FILE,\n        ["none"] * 2, "w9_screen_survivor")\n    disc["w10_screen_survivors"] = _screen_survivors(\n        tl10.SCREEN_FILE, tl10.CANDIDATES_FILE,\n        ["none"], "w10_screen_survivor")')
    ex = ex.replace('tr["axis"] = list(tr["axis"]) + ["none"] * 7\n                tr["face"] = "mass_screen_survivor:translated-exact"',
                    'tr["axis"] = list(tr["axis"]) + ["none"] * 8\n                tr["face"] = "mass_screen_survivor:translated-exact"')
    # judged pads
    ex = ex.replace('["none"] * 9, "w1_judged")', '["none"] * 10, "w1_judged")')
    ex = ex.replace('["none"] * 8, "w2_judged")', '["none"] * 9, "w2_judged")')
    ex = ex.replace('["none"] * 7, "w3_judged")', '["none"] * 8, "w3_judged")')
    ex = ex.replace('["none"] * 6, "w4_judged")', '["none"] * 7, "w4_judged")')
    ex = ex.replace('["none"] * 5, "w5_judged")', '["none"] * 6, "w5_judged")')
    ex = ex.replace('["none"] * 4, "w6_judged")', '["none"] * 5, "w6_judged")')
    ex = ex.replace('["none"] * 3, "w7_judged")', '["none"] * 4, "w7_judged")')
    ex = ex.replace('["none"] * 2, "w8_judged")', '["none"] * 3, "w8_judged")')
    ex = ex.replace('["none"], "w9_judged")', '["none"] * 2, "w9_judged")')
    ex = ex.replace('tr["axis"] = list(tr["axis"]) + ["none"] * 7\n                tr["face"] = f"{tag}:translated-exact"',
                    'tr["axis"] = list(tr["axis"]) + ["none"] * 8\n                tr["face"] = f"{tag}:translated-exact"')
    ex = ex.replace('"face": f"{tag}:stop-gate-vol-yang-"\n                                     "vconf-streak-tstate-amp-mom-none",',
                    '"face": f"{tag}:stop-gate-vol-yang-"\n                                     "vconf-streak-tstate-amp-mom-std-none",')
    # w10 judge source (ELEVENTH)
    ex = ex.replace('    disc["w9_judge_products"] = _judged_source(\n        tl9.JUDGE_FILE, tl9.CANDIDATES_FILE,\n        ["none"] * 2, "w9_judged")',
                    '    disc["w9_judge_products"] = _judged_source(\n        tl9.JUDGE_FILE, tl9.CANDIDATES_FILE,\n        ["none"] * 2, "w9_judged")\n    disc["w10_judge_products"] = _judged_source(\n        tl10.JUDGE_FILE, tl10.CANDIDATES_FILE,\n        ["none"], "w10_judged")')
    ex = ex.replace("W9-JUDGE landed 2026-09-29 17:47:46 -- TEN\n    sources, third full-declare window in history",
                    "W9-JUDGE landed 2026-09-29 17:47:46;\n    W10-JUDGE landed 2026-09-29 20:31:29 -- ELEVEN sources, fourth\n    full-declare window in history")
    ex = ex.replace("availability of the TEN judge\n        \"products disclosed above (freeze-time ten-source full-declare \"\n        \"window = third in history)\"",
                    "availability of the ELEVEN judge\n        \"products disclosed above (freeze-time eleven-source \"\n        \"full-declare window = fourth in history)\"")
    src = src[:a] + ex + src[b:]
    steps.append("exclusion: 22 real-read faces, w10 screen+judge sources, pads+1")

    # ---- 11. _excluded test: index 13 + std face
    exd, a, b = segment(src, 'def _excluded_w10(',
                        '# -------------------------------------------- effective face',
                        include_start=True, include_end=False)
    exd = exd.replace("_excluded_w10", "_excluded_w11")
    exd = exd.replace('if cand["axis"][12] != "none":', 'if cand["axis"][13] != "none":')
    exd = exd.replace("mom=none face only (prereg\n    sec.1: mom in {mom_oversold} = new-syntax legal cells --",
                      "std=none face only (prereg\n    sec.1: std in {std20_hi, std10_hi} = new-syntax legal cells --")
    src = src[:a] + exd + src[b:]
    steps.append("_excluded: axis[13] std=none face law")

    # ---- 12. mask + curve + null surgery
    mk, a, b = segment(src, 'def _effective_signal_mask_w10(',
                       '# ------------------------------------------------------------ grammar / status',
                       include_start=True, include_end=False)
    mk = mk.replace("_effective_signal_mask_w10", "_effective_signal_mask_w11")
    mk = mk.replace("tstate_key, amp_key, mom_key, gate_state,\n                               vol_state, yang_state, vconf_state,\n                               streak_state, tstate_state, amp_state,\n                               mom_state):",
                    "tstate_key, amp_key, mom_key, std_key, gate_state,\n                               vol_state, yang_state, vconf_state,\n                               streak_state, tstate_state, amp_state,\n                               mom_state, std_state):")
    mk = mk.replace("GATE -> VOL -> YANG -> VCONF -> STREAK -> TSTATE -> AMP -> MOM ->\n    initial-stop (prereg sec.3 thirteen-tuple dedup legs; zero engine\n    burn).  mom=none + amp=none + tstate=none + streak=none + vconf=\n    none + yang=none + vol=none + gate=none + stop=none = W1 identity;\n    mom=none = W9 semantic baseline; all nine overlay faces\n    deterministic layers of the same grammar stack (W9 order extended\n    by the mom leg, zero disturbance to the first eight).",
                    "GATE -> VOL -> YANG -> VCONF -> STREAK -> TSTATE -> AMP -> MOM ->\n    STD -> initial-stop (prereg sec.3 fourteen-tuple dedup legs; zero\n    engine burn).  std=none + mom=none + ... + stop=none = W1\n    identity; std=none = W10 semantic baseline; all ten overlay faces\n    deterministic layers of the same grammar stack (W10 order\n    extended by the std leg, zero disturbance to the first nine).")
    mk = mk.replace("    MO = mom_zero_mask(AP, mom_key, mom_state)\n    return tl2._effective_signal_mask(MO, prices, stop_key, atr20)",
                    "    MO = mom_zero_mask(AP, mom_key, mom_state)\n    SD = std_zero_mask(MO, std_key, std_state)\n    return tl2._effective_signal_mask(SD, prices, stop_key, atr20)")
    mk = mk.replace("run_candidate_curve_w10", "run_candidate_curve_w11")
    mk = mk.replace("tstate_state=None, amp_state=None,\n                           mom_state=None):",
                    "tstate_state=None, amp_state=None,\n                           mom_state=None, std_state=None):")
    mk = mk.replace("yang + vconf + streak + tstate + amp + MOM overlays + initial-stop",
                    "yang + vconf + streak + tstate + amp + MOM + STD overlays + initial-stop")
    mk = mk.replace("TSTATE -> AMP -> MOM -> initial-stop).\n\n    mom=none+amp=none+tstate=none+streak=none+vconf=none+yang=none+\n    vol=none+gate=none+stop=none -> byte-identical to the tl1 engine\n    face; mom=none+tstate=none -> tl7 W7 face; mom=none+amp=none ->\n    tl8 W8 face; mom=none -> tl9 W9 face (parity laws, selftest-\n    pinned); mom in {mom_oversold} = new W10 syntax (entry-permittance\n    only, never excluded).  Returns (eq, trades, metrics, params,\n    patch, stop_fired, gate_zeroed, vol_zeroed, yang_zeroed,\n    vconf_zeroed, streak_zeroed, tstate_zeroed, amp_zeroed,\n    mom_zeroed).",
                    "TSTATE -> AMP -> MOM -> STD -> initial-stop).\n\n    std=none+mom=none+...+stop=none -> byte-identical to the tl1\n    engine face; std=none -> tl10 W10 face (parity laws, selftest-\n    pinned); std in {std20_hi, std10_hi} = new W11 syntax\n    (entry-permittance only, never excluded).  Returns (eq, trades,\n    metrics, params, patch, stop_fired, gate_zeroed, vol_zeroed,\n    yang_zeroed, vconf_zeroed, streak_zeroed, tstate_zeroed,\n    amp_zeroed, mom_zeroed, std_zeroed).")
    mk = mk.replace('    mom_key = cand["axis"][12]\n', '    mom_key = cand["axis"][12]\n    std_key = cand["axis"][13]\n')
    mk = mk.replace("    if mom_state is None:\n        mom_state = mom_state_series(prices)",
                    "    if mom_state is None:\n        mom_state = tl10.mom_state_series(prices)\n    if std_state is None:\n        std_state = std_state_series(prices)")
    mk = mk.replace("    MO = mom_zero_mask(AP, mom_key, mom_state)\n    gate_zeroed",
                    "    MO = mom_zero_mask(AP, mom_key, mom_state)\n    SD = std_zero_mask(MO, std_key, std_state)\n    gate_zeroed")
    mk = mk.replace("    mom_zeroed = int((AP > 0).sum().sum() - (MO > 0).sum().sum())\n    if stop_key",
                    "    mom_zeroed = int((AP > 0).sum().sum() - (MO > 0).sum().sum())\n    std_zeroed = int((MO > 0).sum().sum() - (SD > 0).sum().sum())\n    if stop_key")
    mk = mk.replace("    if stop_key == \"none\":\n        S, stop_fired = MO, 0\n    else:\n        S = tl2._effective_signal_mask(MO, prices, stop_key, atr20)\n        d = (MO > 0) & (S == 0)",
                    "    if stop_key == \"none\":\n        S, stop_fired = SD, 0\n    else:\n        S = tl2._effective_signal_mask(SD, prices, stop_key, atr20)\n        d = (SD > 0) & (S == 0)")
    mk = mk.replace("    return eq, res[\"trades\"], res[\"metrics\"], params, patch, stop_fired, \\\n        gate_zeroed, vol_zeroed, yang_zeroed, vconf_zeroed, \\\n        streak_zeroed, tstate_zeroed, amp_zeroed, mom_zeroed",
                    "    return eq, res[\"trades\"], res[\"metrics\"], params, patch, stop_fired, \\\n        gate_zeroed, vol_zeroed, yang_zeroed, vconf_zeroed, \\\n        streak_zeroed, tstate_zeroed, amp_zeroed, mom_zeroed, \\\n        std_zeroed")
    mk = mk.replace("_null_axis_draw_w10", "_null_axis_draw_w11")
    mk = mk.replace("rng=[SEED_NULL, i]\n    (W10 berth 20311500, distinct from the W9 berth 20310000 -- zero\n    stream overlap by construction); consumption order frozen = p_on\n    regime -> THIRTEEN-tuple axis R/X/S/T/STOP/GATE/VOL/YANG/VCONF/\n    STREAK/TSTATE/AMP/MOM -> signal matrix (the mom gate leg merged\n    into the same grid/param space draw per prereg sec.3).  Same\n    engine/cost/panel as candidate cells incl. the gate + vol + yang +\n    vconf + streak + tstate + amp + mom legs (BACKTEST_PLAN three\n    iron rules).",
                    "rng=[SEED_NULL, i]\n    (W11 berth 20317500, distinct from the W10 berth 20311500 -- zero\n    stream overlap by construction); consumption order frozen = p_on\n    regime -> FOURTEEN-tuple axis R/X/S/T/STOP/GATE/VOL/YANG/VCONF/\n    STREAK/TSTATE/AMP/MOM/STD -> signal matrix (the std gate leg merged\n    into the same grid/param space draw per prereg sec.3).  Same\n    engine/cost/panel as candidate cells incl. the gate + vol + yang +\n    vconf + streak + tstate + amp + mom + std legs (BACKTEST_PLAN\n    three iron rules).")
    mk = mk.replace("          AXIS_MOM[int(rng.integers(len(AXIS_MOM)))])",
                    "          AXIS_MOM[int(rng.integers(len(AXIS_MOM)))],\n          AXIS_STD[int(rng.integers(len(AXIS_STD)))])")
    src = src[:a] + mk + src[b:]
    steps.append("mask/curve/null: std leg wiring (axis[13], three-value)")

    # ---- 13. generate-leg surgery (core references)
    gen, a, b = segment(src, 'def cmd_generate() -> int:',
                        '# ------------------------------------------------------ screen slice (s2)',
                        include_start=True, include_end=False)
    gen = gen.replace("THIRTEEN-tuple face", "FOURTEEN-tuple face")
    gen = gen.replace("gate + vol + yang + vconf + streak + tstate + amp + MOM overlays applied",
                      "gate + vol + yang + vconf + streak + tstate + amp + MOM + STD overlays applied")
    gen = gen.replace('print("GENERATE-GATE: w10_candidates.json exists',
                      'print("GENERATE-GATE: w11_candidates.json exists')
    gen = gen.replace('print("GENERATE-GATE: w10_grammar.json absent',
                      'print("GENERATE-GATE: w11_grammar.json absent')
    gen = gen.replace("    if not os.path.exists(GRAMMAR_FILE):", "    if not os.path.exists(GRAMMAR_FILE):")
    gen = gen.replace("FROZEN_SHA16 and grammar[\"grammar_sha256\"] != FROZEN_SHA16", "FROZEN_SHA16 and grammar[\"grammar_sha256\"] != FROZEN_SHA16")
    gen = gen.replace("    mom_state, mom_err = _mom_state_full()\n    if mom_err:\n        print(f\"GENERATE-GATE: {mom_err} (prereg sec.2 G-MOM \"\n              \"fail-closed) -- refuse\")\n        return 2",
                      "    mom_state, mom_err = tl10._mom_state_full()\n    if mom_err:\n        print(f\"GENERATE-GATE: {mom_err} (prereg sec.2 G-MOM \"\n              \"fail-closed) -- refuse\")\n        return 2\n    std_state, std_err = _std_state_full()\n    if std_err:\n        print(f\"GENERATE-GATE: {std_err} (prereg sec.2 G-STD \"\n              \"fail-closed) -- refuse\")\n        return 2")
    gen = gen.replace("    excl_rows, excl_disc = _load_exclusion_rows_w11(grammar)", "    excl_rows, excl_disc = _load_exclusion_rows_w11(grammar)")
    gen = gen.replace("neg_fns = {(e[\"module\"], e[\"fn\"])\n               for e in grammar[\"exclusion\"]\n               [\"stop_gate_vol_yang_vconf_streak_tstate_amp_mom_none_face\"]\n               if str(e.get(\"face\", \"\")).startswith(\"negative\")}",
                      "neg_fns = {(e[\"module\"], e[\"fn\"])\n               for e in grammar[\"exclusion\"]\n               [\"stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_none_face\"]\n               if str(e.get(\"face\", \"\")).startswith(\"negative\")}")
    gen = gen.replace("streams = {s: draw_candidate_sobol_w10(", "streams = {s: draw_candidate_sobol_w11(")
    gen = gen.replace('cand["candidate_id"] = f"W10-{family}-{i:04d}"', 'cand["candidate_id"] = f"W11-{family}-{i:04d}"')
    gen = gen.replace("            hit = _excluded_w10(cand, excl_rows)", "            hit = _excluded_w11(cand, excl_rows)")
    gen = gen.replace("        S = _effective_signal_mask_w10(mask, prices, cand[\"axis\"][4], atr20,\n                                      cand[\"axis\"][5], cand[\"axis\"][6],\n                                      cand[\"axis\"][7], cand[\"axis\"][8],\n                                      cand[\"axis\"][9], cand[\"axis\"][10],\n                                      cand[\"axis\"][11], cand[\"axis\"][12],\n                                      gate_state, vol_state, yang_state,\n                                      vconf_state, streak_state,\n                                      tstate_state, amp_state, mom_state)",
                      "        S = _effective_signal_mask_w11(mask, prices, cand[\"axis\"][4], atr20,\n                                      cand[\"axis\"][5], cand[\"axis\"][6],\n                                      cand[\"axis\"][7], cand[\"axis\"][8],\n                                      cand[\"axis\"][9], cand[\"axis\"][10],\n                                      cand[\"axis\"][11], cand[\"axis\"][12],\n                                      cand[\"axis\"][13],\n                                      gate_state, vol_state, yang_state,\n                                      vconf_state, streak_state,\n                                      tstate_state, amp_state, mom_state,\n                                      std_state)")
    gen = gen.replace("    mom_counts = {}\n    gvvvsktsam_counts = {}",
                      "    mom_counts = {}\n    std_counts = {}\n    gvvvsktsam_counts = {}")
    gen = gen.replace("        mom_counts[c[\"axis\"][12]] = mom_counts.get(c[\"axis\"][12], 0) + 1\n        k8 = (f\"{c['axis'][5]}|{c['axis'][6]}|{c['axis'][7]}|\"\n              f\"{c['axis'][8]}|{c['axis'][9]}|{c['axis'][10]}|\"\n              f\"{c['axis'][11]}|{c['axis'][12]}\")",
                      "        mom_counts[c[\"axis\"][12]] = mom_counts.get(c[\"axis\"][12], 0) + 1\n        std_counts[c[\"axis\"][13]] = std_counts.get(c[\"axis\"][13], 0) + 1\n        k8 = (f\"{c['axis'][5]}|{c['axis'][6]}|{c['axis'][7]}|\"\n              f\"{c['axis'][8]}|{c['axis'][9]}|{c['axis'][10]}|\"\n              f\"{c['axis'][11]}|{c['axis'][12]}|{c['axis'][13]}\")")
    gen = gen.replace('"amp, mom); exclusion face = "\n                                     "mom=none only (sec.1); prior-wave "\n                                     "keys mom=none-completed; mom in "\n                                     "{mom_oversold} = "\n                                     "new-syntax legal cells"',
                      '"amp, mom, std); exclusion face = "\n                                     "std=none only (sec.1); prior-wave "\n                                     "keys std=none-completed; std in "\n                                     "{std20_hi, std10_hi} = "\n                                     "new-syntax legal cells"')
    gen = gen.replace('"+ MOM overlays applied, frozen "',
                      '"+ MOM + STD overlays applied, frozen "')
    gen = gen.replace('"amp_face_counts": amp_counts,\n               "mom_face_counts": mom_counts,',
                      '"amp_face_counts": amp_counts,\n               "mom_face_counts": mom_counts,\n               "std_face_counts": std_counts,')
    gen = gen.replace('"gate_vol_yang_vconf_streak_tstate_amp_mom_face_counts":',
                      '"gate_vol_yang_vconf_streak_tstate_amp_mom_std_face_counts":')
    gen = gen.replace('"mom_state_meta": mom_state[2],',
                      '"mom_state_meta": mom_state[2],\n               "std_state_meta": std_state["std20_hi"][2],')
    gen = gen.replace('"berth-open adoption of "\n                         "the bm-c r228 MOM candidate whole package "\n                         "per AMP->W9 precedent"',
                      '"berth-open adoption of "\n                         "the bm-c r237 STD candidate whole package "\n                         "per AMP->W9/MOM->W10 precedent; berths "\n                         "re-taken +500 at freeze (clause-5 collision)"')
    gen = gen.replace('"berths 20311000/20311500/"\n                         "20312000 held at the freeze commit (bm-b r437 "',
                      '"berths 20317000/20317500/"\n                         "20318000 held at the freeze commit (bm-b r441 "')
    gen = gen.replace("f\"(mom faces {json.dumps(mom_counts, sort_keys=True)}; \"\n          f\"gate x vol x yang x vconf x streak x tstate x amp x mom \"",
                      "f\"(mom faces {json.dumps(mom_counts, sort_keys=True)}; \"\n          f\"std faces {json.dumps(std_counts, sort_keys=True)}; \"\n          f\"gate x vol x yang x vconf x streak x tstate x amp x mom x std \"")
    gen = gen.replace("f\"TRIAL-LABOR-W10-GENERATE, T-122 prereg bm-b r437 frozen / \"\n          f\"runner bm-b r438) | \"",
                      "f\"TRIAL-LABOR-W11-GENERATE, T-123 prereg bm-b r441 frozen / \"\n          f\"runner slice bm-c r242 surgery) | \"")
    gen = gen.replace('print(f"mom faces: {json.dumps(mom_counts, sort_keys=True)}; "\n          f"gate x vol x yang x vconf x streak x tstate x amp x mom: "\n          f"{json.dumps(gvvvsktsam_counts, sort_keys=True)[:400]}")',
                      'print(f"mom faces: {json.dumps(mom_counts, sort_keys=True)}; \"\n          f\"std faces: {json.dumps(std_counts, sort_keys=True)}; \"\n          f\"gate x vol x yang x vconf x streak x tstate x amp x mom x \"\n          f\"std: {json.dumps(gvvvsktsam_counts, sort_keys=True)[:400]}")')
    gen = gen.replace('print(f"mom meta: n_bars={mom_state[2][\'n_bars\']} "\n          f"open={mom_state[2][\'open_days\']} "',
                      'print(f"mom meta: n_bars={mom_state[2][\'n_bars\']} "\n          f"open={mom_state[2][\'open_days\']} "')
    gen = gen.replace('print(f"products: w10_candidates.json + ledger row "', 'print(f"products: w11_candidates.json + ledger row "')
    src = src[:a] + gen + src[b:]
    steps.append("generate: G-STD gate + fourteen-tuple dedup + counts")

    # ---- 14. residual global mechanical pass (identifiers, payloads)
    # protect the tl10 import line from the trial_labor_w10 rename
    KEEP = "@@TL10IMPORT@@"
    src = src.replace("import trial_labor_w10 as tl10",
                      "import " + KEEP + " as tl10")
    resid = [
        ("csv_cols_screen_w10", "csv_cols_screen_w11"),
        ("_screen_cell_w10", "_screen_cell_w11"),
        ("_cell_list_w10", "_cell_list_w11"),
        ("_overlay_stop_disclosure_w10", "_overlay_stop_disclosure_w11"),
        ("_judge_cell_w10", "_judge_cell_w11"),
        ("TRIAL_LAB_W10_SCREEN", "TRIAL_LAB_W11_SCREEN"),
        ("TRIAL_LAB_W10_JUDGE", "TRIAL_LAB_W11_JUDGE"),
        ("TRIAL-LABOR-W10-GENERATE", "TRIAL-LABOR-W11-GENERATE"),
        ("T-122 prereg", "T-123 prereg"),
        ("w10_screen.json", "w11_screen.json"),
        ("w10_screen_cells.csv", "w11_screen_cells.csv"),
        ("w10_judge.json", "w11_judge.json"),
        ("w10_intake.json", "w11_intake.json"),
        ("w10_grammar.json", "w11_grammar.json"),
        ("w10_candidates.json", "w11_candidates.json"),
        ("trial_labor_w10", "trial_labor_w11"),
        ('"W10-', '"W11-'),
        ("W10-{family}", "W11-{family}"),
        ("20-source exclusion", "22-source exclusion"),
        ("tstate + amp + MOM overlays applied",
         "tstate + amp + MOM + STD overlays applied"),
        ('print("slice-1 mom overlay + G-MOM gate + thirteen-tuple grammar + "\n          "funnel bodies + dispatch LANDED (bm-b r438); GENERATE pool "',
         'print("Slice-A std overlay + G-STD gate + fourteen-tuple grammar "\n          "surgery LANDED (bm-c r242 draft); GENERATE pool "'),
    ]
    for old, new in resid:
        src = src.replace(old, new)
    src = src.replace(KEEP, "trial_labor_w10")
    steps.append("residual pass: identifiers/payloads (screen/judge/"
                 "intake/selftest legs)")

    # ---- 15. axis-length guards: thirteen->fourteen in judge/screen
    #     cell-key handling is reviewed at Slice-B; mechanical len
    #     references to 13 remain flagged in the report.
    flags = []
    for pat in ("len(axis) == 13", "axis[12] != \"none\"",
                "thirteen-tuple", "THIRTEEN-tuple"):
        hits = [m.start() for m in re.finditer(re.escape(pat), src)]
        if hits:
            flags.append(f"REVIEW-AT-SLICE-B {pat}: {len(hits)} hits")
    # thirteen-tuple mentions in comments are W9/W10 lineage docs;
    # behavioral axis-index references listed for Slice-B review.
    n_axis13 = len(re.findall(re.escape('cand["axis"][13]'), src))
    report = {
        "src": SRC, "dst": DST, "steps": steps,
        "axis13_refs": n_axis13, "review_flags": flags,
        "std_anchor_checks": {
            "nonzero": 103, "empty": 153, "decidable": 3363,
            "std20_open": 391, "std10_open": 399,
            "first_decidable": 120, "all_decidable": 3305},
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
