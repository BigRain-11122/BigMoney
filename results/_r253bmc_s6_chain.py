#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r253 bm-c S6 chain wrapper: reuse _r430bma driver LEGS (anti-rebuild), evidence -> _r253bmc_s6_chain.json."""
import importlib.util
import json
import subprocess
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

spec = importlib.util.spec_from_file_location("drv", "results/_r430bma_s6_chain_driver.py")
drv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(drv)

rows = []
non_green = []
t0 = time.time()
for i, leg in enumerate(drv.LEGS, 1):
    name = " ".join(leg[1:])
    try:
        p = subprocess.run(leg, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=240)
        out = (p.stdout or "").strip().splitlines()
        err = (p.stderr or "").strip().splitlines()
        tail = out[-1] if out else (err[-1] if err else "<no output>")
        rc = p.returncode
        rows.append({"i": i, "leg": name, "rc": rc, "tail": tail[:260]})
        print(f"[{i:02d}/{len(drv.LEGS)}] rc={rc} {name} :: {tail[:150]}", flush=True)
        if rc != 0:
            non_green.append({"i": i, "leg": name, "rc": rc,
                              "tail3": [ln[:240] for ln in (out + err)[-3:]]})
            for ln in (out + err)[-3:]:
                print(f"    >> {ln[:200]}", flush=True)
    except subprocess.TimeoutExpired:
        non_green.append({"i": i, "leg": name, "rc": "TIMEOUT"})
        print(f"[{i:02d}] TIMEOUT {name}", flush=True)

elapsed = round(time.time() - t0, 1)
report = {
    "round": 253, "machine": "bm-c", "elapsed_sec": elapsed,
    "legs_total": len(rows), "non_green": non_green,
    "note": "rebase double-wedge window; S6 full chain per driver _r430bma (anti-rebuild reuse)",
    "rows": rows,
}
with open("results/_r253bmc_s6_chain.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print(f"DONE elapsed={elapsed}s legs={len(rows)} non_green={len(non_green)}", flush=True)
