# -*- coding: utf-8 -*-
"""One-off probe: dump editor lines containing the literals the gen must rewrite."""
import io
import re

s = io.open("results/_w309bmc_freeze_edits.py", encoding="utf-8").read().split("\n")
pats = [r"\b\d{3}_\d{3}\b", r"batch", r"parity rows", r"legs \(", r"SIXTY", r"HUNDRED-AND",
        r"THREE HUNDRED", r"range\(", r"1_101_941", r"675_520", r'"wave"', r"wave 3", r"CFG_I"]
rx = re.compile("|".join(pats))
out = []
for i, l in enumerate(s, 1):
    if rx.search(l):
        out.append("%d|%s" % (i, l))
io.open("results/_w310bmc_editor_lines.txt", "w", encoding="utf-8").write("\n".join(out))
print(len(out))