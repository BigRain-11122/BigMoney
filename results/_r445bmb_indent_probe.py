# -*- coding: utf-8 -*-
"""_r445bmb_indent_probe.py -- measure exact leading-space counts of the
judge-final-audit-stop-note anchor lines in the frozen W11 runner, plus the
surgeon's expected anchor indent. Read-only."""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
lines = open("scripts/trial_labor_w11.py", encoding="utf-8").read().split("\n")
for n in range(3615, 3621):
    l = lines[n - 1]
    print(n, "indent=", len(l) - len(l.lstrip(" ")), repr(l[:55]))
src = open("results/_r445bmb_w12_surgeon.py", encoding="utf-8").read()
i = src.find('"the protection-floor')
j = src.rfind("'", 0, i)
# find start-of-string literal spaces: walk back over spaces+quote
k = i
while src[k] != "'":
    k -= 1
pre = src[k + 1:i - 0]
# count spaces between opening quote and the double-quote char
sp = 0
for ch in src[k + 1:i + 1]:
    if ch == " ":
        sp += 1
    else:
        break
print("surgeon anchor spaces before text =", sp)
