# -*- coding: utf-8 -*-
"""r1028 bm-c: runner command-dispatch map (absorb verification leg 2)."""
import io, re, sys

if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
t = io.open("scripts/trial_labor_w20.py", encoding="utf-8").read()
lines = t.splitlines()
# all def + dispatch lines with numbers
for i, ln in enumerate(lines, 1):
    if re.match(r"^def \w+", ln) or "args.command" in ln or "add_parser(" in ln or "choices=" in ln:
        print(i, ln[:150])
