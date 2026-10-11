# -*- coding: utf-8 -*-
# r914 helper: dump W215 freeze-time prereg blob to temp file for pair drafting
import subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
BLOB = subprocess.run(["git", "-C", REPO, "show",
                       "1d9008192:research/PERPETUAL_N1_W215_PREREG.md"],
                      capture_output=True).stdout
assert BLOB, "blob fetch failed"
open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r914bmc_w215_blob.md", "wb").write(BLOB)
t = BLOB.decode("utf-8")
print("bytes:", len(BLOB), "| lines:", t.count("\n") + 1)
print("W215 count:", t.count("W215"), "| W214 count:", t.count("W214"), "| W213 count:", t.count("W213"))
print("W214-n1 refs:", t.count("n1_w214"), "| n1_w215:", t.count("n1_w215"), "| n1_w213:", t.count("n1_w213"))
