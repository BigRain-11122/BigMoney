# -*- coding: utf-8 -*-
# Clone r912 S6 chain driver -> r914 (Monday pre-market skip notes, same-day chain face).
import io
t = io.open(r"results\_r912bmc_s6_chain.py", encoding="utf-8").read()
t = t.replace("_r912", "_r914").replace("r912 bm-c", "r914 bm-c")
t = t.replace("Monday pre-market 05:5x, new bar 15:30 today",
              "Monday pre-market 07:1x, new bar 15:30 today")
io.open(r"results\_r914bmc_s6_chain.py", "w", encoding="utf-8").write(t)
print("r914 driver written")
