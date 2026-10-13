# -*- coding: utf-8 -*-
"""r966: census _w231bmc_20261013_probe.py stale-token faces for the W232 derive pairs."""
import io
t = io.open(r"results\_w231bmc_20261013_probe.py", encoding="utf-8").read()
needles = [
 "r963", "r964", "r965", "r962", "_r963bmc_w230_fivekey_receipt",
 "24e12fa5e", "6cfe285e3", "91de0ae83", "0ef11a120", "aec41c57c",
 "6638ddf9f", "aebe0a5ac", "NINETIETH", "NINETY-FIRST", "NINETY-SECOND",
 "NINETY-THIRD", "W230", "W229", "W231", "W232", "927_589", "929_789",
 "503_920", "506_120", "219", "220", "221", "(520_804, 522_803)",
 "(522_804, 523_003)", "(523_004, 525_003)", "(525_004, 525_203)",
 "owner_total", "bmc_ordinal", "NINETY-FIRST instance", "per the same continuity",
 "freeze receipt = ", "live rows + ", "bare230", "STAIRCASE",
 "NINETY-FIRST instance anticipated", "TWO HUNDRED AND THIRTY-FIRST",
 "TWO HUNDRED AND THIRTY-SECOND",
]
for nd in needles:
    print("%-46r %d" % (nd, t.count(nd)))
print("total bytes", len(t))
