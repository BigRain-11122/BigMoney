# -*- coding: utf-8 -*-
# r1019 bm-a: stale seat-suffix contexts + vacancy row-number face
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
t = open("_r1019bma_w246_prereg_frozen.txt", encoding="utf-8").read()
for pat in ["1328-bma-w245-seat", "bma-w246-seat", "785936d84", "零 245", "零 246", "245 行"]:
    for m in re.finditer(re.escape(pat), t):
        i = m.start()
        print(repr(t[max(0, i - 60):i + len(pat) + 20]))
    print("---")
