"""W167 finalize pre-flight probe (r518/r708/r752 laws) - read-only."""
import subprocess, json, glob, os, sys

# r708: live-process check (finalize/aggregator in flight)
cmd = ("Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'finalize' } "
       "| Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress")
out = subprocess.check_output(["powershell", "-NoProfile", "-Command", cmd]).decode("utf-8", errors="replace")
procs = []
if out.strip():
    procs = json.loads(out)
    if isinstance(procs, dict):
        procs = [procs]
hits = [p for p in procs if p.get("CommandLine") and "perpetual_faces_n1" in p["CommandLine"]]
print("live n1 finalize processes:", len(hits))
for h in hits:
    print("  PID", h["ProcessId"], str(h["CommandLine"])[:140])

# r518: origin same-head block check
r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "results/perpetual_faces/"],
                   capture_output=True, text=True)
w167 = [l for l in r.stdout.splitlines() if "w167" in l.lower()]
print("origin n1_w167 results file:", w167 if w167 else "NONE (clear to finalize)")

# local prior finalize files (r538 rerun double-count check)
local = sorted(glob.glob("results/perpetual_faces/n1_w167*"))
print("local n1_w167 finalize files:", local if local else "NONE (first run)")
local166 = sorted(glob.glob("results/perpetual_faces/n1_w166*"))
print("local n1_w166 anchor files:", local166)
