"""r501 bm-b: W6 pool truth heal (r488/r489/r309 double-layer law, r509 raw-text surgical law).

Scope: PERPETUAL-N1-W6-SHARD-0..10 (11 entries). SHARD-11 untouched (bm-a in-flight).
Evidence per shard: results/pool_claims/PERPETUAL-N1-W6-SHARD-<n>/*.json closed+ok
(verified pre-run). Products shard-0..6 verified on origin (git ls-tree pre-run).
Entry provenance done_by/done_at derived from claim records (zero hand-copy).
Shards 5/6 also get shard-layer flip + harvest provenance (mirror W5-S0 pattern).
Surgical: flat-0-key + CRLF preserved; NO whole-file re-serialization (r509 law).
"""
import json, glob, io

PATH = "results/runnable_pool.json"
raw = io.open(PATH, encoding="utf-8", newline="").read()
assert "\r\n" in raw and raw.count("\n") == raw.count("\r\n"), "CRLF invariant"

# derive provenance from claim files (single source)
prov = {}
for n in range(11):
    d = "results/pool_claims/PERPETUAL-N1-W6-SHARD-%d" % n
    fs = glob.glob(d + "/*.json")
    assert len(fs) == 1, "claim file count != 1 for shard %d" % n
    c = json.load(io.open(fs[0], encoding="utf-8"))
    assert c["state"] == "closed" and c["outcome"] == "ok", "claim not closed+ok shard %d" % n
    prov[n] = {
        "by": c["machine_id"],
        "ts": c["closed_at"].replace("T", " ").split("+")[0],  # -> "YYYY-MM-DD HH:MM:SS"
        "claim_file": fs[0].split("\\")[-1],
    }

def entry_block(raw, marker):
    i = raw.find(marker)
    assert i >= 0, "marker not found: " + marker
    start = raw.rfind("{", 0, i)
    depth = 0
    j = start
    while True:
        if raw[j] == "{":
            depth += 1
        elif raw[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    return start, j + 1, raw[start:j + 1]

changed_lines = 0
for n in reversed(range(11)):  # 10..0 so earlier indices stay valid
    marker = '"id": "PERPETUAL-N1-W6-SHARD-%d",\r\n' % n
    start, end, blk = entry_block(raw, marker)
    p = prov[n]

    # a) entry status flip: first "ready" status line before "shards": [
    k_shards = blk.find('"shards": [')
    j = blk.find('"status": "ready",\r\n')
    assert -1 < j < k_shards, "entry status not located shard %d" % n
    blk = blk[:j] + '"status": "done",\r\n' + blk[j + len('"status": "ready",\r\n'):]
    changed_lines += 2  # -1/+1

    # b) entry provenance: insert between workers_plan close '}' and entry close '}'
    assert blk.endswith("}\r\n}"), "unexpected entry tail for shard %d" % n
    ins = '},\r\n"done_by": "%s",\r\n"done_at": "%s"\r\n}' % (p["by"], p["ts"])
    blk = blk[:-len("}\r\n}")] + ins
    changed_lines += 3  # +2 lines, +1 comma on workers_plan close

    # c) shard layer for 5/6: status ready->done + harvest provenance
    if n in (5, 6):
        key = '"key": "n1w6-%dof12",\r\n"status": "ready",\r\n' % n
        assert key in blk, "shard status anchor missing %d" % n
        blk = blk.replace(key, '"key": "n1w6-%dof12",\r\n"status": "done",\r\n' % n, 1)
        changed_lines += 2
        own = '"owner_since": "'
        oi = blk.find(own)
        assert oi >= 0, "owner_since missing %d" % n
        oe = blk.find("\r\n}", oi)
        add = ',\r\n"claimed_since": "%s",\r\n"done_at": "%s",\r\n"harvested_by": "%s",\r\n"harvest_claim": "%s"' % (
            prov[n]["ts"], prov[n]["ts"], p["by"], p["claim_file"])
        blk = blk[:oe] + add + blk[oe:]
        changed_lines += 5

    json.loads(blk)  # parse check before splice
    raw = raw[:start] + blk + raw[end:]

io.open(PATH, "w", encoding="utf-8", newline="").write(raw)

# post-conditions
p2 = json.loads(raw)
assert "\r\n" in raw and raw.count("\n") == raw.count("\r\n"), "CRLF invariant post"
w6 = {e["id"]: e for e in p2["entries"] if e["id"].startswith("PERPETUAL-N1-W6-SHARD-")}
assert len(w6) == 12, "w6 entry count"
for n in range(11):
    e = w6["PERPETUAL-N1-W6-SHARD-%d" % n]
    assert e["status"] == "done", "entry not done %d" % n
    assert e.get("done_by") == prov[n]["by"] and e.get("done_at") == prov[n]["ts"], "provenance mismatch %d" % n
    assert all(s["status"] == "done" for s in e["shards"]), "shard layer not done %d" % n
e11 = w6["PERPETUAL-N1-W6-SHARD-11"]
assert e11["status"] == "ready" and e11["shards"][0]["status"] == "ready" and e11["shards"][0]["owner"] == "bm-a", "shard-11 must be untouched"
print("W6 heal OK: 11 entries done (entry+shard), shard-11 untouched in-flight; est changed lines ~%d" % changed_lines)
print("other ready entries in pool:", sum(1 for e in p2["entries"] if e["status"] == "ready"))
