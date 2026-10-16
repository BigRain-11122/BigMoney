# -*- coding: utf-8 -*-
import io
t = io.open(r"results/_w253bmc_freeze_edits.py", encoding="utf-8").read()
for k in [
    "assert (a_lo, a_hi) == (571_901, 573_900)",
    "bands A 571_901..573_900",
    "fresh legs W239..W252",
    "assert len(owner_rows_live) == 242",
    "assert w252_total == 978_735",
    'SEAT_ORIGIN + " r1050',
    "range(239, 253)",
    "_w253bmc_freeze_receipt.json",
    "bmc_ordinal=73",
    "SECOND consecutive A-hop",
    "THIRD consecutive above-own-A",
]:
    print(t.count(k), "|", k[:60])
print("--- header ---")
print(t[:420])
