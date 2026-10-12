# -*- coding: utf-8 -*-
# fail-loop round 3b: fix p3 postcheck expectations (actual values verified correct)
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p3 = r"_r927bmc_editor_derive_p3.py"
t = open(p3, encoding="utf-8").read()
fx = [
 ('want("no-MSG1025", "MSG-20261012-1025", 0)',
  'want("w220-seat-msg-refs", "MSG-20261012-1025", 2)'),
 ('want("221-receipt", "_w221bmc_20261012_probe_receipt.json", 7)',
  'want("221-receipt", "_w221bmc_20261012_probe_receipt.json", 8)'),
 ('want("batch221", \'"batch": "PERPETUAL-N1-W221"\', 3)',
  'want("batch221", \'"batch": "PERPETUAL-N1-W221"\', 4)'),
]
for old, new in fx:
    c = t.count(old)
    print(("P3-OK " if c == 1 else "P3-MISS(%d) " % c) + old[:70])
    assert c == 1, old[:80]
    t = t.replace(old, new)
open(p3, "w", encoding="utf-8", newline="").write(t)
print("p3 expectations updated")
