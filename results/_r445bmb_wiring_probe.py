# -*- coding: utf-8 -*-
"""_r445bmb_wiring_probe.py -- catalog every std/rsqr wiring point in the
W11 runner after the screen-prep gates (line >2100). Read-only."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src = open("scripts/trial_labor_w11.py", encoding="utf-8").read()
lines = src.split("\n")
pats = ("std_state", "std_meta", "std_face", "std_zeroed", "std_spec",
        "std_anchor", 'axis"][13', "AXIS_STD", "_std_", "std_key")
for i, l in enumerate(lines):
    if i <= 2100:
        continue
    if any(p in l for p in pats):
        print(i + 1, repr(l[:108]))
