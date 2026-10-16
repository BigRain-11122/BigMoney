# -*- coding: utf-8 -*-
import io

t = io.open("research/PERPETUAL_N1_W251_PREREG.md", encoding="utf-8").read()
for kw in ("W211..W233", "W234..W238", "estate "):
    j = t.find(kw)
    print(repr(kw), "at", j)
    if j >= 0:
        print(t[max(0, j - 500):j + 400].encode("unicode_escape").decode("ascii")[:1400])
        print()
