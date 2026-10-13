# -*- coding: utf-8 -*-
# r972 S0.5 ORD consumption: diff docs/orders.md watermark blob vs origin blob.
import subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
G = r"C:\Program Files\Git\cmd\git.exe"
R = r"K:\Fluxgroup\FluxGroup"

def blob(rev):
    b = subprocess.run([G, "-C", R, "show", rev], capture_output=True).stdout
    assert b, f"blob fetch failed {rev}"
    return b.decode("utf-8", errors="replace")

old = blob("90f4d26d5468886588dcca97d66cbdf420690838")
new = blob("6d24f1264dbe62290fcc749f3dda420b708e353b")
old_lines = set(old.splitlines())
print("=== NEW ORDERS ROWS (in origin blob, not in watermark blob) ===")
for ln in new.splitlines():
    if ln not in old_lines and ln.strip():
        print(ln)
print("=== END ===")
