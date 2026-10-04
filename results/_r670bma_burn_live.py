# r670 bm-a: relight liveness + expected completion math (subprocess raw, dual-form)
import subprocess, os, time, json

r = subprocess.run(["powershell", "-NoProfile", "-Command",
    "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | "
    "Where-Object { $_.CommandLine -like '*theme_judge_p1*' } | "
    "Select-Object ProcessId,CreationDate | ConvertTo-Json -Compress"],
    capture_output=True)
out = r.stdout.decode("utf-8", errors="replace").strip()
print("burn procs:", out if out else "NONE FOUND")

# workers count (spawn children)
r2 = subprocess.run(["powershell", "-NoProfile", "-Command",
    "(Get-CimInstance Win32_Process -Filter 'Name=' + [char]39 + 'python.exe' + [char]39).Count"],
    capture_output=True)
print("python.exe total:", r2.stdout.decode(errors="replace").strip())

p = "results/theme_judge_p1/burn_state.json"
print("burn_state exists:", os.path.exists(p))
# progress: count non-empty frags (the pool writes all frags at map end, so
# in-flight progress = py CPU of the pool; just report frag dir state)
import glob
n_nonempty = 0
for f in glob.glob("results/theme_judge_p1/nulls_frags/*.json"):
    row = json.load(open(f, encoding="utf-8"))
    if row.get("ks"):
        n_nonempty += 1
print("non-empty frags:", n_nonempty, "(2=pre-burn healthy chunk_00s only; >2 = new chunks landing)")
