import sys
import argparse
import json
import io

sys.path.insert(0, "Tools")
import autofill

# r434 bm-b: canonical pool submit TRIAL-LABOR-W9-JUDGE (O-1820(3) consumer_plan
# law + r301/r305 contract trio + MSG-1305 host_gates wiring). Entry-time deps
# are re-verified live at run: serial-position face + judge-prep PASS artifact
# (results/trial_labor_w9/judge_state.json, produced by `judge-prep` this round)
# + RAM r354 three-sample + host gate cache presence (48 parquet non-empty,
# Money02/data/cache/t18_deep_panel/ohlcv). File-face driver per pit-law
# batch-80 (CJK command-channel write corruption).
#
# W9 facts (FROZEN prereg bm-b r432, grammar sha16 0601dda70b0209fa):
#   SEED berths same-commit R250: trial_labor_w9_gen=20309500 /
#   trial_labor_w9_scrnull=20310000 / trial_labor_w9_unc=20310500.
#   s3 dual-leg P-5C L/D x {6m,12m,24m} x cost {base x1, x2=CostPatch(2.0)} x
#   regime segmented bear/bull/chop+na + dual nulls B=2000 block bootstrap
#   block=20 + P=2000 sign-flip two-sided, seed [20310500, cell_idx];
#   seven-gate disclosure face gate x vol x yang x vconf x streak x tstate x amp
#   (W8 six-gate + amp expansion); lane_owner=bm-b SCREEN+JUDGE dual-face
#   (W8-corrected value, pit-103 dead-hand config).

# --- live reads (fail-closed) ---
try:
    scr = json.load(io.open(r"results/trial_labor_w9/w9_screen.json", encoding="utf-8"))
    n_distinct = scr["n_distinct"]
    n_nulls = scr["n_nulls"]
    null_p95 = scr["null_p95"]
    survivors = scr["survivors"]
    led = scr["trials_ledger"]
    ledger_total = led["total"]
    cutoff = scr["evidence_cutoff"]
except Exception as ex:
    print("REFUSED: w9_screen.json unreadable/missing fields:", ex)
    sys.exit(2)

try:
    jst = json.load(io.open(r"results/trial_labor_w9/judge_state.json", encoding="utf-8"))
    jprep = jst.get("verdict") or jst.get("status")
except Exception as ex:
    print("REFUSED: judge_state.json unreadable/missing (run judge-prep first):", ex)
    sys.exit(2)

n_cells = "{}+{} cells (distinct+nulls), null p95 {}, survivors {}".format(
    n_distinct, n_nulls, null_p95, survivors)

wp_note = (
    "worker_cap() RAM-guard governs at runtime (runner self-caps, --workers "
    "omitted from runner_args per W5/W6-JUDGE same-machinery precedent); plan "
    "size 20 = floor(16 cores/0.8) per prereg sec.9 lower-bound; judge initargs "
    "carry BOTH leg panels + per-leg ATR20 + per-leg gate/vol/yang/vconf/"
    "streak/tstate/amp state faces = heaviest per-worker state in the fleet; "
    "dual-leg x {6m,12m,24m} x cost {base x1, x2=CostPatch(2)} engine curves "
    "per judged cell WITH gate+vol+yang+vconf+streak+tstate+amp overlays + "
    "dual nulls B/P resampling ~4-6x screen-cell weight; W2-W8 judge "
    "same-machinery precedent")

ticket_ref = (
    "T-2026-09-29-121 WAVE-9 judge slice (CEO O-2026-09-27-2245 thousand-trader "
    "order + O-2026-09-27-2250 standing law; prereg FROZEN bm-b r432 same-commit "
    "SEED berths 20309500/20310000/20310500 R250; runner full-slice built bm-b "
    "r432 selftest 49/49 hermetic sha16 b3d1a8d5dbb022a0; SCREEN-finalize "
    "LANDED bm-b r434: " + n_cells + "; judge-prep " + str(jprep) + " bm-b r434)")

prereg_ref = (
    "research/TRIAL_LABOR_W9_PREREG.md FROZEN sec.0 TRIAL_LAB_W9_JUDGE (s3 full "
    "judgment batch: batch_trials = survivors " + str(survivors) + " judged "
    "cells; dual nulls B/P resampling = not ledger +0 per prereg sec.0) + "
    "sec.0 W9-JUDGE physical-order gate (RAM r354 three-sample gate + "
    "serial-position confirm at entry; W8-JUDGE done + zero in-flight judge "
    "faces = queue face confirmed at entry; 48h CEO report clock starts at "
    "judge-finalize) + sec.4 (g1_prime_v2/g2_registration_v2 shared lib zero "
    "hand-copy; DSR n_trials = live chain head cross-wave no-reset, run-time "
    "live read governs = " + str(ledger_total) + " post-SCREEN; E[FP]=0.05*"
    "N_judged; family PBO CSCV 8 blocks family=strategy-module) + sec.9 pool "
    "routing (lane_owner=bm-b dual-face SCREEN+JUDGE per W8-corrected frozen "
    "law; judge face cache-less machines blocked at claim-time by host_gates "
    "MSG-1305 wiring -- in-runner exit 2 honest remains as second lock)")

data_gates = (
    "READY (entry-time deps re-verified live r434 bm-b): (1) serial-position "
    "face: zero in-flight judge faces ahead (W8-JUDGE entry done; pool judge "
    "face = this entry only); (2) judge-prep " + str(jprep) + " bm-b r434: "
    "results/trial_labor_w9/judge_state.json (manifest/census/gate-meta live "
    "reads by runner; in-runner fail-closed judge_state/w9_screen absent exit "
    "2; grammar sha16 != 0601dda70b0209fa refuse; zero-survivor vacuous face "
    "n/a = " + str(survivors) + " survivors); (3) RAM r354 three-sample gate "
    "re-run at submission. Judge dual-null rng trial_labor_w9_unc=20310500 "
    "[20310500, cell_idx] per prereg sec.3 s3; G2 n_trials live-head read = "
    + str(ledger_total) + " post-SCREEN cross-wave. After shard: "
    "judge-finalize = separate round work (ledger TRIAL_LAB_W9_JUDGE "
    "batch_trials=" + str(survivors) + " literal + w9_judge.json G1'/G2/DSR/"
    "PBO/E[FP] + seven-gate x amp interaction segmented disclosure columns "
    "per sec.3; intake slice next per prereg sec.6; 48h CEO report clock "
    "starts at judge-finalize; W10 prereg reference-band feed per consumer "
    "lineage)")

a = argparse.Namespace(
    id="TRIAL-LABOR-W9-JUDGE",
    runner="scripts/trial_labor_w9.py",
    shards="judge-0of1",
    runner_args="judge --shard 0 --shards 1",
    priority=1,
    lane_owner="bm-b",        # prereg sec.9 W8-corrected dual-face value
    workers=20,               # >= floor(16 cores / 0.8) per prereg sec.9 plan law
    wp_priority="BelowNormal",
    wp_note=wp_note,
    ticket_ref=ticket_ref,
    prereg_ref=prereg_ref,
    data_gates=data_gates,
    host_gates=(
        '[{"kind": "dir_nonempty", '
        '"path": "Money02/data/cache/t18_deep_panel/ohlcv", '
        '"pattern": "*.parquet"}]'),   # MSG-1305 wiring, bm-a r428 precedent
    shard_checkpoint=(
        "results/trial_labor_w9/checkpoint/judge_shard_0of1.jsonl "
        "(append-per-cell done-set resume, W1/W2 cross-kill law; dir "
        "gitignored per r429 root-cause class fix)"),
    shard_note=(
        "judge-0of1 single shard (W1-W8 judge single-shard precedent); "
        "workers BelowNormal; dual nulls B=2000 block bootstrap block=20 + "
        "P=2000 sign-flip two-sided in-shard per prereg sec.3 s3"),
    consumer_plan=(
        "TRIAL-LABOR-W9-JUDGE -> judged verdict face (w9_judge.json) -> s4 "
        "intake (D6 binding gate -> STRATEGY_LIBRARY registration rows) -> "
        "48h CEO report + scorecard CEO face; screen null p95 " + str(null_p95)
        + " -> next-wave prereg reference band (W1-W8 0.5116-0.5196 lineage, "
        "W9 sec.5.2 recalibrated band [0.50, 0.52] honest continuation)"),
)
rc = autofill.submit(a)
print("SUBMIT_RC=", rc)
sys.exit(rc)
