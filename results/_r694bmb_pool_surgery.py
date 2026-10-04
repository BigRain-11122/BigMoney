"""r694 bm-b pool surgery: CONTEST-YTD-P1-RC-0OF1 stage-A' re-anchor face
(MSG-2026-10-04-2110 adjudication case B). Three line-level needles inside
the entry region only (r694-b anchor-region needle law); double-read
freshness gate against the autofill daemon write window; reparse + entry
count assertions. runnable_pool.json is daemon-shared -- byte surgery
only, zero round-trip rewrite (r678 roundtrip-not-identity law)."""
import io
import json

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
FP = ROOT + r"\results\runnable_pool.json"

b1 = io.open(FP, "rb").read()
ENTRY = b'"id": "CONTEST-YTD-P1-RC-0OF1"'
pos = b1.find(ENTRY)
assert pos != -1 and b1.count(ENTRY) == 1, "entry needle not unique"
region_end = b1.find(b'"id": "PERPETUAL-N2-W15-GENERATE"', pos)
assert region_end > pos, "region end anchor missing"
region = b1[pos:region_end]

N1 = b'"data/fundamental/b_layer_mask.csv"'
N2 = b'"data/fundamental/b_layer_mask.stageA_prime_pin.csv"'
assert region.count(N1) == 1, "dep needle count != 1: %d" % region.count(N1)
region = region.replace(N1, N2)

N3 = (b'census-parity anchors vs published shard rows); RAM floor = '
      b'refine_bench_rev_census census law"')
N4 = (b"census-parity anchors vs stage-A' pinned-basis anchors "
      b"(rc_stageA_prime_anchors.json, mask pin b_layer_mask."
      b"stageA_prime_pin.csv) per MSG-2026-10-04-2110 adjudication "
      b"case B (bm-b r694); RAM floor = refine_bench_rev_census "
      b'census law"')
assert region.count(N3) == 1, "prereg needle count != 1"
region = region.replace(N3, N4)

N5 = b'census-stats parity anchors abort on drift"'
N6 = (b"census-stats parity vs stage-A' pinned-basis anchors abort on "
      b'drift (anchor phase burns census-original rows on the pinned '
      b'mask first; basis switch disclosed)"')
assert region.count(N5) == 1, "note needle count != 1"
region = region.replace(N5, N6)

out = b1[:pos] + region + b1[region_end:]
b2 = io.open(FP, "rb").read()
assert b2 == b1, "daemon wrote the pool between reads -- ABORT, rerun"
doc = json.loads(out.decode("utf-8"))
n_before = len(json.loads(b1.decode("utf-8"))["entries"])
assert len(doc["entries"]) == n_before, "entry count drift"
e = [x for x in doc["entries"]
     if x.get("id") == "CONTEST-YTD-P1-RC-0OF1"][0]
assert e["data_deps"][-1] == \
    "data/fundamental/b_layer_mask.stageA_prime_pin.csv", "dep swap miss"
assert "stageA_prime_pin" in e["prereg_ref"], "prereg annotation miss"
sh = e["shards"][0]
assert sh["owner"] == "bm-b" and sh["status"] == "ready", "shard face drift"
io.open(FP, "wb").write(out)
print("POOL SURGERY OK: dep swapped + prereg/note annotated; entries=%d; "
      "shard owner=%s owner_since=%s untouched"
      % (len(doc), sh["owner"], sh["owner_since"]))
