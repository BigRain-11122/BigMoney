# -*- coding: utf-8 -*-
# r674 bm-b: S6 chain liveness after tool cancel (r460 law: driver log = evidence face, CIM full-scan)
import subprocess, json, os, time

def ps(cmd):
    r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True)
    return r.stdout.decode("utf-8", "replace")

out = ps("Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match '_r674bmb_s6_chain' -or $_.CommandLine -match 'update_fundamental' } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress")
try:
    procs = json.loads(out or "[]")
    if isinstance(procs, dict):
        procs = [procs]
except Exception:
    procs = []

logp = r"results\_r674bmb_s6_log.txt"
tail = []
if os.path.exists(logp):
    with open(logp, encoding="utf-8") as f:
        tail = f.read().splitlines()[-6:]

res = {"ts": time.time(),
       "chain_procs": [{"pid": p.get("ProcessId"), "created": p.get("CreationDate"),
                        "cmd": (p.get("CommandLine") or "")[:120]} for p in procs],
       "log_tail": tail,
       "log_mtime_age": round(time.time() - os.stat(logp).st_mtime, 0) if os.path.exists(logp) else None}
with open(r"results\_r674bmb_s6_alive.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print("OK procs=%d log_age=%s" % (len(procs), res["log_mtime_age"]))
