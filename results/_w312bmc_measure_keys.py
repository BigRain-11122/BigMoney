# -*- coding: utf-8 -*-
"""Measure candidate anchor keys for the W312 splice editor bump."""
import io

s = io.open("results/_w311bmc_freeze_edits.py", encoding="utf-8").read()
keys = [
    "SIXTY-FIFTH", "SIXTY-FOURTH", "SIXTY-SIXTH",
    "HUNDRED-AND-TWENTY-EIGHTH", "HUNDRED-AND-TWENTY-NINTH",
    "THREE HUNDRED AND NINTH", "THREE HUNDRED AND TENTH",
    "NEW_W = 311", "PREV_W = 310", "PRIOR_W = 309",
    "w<310>", "w<309>", "w<311>",
    "len(owner_rows_live) == 300 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 129",
    "(expect 300/130/129)",
    "wave 311: ", "311: {\"batch\"", "311: {{\"batch\"", "311: {{\"a\"",
    "range(306, 298, -1)",
    "1_106_341", "1,106,341", "1,104,141", "679,920", "682,120",
    "677_720", "679_920", "169 parity rows",
    "legs (63)", "legs (62)", "15:1x", "5cbfce8417",
    "r1198", "r1200", "MSG-20261024-1540-bmc-w311-seat",
    "762bcad762", "0b0265a62d", "2fdb496bb6", "831cbe0a27",
    "697_101", "699_301", "697_300", "699_500", "697_301",
    "699_501", "697_500", "699_700", "699_100", "701_300",
    "699_300", "701_500", "699_501", "701_500",
    "699_501..701_500", "701_501..701_700",
    "0.000297", "0.000298", "0.000296", "parity",
]
for k in keys:
    print(repr(k), s.count(k))
print("len", len(s))