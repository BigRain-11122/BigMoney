# -*- coding: utf-8 -*-
"""r1055 dbg-2: diff the pre-chunk needle against the dumped intermediate t."""
import io

t = io.open(r"results\_r1055bmc_t_dump.txt", encoding="utf-8").read()
ed = io.open(r"results\_w254bmc_derive_editor.py", encoding="utf-8").read()

i1 = ed.find('"P5e-pre")')
i0 = ed.rfind("chunk('''", 0, i1)
region = ed[i0:i1 + len('"P5e-pre")')]
parts = region.split("'''")
src = parts[1]

# replicate xf
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
print("needle len", len(needle), "count in t:", t.count(needle))
# longest prefix of needle present in t
lo, hi = 0, len(needle)
while lo < hi:
    mid = (lo + hi + 1) // 2
    if t.count(needle[:mid]):
        lo = mid
    else:
        hi = mid - 1
print("longest matching prefix:", lo)
print("...prefix tail:", repr(needle[max(0, lo-80):lo]))
print("...needle continues:", repr(needle[lo:lo+140]))
# where does that prefix sit in t?
j = t.find(needle[:lo]) if lo else -1
if j >= 0:
    print("t continues at that point:", repr(t[j+lo:j+lo+140]))
