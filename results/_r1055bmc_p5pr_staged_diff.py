# -*- coding: utf-8 -*-
"""r1055 absorb: diff staged-t region vs P5e-pr needle, char-exact."""
import io

ST = r"results\_r1055bmc_staged_t.txt"
ED = r"results\_w254bmc_derive_editor.py"

t = io.open(ST, encoding="utf-8").read()
ed = io.open(ED, encoding="utf-8").read()

i1 = ed.find('"P5e-pr")')
i0 = ed.rfind("chunk('''", 0, i1)
region = ed[i0:i1 + len('"P5e-pr")')]
parts = region.split("'''")
src = parts[1]


def xf(s):
    s = s.replace("W254", "W255")
    s = s.replace("253", "254")
    s = s.replace("252", "253")
    s = s.replace("MSG-20261016-12xx-bmc-w254-seat", "MSG-20261016-14xx-bmc-w254-seat")
    s = s.replace("r1050", "r1053")
    s = s.replace("r1052", "r1054")
    s = s.replace("978,735", "980,935")
    s = s.replace("552,320", "554,520")
    s = s.replace("SEVENTY-THIRD", "SEVENTY-FOURTH")
    s = s.replace("TWO HUNDRED AND FIFTY-THIRD", "TWO HUNDRED AND FIFTY-FOURTH")
    s = s.replace("forty-first consecutive", "forty-second consecutive")
    s = s.replace("bmc_ordinal=73", "bmc_ordinal=74")
    s = s.replace("authored 13:2x", "authored 18:0x")
    s = s.replace("f6433ee61", "fa70f3765")
    s = s.replace("741371846", "e2c4b543e")
    return s

needle = xf(src)
print("needle len", len(needle), "count in staged t:", t.count(needle))

j = t.find("A=1-HOP STAIRCASE-AFFECTS-A walk")
# align: needle starts with \n before the A=1-HOP line; find same anchor in needle
k = needle.find("A=1-HOP STAIRCASE-AFFECTS-A walk")
# staged region: start 60 chars before the anchor's line start
t_line_start = t.rfind("\n", 0, j) 
print("=== staged t region (from anchor line start, repr) ===")
print(repr(t[t_line_start:t_line_start + len(needle) + 60]))
print("=== needle (repr) ===")
print(repr(needle))
# longest common prefix
lo, hi = 0, min(len(needle), len(t) - t_line_start)
while lo < hi:
    mid = (lo + hi + 1) // 2
    if t[t_line_start:t_line_start + mid] == needle[:mid]:
        lo = mid
    else:
        hi = mid - 1
print("=== common prefix len:", lo)
print("needle continues:", repr(needle[lo:lo + 200]))
print("t continues:", repr(t[t_line_start + lo:t_line_start + lo + 200]))
