# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
t = open(r"results\_w220bmc_freeze_edits.py", encoding="utf-8").read()
pats = ["EIGHTIETH", "TWO HUNDRED AND TWENTIETH", "MSG-20261012-0916", "r920",
        "@ r921 window", "PERPETUAL-N1-W220-SHARD-11", '220: {"batch"',
        "range(16, 220", "w220_prereg_sha", "w220_receipt_sha",
        "research/PERPETUAL_N1_W220_PREREG.md", "research/PERPETUAL_N1_W219_PREREG.md",
        "results/_w220bmc_20261012_probe_receipt.json", "50th own wave"]
for pat in pats:
    print("== %r count=%d" % (pat, t.count(pat)))
    for m in re.finditer(re.escape(pat), t):
        ln = t.count("\n", 0, m.start()) + 1
        ctx = t[max(0, m.start() - 60):m.start() + 60].replace("\n", " | ")
        print("  L%d: ...%s..." % (ln, ctx))
