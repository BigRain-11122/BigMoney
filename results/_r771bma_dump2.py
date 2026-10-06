# -*- coding: utf-8 -*-
"""r771 bm-a: dump W155 editor lines 82-160 (edit2 defs) and 395-419 (tail)."""
import io

s = io.open(r"results/_r768bma_w155_freeze_edits.py", "r", encoding="utf-8", newline="").read()
lines = s.splitlines()
for rng in [(82, 160), (160, 175), (375, 419)]:
    print(f"===== lines {rng[0]}..{rng[1]} =====")
    for i in range(rng[0], min(rng[1] + 1, len(lines))):
        print(f"{i:4d} {lines[i][:170]}")
    print()
