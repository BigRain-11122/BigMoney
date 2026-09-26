# -*- coding: utf-8 -*-
"""R252 bm-a: target uniqueness for div/t33 (read-only)."""
import io

for p, tt in {
    "results/div_lowvol_p1.json": ['"ledger": {', '"prev_total": 182952', '"total": 182988'],
    "results/t33_attack_wave.json": ['"ledger": {'],
}.items():
    t = io.open(p, encoding="utf-8-sig").read()
    print(p)
    for s in tt:
        print("  ", repr(s), "count=", t.count(s))
