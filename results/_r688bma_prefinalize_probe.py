"""r688 bm-a pre-finalize probe: 777-cell completeness + cross-shard id-dup (r482/r685).

All 4 W3-JUDGE shards done (0=bm-c 17:11:50, 1=bm-b 17:27:12, 2=bm-a 17:29:26,
3=bm-c 17:29:13). Post-merge same-window probe BEFORE judge-finalize --wave 3.
Expected: shard files i%4==0 (195) + i%4==1/2/3 (194 each) = 777 unique cell_ids,
zero duplicate cell_ids within and across files, zero byte-dup rows.
"""
import json
import os

FILES = {
    0: "results/mass_trial/w3_judge_shard_0of4.jsonl",
    1: "results/mass_trial/w3_judge_shard_1of4.jsonl",
    2: "results/mass_trial/w3_judge_shard_2of4.jsonl",
    3: "results/mass_trial/w3_judge_shard_3of4.jsonl",
}
EXPECT = {0: 195, 1: 194, 2: 194, 3: 194}

all_ids = []
all_rows = []
byte_lines = []
for shard, path in FILES.items():
    if not os.path.exists(path):
        raise SystemExit("MISSING shard file: " + path)
    raw = open(path, "rb").read().split(b"\n")
    lines = [l for l in raw if l.strip()]
    rows = [json.loads(l) for l in lines]
    idx = [r["i"] for r in rows]
    ids = [r["cell_id"] for r in rows]
    if len(rows) != EXPECT[shard]:
        raise SystemExit("shard %d rows=%d != %d" % (shard, len(rows), EXPECT[shard]))
    if any(i % 4 != shard for i in idx):
        raise SystemExit("shard %d has non-i%%%d==%d rows" % (shard, shard, shard))
    if len(set(ids)) != len(ids):
        dup = [x for x in ids if ids.count(x) > 1][:3]
        raise SystemExit("shard %d internal cell_id dup: %s" % (shard, dup))
    if len(set(lines)) != len(lines):
        raise SystemExit("shard %d byte-dup rows" % shard)
    # per-row completeness
    for r in rows:
        for k in ("dual_nulls", "sample_sufficient", "legs", "n_eff_start_windows", "candidate_id"):
            if k not in r:
                raise SystemExit("shard %d row missing %s" % (shard, k))
    print("shard %d: %d rows OK (i%%%d==%d, unique, complete)" % (shard, len(rows), shard, shard))
    all_ids.extend(ids)
    all_rows.extend(rows)
    byte_lines.extend(lines)

if len(all_ids) != 777:
    raise SystemExit("total=%d != 777" % len(all_ids))
if len(set(all_ids)) != 777:
    from collections import Counter
    c = Counter(all_ids)
    dups = [k for k, v in c.items() if v > 1][:5]
    raise SystemExit("cross-shard cell_id dup: %s" % dups)
if len(set(byte_lines)) != len(byte_lines):
    raise SystemExit("cross-shard byte-dup rows")

# judge field sanity: dual_nulls shape
r0 = all_rows[0]
print("dual_nulls keys sample:", sorted(r0["dual_nulls"].keys())[:8] if isinstance(r0["dual_nulls"], dict) else type(r0["dual_nulls"]).__name__)
print("PRE-FINALIZE PROBE PASS: 777/777 unique complete cells across 4 shards, zero dups")
