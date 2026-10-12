# -*- coding: utf-8 -*-
import io
t = io.open(r"results\_w223bmc_freeze_edits.py", encoding="utf-8").read()
probes = [
    "assert (a_lo, a_hi) == (505_404, 507_403)",
    "assert (b_lo, b_hi) == (507_404, 507_603)",
    "assert w222_total == 912_189 and w222_merged_n == 486_320",
    'SEAT_MSG = "MSG-20261012-160x-bmc-w223-seat.md"',
    'SEAT_ORIGIN = "8f2d79147"',
    'assert rec["verdict"] == "ADMIT"',
    "assert len(owner_rows_live) == 212 and len(bmc_rows_live) == 52",
    "_set_wave(223)",
    "EIGHTY-FOURTH instance anticipated",
    "int(_estate_ws[78])",
    "81 rows",
    '"w222_block_kept": 1',
    "W222 splice landed r931 window",
    "bmc_ordinal=53",
    "r932 finalize one-pass",
    "in the r933 window (b7d46427d, SEVEN-level lineage replay chain",
]
bad = 0
for p in probes:
    n = t.count(p)
    ok = "OK " if n >= 1 else "MISS"
    if n < 1:
        bad += 1
    print(f"{ok} n={n} | {p[:70]}")
print("BAD:", bad)
