# -*- coding: utf-8 -*-
"""r1055 absorb heal: P5e-pr first-line leading space (src+dst), disclosed needle heal."""
import io

ED = r"results\_w254bmc_derive_editor.py"
t = io.open(ED, encoding="utf-8", newline="").read()

OLD = "\n'          \"A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim, A_clean_at_naive_start=false, \"',"
NEW = "\n '          \"A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim, A_clean_at_naive_start=false, \"',"
n = t.count(OLD)
assert n == 2, f"expect 2 occurrences (src+dst first lines), found {n}"
t2 = t.replace(OLD, NEW)
io.open(ED, "w", encoding="utf-8", newline="").write(t2)
print("P5e-pr first-line heal applied: 2 occurrences (src line 453 + dst line 461)")
