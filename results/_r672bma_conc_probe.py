# r672 bm-a: live codely process probe (r643 three-evidence law, pre-round concurrency check)
import subprocess, io, os

out = os.path.join(os.path.dirname(__file__), "_r672bma_conc_probe.txt")
r = subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*bigmoney*' } | "
     "Select-Object ProcessId, CreationDate | Format-Table -AutoSize | Out-String"],
    capture_output=True, timeout=120)
lines = [l for l in r.stdout.decode("utf-8", errors="replace").splitlines()
         if l.strip()]
with io.open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("procs_with_bigmoney_prompt_lines:", len(lines))
for l in lines[:6]:
    print(l[:120])
