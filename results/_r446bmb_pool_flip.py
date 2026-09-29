"""r446 bm-b pool bookkeeping flip: TRIAL-LABOR-W12-SCREEN -> done
(+result_ref) and TRIAL-LABOR-W12-JUDGE entry enqueue (status=ready).
Single-purpose surgical json edit, verified read-back; W11-JUDGE
entry field pattern mirrored (W5-W11 lineage). Idempotent on rerun
(already-done -> honest skip exit 0)."""

import json
import sys
import time

POOL = "results/runnable_pool.json"
NOW_LOCAL = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")

d = json.load(open(POOL, encoding="utf-8"))
entries = d["entries"]
by_id = {e["id"]: e for e in entries}
changed = []

# --- flip 1: W12-SCREEN -> done
scr = by_id.get("TRIAL-LABOR-W12-SCREEN")
if scr is None:
    print("FLIP FAIL: TRIAL-LABOR-W12-SCREEN entry absent")
    sys.exit(2)
if scr.get("status") == "done":
    print("SCREEN already done -- idempotent skip")
else:
    scr["status"] = "done"
    scr["result_ref"] = (
        "results/trial_labor_w12/w12_screen.json + w12_screen_cells.csv "
        "(screen-finalize 2026-09-30 04:3x exit 0 by bm-b r446; 1,059/1,059 "
        "cells = 859 distinct + 200 nulls; null p95 0.5132 IN sec.5.2 band "
        "[0.50,0.52]; survivors 188/859 = 21.88%; ledger 355,083 linear "
        "append-verified (+1,059 from 354,024); RESEARCH FACTS: "
        "rsqr-axis first screen face rsqr10_hi 26.35% ~ none 25.43% > "
        "rsqr20_hi 8.15% toxic-low face; std10_hi 30.64% > none 20.00% > "
        "std20_hi 18.98% replication (W11 asymmetry holds); mom_oversold "
        "23.81% vs none 20.89% = 1.14x continuation weakening lineage "
        "W10 1.88x -> W11 1.25x -> W12 1.14x) -- burn on autofill "
        "lineage pid~04:10:04-04:13:00 shard ckpt 1,059 lines complete")
    scr["done_at"] = NOW_LOCAL
    for sh in scr.get("shards", []):
        sh["status"] = "done"
        sh["done_note"] = ("burn complete 04:13:00 ckpt 1059/1059; "
                           "finalize by lane-owner r446")
    changed.append("W12-SCREEN->done")

# --- flip 2: W12-JUDGE enqueue
if "TRIAL-LABOR-W12-JUDGE" in by_id:
    print("JUDGE entry already present -- idempotent skip")
else:
    judge_entry = {
        "id": "TRIAL-LABOR-W12-JUDGE",
        "ticket_ref": (
            "T-2026-09-30-124 WAVE-12 judge slice (TRIAL_LABOR_LAW "
            "sec.1 standing supply; prereg FROZEN bm-b r444; runner "
            "FROZEN bm-b r445 grammar sha16 67c86c9cf4ef1ca7 fifteen-"
            "tuple 94,058,496 selftest 48/48 + r446 surgical fixes "
            "screen-prep axis 14->15 one-site miss + screen-finalize "
            "gvvvsktsams_seg init miss + judge-prep rsqr per-leg "
            "slope-sign disclosure key; GENERATE consumed bm-c autofill "
            "03:21:52-03:35:28 859 dedup, pool flip bm-c r250; SCREEN "
            "burned autofill lineage 04:10:04-04:13:00 1,059 cells, "
            "finalize bm-b r446: null p95 0.5132 IN [0.50,0.52], "
            "survivors 188/859 = 21.88%)"),
        "prereg_ref": (
            "research/TRIAL_LABOR_W12_PREREG.md FROZEN sec.0 "
            "TRIAL_LAB_W12_JUDGE (s3 full-judgment batch: "
            "batch_trials = screen survivors 188; dual nulls face; "
            "evidence_cutoff 2026-09-22 P-5C frozen binding; "
            "fifteen-tuple grammar sha16 67c86c9cf4ef1ca7 == FROZEN "
            "pin; judged-supply declare window per prereg sec.0)"),
        "runner": "scripts/trial_labor_w12.py",
        "runner_args": ["judge", "--shard", "0", "--shards", "1"],
        "lane_owner": "bm-b",
        "priority": 1,
        "status": "ready",
        "entered_at": NOW_LOCAL,
        "entered_by": "bm-b r446",
        "data_gates": (
            "GATES ALL GREEN (direct-ready r446, W11-JUDGE lineage): "
            "(1) TRIAL-LABOR-W12-SCREEN done -- w12_screen.json "
            "finalize r446 (1,059/1,059 cells, null p95 0.5132 IN "
            "band, survivors 188, ledger 355,083 linear "
            "append-verified); (2) judge-prep PASS bm-b r446 04:3x "
            "-- manifest 48 members, census L/D == frozen, survivors "
            "188, gate meta L/D all faces incl. std meta "
            "120-bar-warmup 128open/1383closed decidable 1511 "
            "std10-open 147 + rsqr meta L 163open/1348closed "
            "decidable 1511 rsqr10-open 142 slope-split 85up/78down "
            "disclosure (per-leg mirror of full-face sec.2(e)); "
            "(3) grammar sha16 67c86c9cf4ef1ca7 == FROZEN pin; "
            "(4) host_gates Money02 deep-panel parquet 5,383 files "
            "non-empty verified at submission pre-flight (W11 "
            "5,383 parity)"),
        "consumer_plan": (
            "TRIAL-LABOR-W12-JUDGE -> judge-finalize (lane-owner "
            "separate round work per W5-W11 precedent) -> "
            "w12_judge.json (G1'v2/G2/DSR/PBO/E[FP] faces + rsqr-"
            "axis disclosure columns) + ledger TRIAL_LAB_W12_JUDGE "
            "row (live-head prev read) -> s4 intake (D6 binding "
            "gate -> STRATEGY_LIBRARY registration rows + TRIAL-"
            "RSQR-<NN> paper onboarding) -> 48h CEO report clock "
            "starts at judge landing (CEO-REPORT-WAVE12, window by "
            "2026-10-02 04:00) + W13 prereg reference-band feed "
            "(screen null p95 0.5132 entered into lineage table)"),
        "shards": [
            {
                "key": "judge-0of1",
                "status": "ready",
                "checkpoint": (
                    "results/trial_labor_w12/checkpoint/"
                    "judge_shard_0of1.jsonl (append-per-cell done-set "
                    "resume; dir gitignored per r429)"),
                "note": (
                    "single shard; 188 survivors = lightest judge "
                    "batch of W5-W12 (W11 229 ~33min wall)"),
            }
        ],
        "worker_class": "self-contained",
        "workers_plan": (
            "{'workers': 'worker_cap() pool BelowNormal (16-core "
            "bm-b: <=12; W10-JUDGE 283 survivors ~33min wall; "
            "W11-JUDGE 229 survivors; W12-JUDGE 188 survivors "
            "lightest; dual-leg x base/x2 CostPatch(2) engine "
            "curves per cell + window-grouped shared-start "
            "pruning)', 'priority': 'BelowNormal'}"),
    }
    entries.append(judge_entry)
    changed.append("W12-JUDGE enqueued ready")

d["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
d["_stamp_note"] = (
    "r446 bm-b bookkeeping flip: W12-SCREEN done + W12-JUDGE armed "
    "(single_writer control-plane edit; autofill C8 read-side "
    "launches burn)")

with open(POOL, "w", encoding="utf-8", newline="\r\n") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
    f.write("\n")

# read-back verification
d2 = json.load(open(POOL, encoding="utf-8"))
by2 = {e["id"]: e for e in d2["entries"]}
assert by2["TRIAL-LABOR-W12-SCREEN"]["status"] == "done"
assert by2["TRIAL-LABOR-W12-SCREEN"]["shards"][0]["status"] == "done"
assert by2["TRIAL-LABOR-W12-JUDGE"]["status"] == "ready"
assert by2["TRIAL-LABOR-W12-JUDGE"]["runner"] == "scripts/trial_labor_w12.py"
assert len(d2["entries"]) == len(d["entries"])
print("pool flip OK:", ", ".join(changed) if changed else "no-op")
print("entries total:", len(d2["entries"]))
