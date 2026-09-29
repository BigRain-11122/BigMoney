# -*- coding: utf-8 -*-
"""r438 bm-b: W9->W10 runner mechanical transform (step A only: copy +
global renames with probe-facts protection; semantic transplants follow
in steps B+ via targeted edits). Idempotent: refuses if target exists."""
import os
import sys

SRC = "scripts/trial_labor_w9.py"
DST = "scripts/trial_labor_w10.py"
PROTECT = [("_r431bmb_ampgate_w9_probe_facts", "@@P0@@"),
           ("_r417bmb_ampgate_probe_facts", "@@P1@@"),
           ("_r423bmb_w8tstate_probe_facts", "@@P2@@")]

if os.path.exists(DST):
    print("refuse: target exists"); sys.exit(2)
txt = open(SRC, encoding="utf-8").read()
for a, b in PROTECT:
    txt = txt.replace(a, b)
# ordered mechanical renames
txt = txt.replace("trial_labor_w9", "trial_labor_w10")
txt = txt.replace("_w9", "_w10")
txt = txt.replace("w9_", "w10_")
txt = txt.replace("W9", "W10")
txt = txt.replace("20309500", "20311000")
txt = txt.replace("20310000", "20311500")
txt = txt.replace("20310500", "20312000")
for a, b in PROTECT:
    txt = txt.replace(b, a)
open(DST, "w", encoding="utf-8", newline="\n").write(txt)
print("written", DST, len(txt), "bytes")
