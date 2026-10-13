# -*- coding: utf-8 -*-
"""r968 census-2: full context dump for remaining W232 derive tokens."""
import io, re
t = io.open(r"results\_w231bmc_freeze_edits.py", encoding="utf-8", newline="").read()
toks = [
 "NINETY-FIRST", "NINETY-SECOND", "61st", "rows 60 + candidate",
 "rows 220 + candidate", "engine_owner rows 220", "== 220 and len(bmc_rows_live) == 60",
 "expect 220/60", "precedent 219/59", "splice 220/60", "probe_receipt_bmc_ordinal_face",
 "bmc_ordinal=61", "r963", "r964", "r965", "r962", "r961", "2ae8553e6",
 "842f817ad", "1e5ed3326", "PERPETUAL_N1_W230_PREREG", '230: {"batch"',
 "w231_out_path", "n1_w230_results", "n1_w231_results", "_w231bmc_freeze_edits",
 "W232+ projection", "naive W232", "downstream W232", "probe receipt @ r963 window",
 "r963 freeze-window editor", "r963-continuation", "twentieth consecutive",
 "fifth consecutive", "FIFTEEN-level", "MSG-20261013-1155", "MSG-20261013-1000",
 "executed bm-c r962", "seat-time live face", "w<231 count", "if w < 230",
 "below-231", "below 231 composes", "89 rows", "86-row cut", "w228_leg = [",
 "w230_upstream", "w229_transitive", "w225_transitive", "w224_transitive",
 "w223_transitive", "w229_out_path", "w230_out_path", "w231_prereg_sha",
 "w231_receipt_sha", "60 live rows", "61st owned", "62nd",
 "seat published=reserved", "SEAT_ORIGIN", "fin_face", "T-141 s2 lane face",
 "arith_a231", "arith_b231", "n3r1_used231", "liveness_anchors", "block kept",
]
for tok in toks:
    n = t.count(tok)
    print("== %r %d" % (tok, n))
    if n <= 14:
        for m in re.finditer(re.escape(tok), t):
            s = max(0, m.start() - 44)
            print("   ", repr(t[s:m.end() + 44]))
