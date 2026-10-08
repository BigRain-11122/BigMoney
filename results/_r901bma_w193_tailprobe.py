# -*- coding: utf-8 -*-
"""r901 bm-a W193 five-face prep: literal-tail probe of the current W192
materializer face (row keys x message stamps) + W191-face base comparison.
Zero writes; prints facts for the freeze-edits pair list."""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

t = io.open("scripts/perpetual_faces_n1.py", encoding="utf-8",
            newline="").read().replace("\r\n", "\n")

PAT = re.compile(
    r'assert pf\.N1_BANDS\[(\d+)\] == \{"a": \((\d+_\d+), (\d+_\d+)\),'
    r'\s*\n\s*"b_exit": \((\d+_\d+), (\d+_\d+)\),'
    r'\s*\n\s*"engine_owner": "(bm-[ac])"\}, \\'
    r'\s*\n\s*"registered (W\d+) row parity drift \(r307; ([^)]+)\)"')

for face in ("W191", "W192"):
    i = t.find("    # --- %s materializer face" % face)
    j = t.find("\n    # --- T-141 s2 lane face", i)
    blk = t[i:j]
    rows = PAT.findall(blk)
    print("=== %s face: %d literal rows, tail: ===" % (face, len(rows)))
    for r in rows[-4:]:
        print("  row %s a=%s..%s b=%s..%s owner=%s | msg %s @ %s"
              % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))

# also: which lines hold the W189/W190/W191 stamps in the W192 face
i = t.find("    # --- W192 materializer face")
blk = t[i:t.find("\n    # --- T-141 s2 lane face", i)]
for m in re.finditer(r'"registered (W\d+) row parity drift \(r307; ([^)]+)\)"',
                     blk):
    print("W192-face msg:", m.group(1), "@", m.group(2))
