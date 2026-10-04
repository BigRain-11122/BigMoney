# -*- coding: utf-8 -*-
"""r682 bm-a: inspect runnable_pool.json HEAD vs MERGE_HEAD delta (per-face,
r474 law: owner_since newer-wins, never whole-file replay)."""
import json, subprocess, sys, io
sys.stdout =io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def show(ref):
    r = subprocess.run(["git", "show", f"{ref}:results/runnable_pool.json"], capture_output=True)
    return json.loads(r.stdout.decode("utf-8"))

h = show("HEAD")
m = show("MERGE_HEAD")
he = {e["id"]: e for e in h["entries"]}
me = {e["id"]: e for e in m["entries"]}
print("HEAD entries:", len(he), "MERGE_HEAD entries:", len(me))
print("ids only in HEAD:", sorted(set(he) - set(me)))
print("ids only in MERGE_HEAD:", sorted(set(me) - set(he)))
diffs = []
for k in sorted(set(he) & set(me)):
    a, b = he[k], me[k]
    d = []
    for f in ("status",):
        if a.get(f) != b.get(f):
            d.append((f, a.get(f), b.get(f)))
    sa = {s.get("key"): s for s in a.get("shards", [])}
    sb = {s.get("key"): s for s in b.get("shards", [])}
    for sk in sorted(set(sa) | set(sb)):
        x, y = sa.get(sk), sb.get(sk)
        if x is None or y is None:
            d.append((sk, "shard-only-one-side", x, y))
        else:
            for f in ("status", "owner", "owner_since"):
                if x.get(f) != y.get(f):
                    d.append((f"{sk}.{f}", x.get(f), y.get(f)))
    if d:
        diffs.append((k, d))
for k, d in diffs:
    print("ENTRY", k)
    for row in d:
        print("   ", row)
print("total diff entries:", len(diffs))
