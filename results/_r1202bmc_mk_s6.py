# -*- coding: utf-8 -*-
"""r1202 bm-c: derive this window's S6 chain driver from the proven r1199 driver.

Only the receipt filename and the window banner change; the 39 legs are identical
(user law: same legs every round, idempotent by design).
"""
import io

SRC = "results/_r1199bmc_s6_chain.py"
OUT = "results/_r1202bmc_s6_chain.py"

s = io.open(SRC, encoding="utf-8").read()
assert s.count("_r1199bmc_s6_chain.json") == 1, "receipt pointer count %d" % s.count("_r1199bmc_s6_chain.json")
assert s.count("r1199") >= 2, "banner r1199 count %d" % s.count("r1199")
s = s.replace("_r1199bmc_s6_chain.json", "_r1202bmc_s6_chain.json")
s = s.replace("r1199", "r1202")
s = s.replace("W310 Closed window", "W312 open window")
io.open(OUT, "w", encoding="utf-8", newline="\n").write(s)
print("WROTE %s bytes=%d legs=%d" % (OUT, len(s.encode("utf-8")), s.count('("')))