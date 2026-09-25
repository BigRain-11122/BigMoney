# -*- coding: utf-8 -*-
"""r224 (bm-b) pool flip: P1E-NULLS-MCLOSETR shard ready->done
(pool-flip-is-round-work r203; mirrors r222 MCLOSE flip format).
Fail-closed: every evidence leg must hold before the write-back.
"""
import json
import sys

POOL = "results/runnable_pool.json"
ART = "results/shortline/p1e_nulls_M_close_tr.json"

# 1. artifact evidence legs (fail-closed)
a = json.load(open(ART, encoding="utf-8"))
assert a["class"] == "M_close_tr", a["class"]
assert a["n_nulls"] == 50, a["n_nulls"]
assert a["seed_band"] == [67050, 67100], a["seed_band"]  # prereg continuous ledger
assert a["meta"]["equivalence"]["pass"] is True, a["meta"]["equivalence"]
assert set(a["per_h"].keys()) == {"h5", "h10", "h20"}
assert a["mask_cells"] == 16638518  # == r224 production-form mask probe bit-match
print("artifact legs OK: n_nulls=50 seed_band 67050-67100 equiv 2.22e-16 "
      "mask bit-match 16638518")

# 2. flip
raw = open(POOL, "rb").read()
crlf = raw.count(b"\r\n") > 0
pool = json.loads(raw)
hit_e = hit_s = None
for e in pool.get("entries", []):
    if e.get("id") == "P1E-NULLS-MCLOSETR":
        hit_e = e
        for s in e.get("shards", []):
            if s.get("key") == "p1e-nulls-mclosetr":
                hit_s = s
                break
        break
assert hit_e is not None and hit_s is not None, "pool entry/shard not found"
assert hit_e.get("status") == "ready", hit_e.get("status")
assert hit_s.get("status") == "ready", hit_s.get("status")

hit_e["status"] = "done"
hit_s["status"] = "done"
hit_s["done_flip"] = {
    "ts": "2026-09-26 04:57",
    "by": "bm-b r224",
    "evidence": ("artifact p1e_nulls_M_close_tr.json landed ~04:52 "
                 "(pid24824 exited; n_nulls=50, per_h 3-col, equivalence "
                 "2.22e-16 PASS, mask_cells 16638518 == r224 "
                 "production-form mask probe bit-match (close+tr load, "
                 "share 0.3624), seed_band 67050-67100 per prereg "
                 "continuous ledger; elapsed 1902.8s ~= 32min/shard est)")
}
pool["updated_at"] = "2026-09-26 04:57:00"

# 3. write-back mirroring producer format (CRLF, indent=1)
out = json.dumps(pool, ensure_ascii=False, indent=1)
with open(POOL, "wb") as f:
    if crlf:
        f.write(out.replace("\n", "\r\n").encode("utf-8"))
    else:
        f.write(out.encode("utf-8"))

# 4. parse-verify (r185 law)
chk = json.load(open(POOL, encoding="utf-8"))
e2 = [e for e in chk["entries"] if e.get("id") == "P1E-NULLS-MCLOSETR"][0]
s2 = e2["shards"][0]
assert e2["status"] == "done" and s2["status"] == "done"
assert "done_flip" in s2
print("FLIP OK: entry+shard done, done_flip written, parse-verify PASS")
print("remaining P1E pool faces:")
for e in chk["entries"]:
    if str(e.get("id", "")).startswith("P1E"):
        print(" ", e["id"], e.get("status"),
              [s.get("status") for s in e.get("shards", [])])
