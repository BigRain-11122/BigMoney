# -*- coding: utf-8 -*-
# r1019 bm-a: W246-era RAM anchor probe + current free RAM (b6 face facts)
import subprocess, re, sys
sys.stdout.reconfigure(encoding="utf-8")
for sha in ["9ebecf60d", "650953086", "e06f4ee2a"]:
    out = subprocess.run(["git", "show", sha + ":fleet/machines/bm-a.json"],
                         capture_output=True).stdout.decode("utf-8", errors="replace")
    m = re.search(r'"idle_ram_gb"\s*:\s*([\d.]+)', out)
    m2 = re.search(r'"clock_read"\s*:\s*"([^"]+)"', out)
    print(sha, "ram=", m.group(1) if m else None, "clock=", m2.group(1) if m2 else None)
try:
    import psutil
    print("now_free_ram_gb", round(psutil.virtual_memory().available / 1e9, 1))
    print("now_total_ram_gb", round(psutil.virtual_memory().total / 1e9, 1))
except ImportError:
    print("psutil MISSING")
