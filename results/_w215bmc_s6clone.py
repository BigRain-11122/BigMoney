# -*- coding: utf-8 -*-
# Clone r896 S6 chain driver -> r912 (Monday pre-market skip notes).
import io
t = io.open(r"results\_r896bmc_s6_chain.py", encoding="utf-8").read()
t = t.replace("_r896", "_r912").replace("r896 bm-c", "r912 bm-c")
t = t.replace("no new bar (last 2026-10-09 processed; Sunday)",
              "no new bar (Friday 2026-10-09 processed; Monday pre-market 05:5x, new bar 15:30 today)")
t = t.replace("monthly first-round leg; 10-11 is not month-first",
              "monthly first-round leg; 10-12 is not month-first")
io.open(r"results\_r912bmc_s6_chain.py", "w", encoding="utf-8").write(t)
print("r912 driver written")
