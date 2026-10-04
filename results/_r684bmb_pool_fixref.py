# r684 bm-b: surgical byte patch of pool entry ticket_ref typo (r678 surgical
# path after roundtrip-unequal gate; r485 law: needle count==1 + reparse + count).
import io, json

FP = r"results/runnable_pool.json"
NEEDLE = b"O-202601002-2150"
FIX = b"O-20261002-2150"

raw = io.open(FP, "rb").read()
n = raw.count(NEEDLE)
assert n == 1, "needle count %d != 1" % n
n_fix_before = raw.count(FIX)          # 8 MT shard entries carry the correct id
patched = raw.replace(NEEDLE, FIX)
assert patched.count(NEEDLE) == 0 \
    and patched.count(FIX) == n_fix_before + 1 \
    and len(patched) == len(raw) - (len(NEEDLE) - len(FIX)) * n
with io.open(FP, "wb") as f:
    f.write(patched)
# reparse + structure self-check
doc = json.loads(io.open(FP, encoding="utf-8").read())
assert sum(1 for e in doc["entries"]
           if e.get("id") == "CONTEST-YTD-P1-RC-0OF1") == 1
e = [x for x in doc["entries"] if x.get("id") == "CONTEST-YTD-P1-RC-0OF1"][0]
assert FIX.decode() in e["ticket_ref"] and NEEDLE.decode() not in \
    e["ticket_ref"]
assert e["shards"][0]["status"] == "ready"
print("surgical patch OK; entries=", len(doc["entries"]),
      "; typo purged; shard ready")

# lane mirror: same surgical patch (submit wrote lane with same typo)
LANE = r"results/runnable_pool.bm-b.json"
raw_l = io.open(LANE, "rb").read()
n_l = raw_l.count(NEEDLE)
if n_l == 1:
    with io.open(LANE, "wb") as f:
        f.write(raw_l.replace(NEEDLE, FIX))
    json.loads(io.open(LANE, encoding="utf-8").read())
    print("lane mirror patched + reparsed")
else:
    print("lane mirror needle count =", n_l, "(left untouched)")
