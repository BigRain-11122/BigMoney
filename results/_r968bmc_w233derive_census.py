# -*- coding: utf-8 -*-
t = open(r"results\_w232bmc_20261013_probe.py", encoding="utf-8").read()
faces = [
    "_r966bmc_w231_fivekey_receipt", "_r963bmc", "r966", "r963", "r965", "r967", "r968",
    "8d3a1b78a", "6638ddf9f", "aee0bd9fa", "aebe0a5ac", "492972ee7", "4e373b743",
    "931_989", "929_789", "506_120", "503_920",
    "NINETY-SECOND", "NINETY-THIRD", "NINETY-FIRST",
    "(523_004, 525_003)", "(525_004, 525_203)",
    "owner_total == 221", "221st wave", 'bmc_ordinal": 61', 'bmc_ordinal": 62',
    '"ordinal": 221', '"ordinal": 222', "candidate = 62nd", "61st owned", "220th",
    "20261012", "20261013",
    "_w231bmc_20261013_probe_receipt", "w<232", "w<231",
    "range(16, 232)", "range(16, 231)",
    "231", "232", "230",
    "fivekey", "fivekey_receipt", "owner_total", "seat MSG", "MSG-20261013",
    "525_204", "527_203", "527_204", "527_403", "first_clean", "hops",
]
for s in faces:
    print(repr(s), t.count(s))
# dump contexts for r966/r963/fivekey mentions
import re
for pat in ("r966", "r963", "fivekey"):
    print("---- contexts for", pat)
    for m in re.finditer(re.escape(pat), t):
        seg = t[max(0, m.start() - 70):m.start() + 90].replace("\n", "\\n")
        print("   ", repr(seg))
