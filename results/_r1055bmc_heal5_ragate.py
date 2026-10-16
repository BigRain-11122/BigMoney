# -*- coding: utf-8 -*-
"""r1055 absorb heal-5: ra-gate dst key face <- actual W254 probe receipt keys
(receipt = machine truth: W251_W252_W253_bands_respected_A/B; dead window
authored W252_W253 — dst + anti-gate both healed, disclosed)."""
import io

ED = r"results\_w254bmc_derive_editor.py"
t = io.open(ED, encoding="utf-8", newline="").read()

edits = [
    ('ra.get("W252_W253_bands_respected_A") and ra.get("W252_W253_bands_respected_B")',
     'ra.get("W251_W252_W253_bands_respected_A") and ra.get("W251_W252_W253_bands_respected_B")',
     "heal5-dst-keys"),
    ('("W252_W253_bands_respected_A", 1),', '("W251_W252_W253_bands_respected_A", 1),', "heal5-antigate-A"),
    ('("W252_W253_bands_respected_B", 1),', '("W251_W252_W253_bands_respected_B", 1),', "heal5-antigate-B"),
]
for old, new, tag in edits:
    n = t.count(old)
    assert n == 1, f"[{tag}] count {n} != 1"
    t = t.replace(old, new)
    print(f"{tag}: applied")

io.open(ED, "w", encoding="utf-8", newline="").write(t)
print("heal-5 done")
