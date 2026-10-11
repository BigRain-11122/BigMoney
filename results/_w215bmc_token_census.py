# -*- coding: utf-8 -*-
# Token census: enumerate wave-specific strings in the W214 freeze editor
# to build the complete W215 derivation replacement table (zero-omission proof).
import io, sys
sys.stdout.reconfigure(encoding="utf-8")
t = io.open(r"results\_w214bmc_freeze_edits.py", encoding="utf-8").read()
toks = ["W214", "W213", "W212", "W211", "W210", "W209", "SEVENTY-FOUR", "SEVENTY-FIFTH",
        "forty-four", "TWO HUNDRED AND FOURTEENTH", "0438", "d55a6b58b",
        "485604", "487604", "485404", "487803", "487_803", "489603", "489_603",
        "487_604", "485_604", "485_404", "466_520", "466520", "892_389", "892389",
        "485_604", "487_603", "203", "b0aa90376", "a24069f4c", "n1_w213", "n1_w214",
        "PERPETUAL_N1_W213", "PERPETUAL_N1_W214", "_w214bmc", "_w213bmc", "r910", "r909", "r908"]
for p in toks:
    print(f"{p!r}: {t.count(p)}")
