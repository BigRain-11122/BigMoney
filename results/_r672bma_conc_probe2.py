# r672 bm-a: full cmdline of bigmoney-matching processes
import subprocess, io, os

out = os.path.join(os.path.dirname(__file__), "_r672bma_conc_probe2.txt")
r = subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*bigmoney*' } | "
     "ForEach-Object { \"{0}|{1}|{2}\" -f $_.ProcessId, $_.Name, $_.CommandLine } | Out-String -Width 400"],
    capture_output=True, timeout=120)
txt = r.stdout.decode("utf-8", errors="replace")
with io.open(out, "w", encoding="utf-8") as f:
    f.write(txt)
for l in txt.splitlines():
    if l.strip():
        print(l[:200])
