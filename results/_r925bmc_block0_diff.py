# -*- coding: utf-8 -*-
# debug: diff replay block0 vs freeze-time blob (bm-c r925)
import difflib, os, sys
sys.stdout.reconfigure(encoding="utf-8")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(REPO)
src = open(r"results/_r925bmc_w221_replay_dump.py", encoding="utf-8").read()
body = src.split("# preflight")[0]
g = {}
exec(body, g)
OLD20 = g["OLD20"]; t = g["t"]
b0 = OLD20[0]
head = b0[:40]
i = t.find(head)
print("head found at:", i)
if i >= 0:
    seg = t[i:i + len(b0) + 300]
    sm = difflib.SequenceMatcher(None, b0, seg)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            print(tag, "replay[", i1, ":", i2, "]=", repr(b0[i1:i2])[:200])
            print("     blob[", j1, ":", j2, "]=", repr(seg[j1:j2])[:200])
else:
    print("head not found; first 150 of replay block0:")
    print(repr(b0[:150]))
    j = t.find("PERPETUAL-N1-W220")
    print("blob head:", repr(t[j:j + 420]) if j >= 0 else "n/a")
