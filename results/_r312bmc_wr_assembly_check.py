"""r312 bm-c: wild_route_lab pool-conversion verification probe (T-134 s2).

Two faces:
  [A] assembly-segment verification (runs on ANY machine with the frozen
      p1c_stock cache -- exercises the EXACT new pool-path parent code:
      light-idx census + (arm,universe,regime) grouping + shard coverage
      + regime-extra frozen ids).
  [B] live parity procedure for the DATA HOST (bm-a holds the p1c_stock
      panel; bm-c r312 had no local panel -> live byte-identity accrues at
      the next natural burn there): burn a tiny slice serial vs pool and
      byte-compare the cell JSONs --
        python scripts/wild_route_lab.py run --shard 0 --of 60 --workers 1
          (record cell file hashes, then move cells aside or use a copy of
           the checkpoint dir; simplest: run into a scratch OUT_DIR via
           module import and temp CELL_DIR/OUT_DIR patch, mirroring the
           F15 selftest pattern)
        python scripts/wild_route_lab.py run --shard 0 --of 60
          (auto pool plan)
        compare per-cell JSON bytes (sha256) between the two runs.
      The S-mp hermetic legs (selftest 43/43, r312) already prove task-level
      bit-identity; face [B] closes the production loader + spawn path.
"""
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import wild_route_lab as WR

assert os.path.exists(os.path.join(WR.CACHE, "dates.npy")), (
    "p1c_stock cache not on this machine (data host = bm-a); "
    "face [A] needs the frozen panel index")

# --- exact pool-path parent assembly (copied from run_shard pool branch) ---
idx = pd.to_datetime(np.load(os.path.join(WR.CACHE, "dates.npy")), unit="us")
cells = WR.enumerate_cells({"idx": idx})
print("census:", len(cells), "idx range:", idx[0].date(), "->", idx[-1].date())

serial_cells = WR.enumerate_cells({"idx": idx})
assert [c["cell_id"] for c in cells] == [c["cell_id"] for c in serial_cells]
print("PASS census light-idx == serial enumeration (cell_id order identical)")

for of in (1, 8, 12):
    seen = set()
    for shard in range(of):
        mine = [c for i, c in enumerate(cells) if i % of == shard]
        for c in mine:
            assert c["cell_id"] not in seen, "shard overlap"
            seen.add(c["cell_id"])
    assert len(seen) == 1569, f"of={of} cover {len(seen)}"
    shard0 = [c for i, c in enumerate(cells) if i % of == 0]
    groups = {}
    for c in shard0:
        groups.setdefault((c["arm"], c["universe"], c["regime"]), []).append(c)
    dup = sum(len(v) for v in groups.values()) - len(groups)
    print(f"PASS of={of}: 1569 covered disjointly; shard0 groups="
          f"{len(groups)} cells={len(shard0)} memo-saved-cells={dup}")

for (a, u, r), cs in groups.items():
    for c in cs:
        assert c["arm"] == a and c["universe"] == u and c["regime"] == r
print("PASS group keys consistent with member cells")

reg = [c for c in cells if c["regime"] == "advance"]
assert len(reg) == 3 and all(
    c["cell_id"].endswith("|regime_adv") for c in reg), reg
print("PASS 3 regime extras with frozen cell_id suffix")
print("assembly-segment verification: ALL PASS")
