"""r685 bm-a: W3 shard-3 pool flip (ready->done) line-level surgery (r678 law).

runnable_pool.json roundtrip NOT identical -> byte surgery only:
 - locate shard face by unique key needle "w3-screen-3of4"
 - flip status ready->done inside that window only
 - append claimed_since/done_at/harvested_by/harvest_claim after owner_since
   (owner_since gains trailing comma, r629 mirror pit handled)
 - reparse + entry-count + changed-line-count assertions
"""
import json, sys, time

PATH = r"results/runnable_pool.json"
OUT = r"results/_r685bma_pool_flip_shard3.json"
NOW = time.strftime("%Y-%m-%d %H:%M:%S")

raw = open(PATH, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[:5000] else b"\n"
lines = raw.split(eol)

# locate face window: line with key w3-screen-3of4 .. first line that is "    }" after it
start = None
for i, ln in enumerate(lines):
    if b'"key": "w3-screen-3of4"' in ln:
        start = i
        break
assert start is not None, "key line not found"
end = None
for j in range(start + 1, len(lines)):
    if lines[j].strip() == b"}":
        end = j
        break
assert end is not None, "face close brace not found"

window = lines[start:end + 1]
txt = eol.join(window)

# 1. status flip
assert txt.count(b'"status": "ready"') == 1, "status ready count != 1 in window"
window = [ln.replace(b'"status": "ready"', b'"status": "done"') if b'"status"' in ln else ln for ln in window]

# 2. owner_since line: add trailing comma + new fields after it
oi = None
for k, ln in enumerate(window):
    if b'"owner_since"' in ln:
        oi = k
        break
assert oi is not None, "owner_since not found"
assert not window[oi].rstrip().endswith(b","), "unexpected trailing comma on owner_since"
indent = window[oi][: len(window[oi]) - len(window[oi].lstrip())]
window[oi] = window[oi].rstrip() + b","
new_fields = [
    indent + b'"claimed_since": "2026-10-04 15:53:07",',
    indent + f'"done_at": "{NOW}",'.encode(),
    indent + b'"harvested_by": "bm-a",',
    indent + b'"harvest_claim": "w3-screen-3of4.bm-a.json"',
]
window[oi + 1:oi + 1] = new_fields

lines[start:end + 1] = window
out = eol.join(lines)

# assertions before write
p = json.loads(out.decode("utf-8"))
ents = p["entries"] if isinstance(p, dict) and "entries" in p else p
old = json.loads(raw.decode("utf-8"))
old_ents = old["entries"] if isinstance(old, dict) and "entries" in old else old
assert len(ents) == len(old_ents), f"entry count changed {len(old_ents)}->{len(ents)}"
e3 = [x for x in ents if x.get("id") == "MASS-TRIAL-W3-SCREEN-SHARD-3"][0]
f3 = e3["shards"][0]
assert f3["status"] == "done" and f3["owner"] == "bm-a"
assert f3["harvested_by"] == "bm-a" and f3["claimed_since"] == "2026-10-04 15:53:07"
# other shard faces untouched
for x, y in zip(ents, old_ents):
    if x.get("id") != "MASS-TRIAL-W3-SCREEN-SHARD-3":
        assert x == y, f"non-target entry changed: {x.get('id')}"

# changed-line count check (difflib)
import difflib
d = sum(1 for l in difflib.unified_diff(raw.decode("utf-8").splitlines(),
                                        out.decode("utf-8").splitlines(),
                                        lineterm="", n=0)
        if (l.startswith("+") and not l.startswith("+++")) or
           (l.startswith("-") and not l.startswith("---")))
assert d == 8, f"changed lines {d} != 8 (2 modified x2 + 4 added, probe-verified form)"

open(PATH, "wb").write(out)
json.dump({"round": 685, "flip": "w3-screen-3of4 ready->done", "done_at": NOW,
           "changed_lines": d, "entries": len(ents),
           "result_ref": "autofill tick launch 27b7b826d claim 15:53:07; runner log logs/autofill_MASS-TRIAL-W3-SCREEN-SHARD-3.log terminal 'screen: shard done (78s)'; coverage probe _r685bma_w3_shard3_closeout_probe.py 1228/1228 exact, 0 dup, wave 4909/4909"},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({"flipped": True, "done_at": NOW, "changed_lines": d}))
