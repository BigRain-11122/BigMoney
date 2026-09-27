"""r369 bm-a resolver #2: results/runnable_pool.json (pool-entry-done-union).

Ours (origin/upstream) = 88 entries incl. bm-c's 4 new MASS-TRIAL-W1-JUDGE
shards; theirs (my replayed lane-fix commit) = 84 entries with the V2-P1
lane fix (lane_owner=bm-b, stale bm-a claim cleared).

Canon: per-entry union; one-side-only entries preserved (the 4 MASS-TRIAL
shards from ours); shared entries three-way merged (ours==base -> take
theirs' intentional change; theirs==base -> keep ours; both-changed -> done
absorption on shards + flag). Zero-loss assert: entry count == |id union|,
V2-P1 lane_owner==bm-b, owner cleared.
"""
import json
import subprocess
import sys

PATH = "results/runnable_pool.json"


def side(s):
    raw = subprocess.run(["git", "show", f":{s}:{PATH}"],
                         capture_output=True, check=True).stdout
    return json.loads(raw.decode("utf-8-sig"))


ours, theirs, base = side(2), side(3), side(1)
om = {e["id"]: e for e in ours["entries"]}
tm = {e["id"]: e for e in theirs["entries"]}
bm = {e["id"]: e for e in base["entries"]}

merged, flags = [], []
for eid in sorted(om.keys() | tm.keys()):
    o, t, b = om.get(eid), tm.get(eid), bm.get(eid)
    if o is not None and t is None:
        merged.append(o)
        continue
    if t is not None and o is None:
        merged.append(t)
        continue
    # both present: field-level three-way
    out = dict(o)
    oj, tj, bj = (json.dumps(o, sort_keys=True), json.dumps(t, sort_keys=True),
                  json.dumps(b, sort_keys=True) if b else None)
    if oj == tj:
        merged.append(o)
        continue
    if bj is not None and oj == bj:
        merged.append(t)          # only mine changed -> take mine
        continue
    if bj is not None and tj == bj:
        merged.append(o)          # only origin changed -> keep origin
        continue
    # both changed differently -> done-absorption merge
    shards = {}
    for sk in {s["key"] for s in o.get("shards", [])} | \
              {s["key"] for s in t.get("shards", [])}:
        so = next((s for s in o.get("shards", []) if s["key"] == sk), None)
        st = next((s for s in t.get("shards", []) if s["key"] == sk), None)
        if so and st:
            if so.get("status") == "done":
                shards[sk] = so          # done absorbs (r312)
            elif st.get("status") == "done":
                shards[sk] = st
            else:
                shards[sk] = st if (st.get("owner_since") or "") > \
                    (so.get("owner_since") or "") else so
        else:
            shards[sk] = so or st
    out["shards"] = [shards[k] for k in sorted(shards)]
    merged.append(out)
    flags.append(eid)

if flags:
    print("BOTH-CHANGED entries (done-absorbed):", flags)

merged.sort(key=lambda e: (e.get("priority", 9), e.get("entered_at", "")))
out = dict(ours)
out["entries"] = merged

v2 = [e for e in merged if e["id"] == "DECISION-CHAIN-V2-P1"][0]
assert v2["lane_owner"] == "bm-b", v2["lane_owner"]
assert v2["shards"][0]["owner"] is None
assert len(merged) == len(om.keys() | tm.keys()), (len(merged), len(om.keys() | tm.keys()))
mass = [e["id"] for e in merged if e["id"].startswith("MASS-TRIAL")]
assert len(mass) == 4, mass

with open(PATH, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
v = json.load(open(PATH, encoding="utf-8"))
assert len(v["entries"]) == len(merged)
print(f"WROTE {PATH}: entries={len(v['entries'])} "
      f"(ours={len(om)} theirs={len(tm)} union={len(om.keys() | tm.keys())}) "
      f"V2-P1 lane={v2['lane_owner']} owner={v2['shards'][0]['owner']} "
      f"MASS-TRIAL shards={len(mass)}")
