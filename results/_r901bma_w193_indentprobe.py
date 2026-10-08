# -*- coding: utf-8 -*-
"""r901 bm-a W193 freeze prep: indentation probe for WAVE_CONFIGS rows
and the pf N1_BANDS row + claim-block anchor shapes. Zero writes."""
import io

n1 = io.open("scripts/perpetual_faces_n1.py", encoding="utf-8",
             newline="").read()
pf = io.open("scripts/perpetual_faces.py", encoding="utf-8",
             newline="").read()

for key in ("191: {\"batch\"", "192: {\"batch\""):
    i = n1.find(key)
    ls = n1.rfind("\n", 0, i) + 1
    line = n1[ls:n1.find("\n", i)]
    print("n1 row %r leading=%d" % (key[:4], len(line) - len(line.lstrip(" "))))

i = pf.find("192: {\"a\"")
ls = pf.rfind("\n", 0, i) + 1
line = pf[ls:pf.find("\n", i)]
print("pf row 192 leading=%d %r" % (len(line) - len(line.lstrip(" ")),
                                    line[:44]))

# claim anchor shape after the W192 claim
i = n1.find('"r787 bm-c] "')
print("claim tail context: %r" % n1[i:i+60])

# cfg insertion segment uniqueness (engine_owner bm-c close + dict close)
seg = '"engine_owner": "bm-c"},\n' + " " * 23 + "}"
print("cfg close segment count:", n1.count(seg))

# pf row close segment (bm-c row + dict close)
seg2 = '"engine_owner": "bm-c"},\n}'
print("pf close segment count:", pf.count(seg2))
