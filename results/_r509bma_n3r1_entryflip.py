"""r509 bm-a: entry-layer flip, TEXT-LEVEL surgical (the r508/r289真义).

Whole-file re-serialization is FORBIDDEN for runnable_pool.json (custom
flat-0-indent writer shape: keys at col 0, CRLF, EOF newline). Surgical =
flip exactly the 6 entry-level status lines, zero other bytes touched.
"""
import json

PATH = "results/runnable_pool.json"
raw = open(PATH, encoding="utf-8", newline="").read()
assert "\r\n" in raw and raw.count("\n") == raw.count("\r\n"), "CRLF invariant"

members = ["COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
           "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01"]
needle_status = '"status": "ready",\r\n'
flips = 0
for mid in members:
    anchor = f'"id": "PERPETUAL-N3-R1-{mid}",\r\n'
    i = raw.find(anchor)
    assert i >= 0, f"id line not found: {mid}"
    j = raw.find(needle_status, i)
    # entry status must sit before the entry's shards array (sanity bound)
    k = raw.find('"shards": [', i)
    assert i < j < k, f"entry status not located for {mid}"
    raw = raw[:j] + '"status": "done",\r\n' + raw[j + len(needle_status):]
    flips += 1
assert flips == 6

with open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(raw)

# post-conditions: parse + only-6-diffs + shard layers intact
p = json.loads(raw)
n3 = [e for e in p["entries"] if e["id"].startswith("PERPETUAL-N3-R1-")]
assert len(n3) == 6 and all(e["status"] == "done" for e in n3)
assert all(s["status"] == "done" for e in n3 for s in e["shards"])
ready_elsewhere = sum(1 for e in p["entries"] if e["status"] == "ready")
print(f"flipped {flips} entries; N3 all done; other ready entries={ready_elsewhere}")
