# -*- coding: utf-8 -*-
"""One-off: derive the r1198 S6 chain driver from the r1197 driver (output name only)."""
import io

src = io.open("results/_r1197bmc_s6_chain.py", encoding="utf-8").read()
assert "_r1197bmc_s6_chain.json" in src
out = src.replace("_r1197bmc_s6_chain.json", "_r1198bmc_s6_chain.json")
out = out.replace("r1197 bm-c: S6 data/panel chain driver (39 legs, W309 closeout window).",
                  "r1198 bm-c: S6 data/panel chain driver (39 legs, W310 open window).")
io.open("results/_r1198bmc_s6_chain.py", "w", encoding="utf-8", newline="\n").write(out)
print("wrote results/_r1198bmc_s6_chain.py")