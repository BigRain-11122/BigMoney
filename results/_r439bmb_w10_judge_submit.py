# -*- coding: utf-8 -*-
# r439 bm-b: W10-SCREEN burn-landing dual-face flip (pit-89: flip in the round
# where the burn lands; entry+shard same commit) + TRIAL-LABOR-W10-JUDGE pool
# entry submission same commit (r434 W9 precedent: screen-finalize + judge-prep
# + JUDGE submit all in the landing round).
import sys
import json
import io

sys.path.insert(0, "Tools")
import autofill

POOL = r"results/runnable_pool.json"

# --- live reads (fail-closed) ---
try:
    scr = json.load(io.open(r"results/trial_labor_w10/w10_screen.json",
                            encoding="utf-8"))
    n_distinct = scr["n_distinct"]
    n_nulls = scr["k_nulls"]
    null_p95 = scr["null_family"]["p95_line"]
    survivors = scr["n_survivors"]
    led = scr["trials_ledger"]
    ledger_total = led["total"]
    cutoff = scr["evidence_cutoff"]
except Exception as ex:
    print("REFUSED: w10_screen.json unreadable/missing fields:", ex)
    sys.exit(2)

try:
    jst = json.load(io.open(r"results/trial_labor_w10/judge_state.json",
                            encoding="utf-8"))
    jprep = jst["g_manifest"]["verdict"]
except Exception as ex:
    print("REFUSED: judge_state.json unreadable/missing (run judge-prep first):",
          ex)
    sys.exit(2)

n_cells = "{}+{} cells (distinct+nulls), null p95 {}, survivors {}".format(
    n_distinct, n_nulls, null_p95, survivors)

# --- face 1: SCREEN entry + shard -> done (dual-face, same commit) ---
pool = json.load(io.open(POOL, encoding="utf-8"))
flip = None
for e in pool.get("entries", []):
    if e.get("id") == "TRIAL-LABOR-W10-SCREEN":
        assert e.get("status") in ("ready", "running"), (
            "unexpected screen status: %s" % e.get("status"))
        e["status"] = "done"
        e["done_at"] = "2026-09-29T19:54:20+08:00"
        e["result_ref"] = (
            "results/trial_labor_w10/w10_screen.json (2,214/2,214 cells ckpt "
            "complete 19:54 runner pid6200 manual-tick ignition 19:47:02 "
            "r439 autofill lineage; finalize landed same round: distinct "
            "2,014 + nulls 200, null p95_line 0.5164 IN prereg sec.5.2 band "
            "[0.50,0.52] (W1-W9 lineage 0.5116-0.5196 continuation), "
            "survivors 283/2,014 = 14.05%; RESEARCH FACT: MOM segmented "
            "survival mom_oversold 147/736 19.97% vs none 136/1,278 10.64% = "
            "1.88x ENRICHMENT at screen face = momentum-confirmation gate "
            "POSITIVE-axis finding (opposite of W9 AMP anti-enrichment "
            "narrow 7.17% < wide 10.69% < none 11.02%; addresses prereg "
            "sec.1 '121 mom-unique-day speed-axis incremental space' true "
            "question -- screen-face readout, not a registration claim); "
            "eight-gate interaction survival face computed; ledger live-head "
            "prev read + 2,214 = " + str(ledger_total) + " reconcile OK "
            "(pit-112 out-dict embed verified); judge-prep " + str(jprep) +
            " same round (manifest 48, census L/D == frozen, gate meta "
            "incl. G-MOM 153/1339/1492 warmup 139); TRIAL-LABOR-W10-JUDGE "
            "pool entry submitted same commit (host_gates MSG-1305 wiring, "
            "lane_owner=bm-b dual-face)"
        )
        for s in e.get("shards", []):
            if s.get("key") == "screen-0of1":
                s["status"] = "done"
                s["owner"] = "bm-b"
                s["owner_since"] = "2026-09-29 19:47:02"
                s["done_at"] = "2026-09-29 19:54:20"
                s["result_ref"] = (
                    "results/trial_labor_w10/checkpoint/screen_shard_0of1.jsonl "
                    "(2,214/2,214 rows complete, cross-kill resume law)")
        flip = e["id"]
assert flip, "W10-SCREEN entry not found"
with io.open(POOL, "w", encoding="utf-8", newline="") as f:
    json.dump(pool, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("pool flip: TRIAL-LABOR-W10-SCREEN -> done (entry+shard dual-face)")

# --- face 2: JUDGE entry submission (autofill.submit: RAM r354 three-sample
#     in-submit + single-writer pool append) ---
wp_note = (
    "worker_cap() RAM-guard governs at runtime (runner self-caps, --workers "
    "omitted from runner_args per W5/W6/W9-JUDGE same-machinery precedent); "
    "plan size 20 = floor(16 cores/0.8) per prereg sec.0 lower-bound; judge "
    "initargs carry BOTH leg panels + per-leg ATR20 + per-leg gate/vol/yang/"
    "vconf/streak/tstate/amp/mom state faces = heaviest per-worker state in "
    "the fleet; dual-leg x {6m,12m,24m} x cost {base x1, x2=CostPatch(2)} "
    "engine curves per judged cell WITH eight-gate overlays + dual nulls "
    "B/P resampling ~4-6x screen-cell weight; W2-W9 judge same-machinery "
    "precedent")

ticket_ref = (
    "T-2026-09-29-122 WAVE-10 judge slice (CEO O-2026-09-27-2245 thousand-"
    "trader order + O-2026-09-27-2250 standing law; prereg FROZEN bm-b r437 "
    "berth-open adoption of bm-c r228 MOM candidate per AMP->W9 precedent, "
    "same-commit SEED berths 20311000/20311500/20312000 R250 one-step; "
    "runner full-slice built bm-b r438 selftest 47/47 hermetic sha16 "
    "31b23b9f33be2756; GENERATE harvest + SCREEN-finalize LANDED bm-b r439 "
    "same round: " + n_cells + "; judge-prep " + str(jprep) + " bm-b r439)")

prereg_ref = (
    "research/TRIAL_LABOR_W10_PREREG.md FROZEN sec.0 TRIAL_LAB_W10_JUDGE "
    "(s3 full judgment batch: batch_trials = survivors " + str(survivors) +
    " judged cells; dual nulls B/P resampling = not ledger +0 per prereg "
    "sec.0) + sec.0 W10-JUDGE physical-order gate (RAM r354 three-sample "
    "gate + serial-position confirm at entry; W9-JUDGE done + zero "
    "in-flight judge faces = queue face confirmed at entry; 48h CEO report "
    "clock starts at judge-finalize) + sec.4 (g1_prime_v2/g2_registration_v2 "
    "shared lib zero hand-copy; DSR n_trials = live chain head cross-wave "
    "no-reset, run-time live read governs = " + str(ledger_total) +
    " post-SCREEN; E[FP]=0.05*N_judged; family PBO CSCV 8 blocks "
    "family=strategy-module) + sec.6 pool routing (lane_owner=bm-b "
    "dual-face SCREEN+JUDGE; judge face cache-less machines blocked at "
    "claim-time by host_gates MSG-1305 wiring -- in-runner exit 2 honest "
    "remains as second lock)")

data_gates = (
    "READY (entry-time deps re-verified live r439 bm-b): (1) serial-position "
    "face: zero in-flight judge faces ahead (W9-JUDGE entry done; pool judge "
    "face = this entry only); (2) judge-prep " + str(jprep) + " bm-b r439: "
    "results/trial_labor_w10/judge_state.json (manifest/census/gate-meta "
    "live reads by runner; in-runner fail-closed judge_state/w10_screen "
    "absent exit 2; grammar sha16 != e21c7eb83087035c refuse; zero-survivor "
    "vacuous face n/a = " + str(survivors) + " survivors); (3) RAM r354 "
    "three-sample gate re-run at submission. Judge dual-null rng "
    "trial_labor_w10_unc=20312000 [20312000, cell_idx] per prereg sec.3 s3; "
    "G2 n_trials live-head read = " + str(ledger_total) + " post-SCREEN "
    "cross-wave. After shard: judge-finalize = separate round work (ledger "
    "TRIAL_LAB_W10_JUDGE batch_trials=" + str(survivors) + " literal + "
    "w10_judge.json G1'/G2/DSR/PBO/E[FP] + eight-gate x mom interaction "
    "segmented disclosure columns per sec.3 incl. MOM x TSTATE adjacency "
    "audit column; intake slice next per prereg sec.6; 48h CEO report clock "
    "starts at judge-finalize; W11 prereg reference-band feed per consumer "
    "lineage)")

import argparse
a = argparse.Namespace(
    id="TRIAL-LABOR-W10-JUDGE",
    runner="scripts/trial_labor_w10.py",
    shards="judge-0of1",
    runner_args="judge --shard 0 --shards 1",
    priority=1,
    lane_owner="bm-b",        # prereg sec.6 dual-face value
    workers=20,               # >= floor(16 cores / 0.8) per prereg sec.0
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
        "results/trial_labor_w10/checkpoint/judge_shard_0of1.jsonl "
        "(append-per-cell done-set resume, W1/W2 cross-kill law; dir "
        "gitignored per r429 root-cause class fix)"),
    shard_note=(
        "judge-0of1 single shard (W1-W9 judge single-shard precedent); "
        "workers BelowNormal; dual nulls B=2000 block bootstrap block=20 + "
        "P=2000 sign-flip two-sided in-shard per prereg sec.3 s3"),
    consumer_plan=(
        "TRIAL-LABOR-W10-JUDGE -> judged verdict face (w10_judge.json) -> s4 "
        "intake (D6 binding gate -> STRATEGY_LIBRARY registration rows + "
        "TRIAL-<FAMILY>-<NN> paper onboarding) -> 48h CEO report + scorecard "
        "CEO face; screen null p95 " + str(null_p95) + " -> next-wave (W11) "
        "prereg reference band (W1-W9 0.5116-0.5196 lineage, W10 sec.5.2 "
        "band [0.50, 0.52] honest continuation)"),
)
rc = autofill.submit(a)
print("SUBMIT_RC=", rc)
sys.exit(rc)
