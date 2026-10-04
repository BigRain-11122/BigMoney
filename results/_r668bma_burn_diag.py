"""r668 bm-a: inspect latest autofill launches + find theme-judge launch log
+ process liveness (r659 CSV full-scan law: no tasklist /FI single-pid)."""
import csv
import json
import os
import subprocess

d = json.load(open("results/autofill_state.bm-a.json", encoding="utf-8"))
last = d.get("launches", [])[-3:]
for L in last:
    print(json.dumps(L, ensure_ascii=False)[:400])
lt = d.get("last_tick", {})
print("last_tick:", json.dumps(lt, ensure_ascii=False)[:400])
# candidate runner log files, newest first
cands = []
for f in os.listdir("results"):
    if "autofill" in f.lower() or "theme_judge" in f.lower():
        p = os.path.join("results", f)
        if os.path.isfile(p):
            cands.append((os.path.getmtime(p), p))
cands.sort(reverse=True)
for m, p in cands[:6]:
    print("cand:", p, int(m))
# python processes whose cmdline mentions theme_judge (CSV full scan)
r = subprocess.run(["tasklist", "/FO", "CSV"], capture_output=True)
rows = list(csv.reader(r.stdout.decode("gbk", "replace").splitlines()))
pids = []
for row in rows[1:]:
    if len(row) >= 2 and row[0].startswith("python"):
        pids.append(int(row[1]))
alive_tj = []
for pid in pids:
    q = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         f"(Get-CimInstance Win32_Process -Filter 'ProcessId={pid}').CommandLine"],
        capture_output=True)
    cl = q.stdout.decode("gbk", "replace")
    if "theme_judge" in cl:
        alive_tj.append((pid, cl.strip()[:150]))
print("python_procs:", len(pids), "theme_judge_alive:", alive_tj)
