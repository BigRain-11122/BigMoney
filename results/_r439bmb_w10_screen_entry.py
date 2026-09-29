# -*- coding: utf-8 -*-
# r439 bm-b: W10-GENERATE burn-landing dual-face flip (pit-89 law: flip in the
# round where the burn lands; entry+shard same commit) + TRIAL-LABOR-W10-SCREEN
# pool entry submission same commit (r433 W9-SCREEN direct-ready precedent) +
# T-122 progress_r439 note.
import json, io, time

POOL = r"results/runnable_pool.json"
TICKET = r"fleet/tasks/T-2026-09-29-122-P1.json"
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")

pool = json.load(io.open(POOL, encoding="utf-8"))

# --- face 1: GENERATE entry + shard -> done (harvest record) ---
gen = None
for e in pool["entries"]:
    if e.get("id") == "TRIAL-LABOR-W10-GENERATE":
        assert e.get("status") == "ready", "unexpected generate status: %s" % e.get("status")
        e["status"] = "done"
        e["done_at"] = "2026-09-29T19:42:03+08:00"
        e["result_ref"] = (
            "results/trial_labor_w10/w10_candidates.json (single-shot completion "
            "marker landed 19:42:03; manual-tick ignition 19:31:15 pid3808 r438 "
            "lineage after r438 dead-session heritage-absorb unlock [pit-113 "
            "heritage-absorb-first law]; runner exited clean, elapsed 646.4s, "
            "zero engine cells burned); n=2014 (raw 5,000 A500/B4500 -> "
            "exclusion hits 0 -> dedup 2,014 distinct, BELOW the [2,600, 4,600] "
            "sec.5.1 prediction band = falsifiable prediction face per prereg "
            "sec.5.1 pre-noted below-band risk, judged by actual not by band; "
            "fp-collapses 2,410 + corr-collapses 3,619; mom faces {mom_oversold "
            "736, none 1,278}; eight-gate interaction face 111-non-empty "
            "lineage carried in ledger row; TRIAL_GRAMMAR_LEDGER wave-10 row "
            "runner-written at consume (sha16 e21c7eb83087035c, constructively "
            "distinct from W1/MASS/W2-W9); screen-prep PASS bm-b r439 19:45 "
            "same harvest window (panel 48/48, anchors 6/6, census "
            "{6m 1253, 12m 1127, 24m 875}, passive precomputed, G-MOM "
            "153open/1339closed decidable 1492 warmup 139 = frozen anchor); "
            "TRIAL-LABOR-W10-SCREEN pool entry submitted same commit "
            "(2,214 cells = 2,014 distinct + 200 nulls, lane_owner=bm-b "
            "dual-face per pit-103)")
        for s in e.get("shards", []):
            if s.get("key") == "generate-0of1":
                s["status"] = "done"
                s["done_at"] = "2026-09-29T19:42:03+08:00"
                s["result_ref"] = (
                    "results/trial_labor_w10/w10_candidates.json "
                    "(single-shot product = completion marker honored)")
        gen = e["id"]
assert gen, "W10-GENERATE entry not found"

# --- face 2: SCREEN entry submission (ready) ---
if any(e.get("id") == "TRIAL-LABOR-W10-SCREEN" for e in pool["entries"]):
    print("refuse: SCREEN entry exists"); raise SystemExit(2)

entry = {
 "id": "TRIAL-LABOR-W10-SCREEN",
 "ticket_ref": "T-2026-09-29-122 WAVE-10 screen slice (CEO O-2026-09-27-2245 "
   "thousand-trader order + O-2026-09-27-2250 standing law; prereg FROZEN "
   "bm-b r437 berth-open adoption of the bm-c r228 MOM candidate whole "
   "package per AMP->W9 precedent; SEED berths 20311000/20311500/20312000 "
   "registered same freeze-commit R250 one-step law, freeze-time three-step "
   "re-verify ALL GREEN no re-pick; pool routing lane_owner=bm-b SCREEN+JUDGE "
   "per prereg sec.6 both-faces value (W8 freeze-time correction lineage, "
   "pit-103 dead-hand recurrence-proof); runner slice-1 built bm-b r438; "
   "GENERATE landed r438 ignition 19:31:15 pid3808 -> n=2014 19:42:03 + "
   "TRIAL_GRAMMAR_LEDGER wave-10 row, harvest committed r439)",
 "prereg_ref": "research/TRIAL_LABOR_W10_PREREG.md FROZEN sec.0 "
   "TRIAL_LAB_W10_SCREEN (s2 cheap initial screen batch: batch_trials = "
   "2,014 distinct + 200 nulls = 2,214 cells at 1 trial/cell; raw 5,000 -> "
   "dedup 2,014 honest BELOW the [2,600, 4,600] sec.5.1 prediction band = "
   "falsifiable prediction face pre-noted in prereg, judgment by actual not "
   "by band; evidence_cutoff 2026-09-22 P-5C frozen binding on both batches; "
   "thirteen-tuple grammar sha16 e21c7eb83087035c == FROZEN)",
 "runner": "scripts/trial_labor_w10.py",
 "runner_args": ["screen", "--shard", "0", "--shards", "1"],
 "lane_owner": "bm-b",
 "priority": 1,
 "status": "ready",
 "entered_at": NOW,
 "data_gates": "GATES ALL GREEN (direct-ready r439, W1-W9-SCREEN lineage): "
   "(1) TRIAL-LABOR-W10-GENERATE done -- landed 19:42:03 w10_candidates.json "
   "n=2014 single-shot completion marker in-repo this commit "
   "(refuse-if-exists guard); (2) screen-prep PASS -- "
   "results/trial_labor_w10/prep_state.json bm-b r439 19:45: panel 48/48, "
   "anchors 6/6 faithful (grammar_replay IS/OOS == frozen), census "
   "{6m 1253, 12m 1127, 24m 875} == frozen, starts 1253, passive 6m "
   "precomputed, gate na-window 199 bars, G-VOL 594calm/518wild first-valid "
   "519, G-YANG 819yang/812red zero-warmup, G-VCONF 784surge/828dry warmup "
   "19, G-STREAK 384up/389down/856neither warmup 2, G-TSTATE mad60 "
   "188true/1453decidable warmup 178 + rsv60 332true/1572decidable warmup 59, "
   "G-AMP 801wide/811narrow decidable 1612 warmup 19, G-MOM 153open/1339closed "
   "decidable 1492 warmup 139 (NEW wave-10 fail-closed anchor face, "
   "prep-window replay; full-history 374/3344/2970 per r228 probe facts); "
   "(3) grammar sha16 e21c7eb83087035c == FROZEN pinned at candidates "
   "serialization (fail-closed gate-b)",
 "consumer_plan": "TRIAL-LABOR-W10-SCREEN -> screen-finalize (lane-owner "
   "separate round work per W5-W9 precedent) -> w10_screen.json + "
   "w10_screen_cells.csv + null p95 (W1-W9 lineage 0.5116-0.5196 reference "
   "band, W9=0.517199; W10 sec.5.2 band [0.50, 0.52] honest continuation) + "
   "ledger TRIAL_LAB_W10_SCREEN row (science_gates.append_ledger live-head "
   "prev read, pit-112 out-dict embed law; batch_trials=2,214) -> "
   "TRIAL-LABOR-W10-JUDGE entry next (judge-prep + RAM r354 three-sample "
   "gate + serial-position face = zero in-flight judge faces ahead + "
   "host_gates MSG-1305 wiring per pit-103: dir_nonempty Money02 deep-panel "
   "ohlcv parquet verified non-empty at JUDGE submission pre-flight) -> "
   "judged verdict face w10_judge.json (eight-gate x mom interaction "
   "disclosure columns per sec.3 incl. MOM x TSTATE adjacency audit column) "
   "-> s4 intake (D6 binding gate -> STRATEGY_LIBRARY registration rows + "
   "TRIAL-<FAMILY>-<NN> paper onboarding) -> 48h CEO report clock starts at "
   "judge landing; W11 prereg reference-band feed per consumer lineage",
 "shards": [
  {"key": "screen-0of1",
   "status": "ready",
   "checkpoint": "results/trial_labor_w10/checkpoint/screen_shard_0of1.jsonl "
                 "(append-per-cell done-set resume, W1/W2 cross-kill law; "
                 "dir gitignored per r429 root-cause class fix)",
   "note": "single shard; worker_cap() parallelism inside the shard "
           "(W2-W9-SCREEN same shape); multi-shard i%shards split legal "
           "per shard law on partial claim"}
 ],
 "entered_by": "bm-b r439",
 "worker_class": "self-contained",
 "workers_plan": {
   "workers": "worker_cap() pool BelowNormal (16-core bm-b: <=12; "
              "W9-SCREEN 2,715 cells; W10-SCREEN 2,214 cells = 2,014 "
              "distinct + 200 nulls; screen leg-L 6m full-history per cell, "
              "eight-gate face carried per cell)",
   "priority": "BelowNormal",
   "note": "hours-scale pool batch per prereg sec.0 (W9-SCREEN 2,715 cells "
           "burned ~8min wall at 12 workers); checkpoint every 50 candidates "
           "per prereg sec.0"}
}
pool["entries"].append(entry)
pool["updated_at"] = NOW
with io.open(POOL, "w", encoding="utf-8", newline="") as f:
    json.dump(pool, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("pool flip: TRIAL-LABOR-W10-GENERATE -> done (entry+shard dual-face)")
print("pool entry submitted: TRIAL-LABOR-W10-SCREEN ready lane_owner=bm-b "
      "entries=%d" % len(pool["entries"]))

t = json.load(io.open(TICKET, encoding="utf-8"))
t["progress_r439_bmb"] = (
    "r439 bm-b: GENERATE harvest committed + SCREEN slice submitted same "
    "commit (product-priority law) -- w10_candidates.json n=2014 landed "
    "19:42:03 (raw 5,000 -> exclusion 0 -> dedup 2,014 distinct BELOW "
    "[2,600, 4,600] sec.5.1 band = falsifiable prediction face honest, "
    "fp-collapses 2,410 + corr-collapses 3,619, mom faces oversold 736 / "
    "none 1,278, elapsed 646.4s zero engine cells; TRIAL_GRAMMAR_LEDGER "
    "wave-10 row sha16 e21c7eb83087035c runner-written at consume); "
    "screen-prep PASS bm-b r439 19:45 (panel 48/48, anchors 6/6, census "
    "6m/12m/24m 1253/1127/875, passive precomputed, G-MOM 153open/1339closed "
    "decidable 1492 warmup 139 = frozen anchor); TRIAL-LABOR-W10-SCREEN "
    "pool entry submitted same commit (2,214 cells = 2,014 distinct + 200 "
    "nulls, lane_owner=bm-b, consumer_plan per pit-103); screen burn = "
    "autofill face next tick; screen-finalize + JUDGE entry = separate "
    "round work per frozen law (48h CEO report clock starts at "
    "judge-finalize)")
t["progress_r439_ts"] = NOW
with io.open(TICKET, "w", encoding="utf-8", newline="") as f:
    json.dump(t, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("ticket progress_r439 written")
