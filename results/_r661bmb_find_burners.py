# Find actual trio NULLS burner processes (full CIM sweep, cmdline match)
import subprocess, json

r = subprocess.run(["powershell", "-NoProfile", "-Command",
    "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'nulls|fund' } | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress"],
    capture_output=True)
out = r.stdout.decode("utf-8", "replace").strip()
try:
    data = json.loads(out)
except Exception:
    print("RAW:", out[:500]); data = []
if isinstance(data, dict):
    data = [data]
for p in data:
    cl = str(p.get("CommandLine", ""))[:220]
    print("PID", p.get("ProcessId"), "|", p.get("Name"), "|", cl)
print("---total:", len(data))
