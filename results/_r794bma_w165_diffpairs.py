# -*- coding: utf-8 -*-
"""r794 bm-a: unified-diff the three procedural tool pairs (W163->W164) with
pure python (no PS UTF-16 redirect), summarizing changed line pairs per tool
for the v2 deriver site inventory."""
import difflib
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PAIRS = [
    ("face", r"results/_r789bma_w163_face_probe.py",
     r"results/_r792bma_w164_face_probe.py"),
    ("edits", r"results/_r789bma_w163_freeze_edits.py",
     r"results/_r792bma_w164_freeze_edits.py"),
    ("verify", r"results/_r789bma_w163_freeze_verify.py",
     r"results/_r792bma_w164_freeze_verify.py"),
]

for name, pa, pb in PAIRS:
    a = io.open(pa, encoding="utf-8", newline="").read().split("\n")
    b = io.open(pb, encoding="utf-8", newline="").read().split("\n")
    diff = list(difflib.unified_diff(a, b, lineterm="", n=0))
    changed = [ln for ln in diff
               if (ln.startswith("+") or ln.startswith("-"))
               and not ln.startswith(("+++", "---", "@@"))]
    out = f"results/_r794bma_diffpairs_{name}.txt"
    with io.open(out, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(changed))
    print(name, "changed lines:", len(changed), "->", out)
