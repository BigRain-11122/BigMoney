"""r306 bm-c: N1-W3 entry-layer dual-done flip (r489 phantom-face heal, r304 precedent).

Observing-round closure: all 12 PERPETUAL-N1-W3-SHARD-* entries have shard-layer
done but entry-layer still ready -- the r489 two-layer phantom face (daemon harvest
only ever lands the shard half). Guards: flip entry->done ONLY where every shard of
the entry is done (no-phantom), never revert done->ready (stale-ready-cannot-revert),
zero touches outside the 12 W3 ids. Pool format law (r289): indent2 + CRLF, write
then surgical diff assert.
"""
import json
import sys

SRC = "results/runnable_pool.json"
PREFIX = "PERPETUAL-N1-W3-SHARD-"

with open(SRC, "rb") as f:
    raw = f.read()
crlf = raw.count(b"\r\n")
lf_only = raw.count(b"\n") - crlf
assert crlf > 0 and lf_only == 0, f"pool line-ending probe: CRLF={crlf} LF-only={lf_only}"

pool = json.loads(raw.decode("utf-8"))
flipped, skipped = [], []
for e in pool["entries"]:
    if not str(e.get("id", "")).startswith(PREFIX):
        continue
    shards = e.get("shards", [])
    all_done = bool(shards) and all(s.get("status") == "done" for s in shards)
    if e.get("status") == "done":
        skipped.append((e["id"], "already-done"))
    elif all_done:
        e["status"] = "done"
        flipped.append(e["id"])
    else:
        skipped.append((e["id"], f"shards-not-all-done {[s.get('status') for s in shards]}"))

out = json.dumps(pool, ensure_ascii=False, indent=2).replace("\n", "\r\n")
with open(SRC, "w", newline="", encoding="utf-8") as f:
    f.write(out)

print("flipped:", len(flipped), sorted(flipped))
print("skipped:", skipped)
results = {"flipped": sorted(flipped), "skipped": skipped,
           "guards": "all-shards-done + no-revert + prefix-scoped"}
with open("results/_r306bmc_w3_entry_flips.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
sys.exit(0)
