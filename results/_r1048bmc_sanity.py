# -*- coding: utf-8 -*-
import io

t = io.open("results/_w251bmc_freeze_edits.py", encoding="utf-8").read()
lines = t.split("\n")
print("total lines:", len(lines))
keys = ["b_hi < a_lo", "b_lo == a_hi + 1", "hops_B", "B_lands_above_own_A",
        "owner_rows_live) ==", "SEAT_MSG =", "SEAT_ORIGIN =", "arith_b251 =",
        "m234 =", "m239 =", "for _w in range(239",
        'WAVE_CONFIGS[251]["b_exit_seed_base"]', "assert b_lo", "hops_B\"]",
        '"b_exit_seed_base": {b_lo}', "n1_w251_results.json",
        "banned_direction_gate", "PERPETUAL_N1_W251_PREREG"]
for i, l in enumerate(lines, 1):
    if any(k in l for k in keys):
        print(i, "|", l.strip()[:132])
