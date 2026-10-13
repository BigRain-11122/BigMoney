# -*- coding: utf-8 -*-
"""r968 census-4: transitive dep faces + last unknowns."""
import io, re
t = io.open(r"results\_w231bmc_freeze_edits.py", encoding="utf-8", newline="").read()
toks = [
 "w229_", "w225_", "w224_", "w223_", "w226_", "w227_", "n1_w229", "n1_w225",
 "n1_w224", "n1_w223", "927,589", "501,720", "925,389", "499,520",
 "918,789", "492,920", "916,589", "490,720", "914,389", "488,520",
 "w229_transitive", "w228_transitive", "11:5x", "13:2x", "12:4x",
 "engine_owner rows {", "rows 61 +", "= 61st owned", "61st owned",
 "MSG-1231", "wave 231", "w<230", "w<231", "range(16,231)", "range(17,231)",
 "below 230", "PRIOR", "block kept (W2", "_block_kept",
]
for tok in toks:
    n = t.count(tok)
    print("== %r %d" % (tok, n))
    if n <= 12:
        for m in re.finditer(re.escape(tok), t):
            s = max(0, m.start() - 46)
            print("   ", repr(t[s:m.end() + 46]))
