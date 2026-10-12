# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
t = open(r"results\_w221bmc_freeze_edits.py", encoding="utf-8").read().splitlines()
print("==== header 1-32 ====")
for i, l in enumerate(t[:32], 1):
    print(i, l[:160])
print("==== gate anchors ====")
keys = ["expect 210/50", "907_789", "(501_004, 503_003)", "w220_b_tail + 1 == a_lo",
        'leg1["ARITH_A"]', "assert w220_total", "owner_rows_live) == 210", "bmc_rows_live) == 50",
        "par_sec.count", "par_full.count", "_estate_ws[76]", "== 78, ", "== 77 \\",
        "WAVE_CONFIGS[221]", "_set_wave(221)", "range(17, 221)", "range(16, 221)",
        "w221_prereg_sha = (", "SEAT_MSG = ", "SEAT_ORIGIN = ", "RECEIPT_IN = ", "RECEIPT_OUT = "]
for i, l in enumerate(t, 1):
    for k in keys:
        if k in l:
            print(i, l[:170].rstrip())
            break
print("==== pf_row + cfg + materializer head ====")
for i, l in enumerate(t, 1):
    if 'ROW_I}221: {{"a"' in l or '221: {{"batch"' in l or '"a_seed_base": {a_lo}' in l or '"b_exit_seed_base": {b_lo}' in l or '"shard_subdir": "n1_w221"' in l or "--- W221 materializer face" in l or 'WAVE_CONFIGS[220]["a_seed_base"]' in l or 'f"W221 A hits' in l or 'assert pf.N1_BANDS[220] ==' in l:
        print(i, l[:170].rstrip())
