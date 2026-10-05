"""r555 bm-c S6 key-readings extract (for round report face). Read-only."""
import io
import re

s = io.open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r555bmc_s6_log.txt",
            encoding="utf-8-sig").read()
for pat in [r"ZERO-DRIFT.*", r'"verdict": "[a-z_]+"',
            r"asof=\d+ state=\w+.*", r"cell=[A-Z_]+"]:
    m = re.findall(pat, s)
    print(pat[:18], "->", m[:2])
m = re.search(r"latest panel bar[^\n]*", s)
print("bar:", m.group(0) if m else "n/a")
m = re.search(r"data cutoff: [0-9-]+", s)
print("cutoff:", m.group(0) if m else "n/a")
