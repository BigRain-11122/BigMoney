# -*- coding: utf-8 -*-
import io
import re

t = io.open("results/_w302bmc_freeze_edits.py", encoding="utf-8").read()
pats = [r"FIFTY-\w+", r"NINETY\w*", r"HUNDRED[\w-]*", r"TWO HUNDRED[\w ]*",
        r"THREE HUNDRED\w*", r"parity rows", r"\b\d{3}_\d{3}\b",
        r"len\(bmc_rows_live\) == \d+", r"len\(owner_rows_live\) == \d+",
        r"\(expect [\d/]+\)", r"upstream_w\d+", r"_w\d+bmc", r"n1_w\d+",
        r"r118\d", r"w\d{3}_", r'"wave": \d+', r"wave \d+: ", r"range\(\d+, \d+, -1\)",
        r"MSG-[\w.:-]+", r"W\d{3}", r"\d{3}: \{", r"\d+_\d{6}", r"\d,\d{3},\d{3}"]
for p in pats:
    print("%-34s -> %s" % (p, sorted(set(re.findall(p, t)))))
print("batch N1-W302 count", t.count('"batch": "PERPETUAL-N1-W302"'))
print("bytes", len(t))