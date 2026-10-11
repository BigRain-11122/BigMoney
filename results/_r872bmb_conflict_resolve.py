# -*- coding: utf-8 -*-
"""r872 rebase conflict resolver: queue_head_collision_probe.json
machine_id face, newer-wins = bm-b (local probe run 09:01:47 this round
vs bm-c r862 probe <08:59:17 commit b9475e6c6); verdict face identical
CLEAR on both sides -- zero information loss either way."""
import io
import json

P = "results/queue_head_collision_probe.json"
t = io.open(P, encoding="utf-8").read()
lines = t.splitlines()
out = []
mode = None
for ln in lines:
    if ln.startswith("<<<<<<<"):
        mode = "ours"
        continue
    if ln.startswith("=======") and mode == "ours":
        mode = "skip_theirs"
        continue
    if ln.startswith(">>>>>>>") and mode == "skip_theirs":
        mode = None
        continue
    if mode == "ours" or mode is None:
        out.append(ln)
t2 = "\n".join(out) + "\n"
t2 = t2.replace('"machine_id": "bm-c"', '"machine_id": "bm-b"')
j = json.loads(t2)
assert j["machine_id"] == "bm-b" and j["verdict"] == "CLEAR"
assert "<<<<<<<" not in t2 and "=======" not in t2
io.open(P, "w", encoding="utf-8", newline="\n").write(t2)
print("resolved: machine_id=bm-b newer-wins, verdict CLEAR both sides")
