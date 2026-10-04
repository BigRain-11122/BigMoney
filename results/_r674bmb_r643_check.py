# -*- coding: utf-8 -*-
# r674 bm-b r643 three-proof: p1d gates pid parentage + codely session count + gates file writer state
import subprocess, json, os, time

def ps(cmd):
    r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True)
    return r.stdout.decode("utf-8", "replace")

# all processes whose cmdline mentions codely OR the p1d runner pid 28092
out = ps("Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'codely' -or $_.ProcessId -eq 28092 } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress")
try:
    procs = json.loads(out or "[]")
    if isinstance(procs, dict):
        procs = [procs]
except Exception:
    procs = []

res = {"ts": time.time(), "procs": []}
for p in procs:
    res["procs"].append({"pid": p.get("ProcessId"), "parent": p.get("ParentProcessId"),
                         "created": p.get("CreationDate"),
                         "cmd": (p.get("CommandLine") or "")[:160]})
# gates file state
gpath = r"results\p1d_gates.json"
if os.path.exists(gpath):
    st = os.stat(gpath)
    res["p1d_gates_mtime_age_sec"] = round(time.time() - st.st_mtime, 0)
    res["p1d_gates_size"] = st.st_size

with open(r"results\_r674bmb_r643_check.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print("OK n=%d gates_age=%s" % (len(procs), res.get("p1d_gates_mtime_age_sec")))
