# -*- coding: utf-8 -*-
"""_r445bmb_baseaxis_probe.py -- measure exact indentation of the L13
base axis-list lines in the frozen W11 runner (surgeon operates on W11
source, not the draft). Read-only."""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src = open("scripts/trial_labor_w11.py", encoding="utf-8").read()
i = src.find('"axis": ["none", "time_stop_5d"')
print("found at", i)
j = src.rfind("\n", 0, i)
k = src.find("]}", i)
seg = src[j + 1:k + 2]
for ln in seg.split("\n"):
    print(repr(ln))
print("---draft copy---")
d = open("results/_r445bmb_w12_runner_draft.py", encoding="utf-8").read()
i2 = d.find('"axis": ["none", "time_stop_5d"')
j2 = d.rfind("\n", 0, i2)
k2 = d.find("]}", i2)
for ln in d[j2 + 1:k2 + 2].split("\n"):
    print(repr(ln))
