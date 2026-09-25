"""r220: register P-1e zoo IC batch into runnable_pool (prereg SS9 step-2).

House pattern = one entry per shard (BOND-PANEL-SHARD-* / WILD-S1-SHARD-*
precedent): autofill fires entry-level runner_args, so each shard gets its
own entry. lane_owner=bm-b frozen by prereg SS9 (machine-local p1c_stock
cache + turnover sidecar, r188 lane-pin law). Idempotent: skips ids already
present. Single-writer discipline: fresh read -> append -> atomic write.
"""
import json
import os
import time

POOL = "results/runnable_pool.json"
TS = time.strftime("%Y-%m-%d %H:%M:%S")

COMMON = {
    "ticket_ref": "T-2026-09-25-64 slice-5 consumption face (ASTYLE_ZOO "
                  "#85/#92/#93 rows) + F-04 claim MSG-20260926-0255-bm-b "
                  "(r219, commit 48163b47)",
    "prereg_ref": "research/shortline/P1E_ZOO_BEHAVIOR_IC.md (frozen r219):"
                  " N_eff=157 (7 computed + 150 nulls), evidence_cutoff "
                  "2026-09-22, seeds 67000..67149 (SEED_REGISTRY "
                  "p1e_zoo_behavior), recorded-v1 gates via p1c gates_v123",
    "runner": "scripts/p1e_ic_batch.py",
    "lane_owner": "bm-b",
    "priority": 1,
    "status": "ready",
    "entered_at": TS,
    "workers_plan": {
        "workers": 4,
        "priority": "BelowNormal",
        "note": "4 independent entries = the parallelism (P-1d mask-class "
                "null legs x3 + cells); each shard single-process "
                "numpy-vectorized serial-deterministic (O-20260923-1738); "
                "autofill 1 shard/tick/machine, lane bm-b only; est "
                "4-7min/shard per r219 probe timing (471 IC ~15-20min "
                "total split 4 ways); autofill sets BelowNormal on launch",
    },
    "data_gates": "in-runner: batch-pre equivalence gate (real-slice "
                  "_ic_series_fast vs composite_ic.ic_series <=1e-6, abort "
                  "exit 1) + turnover sidecar presence/shape/meta asserts "
                  "(bars turnover col all-NaN never consumed) + idempotent "
                  "checkpoints (exists=skip, kill/restart safe) + finalize "
                  "fail-closed (missing/error part = exit 2 zero artifacts, "
                  "r217) + selftest 9-leg/24-check PASS pre-pooling (r220); "
                  "finalize itself is harvest-round science work, NOT in "
                  "pool (pool-flip-is-round-work r203)",
}

SHARDS = [
    ("P1E-NULLS-MCLOSE",
     ["run-nulls", "--class", "M_close"],
     "p1e-nulls-mclose",
     "K=50 white-noise nulls, mask class M_close (close finite, terrified "
     "inputs), seeds 67000..67049; est ~6-7min (150 IC @ ~1.9s + panel "
     "load close-only)",
     "results/shortline/p1e_nulls_M_close.json (n_nulls==50, per-h p95/p50)"),
    ("P1E-NULLS-MCLOSETR",
     ["run-nulls", "--class", "M_close_tr"],
     "p1e-nulls-mclosetr",
     "K=50 nulls, mask class M_close_tr (close & tr finite, stv+coin_team "
     "inputs), seeds 67050..67099; est ~6-7min (loads close+tr sidecar)",
     "results/shortline/p1e_nulls_M_close_tr.json (n_nulls==50)"),
    ("P1E-NULLS-MARC",
     ["run-nulls", "--class", "M_arc"],
     "p1e-nulls-marc",
     "K=50 nulls, mask class M_arc (close & tr & vwap finite, #93 family "
     "inputs), seeds 67100..67149; est ~6-7min (loads close+tr+vwap)",
     "results/shortline/p1e_nulls_M_arc.json (n_nulls==50)"),
    ("P1E-CELLS",
     ["run-cells"],
     "p1e-cells",
     "7 members x 3 horizons (h5/h10/h20, h10 primary judgement) IC via "
     "_ic_series_fast on frozen p1e_factors constructors; est ~4-5min "
     "(constructors ~53s + 21 IC + close/open/tr/vwap load)",
     "results/shortline/p1e_partial/<factor>.json x7 (status==ok)"),
]

with open(POOL, encoding="utf-8") as f:
    pool = json.load(f)
entries = pool.get("entries", [])
have = {e.get("id") for e in entries}
added = 0
for eid, args, key, note, ckpt in SHARDS:
    if eid in have:
        print(f"skip {eid}: already present")
        continue
    ent = dict(COMMON)
    ent.update({
        "id": eid,
        "runner_args": args,
        "shards": [{
            "key": key,
            "status": "ready",
            "owner": None,
            "owner_since": None,
            "checkpoint": ckpt + " -- session flips shard->done on harvest "
                                 "round (pool-flip-is-round-work r203)",
            "note": note,
        }],
    })
    entries.append(ent)
    added += 1
    print(f"added {eid} ({key})")
pool["entries"] = entries
pool["updated_at"] = TS
json.loads(json.dumps(pool))            # verify-parse before write (r185)
with open(POOL, "w", encoding="utf-8") as f:
    json.dump(pool, f, indent=2, ensure_ascii=False)
print(f"pool updated: +{added} entries, total {len(entries)}")
