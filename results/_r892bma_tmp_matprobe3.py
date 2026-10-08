# -*- coding: utf-8 -*-
import io
import re
t = io.open(r"scripts\perpetual_faces_n1.py", encoding="utf-8", newline="").read()
for w in (187, 188, 189):
    i = t.find("# --- W%d materializer face" % w)
    j = t.find("# --- T-141 s2 lane face", i)
    seg = t[i:j]
    stamps = re.findall(r"registered W(\d+) row parity drift \(r307; bm-a r(\d+)\)", seg)
    rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]", seg)
    chain = rows[rows.index("138"):] if "138" in rows else rows
    print("W%d mat: stamps tail %s | row-index tail %s" % (w, stamps[-3:], chain[-3:]))
# show the last stamp + row + following comment for each
for w in (188, 189):
    i = t.find("# --- W%d materializer face" % w)
    k = t.find("parity drift", i)
    k2 = t.rfind("parity drift", i, t.find("# --- T-141 s2 lane face", i))
    seg = t[i:t.find("# --- T-141 s2 lane face", i)]
    m = re.search(r'"\r\n        assert pf\.N1_BANDS\[186\]', seg)
    print()
    print("=== W%d mat around row 186 ===" % w)
    k3 = seg.find('assert pf.N1_BANDS[186]')
    print(repr(seg[k3-120:k3+330]))
