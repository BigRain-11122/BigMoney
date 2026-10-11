# -*- coding: utf-8 -*-
# Review the W215 editor diff hunk-by-hunk: every -/+ pair printed for eyeball audit.
import io, difflib, sys
sys.stdout.reconfigure(encoding="utf-8")
a = io.open(r"results\_w214bmc_freeze_edits.py", encoding="utf-8").read().splitlines()
b = io.open(r"results\_w215bmc_freeze_edits.py", encoding="utf-8").read().splitlines()
d = list(difflib.unified_diff(a, b, lineterm="", n=0))
out = []
hunk = 0
for l in d:
    if l.startswith("@@"):
        hunk += 1
        out.append(f"\n=== HUNK {hunk} {l}")
    elif l.startswith("-") or l.startswith("+"):
        out.append(l[:200])
open(r"results\_w215bmc_editor_diff.txt", "w", encoding="utf-8").write("\n".join(out))
print("hunks:", hunk, "| written to results/_w215bmc_editor_diff.txt")
