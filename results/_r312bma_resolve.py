"""R312 bm-a resolve: results/runnable_pool.json UU (push-rejection rebase).

Both sides ran the r314 evidence-gate flip in the same window (bm-b flipped
its machine-completed shards; bm-a flipped the 14 it burned in-round).
File shape: {"entries": [ {id, status, shards:[{key,status,owner,...}], ...} ]}.
Zero-loss recipe (absorptive done-union, per shard then per entry):
  * per entry id: if either side has status "done" -> done; shard fields taken
    from the side that has done (the completing machine's record).
  * both-ready -> keep ours (identical science face; owner fields may differ by
    transient autofill claim -- pool owner fields are non-authoritative hints,
    the flip evidence gate is the authority).
  * entry present in only one side -> keep it (union of ids).
Verification: json.loads pass; ids superset of both sides; every entry with
done on either side is done in the output; count report printed.
Stage blobs read via git cat-file (bytes), per SKILL read-face discipline.
"""
import json
import subprocess
import sys

ROOT = __file__.rsplit("\\", 2)[0]


def stage_blob(stage):
    out = subprocess.run(
        ["git", "cat-file", "blob", stage],
        cwd=ROOT, capture_output=True, check=True,
    ).stdout
    return json.loads(out.decode("utf-8"))


def pool_of(blob):
    return blob.get("entries", blob.get("pool", []))


ours = pool_of(stage_blob(":2:results/runnable_pool.json"))
theirs = pool_of(stage_blob(":3:results/runnable_pool.json"))
base = pool_of(stage_blob(":1:results/runnable_pool.json"))

by_id_ours = {e["id"]: e for e in ours}
by_id_theirs = {e["id"]: e for e in theirs}

merged = []
report = []
for eid in sorted(set(by_id_ours) | set(by_id_theirs)):
    o = by_id_ours.get(eid)
    t = by_id_theirs.get(eid)
    if o and t:
        if t.get("status") == "done" and o.get("status") != "done":
            merged.append(t)
            report.append((eid, "done<-theirs"))
        elif o.get("status") == "done" and t.get("status") != "done":
            merged.append(o)
            report.append((eid, "done<-ours"))
        else:
            # both same status; field-level shard union for safety
            m = dict(o)
            os_by_key = {s["key"]: s for s in o.get("shards", [])}
            ts_by_key = {s["key"]: s for s in t.get("shards", [])}
            shards = []
            for k in sorted(set(os_by_key) | set(ts_by_key)):
                so, st = os_by_key.get(k), ts_by_key.get(k)
                if so and st:
                    if st.get("status") == "done" and so.get("status") != "done":
                        shards.append(st)
                    else:
                        shards.append(so)
                else:
                    shards.append(so or st)
            m["shards"] = shards
            merged.append(m)
            report.append((eid, "both-" + str(o.get("status"))))
    else:
        merged.append(o or t)
        report.append((eid, "one-side"))

# stable ordering: keep ours order then theirs-only additions
order = {e["id"]: i for i, e in enumerate(ours)}
merged.sort(key=lambda e: order.get(e["id"], 10**6 + hash(e["id"]) % 10**5))

out = {"entries": merged}
blob_top_ours = stage_blob(":2:results/runnable_pool.json")
if isinstance(blob_top_ours, dict):
    for k, v in blob_top_ours.items():
        if k not in ("entries", "pool"):
            out[k] = v

path = ROOT + "\\results\\runnable_pool.json"
with open(path, "w", encoding="utf-8", newline="") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
    f.write("\n")

# verify
chk = json.load(open(path, encoding="utf-8"))
entries = chk.get("entries", [])
done_n = sum(1 for e in entries if e.get("status") == "done")
other = [e["id"] for e in entries if e.get("status") != "done"]
assert len(entries) >= max(len(ours), len(theirs)), "id union lost entries"
for e in entries:
    src = by_id_ours.get(e["id"])
    dst = by_id_theirs.get(e["id"])
    if (src and src.get("status") == "done") or (dst and dst.get("status") == "done"):
        assert e.get("status") == "done", f"done-absorb violated for {e['id']}"
print(f"resolved entries={len(entries)} done={done_n} non-done={other}")
for r in report:
    print(" ", r[0], "->", r[1])
