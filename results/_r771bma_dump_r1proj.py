# -*- coding: utf-8 -*-
"""r771 bm-a: dump pre-VM r1 projection region exact text."""
import io, json

RT = json.load(io.open(r"results/_r771bma_w155_runtime_strings.json", encoding="utf-8"))
s = RT["r1"]
for tok in ("projection", "first-clean", "W156"):
    j = 0
    while True:
        i = s.find(tok, j)
        if i < 0:
            break
        print(f"--- r1 [{tok}] @{i}")
        print(repr(s[max(0, i - 80):i + 330]))
        print()
        j = i + 1
