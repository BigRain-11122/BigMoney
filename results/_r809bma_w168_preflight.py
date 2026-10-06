"""W168 finalize pre-flight probe (r518/r708/r752 laws) - read-only."""
import subprocess, glob

# r708: live-process check (finalize/aggregator in flight)
out = subprocess.check_output(
    ["powershell", "-NoProfile", "-Command",
     "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'perpetual_faces_n1' }"
     " | Select-Object -ExpandProperty ProcessId"]).decode(errors="replace")
hits = [l for l in out.splitlines() if l.strip()]
print("live n1 processes:", hits if hits else "NONE")

# r518: origin same-head block check
r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "results/perpetual_faces/"],
                   capture_output=True, text=True)
w168 = [l for l in r.stdout.splitlines() if "w168" in l.lower()]
print("origin n1_w168 results file:", w168 if w168 else "NONE (clear to finalize)")

# local prior finalize files (r538 rerun double-count check)
local = sorted(glob.glob("results/perpetual_faces/n1_w168*"))
print("local n1_w168 finalize files:", local if local else "NONE (first run)")
local167 = sorted(glob.glob("results/perpetual_faces/n1_w167*"))
print("local n1_w167 anchor files:", local167)
