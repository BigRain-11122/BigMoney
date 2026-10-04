# -*- coding: utf-8 -*-
"""r479 debug: CODELY.md union missing-line inventory (read-only)."""
import subprocess

C = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def blob(ref, path):
    p = subprocess.run(["git", "show", ref + ":" + path], capture_output=True,
                       creationflags=C, cwd=ROOT)
    return p.stdout


ob = blob("HEAD", "CODELY.md")
tb = blob("MERGE_HEAD", "CODELY.md")
o_lines = ob.split(b"\n")
t_set = set(tb.split(b"\n"))
missing = [ln for ln in o_lines if ln and ln not in t_set]
print("OURS_BYTES=%d THEIRS_BYTES=%d OURS_LINES=%d MISSING=%d" %
      (len(ob), len(tb), len(o_lines), len(missing)))
from collections import Counter
cnt = Counter(missing)
for ln, n in cnt.most_common():
    print("x%d %r" % (n, ln[:100]))
# also reverse: lines theirs has that ours lacks
t_lines = tb.split(b"\n")
o_set = set(o_lines)
tmiss = [ln for ln in t_lines if ln and ln not in o_set]
print("THEIRS_MISSING_FROM_OURS=%d" % len(tmiss))
for ln in tmiss[:6]:
    print("T %r" % ln[:100])
