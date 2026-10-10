"""r956 bm-a: re-assert W17 handover terminal state post-union (O-18261010-1825 sec.1).

Union (newer-wins) mechanically restored bm-c keepalive timestamps (19:04:03)
over the 18:59:43 transfer. CEO order O-20261010-1825 sec.1 + MSG-1900 evidence
chain (zero product + stale heartbeat since 15:15, film-chain CEO priority)
authorize bm-a takeover; this completes the replayed transfer commit's intent.
Surgical per pit-pool-edit laws: region anchors, count==1 asserts, parse gate.
"""
import io, json, datetime

POOL = r"results\runnable_pool.json"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

src = io.open(POOL, encoding="utf-8", newline="").read()
n_entries = src.count('"id": ')

def region(src, anchor):
    i = src.find(anchor)
    assert i >= 0, f"anchor missing: {anchor}"
    j = src.find('"id": ', i + 6)
    return i, (j if j > 0 else len(src))

changed = 0
for n in range(8):
    eid = f'"id": "TRIAL-LABOR-W17-SCREEN-SHARD-{n}"'
    i, j = region(src, eid)
    seg = src[i:j]
    a = seg.count('"lane_owner": "bm-c"')
    b = seg.count('"owner": "bm-c"')
    c = seg.count('"owner_since": "2026-10-10 19:04:03"')
    assert a == 1 and b == 1 and c == 1, f"shard {n}: counts {a}/{b}/{c}"
    seg = seg.replace('"lane_owner": "bm-c"', '"lane_owner": "bm-a"', 1)
    seg = seg.replace('"owner": "bm-c"', '"owner": "bm-a"', 1)
    seg = seg.replace('"owner_since": "2026-10-10 19:04:03"', f'"owner_since": "{NOW}"', 1)
    src = src[:i] + seg + src[j:]
    changed += 3

i, j = region(src, '"id": "TRIAL-LABOR-W17-JUDGE"')
seg = src[i:j]
assert seg.count('"lane_owner": "bm-c"') == 1, "judge lane_owner"
seg = seg.replace('"lane_owner": "bm-c"', '"lane_owner": "bm-a"', 1)
src = src[:i] + seg + src[j:]
changed += 1

data = json.loads(src)
assert len(data["entries"]) == n_entries, "entry count drift"
w17 = [e for e in data["entries"] if "W17" in str(e.get("id", ""))]
for e in w17:
    if "SCREEN-SHARD" in e["id"] or "JUDGE" in e["id"]:
        assert e.get("lane_owner") == "bm-a", f"{e['id']} lane_owner {e.get('lane_owner')}"
        for s in e["shards"]:
            assert s.get("owner") == "bm-a", f"{e['id']}/{s['key']} owner {s.get('owner')}"
assert src.count('"id": ') == n_entries

with io.open(POOL, "w", encoding="utf-8", newline="") as fh:
    fh.write(src)
print("WROTE", POOL, "changed fields:", changed, "now:", NOW)
for e in w17:
    if "SCREEN" in e["id"] or "JUDGE" in e["id"]:
        for s in e["shards"]:
            print(e["id"], s["key"], s.get("owner"), s.get("owner_since"))
