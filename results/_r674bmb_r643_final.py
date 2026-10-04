# -*- coding: utf-8 -*-
# r674 bm-b r643 final: children of concurrent codely pids + repo files modified in last 180s
import subprocess, json, os, time

def ps(cmd):
    r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True)
    return r.stdout.decode("utf-8", "replace")

codely_pids = [49764, 33860, 58824, 17836]
out = ps("Get-CimInstance Win32_Process | Where-Object { " +
         " or ".join("$_.ParentProcessId -eq %d" % p for p in codely_pids) +
         " } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress")
try:
    kids = json.loads(out or "[]")
    if isinstance(kids, dict):
        kids = [kids]
except Exception:
    kids = []

res = {"probe_ts": time.time(), "children": [{"pid": k.get("ProcessId"), "parent": k.get("ParentProcessId"),
        "created": k.get("CreationDate"), "cmd": (k.get("CommandLine") or "")[:140]} for k in kids]}

# recent repo writes (last 180s), excluding my known probe files
recent = []
now = time.time()
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "Money02", "legacy", "node_modules")]
    for fn in files:
        p = os.path.join(root, fn)
        try:
            m = os.stat(p).st_mtime
        except OSError:
            continue
        if now - m < 180:
            recent.append({"path": p, "age_s": round(now - m, 0)})
res["recent_writes"] = sorted(recent, key=lambda x: x["age_s"])[:40]

with open(r"results\_r674bmb_r643_final.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print("OK kids=%d recent=%d" % (len(kids), len(recent)))
