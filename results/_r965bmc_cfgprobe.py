# -*- coding: utf-8 -*-
import io
t = io.open(r"results\_w230bmc_freeze_edits.py", encoding="utf-8", newline="").read()
for pat in ['230: {"batch', '229: {"batch', '230: {"a', '229: {"a']:
    print("=== %r ===" % pat)
    i = 0
    while True:
        i = t.find(pat, i + 1)
        if i < 0:
            break
        print(repr(t[max(0, i - 90):i + 70]))
