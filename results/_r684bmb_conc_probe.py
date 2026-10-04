# r684 bm-b: r643 three-evidence concurrency probe (push rejected; origin holds
# bm-b r688 closeout from a same-window session)
import subprocess, json, datetime

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return r.stdout + r.stderr

# E1: git reflog recent non-self timestamps
print("=== reflog last 6 ===")
print(run(["git", "reflog", "-6", "--date=iso"]))
# E2: codely processes with this repo in cmdline
print("=== codely procs in this repo ===")
ps = run(["powershell", "-NoProfile", "-Command",
          "Get-CimInstance Win32_Process | Where-Object {$_.CommandLine "
          "-like '*bigmoney*'} | Select-Object ProcessId,CreationDate,"
          "@{n='cl';e={$_.CommandLine.Substring(0,"
          "[Math]::Min(120,$_.CommandLine.Length))}} | ConvertTo-Json"])
print(ps[:2000])
# E3: origin pool face — does it carry my RC entry?
print("=== origin pool CONTEST-RC check ===")
out = run(["git", "show", "origin/main:results/runnable_pool.json"])
doc = json.loads(out)
ids = [e.get("id") for e in doc.get("entries", [])]
print("entries:", len(ids), "| CONTEST-YTD-P1-RC-0OF1 present:",
      "CONTEST-YTD-P1-RC-0OF1" in ids)
rc = [e for e in doc["entries"] if e.get("id") == "CONTEST-YTD-P1-RC-0OF1"]
if rc:
    print("shard status:", [(s.get("key"), s.get("status"),
                             s.get("owner")) for s in rc[0].get("shards", [])])
# origin ticket face
print("=== origin T-148 ticket progress keys ===")
out = run(["git", "show", "origin/main:fleet/tasks/T-2026-10-02-148-P1.json"])
tk = json.loads(out)
print([k for k in tk.keys() if k.startswith("progress")])
# origin round reports bm-b tail
print("=== origin round_reports tail (last 3 bm-b lines) ===")
out = run(["git", "show", "origin/main:logs/iteration-loop/round_reports.md"])
lines = [l for l in out.splitlines() if "(bm-b)" in l or "bm-b" in l]
for l in lines[-3:]:
    print(l[:220])
