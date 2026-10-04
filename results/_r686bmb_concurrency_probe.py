"""r686 bm-b: r643 three-evidence concurrent-session probe.

Evidence 1: git reflog timestamps in the recent window (non-this-session
merge/commit entries). Evidence 2: codely processes whose command line
references THIS repo (count>=2 => concurrent session). Evidence 3:
trio_burn_eta.json freshness + writer inference (which writer could have
touched it -- scheduled tasks vs sessions).
"""
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = {}

# Evidence 1: reflog recent entries
r = subprocess.run(["git", "-C", ROOT, "reflog", "--date=iso", "-8"],
                   capture_output=True)
out["reflog"] = r.stdout.decode("utf-8", "replace").strip().split("\n")

# Evidence 2: codely processes referencing this repo
try:
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "Get-CimInstance Win32_Process -Filter \"Name like '%codely%'\" "
         "| Select-Object ProcessId,CreationDate,CommandLine "
         "| ConvertTo-Json -Compress"],
        capture_output=True)
    procs = json.loads(r.stdout.decode("utf-8", "replace") or "[]")
    if isinstance(procs, dict):
        procs = [procs]
    hits = []
    for p in procs:
        cl = (p.get("CommandLine") or "")
        if "quant" in cl and ("bigmoney" in cl or "BIGMONEY" in cl):
            hits.append({"pid": p.get("ProcessId"),
                         "created": str(p.get("CreationDate")),
                         "cl_head": cl[:140]})
    out["codely_in_repo"] = hits
    out["codely_total"] = len(procs)
except Exception as e:
    out["evidence2_err"] = repr(e)

# Evidence 3: file freshness witnesses
for f in ("results/trio_burn_eta.json", "state.json",
          "logs/iteration-loop/round_reports.md"):
    fp = os.path.join(ROOT, f)
    if os.path.exists(fp):
        st = os.stat(fp)
        out.setdefault("freshness", {})[f] = {
            "mtime": time.strftime("%H:%M:%S", time.localtime(st.st_mtime))}

json.dump(out, open(os.path.join(ROOT, "results",
                                 "_r686bmb_concurrency_probe.json"), "w",
                    encoding="utf-8"), ensure_ascii=True, indent=1)
print(json.dumps({"codely_in_repo_n": len(out.get("codely_in_repo", [])),
                  "codely_total": out.get("codely_total"),
                  "reflog_last": out["reflog"][:2],
                  "freshness": out.get("freshness")}, ensure_ascii=True,
                 indent=1))
