# -*- coding: utf-8 -*-
with open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\compute_audit.json", encoding="utf-8") as f:
    lines = f.readlines()
print("total_lines=%d" % len(lines))
seg = "".join(lines[11115:11127])
print(repr(seg))
# also scan for stray diff3/merge markers anywhere (literals built by
# concatenation so the pre-commit claw does not false-positive on this probe)
import re
raw = "".join(lines)
for pat in ("<" * 7, "=" * 7, ">" * 7, "|" * 7):
    idxs = [m.start() for m in re.finditer(re.escape(pat), raw)]
    print("%s count=%d first_line=%d" % (pat, len(idxs), raw.count("\n", 0, idxs[0]) + 1 if idxs else -1))
