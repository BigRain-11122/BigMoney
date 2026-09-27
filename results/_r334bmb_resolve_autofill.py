# -*- coding: utf-8 -*-
"""r334 bm-b: autofill_state.json mixed-dict+ledger resolution (SKILL.md table recipe).

laws: launches union -> ts desc cap50 (keep newest) -> re-sort ts ASC before
write-back (r245: producer appends, desc write = whole-column flip pseudo-diff
inherited by future ticks); last_tick = internal-ts compare, whole-dict assign,
tie -> HEAD ours (r140); newline+indent mirror base blob probe, newline
translation mode write (r223/r234); json.loads verify before add (r185).
rebase side map: :1=base(dcaa14ff) :2=ours(HEAD=d9cea197) :3=theirs(0549f32e).
"""
import io
import json
import re
import subprocess

PATH = "results/autofill_state.json"


def blob(stage):
    return subprocess.run(["git", "show", f"{stage}:{PATH}"],
                          capture_output=True).stdout


b, o, t = blob(":1"), blob(":2"), blob(":3")
jb, jo, jt = json.loads(b), json.loads(o), json.loads(t)

# ---- launches: union by identity -> ts desc -> cap 50 -> re-sort asc (r245)
lo, lt = jo.get("launches", []), jt.get("launches", [])
seen, un = set(), []
for r in lo + lt:
    kk = tuple(r.get(f) for f in ("ts", "machine", "pid", "entry", "shard",
                                  "runner_sha256"))
    if kk not in seen:
        seen.add(kk)
        un.append(r)
print(f"launches: |ours|={len(lo)} |theirs|={len(lt)} union={len(un)}")
un_desc = sorted(un, key=lambda r: r.get("ts", ""), reverse=True)
capped = un_desc[:50]
capped.sort(key=lambda r: r.get("ts", ""))          # asc for write-back (r245)
print(f"cap50 kept={len(capped)} dropped={len(un)-len(capped)}")

out = dict(jo)
out["launches"] = capped

# ---- last_tick: internal ts compare, whole-dict assign, tie -> ours (r140)
lto, ltt = jo.get("last_tick"), jt.get("last_tick")
tso = lto.get("ts", "") if isinstance(lto, dict) else ""
tst = ltt.get("ts", "") if isinstance(ltt, dict) else ""
out["last_tick"] = lto if (tso, "") >= (tst, "") else ltt
assert isinstance(out["last_tick"], dict), "last_tick must stay dict (r140)"
print(f"last_tick: ours ts={tso} theirs ts={tst} -> "
      f"{'ours' if (tso, '') >= (tst, '') else 'theirs'}")

# ---- format mirror base blob: newline + indent probe (r223/r234)
crlf = b"\r\n" in b
m = re.search(rb"\n([ \t]+)\"last_tick\"", b)
indent = m.group(1).decode() if m else " "
print(f"format: crlf={crlf} indent={indent!r}")

data = json.dumps(out, ensure_ascii=False, indent=indent)
with io.open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(data.replace("\n", "\r\n" if crlf else "\n"))
json.loads(io.open(PATH, encoding="utf-8").read())
print("AUTOFILL-RESOLVE-OK")
