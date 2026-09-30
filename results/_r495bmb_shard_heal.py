# r495 bm-b: W9-W13 JUDGE ghost shard heal (ready->done), r489 3a318a952 precedent (shared face only)
# Evidence: entry layer done + judge products in-tree (w9 243/w10 283/w11 229/w12 188/w13 99 cells).
# r489 law: entry+shard flip atomic; these are pre-fix residue (shard never landed).
import json, sys

PATH = "results/runnable_pool.json"
TARGETS = ["TRIAL-LABOR-W%d-JUDGE" % w for w in (9, 10, 11, 12, 13)]

pool = json.load(open(PATH, encoding="utf-8"))
flips = 0
for e in pool.get("entries", []):
    if e.get("id") in TARGETS:
        assert e.get("status") == "done", (e.get("id"), e.get("status"))
        for s in e.get("shards", []):
            if s.get("status") == "ready":
                s["status"] = "done"
                flips += 1
assert flips == 5, flips

out = json.dumps(pool, ensure_ascii=False, indent=2).replace("\n", "\r\n")
with open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(out)
print("flipped=%d targets=%s" % (flips, ",".join(TARGETS)))
