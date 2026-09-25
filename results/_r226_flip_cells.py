# -*- coding: utf-8 -*-
"""r226 (bm-b) pool flip: P1E-CELLS shard ready->done
(pool-flip-is-round-work r203; mirrors r222/r224/r225 flip format).
Fail-closed: every evidence leg must hold before the write-back.
CELSS leg evidence = 7 member partials all status==ok with h5/h10/h20
IS/OOS fields present (real-factor leg; no null-mask probe applies --
mask probes were nulls-leg evidence only, r221/r224/r225)."""
import json
import os
import sys

POOL = "results/runnable_pool.json"
PARTIAL_DIR = os.path.join("results", "shortline", "p1e_partial")
ENTRY = "P1E-CELLS"
SHARD = "p1e-cells"
MEMBERS = ["zoo85_terrified", "zoo85_stv", "zoo92_coin_team",
           "zoo93_arc", "zoo93_vrc", "zoo93_src", "zoo93_krc"]
HORIZONS = ["h5", "h10", "h20"]

# 1. artifact evidence legs (fail-closed; mirrors runner _validate_inputs)
cells = {}
for nm in MEMBERS:
    p = os.path.join(PARTIAL_DIR, nm + ".json")
    assert os.path.exists(p), f"cell checkpoint missing: {nm}"
    with open(p, encoding="utf-8") as f:
        cells[nm] = json.load(f)
    c = cells[nm]
    assert c.get("status") == "ok", (nm, c.get("status"))
    assert c.get("factor") == nm, (nm, c.get("factor"))
    for h in HORIZONS:
        for k in (f"{h}_is_ic", f"{h}_is_ir", f"{h}_is_n", f"{h}_oos_ic"):
            assert k in c, (nm, k)
        assert c.get(f"{h}_is_n", 0) > 0, (nm, f"{h}_is_n")
h10 = {nm: (cells[nm]["h10_is_ic"], cells[nm]["h10_is_ir"]) for nm in MEMBERS}
print("artifact legs OK: 7/7 partials status==ok, 3-horizon IS/OOS fields present")
print("h10 IS face (ic, ir):")
for nm in MEMBERS:
    print(f"  {nm}: {h10[nm][0]:+.4f} / {h10[nm][1]:+.3f}")

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

h10_str = ", ".join(f"{nm} {h10[nm][0]:+.4f}/{h10[nm][1]:+.3f}"
                    for nm in MEMBERS)
hit_e["status"] = "done"
hit_s["status"] = "done"
hit_s["done_flip"] = {
    "ts": "2026-09-26 05:4x",
    "by": "bm-b r226",
    "evidence": ("run-cells landed: 7/7 partials status==ok (runner pid1800 "
                 "launched 05:40:09 via autofill 05:40 tick; 3-horizon "
                 "IS/OOS fields present per member; h10 primary face "
                 "(is_ic/is_ir): " + h10_str + ")"),
}
pool["updated_at"] = "2026-09-26 05:4x:00"

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
print("P1E pool final census (expect 4/4 done):")
for e in chk["entries"]:
    if str(e.get("id", "")).startswith("P1E"):
        print(" ", e["id"], e.get("status"),
              [s.get("status") for s in e.get("shards", [])])
