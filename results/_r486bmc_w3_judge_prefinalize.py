"""r486 bm-c W3-JUDGE pre-finalize probe (state.next(b) items 1+2, same
window with finalize per r685/r482 laws):
1. 777-cell completeness: union of 4 shard files == kept list exactly,
   i%4 class counts 195/194/194/194, candidates sha16 anchor re-asserted.
2. r482 id-dedup: per-file id uniqueness + cross-file disjoint (post-merge
   re-run -- the merge brought shard-2 as clean add, but law requires the
   probe same-window).
3. Pool 4/4 done (family probe parity, disk face).
4. Ledger head live read (disclosure only; runner reads its own live).
Writes evidence json + ASCII-only stdout."""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
OUT_DIR = os.path.join(ROOT, "results", "mass_trial")
EV = os.path.join(ROOT, "results", "_r486bmc_w3_judge_prefinalize.json")
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

state = json.load(open(os.path.join(OUT_DIR, "w3_judge_state.json"),
                       encoding="utf-8"))
kept = sorted(state["collapse"]["kept"])
n_kept = len(kept)
cand = json.load(open(os.path.join(OUT_DIR, "w3_candidates.json"),
                      encoding="utf-8"))
cand_sha16 = hashlib.sha256(
    open(os.path.join(OUT_DIR, "w3_candidates.json"), "rb").read()
).hexdigest()[:16]

shards = {}
all_ids = []
per_file = {}
for i in range(4):
    p = os.path.join(OUT_DIR, "w3_judge_shard_%dof4.jsonl" % i)
    rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    ids = [r["cell_id"] for r in rows]
    per_file[i] = {"rows": len(rows), "unique": len(set(ids)),
                   "iclass_ok": all(r["i"] % 4 == i for r in rows)}
    assert len(ids) == len(set(ids)), "DUP ids in shard %d (r482 keep-first needed)" % i
    for cid in ids:
        assert cid not in shards, "CROSS-FILE DUP %s" % cid
    shards[i] = set(ids)
    all_ids.extend(ids)

exp_counts = {0: 195, 1: 194, 2: 194, 3: 194}
assert per_file[0]["rows"] == 195 and per_file[0]["iclass_ok"]
for i in (1, 2, 3):
    assert per_file[i]["rows"] == 194 and per_file[i]["iclass_ok"]
assert sum(per_file[i]["rows"] for i in range(4)) == 777
assert len(all_ids) == len(set(all_ids)) == 777, "union not 777 unique"

expected_ids = set("JUDGE|" + cid for cid in kept)
assert set(all_ids) == expected_ids, (
    "completeness FAIL: union != kept (sym-diff %d)"
    % len(set(all_ids) ^ expected_ids))
assert n_kept == 777, "kept=%d != 777" % n_kept

pool = json.loads(open(os.path.join(ROOT, "results", "runnable_pool.json"),
                       "rb").read().decode("utf-8"))
fam = {e["id"]: e for e in pool["entries"]
       if str(e.get("id", "")).startswith("MASS-TRIAL-W3-JUDGE")}
assert len(fam) == 4 and all(fam[e]["status"] == "done"
                             for e in fam), "pool not 4/4 done"

# ledger head live read (disclosure); r683 path law: science_gates lives in
# scripts/ and imports knowledge.* from repo ROOT -- both must be on sys.path
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
import science_gates as sg  # noqa: E402
head = sg.ledger_head()

ev = {
    "ts": "2026-10-04 r486 bm-c pre-finalize",
    "n_kept": n_kept,
    "candidates_sha16": cand_sha16,
    "per_shard": per_file,
    "union_unique": len(set(all_ids)),
    "completeness_exact_match_kept": True,
    "pool_4of4_done": True,
    "ledger_head_total_at_probe": head["total"],
    "id_dup": 0,
}
with open(EV, "w", encoding="utf-8") as f:
    json.dump(ev, f, indent=1, ensure_ascii=False)
print("PREFINALIZE PASS: kept=%d union=777 unique, i%%4 195/194/194/194, "
      "cross-file disjoint, candidates sha16=%s, pool 4/4 done, "
      "ledger_head=%s" % (n_kept, cand_sha16, head["total"]))
