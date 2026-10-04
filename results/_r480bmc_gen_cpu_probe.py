"""r480 bm-c: generate process CPU-time probe (in-file per r446 law)."""
import json
import subprocess

r = subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "Get-CimInstance Win32_Process -Filter 'ProcessId=3484' | "
     "Select-Object ProcessId,UserModeTime,KernelModeTime | ConvertTo-Json"],
    capture_output=True, text=True,
    creationflags=0x08000000)
d = json.loads(r.stdout or "null")
if isinstance(d, dict):
    d = [d]
for p in d or []:
    print("pid", p["ProcessId"],
          "user_cpu_s", round(p["UserModeTime"] / 1e7, 1),
          "kernel_cpu_s", round(p["KernelModeTime"] / 1e7, 1))
if not d:
    print("PROC-GONE")
