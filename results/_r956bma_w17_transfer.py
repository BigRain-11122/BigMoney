"""r956 bm-a: W17 shard claim-by-file owner transfer (O-20261010-1825 sec.1 handover).

Takeover evidence chain: bm-c owner_since 15:12-15:20 + zero checkpoint product
(no screen_shard_*.jsonl files) + bm-c heartbeat stale 15:15 (film-chain CEO
priority) + explicit CEO order O-20261010-1825 sec.1 authorizes transfer.
Raw-text surgical edit per pit-pool-edit laws (r509/r629/r678/r694):
region-anchored needles, count==1 assertions, json.loads gate before write.
"""
import io, json, datetime, sys

POOL = r"results\runnable_pool.json"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
EOL = "\r\n"

src = io.open(POOL, encoding="utf-8", newline="").read()
orig = src
n_entries_before = src.count('"id": ')

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
    c = seg.count('"owner_since": "2026-10-10 15:')
    assert a == 1 and b == 1 and c == 1, f"shard {n}: counts {a}/{b}/{c}"
    seg2 = seg.replace('"lane_owner": "bm-c"', '"lane_owner": "bm-a"', 1)
    seg2 = seg2.replace('"owner": "bm-c"', '"owner": "bm-a"', 1)
    k = seg2.find('"owner_since": "')
    k2 = seg2.find('"', k + len('"owner_since": "'))
    seg2 = seg2[:k] + f'"owner_since": "{NOW}' + seg2[k2:]
    src = src[:i] + seg2 + src[j:]
    changed += 3

# judge entry: lane_owner + owner null -> bm-a claim
i, j = region(src, '"id": "TRIAL-LABOR-W17-JUDGE"')
seg = src[i:j]
assert seg.count('"lane_owner": "bm-c"') == 1, "judge lane_owner count"
assert seg.count('"owner": null') == 1, "judge owner null count"
seg2 = seg.replace('"lane_owner": "bm-c"', '"lane_owner": "bm-a"', 1)
seg2 = seg2.replace(
    '"owner": null',
    '"owner": "bm-a",\r\n     "owner_since": "' + NOW + '"',
    1,
)
src = src[:i] + seg2 + src[j:]
changed += 2

# parse gate BEFORE write (r859 law: validate before disk)
data = json.loads(src)
assert data["entries"].__len__() == n_entries_before, "entry count drift"
w17 = [e for e in data["entries"] if str(e.get("id", "")).startswith("TRIAL-LABOR-W17-")]
owners = {}
for e in w17:
    for s in e["shards"]:
        owners[(e["id"], s["key"])] = (s.get("owner"), s.get("owner_since"))
for (eid, key), (o, t) in sorted(owners.items()):
    if "SCREEN-SHARD" in eid or "JUDGE" in eid:
        assert o == "bm-a", f"{eid} owner {o}"
        print(f"{eid} / {key}: owner={o} since={t}")

assert src.count('"id": ') == n_entries_before
assert src.count(EOL) == orig.count(EOL) + 1, "EOL count only +judge owner_since line"

with io.open(POOL, "w", encoding="utf-8", newline="") as fh:
    fh.write(src)
print("WROTE", POOL, "changed fields:", changed, "now:", NOW)
