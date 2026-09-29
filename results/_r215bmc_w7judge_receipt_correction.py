# -*- coding: utf-8 -*-
"""r215 bm-c addendum: W7-JUDGE data_gates factual correction.

The r215 lane_owner amendment receipt claimed "physical-only-bm-b" for
the Money02 t18_deep_panel cache. WRONG: bm-a received the t18 cache in
the r85 T-22 transfer (48/48 dual-manifest full-hash, HANDOVER r85) and
just completed the W7-JUDGE burn on it (pool_worker_ledger 190.3s
exit 0, claim closed outcome=ok, commit 0354aace). True face: t18 cache
physically on {bm-a, bm-b}; bm-c cache-less (r214 takeover instant
P5C-GATE exit verified). lane_owner=bm-b VALUE retained (harmless:
shard complete by bm-a; residual re-burn would go to bm-b = valid
host; lane guard gates claims only, not bm-a's harvest/finalize
control-plane actions).
"""
import json
import os

POOL = "results/runnable_pool.json"
pool = json.load(open(POOL, encoding="utf-8-sig"))

ent = [x for x in pool["entries"] if x["id"] == "TRIAL-LABOR-W7-JUDGE"][0]
assert ent["lane_owner"] == "bm-b", ent["lane_owner"]
assert "r215 bm-c lane_owner amendment null->bm-b" in ent["data_gates"]

# evidence anchors
led = open("results/pool_worker_ledger.jsonl", encoding="utf-8").read()
assert '"machine_id": "bm-a", "entry": "TRIAL-LABOR-W7-JUDGE"' in led \
    and '"duration_sec": 190.3' in led and '"exit_code": 0' in led
cf = json.load(open("results/pool_claims/TRIAL-LABOR-W7-JUDGE/"
                    "judge-0of1.bm-a.json", encoding="utf-8"))
assert cf["state"] == "closed" and cf["outcome"] == "ok" \
    and cf["exit_code"] == 0, cf
print("anchors OK: bm-a ledger 190.3s exit 0 + claim closed ok")

ent["data_gates"] += (
    " | r215 addendum bm-c FACTUAL CORRECTION of the amendment receipt "
    "above: 'physical-only-bm-b' premise WRONG -- bm-a received the t18 "
    "deep-panel cache in the r85 T-22 transfer (48/48 dual-manifest "
    "full-hash) and completed THIS shard's burn on it 11:52:13-11:55:24 "
    "190.3s 32-core exit 0 (pool_worker_ledger + claim closed outcome=ok "
    "commit 0354aace); true cache face = {bm-a, bm-b}, bm-c cache-less "
    "(r214 takeover instant P5C-GATE exit verified locally). lane_owner="
    "bm-b VALUE retained harmless: shard complete by bm-a, residual "
    "re-burn (if artifact verification fails) to bm-b = valid host; lane "
    "guard gates claims only, never bm-a's harvest/done-flip + finalize "
    "control-plane actions")

tmp = POOL + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(pool, f, ensure_ascii=False, indent=1)
os.replace(tmp, POOL)

pool2 = json.load(open(POOL, encoding="utf-8-sig"))
j2 = [x for x in pool2["entries"] if x["id"] == "TRIAL-LABOR-W7-JUDGE"][0]
assert j2["lane_owner"] == "bm-b" and "FACTUAL CORRECTION" in j2["data_gates"]
assert j2["shards"][0]["owner"] == "bm-c"        # stamp untouched still
print("re-read verify OK: correction appended, lane_owner=bm-b kept, "
      "shard stamp intact")
