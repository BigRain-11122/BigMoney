# -*- coding: utf-8 -*-
"""r793 bm-a group-decisions fresh-read scan (r786 law: origin blob via subprocess
bytes, zero tree touch; find rows newer than local watermark consumption window)."""
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
G = r"C:\Users\sjs20\Desktop\FluxGroup"


def show(path: str) -> str:
    return subprocess.run(["git", "-C", G, "show", f"origin/main:{path}"], capture_output=True).stdout.decode("utf-8", errors="replace")


dec = show("docs/decisions.md")
lines = dec.splitlines()
print("decisions total lines:", len(lines))
# rows dated 2026-10-05/10-06 = likely delta after the r790-era watermark
for i, l in enumerate(lines):
    if re.search(r"2026-10-0[56]", l) or "20261005" in l or "20261006" in l or "2026100[56]" in l:
        print(f"L{i+1}: {l[:220]}")

print("\n===== orders.md CEO physical-wait section =====")
orders = show("docs/orders.md")
olines = orders.splitlines()
print("orders total lines:", len(olines))
for i, l in enumerate(olines):
    if re.search(r"2026-10-0[56]", l) and ("BigMoney" in l or "quant" in l or "量化" in l):
        print(f"L{i+1}: {l[:220]}")
