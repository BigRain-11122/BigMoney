import sys
import argparse

sys.path.insert(0, "Tools")
import autofill

# r413 bm-b: canonical pool submit TRIAL-LABOR-W6-JUDGE (O-1820(3) consumer_plan
# law + r301/r305 contract trio + D-20260929-02 inbox declaration guard built
# into Tools/autofill.py submit). All three entry-time deps MET this round:
# serial-position (pool drained 109/109) + judge-prep PASS + RAM r354 3-sample.
# File-face driver per pit-law batch-80 (CJK command-channel write corruption).

a = argparse.Namespace(
    id="TRIAL-LABOR-W6-JUDGE",
    runner="scripts/trial_labor_w6.py",
    shards="judge-0of1",
    runner_args="judge --shard 0 --shards 1",
    priority=1,
    lane_owner=None,          # prereg sec.9 pool routing: lane_owner=null frozen
    workers=20,               # >= floor(16 cores / 0.8) per prereg sec.9 plan law
    wp_priority="BelowNormal",
    wp_note=("worker_cap() RAM-guard governs at runtime (runner self-caps, "
             "--workers omitted from runner_args per W5-JUDGE same-machinery "
             "precedent); plan size 20 = floor(16 cores/0.8) per prereg sec.9 "
             "lower-bound; judge initargs carry BOTH leg panels + per-leg ATR20 "
             "+ per-leg gate/vol/yang/vconf state faces = heaviest per-worker "
             "state in the fleet; dual-leg x {6m,12m,24m} x cost {base x1, "
             "x2=CostPatch(2)} engine curves per judged cell WITH gate+vol+"
             "yang+vconf+stop overlays + dual nulls B/P resampling ~4-6x "
             "screen-cell weight; W2/W3/W4/W5 judge same-machinery precedent"),
    ticket_ref=("T-2026-09-29-117 WAVE-6 judge slice (CEO O-2026-09-27-2245 "
                "thousand-trader order + O-2026-09-27-2250 standing law; prereg "
                "FROZEN bm-c r198 commit ead43f0d2 healthy-takeover; SEED berths "
                "20303500/20304000/20304500 same-commit R250; runner full-slice "
                "built bm-b r410 selftest 80/80 hermetic + fix-first 0006c24f9 "
                "production-validated; SCREEN-finalize LANDED bm-b r413 06:49: "
                "3952+200 cells, null p95 0.5196 (json 6dp 0.519553), survivors "
                "293 -- judge physical dep satisfied; judge-prep PASS bm-b r413)"),
    prereg_ref=("research/TRIAL_LABOR_W6_PREREG.md FROZEN sec.0 TRIAL_LAB_W6_JUDGE "
                "(s3 full judgment batch: batch_trials = survivors 293 judged "
                "cells; dual nulls B/P resampling = not ledger +0 per prereg "
                "sec.0) + sec.0 W6-JUDGE physical-order gate (RAM r354 "
                "three-sample gate + serial-position confirm at entry; W5-JUDGE "
                "+ all other judge faces done = queue face confirmed at entry; "
                "48h CEO report clock starts at judge-finalize) + sec.4 "
                "(g1_prime_v2/g2_registration_v2 shared lib zero hand-copy; DSR "
                "n_trials = live chain head cross-wave no-reset, run-time live "
                "read governs = 333139 post-SCREEN; E[FP]=0.05*N_judged; family "
                "PBO CSCV 8 blocks family=strategy-module) + sec.9 pool routing "
                "(lane_owner=null per frozen law; judge face cache-less machines "
                "in-runner exit 2 honest W1-W5 precedent)"),
    data_gates=("READY (all three entry-time deps MET r413 bm-b): (1) "
                "serial-position face: pool drained 109/109 done at entry "
                "(V3-TOURNAMENT + W6-SCREEN done-flips same round r413), zero "
                "in-flight verdict faces ahead; (2) judge-prep PASS bm-b r413: "
                "manifest PASS 48 members, census L/D == frozen, survivors 293, "
                "gate meta L/D na-window 199/199, vol 519/519 (leg-L anchors "
                "594calm/518wild), yang zero-warmup 819yang/812red, vconf "
                "19-bar warmup 784surge/828dry -> results/trial_labor_w6/"
                "judge_state.json; (3) RAM r354 three-sample PASS 10.38/10.58/"
                "12.71 GB across 31s (>=4GB law). In-runner fail-closed: "
                "judge_state/w6_screen absent exit 2; grammar sha16 != "
                "2d395f5f8e7d16cb refuse; zero-survivor vacuous face n/a (293 "
                "survivors). Judge dual-null rng trial_labor_w6_unc=20304500 "
                "[20304500, cell_idx] per prereg sec.3 s3; G2 n_trials "
                "live-head read = 333139 post-SCREEN cross-wave. After shards: "
                "judge-finalize = separate round work (ledger "
                "TRIAL_LAB_W6_JUDGE batch_trials=293 literal + w6_judge.json "
                "G1'/G2/DSR/PBO/E[FP] + gate x vol x yang x vconf segmented "
                "disclosure; intake slice next per prereg sec.6; 48h CEO report "
                "clock starts at judge-finalize)"),
    shard_checkpoint=("results/trial_labor_w6/checkpoint/judge_shard_0of1.jsonl "
                      "(append-per-cell done-set resume, W1/W2 cross-kill law)"),
    shard_note=("judge-0of1 single shard (W1-W5 judge single-shard precedent); "
                "workers BelowNormal; dual nulls B=2000 block bootstrap + "
                "P=2000 sign-flip in-shard per prereg sec.3 s3"),
    consumer_plan=("TRIAL-LABOR-W6-JUDGE -> judged verdict face (w6_judge.json) "
                   "-> s4 intake -> STRATEGY_LIBRARY + TRIAL-* paper accounts -> "
                   "48h CEO report + scorecard CEO face; screen null p95 -> "
                   "next-wave prereg reference band (W1-W5 0.5116/0.5164 "
                   "lineage)"),
)
rc = autofill.submit(a)
print("SUBMIT_RC=", rc)
sys.exit(rc)
