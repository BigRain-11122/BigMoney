"""r688 bm-a: finalize process liveness + log state after harness 5-min kill."""
import os
import subprocess

# liveness: full CIM scan, match command line
ps = (
    "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" "
    "| Select-Object ProcessId,CommandLine | ConvertTo-Json"
)
out = subprocess.run(
    ["powershell", "-NoProfile", "-Command", ps], capture_output=True
).stdout.decode("gbk", "replace")
import json
procs = json.loads(out) if out.strip()[:1] in "[{" else []
if isinstance(procs, dict):
    procs = [procs]
hits = [p for p in procs if "judge-finalize" in (p.get("CommandLine") or "")]
print("judge-finalize processes alive:", [(p["ProcessId"]) for p in hits])

log = "results/_r688bma_finalize_log.txt"
if os.path.exists(log):
    b = open(log, "rb").read()
    print("log size:", len(b))
    tail = b.decode("utf-8", errors="replace")[-1500:]
    print("LOG TAIL:")
    print(tail)
else:
    print("log missing")

# finalize output faces existence check
for f in ("results/mass_trial/w3_judge.json", "results/trial_labor_w3/w3_judge.json",
          "results/mass_trial/w3_judge_final.json"):
    print(f, "exists:", os.path.exists(f))
