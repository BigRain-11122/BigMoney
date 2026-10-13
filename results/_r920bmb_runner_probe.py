import json, os, subprocess, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = {}
r = subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Get-CimInstance Win32_Process | Where-Object "
                    "{($_.Name -eq 'python.exe' -or $_.Name -eq 'pythonw.exe') -and "
                    "$_.CommandLine -match 'alphagen'} | "
                    "Select-Object ProcessId,Name,CreationDate,CommandLine | ConvertTo-Json -Compress"],
                   capture_output=True, text=True)
out["procs_stdout"] = (r.stdout or "").strip()[:1500]
out["procs_stderr"] = (r.stderr or "").strip()[:300]
# recent files under results/alphagen_rl_p1
d = os.path.join(ROOT, "results", "alphagen_rl_p1")
recent = []
for sub in ("", "ckpt", "logs"):
    p = os.path.join(d, sub) if sub else d
    if not os.path.isdir(p):
        continue
    for fn in os.listdir(p):
        fp = os.path.join(p, fn)
        if os.path.isfile(fp):
            st = os.stat(fp)
            recent.append({"f": os.path.relpath(fp, ROOT), "size": st.st_size,
                           "mtime": time.strftime("%m-%d %H:%M:%S", time.localtime(st.st_mtime))})
recent.sort(key=lambda x: x["mtime"], reverse=True)
out["recent_files"] = recent[:12]
# worker claim files
cd = os.path.join(ROOT, "results", "pool_claims", "N2U3-ALPHAGEN-RL-P1-LEG3-TRAIN")
if os.path.isdir(cd):
    out["claim_files"] = [{"f": f, "mtime": time.strftime("%m-%d %H:%M:%S", time.localtime(os.stat(os.path.join(cd, f)).st_mtime))} for f in os.listdir(cd)]
print(json.dumps(out, ensure_ascii=True, indent=1)[:2500])
