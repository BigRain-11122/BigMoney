import subprocess
out = subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|git|wscript' } | "
     "Select-Object ProcessId,Name,CreationDate,CommandLine | ConvertTo-Json -Compress"],
    capture_output=True).stdout.decode("utf-8", "replace")
import json
try:
    d = json.loads(out)
    if isinstance(d, dict):
        d = [d]
except Exception:
    d = []
for p in d:
    cl = (p.get("CommandLine") or "")
    if any(k in cl for k in ("saturation", "core_sampler", "n1_", "perpetual", "wscript", "git ")):
        print(p.get("ProcessId"), "|", p.get("Name"), "|",
              (p.get("CreationDate") or "")[:19], "|", cl[:150])
print("total scanned:", len(d))
