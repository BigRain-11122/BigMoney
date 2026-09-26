"""R296 bm-a: T-85 s2/s3 FUSION_GRID_P1 runner built + pool entry (R99 chain step 3).

Atomic single-writer updates:
  1. fleet/tasks/T-2026-09-26-85-P1.json  + progress_r296 field
  2. results/runnable_pool.json          + FUSION-GRID-P1 ready entry
     (workers_plan + shards per O-2130 + R293-E1 picker law)
"""
import json
import os
import time

TS = time.strftime("%Y-%m-%d %H:%M:%S")

# ---- 1. ticket progress field
tp = "fleet/tasks/T-2026-09-26-85-P1.json"
t = json.load(open(tp, encoding="utf-8-sig"))
t["progress_r296"] = (
    "s2/s3 runner scripts/fusion_grid_p1.py BUILT per frozen prereg 7cf87f13 (R99 "
    "chain: freeze R295 -> build R296 -> pool -> burn -> harvest): selftest 22/22 "
    "(A regime equivalence = fast dims vs market_regime bench_dims/breadth_dims "
    "truncated on 21 sampled dates + last bench day vs probe() dims, zero mismatch; "
    "B synthetic-member constructive 12 legs incl warmup/drift/DEDUP-collapse/"
    "INV_MDD-floor/cap-ladder/hold-shares; C null determinism + size law + simplex "
    "replay) + real-data gate PASS (members 32 / bars 1631 common grid 2020-01-02.."
    "2026-09-22 lockbox / bench 09-24 / core48 ok / regime v3 EXACT shares GREEN754 "
    "RED141 ORANGE22 YELLOW714 -- probe F4 was the approximate face, exact module "
    "recompute governs, divergence disclosed per prereg sec.2 runner-exact clause; "
    "66 rebalance points, cell window 1379 bars, 0.3s). Pool entry FUSION-GRID-P1 "
    "ready this round; burn via autofill next tick; harvest three-piece (prereg "
    "s7/s8 + gate_attrition r248 + post_review stable anchors) next round on landing."
)
with open(tp + ".tmp", "w", encoding="utf-8") as f:
    json.dump(t, f, ensure_ascii=False, indent=1)
os.replace(tp + ".tmp", tp)

# ---- 2. runnable_pool entry (fresh read right before write; single-writer atomic)
pp = "results/runnable_pool.json"
p = json.load(open(pp, encoding="utf-8-sig"))
if any(e.get("id") == "FUSION-GRID-P1" for e in p.get("entries", [])):
    print("pool already has FUSION-GRID-P1 -- no-op")
else:
    entry = {
        "id": "FUSION-GRID-P1",
        "ticket_ref": ("T-2026-09-26-85-P1 s2/s3 (CEO O-20260926-2320 24h-quench; "
                       "claimed bm-a R277; F-04 MSG-20260927-0515-bm-a declared R295 "
                       "before freeze commit; prereg frozen R295 7cf87f13, runner "
                       "built+gated R296 same cadence)"),
        "prereg_ref": ("research/FUSION_GRID_P1_PREREG.md FROZEN 7cf87f13 precedes "
                       "runner build (R99) precedes ANY run; seed fusion_grid_p1="
                       "20275200 registered at freeze commit (R250 one-step); N bill "
                       "2045 = 45 judged cells + 2000 own-nulls; judged face x1 "
                       "(fusion-layer cost 0 disclosed); RANDOM_LARGE_SAMPLE_LAW "
                       "binding; selftest 22/22 hermetic + real-data gate PASS R296 "
                       "(members 32 / bars 1631 / bench 09-24 / core48 ok / regime "
                       "exact GREEN754 RED141 ORANGE22 YELLOW714, 0.3s)"),
        "runner": "scripts/fusion_grid_p1.py",
        "runner_args": ["run"],
        "lane_owner": None,
        "priority": 1,
        "status": "ready",
        "entered_at": TS,
        "data_gates": ("in-runner fail-closed SystemExit: navs 64 lines (x1/x2 32/32) "
                       "+ anchor_all_ok true + common grid 1631 bars to 2026-09-22 "
                       "lockbox + bench >= cutoff + core48 >=20 bars since 2020-01; "
                       "est 1-3min wall (nulls in-process vectorized + 45 cell jobs x "
                       "4 workers, pure-python bootstrap CI dominant); RAM floor "
                       "trivial (NAV matrices 32x1631 x2); idempotent no-op if "
                       "p1_results.json exists; FUSION_GRID_P1_REFINALIZE=1 only redo"),
        "workers_plan": {
            "workers": 4,
            "priority": "BelowNormal",
            "note": ("run_cells_parallel 4 workers per prereg sec.0 plan (45 cell "
                     "jobs: construction + stats + bootstrap CI + DSR in-worker; "
                     "regime/subset-derivation/nulls in-process); O-2130 multi-core law")
        },
        "shards": [
            {
                "key": "run-0of1",
                "status": "ready",
                "checkpoint": ("results/fusion_grid_p1/p1_results.json terminal + "
                               "regime_series.json + nulls_summary.json + cells/*.json; "
                               "idempotent no-op guard if p1_results.json exists"),
                "note": ("single-vehicle full batch (45 cells + nulls + gates + "
                         "ledger one-shot); takeover = stale owner >20min per fleet law")
            }
        ],
    }
    p["entries"].append(entry)
    p["updated_at"] = TS
    with open(pp + ".tmp", "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=1)
    os.replace(pp + ".tmp", pp)
    print("pool entry FUSION-GRID-P1 appended (ready, 1 shard, workers_plan 4 BelowNormal)")

# verify both files parse
for f in (tp, pp):
    json.load(open(f, encoding="utf-8-sig"))
print("json.loads verification PASS both files")
