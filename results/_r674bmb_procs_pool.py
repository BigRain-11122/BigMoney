# -*- coding: utf-8 -*-
# r674 bm-b: python process listing (daemon liveness) + pool entries trio scan (structure-correct)
import subprocess, json

# --- python processes ---
r = subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"],
                   capture_output=True)
try:
    ps = json.loads(r.stdout.decode("utf-8", "replace") or "[]")
    if isinstance(ps, dict):
        ps = [ps]
except Exception:
    ps = []
OUT = {"py_procs": [{"pid": p.get("ProcessId"),
                     "cmd": (p.get("CommandLine") or "")[:200]} for p in ps]}

# --- pool entries trio scan ---
pool = json.load(open(r"results\runnable_pool.json", encoding="utf-8"))
ents = pool.get("entries", [])
trio = [e for e in ents if isinstance(e, dict) and "fund_" in str(e.get("id", "")) and "p1" in str(e.get("id", ""))]
OUT["pool_trio"] = [{k: e.get(k) for k in ("id", "status", "owner", "owner_since", "lane_owner", "note") if k in e}
                    for e in trio]
OUT["pool_total"] = len(ents)

with open(r"results\_r674bmb_procs_pool.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1)
print("OK procs=%d trio_entries=%d" % (len(ps), len(trio)))
