# -*- coding: utf-8 -*-
import io, re
n2 = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8', newline='').read()
w2 = n2.find("# --- W161 materializer face")
t3 = n2.find("# --- T-141 s2 lane face", w2)
blk = n2[w2:t3]
i = blk.find("REGISTERED")
print(repr(blk[i:i+90]))
print("mat has bm-a r783 freeze ee04482a2:", "bm-a r783 freeze ee04482a2" in blk)
print("mat has 6957f509e:", "6957f509e" in blk)
print("all sha-like tokens in mat blk:", sorted(set(re.findall(r"ee0?4+42a2|ee44482a2|6957f509e|ee44442a2", blk))))
# check the BACK entry in the freeze script
fs = io.open('results/_r785bma_w161_freeze_edits.py', encoding='utf-8').read()
m = re.search(r'\("@MATROW@", "([^"]+)"\)', fs)
print("BACK @MATROW@ =", repr(m.group(1)) if m else "NOT FOUND")
vv = io.open('results/_r785bma_w161_freeze_verify.py', encoding='utf-8').read()
print("verify line:", [l for l in vv.splitlines() if 'mat header registered-row drift heal' in l and 'assert' in l])
