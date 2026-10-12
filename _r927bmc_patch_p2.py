# -*- coding: utf-8 -*-
# patch p2 pair counts (fail-loop round 2)
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"_r927bmc_editor_derive_p2.py"
t = open(p, encoding="utf-8").read()
fixes = [
 ('rep("rcpt1", "results/_w220bmc_20261012_probe_receipt.json", "results/_w221bmc_20261012_probe_receipt.json", 7)',
  'rep("rcpt1", "results/_w220bmc_20261012_probe_receipt.json", "results/_w221bmc_20261012_probe_receipt.json", 8)'),
 ('rep("prg1", "research/PERPETUAL_N1_W220_PREREG.md", "research/PERPETUAL_N1_W221_PREREG.md", 5)',
  'rep("prg1", "research/PERPETUAL_N1_W220_PREREG.md", "research/PERPETUAL_N1_W221_PREREG.md", 4)\n'
  'rep("prg1b", \'"\PERPETUAL_N1_W220_PREREG.md"\', \'"\PERPETUAL_N1_W221_PREREG.md"\')'),
 ('rep("prg2", "research/PERPETUAL_N1_W219_PREREG.md", "research/PERPETUAL_N1_W220_PREREG.md", 3)',
  'rep("prg2", "research/PERPETUAL_N1_W219_PREREG.md", "research/PERPETUAL_N1_W220_PREREG.md", 2)\n'
  'rep("prg2b", \'"\PERPETUAL_N1_W219_PREREG.md"\', \'"\PERPETUAL_N1_W220_PREREG.md"\')'),
 ('rep("own1", "w220_prereg_sha", "w221_prereg_sha", 4)',
  'rep("own1", "w220_prereg_sha", "w221_prereg_sha", 5)'),
 ('rep("own2", "w220_receipt_sha", "w221_receipt_sha", 3)',
  'rep("own2", "w220_receipt_sha", "w221_receipt_sha", 4)'),
 ('rep("seatwin1", "@ r921 window; per-wave prereg + ", "@ r924 window; per-wave prereg + ", 2)',
  'rep("seatwin1", "@ r921 window; per-wave prereg +", "@ r924 window; per-wave prereg +", 2)'),
 ('rep("seatwin2", "MSG-20261012-0916, executed bm-c r919 seat window; engine self-burn 12/12",\n'
  '    "MSG-20261012-1025, executed bm-c r921 seat window; engine self-burn 12/12", 2)',
  'rep("seatwin2a", "MSG-20261012-0916, executed bm-c r920 freeze window; engine self-burn 12/12",\n'
  '    "MSG-20261012-1025, executed bm-c r923 freeze window; engine self-burn 12/12")\n'
  'rep("seatwin2b", "MSG-20261012-0916, executed bm-c r919 seat window; engine self-burn 12/12",\n'
  '    "MSG-20261012-1025, executed bm-c r921 seat window; engine self-burn 12/12")'),
 ('rep("ord2", "EIGHTIETH", "EIGHTY-FIRST", 5)',
  'rep("ord2", "EIGHTIETH", "EIGHTY-FIRST", 7)'),
 ('rep("ord4", "TWO HUNDRED AND TWENTIETH", "TWO HUNDRED AND TWENTY-FIRST", 2)',
  'rep("ord4", "TWO HUNDRED AND TWENTIETH", "TWO HUNDRED AND TWENTY-FIRST", 3)'),
 ('rep("ord7", "(50th own wave per live derive r587/r359; probe receipt leg0 bmc_ordinal=50 seat-time live face disclosed)",\n'
  '    "(51st own wave per live derive r587/r359; probe receipt leg0 bmc_ordinal=51 seat-time live face disclosed)")',
  'rep("ord7a", "(50th own wave per live derive r587/r359; ",\n'
  '    "(51st own wave per live derive r587/r359; ")\n'
  'rep("ord7b", "probe receipt leg0 bmc_ordinal=50 seat-time live face disclosed)",\n'
  '    "probe receipt leg0 bmc_ordinal=51 seat-time live face disclosed)")'),
 ('rep("n5", "\'220: {\\"batch\\"\'", "\'221: {\\"batch\\"\'", 2)',
  'rep("n5", "\'220: {\\"batch\\"", "\'221: {\\"batch\\"", 2)'),
 ('rep("n19", "range(16, 220]", "range(16, 221]")',
  'rep("n19", "range(16, 220)", "range(16, 221)")'),
 ('rep("n20", "arith_a220", "arith_a221", 2)',
  'rep("n20", "arith_a220", "arith_a221", 3)'),
 ('rep("n21", "arith_b220", "arith_b221", 2)',
  'rep("n21", "arith_b220", "arith_b221", 3)'),
 ('rep("n24", "PERPETUAL-N1-W220-SHARD-11", "PERPETUAL-N1-W221-SHARD-11", 2)',
  'rep("n24", "PERPETUAL-N1-W220-SHARD-11", "PERPETUAL-N1-W221-SHARD-11")'),
 ('rep("n27", \'"batch": "PERPETUAL-N1-W220"\', \'"batch": "PERPETUAL-N1-W221"\', 3)',
  'rep("n27", \'"batch": "PERPETUAL-N1-W220"\', \'"batch": "PERPETUAL-N1-W221"\', 4)'),
]
for old, new in fixes:
    old2 = old.replace("\PERPETUAL", "PERPETUAL")
    new2 = new.replace("\PERPETUAL", "PERPETUAL")
    c = t.count(old2)
    print(("FIX-OK " if c == 1 else "FIX-MISS(%d) " % c) + old2[:60])
    assert c == 1, "patch anchor miss: " + old2[:80]
    t = t.replace(old2, new2)
open(p, "w", encoding="utf-8", newline="").write(t)
print("p2 patched")
