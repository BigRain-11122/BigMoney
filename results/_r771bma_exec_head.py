# -*- coding: utf-8 -*-
"""r771 bm-a: execute W155 editor definitions in a sandbox namespace (stop
before first edit() call), capture runtime strings, dump inventory."""
import io

src = io.open(r"results/_r768bma_w155_freeze_edits.py", "r", encoding="utf-8", newline="").read()
lines = src.splitlines(keepends=True)

# find first mutation line: edit(PF,
cut = None
for i, l in enumerate(lines):
    if l.startswith("edit(PF"):
        cut = i
        break
assert cut is not None
head = "".join(lines[:cut])
# neutralize any stray side effects: the head only defines strings/lists
ns = {"__name__": "_w155_head"}
exec(compile(head, "w155_head", "exec"), ns)
print("cut at line", cut)
keys = ["a1", "r1", "a2", "r2", "a3", "r3", "a4", "r4", "prereg_lines"]
inv = {}
for k in keys:
    if k in ns:
        v = ns[k]
        inv[k] = v
        print(f"{k}: {type(v).__name__} len={len(v) if hasattr(v,'__len__') else '-'}")
print()
print("=== a1 ==="); print(repr(ns["a1"])[:300])
print("=== r1 head ==="); print(repr(ns["r1"])[:500])
print("=== r1 tail ==="); print(repr(ns["r1"])[-500:])
print("=== a2 ==="); print(repr(ns["a2"])[:300])
print("=== r2 head ==="); print(repr(ns["r2"])[:400])
print("=== r2 tail ==="); print(repr(ns["r2"])[-300:])
print("=== a3 ==="); print(repr(ns["a3"]))
print("=== r3 head ==="); print(repr(ns["r3"])[:400])
print("=== r3 tail ==="); print(repr(ns["r3"])[-400:])
print("=== a4 ==="); print(repr(ns["a4"])[:300])
print("=== r4 ==="); print(repr(ns["r4"])[:600])
import json
json.dump({k: (v if isinstance(v, str) else v) for k, v in inv.items()},
          open(r"results/_r771bma_w155_runtime_strings.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved runtime strings json")
