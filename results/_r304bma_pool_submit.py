"""Pool submit: CN-MKTNEUTRAL-P1 (R304 bm-a lane, r301 shards-nonempty
contract). Idempotent: refuses if id already present."""
import json
import os
import time

POOL = os.path.join("results", "runnable_pool.json")
BID = "CN-MKTNEUTRAL-P1"

p = json.load(open(POOL, encoding="utf-8"))
if any(e.get("id") == BID for e in p["entries"]):
    print("already present, no-op")
    raise SystemExit(0)

entry = {
    "id": BID,
    "ticket_ref": "T-2026-09-26-87 s2 queue #5 market-neutral stock-quintile x IC constant-short (claimed bm-a; R99 order: prereg frozen 3c71ddb4 R303 -> runner built+gated R304; F-04 MSG-20260927-0750-bm-a declared R303)",
    "prereg_ref": "research/CN_MKTNEUTRAL_PREREG.md FROZEN 3c71ddb4 precedes runner build (R99) precedes ANY run; seed cn_mkneutral_p1=20279300 registered at freeze commit R303, band 20279300..20281300 construction-clean; N bill 2004 = 4 judged cells x1 + 2000 own-nulls; judged face x2 (V2 components + futures per-lot doubled); RANDOM_LARGE_SAMPLE_LAW binding; selftest 42/42 hermetic R304 (B7b contract leg per r297 + hedge machinery synthetic asserts: beta OLS/caps/fallback, lots rounding+sign, margin budget gate, blocked/absent rebalances, roll-day proxy, NAV identity vs independent hand loop, cost twins pointwise-equal) + real-data gate PASS R304 (universe 3106 exact + skip ledger == sector probe + IC 2353 rows first/last exact + cutoff truncation 2 bars + joint window 2352d + K=118, 28.9s)",
    "runner": "scripts/cn_mkneutral_p1.py",
    "runner_args": ["run"],
    "lane_owner": None,
    "priority": 1,
    "status": "ready",
    "entered_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    "data_gates": "in-runner fail-closed exit 2: bars census 5222 + cache meta stamp == actual 2026-09-23 18:12:59 (r299 kenglu) + crosscheck _r299bma 0-mismatch in place + universe re-derive 3106 + skip ledger == frozen sector probe (identical formula+inputs) + IC rows 2353 + IC first/last bar {2017-01-17, 2026-09-24} + cutoff truncation + joint window end bars present; est 30-120min wall (vectorized numpy: panel load ~29s + 4 cells x2 faces sim + 8000 own-null draws (beta-OLS random baskets) + Sobol 500 x1 + census/vstarts/robust legs); RAM floor 16GB (peak ~1GB: close_u f64 ~61MB + amt slice + adv/slip 118x3106); idempotent no-op if results/cn_mkneutral/p1_results.json exists (CN_MKTNEUTRAL_P1_REFINALIZE=1 only redo)",
    "shards": [
        {
            "key": "mkneutral-0of1",
            "status": "ready",
            "checkpoint": "results/cn_mkneutral/cells/<cell>_<face>.json|npy (4 cells x x1/x2) + nulls/<cell>_shard*.npy x8 per cell + sobol/shard*.npy x10; terminal marker = results/cn_mkneutral/p1_results.json (idempotent no-op if exists); est 30-120min wall single-vehicle",
            "note": "single-vehicle full batch (4 judged cells + 2000 own-nulls + Sobol 500 x1 descriptive + census legs, one-shot runner); takeover = stale owner >20min per fleet law",
            "owner": None,
            "owner_since": None,
        }
    ],
}
p["entries"].append(entry)
p["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
with open(POOL + ".tmp", "w", encoding="utf-8") as fh:
    json.dump(p, fh, ensure_ascii=False, indent=1)
os.replace(POOL + ".tmp", POOL)
# self-verify (r301 pool-contract law: shards non-empty, ready present)
q = json.load(open(POOL, encoding="utf-8"))
e = [x for x in q["entries"] if x["id"] == BID][0]
assert len(e["shards"]) >= 1 and e["shards"][0]["status"] == "ready"
assert e["status"] == "ready"
print("pool submit ok:", BID, "| entries:", len(q["entries"]),
      "| shard:", e["shards"][0]["key"])
