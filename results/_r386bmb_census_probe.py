"""r386 bm-b census W2B liveness tree probe (r385 lesson: parent-idle = coordinator
norm; verdict needs worker-tree CPU delta, never parent-pid alone)."""
import json
import subprocess
import time

CMD = ("Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'census' } | "
       "Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json -Compress")


def snap(procs):
    out = {}
    q = subprocess.run(["powershell", "-NoProfile", "-Command", CMD],
                       capture_output=True, text=True)
    data = json.loads(q.stdout or "[]")
    if isinstance(data, dict):
        data = [data]
    for p in data:
        out[p["ProcessId"]] = p
    return data, out


def cpu_total(pid):
    q = subprocess.run(["powershell", "-NoProfile", "-Command",
                        f"(Get-Process -Id {pid} -ErrorAction SilentlyContinue).CPU"],
                       capture_output=True, text=True)
    try:
        return float(q.stdout.strip())
    except (ValueError, TypeError):
        return None


data, _ = snap({})
census = [p for p in data if "census" in (p.get("CommandLine") or "")]
print("census procs:", [(p["ProcessId"], p["Name"]) for p in census])

# worker tree census: any process whose parent is a census proc
parents = {p["ProcessId"] for p in census}
kids = [q for q in subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name | ConvertTo-Json -Compress"],
    capture_output=True, text=True).stdout and json.loads(
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name | ConvertTo-Json -Compress"],
                   capture_output=True, text=True).stdout or "[]") if q.get("ParentProcessId") in parents]

t0 = {k["ProcessId"]: cpu_total(k["ProcessId"]) for k in census + kids}
time.sleep(20)
t1 = {k["ProcessId"]: cpu_total(k["ProcessId"]) for k in census + kids}

alive = []
for pid in t0:
    d = (t1[pid] or 0) - (t0[pid] or 0)
    tag = "census-runner" if pid in parents else "worker"
    if t1[pid] is not None:
        print(f"pid {pid} [{tag}] cpu_delta_20s={d:.1f}s")
    if d > 0.5:
        alive.append((pid, round(d, 1)))

print("VERDICT:", "ALIVE-BURNING (no action, r385 law)" if alive else
      ("NO-LIVE-CPU (finalize/idle tail or dead; check result files)" if census else "NO CENSUS PROCS"))
