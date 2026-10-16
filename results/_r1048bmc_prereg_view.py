# -*- coding: utf-8 -*-
# r1048 bm-c: extract W251 prereg sec.3 mandate + sec.5 projection faces (ASCII-safe echo)
import io, re

t = io.open("research/PERPETUAL_N1_W251_PREREG.md", encoding="utf-8").read()

def show(kw, span=420):
    m = re.search(re.escape(kw), t)
    if not m:
        print("MISS:", kw)
        return
    s = max(0, m.start() - 60)
    seg = t[s:m.start() + span]
    print("=== ", kw, " ===")
    print(seg.encode("unicode_escape").decode("ascii")[:1200])
    print()

for kw in ["sec.3", "estate", "W234..W238", "W239..W250", "109", "sec.5"]:
    show(kw)
