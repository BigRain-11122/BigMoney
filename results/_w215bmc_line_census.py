# -*- coding: utf-8 -*-
# List all lines in the W214 editor containing wave tokens (213/214/W213/W214/band numbers)
# to build the explicit W215 derivation map. Read-only census.
import io, sys
sys.stdout.reconfigure(encoding="utf-8")
lines = io.open(r"results\_w214bmc_freeze_edits.py", encoding="utf-8").read().splitlines()
KEYS = ("213", "214", "W213", "W214", "485", "487", "489", "SEVENTY", "forty", "203",
        "0438", "d55a6b58b", "r908", "r909", "r910", "892", "466", "490", "TWO HUNDRED",
        "_w21", "n1_w", "PERPETUAL")
for i, l in enumerate(lines, 1):
    if any(k in l for k in KEYS):
        print(f"L{i}| {l.strip()[:150]}")
