# -*- coding: utf-8 -*-
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src = open("results/_r792bma_w164_probe.py", encoding="utf-8", newline="").read()
tmp = src
tmp = tmp.replace("W164-B-refuses-W165-A", "W165-B-refuses-W166-A")
tmp = tmp.replace("W165p", "W166p").replace("W165+", "W166+")
tmp = tmp.replace("PERPETUAL-N1-W164", "PERPETUAL-N1-W165")
tmp = tmp.replace("PERPETUAL_N1_W164_PREREG", "PERPETUAL_N1_W165_PREREG")
tmp = tmp.replace("_r792bma_w164", "_r793bma_w165")
tmp = tmp.replace("'164: {\"a\": ('", "'165: {\"a\": ('")
tmp = tmp.replace("W164", "W165").replace("W163", "W164").replace("w164", "w165")
for i, l in enumerate(tmp.splitlines(), 1):
    if "W163" in l:
        print(i, "|", l[:170])
