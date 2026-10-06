# -*- coding: utf-8 -*-
"""r771 bm-a: dump the W155 freeze-edits editor structure (edits, anchors,
injected blocks, gates, calls) to plan a direct W156 rewrite."""
import io, re

s = io.open(r"results/_r768bma_w155_freeze_edits.py", "r", encoding="utf-8", newline="").read()
lines = s.splitlines()
print("TOTAL LINES:", len(lines))
for i, l in enumerate(lines):
    tag = None
    if re.match(r"^# ---", l):
        tag = "SEC"
    elif re.match(r"^(edit|run|gate|ast|probe|selftest|sub|assert)", l):
        tag = "CALL"
    elif re.match(r"^(a1|a2|a3|a4|w155_row|r2|LEG|snip|prereg_lines|W155_PARITY|pairs)\s*=", l):
        tag = "DEF"
    if tag:
        print(f"{i:5d} {tag:4s} {l[:150]}")
