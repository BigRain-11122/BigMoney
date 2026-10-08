p = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\logs\iteration-loop\round_reports-bm-c.md"
d = open(p, "rb").read().decode("utf-8", "replace")
lines = [l for l in d.splitlines() if l.strip()]
r780 = lines[-2]
print("len=", len(r780))
print("TAIL:")
print(r780[2400:])
import os
rp = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r780bmc_row.txt"
print("rowtxt_exists=", os.path.exists(rp), os.path.getsize(rp) if os.path.exists(rp) else -1)
