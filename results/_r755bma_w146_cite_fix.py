# -*- coding: utf-8 -*-
"""r755 bm-a W146 gate-tail citation fix: the W146 A-refusal anticipation came
from the W145 gate leg3 = _r753bma_w145_band_gate.py (r753 window script round,
per the script-anchored convention: 'r752 W144 gate-tail' in the W145 face).
PART 1/2 wrote 'r754' (freeze-round attribution) -- surgical fix to r753 in the
two law faces. Seat MSG already pushed (history preserved, disclosed in round
report). Needle-asserted."""
import io

pairs_pf = [("r754 W145 gate-tail", "r753 W145 gate-tail", 1)]
pf_path = r"scripts\perpetual_faces.py"
pf = io.open(pf_path, encoding="utf-8").read()
for old, new, expect in pairs_pf:
    n = pf.count(old)
    assert n == expect, f"pf: count={n} expect={expect}: {old!r}"
    pf = pf.replace(old, new)
io.open(pf_path, "w", encoding="utf-8", newline="\n").write(pf)
print("pf: gate-tail citation r754->r753 fixed (1)")

n1_path = r"scripts\perpetual_faces_n1.py"
n1 = io.open(n1_path, encoding="utf-8").read()
pairs_n1 = [
    ("r754 W145 gate-tail", "r753 W145 gate-tail", 6),   # wc_new x2 + prose x2 + face band-facts x2 (anticipated + convergence forms)
    ("the r754 gate-tail", "the r753 gate-tail", 1),     # face A assert
]
for old, new, expect in pairs_n1:
    n = n1.count(old)
    assert n == expect, f"n1: count={n} expect={expect}: {old!r}"
    n1 = n1.replace(old, new)
io.open(n1_path, "w", encoding="utf-8", newline="\n").write(n1)
print("n1: gate-tail citations fixed")
