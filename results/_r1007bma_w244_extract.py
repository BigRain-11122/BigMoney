# -*- coding: utf-8 -*-
# r1007: extract exact template bytes for the semantic blocks I must author
import io
t = io.open(r"results/_w243bma_freeze_edits.py", encoding="utf-8").read()
lines = t.split("\n")

def show(a, b, tag):
    print("=== %s (lines %d-%d) ===" % (tag, a, b))
    for i in range(a - 1, b):
        print(repr(lines[i]))

show(21, 28, "HEADER-DISCLOSURE")
# print line B fragments
i0 = None
for i, l in enumerate(lines):
    if 'B=LIVE-SEED-REFUSAL face' in l:
        i0 = i
        break
show(i0 + 1 - 2, i0 + 1 + 4, "PRINT-B-REGION")
# receipt band_semantics B
for i, l in enumerate(lines):
    if '"B": "LIVE-SEED-REFUSAL' in l:
        show(i + 1, i + 1, "RECEipt-B-SEMANTICS")
        break
# downstream seat
for i, l in enumerate(lines):
    if '"downstream_seat"' in l:
        show(i + 1, i + 1, "DOWNSTREAM-SEAT")
        break
# fin_face
for i, l in enumerate(lines):
    if 'fin_face = ' in l:
        show(i + 1, i + 1 + 6, "FIN-FACE")
        break
