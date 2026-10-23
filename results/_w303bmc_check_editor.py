# -*- coding: utf-8 -*-
import io

t = io.open("results/_w303bmc_freeze_edits.py", encoding="utf-8").read()
KEYS = ["NEW_W = 303", "PREV_W = 302", "PRIOR_W = 301", "681_901", "683_900",
        "684_100", "683_700", "161 parity rows", "1_088_741", "662_320",
        "FIFTY-SIXTH", "FIFTY-SEVENTH", "THREE HUNDRED AND FIRST",
        "HUNDRED-AND-TWENTIETH", "upstream_w302", "wave 303: ", "303: {",
        '"wave": 302', "MSG-20261024-0640-bmc-w303-seat", "f09ad33571",
        "_w303bmc_20261024_probe_receipt.json", "2026-10-24 06:4x",
        "range(298, 290, -1)"]
for k in KEYS:
    print("%-46s %d" % (k, t.count(k)))
print("ZZ", t.count("ZZ"), "| 679_", t.count("679_"), "| bytes", len(t))
for line in t.splitlines()[:12]:
    print("H:", line)