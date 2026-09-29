import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

path = "results/runnable_pool.json"
p = json.load(open(path, encoding="utf-8"))

gen = [x for x in p["entries"] if x.get("id") == "TRIAL-LABOR-W11-GENERATE"][0]
# sanity: candidates single-shot product in-repo = completion marker (refuse-if-exists guard)
import os
assert os.path.exists("results/trial_labor_w11/w11_candidates.json"), "candidates missing"
cand = json.load(open("results/trial_labor_w11/w11_candidates.json", encoding="utf-8"))
n_distinct = cand["n"]
sha16 = cand["grammar_sha256"][:16]
assert sha16 == "128962592feeb8d3", f"grammar sha mismatch {sha16}"

gen["status"] = "done"
gen["done_at"] = "2026-09-30T00:49:00+08:00"
gen["result_ref"] = (
    "results/trial_labor_w11/w11_candidates.json (n=1,262 distinct from raw 5,000; single-shot product landed 23:48:32 "
    "autofill pid13836 ignition 23:36:16 post r442-close fix-first; grammar sha16 128962592feeb8d3 == FROZEN pin "
    "verified at adoption; TRIAL_GRAMMAR_LEDGER wave-11 row consumed 23:48:32 in-tree same batch; honest note: "
    "1,262 distinct BELOW sec.5.1 >=3,000 prediction band = falsifiable prediction face pre-noted in prereg, "
    "judgment by actual not by band (W10 2,014-below-band precedent); heritage adoption r443 per r240 law -- "
    "candidates file complete JSON parse-verified, zero live cells burned at generate stage by design)"
)
gen["shards"][0]["status"] = "done"
gen["shards"][0]["done_at"] = "2026-09-29 23:48:32"
gen["shards"][0]["result_ref"] = "results/trial_labor_w11/w11_candidates.json (single-shot completion marker)"

assert not [x for x in p["entries"] if x.get("id") == "TRIAL-LABOR-W11-SCREEN"], "SCREEN entry exists"

screen = {
    "id": "TRIAL-LABOR-W11-SCREEN",
    "ticket_ref": (
        "T-2026-09-29-123 WAVE-11 screen slice (CEO O-2026-09-27-2245 thousand-trader order + O-2026-09-27-2250 "
        "standing law; prereg FROZEN bm-b r441 whole-package adoption of the bm-c r237 STD candidate per AMP->W9->W10 "
        "lineage; SEED berth re-take 20317000/20317500/20318000 same freeze-commit R250 one-step law, three-step "
        "re-verify ALL GREEN no re-pick (r441 collision-re-take clause-5 executed); runner slice-1 built bm-b r442 "
        "selftest 47/47 fourteen-tuple 31,352,832 grammar + r442-close fix-first (surgery-dropped tl9 amp import "
        "restore + FROZEN_SHA16 pin 128962592feeb8d3 + screen-finalize 3-landmine cluster fix); GENERATE landed "
        "23:48:32 pid13816/13836 autofill lineage n=1,262 + TRIAL_GRAMMAR_LEDGER wave-11 row, heritage adopted r443)"
    ),
    "prereg_ref": (
        "research/TRIAL_LABOR_W11_PREREG.md FROZEN sec.0 TRIAL_LAB_W11_SCREEN (s2 cheap initial screen batch: "
        "batch_trials = 1,262 distinct + 200 nulls = 1,462 cells at 1 trial/cell; raw 5,000 -> dedup 1,262 honest "
        "BELOW the >=3,000 sec.5.1 prediction band = falsifiable prediction face pre-noted in prereg, judgment by "
        "actual not by band; evidence_cutoff 2026-09-22 P-5C frozen binding on both batches; fourteen-tuple grammar "
        "sha16 128962592feeb8d3 == FROZEN pin; null p95 prediction band [0.50,0.52] same W10 caliber, reference "
        "lineage W1-W10 (W10 actual 0.516361))"
    ),
    "runner": "scripts/trial_labor_w11.py",
    "runner_args": ["screen", "--shard", "0", "--shards", "1"],
    "lane_owner": "bm-b",
    "priority": 1,
    "status": "ready",
    "entered_at": "2026-09-30T00:49:00+08:00",
    "entered_by": "bm-b r443",
    "data_gates": (
        "GATES ALL GREEN (direct-ready r443, W1-W10-SCREEN lineage): (1) TRIAL-LABOR-W11-GENERATE done -- landed "
        "23:48:32 w11_candidates.json n=1,262 single-shot completion marker in-repo this commit (refuse-if-exists "
        "guard); (2) screen-prep PASS -- results/trial_labor_w11/prep_state.json bm-b r443 00:47: panel 48/48, "
        "anchors 6/6 faithful (grammar_replay IS/OOS == frozen), census {6m 1253, 12m 1127, 24m 875} == frozen, "
        "starts 1253, passive 6m precomputed, gate na-window 199 bars, G-VOL 594calm/518wild first-valid 519, "
        "G-YANG 819yang/812red zero-warmup, G-VCONF 784surge/828dry warmup 19, G-STREAK 384up/389down/856neither "
        "warmup 2, G-TSTATE mad60 188true/1453decidable warmup 178 + rsv60 332true/1572decidable warmup 59, G-AMP "
        "801wide/811narrow decidable 1612 warmup 19, G-MOM 153open/1339closed decidable 1492 warmup 139 (W10 "
        "prep-window replay face carried), G-STD face carried in prep per fourteen-tuple; (3) grammar sha16 "
        "128962592feeb8d3 == FROZEN pinned at candidates serialization (fail-closed gate-b)"
    ),
    "consumer_plan": (
        "TRIAL-LABOR-W11-SCREEN -> screen-finalize (lane-owner separate round work per W5-W10 precedent) -> "
        "w11_screen.json + w11_screen_cells.csv + null p95 (W1-W10 lineage 0.5116-0.5196 reference band, W10=0.516361; "
        "W11 sec.5.2 band [0.50,0.52] honest continuation) + ledger TRIAL_LAB_W11_SCREEN row (science_gates.append_ledger "
        "live-head prev read, pit-112 out-dict embed law; batch_trials=1,462) -> TRIAL-LABOR-W11-JUDGE entry next "
        "(judge-prep + RAM r354 three-sample gate + serial-position face = zero in-flight judge faces ahead + host_gates "
        "MSG-1305 wiring per pit-103: dir_nonempty Money02 deep-panel ohlcv parquet verified non-empty at JUDGE "
        "submission pre-flight) -> judged verdict face w11_judge.json (nine-gate x mom/std interaction disclosure "
        "columns per sec.3 incl. STD x MOM adjacency audit column + W10 real-mom exclusion rows law) -> s4 intake "
        "(D6 binding gate -> STRATEGY_LIBRARY registration rows + TRIAL-<FAMILY>-<NN> paper onboarding) -> 48h CEO "
        "report clock starts at judge landing; W12 prereg reference-band feed per consumer lineage"
    ),
    "shards": [
        {
            "key": "screen-0of1",
            "status": "ready",
            "checkpoint": (
                "results/trial_labor_w11/checkpoint/screen_shard_0of1.jsonl (append-per-cell done-set resume, "
                "W1/W2 cross-kill law; dir gitignored per r429 root-cause class fix)"
            ),
            "note": "single shard; worker_cap() parallelism inside the shard (W2-W10-SCREEN same shape); multi-shard i%shards split legal per shard law on partial claim",
            "owner": "bm-b",
            "owner_since": "2026-09-30 00:49:00",
        }
    ],
    "worker_class": "self-contained",
    "workers_plan": {
        "workers": "worker_cap() pool BelowNormal (16-core bm-b: <=12; W10-SCREEN 2,214 cells ~7min wall at 12 workers; W11-SCREEN 1,462 cells = 1,262 distinct + 200 nulls; screen leg-L 6m full-history per cell, nine-gate face carried per cell)",
        "priority": "BelowNormal",
        "note": "hours-scale pool batch per prereg sec.0 (W9-SCREEN 2,715 cells ~8min; W10-SCREEN 2,214 ~7min; W11 1,462 lighter); checkpoint every 50 candidates per prereg sec.0; free RAM 7.3GB at arm > 4GB r354 three-sample ban threshold",
    },
}
p["entries"].append(screen)
p["updated_at"] = "2026-09-30T00:49:00+08:00"

with open(path, "w", encoding="utf-8") as f:
    json.dump(p, f, ensure_ascii=False, indent=1)
print("pool updated: GENERATE=done + SCREEN=ready armed; entries:", len(p["entries"]))
