"""r536 bm-c S0.5b: dump group orders.md origin blob to UTF-8 scratch file,
extract CEO-pending rows involving this company (BigMoney/quant/bm-c)."""
import os
import re
import subprocess

CREATE_NO_WINDOW = 0x08000000
GROUP = r"K:\Fluxgroup\FluxGroup"
OUT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r536bmc_gorders_dump.txt"

r = subprocess.run(["git", "show", "origin/main:docs/orders.md"], capture_output=True,
                   cwd=GROUP, creationflags=CREATE_NO_WINDOW)
blob = r.stdout or b""
with open(OUT, "wb") as f:
    f.write(blob)
lines = blob.decode("utf-8", "replace").splitlines()
print("rc=%d lines=%d bytes=%d saved=%s" % (r.returncode, len(lines), len(blob), OUT))
# section scan: find CEO pending-physical-items region markers
for i, l in enumerate(lines):
    if ("待办" in l or "物理件" in l) and ("#" in l or l.startswith("|")):
        print("SECTION? L%d %s" % (i + 1, l[:80]))
