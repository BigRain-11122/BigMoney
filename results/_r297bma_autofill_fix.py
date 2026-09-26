"""r297 bm-a autofill_state canonical fix (mixed-dict+ledger, r245/r140 laws).

Git auto-merged launches 47|50 -> 51 (cap breach). Recipe: canon-dedupe union,
sort ts desc, cap 50 (keep newest), write back ts-ASC (r245 producer-format
law), last_tick = newest by internal ts (worktree 05:50:01 mine, r140 tie->HEAD
n/a here). Byte face: mirror current LF/no-BOM, trailing-newline probe.
"""
import json, sys

PATH = "results/autofill_state.json"
raw = open(PATH, "rb").read()
ends_nl = raw.endswith(b"\n")
s = json.loads(raw.decode("utf-8-sig"))

l = s.get("launches", [])
assert isinstance(l, list)
seen, uniq = set(), []
for e in l:
    c = json.dumps(e, sort_keys=True, ensure_ascii=False)
    if c not in seen:
        seen.add(c)
        uniq.append(e)
uniq.sort(key=lambda e: e.get("ts", ""), reverse=True)     # newest first
dropped = uniq[50:]
keep = uniq[:50]
keep.sort(key=lambda e: e.get("ts", ""))                    # write-back ASC
s["launches"] = keep
assert isinstance(s.get("last_tick"), dict)
lt = s["last_tick"]
assert lt.get("ts", "") >= "2026-09-27 05:50", "last_tick regression"

text = json.dumps(s, ensure_ascii=False, indent=1)
if ends_nl:
    text += "\n"
open(PATH, "wb").write(text.encode("utf-8"))

v = json.load(open(PATH, encoding="utf-8-sig"))
lv = v["launches"]
ts = [e["ts"] for e in lv]
assert len(lv) <= 50
assert ts == sorted(ts), "write-back not ASC"
assert isinstance(v["last_tick"], dict)
fg = [e for e in lv if e.get("entry") == "FUSION-GRID-P1"]
assert fg, "FUSION-GRID-P1 launch record lost"
print(f"fixed: {len(l)} raw -> {len(uniq)} unique -> cap50 kept, "
      f"dropped {len(dropped)} oldest: {[d.get('ts')+' '+str(d.get('entry')) for d in dropped]}")
print("ts-ASC OK, last_tick dict OK, FUSION-GRID-P1 record OK, "
      f"last_tick.ts={v['last_tick']['ts']}")
