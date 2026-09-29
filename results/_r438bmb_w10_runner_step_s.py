# -*- coding: utf-8 -*-
"""r438 bm-b step S: replace the W9-inherited selftest body in
trial_labor_w10.py with the W10 MOM-leg selftest (hermetic; W9 49-leg
caliber + MOM causality / 139-warmup / NaN-artifact / identity /
eight-gate intersection / G-MOM real-face anchors / draw determinism /
20-source exclusion loader / engine parity+determinism+bite legs /
null draw / funnel dispatch + CSV contract + pit-95 guards)."""
import sys

T = "scripts/trial_labor_w10.py"
NEW = open("results/_r438bmb_w10_selftest_body.py", encoding="utf-8").read()
txt = open(T, encoding="utf-8").read()
if "L1a mom_oversold causality" in txt:
    print("refuse: already transplanted"); sys.exit(2)
i0 = txt.index("def cmd_selftest() -> int:")
i1 = txt.index("def _build_parser():")
txt = txt[:i0] + NEW + "\n\n" + txt[i1:]
open(T, "w", encoding="utf-8", newline="\n").write(txt)
print("step S done:", len(txt), "bytes")
