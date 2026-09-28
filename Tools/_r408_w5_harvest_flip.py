"""r408 bm-a harvest flip: TRIAL-LABOR-W5-GENERATE ready->done (r244
landed-marker law) + TRIAL-LABOR-W5-SCREEN pool entry direct-ready
(W4-SCREEN lineage; gates all green in-repo this commit). One-shot
surgery script, pool single-writer discipline (round-side write)."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")

with open(POOL, encoding="utf-8") as fh:
    pool = json.load(fh)

ents = {e["id"]: e for e in pool["entries"]}
gen = ents["TRIAL-LABOR-W5-GENERATE"]
assert gen["status"] == "ready", f"generate not ready: {gen['status']}"
sh = gen["shards"][0]
assert sh["status"] == "ready", f"shard not ready: {sh['status']}"
# landed-marker proof (refuse-if-exists product must be present)
cand_path = os.path.join(ROOT, "results", "trial_labor_w5",
                         "w5_candidates.json")
assert os.path.exists(cand_path), "w5_candidates.json absent"
cg = json.load(open(cand_path, encoding="utf-8"))
assert cg["n"] == 3926 and cg["grammar_sha256"][:16] == "29720178c39425de"

ts = "2026-09-29 01:58:30"
sh["status"] = "done"
sh["checkpoint"] = ("results/trial_labor_w5/w5_candidates.json "
                     "(single-shot product = completion marker; "
                     "refuse-if-exists guard)")
sh["note"] = ("DONE r408 bm-a harvest (r244 landed-marker law): autofill "
              "relaunch 01:50:09 pid 81804 on fixed runner sha "
              "5c3a822f193d3922 (r407 fix-first: yang open-face reindex "
              "all-NaN bug + cross-table probe-basis verbatim vs tl3 "
              "warmup-gate semantic) -> landed 01:58:30; products "
              "w5_candidates.json n=3926 distinct grammar "
              "29720178c39425de evidence_cutoff 2026-09-22; G-YANG "
              "frozen anchors {yang 1751, yang&bull 962, red&bear 914} "
              "reproduced live at gate (r407 live-fire exact)")
sh["done_at"] = ts
gen["status"] = "done"
gen["done_at"] = ts
gen["result_ref"] = "results/trial_labor_w5/w5_candidates.json"
gen["done_note"] = ("r408 bm-a harvest (r244 landed-marker law): "
                    "relaunch 01:50:09 on fixed runner sha 5c3a822f193d3922 "
                    "clean burn -> landed 01:58:30; raw 5000 (A500/B4500) -> "
                    "exclusion hits 1 (W5-B-0670 dual_momentum = "
                    "w2_screen_survivor stop-gate-vol-yang-none semantic "
                    "completion, disclosed) -> dedup distinct 3926 (prereg "
                    "sec.5 band [2800,4600] PASS; raw-to-dedup 4999->3926), "
                    "zero engine cells burned, single-shot marker intact; "
                    "yang faces {first_yang 1894, none 2032}; gate faces "
                    "{bear 1249, bull 1355, none 1322}; grammar sha16 "
                    "29720178c39425de anchored; TRIAL_GRAMMAR_LEDGER wave-5 "
                    "row runner-written at consume 01:58:30; next slice = "
                    "W5 screen-prep PASS r408 02:07 (16s; panel 48/48, "
                    "anchors 6/6 faithful, census L {1253,1127,875}, "
                    "leg-L disclosure faces G-VOL 594calm/518wild + G-YANG "
                    "819yang/812red structural-only) + TRIAL-LABOR-W5-SCREEN "
                    "pool entry direct-ready same commit (CPU pool face "
                    "per prereg sec.0)")

assert "TRIAL-LABOR-W5-SCREEN" not in ents, "screen entry already exists"
screen = {
    "id": "TRIAL-LABOR-W5-SCREEN",
    "ticket_ref": ("T-2026-09-29-114 WAVE-5 screen slice (CEO "
                   "O-2026-09-27-2245 thousand-trader order + "
                   "O-2026-09-27-2250 standing law; prereg FROZEN r405 "
                   "commit 26bab31b + seeds R250 same-commit "
                   "20302000/20302500/20303000; runner full-slice built "
                   "r406 selftest 73/73 hermetic + fix-first 777e2b5e "
                   "(yang open-face reindex + probe-basis verbatim "
                   "cross-table) production-validated through real-fire "
                   "landing 01:58:30 n=3926 distinct; screen-prep PASS "
                   "r408 02:07)"),
    "prereg_ref": ("research/TRIAL_LABOR_W5_PREREG.md FROZEN sec.3 s2 "
                   "(each distinct candidate = legacy-axis leg-L 6m "
                   "full-history backtest, W1 13bp base, T+1, "
                   "initial-stop + regime-gate + VOL-gate + NEW "
                   "YANG-gate faces carried per cell, frozen composition "
                   "order filter->timing->GATE->VOL->STOP->YANG per "
                   "MSG-0440 E1 mapping; beat6m >= passive over 1253 "
                   "frozen starts; null family K=200 eight-tuple axis "
                   "R/X/S/T/STOP/GATE/VOL/YANG seed trial_labor_w5_scrnull"
                   "=20302500; survival line = beat6m > null p95 "
                   "program-frozen via tl2._finalize_math import = "
                   "W2/W3/W4 identical law; finalize refuses missing "
                   "cells, checkpoint retained; ledger TRIAL_LAB_W5_SCREEN"
                   " batch = distinct 3926 + 200 nulls literal per "
                   "sec.3; products w5_screen.json + w5_screen_cells.csv "
                   "+ gate x vol x yang segmented survival stats per "
                   "prereg sec.6)"),
    "runner": "scripts/trial_labor_w5.py",
    "runner_args": ["screen", "--shard", "0", "--shards", "1"],
    "lane_owner": None,
    "priority": 1,
    "status": "ready",
    "entered_at": "2026-09-29 02:08:30",
    "workers_plan": {
        "workers": ("worker_cap() pool BelowNormal (W4-SCREEN live: 12 "
                    "workers bm-c; 32-core bm-c: <=25; 32-core bm-a: "
                    "<=25)"),
        "priority": "BelowNormal",
        "note": ("W3-SCREEN 3,752 cells 4.6min (r395) + W4-SCREEN 4,010 "
                 "cells ~12.3min 12-workers (r165) same cell weight -> "
                 "4,126 cells (3,926 distinct + 200 nulls) est "
                 "minutes-level pool batch; per-cell jsonl checkpoint "
                 "cross-kill resume (W1 law); prereg sec.0 worst-case "
                 "anchor stands as ceiling"),
    },
    "data_gates": ("GATES ALL GREEN (direct-ready r408, W1/W2/W3/W4-"
                   "SCREEN lineage): (1) TRIAL-LABOR-W5-GENERATE done -- "
                   "landed 01:58:30 w5_candidates.json n=3926 single-shot "
                   "completion marker in-repo this commit; (2) screen-prep "
                   "PASS -- results/trial_labor_w5/prep_state.json r408 "
                   "02:07 gates G-PANEL 48/48 + G-ANCHOR registered-six "
                   "replay faithful on the W5 eight-tuple identity face + "
                   "G-CENSUS leg-L {1253,1127,875} frozen-match + "
                   "G-EXCLUDE hits disclosed {A:0,B:1} + G-VOL raw-face "
                   "anchors {first-valid 519, calm 1523, wild 1441} + "
                   "G-YANG raw-face anchors {yang 1751, yang&bull 962, "
                   "red&bear 914} both re-verified live fail-closed; (3) "
                   "SCREEN = CPU pool face per prereg sec.0 (RAM "
                   "zero-occupancy disposition -- no waiting-flip gate "
                   "needed; IN-RUNNER fail-closed exit 2: prep/candidates/"
                   "grammar absent, grammar sha != 29720178c39425de "
                   "refuse, tl2._ram_gate_gb 4GB three-sample honest "
                   "refuse). After all shards: screen-finalize = separate "
                   "round work (ledger TRIAL_LAB_W5_SCREEN + w5_screen"
                   ".json + w5_screen_cells.csv; survivors feed the "
                   "W5-JUDGE face next slice -- W2 r362 / W3 r150 / W4 "
                   "r165 precedent)"),
    "shards": [{
        "key": "screen-0of1",
        "status": "ready",
        "owner": None,
        "owner_since": None,
        "checkpoint": ("results/trial_labor_w5/checkpoint/"
                       "screen_shard_0of1.jsonl (append-per-cell; "
                       "finalize gate refuses missing cells)"),
        "note": ("single shard; worker_cap() parallelism inside the shard "
                 "(W2/W3/W4-SCREEN same shape); multi-shard i%shards "
                 "split legal per shard law on partial claim"),
    }],
    "entered_by": "bm-a r408",
    "worker_class": "self-contained",
}
pool["entries"].append(screen)

tmp = POOL + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(pool, fh, ensure_ascii=False, indent=1)
os.replace(tmp, POOL)

# verify round-trip
back = json.load(open(POOL, encoding="utf-8"))
g2 = {e["id"]: e for e in back["entries"]}["TRIAL-LABOR-W5-GENERATE"]
s2 = {e["id"]: e for e in back["entries"]}["TRIAL-LABOR-W5-SCREEN"]
print("generate:", g2["status"], g2["shards"][0]["status"],
      g2["done_at"], g2["result_ref"])
print("screen:", s2["status"], s2["shards"][0]["status"],
      s2["entered_at"])
print("n_entries:", len(back["entries"]))
