"""r224 bm-c S6 chain sliced runner (reuse _r430bma driver LEGS, anti-rebuild).

Usage: python results/_r224bmc_s6_slice.py <start_idx> <end_idx>  (1-based, inclusive)
"""
import subprocess
import sys

import importlib.util

spec = importlib.util.spec_from_file_location("drv", "results/_r430bma_s6_chain_driver.py")
drv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(drv)

start = int(sys.argv[1])
end = int(sys.argv[2])
bad = 0
for i, leg in enumerate(drv.LEGS[start - 1:end], start):
    name = " ".join(leg[1:])
    try:
        p = subprocess.run(leg, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=900)
        out = (p.stdout or "").strip().splitlines()
        err = (p.stderr or "").strip().splitlines()
        tail = out[-1] if out else (err[-1] if err else "<no output>")
        print(f"[{i:02d}/37] rc={p.returncode} {name} :: {tail[:200]}", flush=True)
        if p.returncode != 0:
            bad += 1
            for ln in (out + err)[-3:]:
                print(f"    >> {ln[:240]}", flush=True)
    except subprocess.TimeoutExpired:
        bad += 1
        print(f"[{i:02d}/37] TIMEOUT {name}", flush=True)
    except Exception as exc:
        bad += 1
        print(f"[{i:02d}/37] DRIVER-ERR {name}: {exc}", flush=True)
print(f"SLICE DONE legs {start}-{end}, {bad} non-zero", flush=True)
sys.exit(0)
