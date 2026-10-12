# -*- coding: utf-8 -*-
# fail-loop round 3: remove double-shift corruption sources (prg pairs redundant
# -- the W-passes natively produce correct prereg paths; hdr2 must not carry W tokens)
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

p2 = r"_r927bmc_editor_derive_p2.py"
t = open(p2, encoding="utf-8").read()

# 1. hdr2: strip W tokens (W219->W220 shift belongs to the W-passes)
old_hdr2 = 'rep("hdr2", "(W219 finalize one-pass 10:1x, net chain head 905,589,", "(W220 finalize one-pass 12:0x, net chain head 907,789,")'
new_hdr2 = 'rep("hdr2b", "finalize one-pass 10:1x, net chain head 905,589,", "finalize one-pass 12:0x, net chain head 907,789,")'
assert t.count(old_hdr2) == 1, "hdr2 anchor miss"
t = t.replace(old_hdr2, new_hdr2)

# 2. drop the four prg pairs (redundant: W-passes shift W220->W221 own + W219->W220 upstream natively)
prg_block_start = 'rep("prg1", "research/PERPETUAL_N1_W220_PREREG.md", "research/PERPETUAL_N1_W221_PREREG.md", 4)'
prg_block_end = 'rep("prg2b", \'"\PERPETUAL_N1_W219_PREREG.md"\', \'"\PERPETUAL_N1_W220_PREREG.md"\')'
prg_block_end = prg_block_end.replace("\PERPETUAL", "PERPETUAL")
i = t.find(prg_block_start)
j = t.find(prg_block_end)
assert i >= 0 and j >= 0 and j > i, "prg block anchors miss"
j += len(prg_block_end)
t = t[:i] + "# (prereg paths shift natively via the W-passes -- prg pairs removed, double-shift bug fixed)" + t[j:]

open(p2, "w", encoding="utf-8", newline="").write(t)
print("p2 round-3 patched (hdr2b + prg pairs removed)")

p3 = r"_r927bmc_editor_derive_p3.py"
t3 = open(p3, encoding="utf-8").read()
fx = [
 ('want("no-MSG1025", "MSG-20261012-1025", 0)',
  'want("w220-seat-msg-refs", "MSG-20261012-1025", 2)'),
 ('want("221-receipt", "_w221bmc_20261012_probe_receipt.json", 7)',
  'want("221-receipt", "_w221bmc_20261012_probe_receipt.json", 8)'),
 ('want(\'batch221\', \'"batch": "PERPETUAL-N1-W221"\', 3)',
  'want(\'batch221\', \'"batch": "PERPETUAL-N1-W221"\', 4)'),
]
for old, new in fx:
    c = t3.count(old)
    print(("P3-OK " if c == 1 else "P3-MISS(%d) " % c) + old[:60])
    assert c == 1, old[:80]
    t3 = t3.replace(old, new)
open(p3, "w", encoding="utf-8", newline="").write(t3)
print("p3 postchecks updated")
