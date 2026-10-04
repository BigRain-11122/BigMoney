# -*- coding: utf-8 -*-
"""r677 bm-a: P2 burn liveness probe (CSV full-scan + column compare, r659 law)."""
import csv, io, json, os, subprocess

p = subprocess.run(["tasklist", "/FO", "CSV"], capture_output=True, text=True)
rows = list(csv.DictReader(io.StringIO(p.stdout)))
py = [(r["PID"], r.get("Image Name", "")) for r in rows
      if "python" in (r.get("Image Name") or "").lower()]
res = {"python_procs": len(py), "pids": [x[0] for x in py], "p2_burn": None,
       "frags": 0, "burn_state": None, "pool_shard": None}
# command lines via CIM full scan (second-form cross-check, r661 law)
c = subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "Get-CimInstance Win32_Process | Where-Object { $_.Name -like "
     "'*python*' } | Select-Object ProcessId,CommandLine | ConvertTo-Json"],
    capture_output=True, text=True)
try:
    cj = json.loads(c.stdout)
    if isinstance(cj, dict):
        cj = [cj]
    for r in cj or []:
        cl = r.get("CommandLine") or ""
        if "theme_judge_p2" in cl:
            res["p2_burn"] = {"pid": r.get("ProcessId"), "cmd": cl[:120]}
except Exception as exc:
    res["cim_error"] = repr(exc)[:200]
frags = os.path.join("results", "theme_judge_p2", "nulls_frags")
if os.path.isdir(frags):
    res["frags"] = len([f for f in os.listdir(frags) if f.endswith(".json")])
res["burn_state"] = os.path.exists(
    os.path.join("results", "theme_judge_p2", "burn_state.json"))
pool = json.load(open("results/runnable_pool.json", encoding="utf-8"))
for e in pool["entries"]:
    if e["id"] == "THEME-JUDGE-P2":
        res["pool_shard"] = e["shards"][0]
print(json.dumps(res, ensure_ascii=False))
