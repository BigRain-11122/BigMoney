# -*- coding: utf-8 -*-
# r931 line-map probe: every line containing shift-sensitive tokens (216-221 wave faces)
import io, re
t = io.open(r"results\_w221bmc_freeze_edits.py", encoding="utf-8").read().splitlines()
pat = re.compile(r"W21[6-9]|W22[01]|w21[6-9]|w22[01]|\b21[6-9]\b|\b22[01]\b|\[21[6-9]\]|\[22[01]\]|_21[6-9]|_22[01]")
for i, ln in enumerate(t, 1):
    if pat.search(ln):
        print(f"L{i}: {ln}")
