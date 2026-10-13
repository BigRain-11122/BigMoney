# -*- coding: utf-8 -*-
import io
t = io.open(r"results\_w230bmc_freeze_edits.py", encoding="utf-8", newline="").read()
for pat in ["_estate_ws[83]", "_estate_ws[84]", 'par_sec.count("assert pf.N1_BANDS[")',
            "par_full.count", "estate segment not", "69 estate + W211", "69 estate +"]:
    i = 0
    print("=== %r ===" % pat)
    while True:
        i = t.find(pat, i + 1)
        if i < 0:
            break
        print(repr(t[max(0, i - 100):i + 130]))
