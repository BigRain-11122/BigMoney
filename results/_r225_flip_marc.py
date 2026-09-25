# -*- coding: utf-8 -*-
"""r225 (bm-b) pool flip: P1E-NULLS-MARC shard ready->done
(pool-flip-is-round-work r203; mirrors r222/r224 flip format).
Fail-closed: every evidence leg must hold before the write-back.
Run AFTER _r225_mask_probe.py PASSes (bit-match proof lives there)."""
import json
import sys

POOL = "results/runnable_pool.json"
ART = "results/shortline/p1e_nulls_M_arc.json"
ENTRY = "P1E-NULLS-MARC"
SHARD = "p1e-nulls-marc"

# 1. artifact evidence legs (fail-closed)
a = json.load(open(ART, encoding="utf-8"))
assert a["class"] == "M_arc", a["class"]
assert a["n_nulls"] == 50, a["n_nulls"]
assert a["seed_band"] == [67100, 67150], a["seed_band"]  # prereg continuous ledger
assert a["meta"]["equivalence"]["pass"] is True, a["meta"]["equivalence"]
assert set(a["per_h"].keys()) == {"h5", "h10", "h20"}
print("artifact legs OK: n_nulls=50 seed_band 67100-67150 "
      f"mask_cells {a['mask_cells']} (bit-match proven by _r225_mask_probe)")

# 2. flip
raw = open(POOL, "rb").read()
crlf = raw.count(b"\r\n") > 0
pool = json.loads(raw)
hit_e = hit_s = None
for e in pool.get("entries", []):
    if e.get("id") == ENTRY:
        hit_e = e
        for s in e.get("shards", []):
            if s.get("key") == SHARD:
                hit_s = s
                break
        break
assert hit_e is not None and hit_s is not None, "pool entry/shard not found"
assert hit_e.get("status") == "ready", hit_e.get("status")
assert hit_s.get("status") == "ready", hit_s.get("status")

hit_e["status"] = "done"
hit_s["status"] = "done"
hit_s["done_flip"] = {
    "ts": "2026-09-26 05:35",
    "by": "bm-b r225",
    "evidence": ("artifact p1e_nulls_M_arc.json landed ~05:32 "
                 "(pid27452 launched 05:00:09; n_nulls=50, per_h 3-col, "
                 "equivalence PASS, mask_cells %d == r225 "
                 "production-form mask probe bit-match (close+tr+vwap "
                 "load, share %s), seed_band 67100-67150 per prereg "
                 "continuous ledger)" % (a["mask_cells"], a["mask_cell_share"]))
}
pool["updated_at"] = "2026-09-26 05:35:00"

# 3. write-back mirroring producer format (CRLF, indent=1)
out = json.dumps(pool, ensure_ascii=False, indent=1)
with open(POOL, "wb") as f:
    if crlf:
        f.write(out.replace("\n", "\r\n").encode("utf-8"))
    else:
        f.write(out.encode("utf-8"))

# 4. parse-verify (r185 law)
chk = json.load(open(POOL, encoding="utf-8"))
e2 = [e for e in chk["entries"] if e.get("id") == ENTRY][0]
s2 = e2["shards"][0]
assert e2["status"] == "done" and s2["status"] == "done"
assert "done_flip" in s2
print("FLIP OK: entry+shard done, done_flip written, parse-verify PASS")
print("remaining P1E pool faces:")
for e in chk["entries"]:
    if str(e.get("id", "")).startswith("P1E"):
        print(" ", e["id"], e.get("status"),
              [s.get("status") for s in e.get("shards", [])])
