# -*- coding: utf-8 -*-
# r1226 window: heal stale header prose in the cloned W322 splice editor.
import io

p = "results/_w322bmc_freeze_edits.py"
t = io.open(p, encoding="utf-8", newline="").read()

REP = [
    ("# 2026-10-25 00:5x bm-c r1224 splice window:",
     "# 2026-10-25 03:5x bm-c r1226 splice window:"),
    ("# block's own w<318> boundary is a legitimate prior-wave boundary: it moves from",
     "# block's own w<319> boundary is a legitimate prior-wave boundary: it moves from"),
    ("# the template's w<317> by exactly one).",
     "# the template's w<318> by exactly one)."),
    ("# window): A 721_501..723_500 (STAIRCASE-AFFECTS-A 1-hop walk, SEVENTY-FIFTH",
     "# window): A 723_701..725_700 (STAIRCASE-AFFECTS-A 1-hop walk, SEVENTY-FIFTH"),
    ("# consecutive A-hop; naive 721_301..723_300 refused at start by the registered",
     "# consecutive A-hop; naive 723_501..725_500 refused at start by the registered"),
    ("# W321 B band 721_301..721_500; A base == registered prior-wave B tail+1 EXACT)",
     "# W321 B band 723_501..723_700; A base == registered prior-wave B tail+1 EXACT)"),
    ("# and B 723_501..723_700 (1-hop own-A RESERVATION CASCADE above own-A, SEVENTY-SIXTH",
     "# and B 725_701..725_900 (1-hop own-A RESERVATION CASCADE above own-A, SEVENTY-SIXTH"),
    ("# consecutive above-own-A; naive 721_501..721_700 lands inside the own-wave A",
     "# consecutive above-own-A; naive 723_701..723_900 lands inside the own-wave A"),
]
for o, n in REP:
    c = t.count(o)
    assert c == 1, (c, o[:60])
    t = t.replace(o, n)
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("header prose healed")