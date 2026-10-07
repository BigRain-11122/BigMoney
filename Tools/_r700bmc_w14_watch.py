"""r700 bm-c W14 judge watch: process liveness + recent output faces."""
import glob
import os
import subprocess
import time

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = time.time()

ps = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe' or "
      "Name='pythonw.exe'\" | Where-Object {$_.CommandLine -match "
      "'trial_labor_w14'} | Select-Object ProcessId,CreationDate | "
      "ConvertTo-Json -Compress")
r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                   capture_output=True, text=True, encoding="utf-8",
                   errors="replace")
print("judge procs:", (r.stdout or "").strip()[:300] or "NONE")

for pat in (r"results\trial_labor_w14*", r"results\trial_labor_w14\**",
            r"results\w14*", r"results\trial_labor\**",
            r"results\w14\**", r"results\trial_labor_w14*"):
    for f in glob.glob(os.path.join(REPO, pat)):
        try:
            st = os.stat(f)
        except OSError:
            continue
        age = (now - st.st_mtime) / 60.0
        if age < 120:
            print("RECENT %6.1fmin %8d %s" % (age, st.st_size,
                                              os.path.relpath(f, REPO)))
