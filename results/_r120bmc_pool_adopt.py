# -*- coding: utf-8 -*-
"""r120 pool re-adoption (r348/r349 family recovery): bm-b tick b5be80cd
(00:52:51) stale-model write-back swallowed 2 T-95 s2 pool entries that were
CLAIMED-IN-FLIGHT (bm-a tick 8a1f8613 sleeve shard claim 00:50:05 included).
Idempotent assertion-guarded adoption: restore both entries VERBATIM from
last-known-good blob 8a1f8613 (claim state preserved), no other field touched.
"""
import json, subprocess, sys

POOL = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\runnable_pool.json"
GOOD_REV = "8a1f8613"          # last-known-good: 83 entries incl. claims
TARGETS = ("DECISION-CHAIN-V2-P1", "DECISION-CHAIN-V2-SLEEVE-EXPORT")

r = subprocess.run(["git", "show", GOOD_REV + ":results/runnable_pool.json"],
                   capture_output=True)
assert r.returncode == 0, r.stderr[:200]
good = {e["id"]: e for e in json.loads(r.stdout.decode("utf-8"))["entries"]}

cur_raw = open(POOL, encoding="utf-8").read()
assert "<<<" not in cur_raw and ">>>" not in cur_raw, "markers present"
cur = json.loads(cur_raw)
ids = [e["id"] for e in cur["entries"]]
assert len(ids) == len(set(ids)), "dup ids pre-adopt"

missing = [t for t in TARGETS if t not in ids]
if not missing:
    print("NO-OP: both entries already present (%d entries)" % len(ids))
    sys.exit(0)

for t in missing:
    assert t in good, "target absent in last-known-good blob -- abort"
    cur["entries"].append(good[t])
    e = good[t]
    sh = e.get("shards") or []
    print("adopted %s | status=%s | shard-claims: %s" % (
        t, e.get("status"),
        [(s.get("key"), s.get("owner"), s.get("owner_since")) for s in sh]))

out_raw = json.dumps(cur, ensure_ascii=False, indent=1) + "\n"
json.loads(out_raw)                                   # parse self-verify
assert "<<<" not in out_raw and ">>>" not in out_raw
with open(POOL, "w", encoding="utf-8", newline="\n") as f:
    f.write(out_raw)
print("pool written: %d -> %d entries" % (len(ids), len(cur["entries"])))
