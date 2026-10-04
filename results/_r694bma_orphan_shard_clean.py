"""r694 bm-a: pool orphan-shard cleanup -- remove my duplicate claim shard
'generate-0of1' (owner=bm-a, claim 19:54:08, burn KILLED per later-claimer
yield; bm-b 19:44:22 origin-first live burn remains canonical) from BOTH the
shared runnable_pool.json and my lane mirror runnable_pool.bm-a.json.
Line-level surgery per r678 law + reparse + entry/shard count assertions.
Fail-closed: needle uniqueness asserted before any write."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FACES = [
    os.path.join(ROOT, "results", "runnable_pool.json"),
    os.path.join(ROOT, "results", "runnable_pool.bm-a.json"),
]

for path in FACES:
    raw = open(path, encoding="utf-8", newline="").read()
    eol = "\r\n" if "\r\n" in raw[:2000] else "\n"
    data = json.loads(raw)
    gen = [x for x in data["entries"] if x["id"] == "PERPETUAL-N2-W15-GENERATE"]
    assert len(gen) == 1, "%s: GENERATE entries=%d" % (path, len(gen))
    keys = [s["key"] for s in gen[0]["shards"]]
    assert keys.count("generate-0of1") == 1, "%s: orphan count=%d" % (path, keys.count("generate-0of1"))
    before_shards = len(gen[0]["shards"])

    # locate my orphan shard block SCOPED to the N2 entry region (the
    # 'generate-0of1' key name also exists in TRIAL-LABOR-W2-GENERATE's
    # historical shard -- whole-file find hits that one FIRST; anchor first)
    entry_pos = raw.find('"PERPETUAL-N2-W15-GENERATE"')
    assert entry_pos != -1, "N2 entry id not found"
    kline = ' "key": "generate-0of1"'
    i = raw.find(kline, entry_pos)
    assert i != -1, "orphan key line not found in N2 entry region"
    assert raw.find(kline, i + 1) == -1, "orphan key not unique after N2 anchor"
    # shard object start: backtrack to the '{' line start
    obj_start = raw.rfind("{", 0, i)
    # find object end: the matching '}' at shard indent (3-space ' }')
    j = raw.find("}", i)
    assert obj_start != -1 and j != -1
    # expand to full lines
    line_start = raw.rfind(eol, 0, obj_start) + len(eol)
    line_end = raw.find(eol, j) + len(eol)
    block = raw[line_start:line_end]
    assert '"generate-0of1"' in block and "owner" in block
    assert block.count("{") == block.count("}") == 1, "block brace shape: %r" % block[:80]
    # separator handling: if block preceded by comma (previous shard), strip
    # the preceding comma; if block followed by comma (it was NOT last),
    # strip the block including its trailing comma
    prev_two = raw[line_start - 2:line_start]
    # remove the block; reparse below catches any comma/brace artifact
    block = raw[line_start:line_end]
    new_raw = raw[:line_start] + raw[line_end:]
    # seam fix: if my orphan was the LAST shard (block closer without comma),
    # the previous shard's closer now dangles a trailing comma before ']'
    if not block.rstrip().endswith(","):
        seam_bad = "}," + eol + "   ]"
        assert new_raw.count(seam_bad) == 1, \
            "seam pattern count=%d (expected 1)" % new_raw.count(seam_bad)
        new_raw = new_raw.replace(seam_bad, "}" + eol + "   ]", 1)
    # the removed block either had a trailing comma (mid-array) or none
    # (last). If it was last, the previous shard now has a trailing comma
    # before ']' -- detect '},' + eol + ' ]' inside the shards array region.
    shard_tail = ",%s%s ]" % (eol, eol)
    # normalize: ',,' or ', ]' artifacts
    assert ",,%s" % eol not in new_raw, "double comma artifact"
    # if previous shard now dangles: pattern '},' + eol + eol + ' ]' within
    # the GENERATE entry region is ILLEGAL json; reparse below catches it.
    data2 = json.loads(new_raw)
    gen2 = [x for x in data2["entries"] if x["id"] == "PERPETUAL-N2-W15-GENERATE"]
    assert len(gen2[0]["shards"]) == before_shards - 1
    assert "generate-0of1" not in [s["key"] for s in gen2[0]["shards"]]
    live = [s for s in gen2[0]["shards"] if s["key"] == "n2-w15-generate-0of1"]
    assert live and live[0]["owner"] == "bm-b"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(new_raw)
    data3 = json.loads(open(path, encoding="utf-8").read())
    assert len(data3["entries"]) == len(data["entries"])
    print("CLEAN OK %s: GENERATE shards %d->%d (orphan generate-0of1/bm-a "
          "removed; n2-w15-generate-0of1 owner=bm-b intact)"
          % (os.path.basename(path), before_shards,
             len([x for x in data3["entries"]
                  if x["id"] == "PERPETUAL-N2-W15-GENERATE"][0]["shards"])))
