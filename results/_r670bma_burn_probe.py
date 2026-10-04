# r670 bm-a: burn liveness + progress probe (dual-form per r661 law)
import subprocess, json, os, glob

# Form 1: full CIM scan for theme_judge processes
r = subprocess.run(["powershell", "-NoProfile", "-Command",
    "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*theme_judge_p1*' } | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],
    capture_output=True)
out = r.stdout.decode("utf-8", errors="replace").strip()
print("procs:", out[:1500] if out else "NONE")

# Form 2: python children count
r2 = subprocess.run(["powershell", "-NoProfile", "-Command",
    "(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\").Count"], capture_output=True)
print("python.exe count:", r2.stdout.decode(errors="replace").strip())

# frags progress
frags = sorted(glob.glob("results/theme_judge_p1/nulls_frags/*"), key=os.path.getmtime)
print("frags count:", len(frags))
for f in frags[-5:]:
    print("  ", os.path.basename(f), os.path.getsize(f), os.path.getmtime)
print("burn_state.json exists:", os.path.exists("results/theme_judge_p1/burn_state.json"))
