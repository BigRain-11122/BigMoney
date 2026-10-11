import json, io
OLD = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r896bmc_orders_old.txt"
NEW = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r896bmc_orders_blob.txt"
OUT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r896bmc_orders_delta.txt"
old = io.open(OLD, "r", encoding="utf-8", errors="replace").read().splitlines()
new = io.open(NEW, "r", encoding="utf-8", errors="replace").read().splitlines()
oldset = set(old)
new_rows = [l for l in new if l not in oldset and l.strip()]
with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("old_lines=%d new_lines=%d new_rows=%d\n" % (len(old), len(new), len(new_rows)))
    for l in new_rows:
        f.write(l + "\n---\n")
print("old=%d new=%d new_rows=%d" % (len(old), len(new), len(new_rows)))
