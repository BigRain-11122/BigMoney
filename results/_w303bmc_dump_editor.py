# -*- coding: utf-8 -*-
import io

KEYS = ("CFG_I", "ROW_I", "batch", "parity row", "PARITY", "boundary", "b_exit",
        "expect ", "bmc_rows_live", "owner_rows_live", "upstream_w", "wave ",
        "range(297", "301: ", "302: ", '"wave":', "MSG-2026", "THREE HUNDREDTH",
        "HUNDRED-AND-NINETEENTH", "FIFTY-", "1_086_541", "660_120", "ORDINALS")
lines = io.open("results/_w302bmc_freeze_edits.py", encoding="utf-8").read().splitlines()
for i, l in enumerate(lines, 1):
    if any(k in l for k in KEYS):
        print(i, l)