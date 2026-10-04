"""r486 bm-c post-merge pool integrity probe: verify BOTH parallel surgical
flips survived the ort auto-merge of runnable_pool.json (mine SHARD-3 +
bm-b SHARD-1, different entry regions), fund-trio keepalive face intact,
entries count stable. Run BEFORE push (r678 parallel-surgery risk face)."""
import hashlib
import json

POOL = "results/runnable_pool.json"
d = json.loads(open(POOL, "rb").read().decode("utf-8"))
entries = d["entries"]
assert len(entries) == 376, "entries=%d" % len(entries)
fam = {e["id"]: e for e in entries
       if str(e.get("id", "")).startswith("MASS-TRIAL-W3-JUDGE")}
assert len(fam) == 4, sorted(fam)

exp = {
    "MASS-TRIAL-W3-JUDGE-SHARD-0": ("done", "done", "bm-c"),
    "MASS-TRIAL-W3-JUDGE-SHARD-1": ("done", "done", "bm-b"),
    "MASS-TRIAL-W3-JUDGE-SHARD-2": ("done", "done", "bm-a"),
    "MASS-TRIAL-W3-JUDGE-SHARD-3": ("done", "done", "bm-c"),
}
for eid, (est, sst, owner) in exp.items():
    e = fam[eid]
    s = e["shards"][0]
    assert e["status"] == est, (eid, e["status"], est)
    assert s["status"] == sst, (eid, s["status"], sst)
    assert s.get("owner") == owner, (eid, s.get("owner"), owner)
    assert s.get("done_at") and s.get("harvested_by"), eid
    if owner == "bm-c":
        # r485/r486 recipe sets entry-level done_by/done_at (own face, assert)
        assert e.get("done_by") and e.get("done_at"), eid
    else:
        # sibling owners' flip style: two-layer law = both statuses done;
        # entry-level done_by is owner's face (r626d-ii no re-stamp) -- print
        print("NOTE %s entry done_by=%r done_at=%r (owner %s style)"
              % (eid, e.get("done_by"), e.get("done_at"), owner))

# SHARD-2 provenance (bm-a flipped 17:29:26, on origin, merged)
s2 = fam["MASS-TRIAL-W3-JUDGE-SHARD-2"]["shards"][0]
print("SHARD-2 (bm-a flipped): done_at=%s harvest=%s"
      % (s2.get("done_at"), s2.get("harvest_claim")))
assert s2.get("done_at") and s2.get("harvested_by") == "bm-a"

# fund-trio keepalive face intact (3 NULLS entries, bm-b owner, fresh ts)
trio = 0
for e in entries:
    if str(e.get("id", "")).startswith(("FUND-VALUE-P1-NULLS",
                                        "FUND-QUALITY-P1-NULLS",
                                        "FUND-DIVLOWVOL-P1-NULLS")):
        trio += 1
        for s in e.get("shards", []):
            if s.get("owner") == "bm-b" and s.get("owner_since"):
                assert s["owner_since"] > "2026-10-04 17:", (e["id"], s.get("owner_since"))
print("fund-trio NULLS entries=%d (bm-b keepalive owner_since fresh 17:xx PASS)" % trio)

print("sha16(pool)=%s" % hashlib.sha256(open(POOL, "rb").read()).hexdigest()[:16])
print("POOL INTEGRITY PASS: 4/4 done (0,3 bm-c / 1 bm-b / 2 bm-a), entries=376")
