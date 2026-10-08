# -*- coding: utf-8 -*-
import io
import re
t = io.open(r"scripts\perpetual_faces_n1.py", encoding="utf-8", newline="").read()
for w in (187, 188, 189):
    i = t.find("# --- W%d materializer face" % w)
    j = t.find("# --- T-141 s2 lane face", i)
    seg = t[i:j]
    # pair each row assert with the stamp that FOLLOWS it
    pairs = re.findall(
        r"assert pf\.N1_BANDS\[(\d+)\] == \{\"a\": \((\d+_\d+), (\d+_\d+)\),"
        r"[\s\S]*?registered W(\d+) row parity drift \(r307; bm-a r(\d+)\)",
        seg)
    print("=== W%d mat: %d chain rows ===" % (w, len(pairs)))
    for row, a0, a1, stamp, sess in pairs[-4:]:
        print("  row[%s] bands %s..%s -> stamp W%s(r%s)" % (row, a0, a1, stamp, sess))
