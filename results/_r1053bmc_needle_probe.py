# -*- coding: utf-8 -*-
# r1053 helper: dump exact W252 narrative chunk texts for needle repair
import io, re
L = io.open(r"results/_w252bmc_freeze_edits.py", encoding="utf-8").read().splitlines()
for tag, pat, n in [
    ("HDR", r"NEW FACE vs the W251 editor", 16),
    ("BANDFACTS", r"W252 FACE \(probe receipt leg1", 17),
    ("PFCMT", r"band gate ADMIT results/_w252bmc", 14),
    ("PRE", r'"wave 252: "', 19),
    ("MEM_A", r"law sec\.4 W252 A:", 2),
    ("MEM_B", r"law sec\.4 W252 B:", 2),
    ("TAILCMT", r"band facts \(law sec\.4 W252 row", 25),
    ("PR", r'"A=1-HOP STAIRCASE-AFFECTS-A walk \(hops=1', 7),
    ("TAILMSG", r"W252 A staircase-affects-A walk: the naive", 8),
]:
    for i, l in enumerate(L):
        if re.search(pat, l):
            print("=== %s @%d ===" % (tag, i + 1))
            print("\n".join(L[i:i + n]))
            break
