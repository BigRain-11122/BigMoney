# -*- coding: utf-8 -*-
"""r901 bm-a W193 prereg freeze push-time re-derive (r590 law):
anchor wave + five-face vacancy, immediately before commit/push."""
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
G = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
subprocess.run(["git", "-C", G, "fetch", "origin"], capture_output=True)

r = subprocess.run(["git", "-C", G, "ls-tree", "origin/main",
                    "results/perpetual_faces/n1_w192_results.json"],
                   capture_output=True, text=True).stdout.strip()
print("W192 finalize product:", r if r else "ABSENT (anchor=W191 holds)")
assert r == "", "W192 finalize landed -- anchor must roll to W192 (r590)!"

needle = '193: {"a": (439_404'
r2 = subprocess.run(["git", "-C", G, "log", "origin/main", "--format=%h",
                     "-n", "1", "-S", needle, "--",
                     "scripts/perpetual_faces.py"],
                    capture_output=True, text=True).stdout.strip()
print("W193 five-face on origin:", r2 if r2 else "VACANT (no collision)")
assert r2 == "", "W193 five-face collision!"

r3 = subprocess.run(["git", "-C", G, "log", "origin/main", "--oneline", "-1"],
                    capture_output=True, text=True).stdout.strip()
print("origin tip:", r3[:80])
r4 = subprocess.run(["git", "-C", G, "rev-list", "--count", "main..origin/main"],
                    capture_output=True, text=True).stdout.strip()
print("behind origin:", r4)
print("PUSH-TIME RE-DERIVE GREEN")
