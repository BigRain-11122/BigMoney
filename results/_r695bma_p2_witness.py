# r695 bm-a: P2 judgment products vs stage-A shards vs today's re-run (3-way witness)
import io, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

# 1) stage-A anchors
import contest_ytd_legs as CX
anchors = CX._census_anchor_rows()

# 2) P2 cells products (10 cells x 2 cost faces)
cells = []
for line in io.open(os.path.join(ROOT, "results", "refine_bench_stock",
                                 "rev_p2", "cells"), encoding="utf-8"):
    line = line.strip()
    if line:
        cells.append(json.loads(line))
print("P2 cells rows:", len(cells))
print(json.dumps(cells[0], ensure_ascii=False)[:400])
print("---")
# 3) 3-way compare per cell name (x1 face)
by_name = {}
for c in cells:
    nm = c.get("name") or c.get("cell")
    by_name.setdefault(nm, {})[c.get("cost_face", c.get("cost", "?"))] = c
for nm in sorted(by_name):
    x1 = by_name[nm].get("x1", {})
    a = anchors.get(nm, {})
    ks = x1.get("sharpe_full"); ka = a.get("sharpe_full")
    print("%-34s P2_x1_sharpe=%r stageA=%r same=%s ann %r vs %r entries %r vs %r"
          % (nm, ks, ka, ks == ka, x1.get("ann_ret"), a.get("ann_ret"),
             x1.get("entries"), a.get("entries")))
print("PROBE_OK")
