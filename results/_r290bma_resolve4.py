# -*- coding: utf-8 -*-
"""R290 bm-a stash-pop resolver: autofill_state.json per SKILL.md
mixed-dict+ledger recipe (r203/R208/r215/r220/r245):
  launches = union -> newest-50 cap (ts desc) -> write back ts ASC
  last_tick = whole-dict by internal ts compare (same-second tie -> HEAD)
  byte-face mirror: CRLF/indent per base blob, newline-translate write-back
Sides: :2: = HEAD (bm-b r291 face), :3: = stashed local tick dirt (mine)."""
import json
import subprocess

def stage(n, path):
    return subprocess.run(["git", "show", f":{n}:{path}"],
                          capture_output=True).stdout

raw2 = stage(2, "results/autofill_state.json")
raw3 = stage(3, "results/autofill_state.json")
crlf = b"\r\n" in raw2
base = raw2.decode("utf-8", errors="replace")
d2 = json.loads(base)
d3 = json.loads(raw3.decode("utf-8", errors="replace"))

# launches union (dedupe by canonical json), cap newest 50 by ts
l2 = d2.get("launches", [])
l3 = d3.get("launches", [])
seen = {}
for r in l2 + l3:
    k = json.dumps(r, ensure_ascii=False, sort_keys=True)
    if k not in seen:
        seen[k] = r
union = list(seen.values())
union.sort(key=lambda r: str(r.get("ts", "")), reverse=True)   # newest first
capped = union[:50]
capped.sort(key=lambda r: str(r.get("ts", "")))                # ASC write-back
out = d2 if str(d2.get("last_tick", {}).get("ts", "")) >= \
    str(d3.get("last_tick", {}).get("ts", "")) else d3         # tie -> HEAD side
out["launches"] = capped

txt = json.dumps(out, ensure_ascii=False, indent=1) + "\n"
json.loads(txt)                                                # parse gate (r185)
with open("results/autofill_state.json", "w", encoding="utf-8",
          newline=("\r\n" if crlf else "\n")) as fh:
    fh.write(txt)
assert isinstance(out.get("last_tick"), dict), "last_tick must be dict"
print(f"autofill_state: launches {len(l2)}+{len(l3)} -> union {len(union)} "
      f"-> cap {len(capped)} (ASC); last_tick ts="
      f"{out['last_tick'].get('ts')}; crlf={crlf}")
