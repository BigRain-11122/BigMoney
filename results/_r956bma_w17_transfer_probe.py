import io, datetime, json

POOL = r"results\runnable_pool.json"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
src = io.open(POOL, encoding="utf-8", newline="").read()

def region(src, anchor):
    i = src.find(anchor)
    j = src.find('"id": ', i + 6)
    return i, (j if j > 0 else len(src))

for n in range(8):
    eid = f'"id": "TRIAL-LABOR-W17-SCREEN-SHARD-{n}"'
    i, j = region(src, eid)
    seg = src[i:j]
    seg2 = seg.replace('"lane_owner": "bm-c"', '"lane_owner": "bm-a"', 1)
    seg2 = seg2.replace('"owner": "bm-c"', '"owner": "bm-a"', 1)
    k = seg2.find('"owner_since": "')
    print(f"shard {n}: owner_since needles in region:", seg2.count('"owner_since": "'))
    k2 = seg2.find('"', k + len('"owner_since": "'))
    seg2 = seg2[:k] + f'"owner_since": "{NOW}"' + seg2[k2:]
    src = src[:i] + seg2 + src[j:]

try:
    json.loads(src)
    print("PARSE OK after screen edits")
except json.JSONDecodeError as e:
    print("PARSE FAIL:", e)
    pos = e.pos
    print(repr(src[pos-200:pos+120]))
    print("line", e.lineno)
