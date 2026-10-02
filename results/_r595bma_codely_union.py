# -*- coding: utf-8 -*-
"""CODELY.md zero-loss union (origin dropped the r594 bm-a entry; restore + append my 2)
+ T-145 ticket key-level union (script died before this step)."""
import json, subprocess

def show(ref):
    return subprocess.run(["git", "show", ref], capture_output=True).stdout

old = show("5d234b3d7:CODELY.md").replace(b"\r\n", b"\n")
origin = show("origin/main:CODELY.md").replace(b"\r\n", b"\n")
local = open("CODELY.md", "rb").read().replace(b"\r\n", b"\n")
assert local.startswith(old), "local not superset of old"
mine = local[len(old):]  # blank + e1 + blank + e2 tail

old_lines, origin_lines = old.split(b"\n"), origin.split(b"\n")
origin_set = set(origin_lines)
dropped = [l for l in old_lines if l not in origin_set and l.strip()]
assert len(dropped) == 1, f"expected exactly 1 dropped entry, got {len(dropped)}"
entry = dropped[0]
print("restoring dropped entry:", entry[:60].decode("utf-8", "replace"), "...")
anchor = b"- [2026-10-02 21:2x r595 bm-b]"
i = next(idx for idx, l in enumerate(origin_lines) if l.startswith(anchor))
merged_lines = origin_lines[:i] + [b"", entry, b""] + origin_lines[i:]
merged = b"\n".join(merged_lines)
if not merged.endswith(b"\n"):
    merged += b"\n"
merged += mine if mine.startswith(b"\n") else b"\n" + mine
open("CODELY.md", "wb").write(merged.replace(b"\n", b"\r\n"))

# verify: all four faces present
for probe in [b"21:2x r594 bm-a", b"21:2x r595 bm-b", b"21:5x r595 bm-a"]:
    n = merged.count(probe)
    print("probe", probe.decode(), "count", n)
    assert n >= 1
print("CODELY merged lines:", len(merged_lines))

# T-145 ticket union (key-level)
tp = "fleet/tasks/T-2026-10-02-145-P1.json"
j_old = json.loads(show(f"5d234b3d7:{tp}"))
j_new = json.loads(show("origin/main:" + tp))
j_loc = json.loads(open(tp, "rb").read().decode("utf-8"))
added_local = [k for k in j_loc if k not in j_old]
added_origin = [k for k in j_new if k not in j_old]
for k in added_origin:
    if k in j_loc:
        assert j_loc[k] == j_new[k], f"conflict on {k}"
    j_loc[k] = j_new[k]
open(tp, "wb").write(json.dumps(j_loc, ensure_ascii=False, indent=1).encode("utf-8"))
print("T-145 union local keys:", added_local, "+ origin keys:", added_origin)
