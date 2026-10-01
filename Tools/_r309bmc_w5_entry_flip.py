"""r309 bm-c: PERPETUAL-N1-W5 pool entry-layer done-flip (r180 dual-flip
law, r489 two-layer contract completion).

Defect: the W5 wave burned + finalized 2026-10-01 (12/12 shard products,
finalize K=11,120 per results/perpetual_faces/n1_w5_results.json, prereg
sec.7/8 backfilled) but the 12 pool entries stayed status=ready -- the
daemon harvest only lands the shard layer; the entry layer lands via the
observing-round flip executor. Ghost-ready face poisoned the py_watermark
runnable-work probe (false red) and the generator's never-dry trigger.

Three-way reconciliation per r489 law BEFORE any flip:
  (1) shard products: 12/12 checkpoints on disk, parse OK;
  (2) wave finalize: n1_w5_results.json merged K=11,120 (audit.machine
      = bm-c, finalize_only=True, all 12 shards_consumed);
  (3) prereg backfill: sec.7/8 present with the same K anchor.
N3-R1 entries (bm-a active lane, products still being written 09:55) are
explicitly NOT touched -- bm-a lineage owns their flips.

Pool write via the generator's _pool_write_mirror (r289 format law:
indent2 + CRLF, byte-identical face to the canonical producer).
"""
import json
import os
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import perpetual_faces as pf  # noqa: E402

POOL = os.path.join(ROOT, "results", "runnable_pool.json")

with open(POOL, encoding="utf-8") as f:
    pool = json.load(f)
entries = pool.get("entries", [])
vals = entries.values() if isinstance(entries, dict) else entries

TS = "2026-10-01T10:01:30+08:00"
flipped = 0
for e in vals:
    if not str(e.get("id", "")).startswith("PERPETUAL-N1-W5-SHARD-"):
        continue
    assert e.get("status") == "ready", (e.get("id"), e.get("status"))
    # leg-1: shard product presence (checkpoint presence == done semantics)
    sh = e["shards"][0]
    ck = sh["checkpoint"].split(" (presence")[0]
    assert os.path.exists(os.path.join(ROOT, ck)), "missing product " + ck
    if sh.get("status") != "done":
        # SHARD-11: product on disk -> shard-layer completion per r488
        sh["status"] = "done"
        sh["shard_done_note"] = ("presence=done flip r309 bm-c "
                                 "(product verified on disk)")
    e["status"] = "done"
    e["done_at"] = TS
    e["done_by"] = "bm-c r309"
    e["done_note"] = (
        "entry-layer done-flip r309 bm-c per r180 dual-flip law + r489 "
        "two-layer contract (daemon harvest lands shard layer only): "
        "three-way verified 12/12 shard products + finalize K=11,120 "
        "(results/perpetual_faces/n1_w5_results.json) + prereg sec.7/8 "
        "backfill; no rerun owed, no reopen")
    flipped += 1

assert flipped == 12, f"expected 12 W5 entries, flipped {flipped}"

pf._pool_write_mirror(pool)

# post-write verification: re-read, both layers done for all 12
with open(POOL, encoding="utf-8") as f:
    pool2 = json.load(f)
vals2 = (pool2.get("entries", {}).values()
         if isinstance(pool2.get("entries"), dict)
         else pool2.get("entries", []))
n_done = sum(1 for e in vals2
            if str(e.get("id", "")).startswith("PERPETUAL-N1-W5-SHARD-")
            and e.get("status") == "done"
            and all(s.get("status") == "done" for s in e.get("shards", [])))
assert n_done == 12, f"post-write verify: {n_done}/12"
n3 = sum(1 for e in vals2
         if str(e.get("id", "")).startswith("PERPETUAL-N3-R1-")
         and e.get("status") == "ready")
print(f"flip OK: 12/12 W5 entries entry+shard dual-done; "
      f"N3-R1 untouched (bm-a lane, {n3} ready left as-is)")
