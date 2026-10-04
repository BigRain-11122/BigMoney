"""r497 bm-c: N2-W15 SCREEN shard bounds from ACTUAL rows (real-read
via runner import; r670 tiling law + r481 recipe). Zero engine, zero
ledger, zero registry writes. Evidence -> _r497bmc_n2_bounds.txt."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

import perpetual_faces_n2 as n2  # noqa: E402

cells = n2._cell_list_n2()
n = len(cells)
shards = n2.NSHARDS
assert shards == 12, shards
per = {}
for s in range(shards):
    mine = [c for i, c in enumerate(cells) if i % shards == s]
    per[s] = (mine[0]["cell_id"], mine[-1]["cell_id"], len(mine))
# r670 tiling guard: union over shards == all cells exactly once
seen = []
for s in range(shards):
    seen.extend(c["cell_id"] for i, c in enumerate(cells) if i % shards == s)
assert sorted(seen) == sorted(c["cell_id"] for c in cells), "tiling union broken"
assert len(set(c["cell_id"] for c in cells)) == n, "dup cell_id"
n_cand = sum(1 for c in cells if not c["cell_id"].startswith("SCREEN|NULL-"))
n_null = n - n_cand
cand = json.load(open(n2.CANDIDATES_FILE, encoding="utf-8"))
assert cand["n"] == n_cand == 954, (cand["n"], n_cand)
assert n_null == n2.K_NULLS == 200, (n_null, n2.K_NULLS)
assert os.path.exists(n2.PREP_FILE), "prep state absent"
prep = json.load(open(n2.PREP_FILE, encoding="utf-8"))
assert prep["n_distinct"] == 954 and prep["n_starts_6m"] == 1253

sizes = [per[s][2] for s in range(shards)]
out = {
    "total_cells": n, "candidates": n_cand, "nulls": n_null,
    "shards": shards, "sizes": sizes,
    "size_law": "1154 = 12*96+2 -> shards 0,1 get 97; shards 2-11 get 96",
    "first_last": {str(s): per[s] for s in range(shards)},
    "tiling_union_exactly_once": True,
    "prep_starts_6m": prep["n_starts_6m"],
    "evidence_cutoff": prep.get("evidence_cutoff"),
}
with open(os.path.join(ROOT, "results", "_r497bmc_n2_bounds.json"), "w",
          encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("BOUNDS OK: n=%d (954 cand + 200 null), sizes=%s, tiling union=1x, "
      "starts_6m=%d" % (n, sizes, prep["n_starts_6m"]))
