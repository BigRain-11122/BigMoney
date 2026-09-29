"""r252 bm-c S6 chain wrapper: reuse _r430bma driver LEGS (anti-rebuild), record per-leg rc
into results/_r252bmc_s6_chain.json (evidence file, prior-round _r244/_r249 pattern)."""
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
                           encoding="utf-8", errors="replace", timeout=900)
        out = (p.stdout or "").strip().splitlines()
        err = (p.stderr or "").strip().splitlines()
        tail = out[-1] if out else (err[-1] if err else "<no output>")
        rc = p.returncode
        rows.append({"i": i, "leg": name, "rc": rc, "tail": tail[:260]})
        print(f"[{i:02d}/37] rc={rc} {name} :: {tail[:160]}", flush=True)
        if rc != 0:
            non_green.append({"i": i, "leg": name, "rc": rc,
                              "tail3": [ln[:240] for ln in (out + err)[-3:]]})
            for ln in (out + err)[-3:]:
                print(f"    >> {ln[:220]}", flush=True)
    except subprocess.TimeoutExpired:
        non_green.append({"i": i, "leg": name, "rc": "TIMEOUT", "tail3": []})
        rows.append({"i": i, "leg": name, "rc": "TIMEOUT", "tail": ""})
        print(f"[{i:02d}/37] TIMEOUT {name}", flush=True)
    except Exception as exc:
        non_green.append({"i": i, "leg": name, "rc": "DRIVER-ERR", "tail3": [str(exc)[:240]]})
        rows.append({"i": i, "leg": name, "rc": "DRIVER-ERR", "tail": str(exc)[:200]})
        print(f"[{i:02d}/37] DRIVER-ERR {name}: {exc}", flush=True)

doc = {"round": "r252", "machine": "bm-c", "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
       "legs_total": len(rows), "non_green": non_green, "elapsed_sec": round(time.time() - t0, 1),
       "rows": rows}
with open("results/_r252bmc_s6_chain.json", "w", encoding="utf-8") as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=1)
print(f"CHAIN DONE {len(rows)}/37, non_green={len(non_green)}, elapsed {doc['elapsed_sec']}s", flush=True)
